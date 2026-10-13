# Functional Specification: Visualizer UI Controls, Canvas Stability, and External Government Links

**Document ID:** `functional_specification_006.md`  
**Status:** Requirements Specification  
**Implementation Guidance:** Strictly Prohibited (DO NOT CODE YET)  
**Taxonomy Reference:** [LANGUAGE.md](file:///Users/diesel/Desktop/LAG/LANGUAGE.md)

---

## 1. Objective and Problem Statement

This specification defines the functional requirements for four frontend and visualizer improvements:
1. Removing the redundant physics toggle button from the navigation toolbar.
2. Converting the Blueprint Telemetry HUD into a collapsible accordion to eliminate visual overlap with toolbar controls.
3. Stabilizing canvas node behavior during hover so nodes remain stationary and easy to click.
4. Auditing and fixing all external reference links across all entity types so they navigate to active, valid government web pages.

---

## 2. Taxonomy and Evaluation Terms

All evaluations must adhere strictly to [LANGUAGE.md](file:///Users/diesel/Desktop/LAG/LANGUAGE.md):

* **`{errors}`:** Visual overlap between UI panels, cursor repulsion that prevents node selection, clicking dead/404/invalid links (such as the CMS MCD "Invalid Article Version" error), or console errors during canvas interaction.
* **`{correctness}`:** UI panels render cleanly without overlapping; nodes remain stable under cursor hover; external links navigate directly to valid, live government records matching the selected entity.
* **`{functionality}`:** An uncluttered, stable visualizer interface where users can freely inspect network telemetry, hover and select nodes without jitter or movement, and open verified government source documentation for any entity.
* **`{correct required outputs}`:**
  1. Top toolbar without the "Freeze Physics" button.
  2. A collapsible Blueprint HUD accordion that can be toggled open or closed without covering toolbar menus.
  3. Stationary canvas nodes during cursor hover and selection.
  4. Dynamic, working external links for all entity types (bills, laws, regulations, coverage policies, change requests, procedure codes, diagnosis codes, and jurisdictions).
* **`{sufficient}`:** Complete specification of expected UI states, layout behaviors, link target contracts, and acceptance criteria without implementation instructions.
* **`{insufficient}`:** Any ambiguity requiring assumptions about layout positioning, link URL formatting, or hover stabilization.

---

## 3. Comparison: Current Behavior vs. Desired Behavior

| Feature Area | Current Functionality | Desired Functionality |
| :--- | :--- | :--- |
| **Physics Toggle Control** | The top navigation bar contains a button labeled "FREEZE PHYSICS" / "UNFREEZE". | The button is completely removed. The simulation settles automatically and stays stable without requiring manual toggle controls. |
| **Blueprint Telemetry HUD** | Fixed panel positioned at the top-left that collides and overlaps with the top dropdowns ("JURISDICTION", "POLICY", "GRAPHRAG CHAT") on smaller screens. | The HUD is an accordion panel. Users can collapse it to a compact header bar or expand it to view node/edge counts and FPS, ensuring zero overlap with toolbar controls. |
| **Node Hover Behavior** | Hovering the cursor near or over a node causes the node to push away or move, making it frustrating and difficult to click. | Hovering over a node does not move or repel the node. Nodes remain stationary under the cursor, and clicking is immediate and reliable. |
| **External Government Links** | Links are either hardcoded mock URLs or badly formatted, producing dead links or error pages (e.g., CMS MCD shows *"Invalid Article Version"*). | Every entity type dynamically generates a verified, live government link derived from its specific properties (e.g., Congress.gov bill page, GPO Public Law page, active CMS MCD article search/view page, Federal Register page). |

---

## 4. Functional Requirements

### 4.1. Removal of Physics Toggle Button
1. **Toolbar Cleanup:** The navigation bar must no longer display the "Freeze Physics" or "Unfreeze" button.
2. **Autonomous Stabilization:** The graph layout must allow forces to naturally settle into a stable configuration upon loading.

---

### 4.2. Collapsible Blueprint HUD Accordion
1. **Collapsible State:** The "LAG KNOWLEDGE BLUEPRINT HUD" must function as an accordion with two display states:
   * **Collapsed State:** Displays only a compact header badge (e.g., `◈ BLUEPRINT HUD [▼]`) occupying minimal screen space.
   * **Expanded State:** Displays the full telemetry panel (total nodes, total edges, FPS counter, and current exploration/illuminated status).
2. **Zero Overlap:** The HUD panel must never obscure or overlap the top navigation toolbar dropdowns or chat trigger buttons at any standard screen resolution.
3. **Toggle Persistence:** Clicking the HUD header toggles between collapsed and expanded states cleanly.

---

### 4.3. Canvas Node Hover & Interaction Stability
1. **Zero Repulsion on Hover:** Moving the mouse cursor over or near a node must not apply a repulsive force or displace the node's position.
2. **Stable Click Targeting:** The node must remain stationary under the cursor so that single-click selection in the canvas succeeds on the first attempt.
3. **Cursor Feedback:** The mouse cursor must switch to a pointer when hovering over a node without disturbing the node or adjacent nodes.

---

### 4.4. Systematic External Government Link Audit and Resolution
The system must generate valid, live destination URLs for every node entity type displayed in the node detail drawer:

1. **Coverage Policies (`CoveragePolicy`):**
   * Link must resolve to the active, live CMS Medicare Coverage Database page for the specific policy article (e.g., `A59508`), eliminating the "Invalid Article Version" failure.
2. **Public Laws (`PublicLaw`):**
   * Link must navigate directly to the official GPO GovInfo or Congress.gov enacted law record matching the law number (e.g., Public Law 117-328).
3. **Federal Legislation (`Bill`):**
   * Link must navigate directly to the Congress.gov legislative record matching the specific Congress and bill number (e.g., H.R. 3630, H.R. 2617).
4. **Federal Regulations (`Regulation`):**
   * Link must navigate directly to the Federal Register Final Rule page matching the document number (e.g., 88 FR 77676 / Document 2023-24455).
5. **Statutory Sections (`StatutorySection`):**
   * Link must navigate to the official Legal Information Institute (LII) or US Code GPO page matching the title and section cited (e.g., 42 U.S.C. § 1395x).
6. **Change Requests (`ChangeRequest`):**
   * Link must navigate to the official CMS transmittal document or CMS Transmittals index for the specific Change Request number (e.g., CR 13286).
7. **Regional Contractors (`Jurisdiction`):**
   * Link must navigate to the official DME MAC contractor portal (e.g., CGS Administrators for Jurisdiction B/C, Noridian Healthcare Solutions for Jurisdiction A/D).
8. **Clinical Procedure Codes (`HCPCSCode`):**
   * Link must navigate to the official CMS HCPCS coding or DMEPOS fee schedule reference page for the specific code (e.g., A6522).
9. **Clinical Diagnoses (`ICD10Code`):**
   * Link must navigate to the official CDC/CMS ICD-10-CM clinical code database for the specific diagnosis code (e.g., I97.2).
10. **Lobbying Filings (`LobbyingFiling`):**
    * Link must navigate to the official Senate Office of Public Records (SOPR) Lobbying Disclosure Database.

---

## 5. Acceptance Criteria

The implementation will be considered complete and `{sufficient}` when:

1. **Toolbar Cleanliness:** The top toolbar contains only the Jurisdiction selector, Policy selector, and GraphRAG Assistant trigger. The "Freeze Physics" button is absent.
2. **HUD Accordion Functionality:** Clicking the Blueprint HUD header collapses and expands the panel smoothly. In both states, it does not overlap or block top controls.
3. **Stationary Hover Interaction:** Moving the cursor over any node on the canvas leaves the node firmly in place, allowing immediate click selection without cursor evasion.
4. **100% Live Link Resolution:** Clicking the external source link in the detail drawer for every entity type opens a valid, live government web page in a new browser tab with zero 404s, zero parameter error screens, and zero dead links.
