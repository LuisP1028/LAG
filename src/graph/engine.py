"""
Graph Storage Engine & Invariant Validator (COMP-08).

Assembles the directed property graph across all eight hops (Hops 0–7) and
contextual enrichment (Tier 5), enforces MERGE upsert semantics on deterministic
primary keys, validates all topological and fail-fast invariants specified in
functional_specification_014.md, and exports the graph into structured JSON.
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
    USCSectionNode,
    RegulationNode,
    CFRSectionNode,
    ChangeRequestNode,
    TransmittalNode,
    CoveragePolicyNode,
    JurisdictionNode,
    StateNode,
    FeeScheduleEntryNode,
    FeeScheduleRateNode,
    HCPCSCodeNode,
    ProcedureCodeNode,
    ICD10CodeNode,
    DiagnosisCodeNode,
    LobbyingFilingNode,
    CBOScoreNode,
    LiteratureStudyNode,
    GraphEdge,
    LegislativeHandoff,
    StatutoryHandoff,
    RegulatoryHandoff,
    OperationalHandoff,
    CoverageHandoff,
    CodingHandoff,
    ReimbursementHandoff,
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
    """Directed property graph representation storing typed vertices, edges, and hop handoffs."""

    def __init__(self):
        self.nodes: Dict[str, BaseNode] = {}
        self.edges: List[GraphEdge] = []
        self._edge_keys: Set[str] = set()
        self._adj: Dict[str, List[GraphEdge]] = {}
        self.handoffs: Dict[str, Any] = {}

    def upsert_node(self, node: BaseNode) -> None:
        """Idempotent node upsert by deterministic primary key (MERGE semantics)."""
        if not node.primary_key:
            raise GraphValidationError(f"Node of type {type(node)} has empty primary key.")
        self.nodes[node.primary_key] = node
        if node.primary_key not in self._adj:
            self._adj[node.primary_key] = []

    def upsert_edge(self, edge: GraphEdge) -> None:
        """Idempotent edge insertion with provenance validation."""
        if edge.source_pk not in self.nodes:
            raise GraphValidationError(f"Edge source node {edge.source_pk} does not exist in graph.")
        if edge.target_pk not in self.nodes:
            raise GraphValidationError(f"Edge target node {edge.target_pk} does not exist in graph.")

        edge_key = f"{edge.source_pk}->{edge.label}->{edge.target_pk}"
        if edge_key in self._edge_keys:
            return

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
    """Orchestrates end-to-end 8-hop knowledge graph traversal and validates invariants."""

    def __init__(self, asset_dir: Optional[str] = None):
        self.asset_dir = asset_dir

    def run_pipeline(self, keyword: str, run_id: Optional[str] = None) -> DirectedPropertyGraph:
        """
        Executes all 8 dependent hops (Hops 0–7) plus contextual enrichment (Tier 5)
        and compiles the final directed property graph.
        """
        if not run_id:
            run_id = f"run-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"

        graph = DirectedPropertyGraph()

        # Hop 0 & Hop 1: Legislative Discovery & Omnibus Resolution
        policy_node, bill_nodes, plaw_node, tier1_edges, leg_handoff = discover_legislation(
            keyword=keyword, run_id=run_id, asset_dir=self.asset_dir
        )
        graph.handoffs["legislative"] = leg_handoff
        graph.upsert_node(policy_node)
        for b in bill_nodes:
            graph.upsert_node(b)
        graph.upsert_node(plaw_node)
        for e in tier1_edges:
            graph.upsert_edge(e)

        # Hop 2: Statutory Codification & USLM XML Section Extraction
        bill_titles = [b.title for b in bill_nodes]
        statutory_node, usc_nodes, tier2_edges, stat_handoff = parse_statutory_codification(
            handoff=leg_handoff,
            public_law_node=plaw_node,
            run_id=run_id,
            asset_dir=self.asset_dir,
            bill_titles=bill_titles,
        )
        graph.handoffs["statutory"] = stat_handoff
        graph.upsert_node(statutory_node)
        for u in usc_nodes:
            graph.upsert_node(u)
        for e in tier2_edges:
            graph.upsert_edge(e)

        # Hop 3 & Hop 4: Federal Register Final Rule & CMS Transmittal Harvesting
        regulation_node, cfr_nodes, transmittal_node, tier3_edges, reg_handoff, op_handoff = harvest_regulations(
            handoff=stat_handoff,
            statutory_node=statutory_node,
            run_id=run_id,
            asset_dir=self.asset_dir,
            usc_nodes=usc_nodes,
        )
        graph.handoffs["regulatory"] = reg_handoff
        graph.handoffs["operational"] = op_handoff
        graph.upsert_node(regulation_node)
        for cfr in cfr_nodes:
            graph.upsert_node(cfr)
        graph.upsert_node(transmittal_node)
        for e in tier3_edges:
            graph.upsert_edge(e)

        # Hop 5 & Hop 6: Clinical Coverage Guidance & Operational-Filtered HCPCS Extraction
        coverage_policy_node, hcpcs_nodes, icd10_nodes, tier4a_edges, cov_handoff, coding_handoff = ingest_coverage_policy(
            handoff=op_handoff,
            change_request_node=transmittal_node,
            run_id=run_id,
            asset_dir=self.asset_dir,
            statutory_handoff=stat_handoff,
        )
        graph.handoffs["coverage"] = cov_handoff
        graph.handoffs["coding"] = coding_handoff
        graph.upsert_node(coverage_policy_node)
        for h in hcpcs_nodes:
            graph.upsert_node(h)
        for i in icd10_nodes:
            graph.upsert_node(i)
        for e in tier4a_edges:
            graph.upsert_edge(e)

        # Hop 7: 54-Jurisdiction Fee Schedule Unpivoting & Rate Reconciliation
        juris_nodes, state_nodes, fee_nodes, tier4b_edges, reimb_handoff = normalize_fee_schedules(
            handoff=op_handoff,
            change_request_node=transmittal_node,
            hcpcs_nodes=hcpcs_nodes,
            run_id=run_id,
            asset_dir=self.asset_dir,
            coding_handoff=coding_handoff,
        )
        graph.handoffs["reimbursement"] = reimb_handoff
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
            clinical_citations=None,
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
        Validates all topological and data-contract invariants across the completed property graph.
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

        # Invariant 2: Omnibus vs. Direct Enactment Linear Topology (§3 Rule 2)
        leg_handoff: Optional[LegislativeHandoff] = graph.handoffs.get("legislative")
        if leg_handoff and leg_handoff.introduced_bill_id != leg_handoff.enacting_bill_id:
            for edge in graph.edges:
                if edge.source_pk == leg_handoff.introduced_bill_id and edge.target_pk == leg_handoff.public_law_id:
                    raise GraphValidationError(
                        f"OMNIBUS TOPOLOGY VIOLATION: Direct shortcut edge from introduced bill "
                        f"{leg_handoff.introduced_bill_id} to {leg_handoff.public_law_id} is forbidden when "
                        f"incorporated into omnibus vehicle {leg_handoff.enacting_bill_id}."
                    )

        # Invariant 3: Zero Direct HCPCS -> ICD10 Edges (INV-NO-KEYWORD-BRIDGING)
        for edge in graph.edges:
            if edge.source_pk.startswith("HCPCS-") and edge.target_pk.startswith("ICD10-"):
                raise GraphValidationError(
                    f"INV-NO-KEYWORD-BRIDGING VIOLATION: Direct edge ({edge.source_pk})-[:{edge.label}]->({edge.target_pk}) found!"
                )

        # Invariant 4: 54-Jurisdiction Geographic Completeness (INV-50-STATE-COMPLETENESS)
        jurisdictions = [n for n in graph.nodes.values() if isinstance(n, JurisdictionNode)]
        if len(jurisdictions) != 4:
            raise GraphValidationError(f"Expected exactly 4 DME MAC Jurisdictions, found {len(jurisdictions)}")

        states = [n for n in graph.nodes.values() if isinstance(n, StateNode)]
        if len(states) != 54:
            raise GraphValidationError(
                f"INV-50-STATE-COMPLETENESS VIOLATION: Expected 54 jurisdictions (50 states + DC + PR + VI + GU), found {len(states)}"
            )

        fee_entries = [n for n in graph.nodes.values() if isinstance(n, FeeScheduleEntryNode)]
        if len(fee_entries) == 0:
            raise GraphValidationError("INV-50-STATE-COMPLETENESS VIOLATION: Zero FeeScheduleRate records found.")

        # Invariant 5: Unbroken Ancestry & Graph Reachability (INV-UNBROKEN-ANCESTRY)
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
