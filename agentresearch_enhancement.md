You are completely right. I stripped the healthcare and legislative terms, but I still dragged the structural framework of `functional_specification_001.md`—specifically terms like `Direct Path`, `Structural Traversal`, `Field Access Matrix`, and `Foreign-Key Handoff Contracts`—directly into the prompts. That was wrong. Those are specific requirements of that one specification, not generic agent capabilities.

The goal is strictly to expand the agents' generic toolset and operational mandate to perform research, query APIs, identify datasources, and audit schemas for *any* specification passed to them.

Here is the clean, decoupled technical documentation for the coding assistant.

---

# Technical Specification: Enabling Research, Live API Querying, and Schema Auditing in Wayfinder Prompts

**Target System:** Sandcastle / Wayfinder Multi-Agent Framework (`plan.md`, `plan-scan-1.md`, `plan-scan-2.md`, `tester.md`)

**Implementation Constraint:** Specification blueprint only. **DO NOT WRITE CODE OR EDIT PROMPT FILES YET.**

---

## 1. Objective

Refactor the Wayfinder planning and scanning prompts so agents are not locked into local static code analysis. Upgrade the prompt suite to authorize and instruct agents to:

1. **Research External Datasources:** Autonomously search documentation, evaluate candidate services, and identify authoritative endpoints relevant to whatever input specification is provided.


2. **Execute Live API Queries:** Use available tools (shell commands like `curl`, lightweight scripts, and MCP servers) to query live endpoints, handle authentication/headers, and inspect network responses.


3. **Audit Payloads and Schemas:** Inspect real API responses to analyze data structures, extract fields, verify types, examine pagination/rate limits, and document schemas based on observed evidence rather than assumptions.


4. **Remain Domain-Agnostic:** Do not hardcode domain concepts, specific data models, or bespoke matrix structures into the prompt files. The prompts govern the *investigative methodology*; the input specification at `{{SEED_PATH}}` governs the *subject matter*.



---

## 2. General Capability Expansions

### 2.1 Tool Execution & Active Reconnaissance

- **Current Restriction:** Scanners are restricted to scoped directory searches (e.g., `grep` within named local folders) and fail if a local directory path is missing.


- **Required Change:** Authorize read-only external tool usage. Agents may execute shell commands (`curl`, Python one-liners, `jq`, format parsers) and read-only MCP calls to probe external APIs, inspect headers, and fetch raw payloads.


- **Guardrail:** Network calls must be strictly non-mutating (safe read/GET requests only, unless token generation requires an explicit POST).



### 2.2 Evidence Grounding vs. Local Existence

- **Current Restriction:** A component only qualifies for review if it physically exists in the local repository.


- **Required Change:** Broaden qualification to external entities. If a specification requires external datasources, APIs, or data schemas, qualification requires **verifiable empirical evidence** (e.g., reachable endpoint, verified documentation, or successful test query response). Speculative or hallucinated schemas remain an `{error}`.



### 2.3 Schema and Payload Auditing

- **Current Restriction:** Schemas are audited strictly against local ASTs, local TypeScript interfaces, or database models.


- **Required Change:** Instruct agents to capture and inspect live payloads whenever external interfaces are involved. Agents must document observed fields, nullability, data types, pagination mechanics, and status codes directly from real payloads.



---

## 3. File-by-File Prompt Changes

### 3.1 `plan.md` (`wayfinder-read-and-plan`)

- **Scope & Destination:** Expand the planning mandate. The planner must be able to deconstruct requirements not only into local code edits, but also into discrete research and architectural decision tickets (e.g., datasource selection, endpoint qualification, query structure, and schema reconciliation).


- **Ticket Charting Logic:** When an input spec requires external integration, tickets must lock decisions regarding:
- Selection of candidate datasources based on specced requirements.


- Endpoint operational parameters (HTTP methods, parameters, authentication, rate limits).


- Target data schemas and structural contracts.




- **Evaluation Parameters (`LANGUAGE.md`):**
- `{functionality}`: Covers both internal component behavior and external data retrieval/integration capabilities defined in the specification.


- `{errors}`: Include basing decisions on unverified schema assumptions or hallucinated endpoints.





### 3.2 `plan-scan-1.md` & `plan-scan-2.md` (`wayfinder-plan-scan-1` / `2`)

- **Remove Grep-Only Locking:** Eliminate instructions requiring searches to always be caller/callee traversals within named local directories.


- **Add Research & Probing Directives:**
- Add explicit instructions for querying external APIs, checking endpoint availability, and retrieving sample responses.


- Mandate saving unedited sample responses (JSON, XML, text) into the run's working directory or asset folder when external APIs are audited, ensuring downstream consumers have ground-truth payloads.




- **Schema Auditing Protocol:** Instruct agents to verify exact field names, types, nesting, and pagination from actual captured data.


- **Output Deliverables:** Update the scan report contract to output:
1. An audit of evaluated codebase components and/or candidate external datasources.


2. Documented payload schemas based on verified evidence.


3. An explicit deficiency register for any requirement in the specification that cannot be satisfied by existing code or reachable APIs.




- **Manifest Output (`handoff/{{RUN_ID}}/plan-scan-*.txt`):** The agents record the paths of the authored report and any saved payload sample files.



### 3.3 `tester.md` (`wayfinder-test-plan`)

- **Admissible Schemas & Payloads (`INV-PAYLOAD-01`):**
- Broaden schema admissibility: test payloads can be grounded either in local codebase types OR in authentic observed payloads captured by the research/scanner agents.


- Retain the strict prohibition on hand-synthesized, fake, or mocked payloads.




- **Assertion Oracles (`INV-ASSERTION-01`):**
- Authorize test decision tickets that validate data parsing, contract conformance, and error-handling against live or captured API data structures.





### 3.4 Untouched Files

- **`implementer.md`:** Do not modify. It reads whatever paths are listed in the manifests and applies the locked decisions.


- **`reviewer.md`:** Do not modify. It reviews changes made by the implementer against the spec and tickets.


- **`merger.md`:** Do not modify. It handles branch joins deterministically.



---

## 4. Pipeline Invariants (Strictly Maintained)

1. **`INV-BOUNDARY-01` (DO NOT CODE YET):** The planner, scanners, and test-planner do not write application code. Executing curl or inspection scripts to discover schemas is permitted reconnaissance; implementing features is prohibited.


2. **`INV-MAP-01`:** All decisions must be locked via monotonic ticket generation in `wayfinder/{{RUN_ID}}/tickets/ticket-NNNN.md` and tracked in `wayfinder/{{RUN_ID}}/map.md`.


3. **`INV-MANIFEST-OVERWRITE-01`:** Handoff manifests remain atomic single-file text lists (one path per line). Downstream agents continue consuming purely via manifest paths. 