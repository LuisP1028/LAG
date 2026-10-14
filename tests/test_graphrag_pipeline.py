"""Verification suite validating the 5-stage GraphRAG pipeline against all 6 authoritative oracles across the 8-hop ontology."""

import time
import pytest
from src.graph.neo4j_sync import Neo4jSyncEngine
from src.graphrag.entity_linker import EntityAnchorLinker
from src.graphrag.exceptions import EntityResolutionError
from src.graphrag.models import GraphRAGQueryRequest
from src.graphrag.pipeline import GraphRAGPipeline
from src.graphrag.traversal import TopologicalTraversalEngine


@pytest.fixture(scope="module")
def neo4j_engine():
    engine = Neo4jSyncEngine()
    engine.init_schema()
    yield engine
    engine.close()


def test_oracle_1_patient_benefit_routing(neo4j_engine):
    """Oracle 1: Natural Language Patient Benefit Routing (Workflow 1)."""
    linker = EntityAnchorLinker()
    traverser = TopologicalTraversalEngine()
    pipeline = GraphRAGPipeline(linker=linker, traverser=traverser)

    query = "I am from Wisconsin, survived breast cancer, need lymphedema supplies, I'm on Medicare, can you help?"

    with neo4j_engine.get_driver().session(database=neo4j_engine.database) as session:
        # 1. Anchor resolution validation
        anchors = linker.resolve_anchors(query, session)
        assert anchors.state_anchor is not None
        assert anchors.state_anchor.primary_key == "STATE-WI"
        assert anchors.diagnosis_anchor is not None
        assert anchors.diagnosis_anchor.primary_key == "ICD10-I97.2"
        assert anchors.policy_anchor is not None
        assert anchors.policy_anchor.primary_key == "POLICY-LTA"

        # 2. Subgraph extraction returns mandatory 8-hop + clinical/rate chain
        t0 = time.perf_counter()
        traversal = traverser.extract_connecting_subgraph(anchors, session)
        retrieval_ms = (time.perf_counter() - t0) * 1000.0
        assert retrieval_ms >= 0

        expected_chain = {
            "STATE-WI",
            "JURIS-DME-B",
            "TR-CR13286",
            "DME-MAC-COPE147943",
            "ICD10-I97.2",
            "HCPCS-A6522",
            "FEE-A6522-WI-NR-2024",
        }
        for pk in expected_chain:
            assert pk in traversal.active_node_pks, f"Mandatory node {pk} missing from active chain"

        # 3. Allowable fee rate for A6522 in Wisconsin equals $290.47, coinsurance equals $58.09
        fee_node = next((n for n in traversal.nodes if n.primary_key == "FEE-A6522-WI-NR-2024"), None)
        assert fee_node is not None
        assert fee_node.properties["fee_amount"] == 290.47
        coinsurance = fee_node.properties["fee_amount"] * 0.20
        assert round(coinsurance, 2) == 58.09

        # 4. Regional claims contractor identified as CGS Administrators (Jurisdiction B)
        juris_node = next((n for n in traversal.nodes if n.primary_key == "JURIS-DME-B"), None)
        assert juris_node is not None
        assert "CGS" in juris_node.name or "CGS" in juris_node.properties.get("contractor_name", "")

        # 5. Full pipeline synthesis check
        req = GraphRAGQueryRequest(query=query)
        resp = pipeline.execute_query(req, session)
        assert "290.47" in resp.answer
        assert "58.09" in resp.answer
        assert "DME-MAC-COPE147943" in resp.answer or "TR-CR13286" in resp.answer
        assert len(resp.active_node_pks) >= 7
        assert len(resp.active_edge_keys) >= 7


def test_oracle_2_no_keyword_bridging(neo4j_engine):
    """Oracle 2: Clinical Coverage & Diagnosis Bridging (INV-NO-KEYWORD-BRIDGING)."""
    with neo4j_engine.get_driver().session(database=neo4j_engine.database) as session:
        # Direct ProcedureCode -> DiagnosisCode edges are strictly forbidden across 100% of the graph
        bad_edges = session.run("MATCH (:ProcedureCode)-[r]->(:DiagnosisCode) RETURN count(r) AS cnt").single()["cnt"]
        assert bad_edges == 0, f"Violated INV-NO-KEYWORD-BRIDGING: Found {bad_edges} direct ProcedureCode->DiagnosisCode edges"

        # Procedure code A6583 must route through CoveragePolicy DME-MAC-COPE147943
        path_check = session.run("""
            MATCH (h:ProcedureCode {primary_key: 'HCPCS-A6583'})<-[:COVERS_PROCEDURE]-(cp:CoveragePolicy)-[:REQUIRES_DIAGNOSIS]->(d:DiagnosisCode)
            RETURN cp.primary_key AS cp_pk, count(d) AS diag_count
        """).single()
        assert path_check is not None
        assert path_check["cp_pk"] == "DME-MAC-COPE147943"
        assert path_check["diag_count"] == 4


def test_oracle_3_omnibus_and_8hop_lineage(neo4j_engine):
    """Oracle 3: 8-Hop Legislative Omnibus Incorporation and Regulatory Lineage."""
    pipeline = GraphRAGPipeline()
    query = "How was H.R. 3630 enacted into Public Law 117-328 and implemented in 88 FR 77676?"

    with neo4j_engine.get_driver().session(database=neo4j_engine.database) as session:
        req = GraphRAGQueryRequest(query=query)
        resp = pipeline.execute_query(req, session)

        expected_lineage = {
            "POLICY-LTA",
            "BILL-117-hr-3630",
            "BILL-117-hr-2617",
            "PLAW-117-328",
            "STAT-117-328-SEC-4133",
            "USC-42-1395x-s-2-JJ",
            "REG-FR-2023-24455",
            "CFR-42-410",
            "TR-CR13286",
            "DME-MAC-COPE147943",
        }
        for pk in expected_lineage:
            assert pk in resp.active_node_pks, f"Missing 8-hop lineage node {pk}"

        assert "117-328" in resp.answer
        assert "88 FR 77676" in resp.answer or "REG-FR-2023-24455" in resp.answer


def test_oracle_4_zero_orphan_invariant(neo4j_engine):
    """Oracle 4: Zero Orphan Invariant (INV-UNBROKEN-ANCESTRY)."""
    from collections import deque

    with neo4j_engine.get_driver().session(database=neo4j_engine.database) as session:
        records = session.run("MATCH (a:PolicyNode)-[r]->(b:PolicyNode) RETURN a.primary_key AS src, b.primary_key AS tgt").data()
        adj = {}
        for r in records:
            adj.setdefault(r["src"], []).append(r["tgt"])
            adj.setdefault(r["tgt"], []).append(r["src"])

        all_nodes = {r["pk"] for r in session.run("MATCH (n:PolicyNode) RETURN n.primary_key AS pk").data()}
        root_nodes = [r["pk"] for r in session.run("MATCH (p:Policy) RETURN p.primary_key AS pk").data()]

        visited = set(root_nodes)
        queue = deque(root_nodes)

        while queue:
            curr = queue.popleft()
            for nxt in adj.get(curr, []):
                if nxt not in visited:
                    visited.add(nxt)
                    queue.append(nxt)

        unreachable = all_nodes - visited
        assert len(unreachable) == 0, f"Violated INV-UNBROKEN-ANCESTRY: Found {len(unreachable)} orphaned nodes: {list(unreachable)[:5]}"


def test_oracle_5_edge_provenance_completeness(neo4j_engine):
    """Oracle 5: Edge Provenance Completeness (INV-PROVENANCE-COMPLETENESS)."""
    traverser = TopologicalTraversalEngine()
    linker = EntityAnchorLinker()

    query = "I am from Wisconsin, survived breast cancer, need lymphedema supplies, I'm on Medicare, can you help?"

    with neo4j_engine.get_driver().session(database=neo4j_engine.database) as session:
        anchors = linker.resolve_anchors(query, session)
        result = traverser.extract_connecting_subgraph(anchors, session)

        assert len(result.edges) > 0
        for edge in result.edges:
            prov = edge.provenance
            assert prov.get("source_uri"), f"Missing source_uri on edge {edge.edge_key}"
            assert prov.get("selector"), f"Missing selector on edge {edge.edge_key}"
            assert prov.get("ingestion_timestamp"), f"Missing ingestion_timestamp on edge {edge.edge_key}"
            assert prov.get("run_id"), f"Missing run_id on edge {edge.edge_key}"


def test_oracle_6_fail_fast_error_boundaries(neo4j_engine):
    """Oracle 6: Fail-Fast Error Boundaries (INV-FAIL-FAST)."""
    linker = EntityAnchorLinker()

    with neo4j_engine.get_driver().session(database=neo4j_engine.database) as session:
        # 1. Unindexed geographic jurisdiction
        with pytest.raises(EntityResolutionError) as exc_info:
            linker.resolve_anchors("I am from Atlantis and need supplies", session)
        assert "Atlantis" in str(exc_info.value)

        # 2. Unindexed medical condition
        with pytest.raises(EntityResolutionError) as exc_info2:
            linker.resolve_anchors("I have diabetes and need Medicare coverage", session)
        assert "diabetes" in str(exc_info2.value)

        # 3. Unindexed explicit PK token
        with pytest.raises(EntityResolutionError) as exc_info3:
            linker.resolve_anchors("What is the rate for HCPCS-99999?", session)
        assert "HCPCS-99999" in str(exc_info3.value)


def test_single_state_query_ny_and_guam(neo4j_engine):
    """Verifies single-state queries for New York (JURIS-DME-A) and Guam (54th jurisdiction, JURIS-DME-D)."""
    linker = EntityAnchorLinker()
    traverser = TopologicalTraversalEngine()
    pipeline = GraphRAGPipeline(linker=linker, traverser=traverser)

    with neo4j_engine.get_driver().session(database=neo4j_engine.database) as session:
        # 1. Query: "What contractor covers New York?"
        query1 = "What contractor covers New York?"
        anchors1 = linker.resolve_anchors(query1, session)
        assert anchors1.state_anchor is not None
        assert anchors1.state_anchor.primary_key == "STATE-NY"

        traversal1 = traverser.extract_connecting_subgraph(anchors1, session)
        expected_pks = {"STATE-NY", "JURIS-DME-A", "TR-CR13286", "DME-MAC-COPE147943"}
        for pk in expected_pks:
            assert pk in traversal1.active_node_pks, f"Mandatory node {pk} missing from New York subgraph"

        juris_node = next((n for n in traversal1.nodes if n.primary_key == "JURIS-DME-A"), None)
        assert juris_node is not None
        assert "Noridian" in juris_node.name or "Noridian" in juris_node.properties.get("contractor_name", "")

        ny_fee_node = next((n for n in traversal1.nodes if n.primary_key == "FEE-A6522-NY-NR-2024"), None)
        assert ny_fee_node is not None
        assert ny_fee_node.properties.get("state_code") == "NY"

        # 2. Synthesis check for NY
        req1 = GraphRAGQueryRequest(query=query1)
        resp1 = pipeline.execute_query(req1, session)
        assert "JURIS-DME-A" in resp1.answer
        assert "Noridian" in resp1.answer
        assert "STATE-NY" in resp1.answer or "New York" in resp1.answer

        # 3. Query: "What DME MAC jurisdiction covers Guam?" (54th jurisdiction verification)
        query_gu = "What DME MAC jurisdiction covers Guam?"
        anchors_gu = linker.resolve_anchors(query_gu, session)
        assert anchors_gu.state_anchor is not None
        assert anchors_gu.state_anchor.primary_key == "STATE-GU"

        traversal_gu = traverser.extract_connecting_subgraph(anchors_gu, session)
        assert "STATE-GU" in traversal_gu.active_node_pks
        assert "JURIS-DME-D" in traversal_gu.active_node_pks
        assert "DME-MAC-COPE147943" in traversal_gu.active_node_pks


def test_latency_benchmark_harness(neo4j_engine):
    """Latency Benchmark Harness: verifies Neo4j traversal latency (<20ms) and warm pipeline execution."""
    pipeline = GraphRAGPipeline()
    req = GraphRAGQueryRequest(query="I am from Wisconsin, survived breast cancer, need lymphedema supplies, I'm on Medicare, can you help?")

    with neo4j_engine.get_driver().session(database=neo4j_engine.database) as session:
        anchors = pipeline.linker.resolve_anchors(req.query, session)
        pipeline.traverser.extract_connecting_subgraph(anchors, session)

        traversal_times = []
        for _ in range(10):
            traversal_res = pipeline.traverser.extract_connecting_subgraph(anchors, session)
            traversal_times.append(traversal_res.retrieval_ms)

        avg_traversal = sum(traversal_times) / len(traversal_times)
        assert avg_traversal < 20.0, f"Neo4j traversal average {avg_traversal}ms exceeded SLA"

        t0 = time.perf_counter()
        resp = pipeline.execute_query(req, session)
        t_total = (time.perf_counter() - t0) * 1000.0
        assert resp.duration_ms > 0
        assert t_total < 30000.0, f"Total pipeline execution {t_total}ms exceeded SLA"


def test_single_entity_general_traversal_integrity(neo4j_engine):
    """Verifies that single-entity general traversal extracts valid 8-hop neighbors and zero UNKNOWN edge keys."""
    traverser = TopologicalTraversalEngine()
    nodes_by_pk = {}
    edges_by_key = {}
    active_node_pks = set()
    active_edge_keys = set()

    with neo4j_engine.get_driver().session(database=neo4j_engine.database) as session:
        traverser._execute_single_general_traversal(
            anchor_pk="PLAW-117-328",
            session=session,
            nodes_by_pk=nodes_by_pk,
            edges_by_key=edges_by_key,
            active_node_pks=active_node_pks,
            active_edge_keys=active_edge_keys,
        )

        assert "PLAW-117-328" in nodes_by_pk
        assert len(nodes_by_pk) >= 6
        assert len(edges_by_key) >= 5
        for ek in edges_by_key:
            assert "UNKNOWN" not in ek
            assert "->" in ek
