# Functional Specification: Browser-Based React Graph Visualization & Hugging Face GraphRAG Architecture

**Document ID:** `functional_specification_004.md`  
**Status:** Requirements Specification  
**Implementation Guidance:** Strictly Prohibited (DO NOT CODE YET)  
**Taxonomy Reference:** Authoritative definitions defined in `LANGUAGE.md`

---

## 1. Technical Scope and Objective

This specification defines the functional requirements for a browser-based, interactive graphical visualization interface and an integrated **Graph-Augmented Retrieval Generation (GraphRAG)** conversational intelligence layer powered by Hugging Face open-weight model endpoints.

The system provides three synchronized operational capabilities:
1. **Interactive Graph Visualization:** A web-browser interface capable of rendering, navigating, filtering, and inspecting multi-tier policy property graphs (e.g., LTA, IVIG) containing thousands of nodes and directed edges across federal legislative, statutory, regulatory, operational coding, and geographic payment domains.
2. **Hugging Face GraphRAG Engine:** A generalized graph retrieval and synthesis layer that eliminates both bespoke query coding and model-generated Cypher hallucination. The engine resolves free-form natural language prompts into graph entity anchors, traverses topological neighborhoods ($k$-hop subgraphs), and feeds verified factual graph context to the LLM for grounded answer generation.
3. **Bidirectional Canvas-Agent Synchronization:** Native coupling where user actions on the visual canvas trigger conversational explanations, and the exact subgraphs retrieved by the GraphRAG pipeline dynamically illuminate and focus on the visual canvas in real time.

---

## 2. Taxonomy and Evaluation Parameters

All system evaluations must conform strictly to [LANGUAGE.md](file:///Users/diesel/Desktop/LAG/LANGUAGE.md):

* **`{errors}`:** Execution failures including browser UI crash on high node density, failed connection to the graph database, model API timeout, authentication rejection, or entity resolution failure on unindexed terms.
* **`{correctness}`:** The deterministic retrieval and display of accurate graph nodes, relationships, fee schedule amounts, and unbroken ancestry chains without data dropping or visual distortion.
* **`{functionality}`:** The synchronized operation of an interactive browser graph canvas and a GraphRAG engine that accurately answers unstructured real-world patient and policy questions while visually isolating the corresponding graph paths.
* **`{correct required outputs}`:** A responsive browser application that visualizes the complete knowledge graph, allows model selection from Hugging Face, executes generalized subgraph retrieval against Neo4j, synthesizes zero-hallucination factual responses, and highlights active paths on the visual canvas.
* **`{sufficient}`:** Complete specification of all user interactions, UI states, model interface behaviors, GraphRAG retrieval contracts, error recovery routines, and acceptance gates without ambiguous implementation instructions.
* **`{insufficient}`:** Any ambiguity requiring assumptions regarding user interaction workflows, model parameterization, error states, or data binding semantics.

---

## 3. User Interaction & Visual Presentation Requirements

### 3.1. Browser Graph Canvas Requirements
1. **Entity & Edge Rendering:**
   - The canvas must render all 14 node entity types defined in the system ontology (`Policy`, `Bill`, `PublicLaw`, `StatutorySection`, `Regulation`, `ChangeRequest`, `CoveragePolicy`, `HCPCSCode`, `ICD10Code`, `Jurisdiction`, `State`, `FeeScheduleEntry`, `LobbyingFiling`, `LiteratureStudy`).
   - The canvas must render all 14 directed relationship types with visible directional indicators (arrows) and relationship labels.
2. **Visual Hierarchy & Entity Discrimination:**
   - Each node label must possess distinct, persistent visual styling (shape, color badge, border, and size) to distinguish macro federal entities from clinical codes and microeconomic payment rates.
   - Text captions inside or alongside node circles must display human-readable names (`name` property) rather than internal system identifiers, preventing duplicate label confusion across regional contractors (e.g., displaying `JURIS-DME-B (CGS)` vs. `JURIS-DME-C (CGS)`).
3. **Canvas Navigation & Physics Controls:**
   - The viewport must support smooth pan, zoom (in/out/fit-to-screen), and node dragging.
   - The canvas must support force-directed layout stabilization with the ability to pause or lock physics simulation to avoid continuous node jitter on large topologies.
4. **Scalability & Node Clustering on High-Density Tiers:**
   - The system must gracefully handle high-cardinality clusters (specifically the 3,800+ `:FeeScheduleEntry` nodes) without browser freezing or frame rate drop.
   - The UI must provide a collapse/expand mechanism or localized geographic filtering so users can inspect macro policy lineages without mandatory clutter from thousands of concurrent fee schedule nodes.
5. **Selection & Detail Inspection Panel:**
   - Clicking any node must display a dedicated detail drawer/sidebar showing:
     - Primary key, official title, and label classification.
     - All first-class properties (e.g., fee amount, effective dates, document numbers, rural flags).
     - Plain-English scope/description of the entity.
     - Direct external source URLs (e.g., links to GPO GovInfo, Federal Register, eCFR, or CMS MCD).
     - Full list of immediate incoming and outgoing relationships with clickable neighbor navigation.

---

## 4. Hugging Face GraphRAG Architecture Requirements

### 4.1. Core Architectural Separation: No Bespoke Code, No Cypher Hallucination
The system strictly rejects both manual query coding (writing custom Cypher functions for every user question) and free-form model Cypher generation (letting the LLM guess Cypher syntax on the fly). 

Instead, the system operates as a **Generalized Graph-Augmented Retrieval Generation (GraphRAG)** engine:

```
                            1. Unstructured User Input:
             "I am from Wisconsin, survived breast cancer, need lymphedema 
                     supplies, I'm on Medicare, can you help?"
                                       │
                                       ▼
                       ┌───────────────────────────────┐
                       │    2. Entity Anchor Linking   │
                       └───────────────┬───────────────┘
                                       │
            Resolved Anchors: [State: WI, ICD10: I97.2, Policy: LTA]
                                       │
                                       ▼
                       ┌───────────────────────────────┐
                       │  3. Generalized Subgraph Hop  │
                       │    (Topological Expansion)    │
                       └───────────────┬───────────────┘
                                       │
            Extracts k-hop connecting paths between anchors:
            • JURIS-DME-B (CGS) -[:COVERS_STATE]-> State: WI
            • CoveragePolicy A59508 -[:ALLOWS_DIAGNOSIS]-> ICD10: I97.2
            • CoveragePolicy A59508 -[:GOVERNS]-> HCPCS: A6522, A6583...
            • FeeScheduleEntry -[:APPLIES_TO]-> State: WI (A6522: $290.47)
                                       │
                                       ▼
                       ┌───────────────────────────────┐
                       │ 4. Structured Context Assembly│
                       └───────────────┬───────────────┘
                                       │
            Formats verified graph facts + edge provenance into prompt context
                                       │
                                       ▼
                       ┌───────────────────────────────┐
                       │ 5. Hugging Face LLM Synthesis │
                       └───────────────┬───────────────┘
                                       │
                                       ▼
                 Grounded, Compassionate Answer to the Patient
                 + Simultaneous Path Illumination on React Canvas
```

### 4.2. GraphRAG Pipeline Execution Stages

1. **Stage 1: Entity Anchor Linking:**
   - Free-form user inputs are matched against indexed graph properties (`primary_key`, `name`, `code`, `state_code`, `description`) to identify starting node anchors.
   - Synonyms and clinical lay terms are resolved to standardized graph entities (e.g., `"breast cancer"` + `"swelling"` $\rightarrow$ `ICD10-I97.2` *Postmastectomy lymphedema syndrome*; `"Wisconsin"` $\rightarrow$ `STATE-WI`).
2. **Stage 2: Generalized Topological Subgraph Expansion:**
   - A single, generalized graph traversal algorithm extracts the connecting subgraph between identified anchors without requiring bespoke Cypher queries.
   - Retrieves the $k$-hop directed path (typically $k=1$ to $3$) linking the state, regional contractor, authorizing coverage policy, procedure codes, and local fee schedule reimbursement rates.
3. **Stage 3: Context Assembly & Prompt Grounding:**
   - The retrieved nodes, relationships, and edge provenance metadata are serialized into structured factual statements.
   - The assembled context is injected into the Hugging Face model prompt as authoritative reference material.
4. **Stage 4: Synthesis & Strict Anti-Hallucination Invariant (`INV-FAIL-FAST`):**
   - The model synthesizes a natural, plain-English response derived exclusively from the injected graph context.
   - The model is strictly forbidden from extrapolating unverified medical claims or hallucinating non-existent payment rates. If an anchor cannot be resolved in the graph, the system halts immediately and informs the user that the entity is missing from the database.
5. **Stage 5: Mandatory Provenance Citation (`INV-PROVENANCE-COMPLETENESS`):**
   - Every factual answer generated by the agent must explicitly cite the provenance metadata attached to the traversed edges (source file URI, Federal Register citation, eCFR section, or CMS transmittal number).

---

## 5. Bidirectional Canvas-Agent Synchronization Requirements

The visual graph canvas and the GraphRAG conversational engine must operate as a unified, synchronized exploration environment:

```
                    ┌───────────────────────────────┐
                    │       USER INTERACTION        │
                    └───────┬───────────────┬───────┘
                            │               │
                            ▼               ▼
               ┌─────────────────┐     ┌─────────────────┐
               │  Visual Canvas  │     │   Agent Chat    │
               │   (Click Node)  │     │  (Prompt User)  │
               └────────┬────────┘     └────────┬────────┘
                        │                       │
                        │ Emits Node PK         │ Emits Retrieved Subgraph
                        ▼                       ▼
               ┌─────────────────────────────────────────┐
               │         SYNCHRONIZATION BUS             │
               │                                         │
               │ 1. Canvas click seeds GraphRAG anchors  │
               │ 2. GraphRAG path highlights on canvas   │
               │ 3. Canvas auto-pans to focused subgraph │
               └─────────────────────────────────────────┘
```

1. **Canvas-to-Agent Interaction:**
   - Selecting any node or edge on the visual canvas seeds that entity as an active anchor in the GraphRAG engine.
   - Quick-action prompt buttons appear (e.g., *"Explain this policy"*, *"Show allowed diagnoses"*, *"List state reimbursement rates"*).
2. **Agent-to-Canvas Interaction:**
   - The exact node IDs and edge IDs retrieved in Stage 2 of the GraphRAG pipeline are emitted to the visual canvas.
   - The canvas immediately:
     - Applies an active highlight (e.g., glowing border or distinct color ring) to all traversed nodes and edges.
     - Dims unrelated nodes to draw visual focus to the active path.
     - Smoothly pans and zooms the camera viewport to frame the illuminated subgraph.

---

## 6. Functional User Workflows

### 6.1. Workflow 1: Natural Language Patient Benefit Routing
1. A patient or caregiver inputs an unstructured real-world request:
   > *"I am from Wisconsin, survived breast cancer, need lymphedema supplies, I'm on Medicare, can you help?"*
2. **GraphRAG Anchor Resolution:**
   The engine resolves anchors:
   - Geographic Scope: `STATE-WI` (Wisconsin)
   - Clinical Diagnosis: `ICD10-I97.2` (Postmastectomy lymphedema syndrome)
   - Policy Domain: `POLICY-LTA` (Lymphedema Treatment Act)
3. **Topological Subgraph Retrieval:**
   The generalized traversal engine expands the neighborhood connecting `STATE-WI` and `ICD10-I97.2`:
   $$\text{STATE-WI} \longleftarrow \text{JURIS-DME-B (CGS)} \longleftarrow \text{CMS-CR-13286} \longrightarrow \text{CMS-MCD-A59508} \longrightarrow \text{ICD10-I97.2}$$
   $$\text{CMS-MCD-A59508} \longrightarrow \text{HCPCS-A6522} \longrightarrow \text{FeeScheduleEntry} \longrightarrow \text{STATE-WI}$$
4. **Actionable Patient Guidance Output:**
   Within sub-second latency, the LLM reads the retrieved subgraph and explains:
   - The required prescription diagnosis code (`ICD-10 I97.2`).
   - Covered garment types (daytime sleeves, nighttime compression wraps).
   - Regional claims contractor name: `CGS Administrators (Jurisdiction B)`.
   - Exact allowable reimbursement rates in Wisconsin (e.g., `$290.47` for `A6522`) and the calculated 20% patient coinsurance (`$58.09`).
5. **Synchronized Canvas Highlighting:**
   The canvas immediately frames and illuminates the exact 7-node chain linking Wisconsin to Postmastectomy Lymphedema and the corresponding compression sleeves, fading unrelated states and diagnoses.

### 6.2. Workflow 2: Clinical Coverage & Diagnosis Bridging
1. User inspects a procedure code (`HCPCS-Q2052` or `HCPCS-A6583`) and queries permitted diagnoses.
2. The GraphRAG engine retrieves the intermediary `CoveragePolicy` node.
3. The agent explains the legal constraint mandated by `INV-NO-KEYWORD-BRIDGING`: Medicare law strictly forbids direct procedure-to-diagnosis connections; coverage must be legally authorized by an official CMS Policy Article.
4. Canvas highlights the `CoveragePolicy` node as the mandatory legal intermediary.

### 6.3. Workflow 3: Cross-Policy Comparative Lineage
1. User asks: *"How do IVIG and LTA converge under federal law?"*
2. The GraphRAG engine anchors `POLICY-IVIG` and `POLICY-LTA` and retrieves their shared parents:
   $$\text{POLICY-IVIG} \longrightarrow \text{BILL-117-hr-3808} \longrightarrow \mathbf{PLAW-117-328} \longleftarrow \text{BILL-117-hr-3630} \longleftarrow \text{POLICY-LTA}$$
   $$\text{PLAW-117-328} \longrightarrow \mathbf{FR-2023-24455} \longrightarrow \text{CFR Regulations}$$
3. The LLM explains how both programs were enacted under the Consolidated Appropriations Act, 2023, and finalized under the same Federal Register Final Rule.
4. Canvas highlights the shared omnibus and regulatory nodes in amber and crimson.

---

## 7. Edge Cases, Strict Invariants, and Performance Requirements

In strict accordance with system rules, the architecture rejects passive workarounds, arbitrary delays, and degraded execution states:

1. **Zero Cypher Generation by Model:**
   - Free-form, unconstrained Cypher generation by the LLM is strictly prohibited. The LLM only receives structured factual context extracted by the generalized GraphRAG engine, eliminating 100% of Cypher syntax errors and conversational retry latency.
2. **Absolute Enforcement of `INV-UNBROKEN-ANCESTRY` (Zero Orphan Tolerance):**
   - The system strictly forbids orphaned, unanchored, or disconnected entities from existing in the database or rendering on the canvas.
   - If an entity lacks a verified, directed path to its authorizing parent policy, the graph ingestion engine must abort with a fatal validation error (`GraphValidationError`) prior to visualizer loading. No "unanchored clusters" or degraded visual fallbacks are permitted.
3. **Sub-Second Response Latency SLA:**
   - GraphRAG topological subgraph retrieval must complete within single-digit milliseconds (<20ms) in Neo4j.
   - Total end-to-end response time from user prompt submission to synchronized canvas path illumination must execute within <1.5 seconds.
4. **Performance Throttling on High-Cardinality Tiers:**
   - Visual rendering must paginate or summarize the 3,800+ `:FeeScheduleEntry` nodes by default (expanding only for the user's active state or selected procedure code) to guarantee a locked 60 FPS viewport on consumer hardware.
5. **Model Endpoint Availability & Token Faults:**
   - If the Hugging Face model endpoint returns a connection failure, authentication rejection, or HTTP 5xx error, the UI must halt immediately and surface the exact telemetry error code and required remediation without swallowing exceptions.

---

## 8. Verification & Acceptance Criteria

The system will be deemed functionally complete when:
1. **Natural Language Routing Verification:** The patient query (*"I am from Wisconsin, survived breast cancer, need lymphedema supplies, I'm on Medicare"*) successfully resolves to `ICD10-I97.2`, `JURIS-DME-B`, covered `A65xx` codes, and Wisconsin fee rates within <1.5 seconds.
2. **Synchronized Highlighting:** The canvas automatically illuminates the exact 7-node chain linking Wisconsin to the LTA Coverage Policy and Postmastectomy diagnosis within 500ms of query completion.
3. **Zero Orphan Invariant (`INV-UNBROKEN-ANCESTRY`):** 100% of rendered entities connect via verified directed edges to a root `:Policy` node. Any orphan entity immediately raises a fatal validation exception.
4. **Zero Syntax Failure Rate:** 100% of graph interactions utilize generalized GraphRAG topological retrieval, achieving 0 Cypher syntax errors and 0 retry round-trips.
5. **Strict Provenance Integrity (`INV-PROVENANCE-COMPLETENESS`):** Every node detail panel and agent explanation displays verified primary source metadata and direct government source links.
