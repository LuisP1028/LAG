# Functional Specification 016: Dual-Platform Deployment Architecture for Interactive Engine Web Showcase (GitHub Pages & Hugging Face)

## 1. Objective & Scope

This specification defines the `{functionality}` required for `{correctness}` and `{sufficient}` deployment of the interactive engine showcase across two isolated platforms:
1. **Frontend Presentation Layer:** A standalone, fully interactive static web application deployed to GitHub Pages via a dedicated GitHub repository.
2. **Backend Engine Runtime Layer:** A persistent backend service deployed to Hugging Face Spaces that hosts the engine API, executes extraction/query pipelines, and serves graph topology and context data.

The outcome must allow any external user visiting the public GitHub Pages URL to explore, inspect, query, and interact with the full 8-hop legislative/healthcare engine without running local code or possessing local environment secrets.

In accordance with system rules:
- This document defines only requirements, behaviors, interfaces, constraints, and success criteria.
- It contains no code implementation, scaffolding commands, or library-specific development scripts.
- DO NOT CODE YET gate remains active.

---

## 2. Separate Repository & Source Isolation Requirements

### 2.1 Independent GitHub Repository Creation
* **Desired Behavior & Outcomes:**
  - The project showcase must reside in its own clean, dedicated GitHub repository separate from the local root development repository.
  - The repository must maintain its own independent Git version history, remote tracking, and configuration.
  - The repository root must be structured for static web deployment (e.g. GitHub Pages root or designated publication path).
* **Constraints & Invariants:**
  - Sensitive environment variables (e.g. local credentials, private database connection strings, unmasked tokens) must strictly never be committed to the new repository.
  - The repository must be configured to build and publish static assets publicly via GitHub Pages.

---

## 3. Frontend Functional Requirements (GitHub Pages Showcase)

### 3.1 Interactive Engine Graph Canvas
* **Inputs:** Graph topology payloads retrieved dynamically from the backend service or bundled sample run artifacts.
* **Desired Behavior & `{correct required outputs}`:**
  - Render an interactive, multi-layered visual graph canvas presenting the 8-hop knowledge graph structure:
    - Policy Keyword (`POLICY-...`)
    - Bills (`BILL-...`)
    - Public Laws (`PLAW-...`)
    - Statutory Sections (`STAT-...`)
    - U.S. Code Sections (`USC-...`)
    - Federal Register Rules (`REG-FR-...`)
    - CFR Sections (`CFR-...`)
    - CMS Transmittals (`TR-CR...`)
    - Coverage Policies (`DME-MAC-...`, `CMS-MCD-...`)
    - Procedure Codes (`HCPCS-...`)
    - Fee Schedule Rates (`FEE-...`)
    - Contractors (`JURIS-DME-...`)
    - Jurisdictions / States (`STATE-...`)
    - Contextual Records (`LDA-...`, `CBO-...`, `PUBMED-...`)
  - Node & Edge Interaction:
    - Users must be able to pan, zoom, click, select, drag, and filter nodes by entity category.
    - Selecting any node must open a detailed entity inspection panel showing all native keys, derived keys, citations, and complete provenance metadata (`source_uri`, `selector`, `run_id`, `ingestion_timestamp`).
    - Selecting any edge must display its relationship type and directional linkage between entities.

### 3.2 Dynamic Search & Query Interface
* **Inputs:** User-supplied `{Policy Keyword}` (e.g. `"LTA"`), search terms, state/jurisdiction filters (supporting all 54 US states and territories), or fee schedule expansion flags.
* **Desired Behavior:**
  - Provide a responsive control panel enabling users to:
    1. Select pre-computed policy runs for immediate zero-latency demonstration.
    2. Dispatch dynamic queries to the backend engine to trigger real-time graph traversal, filtering, or synthesis.
  - Display clear visual indicators of execution status (idle, querying, data streaming, completed, error).

### 3.3 Fail-Fast & Telemetry Display
* **Desired Behavior:**
  - If the backend service is unreachable, spinning up, or returns an error status code, the frontend must surface an explicit, human-readable status alert explaining the exact state (e.g., "Backend runtime cold starting / connecting to Hugging Face Space").
  - Silent failures, empty canvases with zero diagnostic feedback, and unhandled promise rejections are strictly prohibited.

---

## 4. Backend Functional Requirements (Hugging Face Space Runtime)

### 4.1 Engine API & Endpoints
* **Inputs:** HTTP requests from the GitHub Pages frontend containing query parameters, policy keywords, or node IDs.
* **Desired Behavior & `{correct required outputs}`:**
  - **Health & Readiness Endpoint:** Returns a 200 OK response with runtime health, loaded policy domains, and service uptime.
  - **Graph Topology Endpoint:** Returns nodes, edges, labels, and metadata filtered by policy, state, or jurisdiction.
  - **Entity Inspection Endpoint:** Returns deep contextual provenance and text excerpts for a specified entity primary key.
  - **Live Query / Pipeline Execution Endpoint:** Processes policy inquiries through the deterministic extraction and retrieval pipeline.
* **Constraints & Invariants:**
  - Cross-Origin Resource Sharing (CORS): Must explicitly allow cross-origin requests originating from the GitHub Pages domain.
  - Configuration Integrity: All third-party upstream API keys and runtime parameters must be injected via Hugging Face Space Secrets/Environment Variables, never baked into the Dockerfile or repository code.

---

## 5. End-to-End Interoperability & Acceptance Criteria

### 5.1 Success Criteria
1. **GitHub Pages Accessibility:** The web application is publicly reachable at `https://<username>.github.io/<repo-name>/` over HTTPS without authentication.
2. **Hugging Face Runtime Availability:** The Hugging Face Space is live, exposes the required endpoints, and responds to queries over HTTPS.
3. **Interactive Showcase Verification:**
   - Navigating to the GitHub Pages site displays the engine canvas.
   - Filtering by state (e.g., `GU`, `CA`, `NY`) updates the visible graph and contractor associations.
   - Inspecting an entity node displays accurate statutory/regulatory text, citations, and provenance URLs.
   - Dynamic requests to the Hugging Face backend complete and stream/render results to the frontend.
4. **Failure Transparency:** If the backend is paused, sleeping, or down, the frontend clearly indicates the backend status rather than failing silently or hanging indefinitely.
