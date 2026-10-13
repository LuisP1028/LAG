# Authoritative Static Codebase Scan, External API Reconnaissance, and Schema Audit Report

**Run ID:** `20261013T185957-734-5ytd`  
**Agent:** `plan-scan-2` (Planning Node / Scanner Agent 2)  
**Governing Specification:** `functional_specification_008.md`  
**Status:** Complete Reconnaissance, Codebase Scan, and Empirical Schema Audit (DO NOT CODE YET)  
**Taxonomy Reference:** [LANGUAGE.md](LANGUAGE.md)

---

## 1. Governing Context & Upstream Ingestion Verification

In strict accordance with `INV-HANDOFF-01`, `INV-SCAN-01`, and workspace rules:
- **Seed Specification Ingested:** `functional_specification_008.md` (*Functional Specification: Dual Jurisdiction and State Governance Architecture*), verified non-empty, fully bound, and consumed as the single specification in scope.
- **Run Identifier:** `20261013T185957-734-5ytd` (verified substituted across all asset and handoff manifest paths).
- **Wayfinder Architectural Map & Decision Tickets Inspected:**
  - Run-scoped directory `wayfinder/20261013T185957-734-5ytd/` is not yet populated prior to ticket synthesis.
  - Baseline Wayfinder Map inspected: `wayfinder/map.md` (*Wayfinder Architectural Map: GraphRAG Specification for Browser Graph Visualizer*)
  - Ticket 001: `wayfinder/tickets/ticket-001.md` — *Decision Ticket 001: Entity Anchor Linking and Layperson Vocabulary Normalization Specification*
  - Ticket 002: `wayfinder/tickets/ticket-002.md` — *Decision Ticket 002: Generalized Topological Subgraph Expansion and Neighborhood Traversal Specification*
  - Ticket 003: `wayfinder/tickets/ticket-003.md` — *Decision Ticket 003: Factual Context Assembly, Edge Provenance Formatting, and Prompt Grounding Specification*
  - Ticket 004: `wayfinder/tickets/ticket-004.md` — *Decision Ticket 004: Bidirectional Visual Canvas Synchronization and Active Subgraph Illumination Specification*
  - Ticket 005: `wayfinder/tickets/ticket-005.md` — *Decision Ticket 005: Master Specification Synthesis and Edits for functional_specification_004.md*
- **Evaluation Parameters Glossary:** Fully bound to [`LANGUAGE.md`](LANGUAGE.md), strictly adhering to authoritative definitions for `{errors}`, `{correctness}`, `{functionality}`, `{correct required outputs}`, `{sufficient}`, and `{insufficient}` without colloquial paraphrasing or semantic divergence.

---

## 2. Master Component Dependency Cone Register

The static scan of the active codebase cataloged all local modules, data models, storage engines, sync clients, API endpoints, GraphRAG pipeline stages, frontend visualizer components, and test suites whose interfaces or behaviors touch the specced functionality in `functional_specification_008.md`:

| Repository-Relative Path | Verbatim Symbols & Interfaces | Role in Architecture | Grounding Justification (`functional_specification_008.md`) |
| :--- | :--- | :--- | :--- |
| `LANGUAGE.md` | `{errors}`, `{correctness}`, `{functionality}`, `{correct required outputs}`, `{sufficient}`, `{insufficient}`, `{Policy Keyword}`, `{Target_Bill_IDs}`, `{Enacted_Law_ID}`, `{US_Code_Citations}`, `{Operational_Filters}`, `{Clinical_Citations}`, `{HCPCS / CPT Codes}` | System-wide evaluation parameters and domain taxonomy glossary. | Section 2 mandates strict conformance of all evaluations to `LANGUAGE.md`. |
| `src/frontend/src/components/FilterToolbar.tsx` | `FilterToolbarProps`, `FilterToolbar`, `handleStateChange`, `handlePolicyChange` | Top navigation bar UI component rendering dropdown selectors, path reset button, and GraphRAG chat toggle. | Section 5.1.1 & 5.1.2 mandate splitting the single `"JURISDICTION:"` dropdown (which currently filters `filterState` across only 5 hardcoded states: `WI`, `IL`, `CA`, `NY`, `TX`) into two distinct, synchronized selectors: `JURISDICTION:` and `STATE:`. |
| `src/frontend/src/context/GraphSyncContext.tsx` | `GraphSyncContextType`, `GraphSyncProvider`, `useGraphSync`, `filterState`, `setFilterState`, `policyKeyword`, `setPolicyKeyword`, `selectNode`, `submitInquiry`, `inquireNode`, `setIlluminatedPath`, `clearIllumination` | React Context synchronization bus managing active node/edge illumination, selected node state, quick prompts, filter state, and `/api/graphrag/query` dispatch. | Section 3, 5.1.1, and 5.1.2 require cascading state/jurisdiction synchronization (`filterJurisdiction` and `filterState`), dynamic quick prompts, and accurate state/jurisdiction context propagation to GraphRAG inquiries. |
| `src/frontend/src/App.tsx` | `MainVisualizer`, `App`, `fetchTopology`, `nodes`, `links`, `loading`, `fetchError` | Top-level visualizer container executing `GET /api/graph/topology` and passing `nodes` and `links` to `GraphCanvas` and `NodeDetailDrawer`. | Section 5.2.1 requires `fetchTopology` to pass both `jurisdiction_filter` and `state_filter` query parameters independently to `/api/graph/topology`. |
| `src/frontend/src/components/GraphCanvas.tsx` | `GraphCanvasProps`, `GraphCanvas`, `frameActiveSubgraph`, `render`, `handlePointerDown`, `handlePointerMove` | HTML5 Canvas force-directed graph visualizer rendering orbital linework around `Policy`, `PublicLaw`, and `Jurisdiction` hubs, active edge pulses, halftone node shading, and 60 FPS telemetry HUD. | Section 5.1.1, 5.1.2, 5.2.1, and Section 6 Criterion 5 mandate highlighting `JURIS-DME-*` and `COVERS_STATE` subgraphs, expanding `FeeScheduleEntry` nodes on state selection, and maintaining 60 FPS on the National Overview (`All Jurisdictions`, `All States`). |
| `src/frontend/src/components/NodeDetailDrawer.tsx` | `NodeDetailDrawerProps`, `NodeDetailDrawer`, `connectedNeighbors`, `getGovernmentSourceLink` | Slide-over inspection drawer displaying node metadata, connected neighbors, government provenance URLs, and one-click GraphRAG inquiry button. | Displays `Jurisdiction`, `State`, and `FeeScheduleEntry` attributes and neighbor connections when inspecting regional contractors or geographic states. |
| `src/frontend/src/components/AgentChatDrawer.tsx` | `AgentChatDrawer`, `handleSend`, `modelId`, `inputQuery` | Conversational GraphRAG terminal drawer displaying quick prompts, synthesis answers, latency telemetry, and illuminated node counts. | Section 1 & 5.3 require GraphRAG intelligence terminal synchronization with regional jurisdiction and state inquiries. |
| `src/frontend/src/utils/promptGenerator.ts` | `constructInquiryPrompt` | Generates deterministic natural language prompts for one-click node inquiries across all 14 node labels (`Jurisdiction`, `State`, `FeeScheduleEntry`, etc.). | Used by `inquireNode` in `GraphSyncContext.tsx` when querying a `Jurisdiction` or `State` node from the canvas. |
| `src/frontend/src/types/graph.ts` | `NodeProperties`, `EdgeProvenance`, `GraphNode`, `GraphLink`, `AnchorEntity`, `GraphRAGQueryResponse`, `GraphSummary` | Frontend TypeScript data contracts for topology nodes, edges, anchors, and GraphRAG responses. | Defines client-side property contracts (`state_code`, `state_name`, `contractor_name`, `code`, `fee_amount`, `is_rural`). |
| `src/frontend/src/styles/graph_theme.ts` | `NodeVisualConfig`, `NODE_THEME_REGISTRY`, `CANVAS_PALETTE`, `getNodeVisual` | Visual styling registry for all 14 node types including `Jurisdiction`, `State`, and `FeeScheduleEntry`. | Supplies badge colors, radii, and shapes for `Jurisdiction`, `State`, and `FeeScheduleEntry` nodes on the canvas. |
| `src/api/routes.py` | `router`, `get_graph_topology`, `resolve_entities`, `get_subgraph_by_anchors`, `execute_graphrag_query`, `get_graph_summary`, `health_check` | FastAPI router exposing `/api/graph/topology`, `/api/entities/resolve`, `/api/graphrag/subgraph`, and `/api/graphrag/query`. | Section 5.2.1 mandates that `/api/graph/topology` accept both `jurisdiction_filter` and `state_filter` as independent optional query parameters and filter the returned subgraph accordingly. |
| `src/api/models.py` | `HealthResponse`, `TopologyNode`, `TopologyEdge`, `TopologyResponse`, `EntityResolveRequest`, `EntityResolveResponse`, `SubgraphRequest`, `SubgraphResponse`, `ErrorEnvelope` | Pydantic request/response schemas for REST API endpoints. | Defines the response schema (`TopologyResponse`) returned by `/api/graph/topology` and `/api/graphrag/subgraph`. |
| `src/api/server.py` | `lifespan`, `create_app`, `app`, `http_exception_handler`, `graphrag_exception_handler` | FastAPI application factory, CORS middleware, Neo4j lifespan connection manager, and standardized error envelope handlers. | Hosts all `/api/*` endpoints and manages the `Neo4jSyncEngine` singleton. |
| `src/api/__init__.py` | Package initialization | API module marker. | Package structure for `src.api`. |
| `src/graphrag/entity_linker.py` | `EntityAnchorLinker`, `STATE_NAME_TO_CODE`, `CLINICAL_SYNONYMS`, `POLICY_TRIGGERS`, `HCPCS_REGEX`, `PK_TOKEN_REGEX`, `resolve_anchors`, `resolve_explicit_anchor`, `_extract_jurisdiction_anchors`, `_extract_state_anchor`, `_extract_hcpcs_anchors` | Deterministic multi-slot entity anchor resolver mapping natural language queries to verified Neo4j `AnchorEntity` records. | Section 5.3.1 & 5.3.2 require resolving regional contractor queries (`Jurisdiction A/B/C/D`, `Noridian`, `CGS`), all 50 states and territories, and multi-state comparative queries (e.g., `California` and `New York`). |
| `src/graphrag/traversal.py` | `TopologicalTraversalEngine`, `extract_connecting_subgraph`, `_execute_single_entity_traversal`, `_execute_single_state_traversal`, `_execute_single_clinical_traversal`, `_execute_single_general_traversal`, `_execute_multi_entity_traversal`, `_execute_pattern_a`, `_execute_pattern_b`, `_execute_pattern_c`, `_convert_node`, `_convert_edge` | Neo4j Cypher subgraph extraction engine for single-entity and multi-entity anchor sets. | Section 5.3.1 & 5.3.2 require complete traversal for single-jurisdiction queries (`JURIS-DME-*` $\rightarrow$ `COVERS_STATE` $\rightarrow$ all constituent `State` nodes + `ChangeRequest` + `CoveragePolicy`), single-state contractor queries (`STATE-TX` $\rightarrow$ `JURIS-DME-C` $\rightarrow$ `CMS-CR-13286`), and cross-jurisdiction multi-state fee comparisons (`HCPCS-A6522` + `STATE-CA` + `STATE-NY`). |
| `src/graphrag/context_assembler.py` | `GraphContextAssembler`, `assemble_context` | Formats `TraversalResult` nodes, edges, fee schedule entries, and provenance into 5 structured Markdown sections for LLM synthesis. | Section 5.3.1 & 5.3.2 require assembling complete state lists for regional contractors and multi-state fee schedule comparisons without dropping secondary states' `A6522` rates. |
| `src/graphrag/synthesizer.py` | `HuggingFaceSynthesizer`, `SYSTEM_PROMPT`, `synthesize`, `_call_hf_inference_api` | Invokes Hugging Face Serverless Inference API (`https://router.huggingface.co/v1/chat/completions`) to synthesize grounded answers citing bracketed primary keys. | Synthesizes final grounded answers for regional contractor and cross-jurisdiction state queries. |
| `src/graphrag/pipeline.py` | `GraphRAGPipeline`, `execute_query` | Orchestrates Stage 1 (Linking), Stage 2 (Traversal), Stage 3 (Context Assembly), and Stage 4/5 (Synthesis & Provenance). | End-to-end execution pipeline for `/api/graphrag/query`. |
| `src/graphrag/models.py` | `AnchorEntity`, `ResolvedAnchors`, `TraversalNode`, `TraversalEdge`, `TraversalResult`, `GraphRAGQueryRequest`, `GraphRAGQueryResponse` | Pydantic models for resolved anchors, traversal subgraphs, and GraphRAG query payloads. | Defines `ResolvedAnchors` (currently holding only singular `state_anchor: Optional[AnchorEntity]` and `jurisdiction_anchor: Optional[AnchorEntity]`) and `GraphRAGQueryRequest`. |
| `src/graphrag/exceptions.py` | `GraphRAGException`, `EntityResolutionError`, `TraversalError`, `ModelInferenceError`, `ModelAuthenticationError`, `ModelRateLimitError`, `GraphValidationError` | Fail-fast exception hierarchy for GraphRAG operations. | Enforces fail-fast error handling (`INV-FAIL-FAST`). |
| `src/graphrag/__init__.py` | Package initialization | GraphRAG module marker. | Package structure for `src.graphrag`. |
| `src/graph/models.py` | `EdgeProvenance`, `GraphEdge`, `BaseNode`, `PolicyNode`, `BillNode`, `PublicLawNode`, `StatutorySectionNode`, `RegulationNode`, `ChangeRequestNode`, `CoveragePolicyNode`, `JurisdictionNode`, `StateNode`, `FeeScheduleEntryNode`, `HCPCSCodeNode`, `ICD10CodeNode`, `LobbyingFilingNode`, `CBOScoreNode`, `LiteratureStudyNode` | Canonical Pydantic models for all 15 graph node types and directed edges. | Defines `JurisdictionNode` (`JURIS-DME-*`), `StateNode` (`STATE-*`), and `FeeScheduleEntryNode` (`FEE-{hcpcs}-{state}-{R|NR}-{year}`). |
| `src/graph/tier4b_fee_schedule.py` | `DME_MAC_JURISDICTIONS`, `normalize_fee_schedules`, `Phase4FeeScheduleDatasetError`, `Phase4IncompleteJurisdictionError` | Authoritative mapping of `JURIS-DME-A`, `JURIS-DME-B`, `JURIS-DME-C`, `JURIS-DME-D` to contractors and states/territories, and unpivoting of CMS DMEPOS fee schedule CSV rates. | Section 4 defines the authoritative CMS DMEPOS regional contractor boundary assignments (`JURIS-DME-A` through `JURIS-DME-D`) and state mappings. |
| `src/graph/tier4a_coverage.py` | `STANDARD_COVERED_DIAGNOSES`, `STANDARD_COVERED_HCPCS`, `ingest_coverage_policy` | Ingests CMS MCD articles (`A59508`, `A59588`), `HCPCSCode` nodes, and `ICD10Code` nodes. | Links `ChangeRequest` to `CoveragePolicy` and `HCPCSCode` nodes used in state and jurisdiction subgraphs. |
| `src/graph/engine.py` | `DirectedPropertyGraph`, `PropertyGraphEngine`, `run_pipeline`, `validate_invariants`, `GraphValidationError` | Assembles multi-tier property graph and validates `INV-50-STATE-COMPLETENESS` and `INV-UNBROKEN-ANCESTRY`. | Enforces graph-level invariants on `JurisdictionNode`, `StateNode`, and `FeeScheduleEntryNode` counts. |
| `src/graph/neo4j_sync.py` | `Neo4jSyncEngine`, `init_schema`, `sync_graph_dict`, `sync_file`, `get_summary_statistics` | Synchronizes `DirectedPropertyGraph` exports into Neo4j using `apoc.merge.node` and `apoc.merge.relationship`. | Persists `Jurisdiction`, `State`, and `FeeScheduleEntry` nodes and `COVERS_STATE`, `APPLIES_TO_JURISDICTION`, `HAS_FEE_SCHEDULE`, `APPLIES_TO` edges in Neo4j. |
| `src/graph/tier1_legislative.py` | `discover_legislation` | Tier 1 legislative discovery (`POLICY-LTA`, `POLICY-IVIG`, `PLAW-117-328`). | Root policy lineage for topology filtering. |
| `src/graph/tier2_statutory.py` | `parse_statutory_codification` | Tier 2 statutory section parser (`USC-42-1395x-*`). | Statutory lineage for topology filtering. |
| `src/graph/tier3_regulatory.py` | `harvest_regulations` | Tier 3 regulation and change request harvester (`FR-2023-24455`, `CMS-CR-13286`, `CMS-CR-13217`). | Change request anchors connecting to `Jurisdiction` and `CoveragePolicy`. |
| `src/graph/tier5_context.py` | `enrich_context` | Tier 5 lobbying, CBO, and PubMed enrichment. | Contextual nodes connected to root policy bills and regulations. |
| `src/graph/__init__.py` | Package Exports | Exports graph models and engine. | Public interface for `src.graph`. |
| `exports/lta_knowledge_graph.json` | Serialized LTA Knowledge Graph | JSON export containing 3,852 nodes and 7,562 edges for `POLICY-LTA`. | Pre-built LTA graph synced into Neo4j. |
| `exports/ivig_knowledge_graph.json` | Serialized IVIG Knowledge Graph | JSON export containing 183 nodes and 289 edges for `POLICY-IVIG`. | Pre-built IVIG graph synced into Neo4j. |
| `tests/test_api_endpoints.py` | `test_api_health`, `test_api_graph_summary`, `test_api_graph_topology`, `test_api_entities_resolve`, `test_api_graphrag_subgraph`, `test_api_graphrag_query`, `test_api_single_state_and_subgraph` | FastAPI TestClient integration test suite. | Tests `/api/graph/topology`, `/api/entities/resolve`, `/api/graphrag/subgraph`, and `/api/graphrag/query`. |
| `tests/test_graph_pipeline.py` | `test_50_state_and_jurisdiction_completeness`, `test_neo4j_sync_and_mcp_invariants` | Graph construction and Neo4j invariant verification suite. | Asserts `len(jurisdictions) == 4` and `len(states) in (53, 54)`. |
| `tests/test_graphrag_pipeline.py` | `test_oracle_1_patient_benefit_routing`, `test_single_state_query_ny`, `test_latency_benchmark_harness` | End-to-end GraphRAG verification suite against Neo4j. | Tests state and jurisdiction traversal and synthesis. |
| `verify_all.py` | `main` | CLI verification runner executing end-to-end GraphRAG workflows. | System verification entrypoint. |

---

## 3. Candidate External Datasource & Schema Audit Register

Active read-only reconnaissance was executed against the live Neo4j property graph instance, the CMS DMEPOS Fee Schedule dataset, and the FastAPI REST/GraphRAG endpoints. All raw, unedited empirical payloads were captured into `assets/20261013T185957-734-5ytd/`.

### 3.1. Neo4j Property Graph Database (`bolt://localhost:7687`, database `neo4j`)
- **Role in Specification:** Primary backing graph store containing `Jurisdiction`, `State`, `FeeScheduleEntry`, `ChangeRequest`, `CoveragePolicy`, `HCPCSCode`, `ICD10Code`, and legislative lineage entities.
- **Connection & Authentication Parameters:**
  - URI: `bolt://localhost:7687` (`NEO4J_URI`)
  - Username: `neo4j` (`NEO4J_USERNAME`)
  - Password: `qwertyui` (`NEO4J_PASSWORD`)
  - Database: `neo4j` (`NEO4J_DATABASE`)
  - Status: **Reachable & Verified** (3,971 total `PolicyNode` vertices, 7,786 total directed relationships).
- **Audited Empirical Schema (`Jurisdiction`, `State`, `FeeScheduleEntry`):**
  1. **`Jurisdiction` (`:PolicyNode:Jurisdiction`) — 4 Nodes:**
     - `JURIS-DME-A`: `{"primary_key": "JURIS-DME-A", "code": "JURIS-DME-A", "name": "JURIS-DME-A (Noridian)", "contractor_name": "Noridian Healthcare Solutions"}`
     - `JURIS-DME-B`: `{"primary_key": "JURIS-DME-B", "code": "JURIS-DME-B", "name": "JURIS-DME-B (CGS)", "contractor_name": "CGS Administrators"}`
     - `JURIS-DME-C`: `{"primary_key": "JURIS-DME-C", "code": "JURIS-DME-C", "name": "JURIS-DME-C (CGS)", "contractor_name": "CGS Administrators"}`
     - `JURIS-DME-D`: `{"primary_key": "JURIS-DME-D", "code": "JURIS-DME-D", "name": "JURIS-DME-D (Noridian)", "contractor_name": "Noridian Healthcare Solutions"}`
     - *Incoming Edges:* `(cr:ChangeRequest)-[:APPLIES_TO_JURISDICTION]->(j:Jurisdiction)` from both `CMS-CR-13286` (LTA) and `CMS-CR-13217` (IVIG).
     - *Outgoing Edges:* `(j:Jurisdiction)-[:COVERS_STATE]->(s:State)`:
       - `JURIS-DME-A` (12 states/territories): `CT, DC, DE, MA, MD, ME, NH, NJ, NY, PA, RI, VT`
       - `JURIS-DME-B` (7 states): `IL, IN, KY, MI, MN, OH, WI`
       - `JURIS-DME-C` (17 states/territories): `AL, AR, CO, FL, GA, LA, MS, NC, NM, OK, PR, SC, TN, TX, VA, VI, WV`
       - `JURIS-DME-D` (17 states currently in Neo4j): `AK, AZ, CA, HI, IA, ID, KS, MO, MT, ND, NE, NV, OR, SD, UT, WA, WY` (Note: `AS`, `GU`, `MP` from Section 4 Table of `functional_specification_008.md` are not currently instantiated in Neo4j or `DME_MAC_JURISDICTIONS`).
  2. **`State` (`:PolicyNode:State`) — 53 Nodes:**
     - Fields: `primary_key` (`"STATE-XX"`, `str`), `state_code` (`"XX"`, `str`), `state_name` (full name, `str`). Note: `State` nodes in Neo4j do NOT have a `.name` property; `convert_node` falls back to `props.get("state_name")`.
     - Every one of the 53 `State` nodes in Neo4j has exactly 72 incoming `[:APPLIES_TO]` edges from `FeeScheduleEntry` nodes (70 non-rural LTA compression codes + 1 non-rural IVIG `Q2052` + 1 rural IVIG `Q2052`).
  3. **`FeeScheduleEntry` (`:PolicyNode:FeeScheduleEntry`) — 3,816 Nodes:**
     - Fields: `primary_key` (`"FEE-{HCPCS}-{STATE}-{NR|R}-2024"`, `str`), `hcpcs_code` (`str`), `state_code` (`str`), `is_rural` (`bool`), `fee_amount` (`float`), `ceiling` (`float`), `floor` (`float`), `year` (`int`), `name` (`str`, e.g., `"A6522 NY NR ($290.47)"`).
- **Saved Ground-Truth Asset:**
  - `assets/20261013T185957-734-5ytd/neo4j_jurisdictions_and_states_audit.json`

---

### 3.2. CMS DMEPOS Fee Schedule Dataset (`stage4b_cms_dmepos_lc_category.csv`)
- **Role in Specification:** Authoritative source table for DMEPOS procedure code payment rates across states and territories (`src/graph/tier4b_fee_schedule.py`).
- **File Location:** `CoveragePolicies_and_Jurisdictions Addition/assets/20261012T231057-024-zqga/stage4b_cms_dmepos_lc_category.csv`
- **Audited Empirical Schema:**
  - 114 columns total: `HCPCS`, `Mod`, `Mod2`, `JURIS`, `CATG`, `Ceiling`, `Floor`, followed by 106 state/territory rate columns (`53 x 2` pairs of `<ST> (NR)` and `<ST> (R)` covering all 50 US states + `DC`, `PR`, `VI`), and `Description`.
  - Pacific territories (`AS`, `GU`, `MP`) are not present as columns in the CMS DMEPOS CSV file.
  - Sample empirical row for `HCPCS = "A6522"` (`CATG = "LC"`):
    - `CA (NR)`: `"290.47"`, `CA (R)`: `"0.00"`
    - `NY (NR)`: `"290.47"`, `NY (R)`: `"0.00"`
    - `OH (NR)`: `"290.47"`, `OH (R)`: `"0.00"`
    - `TX (NR)`: `"290.47"`, `TX (R)`: `"0.00"`
    - `FL (NR)`: `"290.47"`, `FL (R)`: `"0.00"`
    - `WI (NR)`: `"290.47"`, `WI (R)`: `"0.00"`
- **Saved Ground-Truth Asset:**
  - `assets/20261013T185957-734-5ytd/cms_dmepos_fee_schedule_ca_ny_oh_tx_sample.json`

---

### 3.3. Local FastAPI Topology Endpoint (`GET /api/graph/topology`)
- **Role in Specification:** Requirement 5.2.1 mandates multi-tier topology filtering via optional `jurisdiction_filter` and `state_filter` query parameters.
- **Empirical Probing Results:**
  - `GET /api/graph/topology` (no params): Returns HTTP 200 OK with `total_nodes: 155`, `total_edges: 163` (all 4 `Jurisdiction` nodes, all 53 `State` nodes, 0 `FeeScheduleEntry` nodes).
  - `GET /api/graph/topology?jurisdiction_filter=JURIS-DME-B`: Returns HTTP 200 OK with `total_nodes: 155`, `total_edges: 163`, and all 53 `State` nodes because `jurisdiction_filter` is not declared or handled in `src/api/routes.py`.
  - `GET /api/graph/topology?state_filter=OH`: Returns HTTP 200 OK with `total_nodes: 227`, `total_edges: 307`. It includes all 53 `State` nodes and all 4 `Jurisdiction` nodes from `base_query` plus 72 `FeeScheduleEntry` nodes for `OH` (71 non-rural + 1 rural `FEE-Q2052-OH-R-2024`).
- **Saved Ground-Truth Asset:**
  - `assets/20261013T185957-734-5ytd/api_graph_topology_baseline.json`

---

### 3.4. Local FastAPI GraphRAG & Entity Resolution Endpoints (`POST /api/entities/resolve`, `POST /api/graphrag/subgraph`, `POST /api/graphrag/query`)
- **Role in Specification:** Section 5.3.1 (Regional Administrative Queries) and Section 5.3.2 (Cross-Jurisdiction Comparisons).
- **Empirical Probing Results:**
  1. **Probe 1 (`"What states does Jurisdiction B cover?"`):**
     - `POST /api/entities/resolve` $\rightarrow$ Anchors `[{"slot": "jurisdiction", "primary_key": "JURIS-DME-B", "matched_text": "Jurisdiction B", "entity_type": "Jurisdiction", "label": "Jurisdiction"}]`.
     - `POST /api/graphrag/subgraph` $\rightarrow$ Dispatches to `_execute_single_general_traversal` (1-hop `OPTIONAL MATCH (n)-[r]-(m:PolicyNode)` with `.data()`). Returns 10 nodes (`JURIS-DME-B`, 7 Midwestern `State` nodes, `CMS-CR-13217`, `CMS-CR-13286`), omits 2-hop `CoveragePolicy` nodes (`CMS-MCD-A59508`, `CMS-MCD-A59588`), and corrupts all 9 edge labels in `active_edge_keys` to `"RELATED_TO"` (`"JURIS-DME-B->RELATED_TO->STATE-IL"`, etc.) because `session.run(...).data()` converts Neo4j `Relationship` objects into tuples lacking `.type` and `.items()`.
  2. **Probe 2 (`"What policies does CGS administer?"`):**
     - `POST /api/entities/resolve` $\rightarrow$ Anchors ONLY `JURIS-DME-B` (omitting `JURIS-DME-C`, which is also administered by CGS Administrators) and returns 0 `CoveragePolicy` nodes in the 1-hop subgraph.
  3. **Probe 3 (`"Who administers Medicare Part B DME claims in Texas?"`):**
     - `POST /api/entities/resolve` $\rightarrow$ Anchors `STATE-TX`.
     - `POST /api/graphrag/subgraph` $\rightarrow$ Dispatches to `_execute_single_state_traversal`, returning `STATE-TX`, `JURIS-DME-C`, `CMS-CR-13286`, `CMS-CR-13217`, `CMS-MCD-A59508`, `CMS-MCD-A59588`, and Texas non-rural fee schedule entries.
  4. **Probe 4 (`"Compare allowable rates for A6522 between California and New York."`):**
     - `POST /api/entities/resolve` $\rightarrow$ Anchors ONLY `STATE-CA` and `HCPCS-A6522` (**drops `STATE-NY` completely** because `_extract_state_anchor` returns on the first matched state!).
     - `POST /api/graphrag/subgraph` $\rightarrow$ **Returns HTTP 500 Internal Server Error** (`AttributeError: 'list' object has no attribute 'nodes'` at `src/graphrag/traversal.py` line 366 in `_execute_multi_entity_traversal`).
- **Saved Ground-Truth Asset:**
  - `assets/20261013T185957-734-5ytd/api_graphrag_jurisdiction_and_state_probes.json`

---

### 3.5. Hugging Face Serverless Inference Router (`https://router.huggingface.co/v1/chat/completions`)
- **Role in Specification:** OpenAI-compatible chat completions endpoint invoked by `HuggingFaceSynthesizer` (`src/graphrag/synthesizer.py`) to synthesize grounded natural language answers.
- **Authentication:** Bearer token via `HF_TOKEN` or `HUGGINGFACE_API_KEY` environment variable in `.env`.
- **Default & Aliased Models:** `meta-llama/Llama-3.1-8B-Instruct` (aliased from `meta-llama/Meta-Llama-3-8B-Instruct` and `mistralai/Mistral-7B-Instruct-v0.3`), `Qwen/Qwen2.5-72B-Instruct` (aliased from `Qwen/Qwen2.5-7B-Instruct`).

---

## 4. Explicit Deficiency Register

In strict compliance with `INV-ABSENCE-01`, the following specced requirements in `functional_specification_008.md` are currently unprovided or defective in the active codebase. Zero components or endpoints have been invented.

| Deficiency ID | Affected Component(s) | Specced Requirement (`functional_specification_008.md`) | Empirical Observation & Exact Codebase Deficiency |
| :--- | :--- | :--- | :--- |
| **`DEF-001`** | `src/frontend/src/components/FilterToolbar.tsx` (lines 57–80) | **Req 5.1.1 & 5.1.2 (Dual UI Selectors):** Top toolbar must feature two separate, clearly labeled selectors: `JURISDICTION:` (`All Jurisdictions (National Overview)`, `Jurisdiction A (Northeast - Noridian)`, `Jurisdiction B (Midwest - CGS)`, `Jurisdiction C (South - CGS)`, `Jurisdiction D (West - Noridian)`) and `STATE:` (`All States (Overview)` + alphabetical list of all 50 US states, DC, and territories). | `FilterToolbar.tsx` renders only a single `<select>` labeled `JURISDICTION:` that is actually bound to `filterState` and lists only 5 hardcoded state options (`WI`, `IL`, `CA`, `NY`, `TX`) plus `""` (`All States (Fees Collapsed - 60 FPS)`). There is no `JURISDICTION` selector for DME MAC Jurisdictions A–D, and 45+ states/territories are completely inaccessible from the UI. |
| **`DEF-002`** | `src/frontend/src/context/GraphSyncContext.tsx` (lines 17–41, 67–70, 151–161), `src/frontend/src/components/FilterToolbar.tsx` (lines 25–35), `src/frontend/src/App.tsx` (lines 16–25, 67–69) | **Req 5.1.1.3 & 5.1.2.3 (Cascading Filter Synchronization):** Selecting a Jurisdiction must highlight `JURIS-DME-*` and its `COVERS_STATE` states and filter the `STATE:` dropdown to only states in that region; selecting a State must automatically update the `JURISDICTION:` selector to reflect the parent regional jurisdiction covering that state. | `GraphSyncContext.tsx` lacks a `filterJurisdiction` state and has no mapping or synchronization logic between `JURIS-DME-A/B/C/D` and their constituent states. `App.tsx` `fetchTopology` only accepts `(stateFilter, policy)` and does not pass `jurisdiction_filter` to `/api/graph/topology`. |
| **`DEF-003`** | `src/api/routes.py` (`get_graph_topology`, lines 84–250) | **Req 5.2.1 (Multi-Tier Topology Filtering):** `/api/graph/topology` must accept both `jurisdiction_filter` and `state_filter` as optional query parameters: (1) `jurisdiction_filter` returns root policy, governing change requests, coverage policies, regional contractor node, and only the states covered by that contractor (with fees collapsed unless a state is also selected); (2) `state_filter` returns the selected state, its parent regional contractor, governing change request/coverage policy, and localized non-rural fee schedule entries for that state; (3) both `All` returns the complete national macro graph with fee schedules collapsed. | `get_graph_topology` in `src/api/routes.py` does not accept `jurisdiction_filter` at all. Furthermore, `base_query` (lines 164–170) unconditionally loads all 53 `State` nodes and all 4 `Jurisdiction` nodes even when `state_filter` is provided, and `fee_query` (lines 189–193) does not filter `WHERE f.is_rural = false`, returning rural fee entries alongside non-rural entries. Additionally, `policy_keyword` parameter is accepted on line 86 but never used in the Cypher queries. |
| **`DEF-004`** | `src/graphrag/entity_linker.py` (`_extract_state_anchor`, lines 351–403) & `src/graphrag/models.py` (`ResolvedAnchors`, lines 16–30) | **Req 5.3.2 (Cross-Jurisdiction Multi-State Entity Resolution):** Queries comparing two or more states (e.g., *"Compare allowable rates for A6522 between California and New York."*) must anchor all mentioned states (`STATE-CA` and `STATE-NY`). | `_extract_state_anchor` returns `Optional[AnchorEntity]` and immediately exits on the first matched state in `STATE_NAME_TO_CODE` (sorted by name length descending). For `"Compare allowable rates for A6522 between California and New York."`, it returns `STATE-CA` and completely drops `STATE-NY`. |
| **`DEF-005`** | `src/graphrag/entity_linker.py` (`_extract_jurisdiction_anchors`, lines 231–255) | **Section 3 & Req 5.3.1 (Contractor & Regional Jurisdiction Lexical Resolution):** Queries asking about a contractor (e.g., *"What policies does CGS administer?"* or *"What states does Noridian cover?"*) or regional jurisdiction (`Jurisdiction A/B/C/D`, `DME MAC A/B/C/D`) must resolve accurately to all corresponding `JURIS-DME-*` nodes. | In `_extract_jurisdiction_anchors` (lines 234–239), `"noridian"` only maps to `JURIS-DME-A` (ignoring `JURIS-DME-D`), and `"cgs"` only maps to `JURIS-DME-B` (ignoring `JURIS-DME-C`). Patterns like `"DME MAC A"`, `"DME MAC B"`, `"DME MAC C"`, `"DME MAC D"` without the word `"Jurisdiction"` are also not matched. |
| **`DEF-006`** | `src/graphrag/traversal.py` (`_execute_multi_entity_traversal`, lines 350–376) | **Req 5.3.2 (Cross-Jurisdiction Comparative Traversal):** Multi-entity queries combining `HCPCSCode` and one or more `State` or `Jurisdiction` anchors (e.g., `HCPCS-A6522`, `STATE-CA`, `STATE-NY`) must traverse through each state's parent `Jurisdiction` (`JURIS-DME-D`, `JURIS-DME-A`), governing `ChangeRequest` / `CoveragePolicy`, and specific `FeeScheduleEntry` nodes without error. | Branch 4 of `_execute_multi_entity_traversal` runs `MATCH path = allShortestPaths((start)-[*..6]-(target)) RETURN path` via `session.run(...).data()`, which serializes `path` as a Python `list` rather than a `neo4j.graph.Path` object. Line 366 (`for n in path.nodes:`) immediately crashes with `AttributeError: 'list' object has no attribute 'nodes'` (HTTP 500). Furthermore, `allShortestPaths` between `HCPCS-A6522` and `STATE-CA`/`STATE-NY` does not include the `State <-[:COVERS_STATE]- Jurisdiction <-[:APPLIES_TO_JURISDICTION]- ChangeRequest -[:MANDATES_POLICY]-> CoveragePolicy` administrative lineage alongside the `FeeScheduleEntry` path. |
| **`DEF-007`** | `src/graphrag/traversal.py` (`_execute_single_entity_traversal`, lines 77–113; `_execute_single_general_traversal`, lines 262–302) | **Req 5.3.1 (Regional Administrative Queries):** Single-jurisdiction queries (e.g., *"What states does Jurisdiction B cover?"*, *"What is Jurisdiction B?"*, *"What policies does CGS administer?"*) must retrieve the `Jurisdiction` node, all constituent `State` nodes via `COVERS_STATE`, the governing `ChangeRequest` nodes via `APPLIES_TO_JURISDICTION`, and the mandated `CoveragePolicy` nodes via `MANDATES_POLICY` with authentic edge labels and provenance. | `Jurisdiction` anchors fall into `_execute_single_general_traversal`, which: (1) only traverses 1 hop, omitting `CoveragePolicy` nodes (`CMS-MCD-A59508`, `CMS-MCD-A59588`) that are 2 hops away; and (2) uses `session.run(...).data()`, which serializes `r` as a tuple so `_convert_edge(r, src_pk, tgt_pk)` loses the actual relationship type (`COVERS_STATE`, `APPLIES_TO_JURISDICTION`) and replaces all edge labels with `"RELATED_TO"` (`JURIS-DME-B->RELATED_TO->STATE-IL`), breaking canvas edge illumination (`activeEdgeKeys.has(link.edge_key)`) and losing edge provenance. |
| **`DEF-008`** | `src/graphrag/context_assembler.py` (`assemble_context`, lines 75–88, 126–164) & `src/graphrag/pipeline.py` (lines 57–67) | **Req 5.3.1 & 5.3.2 (Regional & Multi-State Context Assembly):** Context assembly must accurately format all constituent states covered by each `Jurisdiction` and must include all anchored states' fee schedule entries (e.g., both California and New York rates for `A6522`) when comparing across states/jurisdictions. | (1) In `assemble_context` lines 141–160, `a6522_fee = next((f for f in candidate_fees if f.properties.get("hcpcs_code") == "A6522"), None)` formats only the **first** `A6522` fee node and line 153 (`if h_code != "A6522"`) skips all remaining `A6522` fee nodes, causing the second state's `A6522` rate to be silently dropped in multi-state comparisons! (2) Line 128 (`target_state = state_nodes[0]...`) labels Section 4 with only the first state in `state_nodes` (e.g., `"Illinois"` when all 7 Jurisdiction B states are present). (3) Line 79 checks `j.properties.get("states", "")`, which does not exist on `Jurisdiction` nodes in Neo4j, instead of deriving covered states from `COVERS_STATE` edges or traversed `State` nodes. |
| **`DEF-009`** | `src/graph/tier4b_fee_schedule.py` (`DME_MAC_JURISDICTIONS`, lines 38–78; line 155), `src/graph/engine.py` (line 218), `src/graphrag/entity_linker.py` (`STATE_NAME_TO_CODE`, lines 15–30) | **Section 4 Table (Authoritative Regional Jurisdiction and State Mapping):** Section 4 specifies: `JURIS-DME-A` (12 jurisdictions: CT, DE, DC, ME, MD, MA, NH, NJ, NY, PA, RI, VT; Noridian Healthcare Solutions), `JURIS-DME-B` (7 states: IL, IN, KY, MI, MN, OH, WI; CGS Administrators, LLC), `JURIS-DME-C` (17 jurisdictions: AL, AR, CO, FL, GA, LA, MS, NM, NC, OK, SC, TN, TX, VA, WV, PR, VI; CGS Administrators, LLC), and `JURIS-DME-D` (20 jurisdictions: AK, AZ, CA, HI, ID, IA, KS, MO, MT, NE, NV, ND, OR, SD, UT, WA, WY, plus American Samoa `AS`, Guam `GU`, Northern Mariana Islands `MP`; Noridian Healthcare Solutions) — totaling 56 jurisdictions (50 states + DC + PR + VI + AS + GU + MP). | `DME_MAC_JURISDICTIONS["D"]` in `src/graph/tier4b_fee_schedule.py` (lines 67–77) and `STATE_NAME_TO_CODE` in `src/graphrag/entity_linker.py` (lines 15–30) currently list 17 jurisdictions in `JURIS-DME-D` (omitting `AS`, `GU`, `MP`) for a total of 53 jurisdictions, and `engine.py` (line 218) / `tier4b_fee_schedule.py` (line 155) hardcode `if len(states) not in (53, 54): raise ...`. Also `contractor_name` for B and C is stored as `"CGS Administrators"` rather than `"CGS Administrators, LLC"`, and `"U.S. Virgin Islands"` is named `"Virgin Islands"` in `tier4b_fee_schedule.py` / `entity_linker.py`. |

---

## 5. Sufficiency & Scan Certification

In strict accordance with [`LANGUAGE.md`](LANGUAGE.md) definitions:
- **`{sufficient}` Certification:** This scan has exhaustively enumerated the complete codebase dependency cone across backend graph models, Neo4j synchronization, FastAPI routes, GraphRAG entity linking/traversal/context assembly/synthesis, frontend React context/toolbar/canvas components, and verification test suites. All external and local datasources have been empirically probed using safe read-only operations, with raw ground-truth payloads saved to `assets/20261013T185957-734-5ytd/`. Every gap between `functional_specification_008.md` and the current codebase is documented with exact file, line, and symbol precision in the Explicit Deficiency Register. Zero ambiguity remains.
- **`{correctness}` Baseline:** All file paths, verbatim identifiers, node labels, edge types, and payload schemas match the active repository and live Neo4j database (`bolt://localhost:7687`) with 100% precision.
- **`{errors}` Absence:** Zero speculative contracts, hallucinated endpoints, mutating network calls, or invented components were introduced (`INV-BOUNDARY-01`, `INV-SCAN-01`, `INV-IDENTITY-01`, `INV-ABSENCE-01`).

---

## 6. Handoff Manifest Affirmation

The dedicated role handoff manifest at `handoff/20261013T185957-734-5ytd/plan-scan-2.txt` is atomically created and overwritten with exclusively repository-relative filepaths (one per line):
1. All reviewed and qualified codebase component files (`LANGUAGE.md`, `src/api/*`, `src/frontend/src/*`, `src/graph/*`, `src/graphrag/*`, `tests/*`, `exports/*`, `verify_all.py`).
2. This authored scan report at `scan_reports/scan_report_008_plan_scan_2.md`.
3. All 4 saved ground-truth empirical payload files in `assets/20261013T185957-734-5ytd/`:
   - `assets/20261013T185957-734-5ytd/neo4j_jurisdictions_and_states_audit.json`
   - `assets/20261013T185957-734-5ytd/cms_dmepos_fee_schedule_ca_ny_oh_tx_sample.json`
   - `assets/20261013T185957-734-5ytd/api_graph_topology_baseline.json`
   - `assets/20261013T185957-734-5ytd/api_graphrag_jurisdiction_and_state_probes.json`

No seed specification paths (`functional_specification_008.md`) are recorded in the handoff manifest, and `handoff/authored.txt`, `handoff/20261013T185957-734-5ytd/plan-scan-1.txt`, and all other run directories remain untouched.

---

## 7. Coding Gate Affirmation

DO NOT CODE YET: Implementation coding gate remains locked. Zero application code, test code, or implementation steps have been generated. Coding waits on an empty frontier and explicit operator authorization.
