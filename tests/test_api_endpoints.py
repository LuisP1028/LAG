"""Integration test suite for FastAPI REST endpoints using TestClient."""

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
    """Verifies /api/graph/summary returns accurate knowledge graph statistics."""
    res = client.get("/api/graph/summary")
    assert res.status_code == 200
    data = res.json()
    assert data["total_nodes"] == 3971
    assert data["total_edges"] >= 7700
    assert len(data["nodes_by_label"]) > 0
    assert len(data["edges_by_type"]) > 0


def test_api_graph_topology(client):
    """Verifies /api/graph/topology with and without high-density fee clustering."""
    # 1. Base non-fee topology (fees collapsed for 60 FPS)
    res_base = client.get("/api/graph/topology")
    assert res_base.status_code == 200
    base_data = res_base.json()
    assert base_data["total_nodes"] < 500
    assert base_data["total_edges"] > 0
    assert all(n["label"] != "FeeScheduleEntry" for n in base_data["nodes"])

    # 2. State-filtered topology (expands Wisconsin fees only)
    res_wi = client.get("/api/graph/topology?state_filter=WI")
    assert res_wi.status_code == 200
    wi_data = res_wi.json()
    assert wi_data["total_nodes"] > base_data["total_nodes"]
    wi_fee_nodes = [n for n in wi_data["nodes"] if n["label"] == "FeeScheduleEntry"]
    assert len(wi_fee_nodes) > 0
    assert all(n["properties"].get("state_code") == "WI" for n in wi_fee_nodes)


def test_api_entities_resolve(client):
    """Verifies /api/entities/resolve extracts anchors and enforces fail-fast error envelopes."""
    # Success case
    res_ok = client.post("/api/entities/resolve", json={"query": "I am from Wisconsin with breast cancer and lymphedema"})
    assert res_ok.status_code == 200
    anchors = res_ok.json()["anchors"]
    anchor_pks = {a["primary_key"] for a in anchors}
    assert "STATE-WI" in anchor_pks
    assert "ICD10-I97.2" in anchor_pks

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
    assert "CMS-MCD-A59508" in node_pks


def test_api_graphrag_query(client):
    """Verifies /api/graphrag/query executes full pipeline, returning answer and illumination telemetry."""
    query_text = "I am from Wisconsin, survived breast cancer, need lymphedema supplies, I'm on Medicare, can you help?"
    res = client.post("/api/graphrag/query", json={"query": query_text})
    assert res.status_code == 200
    data = res.json()

    # Answer validations
    assert "290.47" in data["answer"]
    assert "58.09" in data["answer"]
    assert "CMS-MCD-A59508" in data["answer"]

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
    assert "CMS-CR-13286" in node_pks
    assert "CMS-MCD-A59508" in node_pks

    # 2. POST /api/graphrag/query with single-state question
    res_query = client.post("/api/graphrag/query", json={"query": "What are the allowable compression rates in New York?"})
    assert res_query.status_code == 200
    query_data = res_query.json()
    assert "STATE-NY" in query_data["active_node_pks"]
    assert "JURIS-DME-A" in query_data["active_node_pks"]
    assert "CMS-MCD-A59508" in query_data["active_node_pks"]
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
    assert "[PLAW-117-328]" in data["answer"]
    assert data["duration_ms"] > 0


def test_api_graphrag_query_all_14_entity_types(client):
    """Verifies that one-click inquiry succeeds with >0 illuminated nodes across all 14 entity types."""
    sample_entities = [
        "STATE-WI", "JURIS-DME-B", "CMS-CR-13286", "CMS-MCD-A59508",
        "HCPCS-A6522", "ICD10-I97.2", "FEE-A6522-WI-NR-2024", "POLICY-LTA",
        "PLAW-117-328", "FR-2023-24455", "BILL-117-hr-3630",
        "USC-42-1395x-s-2-JJ", "PUBMED-25574334", "LDA-c8697fc5-7f3b-4861-8a49-d9e6357ad287"
    ]
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

