# Ticket 004: End-to-End Local Container + Public HTTPS Tunnel + GitHub Pages Deployment & Live Acceptance Verification

- **Ticket ID:** `ticket-004`
- **Title:** End-to-End Local Container + Public HTTPS Tunnel + GitHub Pages Deployment & Live Acceptance Verification
- **Type:** `wayfinder:task`
- **Status:** Resolved
- **Claimed by:** `antigravity-wayfinder`
- **Blocked By:** [`ticket-002.md`](ticket-002.md), [`ticket-003.md`](ticket-003.md)
- **Governing Specification:** [`functional_specification_018.md`](file:///Users/diesel/desktop/lag/functional_specification_018.md) (§6.1–§6.4)

---

## 1. Question

How must the deployment and verification orchestrator (`src/deploy/deploy_local_container.py`, `src/deploy/deploy_github_pages.py`, `src/deploy/deploy_all.py`) coordinate local container startup, public HTTPS tunnel provisioning, GitHub Pages static bundle build/push, and end-to-end acceptance verification?

---

## 2. Resolution

1. **Automated Orchestration (`src/deploy/deploy_all.py`):**
   - Step 1: Invokes `deploy_local_container_with_https_ingress()` (`src/deploy/deploy_local_container.py`) to build `lag-policy-engine:local`, start `lag-policy-engine-local` with runtime `.env` secrets and `NEO4J_URI="embedded://exports/lta_knowledge_graph.json"`, start `lag-policy-engine-tunnel` (`cloudflare/cloudflared:latest`), and return the verified public HTTPS ingress URL (`https://*.trycloudflare.com`).
   - Step 2: Updates `DEFAULT_PUBLIC_INGRESS_URL` in `src/frontend/src/utils/apiConfig.ts` and invokes `deploy_to_github_pages(backend_url=public_https_url)` (`src/deploy/deploy_github_pages.py`) to build the static bundle with `VITE_API_BASE_URL=public_https_url`, verify zero secret tokens exist in `dist/`, push to `LuisP1028/lag-policy-engine-showcase`, and verify `https://luisp1028.github.io/lag-policy-engine-showcase/`.
   - Step 3: Executes `verify_end_to_end_deployment()` over the public internet against `<public_https_url>` and `https://luisp1028.github.io/lag-policy-engine-showcase/`:
     - `GET /api/health` -> `200 OK`, `"status": "ok"`, `"neo4j_connected": true`, `"loaded_policies": ["LTA"]`
     - `GET /api/graph/summary` -> `200 OK`, `"total_nodes": 3875`, `"total_edges": 7593`, 17 node labels, 18 relationship types
     - `GET /api/graph/topology` -> `200 OK` (`165` base nodes, `173` base edges) & `?state_filter=WI` (`70` WI fee nodes)
     - `GET /api/entities/PLAW-117-328` -> `200 OK` & nonexistent entity -> `404 Not Found` (`EntityResolutionError`)
     - `POST /api/entities/resolve` -> `200 OK` & invalid entity -> `400 Bad Request` (`EntityResolutionError`)
     - `POST /api/graphrag/subgraph` -> `200 OK`
     - `POST /api/graphrag/query` -> `200 OK` with live LLM synthesis using `ACT-KG-` quoting `$290.47` and `$58.09`
     - `OPTIONS /api/graph/topology` with `Origin: https://luisp1028.github.io` -> `access-control-allow-origin: https://luisp1028.github.io`
   - Step 4: Writes complete verification telemetry to `src/deploy/deployment_manifest.json`.
