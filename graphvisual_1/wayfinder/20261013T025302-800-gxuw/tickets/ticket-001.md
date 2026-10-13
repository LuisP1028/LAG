# Decision Ticket 001: Backend FastAPI Server Architecture, REST Routes, and Neo4j Session Lifecycle Specification

**Ticket ID:** `ticket-001.md`  
**Scope:** Backend Infrastructure & API Service Layer  
**Status:** RESOLVED  
**Claimed By:** `wayfinder-read-and-plan`  
**Blocked By:** None (Root Decision)

---

## 1. Architectural Question

What web server architecture, endpoint routing structure, connection pooling strategy, and error serialization model must be implemented to serve graph topology data, resolve entity anchors, and coordinate GraphRAG interactions between the React browser visualization and the Neo4j knowledge graph with sub-second response times?

---

## 2. Decision and Specification Requirements

### 2.1. Framework Selection and Server Configuration
The backend service must be implemented as an asynchronous Python service using `FastAPI` and `uvicorn`:
- **Server Module:** `src/api/server.py`
- **Route Definitions:** `src/api/routes.py`
- **CORS Middleware:** Configured with `CORSMiddleware` permitting local frontend access (`allow_origins=["http://localhost:3000", "http://localhost:5173"]`, `allow_credentials=True`, `allow_methods=["*"]`, `allow_headers=["*"]`).
- **Server Port:** Default port `8000` (configurable via `API_PORT` environment variable).

### 2.2. Neo4j Driver Lifecycle & Connection Management
The service must manage Neo4j connections through `Neo4jSyncEngine` using FastAPI's application lifespan context manager (`lifespan`):
1. **Startup:**
   - Initialize singleton `Neo4jSyncEngine(uri=os.getenv("NEO4J_URI", "bolt://localhost:7687"), username=os.getenv("NEO4J_USERNAME", "neo4j"), password=os.getenv("NEO4J_PASSWORD", "qwertyui"))`.
   - Execute `engine.init_schema()` to guarantee all 16 node uniqueness constraints and indexes are mounted.
   - Verify active connectivity via `engine.get_driver().verify_connectivity()`.
2. **Shutdown:**
   - Execute `engine.close()` to cleanly drain connection pools.
3. **Request-Scoped Session Dependency:**
   - Define a FastAPI dependency `get_neo4j_session()` yielding a session within a context manager:
     ```python
     def get_neo4j_session():
         engine = get_sync_engine()
         with engine.get_driver().session(database=engine.database) as session:
             yield session
     ```

### 2.3. Authoritative REST Endpoint Contracts

The API must expose the following core routes:

1. **`GET /api/health`**
   - **Response Payload:** `{"status": "ok", "neo4j_connected": true, "timestamp": "<ISO-8601 UTC>"}`
2. **`GET /api/graph/summary`**
   - **Response Payload:** Returns aggregate node counts by label and edge counts by type via `Neo4jSyncEngine.get_summary_statistics()`.
3. **`GET /api/graph/topology`**
   - **Query Parameters:**
     - `policy_keyword`: Optional string (default: `"LTA"`)
     - `include_fee_schedules`: Boolean (default: `false` to avoid sending 3,800+ nodes to the initial browser canvas)
     - `state_filter`: Optional 2-letter state code (e.g., `"WI"`) to restrict fee schedule entries to a single jurisdiction.
   - **Response Payload:**
     - `nodes`: Array of node objects (`primary_key`, `label`, `name`, `properties`).
     - `edges`: Array of edge objects (`source_pk`, `target_pk`, `label`, `provenance`).
4. **`POST /api/entities/resolve`**
   - **Request Body:** `{"query": str}`
   - **Response Payload:** `{"anchors": [{"slot": "state" | "diagnosis" | "policy", "primary_key": str, "matched_text": str, "entity_type": str}]}`
5. **`POST /api/graphrag/subgraph`**
   - **Request Body:** `{"anchors": list[str]}` (array of primary keys)
   - **Response Payload:** `{"nodes": list[dict], "edges": list[dict], "retrieval_ms": float}`
6. **`POST /api/graphrag/query`**
   - **Request Body:** `{"query": str, "model_id": Optional[str], "state_code": Optional[str]}`
   - **Response Payload:**
     - `answer`: Plain-English synthesized explanation citing government sources.
     - `active_node_pks`: Array of traversed primary keys for canvas illumination.
     - `active_edge_keys`: Array of traversed edge keys for canvas illumination.
     - `anchors`: Array of resolved starting anchors.
     - `provenance_sources`: Array of edge provenance records (`source_uri`, `selector`, `ingestion_timestamp`, `run_id`).
     - `duration_ms`: Total execution latency.

### 2.4. Error Handling and Invariant Enforcement (`INV-FAIL-FAST`)
- Any failure in graph query execution, model API communication, or parameter parsing must return a standardized JSON error envelope:
  ```json
  {
    "error": true,
    "error_type": "EntityResolutionError | TraversalError | ModelInferenceError",
    "message": "Human-readable diagnostic description",
    "details": {},
    "timestamp": "2026-10-13T02:53:02Z"
  }
  ```
- HTTP status codes:
  - `400 Bad Request`: Unresolvable clinical term or unrecognized state code.
  - `404 Not Found`: Entity primary key missing from the graph database.
  - `502 Bad Gateway`: Hugging Face model endpoint failure or upstream timeout.
  - `500 Internal Server Error`: Graph invariant violation (`GraphValidationError`).
