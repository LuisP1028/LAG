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
    """Graph entity node across the 17 canonical 8-hop knowledge graph categories."""
    primary_key: str = Field(..., description="Deterministic composite primary key")
    label: str = Field(..., description="Canonical entity category label (1 of 17 8-hop categories)")
    name: str = Field(..., description="Human-readable display name derived from persisted properties")
    properties: Dict[str, Any] = Field(default_factory=dict, description="Full persisted attribute dictionary")


class TopologyEdge(BaseModel):
    """Directed relationship across the 18 canonical 8-hop relationship types with provenance."""
    source_pk: str = Field(..., description="Primary key of source entity")
    target_pk: str = Field(..., description="Primary key of target entity")
    label: str = Field(..., description="Canonical relationship type (1 of 18 8-hop relationship types)")
    edge_key: str = Field(..., description="Composite edge identifier source_pk->label->target_pk")
    provenance: Dict[str, Any] = Field(default_factory=dict, description="Persisted provenance metadata (source_uri, selector, ingestion_timestamp, run_id)")


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
