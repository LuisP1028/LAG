# Decision Ticket 006: Integration Test Architecture, Oracle Grounding, and End-to-End Verification

**Ticket ID:** `ticket-006.md`  
**Scope:** `tests/test_api_endpoints.py` & `tests/test_graphrag_pipeline.py`  
**Status:** RESOLVED  
**Claimed By:** `wayfinder-read-and-plan`  
**Blocked By:** `ticket-001.md`, `ticket-002.md`, `ticket-003.md`, `ticket-004.md`, `ticket-005.md`  
**Taxonomy Reference:** `LANGUAGE.md`

---

## 1. Architectural Question
What automated test suites and verification oracles must be added to guarantee that the one-click inquiry workflow, explicit anchor bypass contract, non-zero illumination, and all 14 entity types execute with zero regressions?

---

## 2. Root Cause & Architectural Audit

1. **Test Coverage Gaps:**
   - Existing tests in `tests/test_api_endpoints.py` only test free-form query strings (Workflow 1, Workflow 3, Workflow 4).
   - There are currently no tests asserting that `primary_key` passed in `GraphRAGQueryRequest` correctly bypasses regex extraction and returns non-zero active nodes for PublicLaw, Bills, Regulations, Coverage Policies, Jurisdictions, or Codes.

2. **Acceptance Criteria Verification Requirements:**
   - Section 6 Acceptance Criteria mandate:
     1. Inquiring about `PLAW-117-328` returns a synthesized explanation and illuminates the public law node and its connected statutory chain on the canvas (`> 0 Nodes Illuminated`).
     2. Correct grounded answer quoting bracketed primary key.
     3. Support across all 14 entity types.
     4. Verified edge keys with 0 `UNKNOWN` values.

---

## 3. Decision & Technical Specifications

### 3.1. API Test Suite Enhancements (`tests/test_api_endpoints.py`)
- **Symbol:** `test_api_graphrag_query_explicit_anchor_plaw`, `test_api_graphrag_query_all_14_entity_types`
- **Actions:**
  1. Add `test_api_graphrag_query_explicit_anchor_plaw(client)`:
     - Request: `POST /api/graphrag/query` with:
       ```json
       {
         "query": "Explain the statutory authority and enacted healthcare provisions of [PLAW-117-328] (Consolidated Appropriations Act, 2023).",
         "primary_key": "PLAW-117-328"
       }
       ```
     - Assertions:
       - Status code: `200`
       - `"PLAW-117-328"` in `data["active_node_pks"]`
       - `len(data["active_node_pks"]) >= 6` (includes bills and statutory sections)
       - `len(data["active_edge_keys"]) >= 5`
       - All edge keys follow `{src}->{rel}->{tgt}` without `"UNKNOWN"`
       - `"[PLAW-117-328]"` in `data["answer"]`
       - `data["duration_ms"] > 0`
  2. Add `test_api_graphrag_query_all_14_entity_types(client)`:
     - Define list of 14 valid entities across all 14 labels:
       `STATE-WI`, `JURIS-DME-B`, `CMS-CR-13286`, `CMS-MCD-A59508`, `HCPCS-A6522`, `ICD10-I97.2`, `FEE-A6522-WI-NR-2024`, `POLICY-LTA`, `PLAW-117-328`, `FR-2023-24455`, `BILL-117-hr-3630`, `USC-42-1395x-s-2-JJ`, `PUBMED-31841362`, `LDA-2023-Q1-001`.
     - For each entity, submit `/api/graphrag/query` with explicit `primary_key`.
     - Assert status `200`, `len(data["active_node_pks"]) > 0`, and `entity_pk` in `data["active_node_pks"]`.
  3. Add `test_api_graphrag_query_invalid_anchor_fails_fast(client)`:
     - Submit `/api/graphrag/query` with `primary_key: "INVALID-NONEXISTENT-PK"`.
     - Assert status `400 Bad Request` with `EntityResolutionError`.

### 3.2. Traversal Engine Test Suite Enhancements (`tests/test_graphrag_pipeline.py`)
- **Symbol:** `test_single_entity_general_traversal_integrity`
- **Actions:**
  1. Instantiate `TopologicalTraversalEngine`.
  2. Execute `_execute_single_general_traversal` on `PLAW-117-328`.
  3. Assert:
     - `nodes_by_pk` has `PLAW-117-328` and incident nodes.
     - `edges_by_key` has valid edges.
     - None of the edges contain `"UNKNOWN"`.

---

## 4. Acceptance Criteria
1. `pytest tests/test_api_endpoints.py` and `pytest tests/test_graphrag_pipeline.py` pass 100% with zero errors.
2. Verified non-zero illumination for `PLAW-117-328` and all 14 entity types.
3. Edge key formatting strictly conforms to `{src}->{rel}->{tgt}`.
4. Fast failure on invalid explicit primary keys is verified.
