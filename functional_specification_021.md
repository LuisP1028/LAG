# Functional Specification 021: Mac Server Migration and Continuous Self-Hosted Runtime Operationalization for the LAG Policy Engine (Frontend & Backend) and Bartending Repositories

## 1. Objective & Scope

This specification defines the `{functionality}`, `{correctness}`, and `{correct required outputs}` required to replicate the dedicated Mac server migration and continuous runtime hosting workflow—recently completed for the `"Polymarket"` (`LuisP1028/ChoppedPoly`) project—across two additional production systems from the operator's GitHub account:

1. **The `lag` Frontend and Backend Engines:**
   - **Backend & Pipeline Repository:** `LuisP1028/LAG` (`https://github.com/LuisP1028/LAG.git`)
   - **Public Frontend Showcase Repository:** `LuisP1028/lag-policy-engine-showcase` (`https://github.com/LuisP1028/lag-policy-engine-showcase.git`, served publicly at `https://luisp1028.github.io/lag-policy-engine-showcase/`)
2. **The `"Bartending"` Application Repository:**
   - **Application & Asset Pipeline Repository:** `LuisP1028/Bartending` (`https://github.com/LuisP1028/Bartending.git`, DITHER-OS Bartending simulator and its public GitHub Pages shell)

The global objective is to transition the continuous execution responsibility for both `lag` and `"Bartending"` onto the dedicated Mac server alongside `"Polymarket"`, ensuring that:
- Both applications run continuously and reliably on the Mac server with zero paid cloud hosting dependencies (eliminating reliance on paid or sleeping Hugging Face Spaces instances).
- All runtime secrets and environment credentials are provisioned securely on the Mac server with zero secret leakage into Git history, container layers, or client-side static bundles.
- External visitors accessing the public GitHub Pages interfaces (`https://luisp1028.github.io/lag-policy-engine-showcase/` and the `"Bartending"` web shell) connect seamlessly over public HTTPS to the Mac server's active runtimes even when the operator's development workstation is powered off or disconnected.
- `"Polymarket"`, `"lag"`, and `"Bartending"` coexist on the Mac server without port conflicts, process collisions, or cross-service resource interference.

In strict compliance with `@File:LANGUAGE.md` and project rules:
- This document specifies exclusively desired behaviors, inputs, outputs, invariants, edge cases, failure modes, and measurable acceptance criteria.
- It contains zero implementation instructions, code snippets, command sequences, component breakdowns, or architectural prescriptions.
- The **DO NOT CODE YET** gate is active.

---

## 2. Domain & Glossary Alignment

All requirements and verification criteria in this specification strictly adopt the authoritative taxonomy in `@File:LANGUAGE.md`:

- **`{errors}`:** Explicit failure states surfaced during migration, startup, or runtime execution across the Mac server and public web interfaces.
  - **Qualifiers:** Unhandled exceptions, non-zero exit codes, port binding conflicts across `"Polymarket"`, `"lag"`, or `"Bartending"`, missing runtime environment variables, CORS rejections, browser Mixed-Content blocks, HTTP 5xx responses, silent connection timeouts, or `Ghost Patron` roster states.
- **`{correctness}`:** The precise, local execution of each migrated engine on the Mac server verifying that it performs its designated task without logical flaws.
  - **Qualifiers:**
    - For `lag`: Exact preservation of the 17-category, 18-relationship, 8-hop knowledge graph (`3,875` nodes and `7,593` edges for `{Policy Keyword}` `"LTA"`, plus `183` nodes for `"IVIG"`), accurate 20% patient coinsurance and allowable fee schedule arithmetic, strict preservation of `{Direct Path (Native Keys)}` and `{Structural Traversal (Derived Keys)}` provenance metadata, deterministic `Qwen/Qwen2.5-7B-Instruct` synthesis, and `<15`-word DeepSeek micro-fact generation.
    - For `"Bartending"`: Accurate execution of all five gameplay and pipeline stages (Boot Intro, Synthwave Main Menu, Bar Playfield & stock patron spawning, Bartending drink mixing & drag-and-drop service, and `Join the bar!` Comm-Link/Visual Uplink patron generation), persistent local SQLite and JSON roster storage, and verified 4-sprite `Ready Pack` availability prior to patron spawning.
- **`{functionality}`:** The broader, global objective of running `"lag"` (frontend and backend engines) and `"Bartending"` continuously on the dedicated Mac server alongside `"Polymarket"`, decoupled from the operator's personal laptop/workstation and decoupled from remote Hugging Face Spaces compute.
- **`{correct required outputs}`:** The exact, objectively measurable HTTP status codes, JSON payloads, CORS response headers, persisted manifest states, and live UI telemetry indicators defined in Sections 3 through 8.
- **`{sufficient}` / `{insufficient}`:** Complete, unambiguous functional specification where zero ambiguity remains and no arbitrary fallbacks or unverified assumptions are permitted.

---

## 3. Mac Server Repository Synchronization & Secret Isolation Requirements

### 3.1 Clean Repository Provisioning on the Mac Server
* **Inputs:**
  - The operator's authenticated GitHub repositories:
    1. `LuisP1028/LAG`
    2. `LuisP1028/lag-policy-engine-showcase`
    3. `LuisP1028/Bartending`
  - Dedicated workspace directories on the Mac server.
* **Desired Behavior & Outcomes:**
  - Each repository must be present on the Mac server at its latest verified branch state (`main`), matching the workflow established during the `"Polymarket"` (`LuisP1028/ChoppedPoly`) server transfer.
  - All tracked runtime assets required for standalone execution—including the persisted `lag` knowledge graph exports (`exports/lta_knowledge_graph.json`, `src/frontend/public/runs/lta_knowledge_graph.json`, `src/frontend/public/runs/ivig_knowledge_graph.json`) and the `"Bartending"` static media, audio, boot video, stock patron sprites, and schema definitions—must be intact and verified on the Mac server filesystem.

### 3.2 Runtime Credential Provisioning & Zero-Leakage Invariant
* **Inputs:**
  - For `lag`:
    - `HF_TOKEN` / `HUGGINGFACE_API_KEY` (preserving the dedicated `ACT-KG-` credential for live `Qwen/Qwen2.5-7B-Instruct` GraphRAG synthesis)
    - `HF_DEEPSEEK_TOKEN` (dedicated Hugging Face User Access Token for `<15`-word dynamic graph micro-fact synthesis)
    - `CONGRESS_API_KEY` (for legislative data lookups)
  - For `"Bartending"`:
    - Runtime environment secrets as applicable (`HUGGINGFACE_TOKEN`, `PII_ENCRYPTION_KEY`, `XAI_API_KEY`) for menu intelligence, encrypted patron signup storage, and generative patron art pipelines.
* **Constraints & Invariants:**
  - **Strict Secret Isolation:** Zero raw credentials, API keys, or encryption secrets may be committed to `LuisP1028/LAG`, `LuisP1028/lag-policy-engine-showcase`, or `LuisP1028/Bartending`, nor baked into container image layers or static frontend bundles.
  - **Fail-Fast Credential Validation:** If a required credential for a requested runtime operation is missing or empty on the Mac server, the system must immediately surface an explicit, deterministic startup or execution error identifying the exact missing variable rather than silently degrading or substituting ungrounded output.

---

## 4. System A: `lag` Backend & Frontend Engines on the Mac Server

### 4.1 Continuous Mac Server Backend Runtime (`LuisP1028/LAG`)
* **Desired Behavior & Outcomes:**
  - The `lag` backend engine must execute continuously on the Mac server as an isolated, self-healing runtime service that automatically restarts unless explicitly stopped by the operator.
  - Upon startup on the Mac server, the backend must load the persisted 8-hop knowledge graph (`3,875` nodes across 17 entity categories and `7,593` edges across 18 relationship types for `{Policy Keyword}` `"LTA"`) without requiring an external cloud-hosted database subscription.
* **Required Live API Contracts & `{correct required outputs}` on the Mac Server:**
  1. **`GET /api/health` (`200 OK`):** Returns `"status": "ok"`, `"neo4j_connected": true`, `"loaded_policies": ["LTA"]`, non-negative `"uptime_seconds"`, `"storage_backend": "embedded"`, and an ISO-8601 UTC `"timestamp"`.
  2. **`GET /api/graph/summary` (`200 OK`):** Returns `"total_nodes": 3875`, `"total_edges": 7593`, 17 distinct node category counts in `"nodes_by_label"`, and 18 distinct relationship type counts in `"edges_by_type"`.
  3. **`GET /api/graph/topology` (`200 OK` / `400 Bad Request`):** Returns `165` non-rate nodes and `173` edges on base overview; returns `70` Wisconsin `FeeScheduleRate` nodes when queried with `state_filter=WI`; fails fast with HTTP `400 Bad Request` when given an invalid state or jurisdiction filter (e.g., `state_filter=XX`).
  4. **`GET /api/entities/{primary_key}` (`200 OK` / `404 Not Found`):** Returns complete native properties (`{Direct Path (Native Keys)}`), derived properties (`{Structural Traversal (Derived Keys)}`), `text_excerpt`, `citations`, `provenance` (`source_uri`, `selector`, `run_id`, `ingestion_timestamp`), and incident `relationships` for any valid entity (e.g., `PLAW-117-328`), and fails fast with HTTP `404 Not Found` (`"error_type": "EntityResolutionError"`) for nonexistent primary keys.
  5. **`POST /api/entities/resolve` (`200 OK` / `400 Bad Request`):** Deterministically resolves natural language queries to canonical `AnchorEntity` records (e.g., resolving Wisconsin breast cancer lymphedema queries to `STATE-WI` and `ICD10-I97.2`) and fails fast with HTTP `400 Bad Request` on unrecognized geography or unindexed conditions.
  6. **`POST /api/graphrag/subgraph` (`200 OK`):** Extracts the connecting multi-hop topological subgraph (including `DME-MAC-COPE147943` for Wisconsin lymphedema anchors) with `nodes`, `edges`, `active_node_pks`, `active_edge_keys`, and `retrieval_ms`.
  7. **`POST /api/graphrag/query` (`200 OK`):** Synthesizes grounded plain-language answers via `Qwen/Qwen2.5-7B-Instruct` using the `ACT-KG-` credential, quoting exact bracketed `[PRIMARY_KEY]` identifiers and exact allowable reimbursement (`$290.47`) and 20% patient coinsurance (`$58.09`) figures for Wisconsin compression garment inquiries.
  8. **Dynamic Micro-Fact Generation (`GET /api/graphrag/microfact` or equivalent startup metadata):** Synthesizes an accurate knowledge-graph micro-fact strictly under 15 words (1 to 14 words inclusive) via the dedicated Hugging Face DeepSeek model endpoint authenticated with `HF_DEEPSEEK_TOKEN` for the **Medical Durable Goods Assistant** header subtitle.

### 4.2 Public HTTPS Ingress & `lag` Frontend Engine Synchronization (`LuisP1028/lag-policy-engine-showcase`)
* **Desired Behavior & Outcomes:**
  - The Mac server must expose the `lag` backend runtime over a public HTTPS ingress URL (standard TLS port 443) so that external browsers on any network can reach the Mac server without Mixed-Content blocks, VPN software, or custom certificates.
  - Cross-Origin Resource Sharing (CORS) on the Mac server backend must explicitly permit `Origin: https://luisp1028.github.io` (as well as `https://*.github.io` and local development origins) across `GET`, `POST`, and `OPTIONS` preflight requests.
  - The `lag` frontend engine must be built and published to `LuisP1028/lag-policy-engine-showcase` (`https://luisp1028.github.io/lag-policy-engine-showcase/`) bound by default to the Mac server's active public HTTPS ingress URL.
  - All recent UI and ergonomics contracts on the `lag` frontend engine must remain 100% preserved in production:
    - Left-hand docked Node & Edge Detail Inspection Drawer (`left: 0`) with `"◈ WHY IS THIS IMPORTANT?"` unified importance inquiry trigger.
    - Complete elimination of the legacy upper-left Blueprint HUD overlay and `"MODEL:"` selector dropdown.
    - Right-hand docked **Medical Durable Goods Assistant** with its `<15`-word dynamic micro-fact subtitle and `Qwen/Qwen2.5-7B-Instruct` default synthesis.
    - Runtime `?api_url=` query parameter and interactive `API ENDPOINT` UI override support, plus strict fail-fast `▲ EXECUTION ERROR` telemetry (`data-testid="backend-error-banner"`) if the Mac server is unreachable.
  - An updated deployment telemetry record (`src/deploy/deployment_manifest.json`) must be persisted on the Mac server recording the verified Mac server container status, active public HTTPS ingress URL, GitHub Pages commit SHA, and end-to-end verification metrics.

---

## 5. System B: `"Bartending"` (`LuisP1028/Bartending`) on the Mac Server

### 5.1 Continuous Mac Server Application & Persistence Runtime
* **Desired Behavior & Outcomes:**
  - The `"Bartending"` application (`bartending_next` / DITHER-OS Bartending simulator) must be migrated onto the Mac server and run continuously as a self-contained service on a dedicated host port that does not conflict with `"Polymarket"` or `"lag"`.
  - Complete remote decoupling from Hugging Face Spaces (`*.hf.space`): zero application page loads, asset fetches, roster lookups, or patron registration calls may depend on or route to `choppedcheese-dither-os-bartending.hf.space`.
  - **Local Persistence Across Restarts:**
    - SQLite database files (`data/`) and runtime JSON patron registries on the Mac server must persist across container or service restarts without data loss or ephemeral wipe.
    - All dynamically generated or pre-installed patron character packs (`Ready Pack` consisting of non-empty `sit.png`, `talk.png`, `walk_01.png`, and `walk_02.png`) must be durably stored on the Mac server and served with HTTP `200 OK`.
    - Zero `Ghost Patron` identities (roster entries lacking a complete 4-file `Ready Pack` on disk) may be spawned into the bar playfield.

### 5.2 Functional Subsystem Requirements on the Mac Server
All core `"Bartending"` subsystems must operate without `{errors}` on the Mac server runtime:
1. **Boot Intro Stage:** Studio boot video and audio assets stream and play cleanly with functional tap/click skip transitions.
2. **Main Menu (Synthwave Navigator):** Game Boy console shell containment, D-pad/A/B navigation (`B` returning deterministically to the previous screen), and mode transitions (`Start Shift`, `Join the bar!`, drink info).
3. **Bar Playfield & Multi-Patron Seating:** Stock patrons (Elder, Caesar, Trump) and verified enrolled patrons spawn, walk, sit across multi-patron bar stools, converse in the retro RPG dialogue box, and turn over cleanly after service.
4. **Bartending Mixing & Drag-and-Drop Service:** Station view stability, bottle pouring, recipe construction, and physical drag-and-drop cocktail delivery to seated patrons execute without layout jitter or unhandled exceptions.
5. **`Join the bar!` (Comm-Link & Visual Uplink Pipeline):**
   - Comm-Link alias/contact entry and Visual Uplink camera capture fill the Game Boy playfield glass without triggering mobile Safari zoom bugs.
   - Camera permission (`getUserMedia`) works under the secure HTTPS / `localhost` context.
   - Submitting a captured portrait invokes the patron generation pipeline on the Mac server and enrolls the patron into the spawnable roster only once all 4 `Ready Pack` sprites are verified on disk.

### 5.3 Public HTTPS Reachability & GitHub Pages Shell Interoperability (`docs/index.html`)
* **Desired Behavior & Outcomes:**
  - When the `"Bartending"` runtime on the Mac server is accessed locally (`http://localhost:<bartending_port>`) or exposed via a dedicated public HTTPS ingress endpoint for external players visiting the GitHub Pages shell (`docs/index.html`), the shell must resolve to the active Mac server endpoint (supporting explicit `?target=https://...` query parameter override or configured default Mac server HTTPS ingress URL).
  - The embedding shell must preserve full hardware permission delegation (`allow="fullscreen; autoplay; clipboard-write; camera; microphone"`) so external players can complete `Join the bar! → Visual Uplink` camera capture over HTTPS.

---

## 6. Multi-Project Coexistence & Operational Isolation on the Mac Server

Because the dedicated Mac server simultaneously hosts `"Polymarket"` (`LuisP1028/ChoppedPoly`), `"lag"` (`LuisP1028/LAG`), and `"Bartending"` (`LuisP1028/Bartending`), the following coexistence invariants must hold at all times:

1. **Zero Port Collisions:**
   - Each project's local host ports (e.g., `"Polymarket"` databases/workers, `"lag"` backend port `7860`, and `"Bartending"` application port `3001` or dedicated container port) must be strictly non-overlapping on the Mac server's loopback and network interfaces.
2. **Zero Container / Process Name Collisions:**
   - Container names, network bridge names, volume mounts, and daemon identifiers for `"lag"` (`lag-policy-engine-local`, `lag-policy-engine-tunnel`, `lag-net`) and `"Bartending"` must be uniquely namespaced so starting, stopping, or rebuilding one project never interrupts `"Polymarket"` or the other service.
3. **Independent Public HTTPS Ingress Channels:**
   - Public HTTPS ingress tunnels for `"lag"` and (if enabled for external access) `"Bartending"` must route independently to their respective backend containers on the Mac server without cross-routing traffic.
4. **Automatic Recovery & Persistence:**
   - Both `"lag"` and `"Bartending"` services on the Mac server must be configured with automatic restart policies (`unless-stopped` or persistent system service equivalents) so they remain continuously available across process crashes or host reboots.

---

## 7. Edge Cases & Fail-Fast Boundary Conditions

1. **Workstation Shutdown / Decoupling Verification:**
   - Once `"lag"` and `"Bartending"` are migrated to and active on the Mac server, stopping any legacy containers on the previous development workstation must have zero impact on live public availability through `https://luisp1028.github.io/lag-policy-engine-showcase/` or the Mac server endpoints.
2. **Ephemeral Public HTTPS URL Rotation:**
   - If a public HTTPS tunnel on the Mac server restarts and receives a new ephemeral URL, the deployment workflow must deterministically synchronize the new URL to the public frontend configuration (and support immediate runtime connection via `?api_url=` on `lag` and `?target=` on `"Bartending"`).
3. **Missing or Unreachable Mac Server Host / SSH Target:**
   - If the Mac server is unreachable during migration or if required authentication/access parameters to the Mac server are missing, the migration process must halt immediately and surface the exact connection failure rather than deploying to the wrong host.
4. **Corrupted or Incomplete Asset / Graph State:**
   - If `exports/lta_knowledge_graph.json` is missing/corrupted on the Mac server for `lag`, or if a patron's 4-sprite `Ready Pack` is incomplete on the Mac server for `"Bartending"`, the respective service must fail fast on that check rather than serving partial or fabricated state.

---

## 8. End-to-End Acceptance Criteria (`{correct required outputs}`)

The migration and operationalization will be evaluated as `{sufficient}` and meeting `{correctness}` and `{functionality}` only when all of the following criteria are objectively verified on the Mac server:

1. **Mac Server Coexistence & Health:**
   - `"Polymarket"`, `"lag"`, and `"Bartending"` are all present and running concurrently on the Mac server with zero port conflicts, zero container name collisions, and zero non-zero exit codes.
2. **`lag` Backend & Public HTTPS Ingress Verification on the Mac Server:**
   - `GET /api/health` on the Mac server (both locally and via its public HTTPS ingress URL) returns HTTP `200 OK` with `"status": "ok"`, `"neo4j_connected": true`, and `"loaded_policies": ["LTA"]`.
   - `GET /api/graph/summary` returns HTTP `200 OK` with `"total_nodes": 3875` and `"total_edges": 7593`.
   - `GET /api/graph/topology` returns `165` base nodes and `173` edges; `GET /api/graph/topology?state_filter=WI` returns `70` Wisconsin `FeeScheduleRate` nodes; invalid filters return HTTP `400`.
   - `GET /api/entities/PLAW-117-328` returns HTTP `200 OK` with complete provenance and relationships; nonexistent primary keys return HTTP `404` (`EntityResolutionError`).
   - `POST /api/graphrag/query` executes live on the Mac server using `Qwen/Qwen2.5-7B-Instruct` and the `ACT-KG-` token, returning exact Wisconsin reimbursement (`$290.47`) and 20% coinsurance (`$58.09`) figures alongside bracketed `[PRIMARY_KEY]` citations.
   - `OPTIONS /api/graph/topology` with `Origin: https://luisp1028.github.io` returns `access-control-allow-origin: https://luisp1028.github.io`.
3. **`lag` Frontend Showcase Live Interoperability:**
   - `https://luisp1028.github.io/lag-policy-engine-showcase/` is live, defaults to the Mac server's public HTTPS ingress URL (`● READY (LIVE API)`), renders the left-docked inspection drawer with `"◈ WHY IS THIS IMPORTANT?"`, renders the right-docked **Medical Durable Goods Assistant** with its `<15`-word DeepSeek micro-fact subtitle, and executes live GraphRAG queries against the Mac server.
4. **`"Bartending"` Runtime & Persistence Verification on the Mac Server:**
   - The `"Bartending"` server responds with HTTP `200 OK` on its dedicated Mac server port and public ingress URL, serving the main application, static media (boot video, audio, stock patron sprites), and `/api/patrons/roster` from local Mac server storage with zero requests to `*.hf.space`.
   - Local SQLite (`data/`) and patron roster persistence survive service restarts on the Mac server, and zero `Ghost Patron` entries exist in the active spawn pool.
5. **Strict Secret Isolation:**
   - Zero secret tokens (`HF_TOKEN`, `HUGGINGFACE_API_KEY`, `HF_DEEPSEEK_TOKEN`, `CONGRESS_API_KEY`, `HUGGINGFACE_TOKEN`, `PII_ENCRYPTION_KEY`, `XAI_API_KEY`) appear in any tracked Git file, Docker image history, or public frontend bundle.
