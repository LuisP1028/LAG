# Authoritative Static Codebase Scan, External API Reconnaissance, and Schema Audit Report

**Run ID:** `20261013T172426-897-pj8g`  
**Agent:** `plan-scan-2` (Planning Node / Scanner Agent 2)  
**Governing Specification:** `functional_specification_007.md`  
**Status:** Complete Reconnaissance, Codebase Scan, and Empirical Schema Audit (DO NOT CODE YET)  
**Taxonomy Reference:** [LANGUAGE.md](LANGUAGE.md)

---

## 1. Governing Context & Upstream Ingestion Verification

In strict accordance with `INV-HANDOFF-01`, `INV-SCAN-01`, and workspace rules:
- **Seed Specification Ingested:** `functional_specification_007.md` (*Functional Specification: Node Detail Contextual Inquire Action and Targeted GraphRAG Execution*), verified non-empty, fully bound, exactly matching single seed scope.
- **Run Identifier:** `20261013T172426-897-pj8g` (verified substituted across all filepaths, asset directories, and handoff manifest paths).
- **Wayfinder Architectural Map & Decision Tickets Inspected:**
  - Map file: `wayfinder/map.md` (*Wayfinder Architectural Map: GraphRAG Specification for Browser Graph Visualizer*)
  - Ticket 001: `wayfinder/tickets/ticket-001.md` — *Decision Ticket 001: Entity Anchor Linking and Layperson Vocabulary Normalization Specification*
  - Ticket 002: `wayfinder/tickets/ticket-002.md` — *Decision Ticket 002: Generalized Topological Subgraph Expansion and Neighborhood Traversal Specification*
  - Ticket 003: `wayfinder/tickets/ticket-003.md` — *Decision Ticket 003: Factual Context Assembly, Edge Provenance Formatting, and Prompt Grounding Specification*
  - Ticket 004: `wayfinder/tickets/ticket-004.md` — *Decision Ticket 004: Bidirectional Visual Canvas Synchronization and Active Subgraph Illumination Specification*
  - Ticket 005: `wayfinder/tickets/ticket-005.md` — *Decision Ticket 005: Master Specification Synthesis and Edits for functional_specification_004.md*
- **Evaluation Parameters Glossary:** Fully bound to [`LANGUAGE.md`](LANGUAGE.md), strictly adhering to authoritative definitions for `{errors}`, `{correctness}`, `{functionality}`, `{correct required outputs}`, `{sufficient}`, and `{insufficient}` without colloquial paraphrasing or semantic divergence.

---

## 2. Master Component Dependency Cone Register

The deterministic static scan of the active codebase cataloged all local modules, data models, storage engines, sync clients, API endpoints, frontend visualizer components, and configuration files whose interfaces or behaviors touch specced functionality:

| Repository-Relative Path | Symbol / Entity | Interface / Role | Grounding Justification |
|---|---|---|---|
| `LANGUAGE.md` | System Glossary & Domain Taxonomy | Authoritative system-wide definitions for `{errors}`, `{correctness}`, `{functionality}`, `{correct required outputs}`, `{sufficient}`, `{insufficient}`, and domain taxonomy (`{Policy Keyword}`, `{Target_Bill_IDs}`, `{Enacted_Law_ID}`, `{US_Code_Citations}`, `{Operational_Filters}`, `{Clinical_Citations}`, `{HCPCS / CPT Codes}`). | Authoritative evaluation baseline mandated by system rules. |
| `src/frontend/src/components/NodeDetailDrawer.tsx` | `NodeDetailDrawer`, button "INQUIRE IN GRAPHRAG CHAT", `selectedNode`, `getGovernmentSourceLink`, `connectedNeighbors` | Slide-over drawer displaying entity details, properties, connected neighbors, and action button. | `functional_specification_007.md` Section 1, 3, 4.1, 4.2 mandates transforming the "INQUIRE IN GRAPHRAG CHAT" button from passive toggle into active one-click inquiry trigger. |
| `src/frontend/src/components/AgentChatDrawer.tsx` | `AgentChatDrawer`, `handleSend`, `messages`, `loading`, `errorMsg`, `inputQuery` | Slide-over chat drawer executing GraphRAG queries and emitting illuminated paths to canvas. | `functional_specification_007.md` Section 4.1 mandates automated drawer opening, prompt insertion, query dispatch with `primary_key`, and response rendering. |
| `src/frontend/src/context/GraphSyncContext.tsx` | `GraphSyncContext`, `GraphSyncProvider`, `useGraphSync`, `selectedNode`, `selectNode`, `seededAnchor`, `isChatOpen`, `setIsChatOpen`, `setIlluminatedPath`, `focusTarget`, `setFocusTarget` | Context provider managing shared application state across canvas, toolbar, drawers, and active path illumination. | Shared state bus for node selection, anchor seeding, drawer visibility, and path illumination. |
| `src/frontend/src/components/GraphCanvas.tsx` | `GraphCanvas`, `render`, `handlePointerDown`, `handlePointerMove`, `focusTarget`, `activeNodePKs`, `activeEdgeKeys` | HTML5 Canvas force-directed graph renderer; renders nodes, laser struts, halos, labels, and handles node selection clicks. | `functional_specification_007.md` Section 4.4 mandates canvas path illumination and viewport centering in amber/gold. |
| `src/frontend/src/components/FilterToolbar.tsx` | `FilterToolbar`, `handleStateChange`, `handlePolicyChange` | Top navigation toolbar rendering jurisdiction selector, policy selector, path reset button, and GraphRAG chat trigger. | Interacts with global visualizer filter states and chat drawer toggle. |
| `src/frontend/src/App.tsx` | `MainVisualizer`, `App`, `fetchTopology`, `nodes`, `links` | Top-level visualizer view orchestrating topology fetching, canvas rendering, toolbar placement, and drawer overlays. | Hosts `NodeDetailDrawer` and `AgentChatDrawer` within `GraphSyncProvider`. |
| `src/frontend/src/types/graph.ts` | `GraphNode`, `GraphLink`, `AnchorEntity`, `GraphRAGQueryResponse`, `GraphSummary` | Client-side TypeScript interfaces for graph nodes, links, and query response payloads. | Contract definitions for frontend node properties and topology data. |
| `src/frontend/src/styles/graph_theme.ts` | `CANVAS_PALETTE`, `NODE_VISUALS`, `getNodeVisual` | Color palette, badge colors, radius specifications, and visual descriptions for 14 node entity types. | Supplies badge colors and visual attributes for node rendering and drawer headers. |
| `src/frontend/src/main.tsx` | Application Root | Bootstraps React application root. | Frontend entry point. |
| `src/frontend/src/App.css` | App Styling | Component layout CSS. | Visual styling. |
| `src/frontend/src/index.css` | Global CSS | Global stylesheet, reset rules, and typography. | Theme styles. |
| `src/frontend/package.json` | Dependencies & Scripts | Defines React 19, Vite 8, Lucide React, and D3 dependencies. | Frontend package configuration. |
| `src/frontend/package-lock.json` | Dependency Lockfile | Exact dependency versions for frontend application. | Frontend lockfile. |
| `src/frontend/vite.config.ts` | Vite Configuration | Dev server port and API proxy routing. | Frontend build configuration. |
| `src/frontend/tsconfig.json` | TypeScript Configuration | Project-wide TypeScript compiler settings. | Compiler settings. |
| `src/frontend/tsconfig.app.json` | TypeScript App Configuration | Application-specific TypeScript configuration. | Compiler settings. |
| `src/frontend/tsconfig.node.json` | TypeScript Node Configuration | Node environment TypeScript configuration. | Compiler settings. |
| `src/frontend/index.html` | HTML Entry Point | Root web page mounting React application. | DOM entry point. |
| `src/api/routes.py` | `execute_graphrag_query`, `get_subgraph_by_anchors`, `resolve_entities`, `get_graph_topology` | REST endpoint `/api/graphrag/query`, `/api/graphrag/subgraph`, `/api/entities/resolve`. | `functional_specification_007.md` Section 4.3 mandates transmitting explicit `primary_key` anchor directly to bypass keyword guessing. |
| `src/api/models.py` | `GraphRAGQueryRequest`, `GraphRAGQueryResponse`, `SubgraphRequest`, `SubgraphResponse`, `TopologyNode`, `TopologyEdge` | Pydantic schemas for API requests and responses. | Contract defining `/api/graphrag/query` request payload. |
| `src/api/server.py` | FastAPI Application Factory | Server configuration and error handling. | API server runner. |
| `src/api/__init__.py` | Package Exports | Exposes API server and routes. | Public interface for API. |
| `src/graphrag/pipeline.py` | `GraphRAGPipeline`, `execute_query` | End-to-end GraphRAG pipeline coordinating linking, traversal, assembly, and synthesis. | Orchestrates retrieval using explicit anchor and returns non-zero illuminated nodes. |
| `src/graphrag/models.py` | `AnchorEntity`, `ResolvedAnchors`, `TraversalResult`, `GraphRAGQueryRequest`, `GraphRAGQueryResponse` | Pipeline data models for anchors, traversals, and query contracts. | Internal data contracts for GraphRAG pipeline. |
| `src/graphrag/entity_linker.py` | `EntityAnchorLinker`, `resolve_anchors`, `_extract_state_anchor`, `_extract_legislative_anchors` | Deterministic entity anchor resolver. | Resolves query text to graph anchors; currently contains regex boundary flaws and lacks pre-resolved anchor bypass. |
| `src/graphrag/traversal.py` | `TopologicalTraversalEngine`, `extract_connecting_subgraph`, `_execute_single_entity_traversal`, `_execute_single_general_traversal` | Generalized topological expansion engine. | Traverses Neo4j subgraphs; currently contains relationship tuple deserialization flaw for single general entities (`PLAW-117-328`). |
| `src/graphrag/context_assembler.py` | `GraphContextAssembler`, `assemble_context` | Formats subgraphs into structured context. | Assembles factual context for synthesis; currently omits `Bill` nodes and generic legislative metadata. |
| `src/graphrag/synthesizer.py` | `HuggingFaceSynthesizer`, `synthesize`, `_call_hf_inference_api` | Synthesizes answers using Hugging Face router API. | Generates grounded responses quoting bracketed primary keys. |
| `src/graphrag/exceptions.py` | Custom Exception Hierarchy (`EntityResolutionError`, `TraversalError`, `GraphValidationError`) | Standardized fail-fast exceptions. | Enforces error boundaries. |
| `src/graphrag/__init__.py` | Package Exports | GraphRAG subsystem exports. | Public interface. |
| `src/graph/models.py` | `BaseNode`, `PolicyNode`, `BillNode`, `PublicLawNode`, `StatutorySectionNode`, `RegulationNode`, `ChangeRequestNode`, `CoveragePolicyNode`, `JurisdictionNode`, `StateNode`, `FeeScheduleEntryNode`, `HCPCSCodeNode`, `ICD10CodeNode`, `LobbyingFilingNode` | Domain models declaring exact properties for all 14 entity types. | Verifies property names across all 14 entity types in Neo4j. |
| `src/graph/neo4j_sync.py` | `Neo4jSyncEngine` | Driver lifecycle manager and Neo4j query interface. | Storage engine for active knowledge graph. |
| `src/graph/engine.py` | `DirectedPropertyGraph`, `PropertyGraphEngine` | In-memory directed graph engine and invariant validator. | Graph structure engine. |
| `src/graph/tier1_legislative.py` | `discover_legislation` | Discovers bills and enacted public laws (`PLAW-117-328`). | Provides legislative properties for bills and laws. |
| `src/graph/tier2_statutory.py` | `parse_statutory_codification` | Parses US Code sections (42 U.S.C. 1395x). | Defines statutory citation structure. |
| `src/graph/tier3_regulatory.py` | `harvest_regulations` | Ingests Federal Register rules and Change Requests. | Defines regulatory document numbers and transmittal numbers. |
| `src/graph/tier4a_coverage.py` | `ingest_coverage_policy`, `STANDARD_COVERED_DIAGNOSES`, `STANDARD_COVERED_HCPCS` | Coverage policy linkage and clinical indication bridges. | Ingests `CoveragePolicy`, `HCPCSCode`, and `ICD10Code` nodes. |
| `src/graph/tier4b_fee_schedule.py` | `normalize_fee_schedules`, `DME_MAC_JURISDICTIONS` | Maps Medicare Administrative Contractors (Noridian, CGS) to Jurisdictions A, B, C, D. | Defines contractor portals and regional jurisdiction contracts. |
| `src/graph/tier5_context.py` | `enrich_context` | Ingests Lobbying Disclosure Act filings. | Defines lobbying filing UUIDs and registrant properties. |
| `src/graph/__init__.py` | Package Exports | Graph domain package exports. | Public interface for graph models. |
| `tests/test_api_endpoints.py` | API Test Suite | Pytest test suite for REST routes. | Verifies endpoint behavior. |
| `tests/test_graph_pipeline.py` | Graph Pipeline Test Suite | Tests graph invariants and sync. | Verifies graph integrity. |
| `tests/test_graphrag_pipeline.py` | GraphRAG Test Suite | Tests GraphRAG pipeline stages and synthesis oracles. | Verifies retrieval and synthesis. |
| `exports/lta_knowledge_graph.json` | LTA Knowledge Graph Export | Complete serialized graph for LTA. | Source dataset. |
| `exports/ivig_knowledge_graph.json` | IVIG Knowledge Graph Export | Complete serialized graph for IVIG. | Source dataset. |
| `verify_all.py` | Root Verification Runner | System-wide verification script. | Test execution script. |
| `package.json` | Root Package Manifest | Workspace root package configuration. | Workspace configuration. |
| `package-lock.json` | Root Dependency Lockfile | Workspace dependency lockfile. | Dependency lockfile. |
| `visualization.md` | Halftone Visualizer Specification | Visualizer aesthetic and rendering architecture. | Architectural design reference. |
| `bad_understanding.md` | Anti-Patterns Document | Common pitfalls and incorrect assumptions. | Design guidelines. |
| `basic_corrections.md` | Corrections Register | Historical record of model corrections. | Reference documentation. |
| `data_extraction_meta.md` | Extraction Metadata | Lineage metadata for extraction tiers. | Data extraction reference. |
| `data_source.md` | External Data Sources Catalog | Overview of primary government datasources. | Datasource catalog. |
| `dataflow.md` | Dataflow Architecture | Pipeline dataflow diagrams. | Dataflow documentation. |
| `datasource_schema.md` | Ingestion Schemas | Schema documentation for raw data. | Schema documentation. |
| `example_output.md` | Example System Outputs | Sample terminal logs and payloads. | Reference output samples. |
| `required_edits.md` | Required Edits Register | Register of required system modifications. | Historical edit log. |
| `agentresearch_enhancement.md` | Research Architecture | Research agents and statutory discovery. | Subsystem documentation. |

---

## 3. Candidate External Datasource & Schema Audit Register

Every external government datasource, portal endpoint, and Neo4j database interface mandated by `functional_specification_007.md` and related decision tickets was probed using active, safe read-only reconnaissance tools (`curl`, Python inspection scripts, and MCP tool calls). Authentic ground-truth response payloads and headers were captured directly into `assets/20261013T172426-897-pj8g/`.

### 3.1. Neo4j Knowledge Graph Instance (`bolt://localhost:7687`)
- **Role in Specification:** Storage engine housing the 14 entity types and active graph lineages for targeted GraphRAG queries.
- **Reachability & Status:** Verified active. Total nodes: 3,971; Total directed relationships: 7,795.
- **Empirical Schema Audited:**
  - `PolicyNode` labels (14 entity types): `Bill` (4), `ChangeRequest` (2), `CoveragePolicy` (2), `FeeScheduleEntry` (3,816), `HCPCSCode` (70), `ICD10Code` (10), `Jurisdiction` (4), `LiteratureStudy` (2), `LobbyingFiling` (2), `Policy` (2), `PublicLaw` (1), `Regulation` (2), `State` (53), `StatutorySection` (2).
  - Relationships: `ALLOWS_DIAGNOSIS` (10), `APPLIES_TO` (3,816), `APPLIES_TO_JURISDICTION` (4), `COVERS_STATE` (53), `ENACTED_AS` (3), `GOVERNS` (70), `HAS_ADVOCACY_RECORD` (2), `HAS_FEE_SCHEDULE` (3,816), `IMPLEMENTED_BY` (2), `ISSUES_TRANSMITTAL` (2), `MANDATES_POLICY` (2), `MODIFIES_CODE` (2), `SUPPORTED_BY_EVIDENCE` (2), `TARGETS_BILL` (4).
- **Target Entity `PLAW-117-328` Audit:**
  - Properties: `primary_key: "PLAW-117-328"`, `congress: 117`, `number: 328`, `title: "Consolidated Appropriations Act, 2023"`, `enacted_date: "2022-12-29"`.
  - Outgoing Edges: `MODIFIES_CODE` $\rightarrow$ `USC-42-1395x-s-2-Z`, `USC-42-1395x-s-2-JJ`.
  - Incoming Edges: `BILL-117-hr-2617` $\xrightarrow{\text{ENACTED\_AS}}$ `PLAW-117-328`, `BILL-117-hr-3630` $\xrightarrow{\text{ENACTED\_AS}}$ `PLAW-117-328`, `BILL-117-hr-3808` $\xrightarrow{\text{ENACTED\_AS}}$ `PLAW-117-328`.
- **Saved Ground-Truth Payloads:**
  - `assets/20261013T172426-897-pj8g/neo4j_summary_statistics.json`
  - `assets/20261013T172426-897-pj8g/neo4j_node_labels_and_counts.json`
  - `assets/20261013T172426-897-pj8g/neo4j_relationship_types_and_counts.json`
  - `assets/20261013T172426-897-pj8g/neo4j_sample_nodes_14_types.json`
  - `assets/20261013T172426-897-pj8g/neo4j_plaw_117_328_details.json`

### 3.2. Public Law Authority — GPO GovInfo Public Law Details
- **Endpoint:** `https://www.govinfo.gov/app/details/PLAW-117publ328`
- **Role in Specification:** External provenance source for Public Law nodes (`PLAW-117-328`).
- **Observed Headers & Schema:** HTTP/2 200 OK, `content-type: text/html;charset=UTF-8`. Title: "Consolidated Appropriations Act, 2023".
- **Saved Ground-Truth Payloads:**
  - `assets/20261013T172426-897-pj8g/govinfo_plaw_117publ328_headers.txt`
  - `assets/20261013T172426-897-pj8g/public_law_govinfo_plaw117publ328_details.html`

### 3.3. Federal Bill Information — Congress.gov
- **Endpoint:** `https://www.congress.gov/bill/117th-congress/house-bill/3630`
- **Role in Specification:** External source for Federal Bill nodes (`BILL-117-hr-3630`).
- **Observed Headers & Schema:** HTTP/2 200 OK.
- **Saved Ground-Truth Payloads:**
  - `assets/20261013T172426-897-pj8g/bill_congress_gov_hr3630_probe.txt`

### 3.4. Administrative Rules — Federal Register API v1
- **Endpoint:** `https://www.federalregister.gov/api/v1/documents/2023-24455.json`
- **Role in Specification:** REST API providing metadata, title, and citation for Regulation nodes (`FR-2023-24455`).
- **Observed Headers & Schema:** HTTP/2 200 OK, `application/json`. Observed keys: `title` ("Medicare Program; Calendar Year 2024 Payment Policies..."), `citation` ("88 FR 77676"), `regulation_id_number` ("0938-AV07"), `publication_date` ("2023-11-15").
- **Saved Ground-Truth Payloads:**
  - `assets/20261013T172426-897-pj8g/federal_register_rule_2023_24455.json`

### 3.5. Coverage Policies — CMS Medicare Coverage Database (MCD)
- **Endpoint:** `https://www.cms.gov/medicare-coverage-database/search-results.aspx?keyword=A59508`
- **Role in Specification:** External search interface for CoveragePolicy nodes (`CMS-MCD-A59508`).
- **Observed Headers & Schema:** HTTP/2 200 OK, `text/html; charset=utf-8`.
- **Saved Ground-Truth Payloads:**
  - `assets/20261013T172426-897-pj8g/cms_mcd_search_results_a59508.html`

### 3.6. Operational Directives — CMS Transmittals & Change Requests
- **Endpoint:** `https://www.cms.gov/medicare/regulations-guidance/transmittals/2024-transmittals`
- **Role in Specification:** External repository for ChangeRequest nodes (`CMS-CR-13286`, `CMS-CR-13217`).
- **Observed Headers & Schema:** HTTP/2 200 OK, `text/html; charset=utf-8`.
- **Saved Ground-Truth Payloads:**
  - `assets/20261013T172426-897-pj8g/cms_transmittals_headers.txt`
  - `assets/20261013T172426-897-pj8g/change_request_cms_transmittals_2024.html`

### 3.7. Regional Medicare Administrative Contractors (Noridian & CGS)
- **Endpoints:**
  - CGS (Jurisdiction B): `https://www.cgsmedicare.com/jb/`
  - Noridian (Jurisdiction A): `https://med.noridianmedicare.com/web/jadme`
- **Role in Specification:** External portals for Jurisdiction nodes (`JURIS-DME-B`, `JURIS-DME-A`).
- **Observed Headers & Schema:** HTTP/1.1 200 OK and HTTP/2 200 OK.
- **Saved Ground-Truth Payloads:**
  - `assets/20261013T172426-897-pj8g/cgs_dme_headers.txt`
  - `assets/20261013T172426-897-pj8g/noridian_dme_headers.txt`

### 3.8. Clinical & Procedure Code Vocabularies — NLM Clinical Tables APIs
- **Endpoints:**
  - ICD-10 Search: `https://clinicaltables.nlm.nih.gov/api/icd10cm/v3/search?terms=I97.2`
  - HCPCS Search: `https://clinicaltables.nlm.nih.gov/api/hcpcs/v3/search?terms=A6522`
- **Role in Specification:** External authoritative lexical search for clinical indication (`ICD10Code`) and procedure (`HCPCSCode`) nodes.
- **Observed Headers & Schema:** HTTP/2 200 OK, JSON array: `[total_count, [code_array], null, [[code, description], ...]]`.
- **Saved Ground-Truth Payloads:**
  - `assets/20261013T172426-897-pj8g/nlm_icd10cm_search_i972.json`
  - `assets/20261013T172426-897-pj8g/nlm_hcpcs_search_a6522.json`

### 3.9. Statutory Codification — Cornell LII 42 U.S.C. 1395x
- **Endpoint:** `https://www.law.cornell.edu/uscode/text/42/1395x`
- **Role in Specification:** External statutory codification for StatutorySection nodes (`USC-42-1395x-s-2-JJ`).
- **Observed Headers & Schema:** HTTP/2 200 OK.
- **Saved Ground-Truth Payloads:**
  - `assets/20261013T172426-897-pj8g/cornell_lii_usc_42_1395x_headers.txt`

### 3.10. Lobbying Disclosures — Senate LDA Electronic Filings
- **Endpoint:** `https://lda.senate.gov/filings/public/filing/c8697fc5-7f3b-4861-8a49-d9e6357ad287/text/`
- **Role in Specification:** External provenance for LobbyingFiling nodes (`LDA-c8697fc5-7f3b-4861-8a49-d9e6357ad287`).
- **Observed Headers & Schema:** HTTP/2 200 OK.
- **Saved Ground-Truth Payloads:**
  - `assets/20261013T172426-897-pj8g/senate_lda_headers.txt`

---

## 4. Explicit Deficiency Register

In strict compliance with `INV-ABSENCE-01`, this register details every specced requirement in `functional_specification_007.md` that cannot be satisfied by current codebase components without modifications. No components or endpoints have been invented:

| Deficiency ID | Affected Subsystem & Files | Observed Codebase State vs. Specced Requirement | Failure Mode & Impact |
|---|---|---|---|
| **DEF-01** | **Node Detail Drawer Action Button**<br>`src/frontend/src/components/NodeDetailDrawer.tsx#L244-L265` | Current button click handler is strictly passive: `onClick={() => setIsChatOpen(true)}`. Discards `selectedNode.primary_key`, does not construct inquiry text, does not append user message, and does not dispatch request. | The user is left with an empty input box; clicking "Inquire" fails to execute any inquiry. |
| **DEF-02** | **Inter-Component Inquiry Bus**<br>`src/frontend/src/context/GraphSyncContext.tsx#L8-L27` | `GraphSyncContext` does not expose an action or state for triggering an inquiry from `NodeDetailDrawer` into `AgentChatDrawer`, nor does it share a global `isQueryLoading` flag to disable the button during active queries. | Clicking the button cannot submit inquiries or display loading states across components. |
| **DEF-03** | **Contextual Prompt Generation by Classification**<br>`src/frontend/src/components/NodeDetailDrawer.tsx` | No prompt construction logic exists to format inquiries according to Section 4.2 entity classification rules (e.g. `PublicLaw`: *"Explain the statutory authority and enacted healthcare provisions of [primary_key] (name)."*). | Inquiries cannot be contextually framed with entity name and bracketed primary key. |
| **DEF-04** | **API Contract Omission of Pre-Resolved Anchor**<br>`src/api/models.py#L58-L63`<br>`src/graphrag/models.py#L58-L63` | `GraphRAGQueryRequest` model only declares `query`, `model_id`, and `state_code`. It lacks an explicit `primary_key` (or `anchor_pk`) parameter as mandated by Section 4.3. | Frontend cannot transmit the verified primary key to the backend, forcing reliance on raw text parsing. |
| **DEF-05** | **Linker Keyword Guessing Failure & Regex Flaw**<br>`src/graphrag/entity_linker.py#L58, L328-L341` | 1. `GEO_LOCATION_INDICATORS` regex lacks leading word boundary: `(?:from|in|...)` matches the substring `"in "` in `"Explain "`. Candidate `"the statutory authority"` fails state lookup, throwing unhandled `EntityResolutionError`.<br>2. Text parser lacks lexical mapping for entity titles (e.g. *"Consolidated Appropriations Act, 2023"*), returning 0 anchors. | Inquiring about `PLAW-117-328` either throws fatal `EntityResolutionError` or returns 0 illuminated nodes. |
| **DEF-06** | **Pipeline Pre-Resolved Anchor Bypass Missing**<br>`src/graphrag/pipeline.py#L35-L50` | `GraphRAGPipeline.execute_query` unconditionally invokes `linker.resolve_anchors(request.query, session)`. It does not support receiving a pre-resolved `primary_key` anchor to bypass keyword guessing as mandated by Section 4.3. | Explicit anchor contract cannot be fulfilled at the pipeline level. |
| **DEF-07** | **Relationship Deserialization Collapse in Single-Entity Traversal**<br>`src/graphrag/traversal.py#L278-L296, L650-L678` | In `_execute_single_general_traversal`, `session.run(...).data()` returns relationships as 3-element tuples `(start_node, rel_type, end_node)`. `hasattr(r, "start_node")` returns `False`, causing `_convert_edge` to default `src` and `tgt` to `"UNKNOWN"`. All edges collapse into `'UNKNOWN->RELATED_TO->UNKNOWN'`. | Active edge keys are completely lost; canvas fails to illuminate traversed connecting struts for single-node inquiries. |
| **DEF-08** | **Omission of Legislative & Contextual Entities in Context Assembler**<br>`src/graphrag/context_assembler.py#L24-L58` | `GraphContextAssembler.assemble_context` omits `Bill` entities (such as `BILL-117-hr-2617`, `BILL-117-hr-3630`, `BILL-117-hr-3808` connected to `PLAW-117-328`), `LobbyingFiling`, and `LiteratureStudy` from Section 1 context. | LLM lacks prompt context regarding connected bills and legislative history. |
| **DEF-09** | **Canvas Viewport Camera Framing Missing for Illuminated Paths**<br>`src/frontend/src/components/AgentChatDrawer.tsx#L78-L80` | `AgentChatDrawer` calls `setIlluminatedPath(data)`, but does not compute or set `focusTarget` to smoothly pan and zoom the canvas viewport to center the illuminated subgraph. | Canvas fails to frame the illuminated path in the visualizer viewport as required by Section 4.4. |
| **DEF-10** | **In-Flight Query Prevention & Successive Inquiries Handling**<br>`src/frontend/src/components/NodeDetailDrawer.tsx` | Lacks disabled/loading state during in-flight queries (Section 5.1). Lacks state management to handle successive clicks on different nodes as distinct conversation turns without race conditions (Section 5.2). | Rapid duplicate clicks cause duplicate requests; successive node inquiries can collide. |

---

## 5. Sufficiency & Scan Certification

In accordance with [`LANGUAGE.md`](LANGUAGE.md) and `INV-SCAN-01`:
- **Exhaustive Enumeration:** The dependency cone covering the visualizer canvas, node detail drawer, agent chat drawer, synchronization bus, REST API routes, pipeline orchestrator, entity linker, traversal engine, context assembler, domain models, and storage layer has been exhaustively scanned down to leaf utilities and database entities.
- **Empirical Grounding:** Every candidate external datasource, government endpoint, and database query has been actively verified with reachable live responses, observed headers, and raw captured payloads saved into `assets/20261013T172426-897-pj8g/`.
- **Zero Invention:** All missing capabilities are recorded in the Explicit Deficiency Register without proposing or inventing application components.
- **Condition `{sufficient}`:** The scan and reconnaissance register provides complete, unambiguous context for planning downstream test plans and implementations without speculative assumptions.

---

## 6. Handoff Manifest Affirmation

In strict compliance with `INV-MANIFEST-OVERWRITE-01`:
- The handoff manifest file at `handoff/20261013T172426-897-pj8g/plan-scan-2.txt` has been atomically created/overwritten.
- It contains exclusively repository-relative filepaths of all identified and reviewed codebase component files, this authored scan report, and all saved ground-truth payload files in `assets/20261013T172426-897-pj8g/`.
- Predecessor manifests (`handoff/authored.txt`) and other run directories remain fully intact.

---

## 7. Coding Gate Affirmation

**DO NOT CODE YET:** Implementation coding gate remains locked. Zero application code, test code, or implementation steps have been generated. Coding waits on an empty frontier and explicit operator authorization.
