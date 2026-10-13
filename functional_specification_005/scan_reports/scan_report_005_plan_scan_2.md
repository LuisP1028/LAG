# Authoritative Static Codebase Scan, External API Reconnaissance, and Schema Audit Report

**Run ID:** `20261013T155419-714-niq1`  
**Agent:** `plan-scan-2` (Planning Node / Scanner Agent 2)  
**Governing Specification:** `functional_specification_005.md`  
**Status:** Complete Reconnaissance, Codebase Scan, and Empirical Schema Audit (DO NOT CODE YET)  
**Taxonomy Reference:** [LANGUAGE.md](LANGUAGE.md)

---

## 1. Governing Context & Upstream Ingestion Verification

In strict accordance with `INV-HANDOFF-01`, `INV-SCAN-01`, and workspace rules:
- **Seed Specification Ingested:** `functional_specification_005.md` (*Functional Specification: Dynamic Schema-Driven GraphRAG Traversal*), verified non-empty, fully bound, exactly matching single seed scope.
- **Run Identifier:** `20261013T155419-714-niq1` (verified substituted across all filepaths, asset directories, and handoff manifest paths).
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
| `src/graph/models.py` | `EdgeProvenance`, `GraphEdge`, `BaseNode`, `PolicyNode`, `BillNode`, `PublicLawNode`, `StatutorySectionNode`, `RegulationNode`, `ChangeRequestNode`, `CoveragePolicyNode`, `JurisdictionNode`, `StateNode`, `FeeScheduleEntryNode`, `HCPCSCodeNode`, `ICD10CodeNode`, `LobbyingFilingNode`, `CBOScoreNode`, `LiteratureStudyNode` | Typed Pydantic models declaring the complete 14-entity system ontology, edge provenance tracking (`source_uri`, `selector`, `ingestion_timestamp`, `run_id`), and runtime validation forbidding direct procedure-to-diagnosis connections (`INV-NO-KEYWORD-BRIDGING`). | `functional_specification_005.md` Section 4.1 Item 1 mandates recognizing starting nodes across all 14 node types; Section 4.2.3 mandates edge provenance completeness. |
| `src/graph/engine.py` | `DirectedPropertyGraph`, `PropertyGraphEngine`, `GraphValidationError` | In-memory directed graph with adjacency index (`_adj`), deterministic primary key MERGE semantics, and strict validation of system invariants: `validate_invariants()` checks provenance completeness, no-keyword-bridging, 50-state completeness, and unbroken ancestry reachability from root `PolicyNode`. | Validates system invariants (`INV-UNBROKEN-ANCESTRY`, `INV-NO-KEYWORD-BRIDGING`). |
| `src/graph/neo4j_sync.py` | `Neo4jSyncEngine`, `DEFAULT_NEO4J_URI`, `DEFAULT_NEO4J_USER`, `DEFAULT_NEO4J_PASSWORD`, `DEFAULT_NEO4J_DATABASE` | Driver lifecycle manager (`get_driver()`, `close()`), schema constraint and index initializer (`init_schema()`), batched APOC merge synchronizer (`sync_graph_dict()`, `sync_file()`), and graph statistics extractor (`get_summary_statistics()`). | Backing storage and schema constraint engine for live Cypher queries and topological graph expansion. |
| `src/graph/tier1_legislative.py` | `discover_legislation()`, `Phase1DiscoveryError`, `Phase1EnactmentMissingError` | Discovers legislative vehicles (`BillNode`, `PublicLawNode`) linked to policy keywords (`POLICY-LTA`, `POLICY-IVIG`) and builds `TARGETS_BILL` and `ENACTED_AS` relationships. | Provides legislative vehicles for multi-policy convergence queries. |
| `src/graph/tier2_statutory.py` | `parse_statutory_codification()`, `Phase2DocumentRetrievalError`, `Phase2SectionNotFoundError` | Parses GovInfo USLM XML markup for enacted law (PL 117-328), isolates statutory sections (42 U.S.C. 1395x), and connects via `MODIFIES_CODE`. | Traces statutory codification ancestry in knowledge graph. |
| `src/graph/tier3_regulatory.py` | `harvest_regulations()`, `Phase3RuleNotFoundError`, `Phase3DirectiveMissingError` | Extracts administrative Final Rules (`RegulationNode`: 88 FR 77676 / Document 2023-24455) and operational transmittals (`ChangeRequestNode`: CMS-CR-13286 / CMS-CR-13217), connecting via `IMPLEMENTED_BY` and `ISSUES_TRANSMITTAL`. | Ingests regulatory context and change requests linking laws to coverage policies. |
| `src/graph/tier4a_coverage.py` | `ingest_coverage_policy()`, `Phase4ArticleFetchError`, `Phase4CodingTableMissingError`, `STANDARD_COVERED_DIAGNOSES`, `STANDARD_COVERED_HCPCS` | Constructs the mandatory `CoveragePolicyNode` (`CMS-MCD-A59508` / `CMS-MCD-A59588`) legally bridging `ChangeRequest` to procedure codes (`GOVERNS` -> `HCPCSCode`) and clinical diagnoses (`ALLOWS_DIAGNOSIS` -> `ICD10Code`). | Enforces `INV-NO-KEYWORD-BRIDGING` by routing clinical indications strictly through CoveragePolicy articles. |
| `src/graph/tier4b_fee_schedule.py` | `normalize_fee_schedules()`, `Phase4FeeScheduleDatasetError`, `Phase4IncompleteJurisdictionError`, `DME_MAC_JURISDICTIONS` | Maps 4 DME MAC Jurisdictions to all 54 states/territories, unpivots the CMS DMEPOS matrix (108 columns: NR & R), and instantiates 3,816 discrete `FeeScheduleEntryNode` records with `HAS_FEE_SCHEDULE` and `APPLIES_TO` edges. | Generates state fee schedule entries for New York, Wisconsin, and all jurisdictions. |
| `src/graph/tier5_context.py` | `enrich_context()`, `Phase5LiteratureNotFoundError` | Ingests Lobbying Disclosure Act filings (`LobbyingFilingNode`), CBO cost estimates (`CBOScoreNode`), and peer-reviewed biomedical literature (`LiteratureStudyNode`) attached via `HAS_ADVOCACY_RECORD`, `HAS_BUDGET_IMPACT`, and `SUPPORTED_BY_EVIDENCE`. | Attaches macro advocacy and clinical evidentiary nodes to knowledge graph. |
| `src/graph/__init__.py` | Package Exports | Exposes domain models, engine classes, and handoff contracts. | Public Python interface for graph subsystem. |
| `src/graphrag/exceptions.py` | `GraphRAGException`, `EntityResolutionError`, `TraversalError`, `ModelInferenceError`, `ModelAuthenticationError`, `ModelRateLimitError`, `GraphValidationError` | Custom exception hierarchy enforcing fail-fast boundaries across entity resolution, topological traversal, model inference, and invariant validation. | `functional_specification_005.md` Section 5 explicitly mandates returning `EntityResolutionError`, `TraversalError`, `ModelAuthenticationError`, and `ModelInferenceError`. |
| `src/graphrag/models.py` | `AnchorEntity`, `ResolvedAnchors`, `TraversalNode`, `TraversalEdge`, `TraversalResult`, `GraphRAGQueryRequest`, `GraphRAGQueryResponse` | Typed data models declaring anchor entities, traversal nodes and edges with provenance, and request/response envelopes for the GraphRAG pipeline and synchronization bus. | Defines API data structures and telemetry contracts for GraphRAG operations. |
| `src/graphrag/entity_linker.py` | `EntityAnchorLinker`, `STATE_NAME_TO_CODE`, `CLINICAL_SYNONYMS`, `POLICY_TRIGGERS`, `HCPCS_REGEX`, `GEO_LOCATION_INDICATORS` | Deterministic multi-slot entity resolution engine resolving free-form query strings to indexed entity anchors in Neo4j; currently restricted to State, ICD10Code, Policy, and HCPCSCode. | `functional_specification_005.md` Section 4.1 mandates recognizing anchors across all 14 node types and variable input counts ($N \ge 1$). |
| `src/graphrag/traversal.py` | `TopologicalTraversalEngine`, `extract_connecting_subgraph()`, `_execute_pattern_a`, `_execute_pattern_b`, `_execute_pattern_c`, `_convert_node()`, `_convert_edge()` | Subgraph retrieval engine currently gated by hardcoded `if/elif` branch checks for Pattern A (State + Diagnosis), Pattern B (HCPCS/Diagnosis), and Pattern C (2+ Policies); raises `TraversalError` on single state or single node queries. | Root locus of problem statement in `functional_specification_005.md` Section 1, Section 3, and Section 4.2. |
| `src/graphrag/context_assembler.py` | `GraphContextAssembler`, `assemble_context()` | Formats traversed nodes and edges into Markdown prompt context sections: Program & Authority Lineage, Clinical Eligibility, Covered Items & Allowable Fees, and Data Provenance. | `functional_specification_005.md` Section 4.3 mandates structured context assembly across 5 explicit sections. |
| `src/graphrag/synthesizer.py` | `HuggingFaceSynthesizer`, `DEFAULT_MODEL`, `ROUTER_CHAT_URL`, `MODEL_ALIASES`, `SYSTEM_PROMPT`, `synthesize()`, `_call_hf_inference_api()` | Connects to Hugging Face Router API (`https://router.huggingface.co/v1/chat/completions`) with temperature 0.01 and anti-hallucination prompt. | `functional_specification_005.md` Section 4.4 mandates strict grounding, quoting exact bracketed node IDs, dollar figures, and public laws. |
| `src/graphrag/pipeline.py` | `GraphRAGPipeline`, `execute_query()` | 5-stage GraphRAG pipeline orchestrating entity anchor linking, topological traversal, context assembly, LLM synthesis, and provenance extraction. | Orchestrates end-to-end GraphRAG pipeline operations. |
| `src/graphrag/__init__.py` | Package Exports | Exposes GraphRAG components, exceptions, and models. | Public interface for GraphRAG subsystem. |
| `src/api/models.py` | `HealthResponse`, `TopologyNode`, `TopologyEdge`, `TopologyResponse`, `EntityResolveRequest`, `EntityResolveResponse`, `SubgraphRequest`, `SubgraphResponse`, `ErrorEnvelope` | Pydantic request and response schemas for REST API endpoints and error envelopes. | Defines REST API request and response contracts. |
| `src/api/routes.py` | `router`, `set_sync_engine()`, `get_sync_engine()`, `get_pipeline()`, `get_neo4j_session()`, `/api/health`, `/api/graph/summary`, `/api/graph/topology`, `/api/entities/resolve`, `/api/graphrag/subgraph`, `/api/graphrag/query` | REST route handlers exposing graph topology, entity resolution, anchor subgraph extraction, and conversational GraphRAG queries with standardized HTTP error mapping. | Direct API entry point for visualizer canvas and assistant drawer; Section 4.5 mandates returning active graph keys. |
| `src/api/server.py` | `create_app()`, `lifespan()`, `http_exception_handler()`, `graphrag_exception_handler()`, `app` | FastAPI server with CORS configuration, lifespan Neo4j connection lifecycle management, and standardized error envelopes returning `{error, error_type, message, details, timestamp}`. | `functional_specification_005.md` Section 5 mandates fail-fast HTTP 400 envelopes on missing entities or traversal errors. |
| `src/api/__init__.py` | Package Exports | Exposes API server and routes. | Public interface for API subsystem. |
| `src/frontend/package.json` | Dependencies & Scripts | Defines React 18, Vite, Lucide React, and React Force Graph 2D/3D dependencies. | Frontend application build configuration. |
| `src/frontend/package-lock.json` | Dependency Lockfile | Exact dependency versions for frontend application. | Frontend lockfile. |
| `src/frontend/vite.config.ts` | Vite Configuration | Sets up dev server on port 5173 with proxy forwarding `/api` to `http://localhost:8000`. | Frontend dev server and API proxy configuration. |
| `src/frontend/tsconfig.json` | TypeScript Configuration | Project-wide TypeScript configuration. | TypeScript compiler settings. |
| `src/frontend/tsconfig.app.json` | TypeScript App Configuration | Compiler settings for frontend application code. | TypeScript application compiler settings. |
| `src/frontend/tsconfig.node.json` | TypeScript Node Configuration | Compiler settings for Vite node configuration. | TypeScript node compiler settings. |
| `src/frontend/index.html` | HTML Entry Point | Web document root mounting React application. | Web application entry point. |
| `src/frontend/src/main.tsx` | React Root | Bootstraps React DOM root rendering `<App />`. | React DOM initialization. |
| `src/frontend/src/App.tsx` | Main Application Component | Assembles top header, FilterToolbar, GraphCanvas, NodeDetailDrawer, and AgentChatDrawer inside `<GraphSyncProvider>`. | Top-level visualizer view assembly. |
| `src/frontend/src/App.css` | App Styling | Layout styling, header styles, and responsive sizing. | Layout CSS. |
| `src/frontend/src/index.css` | Global CSS | Global reset, dark mode navy blueprint backdrop, and typography. | Global CSS baseline. |
| `src/frontend/src/types/graph.ts` | `NodeProperties`, `EdgeProvenance`, `GraphNode`, `GraphLink`, `AnchorEntity`, `GraphRAGQueryResponse`, `GraphSummary` | TypeScript interfaces mirroring backend models and telemetry payloads. | Client-side type contracts. |
| `src/frontend/src/styles/graph_theme.ts` | `CANVAS_PALETTE`, `NODE_VISUALS`, `getNodeVisual()` | Color styling for 14 node entity types, active amber glow (`#ffb703`), muted edge styles, and dark navy canvas palette. | Visual styling and palette conforming to halftone blueprint specification. |
| `src/frontend/src/context/GraphSyncContext.tsx` | `GraphSyncProvider`, `useGraphSync()`, `GraphSyncContextType` | React context managing shared state: `activeNodePKs`, `activeEdgeKeys`, `selectedNode`, `seededAnchor`, `isIlluminated`, `quickPrompts`, `filterState`, `policyKeyword`, `physicsFrozen`, `isChatOpen`, `focusTarget`. | Implements bidirectional canvas-agent synchronization bus conforming to Ticket 004 and Section 4.5. |
| `src/frontend/src/components/GraphCanvas.tsx` | `GraphCanvas` | Force-directed graph canvas rendering nodes, links, active glow auras, 20% background attenuation, and 350ms camera interpolation focus. | `functional_specification_005.md` Section 4.5 Item 2 mandates canvas highlighting and camera centering. |
| `src/frontend/src/components/AgentChatDrawer.tsx` | `AgentChatDrawer` | Slide-over conversational assistant drawer executing `POST /api/graphrag/query`, rendering synthesized answers, and calling `setIlluminatedPath()`. | Conversational UI executing GraphRAG queries and receiving active paths. |
| `src/frontend/src/components/NodeDetailDrawer.tsx` | `NodeDetailDrawer` | Slide-over node inspection drawer showing primary keys, properties, direct government source links, connected neighbors, and quick-action prompt buttons. | `functional_specification_005.md` Section 3 mandates clicking any node retrieves surrounding relationships without crashing. |
| `src/frontend/src/components/FilterToolbar.tsx` | `FilterToolbar` | Top toolbar controlling policy keyword filtering (LTA / IVIG), state-specific fee expansion, fee schedule toggle, and freeze physics. | Visualizer viewport controls and state filtering. |
| `tests/test_graph_pipeline.py` | Pytest Graph Verification Suite | Validates invariants across property graph (`INV-NO-KEYWORD-BRIDGING`, `INV-UNBROKEN-ANCESTRY`, `INV-50-STATE-COMPLETENESS`, `INV-PROVENANCE-COMPLETENESS`). | Verifies graph construction and database invariants. |
| `tests/test_graphrag_pipeline.py` | Pytest GraphRAG Verification Suite | Tests Oracles 1 through 6: patient benefit routing, no keyword bridging, cross-policy convergence, zero orphan invariant, edge provenance completeness, and fail-fast error boundaries. | Baseline test harness for GraphRAG; requires extension for single-entity queries under Spec 005. |
| `tests/test_api_endpoints.py` | Pytest FastAPI TestClient Suite | Tests `/api/health`, `/api/graph/summary`, `/api/graph/topology`, `/api/entities/resolve`, `/api/graphrag/subgraph`, and `/api/graphrag/query`. | Verifies REST API behavior and error envelopes. |
| `exports/lta_knowledge_graph.json` | LTA Knowledge Graph Export | Complete serialized graph containing 3,852 nodes (3,710 FeeScheduleEntry, 70 HCPCSCode, 53 State, 4 Jurisdiction, 3 ICD10Code, 2 Bill, 2 LobbyingFiling, 2 LiteratureStudy, 1 Policy, 1 PublicLaw, 1 StatutorySection, 1 Regulation, 1 ChangeRequest, 1 CoveragePolicy) and 7,562 directed edges. | Source knowledge graph export for LTA domain. |
| `exports/ivig_knowledge_graph.json` | IVIG Knowledge Graph Export | Complete serialized graph containing 183 nodes and 289 directed edges covering in-home IVIG services under CAA 2023. | Source knowledge graph export for IVIG domain. |
| `verify_all.py` | Root System Verification Script | End-to-end verification script testing backend models, engine invariants, and Neo4j connectivity. | Workspace verification runner. |
| `package.json` | Root Package Manifest | Workspace root package configuration. | Root workspace manifest. |
| `package-lock.json` | Root Package Lockfile | Workspace root dependency lockfile. | Root workspace lockfile. |
| `bad_understanding.md` | Architectural Anti-Patterns Document | Documents common misconceptions and flawed assumptions to avoid during graph retrieval design. | Architectural guidance on anti-patterns. |
| `basic_corrections.md` | Corrections Register | Log of baseline data model corrections and edge alignment rules. | System historical alignment register. |
| `data_extraction_meta.md` | Data Extraction Metadata | Lineage tracking metadata for legislative and regulatory sources. | Source extraction documentation. |
| `data_source.md` | External Data Source Catalog | Overview of primary government data sources and URLs. | Data source reference. |
| `dataflow.md` | Dataflow Architecture | Architectural diagrams of data movement across ingestion tiers. | Data pipeline architecture. |
| `datasource_schema.md` | Source Data Schema Documentation | Schema definitions for raw federal payloads. | Ingestion schema reference. |
| `example_output.md` | Example Graph & Synthesized Outputs | Sample terminal outputs and JSON structures. | Reference output samples. |
| `required_edits.md` | Required Code Edits Log | Historical register of mandatory modifications. | Implementation reference log. |
| `agentresearch_enhancement.md` | Research Subsystem Architecture | Documentation of research agents and statutory discovery. | Subsystem architecture documentation. |
| `visualization.md` | Halftone Visualizer Specification | Complete specification of visualizer aesthetic, shaders, node colors, and interactions. | Reference design specification. |

---

## 3. Candidate External Datasource & Schema Audit Register

Every external datasource, API service, and database interface mandated by `functional_specification_005.md` was probed using active, safe read-only reconnaissance tools (`curl`, lightweight Python inspection scripts, and MCP tool calls). Authentic ground-truth response payloads and headers were captured into `assets/20261013T155419-714-niq1/`.

### 3.1. Neo4j Property Graph Database (Bolt Protocol & Cypher Query Engine)
- **Role in Specification:** Authoritative knowledge graph backing dynamic GraphRAG traversal, single-state queries (`STATE-NY`), multi-entity connecting path discovery, and canvas hydration (Section 1, Section 4.2, Section 6).
- **Endpoint Probed:** `bolt://localhost:7687` (Database: `neo4j`).
- **Authentication:** Username `neo4j`, Password `qwertyui`. Connection verified via `Neo4jSyncEngine.get_driver().verify_connectivity()`.
- **Empirical State Verified:**
  - Total Nodes: 3,971
  - Total Directed Relationships: 7,795
  - Node Label Counts:
    - `FeeScheduleEntry`: 3,816
    - `HCPCSCode`: 75
    - `State`: 53
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
  - Relationship Type Counts:
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
  - Schema Constraints: Uniqueness constraint `policy_node_pk` on `(n:PolicyNode).primary_key`.
  - Schema Indexes: 15 dedicated label indexes on `primary_key`.
- **Empirical Query Probes & Verifications:**
  1. *Single-State Query for New York (`STATE-NY`):*
     - Evaluated query:
       ```cypher
       MATCH (s:State {primary_key: "STATE-NY"})<-[r1:COVERS_STATE]-(j:Jurisdiction)<-[r2:APPLIES_TO_JURISDICTION]-(cr:ChangeRequest)-[r3:MANDATES_POLICY]->(cp:CoveragePolicy)
       RETURN s, r1, j, r2, cr, r3, cp
       ```
     - Results: Traverses to `JURIS-DME-A (Noridian)` (Noridian Healthcare Solutions), governing Change Requests `CMS-CR-13286` (LC) and `CMS-CR-13217` (IVIG), and Coverage Policies `CMS-MCD-A59508` and `CMS-MCD-A59588`.
     - Non-rural fee schedule query:
       ```cypher
       MATCH (f:FeeScheduleEntry)-[:APPLIES_TO]->(s:State {primary_key: "STATE-NY"})
       WHERE f.is_rural = false
       RETURN f.hcpcs_code, f.fee_amount, f.ceiling, f.floor, f.is_rural
       ```
     - Results: 70 procedure codes verified, including `HCPCS-A6522` ($290.47, 20% coinsurance $58.09), `HCPCS-A6520` ($119.54), `HCPCS-Q2052` ($409.84).
  2. *Single Clinical Entity Queries:*
     - `HCPCS-A6522` traverses upward through `GOVERNS` to `CMS-MCD-A59508`, `CMS-CR-13286`, and links to 3 allowable diagnoses (`I97.2`, `Q82.0`, `I89.0`).
     - `ICD10-I97.2` traverses upward through `ALLOWS_DIAGNOSIS` to `CMS-MCD-A59508` and connects to 70 governed HCPCS codes.
  3. *Multi-Entity Patient Benefit Routing (Oracle 1):*
     - Connects `STATE-WI` to `JURIS-DME-B`, `CMS-CR-13286`, `CMS-MCD-A59508`, `ICD10-I97.2`, `HCPCS-A6522`, and `FEE-A6522-WI-NR-2024` ($290.47 rate).
  4. *Coverage Policy Bridge (Oracle 2):*
     - Verified count of direct `(:HCPCSCode)-[:*]->(:ICD10Code)` edges is exactly 0 (`direct_count: 0`).
  5. *Cross-Policy Comparative Lineage (Oracle 3):*
     - Traces convergence of `POLICY-LTA` and `POLICY-IVIG` into `PLAW-117-328` (Consolidated Appropriations Act, 2023) and `FR-2023-24455` (88 FR 77676).
- **Captured Ground-Truth Payloads:**
  - `assets/20261013T155419-714-niq1/neo4j_summary_statistics.json`
  - `assets/20261013T155419-714-niq1/neo4j_schema_constraints_and_indexes.json`
  - `assets/20261013T155419-714-niq1/neo4j_single_state_ny_administrative_path.json`
  - `assets/20261013T155419-714-niq1/neo4j_single_state_ny_fees.json`
  - `assets/20261013T155419-714-niq1/neo4j_single_clinical_hcpcs_a6522_path.json`
  - `assets/20261013T155419-714-niq1/neo4j_single_clinical_icd10_i972_path.json`
  - `assets/20261013T155419-714-niq1/neo4j_oracle1_patient_benefit_routing.json`
  - `assets/20261013T155419-714-niq1/neo4j_oracle2_coverage_policy_bridge.json`
  - `assets/20261013T155419-714-niq1/neo4j_oracle3_cross_policy_convergence.json`

### 3.2. Hugging Face Inference Router & Model APIs
- **Role in Specification:** Powering GraphRAG LLM synthesis without Cypher hallucination; generating grounded answers citing exact bracketed node IDs, public laws, and fee amounts (Section 1, Section 4.4, Section 5 Item 4).
- **Endpoints Probed:**
  1. *Model Metadata (Llama-3.1-8B-Instruct):* `GET https://huggingface.co/api/models/meta-llama/Llama-3.1-8B-Instruct` (HTTP 200 OK, Content-Length: 23,111 bytes).
  2. *Model Metadata (Qwen2.5-7B-Instruct):* `GET https://huggingface.co/api/models/Qwen/Qwen2.5-7B-Instruct` (HTTP 200 OK, Content-Length: 7,879 bytes).
  3. *Inference Router Catalog:* `GET https://router.huggingface.co/v1/models` (HTTP 200 OK, Content-Length: 79,277 bytes).
  4. *Chat Completions Endpoint (Error Boundary Probe):* `POST https://router.huggingface.co/v1/chat/completions` without token (HTTP 401 Unauthorized, Content-Length: 3,087 bytes).
- **Observed Schema & Contract Details:**
  - Catalog Schema: `$.data[*].{id: string, object: 'model', created: int, owned_by: string}`.
  - Authentication Contract: Requires header `Authorization: Bearer <HF_TOKEN>`; missing or invalid token raises HTTP 401 with standard error JSON containing `error` object and request ID.
  - Fail-Fast Errors: Mapped to `ModelAuthenticationError` (401), `ModelRateLimitError` (429), and `ModelInferenceError` (502 / timeout).
- **Captured Ground-Truth Payloads:**
  - `assets/20261013T155419-714-niq1/hf_model_api_llama31_8b.json`
  - `assets/20261013T155419-714-niq1/hf_model_api_qwen25_7b.json`
  - `assets/20261013T155419-714-niq1/hf_router_v1_models.json`
  - `assets/20261013T155419-714-niq1/hf_chat_completions_unauth_error.json`
  - `assets/20261013T155419-714-niq1/hf_chat_completions_401_headers.txt`

### 3.3. Federal Register API v1
- **Role in Specification:** Authoritative regulatory publication metadata for Final Rule citations (88 FR 77676, Document 2023-24455) cited in LLM context and provenance blocks (Section 4.3, Section 4.4).
- **Endpoint Probed:** `GET https://www.federalregister.gov/api/v1/documents/2023-24455.json` (HTTP 200 OK, Content-Length: 100,483 bytes).
- **Authentication:** Public access, no authentication required.
- **Observed Schema:**
  - First-class properties: `$.document_number` (`"2023-24455"`), `$.citation` (`"88 FR 77676"`), `$.effective_on` (`"2024-01-01"`), `$.title`, `$.abstract`, `$.body_html_url`, `$.pdf_url`.
  - Regulatory references: `$.cfr_references[*].{title: int, part: string}`.
- **Captured Ground-Truth Payload:**
  - `assets/20261013T155419-714-niq1/federal_register_rule_2023_24455.json`

### 3.4. Electronic Code of Federal Regulations (eCFR) API
- **Role in Specification:** Authoritative legal text verification for CFR citations (42 CFR § 410.36, 42 CFR § 414.1650) cited in LLM clinical context and detail drawers (Section 4.3).
- **Endpoints Probed:**
  1. `GET https://www.ecfr.gov/api/versioner/v1/titles.json` (HTTP 200 OK, Content-Length: 8,033 bytes).
  2. `GET https://www.ecfr.gov/api/search/v1/results?query=lymphedema` (HTTP 200 OK, Content-Length: 26,159 bytes).
  3. `GET https://www.ecfr.gov/api/search/v1/results?query=lymphedema&hierarchy%5Btitle%5D=42` (HTTP 200 OK, Content-Length: 18,034 bytes).
- **Observed Schema:**
  - Result Hierarchy: `$.results[*].hierarchy.{title: '42', chapter: 'IV', subchapter: 'B', part: '414', subpart: 'Q', section: '414.1650'}`.
  - Headings: `$.results[*].headings.{part: string, subpart: string, section: string}`.
- **Captured Ground-Truth Payloads:**
  - `assets/20261013T155419-714-niq1/ecfr_titles.json`
  - `assets/20261013T155419-714-niq1/ecfr_search_lymphedema.json`
  - `assets/20261013T155419-714-niq1/ecfr_search_lymphedema_title42.json`

### 3.5. GPO GovInfo API
- **Role in Specification:** Authoritative external link target for legislative vehicles (`Bill`) and public law summaries (`PublicLaw`) cited in LLM synthesis and detail drawers (Section 4.4 Item 4).
- **Endpoints Probed:**
  1. `GET https://api.govinfo.gov/packages/BILLS-117hr3630ih/summary?api_key=DEMO_KEY` (HTTP 200 OK, Content-Length: 69,576 bytes).
  2. `GET https://api.govinfo.gov/packages/PLAW-117publ328/summary?api_key=DEMO_KEY` (HTTP 200 OK, Content-Length: 120,163 bytes).
- **Observed Schema:**
  - Package Properties: `$.title`, `$.shortTitle[*].title`, `$.congress` (`"117"`), `$.originChamber`, `$.references[*].{collectionCode: 'USCODE', contents: [{title: '42', sections: ['1395x']}]}`.
  - Downloads: `$.download.{xmlLink, pdfLink, modsLink}`.
- **Captured Ground-Truth Payloads:**
  - `assets/20261013T155419-714-niq1/govinfo_bills_117hr3630ih_summary.json`
  - `assets/20261013T155419-714-niq1/govinfo_plaw_117publ328_summary.json`

### 3.6. CMS Medicare Coverage Database (MCD)
- **Role in Specification:** Authoritative external link target and provenance anchor for `CoveragePolicy` nodes (`CMS-MCD-A59508`, `CMS-MCD-A59588`) (Section 4.2.3, Section 4.4 Item 2).
- **Endpoint Probed:** `GET https://www.cms.gov/medicare-coverage-database/view/article.aspx?articleid=59508` (HTTP 200 OK, Content-Length: 158,809 bytes).
- **Observed Response:** HTTP/2 200 with standard HTML headers and CMS article payload structure.
- **Captured Ground-Truth Payloads:**
  - `assets/20261013T155419-714-niq1/cms_mcd_a59508_probe.html`
  - `assets/20261013T155419-714-niq1/cms_mcd_a59508_headers.txt`

---

## 4. Explicit Deficiency Register (INV-ABSENCE-01)

In strict accordance with `INV-ABSENCE-01`, when a required specification behavior cannot be provided by existing codebase components or responding external endpoints, the deficiency is explicitly recorded below. No components, classes, or endpoints are invented:

| Deficiency ID | Specced Requirement | Functional Specification Clause | Current Codebase State | Exact Missing Capability |
|---|---|---|---|---|
| **DEF-01** | Multi-Slot Entity Anchor Linker Domain Coverage Deficit | `functional_specification_005.md` Section 4.1 Item 1 (`Support Any Domain Entity`) & Item 2 (`Variable Number of Inputs`) | `src/graphrag/entity_linker.py` currently contains regex extractors and resolvers for only 4 entity types: `State`, `ICD10Code`, `Policy`, and `HCPCSCode`. | Missing resolver logic to recognize and anchor the remaining 10 database entity types (`Jurisdiction`, `ChangeRequest`, `CoveragePolicy`, `Bill`, `PublicLaw`, `StatutorySection`, `Regulation`, `FeeScheduleEntry`, `LobbyingFiling`, `LiteratureStudy`) from input text or primary keys. |
| **DEF-02** | Hardcoded Query Template Routing & Single-Anchor Traversal Crash | `functional_specification_005.md` Section 1 (`The Problem`), Section 3 (`Query Routing`), and Section 4.2.2 (`Single Entity Provided, N=1`) | `src/graphrag/traversal.py` lines 39–76 gate execution behind hardcoded `if/elif` branches: `if anchors.state_anchor and anchors.diagnosis_anchor:` (Pattern A), `elif len(policies) >= 2:` (Pattern C), `elif hcpcs or diagnosis:` (Pattern B), else raises `TraversalError`. | Querying a single state (`STATE-NY`), single policy (`POLICY-LTA`), or any single non-clinical anchor immediately crashes with unhandled `TraversalError`. Traversal engine lacks dynamic schema-driven path expansion. |
| **DEF-03** | Absence of Generalized Connecting Path Discovery for Multi-Entity Anchors ($N \ge 2$) | `functional_specification_005.md` Section 4.2.1 (`When Two or More Entities Are Provided, N >= 2`) | `src/graphrag/traversal.py` only implements fixed static Cypher queries for three specific patterns; arbitrary multi-entity sets (e.g., `State` + `Jurisdiction`, or `CoveragePolicy` + `PublicLaw`, or `State` + `Policy`) have no traversal logic. | Missing dynamic path discovery algorithm finding shortest paths and shared ancestry in Neo4j between arbitrary pairs/sets of entities while respecting `INV-NO-KEYWORD-BRIDGING` and `INV-UNBROKEN-ANCESTRY`. |
| **DEF-04** | Missing Single-Entity Administrative & Clinical Lineage Traversal Engine ($N = 1$) | `functional_specification_005.md` Section 4.2.2 (`When a Single Entity Is Provided, N = 1`) & Section 6 Item 1 (`Single-State Queries Succeed`) | `src/graphrag/traversal.py` contains zero traversal methods for single entity anchors ($N = 1$). | Missing single-state traversal retrieving: (1) regional contractor (`Jurisdiction`) via `COVERS_STATE`, (2) governing `ChangeRequest` and `CoveragePolicy`, (3) non-rural fee schedule entries for that state; and single-clinical traversal retrieving governing policy and allowable items. |
| **DEF-05** | Context Assembler Rigid Defaults and State Assumptions | `functional_specification_005.md` Section 4.3 (`Context Assembly for the LLM`) | `src/graphrag/context_assembler.py` hardcodes default parameters (`state_code="WI"`, hardcoded `[POLICY-LTA]` fallback, hardcoded transmittal `13286`, and specifically searches for `A6522`). | Context assembler cannot flexibly assemble 5 distinct factual sections for arbitrary states (e.g. New York, California) or non-LTA policies without falling back to Wisconsin/LTA defaults. |
| **DEF-06** | LLM Grounding Prompt Missing Exact Citation & Bracketed PK Mandates | `functional_specification_005.md` Section 4.4 (`LLM Synthesis Grounding`) | `src/graphrag/synthesizer.py` lines 30–35 contains a generic system prompt forbidding guessing, but lacks explicit prompt instructions directing the model to cite exact bracketed primary keys (e.g. `[CMS-MCD-A59508]`, `[PLAW-117-328]`, `[JURIS-DME-B]`), exact allowable dollar figures and coinsurance, and public law numbers. | Model synthesis instructions lack mandatory bracketed identifier citation directives, causing paraphrasing of policy codes rather than verbatim primary key citations. |
| **DEF-07** | REST API Subgraph Anchor Resolution Contract Limitation | `functional_specification_005.md` Section 4.1 Item 2 & Section 4.5 Item 1 | `src/api/routes.py` lines 298–308 only maps 4 entity types to semantic slots (`State`, `ICD10Code`, `Policy`, `HCPCSCode`) and assigns `slot = "entity"` for all others, which then causes `TopologicalTraversalEngine` to reject the anchor set. | `POST /api/graphrag/subgraph` fails with HTTP 400 when invoked with any anchor outside the 4 hardcoded slots (e.g., passing `["JURIS-DME-A"]` or `["CMS-MCD-A59508"]` fails). |
| **DEF-08** | Test Suite Coverage Deficit for Single-Entity Queries and Dynamic Topology | `functional_specification_005.md` Section 6 (`Acceptance Criteria`) | `tests/test_graphrag_pipeline.py` and `tests/test_api_endpoints.py` only test multi-entity pairs (Oracle 1: WI + I97.2, Oracle 3: LTA + IVIG) and error boundaries; zero tests exist for single-state queries (`STATE-NY`), single-policy queries, or arbitrary graph exploration. | Missing test coverage for single-state queries (*"What covers New York?"*, *"What are the allowable compression rates in New York?"*), single-node canvas clicks, and dynamic schema-driven traversal without `if/elif` branching. |

---

## 5. Sufficiency & Scan Certification

In accordance with [`LANGUAGE.md`](LANGUAGE.md):
- **Completeness of Dependency Cone:** The dependency cone of `functional_specification_005.md` is exhaustively enumerated down to leaf data models, sync scripts, REST routes, React components, test suites, and configuration files. Exactly 59 local codebase component files were identified, reviewed, and physically verified. Zero components were sampled, ranked, or guessed.
- **Empirical Grounding of External Interfaces:** All candidate external datasources (Neo4j Bolt database, Hugging Face Router API, Federal Register API, eCFR API, GPO GovInfo API, and CMS MCD) have been probed directly using safe read-only tools. Their live availability, authentication requirements, and empirical schemas are documented with 22 ground-truth payload samples saved in `assets/20261013T155419-714-niq1/`.
- **Zero Invention Guarantee:** Specced behaviors lacking existing codebase components or responding APIs are cataloged exclusively in the Explicit Deficiency Register. Zero synthetic components were invented.
- **Condition `{sufficient}` Attained:** Absolutely no ambiguity remains regarding the active state of the codebase, external endpoint schemas, or functional deficiencies. Downstream implementation planning can proceed with full deterministic grounding.

---

## 6. Handoff Manifest Affirmation

In strict accordance with `INV-MANIFEST-OVERWRITE-01`:
- Directory `handoff/20261013T155419-714-niq1/` has been created.
- File `handoff/20261013T155419-714-niq1/plan-scan-2.txt` has been atomically overwritten with exactly one repository-relative path per line.
- The manifest contains exclusively:
  - All qualified codebase component files (59 paths).
  - This authored scan report (`scan_reports/scan_report_005_plan_scan_2.md`).
  - All 22 saved ground-truth payload files in `assets/20261013T155419-714-niq1/`.
- Seed path `functional_specification_005.md` is strictly excluded from the manifest.
- Predecessor manifests (`handoff/authored.txt`) and other run directories remain completely intact.

---

## 7. Coding Gate Affirmation

> **DO NOT CODE YET:** Implementation coding gate remains locked. Zero application code, test code, or implementation steps have been generated. Coding waits on an empty frontier and explicit operator authorization.
