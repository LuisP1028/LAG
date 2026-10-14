"""Integration test suite for FastAPI REST endpoints across the 17-category 8-hop ontology."""

import pytest
from fastapi.testclient import TestClient
from src.api.server import app


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as test_client:
        yield test_client


def test_api_health(client):
    """Verifies /api/health endpoint returns 200 OK and connected status."""
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "ok"
    assert data["neo4j_connected"] is True
    assert "timestamp" in data


def test_api_graph_summary(client):
    """Verifies /api/graph/summary returns accurate 8-hop knowledge graph statistics (3,875 nodes, 7,593 edges)."""
    res = client.get("/api/graph/summary")
    assert res.status_code == 200
    data = res.json()
    assert data["total_nodes"] == 3875
    assert data["total_edges"] == 7593
    assert len(data["nodes_by_label"]) == 17
    assert len(data["edges_by_type"]) == 18


def test_api_graph_topology(client):
    """Verifies /api/graph/topology with default non-rate overview, state/jurisdiction scoping, and fail-fast validation."""
    # 1. Base non-rate topology (FeeScheduleRate excluded by default for 60 FPS)
    res_base = client.get("/api/graph/topology")
    assert res_base.status_code == 200
    base_data = res_base.json()
    assert base_data["total_nodes"] == 165
    assert base_data["total_edges"] == 173
    assert all(n["label"] != "FeeScheduleRate" for n in base_data["nodes"])

    # Every node has a derived human-readable name
    by_pk = {n["primary_key"]: n for n in base_data["nodes"]}
    assert by_pk["STATE-GU"]["name"] == "Guam"
    assert by_pk["DME-MAC-COPE147943"]["name"] == "Lymphedema Compression Treatment Items – Correct Coding and Billing – Revised"
    assert by_pk["TR-CR13286"]["name"] == "CR13286 (R12471CP)"

    # 2. State-filtered topology for Wisconsin (expands WI FeeScheduleRate nodes and scopes State/Jurisdiction)
    res_wi = client.get("/api/graph/topology?state_filter=WI")
    assert res_wi.status_code == 200
    wi_data = res_wi.json()
    wi_fee_nodes = [n for n in wi_data["nodes"] if n["label"] == "FeeScheduleRate"]
    assert len(wi_fee_nodes) == 70
    assert all(n["properties"].get("state_code") == "WI" for n in wi_fee_nodes)
    wi_states = [n["primary_key"] for n in wi_data["nodes"] if n["label"] == "State"]
    wi_juris = [n["primary_key"] for n in wi_data["nodes"] if n["label"] == "Jurisdiction"]
    assert wi_states == ["STATE-WI"]
    assert wi_juris == ["JURIS-DME-B"]

    # 3. State-filtered topology for Guam (54th jurisdiction under JURIS-DME-D)
    res_gu = client.get("/api/graph/topology?state_filter=GU")
    assert res_gu.status_code == 200
    gu_data = res_gu.json()
    gu_states = [n["primary_key"] for n in gu_data["nodes"] if n["label"] == "State"]
    gu_juris = [n["primary_key"] for n in gu_data["nodes"] if n["label"] == "Jurisdiction"]
    assert gu_states == ["STATE-GU"]
    assert gu_juris == ["JURIS-DME-D"]

    # 4. Fail-fast HTTP 400 on invalid state, jurisdiction, or policy filter
    assert client.get("/api/graph/topology?state_filter=XX").status_code == 400
    assert client.get("/api/graph/topology?jurisdiction_filter=JURIS-DME-Z").status_code == 400
    assert client.get("/api/graph/topology?policy_keyword=NONEXISTENT_POLICY").status_code == 400


def test_api_entities_resolve(client):
    """Verifies /api/entities/resolve extracts anchors across all 17 categories and enforces fail-fast error envelopes."""
    # Success case 1: Wisconsin + breast cancer + lymphedema
    res_ok = client.post("/api/entities/resolve", json={"query": "I am from Wisconsin with breast cancer and lymphedema"})
    assert res_ok.status_code == 200
    anchors = res_ok.json()["anchors"]
    anchor_pks = {a["primary_key"] for a in anchors}
    assert "STATE-WI" in anchor_pks
    assert "ICD10-I97.2" in anchor_pks

    # Success case 2: Guam (54th jurisdiction)
    res_gu = client.post("/api/entities/resolve", json={"query": "What contractor covers Guam?"})
    assert res_gu.status_code == 200
    gu_pks = {a["primary_key"] for a in res_gu.json()["anchors"]}
    assert "STATE-GU" in gu_pks

    # Error case 1: Unrecognized location
    res_bad_geo = client.post("/api/entities/resolve", json={"query": "I am from Atlantis and need supplies"})
    assert res_bad_geo.status_code == 400
    err_geo = res_bad_geo.json()
    assert err_geo["error"] is True
    assert err_geo["error_type"] == "EntityResolutionError"
    assert "Atlantis" in err_geo["message"]

    # Error case 2: Unindexed condition
    res_bad_cond = client.post("/api/entities/resolve", json={"query": "I have diabetes and need coverage"})
    assert res_bad_cond.status_code == 400
    err_cond = res_bad_cond.json()
    assert err_cond["error"] is True
    assert err_cond["error_type"] == "EntityResolutionError"
    assert "diabetes" in err_cond["message"]

    # Error case 3: Nonexistent explicit PK token
    res_bad_pk = client.post("/api/entities/resolve", json={"query": "Check HCPCS-99999 coverage"})
    assert res_bad_pk.status_code == 400


def test_api_graphrag_subgraph(client):
    """Verifies /api/graphrag/subgraph extracts topological path between entity PKs."""
    req_payload = {"anchors": ["STATE-WI", "ICD10-I97.2"]}
    res = client.post("/api/graphrag/subgraph", json=req_payload)
    assert res.status_code == 200
    data = res.json()
    assert data["retrieval_ms"] > 0
    node_pks = {n["primary_key"] for n in data["nodes"]}
    assert "STATE-WI" in node_pks
    assert "ICD10-I97.2" in node_pks
    assert "DME-MAC-COPE147943" in node_pks
    assert "TR-CR13286" in node_pks


def test_api_graphrag_query(client):
    """Verifies /api/graphrag/query executes full pipeline, returning answer and illumination telemetry."""
    query_text = "I am from Wisconsin, survived breast cancer, need lymphedema supplies, I'm on Medicare, can you help?"
    res = client.post("/api/graphrag/query", json={"query": query_text})
    assert res.status_code == 200
    data = res.json()

    # Answer validations
    assert "290.47" in data["answer"]
    assert "58.09" in data["answer"]
    assert "DME-MAC-COPE147943" in data["answer"] or "TR-CR13286" in data["answer"]

    # Telemetry and active nodes/edges for canvas illumination
    assert "STATE-WI" in data["active_node_pks"]
    assert "ICD10-I97.2" in data["active_node_pks"]
    assert "HCPCS-A6522" in data["active_node_pks"]
    assert len(data["active_edge_keys"]) >= 7
    assert data["duration_ms"] > 0
    assert data["duration_ms"] < 30000.0


def test_api_single_state_and_subgraph(client):
    """Verifies single-state API routing and subgraph extraction without query templates."""
    # 1. POST /api/graphrag/subgraph with single state anchor
    res_subgraph = client.post("/api/graphrag/subgraph", json={"anchors": ["STATE-NY"]})
    assert res_subgraph.status_code == 200
    subgraph_data = res_subgraph.json()
    assert len(subgraph_data["nodes"]) > 0
    node_pks = {n["primary_key"] for n in subgraph_data["nodes"]}
    assert "STATE-NY" in node_pks
    assert "JURIS-DME-A" in node_pks
    assert "TR-CR13286" in node_pks
    assert "DME-MAC-COPE147943" in node_pks

    # 2. POST /api/graphrag/query with single-state question
    res_query = client.post("/api/graphrag/query", json={"query": "What are the allowable compression rates in New York?"})
    assert res_query.status_code == 200
    query_data = res_query.json()
    assert "STATE-NY" in query_data["active_node_pks"]
    assert "JURIS-DME-A" in query_data["active_node_pks"]
    assert "DME-MAC-COPE147943" in query_data["active_node_pks"]
    assert len(query_data["active_edge_keys"]) > 0
    assert len(query_data["provenance_sources"]) > 0
    assert query_data["duration_ms"] > 0


def test_api_graphrag_query_explicit_anchor_plaw(client):
    """Verifies one-click inquiry with explicit primary_key for PLAW-117-328."""
    payload = {
        "query": "Explain the statutory authority and enacted healthcare provisions of [PLAW-117-328] (Consolidated Appropriations Act, 2023).",
        "primary_key": "PLAW-117-328",
    }
    res = client.post("/api/graphrag/query", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "PLAW-117-328" in data["active_node_pks"]
    assert len(data["active_node_pks"]) >= 6
    assert len(data["active_edge_keys"]) >= 5
    assert all("UNKNOWN" not in ek for ek in data["active_edge_keys"])
    assert "117-328" in data["answer"]
    assert data["duration_ms"] > 0


def test_api_graphrag_query_all_17_entity_types(client):
    """Verifies that one-click inquiry succeeds with >0 illuminated nodes across all 17 entity categories."""
    sample_entities = [
        "POLICY-LTA",
        "BILL-117-hr-3630",
        "PLAW-117-328",
        "STAT-117-328-SEC-4133",
        "USC-42-1395x-s-2-JJ",
        "REG-FR-2023-24455",
        "CFR-42-410",
        "TR-CR13286",
        "DME-MAC-COPE147943",
        "ICD10-I97.2",
        "HCPCS-A6522",
        "FEE-A6522-WI-NR-2024",
        "JURIS-DME-B",
        "STATE-WI",
        "LDA-c8697fc5-7f3b-4861-8a49-d9e6357ad287",
        "CBO-58517",
        "PUBMED-25574334",
    ]
    assert len(sample_entities) == 17
    for pk in sample_entities:
        res = client.post("/api/graphrag/query", json={"query": f"Inquire about [{pk}]", "primary_key": pk})
        assert res.status_code == 200
        data = res.json()
        assert len(data["active_node_pks"]) > 0
        assert pk in data["active_node_pks"]


def test_api_graphrag_query_invalid_anchor_fails_fast(client):
    """Verifies fast-fail HTTP 400 when an invalid primary key is supplied."""
    payload = {
        "query": "Inquire about nonexistent node",
        "primary_key": "NONEXISTENT-PK-9999",
    }
    res = client.post("/api/graphrag/query", json=payload)
    assert res.status_code == 400
