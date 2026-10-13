# Decision Ticket 007: Verification Oracles, Acceptance Test Suite, and SLA Conformance Specification

**Ticket ID:** `ticket-007.md`  
**Scope:** Testing, Automated Verification, and SLA Conformance  
**Status:** RESOLVED  
**Claimed By:** `wayfinder-read-and-plan`  
**Blocked By:** `ticket-001.md`, `ticket-002.md`, `ticket-003.md`, `ticket-004.md`, `ticket-005.md`, `ticket-006.md`

---

## 1. Architectural Question

What automated verification oracles, pytest test suites, latency benchmark harnesses, and invariant validation assertions must be defined to prove that the GraphRAG pipeline and visualizer API satisfy 100% of the requirements in `functional_specification_004.md` without regressions or unverified claims?

---

## 2. Decision and Specification Requirements

### 2.1. Test Suite Architecture
- **Test Modules:**
  - `tests/test_graphrag_pipeline.py`: Comprehensive test suite for anchor resolution, topological expansion, context assembly, and synthesis.
  - `tests/test_api_endpoints.py`: Integration test suite for FastAPI REST routes using `fastapi.testclient.TestClient`.

### 2.2. Deterministic Verification Oracles

The test suite must implement six explicit verification oracles:

#### Oracle 1: Natural Language Patient Benefit Routing (Workflow 1)
- **Input Query:** *"I am from Wisconsin, survived breast cancer, need lymphedema supplies, I'm on Medicare, can you help?"*
- **Assertions:**
  1. Anchor resolution outputs: `state="STATE-WI"`, `diagnosis="ICD10-I97.2"`, `policy="POLICY-LTA"`.
  2. Subgraph extraction returns all 7 mandatory path nodes:
     - `STATE-WI`
     - `JURIS-DME-B (CGS)`
     - `CMS-CR-13286`
     - `CMS-MCD-A59508`
     - `ICD10-I97.2`
     - `HCPCS-A6522`
     - `FEE-A6522-WI-NR-2024`
  3. Allowable fee rate for `A6522` in Wisconsin equals `$290.47`, and 20% patient coinsurance equals `$58.09`.
  4. Regional claims contractor identified as `CGS Administrators (Jurisdiction B)`.
  5. Topologically extracted subgraph query completes in $<20\text{ms}$ in Neo4j.

#### Oracle 2: Clinical Coverage & Diagnosis Bridging (`INV-NO-KEYWORD-BRIDGING`)
- **Assertions:**
  1. For procedure code `HCPCS-A6583`, verified path to allowed diagnoses must route through `CMS-MCD-A59508`.
  2. Zero direct edges connect any `HCPCSCode` node directly to an `ICD10Code` node across 100% of the graph database.

#### Oracle 3: Cross-Policy Comparative Lineage (Workflow 3)
- **Input Query:** *"How do IVIG and LTA converge under federal law?"*
- **Assertions:**
  1. Resolves `POLICY-IVIG` and `POLICY-LTA`.
  2. Identifies shared public law `PLAW-117-328` (Consolidated Appropriations Act, 2023).
  3. Identifies shared implementing Federal Register Final Rule `FR-2023-24455` (88 FR 77676).

#### Oracle 4: Zero Orphan Invariant (`INV-UNBROKEN-ANCESTRY`)
- **Assertions:**
  1. Executes directed reachability traversal from root `POLICY` nodes across all active graph nodes.
  2. Asserts that the unreachable set is strictly empty (`len(unreachable) == 0`). Any orphan node causes immediate test failure.

#### Oracle 5: Edge Provenance Completeness (`INV-PROVENANCE-COMPLETENESS`)
- **Assertions:**
  1. Iterates over 100% of edges in `TraversalResult`.
  2. Asserts that `source_uri`, `selector`, `ingestion_timestamp`, and `run_id` are non-empty strings.

#### Oracle 6: Fail-Fast Error Boundaries (`INV-FAIL-FAST`)
- **Assertions:**
  1. Prompt containing an unindexed location (e.g., *"I am from Atlantis..."*) raises HTTP 400 / `EntityResolutionError` without fallback.
  2. Prompt requesting an unindexed medical condition raises HTTP 400 / `EntityResolutionError` indicating no coverage article exists.
  3. Model API timeout or authentication rejection returns a structured error envelope with HTTP 502/401 and descriptive diagnostic telemetry.

### 2.3. Latency Benchmark Harness
- An automated benchmark executes 10 iterations of the patient routing query:
  - Asserts Neo4j traversal latency $p95 < 20\text{ms}$.
  - Asserts end-to-end GraphRAG pipeline latency $p95 < 1500\text{ms}$ (when model endpoint is responsive).
