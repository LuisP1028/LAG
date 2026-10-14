# Functional Specification 017: Interactive Showcase Component Behaviors, Data Contracts, and Deployment Workflows

## 1. Objective & Scope

This specification establishes the exact desired `{functionality}` and `{correct required outputs}` for the separate deployment artifacts across GitHub Pages (Frontend) and Hugging Face (Backend). 

The goal is to deliver an external, zero-configuration interactive showcase where users can visualize the 8-hop legislative, regulatory, and procedural data engine, inspect individual nodes and relationships with complete legal and administrative provenance, and issue queries against the engine backend.

This document strictly specifies behavior, inputs, outputs, UI states, data schemas, and edge case responses without supplying implementation code, scaffolding scripts, or component code sketches.

---

## 2. Separate Repository Lifecycle & Deployment Specifications

### 2.1 Repository Setup & Topology
* **Inputs:** Desired repository name on GitHub under the authenticated user account (`LuisP1028`).
* **Desired Behavior & Outcomes:**
  - Create a completely new, clean, standalone GitHub repository.
  - The repository root must be decoupled from the primary local development workspace.
  - The repository must include:
    1. A static frontend directory or root configured to serve the interactive web application via GitHub Pages.
    2. A backend directory or standalone Hugging Face Space repository configured to run the backend API service.
    3. Clear, authoritative configuration files for automated deployment (e.g. GitHub Actions Pages workflow or branch publishing configuration).
* **Constraints & Invariants:**
  - Zero leakage of private local development history, local `.env` files, or unmasked API credentials into the public repository history.
  - All upstream external API keys (Congress.gov, Federal Register, openFEC, etc.) must remain configurable via deployment environment variables.

### 2.2 Dual-Platform Delivery Pipeline
* **GitHub Pages (Static Hosting):**
  - Host the static HTML/CSS/JS frontend application reachable publicly over standard HTTPS.
  - Must function cleanly on all standard modern desktop and mobile browsers.
* **Hugging Face Space (Compute & Backend Hosting):**
  - Host the engine service (e.g. Docker / Python application space).
  - Serve endpoints for live query dispatch, graph topology extraction, and context retrieval.
  - Include an explicit Cross-Origin Resource Sharing (CORS) policy allowing GET/POST traffic from the GitHub Pages host.

---

## 3. Detailed Frontend Interaction & Display Behaviors

### 3.1 Primary Graph Exploration Canvas
* **Inputs:** Serialized graph topology containing nodes, edges, labels, properties, and provenance metadata.
* **Desired Behavior:**
  - **Dynamic Topology Layout:** The canvas renders nodes clustered or layered across the 8 functional hops:
    1. Policy Term (`POLICY-...`)
    2. Enacted & Standalone Bills (`BILL-...`, `PLAW-...`)
    3. Statutory & US Code Codification (`STAT-...`, `USC-...`)
    4. Federal Register Final Rules & CFR Regulations (`REG-FR-...`, `CFR-...`)
    5. CMS Change Requests & Manual Transmittals (`TR-CR...`)
    6. DME MAC Local & National Coverage Policies (`DME-MAC-...`, `CMS-MCD-...`)
    7. HCPCS Procedure & ICD-10 Diagnosis Codes (`HCPCS-...`, `ICD10-...`)
    8. Fee Schedule Rates, Contractors, & Jurisdictions (`FEE-...`, `JURIS-DME-...`, `STATE-...`)
  - **User Manipulation:**
    - Zoom (mouse scroll / pinch-to-zoom) across a wide range (e.g., 0.1x to 3.0x).
    - Canvas panning with mouse drag.
    - Node dragging with auto-stabilization / physics dampening.
    - Category filtering: Toggle visibility of specific entity types (e.g. hide fee rates to view macro policy relationships, or show fee rates for deep dive).

### 3.2 Node & Edge Inspection Drawer
* **Inputs:** User clicks on an entity node or directional edge.
* **Desired Behavior & `{correct required outputs}`:**
  - Opens a responsive side panel or drawer showing:
    1. **Primary Entity Header:** Entity identifier, category badge, and canonical display title.
    2. **Extracted Attributes:** All native key-value pairs (e.g., public law number, bill introduced date, CFR part, transmittal manual publication, allowable fee amount, BETOS code).
    3. **Legal / Administrative Text Excerpt:** Direct statutory/regulatory language, policy rationale, or description text.
    4. **Verified Provenance Block:** Clickable external hyperlink to official government source (e.g. Congress.gov XML, Federal Register API/URL, CMS Transmittal PDF, GovInfo USLM) and exact structural selector/pointer.
    5. **Hop Connections List:** Direct incoming and outgoing relationships with clickable links to jump focus to neighboring nodes.

### 3.3 Interactive Query & Parameter Controls
* **Inputs:** 
  - Policy selector (dropdown of pre-indexed policy runs, such as `"LTA"`).
  - Geographic state/territory selector (covering all 50 states, DC, PR, VI, and GU).
  - Jurisdiction selector (DME MAC Jurisdictions A, B, C, D).
  - Fee schedule toggle (expand/collapse granular reimbursement rates).
* **Desired Behavior:**
  - Selecting a pre-indexed run instantly populates the graph without network lag using bundled high-fidelity snapshot payloads.
  - Submitting an ad-hoc query dispatches an asynchronous request to the Hugging Face backend.
  - UI indicates live network activity with a deterministic loading indicator and progress steps.

---

## 4. Backend Service Endpoints & Contract Specifications

### 4.1 Required API Contracts
* **`GET /health`**
  - **Outputs:** HTTP 200 OK JSON object containing:
    - `status`: `"healthy"`
    - `engine_version`: Version string
    - `loaded_policies`: Array of available cached/indexed policy keywords
* **`GET /api/graph`**
  - **Inputs:**
    - `policy` (required string): Policy keyword identifier.
    - `state` (optional string): Two-letter state code.
    - `jurisdiction` (optional string): Contractor jurisdiction identifier.
    - `expand_rates` (optional boolean, default `false`): Include or exclude fee schedule child nodes.
  - **Outputs:** HTTP 200 OK JSON object containing:
    - `nodes`: Array of node objects (`{ id, label, display_name, properties, provenance }`).
    - `edges`: Array of edge objects (`{ source, target, type, properties }`).
    - `meta`: Execution timestamp, node count, edge count.
* **`GET /api/entity/{entity_id}`**
  - **Inputs:** `entity_id` string (e.g. `HCPCS-A4269`, `PLAW-117-169`).
  - **Outputs:** HTTP 200 OK JSON object containing full attribute set, inbound/outbound relationships, and verified source provenance.
* **`POST /api/query`**
  - **Inputs:** JSON payload `{ "query": string, "policy": string, "filters": object }`.
  - **Outputs:** HTTP 200 OK JSON payload containing dynamic retrieval results, relevant subgraphs, and synthesized context summary.

### 4.2 Fail-Fast Exception Handling Contracts
* **Unrecognized Query Parameters:**
  - Request with an invalid state postal code (not in the 54 valid jurisdictions) must return HTTP 400 Bad Request with:
    `{ "error": "INVALID_STATE_CODE", "message": "State code 'XX' is not a recognized US state or territory." }`
* **Missing Policy Domain:**
  - Query for an unindexed or nonexistent policy must return HTTP 404 Not Found with explicit remediation instructions.
* **Upstream Service Timeouts:**
  - If a live extraction query times out against an external agency API, the backend must return HTTP 504 Gateway Timeout detailing which agency upstream timed out.

---

## 5. Verification & Acceptance Criteria

### 5.1 Verification Matrix
| Component | Verification Check | Expected Result |
| :--- | :--- | :--- |
| **GitHub Repository** | `gh repo view` | Repository exists, is public, has separate git history, and contains no credentials. |
| **GitHub Pages** | HTTP GET `https://<user>.github.io/<repo>/` | Returns HTTP 200 OK with rendered interactive canvas UI. |
| **Hugging Face Space** | HTTP GET `<space-url>/health` | Returns HTTP 200 OK with status `healthy` and CORS headers allowing GitHub Pages origin. |
| **Graph Exploration** | Browser interaction on GitHub Pages | User can pan, zoom, click nodes, inspect attributes, and view full provenance links. |
| **State Filtering** | Filter selection for state `GU` (Guam) | Correctly isolates DME MAC Jurisdiction D and filters state nodes without crash or data loss. |
| **Error Handling** | Backend unavailable simulation | Frontend immediately surfaces clear diagnostic alert; zero unhandled promise rejections. |
