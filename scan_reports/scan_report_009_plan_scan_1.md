# Deterministic Codebase Static Scan, External API Reconnaissance & Empirical Schema Audit Report (Agent 1: `plan-scan-1`)

**Run ID:** `20261013T194318-162-mbmi`  
**Node / Role:** Planning Node (`plan-scan-1`, Agent 1)  
**Governing Specification:** `functional_specification_009.md`  
**Taxonomy Reference:** `LANGUAGE.md`  
**Gate Status:** STRICT "DO NOT CODE YET" (`INV-BOUNDARY-01`)

---

## 1. Governing Context

### 1.1 Single Seed Specification Consumed
- **`functional_specification_009.md`** (*Functional Specification: Immediate Synchronous Visualizer Illumination and Zero-Latency Canvas State Synchronization*).
- Consumed directly from repository root (`functional_specification_009.md`). No other specifications or `handoff/authored.txt` entries were scanned (`INV-HANDOFF-01`).

### 1.2 Wayfinder Map & Tickets Inspected
- **Wayfinder Map Path:** `wayfinder/20261013T194318-162-mbmi/map.md` (Not yet created prior to `plan-scan-1` execution; `plan-scan-1` is the upstream reconnaissance node for run `20261013T194318-162-mbmi`).
- **Wayfinder Tickets Path:** `wayfinder/20261013T194318-162-mbmi/tickets/` (`0` pre-existing ticket files at scan time).

### 1.3 Strict Alignment with `LANGUAGE.md` Evaluation Parameters
All observations and evaluations in this report adhere strictly to the definitions in `LANGUAGE.md`:
- **`{errors}`:** Explicit failure states surfaced during execution of a component, including stack traces, syntax errors, unhandled exceptions, non-zero exit codes, fatal timeouts, or canvas rendering failures where the canvas displays stale/unilluminated state after query resolution, active nodes remain dark until manual user interaction, canvas fails to redraw upon state commit, camera transitions decouple from visual highlights, or canvas rendering freezes.
- **`{correctness}`:** The precise, local execution of a specific component, verifying that it performs its designated task without logical flaws—specifically that state transitions in `activeNodePKs`, `activeEdgeKeys`, or `isIlluminated` immediately produce an exact visual update on the HTML5 `<canvas>`, accurately rendering node colors, glow halos, line weights, and leader badges.
- **`{functionality}`:** The broader, global objective or business logic the component is meant to achieve within the larger system: a responsive visual synchronization system where every graph state transition (query illumination, clearing illumination, node selection, or filtering) is visually reflected on screen in real time without requiring manual user interaction to force a repaint.
- **`{correct required outputs}`:** The exact, literal expected state after a component executes successfully:
  1. Instantaneous illumination of active nodes in gold/amber (`#ffb703`) with active radial glow halos (`rgba(255, 183, 3, 0.45)`) upon query response arrival.
  2. Instantaneous illumination of active relationship edges (`activeEdgeKeys`) connecting the retrieved path.
  3. Automatic smooth camera transition centering and framing the illuminated subgraph while rendering active highlights on every intermediate animation frame and the final stabilized frame.
  4. Instantaneous clearing of illuminated highlights when the illumination state is reset (`clearIllumination`, search clear, or closing chat inquiry).
  5. Zero requirement for manual mouse movement, dragging, clicking, or zooming to trigger the display of query results.
- **`{sufficient}`:** The state of documentation where absolutely no ambiguity remains, all necessary file structures and dependencies are listed, empirical schemas are verified with ground-truth payloads, and `{correct required outputs}` are established.
- **`{insufficient}`:** The state of documentation where critical context is missing, ambiguous, or contradictory, requiring assumptions to write code.

---

## 2. Master Component Dependency Cone Register

Every component listed below physically exists in the repository under its verbatim path and symbol names and was directly inspected during this static scan.

| Component ID | Repository-Relative Path | Verbatim Symbols & Interfaces | Role in Dependency Cone & Grounding Justification |
| :--- | :--- | :--- | :--- |
| **`COMP-FE-01`** | `src/frontend/src/components/GraphCanvas.tsx` | `GraphCanvasProps` (`nodes: GraphNode[]`, `links: GraphLink[]`, `loading: boolean`), `GraphCanvas`, `canvasRef`, `simulationRef`, `transformRef`, `zoomBehaviorRef`, `renderRef`, `hoveredNode`, `fps`, `isHudOpen`, `frameActiveSubgraph(targetPKs: Set<string>)`, `render()`, `handlePointerDown(e)`, `handlePointerMove(e)` | Core HTML5 2D `<canvas>` force-directed visualizer component. Consumes `activeNodePKs`, `activeEdgeKeys`, `isIlluminated`, `selectedNode`, and `selectNode` from `useGraphSync()`. Manages the `d3.forceSimulation`, `d3.zoom` behavior, 350ms `d3.easeCubicInOut` viewport framing transition, node/edge/halo/caption drawing loop (`render`), window resize listener, and Blueprint HUD overlay (`STATUS: PATH ILLUMINATED` vs `EXPLORATION MODE`). Directly governs Requirements 4.1, 4.2, 4.3, 4.4, and Section 5. |
| **`COMP-FE-02`** | `src/frontend/src/context/GraphSyncContext.tsx` | `ChatMessage`, `StateOption`, `JurisdictionMetadata`, `DME_JURISDICTIONS`, `STATE_TO_JURISDICTION`, `ALL_STATES_SORTED`, `GraphSyncContextType`, `GraphSyncProvider`, `useGraphSync`, `activeNodePKs`, `activeEdgeKeys`, `selectedNode`, `seededAnchor`, `isIlluminated`, `quickPrompts`, `filterJurisdiction`, `filterState`, `availableStates`, `policyKeyword`, `isChatOpen`, `messages`, `isQueryLoading`, `errorMsg`, `focusTarget`, `selectNode`, `setIlluminatedPath`, `clearIllumination`, `illuminateJurisdiction`, `setFilterJurisdiction`, `setFilterState`, `submitInquiry`, `inquireNode` | Bidirectional Canvas-Agent Synchronization Bus React context provider. Owns state for `activeNodePKs: Set<string>`, `activeEdgeKeys: Set<string>`, `isIlluminated: boolean`, `selectedNode: GraphNode | null`, and `isChatOpen: boolean`. Executes `fetch('/api/graphrag/query')` inside `submitInquiry` and commits `setIlluminatedPath(data)`. Exposes `clearIllumination()` and `inquireNode(node)`. Directly governs Requirements 4.1, 4.3, 4.4, and Section 5. |
| **`COMP-FE-03`** | `src/frontend/src/components/AgentChatDrawer.tsx` | `AgentChatDrawer`, `inputQuery`, `modelId`, `handleSend(queryText?: string)` | Conversational GraphRAG assistant drawer component. Consumes `isChatOpen`, `setIsChatOpen`, `quickPrompts`, `messages`, `isQueryLoading`, `errorMsg`, `submitInquiry`, and `seededAnchor` from `useGraphSync()`. Renders telemetry badge (`msg.responsePayload.duration_ms` and `msg.responsePayload.active_node_pks.length` *"Nodes Illuminated"*) and drawer close button (`✕`). Touches Requirement 4.1 and Requirement 4.3.1 (closing chat inquiry). |
| **`COMP-FE-04`** | `src/frontend/src/components/NodeDetailDrawer.tsx` | `NodeDetailDrawerProps` (`nodes: GraphNode[]`, `links: GraphLink[]`), `NodeDetailDrawer`, `connectedNeighbors`, `getGovernmentSourceLink()` | Entity inspection drawer rendered when `selectedNode` is non-null. Contains the one-click action button `"◈ INQUIRE IN GRAPHRAG CHAT"` (`onClick={() => selectedNode && inquireNode(selectedNode)}`) and neighbor selection links (`selectNode(cn.neighborNode)`). Touches Requirement 1, Requirement 4.4.1, and Acceptance Criterion 1. |
| **`COMP-FE-05`** | `src/frontend/src/components/FilterToolbar.tsx` | `FilterToolbarProps` (`onReloadTopology: (state: string, policy: string, jurisdiction: string) => void`), `FilterToolbar`, `handleJurisdictionChange`, `handleStateChange`, `handlePolicyChange` | Top navigation filter toolbar. Consumes `filterJurisdiction`, `setFilterJurisdiction`, `filterState`, `setFilterState`, `availableStates`, `policyKeyword`, `setPolicyKeyword`, `isIlluminated`, `clearIllumination`, `isChatOpen`, and `setIsChatOpen` from `useGraphSync()`. Renders `"✕ RESET PATH"` button (`onClick={clearIllumination}`) when `isIlluminated` is true, and `"◈ GRAPHRAG CHAT"` toggle button. Touches Requirements 4.1 and 4.3. |
| **`COMP-FE-06`** | `src/frontend/src/styles/graph_theme.ts` | `NodeVisualConfig`, `NODE_THEME_REGISTRY`, `CANVAS_PALETTE` (`bgVoid: '#0a1128'`, `gridLines: 'rgba(30, 41, 59, 0.45)'`, `accentAmber: '#ffb703'`, `activeHalo: '#f59e0b'`, `activeEdge: '#fbbf24'`, `inactiveAttenuation: 0.18`, `textPrimary: '#f8fafc'`, `textMuted: '#94a3b8'`, `panelBg: 'rgba(15, 23, 42, 0.92)'`, `panelBorder: '#1e293b'`), `getNodeVisual(label: string)` | Authoritative visual theme registry for all 14 node labels (`Policy`, `Bill`, `PublicLaw`, `StatutorySection`, `Regulation`, `ChangeRequest`, `CoveragePolicy`, `HCPCSCode`, `ICD10Code`, `Jurisdiction`, `State`, `FeeScheduleEntry`, `LobbyingFiling`, `LiteratureStudy`) and canvas color palette constants consumed by `GraphCanvas.tsx`. Touches Requirement 4.1.3 and 4.3.2. |
| **`COMP-FE-07`** | `src/frontend/src/types/graph.ts` | `NodeProperties`, `EdgeProvenance`, `GraphNode`, `GraphLink`, `AnchorEntity`, `GraphRAGQueryResponse`, `GraphSummary` | TypeScript interfaces defining graph nodes (`primary_key`, `label`, `name`, `properties`, `radius`, `color`, `shape`, `x`, `y`, `vx`, `vy`, `fx`, `fy`), edges (`source`, `target`, `label`, `edge_key`, `provenance`), and `GraphRAGQueryResponse` (`answer`, `active_node_pks`, `active_edge_keys`, `anchors`, `provenance_sources`, `duration_ms`). |
| **`COMP-FE-08`** | `src/frontend/src/utils/promptGenerator.ts` | `constructInquiryPrompt(node: GraphNode): string` | Pure utility generating deterministic natural-language prompts with bracketed `[primary_key]` citations across all 14 entity labels when `inquireNode(node)` is triggered via `"◈ INQUIRE IN GRAPHRAG CHAT"`. |
| **`COMP-FE-09`** | `src/frontend/src/App.tsx` | `RawTopologyNode`, `RawTopologyEdge`, `RawTopologyResponse`, `MainVisualizer`, `fetchTopology(stateFilter, policy, jurisdictionFilter)`, `App` | Root application component wrapping `MainVisualizer` in `GraphSyncProvider`. Fetches `/api/graph/topology` and transforms raw API nodes/edges into `GraphNode[]` and `GraphLink[]` passed to `GraphCanvas` and `NodeDetailDrawer`. |
| **`COMP-FE-10`** | `src/frontend/src/main.tsx` | `createRoot(document.getElementById('root')!).render(<StrictMode><App /></StrictMode>)` | React 19 DOM entry point mounting `App` inside `React.StrictMode`. |
| **`COMP-FE-11`** | `src/frontend/src/index.css` | `:root` CSS variables (`--bg-void: #0a1128`, `--text-main: #f8fafc`, `--accent-amber: #ffb703`, `--border-slate: #1e293b`), `#root` layout rules | Global stylesheet establishing full-viewport (`100vw` x `100vh`, `overflow: hidden`) container layout for the visualizer canvas. |
| **`COMP-FE-12`** | `src/frontend/vite.config.ts` | `defineConfig` (`server.port: 5173`, `server.proxy['/api'].target: 'http://localhost:8000'`) | Vite frontend dev server and `/api` reverse-proxy configuration. |
| **`COMP-FE-13`** | `src/frontend/package.json` | Dependencies: `react` (`^19.2.8`), `react-dom` (`^19.2.8`), `d3` (`^7.9.0`), `lucide-react` (`^1.55.0`); Scripts: `dev`, `build`, `lint`, `preview` | Frontend package manifest and build toolchain configuration. |
| **`COMP-BE-01`** | `src/api/routes.py` | `router`, `set_sync_engine`, `get_sync_engine`, `get_pipeline`, `get_neo4j_session`, `health_check` (`GET /api/health`), `get_graph_summary` (`GET /api/graph/summary`), `get_graph_topology` (`GET /api/graph/topology`), `resolve_entities` (`POST /api/entities/resolve`), `get_subgraph_by_anchors` (`POST /api/graphrag/subgraph`), `execute_graphrag_query` (`POST /api/graphrag/query`) | FastAPI REST router serving graph topology and executing GraphRAG queries that return `active_node_pks` and `active_edge_keys` to the frontend. |
| **`COMP-BE-02`** | `src/api/models.py` | `HealthResponse`, `TopologyNode`, `TopologyEdge`, `TopologyResponse`, `EntityResolveRequest`, `EntityResolveResponse`, `SubgraphRequest`, `SubgraphResponse`, `ErrorEnvelope` | Pydantic response and request models for `/api/graph/topology`, `/api/graphrag/subgraph`, and `/api/entities/resolve`. |
| **`COMP-BE-03`** | `src/api/server.py` | `lifespan`, `create_app`, `http_exception_handler`, `graphrag_exception_handler`, `app` | FastAPI server entrypoint managing Neo4j connection lifecycle, CORS middleware, and standardized JSON error envelopes. |
| **`COMP-GR-01`** | `src/graphrag/models.py` | `AnchorEntity`, `ResolvedAnchors`, `TraversalNode`, `TraversalEdge`, `TraversalResult`, `GraphRAGQueryRequest`, `GraphRAGQueryResponse` | Core Pydantic data models for the 5-stage GraphRAG pipeline and canvas illumination payload (`active_node_pks: List[str]`, `active_edge_keys: List[str]`). |
| **`COMP-GR-02`** | `src/graphrag/pipeline.py` | `GraphRAGPipeline`, `execute_query(request: GraphRAGQueryRequest, session: Session) -> GraphRAGQueryResponse` | Orchestrates entity resolution, topological subgraph traversal, context assembly, and LLM synthesis, returning `GraphRAGQueryResponse`. |
| **`COMP-GR-03`** | `src/graphrag/traversal.py` | `TopologicalTraversalEngine`, `extract_connecting_subgraph`, `_execute_single_entity_traversal`, `_execute_jurisdiction_traversal`, `_execute_single_state_traversal`, `_execute_single_clinical_traversal`, `_execute_single_general_traversal`, `_execute_multi_entity_traversal`, `_execute_pattern_a`, `_execute_pattern_b`, `_execute_pattern_c`, `_convert_node`, `_convert_edge` | Neo4j Cypher traversal engine computing `active_node_pks` and `active_edge_keys` (`{source_pk}->{rel_type}->{target_pk}`). |
| **`COMP-GR-04`** | `src/graphrag/entity_linker.py` | `EntityAnchorLinker`, `resolve_anchors`, `resolve_explicit_anchor` | Deterministic multi-slot entity anchor resolver and explicit `primary_key` anchor validator against Neo4j. |
| **`COMP-GR-05`** | `src/graphrag/context_assembler.py` | `GraphContextAssembler`, `assemble_context` | Formats traversed graph nodes, fee schedules, and edge provenance into structured Markdown sections for synthesis. |
| **`COMP-GR-06`** | `src/graphrag/synthesizer.py` | `HuggingFaceSynthesizer`, `synthesize`, `_call_hf_inference_api` | Invokes Hugging Face Router Chat Completions API (`https://router.huggingface.co/v1/chat/completions`) to synthesize grounded responses. |
| **`COMP-GR-07`** | `src/graphrag/exceptions.py` | `GraphRAGException`, `EntityResolutionError`, `TraversalError`, `ModelInferenceError`, `ModelAuthenticationError`, `ModelRateLimitError`, `GraphValidationError` | Fail-fast exception hierarchy for the GraphRAG pipeline. |
| **`COMP-DB-01`** | `src/graph/neo4j_sync.py` | `Neo4jSyncEngine`, `get_driver`, `close`, `init_schema`, `sync_graph_dict`, `sync_file`, `get_summary_statistics` | Neo4j Bolt driver manager (`bolt://localhost:7687`) and schema initializer. |
| **`COMP-TEST-01`** | `tests/test_api_endpoints.py` | `test_api_health`, `test_api_graph_summary`, `test_api_graph_topology`, `test_api_entities_resolve`, `test_api_graphrag_subgraph`, `test_api_graphrag_query`, `test_api_single_state_and_subgraph`, `test_api_graphrag_query_explicit_anchor_plaw`, `test_api_graphrag_query_all_14_entity_types`, `test_api_graphrag_query_invalid_anchor_fails_fast` | FastAPI endpoint integration test suite verifying REST contracts and `active_node_pks` / `active_edge_keys` payloads. |
| **`COMP-TEST-02`** | `tests/test_graphrag_pipeline.py` | `test_oracle_1_patient_benefit_routing`, `test_oracle_2_no_keyword_bridging`, `test_oracle_3_cross_policy_convergence`, `test_oracle_4_zero_orphan_invariant`, `test_oracle_5_edge_provenance_completeness`, `test_oracle_6_fail_fast_error_boundaries`, `test_single_state_query_ny`, `test_latency_benchmark_harness`, `test_single_entity_general_traversal_integrity` | Pipeline verification suite validating the 6 domain oracles and traversal latency. |

---

## 3. Candidate External Datasource & Schema Audit Register

Active read-only reconnaissance was executed against the local FastAPI / Neo4j / Hugging Face GraphRAG service stack to verify endpoint availability, status codes, and authentic payload schemas consumed by the frontend visualizer. All raw, unedited responses were captured to `assets/20261013T194318-162-mbmi/`.

### 3.1 Endpoint 1: Health & Neo4j Connectivity Probe (`GET /api/health`)
- **Endpoint URI:** `/api/health` (backed by Neo4j at `bolt://localhost:7687`)
- **HTTP Method:** `GET` (Read-Only)
- **Authentication:** None on local REST route; Neo4j driver uses `NEO4J_URI` (`bolt://localhost:7687`), `NEO4J_USERNAME` (`neo4j`), `NEO4J_PASSWORD`.
- **Observed HTTP Status:** `200 OK`
- **Saved Ground-Truth Payload File:** `assets/20261013T194318-162-mbmi/api_health_response.json`
- **Empirical Schema Audit (`HealthResponse`):**
  - `status`: `string` (non-null, observed `"ok"`)
  - `neo4j_connected`: `boolean` (non-null, observed `true`)
  - `timestamp`: `string` (non-null, ISO-8601 UTC timestamp, observed `"2026-10-13T19:46:11.107350+00:00"`)

### 3.2 Endpoint 2: Visualizer Canvas Topology Feed (`GET /api/graph/topology?policy_keyword=LTA`)
- **Endpoint URI:** `/api/graph/topology?policy_keyword=LTA`
- **HTTP Method:** `GET` (Read-Only)
- **Pagination / Query Parameters:**
  - `policy_keyword`: optional `string` (default `"LTA"`)
  - `include_fee_schedules`: optional `boolean` (default `false`)
  - `jurisdiction_filter`: optional `string | null` (default `null`)
  - `state_filter`: optional `string | null` (default `null`)
- **Observed HTTP Status:** `200 OK`
- **Saved Ground-Truth Payload File:** `assets/20261013T194318-162-mbmi/api_graph_topology_lta.json`
- **Empirical Schema Audit (`TopologyResponse`):**
  - `nodes`: `Array<TopologyNode>` (non-null, observed `155` items when `state_filter` is omitted)
    - `nodes[].primary_key`: `string` (non-null, e.g., `"POLICY-LTA"`, `"PLAW-117-328"`, `"CMS-MCD-A59508"`, `"STATE-WI"`, `"HCPCS-A6522"`, `"ICD10-I97.2"`)
    - `nodes[].label`: `string` (non-null, one of the 14 domain entity labels)
    - `nodes[].name`: `string` (non-null, human-readable display name)
    - `nodes[].properties`: `object` (non-null dictionary of entity attributes)
  - `edges`: `Array<TopologyEdge>` (non-null, observed `163` items)
    - `edges[].source_pk`: `string` (non-null)
    - `edges[].target_pk`: `string` (non-null)
    - `edges[].label`: `string` (non-null relationship type, e.g., `"TARGETS_BILL"`, `"ENACTED_AS"`, `"MODIFIES_CODE"`, `"IMPLEMENTED_BY"`, `"ISSUES_TRANSMITTAL"`, `"MANDATES_POLICY"`, `"APPLIES_TO_JURISDICTION"`, `"COVERS_STATE"`, `"GOVERNS"`, `"ALLOWS_DIAGNOSIS"`)
    - `edges[].edge_key`: `string` (non-null composite key `{source_pk}->{label}->{target_pk}`)
    - `edges[].provenance`: `object` (`source_uri: string`, `selector: string`, `ingestion_timestamp: string`, `run_id: string`)
  - `total_nodes`: `integer` (non-null, observed `155`)
  - `total_edges`: `integer` (non-null, observed `163`)

### 3.3 Endpoint 3: Conversational GraphRAG Query (`POST /api/graphrag/query` — Natural Language Chat Prompt)
- **Endpoint URI:** `/api/graphrag/query` (orchestrates Neo4j read-only Cypher traversal and Hugging Face Router API `https://router.huggingface.co/v1/chat/completions`)
- **HTTP Method:** `POST` (Read-Only Query & Inference)
- **Authentication:** Uses `HF_TOKEN` / `HUGGINGFACE_API_KEY` environment variable for upstream Hugging Face Router inference.
- **Observed HTTP Status:** `200 OK`
- **Saved Ground-Truth Payload File:** `assets/20261013T194318-162-mbmi/api_graphrag_query_chat_prompt.json`
- **Empirical Schema Audit (`GraphRAGQueryResponse`):**
  - `answer`: `string` (non-null synthesized markdown answer citing bracketed primary keys and `$290.47` / `$58.09` fee figures)
  - `active_node_pks`: `Array<string>` (non-null, observed `7` items: `["CMS-CR-13286", "CMS-MCD-A59508", "FEE-A6522-WI-NR-2024", "HCPCS-A6522", "ICD10-I97.2", "JURIS-DME-B", "STATE-WI"]`)
  - `active_edge_keys`: `Array<string>` (non-null, observed `7` items: `["CMS-CR-13286->APPLIES_TO_JURISDICTION->JURIS-DME-B", "CMS-CR-13286->MANDATES_POLICY->CMS-MCD-A59508", "CMS-MCD-A59508->ALLOWS_DIAGNOSIS->ICD10-I97.2", "CMS-MCD-A59508->GOVERNS->HCPCS-A6522", "FEE-A6522-WI-NR-2024->APPLIES_TO->STATE-WI", "HCPCS-A6522->HAS_FEE_SCHEDULE->FEE-A6522-WI-NR-2024", "JURIS-DME-B->COVERS_STATE->STATE-WI"]`)
  - `anchors`: `Array<AnchorEntity>` (non-null, each item containing `slot: string`, `primary_key: string`, `matched_text: string`, `entity_type: string`, `label: string`)
  - `provenance_sources`: `Array<object>` (non-null, each item containing `source_uri: string`, `selector: string`, `ingestion_timestamp: string`, `run_id: string`)
  - `duration_ms`: `number` (float, non-null, observed `8481.13`)

### 3.4 Endpoint 4: One-Click Node Inquiry (`POST /api/graphrag/query` — Explicit `primary_key` Bypass)
- **Endpoint URI:** `/api/graphrag/query`
- **HTTP Method:** `POST` (Read-Only Query & Inference)
- **Request Payload:** `{"query": "Explain the statutory authority and enacted healthcare provisions of [PLAW-117-328] (Consolidated Appropriations Act, 2023).", "model_id": "meta-llama/Meta-Llama-3-8B-Instruct", "primary_key": "PLAW-117-328"}`
- **Observed HTTP Status:** `200 OK`
- **Saved Ground-Truth Payload File:** `assets/20261013T194318-162-mbmi/api_graphrag_query_one_click_inquire.json`
- **Empirical Schema Audit (`GraphRAGQueryResponse`):**
  - `answer`: `string` (non-null)
  - `active_node_pks`: `Array<string>` (non-null, observed `6` items: `["BILL-117-hr-2617", "BILL-117-hr-3630", "BILL-117-hr-3808", "PLAW-117-328", "USC-42-1395x-s-2-JJ", "USC-42-1395x-s-2-Z"]`)
  - `active_edge_keys`: `Array<string>` (non-null, observed `5` items: `["BILL-117-hr-2617->RELATED_TO->PLAW-117-328", "BILL-117-hr-3630->RELATED_TO->PLAW-117-328", "BILL-117-hr-3808->RELATED_TO->PLAW-117-328", "PLAW-117-328->RELATED_TO->USC-42-1395x-s-2-JJ", "PLAW-117-328->RELATED_TO->USC-42-1395x-s-2-Z"]`)
  - `anchors`: `Array<AnchorEntity>` (non-null, `1` item for `PLAW-117-328`)
  - `provenance_sources`: `Array<object>` (non-null, `1` item)
  - `duration_ms`: `number` (float, non-null, observed `11278.12`)

### 3.5 Endpoint 5: Subgraph Retrieval Empty-Anchor Boundary (`POST /api/graphrag/subgraph`)
- **Endpoint URI:** `/api/graphrag/subgraph`
- **HTTP Method:** `POST` (Read-Only)
- **Request Payload:** `{"anchors": []}`
- **Observed HTTP Status:** `200 OK`
- **Saved Ground-Truth Payload File:** `assets/20261013T194318-162-mbmi/api_graphrag_subgraph_empty.json`
- **Empirical Schema Audit (`SubgraphResponse`):**
  - `nodes`: `Array<TopologyNode>` (observed `[]`)
  - `edges`: `Array<TopologyEdge>` (observed `[]`)
  - `active_node_pks`: `Array<string>` (observed `[]`)
  - `active_edge_keys`: `Array<string>` (observed `[]`)
  - `retrieval_ms`: `number` (float, observed `0.0`)

---

## 4. Explicit Deficiency Register (`INV-ABSENCE-01`)

In strict accordance with `INV-ABSENCE-01` and `RULE[user_global]`, the following deficiencies between the requirements of `functional_specification_009.md` and the current codebase were deterministically identified and verified directly against source files and live payloads:

### `DEF-009-01`: Stale `d3.zoom` Closure and `useEffect` Ordering Race Overwriting Canvas Illumination During Camera Transition
- **Governing Specification Requirements:** Section 1 (Problem Statement 1 & 2, Desired Solution 1–3), Section 4.1.1 (Trigger Condition), Section 4.1.2 (Zero Interaction Dependency), Section 4.2.1–4.2.3 (Synchronized Viewport Framing), Section 5.2 (Simulation Settled State), Acceptance Criteria 1 & 3.
- **Touched Component:** `src/frontend/src/components/GraphCanvas.tsx` (lines 40–81, 314–316, 358–380).
- **Verified Empirical Root Cause:**
  1. In `GraphCanvas.tsx`, the `render` callback (lines 84–312) depends on `[nodes, links, isIlluminated, activeNodePKs, activeEdgeKeys, selectedNode, hoveredNode]`.
  2. When a GraphRAG query resolves and `setIlluminatedPath(data)` commits new `activeNodePKs`, `activeEdgeKeys`, and `isIlluminated = true`, React recreates `render` (`render_NEW`) and runs `useEffect` hooks in declaration order:
     - **Effect #1 (lines 77–81)** runs **first**: `if (isIlluminated && activeNodePKs.size > 0) { frameActiveSubgraph(activeNodePKs); }`.
     - Inside `frameActiveSubgraph` (lines 70–73), `selection.transition().duration(350).ease(d3.easeCubicInOut).call(zoomBehaviorRef.current.transform, targetTransform)` is invoked.
     - At the moment Effect #1 executes, **Effect #4 (lines 358–380)** has **not yet run** for the current render cycle. Consequently, `zoomBehaviorRef.current` still points to the **previous** `d3.zoom` instance (`zoom_OLD`), whose `.on('zoom', ...)` listener closes over the **stale** `render` callback (`render_OLD`, where `isIlluminated === false` and `activeNodePKs` is an empty `Set`).
     - **Effect #4 (lines 358–380)** then runs with `[render]`, creates a new `d3.zoom` instance (`zoom_NEW`), re-binds DOM listeners via `d3.select(canvas).call(zoom_NEW)`, resets `canvas.width` and `canvas.height` (lines 376–377), and calls `render_NEW()` once at `t = 0ms`.
     - However, over the next `350ms` (`t = 16ms ... 350ms`), the active D3 transition scheduled in Effect #1 invokes `zoom_OLD.transform` on every animation frame, which dispatches `'zoom'` events to `zoom_OLD`'s internal listener—calling `render_OLD()` (`isIlluminated = false`, `activeNodePKs = Set(0)`) on every frame through completion of the 350ms transition.
     - Because the `d3.forceSimulation` has already settled (`alpha < alphaMin`) by the time the query response arrives (~8–11 seconds), `simulation.on('tick', () => renderRef.current())` is idle and never repaints the canvas after the transition finishes.
     - As a result, the canvas is left painted in its dormant, unilluminated state until the user manually interacts with the `<canvas>` (e.g., dragging, panning, zooming, or hovering a node), which triggers `zoom_NEW` on the DOM element and finally invokes `render_NEW()`.

### `DEF-009-02`: Re-Initialization of `d3.zoom` and Canvas Bitmap Buffer Reset on Every State / Hover Render Change
- **Governing Specification Requirements:** Section 4.1.1, Section 4.2.2, Section 4.4.2 (Hover Interaction During Illumination), Section 5.4 (Canvas Resizing During Query Delivery), Acceptance Criterion 5 (Frame Rate Stability).
- **Touched Component:** `src/frontend/src/components/GraphCanvas.tsx` (lines 358–380, 383–396).
- **Verified Empirical Root Cause:**
  - `useEffect` at lines 358–380 has `[render]` as its dependency array. Because `render` depends on `[nodes, links, isIlluminated, activeNodePKs, activeEdgeKeys, selectedNode, hoveredNode]`, every change to `hoveredNode` (on `mousemove`), `selectedNode`, `isIlluminated`, `activeNodePKs`, or `activeEdgeKeys` re-executes lines 358–380:
    1. Recreating a new `d3.zoom()` behavior and re-attaching it to the canvas (`d3.select(canvas).call(zoom)`).
    2. Resetting `canvas.width = rect.width * dpr` and `canvas.height = rect.height * dpr` (lines 376–377), which reallocates the HTML5 canvas backing store on every state or hover transition instead of only on initial mount and viewport/container resize events (`ResizeObserver` / `window` resize), and does not synchronize `d3.select(canvas)`'s internal `__zoom` state with `transformRef.current`.

### `DEF-009-03`: Active Node Base Fill Color and Radial Glow Halo Do Not Match Specification Palette Contract
- **Governing Specification Requirements:** Section 4.1.3 (Visual Elements Illuminated Immediately) and Section 4.4.1 (Selected Node Highlighting).
- **Touched Component:** `src/frontend/src/components/GraphCanvas.tsx` (lines 225–240) and `src/frontend/src/styles/graph_theme.ts` (lines 99–110).
- **Verified Empirical Root Cause:**
  1. Requirement 4.1.3 mandates: *"All nodes whose primary keys belong to `activeNodePKs` must immediately render in gold/amber (`#ffb703`) with active radial glow halos (`rgba(255, 183, 3, 0.45)`)."*
  2. In `GraphCanvas.tsx` line 239, base node fill is unconditionally set to `ctx.fillStyle = visual.badgeColor;` rather than rendering active nodes (`isActive`) in gold/amber (`#ffb703` / `CANVAS_PALETTE.accentAmber`).
  3. In `GraphCanvas.tsx` lines 226–234, the outer halo for `if (isActive || isSelected)` draws a single stroke ring with `CANVAS_PALETTE.activeHalo` (`#f59e0b`) rather than an active radial glow halo using `rgba(255, 183, 3, 0.45)` for active nodes and a distinct persistent selection ring/pulse effect for `selectedNode` (Requirement 4.4.1: *"If a node is currently selected in the detail drawer, its distinctive selection ring and pulse effect must persist uninterrupted during and after path illumination"*).

### `DEF-009-04`: Closing the Chat Inquiry Drawer Does Not Revert `isIlluminated` to `false`
- **Governing Specification Requirements:** Section 4.3.1 (Immediate Reset: *"When the user clears the search, closes the chat inquiry, or triggers a reset action, `isIlluminated` reverts to false"*) and Section 4.3.2 (Autonomous Repaint on Clear).
- **Touched Components:** `src/frontend/src/components/AgentChatDrawer.tsx` (line 72), `src/frontend/src/components/FilterToolbar.tsx` (line 163), and `src/frontend/src/context/GraphSyncContext.tsx` (lines 201, 275–279).
- **Verified Empirical Root Cause:**
  - In `AgentChatDrawer.tsx` line 72, the close button handler `onClick={() => setIsChatOpen(false)}` only sets `isChatOpen` to `false` without calling `clearIllumination()` (and `setIsChatOpen` in `GraphSyncContext.tsx` does not clear illumination when transitioning `isChatOpen` to `false`), leaving `isIlluminated` as `true` and keeping the canvas dimmed/highlighted after the chat inquiry is closed.

### `DEF-009-05`: Empty Subgraph Response Sets `isIlluminated = true` Instead of Clearing Illumination
- **Governing Specification Requirements:** Section 5.3 (Empty Subgraph Response: *"If a query returns zero active nodes, the canvas must immediately clear any existing illumination and maintain baseline rendering without throwing render errors or visual artifacts"*).
- **Touched Component:** `src/frontend/src/context/GraphSyncContext.tsx` (lines 269–273).
- **Verified Empirical Root Cause:**
  - In `GraphSyncContext.tsx` lines 269–273:
    ```ts
    const setIlluminatedPath = useCallback((response: GraphRAGQueryResponse) => {
      setActiveNodePKs(new Set(response.active_node_pks));
      setActiveEdgeKeys(new Set(response.active_edge_keys));
      setIsIlluminated(true);
    }, []);
    ```
  - When `response.active_node_pks` is empty (`length === 0`), `setIlluminatedPath` still sets `isIlluminated` to `true` instead of reverting `isIlluminated` to `false` (`clearIllumination()`). When `isIlluminated === true` and `activeNodePKs.size === 0`, `GraphCanvas.tsx` (lines 167, 215) attenuates 100% of nodes and edges to `0.18` opacity instead of maintaining baseline rendering.

### `DEF-009-06`: Rapid Successive Queries Blocked / Unsynchronized in `submitInquiry`
- **Governing Specification Requirements:** Section 5.1 (Rapid Successive Queries: *"If a user executes multiple queries in rapid succession, each arriving response must immediately overwrite the previous active path and instantly repaint the canvas with the newest active nodes"*).
- **Touched Component:** `src/frontend/src/context/GraphSyncContext.tsx` (lines 340–399).
- **Verified Empirical Root Cause:**
  - In `GraphSyncContext.tsx` line 343, `if (!q || isQueryLoading) return;` drops any query submitted while `isQueryLoading` is true, and there is no request sequence counter or `AbortController` to ensure that rapid successive queries are accepted and that each arriving response (or the latest response) deterministically overwrites the previous active path without out-of-order race conditions.

### `DEF-009-07`: Single-Entity General Traversal Serializes Relationship Type as `"RELATED_TO"` in `active_edge_keys`
- **Governing Specification Requirements:** Section 2 (`{correctness}` and `{correct required outputs}` #2: *"Instantaneous illumination of active relationship edges connecting the retrieved path"*) and Section 4.1.3 (*"All relationship edges whose keys belong to `activeEdgeKeys` must immediately render with active stroke color, increased line thickness, and amber contrast"*).
- **Touched Component:** `src/graphrag/traversal.py` (lines 345–385, 772–800).
- **Verified Empirical Root Cause:**
  - Observed directly in captured ground-truth payload `assets/20261013T194318-162-mbmi/api_graphrag_query_one_click_inquire.json`: when executing a one-click inquiry on `PLAW-117-328`, `active_edge_keys` returns `["BILL-117-hr-2617->RELATED_TO->PLAW-117-328", ...]` whereas `/api/graph/topology` (`assets/20261013T194318-162-mbmi/api_graph_topology_lta.json`) keys the same edges by their authentic Neo4j relationship type `["BILL-117-hr-2617->ENACTED_AS->PLAW-117-328", "PLAW-117-328->MODIFIES_CODE->USC-42-1395x-s-2-JJ", ...]`.
  - In `src/graphrag/traversal.py` line 365, `session.run(query, anchor_pk=anchor_pk).data()` converts Neo4j `Relationship` objects into tuples, so `hasattr(r, "type")` in `_convert_edge` (line 774) is `False` and defaults to `"RELATED_TO"`, ignoring `rel_type = row.get("rel_type")` fetched on line 372. While `GraphCanvas.tsx` line 155 currently has a secondary check `(activeNodePKs.has(source.primary_key) && activeNodePKs.has(target.primary_key))`, `activeEdgeKeys.has(link.edge_key)` fails to match the `RELATED_TO` edge keys returned by `_execute_single_general_traversal`.

---

## 5. Sufficiency & Scan Certification

- **Dependency Cone Completeness:** Every frontend React component, context provider, theme module, utility, FastAPI route, GraphRAG pipeline stage, Neo4j synchronization engine, and integration test suite touching `functional_specification_009.md` has been deterministically enumerated and inspected by verbatim symbol and filepath.
- **Empirical Schema Grounding:** Every API endpoint involved in topology loading and GraphRAG query execution (`/api/health`, `/api/graph/topology`, `/api/graphrag/query`, `/api/graphrag/subgraph`) was probed via non-mutating read-only requests, and raw unedited response payloads were saved into `assets/20261013T194318-162-mbmi/`.
- **Sufficiency Determination (`LANGUAGE.md`):** The static scan, active reconnaissance, empirical schema audit, and deficiency register are **`{sufficient}`** for downstream Wayfinder ticket decomposition and planning. Zero unverified assumptions or speculative contracts remain.

---

## 6. Handoff Manifest Affirmation

The role handoff manifest at `handoff/20261013T194318-162-mbmi/plan-scan-1.txt` has been atomically overwritten (`INV-MANIFEST-OVERWRITE-01`) with exclusively the repository-relative filepaths of:
1. All qualified and reviewed codebase component files in the dependency cone.
2. This authored scan report (`scan_reports/scan_report_009_plan_scan_1.md`).
3. All saved ground-truth payload sample files in `assets/20261013T194318-162-mbmi/`.

No seed specification paths (`functional_specification_009.md`) were recorded in `handoff/20261013T194318-162-mbmi/plan-scan-1.txt`, and `handoff/authored.txt` and all other run directories remain untouched.

---

## 7. Coding Gate Affirmation

*DO NOT CODE YET: Implementation coding gate remains locked. Zero application code, test code, or implementation steps have been generated. Coding waits on an empty frontier and explicit operator authorization.*
