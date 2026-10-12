# Required Edits: Enabling Research, Live API Querying, and Schema Auditing in Wayfinder Prompts

**Target Files:**
1. `.sandcastle/plan.md`
2. `.sandcastle/plan-scan-1.md`
3. `.sandcastle/plan-scan-2.md`
4. `.sandcastle/tester.md`

**Status:** Implementation Blueprint (DO NOT CODE YET)

---

## 1. Modifications to `.sandcastle/plan.md` (`wayfinder-read-and-plan`)

### 1.1. Description & Role Definition
* **Location:** YAML frontmatter (`description`) and Header section (Lines 1–10).
* **Edit:**
  * Expand the operational scope from solely local code deconstruction to include external datasource identification, endpoint qualification, live API query structure, and schema reconciliation tickets.

### 1.2. Section 1.1: Evaluation Parameters (`LANGUAGE.md`)
* **Location:** Lines 60–87.
* **Edits:**
  * Update `{functionality}` definition: Extend beyond internal local components to encompass external data retrieval and API integration capabilities mandated by `{{SEED_PATH}}`.
  * Update `{errors}` definition: Add explicit error criteria for basing planning decisions on unverified schema assumptions, hallucinated endpoints, or ungrounded payload contracts.
  * Update `{correct required outputs}` definition: Authorize decision tickets that lock candidate datasource selection, endpoint operational parameters (HTTP method, headers, rate limits), and target data schemas.

### 1.3. Section 2: Core Invariants
* **Location:** Lines 88–115.
* **Edits:**
  * Clarify `INV-BOUNDARY-01`: Explicitly distinguish application implementation (strictly prohibited) from read-only reconnaissance (safe queries, schema discovery).
  * Update ticket charting rules (`INV-ATOMIC-01`): When an input spec requires external integration, tickets must lock:
    1. Selection of authoritative candidate datasources.
    2. Endpoint operational parameters (HTTP method, query parameters, authentication, rate limits).
    3. Target data schemas and structural contracts.

### 1.4. Section 3: Orchestration Architecture & Workflow Steps
* **Location:** Lines 116–162.
* **Edits:**
  * Update Stage 4 & Stage 5: Include deconstruction of external API requirements, endpoint verification tickets, and empirical schema reconciliation alongside internal codebase components.

---

## 2. Modifications to `.sandcastle/plan-scan-1.md` & `.sandcastle/plan-scan-2.md` (`wayfinder-plan-scan-1` / `2`)

### 2.1. Ingestion & Component Qualification Gate
* **Location:** Lines 31–49 (`Static Scan & Dependency Cone Enumeration Instructions`) and Section 2 (`INV-SCAN-01`).
* **Edits:**
  * Remove grep-only locking: Eliminate constraints restricting searches exclusively to caller/callee traversals within named local folders.
  * Broaden entity qualification: An external datasource, service, or API qualifies for inclusion when supported by verifiable empirical evidence (reachable endpoint, official technical documentation, or captured payload).
  * Define `{errors}`: Unverified assumptions or hallucinated endpoints remain explicit fatal errors (`{error}`).

### 2.2. Tool Execution & Active Reconnaissance Directives
* **Location:** Add to Section 2 and Section 4.
* **Edits:**
  * Authorize non-mutating shell commands (`curl`, lightweight Python inspection scripts, `jq`) and read-only MCP tool calls to inspect headers, check endpoint availability, and fetch live payload structures.
  * Safety guardrail: Enforce that all network calls are safe GET / read requests (unless token acquisition mandates an explicit POST).

### 2.3. Schema Auditing Protocol & Raw Payload Capture
* **Location:** Section 2 and Section 4.
* **Edits:**
  * Mandate saving unedited raw sample responses (JSON, XML, text) into `assets/{{RUN_ID}}/` or working asset directories.
  * Instruct agents to verify exact field names, nested hierarchy, observed data types, nullability, pagination mechanics, and status codes directly from captured payloads.

### 2.4. Output Deliverables & Manifest Overwrite Contract
* **Location:** Section 1.2 (`{correct required outputs}`) and Section 2.6 (`INV-MANIFEST-OVERWRITE-01`).
* **Edits:**
  * Update scan report deliverables to include:
    1. Audit of evaluated codebase components and/or candidate external datasources.
    2. Documented payload schemas grounded in captured evidence.
    3. Deficiency register listing any specced requirements unsatisfied by existing code or reachable APIs.
  * Update handoff manifest (`handoff/{{RUN_ID}}/plan-scan-1.txt` and `handoff/{{RUN_ID}}/plan-scan-2.txt`) to record:
    - Path of authored scan report.
    - Exact paths of all saved ground-truth payload sample files.

---

## 3. Modifications to `.sandcastle/tester.md` (`wayfinder-test-plan`)

### 3.1. Section 2.1: Payload Law (`INV-PAYLOAD-01`)
* **Location:** Lines 105–111.
* **Edits:**
  * Broaden schema admissibility: Test payloads may be grounded either in local codebase interfaces OR in authentic observed payloads captured during the active reconnaissance phase by scanner agents.
  * Reiterate that synthesized, fake, or mocked payloads remain strictly prohibited.

### 3.2. Section 2.2: Assertion Law (`INV-ASSERTION-01`)
* **Location:** Lines 112–116.
* **Edits:**
  * Authorize test decision tickets that validate data parsing, contract conformance, and error handling against live or captured API data structures.

### 3.3. Section 1.2: Evaluation Parameters & Outputs
* **Location:** Lines 76–98.
* **Edits:**
  * Update `{correctness}` and `{sufficient}` to recognize captured payloads and real API response schemas as valid verification oracles.

---

## 4. Invariants and Guardrails
* **Untouched Files:** `implementer.md`, `reviewer.md`, and `merger.md` must not be modified.
* **Preserve Pipeline Invariants:**
  * `INV-BOUNDARY-01`: No application implementation code written during planning/scanning.
  * `INV-MAP-01`: Monotonic ticket generation in `wayfinder/{{RUN_ID}}/tickets/`.
  * `INV-MANIFEST-OVERWRITE-01`: Atomic single-file manifests listing relative paths.
