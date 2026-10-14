# Deterministic Codebase Static Scan, External API Reconnaissance & Empirical Schema Audit Report (Agent 1: `plan-scan-1`)

**Run ID:** `20261014T030858-722-708n`  
**Node / Role:** Planning Node (`plan-scan-1`, Agent 1)  
**Governing Specification:** `functional_specification_015.md`  
**Taxonomy Reference:** `LANGUAGE.md`  
**Gate Status:** STRICT "DO NOT CODE YET" (`INV-BOUNDARY-01`)

---

## 1. Governing Context

### 1.1 Single Seed Specification Consumed
- **`functional_specification_015.md`** (*Functional Specification 015: End-to-End Agnostic Graph Persistence, Retrieval, and Visualization Alignment*).
- Consumed directly and exclusively from repository root (`functional_specification_015.md`). No other lines in `handoff/authored.txt` or unassigned specifications across `specs/` were read or scanned (`INV-HANDOFF-01`).

### 1.2 Wayfinder Map & Decision Tickets Inspected
The Wayfinder architectural map and decision ticket register in `wayfinder/` was directly inspected:
- **Wayfinder Architectural Map:** `wayfinder/map.md` (*Wayfinder Architectural Map: GraphRAG Specification for Browser Graph Visualizer*).
- **Decision Tickets Inspected:**
  1. `wayfinder/tickets/ticket-001.md`: *Entity Anchor Linking and Layperson Vocabulary Normalization Specification* (Scope: GraphRAG Stage 1 - Input Entity Resolution).
  2. `wayfinder/tickets/ticket-002.md`: *Generalized Topological Subgraph Expansion and Neighborhood Traversal Specification* (Scope: GraphRAG Stage 2 - Graph Topology Retrieval).
  3. `wayfinder/tickets/ticket-003.md`: *Factual Context Assembly, Edge Provenance Formatting, and Prompt Grounding Specification* (Scope: GraphRAG Stage 3 - Context Synthesis & Grounding).
  4. `wayfinder/tickets/ticket-004.md`: *Bidirectional Visual Canvas Synchronization and Active Subgraph Illumination Specification* (Scope: GraphRAG Stage 4 - Canvas-Agent Interaction Bus).
  5. `wayfinder/tickets/ticket-005.md`: *Master Specification Synthesis and Edits for functional_specification_004.md* (Scope: Specification Compilation & Synthesis).

### 1.3 Strict Alignment with `LANGUAGE.md` Evaluation Parameters
All evaluations and deficiency determinations in this report strictly adhere to the authoritative glossary in [`LANGUAGE.md`](file:///Users/diesel/Desktop/LAG/.sandcastle/worktrees/agent-plan-scan-1-20261014T030858-722-708n/LANGUAGE.md):
- **`{errors}`:** Explicit failure states surfaced during execution: unhandled exceptions, non-zero exit codes, unresolved symbols, missing graph entities, unmapped entity categories, hardcoded fallback identifiers, static synthetic links, or obsolete shortcut relationships in the database, API responses, or UI.
- **`{correctness}`:** The precise, local execution of a specific component verifying that it performs its designated task without logical flaws, respecting data types, schema definitions, and invariant boundaries.
- **`{functionality}`:** The broader, global system objective or business logic required by `functional_specification_015.md`: end-to-end alignment across the live Neo4j graph database, backend retrieval and context synthesis services, and the frontend visualizer canvas and detail drawer without hardcoded seeds, static fallbacks, or unmapped entity categories.
- **`{correct required outputs}`:** Objectively measurable deliverables:
  1. Exhaustive Component Dependency Cone Register.
  2. External API Reconnaissance and Empirical Schema Audit Register.
  3. Ground-truth payload captures in `assets/20261014T030858-722-708n/`.
  4. Explicit Deficiency Register detailing exact specification gaps without component invention.
  5. Dedicated role handoff manifest at `handoff/20261014T030858-722-708n/plan-scan-1.txt` atomically overwritten with one repository-relative path per line.
  6. Exactly zero lines of implementation or application feature code written.
- **`{sufficient}`:** The state of documentation where absolutely no ambiguity remains, all dependency cone components are identified, empirical schemas are verified, and downstream implementation can proceed deterministically.
- **`{insufficient}`:** Any state relying on unverified assumptions, speculative contracts, hallucinated endpoints, or static fallback placeholders.

---

## 2. Master Component Dependency Cone Register

Every component listed below physically exists in the codebase under its verbatim path and symbol names, and was directly inspected and verified during this static scan.

### 2.1 Frontend Visualization & Inspection Drawer Components

| Component ID | Repository-Relative Path | Verbatim Symbols & Interfaces | Role in Dependency Cone & Grounding Justification |
| :--- | :--- | :--- | :--- |
| **`COMP-FE-01`** | `src/frontend/src/components/GraphCanvas.tsx` | `GraphCanvasProps` (`nodes: GraphNode[]`, `links: GraphLink[]`, `loading: boolean`), `GraphCanvas`, `canvasRef`, `simulationRef`, `transformRef`, `zoomBehaviorRef`, `renderRef`, `hoveredNode`, `fps`, `isHudOpen`, `frameActiveSubgraph(targetPKs: Set<string>)`, `render()`, `handlePointerDown(e)`, `handlePointerMove(e)` | Core HTML5 2D `<canvas>` visualizer rendering force-directed graph. Consumes `activeNodePKs`, `activeEdgeKeys`, `isIlluminated`, `selectedNode` from `useGraphSync()`. Renders distinct node shapes, radii, colors, glow halos, and edge lines. Touches Section 4.1. |
| **`COMP-FE-02`** | `src/frontend/src/context/GraphSyncContext.tsx` | `ChatMessage`, `StateOption`, `JurisdictionMetadata`, `DME_JURISDICTIONS`, `STATE_TO_JURISDICTION`, `ALL_STATES_SORTED`, `GraphSyncContextType`, `GraphSyncProvider`, `useGraphSync`, `activeNodePKs`, `activeEdgeKeys`, `selectedNode`, `seededAnchor`, `isIlluminated`, `quickPrompts`, `filterJurisdiction`, `filterState`, `availableStates`, `policyKeyword`, `isChatOpen`, `messages`, `isQueryLoading`, `errorMsg`, `focusTarget`, `selectNode`, `setIlluminatedPath`, `clearIllumination`, `illuminateJurisdiction`, `setFilterJurisdiction`, `setFilterState`, `submitInquiry`, `inquireNode` | Bidirectional Canvas-Agent Synchronization Bus React context provider. Owns state for active nodes, edge keys, illumination, selected node, state/jurisdiction filters. Directly governs Section 4.3 and Section 3.1 filter interactions. |
| **`COMP-FE-03`** | `src/frontend/src/components/NodeDetailDrawer.tsx` | `NodeDetailDrawerProps` (`nodes: GraphNode[]`, `links: GraphLink[]`), `NodeDetailDrawer`, `connectedNeighbors`, `getGovernmentSourceLink()` | Node detail inspection drawer displaying all persisted properties of `selectedNode` and constructing official government external links (Congress.gov, GovInfo, Federal Register, Cornell LII, CMS Transmittals, CMS MCD, CDC, Noridian, CGS). Directly touches Section 4.2. |
| **`COMP-FE-04`** | `src/frontend/src/components/FilterToolbar.tsx` | `FilterToolbarProps` (`onReloadTopology`), `FilterToolbar`, `handleJurisdictionChange`, `handleStateChange`, `handlePolicyChange` | Top navigation toolbar providing dropdown selectors for DME MAC jurisdiction, state/territory, and policy keyword. Directly touches Section 4.3. |
| **`COMP-FE-05`** | `src/frontend/src/components/AgentChatDrawer.tsx` | `AgentChatDrawer`, `inputQuery`, `modelId`, `handleSend(queryText?: string)` | Conversational GraphRAG drawer component displaying synthesized answers, duration badges, and active node counts. Touches Section 3.3. |
| **`COMP-FE-06`** | `src/frontend/src/styles/graph_theme.ts` | `NodeVisualConfig`, `NODE_THEME_REGISTRY`, `CANVAS_PALETTE`, `getNodeVisual(label: string)` | Authoritative visual theme registry mapping entity category labels to colors, shapes, and radii. Directly touches Section 4.1. |
| **`COMP-FE-07`** | `src/frontend/src/types/graph.ts` | `NodeProperties`, `EdgeProvenance`, `GraphNode`, `GraphLink`, `AnchorEntity`, `GraphRAGQueryResponse`, `GraphSummary` | TypeScript interfaces defining graph nodes, relationships, provenance metadata, and GraphRAG response contracts. Touches Sections 2.1, 3.1, 4.1, 4.2. |
| **`COMP-FE-08`** | `src/frontend/src/utils/promptGenerator.ts` | `constructInquiryPrompt(node: GraphNode): string` | Deterministic natural-language inquiry generator formatting bracketed `[primary_key]` prompts across entity types. Touches Section 3.2. |
| **`COMP-FE-09`** | `src/frontend/src/App.tsx` | `RawTopologyNode`, `RawTopologyEdge`, `RawTopologyResponse`, `MainVisualizer`, `fetchTopology(stateFilter, policy, jurisdictionFilter)`, `App` | Root application component orchestrating topology fetch from `/api/graph/topology` and mapping API data into `GraphNode[]` and `GraphLink[]`. Touches Sections 3.1 and 4.1. |
| **`COMP-FE-10`** | `src/frontend/src/main.tsx` | `createRoot` entrypoint mounting `<App />`. | React 19 application mount. |
| **`COMP-FE-11`** | `src/frontend/src/index.css` | Global stylesheet defining CSS variables and full-viewport visual layout. | Base styling and container dimensions. |
| **`COMP-FE-12`** | `src/frontend/vite.config.ts` | Vite dev server configuration and `/api` reverse proxy to `http://localhost:8000`. | Build and network toolchain. |
| **`COMP-FE-13`** | `src/frontend/package.json` | Dependencies: `react`, `react-dom`, `d3`, `lucide-react`. Scripts: `dev`, `build`, `lint`. | Frontend dependency manifest. |

### 2.2 Backend Retrieval & Context Services Components

| Component ID | Repository-Relative Path | Verbatim Symbols & Interfaces | Role in Dependency Cone & Grounding Justification |
| :--- | :--- | :--- | :--- |
| **`COMP-BE-01`** | `src/api/routes.py` | `router`, `set_sync_engine`, `get_sync_engine`, `get_pipeline`, `get_neo4j_session`, `health_check` (`GET /api/health`), `get_graph_summary` (`GET /api/graph/summary`), `get_graph_topology` (`GET /api/graph/topology`), `resolve_entities` (`POST /api/entities/resolve`), `get_subgraph_by_anchors` (`POST /api/graphrag/subgraph`), `execute_graphrag_query` (`POST /api/graphrag/query`) | FastAPI REST router implementing graph summary, topology filtering, entity resolution, and GraphRAG endpoints. Directly implements Section 3.1, 3.2, 3.3. |
| **`COMP-BE-02`** | `src/api/models.py` | `HealthResponse`, `TopologyNode`, `TopologyEdge`, `TopologyResponse`, `EntityResolveRequest`, `EntityResolveResponse`, `SubgraphRequest`, `SubgraphResponse`, `ErrorEnvelope` | Pydantic response and request models for REST endpoints. Governs API output schemas for Section 3.1, 3.2, 3.3. |
| **`COMP-BE-03`** | `src/api/server.py` | `lifespan`, `create_app`, `http_exception_handler`, `graphrag_exception_handler`, `app` | FastAPI server entry point managing Neo4j connection lifecycle, CORS middleware, and standardized JSON error envelopes. Touches Section 3.1, 3.2 fail-fast behavior. |
| **`COMP-GR-01`** | `src/graphrag/models.py` | `AnchorEntity`, `ResolvedAnchors`, `TraversalNode`, `TraversalEdge`, `TraversalResult`, `GraphRAGQueryRequest`, `GraphRAGQueryResponse` | Core Pydantic data models for the 5-stage GraphRAG pipeline and canvas illumination telemetry. Directly governs Sections 3.2, 3.3, 4.1. |
| **`COMP-GR-02`** | `src/graphrag/pipeline.py` | `GraphRAGPipeline`, `execute_query(request: GraphRAGQueryRequest, session: Session) -> GraphRAGQueryResponse` | Orchestrates entity resolution, topological subgraph traversal, context assembly, and LLM synthesis. Directly implements Section 3.3. |
| **`COMP-GR-03`** | `src/graphrag/entity_linker.py` | `EntityAnchorLinker`, `STATE_NAME_TO_CODE`, `CLINICAL_SYNONYMS`, `POLICY_TRIGGERS`, `HCPCS_REGEX`, `GEO_LOCATION_INDICATORS`, `PK_TOKEN_REGEX`, `resolve_anchors`, `resolve_explicit_anchor` | Dynamic multi-slot anchor resolution engine matching search terms, citations, codes, and location names against persisted graph entities. Directly implements Section 3.2. |
| **`COMP-GR-04`** | `src/graphrag/traversal.py` | `TopologicalTraversalEngine`, `extract_connecting_subgraph`, `_execute_patient_subgraph_traversal`, `_execute_cross_policy_traversal`, `_execute_single_general_traversal` | Generalized topological path extraction traversing connecting edges between resolved anchors. Directly implements Section 3.3. |
| **`COMP-GR-05`** | `src/graphrag/context_assembler.py` | `GraphContextAssembler`, `assemble_context(traversal_result: TraversalResult, state_code: Optional[str]) -> str` | Structured factual context synthesizer formatting traversed node attributes and edge provenance into Markdown blocks. Directly implements Section 3.3. |
| **`COMP-GR-06`** | `src/graphrag/synthesizer.py` | `HuggingFaceSynthesizer`, `synthesize`, `_call_hf_inference_api`, `SYSTEM_PROMPT` | Grounded synthesis engine calling Hugging Face Router API with strict anti-hallucination guardrails and bracketed primary key citation mandates. Implements Section 3.3 synthesis. |
| **`COMP-GR-07`** | `src/graphrag/exceptions.py` | `GraphRAGException`, `EntityResolutionError`, `TraversalError`, `ModelAuthenticationError`, `ModelRateLimitError`, `ModelInferenceError`, `GraphValidationError` | Fail-fast exception classes for GraphRAG operations. Enforces fail-fast behavior mandated by Section 3.1 and 3.2. |

### 2.3 Graph Ingestion, Extraction Pipeline & Persistence Components

| Component ID | Repository-Relative Path | Verbatim Symbols & Interfaces | Role in Dependency Cone & Grounding Justification |
| :--- | :--- | :--- | :--- |
| **`COMP-DB-01`** | `src/graph/neo4j_sync.py` | `Neo4jSyncEngine`, `init_schema()`, `sync_graph_dict(graph_dict, batch_size)`, `sync_file(json_path, batch_size)`, `get_summary_statistics()` | Neo4j property graph synchronization engine using APOC merge operations, primary key constraints, and secondary label indexes. Directly implements Section 2.1 ingestion and synchronization. |
| **`COMP-DB-02`** | `src/graph/models.py` | `EdgeProvenance`, `GraphEdge`, `BaseNode`, `PolicyNode`, `BillNode`, `PublicLawNode`, `StatutorySectionNode`, `USCSectionNode`, `RegulationNode`, `CFRSectionNode`, `ChangeRequestNode`, `TransmittalNode`, `CoveragePolicyNode`, `JurisdictionNode`, `StateNode`, `FeeScheduleEntryNode`, `FeeScheduleRateNode`, `HCPCSCodeNode`, `ProcedureCodeNode`, `ICD10CodeNode`, `DiagnosisCodeNode`, `LobbyingFilingNode`, `CBOScoreNode`, `LiteratureStudyNode`, `LegislativeHandoff`, `StatutoryHandoff`, `RegulatoryHandoff`, `OperationalHandoff`, `CoverageHandoff`, `CodingHandoff`, `FeeScheduleRecord`, `ReimbursementHandoff` | Master domain models defining all 17 entity types, deterministic primary key formats, edge schemas with provenance metadata, and inter-hop typed handoffs. Directly governs Section 2.1. |
| **`COMP-DB-03`** | `src/graph/engine.py` | `GraphValidationError`, `DirectedPropertyGraph`, `PropertyGraphEngine`, `run_pipeline(keyword, run_id)`, `validate_invariants(graph, keyword)` | 8-hop knowledge graph pipeline orchestrator enforcing MERGE upsert semantics, linear omnibus ancestry, provenance completeness, and 54-jurisdiction completeness. Directly implements Section 2.1. |
| **`COMP-DB-04`** | `src/graph/tier1_legislative.py` | `discover_legislation(keyword, run_id, asset_dir)` | Hops 0 & 1: Legislative discovery and omnibus resolution creating `PolicyNode`, `BillNode`, `PublicLawNode`, and edges `DISCOVERED_BILL`, `INCORPORATED_INTO`, `ENACTED_AS`. Directly implements Section 2.1 #1, #2, #3. |
| **`COMP-DB-05`** | `src/graph/tier2_statutory.py` | `parse_statutory_codification(handoff, public_law_node, run_id, asset_dir, bill_titles)` | Hop 2: USLM XML parsing creating `StatutorySectionNode`, `USCSectionNode`, and edges `CONTAINS`, `AMENDS`. Directly implements Section 2.1 #4, #5. |
| **`COMP-DB-06`** | `src/graph/tier3_regulatory.py` | `harvest_regulations(handoff, statutory_node, run_id, asset_dir, usc_nodes)` | Hops 3 & 4: Federal Register Final Rule harvest and CMS Transmittal extraction creating `RegulationNode`, `CFRSectionNode`, `TransmittalNode`, and edges `AUTHORIZED_BY`, `CODIFIED_IN`, `IMPLEMENTED_BY`. Directly implements Section 2.1 #6, #7, #8. |
| **`COMP-DB-07`** | `src/graph/tier4a_coverage.py` | `ingest_coverage_policy(handoff, change_request_node, run_id, asset_dir, statutory_handoff)` | Hops 5 & 6: Coverage Guidance and HCPCS isolation creating `CoveragePolicyNode`, `ProcedureCodeNode`, `DiagnosisCodeNode`, and edges `MANDATES_POLICY`, `REQUIRES_DIAGNOSIS`, `COVERS_PROCEDURE`. Directly implements Section 2.1 #9, #10, #11. |
| **`COMP-DB-08`** | `src/graph/tier4b_fee_schedule.py` | `normalize_fee_schedules(handoff, change_request_node, hcpcs_nodes, run_id, asset_dir, coding_handoff)`, `DME_MAC_JURISDICTIONS` | Hop 7: 54-jurisdiction DMEPOS fee schedule unpivoting creating `JurisdictionNode`, `StateNode`, `FeeScheduleRateNode`, and edges `APPLIES_TO_JURISDICTION`, `COVERS_STATE`, `HAS_RATE`, `APPLIES_TO_STATE`. Directly implements Section 2.1 #12, #13, #14. |
| **`COMP-DB-09`** | `src/graph/tier5_context.py` | `enrich_context(target_bills, regulation_node, clinical_citations, run_id, asset_dir)` | Tier 5: Contextual enrichment creating `LobbyingFilingNode`, `CBOScoreNode`, `LiteratureStudyNode`, and edges `HAS_ADVOCACY_RECORD`, `HAS_BUDGET_IMPACT`, `SUPPORTED_BY_EVIDENCE`. Directly implements Section 2.1 #15. |

### 2.4 Verification, Demonstration & Test Suites

| Component ID | Repository-Relative Path | Verbatim Symbols & Interfaces | Role in Dependency Cone & Grounding Justification |
| :--- | :--- | :--- | :--- |
| **`COMP-TEST-01`** | `verify_all.py` | `main()` | End-to-end system verification script verifying live Neo4j connectivity, summary statistics, natural language patient benefit routing (Workflow 1), cross-policy legislative convergence (Workflow 3), and single-state dynamic inquiry (Workflow 4). Directly validates Acceptance Criteria 1, 2, 3. |
| **`COMP-TEST-02`** | `tests/test_graph_pipeline.py` | 11 automated pytest test functions verifying Hops 0–7, omnibus linearity, provenance completeness, and fail-fast exception classes. | Automated pipeline verification validating Section 2.1 and Acceptance Criterion 4. |
| **`COMP-TEST-03`** | `tests/test_api_endpoints.py` | 10 automated pytest test functions verifying FastAPI REST endpoints (`/api/health`, `/api/graph/summary`, `/api/graph/topology`, `/api/entities/resolve`, `/api/graphrag/subgraph`, `/api/graphrag/query`). | Automated API verification validating Section 3.1, 3.2, 3.3 and Acceptance Criterion 4. |
| **`COMP-TEST-04`** | `tests/test_graphrag_pipeline.py` | 9 automated pytest test functions validating the 5-stage GraphRAG pipeline, topological traversal, sub-second latency SLAs, and anti-hallucination synthesis. | Automated GraphRAG verification validating Section 3.3 and Acceptance Criterion 4. |

---

## 3. Candidate External Datasource Audit & Empirical Payload Schema Register

All candidate external datasources and API endpoints required by `functional_specification_015.md` were probed via safe, read-only GET requests or authoritative MCP tool calls. Unedited raw payloads were captured and saved directly into `assets/20261014T030858-722-708n/`.

| Datasource / API Identifier | Candidate Endpoint / Method | Verified Auth & Status | Captured Raw Payload File | Documented Empirical Schema & Observed Key Attributes |
| :--- | :--- | :--- | :--- | :--- |
| **Federal Register API (Final Rule)** | `https://www.federalregister.gov/api/v1/documents/2023-24455.json` | Status: `200 OK`. Public non-authenticated REST API. | `assets/20261014T030858-722-708n/external_federal_register_rule_2023_24455.json` (130,736 bytes) | `document_number: string` ("2023-24455"), `citation: string` ("88 FR 77676"), `title: string`, `action: string`, `effective_on: string` ("2024-01-01"), `cfr_references: list[dict]` (`title: int`, `part: int`), `docket_ids: list[string]` (["CMS-1780-F"]), `regulation_id_number: string` ("0938-AV03"). |
| **NLM Clinical Tables (HCPCS Code Search)** | `https://clinicaltables.nlm.nih.gov/api/hcpcs/v3/search?terms=A6522` | Status: `200 OK`. Public non-authenticated REST API. | `assets/20261014T030858-722-708n/external_nlm_hcpcs_search_a6522.json` (108 bytes) | Top-level 4-element JSON array: `[count: int, [code: string], null, [[code: string, description: string]]]`. Observed: `[1, ["A6522"], null, [["A6522", "GRADIENT COMPRESSION WRAP..."]]]`. |
| **NLM Clinical Tables (ICD-10-CM Search)** | `https://clinicaltables.nlm.nih.gov/api/icd10cm/v3/search?terms=I97.2` | Status: `200 OK`. Public non-authenticated REST API. | `assets/20261014T030858-722-708n/external_nlm_icd10cm_search_i972.json` (115 bytes) | Top-level 4-element JSON array: `[count: int, [code: string], null, [[code: string, description: string]]]`. Observed: `[1, ["I97.2"], null, [["I97.2", "Postmastectomy lymphedema syndrome"]]]`. |
| **NCBI PubMed Summary API (Clinical Evidence)** | `https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id=25574334&retmode=json` | Status: `200 OK`. Public non-authenticated E-utilities API. | `assets/20261014T030858-722-708n/external_pubmed_summary_25574334.json` (3,439 bytes) | `result: dict` containing `uids: list[string]` and dictionary keyed by UID with `uid: string`, `title: string`, `source: string` (journal name), `pubdate: string`, `articleids: list[dict]` (`idtype: "doi" / "pubmed"`). |
| **Hugging Face Router / Serverless Inference** | `https://router.huggingface.co/v1/chat/completions` (via `hf_whoami` MCP probe) | Status: `200 OK` authenticated. Fine-grained personal access token (`ChoppedCheese`, ID: `662eff76b10f82aa4fb0d8ce`). | `assets/20261014T030858-722-708n/external_hf_whoami.json` (288 bytes) | Account: `ChoppedCheese`, permissions: `inference.serverless.write`, `inference.endpoints.infer.write`, `repo.read`, `repo.write`. Used for anti-hallucination context synthesis. |
| **GPO GovInfo Public Law Service** | `https://www.govinfo.gov/app/details/PLAW-117publ328` | Status: `200 OK`. Authoritative GPO repository. | `assets/20261014T030858-722-708n/external_govinfo_plaw_117publ328_headers.txt` (1,938 bytes) | HTTP Headers verified: `Server: AkamaiGHost`, `Content-Type: text/html; charset=UTF-8`, `Status: 200 OK`. Details page for Public Law 117-328. |
| **Cornell Law School Legal Information Institute (LII)** | `https://www.law.cornell.edu/uscode/text/42/1395x` | Status: `200 OK`. Authoritative statutory codification host. | `assets/20261014T030858-722-708n/external_cornell_lii_usc_42_1395x_headers.txt` (602 bytes) | HTTP Headers verified: `Server: nginx`, `Content-Type: text/html; charset=UTF-8`, `Status: 200 OK`. Statutory text for 42 U.S.C. § 1395x. |
| **CMS Transmittals & Change Requests Portal** | `https://www.cms.gov/medicare/regulations-guidance/transmittals` | Status: `200 OK`. Official CMS operational directives index. | `assets/20261014T030858-722-708n/external_cms_transmittals_headers.txt` (1,015 bytes) | HTTP Headers verified: `Server: AkamaiNetStorage`, `Content-Type: text/html; charset=UTF-8`, `Status: 200 OK`. Search URL: `https://www.cms.gov/medicare/regulations-guidance/transmittals?search={CR_NUM}`. |
| **CMS Medicare Coverage Database (MCD)** | `https://www.cms.gov/medicare-coverage-database/search-results.aspx?keyword=A59508` | Status: `200 OK`. Official clinical coverage policy database. | `assets/20261014T030858-722-708n/external_cms_mcd_search_results_a59508_headers.txt` (1,573 bytes) | HTTP Headers verified: `Server: Microsoft-IIS/10.0`, `Content-Type: text/html; charset=utf-8`, `Status: 200 OK`. Search query verified for Article A59508. |
| **Noridian Healthcare Solutions (DME MAC A/D)** | `https://med.noridianmedicare.com/web/jadme` | Status: `200 OK`. Official MAC Jurisdiction A and D portal. | `assets/20261014T030858-722-708n/external_noridian_dme_headers.txt` (578 bytes) | HTTP Headers verified: `Content-Type: text/html;charset=UTF-8`, `Status: 200 OK`. Primary contractor portal for DME MAC Jurisdictions A and D. |
| **CGS Administrators (DME MAC B/C)** | `https://www.cgsmedicare.com/jb/` | Status: `200 OK`. Official MAC Jurisdiction B and C portal. | `assets/20261014T030858-722-708n/external_cgs_dme_headers.txt` (2,808 bytes) | HTTP Headers verified: `Server: Apache`, `Content-Type: text/html; charset=UTF-8`, `Status: 200 OK`. Primary contractor portal for DME MAC Jurisdictions B and C. |
| **U.S. Senate Lobbying Disclosure Act (LDA)** | `https://lda.senate.gov/filings/public/filing/search/` | Status: `200 OK`. Official Senate advocacy disclosures portal. | `assets/20261014T030858-722-708n/external_senate_lda_headers.txt` (411 bytes) | HTTP Headers verified: `Content-Type: text/html; charset=utf-8`, `Status: 200 OK`. Search portal for Lobbying Disclosure Act filings. |
| **Congress.gov Legislative Tracking Service** | `https://www.congress.gov/bill/117th-congress/house-bill/3630` | Status: `403 Forbidden` on automated curl User-Agent (Cloudflare Bot Protection). | `assets/20261014T030858-722-708n/external_congress_gov_bill_hr3630_headers.txt` (2,201 bytes) | HTTP Headers verified: `Server: cloudflare`, `Status: 403 Forbidden`. Dynamic link syntax in `NodeDetailDrawer.tsx` verified against Congress.gov URL scheme (`https://www.congress.gov/bill/{ordinal}-congress/{type}/{number}`). |
| **Live Neo4j Database (Summary Statistics)** | `bolt://localhost:7687` (via `Neo4jSyncEngine.get_summary_statistics()`) | Status: `Connected`. Bolt protocol 6.1.0. | `assets/20261014T030858-722-708n/neo4j_summary_statistics.json` (2,458 bytes) | `total_nodes: 3971`, `total_edges: 7795`, `nodes_by_label: list[dict]`, `edges_by_type: list[dict]`. |
| **Live Neo4j Database (Node Labels & Counts)** | `bolt://localhost:7687` (via `CALL db.labels()`) | Status: `Connected`. | `assets/20261014T030858-722-708n/neo4j_node_labels_and_counts.json` (1,223 bytes) | Label counts: `FeeScheduleEntry: 3816`, `HCPCSCode: 75`, `State: 53`, `ICD10Code: 6`, `Jurisdiction: 4`, `Bill: 3`, `Policy: 2`, `StatutorySection: 2`, `ChangeRequest: 2`, `CoveragePolicy: 2`, `LobbyingFiling: 2`, `LiteratureStudy: 2`, `PublicLaw: 1`, `Regulation: 1`. |
| **Live Neo4j Database (Relationship Types)** | `bolt://localhost:7687` (via `CALL db.relationshipTypes()`) | Status: `Connected`. | `assets/20261014T030858-722-708n/neo4j_relationship_types_and_counts.json` (832 bytes) | Relationship counts: `HAS_FEE_SCHEDULE: 3816`, `APPLIES_TO: 3816`, `GOVERNS: 75`, `COVERS_STATE: 53`, `APPLIES_TO_JURISDICTION: 8`, `ALLOWS_DIAGNOSIS: 6`, `TARGETS_BILL: 4`, `HAS_ADVOCACY_RECORD: 4`, `ENACTED_AS: 3`, `MODIFIES_CODE: 2`, `IMPLEMENTED_BY: 2`, `ISSUES_TRANSMITTAL: 2`, `SUPPORTED_BY_EVIDENCE: 2`, `MANDATES_POLICY: 2`. |
| **Live Neo4j Database (Sample Nodes by Type)** | `bolt://localhost:7687` (15 node type query) | Status: `Connected`. | `assets/20261014T030858-722-708n/neo4j_sample_nodes_15_types.json` (3,690 bytes) | Verbatim property dictionaries for 14 active node types, with `CBOScore` confirmed as `null` (zero nodes in live database). |
| **Local FastAPI Backend: Health Check** | `GET /api/health` | Status: `200 OK`. | `assets/20261014T030858-722-708n/api_health.json` (98 bytes) | `status: "ok"`, `neo4j_connected: true`, `timestamp: string`. |
| **Local FastAPI Backend: Graph Summary** | `GET /api/graph/summary` | Status: `200 OK`. | `assets/20261014T030858-722-708n/api_graph_summary.json` (2,458 bytes) | `total_nodes: 3971`, `total_edges: 7795`, `nodes_by_label: [...]`, `edges_by_type: [...]`. |
| **Local FastAPI Backend: Baseline Topology** | `GET /api/graph/topology` | Status: `200 OK`. | `assets/20261014T030858-722-708n/api_graph_topology_baseline.json` (128,803 bytes) | `nodes: list[TopologyNode]`, `edges: list[TopologyEdge]`, `total_nodes: 155`, `total_edges: 163`. Fee schedule nodes collapsed by default for 60 FPS performance. |
| **Local FastAPI Backend: State Topology (WI)** | `GET /api/graph/topology?state_filter=WI` | Status: `200 OK`. | `assets/20261014T030858-722-708n/api_graph_topology_wi.json` (188,597 bytes) | `total_nodes: 226`, `total_edges: 304`. Expands 71 Wisconsin-specific non-rural `FeeScheduleEntry` nodes. |
| **Local FastAPI Backend: Entity Resolution** | `POST /api/entities/resolve` | Status: `200 OK`. | `assets/20261014T030858-722-708n/api_entities_resolve.json` (369 bytes) | `anchors: list[AnchorEntity]` resolving `STATE-WI` (Wisconsin) and `ICD10-I97.2` (postmastectomy lymphedema syndrome). |
| **Local FastAPI Backend: Subgraph Traversal** | `POST /api/graphrag/subgraph` | Status: `200 OK`. | `assets/20261014T030858-722-708n/api_graphrag_subgraph.json` (161,310 bytes) | `active_node_pks: list[string]` (7 mandatory nodes), `active_edge_keys: list[string]` (7 connecting edges), `retrieval_ms: float` (3.78ms). |
| **Local FastAPI Backend: GraphRAG Query** | `POST /api/graphrag/query` | Status: `200 OK`. | `assets/20261014T030858-722-708n/api_graphrag_query_response.json` (3,382 bytes) | `answer: string`, `active_node_pks: list[string]`, `active_edge_keys: list[string]`, `anchors: list[AnchorEntity]`, `provenance_sources: list[dict]`, `duration_ms: float`. |

---

## 4. Explicit Deficiency Register

In strict adherence to `INV-ABSENCE-01` and `LANGUAGE.md`, the following deficiencies record exact discrepancies between existing codebase components or live database states and the requirements in `functional_specification_015.md`. No components, classes, or endpoints have been invented.

### `DEF-015-01`: Guam (`STATE-GU`) Missing from Live Neo4j, Entity Linker, and Frontend Jurisdiction Registry
- **Governing Specification Requirements:** Section 2.1 #14 (*"All 54 US states, districts, and territories (50 states + DC + PR + VI + GU) with two-letter postal code and full name"*), Section 3.1 (*"supporting all 54 jurisdictions including GU"*), Section 3.2 (*"Recognize all 54 US states and territories as valid geographic anchors"*), and Section 4.3 (*"Populate the state filter with all 54 US jurisdictions (50 states + DC + PR + VI + GU)"*).
- **Touched Components:**
  1. Live Neo4j Database: `MATCH (s:State)` returns exactly 53 nodes. `MATCH (s:State {state_code: "GU"})` returns empty (`[]`).
  2. `src/graphrag/entity_linker.py` (lines 14–31): `STATE_NAME_TO_CODE` has exactly 53 entries; `"guam": "GU"` is omitted. A user inquiry specifying "Guam" raises `EntityResolutionError` ("Unrecognized geographic location 'Guam'").
  3. `src/frontend/src/context/GraphSyncContext.tsx` (lines 96–122): `DME_JURISDICTIONS['JURIS-DME-D'].states` lists 17 states and omits `GU` (Guam). Total states across all 4 jurisdictions is 53 (`ALL_STATES_SORTED.length === 53`).
  4. `src/graph/engine.py` (lines 269–272): `if len(states) not in (53, 54):` explicitly allows an incomplete 53-state graph rather than failing fast on the absence of Guam.
  5. `src/api/routes.py` (lines 133–146): When `state_filter=GU` is requested, `MATCH (j:Jurisdiction)-[:COVERS_STATE]->(s:State {state_code: "GU"})` returns null and raises HTTP 400 Bad Request ("Unrecognized state code 'GU'").
- **Verified Empirical Root Cause:** Upstream `tier4b_fee_schedule.py` line 76 defines `("GU", "Guam")` under Jurisdiction D, but the existing export fixture loaded into Neo4j (`exports/lta_knowledge_graph.json` line 124964) was generated prior to Guam inclusion and has only 53 state records. Downstream entity linker and frontend context were written against the 53-state fixture.

### `DEF-015-02`: Obsolete Relationship Types Persisted in Live Neo4j and Hardcoded in Backend Traversal Cypher Queries
- **Governing Specification Requirements:** Section 2.1 Relationship Ingestion (*"Persist all relationship types with complete provenance metadata: DISCOVERED_BILL, INCORPORATED_INTO, ENACTED_AS, CONTAINS, AMENDS, AUTHORIZED_BY, CODIFIED_IN, IMPLEMENTED_BY, MANDATES_POLICY, REQUIRES_DIAGNOSIS, COVERS_PROCEDURE, HAS_RATE, APPLIES_TO_STATE, APPLIES_TO_JURISDICTION, COVERS_STATE, HAS_ADVOCACY_RECORD, HAS_BUDGET_IMPACT, and SUPPORTED_BY_EVIDENCE"*), Section 3.1, and Section 3.3.
- **Touched Components:**
  1. Live Neo4j Database: Captured in `assets/20261014T030858-722-708n/neo4j_relationship_types_and_counts.json`:
     - 3,816 edges of type `HAS_FEE_SCHEDULE` (specced as `HAS_RATE`).
     - 3,816 edges of type `APPLIES_TO` (specced as `APPLIES_TO_STATE`).
     - 75 edges of type `GOVERNS` (specced as `COVERS_PROCEDURE`).
     - 6 edges of type `ALLOWS_DIAGNOSIS` (specced as `REQUIRES_DIAGNOSIS`).
     - 4 edges of type `TARGETS_BILL` (specced as `DISCOVERED_BILL`).
     - 2 edges of type `MODIFIES_CODE` (specced as `CONTAINS` / `AMENDS`).
     - 2 edges of type `ISSUES_TRANSMITTAL` (specced as `IMPLEMENTED_BY`).
  2. `src/api/routes.py`:
     - Lines 270, 272: `MATCH (f:FeeScheduleEntry)-[r1:APPLIES_TO]->(s:State {state_code: $state_code}) ... MATCH (h:HCPCSCode)-[r2:HAS_FEE_SCHEDULE]->(f)`
     - Lines 303, 311: `MATCH (h:HCPCSCode)-[r2:HAS_FEE_SCHEDULE]->(f:FeeScheduleEntry)-[r1:APPLIES_TO]->(s:State)`
  3. `src/graphrag/traversal.py`:
     - Lines 98–145: Cypher queries explicitly match `[:ALLOWS_DIAGNOSIS]`, `[:GOVERNS]`, `[:HAS_FEE_SCHEDULE]`, and `[:APPLIES_TO]`.
- **Verified Empirical Root Cause:** `src/graph/tier1_legislative.py` through `tier4b_fee_schedule.py` were refactored to emit the specification relationship labels (`HAS_RATE`, `APPLIES_TO_STATE`, `COVERS_PROCEDURE`, `REQUIRES_DIAGNOSIS`), but the live Neo4j database was populated with old exports (`exports/lta_knowledge_graph.json` and `ivig_knowledge_graph.json`), and the retrieval services in `src/api/routes.py` and `src/graphrag/traversal.py` remain hardcoded to the obsolete relationship types.

### `DEF-015-03`: Primary Key Prefix Mismatches for Regulations (`FR-` vs `REG-FR-`) and Transmittals (`CMS-CR-` vs `TR-CR`)
- **Governing Specification Requirements:** Section 2.1 #6 (*"Federal Register Final Rule (REG-FR-...)"*), Section 2.1 #8 (*"Transmittal (TR-CR...)"*), and Section 3.2 (*"Support explicit primary key lookup across all valid prefixes (POLICY-, BILL-, PLAW-, STAT-, USC-, REG-FR-, CFR-, TR-CR, DME-MAC-, CMS-MCD-, ICD10-, HCPCS-, FEE-, JURIS-DME-, STATE-, LDA-, CBO-, PUBMED-)"*).
- **Touched Components:**
  1. Live Neo4j Database: Captured in `assets/20261014T030858-722-708n/neo4j_sample_nodes_15_types.json`:
     - Regulation node has `primary_key: "FR-2023-24455"` instead of `REG-FR-2023-24455`.
     - ChangeRequest nodes have `primary_key: "CMS-CR-13286"` and `"CMS-CR-13217"` instead of `TR-CR13286` and `TR-CR13217`.
  2. `src/api/routes.py`:
     - Line 194: `elif pk.startswith("FR-"): label = "Regulation"`
     - Line 196: `elif pk.startswith("CMS-CR-"): label = "ChangeRequest"`
  3. `src/graphrag/entity_linker.py`:
     - Line 62: `PK_TOKEN_REGEX = re.compile(r"\b([A-Z0-9]+-[A-Z0-9\-_.]{2,})\b")` does not match unhyphenated transmittal prefix `TR-CR13286` without an additional token separator.
  4. `src/graphrag/traversal.py`:
     - Hardcoded checks for `"CMS-CR-"` in lines 112, 126, 381.
- **Verified Empirical Root Cause:** `src/graph/models.py` line 148 defines `primary_key = f"REG-FR-{self.document_number}"` and line 189 defines `primary_key = f"TR-CR{clean_cr}"`, but historical Neo4j fixture data and downstream retrieval components still expect the older prefixes `FR-` and `CMS-CR-`.

### `DEF-015-04`: Discrepant Node Labels and Incomplete Label Taxonomy Across Neo4j, Routes, and Visual Theme Registry
- **Governing Specification Requirements:** Section 2.1 (Persist all 15 entity types), Section 3.1 (Return node with entity label), and Section 4.1 (*"Render and distinguish all entity categories on the graph canvas (Policy, Bill, PublicLaw, StatutorySection, USCSection, Regulation, CFRSection, Transmittal, CoveragePolicy, DiagnosisCode, ProcedureCode, FeeScheduleRate, Jurisdiction, State, LobbyingFiling, CBOScore, LiteratureStudy)"*).
- **Touched Components:**
  1. Live Neo4j Database:
     - Uses label `FeeScheduleEntry` instead of `FeeScheduleRate`.
     - Uses label `ChangeRequest` instead of `Transmittal`.
     - Uses label `HCPCSCode` instead of `ProcedureCode`.
     - Uses label `ICD10Code` instead of `DiagnosisCode`.
     - Zero `USCSection`, `CFRSection`, or `CBOScore` nodes exist in the live database.
  2. `src/graph/neo4j_sync.py`:
     - Lines 63–79: `init_schema()` creates indexes for obsolete labels (`ChangeRequest`, `HCPCSCode`, `ICD10Code`, `FeeScheduleEntry`) and completely lacks index creation for `USCSection`, `CFRSection`, `Transmittal`, `ProcedureCode`, `DiagnosisCode`, and `FeeScheduleRate`.
  3. `src/frontend/src/styles/graph_theme.ts`:
     - Lines 12–97: `NODE_THEME_REGISTRY` contains visual configurations for only 14 labels. It is missing definitions for `USCSection`, `CFRSection`, `Transmittal`, `ProcedureCode`, `DiagnosisCode`, `FeeScheduleRate`, and `CBOScore`.
- **Verified Empirical Root Cause:** The schema indexer in `neo4j_sync.py` and the visualizer theme in `graph_theme.ts` were created under an earlier 14-label specification (`functional_specification_007.md` / `009.md`) and have not been updated to the comprehensive 17-label taxonomy defined in `functional_specification_015.md`.

### `DEF-015-05`: Static Hardcoded Fallback Identifiers in Frontend `NodeDetailDrawer.tsx`
- **Governing Specification Requirements:** Section 1 (*"Any hardcoded policy identifiers, static fallback text, unmapped entity categories, or outdated shortcut relationships in the database, API responses, or UI constitute {errors} and make the system {insufficient}"*) and Section 4.2 (*"Construct external government links dynamically from node attributes (e.g. Congress.gov, Federal Register, eCFR, CMS MCD, PubMed). If required attributes are missing, omit the link rather than substituting fallback IDs"*).
- **Touched Component:** `src/frontend/src/components/NodeDetailDrawer.tsx` (lines 78–104).
- **Verified Empirical Root Cause:**
  - In `NodeDetailDrawer.tsx`, the `getGovernmentSourceLink()` helper injects hardcoded fallback strings when node properties are missing:
    - Line 78: `props.congress || selectedNode.primary_key.match(/PLAW-(\d+)-/)?.[1] || '117'`
    - Line 79: `props.number || selectedNode.primary_key.match(/PLAW-\d+-(\d+)/)?.[1] || '328'`
    - Line 86: `Number(props.congress || selectedNode.primary_key.match(/BILL-(\d+)-/)?.[1] || 117)`
    - Line 88: `props.number || selectedNode.primary_key.match(/BILL-\d+-[a-z]+-(\d+)/)?.[1] || '3630'`
    - Line 102: `const title = props.title || '42';`
    - Line 103: `const rawSec = props.section || selectedNode.primary_key.replace(/^USC-\d+-/, '') || '1395x';`
  - Under Section 4.2, if required attributes (`congress`, `number`, `title`, `section`) are missing, the drawer MUST omit the link entirely rather than substituting synthetic fallback IDs like `'117'`, `'328'`, `'3630'`, or `'1395x'`.

### `DEF-015-06`: Missing Direct Link Construction for `eCFR` and `PubMed` in `NodeDetailDrawer.tsx`
- **Governing Specification Requirements:** Section 4.2 (*"Construct external government links dynamically from node attributes (e.g. Congress.gov, Federal Register, eCFR, CMS MCD, PubMed)"*).
- **Touched Component:** `src/frontend/src/components/NodeDetailDrawer.tsx` (lines 69–140).
- **Verified Empirical Root Cause:**
  - `NodeDetailDrawer.tsx` implements link generators for `CoveragePolicy`, `PublicLaw`, `Bill`, `Regulation`, `StatutorySection`, `ChangeRequest`, `Jurisdiction`, `HCPCSCode`, and `ICD10Code`.
  - It completely lacks branch handlers for:
    1. `CFRSection`: no dynamic link to official eCFR (`https://www.ecfr.gov/current/title-{title}/part-{part}`).
    2. `LiteratureStudy` / PubMed: no dynamic link to NCBI PubMed (`https://pubmed.ncbi.nlm.nih.gov/{pmid}/`).
    3. `CBOScore`: no dynamic link to official CBO score reports.

---

## 5. Sufficiency & Scan Certification

- **Dependency Cone Completeness:** Every codebase component across the frontend React visualizer, FastAPI REST router, GraphRAG retrieval engine, Neo4j persistence engine, 8-hop extraction pipeline, and test suites has been cataloged under its verbatim symbol and file path.
- **Empirical Reconnaissance Grounding:** All external endpoints and datasources (Federal Register API, NLM Clinical Tables for HCPCS and ICD-10, NCBI PubMed E-utilities, GovInfo, Cornell LII, CMS Transmittals, CMS MCD, DME MAC portals, Senate LDA, Hugging Face Router API, and live Neo4j database) were probed via non-mutating requests, and authentic raw payload responses were saved into `assets/20261014T030858-722-708n/`.
- **Deficiency Grounding:** Every deficiency recorded in Section 4 is verified by direct empirical evidence in code and database telemetry, with zero speculative assumptions or invented components (`INV-ABSENCE-01`).
- **Sufficiency Determination (`LANGUAGE.md`):** The static codebase scan, active API reconnaissance, empirical schema audit, and deficiency register are **`{sufficient}`** for downstream planning and Wayfinder ticket generation.

---

## 6. Handoff Manifest Affirmation

The role handoff manifest at `handoff/20261014T030858-722-708n/plan-scan-1.txt` has been atomically overwritten (`INV-MANIFEST-OVERWRITE-01`) with exclusively the repository-relative filepaths of:
1. All qualified codebase component files reviewed during this scan.
2. This authored scan report (`scan_reports/scan_report_015_plan_scan_1.md`).
3. All 24 saved ground-truth payload sample files in `assets/20261014T030858-722-708n/`.

No seed specification paths (`functional_specification_015.md` or ticket paths) were written to the handoff manifest. Predecessor manifests (`handoff/authored.txt`) and other run directories remain fully preserved.

---

## 7. Coding Gate Affirmation

*DO NOT CODE YET: Implementation coding gate remains locked. Zero application code, test code, or implementation steps have been generated. Coding waits on an empty frontier and explicit operator authorization.*
