# Decision Ticket 006: Integration Test Suite and Acceptance Oracle Verification Specification

**Ticket ID:** `ticket-006.md`  
**Scope:** Test Verification Suite & Acceptance Oracles (`tests/test_graphrag_pipeline.py`, `tests/test_api_endpoints.py`)  
**Status:** RESOLVED  
**Claimed By:** `wayfinder-read-and-plan`  
**Blocked By:** `ticket-001.md`, `ticket-002.md`, `ticket-003.md`, `ticket-004.md`, `ticket-005.md`  

---

## 1. Architectural Question
How must the automated test suites in `tests/test_graphrag_pipeline.py` and `tests/test_api_endpoints.py` be expanded and structured to rigorously verify all acceptance criteria and system invariants defined in `functional_specification_005.md` Section 6 without regressions or unhandled exceptions?

---

## 2. Technical Audit and Empirical Findings

1. **Current Test Suite Capabilities:**
   - `tests/test_graphrag_pipeline.py` defines tests for Oracles 1 through 6, plus latency benchmarks.
   - However, it currently lacks tests for:
     - Single-entity inquiries (e.g. single state `STATE-NY`, single procedure `HCPCS-A6522`, single policy `POLICY-LTA`).
     - Natural language single-state queries: *"What covers New York?"* and *"What are the allowable compression rates in New York?"*.
     - Dynamic query routing verification ensuring no `if/elif` template branching is required.
   - `tests/test_api_endpoints.py` lacks tests for:
     - `/api/graphrag/subgraph` with a single primary key anchor (e.g. `["STATE-NY"]`).
     - `/api/graphrag/query` with single-state questions.

---

## 3. Concrete Architectural Decision & Test Oracles

### 3.1. Single-State Query Verification Oracles
Add test cases in `tests/test_graphrag_pipeline.py` and `tests/test_api_endpoints.py`:
1. **Pipeline Level: `test_single_state_query_ny(neo4j_engine)`:**
   - Execute query: `"What contractor covers New York?"` and `"What are the allowable compression rates in New York?"`.
   - Resolve anchors: asserts `STATE-NY` is extracted.
   - Extract connecting subgraph: asserts `STATE-NY`, `JURIS-DME-A`, `CMS-CR-13286`, and `CMS-MCD-A59508` are present in `traversal.nodes`.
   - Verify Contractor: asserts contractor is identified as `Noridian Healthcare Solutions` (Jurisdiction A).
   - Verify Fee Schedule: asserts New York fee schedule entries are retrieved (e.g. `FEE-A6522-NY-NR-2024`).
   - Execute synthesis: asserts answer quotes `[JURIS-DME-A]`, `Noridian`, and `[STATE-NY]`.
2. **API Endpoint Level: `test_api_single_state_and_subgraph(client)`:**
   - POST `/api/graphrag/subgraph` with `{"anchors": ["STATE-NY"]}`: asserts HTTP 200, `len(nodes) > 0`, `STATE-NY` in node PKs, `JURIS-DME-A` in node PKs.
   - POST `/api/graphrag/query` with `{"query": "What are the allowable compression rates in New York?"}`: asserts HTTP 200, `active_node_pks` contains `STATE-NY` and `JURIS-DME-A`.

### 3.2. Preservation of Existing Oracles
Ensure all 6 existing oracles continue to execute deterministically:
1. **Oracle 1 (Patient Benefit Routing):**
   - Query: `"I am from Wisconsin, survived breast cancer, need lymphedema supplies, I'm on Medicare, can you help?"`
   - Mandatory 7-node chain: `STATE-WI`, `JURIS-DME-B`, `CMS-CR-13286`, `CMS-MCD-A59508`, `ICD10-I97.2`, `HCPCS-A6522`, `FEE-A6522-WI-NR-2024`.
   - Verified fee: `$290.47`, coinsurance: `$58.09`.
2. **Oracle 2 (No Direct Procedure-Diagnosis Edges):**
   - Asserts 0 direct `(:HCPCSCode)-[:*]->(:ICD10Code)` edges across the entire database (`INV-NO-KEYWORD-BRIDGING`).
3. **Oracle 3 (Cross-Policy Convergence):**
   - Query: `"How do IVIG and LTA converge under federal law?"`
   - Convergence nodes in active path: `PLAW-117-328` and `FR-2023-24455`.
   - Synthesis cites Public Law 117-328 and 88 FR 77676.
4. **Oracle 4 (Zero Orphan Invariant):**
   - Asserts 0 orphaned nodes out of 3,971 nodes (`INV-UNBROKEN-ANCESTRY`).
5. **Oracle 5 (Edge Provenance Completeness):**
   - Asserts non-empty `source_uri`, `selector`, `ingestion_timestamp`, `run_id` on all edges (`INV-PROVENANCE-COMPLETENESS`).
6. **Oracle 6 (Fail-Fast Error Boundaries):**
   - Unrecognized location ("Atlantis") -> `EntityResolutionError` (HTTP 400).
   - Unindexed condition ("diabetes") -> `EntityResolutionError` (HTTP 400).

### 3.3. Test Execution Command Contract
The complete test suite must be executable via:
```bash
PYTHONPATH=. pytest tests/test_graphrag_pipeline.py tests/test_api_endpoints.py -v
```
All tests must execute with zero unhandled exceptions and pass all assertions.
