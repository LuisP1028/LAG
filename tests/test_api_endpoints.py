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
    assert len(data["provenance_sources"]) > 0
    assert data["duration_ms"] < 1500.0
