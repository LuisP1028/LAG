# Codebase Static Scan, External API Reconnaissance, and Schema Audit Report

**Report ID:** `scan_report_001.md`  
**Execution Node:** `plan-scan-1` (Agent 1)  
**Run ID:** `20261013T155419-714-niq1`  
**Timestamp:** `2026-10-13T15:54:19-07:00`  
**Governing Specification:** [`functional_specification_005.md`](functional_specification_005.md) (*Functional Specification: Dynamic Schema-Driven GraphRAG Traversal*)  
**Status:** Complete Reconnaissance & Schema Audit Register  
**Implementation Gate:** Strict Boundary Enforced (**DO NOT CODE YET**)

---

## 1. Governing Context & Ingestion Verification

In strict compliance with `INV-HANDOFF-01`, workspace architectural rules, and the loading hierarchy:

1. **Single Upstream Specification in Scope:**
   - Ingested verbatim and strictly bounded to: [`functional_specification_005.md`](functional_specification_005.md) (*Functional Specification: Dynamic Schema-Driven GraphRAG Traversal*).
   - Predecessor manifest verified: `handoff/authored.txt` records `functional_specification_005.md` as the first active target.
   - Zero scanning across unassigned specifications; no multiple seed paths consumed.
2. **Wayfinder Architectural Map and Decision Tickets Inspected:**
   - [`wayfinder/map.md`](wayfinder/map.md): *Wayfinder Architectural Map: GraphRAG Specification for Browser Graph Visualizer*
   - [`wayfinder/tickets/ticket-001.md`](wayfinder/tickets/ticket-001.md): *Entity Anchor Linking and Layperson Vocabulary Normalization Specification* (RESOLVED)
   - [`wayfinder/tickets/ticket-002.md`](wayfinder/tickets/ticket-002.md): *Generalized Topological Subgraph Expansion and Neighborhood Traversal Specification* (RESOLVED)
   - [`wayfinder/tickets/ticket-003.md`](wayfinder/tickets/ticket-003.md): *Factual Context Assembly, Edge Provenance Formatting, and Prompt Grounding Specification* (RESOLVED)
   - [`wayfinder/tickets/ticket-004.md`](wayfinder/tickets/ticket-004.md): *Bidirectional Visual Canvas Synchronization and Active Subgraph Illumination Specification* (RESOLVED)
   - [`wayfinder/tickets/ticket-005.md`](wayfinder/tickets/ticket-005.md): *Master Specification Synthesis and Edits for functional_specification_004.md* (RESOLVED)
3. **Evaluation Parameters Adherence ([`LANGUAGE.md`](LANGUAGE.md)):**
   - **`{errors}`**: Explicit failure states surfaced immediately during execution (system crashes, unhandled exceptions, unindexed entity resolution failures, traversal crashes when querying valid database entities such as `STATE-NY`, missing foreign keys, API timeouts, HTTP 401/429/503 errors).
   - **`{correctness}`**: Precise, local execution of graph traversal and context assembly without logical flaws; exact node, relationship, and fee schedule retrieval matching actual data in Neo4j without guessing or data truncation.
   - **`{functionality}`**: The complete GraphRAG pipeline accepts any valid entity or set of entities ($N \ge 1$), finds the relevant connecting subgraph or statutory/administrative lineage in Neo4j without hardcoded `if/elif` template branching, sends verified facts to the Hugging Face model, and highlights active paths on the canvas.
   - **`{correct required outputs}`**: 
     1. A graph result containing verified nodes, edges, and source provenance from Neo4j.
     2. An LLM-synthesized answer that quotes exact node IDs (e.g., `[CMS-MCD-A59508]`), public laws, and fee amounts.
     3. Visual highlighting of active nodes and edges on the browser canvas.
     4. Immediate `HTTP 400` errors (`EntityResolutionError`) if a term does not exist in the database.
     5. Saved empirical payload samples in `assets/20261013T155419-714-niq1/`.
     6. Dedicated handoff manifest at `handoff/20261013T155419-714-niq1/plan-scan-1.txt` atomically overwritten.
   - **`{sufficient}`**: Requirements and scan registers are complete, unambiguous, and empirically grounded, permitting implementation planning without guesswork.
   - **`{insufficient}`**: Any ambiguity requiring assumptions regarding system behavior, template queries, error states, or data contracts.

---

## 2. Master Component Dependency Cone Register

A deterministic static scan of the active codebase was performed. Each qualified local component whose interface touches specced functionality was reviewed and grounded:

| Repository-Relative Path | Verbatim Symbol / Entity | Interface / Active Role | Specification & Ticket Grounding Justification |
|---|---|---|---|
| [`LANGUAGE.md`](LANGUAGE.md) | `System Glossary & Evaluation Parameters` | Authoritative system taxonomy: `{errors}`, `{correctness}`, `{functionality}`, `{correct required outputs}`, `{sufficient}`, `{insufficient}`, `{Policy Keyword}`, `{Target_Bill_IDs}`, `{Enacted_Law_ID}`, `{US_Code_Citations}`, `{Operational_Filters}`, `{Clinical_Citations}`, `{HCPCS / CPT Codes}`, `{Direct Path (Native Keys)}`, `{Structural Traversal (Derived Keys)}`. | Mandated root glossary by `functional_specification_005.md` Section 2 and `RULE[user_global]`. |
| [`package.json`](package.json) | `@ai-hero/sandcastle: ^0.12.0` | Node.js workspace package manifest defining test and runtime dependencies. | Workspace dependency root. |
| [`visualization.md`](visualization.md) | `GraphRAG Halftone 3D Visualization System` | Technical specification for 3D canvas styling, halftone screen shading, duotone color grading, optical depth of field, telemetry HUD, 3D physics clustering, and camera interpolation. | Informs visual rendering requirements in `functional_specification_005.md` Section 4.5. |
| [`wayfinder/map.md`](wayfinder/map.md) | `Wayfinder Architectural Map: GraphRAG Specification` | Master architecture map defining destinations, GraphRAG invariants (`INV-UNBROKEN-ANCESTRY`, `INV-NO-KEYWORD-BRIDGING`, `INV-FAIL-FAST`, `INV-PROVENANCE-COMPLETENESS`), and dependency DAG. | Master governing planning map. |
| [`wayfinder/tickets/ticket-001.md`](wayfinder/tickets/ticket-001.md) | `Decision Ticket 001` | Entity anchor linking and multi-slot layperson vocabulary normalization specification (State, ICD10Code, Policy). | Informs Stage 1 requirements in `functional_specification_005.md` Section 4.1. |
| [`wayfinder/tickets/ticket-002.md`](wayfinder/tickets/ticket-002.md) | `Decision Ticket 002` | Generalized topological subgraph expansion and $k$-hop neighborhood traversal specification ($k=1$ to $3$, <25ms Neo4j SLA). | Informs Stage 2 requirements in `functional_specification_005.md` Section 4.2. |
| [`wayfinder/tickets/ticket-003.md`](wayfinder/tickets/ticket-003.md) | `Decision Ticket 003` | Factual context assembly, edge provenance formatting, and prompt grounding specification into structured Markdown blocks. | Informs Stage 3 requirements in `functional_specification_005.md` Section 4.3. |
| [`wayfinder/tickets/ticket-004.md`](wayfinder/tickets/ticket-004.md) | `Decision Ticket 004` | Bidirectional visual canvas synchronization, event bus contracts, and active subgraph path illumination within <500ms. | Informs canvas synchronization in `functional_specification_005.md` Section 4.5. |
| [`wayfinder/tickets/ticket-005.md`](wayfinder/tickets/ticket-005.md) | `Decision Ticket 005` | Master specification synthesis and section edit mappings for GraphRAG architecture. | Governs integration of GraphRAG across specification sections. |
| [`src/graph/__init__.py`](src/graph/__init__.py) | `src.graph` Package Manifest | Exports all 14 node entity types, `EdgeProvenance`, `GraphEdge`, inter-tier handoffs, and `PropertyGraphEngine`. | Package entry point for backend graph representations. |
| [`src/graph/models.py`](src/graph/models.py) | Master Graph Data Contracts | Defines typed Pydantic models for all 14 node types (`StateNode`, `JurisdictionNode`, `ChangeRequestNode`, `CoveragePolicyNode`, `HCPCSCodeNode`, `ICD10CodeNode`, `PolicyNode`, `BillNode`, `PublicLawNode`, `StatutorySectionNode`, `RegulationNode`, `FeeScheduleEntryNode`, `LobbyingFilingNode`, `LiteratureStudyNode`), plus `CBOScoreNode`, `EdgeProvenance`, and `GraphEdge`. | Defines the exact 14 node types mandated in `functional_specification_005.md` Section 4.1. |
| [`src/graph/engine.py`](src/graph/engine.py) | `DirectedPropertyGraph`, `PropertyGraphEngine`, `GraphValidationError` | Multi-tier graph ingestion, maintains adjacency indices, enforces MERGE upsert semantics, exports to JSON, and validates system invariants (`INV-UNBROKEN-ANCESTRY`, `INV-50-STATE-COMPLETENESS`). | Invariant validation and graph store engine. |
| [`src/graph/neo4j_sync.py`](src/graph/neo4j_sync.py) | `Neo4jSyncEngine` | Connects to Neo4j, initializes uniqueness constraints (`policy_node_pk`) and label indexes, executes batched APOC MERGE upserts, and computes summary statistics. | Driver and connectivity interface for Neo4j serving GraphRAG retrieval. |
| [`src/graph/tier1_legislative.py`](src/graph/tier1_legislative.py) | `discover_legislation`, `Phase1DiscoveryError`, `Phase1EnactmentMissingError` | Discovers legislative vehicles (H.R. 3630, H.R. 3808, H.R. 2617) and connects to Public Law `PLAW-117-328`. | Constructs legislative ancestry nodes for cross-policy inquiries. |
| [`src/graph/tier2_statutory.py`](src/graph/tier2_statutory.py) | `parse_statutory_codification`, `Phase2DocumentRetrievalError` | Parses USLM XML for PL 117-328, isolating Section 4133 (amending 42 U.S.C. 1395x for LTA) and Section 4134 (for IVIG). | Constructs statutory codification nodes for legal authority tracing. |
| [`src/graph/tier3_regulatory.py`](src/graph/tier3_regulatory.py) | `harvest_regulations`, `Phase3RuleNotFoundError` | Ingests CMS Final Rule (88 FR 77676 / `FR-2023-24455`) and operational Change Requests (`CMS-CR-13286` for LTA, `CMS-CR-13217` for IVIG). | Administrative rulemaking lineage connecting statute to operational directives. |
| [`src/graph/tier4a_coverage.py`](src/graph/tier4a_coverage.py) | `ingest_coverage_policy`, `STANDARD_COVERED_DIAGNOSES`, `STANDARD_COVERED_HCPCS` | Ingests CMS MCD Policy Articles (`CMS-MCD-A59508`, `CMS-MCD-A59588`), connects `CoveragePolicy` to `HCPCSCode` via `GOVERNS` and to `ICD10Code` via `ALLOWS_DIAGNOSIS`. Strictly blocks direct HCPCS->ICD10 edges. | Implements mandatory `CoveragePolicy` intermediary mandated in `INV-NO-KEYWORD-BRIDGING`. |
| [`src/graph/tier4b_fee_schedule.py`](src/graph/tier4b_fee_schedule.py) | `normalize_fee_schedules`, `DME_MAC_JURISDICTIONS` | Maps 4 regional DME MAC contractors (`JURIS-DME-A`, `B`, `C`, `D`), expands 53/54 states, unpivots CMS DMEPOS fee schedule matrix into 3,816 `FeeScheduleEntry` records. | Provides ground-truth fee data ($290.47 for A6522 in WI, $151.38 for A6583) and regional contractor mappings. |
| [`src/graph/tier5_context.py`](src/graph/tier5_context.py) | `enrich_context` | Ingests Lobbying Disclosure Act reports (`LobbyingFilingNode`), CBO Cost Estimates (`CBOScoreNode`), and PubMed literature studies (`LiteratureStudyNode`). | Enriches graph with macroeconomic and biomedical evidence. |
| [`src/graphrag/__init__.py`](src/graphrag/__init__.py) | `src.graphrag` Package Manifest | Package entry point exporting pipeline, models, and exceptions. | Entry point for GraphRAG module. |
| [`src/graphrag/models.py`](src/graphrag/models.py) | `AnchorEntity`, `ResolvedAnchors`, `TraversalNode`, `TraversalEdge`, `TraversalResult`, `GraphRAGQueryRequest`, `GraphRAGQueryResponse` | Core data models governing entity resolution, topological subgraph retrieval, and API serialization. | Contracts for data transfer across GraphRAG stages. |
| [`src/graphrag/exceptions.py`](src/graphrag/exceptions.py) | `GraphRAGException`, `EntityResolutionError`, `TraversalError`, `ModelInferenceError`, `ModelAuthenticationError`, `ModelRateLimitError`, `GraphValidationError` | Fail-fast error hierarchy enforcing HTTP 400, 401, 429, 500, and 502 status mapping. | Implements fail-fast boundaries required by `functional_specification_005.md` Section 5. |
| [`src/graphrag/entity_linker.py`](src/graphrag/entity_linker.py) | `EntityAnchorLinker` | Resolves natural language text to entity anchors in Neo4j. Currently limited to state, diagnosis, policy, and HCPCS slots. | Focus of `functional_specification_005.md` Section 4.1 requirements. |
| [`src/graphrag/traversal.py`](src/graphrag/traversal.py) | `TopologicalTraversalEngine` | Executes subgraph extraction in Neo4j. Currently contains hardcoded 3-pattern `if/elif` Cypher branching (`_execute_pattern_a`, `_execute_pattern_b`, `_execute_pattern_c`). | Primary focus of `functional_specification_005.md` Sections 1, 3, and 4.2. |
| [`src/graphrag/context_assembler.py`](src/graphrag/context_assembler.py) | `GraphContextAssembler` | Formats retrieved graph nodes, relationships, and edge provenance into structured Markdown context blocks for the LLM. | Implements Section 4.3 structured context formatting. |
| [`src/graphrag/synthesizer.py`](src/graphrag/synthesizer.py) | `HuggingFaceSynthesizer` | Calls Hugging Face Router API (`https://router.huggingface.co/v1/chat/completions`) with strict grounding prompt and zero fallback. | Implements Section 4.4 LLM synthesis grounding. |
| [`src/graphrag/pipeline.py`](src/graphrag/pipeline.py) | `GraphRAGPipeline` | Orchestrates 5-stage GraphRAG pipeline from user query to answer and telemetry. Contains hardcoded `"WI"` fallback. | Pipeline controller satisfying Section 4. |
| [`src/api/__init__.py`](src/api/__init__.py) | `src.api` Package Manifest | REST API package entry point. | Entry point for API layer. |
| [`src/api/models.py`](src/api/models.py) | `HealthResponse`, `TopologyNode`, `TopologyEdge`, `TopologyResponse`, `EntityResolveRequest`, `EntityResolveResponse`, `SubgraphRequest`, `SubgraphResponse` | Pydantic models for REST endpoints. | Request and response schema contracts. |
| [`src/api/routes.py`](src/api/routes.py) | FastAPI REST Router (`/api`) | Exposes endpoints for `/health`, `/graph/summary`, `/graph/topology`, `/entities/resolve`, `/graphrag/subgraph`, and `/graphrag/query`. | REST API gateway powering canvas and assistant drawer. |
| [`src/api/server.py`](src/api/server.py) | `create_app`, `lifespan` | Configures FastAPI app, CORS middleware, lifespan management, and global exception handlers. | HTTP application server. |
| [`src/frontend/package.json`](src/frontend/package.json) | React & Vite Frontend Manifest | Frontend workspace dependencies including `react`, `react-dom`, `lucide-react`, and `vite`. | Frontend build configuration. |
| [`src/frontend/src/types/graph.ts`](src/frontend/src/types/graph.ts) | TypeScript Interfaces | Type contracts for `GraphNode`, `GraphLink`, `AnchorEntity`, `GraphRAGQueryResponse`, `FilterState`. | Type safety between frontend and backend. |
| [`src/frontend/src/context/GraphSyncContext.tsx`](src/frontend/src/context/GraphSyncContext.tsx) | `GraphSyncContext`, `GraphSyncProvider`, `useGraphSync` | Synchronizes active canvas node/edge highlighting, camera centering, filter states, and chat drawer visibility. | State management satisfying Section 4.5. |
| [`src/frontend/src/components/AgentChatDrawer.tsx`](src/frontend/src/components/AgentChatDrawer.tsx) | `AgentChatDrawer` | Conversational drawer component sending GraphRAG queries and dispatching active path illumination to the canvas. | User interface for conversational GraphRAG. |
| [`src/frontend/src/components/GraphCanvas.tsx`](src/frontend/src/components/GraphCanvas.tsx) | `GraphCanvas` | 2D/3D ForceGraph visual canvas rendering nodes, edges, active path highlighting in amber/gold, background attenuation, and camera transitions. | Implements Section 4.5 visual illumination. |
| [`src/frontend/src/components/NodeDetailDrawer.tsx`](src/frontend/src/components/NodeDetailDrawer.tsx) | `NodeDetailDrawer` | Inspector drawer displaying entity properties, connected neighbors, and quick-action query buttons. | Canvas node click interaction target. |
| [`src/frontend/src/components/FilterToolbar.tsx`](src/frontend/src/components/FilterToolbar.tsx) | `FilterToolbar` | Top toolbar for policy selection, state filtering, and camera controls. | Visual filtering controls. |
| [`src/frontend/src/styles/graph_theme.ts`](src/frontend/src/styles/graph_theme.ts) | `CANVAS_PALETTE`, `NODE_CATEGORY_STYLES` | Visual color palette and styling definitions. | Canvas visual design system. |
| [`tests/test_graph_pipeline.py`](tests/test_graph_pipeline.py) | Regression Test Suite | Validates multi-tier graph ingestion, invariant enforcement (`INV-UNBROKEN-ANCESTRY`, `INV-NO-KEYWORD-BRIDGING`), and data integrity. | Backend regression test baseline. |
| [`tests/test_graphrag_pipeline.py`](tests/test_graphrag_pipeline.py) | Test Suite (`test_oracle_1` through `test_oracle_6`) | Validates GraphRAG pipeline against 6 test oracles and latency benchmarks. | Pipeline oracle test baseline. |
| [`tests/test_api_endpoints.py`](tests/test_api_endpoints.py) | REST API Test Suite | Validates all FastAPI endpoints via `TestClient`. | Integration test baseline. |
| [`verify_all.py`](verify_all.py) | `main()` Verification Script | Standalone end-to-end verification and demonstration script. | Verification automation. |
| [`exports/lta_knowledge_graph.json`](exports/lta_knowledge_graph.json) | LTA Serialized Graph Dataset | Complete property graph dataset for LTA policy (3,852 nodes, 7,562 edges) across all 14 node entity types. | Verified offline graph fixture. |
| [`exports/ivig_knowledge_graph.json`](exports/ivig_knowledge_graph.json) | IVIG Serialized Graph Dataset | Complete property graph dataset for IVIG policy (183 nodes, 289 edges). | Verified offline graph fixture for cross-policy convergence. |

---

## 3. Candidate External Datasource Audit & Empirical Payload Schema Register

Active, safe, read-only reconnaissance was conducted across candidate external endpoints representing Hugging Face model endpoints, the Neo4j graph database, and federal documentation sources. Observed behaviors, status codes, headers, and exact empirical schemas are detailed below, with unedited raw response files archived in `assets/20261013T155419-714-niq1/`:

### 3.1. Hugging Face Open-Weight Model Endpoints

* **Candidate Endpoint 1: Hugging Face Model Discovery & Metadata API**
  * **Endpoint:** `GET https://huggingface.co/api/models/meta-llama/Llama-3.1-8B-Instruct`
  * **Authentication:** Open Access (Zero API Key required for model card & metadata inspection).
  * **Observed Status Code:** `HTTP/2 200 OK` (Content-Type: `application/json; charset=utf-8`, Size: 23,111 bytes).
  * **Saved Payload:** [`assets/20261013T155419-714-niq1/hf_model_meta_llama_3_1_8b_instruct.json`](assets/20261013T155419-714-niq1/hf_model_meta_llama_3_1_8b_instruct.json)
  * **Additional Probed Models:**
    - Mistral 7B Instruct: [`assets/20261013T155419-714-niq1/hf_model_mistral_7b_instruct_v0_3.json`](assets/20261013T155419-714-niq1/hf_model_mistral_7b_instruct_v0_3.json) (`HTTP/2 200 OK`, 8,864 bytes)
    - Qwen 2.5 7B Instruct: [`assets/20261013T155419-714-niq1/hf_model_qwen_2_5_7b_instruct.json`](assets/20261013T155419-714-niq1/hf_model_qwen_2_5_7b_instruct.json) (`HTTP/2 200 OK`, 7,879 bytes)
  * **Empirical Schema (HF Model Metadata JSON):**
    - `id`: `string` (e.g., `"meta-llama/Llama-3.1-8B-Instruct"`)
    - `pipeline_tag`: `string` (`"text-generation"`)
    - `library_name`: `string` (`"transformers"`)
    - `tags`: `array[string]` (e.g., `["transformers", "safetensors", "llama", "text-generation", "conversational", ...]`)
    - `downloads`: `integer` (`5858450`)
    - `likes`: `integer` (`8377`)
    - `config`: `object` (`architectures: array[string]`, `model_type: string`, `tokenizer_config: object`)
    - `safetensors.parameters.BF16`: `integer` (`8030261248`)

* **Candidate Endpoint 2: Hugging Face Inference Router API Probe**
  * **Endpoint:** `POST https://router.huggingface.co/hf-inference/models/meta-llama/Llama-3.1-8B-Instruct`
  * **Authentication:** Bearer Token (`Authorization: Bearer <HF_TOKEN>`).
  * **Probe Condition A (Unauthenticated Request):**
    - **Observed Status Code:** `HTTP/2 401 Unauthorized`
    - **Saved Payload:** [`assets/20261013T155419-714-niq1/hf_router_unauthorized_probe.txt`](assets/20261013T155419-714-niq1/hf_router_unauthorized_probe.txt)
    - **Headers:** `server: CloudFront`, `x-error-message: Unauthorized access.`
  * **Probe Condition B (Invalid Token Request):**
    - **Observed Status Code:** `HTTP/2 401 Unauthorized`
    - **Saved Payload:** [`assets/20261013T155419-714-niq1/hf_router_invalid_token_probe.txt`](assets/20261013T155419-714-niq1/hf_router_invalid_token_probe.txt)
    - **Body:** `{"error": "Invalid username or password."}`

### 3.2. Neo4j Graph Database & Topology Schemas

* **Database Configuration:** `bolt://localhost:7687`, database: `neo4j`.
* **Summary Statistics:** [`assets/20261013T155419-714-niq1/neo4j_summary_statistics.json`](assets/20261013T155419-714-niq1/neo4j_summary_statistics.json)
  - `total_nodes`: `3971`
  - `total_edges`: `7795`
* **Node Labels & Cardinalities:** [`assets/20261013T155419-714-niq1/neo4j_node_labels_and_counts.json`](assets/20261013T155419-714-niq1/neo4j_node_labels_and_counts.json)
  - `FeeScheduleEntry`: 3,816
  - `ICD10Code`: 35
  - `State`: 53
  - `LiteratureStudy`: 30
  - `LobbyingFiling`: 16
  - `HCPCSCode`: 10
  - `StatutorySection`: 3
  - `Jurisdiction`: 4
  - `Bill`: 3
  - `ChangeRequest`: 2
  - `CoveragePolicy`: 2
  - `Regulation`: 2
  - `Policy`: 2
  - `PublicLaw`: 1
* **Relationship Types & Cardinalities:** [`assets/20261013T155419-714-niq1/neo4j_relationship_types_and_counts.json`](assets/20261013T155419-714-niq1/neo4j_relationship_types_and_counts.json)
  - `APPLIES_TO`: 3,816
  - `HAS_FEE_SCHEDULE`: 3,816
  - `COVERS_STATE`: 53
  - `ALLOWS_DIAGNOSIS`: 35
  - `SUPPORTED_BY_EVIDENCE`: 30
  - `HAS_ADVOCACY_RECORD`: 16
  - `GOVERNS`: 10
  - `APPLIES_TO_JURISDICTION`: 4
  - `TARGETS_BILL`: 3
  - `ENACTED_AS`: 3
  - `MODIFIES_CODE`: 3
  - `IMPLEMENTED_BY`: 2
  - `ISSUES_TRANSMITTAL`: 2
  - `MANDATES_POLICY`: 2
* **Sample Nodes Across All 14 Types:** [`assets/20261013T155419-714-niq1/neo4j_sample_nodes_14_types.json`](assets/20261013T155419-714-niq1/neo4j_sample_nodes_14_types.json)
* **Empirical Subgraph Payloads Captured:**
  - Workflow 1 (WI + Postmastectomy Lymphedema): [`assets/20261013T155419-714-niq1/neo4j_workflow1_patient_routing_subgraph.json`](assets/20261013T155419-714-niq1/neo4j_workflow1_patient_routing_subgraph.json)
  - Workflow 2 (Coverage Policy Bridge): [`assets/20261013T155419-714-niq1/neo4j_workflow2_coverage_policy_bridge.json`](assets/20261013T155419-714-niq1/neo4j_workflow2_coverage_policy_bridge.json)
  - Workflow 3 (Cross-Policy Lineage): [`assets/20261013T155419-714-niq1/neo4j_workflow3_cross_policy_lineage.json`](assets/20261013T155419-714-niq1/neo4j_workflow3_cross_policy_lineage.json)
  - **Single Entity State NY Lineage Subgraph:** [`assets/20261013T155419-714-niq1/neo4j_single_entity_state_ny_subgraph.json`](assets/20261013T155419-714-niq1/neo4j_single_entity_state_ny_subgraph.json) (146 nodes, 215 edges linking `STATE-NY` to `JURIS-DME-A` (Noridian), `CMS-CR-13286`, `CMS-MCD-A59508`, and all NY non-rural fee schedule entries)
  - **Single Entity Clinical HCPCS-A6522 Subgraph:** [`assets/20261013T155419-714-niq1/neo4j_single_entity_clinical_hcpcs_a6522_subgraph.json`](assets/20261013T155419-714-niq1/neo4j_single_entity_clinical_hcpcs_a6522_subgraph.json)

### 3.3. Federal Documentation & Clinical Datasources

* **Authoritative Source 1: NLM Clinical Tables ICD-10-CM API**
  * **Endpoint:** `GET https://clinicaltables.nlm.nih.gov/api/icd10cm/v3/search?terms=I97.2`
  * **Observed Status Code:** `HTTP/1.1 200 OK`
  * **Saved Payload:** [`assets/20261013T155419-714-niq1/stage1_nlm_icd10cm_search_i972.json`](assets/20261013T155419-714-niq1/stage1_nlm_icd10cm_search_i972.json)
  * **Empirical Schema:** `[total: integer, codes: array[string], extra: null, display: array[array[string]]]`
  * **Observed Content:** `[1, ["I97.2"], null, [["I97.2", "Postmastectomy lymphedema syndrome"]]]`

* **Authoritative Source 2: NLM Clinical Tables HCPCS API**
  * **Endpoint:** `GET https://clinicaltables.nlm.nih.gov/api/hcpcs/v3/search?terms=A6522`
  * **Observed Status Code:** `HTTP/1.1 200 OK`
  * **Saved Payload:** [`assets/20261013T155419-714-niq1/stage4_nlm_hcpcs_search_a6522.json`](assets/20261013T155419-714-niq1/stage4_nlm_hcpcs_search_a6522.json)
  * **Observed Content:** `[1, ["A6522"], null, [["A6522", "Gradient compression arm sleeve, custom"]]]`
  * **Additional Code (A6583):** [`assets/20261013T155419-714-niq1/stage4_nlm_hcpcs_search_a6583.json`](assets/20261013T155419-714-niq1/stage4_nlm_hcpcs_search_a6583.json) (`HTTP/1.1 200 OK`)

* **Authoritative Source 3: National Archives Federal Register API**
  * **Endpoint:** `GET https://www.federalregister.gov/api/v1/documents/2023-24455.json`
  * **Observed Status Code:** `HTTP/2 200 OK` (Content-Length: 100,483 bytes)
  * **Saved Payload:** [`assets/20261013T155419-714-niq1/stage3_federal_register_rule_2023_24455.json`](assets/20261013T155419-714-niq1/stage3_federal_register_rule_2023_24455.json)
  * **Empirical Schema:** `document_number: string`, `citation: string` (`88 FR 77676`), `title: string`, `action: string`, `cfr_references: array[object]`, `effective_on: string` (`2024-01-01`), `regulation_id_number: string` (`0938-AV07`).

* **Authoritative Source 4: Electronic Code of Federal Regulations (eCFR) API**
  * **Endpoint:** `GET https://www.ecfr.gov/api/search/v1/results?query=lymphedema`
  * **Observed Status Code:** `HTTP/2 200 OK` (Content-Length: 26,159 bytes)
  * **Saved Payload:** [`assets/20261013T155419-714-niq1/stage3_ecfr_search_lymphedema.json`](assets/20261013T155419-714-niq1/stage3_ecfr_search_lymphedema.json)
  * **Empirical Schema:** `results: array[object]` (`hierarchy: object`, `title: string`, `part: string`, `section: string`, `score: float`).

* **Authoritative Source 5: GPO GovInfo Public Law 117-328 Endpoint**
  * **Endpoint:** `GET https://www.govinfo.gov/content/pkg/PLAW-117publ328/html/PLAW-117publ328.htm`
  * **Observed Status Code:** `HTTP/2 200 OK`
  * **Saved Payload:** [`assets/20261013T155419-714-niq1/stage2_govinfo_plaw_117publ328_summary.html`](assets/20261013T155419-714-niq1/stage2_govinfo_plaw_117publ328_summary.html)

* **Authoritative Source 6: CMS Medicare Coverage Database (MCD) Web Endpoint**
  * **Endpoint:** `GET https://www.cms.gov/medicare-coverage-database/view/article.aspx?articleid=59508`
  * **Observed Status Code:** `HTTP/2 503 Service Unavailable`
  * **Saved Payload:** [`assets/20261013T155419-714-niq1/stage4_cms_mcd_a59508_headers.txt`](assets/20261013T155419-714-niq1/stage4_cms_mcd_a59508_headers.txt)
  * **Empirical Finding:** Akamai bot protection intercepts direct programmatic HTTP requests (`akamai-grn: 0.5094d817.1791907093.2f0bfc90`). Ground truth for MCD Article A59508 is preserved in verified property graph entities (`CoveragePolicy` `CMS-MCD-A59508`).

---

## 4. Explicit Deficiency Register

In strict adherence to `INV-ABSENCE-01`, this register details every specced requirement in `functional_specification_005.md` that cannot be satisfied by existing codebase components or reachable external endpoints. Zero components or endpoints have been invented:

| Deficiency ID | Specced Requirement / Behavioral Contract | Existing Codebase State | Exact Gap Description & System Impact |
|---|---|---|---|
| **DEF-01** | Dynamic Topological Traversal Without Hardcoded Branches (`functional_specification_005.md` Section 1, Section 3, Section 4.2, Acceptance Criteria 3) | `TopologicalTraversalEngine.extract_connecting_subgraph` in `src/graphrag/traversal.py#L40-L76` relies strictly on three hardcoded `if/elif` branches: Pattern A (State + Diagnosis), Pattern C (Policy $\ge 2$), and Pattern B (HCPCS or Diagnosis). | The engine has no generic graph traversal algorithm. Any query outside the 3 hardcoded combinations falls through to line 72 and immediately raises a fatal `TraversalError`. |
| **DEF-02** | Single-Entity Lineage Traversal ($N = 1$) (`functional_specification_005.md` Section 4.2.2, Acceptance Criteria 1) | `src/graphrag/traversal.py` contains zero handling for $N = 1$ anchor queries when only a State or non-paired entity is passed. | Querying a single state like `STATE-NY` (*"What covers New York?"*) crashes with `TraversalError` instead of retrieving the regional contractor (`JURIS-DME-A`), governing `ChangeRequest`, `CoveragePolicy`, and non-rural NY fee schedule entries. |
| **DEF-03** | Universal 14-Node Entity Resolution ($N \ge 1$) (`functional_specification_005.md` Section 4.1 Items 1 & 2) | `EntityAnchorLinker` in `src/graphrag/entity_linker.py` only parses 4 hardcoded slots: `state`, `diagnosis`, `policy`, `hcpcs`. `ResolvedAnchors` in `src/graphrag/models.py` only defines fields for these 4 slots. | The linker cannot resolve anchors across the remaining 10 node types in the database (`Jurisdiction`, `ChangeRequest`, `CoveragePolicy`, `Bill`, `PublicLaw`, `StatutorySection`, `Regulation`, `FeeScheduleEntry`, `LobbyingFiling`, `LiteratureStudy`). |
| **DEF-04** | Prohibition of Arbitrary Fallbacks / Silent Defaults (`functional_specification_005.md` Section 5 Item 1, `RULE[user_global]`) | `GraphRAGPipeline.execute_query` in `src/graphrag/pipeline.py#L53-L58` defaults `state_code = "WI"` when no state anchor is present. | Violates `INV-FAIL-FAST` and zero-fallback mandate by injecting Wisconsin state fees into queries for other jurisdictions or unanchored queries. |
| **DEF-05** | Dynamic Structured Context Assembly for Any Entity Set (`functional_specification_005.md` Section 4.3) | `GraphContextAssembler` in `src/graphrag/context_assembler.py#L27-L29, L69-L80` contains hardcoded LTA fallbacks (`[POLICY-LTA] Lymphedema Treatment Act`) and hardcoded fee filters for `A6522` in Wisconsin. | Fails to format clean, dynamic context blocks when traversing non-LTA policies or single-state subgraphs (such as New York allowable rates). |
| **DEF-06** | Canvas Node Click Assistant Drawer Integration (`functional_specification_005.md` Section 3, Section 4.5) | Clicking "INQUIRE IN GRAPHRAG CHAT" in `NodeDetailDrawer.tsx` or submitting single node PKs to `/api/graphrag/subgraph` in `routes.py#L286-L352` maps single PKs to slot `"entity"` and calls `extract_connecting_subgraph`, which fails with `TraversalError`. | Single-node canvas inspection crashes the assistant drawer instead of retrieving surrounding relationships. |
| **DEF-07** | Test Suite Validation for Single-Entity & Dynamic Topologies (`functional_specification_005.md` Section 6 Acceptance Criteria 1 & 3) | `tests/test_graphrag_pipeline.py` and `tests/test_api_endpoints.py` only test the three pre-baked combinations. | No test cases exist verifying single-state queries (`STATE-NY`), single-jurisdiction inquiries, or dynamic traversal across arbitrary starting entity sets. |

---

## 5. Sufficiency & Scan Certification

In strict accordance with the evaluation parameters in [`LANGUAGE.md`](LANGUAGE.md):

- **`{sufficient}` Certification:** The static scan of the codebase and active read-only reconnaissance of external datasources are complete, exhaustive, and rigorously verified. Every qualified codebase component touching `functional_specification_005.md` has been cataloged under its verbatim symbol and file path. Every candidate external endpoint (Hugging Face Model & Router APIs, Neo4j Graph Database, GPO GovInfo, Federal Register, eCFR, and NLM APIs) has been actively probed and empirically audited, with 21 raw unedited payload files captured in `assets/20261013T155419-714-niq1/`. Zero ambiguity remains regarding the existing dependency cone, external contracts, or observed system behaviors.
- **Zero Invention Guarantee:** In accordance with `INV-ABSENCE-01`, no missing components, traversal algorithms, or API endpoints have been simulated, assumed, or hallucinated. All functional gaps are registered in the Explicit Deficiency Register.

---

## 6. Handoff Manifest Affirmation

In strict compliance with `INV-HANDOFF-01` and `INV-MANIFEST-OVERWRITE-01`:
- Directory `handoff/20261013T155419-714-niq1/` was verified and created.
- File [`handoff/20261013T155419-714-niq1/plan-scan-1.txt`](handoff/20261013T155419-714-niq1/plan-scan-1.txt) was atomically overwritten.
- It contains exclusively the exact repository-relative paths of all qualified codebase components, the authored scan report, and all 21 captured ground-truth payload files in `assets/20261013T155419-714-niq1/`.
- Predecessor manifest `handoff/authored.txt` and all other run directories remain completely intact.
- Zero seed paths are recorded in `handoff/20261013T155419-714-niq1/plan-scan-1.txt`.

---

## 7. Coding Gate Affirmation

**DO NOT CODE YET: Implementation coding gate remains locked. Zero application code, test code, or implementation steps have been generated. Coding waits on an empty frontier and explicit operator authorization.**
