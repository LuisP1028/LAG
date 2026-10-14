# Ticket 004: Dynamic Search, Pre-Computed Policy Runs, Fee Schedule Expansion & Fail-Fast Telemetry UI (`App.tsx`, `FilterToolbar.tsx`, `GraphSyncContext.tsx`, `AgentChatDrawer.tsx`, `apiConfig.ts`)

- **Ticket ID:** `ticket-004`
- **Title:** Dynamic Search, Pre-Computed Policy Runs, Fee Schedule Expansion & Fail-Fast Telemetry UI (`App.tsx`, `FilterToolbar.tsx`, `GraphSyncContext.tsx`, `AgentChatDrawer.tsx`, `apiConfig.ts`)
- **Status:** Resolved
- **Claimed by:** `wayfinder-read-and-plan`
- **Blocked By:** `ticket-001`, `ticket-003`
- **Governing Specification:** `functional_specification_016.md` (§3.2 Dynamic Search & Query Interface, §3.3 Fail-Fast & Telemetry Display, §5.1.3, §5.1.4 Failure Transparency)

---

## 1. Decision Question

How must the frontend control panel (`FilterToolbar.tsx`, `App.tsx`, `GraphSyncContext.tsx`, `AgentChatDrawer.tsx`, and `src/frontend/src/utils/apiConfig.ts`) be engineered so that external users visiting the GitHub Pages showcase can:
1. Select pre-computed policy runs (`LTA`, `IVIG`) for immediate zero-latency demonstration or dispatch dynamic queries to the live Hugging Face Space backend (`https://choppedcheese-lag-policy-engine.hf.space`);
2. Filter and search nodes by `{Policy Keyword}`, lexical search terms, all 54 US states and territories (including `GU`), DME MAC contractor jurisdictions, entity categories, and fee schedule expansion flags (`include_fee_schedules`);
3. Observe explicit visual indicators of execution status (`idle`, `querying`, `streaming`, `completed`, `error`); and
4. Receive immediate, human-readable fail-fast status alerts whenever the backend runtime is cold starting, unreachable, or returns an HTTP error status code—with zero silent failures or unhandled promise rejections?

---

## 2. Codebase Grounding

1. **Hardcoded Relative `/api` Fetch Calls (`src/frontend/src/App.tsx` line 52, `src/frontend/src/context/GraphSyncContext.tsx` line 401):**
   - `App.tsx` currently calls `fetch('/api/graph/topology?...')` and `GraphSyncContext.tsx` calls `fetch('/api/graphrag/query', ...)`.
   - On GitHub Pages (`https://luisp1028.github.io/lag-policy-engine-showcase/`), relative `/api/...` requests hit `https://luisp1028.github.io/api/...` (404 Not Found) unless routed through a deterministic API base URL helper (`src/frontend/src/utils/apiConfig.ts`) that resolves `VITE_API_BASE_URL` or defaults to `https://choppedcheese-lag-policy-engine.hf.space` when hosted on `github.io` while keeping `""` (relative proxy) on `localhost` / `127.0.0.1`.
2. **Pre-Computed Policy Run Artifacts (`exports/lta_knowledge_graph.json` and `exports/ivig_knowledge_graph.json`):**
   - `functional_specification_016.md` §3.1 and §3.2 require supporting both dynamic backend retrieval and bundled pre-computed policy runs for immediate zero-latency demonstration.
   - Copying `exports/lta_knowledge_graph.json` and `exports/ivig_knowledge_graph.json` into `src/frontend/public/runs/lta_knowledge_graph.json` and `src/frontend/public/runs/ivig_knowledge_graph.json` makes both pre-computed 8-hop runs available as static assets under `${import.meta.env.BASE_URL}runs/<run>.json`.
3. **Missing Controls in `FilterToolbar.tsx` (Lines 48–189):**
   - Currently provides `JURISDICTION`, `STATE`, `POLICY`, `RESET PATH`, and `GRAPHRAG CHAT`.
   - Needs:
     - Pre-computed Run / Mode selector (`data-testid="run-mode-select"`: `Live Backend (HF Space)`, `Pre-Computed Run: LTA`, `Pre-Computed Run: IVIG`)
     - Entity Category filter selector (`data-testid="category-select"`: all 17 canonical 8-hop labels)
     - Search term input (`data-testid="node-search-input"`)
     - Fee Schedule Expansion checkbox/toggle (`data-testid="fee-schedule-toggle"`)
     - Execution status indicator badge (`data-testid="execution-status-badge"`: `IDLE`, `QUERYING`, `DATA STREAMING`, `COMPLETED`, `ERROR`)

---

## 3. Locked Architectural Decision

### 3.1 API Base URL & Pre-Computed Run Resolver (`src/frontend/src/utils/apiConfig.ts`)
Create `src/frontend/src/utils/apiConfig.ts`:
- `DEFAULT_HF_SPACE_URL = "https://choppedcheese-lag-policy-engine.hf.space"`.
- `getApiBaseUrl(): string`:
  - Checks `import.meta.env.VITE_API_BASE_URL`. If set and non-empty, returns it stripped of trailing slash.
  - Otherwise, if `typeof window !== 'undefined'` and `window.location.hostname.endsWith('github.io')`, returns `DEFAULT_HF_SPACE_URL`.
  - Otherwise returns `""` (so local Vite dev server proxy and local integration tests use `/api/...`).
- `getPrecomputedRunUrl(policy: 'LTA' | 'IVIG'): string`:
  - Uses `const base = import.meta.env.BASE_URL || './';` and resolves `${base.endsWith('/') ? base : base + '/'}runs/${policy.toLowerCase()}_knowledge_graph.json`.

### 3.2 Bundled Pre-Computed Policy Run Artifacts (`src/frontend/public/runs/`)
- Copy `exports/lta_knowledge_graph.json` to `src/frontend/public/runs/lta_knowledge_graph.json` and `exports/ivig_knowledge_graph.json` to `src/frontend/public/runs/ivig_knowledge_graph.json`.
- Implement client-side topology filtering in `src/frontend/src/utils/precomputedTopology.ts` (`filterPrecomputedTopology(rawGraph, { policyKeyword, stateFilter, jurisdictionFilter, includeFeeSchedules })`) mirroring the exact filtering and `derive_node_display_name` / `resolve_label_from_pk_and_labels` rules in `src/api/routes.py`:
  - Excludes `FeeScheduleRate` / `FeeScheduleEntry` nodes by default unless `stateFilter` is set (which expands that state's fee rates) or `includeFeeSchedules` is `true` (up to 4,000 fee nodes).
  - Scopes `Jurisdiction` and `State` nodes when `stateFilter` or `jurisdictionFilter` is active.
  - Validates `stateFilter` against all 54 US states/territories (`VALID_STATE_CODES` including `GU`) and `jurisdictionFilter` against `JURIS-DME-A..D`, throwing an explicit `Error` on unrecognized codes.

### 3.3 Fail-Fast Backend Readiness & Status Banner (`src/frontend/src/App.tsx` & `GraphSyncContext.tsx`)
1. **Health Probe & Cold-Start Telemetry:**
   - On mount and when in `'live'` mode, `App.tsx` probes `${getApiBaseUrl()}/api/health` with an `AbortController` timeout (15s) and tracks `backendState`:
     - While connecting (`loading` exceeds 1.2s or initial handshake in flight): sets `backendState = 'cold_starting'` and surfaces a prominent status alert banner (`data-testid="backend-status-banner"`):
       `"Backend runtime cold starting / connecting to Hugging Face Space (https://choppedcheese-lag-policy-engine.hf.space)..."`
     - On HTTP 200 OK: sets `backendState = 'online'`, updates `availablePolicies` from `health.loaded_policies` (preserving `LTA` and `IVIG`), and clears any connection alert.
     - On network error, timeout, or non-2xx HTTP status: sets `backendState = 'error'`, `executionStatus = 'error'`, and renders a high-visibility fail-fast diagnostic banner (`data-testid="backend-error-banner"`) stating the exact error reason (e.g., `"Backend runtime unreachable or returned HTTP <status>: <message>. Retry live connection or switch to Pre-Computed Policy Run."`) with both a `[Retry Connection]` button and a `[Load Pre-Computed LTA Run]` button (explicit user-initiated action, never a silent exception swallow).
2. **Filtered Node & Link Computation (`App.tsx`):**
   - Applies `filterCategory` (matching `node.label === filterCategory`) and `searchQuery` (case-insensitive substring match against `node.primary_key`, `node.name`, `node.label`, or `node.properties.code` / `node.properties.title` / `node.properties.citation`) to compute `visibleNodes` and `visibleLinks` passed to `GraphCanvas` and `NodeDetailDrawer`.
   - If a user filter yields 0 matching nodes, displays an explicit diagnostic overlay on the canvas (`"0 nodes match the active category/search filter — click Reset Filters to restore view"`) so the canvas is never blank without diagnostic feedback (§3.3).

### 3.4 Control Panel Enhancements (`src/frontend/src/components/FilterToolbar.tsx`)
Update `FilterToolbar.tsx` to include:
1. **Run Source Selector (`data-testid="run-mode-select"`):**
   - `live`: `"Live Engine API (HF Space)"`
   - `precomputed_lta`: `"Pre-Computed Run: LTA (Zero-Latency)"`
   - `precomputed_ivig`: `"Pre-Computed Run: IVIG (Zero-Latency)"`
2. **Policy Selector (`data-testid="policy-select"`):** `LTA`, `IVIG`, `ALL`.
3. **Jurisdiction Selector (`data-testid="jurisdiction-select"`):** `All Jurisdictions`, `JURIS-DME-A`, `JURIS-DME-B`, `JURIS-DME-C`, `JURIS-DME-D`.
4. **State Selector (`data-testid="state-select"`):** All 54 US states and territories (`AL`..`WY`, including `DC`, `GU`, `PR`, `VI`).
5. **Entity Category Selector (`data-testid="category-select"`):** All 17 canonical 8-hop categories (`Policy`, `Bill`, `PublicLaw`, `StatutorySection`, `USCSection`, `Regulation`, `CFRSection`, `Transmittal`, `CoveragePolicy`, `DiagnosisCode`, `ProcedureCode`, `FeeScheduleRate`, `Jurisdiction`, `State`, `LobbyingFiling`, `CBOScore`, `LiteratureStudy`).
6. **Search Input (`data-testid="node-search-input"`):** Real-time filter by keyword, citation, or primary key.
7. **Fee Schedule Expansion Flag (`data-testid="fee-schedule-toggle"`):** Checkbox toggling `include_fee_schedules=true|false` and reloading topology.
8. **Execution Status Indicator (`data-testid="execution-status-badge"`):** Displays `IDLE`, `QUERYING`, `STREAMING`, `COMPLETED`, or `ERROR` with distinct color telemetry.

---

## 4. Verification Criteria

- Selecting `Pre-Computed Run: LTA` or `Pre-Computed Run: IVIG` renders the 8-hop topology immediately with zero latency.
- Selecting `Live Engine API` fetches from `${getApiBaseUrl()}/api/graph/topology` and dispatches GraphRAG queries to `${getApiBaseUrl()}/api/graphrag/query`.
- Filtering by state (`GU`, `CA`, `NY`, `WI`), contractor jurisdiction, entity category, search term, or fee schedule expansion updates the visible graph and contractor associations.
- Execution status indicator transitions deterministically across `idle` -> `querying` -> `streaming` -> `completed` / `error`.
- When the backend is unreachable or returns an error status, an explicit status alert banner is rendered with zero unhandled promise rejections.
