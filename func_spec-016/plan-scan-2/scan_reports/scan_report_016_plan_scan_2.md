# Authoritative Static Codebase Scan, External API Reconnaissance, and Schema Audit Report

**Run ID:** `20261014T044849-392-31ky`  
**Agent:** `plan-scan-2` (Planning Node / Scanner Agent 2)  
**Governing Specification:** `functional_specification_016.md`  
**Status:** Complete Reconnaissance, Codebase Scan, and Empirical Schema Audit (DO NOT CODE YET)  
**Taxonomy Reference:** [LANGUAGE.md](file:///Users/diesel/Desktop/LAG/.sandcastle/worktrees/agent-plan-scan-2-20261014T044849-392-31ky/LANGUAGE.md)

---

## 1. Governing Context & Upstream Ingestion Verification

In strict accordance with `INV-HANDOFF-01`, `INV-SCAN-01`, `INV-BOUNDARY-01`, and workspace rules:
- **Seed Specification Ingested:** `functional_specification_016.md` (*Dual-Platform Deployment Architecture for Interactive Engine Web Showcase (GitHub Pages & Hugging Face)*), verified non-empty, fully bound, and consumed as the single specification in scope. No other seed lines or unassigned specifications were scanned.
- **Run Identifier:** `20261014T044849-392-31ky` (verified substituted across all asset paths and handoff manifest paths).
- **Wayfinder Architectural Map & Decision Tickets Inspected:**
  - Run-scoped directory `wayfinder/20261014T044849-392-31ky/` was inspected (not yet synthesized prior to downstream planning).
  - Baseline Wayfinder Map inspected: `wayfinder/map.md` (*Wayfinder Architectural Map: GraphRAG Specification for Browser Graph Visualizer*)
  - Ticket 001: `wayfinder/tickets/ticket-001.md` — *Decision Ticket 001: Entity Anchor Linking and Layperson Vocabulary Normalization Specification*
  - Ticket 002: `wayfinder/tickets/ticket-002.md` — *Decision Ticket 002: Generalized Topological Subgraph Expansion and Neighborhood Traversal Specification*
  - Ticket 003: `wayfinder/tickets/ticket-003.md` — *Decision Ticket 003: Factual Context Assembly, Edge Provenance Formatting, and Prompt Grounding Specification*
  - Ticket 004: `wayfinder/tickets/ticket-004.md` — *Decision Ticket 004: Bidirectional Visual Canvas Synchronization and Active Subgraph Illumination Specification*
  - Ticket 005: `wayfinder/tickets/ticket-005.md` — *Decision Ticket 005: Master Specification Synthesis and Edits for functional_specification_004.md*
- **Evaluation Parameters Glossary:** Fully bound to [`LANGUAGE.md`](file:///Users/diesel/Desktop/LAG/.sandcastle/worktrees/agent-plan-scan-2-20261014T044849-392-31ky/LANGUAGE.md), strictly adhering to authoritative definitions for `{errors}`, `{correctness}`, `{functionality}`, `{correct required outputs}`, `{sufficient}`, and `{insufficient}` without colloquial paraphrasing or semantic divergence.

---

## 2. Master Component Dependency Cone Register

The deterministic static scan of the active codebase cataloged all local modules, server factories, REST routers, data models, graph persistence engines, traversal engines, entity linkers, frontend visualizer components, synchronization context providers, styling registries, and automated test suites whose interfaces touch specced functionality in `functional_specification_016.md`:

| Repository-Relative Path | Verbatim Symbols & Interfaces | Role in Architecture | Grounding Justification (`functional_specification_016.md`) |
| :--- | :--- | :--- | :--- |
| `LANGUAGE.md` | `{errors}`, `{correctness}`, `{functionality}`, `{correct required outputs}`, `{sufficient}`, `{insufficient}`, `{Policy Keyword}`, `{Target_Bill_IDs}`, `{Enacted_Law_ID}`, `{US_Code_Citations}`, `{Operational_Filters}`, `{Clinical_Citations}`, `{HCPCS / CPT Codes}` | System-wide evaluation parameters and domain taxonomy glossary. | Section 1 mandates strict adherence of all evaluations and diagnostics to `LANGUAGE.md`. |
| `src/api/server.py` | `lifespan`, `create_app`, `app`, `http_exception_handler`, `graphrag_exception_handler` | FastAPI server factory, Neo4j connection lifecycle manager, CORS middleware configuration (`allow_origins`), standardized error envelopes, and entrypoint runner. | Governs Section 4 (Backend Runtime Layer), Section 4.1 (CORS configuration allowing GitHub Pages domain), and port/environment configuration for Hugging Face Spaces. |
| `src/api/routes.py` | `router`, `set_sync_engine`, `get_sync_engine`, `get_pipeline`, `get_neo4j_session`, `health_check`, `get_graph_summary`, `derive_node_display_name`, `resolve_label_from_pk_and_labels`, `get_graph_topology`, `resolve_entities`, `get_subgraph_by_anchors`, `execute_graphrag_query`, `VALID_STATE_CODES`, `VALID_JURISDICTION_CODES` | FastAPI REST router exposing graph topology, entity resolution, subgraph extraction, and conversational synthesis endpoints. | Governs Section 4.1 (Engine API & Endpoints: Health & Readiness, Graph Topology, Entity Inspection, Live Query). |
| `src/api/models.py` | `HealthResponse`, `TopologyNode`, `TopologyEdge`, `TopologyResponse`, `EntityResolveRequest`, `EntityResolveResponse`, `SubgraphRequest`, `SubgraphResponse`, `ErrorEnvelope` | Pydantic request/response schema models for backend API endpoints. | Defines data contracts for health response, topology nodes/edges, and query responses (Section 4.1). |
| `src/api/__init__.py` | `app`, `create_app` | API package initialization and export boundary. | Core boundary for backend service execution. |
| `src/graph/neo4j_sync.py` | `Neo4jSyncEngine`, `get_driver`, `close`, `init_schema`, `sync_graph_dict`, `sync_file`, `get_summary_statistics`, `DEFAULT_NEO4J_URI`, `DEFAULT_NEO4J_USER`, `DEFAULT_NEO4J_PASSWORD`, `DEFAULT_NEO4J_DATABASE` | Neo4j property graph synchronization engine managing driver pool, APOC batch merges, schema constraints, and summary metrics. | Governs backend data access layer connecting to persistent Neo4j backing store (Section 4 & Section 1). |
| `src/graph/models.py` | `EdgeProvenance`, `GraphEdge`, `BaseNode`, `PolicyNode`, `BillNode`, `PublicLawNode`, `StatutorySectionNode`, `USCSectionNode`, `RegulationNode`, `CFRSectionNode`, `ChangeRequestNode`, `TransmittalNode`, `CoveragePolicyNode`, `JurisdictionNode`, `StateNode`, `FeeScheduleEntryNode`, `FeeScheduleRateNode`, `HCPCSCodeNode`, `ProcedureCodeNode`, `ICD10CodeNode`, `DiagnosisCodeNode`, `LobbyingFilingNode`, `CBOScoreNode`, `LiteratureStudyNode`, `PolicyTraversalError` | Canonical domain graph entity models across all 17 8-hop entity categories and provenance schemas. | Governs 8-hop knowledge graph structure listed in Section 3.1 (`POLICY-...`, `BILL-...`, `PLAW-...`, `STAT-...`, `USC-...`, `REG-FR-...`, `CFR-...`, `TR-CR...`, `DME-MAC-...`, `HCPCS-...`, `FEE-...`, `JURIS-DME-...`, `STATE-...`, `LDA-...`, `CBO-...`, `PUBMED-...`). |
| `src/graph/engine.py` | `DirectedPropertyGraph`, `PropertyGraphEngine`, `GraphValidationError`, `run_pipeline`, `validate_invariants` | In-memory property graph assembly, idempotent ingestion, and topological invariant validation engine. | Governs graph structure and extraction pipeline execution (Section 4.1 Live Query / Pipeline Execution). |
| `src/graphrag/entity_linker.py` | `EntityAnchorLinker`, `STATE_NAME_TO_CODE`, `CLINICAL_SYNONYMS`, `POLICY_TRIGGERS`, `HCPCS_REGEX`, `GEO_LOCATION_INDICATORS`, `PK_TOKEN_REGEX`, `resolve_anchors`, `resolve_explicit_anchor` | Multi-slot entity anchor linker resolving natural language queries and explicit primary keys against Neo4j. | Governs Section 3.2 (Dynamic Search & Query Interface) and Section 4.1 (Live Query Endpoint). |
| `src/graphrag/traversal.py` | `TopologicalTraversalEngine`, `extract_connecting_subgraph` | Neo4j Cypher topological traversal engine expanding multi-hop relationship chains between anchors. | Governs real-time graph traversal and subgraph extraction (Section 3.2 & Section 4.1). |
| `src/graphrag/context_assembler.py` | `GraphContextAssembler`, `assemble_context` | Assembles structured factual Markdown contexts from traversed node and edge attributes. | Governs text context assembly for entity inspection and synthesis (Section 3.1 & Section 4.1). |
| `src/graphrag/synthesizer.py` | `HuggingFaceSynthesizer`, `synthesize`, `_call_hf_inference_api` | Calls Hugging Face Serverless Inference API with assembled context. | Governs natural language synthesis in backend runtime layer (Section 4.1). |
| `src/graphrag/pipeline.py` | `GraphRAGPipeline`, `execute_query` | Orchestrates end-to-end GraphRAG pipeline from query to anchor resolution, traversal, assembly, and synthesis. | Governs Live Query execution (Section 4.1). |
| `src/graphrag/models.py` | `AnchorEntity`, `ResolvedAnchors`, `TraversalNode`, `TraversalEdge`, `TraversalResult`, `GraphRAGQueryRequest`, `GraphRAGQueryResponse` | Pydantic schemas for anchors, traversals, and query responses. | Defines internal and API data contracts for GraphRAG operations. |
| `src/graphrag/exceptions.py` | `GraphRAGException`, `EntityResolutionError`, `TraversalError`, `ModelInferenceError`, `ModelAuthenticationError`, `ModelRateLimitError`, `GraphValidationError` | Strict fail-fast exception hierarchy enforcing `INV-FAIL-FAST`. | Governs Section 3.3 (Fail-Fast & Telemetry Display) and HTTP error envelope generation. |
| `src/graphrag/__init__.py` | GraphRAG package exports | Root exports for GraphRAG pipeline, models, and exceptions. | Package export boundary. |
| `src/frontend/package.json` | Dependencies and npm scripts (`build`, `dev`, `lint`, `preview`) | Frontend manifest (`react@^19.2.8`, `d3@^7.9.0`, `lucide-react@^1.55.0`, `vite@^8.3.0`, `typescript@~6.0.2`). | Governs Section 2.1 (static web deployment) and Section 3 (Frontend Presentation Layer). |
| `src/frontend/vite.config.ts` | Vite dev server and proxy configuration | Bundler configuration defining dev server proxy and build plugins. | Governs static build output and base URL configuration for GitHub Pages deployment (Section 2.1 & 5.1). |
| `src/frontend/src/App.tsx` | `MainVisualizer`, `App`, `fetchTopology`, `RawTopologyNode`, `RawTopologyEdge`, `RawTopologyResponse` | Top-level React component fetching topology, managing canvas rendering, and error banner display. | Governs Section 3.1 (Interactive Engine Graph Canvas) and Section 3.3 (Fail-Fast & Telemetry Display). |
| `src/frontend/src/main.tsx` | `createRoot`, `StrictMode`, `App` | React 19 application entrypoint. | Application mounting entrypoint. |
| `src/frontend/src/index.css` | Global styling (`#root`, `body`, `html`) | Full-viewport styles. | Viewport container dimensions. |
| `src/frontend/src/App.css` | Component styles | CSS styling asset. | Frontend asset. |
| `src/frontend/src/components/GraphCanvas.tsx` | `GraphCanvasProps`, `GraphCanvas` | Force-directed HTML5 canvas visualizer executing D3 simulation, active path illumination, and zoom/pan camera framing. | Governs Section 3.1 Node & Edge Interaction (pan, zoom, click, select, drag, filter). |
| `src/frontend/src/components/FilterToolbar.tsx` | `FilterToolbarProps`, `FilterToolbar` | Top navigation toolbar containing jurisdiction, state (all 54 US jurisdictions), and policy dropdown selectors and reset controls. | Governs Section 3.2 (Dynamic Search & Query Interface) and state filtering (Section 5.1). |
| `src/frontend/src/components/NodeDetailDrawer.tsx` | `NodeDetailDrawerProps`, `NodeDetailDrawer` | Slide-over inspection drawer rendering full persisted property tables, provenance metadata (`source_uri`, `selector`, `run_id`, `ingestion_timestamp`), connected neighbors, and external government links. | Governs Section 3.1 (Detailed Entity Inspection Panel) and Section 5.1. |
| `src/frontend/src/components/AgentChatDrawer.tsx` | `AgentChatDrawer`, `ChatMessage` | Conversational GraphRAG drawer displaying quick prompts, synthesized answers, execution status indicators, and illumination badges. | Governs Section 3.2 (Dynamic Search & Query Interface: visual indicators of execution status). |
| `src/frontend/src/context/GraphSyncContext.tsx` | `ChatMessage`, `StateOption`, `JurisdictionMetadata`, `DME_JURISDICTIONS`, `STATE_TO_JURISDICTION`, `ALL_STATES_SORTED`, `GraphSyncContextType`, `GraphSyncProvider`, `useGraphSync` | React Context synchronization bus managing active nodes/edges, selection, filter state, and API inquiries. | Governs state and jurisdiction filtering across all 54 jurisdictions and canvas-agent synchronization. |
| `src/frontend/src/styles/graph_theme.ts` | `NodeVisualConfig`, `NODE_THEME_REGISTRY`, `CANVAS_PALETTE`, `getNodeVisual` | Authoritative visual theme registry defining colors, radii, and shapes for all 17 entity categories. | Governs visual graph representation across Section 3.1. |
| `src/frontend/src/types/graph.ts` | `NodeProperties`, `EdgeProvenance`, `GraphNode`, `GraphLink`, `AnchorEntity`, `GraphRAGQueryResponse`, `GraphSummary` | TypeScript interfaces for graph topology nodes, directed links, provenance metadata, and query responses. | Defines the visualizer data model across Section 3 and Section 4. |
| `src/frontend/src/utils/promptGenerator.ts` | `constructInquiryPrompt` | Generates deterministic inquiry prompts for node inspection inquiries. | Governs drawer inquiry actions (Section 3.1). |
| `tests/test_api_endpoints.py` | FastAPI REST integration test suite | Verifies `/api/health`, `/api/graph/summary`, `/api/graph/topology`, `/api/entities/resolve`, `/api/graphrag/subgraph`, and `/api/graphrag/query`. | Validates Section 4.1 backend endpoints. |
| `tests/test_graphrag_pipeline.py` | GraphRAG pipeline and oracle verification test suite | Tests all retrieval and synthesis oracles and latency benchmarks. | Validates Section 4.1 live query pipeline. |
| `tests/test_graph_pipeline.py` | Graph construction and invariant verification test suite | Verifies 8 hops, typed handoffs, omnibus topology, 54 jurisdictions, and fail-fast errors. | Validates 8-hop knowledge graph integrity. |
| `verify_all.py` | `main` | CLI verification test harness orchestrating unit and integration suites. | Validates Section 5.1 end-to-end verification. |
| `docs/research_api_keys_and_auth.md` | Research report on API keys, auth parameters, and third-party secrets | Documents secret management, unauthenticated endpoints, and token requirements. | Governs Section 4.1 Configuration Integrity (Hugging Face Space Secrets). |

---

## 3. Candidate External Datasource & Schema Audit Register

In strict adherence to `INV-SCAN-01`, active read-only reconnaissance was conducted against live external datasources, public government endpoints, GitHub API, Hugging Face Hub/Spaces API, the live Neo4j graph database, and local FastAPI services. All queries were non-mutating (safe GET requests). Raw, unedited empirical payloads were captured directly into `assets/20261014T044849-392-31ky/`.

### 3.1. GitHub API & GitHub Pages Infrastructure
- **Role in Specification:** Frontend Presentation Layer hosting target (`https://<username>.github.io/<repo-name>/`) and source isolation repository (Section 2.1 & 5.1).
- **Probed Endpoints & Authentication Context:**
  - `GET https://api.github.com/user`: Authenticated via GitHub CLI (`gh`) keyring with scopes `repo`, `workflow`, `read:org`, `gist`.
  - `GET https://api.github.com/repos/LuisP1028/LAG`: Existing development repository metadata.
  - `GET https://api.github.com/repos/LuisP1028/LAG/pages`: Probes GitHub Pages deployment status on current repository.
- **Audited Empirical Schemas & Findings:**
  - Authenticated user: `LuisP1028` (ID `185441252`, user type `User`).
  - Current repository: `LuisP1028/LAG` (`visibility`: `public`, `default_branch`: `main`, `has_pages`: `false`).
  - GitHub Pages status: Returns HTTP 404 (`gh: Not Found (HTTP 404)`), confirming GitHub Pages is currently not activated on the root repository.
- **Saved Ground-Truth Assets:**
  - `assets/20261014T044849-392-31ky/external_github_user.json`
  - `assets/20261014T044849-392-31ky/external_github_repo_lag.json`
  - `assets/20261014T044849-392-31ky/external_github_pages_status.json`

### 3.2. Hugging Face Spaces & Hub API
- **Role in Specification:** Persistent Backend Engine Runtime Layer hosting target (Section 4 & 5.1).
- **Probed Endpoints & Authentication Context:**
  - `GET https://huggingface.co/api/whoami-v2`: Authenticated via `HF_TOKEN` fine-grained access token.
  - `GET https://huggingface.co/api/spaces?author=ChoppedCheese`: Probes all existing spaces under the authenticated account.
  - `GET https://huggingface.co/api/spaces/ChoppedCheese/dither-os-bartending`: Probes exact runtime configuration schema of an active Docker SDK Space on Hugging Face.
- **Audited Empirical Schemas & Findings:**
  - Authenticated user: `ChoppedCheese` (Account ID `662eff76b10f82aa4fb0d8ce`, account type `user`, role `fine_grained`).
  - Scoped permissions: `repo.write`, `repo.content.read`, `inference.serverless.write`, `inference.endpoints.infer.write`, `job.write`.
  - Hugging Face Spaces Docker SDK Architecture:
    - Host URL format: `https://<subdomain>.hf.space` (e.g. `https://choppedcheese-dither-os-bartending.hf.space`).
    - Standard listening port: `7860` (`app_port: 7860` configured in `README.md` YAML frontmatter cardData).
    - Secret injection: Variables and secrets are managed via Hugging Face Space Settings, accessible in the container environment via standard `os.environ`.
- **Saved Ground-Truth Assets:**
  - `assets/20261014T044849-392-31ky/external_hf_whoami.json`
  - `assets/20261014T044849-392-31ky/external_hf_spaces_list.json`
  - `assets/20261014T044849-392-31ky/external_hf_space_detail.json`

### 3.3. Live Neo4j Graph Database (`bolt://localhost:7687`, database `neo4j`)
- **Role in Specification:** Persistent graph backing store hosting the 8-hop knowledge graph structure (Section 1 & 3.1).
- **Connection Parameters:** `bolt://localhost:7687`, user `neo4j`, password `qwertyui`, database `neo4j`. Verified live and connected.
- **Audited Empirical Schema & Statistics:**
  - **Total Nodes:** `3,875`
  - **Total Edges:** `7,593`
  - **Observed Node Labels & Counts:**
    - `PolicyNode, FeeScheduleRate`: `3,710`
    - `PolicyNode, ProcedureCode`: `77`
    - `PolicyNode, State`: `54`
    - `PolicyNode, CFRSection`: `7`
    - `PolicyNode, USCSection`: `4`
    - `PolicyNode, Jurisdiction`: `4`
    - `PolicyNode, DiagnosisCode`: `4`
    - `PolicyNode, LiteratureStudy`: `4`
    - `PolicyNode, Bill`: `2`
    - `PolicyNode, StatutorySection`: `2`
    - `PolicyNode, LobbyingFiling`: `2`
    - `PolicyNode, Policy`: `1`
    - `PolicyNode, PublicLaw`: `1`
    - `PolicyNode, Regulation`: `1`
    - `PolicyNode, Transmittal`: `1`
    - `PolicyNode, CoveragePolicy`: `1`
    - `PolicyNode, CBOScore`: `1`
  - **Observed Relationship Types & Counts:**
    - `HAS_RATE`: `3,710`
    - `APPLIES_TO_STATE`: `3,710`
    - `COVERS_STATE`: `54`
    - `APPLIES_TO_JURISDICTION`: `8`
    - `CODIFIED_IN`: `7`
    - `AMENDS`: `4`
    - `IMPLEMENTED_BY`: `4`
    - `HAS_ADVOCACY_RECORD`: `4`
    - `SUPPORTED_BY_EVIDENCE`: `4`
    - `INCORPORATED_INTO`: `1`
    - `ENACTED_AS`: `1`
    - `CONTAINS`: `1`
    - `AUTHORIZED_BY`: `1`
    - `MANDATES_POLICY`: `1`
    - `REQUIRES_DIAGNOSIS`: `1`
    - `COVERS_PROCEDURE`: `1`
    - `HAS_BUDGET_IMPACT`: `1`
    - `DISCOVERED_BILL`: `1`
- **Saved Ground-Truth Assets:**
  - `assets/20261014T044849-392-31ky/neo4j_summary_statistics.json`
  - `assets/20261014T044849-392-31ky/neo4j_node_labels_and_counts.json`
  - `assets/20261014T044849-392-31ky/neo4j_relationship_types_and_counts.json`
  - `assets/20261014T044849-392-31ky/neo4j_sample_nodes_17_types.json`

### 3.4. Backend Engine API Endpoints (`src.api.server:app`)
- **Role in Specification:** Service endpoints serving graph topology, health, entity resolution, and live GraphRAG execution (Section 4.1).
- **Audited Empirical Schemas:**
  - `GET /api/health`: Returns `{"status": "ok", "neo4j_connected": true, "timestamp": "..."}`.
  - `GET /api/graph/summary`: Returns `{"total_nodes": 3875, "total_edges": 7593, "nodes_by_label": [...], "edges_by_type": [...]}`.
  - `GET /api/graph/topology`: Returns `TopologyResponse` (`nodes`: `List[TopologyNode]`, `edges`: `List[TopologyEdge]`, `total_nodes`: `int`, `total_edges`: `int`).
    - Baseline (unexpanded): `165` nodes, `173` edges.
    - State-filtered Guam (`state_filter=GU`): `165` nodes, `173` edges (verifies 54th US jurisdiction support).
    - State-filtered California (`state_filter=CA`): `235` nodes, `313` edges (70 CA fee schedule rates expanded).
    - State-filtered New York (`state_filter=NY`): `235` nodes, `313` edges (70 NY fee schedule rates expanded).
  - `POST /api/entities/resolve`: Returns `{"anchors": [{"slot": "state", "primary_key": "STATE-WI", "matched_text": "Wisconsin", "entity_type": "State", "label": "State"}, ...]}`.
  - `POST /api/graphrag/subgraph`: Returns `SubgraphResponse` (`nodes`, `edges`, `active_node_pks`, `active_edge_keys`, `retrieval_ms`).
  - `POST /api/graphrag/query`: Returns `GraphRAGQueryResponse` (`answer`: string, `active_node_pks`: `32` illuminated node PKs, `active_edge_keys`: `32` illuminated edge keys, `duration_ms`: float).
- **Saved Ground-Truth Assets:**
  - `assets/20261014T044849-392-31ky/api_health.json`
  - `assets/20261014T044849-392-31ky/api_graph_summary.json`
  - `assets/20261014T044849-392-31ky/api_graph_topology_baseline.json`
  - `assets/20261014T044849-392-31ky/api_graph_topology_gu.json`
  - `assets/20261014T044849-392-31ky/api_graph_topology_ca.json`
  - `assets/20261014T044849-392-31ky/api_graph_topology_ny.json`
  - `assets/20261014T044849-392-31ky/api_entities_resolve.json`
  - `assets/20261014T044849-392-31ky/api_graphrag_subgraph.json`
  - `assets/20261014T044849-392-31ky/api_graphrag_query_response.json`

### 3.5. Upstream Government & Academic Public Datasources
- **Role in Specification:** Upstream statutory, regulatory, and clinical evidence cited in the 8-hop graph (Section 3.1 & 5.1).
- **Audited Endpoints & Responses:**
  - **Federal Register API** (`https://www.federalregister.gov/api/v1/documents/2023-24455.json`): HTTP 200 OK. Returns complete document metadata, citation `88 FR 77676`, publication date `2023-11-15`, effective date `2024-01-01`, and CFR references.
  - **NCBI PubMed E-Utilities** (`https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id=25574334&retmode=json`): HTTP 200 OK. Returns article metadata for PMID `25574334` ("A randomized controlled trial of a compression garment for the prevention of breast cancer-related lymphedema").
  - **GPO GovInfo Public Law Details** (`https://www.govinfo.gov/app/details/PLAW-117publ328`): HTTP 200 OK.
  - **Congress.gov Bill Details** (`https://www.congress.gov/bill/117th-congress/house-bill/3630`): HTTP 403 Forbidden (Cloudflare bot defense blocks automated scraper user-agents; requires browser headers or official `api.congress.gov`).
  - **CMS MCD Coverage Article** (`https://www.cms.gov/medicare-coverage-database/view/article.aspx?articleid=59508`): HTTP 200 OK.
  - **CMS Transmittals Index** (`https://www.cms.gov/medicare/transmittals`): HTTP 404 (moved/redirected URL).
  - **CGS Medicare DME Article** (`https://www.cgsmedicare.com/jb/coverage/mr/action_correct_coding_lymphedema.html`): HTTP 404 (article archived/relocated).
  - **Senate LDA Filing Portal** (`https://lda.senate.gov/`): HTTP 403 Forbidden (requires browser user-agent headers).
- **Saved Ground-Truth Assets:**
  - `assets/20261014T044849-392-31ky/external_federal_register_rule_2023_24455.json`
  - `assets/20261014T044849-392-31ky/external_pubmed_summary_25574334.json`
  - `assets/20261014T044849-392-31ky/external_govinfo_plaw_117publ328_headers.txt`
  - `assets/20261014T044849-392-31ky/external_congress_gov_bill_hr3630_headers.txt`
  - `assets/20261014T044849-392-31ky/external_cms_mcd_search_results_a59508_headers.txt`
  - `assets/20261014T044849-392-31ky/external_cms_transmittals_headers.txt`
  - `assets/20261014T044849-392-31ky/external_cgs_dme_headers.txt`
  - `assets/20261014T044849-392-31ky/external_senate_lda_headers.txt`

---

## 4. Explicit Deficiency Register

In strict adherence to `INV-ABSENCE-01`, every specced requirement in `functional_specification_016.md` that cannot be satisfied by existing codebase components or reachable endpoints has been cataloged without inventing components, classes, or endpoints:

### DEF-001: Missing Dedicated Standalone GitHub Repository for Showcase
- **Governing Specification Requirement:** Section 2.1 mandates: *"The project showcase must reside in its own clean, dedicated GitHub repository separate from the local root development repository. The repository must maintain its own independent Git version history, remote tracking, and configuration. The repository root must be structured for static web deployment."*
- **Empirical Codebase Finding:** `src/frontend` currently exists as an un-isolated subfolder in the monolithic development repository (`LuisP1028/LAG`). No standalone GitHub repository has been created or linked as a separate remote. Furthermore, `external_github_pages_status.json` verifies that GitHub Pages is not configured (`HTTP 404 Not Found`).
- **Failure Mode / Architectural Deficiency:** Direct deployment from the local development root would leak un-masked development files, local credentials, and build scripts, violating Section 2.1 isolation invariants.
- **Architectural Remediation Requirement:** Downstream implementation must construct an isolated export/bundle repository for the frontend with independent Git remote tracking and GitHub Pages publication workflow.

### DEF-002: Missing Dedicated Entity Inspection REST Endpoint
- **Governing Specification Requirement:** Section 4.1 mandates: *"Entity Inspection Endpoint: Returns deep contextual provenance and text excerpts for a specified entity primary key."*
- **Empirical Codebase Finding:** In `src/api/routes.py`, the exposed endpoints are `/api/health`, `/api/graph/summary`, `/api/graph/topology`, `/api/entities/resolve`, `/api/graphrag/subgraph`, and `/api/graphrag/query`. There is no dedicated entity inspection endpoint (e.g., `GET /api/entities/{primary_key}` or `GET /api/entities/inspect`).
- **Failure Mode / Architectural Deficiency:** Frontend cannot query backend directly for deep provenance and text excerpts of a specific entity node if full node attributes are not bundled or pre-fetched.
- **Architectural Remediation Requirement:** Downstream implementation must add a dedicated entity inspection route to `src/api/routes.py` and declare its request/response schemas in `src/api/models.py`.

### DEF-003: Incomplete Health & Readiness Response Schema
- **Governing Specification Requirement:** Section 4.1 mandates: *"Health & Readiness Endpoint: Returns a 200 OK response with runtime health, loaded policy domains, and service uptime."*
- **Empirical Codebase Finding:** As captured in `assets/20261014T044849-392-31ky/api_health.json` and defined in `src/api/models.py`, `HealthResponse` only returns `{"status": "ok", "neo4j_connected": true, "timestamp": "..."}`. It lacks fields for `loaded_policy_domains` (e.g. `["LTA"]`) and `service_uptime` (uptime in seconds).
- **Failure Mode / Architectural Deficiency:** Health check does not expose operational readiness details, policy domains, or uptime to telemetry monitoring systems or frontend cold-start detectors.
- **Architectural Remediation Requirement:** `src/api/models.py` and `health_check` in `src/api/routes.py` must be augmented to include `loaded_policy_domains: List[str]` and `service_uptime: float`.

### DEF-004: Hardcoded Relative API Paths in Frontend Client
- **Governing Specification Requirement:** Section 1 & Section 5.1 mandate that the frontend deployed on GitHub Pages (`https://<username>.github.io/<repo-name>/`) communicates over HTTPS with the backend deployed on Hugging Face Spaces (`https://<username>-<space-name>.hf.space`).
- **Empirical Codebase Finding:** In `src/frontend/src/App.tsx` (L52: `fetch('/api/graph/topology?...')`) and `src/frontend/src/context/GraphSyncContext.tsx` (L401: `fetch('/api/graphrag/query', ...)`), endpoints are hardcoded to relative path `/api/...`.
- **Failure Mode / Architectural Deficiency:** When served statically from GitHub Pages, relative requests resolve to `https://<username>.github.io/api/...`, resulting in immediate HTTP 404 failures.
- **Architectural Remediation Requirement:** Frontend must support dynamic configuration of the backend API origin (e.g., `import.meta.env.VITE_API_BASE_URL` with runtime fallback or Space domain selector).

### DEF-005: Missing Bundled Pre-computed Policy Run Artifacts for Offline / Zero-Latency Demonstration
- **Governing Specification Requirement:** Section 3.1 & 3.2 mandate: *"Inputs: Graph topology payloads retrieved dynamically from the backend service or bundled sample run artifacts... Provide a responsive control panel enabling users to: 1. Select pre-computed policy runs for immediate zero-latency demonstration."*
- **Empirical Codebase Finding:** `src/frontend` only fetches topology dynamically from `/api/graph/topology` on mount. If the backend is cold-starting or unavailable, `App.tsx` displays an error banner with an empty canvas. No pre-computed policy run payloads are bundled into `src/frontend/src/assets/` or selectable in `FilterToolbar.tsx`.
- **Failure Mode / Architectural Deficiency:** Visitors encountering a sleeping or cold-starting Hugging Face Space receive a blank screen or connection error instead of immediate zero-latency exploration of the sample policy run.
- **Architectural Remediation Requirement:** Pre-computed topology payloads (e.g., LTA baseline, state-filtered subgraphs) must be bundled as static assets in the frontend build and wired to a demonstration mode selector in `FilterToolbar.tsx` and `App.tsx`.

### DEF-006: Missing Backend Cold-Start / Spinning-Up Status Feedback
- **Governing Specification Requirement:** Section 3.3 mandates: *"If the backend service is unreachable, spinning up, or returns an error status code, the frontend must surface an explicit, human-readable status alert explaining the exact state (e.g., 'Backend runtime cold starting / connecting to Hugging Face Space'). Silent failures, empty canvases with zero diagnostic feedback, and unhandled promise rejections are strictly prohibited."*
- **Empirical Codebase Finding:** `App.tsx` catches fetch errors with a generic `catch (err: unknown)` block that displays a static red box with `Retry`. It has no polling mechanism, no health-check probe, and no cold-start telemetry message explaining that Hugging Face Spaces require 30–60 seconds to spin up from sleep.
- **Failure Mode / Architectural Deficiency:** First-time visitors assume the application is broken rather than waiting for backend container boot.
- **Architectural Remediation Requirement:** Frontend must implement an automated health-check polling loop with descriptive cold-start telemetry ("Connecting to Hugging Face Space runtime... warming up backend").

### DEF-007: Missing Hugging Face Space Dockerfile & Configuration
- **Governing Specification Requirement:** Section 4 mandates: persistent backend service deployed to Hugging Face Spaces hosting the engine API. Section 4.1 mandates: third-party secrets injected via Space Secrets, CORS allowing GitHub Pages domain.
- **Empirical Codebase Finding:** The repository contains no `Dockerfile` tailored for Hugging Face Spaces (`app_port: 7860`), no `README.md` with Space metadata YAML frontmatter, and `src/api/server.py` defaults to port `8000` rather than the Hugging Face Space standard port `7860`.
- **Failure Mode / Architectural Deficiency:** Repository cannot be directly pushed to a Hugging Face Docker Space without a valid Dockerfile exposing port 7860 and initializing server dependencies.
- **Architectural Remediation Requirement:** Downstream implementation must create a production `Dockerfile` for Hugging Face Spaces (exposing port 7860) and Space metadata card.

### DEF-008: Vite Base Path Not Configured for GitHub Pages Subpath
- **Governing Specification Requirement:** Section 5.1 Success Criterion 1 mandates: *"The web application is publicly reachable at `https://<username>.github.io/<repo-name>/` over HTTPS without authentication."*
- **Empirical Codebase Finding:** In `src/frontend/vite.config.ts`, no `base` path property is set. Vite defaults to `base: '/'`.
- **Failure Mode / Architectural Deficiency:** When deployed to GitHub Pages at `https://<username>.github.io/<repo-name>/`, all generated JavaScript, CSS, and asset tags resolve to the root domain (`https://<username>.github.io/assets/...`) and fail with HTTP 404, resulting in a blank page.
- **Architectural Remediation Requirement:** `vite.config.ts` must configure `base: './'` or dynamic `process.env.VITE_BASE_PATH` to ensure relative asset loading across any repository name.

---

## 5. Sufficiency & Scan Certification

- **Dependency Cone Exhaustiveness:** The scan evaluated all active modules in `src/api/`, `src/graph/`, `src/graphrag/`, `src/frontend/`, and `tests/`. Exactly 35 local component files touching specced functionality have been verified and cataloged.
- **Empirical Grounding:** All external endpoints (GitHub API, Hugging Face Hub/Spaces, Neo4j, Federal Register, PubMed, GPO GovInfo, CMS MCD) were probed via non-mutating requests, and 27 unedited ground-truth payloads/headers were captured in `assets/20261014T044849-392-31ky/`.
- **Sufficiency Condition:** The evaluation is `{sufficient}`. All interfaces, schemas, and missing capabilities are documented with empirical evidence and verbatim identifiers. Zero ambiguity remains.

---

## 6. Handoff Manifest Affirmation

The dedicated role handoff manifest at `handoff/20261014T044849-392-31ky/plan-scan-2.txt` has been atomically overwritten. It records exclusively repository-relative filepaths (exactly one per line) for all 35 qualified codebase component files, this authored scan report, and all 27 saved ground-truth payload files in `assets/20261014T044849-392-31ky/`. No seed paths or predecessor manifests were modified.

---

## 7. Coding Gate Affirmation

> [!IMPORTANT]
> **DO NOT CODE YET: Implementation coding gate remains locked.** Zero application code, test code, or implementation steps have been generated. Coding waits on an empty frontier and explicit operator authorization.
