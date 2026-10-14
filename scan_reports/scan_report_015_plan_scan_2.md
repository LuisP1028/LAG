# Authoritative Static Codebase Scan, External API Reconnaissance, and Schema Audit Report

**Run ID:** `20261014T030858-722-708n`  
**Agent:** `plan-scan-2` (Planning Node / Scanner Agent 2)  
**Governing Specification:** `functional_specification_015.md`  
**Status:** Complete Reconnaissance, Codebase Scan, and Empirical Schema Audit (DO NOT CODE YET)  
**Taxonomy Reference:** [LANGUAGE.md](file:///Users/diesel/Desktop/LAG/.sandcastle/worktrees/agent-plan-scan-2-20261014T030858-722-708n/LANGUAGE.md)

---

## 1. Governing Context & Upstream Ingestion Verification

In strict accordance with `INV-HANDOFF-01`, `INV-SCAN-01`, `INV-BOUNDARY-01`, and workspace rules:
- **Seed Specification Ingested:** `functional_specification_015.md` (*End-to-End Agnostic Graph Persistence, Retrieval, and Visualization Alignment*), verified non-empty, fully bound, and consumed as the single specification in scope. No other seed lines or unassigned specifications were scanned.
- **Run Identifier:** `20261014T030858-722-708n` (verified substituted across all asset paths and handoff manifest paths).
- **Wayfinder Architectural Map & Decision Tickets Inspected:**
  - Run-scoped directory `wayfinder/20261014T030858-722-708n/` was inspected (not yet synthesized prior to downstream planning).
  - Baseline Wayfinder Map inspected: `wayfinder/map.md` (*Wayfinder Architectural Map: GraphRAG Specification for Browser Graph Visualizer*)
  - Ticket 001: `wayfinder/tickets/ticket-001.md` — *Decision Ticket 001: Entity Anchor Linking and Layperson Vocabulary Normalization Specification*
  - Ticket 002: `wayfinder/tickets/ticket-002.md` — *Decision Ticket 002: Generalized Topological Subgraph Expansion and Neighborhood Traversal Specification*
  - Ticket 003: `wayfinder/tickets/ticket-003.md` — *Decision Ticket 003: Factual Context Assembly, Edge Provenance Formatting, and Prompt Grounding Specification*
  - Ticket 004: `wayfinder/tickets/ticket-004.md` — *Decision Ticket 004: Bidirectional Visual Canvas Synchronization and Active Subgraph Illumination Specification*
  - Ticket 005: `wayfinder/tickets/ticket-005.md` — *Decision Ticket 005: Master Specification Synthesis and Edits for functional_specification_004.md*
- **Evaluation Parameters Glossary:** Fully bound to [`LANGUAGE.md`](file:///Users/diesel/Desktop/LAG/.sandcastle/worktrees/agent-plan-scan-2-20261014T030858-722-708n/LANGUAGE.md), strictly adhering to authoritative definitions for `{errors}`, `{correctness}`, `{functionality}`, `{correct required outputs}`, `{sufficient}`, and `{insufficient}` without colloquial paraphrasing or semantic divergence.

---

## 2. Master Component Dependency Cone Register

The deterministic static scan of the active codebase cataloged all local modules, graph persistence engines, data models, REST endpoints, traversal engines, entity linkers, frontend visualizer components, synchronization context providers, styling registries, and automated test suites whose interfaces touch specced functionality in `functional_specification_015.md`:

| Repository-Relative Path | Verbatim Symbols & Interfaces | Role in Architecture | Grounding Justification (`functional_specification_015.md`) |
| :--- | :--- | :--- | :--- |
| `LANGUAGE.md` | `{errors}`, `{correctness}`, `{functionality}`, `{correct required outputs}`, `{sufficient}`, `{insufficient}`, `{Policy Keyword}`, `{Target_Bill_IDs}`, `{Enacted_Law_ID}`, `{US_Code_Citations}`, `{Operational_Filters}`, `{Clinical_Citations}`, `{HCPCS / CPT Codes}` | System-wide evaluation parameters and domain taxonomy glossary. | Section 1 mandates strict adherence of all evaluations and diagnostics to `LANGUAGE.md`. |
| `src/graph/models.py` | `EdgeProvenance`, `GraphEdge`, `BaseNode`, `PolicyNode`, `BillNode`, `PublicLawNode`, `StatutorySectionNode`, `USCSectionNode`, `RegulationNode`, `CFRSectionNode`, `ChangeRequestNode`, `TransmittalNode`, `CoveragePolicyNode`, `JurisdictionNode`, `StateNode`, `FeeScheduleEntryNode`, `FeeScheduleRateNode`, `HCPCSCodeNode`, `ProcedureCodeNode`, `ICD10CodeNode`, `DiagnosisCodeNode`, `LobbyingFilingNode`, `CBOScoreNode`, `LiteratureStudyNode`, `PolicyTraversalError`, `LegislativeHandoff`, `StatutoryHandoff`, `RegulatoryHandoff`, `OperationalHandoff`, `CoverageHandoff`, `CodingHandoff`, `ReimbursementHandoff` | Canonical domain graph entity models, typed handoff data contracts, and fail-fast exception classes. | Section 2.1 mandates exact schema, primary key formats, and attributes for all 15 node types. |
| `src/graph/engine.py` | `GraphValidationError`, `DirectedPropertyGraph`, `PropertyGraphEngine`, `run_pipeline`, `validate_invariants` | 8-hop knowledge graph assembly, MERGE idempotency, and topological invariant validation engine. | Section 2.1 mandates 8-hop graph topology synchronization, idempotent ingestion, and removal of stale/shortcut edges. |
| `src/graph/neo4j_sync.py` | `DEFAULT_NEO4J_URI`, `DEFAULT_NEO4J_USER`, `DEFAULT_NEO4J_PASSWORD`, `DEFAULT_NEO4J_DATABASE`, `Neo4jSyncEngine`, `get_driver`, `close`, `init_schema`, `sync_graph_dict`, `sync_file`, `get_summary_statistics` | Neo4j property graph synchronization engine executing APOC batched merge statements, constraint creation, and summary metrics. | Section 2.1 requires live Neo4j graph database synchronization with unique primary key constraints across all entity types. |
| `src/graph/tier1_legislative.py` | `discover_legislation` | Tier 1 legislative discovery and omnibus incorporation pipeline module. | Generates `Policy`, `Bill`, and `PublicLaw` nodes with `DISCOVERED_BILL`, `INCORPORATED_INTO`, and `ENACTED_AS` relationships (Section 2.1). |
| `src/graph/tier2_statutory.py` | `parse_statutory_codification` | Tier 2 statutory codification and USLM XML section extraction pipeline module. | Generates `StatutorySection` and `USCSection` nodes with `CONTAINS` and `AMENDS` relationships (Section 2.1). |
| `src/graph/tier3_regulatory.py` | `harvest_regulations` | Tier 3 Federal Register Final Rule and CMS Transmittal harvesting pipeline module. | Generates `Regulation`, `CFRSection`, and `Transmittal` nodes with `AUTHORIZED_BY`, `CODIFIED_IN`, and `IMPLEMENTED_BY` relationships (Section 2.1). |
| `src/graph/tier4a_coverage.py` | `ingest_coverage_policy` | Tier 4A clinical coverage policy guidance and ICD-10 diagnosis / HCPCS procedure extraction module. | Generates `CoveragePolicy`, `DiagnosisCode`, and `ProcedureCode` nodes with `MANDATES_POLICY`, `REQUIRES_DIAGNOSIS`, and `COVERS_PROCEDURE` relationships (Section 2.1). |
| `src/graph/tier4b_fee_schedule.py` | `DME_MAC_JURISDICTIONS`, `normalize_fee_schedules` | Tier 4B jurisdiction contractor, 54-jurisdiction state mapping, and DMEPOS fee schedule normalization module. | Generates `Jurisdiction`, `State` (all 54 jurisdictions), and `FeeScheduleRate` nodes with `APPLIES_TO_JURISDICTION`, `COVERS_STATE`, `HAS_RATE`, and `APPLIES_TO_STATE` relationships (Section 2.1). |
| `src/graph/tier5_context.py` | `enrich_context` | Tier 5 contextual record enrichment module. | Generates `LobbyingFiling`, `CBOScore`, and `LiteratureStudy` nodes with `HAS_ADVOCACY_RECORD`, `HAS_BUDGET_IMPACT`, and `SUPPORTED_BY_EVIDENCE` relationships (Section 2.1). |
| `src/graph/__init__.py` | Graph package exports | Root exports for property graph models, engine, and synchronization. | Core module boundary for `src.graph`. |
| `src/api/routes.py` | `router`, `set_sync_engine`, `get_sync_engine`, `get_pipeline`, `get_neo4j_session`, `health_check`, `get_graph_summary`, `get_graph_topology`, `resolve_entities`, `get_subgraph_by_anchors`, `execute_graphrag_query` | FastAPI REST router exposing graph topology, entity resolution, subgraph extraction, and conversational synthesis endpoints. | Governs Section 3.1 (Graph Topology & Summary Service), Section 3.2 (Dynamic Entity Anchor Resolution), and Section 3.3 (Subgraph Traversal). |
| `src/api/models.py` | `HealthResponse`, `TopologyNode`, `TopologyEdge`, `TopologyResponse`, `EntityResolveRequest`, `EntityResolveResponse`, `SubgraphRequest`, `SubgraphResponse`, `ErrorEnvelope` | Pydantic request/response schema models for API endpoints. | Defines data contracts for topology nodes, edges, provenance metadata, and error envelopes (Section 3.1 & Section 3.2). |
| `src/api/server.py` | `lifespan`, `create_app`, `app`, `http_exception_handler`, `graphrag_exception_handler` | FastAPI application factory, lifespan manager initializing Neo4j driver and GraphRAG pipeline, and global exception handlers. | Hosts the backend API server and manages connection lifecycles. |
| `src/api/__init__.py` | API package exports (`app`, `create_app`) | Module boundary for `src.api`. | Package export interface. |
| `src/graphrag/traversal.py` | `TopologicalTraversalEngine`, `extract_connecting_subgraph`, `_execute_single_entity_traversal`, `_execute_jurisdiction_traversal`, `_execute_single_state_traversal`, `_execute_single_clinical_traversal`, `_execute_single_general_traversal`, `_execute_multi_entity_traversal`, `_execute_pattern_a`, `_execute_pattern_b`, `_execute_pattern_c`, `_convert_node`, `_convert_edge` | Neo4j Cypher topological traversal engine executing single-entity and multi-entity relationship chain expansions. | Section 3.3 requires traversing the complete relationship chain: `DISCOVERED_BILL` $\to$ `INCORPORATED_INTO` $\to$ `ENACTED_AS` $\to$ `CONTAINS` $\to$ `AMENDS` $\to$ `AUTHORIZED_BY` $\to$ `CODIFIED_IN` $\to$ `IMPLEMENTED_BY` $\to$ `MANDATES_POLICY` $\to$ `REQUIRES_DIAGNOSIS` / `COVERS_PROCEDURE` $\to$ `HAS_RATE` $\to$ `APPLIES_TO_STATE`. |
| `src/graphrag/entity_linker.py` | `EntityAnchorLinker`, `STATE_NAME_TO_CODE`, `CLINICAL_SYNONYMS`, `POLICY_TRIGGERS`, `HCPCS_REGEX`, `GEO_LOCATION_INDICATORS`, `PK_TOKEN_REGEX`, `resolve_anchors`, `resolve_explicit_anchor` | Multi-slot entity anchor linker resolving natural language terms and explicit primary keys against Neo4j. | Section 3.2 requires dynamic entity anchor resolution across all 54 states/territories and explicit primary key lookups across all valid prefixes. |
| `src/graphrag/context_assembler.py` | `GraphContextAssembler`, `assemble_context`, `_assemble_administrative_block`, `_assemble_clinical_block`, `_assemble_reimbursement_block`, `_format_provenance_citations` | Assembles structured factual Markdown contexts from traversed node and edge attributes. | Section 3.3 requires context synthesis exclusively from traversed node and edge attributes without static fallbacks or hardcoded citations. |
| `src/graphrag/synthesizer.py` | `HuggingFaceSynthesizer`, `synthesize`, `_call_hf_inference_api` | Calls Hugging Face Serverless Inference Router for natural language synthesis grounded in assembled context. | Section 3.3 context synthesis consumer. |
| `src/graphrag/pipeline.py` | `GraphRAGPipeline`, `execute_query` | Orchestrates end-to-end GraphRAG pipeline from user query to anchor resolution, traversal, assembly, and synthesis. | Section 3 retrieval and context synthesis service. |
| `src/graphrag/models.py` | `AnchorEntity`, `ResolvedAnchors`, `TraversalNode`, `TraversalEdge`, `TraversalResult`, `GraphRAGQueryRequest`, `GraphRAGQueryResponse` | Pydantic data models for GraphRAG pipeline stages. | Defines data contracts for traversed nodes, edges, and query responses. |
| `src/graphrag/exceptions.py` | `GraphRAGException`, `EntityResolutionError`, `TraversalError`, `ModelInferenceError`, `ModelAuthenticationError`, `ModelRateLimitError`, `GraphValidationError` | Strict fail-fast exception hierarchy enforcing `INV-FAIL-FAST`. | Section 3.1 & 3.2 fail-fast behavior contracts. |
| `src/graphrag/__init__.py` | GraphRAG package exports | Module boundary for `src.graphrag`. | Package export interface. |
| `src/frontend/src/types/graph.ts` | `NodeProperties`, `EdgeProvenance`, `GraphNode`, `GraphLink`, `AnchorEntity`, `GraphRAGQueryResponse`, `GraphSummary` | TypeScript interfaces for graph topology nodes, directed links, provenance metadata, and query responses. | Defines the visualizer data model across Section 3 and Section 4. |
| `src/frontend/src/styles/graph_theme.ts` | `NodeVisualConfig`, `NODE_THEME_REGISTRY`, `CANVAS_PALETTE`, `getNodeVisual` | Authoritative visual theme registry defining colors, radii, and shapes for graph entity labels. | Section 4.1 mandates visual taxonomy distinguishing all 17 entity categories. |
| `src/frontend/src/components/GraphCanvas.tsx` | `GraphCanvasProps`, `GraphCanvas`, `canvasRef`, `simulationRef`, `transformRef`, `zoomBehaviorRef`, `renderRef`, `frameActiveSubgraph`, `render` | Force-directed HTML5 canvas visualizer executing D3 simulation, active path illumination, and zoom/pan camera framing. | Section 4.1 requires rendering all entity categories with distinct visuals and dynamic labels/tooltips. |
| `src/frontend/src/components/NodeDetailDrawer.tsx` | `NodeDetailDrawerProps`, `NodeDetailDrawer`, `connectedNeighbors`, `getGovernmentSourceLink`, `selectedNode`, `selectNode`, `inquireNode` | Slide-over inspection drawer rendering full persisted property tables and external government source links. | Section 4.2 mandates display of all persisted properties without omission and dynamic construction of government links without static fallback IDs. |
| `src/frontend/src/components/FilterToolbar.tsx` | `FilterToolbarProps`, `FilterToolbar`, `handleJurisdictionChange`, `handleStateChange`, `handlePolicyChange`, `clearIllumination` | Top navigation toolbar containing jurisdiction, state, and policy dropdown selectors and reset controls. | Section 4.3 mandates interactive filter controls populated with all 54 jurisdictions and dynamic policy selectors. |
| `src/frontend/src/components/AgentChatDrawer.tsx` | `AgentChatDrawer`, `handleSend`, `inputQuery`, `modelId`, `isChatOpen`, `setIsChatOpen`, `messages`, `isQueryLoading`, `errorMsg`, `submitInquiry` | Conversational GraphRAG drawer displaying quick prompts, synthesized answers, and illumination badges. | Section 3 & 4 user interface layer. |
| `src/frontend/src/context/GraphSyncContext.tsx` | `ChatMessage`, `StateOption`, `JurisdictionMetadata`, `DME_JURISDICTIONS`, `STATE_TO_JURISDICTION`, `ALL_STATES_SORTED`, `GraphSyncContextType`, `GraphSyncProvider`, `useGraphSync` | React Context synchronization bus managing active nodes/edges, selection, filter state, and API inquiries. | Section 4.3 state and jurisdiction population and canvas-agent synchronization. |
| `src/frontend/src/utils/promptGenerator.ts` | `constructInquiryPrompt` | Generates deterministic inquiry prompts for node inspection inquiries. | Section 4.2 drawer inquiry actions. |
| `src/frontend/src/App.tsx` | `RawTopologyNode`, `RawTopologyEdge`, `RawTopologyResponse`, `MainVisualizer`, `App`, `fetchTopology` | Top-level visualizer application fetching topology and coordinating layout. | Section 4 visualizer integration. |
| `src/frontend/src/main.tsx` | `createRoot`, `StrictMode`, `App` | React 19 entrypoint mounting visualizer. | Application entrypoint. |
| `src/frontend/src/index.css` | Global styling (`#root`, `body`, `html`) | Full-viewport styles. | Viewport container dimensions. |
| `src/frontend/src/App.css` | Component styles | CSS styling asset. | Frontend asset. |
| `src/frontend/package.json` | Dependencies and npm scripts | Frontend manifest (`react@^19.2.8`, `d3@^7.9.0`, `lucide-react`). | Build and dependency manifest. |
| `src/frontend/vite.config.ts` | Vite dev server and proxy configuration | Proxies `/api` to FastAPI backend. | Local dev server configuration. |
| `tests/test_graph_pipeline.py` | Graph construction and invariant verification test suite | Verifies 8 hops, typed handoffs, omnibus topology, 54 jurisdictions, and fail-fast errors. | Validates Acceptance Criterion 1 & 4 (Section 5). |
| `tests/test_api_endpoints.py` | FastAPI REST integration test suite | Verifies `/api/health`, `/api/graph/summary`, `/api/graph/topology`, `/api/entities/resolve`, `/api/graphrag/subgraph`, and `/api/graphrag/query`. | Validates Acceptance Criterion 2, 3, & 4 (Section 5). |
| `tests/test_graphrag_pipeline.py` | GraphRAG pipeline and oracle verification test suite | Tests all 6 retrieval and synthesis oracles and latency benchmarks. | Validates Acceptance Criterion 3 & 4 (Section 5). |
| `verify_all.py` | `main` | CLI verification test harness orchestrating unit and integration suites. | Acceptance testing harness. |

---

## 3. Candidate External Datasource & Schema Audit Register

In strict adherence to `INV-SCAN-01`, active read-only reconnaissance was conducted against live external datasources, public government endpoints, the live Neo4j graph database, and local FastAPI services. All queries were non-mutating (safe GET requests). Raw, unedited empirical payloads were captured directly into `assets/20261014T030858-722-708n/`.

### 3.1. Live Neo4j Graph Database (`bolt://localhost:7687`, database `neo4j`)
- **Role in Specification:** The live persistent graph backing store across Section 2, Section 3, and Section 4.
- **Connection Parameters:** `bolt://localhost:7687`, user `neo4j`, pass `qwertyui`, database `neo4j`. Verified live and connected via Python Neo4j driver and FastAPI health check.
- **Audited Empirical Schema & Statistics:**
  - **Total Nodes:** `3,971` nodes.
  - **Observed Node Labels & Counts:**
    - `['PolicyNode', 'FeeScheduleEntry']`: `3,816`
    - `['PolicyNode', 'HCPCSCode']`: `75`
    - `['PolicyNode', 'State']`: `53`
    - `['Strategy']`: `7`
    - `['PolicyNode', 'ICD10Code']`: `6`
    - `['PolicyNode', 'Jurisdiction']`: `4`
    - `['PolicyNode', 'Bill']`: `3`
    - `['PolicyNode', 'Policy']`: `2`
    - `['PolicyNode', 'StatutorySection']`: `2`
    - `['PolicyNode', 'ChangeRequest']`: `2`
    - `['PolicyNode', 'CoveragePolicy']`: `2`
    - `['PolicyNode', 'LobbyingFiling']`: `2`
    - `['PolicyNode', 'LiteratureStudy']`: `2`
    - `['PolicyNode', 'PublicLaw']`: `1`
    - `['PolicyNode', 'Regulation']`: `1`
    - `USCSection`: `0` nodes present.
    - `CFRSection`: `0` nodes present.
    - `CBOScore`: `0` nodes present.
  - **Total Edges:** `7,786` relationships.
  - **Observed Relationship Types & Counts:**
    - `HAS_FEE_SCHEDULE`: `3,816`
    - `APPLIES_TO`: `3,816`
    - `GOVERNS`: `75`
    - `COVERS_STATE`: `53`
    - `APPLIES_TO_JURISDICTION`: `8`
    - `ALLOWS_DIAGNOSIS`: `6`
    - `TARGETS_BILL`: `4`
    - `HAS_ADVOCACY_RECORD`: `4`
    - `ENACTED_AS`: `3`
    - `MODIFIES_CODE`: `2`
    - `IMPLEMENTED_BY`: `2`
    - `ISSUES_TRANSMITTAL`: `2`
    - `SUPPORTED_BY_EVIDENCE`: `2`
    - `MANDATES_POLICY`: `2`
  - **Constraints:**
    - `policy_node_pk` on `PolicyNode(primary_key)`
    - `constraint_2423f728` on `Strategy(id)`
  - **Saved Ground-Truth Assets:**
    - `assets/20261014T030858-722-708n/neo4j_node_labels_and_counts.json`
    - `assets/20261014T030858-722-708n/neo4j_relationship_types_and_counts.json`
    - `assets/20261014T030858-722-708n/neo4j_schema_constraints.json`
    - `assets/20261014T030858-722-708n/neo4j_schema_indexes.json`
    - `assets/20261014T030858-722-708n/neo4j_sample_nodes_by_label.json`
    - `assets/20261014T030858-722-708n/neo4j_sample_edges_with_provenance.json`

---

### 3.2. Local FastAPI Endpoints (`/api/graph/topology`, `/api/entities/resolve`, `/api/graphrag/subgraph`)
- **Role in Specification:** Backend retrieval and context synthesis API endpoints consumed by the React visualizer and inspection drawer.
- **Audited Empirical Schemas:**
  - `GET /api/graph/topology`: Returns `TopologyResponse` (`nodes`: `List[TopologyNode]`, `edges`: `List[TopologyEdge]`, `total_nodes`: `int`, `total_edges`: `int`).
    - Baseline (unexpanded): `155` nodes, `163` edges.
    - State-filtered (`state_filter=WI`): `226` nodes, `305` edges.
  - `POST /api/entities/resolve`: Returns `EntityResolveResponse` (`anchors`: `List[AnchorEntity]`, `total_anchors`: `int`).
    - Input: `{"query": "I am from Wisconsin with breast cancer and lymphedema"}`
    - Output: Resolves `STATE-WI` and `ICD10-I97.2`.
  - `POST /api/graphrag/subgraph`: Returns `SubgraphResponse` (`nodes`, `edges`, `retrieval_ms`, `total_nodes`, `total_edges`).
  - **Saved Ground-Truth Assets:**
    - `assets/20261014T030858-722-708n/api_graph_topology_baseline.json`
    - `assets/20261014T030858-722-708n/api_graph_topology_state_wi.json`
    - `assets/20261014T030858-722-708n/api_entities_resolve_response.json`
    - `assets/20261014T030858-722-708n/api_graphrag_subgraph_response.json`

---

### 3.3. Federal Register API (`https://www.federalregister.gov/api/v1/documents/2023-24455.json`)
- **Role in Specification:** Authoritative source for Federal Register Final Rules (Hop 3 / Section 2.1 Entity 6).
- **Authentication:** Public GET, no authentication required.
- **Audited Empirical Schema:**
  - `document_number`: `"2023-24455"` (`str`)
  - `citation`: `"88 FR 77676"` (`str`)
  - `docket_ids`: `["CMS-1780-F"]` (`List[str]`)
  - `regulation_id_number`: `"0938-AV03"` (`str`)
  - `effective_on`: `"2024-01-01"` (`str`)
  - `cfr_references`: Array of objects `[{"title": 42, "part": 414}, ...]`
- **Saved Ground-Truth Asset:**
  - `assets/20261014T030858-722-708n/stage3_federal_register_rule_2023_24455.json`

---

### 3.4. eCFR API (`https://www.ecfr.gov/api/search/v1/results?query=lymphedema`)
- **Role in Specification:** Authoritative source for codified Code of Federal Regulations sections (Hop 3 / Section 2.1 Entity 7).
- **Authentication:** Public GET, no authentication required.
- **Audited Empirical Schema:**
  - `results`: Array of section objects:
    - `starts_on`: `"2024-01-01"`
    - `type`: `"Section"`
    - `hierarchy`: `{"title": "42", "part": "414", "section": "414.1650", ...}`
- **Saved Ground-Truth Asset:**
  - `assets/20261014T030858-722-708n/ecfr_search_lymphedema.json`

---

### 3.5. NIH / NLM Clinical Tables APIs (ICD-10-CM & HCPCS)
- **Role in Specification:** Authoritative clinical vocabulary endpoints for qualifying diagnosis codes and covered procedure codes (Hop 5 & Hop 6 / Section 2.1 Entities 10 & 11).
- **Endpoints Probed:**
  1. `https://clinicaltables.nlm.nih.gov/api/icd10cm/v3/search?terms=lymphedema&sf=code,name&maxList=10`
     - Status: 200 OK.
     - Payload Structure: Array format `[total_count, [codes], null, [[code, description], ...]]`
     - Returns: `Q82.0` (*Hereditary lymphedema*), `I97.2` (*Postmastectomy lymphedema syndrome*), `I89.0` (*Lymphedema, not elsewhere classified*).
  2. `https://clinicaltables.nlm.nih.gov/api/hcpcs/v3/search?terms=A6522&sf=code,name&maxList=5`
     - Status: 200 OK.
     - Payload Structure: Array format `[1, ["A6522"], null, [["A6522", "G com garment arm nighttime"]]]`
- **Saved Ground-Truth Assets:**
  - `assets/20261014T030858-722-708n/nlm_icd10cm_search_lymphedema.json`
  - `assets/20261014T030858-722-708n/nlm_hcpcs_search_a6522.json`

---

### 3.6. NCBI PubMed ESummary API (`https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi`)
- **Role in Specification:** Evidentiary biomedical literature studies cited in regulatory preambles (Hop 8 / Section 2.1 Entity 15).
- **Authentication:** Public GET, no API key required for low-volume queries.
- **Audited Empirical Schema:**
  - `result`: Object mapping `uids: ["37924455"]` and `37924455: {"uid": "37924455", "pubdate": "2023 Dec", "source": "Clin Exp Med", "title": "...", "authors": [...]}`
- **Saved Ground-Truth Asset:**
  - `assets/20261014T030858-722-708n/ncbi_pubmed_esummary.json`

---

### 3.7. Hugging Face Serverless Inference Router (`https://router.huggingface.co/v1/models`)
- **Role in Specification:** Natural language context synthesis engine (Section 3.3).
- **Authentication:** Bearer token via `HF_TOKEN` in `.env`.
- **Status:** Reachable, 200 OK, returns 79KB model directory.
- **Saved Ground-Truth Asset:**
  - `assets/20261014T030858-722-708n/hf_router_v1_models.json`

---

### 3.8. Senate Lobbying Disclosure Act (LDA) API (`https://lda.senate.gov/api/v1/filings/`)
- **Role in Specification:** Contextual lobbying records (Hop 8 / Section 2.1 Entity 15).
- **Authentication & Behavior:** Redirects 301 from `lda.senate.gov` to `lda.gov/api/v1/filings/`, responding with 200 OK JSON payload (`count: 93513`, `results: [...]`).
- **Saved Ground-Truth Assets:**
  - `assets/20261014T030858-722-708n/lda_filings_probe_headers.txt`
  - `assets/20261014T030858-722-708n/lda_filings_redirect_headers.txt`
  - `assets/20261014T030858-722-708n/stage5_lda_lobbying_filings_sample.json`

---

### 3.9. Government Web Portals & Authenticated APIs Probing
- **GPO GovInfo (`https://www.govinfo.gov/app/details/PLAW-117publ328`):** Public web page reachable, returns HTML with metadata tags (`dc.title`, `dc.date`). API (`api.govinfo.gov`) requires `api_key` (returns 401 `API_KEY_MISSING` without key).
  - Saved: `assets/20261014T030858-722-708n/govinfo_plaw_117publ328_probe.html`, `assets/20261014T030858-722-708n/govinfo_api_no_key_probe.txt`.
- **Congress.gov (`https://api.congress.gov/v3/bill/117/hr/3630`):** API requires `api_key` (returns 403 `API_KEY_MISSING`). Public web page utilizes Cloudflare challenge for automated user-agents.
  - Saved: `assets/20261014T030858-722-708n/congress_api_no_key_probe.txt`, `assets/20261014T030858-722-708n/congress_gov_bill_3630_probe.html`.
- **CMS MCD (`https://www.cms.gov/medicare-coverage-database/view/article.aspx?articleid=59508`):** Returns 302 with session cookie.
  - Saved: `assets/20261014T030858-722-708n/cms_mcd_a59508_headers.txt`.

---

## 4. Explicit Deficiency Register

In strict compliance with `INV-ABSENCE-01`, the following specced requirements in `functional_specification_015.md` are currently defective, incomplete, or divergent in the active codebase. Zero components or endpoints have been invented.

| Deficiency ID | Affected Component(s) | Specced Requirement (`functional_specification_015.md`) | Empirical Observation & Exact Codebase Deficiency |
| :--- | :--- | :--- | :--- |
| **`DEF-001`** | `src/graph/neo4j_sync.py`, `exports/lta_knowledge_graph.json`, Live Neo4j Database | **Req 2.1 (Agnostic Node Label & Entity Persistence):** Persist all 15 entity types with unique primary key constraints: `Policy`, `Bill`, `PublicLaw`, `StatutorySection`, `USCSection`, `Regulation`, `CFRSection`, `Transmittal`, `CoveragePolicy`, `DiagnosisCode`, `ProcedureCode`, `FeeScheduleRate`, `Jurisdiction`, `State`, `LobbyingFiling`, `CBOScore`, `LiteratureStudy`. | **Live Neo4j and Export Schema Divergence:** The live Neo4j database currently contains legacy node labels: `FeeScheduleEntry` (3,816 nodes) instead of `FeeScheduleRate`, `HCPCSCode` (75 nodes) instead of `ProcedureCode`, `ICD10Code` (6 nodes) instead of `DiagnosisCode`, `ChangeRequest` (2 nodes) instead of `Transmittal`. Furthermore, `USCSection`, `CFRSection`, and `CBOScore` have 0 nodes in the live graph. `neo4j_sync.py`'s `init_schema` omits uniqueness constraints/indexes for `USCSection` and `CFRSection`, and only indexes the legacy labels. |
| **`DEF-002`** | `src/graph/neo4j_sync.py`, `src/graphrag/traversal.py`, `exports/lta_knowledge_graph.json`, Live Neo4j Database | **Req 2.1 & 3.3 (Topological Relationship Types):** Persist and traverse the canonical relationship chain: `DISCOVERED_BILL` $\to$ `INCORPORATED_INTO` $\to$ `ENACTED_AS` $\to$ `CONTAINS` $\to$ `AMENDS` $\to$ `AUTHORIZED_BY` $\to$ `CODIFIED_IN` $\to$ `IMPLEMENTED_BY` $\to$ `MANDATES_POLICY` $\to$ `REQUIRES_DIAGNOSIS` / `COVERS_PROCEDURE` $\to$ `HAS_RATE` $\to$ `APPLIES_TO_STATE`. | **Obsolete Shortcut and Legacy Relationship Types in Live DB and Traversal:** The live database and `exports/lta_knowledge_graph.json` contain legacy relationship types: `TARGETS_BILL` (4) instead of `DISCOVERED_BILL`, `MODIFIES_CODE` (2) instead of `CONTAINS` and `AMENDS`, `ISSUES_TRANSMITTAL` (2) instead of `CODIFIED_IN` and `IMPLEMENTED_BY`, `ALLOWS_DIAGNOSIS` (6) instead of `REQUIRES_DIAGNOSIS`, `GOVERNS` (75) instead of `COVERS_PROCEDURE`, `HAS_FEE_SCHEDULE` (3,816) instead of `HAS_RATE`, `APPLIES_TO` (3,816) instead of `APPLIES_TO_STATE`. In `src/graphrag/traversal.py`, Cypher queries hardcode these obsolete labels, omitting `USCSection` and `CFRSection` intermediate hops. |
| **`DEF-003`** | `src/graph/tier4b_fee_schedule.py`, `src/graphrag/entity_linker.py`, `src/frontend/src/context/GraphSyncContext.tsx`, Live Neo4j Database | **Req 2.1, 3.1, 3.2, 4.3 (Complete 54-Jurisdiction Support Including Guam `GU`):** Ingestion, retrieval, entity resolution, and UI state filters must support all 54 US states, districts, and territories (`50 states + DC + PR + VI + GU`). | **Missing Guam (`GU`) Across Graph and Frontend:** The live Neo4j database contains exactly 53 `State` nodes (Guam `STATE-GU` is missing). In `src/graphrag/entity_linker.py`, `STATE_NAME_TO_CODE` lists only 53 entries (Guam is missing). In `src/frontend/src/context/GraphSyncContext.tsx`, `DME_JURISDICTIONS['JURIS-DME-D']` lists 17 states omitting `GU`, leaving `ALL_STATES_SORTED` with 53 entries. |
| **`DEF-004`** | `src/api/routes.py` (lines 176–206, 241–335) | **Req 3.1 (Agnostic Topology Retrieval & State/Jurisdiction Scoping):** Query baseline non-rate topology, state-filtered rates, and contractor/state nodes scoped to selected jurisdiction/state. | **Hardcoded Legacy Label Filters in API Routes:** In `src/api/routes.py`, `get_graph_topology` queries `MATCH (n:PolicyNode) WHERE NOT n:FeeScheduleEntry`, and state fee query matches `(f:FeeScheduleEntry)-[r1:APPLIES_TO]->(s:State) ... (h:HCPCSCode)-[r2:HAS_FEE_SCHEDULE]->(f)`. If canonical nodes (`FeeScheduleRate`, `HAS_RATE`, `APPLIES_TO_STATE`, `ProcedureCode`) are present, they are unqueried. Furthermore, `convert_node` lacks fallback cases for `STAT-`, `REG-FR-`, `CFR-`, `TR-CR`, `DME-MAC-`, `CBO-`, and incorrectly maps `USC-` to `StatutorySection` instead of `USCSection`. |
| **`DEF-005`** | `src/graphrag/entity_linker.py` (lines 14–63, 73–102, 553–570) | **Req 3.2 (Dynamic Entity Anchor Resolution across All Prefixes):** Resolve candidate search terms and codes dynamically against persisted graph entities, supporting explicit primary key lookup across all 17 valid prefixes (`POLICY-`, `BILL-`, `PLAW-`, `STAT-`, `USC-`, `REG-FR-`, `CFR-`, `TR-CR`, `DME-MAC-`, `CMS-MCD-`, `ICD10-`, `HCPCS-`, `FEE-`, `JURIS-DME-`, `STATE-`, `LDA-`, `CBO-`, `PUBMED-`). | **Hardcoded Keyword Triggers and Incomplete Prefix Mapping:** `EntityAnchorLinker` in `entity_linker.py` relies on hardcoded regex triggers (`POLICY_TRIGGERS` for `LTA` and `IVIG`, `CLINICAL_SYNONYMS` for 4 conditions) rather than resolving dynamically against graph titles/keywords. Its slot mapping in `resolve_anchors` does not recognize `statutorysection`, `uscsection`, `cfrsection`, `transmittal`, `feeschedulerate`, or `cboscore`. |
| **`DEF-006`** | `src/frontend/src/styles/graph_theme.ts` (lines 12–97) | **Req 4.1 (Visual Taxonomy for All 17 Entity Categories):** Render and distinguish all entity categories on canvas (`Policy`, `Bill`, `PublicLaw`, `StatutorySection`, `USCSection`, `Regulation`, `CFRSection`, `Transmittal`, `CoveragePolicy`, `DiagnosisCode`, `ProcedureCode`, `FeeScheduleRate`, `Jurisdiction`, `State`, `LobbyingFiling`, `CBOScore`, `LiteratureStudy`). | **Missing Visual Configurations in Theme Registry:** `NODE_THEME_REGISTRY` contains only 14 configurations. `USCSection`, `CFRSection`, and `CBOScore` are completely absent. In addition, existing entries use legacy names (`ChangeRequest`, `HCPCSCode`, `ICD10Code`, `FeeScheduleEntry`), causing new canonical labels to default to generic gray circles (`#64748b`, radius 9). |
| **`DEF-007`** | `src/frontend/src/components/NodeDetailDrawer.tsx` (lines 69–157, 312–330) | **Req 4.2 (Node Detail Drawer & Dynamic Government Source Links):** Display all persisted properties without omission; construct external government links dynamically from node attributes, omitting links if required attributes are missing. | **Static Fallback Identifiers in Government Link Construction:** In `NodeDetailDrawer.tsx`, `getGovernmentSourceLink` hardcodes static fallback identifiers: Congress `'117'`, Bill number `'3630'`, Public Law number `'328'`, Title `'42'`, Section `'1395x'`, violating Section 1 & Section 4.2 ("If required attributes are missing, omit the link rather than substituting fallback IDs"). Links for `USCSection`, `CFRSection`, and `CBOScore` are unhandled. |
| **`DEF-008`** | `src/frontend/src/components/FilterToolbar.tsx` (lines 120–140) | **Req 4.3 (Interactive Filter Controls Populated Dynamically):** Populate policy and domain selectors dynamically from entities available in the graph database. | **Hardcoded Policy Selector Dropdown:** `FilterToolbar.tsx` hardcodes static options (`<option value="LTA">`, `<option value="IVIG">`, `<option value="ALL">`) rather than fetching available policies dynamically from `/api/graph/topology` or `/api/graph/summary`. |
| **`DEF-009`** | `tests/test_api_endpoints.py`, `tests/test_graphrag_pipeline.py` | **Req 5.4 (Automated Verification):** Verification test suites must validate agnostic multi-hop graph contracts, canonical labels, and dynamic resolution. | **Test Suites Bound to Legacy Schema and Static Node Counts:** `tests/test_api_endpoints.py` asserts hardcoded node counts (`assert data["total_nodes"] == 3971`) and legacy labels (`FeeScheduleEntry`). `tests/test_graphrag_pipeline.py` asserts legacy chain keys (`CMS-CR-13286`, `GOVERNS`, `ALLOWS_DIAGNOSIS`). |

---

## 5. Sufficiency & Scan Certification

- **Dependency Cone Exhaustiveness:** Every active module and interface touching graph persistence, API routing, GraphRAG retrieval, and visualizer UI has been static-scanned and recorded in Section 2.
- **Empirical Grounding:** All 24 ground-truth sample payloads in `assets/20261014T030858-722-708n/` were captured from responding live systems (local Neo4j instance, local FastAPI TestClient, Federal Register API, eCFR API, NIH NLM ICD-10 & HCPCS APIs, NCBI PubMed API, Hugging Face Router, Senate LDA API, and GPO GovInfo). Zero schemas were hallucinated or assumed.
- **Sufficiency State:** The documentation and empirical findings in this report achieve the `{sufficient}` state under [`LANGUAGE.md`](file:///Users/diesel/Desktop/LAG/.sandcastle/worktrees/agent-plan-scan-2-20261014T030858-722-708n/LANGUAGE.md). Zero ambiguity remains regarding the discrepancies between `functional_specification_015.md` and the existing codebase.

---

## 6. Handoff Manifest Affirmation

The dedicated role handoff manifest at `handoff/20261014T030858-722-708n/plan-scan-2.txt` has been atomically overwritten with exactly one repository-relative path per line. It includes all qualified codebase component files, this authored scan report, and all saved ground-truth payload sample files in `assets/20261014T030858-722-708n/`. It records zero seed paths.

---

## 7. Coding Gate Affirmation

> [!IMPORTANT]
> **DO NOT CODE YET: Implementation coding gate remains locked. Zero application code, test code, or implementation steps have been generated. Coding waits on an empty frontier and explicit operator authorization.**
