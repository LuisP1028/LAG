"""Data models for the GraphRAG pipeline and visualization synchronization."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class AnchorEntity(BaseModel):
    """A resolved entity anchor linking user query terms to a knowledge graph entity."""
    slot: str  # "state" | "diagnosis" | "policy" | "hcpcs" | "jurisdiction"
    primary_key: str
    matched_text: str
    entity_type: str
    label: str


class ResolvedAnchors(BaseModel):
    """Collection of resolved entity anchors across semantic slots."""
    state_anchor: Optional[AnchorEntity] = None
    diagnosis_anchor: Optional[AnchorEntity] = None
    policy_anchor: Optional[AnchorEntity] = None
    all_anchors: List[AnchorEntity] = Field(default_factory=list)


class TraversalNode(BaseModel):
    """Graph node extracted during topological subgraph expansion."""
    primary_key: str
    label: str
    name: str
    properties: Dict[str, Any] = Field(default_factory=dict)


class TraversalEdge(BaseModel):
    """Directed relationship extracted during topological subgraph expansion."""
    source_pk: str
    target_pk: str
    label: str
    edge_key: str
    provenance: Dict[str, Any] = Field(default_factory=dict)


class TraversalResult(BaseModel):
    """Result of generalized topological subgraph retrieval."""
    nodes: List[TraversalNode] = Field(default_factory=list)
    edges: List[TraversalEdge] = Field(default_factory=list)
    active_node_pks: List[str] = Field(default_factory=list)
    active_edge_keys: List[str] = Field(default_factory=list)
    retrieval_ms: float = 0.0


class GraphRAGQueryRequest(BaseModel):
    """Request payload for conversational GraphRAG synthesis."""
    query: str
    model_id: Optional[str] = "meta-llama/Meta-Llama-3-8B-Instruct"
    state_code: Optional[str] = None


class GraphRAGQueryResponse(BaseModel):
    """Response payload containing synthesized answer and visual illumination metadata."""
    answer: str
    active_node_pks: List[str]
    active_edge_keys: List[str]
    anchors: List[AnchorEntity]
    provenance_sources: List[Dict[str, Any]]
    duration_ms: float
