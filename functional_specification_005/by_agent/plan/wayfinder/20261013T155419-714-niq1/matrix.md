# Master Component-to-Edit Matrix: Dynamic Schema-Driven GraphRAG Traversal

**Governing Specification:** `functional_specification_005.md`  
**Run ID:** `20261013T155419-714-niq1`  
**Planning Status:** Resolved Frontier  
**Planning Node:** `wayfinder-read-and-plan`  
**Taxonomy Reference:** [`LANGUAGE.md`](file:///Users/diesel/Desktop/LAG/LANGUAGE.md)  

---

## 1. Component Transformation Overview

| Component File | Target Symbols / Classes | Targeted Line Range | Architectural Transformation | Governing Ticket |
|---|---|---|---|---|
| `src/graphrag/models.py` | `AnchorEntity`, `ResolvedAnchors` | Lines 7–23 | Generalize anchor models across all 14 node types with primary key accessors | [`ticket-001.md`](tickets/ticket-001.md) |
| `src/graphrag/entity_linker.py` | `EntityAnchorLinker` | Lines 11–230 | Implement direct primary key token resolution, 14-entity lexical matching, and fail-fast validation (`EntityResolutionError`) | [`ticket-001.md`](tickets/ticket-001.md) |
| `src/graphrag/traversal.py` | `TopologicalTraversalEngine` | Lines 18–329 | Eliminate hardcoded `if/elif` query templates; implement dynamic single-entity lineage ($N=1$) and multi-entity shortest-path traversal ($N \ge 2$) enforcing `INV-NO-KEYWORD-BRIDGING`, `INV-UNBROKEN-ANCESTRY`, and `INV-PROVENANCE-COMPLETENESS` | [`ticket-002.md`](tickets/ticket-002.md) |
| `src/graphrag/context_assembler.py` | `GraphContextAssembler` | Lines 7–113 | Eliminate synthetic fallbacks and defaults; assemble five authoritative sections with exact 20% patient coinsurance calculation | [`ticket-003.md`](tickets/ticket-003.md) |
| `src/graphrag/synthesizer.py` | `HuggingFaceSynthesizer` | Lines 18–96 | Update system prompt to mandate exact bracketed IDs, exact dollar amounts, and official citations; configure Router API parameters and fail-fast boundaries | [`ticket-004.md`](tickets/ticket-004.md) |
| `src/api/routes.py` | `resolve_entities`, `get_subgraph_by_anchors`, `execute_graphrag_query` | Lines 253–389 | Generalize `/api/graphrag/subgraph` for single and multi-node inputs across all 14 node types; return complete illumination telemetry in `/api/graphrag/query` | [`ticket-005.md`](tickets/ticket-005.md) |
| `tests/test_graphrag_pipeline.py` | `test_single_state_query_ny`, `test_oracle_1` through `test_oracle_6` | Lines 21–214 | Add verification for single-state queries (`STATE-NY`, Noridian Jurisdiction A, NY fees), single-entity resolution, and preserve existing test oracles | [`ticket-006.md`](tickets/ticket-006.md) |
| `tests/test_api_endpoints.py` | `test_api_graphrag_subgraph`, `test_api_graphrag_query` | Lines 82–114 | Add verification for single-anchor subgraph extraction and single-state conversational GraphRAG queries | [`ticket-006.md`](tickets/ticket-006.md) |

---

## 2. Detailed File-by-File Technical Specifications

### 2.1. `src/graphrag/models.py`
- **File Path:** `src/graphrag/models.py`
- **Lines:** 7–23
- **Symbols:** `AnchorEntity`, `ResolvedAnchors`
- **Modifications:**
  - Add support for 14 node slots in `AnchorEntity.slot`: `"state"`, `"jurisdiction"`, `"changerequest"`, `"coveragepolicy"`, `"hcpcscode"`, `"icd10code"`, `"policy"`, `"bill"`, `"publiclaw"`, `"statutorysection"`, `"regulation"`, `"feescheduleentry"`, `"lobbyingfiling"`, `"literaturestudy"`.
  - In `ResolvedAnchors`: maintain `all_anchors: List[AnchorEntity]` as primary collection; provide helper property `primary_keys -> List[str]`; provide optional slot accessors (`state_anchor`, `diagnosis_anchor`, `policy_anchor`, `jurisdiction_anchor`, `hcpcs_anchor`, `change_request_anchor`, `coverage_policy_anchor`).

### 2.2. `src/graphrag/entity_linker.py`
- **File Path:** `src/graphrag/entity_linker.py`
- **Lines:** 11–230
- **Symbols:** `EntityAnchorLinker`
- **Modifications:**
  - Direct Primary Key Token Resolution: Detect tokens matching `\b([A-Z0-9]+-[A-Z0-9\-_.]{2,})\b` and verify against Neo4j via `MATCH (n:PolicyNode {primary_key: $pk}) RETURN n.primary_key AS primary_key, labels(n) AS labels, n.name AS name, n.title AS title`.
  - Add lexical resolvers for `Jurisdiction` (Noridian -> `JURIS-DME-A`, CGS -> `JURIS-DME-B`), `ChangeRequest` (`CMS-CR-13286`), `CoveragePolicy` (`CMS-MCD-A59508`), `PublicLaw` (`PLAW-117-328`), `Regulation` (`FR-2023-24455`), and `Bill` (`BILL-117-hr-3630`).
  - Preserve `STATE_NAME_TO_CODE` dictionary, clinical synonym table (`CLINICAL_SYNONYMS`), policy triggers (`POLICY_TRIGGERS`), and `HCPCS_REGEX`.
  - Fail-Fast Enforcement: Raise `EntityResolutionError` on unindexed locations ("Atlantis") and conditions ("diabetes").

### 2.3. `src/graphrag/traversal.py`
- **File Path:** `src/graphrag/traversal.py`
- **Lines:** 18–329
- **Symbols:** `TopologicalTraversalEngine`, `extract_connecting_subgraph`, `_execute_pattern_a`, `_execute_pattern_b`, `_execute_pattern_c`, `_convert_node`, `_convert_edge`
- **Modifications:**
  - Remove hardcoded `if/elif` pattern branching in lines 39–76.
  - Implement Single-Anchor Traversal ($N = 1$):
    - State anchor (`STATE-NY` or `STATE-WI`): query regional `Jurisdiction` via `COVERS_STATE`, governing `ChangeRequest` via `APPLIES_TO_JURISDICTION`, governing `CoveragePolicy` via `MANDATES_POLICY`, and non-rural `FeeScheduleEntry` nodes via `APPLIES_TO` from covered `HCPCSCode` nodes.
    - Clinical anchor (`HCPCSCode` or `ICD10Code`): query connecting `CoveragePolicy`, associated procedure/diagnosis codes, and authorizing `ChangeRequest`.
    - General anchor: query immediate 1-to-2 hop connected schema neighborhood.
  - Implement Multi-Anchor Traversal ($N \ge 2$):
    - Discover connecting shortest paths between all pairs of anchor nodes in Neo4j.
    - Enrich with clinical-geographic 7-node chain (Oracle 1) when State and Diagnosis are present.
    - Enrich with cross-policy convergence (Oracle 3) when multiple Policy nodes are present.
    - Enforce `INV-NO-KEYWORD-BRIDGING`: strictly prohibit direct `HCPCSCode -> ICD10Code` edges.
  - Retain all four provenance metadata fields (`source_uri`, `selector`, `ingestion_timestamp`, `run_id`) on all traversed edges (`INV-PROVENANCE-COMPLETENESS`).
  - Fail-Fast: Raise `TraversalError` if two valid nodes have no connecting path across the database schema.

### 2.4. `src/graphrag/context_assembler.py`
- **File Path:** `src/graphrag/context_assembler.py`
- **Lines:** 7–113
- **Symbols:** `GraphContextAssembler`, `assemble_context`
- **Modifications:**
  - Remove all synthetic fallbacks (`[POLICY-LTA]`, `CGS Administrators`, hardcoded states, hardcoded citations).
  - Format output into five explicit Markdown sections:
    1. `### 1. Program & Legal Authority` (Policy, PublicLaw, StatutorySection, Regulation, ChangeRequest, CoveragePolicy)
    2. `### 2. Contractor & Region` (Jurisdiction name, contractor_name, covered states, target state)
    3. `### 3. Clinical Criteria` (ICD10Code diagnosis description, HCPCSCode procedure descriptions)
    4. `### 4. Fees and Patient Costs` (Target state allowable fee amounts and calculated 20% patient coinsurance: `coinsurance = round(fee_amount * 0.20, 2)`)
    5. `### 5. Data Sources & Provenance` (Unique `source_uri`, selectors, change request transmittal numbers, run IDs)

### 2.5. `src/graphrag/synthesizer.py`
- **File Path:** `src/graphrag/synthesizer.py`
- **Lines:** 18–96
- **Symbols:** `HuggingFaceSynthesizer`, `SYSTEM_PROMPT`, `synthesize`, `_call_hf_inference_api`
- **Modifications:**
  - Update `SYSTEM_PROMPT` to mandate:
    1. Relying strictly on GRAPH CONTEXT without extrapolation.
    2. Quoting exact bracketed primary key IDs (e.g. `[CMS-MCD-A59508]`, `[PLAW-117-328]`, `[JURIS-DME-A]`, `[STATE-NY]`).
    3. Quoting exact dollar amounts (e.g. `$290.47`) and calculated 20% coinsurance (e.g. `$58.09`).
    4. Quoting official legal citations (`Public Law 117-328`, `88 FR 77676`).
  - Maintain fail-fast HTTP boundaries for token authentication (401), rate limits (429), and remote inference errors (>=400 / timeout).

### 2.6. `src/api/routes.py`
- **File Path:** `src/api/routes.py`
- **Lines:** 253–389
- **Symbols:** `resolve_entities`, `get_subgraph_by_anchors`, `execute_graphrag_query`
- **Modifications:**
  - In `get_subgraph_by_anchors` (`/api/graphrag/subgraph`):
    - Support single-entity primary key lists (`["STATE-NY"]`) and canvas node click selections.
    - Query Neo4j for node existence across all 14 node types; return HTTP 404 with `EntityNotFoundError` if missing.
    - Invoke dynamic `extract_connecting_subgraph`.
    - Return `SubgraphResponse` with traversed nodes, edges, active keys, and retrieval latency.
  - In `execute_graphrag_query` (`/api/graphrag/query`):
    - Ensure active node keys and active edge keys are returned for all queries.

### 2.7. `tests/test_graphrag_pipeline.py` & `tests/test_api_endpoints.py`
- **File Paths:** `tests/test_graphrag_pipeline.py`, `tests/test_api_endpoints.py`
- **Symbols:** Integration test suite
- **Modifications:**
  - Add test `test_single_state_query_ny` verifying `"What contractor covers New York?"` and `"What are the allowable compression rates in New York?"` return HTTP 200, Noridian Jurisdiction A (`JURIS-DME-A`), Change Request 13286, Policy A59508, and New York fee schedules.
  - Add test for `/api/graphrag/subgraph` with `{"anchors": ["STATE-NY"]}`.
  - Preserve all 6 existing test oracles (Patient Benefit Routing, No Keyword Bridging, Cross-Policy Convergence, Zero Orphans, Edge Provenance Completeness, Fail-Fast Boundaries).
