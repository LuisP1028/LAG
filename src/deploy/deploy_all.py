"""
Master End-to-End Self-Hosted Container + Public HTTPS Ingress + GitHub Pages Orchestrator.

Implements `functional_specification_018.md` §3–§6:
1. Containerized Backend deployment to local Docker (`lag-policy-engine-local`) with
   companion public HTTPS ingress tunnel (`lag-policy-engine-tunnel` via `cloudflare/cloudflared:latest`).
2. Static Frontend build & deployment to GitHub Pages (`LuisP1028/lag-policy-engine-showcase`)
   bound to the active public HTTPS tunnel URL (with runtime `?api_url=` override support).
3. End-to-end live verification over the public internet across `/api/health`,
   `/api/graph/summary`, `/api/graph/topology`, `/api/entities/{pk}`, `/api/entities/resolve`,
   `/api/graphrag/subgraph`, `/api/graphrag/query` (synthesized via `ACT-KG-`),
   CORS preflight headers (`access-control-allow-origin: https://luisp1028.github.io`),
   and GitHub Pages bundled pre-computed runs (`LTA` & `IVIG`).
4. Persists verified live URLs and telemetry to `src/deploy/deployment_manifest.json`.
"""

from __future__ import annotations
from datetime import datetime, timezone
import json
from pathlib import Path
import re
from typing import Any, Dict
import httpx

from src.deploy.deploy_github_pages import deploy_to_github_pages
from src.deploy.deploy_local_container import deploy_local_container_with_https_ingress


def _sync_default_ingress_url_in_frontend(root: Path, public_https_url: str) -> None:
    """Updates DEFAULT_PUBLIC_INGRESS_URL in src/frontend/src/utils/apiConfig.ts before static build."""
    api_config_path = root / "src" / "frontend" / "src" / "utils" / "apiConfig.ts"
    if not api_config_path.exists():
        return
    content = api_config_path.read_text(encoding="utf-8")
    updated = re.sub(
        r"export const DEFAULT_PUBLIC_INGRESS_URL = '[^']+';",
        f"export const DEFAULT_PUBLIC_INGRESS_URL = '{public_https_url.rstrip('/')}';",
        content,
    )
    if updated != content:
        api_config_path.write_text(updated, encoding="utf-8")


def verify_end_to_end_deployment(public_https_url: str, pages_url: str) -> Dict[str, Any]:
    """Performs strict fail-fast HTTP verification against both the public HTTPS ingress and GitHub Pages."""
    base_url = public_https_url.rstrip("/")
    with httpx.Client(timeout=60.0, follow_redirects=True) as client:
        # 1. Verify Backend Health (GET /api/health)
        health_res = client.get(f"{base_url}/api/health")
        health_res.raise_for_status()
        health_json = health_res.json()
        if health_json.get("status") != "ok" or health_json.get("neo4j_connected") is not True:
            raise RuntimeError(f"Live backend health check failed: {health_json}")
        if "LTA" not in (health_json.get("loaded_policies") or []):
            raise RuntimeError(f"Expected 'LTA' in loaded_policies: {health_json}")

        # 2. Verify Knowledge Graph Summary (GET /api/graph/summary)
        summary_res = client.get(f"{base_url}/api/graph/summary")
        summary_res.raise_for_status()
        summary_json = summary_res.json()
        if summary_json.get("total_nodes") != 3875 or summary_json.get("total_edges") != 7593:
            raise RuntimeError(f"Graph summary mismatch: {summary_json}")
        if len(summary_json.get("nodes_by_label", [])) != 17 or len(summary_json.get("edges_by_type", [])) != 18:
            raise RuntimeError(f"Expected 17 node labels and 18 edge types: {summary_json}")

        # 3. Verify CORS Preflight for GitHub Pages Origin (OPTIONS /api/graph/topology)
        cors_res = client.options(
            f"{base_url}/api/graph/topology",
            headers={
                "Origin": "https://luisp1028.github.io",
                "Access-Control-Request-Method": "GET",
                "Access-Control-Request-Headers": "Content-Type, Authorization",
            },
        )
        allow_origin = cors_res.headers.get("access-control-allow-origin", "")
        if allow_origin != "https://luisp1028.github.io":
            raise RuntimeError(
                f"Expected access-control-allow-origin 'https://luisp1028.github.io', got '{allow_origin}': {dict(cors_res.headers)}"
            )

        # 4. Verify Filtered Graph Topology (GET /api/graph/topology & ?state_filter=WI)
        topo_res = client.get(f"{base_url}/api/graph/topology")
        topo_res.raise_for_status()
        topo_json = topo_res.json()
        if topo_json.get("total_nodes") != 165 or topo_json.get("total_edges") != 173:
            raise RuntimeError(
                f"Unexpected base topology counts: nodes={topo_json.get('total_nodes')}, edges={topo_json.get('total_edges')}"
            )

        topo_wi = client.get(f"{base_url}/api/graph/topology?state_filter=WI")
        topo_wi.raise_for_status()
        wi_json = topo_wi.json()
        wi_fee_nodes = [n for n in wi_json.get("nodes", []) if n.get("label") == "FeeScheduleRate"]
        if len(wi_fee_nodes) != 70:
            raise RuntimeError(f"Expected 70 WI FeeScheduleRate nodes, got {len(wi_fee_nodes)}")

        topo_bad = client.get(f"{base_url}/api/graph/topology?state_filter=XX")
        if topo_bad.status_code != 400:
            raise RuntimeError(f"Expected 400 for invalid state_filter=XX, got {topo_bad.status_code}")

        # 5. Verify Entity Inspection (GET /api/entities/PLAW-117-328 & 404 Fail-Fast)
        ent_res = client.get(f"{base_url}/api/entities/PLAW-117-328")
        ent_res.raise_for_status()
        ent_json = ent_res.json()
        if ent_json.get("primary_key") != "PLAW-117-328":
            raise RuntimeError(f"Entity inspection mismatch: {ent_json}")

        ent_404 = client.get(f"{base_url}/api/entities/NONEXISTENT-PK-9999")
        if ent_404.status_code != 404 or ent_404.json().get("error_type") != "EntityResolutionError":
            raise RuntimeError(f"Expected 404 EntityResolutionError, got {ent_404.status_code}: {ent_404.text}")

        # 6. Verify Entity Anchor Resolution (POST /api/entities/resolve) & Subgraph (POST /api/graphrag/subgraph)
        res_resolve = client.post(
            f"{base_url}/api/entities/resolve",
            json={"query": "I am from Wisconsin with breast cancer and lymphedema"},
        )
        res_resolve.raise_for_status()
        resolved_pks = {a.get("primary_key") for a in res_resolve.json().get("anchors", [])}
        if "STATE-WI" not in resolved_pks or "ICD10-I97.2" not in resolved_pks:
            raise RuntimeError(f"Unexpected resolved anchors: {resolved_pks}")

        res_sub = client.post(
            f"{base_url}/api/graphrag/subgraph",
            json={"anchors": ["STATE-WI", "ICD10-I97.2"]},
        )
        res_sub.raise_for_status()
        sub_json = res_sub.json()
        if "DME-MAC-COPE147943" not in (sub_json.get("active_node_pks") or []):
            raise RuntimeError(f"Subgraph missing DME-MAC-COPE147943: {sub_json.get('active_node_pks')}")

        # 7. Verify Live GraphRAG Synthesis (POST /api/graphrag/query using ACT-KG- credential)
        q_res = client.post(
            f"{base_url}/api/graphrag/query",
            json={
                "query": "I am from Wisconsin, survived breast cancer, need lymphedema supplies, I'm on Medicare, can you help?"
            },
        )
        q_res.raise_for_status()
        q_json = q_res.json()
        answer_text = q_json.get("answer", "")
        if "290.47" not in answer_text or "58.09" not in answer_text:
            raise RuntimeError(f"GraphRAG answer missing required WI fee/coinsurance figures: {answer_text}")

        # 7b. Verify Dynamic Micro-Fact Synthesis (<15 words via HF_DEEPSEEK_TOKEN)
        mf_res = client.get(f"{base_url}/api/graphrag/microfact")
        mf_res.raise_for_status()
        mf_json = mf_res.json()
        mf_wc = int(mf_json.get("word_count", 0))
        if not (1 <= mf_wc < 15):
            raise RuntimeError(f"Micro-fact word count out of bounds (expected 1..14, got {mf_wc}): {mf_json}")

        # 8. Verify GitHub Pages HTML and Bundled Pre-Computed Run Artifacts
        pages_res = client.get(pages_url)
        pages_res.raise_for_status()

        lta_res = client.get(f"{pages_url.rstrip('/')}/runs/lta_knowledge_graph.json")
        lta_res.raise_for_status()
        lta_json = lta_res.json()

        ivig_res = client.get(f"{pages_url.rstrip('/')}/runs/ivig_knowledge_graph.json")
        ivig_res.raise_for_status()
        ivig_json = ivig_res.json()

    return {
        "backend_health": health_json,
        "graph_summary": {
            "total_nodes": summary_json.get("total_nodes"),
            "total_edges": summary_json.get("total_edges"),
            "label_categories": len(summary_json.get("nodes_by_label", [])),
            "relationship_types": len(summary_json.get("edges_by_type", [])),
        },
        "cors_allow_origin": allow_origin,
        "live_topology_nodes": topo_json.get("total_nodes"),
        "live_topology_edges": topo_json.get("total_edges"),
        "wi_fee_schedule_nodes": len(wi_fee_nodes),
        "inspected_entity_pk": ent_json.get("primary_key"),
        "graphrag_query_duration_ms": q_json.get("duration_ms"),
        "graphrag_illuminated_nodes": len(q_json.get("active_node_pks", [])),
        "micro_fact": mf_json,
        "pages_lta_nodes": len(lta_json.get("nodes", [])),
        "pages_ivig_nodes": len(ivig_json.get("nodes", [])),
    }


def deploy_all() -> Dict[str, Any]:
    root = Path(__file__).resolve().parents[2]
    container_info = deploy_local_container_with_https_ingress(project_root=root)
    public_https_url = container_info["public_https_url"]

    _sync_default_ingress_url_in_frontend(root, public_https_url)

    gh_info = deploy_to_github_pages(
        backend_url=public_https_url,
        project_root=root,
    )
    verification = verify_end_to_end_deployment(
        public_https_url=public_https_url,
        pages_url=gh_info["pages_url"],
    )

    manifest = {
        "deployed_at": datetime.now(timezone.utc).isoformat(),
        "local_container_ingress": container_info,
        "github_pages": gh_info,
        "verification": verification,
    }

    manifest_path = root / "src" / "deploy" / "deployment_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return manifest


if __name__ == "__main__":
    out = deploy_all()
    print(json.dumps(out, indent=2))
