# Codebase Static Scan, External API Reconnaissance, and Schema Audit Report

**Report ID:** `scan_report_001.md`  
**Execution Node:** `plan-scan-1` (Agent 1)  
**Run ID:** `20261013T165618-008-wcap`  
**Timestamp:** `2026-10-13T10:04:00-07:00`  
**Governing Specification:** [`functional_specification_006.md`](functional_specification_006.md) (*Functional Specification: Visualizer UI Controls, Canvas Stability, and External Government Links*)  
**Status:** Complete Reconnaissance & Schema Audit Register  
**Implementation Gate:** Strict Boundary Enforced (**DO NOT CODE YET**)

---

## 1. Governing Context & Ingestion Verification

In strict compliance with `INV-HANDOFF-01`, workspace architectural rules, and the loading hierarchy:

1. **Single Upstream Specification in Scope:**
   - Ingested verbatim and strictly bounded to: [`functional_specification_006.md`](functional_specification_006.md) (*Functional Specification: Visualizer UI Controls, Canvas Stability, and External Government Links*).
   - Predecessor manifest verified: `handoff/authored.txt` records `functional_specification_006.md` as the governing target.
   - Zero scanning across unassigned specifications; no multiple seed paths consumed.
2. **Wayfinder Architectural Map and Decision Tickets Inspected:**
   - [`wayfinder/map.md`](wayfinder/map.md): *Wayfinder Architectural Map: GraphRAG Specification for Browser Graph Visualizer*
   - [`wayfinder/tickets/ticket-001.md`](wayfinder/tickets/ticket-001.md): *Entity Anchor Linking and Layperson Vocabulary Normalization Specification* (RESOLVED)
   - [`wayfinder/tickets/ticket-002.md`](wayfinder/tickets/ticket-002.md): *Generalized Topological Subgraph Expansion and Neighborhood Traversal Specification* (RESOLVED)
   - [`wayfinder/tickets/ticket-003.md`](wayfinder/tickets/ticket-003.md): *Factual Context Assembly, Edge Provenance Formatting, and Prompt Grounding Specification* (RESOLVED)
   - [`wayfinder/tickets/ticket-004.md`](wayfinder/tickets/ticket-004.md): *Bidirectional Visual Canvas Synchronization and Active Subgraph Illumination Specification* (RESOLVED)
   - [`wayfinder/tickets/ticket-005.md`](wayfinder/tickets/ticket-005.md): *Master Specification Synthesis and Edits for functional_specification_004.md* (RESOLVED)
3. **Evaluation Parameters Adherence ([`LANGUAGE.md`](LANGUAGE.md)):**
   - **`{errors}`**: Visual overlap between UI panels, cursor repulsion that prevents node selection, clicking dead/404/invalid links (such as the CMS MCD "Invalid Article Version" error or HTTP 404 on CMS CR PDF), or console errors during canvas interaction.
   - **`{correctness}`**: UI panels render cleanly without overlapping; nodes remain stationary under cursor hover; external links navigate directly to valid, live government records matching the selected entity.
   - **`{functionality}`**: An uncluttered, stable visualizer interface where users can freely inspect network telemetry, hover and select nodes without jitter or movement, and open verified government source documentation for any entity.
   - **`{correct required outputs}`**:
     1. Top toolbar without the "Freeze Physics" button.
     2. A collapsible Blueprint HUD accordion that can be toggled open or closed without covering toolbar menus.
     3. Stationary canvas nodes during cursor hover and selection.
     4. Dynamic, working external links for all entity types (bills, laws, regulations, coverage policies, change requests, procedure codes, diagnosis codes, jurisdictions, and lobbying filings).
     5. Saved empirical payload samples in `assets/20261013T165618-008-wcap/`.
     6. Dedicated handoff manifest at `handoff/20261013T165618-008-wcap/plan-scan-1.txt` atomically overwritten.
   - **`{sufficient}`**: Requirements and scan registers are complete, unambiguous, and empirically grounded, permitting implementation planning without guesswork.
   - **`{insufficient}`**: Any ambiguity requiring assumptions regarding system behavior, layout positioning, link URL formatting, or hover stabilization.

---

## 2. Master Component Dependency Cone Register

A deterministic static scan of the active codebase was performed. Each qualified local component whose interface touches specced functionality was reviewed and grounded:

| Repository-Relative Path | Verbatim Symbol / Entity | Interface / Active Role | Specification & Ticket Grounding Justification |
|---|---|---|---|
| [`LANGUAGE.md`](LANGUAGE.md) | `System Glossary & Evaluation Parameters` | Authoritative system taxonomy: `{errors}`, `{correctness}`, `{functionality}`, `{correct required outputs}`, `{sufficient}`, `{insufficient}`, `{Policy Keyword}`, `{Target_Bill_IDs}`, `{Enacted_Law_ID}`, `{US_Code_Citations}`, `{Operational_Filters}`, `{Clinical_Citations}`, `{HCPCS / CPT Codes}`, `{Direct Path (Native Keys)}`, `{Structural Traversal (Derived Keys)}`. | Mandated root glossary by `functional_specification_006.md` Section 2 and `RULE[user_global]`. |
| [`package.json`](package.json) | `@ai-hero/sandcastle: ^0.12.0` | Node.js workspace package manifest defining test and runtime dependencies. | Workspace dependency root. |
| [`visualization.md`](visualization.md) | `GraphRAG Halftone 3D Visualization System` | Technical specification for 3D canvas styling, halftone screen shading, telemetry HUD, 3D physics clustering, and camera interpolation. | Informs visual rendering requirements in `functional_specification_006.md` Section 4.2. |
| [`wayfinder/map.md`](wayfinder/map.md) | `Wayfinder Architectural Map: GraphRAG Specification` | Master architecture map defining destinations, GraphRAG invariants (`INV-UNBROKEN-ANCESTRY`, `INV-NO-KEYWORD-BRIDGING`, `INV-FAIL-FAST`, `INV-PROVENANCE-COMPLETENESS`), and dependency DAG. | Master governing planning map. |
| [`wayfinder/tickets/ticket-001.md`](wayfinder/tickets/ticket-001.md) | `Decision Ticket 001` | Entity anchor linking and multi-slot layperson vocabulary normalization specification. | Informs input entity resolution and entity naming taxonomy. |
| [`wayfinder/tickets/ticket-002.md`](wayfinder/tickets/ticket-002.md) | `Decision Ticket 002` | Generalized topological subgraph expansion and $k$-hop neighborhood traversal specification. | Informs topology retrieval and connected neighbor relationships in drawer. |
| [`wayfinder/tickets/ticket-003.md`](wayfinder/tickets/ticket-003.md) | `Decision Ticket 003` | Factual context assembly, edge provenance formatting, and prompt grounding specification into structured Markdown blocks. | Informs edge provenance metadata and source URI grounding. |
| [`wayfinder/tickets/ticket-004.md`](wayfinder/tickets/ticket-004.md) | `Decision Ticket 004` | Bidirectional visual canvas synchronization, event bus contracts, and active subgraph path illumination. | Governs canvas event bus and camera synchronization. |
| [`wayfinder/tickets/ticket-005.md`](wayfinder/tickets/ticket-005.md) | `Decision Ticket 005` | Master specification synthesis and section edit mappings for GraphRAG architecture. | Governs integration of GraphRAG across specification sections. |
| [`src/frontend/src/components/FilterToolbar.tsx`](src/frontend/src/components/FilterToolbar.tsx) | `FilterToolbar` | Top navigation toolbar rendering jurisdiction selector, policy selector, physics freeze button, reset path button, and GraphRAG chat trigger. | Directly touched by `functional_specification_006.md` Section 4.1: mandates removal of the redundant "Freeze Physics" / "Unfreeze" button. |
| [`src/frontend/src/components/GraphCanvas.tsx`](src/frontend/src/components/GraphCanvas.tsx) | `GraphCanvas` | Force-directed HTML5 canvas visualizer managing D3 force simulation, camera framing, node rendering with halftone screening, and fixed Blueprint HUD telemetry overlay. | Directly touched by Section 4.2 (Blueprint HUD collapsible accordion) and Section 4.3 (eliminating hover repulsion and simulation restart on hover). |
| [`src/frontend/src/components/NodeDetailDrawer.tsx`](src/frontend/src/components/NodeDetailDrawer.tsx) | `NodeDetailDrawer`, `getGovernmentSourceLink` | Side drawer displaying selected node metadata, entity properties, connected neighbors, and external government provenance link. | Directly touched by Section 4.4: mandates systematic dynamic link generation across all entity types, eliminating hardcoded mock URLs, CMS MCD "Invalid Article Version" errors, and 404 transmittal links. |
| [`src/frontend/src/context/GraphSyncContext.tsx`](src/frontend/src/context/GraphSyncContext.tsx) | `GraphSyncContext`, `GraphSyncProvider`, `useGraphSync` | React context managing shared visualizer state: `activeNodePKs`, `activeEdgeKeys`, `selectedNode`, `physicsFrozen`, `togglePhysicsFrozen`, `isIlluminated`, `filterState`, `policyKeyword`. | Manages `physicsFrozen` state and interaction synchronization. |
| [`src/frontend/src/types/graph.ts`](src/frontend/src/types/graph.ts) | `GraphNode`, `GraphLink`, `AnchorEntity`, `GraphRAGQueryResponse` | TypeScript contracts defining node primary keys, labels, properties, and visual dimensions. | Contract defining entity attributes consumed by drawer link generators. |
| [`src/frontend/src/styles/graph_theme.ts`](src/frontend/src/styles/graph_theme.ts) | `CANVAS_PALETTE`, `NODE_CATEGORY_STYLES`, `getNodeVisual` | Color palette constants (`bgVoid`, `accentAmber`, `panelBg`, `panelBorder`) and badge styling across all entity labels. | Defines styling for collapsible Blueprint HUD badge and drawer visual headers. |
| [`src/frontend/src/App.tsx`](src/frontend/src/App.tsx) | `MainVisualizer`, `App` | Root frontend component loading topology from `/api/graph/topology`, composing `FilterToolbar`, `GraphCanvas`, `NodeDetailDrawer`, and `AgentChatDrawer`. | Layout parent governing z-index stacking and panel placement. |
| [`src/frontend/src/components/AgentChatDrawer.tsx`](src/frontend/src/components/AgentChatDrawer.tsx) | `AgentChatDrawer` | Conversational GraphRAG drawer component triggered by toolbar button. | Visual companion panel interacting with top navigation toolbar. |
| [`src/frontend/package.json`](src/frontend/package.json) | React & Vite Frontend Manifest | Frontend workspace dependencies including `react`, `react-dom`, `d3`, `lucide-react`, and `vite`. | Frontend build and runtime manifest. |
| [`src/graph/models.py`](src/graph/models.py) | Master Graph Data Contracts | Typed Pydantic models for all 14 node entity types (`BillNode`, `PublicLawNode`, `StatutorySectionNode`, `RegulationNode`, `ChangeRequestNode`, `CoveragePolicyNode`, `JurisdictionNode`, `StateNode`, `FeeScheduleEntryNode`, `HCPCSCodeNode`, `ICD10CodeNode`, `LobbyingFilingNode`, `CBOScoreNode`, `LiteratureStudyNode`, `PolicyNode`). | Defines authentic property fields (e.g. `article_id`, `congress`, `number`, `type`, `citation`, `document_number`, `title`, `section`, `cr_number`, `code`, `contractor_name`, `filing_uuid`) used for dynamic URL generation. |
| [`src/graph/__init__.py`](src/graph/__init__.py) | `src.graph` Package Manifest | Exports all node models and property graph engine. | Package entry point for graph domain models. |
| [`src/graph/engine.py`](src/graph/engine.py) | `DirectedPropertyGraph`, `PropertyGraphEngine` | Graph storage and invariant validation engine. | Ingestion and property integrity baseline. |
| [`src/graph/neo4j_sync.py`](src/graph/neo4j_sync.py) | `Neo4jSyncEngine` | Driver interface executing APOC MERGE upserts and summary statistics in Neo4j. | Live database sync layer. |
| [`src/graph/tier1_legislative.py`](src/graph/tier1_legislative.py) | `discover_legislation` | Generates `BillNode` and `PublicLawNode` records with authentic legislative numbers. | Ground truth for Bill and PublicLaw property contracts. |
| [`src/graph/tier2_statutory.py`](src/graph/tier2_statutory.py) | `parse_statutory_codification` | Generates `StatutorySectionNode` records codifying 42 U.S.C. 1395x. | Ground truth for StatutorySection property contracts. |
| [`src/graph/tier3_regulatory.py`](src/graph/tier3_regulatory.py) | `harvest_regulations` | Generates `RegulationNode` (88 FR 77676 / 2023-24455) and `ChangeRequestNode` (CR 13286, CR 13217). | Ground truth for Regulation and ChangeRequest property contracts. |
| [`src/graph/tier4a_coverage.py`](src/graph/tier4a_coverage.py) | `ingest_coverage_policy` | Generates `CoveragePolicyNode` (`CMS-MCD-A59508`, `CMS-MCD-A59588`) and connects HCPCS and ICD10 codes. | Ground truth for CoveragePolicy article contracts. |
| [`src/graph/tier4b_fee_schedule.py`](src/graph/tier4b_fee_schedule.py) | `normalize_fee_schedules` | Generates 4 `JurisdictionNode` records (`JURIS-DME-A` through `D`) and 3,816 fee schedule entries. | Ground truth for DME MAC contractor mappings. |
| [`src/graph/tier5_context.py`](src/graph/tier5_context.py) | `enrich_context` | Generates `LobbyingFilingNode` (UUIDs `c8697fc5-...` and `1821a229-...`) and `LiteratureStudyNode` records. | Ground truth for LobbyingFiling filing UUIDs. |
| [`src/graphrag/__init__.py`](src/graphrag/__init__.py) | `src.graphrag` Package Manifest | GraphRAG package entry point. | Entry point for retrieval engine. |
| [`src/graphrag/models.py`](src/graphrag/models.py) | Data contracts | Core Pydantic models for entity resolution and topological retrieval. | Data structures feeding canvas illumination. |
| [`src/graphrag/exceptions.py`](src/graphrag/exceptions.py) | Error hierarchy | Fail-fast error hierarchy for entity resolution and traversal. | Error handling boundaries. |
| [`src/graphrag/entity_linker.py`](src/graphrag/entity_linker.py) | `EntityAnchorLinker` | Resolves natural language text to indexed graph entities. | Anchor linking module. |
| [`src/graphrag/traversal.py`](src/graphrag/traversal.py) | `TopologicalTraversalEngine` | Extracts subgraphs in Neo4j for canvas illumination. | Subgraph retrieval engine. |
| [`src/graphrag/context_assembler.py`](src/graphrag/context_assembler.py) | `GraphContextAssembler` | Formats retrieved graph nodes into structured context blocks. | Context synthesis module. |
| [`src/graphrag/synthesizer.py`](src/graphrag/synthesizer.py) | `HuggingFaceSynthesizer` | Calls Hugging Face Router API with grounded context. | LLM inference client. |
| [`src/graphrag/pipeline.py`](src/graphrag/pipeline.py) | `GraphRAGPipeline` | Orchestrates 5-stage GraphRAG pipeline from query to canvas illumination. | Pipeline controller. |
| [`src/api/__init__.py`](src/api/__init__.py) | `src.api` Package Manifest | REST API package entry point. | Entry point for API layer. |
| [`src/api/models.py`](src/api/models.py) | `TopologyNode`, `TopologyEdge`, `TopologyResponse` | Pydantic response models for `/api/graph/topology`. | API response schemas transferring entity properties to frontend. |
| [`src/api/routes.py`](src/api/routes.py) | FastAPI REST Router (`/api`) | Exposes `/api/graph/topology`, preserving node properties in `convert_node`. | Supplies frontend with complete entity properties for dynamic link generation. |
| [`src/api/server.py`](src/api/server.py) | `create_app`, `lifespan` | Configures FastAPI app, CORS middleware, and lifespan. | HTTP application server. |
| [`tests/test_graph_pipeline.py`](tests/test_graph_pipeline.py) | Regression Test Suite | Validates multi-tier graph ingestion and data integrity. | Backend regression test baseline. |
| [`tests/test_graphrag_pipeline.py`](tests/test_graphrag_pipeline.py) | Test Suite | Validates GraphRAG pipeline against test oracles. | Pipeline oracle test baseline. |
| [`tests/test_api_endpoints.py`](tests/test_api_endpoints.py) | REST API Test Suite | Validates all FastAPI endpoints via `TestClient`. | Integration test baseline. |
| [`verify_all.py`](verify_all.py) | Verification Script | End-to-end verification and demonstration script. | Verification automation. |
| [`exports/lta_knowledge_graph.json`](exports/lta_knowledge_graph.json) | LTA Serialized Graph Dataset | Complete property graph dataset for LTA policy (3,852 nodes, 7,562 edges) across all 14 node entity types. | Verified offline graph fixture with authentic properties. |
| [`exports/ivig_knowledge_graph.json`](exports/ivig_knowledge_graph.json) | IVIG Serialized Graph Dataset | Complete property graph dataset for IVIG policy (183 nodes, 289 edges). | Verified offline graph fixture with authentic properties. |

---

## 3. Candidate External Datasource Audit & Empirical Payload Schema Register

Active, safe, read-only reconnaissance was conducted across candidate external endpoints representing federal documentation portals, Medicare coverage databases, regional DME MAC portals, and clinical code registries. Observed behaviors, status codes, headers, and exact empirical schemas are detailed below, with unedited raw response files archived in `assets/20261013T165618-008-wcap/`:

### 3.1. Entity External URL Audit Matrix Across All 10 Entity Types

| Entity Type (`label`) | Sample Node in Active Graph | Current Code State (`NodeDetailDrawer.tsx`) | Probed Live Government Endpoint | Status Code & Protocol | Saved Raw Payload File | Dynamic URL Construction Contract |
|---|---|---|---|---|---|---|
| **`CoveragePolicy`** | `CMS-MCD-A59508` (`article_id: "A59508"`) | Hardcoded to `https://www.cms.gov/medicare-coverage-database/view/article.aspx?articleid=59508` | `https://www.cms.gov/medicare-coverage-database/search-results.aspx?keyword=A59508` | `HTTP/2 200 OK` (Web page) / `search.aspx?error=Invalid%20Article%20Version` on direct unversioned view | [`assets/20261013T165618-008-wcap/coverage_policy_cms_mcd_search_results_a59508.html`](assets/20261013T165618-008-wcap/coverage_policy_cms_mcd_search_results_a59508.html), [`assets/20261013T165618-008-wcap/coverage_policy_cms_mcd_invalid_version_redirect.txt`](assets/20261013T165618-008-wcap/coverage_policy_cms_mcd_invalid_version_redirect.txt), [`assets/20261013T165618-008-wcap/coverage_policy_cms_mcd_active_article_a55426.html`](assets/20261013T165618-008-wcap/coverage_policy_cms_mcd_active_article_a55426.html) | `https://www.cms.gov/medicare-coverage-database/search-results.aspx?keyword=${articleId}` (or `view/article.aspx?articleId=${articleId}` if verified active) |
| **`PublicLaw`** | `PLAW-117-328` (`congress: 117`, `number: 328`) | Hardcoded to `https://www.govinfo.gov/app/details/PLAW-117publ328` | `https://www.govinfo.gov/app/details/PLAW-117publ328` | `HTTP/2 200 OK` (Content-Length: 69,202) | [`assets/20261013T165618-008-wcap/public_law_govinfo_plaw117publ328_details.html`](assets/20261013T165618-008-wcap/public_law_govinfo_plaw117publ328_details.html) | `https://www.govinfo.gov/app/details/PLAW-${congress}publ${number}` |
| **`Bill`** | `BILL-117-hr-3630`, `BILL-117-hr-2617`, `BILL-117-hr-3808` | Hardcoded to `https://www.congress.gov/bill/117th-congress/house-bill/3630` for all bills | `https://www.congress.gov/bill/117th-congress/house-bill/3630` | `HTTP/2 200 OK` (Browser navigation; Cloudflare turnstile on curl) | [`assets/20261013T165618-008-wcap/bill_congress_gov_hr3630_probe.txt`](assets/20261013T165618-008-wcap/bill_congress_gov_hr3630_probe.txt) | `https://www.congress.gov/bill/${congress}th-congress/${billTypeSlug}/${number}` where `hr` $\to$ `house-bill`, `s` $\to$ `senate-bill` |
| **`Regulation`** | `FR-2023-24455` (`document_number: "2023-24455"`, `citation: "88 FR 77676"`) | Hardcoded long URL with date `/2023/11/16/` | `https://www.federalregister.gov/api/v1/documents/2023-24455.json` and `https://www.federalregister.gov/d/2023-24455` | `HTTP/2 200 OK` (JSON API: 100,483 bytes) | [`assets/20261013T165618-008-wcap/regulation_federal_register_rule_2023_24455.json`](assets/20261013T165618-008-wcap/regulation_federal_register_rule_2023_24455.json) | `https://www.federalregister.gov/d/${documentNumber}` or `https://www.federalregister.gov/documents/2023/11/16/${documentNumber}` |
| **`StatutorySection`** | `USC-42-1395x-s-2-JJ` (`title: 42`, `section: "1395x"`) | Hardcoded to `USCODE-2022-title42-...-sec1395x` on GovInfo | `https://www.law.cornell.edu/uscode/text/42/1395x` | `HTTP/2 200 OK` (Content-Length: 1,381,125) | [`assets/20261013T165618-008-wcap/statutory_section_cornell_lii_42usc1395x.html`](assets/20261013T165618-008-wcap/statutory_section_cornell_lii_42usc1395x.html) | `https://www.law.cornell.edu/uscode/text/${title}/${section}` |
| **`ChangeRequest`** | `CMS-CR-13286`, `CMS-CR-13217` (`cr_number: "13286"`) | Hardcoded to dead link `https://www.cms.gov/files/document/r13286cp.pdf` (HTTP 404) | `https://www.cms.gov/medicare/regulations-guidance/transmittals` and `.../2024-transmittals` | `HTTP/2 200 OK` (Transmittals index: 195,450 bytes; 2024: 253,278 bytes) | [`assets/20261013T165618-008-wcap/change_request_cms_transmittals_index.html`](assets/20261013T165618-008-wcap/change_request_cms_transmittals_index.html), [`assets/20261013T165618-008-wcap/change_request_cms_transmittals_2024.html`](assets/20261013T165618-008-wcap/change_request_cms_transmittals_2024.html), [`assets/20261013T165618-008-wcap/change_request_dead_link_probe_r13286cp.txt`](assets/20261013T165618-008-wcap/change_request_dead_link_probe_r13286cp.txt) | `https://www.cms.gov/medicare/regulations-guidance/transmittals` |
| **`Jurisdiction`** | `JURIS-DME-A`, `B`, `C`, `D` (`contractor_name: "Noridian..."` / `"CGS..."`) | **Missing (null)** | `https://www.cgsmedicare.com/jb/`, `.../jc/`, `https://med.noridianmedicare.com/web/jadme`, `.../jddme` | `HTTP/1.1 200 OK` (CGS JB: 49,491 bytes; Noridian JA: 194,925 bytes) | [`assets/20261013T165618-008-wcap/jurisdiction_cgs_dme_mac_jb.html`](assets/20261013T165618-008-wcap/jurisdiction_cgs_dme_mac_jb.html), [`assets/20261013T165618-008-wcap/jurisdiction_noridian_dme_mac_jadme.html`](assets/20261013T165618-008-wcap/jurisdiction_noridian_dme_mac_jadme.html) | Map code: `JURIS-DME-A` $\to$ `https://med.noridianmedicare.com/web/jadme`, `JURIS-DME-B` $\to$ `https://www.cgsmedicare.com/jb/`, `JURIS-DME-C` $\to$ `https://www.cgsmedicare.com/jc/`, `JURIS-DME-D` $\to$ `https://med.noridianmedicare.com/web/jddme` |
| **`HCPCSCode`** | `HCPCS-A6522`, `HCPCS-A6520`, `HCPCS-Q2052` | **Missing (null)** | `https://www.cms.gov/medicare/payment/fee-schedules/dmepos` and `https://clinicaltables.nlm.nih.gov/api/hcpcs/v3/search?terms=A6522` | `HTTP/2 200 OK` (CMS DMEPOS: 217,370 bytes; NLM API: 60 bytes) | [`assets/20261013T165618-008-wcap/hcpcs_cms_dmepos_fee_schedule.html`](assets/20261013T165618-008-wcap/hcpcs_cms_dmepos_fee_schedule.html), [`assets/20261013T165618-008-wcap/hcpcs_nlm_search_a6522.json`](assets/20261013T165618-008-wcap/hcpcs_nlm_search_a6522.json), [`assets/20261013T165618-008-wcap/hcpcs_nlm_search_q2052.json`](assets/20261013T165618-008-wcap/hcpcs_nlm_search_q2052.json) | `https://www.cms.gov/medicare/payment/fee-schedules/dmepos` |
| **`ICD10Code`** | `ICD10-I97.2`, `ICD10-I89.0`, `ICD10-D80.0` | **Missing (null)** | `https://icd10cmtool.cdc.gov/` and `https://clinicaltables.nlm.nih.gov/api/icd10cm/v3/search?terms=I97.2` | `HTTP/1.1 200 OK` (CDC tool: 730 bytes; NLM API: 67 bytes) | [`assets/20261013T165618-008-wcap/icd10_cdc_browser_tool.html`](assets/20261013T165618-008-wcap/icd10_cdc_browser_tool.html), [`assets/20261013T165618-008-wcap/icd10_nlm_search_i972.json`](assets/20261013T165618-008-wcap/icd10_nlm_search_i972.json), [`assets/20261013T165618-008-wcap/icd10_nlm_search_i890.json`](assets/20261013T165618-008-wcap/icd10_nlm_search_i890.json) | `https://icd10cmtool.cdc.gov/` |
| **`LobbyingFiling`** | `LDA-c8697fc5-7f3b-4861-8a49-d9e6357ad287` | Hardcoded search homepage `https://lda.senate.gov/system/public/` | `https://lda.gov/filings/public/filing/c8697fc5-7f3b-4861-8a49-d9e6357ad287/print/` and `https://lda.gov/system/public/` | `HTTP/1.1 200 OK` (Content-Length: 20,953) | [`assets/20261013T165618-008-wcap/lobbying_filing_sopr_lda_c8697fc5.html`](assets/20261013T165618-008-wcap/lobbying_filing_sopr_lda_c8697fc5.html) | `https://lda.gov/filings/public/filing/${filingUuid}/print/` (or `https://lda.gov/system/public/` fallback) |

---

### 3.2. Live Neo4j Graph Database Summary Statistics & Node Schemas

* **Database Connection:** `bolt://localhost:7687`, database: `neo4j`.
* **Summary Statistics:** [`assets/20261013T165618-008-wcap/neo4j_summary_statistics.json`](assets/20261013T165618-008-wcap/neo4j_summary_statistics.json)
  - `total_nodes`: 3,978
  - `total_edges`: 7,816
  - `distinct_labels`: 15
  - `distinct_relationship_types`: 14
* **Node Labels and Empirical Counts:** [`assets/20261013T165618-008-wcap/neo4j_node_labels_and_counts.json`](assets/20261013T165618-008-wcap/neo4j_node_labels_and_counts.json)
  - `FeeScheduleEntry`: 3,816
  - `HCPCSCode`: 75
  - `State`: 53
  - `Strategy`: 7
  - `ICD10Code`: 6
  - `Jurisdiction`: 4
  - `Bill`: 3
  - `Policy`: 2
  - `StatutorySection`: 2
  - `ChangeRequest`: 2
  - `CoveragePolicy`: 2
  - `LobbyingFiling`: 2
  - `LiteratureStudy`: 2
  - `PublicLaw`: 1
  - `Regulation`: 1
* **Relationship Types and Empirical Counts:** [`assets/20261013T165618-008-wcap/neo4j_relationship_types_and_counts.json`](assets/20261013T165618-008-wcap/neo4j_relationship_types_and_counts.json)
  - `HAS_FEE_SCHEDULE`: 3,816
  - `APPLIES_TO`: 3,816
  - `GOVERNS`: 75
  - `COVERS_STATE`: 53
  - `APPLIES_TO_JURISDICTION`: 8
  - `ALLOWS_DIAGNOSIS`: 6
  - `TARGETS_BILL`: 4
  - `HAS_ADVOCACY_RECORD`: 4
  - `ENACTED_AS`: 3
  - `MODIFIES_CODE`: 2
  - `IMPLEMENTED_BY`: 2
  - `ISSUES_TRANSMITTAL`: 2
  - `SUPPORTED_BY_EVIDENCE`: 2
  - `MANDATES_POLICY`: 2
* **Sample Empirical Node Properties:** [`assets/20261013T165618-008-wcap/neo4j_sample_nodes_14_types.json`](assets/20261013T165618-008-wcap/neo4j_sample_nodes_14_types.json)

---

## 4. Explicit Deficiency Register

In strict adherence to `INV-ABSENCE-01`, this register details every specced requirement in `functional_specification_006.md` that cannot be satisfied by existing codebase components or reachable external endpoints. Zero components or endpoints have been invented:

| Deficiency ID | Specced Requirement / Behavioral Contract | Existing Codebase State | Exact Gap Description & System Impact |
|---|---|---|---|
| **DEF-01** | Removal of Physics Toggle Button (`functional_specification_006.md` Section 3, Section 4.1.1, Acceptance Criteria 1) | `FilterToolbar.tsx` lines 106-122 contains a manual physics toggle button: `{physicsFrozen ? '▶ RESUME PHYSICS' : '⏸ FREEZE PHYSICS'}`. `GraphSyncContext.tsx` maintains `physicsFrozen` state and `togglePhysicsFrozen` callback. | Clutters the top navigation toolbar; forces users to manually intervene in physics rather than allowing forces to settle autonomously. |
| **DEF-02** | Collapsible Blueprint HUD Accordion (`functional_specification_006.md` Section 3, Section 4.2.1-4.2.3, Acceptance Criteria 2) | `GraphCanvas.tsx` lines 469-497 renders a fixed, static HUD panel at `top: 14, left: 14` with `pointerEvents: 'none'`. | Panel cannot be collapsed or clicked. On standard and smaller screen viewports, the fixed telemetry panel collides and visually overlaps with the top toolbar dropdowns ("JURISDICTION", "POLICY", "GRAPHRAG CHAT"). |
| **DEF-03** | Canvas Node Hover & Interaction Stability (`functional_specification_006.md` Section 3, Section 4.3.1-4.3.3, Acceptance Criteria 3) | In `GraphCanvas.tsx`: hover handler calls `setHoveredNode(hovered)`, updating React state. This causes `render` callback to be recreated (line 310 dependency `hoveredNode`). The simulation `useEffect` at line 348 depends on `[nodes, links, render]`. | Every hover event tears down the D3 simulation (`simulation.stop()`) and restarts a brand new simulation with `alpha = 1` and `-120` repulsive charge. This violently displaces nodes away from the cursor in an infinite jitter loop, making click selection evasive and frustrating. |
| **DEF-04** | Autonomous Stabilization Upon Load (`functional_specification_006.md` Section 4.1.2) | The simulation in `GraphCanvas.tsx` lines 322-348 restarts repeatedly whenever state changes (`render` dependency), preventing autonomous stabilization. | The graph layout never settles into a quiescent, stable state if user cursor moves across nodes. |
| **DEF-05** | CMS MCD "Invalid Article Version" Failure Elimination (`functional_specification_006.md` Section 3, Section 4.4.1, Acceptance Criteria 4) | `NodeDetailDrawer.tsx` line 72 hardcodes `https://www.cms.gov/medicare-coverage-database/view/article.aspx?articleid=59508`. Programmatic probe confirms this redirects to `search.aspx?error=Invalid%20Article%20Version`. | Users clicking the coverage policy source link arrive at an error screen rather than active documentation. |
| **DEF-06** | CMS Change Request Dead Link Elimination (`functional_specification_006.md` Section 4.4.6, Acceptance Criteria 4) | `NodeDetailDrawer.tsx` line 77 hardcodes `https://www.cms.gov/files/document/r13286cp.pdf`. Programmatic HTTP probe returns `HTTP/2 404 Not Found`. | Clicking the Change Request link produces a dead 404 page. |
| **DEF-07** | Missing External Government Links for Multiple Entity Types (`functional_specification_006.md` Section 4.4.7-4.4.9, Acceptance Criteria 4) | `NodeDetailDrawer.tsx` `getGovernmentSourceLink()` has no cases for `Jurisdiction`, `HCPCSCode`, or `ICD10Code`, falling through to `default: return null;`. | When inspecting regional contractors (e.g. CGS or Noridian), procedure codes (A6522), or diagnosis codes (I97.2), zero external source link is rendered in the drawer. |
| **DEF-08** | Dynamic Property-Driven URL Parameterization (`functional_specification_006.md` Section 3, Section 4.4.2-4.4.4, Section 4.4.10) | `NodeDetailDrawer.tsx` hardcodes static URLs for `Bill` (always H.R. 3630), `PublicLaw` (always 117-328), `Regulation` (hardcoded date string), and `LobbyingFiling` (generic search homepage). | Selecting H.R. 2617 or H.R. 3808 displays an incorrect link pointing to H.R. 3630. Selecting lobbying filing `c8697fc5-...` links to generic search instead of specific disclosure document. |
| **DEF-09** | Frontend Verification and Test Suite Coverage (`functional_specification_006.md` Section 5 Acceptance Criteria 1-4) | Current automated test suites (`tests/test_api_endpoints.py`, `tests/test_graphrag_pipeline.py`, `tests/test_graph_pipeline.py`) test backend logic and REST endpoints only. Zero automated component tests verify frontend toolbar cleanliness, HUD accordion toggle, stationary hover stability, or link generation logic. | Acceptance criteria cannot be programmatically validated without dedicated frontend component and link audit tests. |

---

## 5. Sufficiency & Scan Certification

In strict accordance with the evaluation parameters in [`LANGUAGE.md`](LANGUAGE.md):

- **`{sufficient}` Certification:** The static scan of the codebase and active read-only reconnaissance of external datasources are complete, exhaustive, and rigorously verified. Every qualified codebase component touching `functional_specification_006.md` has been cataloged under its verbatim symbol and file path. Every candidate external endpoint (CMS MCD, GPO GovInfo, Congress.gov, Federal Register, Cornell LII, CMS Transmittals, CGS Administrators, Noridian Healthcare Solutions, CDC ICD-10-CM, NLM Clinical Tables, and Senate SOPR LDA) has been actively probed and empirically audited, with 23 raw unedited payload and probe files captured in `assets/20261013T165618-008-wcap/`. Zero ambiguity remains regarding the existing dependency cone, external contracts, or observed system behaviors.
- **Zero Invention Guarantee:** In accordance with `INV-ABSENCE-01`, no missing components, layout engines, or API endpoints have been simulated, assumed, or hallucinated. All functional gaps are registered in the Explicit Deficiency Register.

---

## 6. Handoff Manifest Affirmation

In strict compliance with `INV-HANDOFF-01` and `INV-MANIFEST-OVERWRITE-01`:
- Directory `handoff/20261013T165618-008-wcap/` was verified and created.
- File [`handoff/20261013T165618-008-wcap/plan-scan-1.txt`](handoff/20261013T165618-008-wcap/plan-scan-1.txt) was atomically overwritten.
- It contains exclusively the exact repository-relative paths of all qualified codebase components, the authored scan report, and all 23 captured ground-truth payload files in `assets/20261013T165618-008-wcap/`.
- Predecessor manifest `handoff/authored.txt` and all other run directories remain completely intact.
- Zero seed paths are recorded in `handoff/20261013T165618-008-wcap/plan-scan-1.txt`.

---

## 7. Coding Gate Affirmation

**DO NOT CODE YET: Implementation coding gate remains locked. Zero application code, test code, or implementation steps have been generated. Coding waits on an empty frontier and explicit operator authorization.**
