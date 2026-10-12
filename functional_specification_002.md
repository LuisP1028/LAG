# Functional Specification: Enabling Research, Live API Querying, and Schema Auditing in Wayfinder Prompts

**Document ID:** `functional_specification_002.md`  
**Status:** Requirements Specification  
**Implementation Guidance:** Prohibited (DO NOT CODE YET)

---

## 1. Objective and Scope

This specification defines the functional requirements for upgrading the Wayfinder multi-agent planning and scanning pipeline (`plan.md`, `plan-scan-1.md`, `plan-scan-2.md`, and `tester.md`). 

The objective is to eliminate artificial restrictions that constrain agents solely to local static code analysis. The pipeline must authorize agents to conduct active external reconnaissance, query live APIs, capture real network payloads, audit data schemas empirically, and ground test planning in authentic observed responses for any input specification, while remaining completely domain-agnostic and preserving all pipeline invariants.

---

## 2. Core Functional Requirements

### 2.1. Domain-Agnostic Operational Mandate
* The prompt framework must govern solely the *investigative methodology* and verification standards, not the subject matter.
* Prompts must be strictly decoupled from any specific business domain, external vendor, or bespoke matrix structure (including legislative, healthcare, financial, or specific handoff contract terminology).
* All domain logic, target endpoints, and schema expectations must derive dynamically from the input specification provided at `{{SEED_PATH}}`.

### 2.2. Tool Execution and Active Reconnaissance
* Agents within planning and scanning phases must be authorized to execute safe, read-only inspection tools:
  * Network requests via shell commands (such as `curl` or non-mutating HTTP queries) to probe external APIs and fetch live responses.
  * Lightweight parser executions (such as `jq` or JSON/XML format inspectors) to evaluate payload structures.
  * Read-only Model Context Protocol (MCP) server invocations.
* **Safety Guardrail:** Network calls must be strictly non-mutating (safe read operations / GET requests only, unless token authentication explicitly requires a credential-exchange POST). State mutations on external targets are strictly prohibited.

### 2.3. Verifiable Empirical Evidence Grounding
* Qualification of entities, interfaces, and schemas must not be restricted to files physically present in the local codebase repository.
* When an input specification references external interfaces, candidate datasources, or API endpoints, qualification requires verifiable empirical evidence:
  * Reachable, responding network endpoints.
  * Authoritative, verified technical documentation.
  * Captured sample payloads demonstrating schema feasibility.
* Reliance on unverified assumptions, speculative contracts, or hallucinated schemas constitutes a fatal error (`{error}`).

### 2.4. Live Payload Capture and Schema Auditing
* When an input specification involves external services or APIs, scanning agents must:
  * Fetch and save unedited, raw sample responses (JSON, XML, text) into the designated run directory (`assets/{{RUN_ID}}/` or working asset store).
  * Document payload schemas empirically: exact field names, nested hierarchy, observed data types, nullability, pagination mechanics, and HTTP response codes.
  * Identify deficiencies where specced requirements cannot be fulfilled by either existing local code or verified external APIs, logging them in an explicit deficiency register.
* The scanning agent handoff manifest (`handoff/{{RUN_ID}}/plan-scan-*.txt`) must atomically record the relative filepaths of both the authored scan report and all saved payload sample files.

### 2.5. Expanded Test Payload Admissibility
* Test planning agents (`tester.md`) must accept test payloads grounded either in local codebase types or in authentic observed payloads captured during the active reconnaissance phase.
* Prohibition against synthetic, mocked, or fabricated payloads remains absolute (`INV-PAYLOAD-01`).
* Test decision tickets must validate data parsing, contract conformance, and error handling against actual observed payloads.

---

## 3. Preserved Pipeline Invariants

1. **`INV-BOUNDARY-01` (DO NOT CODE YET):** Planning, scanning, and test-planning agents must not write or modify application implementation code, run database migrations, or execute feature builds. Reconnaissance (safe read-only probing to discover schemas) is authorized; writing product implementation code is strictly prohibited.
2. **`INV-MAP-01` (Deterministic Monotonic Ticketing):** All architectural and testing decisions must be locked via monotonic ticket generation in `wayfinder/{{RUN_ID}}/tickets/ticket-NNNN.md` and registered in `wayfinder/{{RUN_ID}}/map.md`.
3. **`INV-MANIFEST-OVERWRITE-01` (Atomic Manifest Handoff):** Handoff manifests remain single-file atomic text files listing repository-relative paths (exactly one path per line). Downstream agents ingest only paths explicitly recorded in manifests.
