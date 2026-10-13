"""Complete GraphRAG pipeline orchestrating entity resolution, traversal, assembly, and synthesis."""

import time
from typing import Any, Dict, List, Optional
from neo4j import Session

from src.graphrag.context_assembler import GraphContextAssembler
from src.graphrag.entity_linker import EntityAnchorLinker
from src.graphrag.models import (
    AnchorEntity,
    GraphRAGQueryRequest,
    GraphRAGQueryResponse,
    ResolvedAnchors,
    TraversalResult,
)
from src.graphrag.synthesizer import HuggingFaceSynthesizer
from src.graphrag.traversal import TopologicalTraversalEngine


class GraphRAGPipeline:
    """End-to-end GraphRAG pipeline integrating Neo4j knowledge graph and Hugging Face models."""

    def __init__(
        self,
        linker: Optional[EntityAnchorLinker] = None,
        traverser: Optional[TopologicalTraversalEngine] = None,
        assembler: Optional[GraphContextAssembler] = None,
        synthesizer: Optional[HuggingFaceSynthesizer] = None,
    ):
        self.linker = linker or EntityAnchorLinker()
        self.traverser = traverser or TopologicalTraversalEngine()
        self.assembler = assembler or GraphContextAssembler()
        self.synthesizer = synthesizer or HuggingFaceSynthesizer()

    def execute_query(
        self,
        request: GraphRAGQueryRequest,
        session: Session,
    ) -> GraphRAGQueryResponse:
        """Executes the full 5-stage GraphRAG pipeline and returns synthesized guidance and canvas telemetry."""
        start_time = time.perf_counter()

        # Stage 1: Entity Anchor Linking
        anchors: ResolvedAnchors = self.linker.resolve_anchors(request.query, session)

        # Stage 2: Topological Subgraph Expansion
        traversal_result: TraversalResult = self.traverser.extract_connecting_subgraph(
            anchors=anchors,
            session=session,
        )

        # Determine active state code for context assembly
        state_code = "WI"
        if anchors.state_anchor:
            state_code = anchors.state_anchor.primary_key.replace("STATE-", "")
        elif request.state_code:
            state_code = request.state_code

        # Stage 3: Structured Context Assembly
        context_markdown: str = self.assembler.assemble_context(
            traversal_result=traversal_result,
            state_code=state_code,
        )

        # Stage 4 & 5: LLM Synthesis with Anti-Hallucination Guardrail
        answer_text: str = self.synthesizer.synthesize(
            query=request.query,
            context=context_markdown,
            model_id=request.model_id,
        )

        # Collect unique provenance records from traversed edges
        provenance_sources: List[Dict[str, Any]] = []
        seen_uris = set()
        for edge in traversal_result.edges:
            prov = edge.provenance
            uri = prov.get("source_uri")
            if uri and uri not in seen_uris:
                seen_uris.add(uri)
                provenance_sources.append(prov)

        elapsed_ms = (time.perf_counter() - start_time) * 1000.0

        return GraphRAGQueryResponse(
            answer=answer_text,
            active_node_pks=traversal_result.active_node_pks,
            active_edge_keys=traversal_result.active_edge_keys,
            anchors=anchors.all_anchors,
            provenance_sources=provenance_sources,
            duration_ms=round(elapsed_ms, 2),
        )
