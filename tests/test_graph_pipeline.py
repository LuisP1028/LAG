"""
Automated Verification Suite for Policy Knowledge Graph Pipeline.

Tests all acceptance criteria, system invariants, foreign-key handoffs,
relational geographic unpivoting, and coverage policy bridge semantics.
"""

import os
import pytest
from src.graph.models import (
    PolicyNode,
    HCPCSCodeNode,
    ICD10CodeNode,
    JurisdictionNode,
    StateNode,
    FeeScheduleEntryNode,
    CoveragePolicyNode,
    EdgeProvenance,
    GraphEdge,
)
from src.graph.engine import PropertyGraphEngine, DirectedPropertyGraph, GraphValidationError

ASSET_DIR = "CoveragePolicies_and_Jurisdictions Addition/assets/20261012T231057-024-zqga"


@pytest.fixture(scope="module")
def graph():
    """Runs the pipeline once for the module and returns the constructed graph."""
    engine = PropertyGraphEngine(asset_dir=ASSET_DIR)
    return engine.run_pipeline(keyword="LTA", run_id="test-run-verification")


def test_root_policy_anchor(graph):
    """Verifies that the root Policy node is instantiated with execution metadata."""
    assert "POLICY-LTA" in graph.nodes
    policy = graph.nodes["POLICY-LTA"]
    assert isinstance(policy, PolicyNode)
    assert policy.keyword == "LTA"
    assert policy.run_id == "test-run-verification"
    assert policy.timestamp != ""


def test_statutory_and_regulatory_lineage(graph):
    """Verifies statutory codification and regulatory rulemaking handoff chain."""
    assert "PLAW-117-328" in graph.nodes
    assert "USC-42-1395x-s-2-JJ" in graph.nodes
    assert "FR-2023-24455" in graph.nodes
    assert "CMS-CR-13286" in graph.nodes

    # Check edges
    edge_keys = {(e.source_pk, e.label, e.target_pk) for e in graph.edges}
    assert ("PLAW-117-328", "MODIFIES_CODE", "USC-42-1395x-s-2-JJ") in edge_keys
    assert ("USC-42-1395x-s-2-JJ", "IMPLEMENTED_BY", "FR-2023-24455") in edge_keys
    assert ("FR-2023-24455", "ISSUES_TRANSMITTAL", "CMS-CR-13286") in edge_keys


def test_coverage_policy_bridge(graph):
    """Verifies the mandatory CoveragePolicy bridge and prohibition of direct code-to-diagnosis links."""
    assert "CMS-MCD-A59508" in graph.nodes
    cov_node = graph.nodes["CMS-MCD-A59508"]
    assert isinstance(cov_node, CoveragePolicyNode)
    assert cov_node.article_id == "A59508"

    edge_keys = {(e.source_pk, e.label, e.target_pk) for e in graph.edges}
    assert ("CMS-CR-13286", "MANDATES_POLICY", "CMS-MCD-A59508") in edge_keys

    # Policy governs procedure codes
    assert ("CMS-MCD-A59508", "GOVERNS", "HCPCS-A6583") in edge_keys
    assert ("CMS-MCD-A59508", "ALLOWS_DIAGNOSIS", "ICD10-I97.2") in edge_keys
    assert ("CMS-MCD-A59508", "ALLOWS_DIAGNOSIS", "ICD10-I89.0") in edge_keys

    # Zero direct edges between any HCPCS and ICD10
    for e in graph.edges:
        assert not (e.source_pk.startswith("HCPCS-") and e.target_pk.startswith("ICD10-")), (
            f"Forbidden direct edge found: {e.source_pk} -> {e.target_pk}"
        )


def test_direct_hcpcs_to_icd10_prohibition_raises_error():
    """Asserts that attempting to construct a direct HCPCS->ICD10 edge immediately raises an error."""
    prov = EdgeProvenance(
        source_uri="test",
        selector="test",
        ingestion_timestamp="2026-10-12T00:00:00Z",
        run_id="test",
    )
    with pytest.raises(ValueError, match="Direct edge between HCPCSCode and ICD10Code is strictly prohibited"):
        GraphEdge(
            source_pk="HCPCS-A6583",
            label="REQUIRES_DIAGNOSIS",
            target_pk="ICD10-I97.2",
            provenance=prov,
        )


def test_50_state_and_jurisdiction_completeness(graph):
    """Verifies 4 DME MAC Jurisdictions, all states, and unpivoted fee schedule entries."""
    jurisdictions = [n for n in graph.nodes.values() if isinstance(n, JurisdictionNode)]
    assert len(jurisdictions) == 4
    juris_pks = {j.primary_key for j in jurisdictions}
    assert juris_pks == {"JURIS-DME-A", "JURIS-DME-B", "JURIS-DME-C", "JURIS-DME-D"}

    states = [n for n in graph.nodes.values() if isinstance(n, StateNode)]
    assert len(states) in (53, 54)
    state_codes = {s.state_code for s in states}
    assert "WY" in state_codes
    assert "CA" in state_codes
    assert "NY" in state_codes
    assert "PR" in state_codes
    assert "VI" in state_codes

    fee_entries = [n for n in graph.nodes.values() if isinstance(n, FeeScheduleEntryNode)]
    assert len(fee_entries) > 3000

    # Verify Wyoming fee entry for A6583
    wy_fees = [f for f in fee_entries if f.hcpcs_code == "A6583" and f.state_code == "WY"]
    assert len(wy_fees) >= 1
    wy_nr = [f for f in wy_fees if not f.is_rural][0]
    assert wy_nr.fee_amount == 151.38


def test_edge_provenance_completeness(graph):
    """Verifies that 100% of edges have non-empty provenance metadata."""
    assert len(graph.edges) > 5000
    for edge in graph.edges:
        prov = edge.provenance
        assert prov.source_uri != ""
        assert prov.selector != ""
        assert prov.ingestion_timestamp != ""
        assert prov.run_id != ""


def test_unbroken_ancestry_invariant(graph):
    """Verifies that every single node in the graph is reachable from POLICY-LTA."""
    root_pk = "POLICY-LTA"
    from collections import deque
    visited = set()
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
    assert len(unreachable) == 0, f"Unreachable orphan nodes: {unreachable}"


def test_idempotent_upserts():
    """Verifies that re-running ingestion or upserting identical nodes/edges is idempotent."""
    engine = PropertyGraphEngine(asset_dir=ASSET_DIR)
    g1 = engine.run_pipeline(keyword="LTA", run_id="run-idempotency-1")
    count_nodes_1 = len(g1.nodes)
    count_edges_1 = len(g1.edges)

    # Upsert again into same graph
    policy = g1.nodes["POLICY-LTA"]
    g1.upsert_node(policy)
    assert len(g1.nodes) == count_nodes_1

    edge = g1.edges[0]
    g1.upsert_edge(edge)
    assert len(g1.edges) == count_edges_1


def test_ivig_pipeline_execution_and_invariants():
    """Verifies end-to-end pipeline execution and system invariants for IVIG policy keyword."""
    from src.graph.tier1_legislative import Phase1DiscoveryError

    engine = PropertyGraphEngine(asset_dir=ASSET_DIR)
    g_ivig = engine.run_pipeline(keyword="IVIG", run_id="test-ivig-verification")

    # Verify Root Policy Anchor
    assert "POLICY-IVIG" in g_ivig.nodes
    policy = g_ivig.nodes["POLICY-IVIG"]
    assert policy.keyword == "IVIG"

    # Verify Lineage Handoffs
    assert "BILL-117-hr-3808" in g_ivig.nodes
    assert "PLAW-117-328" in g_ivig.nodes
    assert "USC-42-1395x-s-2-Z" in g_ivig.nodes
    assert "FR-2023-24455" in g_ivig.nodes
    assert "CMS-CR-13217" in g_ivig.nodes
    assert "CMS-MCD-A59588" in g_ivig.nodes
    assert "HCPCS-Q2052" in g_ivig.nodes
    assert "ICD10-D80.0" in g_ivig.nodes

    # Verify Geographic Completeness (INV-50-STATE-COMPLETENESS)
    jurisdictions = [n for n in g_ivig.nodes.values() if isinstance(n, JurisdictionNode)]
    assert len(jurisdictions) == 4
    states = [n for n in g_ivig.nodes.values() if isinstance(n, StateNode)]
    assert len(states) in (53, 54)
    fee_entries = [n for n in g_ivig.nodes.values() if isinstance(n, FeeScheduleEntryNode)]
    assert len(fee_entries) > 0
    assert any(f.hcpcs_code == "Q2052" and f.state_code == "WY" for f in fee_entries)

    # Verify No Direct HCPCS->ICD10 Edges (INV-NO-KEYWORD-BRIDGING)
    for e in g_ivig.edges:
        assert not (e.source_pk.startswith("HCPCS-") and e.target_pk.startswith("ICD10-"))

    # Verify Unbroken Ancestry from POLICY-IVIG (INV-UNBROKEN-ANCESTRY)
    from collections import deque
    root_pk = "POLICY-IVIG"
    visited = set()
    queue = deque([root_pk])
    visited.add(root_pk)
    while queue:
        curr = queue.popleft()
        for edge in g_ivig._adj.get(curr, []):
            nxt = edge.target_pk
            if nxt not in visited:
                visited.add(nxt)
                queue.append(nxt)
    unreachable = set(g_ivig.nodes.keys()) - visited
    assert len(unreachable) == 0

    # Fail-fast on unsupported keyword (INV-FAIL-FAST)
    with pytest.raises(Phase1DiscoveryError):
        engine.run_pipeline(keyword="UNKNOWN_NONEXISTENT_KEYWORD")


def test_neo4j_sync_and_mcp_invariants():
    """Verifies that the policy graphs synchronize into Neo4j with 100% invariant compliance."""
    from src.graph.neo4j_sync import Neo4jSyncEngine

    sync_engine = Neo4jSyncEngine()
    try:
        driver = sync_engine.get_driver()
        driver.verify_connectivity()
    except Exception as e:
        pytest.skip(f"Neo4j instance not reachable: {e}")

    try:
        # Sync IVIG graph
        ivig_stats = sync_engine.sync_file("exports/ivig_knowledge_graph.json")
        assert ivig_stats["nodes_synced"] == 183
        assert ivig_stats["edges_synced"] == 289

        # Verify summary statistics and invariants in Neo4j
        summary = sync_engine.get_summary_statistics()
        assert summary["total_nodes"] >= 183
        assert summary["total_edges"] >= 289

        with sync_engine.get_driver().session(database=sync_engine.database) as session:
            # Invariant: INV-NO-KEYWORD-BRIDGING (Zero direct HCPCS->ICD10 edges)
            illegal_res = session.run("MATCH (h:HCPCSCode)-[r]-(i:ICD10Code) RETURN count(r) AS illegal").single()
            assert illegal_res["illegal"] == 0

            # Invariant: INV-50-STATE-COMPLETENESS (All 4 DME MAC Jurisdictions present)
            juris_res = session.run("MATCH (j:Jurisdiction) RETURN count(j) AS cnt").single()
            assert juris_res["cnt"] == 4

            # Invariant: INV-PROVENANCE-COMPLETENESS (Zero edges missing provenance)
            prov_res = session.run(
                "MATCH ()-[r]->() WHERE r.source_uri IS NULL OR r.selector IS NULL "
                "OR r.ingestion_timestamp IS NULL OR r.run_id IS NULL RETURN count(r) AS cnt"
            ).single()
            assert prov_res["cnt"] == 0
    finally:
        sync_engine.close()

