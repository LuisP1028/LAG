"""
Automated Verification Suite for the Agnostic Zero-Seed Policy Traversal &
Knowledge Graph Reconstruction Engine (functional_specification_014.md & functional_specification_015.md).

Tests all 8 pipeline hops (Hops 0–7), Tier 5 contextual sidecars, typed inter-hop handoff contracts,
omnibus linear topology, supersession resolution, MCD-to-DME-MAC clinical
routing, operational-key HCPCS filtering, 54-jurisdiction fee schedule unpivoting,
Neo4j idempotent synchronization, and the 8 fail-fast exception classes.
"""

import pytest
from collections import deque

from src.graph.models import (
    PolicyNode,
    BillNode,
    PublicLawNode,
    StatutorySectionNode,
    USCSectionNode,
    RegulationNode,
    CFRSectionNode,
    TransmittalNode,
    CoveragePolicyNode,
    ProcedureCodeNode,
    DiagnosisCodeNode,
    JurisdictionNode,
    StateNode,
    FeeScheduleRateNode,
    CBOScoreNode,
    LobbyingFilingNode,
    LiteratureStudyNode,
    EdgeProvenance,
    GraphEdge,
    PolicyTraversalError,
    LegislativeResolutionError,
    EnactedLawNotFoundError,
    StatutorySectionNotFoundError,
    RegulatoryRuleResolutionError,
    OperationalDirectiveMissingError,
    ClinicalCoverageMissingError,
    CodingTableMismatchError,
    FeeScheduleIngestionError,
    LegislativeHandoff,
    StatutoryHandoff,
    RegulatoryHandoff,
    OperationalHandoff,
    CoverageHandoff,
    CodingHandoff,
    ReimbursementHandoff,
)
from src.graph.engine import PropertyGraphEngine, GraphValidationError

ASSET_DIR = "Extraction/assets"


@pytest.fixture(scope="module")
def graph():
    """Executes the 8-hop agnostic pipeline from a runtime policy keyword."""
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


def test_hop0_and_hop1_omnibus_lineage(graph):
    """
    Verifies Hop 0 legislative discovery and Hop 1 omnibus incorporation:
    Policy -[:DISCOVERED_BILL]-> Bill (Introduced) -[:INCORPORATED_INTO]-> Bill (Omnibus) -[:ENACTED_AS]-> PublicLaw,
    with zero direct shortcut edge from the introduced bill to the Public Law.
    """
    leg: LegislativeHandoff = graph.handoffs["legislative"]
    assert isinstance(leg, LegislativeHandoff)
    assert leg.introduced_bill_id == "BILL-117-hr-3630"
    assert leg.enacting_bill_id == "BILL-117-hr-2617"
    assert leg.public_law_id == "PLAW-117-328"
    assert leg.congress == 117
    assert leg.enacted_date == "2022-12-29"

    assert "BILL-117-hr-3630" in graph.nodes
    assert "BILL-117-hr-2617" in graph.nodes
    assert "PLAW-117-328" in graph.nodes

    edge_keys = {(e.source_pk, e.label, e.target_pk) for e in graph.edges}
    assert ("POLICY-LTA", "DISCOVERED_BILL", "BILL-117-hr-3630") in edge_keys
    assert ("BILL-117-hr-3630", "INCORPORATED_INTO", "BILL-117-hr-2617") in edge_keys
    assert ("BILL-117-hr-2617", "ENACTED_AS", "PLAW-117-328") in edge_keys
    assert ("BILL-117-hr-3630", "ENACTED_AS", "PLAW-117-328") not in edge_keys


def test_hop2_statutory_codification_and_uslm_extraction(graph):
    """
    Verifies Hop 2 USLM XML section extraction, U.S. Code citations, and effective date.
    """
    stat: StatutoryHandoff = graph.handoffs["statutory"]
    assert isinstance(stat, StatutoryHandoff)
    assert stat.public_law_id == "PLAW-117-328"
    assert stat.uslm_section_path == "/us/pl/117/328/dFF/tIV/stD/s4133"
    assert stat.statute_section_number == "4133"
    assert "LYMPHEDEMA COMPRESSION TREATMENT ITEMS" in stat.statute_heading.upper()
    assert "42 U.S.C. 1395x(s)(2)(JJ)" in stat.amended_usc_citations
    assert "42 U.S.C. 1395m" in stat.amended_usc_citations
    assert "42 U.S.C. 1395l(a)(1)" in stat.amended_usc_citations
    assert stat.effective_date == "2024-01-01"

    assert "STAT-117-328-SEC-4133" in graph.nodes
    assert "USC-42-1395x-s-2-JJ" in graph.nodes
    assert "USC-42-1395m" in graph.nodes
    assert "USC-42-1395l-a-1" in graph.nodes

    edge_keys = {(e.source_pk, e.label, e.target_pk) for e in graph.edges}
    assert ("PLAW-117-328", "CONTAINS", "STAT-117-328-SEC-4133") in edge_keys
    assert ("STAT-117-328-SEC-4133", "AMENDS", "USC-42-1395x-s-2-JJ") in edge_keys


def test_hop3_and_hop4_regulatory_and_operational_handoffs(graph):
    """
    Verifies Hop 3 Federal Register Final Rule resolution and Hop 4 CMS Transmittal
    supersession resolution and operational filter extraction.
    """
    reg: RegulatoryHandoff = graph.handoffs["regulatory"]
    assert isinstance(reg, RegulatoryHandoff)
    assert reg.fr_document_number == "2023-24455"
    assert reg.fr_citation == "88 FR 77676"
    assert reg.docket_id == "CMS-1780-F"
    assert reg.rin == "0938-AV03"
    assert "42 CFR Part 410" in reg.cfr_references
    assert "42 CFR Part 414" in reg.cfr_references
    assert reg.effective_date == "2024-01-01"

    op: OperationalHandoff = graph.handoffs["operational"]
    assert isinstance(op, OperationalHandoff)
    assert op.change_request_number == "CR13286"
    assert op.active_transmittal_number == "R12471CP"
    assert "R12379CP" in op.superseded_transmittal_numbers
    assert op.cms_manual_publication == "Pub 100-04"
    assert op.benefit_category_code == "LC"
    assert op.pricing_indicator_code == "40"
    assert op.betos_code == "O1L"
    assert op.effective_date == "2024-01-01"

    assert "REG-FR-2023-24455" in graph.nodes
    assert "CFR-42-410" in graph.nodes
    assert "CFR-42-414" in graph.nodes
    assert "TR-CR13286" in graph.nodes

    edge_keys = {(e.source_pk, e.label, e.target_pk) for e in graph.edges}
    assert ("USC-42-1395x-s-2-JJ", "AUTHORIZED_BY", "REG-FR-2023-24455") in edge_keys
    assert ("REG-FR-2023-24455", "CODIFIED_IN", "CFR-42-410") in edge_keys
    assert ("CFR-42-410", "IMPLEMENTED_BY", "TR-CR13286") in edge_keys


def test_hop5_and_hop6_clinical_coverage_and_operational_hcpcs(graph):
    """
    Verifies Hop 5 MCD-to-DME-MAC clinical coverage routing (ICD-10-CM diagnosis table,
    clean publication title without CPT license banner) and Hop 6 operational-key-only
    HCPCS procedure code extraction (all 77 codes A6520-A6610).
    """
    cov: CoverageHandoff = graph.handoffs["coverage"]
    assert isinstance(cov, CoverageHandoff)
    assert cov.publisher_type == "DME_MAC_JOINT_PUBLICATION"
    assert cov.publication_title == "Lymphedema Compression Treatment Items – Correct Coding and Billing – Revised"
    assert "License for Use" not in cov.publication_title
    assert set(cov.qualifying_icd10_codes) == {"I89.0", "I97.2", "I97.89", "Q82.0"}
    assert len(cov.clinical_prerequisites) >= 1

    coding: CodingHandoff = graph.handoffs["coding"]
    assert isinstance(coding, CodingHandoff)
    assert coding.benefit_category_code == "LC"
    assert coding.betos_code == "O1L"
    assert len(coding.hcpcs_codes) == 77
    assert coding.hcpcs_codes[0] == "A6520"
    assert coding.hcpcs_codes[-1] == "A6610"
    assert all(pi == "40" for pi in coding.code_pricing_indicators.values())

    cov_pk = cov.coverage_guidance_id
    assert cov_pk in graph.nodes
    assert graph.nodes[cov_pk].title == "Lymphedema Compression Treatment Items – Correct Coding and Billing – Revised"
    assert "License for Use" not in graph.nodes[cov_pk].title

    edge_keys = {(e.source_pk, e.label, e.target_pk) for e in graph.edges}
    assert ("TR-CR13286", "MANDATES_POLICY", cov_pk) in edge_keys
    assert (cov_pk, "REQUIRES_DIAGNOSIS", "ICD10-I89.0") in edge_keys
    assert (cov_pk, "REQUIRES_DIAGNOSIS", "ICD10-I97.2") in edge_keys
    assert (cov_pk, "REQUIRES_DIAGNOSIS", "ICD10-I97.89") in edge_keys
    assert (cov_pk, "REQUIRES_DIAGNOSIS", "ICD10-Q82.0") in edge_keys
    assert (cov_pk, "COVERS_PROCEDURE", "HCPCS-A6520") in edge_keys
    assert (cov_pk, "COVERS_PROCEDURE", "HCPCS-A6583") in edge_keys
    assert (cov_pk, "COVERS_PROCEDURE", "HCPCS-A6610") in edge_keys

    # Zero direct edges between any HCPCS and ICD10
    for e in graph.edges:
        assert not (e.source_pk.startswith("HCPCS-") and e.target_pk.startswith("ICD10-"))


def test_tier5_contextual_sidecars(graph):
    """Verifies Tier 5 CBO score, Senate LDA lobbying filings, and PubMed clinical studies."""
    assert "CBO-58517" in graph.nodes
    cbo_node = graph.nodes["CBO-58517"]
    assert isinstance(cbo_node, CBOScoreNode)
    assert "H.R. 3630" in cbo_node.title

    for lda_pk in ("LDA-c8697fc5-7f3b-4861-8a49-d9e6357ad287", "LDA-1821a229-8264-40c2-9b04-49169d917adf"):
        assert lda_pk in graph.nodes
        assert isinstance(graph.nodes[lda_pk], LobbyingFilingNode)

    for pub_pk in ("PUBMED-31454178", "PUBMED-27549490", "PUBMED-25574334", "PUBMED-31298495"):
        assert pub_pk in graph.nodes
        assert isinstance(graph.nodes[pub_pk], LiteratureStudyNode)

    edge_keys = {(e.source_pk, e.label, e.target_pk) for e in graph.edges}
    assert ("BILL-117-hr-3630", "HAS_BUDGET_IMPACT", "CBO-58517") in edge_keys
    assert ("BILL-117-hr-3630", "HAS_ADVOCACY_RECORD", "LDA-c8697fc5-7f3b-4861-8a49-d9e6357ad287") in edge_keys
    assert ("BILL-117-hr-3630", "HAS_ADVOCACY_RECORD", "LDA-1821a229-8264-40c2-9b04-49169d917adf") in edge_keys
    assert ("REG-FR-2023-24455", "SUPPORTED_BY_EVIDENCE", "PUBMED-25574334") in edge_keys


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


def test_hop7_54_jurisdiction_fee_schedule_and_custom_code_reconciliation(graph):
    """
    Verifies Hop 7 54-jurisdiction geographic unpivoting, rate extraction, and
    reconciliation of the 70 national fee schedule codes vs. 7 local contractor pricing codes.
    """
    reimb: ReimbursementHandoff = graph.handoffs["reimbursement"]
    assert isinstance(reimb, ReimbursementHandoff)
    assert reimb.jurisdiction_count == 54
    assert set(reimb.unpriced_custom_codes) == {
        "A6549", "A6559", "A6560", "A6561", "A6584", "A6593", "A6609"
    }

    jurisdictions = [n for n in graph.nodes.values() if isinstance(n, JurisdictionNode)]
    assert len(jurisdictions) == 4

    states = [n for n in graph.nodes.values() if isinstance(n, StateNode)]
    assert len(states) == 54
    assert "STATE-GU" in graph.nodes

    fee_entries = [n for n in graph.nodes.values() if isinstance(n, FeeScheduleRateNode)]
    assert len(fee_entries) == 3710

    wy_fees = [f for f in fee_entries if f.hcpcs_code == "A6583" and f.state_code == "WY" and not f.is_rural]
    assert len(wy_fees) == 1
    assert wy_fees[0].fee_amount == 151.38


def test_edge_provenance_and_unbroken_ancestry(graph):
    """Verifies 100% edge provenance completeness and unbroken reachability from POLICY-LTA."""
    assert len(graph.nodes) == 3875
    assert len(graph.edges) == 7593
    for edge in graph.edges:
        prov = edge.provenance
        assert prov.source_uri != ""
        assert prov.selector != ""
        assert prov.ingestion_timestamp != ""
        assert prov.run_id != ""

    root_pk = "POLICY-LTA"
    visited = {root_pk}
    queue = deque([root_pk])
    while queue:
        curr = queue.popleft()
        for edge in graph._adj.get(curr, []):
            if edge.target_pk not in visited:
                visited.add(edge.target_pk)
                queue.append(edge.target_pk)

    unreachable = set(graph.nodes.keys()) - visited
    assert len(unreachable) == 0


def test_full_phrase_keyword_resolution():
    """Verifies that running with full natural language phrase resolves identical graph topology."""
    engine = PropertyGraphEngine(asset_dir=ASSET_DIR)
    g_full = engine.run_pipeline(keyword="Lymphedema Treatment Act", run_id="test-full-phrase")
    assert "POLICY-LYMPHEDEMA TREATMENT ACT" in g_full.nodes
    assert g_full.handoffs["legislative"].introduced_bill_id == "BILL-117-hr-3630"
    assert g_full.handoffs["legislative"].enacting_bill_id == "BILL-117-hr-2617"
    assert g_full.handoffs["statutory"].statute_section_number == "4133"
    assert len(g_full.handoffs["coding"].hcpcs_codes) == 77


def test_fail_fast_exception_hierarchy():
    """Verifies that all 8 hop-specific exception classes inherit from PolicyTraversalError and fail fast."""
    for exc_cls in (
        LegislativeResolutionError,
        EnactedLawNotFoundError,
        StatutorySectionNotFoundError,
        RegulatoryRuleResolutionError,
        OperationalDirectiveMissingError,
        ClinicalCoverageMissingError,
        CodingTableMismatchError,
        FeeScheduleIngestionError,
    ):
        assert issubclass(exc_cls, PolicyTraversalError)

    engine = PropertyGraphEngine(asset_dir=ASSET_DIR)
    with pytest.raises(LegislativeResolutionError):
        engine.run_pipeline(keyword="NONEXISTENT_POLICY_XYZ_999")


def test_neo4j_sync_and_mcp_invariants():
    """Verifies that the 8-hop LTA graph synchronizes idempotently into Neo4j with 100% invariant compliance."""
    from src.graph.neo4j_sync import Neo4jSyncEngine

    sync_engine = Neo4jSyncEngine()
    try:
        driver = sync_engine.get_driver()
        driver.verify_connectivity()
    except Exception as e:
        pytest.fail(f"Neo4j instance not reachable: {e}")

    try:
        stats1 = sync_engine.sync_file("exports/lta_knowledge_graph.json", purge_stale=True)
        assert stats1["nodes_synced"] == 3875
        assert stats1["edges_synced"] == 7593

        # Idempotent second sync run
        stats2 = sync_engine.sync_file("exports/lta_knowledge_graph.json", purge_stale=True)
        assert stats2["nodes_synced"] == 3875
        assert stats2["edges_synced"] == 7593

        summary = sync_engine.get_summary_statistics()
        assert summary["total_nodes"] == 3875
        assert summary["total_edges"] == 7593
        assert len(summary["nodes_by_label"]) == 17
        assert len(summary["edges_by_type"]) == 18

        with sync_engine.get_driver().session(database=sync_engine.database) as session:
            illegal_res = session.run("MATCH (h:ProcedureCode)-[r]-(i:DiagnosisCode) RETURN count(r) AS illegal").single()
            assert illegal_res["illegal"] == 0

            shortcut_res = session.run(
                "MATCH (:Bill {primary_key: 'BILL-117-hr-3630'})-[r:ENACTED_AS]->(:PublicLaw) RETURN count(r) AS cnt"
            ).single()
            assert shortcut_res["cnt"] == 0

            juris_res = session.run("MATCH (j:Jurisdiction) RETURN count(j) AS cnt").single()
            assert juris_res["cnt"] == 4

            state_res = session.run("MATCH (s:State) RETURN count(s) AS cnt").single()
            assert state_res["cnt"] == 54

            guam_res = session.run(
                "MATCH (j:Jurisdiction {primary_key: 'JURIS-DME-D'})-[:COVERS_STATE]->(s:State {primary_key: 'STATE-GU'}) RETURN count(s) AS cnt"
            ).single()
            assert guam_res["cnt"] == 1

            prov_res = session.run(
                "MATCH ()-[r]->() WHERE r.source_uri IS NULL OR r.selector IS NULL "
                "OR r.ingestion_timestamp IS NULL OR r.run_id IS NULL RETURN count(r) AS cnt"
            ).single()
            assert prov_res["cnt"] == 0
    finally:
        sync_engine.close()
