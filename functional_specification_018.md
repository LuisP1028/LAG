# Functional Specification 018: Self-Hosted Local Container Runtime with Public HTTPS Ingress for Live GitHub Pages Interoperability

## 1. Objective & Scope

This specification defines the `{functionality}`, `{correctness}`, and `{correct required outputs}` required to transition the backend execution runtime from paid cloud hosting (Hugging Face Spaces) to a zero-cost, self-hosted local container running on the operator's host machine, while maintaining full live API connectivity for any external internet user visiting the public GitHub Pages showcase (`https://luisp1028.github.io/lag-policy-engine-showcase/`).

In accordance with `@File:LANGUAGE.md` and project rules:
- This document specifies only desired behaviors, inputs, outputs, constraints, edge cases, failure modes, and measurable acceptance criteria.
- It contains zero implementation instructions, code snippets, command sequences, or architectural prescriptions.
- The **DO NOT CODE YET** gate is active.

---

## 2. Domain & Glossary Alignment

All requirements and verification criteria in this specification are governed by the taxonomy in `@File:LANGUAGE.md`:
- **`{errors}`:** Any unhandled exception, non-zero exit code, CORS rejection, browser Mixed-Content block, silent connection timeout, or HTTP 5xx failure.
- **`{correctness}`:** Exact adherence to the 17-category, 18-relationship, 8-hop knowledge graph schema (3,875 nodes and 7,593 edges for `{Policy Keyword}` `"LTA"`), accurate mathematical calculation of 20% patient coinsurance and allowable fee schedule rates, and strict preservation of provenance metadata.
- **`{functionality}`:** End-to-end live interoperability between the public GitHub Pages web application and the locally hosted container runtime over the public internet whenever the host computer is powered on.
- **`{correct required outputs}`:** Deterministic JSON responses, HTTP status codes, CORS headers, and UI telemetry states defined in Sections 3 through 6.
- **`{sufficient}` / `{insufficient}`:** Complete, unambiguous behavioral specification requiring zero assumptions or probabilistic fallbacks.

---

## 3. Local Containerized Backend Runtime Requirements

### 3.1 Self-Contained Execution Lifecycle
* **Inputs:**
  - Persisted 8-hop knowledge graph data (`3,875` nodes across 17 entity categories and `7,593` edges across 18 relationship types).
  - Runtime environment credentials supplied externally at container startup, specifically preserving the existing `ACT-KG-` Hugging Face credential (`HF_TOKEN` / `HUGGINGFACE_API_KEY`) for outbound language model synthesis and `CONGRESS_API_KEY` for legislative lookups.
* **Desired Behavior & Outcomes:**
  - The backend service must execute inside an isolated local container on the operator's machine at zero recurring platform cost.
  - Upon container startup, the runtime must verify graph store availability and expose all REST API endpoints without requiring an external cloud-hosted database subscription.
  - When the host machine is powered on and the container is active, the backend must continuously service incoming HTTP requests with deterministic low latency.
* **Constraints & Invariants:**
  - **Secret Isolation:** Neither the container image definition nor any committed repository file may contain hardcoded or baked-in API tokens (`HF_TOKEN`, `HUGGINGFACE_API_KEY`, `HF_DEPLOY_TOKEN`, `CONGRESS_API_KEY`, or database passwords). All sensitive credentials must be injected exclusively at runtime.
  - **Credential Preservation:** The `ACT-KG-` token must remain dedicated to and active for live language model synthesis during GraphRAG query execution.

### 3.2 Required Live API Endpoints & `{correct required outputs}`
1. **Health & Readiness (`GET /api/health`):**
   - **Output (`200 OK`):** JSON payload containing `"status": "ok"`, `"neo4j_connected": true`, `"loaded_policies"` (including `"LTA"`), `"uptime_seconds"` (non-negative float), `"storage_backend"`, and an ISO-8601 UTC `"timestamp"`.
2. **Knowledge Graph Summary (`GET /api/graph/summary`):**
   - **Output (`200 OK`):** JSON payload reporting `"total_nodes": 3875`, `"total_edges": 7593`, 17 distinct node category counts in `"nodes_by_label"`, and 18 distinct relationship type counts in `"edges_by_type"`.
3. **Filtered Graph Topology (`GET /api/graph/topology`):**
   - **Inputs:** Optional query parameters `policy_keyword`, `state_filter` (supporting all 54 US states and territories including `GU`), `jurisdiction_filter` (`JURIS-DME-A` through `JURIS-DME-D`), and `include_fee_schedules` (boolean).
   - **Output (`200 OK`):** JSON payload containing `"nodes"`, `"edges"`, `"total_nodes"`, and `"total_edges"`. Base overview (without state filter or fee expansion) returns `165` non-rate nodes and `173` edges; filtering by `state_filter=WI` expands the `70` Wisconsin `FeeScheduleRate` nodes and scopes geography to `STATE-WI` and `JURIS-DME-B`.
   - **Fail-Fast Output (`400 Bad Request`):** Structured error envelope when any unrecognized `state_filter`, `jurisdiction_filter`, or `policy_keyword` is supplied.
4. **Single-Entity Deep Inspection (`GET /api/entities/{primary_key}`):**
   - **Inputs:** Entity `primary_key` path parameter across any of the 17 canonical categories.
   - **Output (`200 OK`):** JSON payload containing `"primary_key"`, `"label"`, `"name"`, `"properties"` (both `{Direct Path (Native Keys)}` and `{Structural Traversal (Derived Keys)}`), `"text_excerpt"`, `"citations"`, `"provenance"` (`source_uri`, `selector`, `run_id`, `ingestion_timestamp`), and incident `"relationships"`.
   - **Fail-Fast Output (`404 Not Found`):** Structured error envelope with `"error_type": "EntityResolutionError"` when the requested `primary_key` does not exist in the graph.
5. **Deterministic Entity Anchor Resolution (`POST /api/entities/resolve`):**
   - **Inputs:** JSON body `{"query": "<natural language string>"}`.
   - **Output (`200 OK`):** JSON payload listing resolved `AnchorEntity` records across the 17 categories.
   - **Fail-Fast Output (`400 Bad Request`):** Structured `"EntityResolutionError"` envelope if the query references an unrecognized geographic location (e.g., `"Atlantis"`), an unindexed medical condition (e.g., `"diabetes"`), or a nonexistent explicit primary key token (e.g., `"HCPCS-99999"`).
6. **Topological Subgraph Extraction (`POST /api/graphrag/subgraph`):**
   - **Inputs:** JSON body `{"anchors": ["<primary_key_1>", ...]}`.
   - **Output (`200 OK`):** JSON payload containing the connecting `"nodes"`, `"edges"`, `"active_node_pks"`, `"active_edge_keys"`, and `"retrieval_ms"`.
7. **Live GraphRAG Synthesis & Path Illumination (`POST /api/graphrag/query`):**
   - **Inputs:** JSON body containing `"query"` and optional `"primary_key"`, `"state_code"`, or `"model_id"`.
   - **Output (`200 OK`):** JSON payload containing the grounded `"answer"` (synthesized using the `ACT-KG-` credential, quoting exact bracketed primary keys and exact allowable reimbursement/20% coinsurance dollar figures when applicable), `"active_node_pks"`, `"active_edge_keys"`, `"anchors"`, `"provenance_sources"`, and `"duration_ms"`.

---

## 4. Public HTTPS Ingress & Cross-Origin Connectivity Requirements

### 4.1 Secure Public Internet Reachability
* **Problem Context:** The GitHub Pages showcase is served over HTTPS (`https://luisp1028.github.io`). Modern web browsers enforce strict Mixed-Content security policies that block HTTPS pages from issuing `fetch` or `XMLHttpRequest` calls to plain `http://` endpoints or unroutable local addresses (`localhost` / `127.0.0.1`) for external visitors.
* **Desired Behavior & Outcomes:**
  - The local containerized backend must be reachable via a public HTTPS ingress URL over standard TLS (port 443) whenever the host computer and container are running.
  - Any external user on any network or device worldwide who visits `https://luisp1028.github.io/lag-policy-engine-showcase/` must be able to execute live API requests against the operator's local container through this public HTTPS endpoint without installing local software, VPN clients, or custom certificates.

### 4.2 Cross-Origin Resource Sharing (CORS) Policy
* **Desired Behavior & `{correct required outputs}`:**
  - The backend runtime must explicitly allow cross-origin `GET`, `POST`, and `OPTIONS` preflight requests originating from:
    - `https://luisp1028.github.io`
    - Any `https://*.github.io` origin
    - Local development origins (`http://localhost:*`, `http://127.0.0.1:*`)
  - Preflight `OPTIONS` responses must return HTTP `200 OK` (or `204 No Content`) with `Access-Control-Allow-Origin` matching the requesting GitHub Pages origin, `Access-Control-Allow-Methods` permitting `GET, POST, OPTIONS`, and `Access-Control-Allow-Headers` permitting `Content-Type, Authorization`.

---

## 5. Frontend Live API Binding & Offline Fail-Fast Behavior

### 5.1 Live Endpoint Resolution on GitHub Pages
* **Inputs:**
  - Configured public HTTPS backend ingress URL baked at build time or supplied via a runtime query parameter / user-configurable endpoint setting.
* **Desired Behavior & Outcomes:**
  - By default, when any user opens `https://luisp1028.github.io/lag-policy-engine-showcase/`, the application must default to **Live API Mode** (`dataSourceMode = "live"`) targeting the public HTTPS ingress URL of the local Docker container.
  - In addition, if the public HTTPS tunnel URL changes across host machine restarts (e.g., ephemeral public tunnel URLs), the frontend must support specifying or updating the live backend HTTPS URL via a URL query parameter (e.g., `?api_url=https://...`) or an interactive UI connection setting, so the operator or external users can connect to a newly generated tunnel URL immediately, as well as supporting automated redeployment of the configured URL to GitHub Pages.

### 5.2 Host-Offline & Container-Stopped Edge Cases (Fail-Fast Telemetry)
* **Desired Behavior & Outcomes:**
  - Because the backend is hosted on the operator's personal computer, the backend will be unreachable whenever the host computer is powered off, asleep, disconnected from the internet, or the local container is stopped.
  - When the local container is unreachable or returns a non-200 status during `/api/health` or `/api/graph/topology` requests:
    1. **Fail Fast (Zero Silent Fallbacks):** The frontend must immediately transition its execution status badge to `EXECUTION ERROR` and surface the visible error banner (`data-testid="backend-error-banner"`) stating the exact connection failure reason. It must **never** silently substitute static data while claiming to be in Live API mode.
    2. **Explicit User Recovery Controls:** The error banner and toolbar must provide explicit, user-triggered actions to:
       - **Retry Live API:** Re-probe `/api/health` and reload live topology once the host container is back online.
       - **Switch to Pre-Computed Snapshots (`LTA` or `IVIG`):** Allow external visitors to explicitly switch `SOURCE` to the bundled pre-computed runs (`precomputed_lta` or `precomputed_ivig`) when the host computer is turned off.

---

## 6. End-to-End Acceptance Criteria

The implementation will be evaluated as `{sufficient}` and meeting `{correctness}` and `{functionality}` only when all of the following criteria are objectively verified:

1. **Local Container Execution:**
   - The backend container builds cleanly and runs on the local host machine using externally injected environment variables from `.env` (preserving `ACT-KG-` for LLM synthesis), with zero secrets present in the image layers or source repository.
   - `GET /api/health` on the local container returns HTTP `200 OK` with `"status": "ok"` and `"neo4j_connected": true`.
2. **Public HTTPS Ingress Verification:**
   - A public HTTPS URL routes external internet traffic directly to the local container's port.
   - Issuing `GET <public_https_url>/api/health`, `GET <public_https_url>/api/graph/topology`, `GET <public_https_url>/api/entities/PLAW-117-328`, and `POST <public_https_url>/api/graphrag/query` over the public internet returns HTTP `200 OK` with `{correct required outputs}`.
   - Issuing an `OPTIONS` preflight request with `Origin: https://luisp1028.github.io` against `<public_https_url>/api/graph/topology` returns `access-control-allow-origin: https://luisp1028.github.io`.
3. **Live GitHub Pages Interoperability:**
   - The public GitHub Pages showcase (`https://luisp1028.github.io/lag-policy-engine-showcase/`) is deployed and configured with the active public HTTPS backend URL (and supports runtime `?api_url=` override for tunnel URL rotation).
   - Visiting the GitHub Pages URL while the local container and HTTPS ingress are running loads the 8-hop topology live from the local container, shows `● READY (LIVE API)`, and executes live GraphRAG queries end-to-end.
4. **Zero-Cost & Zero-Leakage Compliance:**
   - No paid Hugging Face Spaces compute tier is required or used for hosting the backend container.
   - Zero secret tokens exist in the public GitHub repository (`LuisP1028/lag-policy-engine-showcase`) or static bundle assets.
