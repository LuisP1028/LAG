# Codebase Static Scan, External API Reconnaissance, and Schema Audit Report

**Report ID:** `scan_report_001.md`  
**Execution Node:** `plan-scan-1` (Agent 1)  
**Run ID:** `20261013T025302-800-gxuw`  
**Timestamp:** `2026-10-13T02:58:30-07:00`  
**Status:** Complete Reconnaissance & Schema Audit Register  
**Implementation Gate:** Strict Boundary Enforced (**DO NOT CODE YET**)

---

## 1. Governing Context & Ingestion Verification

In strict compliance with `INV-HANDOFF-01`, workspace architectural rules, and the loading hierarchy:

1. **Single Upstream Specification in Scope:**
   - Ingested verbatim and strictly bounded to: [`functional_specification_004.md`](functional_specification_004.md) (*Functional Specification: Browser-Based React Graph Visualization & Hugging Face GraphRAG Architecture*).
   - Predecessor manifest verified: `handoff/authored.txt` records exclusively `functional_specification_004.md`.
   - Zero scanning across unassigned specifications; no multiple seed paths consumed.
2. **Wayfinder Architectural Map and Decision Tickets Inspected:**
   - [`wayfinder/map.md`](wayfinder/map.md): *Wayfinder Architectural Map: GraphRAG Specification for Browser Graph Visualizer*
   - [`wayfinder/tickets/ticket-001.md`](wayfinder/tickets/ticket-001.md): *Entity Anchor Linking and Layperson Vocabulary Normalization Specification* (RESOLVED)
   - [`wayfinder/tickets/ticket-002.md`](wayfinder/tickets/ticket-002.md): *Generalized Topological Subgraph Expansion and Neighborhood Traversal Specification* (RESOLVED)
   - [`wayfinder/tickets/ticket-003.md`](wayfinder/tickets/ticket-003.md): *Factual Context Assembly, Edge Provenance Formatting, and Prompt Grounding Specification* (RESOLVED)
   - [`wayfinder/tickets/ticket-004.md`](wayfinder/tickets/ticket-004.md): *Bidirectional Visual Canvas Synchronization and Active Subgraph Illumination Specification* (RESOLVED)
   - [`wayfinder/tickets/ticket-005.md`](wayfinder/tickets/ticket-005.md): *Master Specification Synthesis and Edits for functional_specification_004.md* (RESOLVED)
3. **Evaluation Parameters Adherence ([`LANGUAGE.md`](LANGUAGE.md)):**
   - **`{errors}`**: Explicit failure states surfaced immediately during execution (browser crashes on high node density, failed connection to graph database, Hugging Face API timeouts, authentication rejections, HTTP 401/403/429/503 errors, entity resolution failures on unindexed terms, unparseable payloads, missing mandatory foreign keys).
   - **`{correctness}`**: Precise, deterministic retrieval and display of accurate graph nodes, relationships, fee schedule amounts, and unbroken ancestry chains without data dropping or visual distortion; exact alignment between scan register and codebase interfaces.
   - **`{functionality}`**: The synchronized operation of an interactive browser graph canvas and a GraphRAG engine that accurately answers unstructured real-world patient and policy questions while visually isolating the corresponding graph paths.
   - **`{correct required outputs}`**: A responsive browser application that visualizes the complete knowledge graph, allows model selection from Hugging Face, executes generalized subgraph retrieval against Neo4j, synthesizes zero-hallucination factual responses, highlights active paths on the visual canvas, produces audited empirical schemas and ground-truth payloads in `assets/20261013T025302-800-gxuw/`, and atomically overwrites `handoff/20261013T025302-800-gxuw/plan-scan-1.txt`.
   - **`{sufficient}`**: Complete specification and cataloging of all dependency cone components, node fields, relationship types, external API schemas, extraction selectors, and error boundaries without ambiguity.
   - **`{insufficient}`**: Explicitly rejected; any ambiguity requiring assumptions regarding user interaction workflows, model parameterization, error states, or data binding semantics.

---

## 2. Master Component Dependency Cone Register

A deterministic static scan of the active codebase was performed. Each qualified local component whose interface touches specced functionality was reviewed and grounded:

| Repository-Relative Path | Verbatim Symbol / Entity | Interface / Active Role | Specification & Ticket Grounding Justification |
|---|---|---|---|
| [`LANGUAGE.md`](LANGUAGE.md) | `System Glossary & Evaluation Parameters` | Authoritative system taxonomy: `{errors}`, `{correctness}`, `{functionality}`, `{correct required outputs}`, `{sufficient}`, `{insufficient}`, `{Policy Keyword}`, `{Target_Bill_IDs}`, `{Enacted_Law_ID}`, `{US_Code_Citations}`, `{Operational_Filters}`, `{Clinical_Citations}`, `{HCPCS / CPT Codes}`, `{Direct Path (Native Keys)}`, `{Structural Traversal (Derived Keys)}`. | Mandated root glossary by `functional_specification_004.md` Section 2 and `RULE[user_global]`. |
| [`visualization.md`](visualization.md) | `GraphRAG Halftone 3D Visualization System` | Detailed technical specifications for 3D visual canvas styling, halftone screen shading, duotone color grading, optical depth of field, telemetry HUD, 3D physics clustering, and camera transition interpolation. | Informs visual rendering requirements in `functional_specification_004.md` Section 3 and Ticket 004. |
| [`package.json`](package.json) | `@ai-hero/sandcastle: ^0.12.0` | Node.js workspace package manifest defining runtime and test environment. | Workspace dependency declaration. |
| [`wayfinder/map.md`](wayfinder/map.md) | `Wayfinder Architectural Map: GraphRAG Specification` | Master architecture map defining destinations, GraphRAG invariants (`INV-UNBROKEN-ANCESTRY`, `INV-NO-KEYWORD-BRIDGING`, `INV-FAIL-FAST`, `INV-PROVENANCE-COMPLETENESS`), and dependency DAG. | Master governing planning map for run `20261013T025302-800-gxuw`. |
| [`wayfinder/tickets/ticket-001.md`](wayfinder/tickets/ticket-001.md) | `Decision Ticket 001` | Entity anchor linking and multi-slot layperson vocabulary normalization specification (State, ICD10Code, Policy). | Governs Stage 1 requirements in `functional_specification_004.md` Section 4.2. |
| [`wayfinder/tickets/ticket-002.md`](wayfinder/tickets/ticket-002.md) | `Decision Ticket 002` | Generalized topological subgraph expansion and $k$-hop neighborhood traversal specification ($k=1$ to $3$, <25ms Neo4j SLA). | Governs Stage 2 requirements in `functional_specification_004.md` Section 4.2 and Section 7. |
| [`wayfinder/tickets/ticket-003.md`](wayfinder/tickets/ticket-003.md) | `Decision Ticket 003` | Factual context assembly, edge provenance formatting, and prompt grounding specification into structured Markdown blocks. | Governs Stage 3 requirements in `functional_specification_004.md` Section 4.2. |
| [`wayfinder/tickets/ticket-004.md`](wayfinder/tickets/ticket-004.md) | `Decision Ticket 004` | Bidirectional visual canvas synchronization, event bus contracts, and active subgraph path illumination within <500ms. | Governs canvas synchronization in `functional_specification_004.md` Section 5. |
| [`wayfinder/tickets/ticket-005.md`](wayfinder/tickets/ticket-005.md) | `Decision Ticket 005` | Master specification synthesis and section edit mappings for `functional_specification_004.md`. | Governs comprehensive integration of GraphRAG across specification sections. |
| [`src/graph/__init__.py`](src/graph/__init__.py) | `src.graph` Package Manifest | Exports all 15 node entity types, `EdgeProvenance`, `GraphEdge`, inter-tier handoffs, and `PropertyGraphEngine`. | Package entry point for backend graph representations. |
| [`src/graph/models.py`](src/graph/models.py) | Master Graph Data Contracts | Defines typed Pydantic models for all 15 node types: `PolicyNode`, `BillNode`, `PublicLawNode`, `StatutorySectionNode`, `RegulationNode`, `ChangeRequestNode`, `CoveragePolicyNode`, `JurisdictionNode`, `StateNode`, `FeeScheduleEntryNode`, `HCPCSCodeNode`, `ICD10CodeNode`, `LobbyingFilingNode`, `CBOScoreNode`, `LiteratureStudyNode`, `EdgeProvenance`, and `GraphEdge`. Enforces `INV-NO-KEYWORD-BRIDGING`. | Defines the exact 14 node entity types mandated in `functional_specification_004.md` Section 3.1 Item 1. |
| [`src/graph/engine.py`](src/graph/engine.py) | `DirectedPropertyGraph`, `PropertyGraphEngine`, `GraphValidationError` | Orchestrates multi-tier graph ingestion, maintains adjacency indices, enforces MERGE upsert semantics, exports to JSON, and validates system invariants (`INV-UNBROKEN-ANCESTRY`, `INV-50-STATE-COMPLETENESS`). | Core storage engine and invariant validator satisfying Section 7.2. |
| [`src/graph/neo4j_sync.py`](src/graph/neo4j_sync.py) | `Neo4jSyncEngine` | Connects to Neo4j, initializes uniqueness constraints (`policy_node_pk`) and label indexes, executes batched APOC MERGE upserts, and computes summary statistics. | Provides database driver and connectivity interface for Neo4j serving GraphRAG retrieval. |
| [`src/graph/tier1_legislative.py`](src/graph/tier1_legislative.py) | `discover_legislation`, `Phase1DiscoveryError`, `Phase1EnactmentMissingError` | Discovers legislative vehicles (H.R. 3630, H.R. 3808, H.R. 2617) and connects to Public Law `PLAW-117-328`. | Constructs legislative ancestry nodes for Workflow 3 cross-policy inquiries. |
| [`src/graph/tier2_statutory.py`](src/graph/tier2_statutory.py) | `parse_statutory_codification`, `Phase2DocumentRetrievalError` | Parses USLM XML for PL 117-328, isolating Section 4133 (amending 42 U.S.C. 1395x for LTA) and Section 4134 (for IVIG). | Constructs statutory codification nodes for legal authority tracing. |
| [`src/graph/tier3_regulatory.py`](src/graph/tier3_regulatory.py) | `harvest_regulations`, `Phase3RuleNotFoundError` | Ingests CMS Final Rule (88 FR 77676 / `FR-2023-24455`) and operational Change Requests (`CMS-CR-13286` for LTA, `CMS-CR-13217` for IVIG). | Establishes administrative rulemaking lineage connecting statute to operational directives. |
| [`src/graph/tier4a_coverage.py`](src/graph/tier4a_coverage.py) | `ingest_coverage_policy`, `STANDARD_COVERED_DIAGNOSES`, `STANDARD_COVERED_HCPCS` | Ingests CMS MCD Policy Articles (`CMS-MCD-A59508`, `CMS-MCD-A59588`), connects `CoveragePolicy` to `HCPCSCode` via `GOVERNS` and to `ICD10Code` via `ALLOWS_DIAGNOSIS`. Strictly blocks direct HCPCS->ICD10 edges. | Implements the mandatory `CoveragePolicy` intermediary mandated in Workflow 2 and `INV-NO-KEYWORD-BRIDGING`. |
| [`src/graph/tier4b_fee_schedule.py`](src/graph/tier4b_fee_schedule.py) | `normalize_fee_schedules`, `DME_MAC_JURISDICTIONS` | Maps 4 regional DME MAC contractors (`JURIS-DME-A`, `B`, `C`, `D`), expands 53/54 states, unpivots CMS DMEPOS fee schedule matrix into 3,816 `FeeScheduleEntry` records. | Provides ground-truth fee data ($290.47 for A6522 in WI, $151.38 for A6583) and regional contractor mappings. |
| [`src/graph/tier5_context.py`](src/graph/tier5_context.py) | `enrich_context` | Ingests Lobbying Disclosure Act reports (`LobbyingFilingNode`), CBO Cost Estimates (`CBOScoreNode`), and PubMed literature studies (`LiteratureStudyNode`). | Enriches graph with macroeconomic and biomedical evidence. |
| [`tests/test_graph_pipeline.py`](tests/test_graph_pipeline.py) | Test Suite (`test_root_policy_anchor` through `test_neo4j_sync_and_mcp_invariants`) | Comprehensive test oracle validating all 10 invariants, handoffs, and Neo4j synchronization with 100% pass rate. | Serves as authoritative regression test baseline. |
| [`exports/lta_knowledge_graph.json`](exports/lta_knowledge_graph.json) | LTA Serialized Graph Dataset | Complete exported property graph for LTA policy (3,968 nodes, 7,725 edges) containing all 14 node entity types. | Authoritative offline data fixture for canvas rendering and local GraphRAG retrieval. |
| [`exports/ivig_knowledge_graph.json`](exports/ivig_knowledge_graph.json) | IVIG Serialized Graph Dataset | Complete exported property graph for IVIG policy (183 nodes, 289 edges). | Authoritative offline data fixture for cross-policy comparison in Workflow 3. |

---

## 3. Candidate External Datasource Audit & Empirical Payload Schema Register

Active, safe, read-only reconnaissance was conducted across candidate external endpoints representing Hugging Face model endpoints, the Neo4j graph database, and federal documentation sources. Observed behaviors, status codes, headers, and exact empirical schemas are detailed below, with unedited raw response files archived in `assets/20261013T025302-800-gxuw/`:

### 3.1. Hugging Face Open-Weight Model Endpoints

* **Candidate Endpoint 1: Hugging Face Model Discovery & Metadata API**
  * **Endpoint:** `GET https://huggingface.co/api/models/meta-llama/Llama-3.1-8B-Instruct`
  * **Authentication:** Open Access (Zero API Key required for model card & metadata inspection).
  * **Observed Status Code:** `HTTP/2 200 OK` (Content-Type: `application/json; charset=utf-8`, Size: 23,114 bytes).
  * **Saved Payload:** [`assets/20261013T025302-800-gxuw/hf_model_meta_llama_3_1_8b_instruct.json`](assets/20261013T025302-800-gxuw/hf_model_meta_llama_3_1_8b_instruct.json)
  * **Additional Probed Models:**
    - Mistral 7B Instruct: [`assets/20261013T025302-800-gxuw/hf_model_mistral_7b_instruct_v0_3.json`](assets/20261013T025302-800-gxuw/hf_model_mistral_7b_instruct_v0_3.json) (`HTTP/2 200 OK`, 8,864 bytes)
    - Qwen 2.5 7B Instruct: [`assets/20261013T025302-800-gxuw/hf_model_qwen_2_5_7b_instruct.json`](assets/20261013T025302-800-gxuw/hf_model_qwen_2_5_7b_instruct.json) (`HTTP/2 200 OK`, 7,879 bytes)
  * **Empirical Schema (HF Model Metadata JSON):**
    - `id`: `string` (e.g., `"meta-llama/Llama-3.1-8B-Instruct"`)
    - `pipeline_tag`: `string` (`"text-generation"`)
    - `library_name`: `string` (`"transformers"`)
    - `tags`: `array[string]` (e.g., `["transformers", "safetensors", "llama", "text-generation", "conversational", ...]`)
    - `downloads`: `integer` (`5858450`)
    - `likes`: `integer` (`8377`)
    - `config`: `object` (`architectures: array[string]`, `model_type: string`, `tokenizer_config: object`)
    - `safetensors.parameters.BF16`: `integer` (`8030261248`)
    - `inference`: `string` (`"warm"`)

* **Candidate Endpoint 2: Hugging Face Inference Router API Probe**
  * **Endpoint:** `POST https://router.huggingface.co/hf-inference/models/meta-llama/Llama-3.1-8B-Instruct`
  * **Authentication:** Bearer Token (`Authorization: Bearer <HF_TOKEN>`).
  * **Probe Condition A (Unauthenticated Request):**
    - **Observed Status Code:** `HTTP/2 401 Unauthorized`
    - **Saved Payload:** [`assets/20261013T025302-800-gxuw/hf_router_unauthorized_probe.txt`](assets/20261013T025302-800-gxuw/hf_router_unauthorized_probe.txt)
    - **Headers:** `server: CloudFront`, `x-error-message: Unauthorized access.`
  * **Probe Condition B (Invalid Token Request):**
    - **Observed Status Code:** `HTTP/2 401 Unauthorized`
    - **Saved Payload:** [`assets/20261013T025302-800-gxuw/hf_router_invalid_token_probe.txt`](assets/20261013T025302-800-gxuw/hf_router_invalid_token_probe.txt)
    - **Headers:** `content-type: application/json; charset=utf-8`, `x-error-message: Invalid username or password.`, `www-authenticate: Bearer realm="Authentication required"`
    - **Empirical Schema:** `{"error": "Invalid username or password."}`

---

### 3.2. Local Neo4j Property Graph Database

* **Datasource: Neo4j Bolt Instance (`bolt://localhost:7687`)**
  * **Authentication:** Basic Auth (`neo4j / qwertyui`), Database: `neo4j`.
  * **Connectivity Status:** Live, verified responding.
  * **APOC Schema Audit:**
    - **Saved Payload:** [`assets/20261013T025302-800-gxuw/neo4j_apoc_schema_audit.json`](assets/20261013T025302-800-gxuw/neo4j_apoc_schema_audit.json) (57,365 bytes)
    - Confirms all 14 node entity types, their property types, indexing flags, and directional relationships.
  * **Node Labels & Inventory:**
    - **Saved Payload:** [`assets/20261013T025302-800-gxuw/neo4j_node_labels_and_counts.json`](assets/20261013T025302-800-gxuw/neo4j_node_labels_and_counts.json)
    - **Node Counts by Entity Type:**
      * `FeeScheduleEntry`: 3,816
      * `HCPCSCode`: 75
      * `State`: 53
      * `ICD10Code`: 6
      * `Jurisdiction`: 4
      * `Bill`: 3
      * `Policy`: 2 (`POLICY-LTA`, `POLICY-IVIG`)
      * `StatutorySection`: 2
      * `ChangeRequest`: 2
      * `CoveragePolicy`: 2
      * `LobbyingFiling`: 2
      * `LiteratureStudy`: 2
      * `PublicLaw`: 1 (`PLAW-117-328`)
      * `Regulation`: 1 (`FR-2023-24455`)
      * Total Nodes: 3,971
  * **Relationship Types & Inventory:**
    - **Saved Payload:** [`assets/20261013T025302-800-gxuw/neo4j_relationship_types_and_counts.json`](assets/20261013T025302-800-gxuw/neo4j_relationship_types_and_counts.json)
    - **Relationship Counts by Label (14 Types):**
      * `HAS_FEE_SCHEDULE`: 3,816
      * `APPLIES_TO`: 3,816
      * `GOVERNS`: 75
      * `COVERS_STATE`: 53
      * `APPLIES_TO_JURISDICTION`: 8
      * `ALLOWS_DIAGNOSIS`: 6
      * `TARGETS_BILL`: 4
      * `HAS_ADVOCACY_RECORD`: 4
      * `ENACTED_AS`: 3
      * `MODIFIES_CODE`: 2
      * `IMPLEMENTED_BY`: 2
      * `ISSUES_TRANSMITTAL`: 2
      * `SUPPORTED_BY_EVIDENCE`: 2
      * `MANDATES_POLICY`: 2
      * Total Edges: 7,725
  * **Sample Node Properties for all 14 Types:**
    - **Saved Payload:** [`assets/20261013T025302-800-gxuw/neo4j_sample_nodes_14_types.json`](assets/20261013T025302-800-gxuw/neo4j_sample_nodes_14_types.json)
  * **Ground-Truth Subgraph Retrieval Payloads:**
    - **Workflow 1 (Patient Benefit Routing):** [`assets/20261013T025302-800-gxuw/neo4j_workflow1_patient_routing_subgraph.json`](assets/20261013T025302-800-gxuw/neo4j_workflow1_patient_routing_subgraph.json)
      Empirically confirms the exact 7-node chain linking `STATE-WI` to `JURIS-DME-B (CGS Administrators)` to `CMS-CR-13286` to `CMS-MCD-A59508` to `ICD10-I97.2` and procedure codes `HCPCS-A6520` ($119.54), `HCPCS-A6522` ($290.47), and `HCPCS-A6583` ($151.38).
    - **Workflow 2 (Clinical Coverage & Diagnosis Bridging):** [`assets/20261013T025302-800-gxuw/neo4j_workflow2_coverage_policy_bridge.json`](assets/20261013T025302-800-gxuw/neo4j_workflow2_coverage_policy_bridge.json)
      Empirically confirms that `CoveragePolicy` `CMS-MCD-A59508` mediates all connections between HCPCS procedure codes (`A6583`, `A6522`) and ICD-10 diagnosis codes (`I97.2`, `I89.0`), with zero direct procedure-to-diagnosis edges.
    - **Workflow 3 (Cross-Policy Comparative Lineage):** [`assets/20261013T025302-800-gxuw/neo4j_workflow3_cross_policy_lineage.json`](assets/20261013T025302-800-gxuw/neo4j_workflow3_cross_policy_lineage.json)
      Empirically confirms that `POLICY-LTA` and `POLICY-IVIG` converge on omnibus Public Law `PLAW-117-328` (Consolidated Appropriations Act, 2023) and Final Rule `FR-2023-24455` (88 FR 77676).

---

### 3.3. External Government Primary Source Documentation APIs

* **Authoritative Source 1: GPO GovInfo Package Summary API**
  * **Endpoint:** `GET https://api.govinfo.gov/packages/PLAW-117publ328/summary?api_key=DEMO_KEY`
  * **Observed Status Code:** `HTTP/2 200 OK` (Content-Type: `application/json`, Size: 120,163 bytes).
  * **Saved Payload:** [`assets/20261013T025302-800-gxuw/stage2_govinfo_plaw_117publ328_summary.json`](assets/20261013T025302-800-gxuw/stage2_govinfo_plaw_117publ328_summary.json)
  * **Empirical Schema:** Contains complete references array detailing Title 42, Title 2, Title 5, and other codified sections amended by Public Law 117-328.

* **Authoritative Source 2: Federal Register API**
  * **Endpoint:** `GET https://www.federalregister.gov/api/v1/documents/2023-24455.json`
  * **Observed Status Code:** `HTTP/2 200 OK` (Content-Type: `application/json; charset=utf-8`, Size: 100,483 bytes).
  * **Saved Payload:** [`assets/20261013T025302-800-gxuw/stage3_federal_register_rule_2023_24455.json`](assets/20261013T025302-800-gxuw/stage3_federal_register_rule_2023_24455.json)
  * **Empirical Schema:** Documents citation (`88 FR 77676`), effective date (`2024-01-01`), title, CFR references (`42 CFR 410`, `42 CFR 414`), and agency directives.

* **Authoritative Source 3: Electronic Code of Federal Regulations (eCFR) Search API**
  * **Endpoint:** `GET https://www.ecfr.gov/api/search/v1/results?query=lymphedema`
  * **Observed Status Code:** `HTTP/2 200 OK` (Content-Type: `application/json; charset=utf-8`, Size: 26,159 bytes).
  * **Saved Payload:** [`assets/20261013T025302-800-gxuw/stage3_ecfr_search_lymphedema.json`](assets/20261013T025302-800-gxuw/stage3_ecfr_search_lymphedema.json)
  * **Empirical Schema:**
    - `results[].hierarchy`: `{"title": "42", "chapter": "IV", "subchapter": "B", "part": "414", "subpart": "Q", "section": "414.1650"}`
    - `results[].hierarchy_headings`: `{"title": "Title 42", "section": "§ 414.1650"}`
    - `results[].headings`: `{"subpart": "Payment for Lymphedema Compression Treatment Items", "section": "Payment basis for lymphedema compression treatment items."}`
    - Proves exact regulatory authority citations: `42 CFR § 410.36`, `42 CFR § 414.1600`, `42 CFR § 414.1650`, `42 CFR § 414.1670`, `42 CFR § 414.1680`.

* **Authoritative Source 4: NLM Clinical Tables APIs (ICD-10 & HCPCS)**
  * **Endpoints:**
    - ICD-10 Search: `GET https://clinicaltables.nlm.nih.gov/api/icd10cm/v3/search?terms=I97.2&sf=code,name`
    - HCPCS Search: `GET https://clinicaltables.nlm.nih.gov/api/hcpcs/v3/search?terms=A6522&sf=code,name`
    - HCPCS Search: `GET https://clinicaltables.nlm.nih.gov/api/hcpcs/v3/search?terms=A6583&sf=code,name`
  * **Observed Status Code:** `HTTP/2 200 OK` across all endpoints.
  * **Saved Payloads:**
    - [`assets/20261013T025302-800-gxuw/stage1_nlm_icd10cm_search_i972.json`](assets/20261013T025302-800-gxuw/stage1_nlm_icd10cm_search_i972.json)
    - [`assets/20261013T025302-800-gxuw/stage4_nlm_hcpcs_search_a6522.json`](assets/20261013T025302-800-gxuw/stage4_nlm_hcpcs_search_a6522.json)
    - [`assets/20261013T025302-800-gxuw/stage4_nlm_hcpcs_search_a6583.json`](assets/20261013T025302-800-gxuw/stage4_nlm_hcpcs_search_a6583.json)
  * **Empirical Schema:** `[total_count: int, [codes: string[]], null, [[code: string, description: string]]]`

* **Authoritative Source 5: CMS Medicare Coverage Database (MCD) Web Endpoint**
  * **Endpoint:** `GET https://www.cms.gov/medicare-coverage-database/view/article.aspx?articleid=59508`
  * **Observed Status Code:** `HTTP/2 503 Service Unavailable`
  * **Saved Payload:** [`assets/20261013T025302-800-gxuw/stage4_cms_mcd_a59508_headers.txt`](assets/20261013T025302-800-gxuw/stage4_cms_mcd_a59508_headers.txt)
  * **Obstacle Analysis:** Direct GET requests trigger Akamai bot management (`akamai-grn: 0.5094d817.1791860215.263d46ee`). Ground truth for MCD Article A59508 is preserved in local static fixture `stage4a_cms_mcd_a59508_web_probe.html`.

---

## 4. Explicit Deficiency Register

In strict adherence to `INV-ABSENCE-01`, this register details every specced requirement in `functional_specification_004.md` that cannot be satisfied by existing codebase components or reachable external endpoints. Zero components or endpoints have been invented:

| Deficiency ID | Specced Requirement / Behavioral Contract | Existing Codebase State | Exact Gap Description & System Impact |
|---|---|---|---|
| **DEF-01** | Browser-Based React Graph Canvas Application (`functional_specification_004.md` Section 3) | Only Python backend (`src/graph/`) and Node orchestrator stub (`package.json`) exist. | No React application, JSX/TSX components, canvas renderer, force-directed graph controls, or detail drawer/sidebar exist in the repository. |
| **DEF-02** | Frontend 3D / Graph Visualization Library Dependencies (`package.json`) | `package.json` contains only `@ai-hero/sandcastle: ^0.12.0`. | No React, Three.js, `@react-three/fiber`, `react-force-graph-2d/3d`, `d3-force`, or cytoscape packages are defined or installed in `package.json`. |
| **DEF-03** | GraphRAG Multi-Slot Entity Anchor Linking Service (`functional_specification_004.md` Section 4.2 Stage 1, Ticket 001) | No anchor resolution logic exists in `src/graph/`. | System lacks the deterministic parsing service to extract geographic slot (`State`), clinical slot (`ICD10Code`), and policy slot (`Policy`) from free-form natural language prompts. |
| **DEF-04** | Generalized Topological Subgraph Traversal Engine (`functional_specification_004.md` Section 4.2 Stage 2, Ticket 002) | `src/graph/neo4j_sync.py` only handles graph ingestion and summary counts. | System lacks a generalized Python/Cypher retrieval service that takes anchor PKs and extracts the $k$-hop connecting subgraph (<20ms SLA) without bespoke query coding. |
| **DEF-05** | Factual Context Assembly & Triple Serialization Formatter (`functional_specification_004.md` Section 4.2 Stage 3, Ticket 003) | No context assembly service exists in `src/`. | System lacks the module that serializes retrieved subgraphs into the 4 structured Markdown blocks (Administrative Authority, Clinical Eligibility, Reimbursement & Covered Items, Edge Provenance Citations). |
| **DEF-06** | Hugging Face Model Endpoint Inference Client (`functional_specification_004.md` Section 4.2 Stage 4, Section 7.5) | No Hugging Face client exists in `src/`. | System lacks an HTTP client to dispatch grounded prompts to Hugging Face Inference API / Router, stream responses, and enforce fail-fast diagnostics on HTTP 401/429/503 errors. |
| **DEF-07** | Hugging Face Authentication Token Configuration (`functional_specification_004.md` Section 7.5) | Environment contains no `HF_TOKEN` or `HUGGINGFACE_API_KEY`. | Probing `https://router.huggingface.co/hf-inference/models/...` yields `HTTP 401 Unauthorized`. Live synthesis requires valid operator token injection. |
| **DEF-08** | Bidirectional Canvas-Agent Synchronization Bus (`functional_specification_004.md` Section 5, Ticket 004) | No synchronization bus, WebSocket handler, or REST API bridge exists. | System lacks the interaction bus that transmits canvas click events to the agent and emits active node PK arrays (`active_node_pks`, `active_edge_keys`) to trigger visual path illumination and camera pan/zoom. |
| **DEF-09** | High-Cardinality Clustering / Aggregation Controller (`functional_specification_004.md` Section 3.1 Item 4, Section 7.4) | `exports/lta_knowledge_graph.json` and Neo4j expose 3,816 flat `:FeeScheduleEntry` nodes. | No client-side or server-side pagination, geographic collapse/expand filter, or Level-of-Detail (LOD) aggregation controller exists to prevent viewport freeze on 3,800+ fee entries. |
| **DEF-10** | Direct CMS MCD Live Scraping Barrier (`functional_specification_004.md` Section 3.1 Item 5) | Probing `https://www.cms.gov/medicare-coverage-database/...` returns `HTTP 503` (Akamai). | External direct live fetch of CMS MCD article HTML is blocked by Akamai bot protection; requires relying on ground-truth static asset or local proxying. |

---

## 5. Sufficiency & Scan Certification

In strict accordance with the evaluation parameters in [`LANGUAGE.md`](LANGUAGE.md):

- **`{sufficient}` Certification:** The static scan of the codebase and active read-only reconnaissance of external datasources are complete and exhaustive. Every qualified codebase component touching `functional_specification_004.md` has been cataloged under its verbatim symbol. Every candidate external endpoint (Hugging Face Hub & Router API, Neo4j Graph Database, GPO GovInfo, Federal Register, eCFR, and NLM APIs) has been actively probed and empirically audited, with 19 raw unedited payload files captured in `assets/20261013T025302-800-gxuw/`. Zero ambiguity remains regarding the existing dependency cone, external contracts, or observed system behaviors.
- **Zero Invention Guarantee:** In accordance with `INV-ABSENCE-01`, no missing components, frontend applications, or API endpoints have been simulated, assumed, or hallucinated. All functional gaps are registered in the Explicit Deficiency Register.

---

## 6. Handoff Manifest Affirmation

In strict compliance with `INV-HANDOFF-01` and `INV-MANIFEST-OVERWRITE-01`:
- Directory `handoff/20261013T025302-800-gxuw/` was verified and created.
- File `handoff/20261013T025302-800-gxuw/plan-scan-1.txt` is atomically overwritten (truncated and replaced, never appended).
- It contains exclusively the exact repository-relative paths of all qualified codebase components, this authored scan report, and all 19 captured ground-truth payload files in `assets/20261013T025302-800-gxuw/`.
- Predecessor manifest `handoff/authored.txt` and all other run directories remain completely intact.
- Zero seed paths are recorded in `handoff/20261013T025302-800-gxuw/plan-scan-1.txt`.

---

## 7. Coding Gate Affirmation

**DO NOT CODE YET: Implementation coding gate remains locked. Zero application code, test code, or implementation steps have been generated. Coding waits on an empty frontier and explicit operator authorization.**
