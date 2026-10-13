"""
Graph Storage Engine & Invariant Validator (COMP-08).

Assembles the directed property graph across all five tiers, enforces MERGE
upsert semantics on deterministic primary keys, validates system invariants,
and exports the graph into structured JSON/JSON-LD.
"""

from __future__ import annotations
import json
from collections import deque
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Set

from src.graph.models import (
    BaseNode,
    PolicyNode,
    BillNode,
    PublicLawNode,
    StatutorySectionNode,
    RegulationNode,
    ChangeRequestNode,
    CoveragePolicyNode,
    JurisdictionNode,
    StateNode,
    FeeScheduleEntryNode,
    HCPCSCodeNode,
    ICD10CodeNode,
    LobbyingFilingNode,
    CBOScoreNode,
    LiteratureStudyNode,
    GraphEdge,
)
from src.graph.tier1_legislative import discover_legislation
from src.graph.tier2_statutory import parse_statutory_codification
from src.graph.tier3_regulatory import harvest_regulations
from src.graph.tier4a_coverage import ingest_coverage_policy
from src.graph.tier4b_fee_schedule import normalize_fee_schedules
from src.graph.tier5_context import enrich_context


class GraphValidationError(Exception):
    """Raised when the constructed graph violates system invariants."""
    pass


class DirectedPropertyGraph:
    """Directed property graph representation storing typed vertices and edges."""

    def __init__(self):
        self.nodes: Dict[str, BaseNode] = {}
        self.edges: List[GraphEdge] = []
        self._edge_keys: Set[str] = set()
        self._adj: Dict[str, List[GraphEdge]] = {}

    def upsert_node(self, node: BaseNode) -> None:
        """Idempotent node upsert by deterministic primary key (MERGE semantics)."""
        if not node.primary_key:
            raise GraphValidationError(f"Node of type {type(node)} has empty primary key.")
        self.nodes[node.primary_key] = node
        if node.primary_key not in self._adj:
            self._adj[node.primary_key] = []

    def upsert_edge(self, edge: GraphEdge) -> None:
        """Idempotent edge insertion with provenance validation."""
        # Validate that both endpoints exist
        if edge.source_pk not in self.nodes:
            raise GraphValidationError(f"Edge source node {edge.source_pk} does not exist in graph.")
        if edge.target_pk not in self.nodes:
            raise GraphValidationError(f"Edge target node {edge.target_pk} does not exist in graph.")

        edge_key = f"{edge.source_pk}->{edge.label}->{edge.target_pk}"
        if edge_key in self._edge_keys:
            return  # Idempotent skip for duplicate edge

        self._edge_keys.add(edge_key)
        self.edges.append(edge)
        self._adj[edge.source_pk].append(edge)

    def to_dict(self) -> Dict[str, Any]:
        """Serializes the graph into a dictionary for JSON output."""
        return {
            "node_count": len(self.nodes),
            "edge_count": len(self.edges),
            "nodes": [n.model_dump() for n in self.nodes.values()],
            "edges": [e.model_dump() for e in self.edges],
        }

    def export_json(self, filepath: str) -> None:
        """Exports the graph to a JSON file."""
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2)


class PropertyGraphEngine:
    """Orchestrates end-to-end knowledge graph ingestion and validates invariants."""

    def __init__(self, asset_dir: Optional[str] = None):
        self.asset_dir = asset_dir

    def run_pipeline(self, keyword: str, run_id: Optional[str] = None) -> DirectedPropertyGraph:
        """
        Executes all five dependent stages and compiles the final directed property graph.
        """
        if not run_id:
            run_id = f"run-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"

        graph = DirectedPropertyGraph()

        # Tier 1: Legislative Genesis
        policy_node, bill_nodes, plaw_node, tier1_edges, tier1_handoff = discover_legislation(
            keyword=keyword, run_id=run_id, asset_dir=self.asset_dir
        )
        graph.upsert_node(policy_node)
        for b in bill_nodes:
            graph.upsert_node(b)
        graph.upsert_node(plaw_node)
        for e in tier1_edges:
            graph.upsert_edge(e)

        # Tier 2: Statutory Codification
        statutory_node, tier2_edges, tier2_handoff = parse_statutory_codification(
            handoff=tier1_handoff, public_law_node=plaw_node, run_id=run_id, asset_dir=self.asset_dir
        )
        graph.upsert_node(statutory_node)
        for e in tier2_edges:
            graph.upsert_edge(e)

        # Tier 3: Regulatory Rulemaking
        regulation_node, cr_node, tier3_edges, tier3_handoff = harvest_regulations(
            handoff=tier2_handoff, statutory_node=statutory_node, run_id=run_id, asset_dir=self.asset_dir
        )
        graph.upsert_node(regulation_node)
        graph.upsert_node(cr_node)
        for e in tier3_edges:
            graph.upsert_edge(e)

        # Tier 4A: Coverage Policy Bridge
        coverage_policy_node, hcpcs_nodes, icd10_nodes, tier4a_edges = ingest_coverage_policy(
            handoff=tier3_handoff, change_request_node=cr_node, run_id=run_id, asset_dir=self.asset_dir
        )
        graph.upsert_node(coverage_policy_node)
        for h in hcpcs_nodes:
            graph.upsert_node(h)
        for i in icd10_nodes:
            graph.upsert_node(i)
        for e in tier4a_edges:
            graph.upsert_edge(e)

        # Tier 4B: Geographic Fee Schedule Normalization
        juris_nodes, state_nodes, fee_nodes, tier4b_edges = normalize_fee_schedules(
            handoff=tier3_handoff,
            change_request_node=cr_node,
            hcpcs_nodes=hcpcs_nodes,
            run_id=run_id,
            asset_dir=self.asset_dir,
        )
        for j in juris_nodes:
            graph.upsert_node(j)
        for s in state_nodes:
            graph.upsert_node(s)
        for f in fee_nodes:
            graph.upsert_node(f)
        for e in tier4b_edges:
            graph.upsert_edge(e)

        # Tier 5: Contextual Enrichment
        filing_nodes, cbo_nodes, study_nodes, tier5_edges = enrich_context(
            target_bills=bill_nodes,
            regulation_node=regulation_node,
            clinical_citations=tier3_handoff.clinical_citations,
            run_id=run_id,
            asset_dir=self.asset_dir,
        )
        for fil in filing_nodes:
            graph.upsert_node(fil)
        for c in cbo_nodes:
            graph.upsert_node(c)
        for st in study_nodes:
            graph.upsert_node(st)
        for e in tier5_edges:
            graph.upsert_edge(e)

        # Invariant Verification Gate
        self.validate_invariants(graph=graph, keyword=keyword)

        return graph

    def validate_invariants(self, graph: DirectedPropertyGraph, keyword: str) -> None:
        """
        Validates all five system invariants across the completed property graph.
        """
        root_pk = f"POLICY-{keyword.strip().upper()}"
        if root_pk not in graph.nodes:
            raise GraphValidationError(f"Root policy node {root_pk} is missing from the graph.")

        # Invariant 1: 100% Edge Provenance Completeness
        for edge in graph.edges:
            prov = edge.provenance
            if not prov.source_uri or not prov.selector or not prov.ingestion_timestamp or not prov.run_id:
                raise GraphValidationError(
                    f"Edge ({edge.source_pk})-[:{edge.label}]->({edge.target_pk}) has incomplete provenance."
                )

        # Invariant 2: Zero Direct HCPCS -> ICD10 Edges (INV-NO-KEYWORD-BRIDGING)
        for edge in graph.edges:
            if edge.source_pk.startswith("HCPCS-") and edge.target_pk.startswith("ICD10-"):
                raise GraphValidationError(
                    f"INV-NO-KEYWORD-BRIDGING VIOLATION: Direct edge ({edge.source_pk})-[:{edge.label}]->({edge.target_pk}) found!"
                )

        # Invariant 3: 50-State Geographic Completeness (INV-50-STATE-COMPLETENESS)
        jurisdictions = [n for n in graph.nodes.values() if isinstance(n, JurisdictionNode)]
        if len(jurisdictions) != 4:
            raise GraphValidationError(f"Expected exactly 4 DME MAC Jurisdictions, found {len(jurisdictions)}")

        states = [n for n in graph.nodes.values() if isinstance(n, StateNode)]
        if len(states) not in (53, 54):
            raise GraphValidationError(
                f"INV-50-STATE-COMPLETENESS VIOLATION: Expected 53 or 54 states/territories (50 states + DC + PR + VI), found {len(states)}"
            )

        fee_entries = [n for n in graph.nodes.values() if isinstance(n, FeeScheduleEntryNode)]
        if len(fee_entries) == 0:
            raise GraphValidationError("INV-50-STATE-COMPLETENESS VIOLATION: Zero FeeScheduleEntry records found.")

        # Invariant 4: Unbroken Ancestry & Graph Reachability (INV-UNBROKEN-ANCESTRY)
        # Verify directed reachability from POLICY root to all nodes
        visited: Set[str] = set()
        queue = deque([root_pk])
        visited.add(root_pk)

        while queue:
            curr = queue.popleft()
            for edge in graph._adj.get(curr, []):
                nxt = edge.target_pk
                if nxt not in visited:
                    visited.add(nxt)
                    queue.append(nxt)

        unreachable = set(graph.nodes.keys()) - visited
        if unreachable:
            raise GraphValidationError(
                f"INV-UNBROKEN-ANCESTRY VIOLATION: {len(unreachable)} orphan nodes detected: {list(unreachable)[:5]}"
            )
