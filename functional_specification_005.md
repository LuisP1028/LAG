# Functional Specification: Dynamic Schema-Driven GraphRAG Traversal

**Document ID:** `functional_specification_005.md`  
**Status:** Requirements Specification  
**Implementation Guidance:** Strictly Prohibited (DO NOT CODE YET)  
**Taxonomy Reference:** [LANGUAGE.md](file:///Users/diesel/Desktop/LAG/LANGUAGE.md)

---

## 1. Objective and Problem Statement

The goal of this specification is to replace the current hardcoded query routing with a dynamic, schema-driven **Graph Retrieval-Augmented Generation (GraphRAG)** engine.

### The Problem
The current graph retrieval engine relies on three hardcoded query templates wrapped in an `if/elif` block. It requires every user query to match one of three exact input combinations:
1. Both a State AND a Medical Diagnosis (e.g., Wisconsin + Postmastectomy Lymphedema).
2. Two or more Policies (e.g., LTA + IVIG).
3. A Procedure Code or a Medical Diagnosis.

If a query contains any other valid input—such as asking about a single state (`STATE-NY`), a single policy, a Medicare contractor, or clicking an individual node on the graph visualizer—the engine has no matching rule and crashes with a fatal error.

### The Desired Solution
The graph retrieval engine must operate like a genuine graph engine. Given any starting node or set of nodes (anchors) extracted from user text or canvas clicks:
* If two or more nodes are provided, it must find the connecting paths and shared ancestry between them in Neo4j.
* If a single node is provided (such as `STATE-NY`), it must find its connected administrative, legal, and pricing relationships.
* It must not use hardcoded query templates or `if/elif` slot checks to restrict which questions can be asked.
* It must feed this retrieved graph context to the Hugging Face language model to generate a factual, grounded answer.

---

## 2. Taxonomy and Evaluation Terms

All terms are evaluated against [LANGUAGE.md](file:///Users/diesel/Desktop/LAG/LANGUAGE.md):

* **`{errors}`:** System crashes, unhandled exceptions, traversal failures when querying valid database entities (such as `STATE-NY`), or API timeouts.
* **`{correctness}`:** The graph engine returns accurate nodes, relationships, and fee rates that match the actual data in Neo4j without logical flaws or guesses.
* **`{functionality}`:** The complete GraphRAG pipeline accepts any valid entity or set of entities, finds the relevant subgraph in Neo4j, sends the facts to the language model, and returns an accurate answer while highlighting the active path on the UI canvas.
* **`{correct required outputs}`:** 
  1. A graph result containing verified nodes, edges, and source provenance from Neo4j.
  2. An LLM-synthesized answer that quotes exact node IDs (e.g., `[CMS-MCD-A59508]`), public laws, and fee amounts.
  3. Visual highlighting of the active nodes and edges on the browser canvas.
  4. Immediate `HTTP 400` errors if a term does not exist in the database.
* **`{sufficient}`:** Requirements are clear, complete, and unambiguous so that implementation can proceed without guesswork.
* **`{insufficient}`:** Any ambiguity requiring assumptions about system behavior, inputs, or error states.

---

## 3. Comparison: Current Behavior vs. Desired Behavior

| Feature | Current Functionality | Desired Functionality |
| :--- | :--- | :--- |
| **Query Routing** | Three hardcoded Cypher query templates gated by `if/elif` checks. | Dynamic graph traversal based on relationships in the Neo4j schema. |
| **Single-Entity Inquiries** | **Fails and crashes:** Querying a single entity like `STATE-NY` or `POLICY-LTA` raises an unhandled `TraversalError`. | **Succeeds:** Finds the entity's direct administrative and statutory lineage (e.g., State $\rightarrow$ Contractor $\rightarrow$ Policy $\rightarrow$ Fees). |
| **Multi-Entity Inquiries** | Only works for exact pairs hardcoded for test cases (e.g., State + Diagnosis). | Finds the connecting paths between any two or more valid entities. |
| **Geographic Questions** | Fails on any state question without a diagnosis (e.g., *"What contractor covers New York?"* crashes). | Returns the regional contractor, change request, policy, and state fee schedule entries. |
| **Canvas Node Clicks** | Clicking individual nodes on the visual canvas crashes the assistant drawer. | Clicking any node retrieves its surrounding relationships and displays its details cleanly. |
| **Fallback Handling** | Previously used a blind 2-hop crawl that stripped node properties and caused 500 errors. | **Zero fallbacks.** Immediately fails fast with an explicit error only if an entity is not in the database. |
| **LLM Synthesis** | The model previously paraphrased facts and omitted exact policy codes. | The model is strictly instructed to quote exact bracketed node IDs, law numbers, and dollar amounts. |

---

## 4. Functional Requirements

### 4.1. Entity Resolution (Finding Starting Pins)
1. **Support Any Domain Entity:** The system must recognize starting nodes (anchors) across all 14 node types in the database (State, Jurisdiction, ChangeRequest, CoveragePolicy, HCPCSCode, ICD10Code, Policy, Bill, PublicLaw, StatutorySection, Regulation, FeeScheduleEntry, LobbyingFiling, LiteratureStudy).
2. **Variable Number of Inputs:** The system must accept any number of recognized entities ($N \ge 1$). It must not require a specific combination of inputs.
3. **Fail Fast on Unknown Inputs:** If a user asks about an unindexed location (e.g., "Atlantis") or condition (e.g., "diabetes"), the system must immediately return an `EntityResolutionError` explaining that the term is not in the database.

---

### 4.2. Dynamic Graph Traversal

#### 4.2.1. When Two or More Entities Are Provided ($N \ge 2$)
* **Find Connecting Paths:** The engine must query Neo4j for the connecting paths between the entities.
* **Respect Coverage Policy Rules (`INV-NO-KEYWORD-BRIDGING`):** Procedure codes (`HCPCSCode`) and diagnosis codes (`ICD10Code`) must connect through an authorizing `CoveragePolicy`. Direct links between procedure codes and diagnoses are prohibited.
* **Include Regulatory Context:** The retrieved path must include the intermediate legal and administrative nodes (Public Law, Regulation, Change Request, Jurisdiction) that connect the entities.

#### 4.2.2. When a Single Entity Is Provided ($N = 1$)
* **Trace Legal and Administrative Lineage (`INV-UNBROKEN-ANCESTRY`):** The engine must trace connected paths upward to authorizing laws/policies and downward to operational guidelines.
* **State Entity Behavior:** If the input is a single State (e.g., `STATE-NY`), the engine must retrieve:
  1. The regional Medicare contractor (`Jurisdiction`) that covers the state via the `COVERS_STATE` edge.
  2. The governing `ChangeRequest` and `CoveragePolicy`.
  3. The non-rural fee schedule entries for that state.
* **Clinical Entity Behavior:** If the input is a single procedure code or diagnosis code, the engine must retrieve its governing `CoveragePolicy` and related allowable items.

#### 4.2.3. Audit Provenance (`INV-PROVENANCE-COMPLETENESS`)
Every edge returned by the graph traversal must retain its provenance metadata:
* `source_uri`: Official government source link.
* `selector`: Direct pointer or selector used during data ingestion.
* `ingestion_timestamp`: Timestamp when the data was loaded.
* `run_id`: Pipeline execution ID.

---

### 4.3. Context Assembly for the LLM
The system must format the retrieved graph nodes and edges into clear, structured text for the language model, organized into sections:
1. **Program Authority:** Root policies, Public Laws, and Federal Register rules.
2. **Contractor & Region:** Regional claims contractor and covered states.
3. **Clinical Criteria:** Permitted diagnoses and covered procedure codes.
4. **Fees and Patient Costs:** Allowable reimbursement amounts and calculated 20% patient coinsurance for the state.
5. **Data Sources:** Source links and transmittal IDs.

---

### 4.4. LLM Synthesis Grounding
1. **Rely Strictly on Context:** The language model must answer using only the graph facts provided in the prompt. It must not guess or extrapolate unlisted fees or coverage.
2. **Quote Exact Identifiers:** The model must explicitly cite the bracketed primary key IDs (such as `[CMS-MCD-A59508]`, `[PLAW-117-328]`, `[JURIS-DME-B]`) when mentioning policies, laws, contractors, or codes.
3. **Quote Exact Dollar Figures:** When listing prices, the model must quote the exact allowable amount (e.g., `$290.47`) and 20% coinsurance (e.g., `$58.09`).
4. **Quote Legal Citations:** When discussing legislation, the model must quote the Public Law number (e.g., `Public Law 117-328`) and Federal Register citation (e.g., `88 FR 77676`).

---

### 4.5. Canvas Illumination
1. **Return Active Graph Keys:** The API response must return the list of all node IDs and edge keys included in the retrieved path.
2. **Visual Highlighting:** The web browser canvas must highlight the active nodes and edges in amber/gold, dim unrelated nodes, and center the camera on the active path.

---

## 5. Error Boundaries and Fail-Fast Rules

1. **No Silent Fallbacks:** The system must never use blind fallback searches, silent exception catching, or canned mock answers.
2. **Missing Entity:** If a term cannot be linked to the database, return `HTTP 400` with `error_type: "EntityResolutionError"`.
3. **No Path Exists:** If two valid nodes have no connecting path in the database schema, return `HTTP 400` with `error_type: "TraversalError"`.
4. **Model API Failure:** If the Hugging Face token is missing, raise `ModelAuthenticationError`. If the remote model times out or returns an error, raise `ModelInferenceError`.

---

## 6. Acceptance Criteria

The system will be considered complete and `{sufficient}` when:

1. **Single-State Queries Succeed:** Querying *"What covers New York?"* or *"What are the allowable compression rates in New York?"* succeeds with `HTTP 200`, returning the Noridian Jurisdiction A path and New York fee schedules without error.
2. **Existing Test Oracles Pass:**
   * **Oracle 1 (Patient Routing):** Wisconsin + Postmastectomy Lymphedema returns the complete 7-node chain linking Wisconsin to ICD-10 `I97.2`, HCPCS `A6522`, and the `$290.47` rate.
   * **Oracle 2 (No Direct Procedure-Diagnosis Edges):** Direct HCPCS $\rightarrow$ ICD10 links remain strictly prohibited; all procedures link through `CoveragePolicy`.
   * **Oracle 3 (Cross-Policy Convergence):** IVIG + LTA returns their shared convergence on Public Law 117-328 and Federal Register rule 88 FR 77676.
3. **Zero Hardcoded Template Branching:** The traversal engine does not use `if/elif` statements to enforce query combinations. Retrieval is dynamically determined by Neo4j graph topology.
4. **Canvas Highlighting Works:** Active nodes and edges returned by any query illuminate accurately on the browser canvas.
5. **All Tests Pass:** The test suite executes with zero unhandled exceptions.
