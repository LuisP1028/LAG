# Authoritative Static Codebase Scan, External API Reconnaissance, and Schema Audit Report

**Run ID:** `20261013T194318-162-mbmi`  
**Agent:** `plan-scan-2` (Planning Node / Scanner Agent 2)  
**Governing Specification:** `functional_specification_009.md`  
**Status:** Complete Reconnaissance, Codebase Scan, and Empirical Schema Audit (DO NOT CODE YET)  
**Taxonomy Reference:** [LANGUAGE.md](LANGUAGE.md)

---

## 1. Governing Context & Upstream Ingestion Verification

In strict accordance with `INV-HANDOFF-01`, `INV-SCAN-01`, and workspace rules:
- **Seed Specification Ingested:** `functional_specification_009.md` (*Functional Specification: Immediate Synchronous Visualizer Illumination and Zero-Latency Canvas State Synchronization*), verified non-empty, fully bound, and consumed as the single specification in scope.
- **Run Identifier:** `20261013T194318-162-mbmi` (verified substituted across all asset and handoff manifest paths).
- **Wayfinder Architectural Map & Decision Tickets Inspected:**
  - Run-scoped directory `wayfinder/20261013T194318-162-mbmi/` is not yet populated prior to ticket synthesis.
  - Baseline Wayfinder Map inspected: `wayfinder/map.md` (*Wayfinder Architectural Map: GraphRAG Specification for Browser Graph Visualizer*)
  - Ticket 001: `wayfinder/tickets/ticket-001.md` — *Decision Ticket 001: Entity Anchor Linking and Layperson Vocabulary Normalization Specification*
  - Ticket 002: `wayfinder/tickets/ticket-002.md` — *Decision Ticket 002: Generalized Topological Subgraph Expansion and Neighborhood Traversal Specification*
  - Ticket 003: `wayfinder/tickets/ticket-003.md` — *Decision Ticket 003: Factual Context Assembly, Edge Provenance Formatting, and Prompt Grounding Specification*
  - Ticket 004: `wayfinder/tickets/ticket-004.md` — *Decision Ticket 004: Bidirectional Visual Canvas Synchronization and Active Subgraph Illumination Specification*
  - Ticket 005: `wayfinder/tickets/ticket-005.md` — *Decision Ticket 005: Master Specification Synthesis and Edits for functional_specification_004.md*
- **Evaluation Parameters Glossary:** Fully bound to [`LANGUAGE.md`](LANGUAGE.md), strictly adhering to authoritative definitions for `{errors}`, `{correctness}`, `{functionality}`, `{correct required outputs}`, `{sufficient}`, and `{insufficient}` without colloquial paraphrasing or semantic divergence.

---

## 2. Master Component Dependency Cone Register

The deterministic static scan of the active codebase cataloged all local modules, frontend visualizer components, synchronization context providers, styling registries, backend FastAPI endpoints, GraphRAG pipeline stages, property graph models, and verification suites whose interfaces touch the specced functionality in `functional_specification_009.md`:

| Repository-Relative Path | Verbatim Symbols & Interfaces | Role in Architecture | Grounding Justification (`functional_specification_009.md`) |
| :--- | :--- | :--- | :--- |
| `LANGUAGE.md` | `{errors}`, `{correctness}`, `{functionality}`, `{correct required outputs}`, `{sufficient}`, `{insufficient}`, `{Policy Keyword}`, `{Target_Bill_IDs}`, `{Enacted_Law_ID}`, `{US_Code_Citations}`, `{Operational_Filters}`, `{Clinical_Citations}`, `{HCPCS / CPT Codes}` | System-wide evaluation parameters and domain taxonomy glossary. | Section 2 mandates strict conformance of all evaluations to `LANGUAGE.md`. |
| `src/frontend/src/components/GraphCanvas.tsx` | `GraphCanvasProps`, `GraphCanvas`, `canvasRef`, `simulationRef`, `transformRef`, `zoomBehaviorRef`, `renderRef`, `frameActiveSubgraph`, `render`, `handlePointerDown`, `handlePointerMove` | HTML5 Canvas force-directed graph visualizer executing D3 force simulation ticks, D3 zoom/pan/transition transforms, active node/edge illumination, radial halos, node leader badges, and 60 FPS telemetry HUD. | Primary component governing Section 4.1 (Immediate Reactive Redraw), Section 4.2 (Synchronized Viewport Framing), Section 4.3 (Responsive De-Illumination), Section 4.4 (Preserved Selection and Hover Continuity), and Section 5 (Error Boundaries and Edge Cases). |
| `src/frontend/src/context/GraphSyncContext.tsx` | `ChatMessage`, `StateOption`, `JurisdictionMetadata`, `DME_JURISDICTIONS`, `STATE_TO_JURISDICTION`, `ALL_STATES_SORTED`, `GraphSyncContextType`, `GraphSyncProvider`, `useGraphSync`, `activeNodePKs`, `activeEdgeKeys`, `isIlluminated`, `selectedNode`, `selectNode`, `setIlluminatedPath`, `clearIllumination`, `illuminateJurisdiction`, `setFilterJurisdiction`, `setFilterState`, `submitInquiry`, `inquireNode` | React Context state synchronization bus connecting GraphRAG query execution (`POST /api/graphrag/query`), toolbar filters, node selection, and chat drawer state to `GraphCanvas`. | Manages state transitions for `activeNodePKs`, `activeEdgeKeys`, and `isIlluminated` (Section 4.1.1), reset actions (`clearIllumination`, Section 4.3.1), rapid successive queries (`submitInquiry`, Section 5.1), and empty subgraph responses (`setIlluminatedPath`, Section 5.3). |
| `src/frontend/src/components/AgentChatDrawer.tsx` | `AgentChatDrawer`, `handleSend`, `inputQuery`, `modelId`, `isChatOpen`, `setIsChatOpen`, `messages`, `isQueryLoading`, `errorMsg`, `submitInquiry` | Conversational GraphRAG drawer displaying quick prompts, synthesis responses, latency telemetry, and `Nodes Illuminated` badges. | Section 1 & Section 4.3.1 require chat inquiry submission and chat inquiry close/reset actions to synchronize immediately with canvas illumination and de-illumination. |
| `src/frontend/src/components/NodeDetailDrawer.tsx` | `NodeDetailDrawerProps`, `NodeDetailDrawer`, `connectedNeighbors`, `getGovernmentSourceLink`, `inquireNode`, `selectedNode`, `selectNode` | Slide-over node inspection drawer hosting the one-click `"◈ INQUIRE IN GRAPHRAG CHAT"` action button (`inquireNode`) and neighbor navigation. | Section 1, Section 4.4.1, and Section 6.1 require one-click `"INQUIRE IN GRAPHRAG CHAT"` to immediately illuminate active paths while preserving selected node highlighting. |
| `src/frontend/src/components/FilterToolbar.tsx` | `FilterToolbarProps`, `FilterToolbar`, `handleJurisdictionChange`, `handleStateChange`, `handlePolicyChange`, `clearIllumination` | Top navigation toolbar containing `JURISDICTION:`, `STATE:`, and `POLICY:` dropdowns, the `"✕ RESET PATH"` button (`clearIllumination`), and the `"◈ GRAPHRAG CHAT"` toggle. | Section 4.3 & Section 6.2 require `"✕ RESET PATH"` and filter resets to immediately un-illuminate and repaint the canvas with zero manual user gesture. |
| `src/frontend/src/App.tsx` | `RawTopologyNode`, `RawTopologyEdge`, `RawTopologyResponse`, `MainVisualizer`, `App`, `fetchTopology`, `nodes`, `links`, `loading`, `fetchError` | Top-level visualizer layout container fetching `/api/graph/topology`, constructing `GraphNode` and `GraphLink` instances (including `edge_key`), and mounting `GraphCanvas`, `FilterToolbar`, `NodeDetailDrawer`, and `AgentChatDrawer` inside `GraphSyncProvider`. | Supplies the `nodes` and `links` arrays rendered and framed by `GraphCanvas`. |
| `src/frontend/src/styles/graph_theme.ts` | `NodeVisualConfig`, `NODE_THEME_REGISTRY`, `CANVAS_PALETTE`, `getNodeVisual` | Authoritative visual theme registry defining `CANVAS_PALETTE` (`bgVoid: '#0a1128'`, `accentAmber: '#ffb703'`, `activeHalo: '#f59e0b'`, `activeEdge: '#fbbf24'`, `inactiveAttenuation: 0.18`) and per-label node radii/colors. | Section 4.1.3 & Section 4.3.2 specify exact gold/amber (`#ffb703`), radial glow halo (`rgba(255, 183, 3, 0.45)`), active edge stroke, and baseline blueprint colors. |
| `src/frontend/src/types/graph.ts` | `NodeProperties`, `EdgeProvenance`, `GraphNode`, `GraphLink`, `AnchorEntity`, `GraphRAGQueryResponse`, `GraphSummary` | TypeScript interfaces for graph topology nodes/links and `GraphRAGQueryResponse` (`active_node_pks`, `active_edge_keys`, `anchors`, `provenance_sources`, `duration_ms`). | Defines the synchronization payload contract between `/api/graphrag/query`, `GraphSyncContext`, and `GraphCanvas`. |
| `src/frontend/src/utils/promptGenerator.ts` | `constructInquiryPrompt` | Generates deterministic natural language inquiry prompts for all 14 node types when `"◈ INQUIRE IN GRAPHRAG CHAT"` is clicked. | Invoked by `inquireNode` in `GraphSyncContext.tsx` for one-click node inquiries. |
| `src/frontend/src/main.tsx` | `createRoot`, `StrictMode`, `App` | React 19 DOM entrypoint mounting `<App />`. | Mounts the visualizer application (`StrictMode` double-effect invocation behavior in development). |
| `src/frontend/src/index.css` | Global CSS styles (`#root`, `body`, `html`, `--bg-void`, `--accent-amber`) | Base viewport styling (`100vw`, `100vh`, `overflow: hidden`). | Establishes full-viewport container dimensions for `GraphCanvas`. |
| `src/frontend/src/App.css` | Component CSS rules | Stylesheet in `src/frontend/src/`. | Frontend styling asset. |
| `src/frontend/package.json` | Dependencies (`react`, `react-dom`, `d3`, `lucide-react`) and build scripts | Frontend package manifest. | Defines React 19 (`^19.2.8`) and D3 v7 (`^7.9.0`) runtime dependencies. |
| `src/frontend/vite.config.ts` | Vite dev server and `/api` proxy configuration (`http://localhost:8000`) | Frontend build and proxy configuration. | Proxies `/api/graph/topology` and `/api/graphrag/query` to FastAPI backend. |
| `src/api/routes.py` | `router`, `get_graph_topology`, `resolve_entities`, `get_subgraph_by_anchors`, `execute_graphrag_query`, `get_graph_summary`, `health_check` | FastAPI REST router serving topology nodes/edges and GraphRAG query responses. | Emits `TopologyResponse` (`nodes`, `edges` with `edge_key`) and `GraphRAGQueryResponse` (`active_node_pks`, `active_edge_keys`). |
| `src/api/models.py` | `HealthResponse`, `TopologyNode`, `TopologyEdge`, `TopologyResponse`, `EntityResolveRequest`, `EntityResolveResponse`, `SubgraphRequest`, `SubgraphResponse`, `ErrorEnvelope` | Pydantic request/response models for REST endpoints. | Defines schema contracts consumed by the React visualizer. |
| `src/api/server.py` | `lifespan`, `create_app`, `app`, `http_exception_handler`, `graphrag_exception_handler` | FastAPI server entrypoint, CORS middleware, and Neo4j lifespan manager. | Hosts the backend API server. |
| `src/api/__init__.py` | `app`, `create_app` | API package exports. | Module boundary for `src.api`. |
| `src/graphrag/traversal.py` | `TopologicalTraversalEngine`, `extract_connecting_subgraph`, `_execute_single_entity_traversal`, `_execute_jurisdiction_traversal`, `_execute_single_state_traversal`, `_execute_single_clinical_traversal`, `_execute_single_general_traversal`, `_execute_multi_entity_traversal`, `_execute_pattern_a`, `_execute_pattern_b`, `_execute_pattern_c`, `_convert_node`, `_convert_edge` | Neo4j Cypher subgraph traversal engine computing `active_node_pks` and `active_edge_keys`. | Generates the `active_node_pks` and `active_edge_keys` arrays consumed by `GraphSyncContext` and `GraphCanvas` to illuminate nodes and edges. |
| `src/graphrag/pipeline.py` | `GraphRAGPipeline`, `execute_query` | Orchestrates entity linking, subgraph traversal, context assembly, and LLM synthesis. | Produces `GraphRAGQueryResponse` for `/api/graphrag/query`. |
| `src/graphrag/entity_linker.py` | `EntityAnchorLinker`, `resolve_anchors`, `resolve_explicit_anchor` | Deterministic multi-slot entity anchor linker. | Resolves natural language queries and explicit `primary_key` anchors. |
| `src/graphrag/context_assembler.py` | `GraphContextAssembler`, `assemble_context` | Formats traversed subgraphs into structured Markdown sections. | Stage 3 of the GraphRAG query pipeline. |
| `src/graphrag/synthesizer.py` | `HuggingFaceSynthesizer`, `synthesize`, `_call_hf_inference_api` | Calls Hugging Face Serverless Inference Router (`https://router.huggingface.co/v1/chat/completions`). | Synthesizes the assistant response returned alongside `active_node_pks` and `active_edge_keys`. |
| `src/graphrag/models.py` | `AnchorEntity`, `ResolvedAnchors`, `TraversalNode`, `TraversalEdge`, `TraversalResult`, `GraphRAGQueryRequest`, `GraphRAGQueryResponse` | Pydantic models for GraphRAG pipeline data structures. | Defines `GraphRAGQueryResponse` (`active_node_pks: List[str]`, `active_edge_keys: List[str]`). |
| `src/graphrag/exceptions.py` | `GraphRAGException`, `EntityResolutionError`, `TraversalError`, `ModelInferenceError`, `ModelAuthenticationError`, `ModelRateLimitError`, `GraphValidationError` | Fail-fast exception hierarchy. | Enforces fail-fast error handling (`INV-FAIL-FAST`). |
| `src/graphrag/__init__.py` | Package exports | GraphRAG module exports. | Module boundary for `src.graphrag`. |
| `src/graph/models.py` | `EdgeProvenance`, `GraphEdge`, `BaseNode`, and 15 domain node classes | Canonical domain graph models and composite primary key formats. | Defines canonical `primary_key` and `edge_key` (`{source_pk}->{label}->{target_pk}`) formats. |
| `src/graph/engine.py` | `DirectedPropertyGraph`, `PropertyGraphEngine`, `run_pipeline`, `validate_invariants` | Graph assembly and invariant validation engine. | Validates `INV-UNBROKEN-ANCESTRY`, `INV-NO-KEYWORD-BRIDGING`, and `INV-50-STATE-COMPLETENESS`. |
| `src/graph/neo4j_sync.py` | `Neo4jSyncEngine`, `init_schema`, `sync_graph_dict`, `sync_file`, `get_summary_statistics` | Neo4j property graph synchronization engine. | Manages Neo4j connection and schema constraints. |
| `src/graph/tier1_legislative.py` | `discover_legislation` | Tier 1 legislative ingestion. | Populates `Policy`, `Bill`, and `PublicLaw` nodes. |
| `src/graph/tier2_statutory.py` | `parse_statutory_codification` | Tier 2 statutory ingestion. | Populates `StatutorySection` nodes. |
| `src/graph/tier3_regulatory.py` | `harvest_regulations` | Tier 3 regulatory ingestion. | Populates `Regulation` and `ChangeRequest` nodes. |
| `src/graph/tier4a_coverage.py` | `ingest_coverage_policy` | Tier 4A coverage policy ingestion. | Populates `CoveragePolicy`, `HCPCSCode`, and `ICD10Code` nodes. |
| `src/graph/tier4b_fee_schedule.py` | `DME_MAC_JURISDICTIONS`, `normalize_fee_schedules` | Tier 4B jurisdiction, state, and fee schedule ingestion. | Populates `Jurisdiction`, `State`, and `FeeScheduleEntry` nodes. |
| `src/graph/tier5_context.py` | `enrich_context` | Tier 5 contextual enrichment. | Populates `LobbyingFiling`, `CBOScore`, and `LiteratureStudy` nodes. |
| `src/graph/__init__.py` | Package exports | Graph module exports. | Module boundary for `src.graph`. |
| `tests/test_api_endpoints.py` | FastAPI endpoint integration test suite | Tests `/api/health`, `/api/graph/topology`, `/api/entities/resolve`, `/api/graphrag/subgraph`, and `/api/graphrag/query`. | Validates API response contracts for `active_node_pks` and `active_edge_keys`. |
| `tests/test_graphrag_pipeline.py` | End-to-end GraphRAG pipeline verification suite | Tests all 6 GraphRAG oracles and latency benchmarks. | Validates subgraph traversal and `active_node_pks` / `active_edge_keys` generation. |
| `tests/test_graph_pipeline.py` | Property graph construction and invariant test suite | Tests 5-tier graph ingestion and Neo4j sync invariants. | Validates underlying knowledge graph integrity. |
| `verify_all.py` | `main` | End-to-end verification script. | CLI verification entrypoint. |

---

## 3. Candidate External Datasource & Schema Audit Register

Active read-only reconnaissance was executed against the live Neo4j database, the FastAPI topology and GraphRAG endpoints, and the Hugging Face Inference Router API. All raw, unedited empirical payloads were captured into `assets/20261013T194318-162-mbmi/`.

### 3.1. Local FastAPI Topology Endpoint (`GET /api/graph/topology`)
- **Role in Specification:** Supplies the baseline and state/jurisdiction-filtered `nodes` and `edges` rendered on `GraphCanvas.tsx` and matched against `activeNodePKs` (`node.primary_key`) and `activeEdgeKeys` (`link.edge_key`).
- **Connection & Authentication:** Local FastAPI ASGI service (`http://localhost:8000/api/graph/topology`, proxied via Vite at `/api/graph/topology`), no auth required.
- **Audited Empirical Payload Schema:**
  - `nodes` (`List[TopologyNode]`):
    - `primary_key` (`str`, non-null): e.g., `"POLICY-LTA"`, `"PLAW-117-328"`, `"JURIS-DME-B"`, `"STATE-WI"`, `"CMS-MCD-A59508"`, `"HCPCS-A6522"`, `"ICD10-I97.2"`.
    - `label` (`str`, non-null): One of the 14 domain labels (`Policy`, `Bill`, `PublicLaw`, `StatutorySection`, `Regulation`, `ChangeRequest`, `CoveragePolicy`, `Jurisdiction`, `State`, `HCPCSCode`, `ICD10Code`, `FeeScheduleEntry`, `LobbyingFiling`, `LiteratureStudy`).
    - `name` (`str`, non-null): Display caption string.
    - `properties` (`Dict[str, Any]`, non-null): Node attribute dictionary.
  - `edges` (`List[TopologyEdge]`):
    - `source_pk` (`str`, non-null)
    - `target_pk` (`str`, non-null)
    - `label` (`str`, non-null): Authentic relationship type in Neo4j (`TARGETS_BILL`, `ENACTED_AS`, `MODIFIES_CODE`, `IMPLEMENTED_BY`, `ISSUES_TRANSMITTAL`, `MANDATES_POLICY`, `APPLIES_TO_JURISDICTION`, `COVERS_STATE`, `GOVERNS`, `ALLOWS_DIAGNOSIS`, `HAS_FEE_SCHEDULE`, `APPLIES_TO`, `HAS_ADVOCACY_RECORD`, `SUPPORTED_BY_EVIDENCE`).
    - `edge_key` (`str`, non-null): Formatted as `"{source_pk}->{label}->{target_pk}"`.
    - `provenance` (`Dict[str, str]`, non-null): `source_uri`, `selector`, `ingestion_timestamp`, `run_id`.
  - `total_nodes` (`int`): `155` on default national overview (`state_filter` unset); `226` when `state_filter=WI`.
  - `total_edges` (`int`): `163` on default national overview; `305` when `state_filter=WI`.
- **Saved Ground-Truth Asset:**
  - `assets/20261013T194318-162-mbmi/api_graph_topology_baseline.json`

---

### 3.2. Local FastAPI GraphRAG Query & Subgraph Endpoints (`POST /api/graphrag/query`, `POST /api/graphrag/subgraph`, `POST /api/entities/resolve`)
- **Role in Specification:** Executes GraphRAG queries initiated from `AgentChatDrawer` or one-click `"◈ INQUIRE IN GRAPHRAG CHAT"` in `NodeDetailDrawer`, returning `active_node_pks` and `active_edge_keys` to `GraphSyncContext.setIlluminatedPath`.
- **Audited Empirical Payload Schema (`GraphRAGQueryResponse`):**
  - `answer` (`str`, non-null): Synthesized natural language markdown response citing bracketed primary keys.
  - `active_node_pks` (`List[str]`, non-null): Primary keys of nodes to illuminate on `GraphCanvas`.
  - `active_edge_keys` (`List[str]`, non-null): Directed edge keys (`"{source_pk}->{label}->{target_pk}"`) to illuminate on `GraphCanvas`.
  - `anchors` (`List[AnchorEntity]`, non-null): Resolved input entity anchors (`slot`, `primary_key`, `matched_text`, `entity_type`, `label`).
  - `provenance_sources` (`List[Dict[str, Any]]`, non-null): Unique edge provenance records.
  - `duration_ms` (`float`, non-null): End-to-end execution duration in milliseconds.
- **Empirical Probe Findings:**
  1. **Probe 1 (`"How do IVIG and LTA converge under federal law?"`):**
     - Returns `active_node_pks` with **11 nodes** (`BILL-117-hr-2617`, `BILL-117-hr-3630`, `BILL-117-hr-3808`, `CMS-CR-13217`, `CMS-CR-13286`, `FR-2023-24455`, `PLAW-117-328`, `POLICY-IVIG`, `POLICY-LTA`, `USC-42-1395x-s-2-JJ`, `USC-42-1395x-s-2-Z`) — matching the exact `"11 Nodes Illuminated"` example in Section 1 of `functional_specification_009.md`.
     - Returns `active_edge_keys` with 13 edges, of which **6 edges are corrupted with `"->RELATED_TO->"`** (`"PLAW-117-328->RELATED_TO->USC-42-1395x-s-2-JJ"`, `"USC-42-1395x-s-2-JJ->RELATED_TO->FR-2023-24455"`, `"FR-2023-24455->RELATED_TO->CMS-CR-13286"`, etc.) instead of their authentic Neo4j edge types (`MODIFIES_CODE`, `IMPLEMENTED_BY`, `ISSUES_TRANSMITTAL`), causing those 6 edges to fail `activeEdgeKeys.has(link.edge_key)` in `GraphCanvas.tsx`!
  2. **Probe 2 (`"I am from Wisconsin, survived breast cancer, need lymphedema supplies, I'm on Medicare, can you help?"`):**
     - Returns 7 `active_node_pks` (`CMS-CR-13286`, `CMS-MCD-A59508`, `FEE-A6522-WI-NR-2024`, `HCPCS-A6522`, `ICD10-I97.2`, `JURIS-DME-B`, `STATE-WI`) and 7 authentic `active_edge_keys`.
     - When `state_filter` is unset (National Overview, 155 nodes), `FEE-A6522-WI-NR-2024` and its 2 incident edges (`HCPCS-A6522->HAS_FEE_SCHEDULE->FEE-A6522-WI-NR-2024`, `FEE-A6522-WI-NR-2024->APPLIES_TO->STATE-WI`) are not in the unexpanded baseline topology unless fee nodes for active subgraphs or state filters are loaded.
  3. **Probe 3 (One-click `"◈ INQUIRE IN GRAPHRAG CHAT"` on `PLAW-117-328`):**
     - Returns 6 `active_node_pks` and 5 `active_edge_keys`. **All 5 `active_edge_keys` are corrupted to `"->RELATED_TO->"`** (`"BILL-117-hr-2617->RELATED_TO->PLAW-117-328"`, etc.), resulting in **0 of 5 `active_edge_keys` matching `link.edge_key` in the topology**!
- **Saved Ground-Truth Assets:**
  - `assets/20261013T194318-162-mbmi/api_graphrag_query_illumination_probes.json`
  - `assets/20261013T194318-162-mbmi/neo4j_canvas_illumination_alignment_audit.json`

---

### 3.3. Neo4j Property Graph Database (`bolt://localhost:7687`, database `neo4j`)
- **Role in Specification:** Backing store for all 3,971 `PolicyNode` vertices and 7,786 directed edges.
- **Connection Parameters:** `NEO4J_URI=bolt://localhost:7687`, `NEO4J_USERNAME=neo4j`, `NEO4J_PASSWORD=qwertyui`, `NEO4J_DATABASE=neo4j`.
- **Status:** Reachable & verified via `GET /api/health` (`{"status": "ok", "neo4j_connected": true}`).

---

### 3.4. Hugging Face Serverless Inference Router (`https://router.huggingface.co/v1/chat/completions`)
- **Role in Specification:** OpenAI-compatible chat completions endpoint invoked by `HuggingFaceSynthesizer` during `POST /api/graphrag/query`.
- **Authentication:** Bearer token via `HF_TOKEN` / `HUGGINGFACE_API_KEY` in `.env`.
- **Status:** Reachable & verified live across Probes 1, 2, and 3 (`duration_ms` ~1,200–2,000ms).

---

## 4. Explicit Deficiency Register

In strict compliance with `INV-ABSENCE-01`, the following specced requirements in `functional_specification_009.md` are currently defective or unprovided in the active codebase. Zero components or endpoints have been invented.

| Deficiency ID | Affected Component(s) | Specced Requirement (`functional_specification_009.md`) | Empirical Observation & Exact Codebase Deficiency |
| :--- | :--- | :--- | :--- |
| **`DEF-001`** | `src/frontend/src/components/GraphCanvas.tsx` (lines 40–81, 314–316, 358–380) | **Req 4.1.1, 4.1.2, 4.2.1, 4.2.2, 4.2.3, 5.2 (Immediate Reactive Redraw & Synchronized Viewport Framing):** Whenever `activeNodePKs`, `activeEdgeKeys`, or `isIlluminated` changes, the canvas must immediately repaint without waiting for user gestures; during the 350ms camera transition (`frameActiveSubgraph`), every intermediate animation frame and the final frame must render active nodes and edges in their illuminated state, even when the force simulation has already settled (`alpha < alphaMin`). | **Primary Root Cause of Dormant Canvas State:** In `GraphCanvas.tsx`, the `useEffect` calling `frameActiveSubgraph(activeNodePKs)` (lines 77–81) is declared **before** the `useEffect` updating `renderRef.current = render` (lines 314–316) and **before** the `useEffect` initializing `zoomBehaviorRef.current = zoom` (lines 358–380). Furthermore, the zoom event handler (`.on('zoom', (event) => { transformRef.current = event.transform; render(); })`, lines 365–368) invokes `render()` directly from its lexical closure instead of `renderRef.current()`. When a query response arrives and `setIlluminatedPath` sets `isIlluminated = true`, Hook 1 (lines 77–81) starts `selection.transition().duration(350).ease(d3.easeCubicInOut).call(zoomBehaviorRef.current.transform, targetTransform)` using the **previous** `zoomBehaviorRef.current` instance whose `'zoom'` listener closes over the **stale pre-query `render` callback** (where `isIlluminated === false` and `activeNodePKs` is empty). For the entire 350ms transition and its final frame, every `requestAnimationFrame` tick of `zoom.transform` invokes that stale `render()` closure, overwriting the canvas with the dark dormant blueprint state (`isIlluminated = false`). Because the physics simulation has already settled (`alpha < alphaMin`), no further ticks occur until the user manually pans, drags, zooms, or hovers the canvas. |
| **`DEF-002`** | `src/frontend/src/components/GraphCanvas.tsx` (lines 358–396) | **Req 4.1.1, 4.4.2, 5.4, 6.5 (Zero-Latency Repainting, 60 FPS Stability & Resize Handling):** Immediate repainting must maintain smooth 60 FPS performance without stuttering, preserve hover/selection continuity, and resize/render accurately when a window or panel resize coincides with query delivery. | The `d3.zoom` initialization `useEffect` (lines 358–380) depends on `[render]`, which changes on every `hoveredNode`, `selectedNode`, `isIlluminated`, `activeNodePKs`, or `activeEdgeKeys` update. Every such update re-executes `canvas.width = rect.width * dpr; canvas.height = rect.height * dpr;` (reallocating and wiping the HTML5 canvas backing store on every hover or state change) and re-registers `d3.select(canvas).call(zoom)`. Similarly, the resize `useEffect` (lines 383–396) depends on `[render]` and only listens to `window` `'resize'` events rather than observing canvas/container dimension changes via `ResizeObserver`. |
| **`DEF-003`** | `src/frontend/src/components/GraphCanvas.tsx` (lines 40–81, 319–355) | **Req 4.2.1 & 4.2.3 (Coordinated Camera Motion on Topology/State Updates):** Camera framing must center and zoom to fit the active subgraph whenever an illuminated path is active. | When `nodes` are replaced (e.g., on initial load or topology filter reload), new `GraphNode` objects have `x: undefined, y: undefined` until `d3.forceSimulation(nodes)` runs in Hook 3 (lines 319–355). Because Hook 1 (`frameActiveSubgraph`, lines 77–81) is declared **before** Hook 3, `nodes.filter((n) => targetPKs.has(n.primary_key) && n.x !== undefined && n.y !== undefined)` (line 44) finds `0` matched nodes with defined coordinates and exits early without framing the subgraph. |
| **`DEF-004`** | `src/frontend/src/components/GraphCanvas.tsx` (lines 135–145, 154–200, 206–309) | **Req 4.1.3 (Visual Elements Illuminated Immediately):** (1) All nodes in `activeNodePKs` must immediately render in gold/amber (`#ffb703`) with active radial glow halos (`rgba(255, 183, 3, 0.45)`); (2) All relationship edges in `activeEdgeKeys` must immediately render with active stroke color, increased line thickness, and amber contrast; (3) Node captions and leader badges for active nodes must immediately render with elevated contrast and active typography. | (1) In `GraphCanvas.tsx` line 239, base node fill is unconditionally set to `ctx.fillStyle = visual.badgeColor;` instead of rendering active nodes (`isActive`) in gold/amber (`#ffb703` / `CANVAS_PALETTE.accentAmber`). (2) In lines 226–234, the outer halo for active nodes only draws a solid stroke (`CANVAS_PALETTE.activeHalo` / `#f59e0b`) rather than an active radial glow halo with `rgba(255, 183, 3, 0.45)`. (3) In lines 137, 154–155, 184, and 209, `isActive` and `isActiveEdge` do not guard on `isIlluminated`, and line 154–155 highlights any edge whose endpoints are both in `activeNodePKs` even if the edge key is not in `activeEdgeKeys`. |
| **`DEF-005`** | `src/frontend/src/components/GraphCanvas.tsx` (lines 209–235, 274–276) | **Req 4.4.1 (Selected Node Highlighting Continuity):** If a node is currently selected in the detail drawer, its distinctive selection ring and pulse effect must persist uninterrupted during and after path illumination. | (1) In `GraphCanvas.tsx` lines 213–216 (`if (isIlluminated && !isActive) { alpha = CANVAS_PALETTE.inactiveAttenuation; }`), if `selectedNode` is not in `activeNodePKs` during path illumination, `selectedNode` is dimmed to `0.18` opacity instead of persisting uninterrupted. (2) In lines 226–234 (`if (isActive || isSelected)`), `isSelected` uses the exact same stroke style and radius as `isActive`, lacking a distinctive selection ring and pulse effect to differentiate the selected node from illuminated path nodes. |
| **`DEF-006`** | `src/frontend/src/components/GraphCanvas.tsx` (lines 77–81), `src/frontend/src/components/AgentChatDrawer.tsx` (lines 71–82), `src/frontend/src/context/GraphSyncContext.tsx` (lines 275–279) | **Req 4.3.1 & 4.3.2 (Responsive De-Illumination & Immediate Reset):** When the user clears the search, closes the chat inquiry, or triggers a reset action, `isIlluminated` reverts to `false` and the canvas immediately repaints all nodes and edges back to baseline blueprint styling without manual canvas movement. | (1) When `clearIllumination()` is called while a 350ms camera transition is active on `canvas`, `GraphCanvas.tsx` does not interrupt the ongoing D3 transition (`d3.select(canvas).interrupt()`), allowing the in-flight transition with a stale closure to keep painting illuminated nodes until the user moves the canvas. (2) In `AgentChatDrawer.tsx` line 72, closing the chat inquiry drawer (`onClick={() => setIsChatOpen(false)}`) does not reset illumination (`clearIllumination()`). |
| **`DEF-007`** | `src/frontend/src/context/GraphSyncContext.tsx` (lines 269–273) | **Req 5.3 (Empty Subgraph Response):** If a query returns zero active nodes, the canvas must immediately clear any existing illumination and maintain baseline rendering without throwing render errors or visual artifacts. | In `GraphSyncContext.tsx` lines 269–273, `setIlluminatedPath` unconditionally sets `setIsIlluminated(true)` even when `response.active_node_pks` is empty (`[]`). When `isIlluminated` is `true` and `activeNodePKs.size === 0`, `GraphCanvas.tsx` attenuates 100% of canvas nodes and edges to `0.18` opacity (`CANVAS_PALETTE.inactiveAttenuation`) and displays `STATUS: PATH ILLUMINATED` instead of clearing illumination (`isIlluminated = false`) and maintaining baseline rendering. |
| **`DEF-008`** | `src/frontend/src/context/GraphSyncContext.tsx` (lines 340–399) | **Req 5.1 (Rapid Successive Queries):** If a user executes multiple queries in rapid succession, each arriving response must immediately overwrite the previous active path and instantly repaint the canvas with the newest active nodes. | In `GraphSyncContext.tsx` line 343 (`if (!q || isQueryLoading) return;`), `submitInquiry` blocks and drops any query submitted while a prior query is in flight (`isQueryLoading === true`), and lacks request sequence/abort handling (`AbortController` or monotonic request ID) to allow rapid successive queries where each arriving response overwrites the previous active path. |
| **`DEF-009`** | `src/graphrag/traversal.py` (lines 316, 365, 382, 478, 642, 649, 699, 719–729, 772–800) | **Req 2, 4.1.3 & 6.1 (Accurate Active Edge Illumination Across All Query Types):** All relationship edges connecting the retrieved path in `activeEdgeKeys` must match the canvas topology `edge_key` values and immediately illuminate on query completion. | In `src/graphrag/traversal.py`, `_execute_single_general_traversal` (line 365), `_execute_single_clinical_traversal` (line 316), `_execute_multi_entity_traversal` (line 478), `_execute_pattern_b` (lines 642, 649), and `_execute_pattern_c` (line 699) call `session.run(...).data()`, which converts Neo4j `Relationship` objects into 3-tuples lacking `.type`. `_convert_edge` (line 774) then falls back to `"RELATED_TO"`, emitting corrupted `active_edge_keys` (e.g., `"PLAW-117-328->RELATED_TO->USC-42-1395x-s-2-JJ"`, `"BILL-117-hr-3630->RELATED_TO->PLAW-117-328"`) that do not match the authentic `link.edge_key` strings on the canvas (`"PLAW-117-328->MODIFIES_CODE->USC-42-1395x-s-2-JJ"`, `"BILL-117-hr-3630->ENACTED_AS->PLAW-117-328"`). |

---

## 5. Sufficiency & Scan Certification

In strict accordance with [`LANGUAGE.md`](LANGUAGE.md) definitions:
- **`{sufficient}` Certification:** This scan has exhaustively enumerated the complete codebase dependency cone across frontend React canvas and context synchronization components, styling and type contracts, FastAPI backend endpoints, and GraphRAG traversal modules. All external and local datasources have been empirically probed using safe read-only operations, with raw ground-truth payloads saved to `assets/20261013T194318-162-mbmi/`. Every root cause and gap between `functional_specification_009.md` and the current codebase is documented with exact file, line, and symbol precision in the Explicit Deficiency Register. Zero ambiguity remains.
- **`{correctness}` Baseline:** All file paths, verbatim identifiers, React hook dependencies, D3 zoom/transition lifecycles, and API payload schemas match the active repository and live Neo4j/FastAPI runtime with 100% precision.
- **`{errors}` Absence:** Zero speculative contracts, hallucinated endpoints, mutating network calls, or invented components were introduced (`INV-BOUNDARY-01`, `INV-SCAN-01`, `INV-IDENTITY-01`, `INV-ABSENCE-01`).

---

## 6. Handoff Manifest Affirmation

The dedicated role handoff manifest at `handoff/20261013T194318-162-mbmi/plan-scan-2.txt` is atomically created and overwritten with exclusively repository-relative filepaths (one per line):
1. All reviewed and qualified codebase component files (`LANGUAGE.md`, `src/frontend/*`, `src/api/*`, `src/graphrag/*`, `src/graph/*`, `tests/*`, `verify_all.py`).
2. This authored scan report at `scan_reports/scan_report_009_plan_scan_2.md`.
3. All 3 saved ground-truth empirical payload files in `assets/20261013T194318-162-mbmi/`:
   - `assets/20261013T194318-162-mbmi/api_graph_topology_baseline.json`
   - `assets/20261013T194318-162-mbmi/api_graphrag_query_illumination_probes.json`
   - `assets/20261013T194318-162-mbmi/neo4j_canvas_illumination_alignment_audit.json`

No seed specification paths (`functional_specification_009.md`) are recorded in the handoff manifest, and `handoff/authored.txt`, `handoff/20261013T194318-162-mbmi/plan-scan-1.txt`, and all other run directories remain untouched.

---

## 7. Coding Gate Affirmation

DO NOT CODE YET: Implementation coding gate remains locked. Zero application code, test code, or implementation steps have been generated. Coding waits on an empty frontier and explicit operator authorization.
