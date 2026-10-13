"""FastAPI application server with lifespan management and standardized error envelopes."""

import os
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.api.routes import router, set_sync_engine
from src.graph.neo4j_sync import Neo4jSyncEngine
from src.graphrag.exceptions import GraphRAGException

# Load environment variables from .env file
load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manages Neo4j driver connection lifecycle during server startup and shutdown."""
    neo4j_uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    neo4j_user = os.getenv("NEO4J_USERNAME", "neo4j")
    neo4j_pass = os.getenv("NEO4J_PASSWORD", "qwertyui")

    engine = Neo4jSyncEngine(uri=neo4j_uri, username=neo4j_user, password=neo4j_pass)
    engine.init_schema()
    engine.get_driver().verify_connectivity()
    set_sync_engine(engine)
    print(f"[API Server] Connected to Neo4j at {neo4j_uri}")

    yield

    engine.close()
    print("[API Server] Neo4j connection pool drained cleanly.")


def create_app() -> FastAPI:
    """Builds and configures the FastAPI application instance."""
    app = FastAPI(
        title="LAG Policy Graph & GraphRAG API",
        description="Browser-based Graph Visualizer and Hugging Face GraphRAG Engine API",
        version="1.0.0",
        lifespan=lifespan,
    )

    # Configure CORS for local React/Vite development
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:3000",
            "http://localhost:5173",
            "http://127.0.0.1:3000",
            "http://127.0.0.1:5173",
            "*",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Standardized Error Envelope Handler for HTTPExceptions
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        detail = exc.detail
        if isinstance(detail, dict):
            error_type = detail.get("error_type", "HTTPException")
            message = detail.get("message", str(detail))
            details = detail.get("details", {})
        else:
            error_type = "HTTPException"
            message = str(detail)
            details = {}

        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": True,
                "error_type": error_type,
                "message": message,
                "details": details,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
        )

    # Standardized Error Envelope Handler for uncaught GraphRAGExceptions
    @app.exception_handler(GraphRAGException)
    async def graphrag_exception_handler(request: Request, exc: GraphRAGException):
        return JSONResponse(
            status_code=400,
            content={
                "error": True,
                "error_type": exc.__class__.__name__,
                "message": exc.message,
                "details": exc.details,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
        )

    app.include_router(router)
    return app


app = create_app()

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("API_PORT", "8000"))
    uvicorn.run("src.api.server:app", host="0.0.0.0", port=port, reload=True)
