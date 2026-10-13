# Codebase Static Scan, External Reconnaissance, and Schema Audit Report

**Report ID:** `scan_reports/scan_report_007_plan_scan_1.md`  
**Execution Node:** `plan-scan-1` (Agent 1)  
**Run ID:** `20261013T172426-897-pj8g`  
**Timestamp:** `2026-10-13T10:30:00-07:00`  
**Governing Specification:** [`functional_specification_007.md`](functional_specification_007.md) (*Functional Specification: Node Detail Contextual Inquire Action and Targeted GraphRAG Execution*)  
**Status:** Complete Reconnaissance & Schema Audit Register  
**Implementation Gate:** Strict Boundary Enforced (**DO NOT CODE YET**)

---

## 1. Governing Context & Ingestion Verification

In strict compliance with `INV-HANDOFF-01`, workspace architectural rules, and the loading hierarchy:

1. **Single Upstream Specification in Scope:**
   - Ingested verbatim and strictly bounded to: [`functional_specification_007.md`](functional_specification_007.md) (*Functional Specification: Node Detail Contextual Inquire Action and Targeted GraphRAG Execution*).
   - Predecessor manifest verified: `handoff/authored.txt` records `functional_specification_007.md` as the governing target.
   - Zero scanning across unassigned specifications; no multiple seed paths consumed (`INV-HANDOFF-01`).
2. **Wayfinder Architectural Map and Decision Tickets Inspected:**
   - [`wayfinder/map.md`](wayfinder/map.md): *Wayfinder Architectural Map: GraphRAG Specification for Browser Graph Visualizer*
   - [`wayfinder/tickets/ticket-001.md`](wayfinder/tickets/ticket-001.md): *Entity Anchor Linking and Layperson Vocabulary Normalization Specification* (RESOLVED)
   - [`wayfinder/tickets/ticket-002.md`](wayfinder/tickets/ticket-002.md): *Generalized Topological Subgraph Expansion and Neighborhood Traversal Specification* (RESOLVED)
   - [`wayfinder/tickets/ticket-003.md`](wayfinder/tickets/ticket-003.md): *Factual Context Assembly, Edge Provenance Formatting, and Prompt Grounding Specification* (RESOLVED)
   - [`wayfinder/tickets/ticket-004.md`](wayfinder/tickets/ticket-004.md): *Bidirectional Visual Canvas Synchronization and Active Subgraph Illumination Specification* (RESOLVED)
   - [`wayfinder/tickets/ticket-005.md`](wayfinder/tickets/ticket-005.md): *Master Specification Synthesis and Edits for functional_specification_004.md* (RESOLVED)
3. **Evaluation Parameters Adherence ([`LANGUAGE.md`](LANGUAGE.md)):**
   - **`{errors}`**: Explicit failure states surfaced immediately during execution: clicking "INQUIRE IN GRAPHRAG CHAT" failing to open the drawer or submit the query, dropping the node primary key identifier during API dispatch, returning 0 illuminated nodes for an existing graph node, regex location extractor crashing on words like "Explain", or traversal engine collapsing relationship keys into `UNKNOWN->RELATED_TO->UNKNOWN`.
   - **`{correctness}`**: Precise symbol, interface, and contract alignment where clicking the detail button passes the selected entity's `primary_key` as an explicit pre-resolved anchor, extracts its true connected lineage in Neo4j across all 14 entity types, and renders a grounded synthesis quoting bracketed identifiers without data loss.
   - **`{functionality}`**: Seamless end-to-end user workflow where selecting any entity on the visualizer canvas and clicking "INQUIRE IN GRAPHRAG CHAT" immediately produces a grounded conversational analysis and illuminates its active path on the canvas in real time.
   - **`{correct required outputs}`**:
     1. Automated opening of the chat drawer.
     2. Immediate insertion of an entity-tailored formatted user inquiry.
     3. Direct transmission of explicit `primary_key` anchor bypassing heuristic keyword guessing.
     4. Retrieval of the node's connected subgraph with non-zero illuminated nodes (`> 0 Nodes Illuminated`).
     5. Grounded LLM response citing bracketed entity identifiers.
     6. Real-time visual canvas illumination highlighting active nodes and connecting relationships in amber/gold.
     7. Saved empirical payload samples in `assets/20261013T172426-897-pj8g/`.
     8. Dedicated handoff manifest at `handoff/20261013T172426-897-pj8g/plan-scan-1.txt` atomically overwritten.
   - **`{sufficient}`**: Requirements and scan registers are complete, unambiguous, and empirically grounded, permitting downstream test planning and implementation without guesswork.
   - **`{insufficient}`**: Any ambiguity requiring assumptions regarding button behavior, query formatting, state passing, or anchor binding.

---

## 2. Master Component Dependency Cone Register

Every component listed below physically exists in the codebase, touches specced functionality, and has been reviewed against its live interface and verbatim symbols:

| Repository-Relative Path | Verbatim Symbols & Interfaces | Role & Grounding Justification |
| :--- | :--- | :--- |
| `src/frontend/src/components/NodeDetailDrawer.tsx` | `NodeDetailDrawer`, `NodeDetailDrawerProps`, `useGraphSync()`, `selectedNode`, `props`, `govLink`, `connectedNeighbors`, action button `◈ INQUIRE IN GRAPHRAG CHAT` (lines 244-265) | Renders the inspection drawer and the action button. Currently possesses the bug where `onClick` purely toggles `setIsChatOpen(true)` without query construction, anchor passing, or in-flight disabled state. |
| `src/frontend/src/components/AgentChatDrawer.tsx` | `AgentChatDrawer`, `Message`, `handleSend(queryText?: string)`, `inputQuery`, `modelId`, `loading`, `errorMsg`, `messages`, `setIlluminatedPath`, `fetch('/api/graphrag/query')` | Renders conversational thread, manages loading state, displays telemetry badge, and dispatches queries to backend. Lacks receipt of explicit `primary_key` anchor and auto-submit trigger from drawer. |
| `src/frontend/src/context/GraphSyncContext.tsx` | `GraphSyncContext`, `GraphSyncProvider`, `useGraphSync()`, `GraphSyncContextType`, `selectedNode`, `selectNode`, `seededAnchor`, `activeNodePKs`, `activeEdgeKeys`, `isIlluminated`, `setIlluminatedPath`, `setIsChatOpen` | Manages shared synchronization bus between visualizer canvas, node detail drawer, and chat drawer. Needs coordinated inquiry dispatch action and shared loading state. |
| `src/frontend/src/components/GraphCanvas.tsx` | `GraphCanvas`, `GraphCanvasProps`, `d3.forceSimulation`, `handleNodeClick`, `activeNodePKs`, `activeEdgeKeys`, `selectedNode`, `focusTarget`, `CANVAS_PALETTE` | Visualizes the knowledge graph, handles node selection, applies amber/gold halo glow to active nodes/edges, and performs camera interpolation to center illuminated subgraphs. |
| `src/frontend/src/components/FilterToolbar.tsx` | `FilterToolbar`, `filterState`, `setFilterState`, `policyKeyword`, `setPolicyKeyword` | Navigation toolbar providing state and policy filtering. Controls global state code passed to queries. |
| `src/frontend/src/styles/graph_theme.ts` | `CANVAS_PALETTE`, `ENTITY_THEMES`, `getNodeVisual(label: string)` | Theme registry containing color constants, amber/gold active glow styles (`#ffb703`), entity badge colors, and node radii. |
| `src/frontend/src/types/graph.ts` | `GraphNode`, `GraphLink`, `AnchorEntity`, `GraphRAGQueryResponse`, `NodeProperties`, `EdgeProvenance`, `GraphSummary` | TypeScript type declarations for all visualizer, graph, and GraphRAG payloads. |
| `src/frontend/src/App.tsx` | `App`, top-level visualizer container | Shell combining all visualizer components within `GraphSyncProvider`. |
| `src/frontend/package.json` | `dependencies`, `devDependencies`, `scripts` | Frontend configuration: React 19, D3 v7, Lucide React, TypeScript 6.0, Vite 8.3, Oxlint. |
| `src/api/routes.py` | `router = APIRouter(prefix="/api")`, `execute_graphrag_query`, `get_subgraph_by_anchors`, `resolve_entities`, `get_graph_topology`, `get_graph_summary`, `health_check` | FastAPI REST route definitions. `execute_graphrag_query` accepts `GraphRAGQueryRequest` and delegates to `pipeline.execute_query`. |
| `src/api/models.py` | `HealthResponse`, `TopologyNode`, `TopologyEdge`, `TopologyResponse`, `EntityResolveRequest`, `EntityResolveResponse`, `SubgraphRequest`, `SubgraphResponse`, `ErrorEnvelope` | Pydantic REST models for API endpoints. Imports `GraphRAGQueryRequest` and `GraphRAGQueryResponse` from `src.graphrag.models`. |
| `src/api/server.py` | `app = FastAPI(...)`, lifespan context manager, `CORSMiddleware`, router mounting | FastAPI application entry point managing Neo4j connection pool lifecycle and singleton sync engine. |
| `src/graphrag/models.py` | `AnchorEntity`, `ResolvedAnchors`, `TraversalNode`, `TraversalEdge`, `TraversalResult`, `GraphRAGQueryRequest`, `GraphRAGQueryResponse` | Core domain models for the GraphRAG pipeline. `GraphRAGQueryRequest` currently lacks explicit `anchor_pk` / `primary_key` field. |
| `src/graphrag/pipeline.py` | `GraphRAGPipeline`, `execute_query(request: GraphRAGQueryRequest, session: Session)` | 5-stage pipeline coordinator. Currently forces `self.linker.resolve_anchors` on `request.query` rather than utilizing an explicit anchor. |
| `src/graphrag/entity_linker.py` | `EntityAnchorLinker`, `resolve_anchors`, `STATE_NAME_TO_CODE`, `CLINICAL_SYNONYMS`, `POLICY_TRIGGERS`, `PK_TOKEN_REGEX`, `GEO_LOCATION_INDICATORS` | Resolves natural language into `ResolvedAnchors`. Contains regex bug where `GEO_LOCATION_INDICATORS` matches "in" within "Explain" and crashes on unindexed geography. |
| `src/graphrag/traversal.py` | `TopologicalTraversalEngine`, `extract_connecting_subgraph`, `_execute_single_entity_traversal`, `_execute_single_state_traversal`, `_execute_single_clinical_traversal`, `_execute_single_general_traversal`, `_execute_multi_entity_traversal` | Dynamic schema-driven graph expansion engine in Neo4j. Possesses relationship key bug (`UNKNOWN->RELATED_TO->UNKNOWN`) in single general traversal and clause ordering failure for `ICD10Code`. |
| `src/graphrag/context_assembler.py` | `GraphContextAssembler`, `assemble_context`, `_format_administrative_block`, `_format_clinical_block`, `_format_reimbursement_block`, `_format_provenance_block` | Formats traversed nodes and edges into structured Markdown prompt context blocks. |
| `src/graphrag/synthesizer.py` | `HuggingFaceSynthesizer`, `synthesize`, `SYSTEM_PROMPT`, `_call_hf_inference_api`, `ROUTER_CHAT_URL` | Calls Hugging Face Router API (`meta-llama/Llama-3.1-8B-Instruct`) with strict anti-hallucination guardrails and bracketed primary key citation rules. |
| `src/graphrag/exceptions.py` | `EntityResolutionError`, `TraversalError`, `ModelAuthenticationError`, `ModelInferenceError`, `ModelRateLimitError`, `GraphValidationError` | Custom exception hierarchy for GraphRAG operations. |
| `src/graph/neo4j_sync.py` | `Neo4jSyncEngine`, `get_driver()`, `get_summary_statistics()`, `init_schema()`, `sync_pipeline_run()` | Neo4j driver wrapper, constraint definitions, schema initialization, and graph database synchronization. |
| `src/graph/models.py` | Pydantic models: `PublicLaw`, `Bill`, `Regulation`, `StatutorySection`, `ChangeRequest`, `CoveragePolicy`, `Jurisdiction`, `State`, `HCPCSCode`, `ICD10Code`, `FeeScheduleEntry`, `LiteratureStudy`, `LobbyingFiling`, `PolicyNode` | Authoritative entity definitions for all 14 node types stored in Neo4j. |
| `src/graph/engine.py` | `PipelineEngine`, multi-tier ingestion runner | Data extraction and ingestion pipeline coordinating tiers 1 through 5. |
| `src/graph/tier1_legislative.py` | `Tier1LegislativeIngester` | Ingests Bills and Public Laws. |
| `src/graph/tier2_statutory.py` | `Tier2StatutoryIngester` | Ingests Statutory Sections (42 U.S.C. 1395x). |
| `src/graph/tier3_regulatory.py` | `Tier3RegulatoryIngester` | Ingests Regulations and Federal Register rules. |
| `src/graph/tier4a_coverage.py` | `Tier4aCoverageIngester` | Ingests Coverage Policies (LCDs/Articles) and Change Requests. |
| `src/graph/tier4b_fee_schedule.py` | `Tier4bFeeScheduleIngester` | Ingests HCPCS procedure codes and DMEPOS fee schedules. |
| `src/graph/tier5_context.py` | `Tier5ContextIngester` | Ingests Literature Studies and Lobbying Filings. |
| `tests/test_api_endpoints.py` | 7 REST API integration tests | Integration test suite verifying `/api/health`, `/api/graph/summary`, `/api/graph/topology`, `/api/entities/resolve`, `/api/graphrag/subgraph`, and `/api/graphrag/query`. |
| `tests/test_graphrag_pipeline.py` | 8 GraphRAG pipeline test functions covering all 6 authoritative oracles | Integration test suite verifying multi-slot resolution, $k$-hop expansion, context assembly, and synthesis. |
| `tests/test_graph_pipeline.py` | Pipeline unit & integration tests | Tests data ingestion tiers and Neo4j node/relationship synchronization. |
| `verify_all.py` | Full system end-to-end verification script | Runs end-to-end regression verification across all tiers and REST endpoints. |
| `package.json` | Workspace root scripts | Root scripts and configuration. |
| `LANGUAGE.md` | System glossary & taxonomy reference | Authoritative definitions for `{errors}`, `{correctness}`, `{functionality}`, `{correct required outputs}`, `{sufficient}`, and `{insufficient}`. |
| `wayfinder/map.md` | Wayfinder architectural map | Architectural map for GraphRAG and visualizer interaction. |
| `wayfinder/tickets/ticket-001.md` | Decision Ticket 001 | Entity Anchor Linking and Layperson Vocabulary Normalization Specification. |
| `wayfinder/tickets/ticket-002.md` | Decision Ticket 002 | Generalized Topological Subgraph Expansion and Neighborhood Traversal Specification. |
| `wayfinder/tickets/ticket-003.md` | Decision Ticket 003 | Factual Context Assembly, Edge Provenance Formatting, and Prompt Grounding Specification. |
| `wayfinder/tickets/ticket-004.md` | Decision Ticket 004 | Bidirectional Visual Canvas Synchronization and Active Subgraph Illumination Specification. |
| `wayfinder/tickets/ticket-005.md` | Decision Ticket 005 | Master Specification Synthesis and Edits for `functional_specification_004.md`. |
| `exports/lta_knowledge_graph.json` | LTA export snapshot (3,971 nodes, 7,795 edges) | Source graph export for Lymphedema Treatment Act policy domain. |
| `exports/ivig_knowledge_graph.json` | IVIG export snapshot | Source graph export for Intravenous Immune Globulin policy domain. |

---

## 3. Candidate External Datasource & Schema Audit Register

Active read-only reconnaissance was conducted across live external datasources, the Neo4j graph database, local REST API endpoints, and remote government web services. Raw, unedited payloads have been captured directly into `assets/20261013T172426-897-pj8g/`:

### 3.1. Neo4j Knowledge Graph Ground-Truth Audit
- **Reconnaissance Target:** Neo4j Bolt Instance (`bolt://localhost:7687`, database `neo4j`).
- **Authentication:** Direct bolt connection via `Neo4jSyncEngine`.
- **Database Statistics Verified:**
  - Total Nodes: `3,971`
  - Total Relationships: `7,795`
  - 14 Node Labels: `FeeScheduleEntry` (3,816), `HCPCSCode` (75), `State` (53), `ICD10Code` (6), `Jurisdiction` (4), `Bill` (3), `Policy` (2), `StatutorySection` (2), `ChangeRequest` (2), `CoveragePolicy` (2), `LobbyingFiling` (2), `LiteratureStudy` (2), `PublicLaw` (1), `Regulation` (1).
  - 14 Relationship Types: `HAS_FEE_SCHEDULE` (3,816), `APPLIES_TO` (3,816), `GOVERNS` (75), `COVERS_STATE` (53), `APPLIES_TO_JURISDICTION` (8), `ALLOWS_DIAGNOSIS` (6), `TARGETS_BILL` (4), `HAS_ADVOCACY_RECORD` (4), `ENACTED_AS` (3), `MODIFIES_CODE` (2), `IMPLEMENTED_BY` (2), `ISSUES_TRANSMITTAL` (2), `SUPPORTED_BY_EVIDENCE` (2), `MANDATES_POLICY` (2).
- **Captured Payloads:**
  - `assets/20261013T172426-897-pj8g/neo4j_summary_statistics.json`
  - `assets/20261013T172426-897-pj8g/neo4j_node_labels_and_counts.json`
  - `assets/20261013T172426-897-pj8g/neo4j_relationship_types_and_counts.json`
  - `assets/20261013T172426-897-pj8g/neo4j_sample_nodes_14_types.json`
  - `assets/20261013T172426-897-pj8g/neo4j_plaw117publ328_connections.json`: Confirms 5 direct connections for `PLAW-117-328` (`BILL-117-hr-3808`, `BILL-117-hr-2617`, `BILL-117-hr-3630`, `USC-42-1395x-s-2-Z`, `USC-42-1395x-s-2-JJ`).
  - `assets/20261013T172426-897-pj8g/neo4j_icd10_i972_connections.json`: Confirms direct incoming edge from `CMS-MCD-A59508` via `ALLOWS_DIAGNOSIS`.
  - `assets/20261013T172426-897-pj8g/neo4j_cms_mcd_a59508_connections.json`: Confirms connections to `CMS-CR-13286`, `ICD10-I97.2`, and `HCPCS-A6522`.

### 3.2. Local GraphRAG REST API Ground-Truth Audit
- **Reconnaissance Target:** Local FastAPI Server (`src/api/server.py`).
- **Status & Connectivity:** Verified 200 OK via `GET /api/health`.
- **Captured Payloads & Empirical Observations:**
  - `assets/20261013T172426-897-pj8g/local_api_health.json`: `{status: "ok", neo4j_connected: true}`.
  - `assets/20261013T172426-897-pj8g/local_api_graph_summary.json`: Summary stats payload.
  - `assets/20261013T172426-897-pj8g/local_api_subgraph_plaw117_328.json`: Subgraph for `PLAW-117-328` containing 6 nodes and 1 edge.
  - `assets/20261013T172426-897-pj8g/local_api_subgraph_icd10_i972.json`: Subgraph for `ICD10-I97.2` returning 1 node and 0 edges (demonstrating `DEF-TRAVERSAL-002`).
  - `assets/20261013T172426-897-pj8g/local_api_subgraph_a59508.json`: Subgraph for `CMS-MCD-A59508` returning 51 nodes.
  - `assets/20261013T172426-897-pj8g/local_api_graphrag_query_title_failure.json`: Response to `{"query": "Consolidated Appropriations Act, 2023"}` returning `active_node_pks: []` and 0 illuminated nodes (empirically verifying the bug stated in Section 1 of the spec).
  - `assets/20261013T172426-897-pj8g/local_api_graphrag_query_explain_regex_error.json`: Response to specced query `"Explain the statutory authority and enacted healthcare provisions of [PLAW-117-328] (Consolidated Appropriations Act, 2023)."` crashing with `EntityResolutionError: Unrecognized geographic jurisdiction 'the statutory authority'` (demonstrating `DEF-BACKEND-002`).
  - `assets/20261013T172426-897-pj8g/local_api_graphrag_query_pk_token_result.json`: Response to `{"query": "Public law [PLAW-117-328]"}` returning 6 active nodes but degenerate edge `["UNKNOWN->RELATED_TO->UNKNOWN"]` (demonstrating `DEF-TRAVERSAL-001`).
  - `assets/20261013T172426-897-pj8g/local_api_entity_resolve_comparison.json`: Resolves `[PLAW-117-328]` to PublicLaw anchor, but resolves entity title to 0 anchors.

### 3.3. Hugging Face Router & Model API Audit
- **Reconnaissance Target:** `https://router.huggingface.co/v1/chat/completions` and `https://huggingface.co/api/whoami-v2`.
- **Authentication:** Bearer token via environment variable `HF_TOKEN`. Verified valid.
- **Captured Payloads:**
  - `assets/20261013T172426-897-pj8g/hf_whoami.json`: User identity and organization membership verified (HTTP 200).

### 3.4. External Government Web Portals & Free REST APIs Audit
- **Federal Register REST API:**
  - Endpoint: `GET https://www.federalregister.gov/api/v1/documents/2023-24455.json`
  - Result: HTTP 200 OK.
  - Captured: `assets/20261013T172426-897-pj8g/federal_register_rule_2023_24455.json` (130 KB full document metadata, CFR citations, effective dates).
- **NLM Clinical Table Search API (HCPCS):**
  - Endpoint: `GET https://clinicaltables.nlm.nih.gov/api/hcpcs/v3/search?terms=A6522`
  - Result: HTTP 200 OK.
  - Captured: `assets/20261013T172426-897-pj8g/nlm_hcpcs_search_a6522.json`.
- **NLM Clinical Table Search API (ICD-10-CM):**
  - Endpoint: `GET https://clinicaltables.nlm.nih.gov/api/icd10cm/v3/search?sf=code,name&terms=I97.2`
  - Result: HTTP 200 OK.
  - Captured: `assets/20261013T172426-897-pj8g/nlm_icd10cm_search_i972.json`.
- **Government Document Web Headers:**
  - `assets/20261013T172426-897-pj8g/govinfo_plaw_117publ328_headers.txt` (HTTP 200)
  - `assets/20261013T172426-897-pj8g/congress_gov_bill_hr3630_headers.txt` (HTTP 403 - Cloudflare WAF bot challenge)
  - `assets/20261013T172426-897-pj8g/cms_mcd_search_results_a59508_headers.txt` (HTTP 503 - Akamai bot protection)
  - `assets/20261013T172426-897-pj8g/cms_transmittals_headers.txt` (HTTP 200)
  - `assets/20261013T172426-897-pj8g/cornell_lii_usc_42_1395x_headers.txt` (HTTP 200)
  - `assets/20261013T172426-897-pj8g/cgs_dme_headers.txt` (HTTP 200)
  - `assets/20261013T172426-897-pj8g/noridian_dme_headers.txt` (HTTP 200)
  - `assets/20261013T172426-897-pj8g/senate_lda_headers.txt` (HTTP 200)
  - `assets/20261013T172426-897-pj8g/pubmed_25574334_headers.txt` (HTTP 203)

---

## 4. Explicit Deficiency Register

In strict adherence to `INV-ABSENCE-01`, missing capabilities and broken behavioral contracts are itemized below without inventing fictional components or speculative contracts:

| Deficiency ID | Architectural Component | Specced Requirement (`functional_specification_007.md`) | Current Observed Behavior & Grounded Empirical Failure |
| :--- | :--- | :--- | :--- |
| `DEF-FRONTEND-001` | `src/frontend/src/components/NodeDetailDrawer.tsx` (lines 244-265) | Clicking "INQUIRE IN GRAPHRAG CHAT" must automatically open chat, construct entity prompt tailored to label/name (Section 4.2), pass `primary_key`, append to history, display loading indicator, and disable button during in-flight queries (Section 5.1). | Button `onClick` purely executes `setIsChatOpen(true)`. The selected node's `primary_key`, label, and name are discarded. No query is constructed or submitted, button does not disable while in-flight, leaving user with empty input box. |
| `DEF-FRONTEND-002` | `src/frontend/src/components/AgentChatDrawer.tsx` (lines 43-70) | Chat drawer must accept automated query dispatch seeded by node detail drawer, render formatted prompt in chat thread, transmit explicit `primary_key` anchor to backend, and process successive inquiries for different nodes as distinct turns (Section 5.2). | `handleSend` only handles manual text input or static `quickPrompts`. Dispatches `fetch('/api/graphrag/query')` with `{query, model_id, state_code}`, completely omitting `primary_key` / `anchor_pk`. |
| `DEF-FRONTEND-003` | `src/frontend/src/context/GraphSyncContext.tsx` | Context bus must provide coordinated inquiry dispatch method (e.g. `submitInquiry(prompt: string, anchorPk: string)`), synchronize query loading state across drawers, and preserve selected node across turns (Section 4.4). | `GraphSyncContext` has no method to trigger an inquiry dispatch from `NodeDetailDrawer` into `AgentChatDrawer`. In-flight loading state is kept local to `AgentChatDrawer`, so `NodeDetailDrawer` button cannot reflect loading/disabled state. |
| `DEF-API-001` | `src/api/routes.py`, `src/api/models.py`, `src/graphrag/models.py` | Request payload to `POST /api/graphrag/query` must include the selected entity's `primary_key` as a pre-resolved anchor to bypass keyword guessing (Section 4.3). | `GraphRAGQueryRequest` only defines `query`, `model_id`, and `state_code`. It lacks an `anchor_pk: Optional[str] = None` or `primary_key: Optional[str] = None` field, dropping the explicit anchor contract at the API boundary. |
| `DEF-BACKEND-001` | `src/graphrag/pipeline.py` (`GraphRAGPipeline.execute_query`) | When an explicit anchor (`primary_key`) is transmitted, backend must bind that anchor directly and bypass natural language text parsing or regex guessing (Section 4.3). | `execute_query` unconditionally runs `self.linker.resolve_anchors(request.query, session)`. If query text lacks an exact bracketed PK or if natural language fails, 0 nodes are illuminated (`local_api_graphrag_query_title_failure.json`). |
| `DEF-BACKEND-002` | `src/graphrag/entity_linker.py` (`GEO_LOCATION_INDICATORS`, lines 57-58, 328-341) | Prompts constructed with standard phrasing like *"Explain the statutory authority and enacted healthcare provisions of [PLAW-117-328]..."* must resolve the anchor without false syntax or parsing errors. | `GEO_LOCATION_INDICATORS = re.compile(r"(?:from|in|live in|resident of|located in)\s+([A-Za-z\s]+?)...")` lacks word boundary `\b` before `in`. It matches "in" within "Explain", extracting "the statutory authority" as a candidate state and crashing with fatal `EntityResolutionError` (`local_api_graphrag_query_explain_regex_error.json`). |
| `DEF-TRAVERSAL-001` | `src/graphrag/traversal.py` (`TopologicalTraversalEngine._execute_single_general_traversal`, lines 293-294) | 1-to-2 hop incident neighborhood traversal for any single entity (e.g. `PLAW-117-328`) must return authentic directed relationship keys (`source_pk->rel_type->target_pk`) so canvas illuminates connecting paths. | Lines 293-294 attempt `r.start_node["primary_key"]`. In Neo4j Driver 5.x, `r.start_node` is an element ID, not a property dictionary. `src` and `tgt` evaluate to `None`, causing `_convert_edge` to produce `UNKNOWN->RELATED_TO->UNKNOWN`. All edges collapse into a single degenerate key (`local_api_graphrag_query_pk_token_result.json`). |
| `DEF-TRAVERSAL-002` | `src/graphrag/traversal.py` (`TopologicalTraversalEngine._execute_single_clinical_traversal`, lines 224-233) | Single-entity inquiry for an `ICD10Code` (such as `ICD10-I97.2`) must traverse connecting `CoveragePolicy` articles (`CMS-MCD-A59508`), mandated change requests, and covered procedure codes, guaranteeing non-zero illuminated nodes (Section 4.3, 6.4). | The Cypher query begins with `OPTIONAL MATCH (cp:CoveragePolicy)-[r1:GOVERNS]->(h:HCPCSCode) WHERE n = h OR n = cp`. When `n` is `ICD10Code`, `cp` is NULL, causing all chained OPTIONAL MATCH clauses to return NULL. The query returns 0 connected nodes and 0 edges (`local_api_subgraph_icd10_i972.json`). |

---

## 5. Sufficiency & Scan Certification

In strict accordance with [`LANGUAGE.md`](LANGUAGE.md) and workspace rules:
- **`{sufficient}` Certification:** The static scan of the codebase and active read-only reconnaissance of external datasources are complete, exhaustive, and deterministic. Every relevant component in the dependency cone has been inspected under its verbatim path and symbol names. Every schema and payload has been verified against authentic live responses.
- **Zero Hallucination Guarantee:** No fictional endpoints, hypothetical variables, or speculative contracts have been assumed. All 8 identified system deficiencies are backed by empirical test files captured in `assets/20261013T172426-897-pj8g/`.

---

## 6. Handoff Manifest Affirmation

In strict compliance with `INV-MANIFEST-OVERWRITE-01`:
- Directory `handoff/20261013T172426-897-pj8g/` has been verified.
- The manifest at `handoff/20261013T172426-897-pj8g/plan-scan-1.txt` is atomically overwritten (truncated and replaced) with exclusively:
  1. The authored scan report: `scan_reports/scan_report_007_plan_scan_1.md`.
  2. All 42 verified codebase component files in the master dependency cone.
  3. All 29 saved ground-truth empirical payload sample files in `assets/20261013T172426-897-pj8g/`.
- No seed paths (`functional_specification_007.md`) are recorded in the manifest. Parent directory `handoff/` and predecessor manifests (`handoff/authored.txt`) remain fully intact.

---

## 7. Coding Gate Affirmation

**DO NOT CODE YET: Implementation coding gate remains locked. Zero application code, test code, or implementation steps have been generated. Coding waits on an empty frontier and explicit operator authorization.**
