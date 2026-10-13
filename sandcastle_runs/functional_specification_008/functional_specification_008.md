# Functional Specification: Dual Jurisdiction and State Governance Architecture

**Document ID:** `functional_specification_008.md`  
**Status:** Requirements Specification  
**Implementation Guidance:** Strictly Prohibited (DO NOT CODE YET)  
**Taxonomy Reference:** [LANGUAGE.md](file:///Users/diesel/Desktop/LAG/LANGUAGE.md)

---

## 1. Objective and Problem Statement

This specification defines the functional requirements for cleanly separating and supporting **both Regional Medicare Jurisdictions (DME MACs)** and **Individual Geographic States** across the graph visualization, data filtering API, and GraphRAG retrieval pipeline.

### The Problem
Currently, the application conflates regional Medicare Jurisdictions with individual States:
1. **Misleading UI Filter:** The top navigation bar features a single dropdown labeled `"JURISDICTION:"` that actually filters by State, yet only lists 5 arbitrary states (`WI`, `IL`, `CA`, `NY`, `TX`), completely omitting the remaining 45 states.
2. **Missing Jurisdiction Filtering:** Users cannot filter the visual canvas or query the pipeline by actual CMS DME MAC Jurisdictions (Jurisdiction A, B, C, or D).
3. **Domain Confusion:** In Medicare Part B Durable Medical Equipment (DMEPOS), **Jurisdictions** are regional administrative zones operated by multi-state contractors (Noridian and CGS), whereas **States** are geographic jurisdictions that anchor localized fee schedule payment rates. Conflating them breaks user navigation and prevents regional analysis.

### The Desired Solution
The application must provide first-class, independent, and synchronized support for **both** entities:
1. **CMS DME MAC Jurisdictions:** Full operational support for all 4 regional zones (`Jurisdiction A`, `Jurisdiction B`, `Jurisdiction C`, `Jurisdiction D`) and their assigned contractors (Noridian and CGS).
2. **50 Geographic States:** Complete support for all 50 US States and territories, linking each state to its governing regional contractor and local fee schedule rates.
3. **Synchronized UI Controls:** Clear, distinct controls for both `JURISDICTION` and `STATE` that dynamically synchronize with the visual canvas and GraphRAG intelligence terminal.

---

## 2. Taxonomy and Evaluation Parameters

All evaluations must conform strictly to [LANGUAGE.md](file:///Users/diesel/Desktop/LAG/LANGUAGE.md):

* **`{errors}`:** Selecting any state or jurisdiction results in an unhandled exception, empty canvas, missing fee schedules, disconnected state nodes, or incorrect contractor-to-state mapping.
* **`{correctness}`:** Every state maps strictly to its legally assigned DME MAC contractor in accordance with CMS regulations; fee schedules for any selected state load accurate dollar amounts; regional jurisdiction filters display all constituent states.
* **`{functionality}`:** Users can seamlessly explore policy data at either the macro regional level (Jurisdictions A, B, C, D) or the micro geographic level (all 50 individual States), with both controls accurately reflected in canvas visualization and GraphRAG answers.
* **`{correct required outputs}`:**
  1. A dedicated `JURISDICTION` selector with options for All Jurisdictions, Jurisdiction A (Noridian), Jurisdiction B (CGS), Jurisdiction C (CGS), and Jurisdiction D (Noridian).
  2. A dedicated `STATE` selector providing access to all 50 US states, dynamically cascading based on the selected jurisdiction.
  3. API endpoints accepting both `jurisdiction_filter` and `state_filter` parameters independently.
  4. GraphRAG pipeline correctly answering questions at both regional contractor levels and state payment levels.
* **`{sufficient}`:** Complete specification of jurisdiction-to-state mapping rules, filtering behaviors, API contracts, and user interactions without implementation guidance.
* **`{insufficient}`:** Any ambiguity regarding state assignment, cascading selector behavior, or fee schedule expansion.

---

## 3. Comparison: Current Behavior vs. Desired Behavior

| Feature Area | Current Functionality | Desired Functionality |
| :--- | :--- | :--- |
| **Control Organization** | A single dropdown labeled `"JURISDICTION:"` that actually filters by State code. | Two separate, clearly labeled selectors: **`JURISDICTION`** (macro regional contractor) and **`STATE`** (micro payment geography). |
| **Jurisdiction Options** | None. Cannot filter by actual CMS DME MAC Jurisdictions (A, B, C, or D). | Full support for all 4 CMS DME MAC Jurisdictions: Jurisdiction A (Northeast), B (Midwest), C (South), and D (West). |
| **State Coverage** | Only 5 hardcoded states are available (`WI`, `IL`, `CA`, `NY`, `TX`). The other 45 states are inaccessible. | All 50 US States and territories are available for selection and visualization. |
| **Filter Synchronization** | Selecting a state does not update or communicate regional contractor boundaries. | Cascading synchronization: Selecting a Jurisdiction filters the State dropdown to only states in that region; selecting a State highlights its parent Jurisdiction. |
| **Canvas Topology Filtering** | Backend only filters by `state_filter`; cannot request an entire regional jurisdiction subgraph. | Backend supports filtering the canvas by either `jurisdiction_filter` (showing the contractor and all its covered states) or `state_filter`. |
| **GraphRAG Inquiries** | Queries asking about a contractor or jurisdiction alone fail or return incomplete context. | The GraphRAG pipeline natively answers regional contractor questions (e.g., *"What policies does CGS administer?"*) and state fee questions (e.g., *"What is covered in Ohio?"*). |

---

## 4. Authoritative Regional Jurisdiction and State Mapping

The system must strictly maintain the official CMS DMEPOS contractor regional boundary assignments:

| Jurisdiction ID | Official Name | Awarded Contractor | Assigned States and Territories |
| :--- | :--- | :--- | :--- |
| **`JURIS-DME-A`** | Jurisdiction A | **Noridian Healthcare Solutions** | Connecticut, Delaware, District of Columbia, Maine, Maryland, Massachusetts, New Hampshire, New Jersey, New York, Pennsylvania, Rhode Island, Vermont (12 jurisdictions). |
| **`JURIS-DME-B`** | Jurisdiction B | **CGS Administrators, LLC** | Illinois, Indiana, Kentucky, Michigan, Minnesota, Ohio, Wisconsin (7 states). |
| **`JURIS-DME-C`** | Jurisdiction C | **CGS Administrators, LLC** | Alabama, Arkansas, Colorado, Florida, Georgia, Louisiana, Mississippi, New Mexico, North Carolina, Oklahoma, South Carolina, Tennessee, Texas, Virginia, West Virginia, Puerto Rico, U.S. Virgin Islands (17 jurisdictions). |
| **`JURIS-DME-D`** | Jurisdiction D | **Noridian Healthcare Solutions** | Alaska, Arizona, California, Hawaii, Idaho, Iowa, Kansas, Missouri, Montana, Nebraska, Nevada, North Dakota, Oregon, South Dakota, Utah, Washington, Wyoming, American Samoa, Guam, Northern Mariana Islands (20 jurisdictions). |

---

## 5. Functional Requirements

### 5.1. UI Navigation Controls

#### Requirement 5.1.1: Dedicated Jurisdiction Selector
1. **Control Label:** Must be clearly labeled `JURISDICTION:`.
2. **Options:**
   * `All Jurisdictions (National Overview)`
   * `Jurisdiction A (Northeast - Noridian)`
   * `Jurisdiction B (Midwest - CGS)`
   * `Jurisdiction C (South - CGS)`
   * `Jurisdiction D (West - Noridian)`
3. **Behavior upon Selection:**
   * Filtering to a specific Jurisdiction highlights the regional contractor node (`JURIS-DME-*`) and all states linked via `COVERS_STATE`.
   * The State selector dynamically filters to show only the states assigned to that jurisdiction.

#### Requirement 5.1.2: Dedicated State Selector
1. **Control Label:** Must be clearly labeled `STATE:`.
2. **Options:**
   * `All States (Overview)`
   * An alphabetical list of all 50 US States (plus DC and territories).
3. **Behavior upon Selection:**
   * Selecting a State loads and visualizes that specific state's node and expands its local fee schedule payment entries (`FeeScheduleEntry`).
   * The Jurisdiction selector automatically updates to reflect the parent regional jurisdiction that legally covers the chosen state.

---

### 5.2. Backend Data Filtering and Graph Topology

#### Requirement 5.2.1: Multi-Tier Topology Filtering
1. **Independent Parameters:** The `/api/graph/topology` endpoint must accept both `jurisdiction_filter` and `state_filter` as optional query parameters.
2. **Jurisdiction-Level Filter:**
   * When `jurisdiction_filter` is provided (e.g., `JURIS-DME-B`), the endpoint returns the root policy, governing change requests, coverage policies, the regional contractor node, and all states legally covered by that contractor.
   * Fee schedule entries for the jurisdiction remain collapsed unless an individual state is selected or explicitly requested.
3. **State-Level Filter:**
   * When `state_filter` is provided (e.g., `OH` or `NY`), the endpoint returns the state, its parent regional contractor, the governing change request/coverage policy, and all localized non-rural fee schedule entries for that state.
4. **National Overview:**
   * When both filters are set to `All`, the endpoint returns the complete national macro graph (all 4 jurisdictions and all 50 states) with fee schedules collapsed, maintaining smooth 60 FPS viewport rendering.

---

### 5.3. GraphRAG Pipeline Integration

#### Requirement 5.3.1: Regional Administrative Queries
1. The pipeline must natively handle questions framed at the regional contractor level without requiring a state or diagnosis code:
   * Example: *"What states does Jurisdiction B cover?"*
   * Expected Outcome: The system anchors to `JURIS-DME-B`, retrieves all 7 midwestern states connected via `COVERS_STATE`, and synthesizes a complete answer naming CGS Administrators and all 7 states.
2. Example: *"Who administers Medicare Part B DME claims in Texas?"*
   * Expected Outcome: The system anchors to `STATE-TX`, traverses to `JURIS-DME-C`, and identifies CGS Administrators under operational change request `CMS-CR-13286`.

#### Requirement 5.3.2: Cross-Jurisdiction Comparisons
1. The pipeline must support comparative inquiries across regional boundaries:
   * Example: *"Compare allowable rates for A6522 between California and New York."*
   * Expected Outcome: The system anchors to `HCPCS-A6522`, `STATE-CA`, and `STATE-NY`, traverses through Jurisdiction D (Noridian) and Jurisdiction A (Noridian), and reports the specific fee schedule rates for both states.

---

## 6. Acceptance Criteria

The implementation will be considered complete and `{sufficient}` when:

1. **Dual Selectors Present and Labeled:** The top toolbar features two distinct, clearly labeled dropdowns: `JURISDICTION` and `STATE`.
2. **50-State Access:** Users can select any of the 50 US States from the state dropdown, and the canvas successfully loads that state without errors.
3. **Accurate Regional Assignment:** Selecting any state automatically reflects its correct governing CMS DME MAC contractor (e.g., selecting Ohio displays Jurisdiction B / CGS; selecting New York displays Jurisdiction A / Noridian).
4. **Jurisdiction Cascading:** Selecting `Jurisdiction B` limits the state dropdown to the 7 Midwestern states (IL, IN, KY, MI, MN, OH, WI).
5. **Macro Performance Guarantee:** Loading the national overview (All Jurisdictions, All States) maintains 60 FPS canvas rendering by default by keeping fee schedule nodes collapsed until a specific state is targeted.
6. **GraphRAG Regional Accuracy:** Submitting inquiries about either a regional jurisdiction (e.g., *"What is Jurisdiction B?"*) or an individual state (e.g., *"What contractor covers Florida?"*) returns accurate, grounded answers citing the correct contractor and transmittal IDs.
