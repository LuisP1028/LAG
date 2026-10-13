# Functional Specification: Node Detail Contextual Inquire Action and Targeted GraphRAG Execution

**Document ID:** `functional_specification_007.md`  
**Status:** Requirements Specification  
**Implementation Guidance:** Strictly Prohibited (DO NOT CODE YET)  
**Taxonomy Reference:** [LANGUAGE.md](file:///Users/diesel/Desktop/LAG/LANGUAGE.md)

---

## 1. Objective and Problem Statement

This specification defines the functional requirements for refining the **"INQUIRE IN GRAPHRAG CHAT"** action button located in the node detail inspection drawer.

### The Problem
Currently, clicking the "INQUIRE IN GRAPHRAG CHAT" button in the node detail drawer only opens the chat drawer. It does not submit an inquiry, does not pass the selected node's identity to the backend, and leaves the user with an empty input box. Furthermore, if a user manually types the node's title (such as *"Consolidated Appropriations Act, 2023"*), the query fails with zero nodes illuminated because the node primary key was discarded rather than passed to the retrieval engine.

### The Desired Solution
Clicking "INQUIRE IN GRAPHRAG CHAT" must act as an active, one-click intelligence trigger. It must automatically open the chat interface, submit a contextual inquiry focused on the selected node, pass the node's explicit primary key (`primary_key`) to the GraphRAG pipeline, retrieve the connected graph lineage from Neo4j, and render the grounded LLM synthesis while illuminating the active path on the canvas.

---

## 2. Taxonomy and Evaluation Parameters

All evaluations must adhere strictly to [LANGUAGE.md](file:///Users/diesel/Desktop/LAG/LANGUAGE.md):

* **`{errors}`:** Clicking the button fails to open the drawer, fails to submit the query, causes unhandled runtime exceptions, returns zero illuminated nodes for an existing graph node, or drops the node's primary key identifier during API dispatch.
* **`{correctness}`:** The action correctly binds the selected node's primary key and title, passes them to the backend, extracts its true connected lineage in Neo4j, and renders an accurate explanation without data loss.
* **`{functionality}`:** Seamless end-to-end user workflow where selecting any entity on the visualizer canvas and clicking "INQUIRE IN GRAPHRAG CHAT" immediately produces a grounded, conversational analysis of that entity and illuminates its path on the canvas.
* **`{correct required outputs}`:**
  1. Automated opening of the chat drawer.
  2. Immediate insertion of a formatted user inquiry referencing the node.
  3. Retrieval of the node's connected subgraph with non-zero illuminated nodes.
  4. Grounded LLM response explaining the entity's regulatory, clinical, or payment role.
  5. Real-time canvas illumination highlighting the selected node and its connected relationships.
* **`{sufficient}`:** Complete specification of user interaction workflows, input payloads, event triggers, and acceptance criteria without implementation instructions.
* **`{insufficient}`:** Any ambiguity requiring assumptions about button behavior, query formatting, or state passing.

---

## 3. Comparison: Current Behavior vs. Desired Behavior

| Feature Area | Current Functionality | Desired Functionality |
| :--- | :--- | :--- |
| **Button Action** | Purely passive: executes a state toggle that only opens the right-hand chat drawer. | Active workflow trigger: opens the chat drawer **and immediately dispatches** a targeted GraphRAG query for the selected node. |
| **Node Identity Passing** | **Node ID is discarded.** The chat drawer opens with a blank text input, forcing the user to re-type the entity name. | **Node ID is preserved.** The selected node's `primary_key` (e.g., `PLAW-117-328`) is passed directly to the backend as an explicit anchor. |
| **Inquiry Text Generation** | None. The user must manually write a prompt or pick an unlinked quick prompt. | The system automatically constructs and submits a relevant prompt referencing the entity (e.g., *"Explain the statutory and operational role of [PLAW-117-328] (Consolidated Appropriations Act, 2023)"*). |
| **Graph Retrieval Outcome** | Manual queries often return `0 Nodes Illuminated` because backend regexes fail to recognize entity titles from raw text. | Traversal starts directly from the verified `primary_key`, reliably illuminating the active node and its connected lineage on the canvas. |
| **User Experience** | Fragmented: selecting a node and clicking "Inquire" leaves the user stranded with no answer. | One-click intelligence: selecting a node and clicking "Inquire" delivers an immediate synthesized analysis and highlighted canvas path. |

---

## 4. Functional Requirements

### 4.1. Trigger and Event Workflow
1. **Selection Precondition:**
   * The "INQUIRE IN GRAPHRAG CHAT" button is active whenever any node on the blueprint canvas is selected and displayed in the node detail drawer.
2. **One-Click Execution:**
   * When clicked, the system must perform the following actions sequentially and automatically:
     1. Open the GraphRAG chat drawer if it is currently closed.
     2. Construct an inquiry prompt tailored to the selected node's label and name (e.g., *"Explain the regulatory and coverage role of [CMS-MCD-A59508]"*).
     3. Append the inquiry message to the chat message history as a user message with the current timestamp.
     4. Display a loading indicator in the chat thread showing that graph traversal and synthesis are in progress.
     5. Dispatch the query to the backend, transmitting both the query text and the explicit anchor identifier (`primary_key`).
     6. Upon receiving the response, render the assistant's answer and telemetry badge in the chat thread.
     7. Trigger canvas illumination focusing on the retrieved active subgraph.

---

### 4.2. Query Construction by Entity Classification
The automatic inquiry text must be clear, concise, and contextually appropriate for the node's label:

* **Public Law (`PublicLaw`):** *"Explain the statutory authority and enacted healthcare provisions of [primary_key] (name)."*
* **Federal Bill (`Bill`):** *"What is the legislative history and purpose of [primary_key] (name)?"*
* **Regulation (`Regulation`):** *"What policies and administrative instructions are implemented by [primary_key] (name)?"*
* **Coverage Policy (`CoveragePolicy`):** *"What diagnoses and procedure codes are governed by coverage article [primary_key] (name)?"*
* **Change Request (`ChangeRequest`):** *"What operational instructions and benefit categories are mandated by [primary_key] (name)?"*
* **Medicare Jurisdiction (`Jurisdiction`):** *"What states and coverage policies are administered by [primary_key] (name)?"*
* **Geographic State (`State`):** *"What Medicare contractor, coverage policies, and allowable fee schedules apply to [primary_key] (name)?"*
* **Procedure Code (`HCPCSCode`):** *"What are the coverage criteria, physician requirements, and allowable rates for [primary_key] (name)?"*
* **Diagnosis Code (`ICD10Code`):** *"What coverage policies and durable medical equipment items are authorized for diagnosis [primary_key] (name)?"*

---

### 4.3. Explicit Anchor Transmission Contract
1. **Direct Anchor Binding:**
   * The request sent to the GraphRAG backend must include the selected entity's `primary_key` as a pre-resolved anchor.
2. **Bypass Keyword Guessing:**
   * The backend must use this explicit anchor directly rather than relying on natural language text parsing or regex matching to rediscover the node.
3. **Retrieval Guarantee:**
   * The resulting retrieval must guarantee non-zero active nodes for all valid database entities.

---

### 4.4. Visualizer Canvas Synchronization
1. **Immediate Focus & Illumination:**
   * The returned active node IDs and edge keys must immediately illuminate on the canvas in amber/gold.
   * The canvas viewport must smoothly transition and frame the illuminated path.
2. **Preserved Selection:**
   * The originally selected node must remain selected or prominently badged so the user maintains visual continuity between the detail drawer, the canvas, and the chat conversation.

---

## 5. Error Boundaries and Edge Cases

1. **In-Flight Query Prevention:**
   * While an inquiry is loading, the button must show a disabled/loading state to prevent duplicate submissions from rapid repeated clicks.
2. **Successive Inquiries:**
   * If a user clicks a different node and presses "INQUIRE IN GRAPHRAG CHAT", the system must process the new inquiry as a distinct turn in the conversation thread without clearing prior messages.
3. **API Failure Handling:**
   * If the backend returns an error (e.g., model timeout or network failure), the chat thread must display a clear, formatted error message stating the exact point of failure, and the loading state must be cleared.

---

## 6. Acceptance Criteria

The implementation will be considered complete and `{sufficient}` when:

1. **One-Click Execution:** Clicking "INQUIRE IN GRAPHRAG CHAT" on any node opens the chat drawer and immediately generates an in-thread response without requiring manual typing.
2. **Non-Zero Illumination:** Inquiring about `PLAW-117-328` (Consolidated Appropriations Act, 2023) returns a synthesized explanation and illuminates the public law node and its connected statutory chain on the canvas (`> 0 Nodes Illuminated`).
3. **Correct Grounded Answer:** The synthesized answer accurately explains the entity's role using facts retrieved from Neo4j, quoting the bracketed primary key.
4. **All Entity Labels Supported:** The one-click inquiry succeeds across all 14 entity types (states, jurisdictions, policies, laws, regulations, codes, fees).
5. **Canvas Synchronization:** The active path returned by the inquiry illuminates and centers in the visualizer viewport in real time.
