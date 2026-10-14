# Ticket 007: Autonomous Routing Engine Orchestration, Tier 5 Dynamic Context Linkage, Downstream GraphRAG/API Alignment, & Verification Suite

## Status
**Locked** — Architectural Decision & Edit Plan

## Context & Problem Statement
[`src/graph/engine.py`](file:///Users/diesel/Desktop/LAG/.sandcastle/worktrees/agent-plan-20261013T225035-656-0beg/src/graph/engine.py) (lines 180–245), [`src/graph/tier5_context.py`](file:///Users/diesel/Desktop/LAG/.sandcastle/worktrees/agent-plan-20261013T225035-656-0beg/src/graph/tier5_context.py) (lines 159–203), and downstream consumers (`src/graphrag/entity_linker.py`, `src/api/routes.py`, `tests/test_graph_pipeline.py`, `tests/test_api_endpoints.py`, `tests/test_graphrag_pipeline.py`) must be updated to orchestrate the complete 8-hop autonomous traversal routing map defined in [`functional_specification_013.md`](file:///Users/diesel/Desktop/LAG/.sandcastle/worktrees/agent-plan-20261013T225035-656-0beg/functional_specification_013.md):
1. **`PropertyGraphEngine.build_pipeline` Handoff Chain:** Currently `build_pipeline` only captures `t1_handoff`, `t2_handoff`, `t3_handoff`, and `hcpcs_codes`, and does not store or expose the complete 8-hop handoff chain (`LegislativeHandoff`, `StatutoryHandoff`, `RegulatoryHandoff`, `OperationalHandoff`, `CoverageHandoff`, `CodingHandoff`, `ReimbursementHandoff`) or a structured traversal routing trace.
2. **`tier5_context.py` Hardcoded Node IDs:** `ingest_context_tier` (lines 159–203) hardcodes `bill_id = "BILL-117-hr-3630"`, `stat_id = "STAT-117-328-SEC-4133"`, `reg_id = "REG-FR-2023-24455"` instead of consuming the upstream handoff contracts (`LegislativeHandoff`, `StatutoryHandoff`, `RegulatoryHandoff`) when linking GAO reports, MedPAC analyses, and legislative hearings.
3. **Downstream Entity Linker & API Route Alignment:**
   - [`src/graphrag/entity_linker.py`](file:///Users/diesel/Desktop/LAG/.sandcastle/worktrees/agent-plan-20261013T225035-656-0beg/src/graphrag/entity_linker.py) (line 36) and [`src/api/routes.py`](file:///Users/diesel/Desktop/LAG/.sandcastle/worktrees/agent-plan-20261013T225035-656-0beg/src/api/routes.py) must recognize both `"DME-MAC-PUB-LYMPHEDEMA"` and legacy `"A59508"` / `"CMS-MCD-A59508"` queries (mapping `"A59508"` to the `CoveragePolicyNode` `"DME-MAC-PUB-LYMPHEDEMA"` via `legacy_article_id`), as well as active transmittal `"R12471CP"`, superseded transmittal `"R12379CP"`, ICD-10 `"I97.89"`, and all 77 HCPCS codes (`A6520`–`A6610`).
4. **Verification Suite Alignment (`tests/test_graph_pipeline.py`):**
   - Existing tests in [`tests/test_graph_pipeline.py`](file:///Users/diesel/Desktop/LAG/.sandcastle/worktrees/agent-plan-20261013T225035-656-0beg/tests/test_graph_pipeline.py) must be updated and expanded to verify every hop (Hops 0 through 7), every typed handoff model (`LegislativeHandoff`, `StatutoryHandoff`, `RegulatoryHandoff`, `OperationalHandoff`, `CoverageHandoff`, `CodingHandoff`, `ReimbursementHandoff`), all 8 fail-fast exceptions (`LegislativeResolutionError` through `FeeScheduleIngestionError`), the 5 amended USC citations for Section 4133, the active transmittal `R12471CP` (superseding `R12379CP`), the Joint DME MAC coverage guidance node `DME-MAC-PUB-LYMPHEDEMA` with 4 ICD-10 codes (`I89.0`, `I97.2`, `I97.89`, `Q82.0`), the 77 `LC` HCPCS codes (`A6520`–`A6610` including the 7 `LOCAL_CONTRACTOR_PRICING` NOS codes), and the 54-jurisdiction fee schedule unpivot.

## Architectural Decisions Locked

### 1. `PropertyGraphEngine` 8-Hop Orchestration & Handoff Ledger (`src/graph/engine.py`)
In [`src/graph/engine.py`](file:///Users/diesel/Desktop/LAG/.sandcastle/worktrees/agent-plan-20261013T225035-656-0beg/src/graph/engine.py):
- Add `self.handoffs: dict[str, Any] = {}` to `PropertyGraphEngine.__init__`.
- In `build_pipeline(self, policy_keyword: str = "LTA")`:
  1. Execute **Hops 0 & 1** via `ingest_legislative_tier(self, policy_keyword=policy_keyword)` $\to$ store `self.handoffs["legislative"] = t1_handoff`.
  2. Execute **Hop 2** via `ingest_statutory_tier(self, t1_handoff)` $\to$ store `self.handoffs["statutory"] = t2_handoff`.
  3. Execute **Hops 3 & 4** via `ingest_regulatory_tier(self, t2_handoff, policy_keyword=policy_keyword)` $\to$ store `self.handoffs["regulatory"] = t3_handoff.regulatory_handoff` and `self.handoffs["operational"] = t3_handoff.operational_handoff`.
  4. Execute **Hops 5 & 6** via `ingest_coverage_tier(self, t3_handoff, policy_keyword=policy_keyword)` $\to$ store `self.handoffs["coverage"] = coverage_handoff` and `self.handoffs["coding"] = coding_handoff`.
  5. Execute **Hop 7** via `ingest_fee_schedule_tier(self, coding_handoff, policy_keyword=policy_keyword)` $\to$ store `self.handoffs["reimbursement"] = reimbursement_handoff`.
  6. Execute **Tier 5 Context** via `ingest_context_tier(self, policy_keyword=policy_keyword, legislative_handoff=t1_handoff, statutory_handoff=t2_handoff, regulatory_handoff=t3_handoff.regulatory_handoff)`.

### 2. Dynamic Handoff Consumption in `tier5_context.py`
In [`src/graph/tier5_context.py`](file:///Users/diesel/Desktop/LAG/.sandcastle/worktrees/agent-plan-20261013T225035-656-0beg/src/graph/tier5_context.py) (lines 159–203):
- Update `ingest_context_tier` to accept optional `legislative_handoff`, `statutory_handoff`, and `regulatory_handoff`.
- Derive `bill_id = legislative_handoff.introduced_bill_id`, `stat_id = f"STAT-{legislative_handoff.public_law_id.removeprefix('PLAW-')}-SEC-{statutory_handoff.statute_section_number}"`, and `reg_id = f"REG-FR-{regulatory_handoff.fr_document_number}"` dynamically from the handoffs when provided (falling back to node inspection in `engine.nodes` only when invoked standalone).

### 3. Entity Linker & API Lookup Compatibility (`src/graphrag/entity_linker.py`)
In [`src/graphrag/entity_linker.py`](file:///Users/diesel/Desktop/LAG/.sandcastle/worktrees/agent-plan-20261013T225035-656-0beg/src/graphrag/entity_linker.py):
- Ensure regex and keyword entity linking resolves `"DME-MAC-PUB-LYMPHEDEMA"`, `"DME-MAC-PUB-IVIG"`, `"R12471CP"`, `"R12379CP"`, `"I97.89"`, and legacy article reference `"A59508"` (resolving to the `CoveragePolicy` node matching `article_id` or `legacy_article_id`).

### 4. Comprehensive Verification Suite (`tests/test_graph_pipeline.py`)
In [`tests/test_graph_pipeline.py`](file:///Users/diesel/Desktop/LAG/.sandcastle/worktrees/agent-plan-20261013T225035-656-0beg/tests/test_graph_pipeline.py):
- Update and expand tests to assert:
  - **Hop 0 & 1 (`LegislativeHandoff`):** `BILL-117-hr-3630 -[:INCORPORATED_INTO]-> BILL-117-hr-2617 -[:ENACTED_AS]-> PLAW-117-328`, `congress == 117`, `enacted_date == "2022-12-29"`, and fail-fast `LegislativeResolutionError` / `EnactedLawNotFoundError`.
  - **Hop 2 (`StatutoryHandoff`):** `uslm_section_path == "/us/pl/117/328/dFF/tIV/stD/s4133"`, `statute_section_number == "4133"`, all 5 amended USC citations (`42 U.S.C. 1395x(s)(2)(JJ)`, `42 U.S.C. 1395x(mmm)`, `42 U.S.C. 1395l(a)(1)(GG)`, `42 U.S.C. 1395m(z)`, `42 U.S.C. 1395w-3(a)(2)(D)`), `effective_date == "2024-01-01"`, and fail-fast `StatutorySectionNotFoundError`.
  - **Hop 3 (`RegulatoryHandoff`):** `fr_document_number == "2023-24455"`, `fr_citation == "88 FR 77676"`, `docket_id == "CMS-1780-F"`, `rin == "0938-AV03"`, `cfr_references` containing `42 CFR Part 410`, `42 CFR Part 414`, `42 CFR Part 424`, `42 CFR Part 484`, and fail-fast `RegulatoryRuleResolutionError`.
  - **Hop 4 (`OperationalHandoff`):** `change_request_number == "13286"`, `active_transmittal_number == "R12471CP"`, `superseded_transmittal_numbers == ["R12379CP"]`, `cms_manual_publication == "100-04"`, `benefit_category_code == "LC"`, `pricing_indicator_code == "40"`, and fail-fast `OperationalDirectiveMissingError`.
  - **Hop 5 (`CoverageHandoff`):** `coverage_guidance_id == "DME-MAC-PUB-LYMPHEDEMA"`, `publisher_type == "DME_MAC_JOINT_PUBLICATION"`, `qualifying_icd10_codes == ["I89.0", "I97.2", "I97.89", "Q82.0"]`, and fail-fast `ClinicalCoverageMissingError`.
  - **Hop 6 (`CodingHandoff`):** `benefit_category_code == "LC"`, `betos_code == "O1L"`, `len(hcpcs_codes) == 77` (`A6520`–`A6610`), and fail-fast `CodingTableMismatchError`.
  - **Hop 7 (`ReimbursementHandoff`):** `fee_schedule_release == "2024-JAN"`, `jurisdiction_count == 54`, `unpriced_custom_codes == ["A6549", "A6559", "A6560", "A6561", "A6584", "A6593", "A6609"]`, 3,780 numeric `FeeScheduleRateNode` records (`A6530` TX NR `$24.97`, TX R `$25.20`; `A6520` CA NR `$82.34`), and fail-fast `FeeScheduleIngestionError`.

## Target Files & Line-Range Edits
- [`src/graph/engine.py`](file:///Users/diesel/Desktop/LAG/.sandcastle/worktrees/agent-plan-20261013T225035-656-0beg/src/graph/engine.py) (lines 38–46, 180–245): Add `self.handoffs` ledger and wire all 8 hop handoffs through `build_pipeline`.
- [`src/graph/tier5_context.py`](file:///Users/diesel/Desktop/LAG/.sandcastle/worktrees/agent-plan-20261013T225035-656-0beg/src/graph/tier5_context.py) (lines 159–204): Consume upstream handoffs instead of hardcoded node IDs.
- [`src/graphrag/entity_linker.py`](file:///Users/diesel/Desktop/LAG/.sandcastle/worktrees/agent-plan-20261013T225035-656-0beg/src/graphrag/entity_linker.py) (lines 1–120): Support `DME-MAC-PUB-*`, `R12471CP`, `I97.89`, and `legacy_article_id` resolution.
- [`tests/test_graph_pipeline.py`](file:///Users/diesel/Desktop/LAG/.sandcastle/worktrees/agent-plan-20261013T225035-656-0beg/tests/test_graph_pipeline.py) (lines 1–266): Update assertions for the 8-hop autonomous pipeline and add unit tests for all 8 handoff contracts and 8 fail-fast exceptions.

## Verification Criteria
- Full pytest suite (`pytest tests/test_graph_pipeline.py tests/test_api_endpoints.py tests/test_graphrag_pipeline.py`) passes with zero errors and verifies all 8 hops and fail-fast boundaries.
