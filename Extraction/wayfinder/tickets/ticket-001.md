# Ticket 001: Typed Pipeline Handoff Contracts, Graph Node Schema Extensions, and Fail-Fast Exception Hierarchy

## Status
**Locked** — Architectural Decision & Edit Plan

## Context & Problem Statement
In [`src/graph/models.py`](file:///Users/diesel/Desktop/LAG/.sandcastle/worktrees/agent-plan-20261013T225035-656-0beg/src/graph/models.py) (lines 240–279), the existing pipeline only defines three partial handoff models (`Tier1Handoff`, `Tier2Handoff`, `Tier3Handoff`) and lacks typed stage-to-stage handoff contracts for Operational Directives (Hop 4), Clinical Coverage Guidance (Hop 5), HCPCS Coding Tables (Hop 6), and State Fee Schedule Matrices (Hop 7). Furthermore, [`functional_specification_013.md`](file:///Users/diesel/Desktop/LAG/.sandcastle/worktrees/agent-plan-20261013T225035-656-0beg/functional_specification_013.md) Section 5 and Section 6 mandate strict Pydantic handoff schemas (`LegislativeHandoff`, `StatutoryHandoff`, `RegulatoryHandoff`, `OperationalHandoff`, `CoverageHandoff`, `CodingHandoff`, `FeeScheduleRecord`, `ReimbursementHandoff`) and an 8-stage fail-fast exception hierarchy (`LegislativeResolutionError`, `EnactedLawNotFoundError`, `StatutorySectionNotFoundError`, `RegulatoryRuleResolutionError`, `OperationalDirectiveMissingError`, `ClinicalCoverageMissingError`, `CodingTableMismatchError`, `FeeScheduleIngestionError`).

Additionally, `TransmittalNode`, `CoveragePolicyNode`, `ProcedureCodeNode`, and `FeeScheduleRateNode` require explicit fields to track supersession lineage (`superseded_transmittal_numbers`, `benefit_category_code`, `pricing_indicator_code`), publisher provenance (`publisher_type`, `publication_source_title`), BETOS/pricing classifications (`betos_code`, `pricing_indicator`), and local contractor pricing methodology (`pricing_methodology`, `jurisdiction_postal_code`, `rural_designation`) without breaking existing node fields consumed by `src/graph/neo4j_sync.py`, `src/api/routes.py`, or `src/graphrag/`.

## Architectural Decisions Locked

### 1. Canonical Fail-Fast Exception Hierarchy (`src/graph/models.py`)
Define a base `PolicyTraversalError(RuntimeError)` in [`src/graph/models.py`](file:///Users/diesel/Desktop/LAG/.sandcastle/worktrees/agent-plan-20261013T225035-656-0beg/src/graph/models.py) and derive all 8 specification-mandated hop exceptions from it:
- `LegislativeResolutionError(PolicyTraversalError)` — Raised in Hop 0 when Congress.gov search returns 0 items, authentication fails, or no candidate advocacy bill matches `{Policy Keyword}`.
- `EnactedLawNotFoundError(PolicyTraversalError)` — Raised in Hop 1 when neither `bill.laws` nor `relatedbills[*].laws` resolves to an enacted Public Law (`Public Law` or `PLAW-{congress}-{number}`).
- `StatutorySectionNotFoundError(PolicyTraversalError)` — Raised in Hop 2 when the GovInfo USLM XML package is unreachable/corrupted or contains no `<section>` matching the policy keyword or statutory division/section identifier, or yields zero amended U.S. Code citations.
- `RegulatoryRuleResolutionError(PolicyTraversalError)` — Raised in Hop 3 when the Federal Register API query returns 0 final rules (`type="RULE"`) for the target USC citation and agency (`centers-for-medicare-medicaid-services`), or lacks CFR references.
- `OperationalDirectiveMissingError(PolicyTraversalError)` — Raised in Hop 4 when no CMS Change Request (CR) or active Transmittal ID is discovered for the regulation/statute, or when operational Benefit Category (`benefit_category_code`) and Pricing Indicator (`pricing_indicator_code`) cannot be extracted.
- `ClinicalCoverageMissingError(PolicyTraversalError)` — Raised in Hop 5 when both the primary CMS Medicare Coverage Database (MCD) lookup and the secondary Joint DME MAC Administrative Publication discovery fail to yield coverage guidance and qualifying ICD-10-CM diagnosis codes.
- `CodingTableMismatchError(PolicyTraversalError)` — Raised in Hop 6 when the HCPCS Alpha-Numeric repository / CR attachment yields zero procedure codes matching the operational Benefit Category / BETOS / Pricing Indicator filter.
- `FeeScheduleIngestionError(PolicyTraversalError)` — Raised in Hop 7 when the DMEPOS Fee Schedule release lacks rows for the target Benefit Category (`CATG`), fails 54-jurisdiction unpivoting, or leaves any of the extracted HCPCS codes unaccounted for across national rates and local contractor pricing rules.

To preserve backward compatibility with existing module imports and tests, alias or subclass the legacy stage exceptions (`Phase1LegislativeError = LegislativeResolutionError`, `Phase2StatutoryError = StatutorySectionNotFoundError`, `Phase3RegulatoryError = RegulatoryRuleResolutionError`, `Phase4aCoverageError = ClinicalCoverageMissingError`, `Phase4bFeeScheduleError = FeeScheduleIngestionError`, `Phase5ContextError(PolicyTraversalError)`).

### 2. Specification-Exact Typed Handoff Models (`src/graph/models.py`)
Define all 8 Pydantic handoff contracts in [`src/graph/models.py`](file:///Users/diesel/Desktop/LAG/.sandcastle/worktrees/agent-plan-20261013T225035-656-0beg/src/graph/models.py) (lines 240–280) with `ConfigDict(extra="forbid")`:

1. **`LegislativeHandoff` (Hops 0 $\to$ 1 Output):**
   - `policy_keyword: str`
   - `introduced_bill_id: str` (e.g., `"BILL-117-hr-3630"`)
   - `enacting_bill_id: str` (e.g., `"BILL-117-hr-2617"`)
   - `public_law_id: str` (e.g., `"PLAW-117-328"`)
   - `congress: int` (e.g., `117`)
   - `enacted_date: str` (e.g., `"2022-12-29"`)
   - Backward-compatible computed/default properties or fields (`bill_id` defaulting to `introduced_bill_id`, `enacting_vehicle_id` defaulting to `enacting_bill_id`) via `Tier1Handoff(LegislativeHandoff)` subclass so callers inspecting either contract name or attribute set succeed deterministically.

2. **`StatutoryHandoff` (Hop 2 Output):**
   - `public_law_id: str` (e.g., `"PLAW-117-328"`)
   - `uslm_section_path: str` (e.g., `"/us/pl/117/328/dFF/tIV/stD/s4133"`)
   - `statute_section_number: str` (e.g., `"4133"`)
   - `statute_heading: str` (e.g., `"Medicare coverage of lymphedema compression treatment items"`)
   - `amended_usc_citations: list[str]` (e.g., `["42 U.S.C. 1395x(s)(2)(JJ)", "42 U.S.C. 1395x(mmm)", "42 U.S.C. 1395l(a)(1)(GG)", "42 U.S.C. 1395m(z)", "42 U.S.C. 1395w-3(a)(2)(D)"]`)
   - `effective_date: str` (e.g., `"2024-01-01"`)
   - Subclass `Tier2Handoff(StatutoryHandoff)` adding `statutory_section_id: str` (e.g., `"STAT-117-328-SEC-4133"`) and `usc_section_ids: list[str]` (e.g., `["USC-42-1395x-s-2-JJ", "USC-42-1395x-mmm", ...]`) for seamless graph edge wiring.

3. **`RegulatoryHandoff` (Hop 3 Output):**
   - `fr_document_number: str` (e.g., `"2023-24455"`)
   - `fr_citation: str` (e.g., `"88 FR 77676"`)
   - `docket_id: str` (e.g., `"CMS-1780-F"`)
   - `rin: str` (e.g., `"0938-AV03"`)
   - `cfr_references: list[str]` (e.g., `["42 CFR Part 410", "42 CFR Part 414", "42 CFR Part 424", "42 CFR Part 484"]` alongside specific codified parts `"42 CFR 410.36"`, `"42 CFR 414.1600"`, `"42 CFR 414.1650"`, `"42 CFR 414.1690"`)
   - `effective_date: str` (e.g., `"2024-01-01"`)

4. **`OperationalHandoff` (Hop 4 Output):**
   - `change_request_number: str` (e.g., `"13286"`)
   - `active_transmittal_number: str` (e.g., `"R12471CP"`)
   - `superseded_transmittal_numbers: list[str]` (e.g., `["R12379CP"]`)
   - `cms_manual_publication: str` (e.g., `"100-04"`)
   - `benefit_category_code: str` (e.g., `"LC"`)
   - `pricing_indicator_code: str` (e.g., `"40"`)
   - `effective_date: str` (e.g., `"2024-01-01"`)
   - Maintain `Tier3Handoff` compatibility so callers expecting combined regulatory + operational identifiers (`fr_document_number`, `cfr_section_ids`, `transmittal_id`, `cr_number`, `benefit_category`) have full access.

5. **`CoverageHandoff` (Hop 5 Output):**
   - `coverage_guidance_id: str` (e.g., `"DME-MAC-PUB-LYMPHEDEMA"`)
   - `publisher_type: Literal["CMS_MCD", "DME_MAC_JOINT_PUBLICATION"]`
   - `publication_title: str` (e.g., `"Lymphedema Compression Treatment Items – Correct Coding and Billing"`)
   - `qualifying_icd10_codes: list[str]` (e.g., `["I89.0", "I97.2", "I97.89", "Q82.0"]`)
   - `clinical_prerequisites: list[str]`

6. **`CodingHandoff` (Hop 6 Output):**
   - `benefit_category_code: str` (e.g., `"LC"`)
   - `betos_code: str` (e.g., `"O1L"`)
   - `hcpcs_codes: list[str]` (all 77 procedure codes `A6520`–`A6610` for `LC`)
   - `code_descriptions: dict[str, str]`
   - `code_pricing_indicators: dict[str, str]` (mapping each HCPCS code to `"40"`, etc.)

7. **`FeeScheduleRecord` & `ReimbursementHandoff` (Hop 7 Output):**
   - `FeeScheduleRecord`:
     - `hcpcs_code: str`
     - `jurisdiction_postal_code: str` (2-letter state/territory code across all 54 DMEPOS columns)
     - `rural_designation: Literal["NR", "R"]`
     - `rate_usd: Optional[float]` (`None` for gap/custom codes priced by local contractor)
     - `pricing_methodology: Literal["NATIONAL_FEE_SCHEDULE", "LOCAL_CONTRACTOR_PRICING"]`
   - `ReimbursementHandoff`:
     - `fee_schedule_release: str` (e.g., `"2024-JAN"`)
     - `jurisdiction_count: int` (`54`)
     - `records: list[FeeScheduleRecord]`
     - `unpriced_custom_codes: list[str]` (`["A6549", "A6559", "A6560", "A6561", "A6584", "A6593", "A6609"]`)

### 3. Node Model Extensions (`src/graph/models.py`)
Extend the existing node models in [`src/graph/models.py`](file:///Users/diesel/Desktop/LAG/.sandcastle/worktrees/agent-plan-20261013T225035-656-0beg/src/graph/models.py) with optional/defaulted fields so both the new autonomous pipeline and existing Neo4j / API / GraphRAG consumers operate seamlessly:
- `TransmittalNode` (lines 118–128): add `superseded_transmittal_numbers: list[str] = Field(default_factory=list)` and `pricing_indicator_code: Optional[str] = None`.
- `CoveragePolicyNode` (lines 130–141): add `publisher_type: str = "DME_MAC_JOINT_PUBLICATION"`, `publication_title: Optional[str] = None`, and `legacy_article_id: Optional[str] = None` (to record that MCD lookup for `"A59508"` returned 404 and routed to `"DME-MAC-PUB-LYMPHEDEMA"` while still allowing entity linker lookup by either ID).
- `ProcedureCodeNode` (lines 154–165): add `betos_code: Optional[str] = None`, `pricing_indicator: Optional[str] = None`, and `pricing_methodology: str = "NATIONAL_FEE_SCHEDULE"`.
- `FeeScheduleRateNode` (lines 178–194): make `non_rural_rate: Optional[float] = None` and `rural_rate: Optional[float] = None` optional (to support the 7 `LOCAL_CONTRACTOR_PRICING` gap codes `A6549`, `A6559`, `A6560`, `A6561`, `A6584`, `A6593`, `A6609` without fabricating dollar amounts), and add `pricing_methodology: str = "NATIONAL_FEE_SCHEDULE"`.

## Target Files & Line-Range Edits
- [`src/graph/models.py`](file:///Users/diesel/Desktop/LAG/.sandcastle/worktrees/agent-plan-20261013T225035-656-0beg/src/graph/models.py) (lines 118–280): Update `TransmittalNode`, `CoveragePolicyNode`, `ProcedureCodeNode`, `FeeScheduleRateNode`; add the 8 fail-fast exception classes; replace/extend lines 240–280 with the 8 specification-mandated handoff models (`LegislativeHandoff`, `StatutoryHandoff`, `RegulatoryHandoff`, `OperationalHandoff`, `CoverageHandoff`, `CodingHandoff`, `FeeScheduleRecord`, `ReimbursementHandoff`) and backward-compatible `Tier1Handoff`, `Tier2Handoff`, `Tier3Handoff` subclasses.
- [`src/graph/__init__.py`](file:///Users/diesel/Desktop/LAG/.sandcastle/worktrees/agent-plan-20261013T225035-656-0beg/src/graph/__init__.py) (lines 1–57): Export all new handoff models and fail-fast exception classes in `__all__`.

## Verification Criteria
- Instantiating each of the 8 handoff models with valid data succeeds; passing extra unknown fields raises `ValidationError` (`extra="forbid"`).
- All 8 fail-fast exceptions (`LegislativeResolutionError` through `FeeScheduleIngestionError`) are importable from `src.graph.models` and `src.graph`.
