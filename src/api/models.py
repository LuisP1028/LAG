"""API schemas and models for the LAG GraphRAG visualizer backend."""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from src.graphrag.models import AnchorEntity, GraphRAGQueryRequest, GraphRAGQueryResponse


class HealthResponse(BaseModel):
    status: str = "ok"
    neo4j_connected: bool = True
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class TopologyNode(BaseModel):
    primary_key: str
    label: str
    name: str
    properties: Dict[str, Any] = Field(default_factory=dict)


class TopologyEdge(BaseModel):
    source_pk: str
    target_pk: str
    label: str
    edge_key: str
    provenance: Dict[str, Any] = Field(default_factory=dict)


class TopologyResponse(BaseModel):
    nodes: List[TopologyNode]
    edges: List[TopologyEdge]
    total_nodes: int
    total_edges: int


class EntityResolveRequest(BaseModel):
    query: str


class EntityResolveResponse(BaseModel):
    anchors: List[AnchorEntity]


class SubgraphRequest(BaseModel):
    anchors: List[str]  # Primary keys


class SubgraphResponse(BaseModel):
    nodes: List[TopologyNode]
    edges: List[TopologyEdge]
    active_node_pks: List[str]
    active_edge_keys: List[str]
    retrieval_ms: float


class ErrorEnvelope(BaseModel):
    error: bool = True
    error_type: str
    message: str
    details: Dict[str, Any] = Field(default_factory=dict)
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
