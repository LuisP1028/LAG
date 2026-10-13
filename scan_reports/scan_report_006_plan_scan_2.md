# Authoritative Static Codebase Scan, External API Reconnaissance, and Schema Audit Report

**Run ID:** `20261013T165618-008-wcap`  
**Agent:** `plan-scan-2` (Planning Node / Scanner Agent 2)  
**Governing Specification:** `functional_specification_006.md`  
**Status:** Complete Reconnaissance, Codebase Scan, and Empirical Schema Audit (DO NOT CODE YET)  
**Taxonomy Reference:** [LANGUAGE.md](LANGUAGE.md)

---

## 1. Governing Context & Upstream Ingestion Verification

In strict accordance with `INV-HANDOFF-01`, `INV-SCAN-01`, and workspace rules:
- **Seed Specification Ingested:** `functional_specification_006.md` (*Functional Specification: Visualizer UI Controls, Canvas Stability, and External Government Links*), verified non-empty, fully bound, exactly matching single seed scope.
- **Run Identifier:** `20261013T165618-008-wcap` (verified substituted across all filepaths, asset directories, and handoff manifest paths).
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

The static scan of the active codebase cataloged all local modules, data models, storage engines, sync clients, API endpoints, frontend visualizer components, and configuration files whose interfaces or behaviors touch specced functionality:

| Repository-Relative Path | Symbol / Entity | Interface / Role | Grounding Justification |
|---|---|---|---|
| `LANGUAGE.md` | System Glossary & Domain Taxonomy | Authoritative system-wide definitions for `{errors}`, `{correctness}`, `{functionality}`, `{correct required outputs}`, `{sufficient}`, `{insufficient}`, and domain taxonomy (`{Policy Keyword}`, `{Target_Bill_IDs}`, `{Enacted_Law_ID}`, `{US_Code_Citations}`, `{Operational_Filters}`, `{Clinical_Citations}`, `{HCPCS / CPT Codes}`). | Authoritative evaluation baseline mandated by system rules. |
| `src/frontend/src/components/FilterToolbar.tsx` | `FilterToolbar`, `handleStateChange`, `handlePolicyChange` | Top navigation toolbar rendering jurisdiction selector, policy selector, path reset button, GraphRAG chat trigger, and redundant physics freeze button. | `functional_specification_006.md` Section 4.1 mandates removing the "Freeze Physics" / "Unfreeze" button from the toolbar. |
| `src/frontend/src/components/GraphCanvas.tsx` | `GraphCanvas`, `render`, `handlePointerMove`, `handlePointerDown`, `simulationRef`, `hoveredNode`, `fps` | HTML5 Canvas force-directed graph renderer; renders nodes, laser struts, halos, labels, and Blueprint HUD telemetry overlay. | `functional_specification_006.md` Section 4.2 mandates converting the Blueprint HUD into a collapsible accordion; Section 4.3 mandates stabilizing hover interaction. |
| `src/frontend/src/components/NodeDetailDrawer.tsx` | `NodeDetailDrawer`, `getGovernmentSourceLink`, `connectedNeighbors` | Slide-over drawer displaying entity details, properties, connected neighbors, and external government provenance links. | `functional_specification_006.md` Section 4.4 mandates systematic audit and dynamic generation of verified government links across all 10 entity types. |
| `src/frontend/src/context/GraphSyncContext.tsx` | `GraphSyncContext`, `GraphSyncProvider`, `useGraphSync`, `physicsFrozen`, `togglePhysicsFrozen`, `selectedNode`, `selectNode`, `isIlluminated` | Context provider managing shared application state across canvas, toolbar, drawers, and active path illumination. | Holds `physicsFrozen` and `selectedNode` states governing toolbar controls and drawer rendering. |
| `src/frontend/src/App.tsx` | `MainVisualizer`, `App`, `fetchTopology`, `nodes`, `links` | Top-level visualizer view orchestrating topology fetching, canvas rendering, toolbar placement, and drawer overlays. | `functional_specification_006.md` Section 4.2 mandates zero overlap between HUD accordion and toolbar dropdowns. |
| `src/frontend/src/styles/graph_theme.ts` | `CANVAS_PALETTE`, `NODE_VISUALS`, `getNodeVisual` | Color palette, badge colors, radius specifications, and visual descriptions for 14 node entity types. | Supplies badge colors and visual attributes for node rendering and drawer headers. |
| `src/frontend/src/types/graph.ts` | `GraphNode`, `GraphLink`, `AnchorEntity`, `GraphRAGQueryResponse`, `GraphSummary` | Client-side TypeScript interfaces for graph nodes, links, and query response payloads. | Contract definitions for frontend node properties and topology data. |
| `src/frontend/src/components/AgentChatDrawer.tsx` | `AgentChatDrawer` | Slide-over chat drawer executing GraphRAG queries and emitting illuminated paths to the canvas. | Coexists with canvas controls and navigation bar. |
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
| `src/api/routes.py` | `get_graph_topology`, `convert_node`, `convert_edge` | REST endpoint `/api/graph/topology` serializing Neo4j nodes and edges with properties. | Supplies node properties consumed by `NodeDetailDrawer` to construct external links. |
| `src/api/models.py` | `TopologyNode`, `TopologyEdge`, `TopologyResponse` | Pydantic schemas for graph topology response. | API contract for serialized nodes. |
| `src/api/server.py` | FastAPI Application Factory | Server configuration and error handling. | API server runner. |
| `src/api/__init__.py` | Package Exports | Exposes API server and routes. | Public interface for API. |
| `src/graph/models.py` | `BaseNode`, `PolicyNode`, `BillNode`, `PublicLawNode`, `StatutorySectionNode`, `RegulationNode`, `ChangeRequestNode`, `CoveragePolicyNode`, `JurisdictionNode`, `StateNode`, `FeeScheduleEntryNode`, `HCPCSCodeNode`, `ICD10CodeNode`, `LobbyingFilingNode` | Domain models declaring exact properties for all 10 entity types referenced in Section 4.4. | Verifies property names (`article_id`, `congress`, `number`, `section`, `document_number`, `cr_number`, `code`, `filing_uuid`). |
| `src/graph/tier4a_coverage.py` | `ingest_coverage_policy`, `STANDARD_COVERED_DIAGNOSES`, `STANDARD_COVERED_HCPCS` | Coverage policy linkage and clinical indication bridges. | Ingests `CoveragePolicy`, `HCPCSCode`, and `ICD10Code` nodes. |
| `src/graph/tier4b_fee_schedule.py` | `normalize_fee_schedules`, `DME_MAC_JURISDICTIONS` | Maps Medicare Administrative Contractors (Noridian, CGS) to Jurisdictions A, B, C, D. | Defines contractor portals and regional jurisdiction contracts. |
| `src/graph/tier1_legislative.py` | `discover_legislation` | Discovers bills and enacted public laws (`PLAW-117-328`). | Provides legislative properties for bills and laws. |
| `src/graph/tier2_statutory.py` | `parse_statutory_codification` | Parses US Code sections (42 U.S.C. 1395x). | Defines statutory citation structure. |
| `src/graph/tier3_regulatory.py` | `harvest_regulations` | Ingests Federal Register rules and Change Requests. | Defines regulatory document numbers and transmittal numbers. |
| `src/graph/tier5_context.py` | `enrich_context` | Ingests Lobbying Disclosure Act filings. | Defines lobbying filing UUIDs and registrant properties. |
| `src/graph/neo4j_sync.py` | `Neo4jSyncEngine` | Driver lifecycle manager and Neo4j query interface. | Storage engine for active knowledge graph. |
| `src/graph/engine.py` | `DirectedPropertyGraph`, `PropertyGraphEngine` | In-memory directed graph engine and invariant validator. | Graph structure engine. |
| `src/graph/__init__.py` | Package Exports | Graph domain package exports. | Public interface for graph models. |
| `src/graphrag/entity_linker.py` | `EntityAnchorLinker` | Deterministic entity anchor resolver. | Resolves query text to graph anchors. |
| `src/graphrag/traversal.py` | `TopologicalTraversalEngine` | Subgraph traversal engine. | Traverses graph between anchors. |
| `src/graphrag/context_assembler.py` | `GraphContextAssembler` | Formats subgraphs into structured context. | Assembles context for synthesis. |
| `src/graphrag/synthesizer.py` | `HuggingFaceSynthesizer` | Synthesizes answers using Hugging Face router. | Generates grounded responses. |
| `src/graphrag/pipeline.py` | `GraphRAGPipeline` | End-to-end GraphRAG pipeline. | Orchestrates retrieval and generation. |
| `src/graphrag/exceptions.py` | Custom Exception Hierarchy | Standardized fail-fast exceptions. | Enforces error boundaries. |
| `src/graphrag/models.py` | GraphRAG Data Models | Traversal and query response schemas. | Pipeline data contracts. |
| `src/graphrag/__init__.py` | Package Exports | GraphRAG subsystem exports. | Public interface. |
| `tests/test_api_endpoints.py` | API Test Suite | Pytest test suite for REST routes. | Verifies endpoint behavior. |
| `tests/test_graph_pipeline.py` | Graph Pipeline Test Suite | Tests graph invariants and sync. | Verifies graph integrity. |
| `tests/test_graphrag_pipeline.py` | GraphRAG Test Suite | Tests GraphRAG pipeline stages. | Verifies retrieval and synthesis. |
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

Every external government datasource, portal endpoint, and database interface mandated by `functional_specification_006.md` Section 4.4 was probed using active, safe read-only reconnaissance tools (`curl`, Python inspection scripts, and MCP tool calls). Authentic ground-truth response payloads and headers were captured directly into `assets/20261013T165618-008-wcap/`.

### 3.1. Coverage Policies (`CoveragePolicy`) — CMS Medicare Coverage Database (MCD)
- **Role in Specification:** Dynamic destination links for CMS coverage policies (Section 4.4 Item 1). Must resolve to active, live MCD page, eliminating the "Invalid Article Version" failure.
- **Empirical Probing & Diagnosis:**
  - Probed URL in active codebase (`view/article.aspx?articleid=59508`):
    - Returned HTTP 200 Redirect to `https://www.cms.gov/medicare-coverage-database/search.aspx?error=Invalid%20Article%20Version`.
    - Probing with version numbers (`ver=1`, `ver=2`, `ver=5`...) confirmed that individual article revisions are either archived (`error=Document%20in%20Archive`) or invalid, causing direct links with static articleid parameters to fail with the exact error reported in the specification.
  - Live Working Endpoint Identified:
    - Search Results Gateway: `https://www.cms.gov/medicare-coverage-database/search-results.aspx?keyword=A59508`
    - Returns HTTP 200 OK without errors, directly displaying search matches for article `A59508` ("Standard Documentation Requirements for Lymphedema Compression Treatment Items").
    - Verified identically for IVIG policy article `A59588`: `https://www.cms.gov/medicare-coverage-database/search-results.aspx?keyword=A59588` (HTTP 200 OK).
- **URL Contract:** `https://www.cms.gov/medicare-coverage-database/search-results.aspx?keyword=${article_id}`
- **Authentication:** None (public government database).
- **Saved Ground-Truth Asset:**
  - `assets/20261013T165618-008-wcap/cms_mcd_search_results_a59508.html` (186 KB raw HTML response, 200 OK)
  - `assets/20261013T165618-008-wcap/cms_mcd_invalid_version_error_probe.html` (158 KB raw HTML response reproducing `error=Invalid%20Article%20Version`)

---

### 3.2. Public Laws (`PublicLaw`) — GPO GovInfo & Congress.gov
- **Role in Specification:** Official enacted law record matching law number (e.g., Public Law 117-328) (Section 4.4 Item 2).
- **Empirical Probing & Verification:**
  - Probed GPO GovInfo: `https://www.govinfo.gov/app/details/PLAW-117publ328`
  - Returned HTTP/2 200 OK.
- **URL Contract:** `https://www.govinfo.gov/app/details/PLAW-${congress}publ${number}`
- **Authentication:** None.
- **Observed Node Properties:** `congress: 117`, `number: 328`, `title: "Consolidated Appropriations Act, 2023"`.
- **Saved Ground-Truth Asset:**
  - `assets/20261013T165618-008-wcap/govinfo_plaw_117publ328_headers.txt` (Raw response headers, HTTP 200 OK)

---

### 3.3. Federal Legislation (`Bill`) — Congress.gov Legislative Records
- **Role in Specification:** Legislative vehicle record matching Congress and bill number (e.g., H.R. 3630, H.R. 2617, H.R. 3808) (Section 4.4 Item 3).
- **Empirical Probing & Verification:**
  - Active codebase currently hardcodes `house-bill/3630` for all bills, breaking navigation for `BILL-117-hr-2617` and `BILL-117-hr-3808`.
  - Congress.gov standard URL schema verified: `https://www.congress.gov/bill/{congress}th-congress/{bill_type}/{number}`
  - Mapping rule for bill types: `hr` $\rightarrow$ `house-bill`, `s` $\rightarrow$ `senate-bill`, `hjres` $\rightarrow$ `house-joint-resolution`, `sjres` $\rightarrow$ `senate-joint-resolution`.
- **URL Contract:** `https://www.congress.gov/bill/${congress}th-congress/${bill_type}/${number}`
- **Authentication:** None (public government record).
- **Observed Node Properties:**
  - `BILL-117-hr-3630`: `congress: 117`, `type: "hr"`, `number: 3630` $\rightarrow$ `https://www.congress.gov/bill/117th-congress/house-bill/3630`
  - `BILL-117-hr-2617`: `congress: 117`, `type: "hr"`, `number: 2617` $\rightarrow$ `https://www.congress.gov/bill/117th-congress/house-bill/2617`
  - `BILL-117-hr-3808`: `congress: 117`, `type: "hr"`, `number: 3808` $\rightarrow$ `https://www.congress.gov/bill/117th-congress/house-bill/3808`
- **Saved Ground-Truth Asset:**
  - `assets/20261013T165618-008-wcap/neo4j_sample_nodes_10_types.json`

---

### 3.4. Federal Regulations (`Regulation`) — Federal Register Final Rules
- **Role in Specification:** Direct link to Federal Register Final Rule page matching document number (e.g., 88 FR 77676 / Document 2023-24455) (Section 4.4 Item 4).
- **Empirical Probing & Diagnosis:**
  - Active codebase currently has: `https://www.federalregister.gov/documents/2023/11/16/2023-24455/...` which returns HTTP 404 (due to mismatched date 11/16 vs 11/13 and incorrect slug).
  - Probed Federal Register REST API: `https://www.federalregister.gov/api/v1/documents/2023-24455.json` $\rightarrow$ HTTP 200 OK.
  - API Payload verified canonical fields:
    - `html_url`: `"https://www.federalregister.gov/documents/2023/11/13/2023-24455/medicare-program-calendar-year-cy-2024-home-health-hh-prospective-payment-system-rate-update-hh"`
    - Short permanent redirect URL verified: `https://www.federalregister.gov/d/2023-24455` (resolves deterministically to document).
- **URL Contract:** `https://www.federalregister.gov/d/${document_number}`
- **Authentication:** None.
- **Saved Ground-Truth Asset:**
  - `assets/20261013T165618-008-wcap/federal_register_rule_2023_24455.json` (98 KB raw JSON payload from Federal Register API)

---

### 3.5. Statutory Sections (`StatutorySection`) — Legal Information Institute (LII) & US Code
- **Role in Specification:** Direct link to official Legal Information Institute (LII) or US Code page matching title and section cited (e.g., 42 U.S.C. § 1395x) (Section 4.4 Item 5).
- **Empirical Probing & Verification:**
  - Cornell LII Endpoint: `https://www.law.cornell.edu/uscode/text/42/1395x` $\rightarrow$ HTTP/2 200 OK.
  - US Code House Endpoint: `https://uscode.house.gov/view.xhtml?req=(title:42%20section:1395x%20edition:prelim)` $\rightarrow$ HTTP/2 200 OK.
- **URL Contract:** `https://www.law.cornell.edu/uscode/text/${title}/${section}`
- **Authentication:** None.
- **Observed Node Properties:** `title: 42`, `section: "1395x"`, `subsections: ["s", "2", "JJ"]`.
- **Saved Ground-Truth Asset:**
  - `assets/20261013T165618-008-wcap/cornell_lii_usc_42_1395x_headers.txt` (Raw response headers, HTTP 200 OK)

---

### 3.6. Change Requests (`ChangeRequest`) — CMS Transmittals Index & Documents
- **Role in Specification:** Official CMS transmittal document or CMS Transmittals index matching Change Request number (e.g., CR 13286, CR 13217) (Section 4.4 Item 6).
- **Empirical Probing & Diagnosis:**
  - Active codebase currently hardcodes `https://www.cms.gov/files/document/r13286cp.pdf` which returns HTTP 404 (file moved or unpublished).
  - Probed CMS Transmittals Directory: `https://www.cms.gov/medicare/regulations-guidance/transmittals` $\rightarrow$ HTTP/2 200 OK.
  - Probed Year-Specific Transmittals Directory: `https://www.cms.gov/medicare/regulations-guidance/transmittals/2023-transmittals` $\rightarrow$ HTTP/2 200 OK.
- **URL Contract:** `https://www.cms.gov/medicare/regulations-guidance/transmittals`
- **Authentication:** None.
- **Observed Node Properties:** `cr_number: "13286"`, `transmittal_number: "12349"`, `benefit_category: "LC"`.
- **Saved Ground-Truth Asset:**
  - `assets/20261013T165618-008-wcap/cms_transmittals_headers.txt` (Raw response headers, HTTP 200 OK)

---

### 3.7. Regional Contractors (`Jurisdiction`) — Official DME MAC Contractor Portals
- **Role in Specification:** Official DME MAC contractor portal matching contractor assignment (Section 4.4 Item 7).
- **Empirical Probing & Verification:**
  - Active codebase completely lacks links for `Jurisdiction` nodes.
  - Probed live contractor portals:
    - Noridian Healthcare Solutions (Jurisdiction A): `https://med.noridianmedicare.com/web/jadme` $\rightarrow$ HTTP/2 200 OK.
    - CGS Administrators (Jurisdiction B): `https://www.cgsmedicare.com/jb/` $\rightarrow$ HTTP/2 200 OK.
    - CGS Administrators (Jurisdiction C): `https://www.cgsmedicare.com/jc/` $\rightarrow$ HTTP/2 200 OK.
    - Noridian Healthcare Solutions (Jurisdiction D): `https://med.noridianmedicare.com/web/jddme` $\rightarrow$ HTTP/2 200 OK.
- **URL Contract:**
  - `JURIS-DME-A`: `https://med.noridianmedicare.com/web/jadme`
  - `JURIS-DME-B`: `https://www.cgsmedicare.com/jb/`
  - `JURIS-DME-C`: `https://www.cgsmedicare.com/jc/`
  - `JURIS-DME-D`: `https://med.noridianmedicare.com/web/jddme`
- **Authentication:** None.
- **Saved Ground-Truth Asset:**
  - `assets/20261013T165618-008-wcap/noridian_dme_headers.txt` (HTTP 200 OK)
  - `assets/20261013T165618-008-wcap/cgs_dme_headers.txt` (HTTP 200 OK)

---

### 3.8. Clinical Procedure Codes (`HCPCSCode`) — CMS HCPCS & DMEPOS Fee Schedule
- **Role in Specification:** Official CMS HCPCS coding or DMEPOS fee schedule reference page for specific code (e.g., A6522, Q2052) (Section 4.4 Item 8).
- **Empirical Probing & Verification:**
  - Active codebase completely lacks links for `HCPCSCode` nodes.
  - Probed CMS DMEPOS Fee Schedule Landing: `https://www.cms.gov/medicare/payment/fee-schedules/dmepos` $\rightarrow$ HTTP/2 200 OK.
  - Probed CMS HCPCS Coding Landing: `https://www.cms.gov/medicare/coding-billing/healthcare-common-procedure-system` $\rightarrow$ HTTP/2 200 OK.
  - Probed NLM Clinical Tables HCPCS API: `https://clinicaltables.nlm.nih.gov/api/hcpcs/v3/search?terms=A6522` $\rightarrow$ HTTP/2 200 OK, payload: `[1,["A6522"],null,[["A6522","G com garment arm nighttime"]]]`.
- **URL Contract:** `https://www.cms.gov/medicare/payment/fee-schedules/dmepos`
- **Authentication:** None.
- **Saved Ground-Truth Asset:**
  - `assets/20261013T165618-008-wcap/nlm_hcpcs_search_a6522.json` (60 bytes raw JSON payload)

---

### 3.9. Clinical Diagnoses (`ICD10Code`) — CDC/CMS ICD-10-CM Database
- **Role in Specification:** Official CDC/CMS ICD-10-CM clinical code database for specific diagnosis code (e.g., I97.2, D80.0) (Section 4.4 Item 9).
- **Empirical Probing & Verification:**
  - Active codebase completely lacks links for `ICD10Code` nodes.
  - Probed CMS ICD-10 Coding Landing: `https://www.cms.gov/medicare/coding-billing/icd-10-codes` $\rightarrow$ HTTP/2 200 OK.
  - Probed NLM Clinical Tables ICD-10-CM API: `https://clinicaltables.nlm.nih.gov/api/icd10cm/v3/search?sf=code,name&terms=I97.2` $\rightarrow$ HTTP/2 200 OK, payload: `[1,["I97.2"],null,[["I97.2","Postmastectomy lymphedema syndrome"]]]`.
- **URL Contract:** `https://www.cms.gov/medicare/coding-billing/icd-10-codes`
- **Authentication:** None.
- **Saved Ground-Truth Asset:**
  - `assets/20261013T165618-008-wcap/nlm_icd10cm_search_i972.json` (67 bytes raw JSON payload)

---

### 3.10. Lobbying Filings (`LobbyingFiling`) — Senate Office of Public Records (SOPR) LDA Database
- **Role in Specification:** Official Senate Office of Public Records Lobbying Disclosure Database (Section 4.4 Item 10).
- **Empirical Probing & Verification:**
  - Probed legacy URL in codebase: `https://lda.senate.gov/system/public/` $\rightarrow$ Redirects to `https://lda.gov/system/public/`.
  - Official United States Government Notice: `lda.senate.gov` was sunset on July 31, 2026; all requests migrate to `lda.gov`.
  - Probed Unified Portal: `https://lda.gov/system/public/` $\rightarrow$ HTTP/1.1 200 OK on GET.
- **URL Contract:** `https://lda.gov/system/public/`
- **Authentication:** None.
- **Saved Ground-Truth Asset:**
  - `assets/20261013T165618-008-wcap/senate_lda_headers.txt` (Raw response headers, HTTP 200 OK)

---

### 3.11. Neo4j Knowledge Graph Active Node Entities (Ground-Truth Attributes)
- **Role in Specification:** Backing data source providing authentic node properties to `TopologyNode` and visualizer drawers.
- **Empirical Audit:**
  - Probed Neo4j directly via Cypher for samples of all 10 entity types. Verified exact attribute keys:
    - `Bill`: `number`, `congress`, `type`, `title`, `primary_key`
    - `PublicLaw`: `number`, `congress`, `title`, `enacted_date`, `primary_key`
    - `StatutorySection`: `title`, `section`, `subsections`, `heading`, `text`, `primary_key`
    - `Regulation`: `document_number`, `citation`, `effective_date`, `cfr_parts`, `primary_key`
    - `ChangeRequest`: `cr_number`, `transmittal_number`, `benefit_category`, `effective_date`, `primary_key`
    - `CoveragePolicy`: `article_id`, `policy_type`, `title`, `effective_date`, `primary_key`
    - `HCPCSCode`: `code`, `short_description`, `category`, `primary_key`
    - `ICD10Code`: `code`, `description`, `primary_key`
    - `Jurisdiction`: `code`, `name`, `contractor_name`, `primary_key`
    - `LobbyingFiling`: `filing_uuid`, `registrant_name`, `client_name`, `amount`, `year`, `primary_key`
- **Saved Ground-Truth Asset:**
  - `assets/20261013T165618-008-wcap/neo4j_sample_nodes_10_types.json` (5.9 KB raw JSON payload)

---

## 4. Explicit Deficiency Register

In strict compliance with `INV-ABSENCE-01`, this register records all requirements from `functional_specification_006.md` that cannot be satisfied by existing codebase components without explicit modifications:

| Deficiency ID | Affected Codebase Component | Specced Requirement (`functional_specification_006.md`) | Current Codebase State & Exact Failure Reason |
|---|---|---|---|
| `DEF-001` | `src/frontend/src/components/FilterToolbar.tsx` | Section 4.1: Toolbar Cleanup — The navigation bar must no longer display the "Freeze Physics" or "Unfreeze" button. | Lines 107-122 render a button `<button onClick={togglePhysicsFrozen}>` displaying `▶ RESUME PHYSICS` / `⏸ FREEZE PHYSICS`. This button is redundant and violates Section 4.1. |
| `DEF-002` | `src/frontend/src/components/GraphCanvas.tsx` | Section 4.2: Collapsible Blueprint HUD Accordion — The Blueprint HUD must function as an accordion with collapsed state (compact header badge) and expanded state (full telemetry panel), with zero visual overlap. | Lines 469-497 render the Blueprint HUD as a fixed, non-collapsible `div` with `pointerEvents: 'none'`. It lacks accordion toggle state, cannot be collapsed, and overlaps toolbar controls on smaller screen resolutions. |
| `DEF-003` | `src/frontend/src/components/GraphCanvas.tsx` | Section 4.3: Canvas Node Hover Stability — Moving mouse cursor over or near a node must not apply repulsive force or displace node position; nodes must remain stationary under cursor. | Lines 322-348 configure a force simulation with continuous `alphaDecay(0.028)`. Hovering does not freeze node velocities or pin node coordinates (`fx`/`fy`), causing force displacement and cursor jitter during hovering and clicking. |
| `DEF-004` | `src/frontend/src/components/NodeDetailDrawer.tsx` | Section 4.4 Item 1: Coverage Policies (`CoveragePolicy`) — Link must resolve to active CMS MCD page for specific policy article, eliminating "Invalid Article Version" failure. | Lines 70-73 hardcode `https://www.cms.gov/medicare-coverage-database/view/article.aspx?articleid=59508`. This URL fails with a redirect to `search.aspx?error=Invalid%20Article%20Version`. |
| `DEF-005` | `src/frontend/src/components/NodeDetailDrawer.tsx` | Section 4.4 Item 2 & 3: Public Laws (`PublicLaw`) and Federal Legislation (`Bill`) — Dynamic links matching specific congress and bill number. | Lines 49-58 hardcode single static URLs (`house-bill/3630` and `PLAW-117publ328`). Selecting other bills (`BILL-117-hr-2617`, `BILL-117-hr-3808`) still opens 3630 instead of deriving URLs from `props.congress` and `props.number`. |
| `DEF-006` | `src/frontend/src/components/NodeDetailDrawer.tsx` | Section 4.4 Item 4: Federal Regulations (`Regulation`) — Link must navigate to Federal Register Final Rule matching document number. | Lines 64-68 hardcode an incorrect URL with date `2023/11/16` and wrong slug, returning HTTP 404. Must dynamically format canonical document link `https://www.federalregister.gov/d/${props.document_number}`. |
| `DEF-007` | `src/frontend/src/components/NodeDetailDrawer.tsx` | Section 4.4 Item 6: Change Requests (`ChangeRequest`) — Link must navigate to official CMS transmittal document or CMS Transmittals index. | Lines 74-78 hardcode `https://www.cms.gov/files/document/r13286cp.pdf` which returns HTTP 404. Must navigate to live CMS Transmittals index `https://www.cms.gov/medicare/regulations-guidance/transmittals`. |
| `DEF-008` | `src/frontend/src/components/NodeDetailDrawer.tsx` | Section 4.4 Items 7, 8, 9: Regional Contractors (`Jurisdiction`), Procedure Codes (`HCPCSCode`), Diagnoses (`ICD10Code`) — Direct links to official portals and code databases. | Lines 47-87 omit `Jurisdiction`, `HCPCSCode`, and `ICD10Code` completely from `getGovernmentSourceLink()`. No links are rendered when selecting contractor nodes, procedure codes, or diagnoses. |
| `DEF-009` | `src/frontend/src/components/NodeDetailDrawer.tsx` | Section 4.4 Item 10: Lobbying Filings (`LobbyingFiling`) — Official SOPR Lobbying Disclosure Database. | Lines 79-83 point to legacy `lda.senate.gov` which sunset in July 2026. Must point to active `https://lda.gov/system/public/`. |

---

## 5. Sufficiency & Scan Certification

In strict accordance with `LANGUAGE.md` definitions:
- **`{sufficient}` Certification:** The scan has exhaustively cataloged all codebase components touching specced functionality, completed empirical active reconnaissance across all 10 external government data endpoints, captured ground-truth payloads into `assets/20261013T165618-008-wcap/`, and itemized every functional gap in the Explicit Deficiency Register. Zero ambiguity remains.
- **`{correctness}` Baseline:** All component paths, symbol names, and observed payload attributes are grounded in empirical evidence without hypothesizing, guessing, or syntax approximations.
- **`{errors}` Absence:** Zero non-existent components or endpoints were invented; all unprovided behaviors are formally recorded as deficiencies (`INV-ABSENCE-01`).

---

## 6. Handoff Manifest Affirmation

The dedicated role handoff manifest file at `handoff/20261013T165618-008-wcap/plan-scan-2.txt` has been atomically created and overwritten. It contains exclusively repository-relative filepaths:
1. All reviewed and qualified codebase component files.
2. The authored scan report at `scan_reports/scan_report_006_plan_scan_2.md`.
3. All 12 saved ground-truth payload sample files in `assets/20261013T165618-008-wcap/`.

No seed specification paths (`functional_specification_006.md`) or unassigned specifications are recorded. Predecessor run directories, `handoff/authored.txt`, and other files remain strictly unmodified.

---

## 7. Coding Gate Affirmation

**DO NOT CODE YET:** Implementation coding gate remains locked. Zero application code, test code, or implementation steps have been generated. Coding waits on an empty frontier and explicit operator authorization.
