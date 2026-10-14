# Ticket 006: Hop 7 — 54-Jurisdiction DMEPOS Fee Schedule Unpivoting & Local Contractor Pricing Gap-Filling

## Status
**Locked** — Architectural Decision & Edit Plan

## Context & Problem Statement
[`src/graph/tier4b_fee_schedule.py`](file:///Users/diesel/Desktop/LAG/.sandcastle/worktrees/agent-plan-20261013T225035-656-0beg/src/graph/tier4b_fee_schedule.py) (lines 142–300) currently exhibits three gaps relative to [`functional_specification_013.md`](file:///Users/diesel/Desktop/LAG/.sandcastle/worktrees/agent-plan-20261013T225035-656-0beg/functional_specification_013.md) Section 3, Section 4 (Hop 7), and Section 5 (`FeeScheduleRecord`, `ReimbursementHandoff`):
1. **Static File & Category Assumption:** `ingest_fee_schedule_tier` does not consume `CodingHandoff` (`benefit_category_code`, `hcpcs_codes`, `code_pricing_indicators`) and `OperationalHandoff` (`pricing_indicator_code`), nor does it return a typed `ReimbursementHandoff`.
2. **Missing Gap-Code Accounting for the 7 Local-Contractor-Priced NOS Codes:** In `DMEPOS_JAN.csv` (inside `phase4_cms_dmepos_fee_schedule_2024.zip`) and `phase4_cms_dmepos_lc_category.csv`, 70 of the 77 `LC` HCPCS codes have national numeric payment amounts across all 54 jurisdictions (`AL (NR)` through `VI (R)` = 108 columns), yielding `70 * 54 = 3,780` state-level `FeeScheduleRateNode` records (and `70 * 108 = 7,560` NR/R `FeeScheduleRecord` entries). However, the 7 custom/NOS codes (`A6549`, `A6559`, `A6560`, `A6561`, `A6584`, `A6593`, `A6609`) are omitted from `DMEPOS_JAN.csv` because CMS CR 13286 (`R12471CP`) designates them for individual consideration / local contractor pricing by the 4 DME MACs.
3. **Strict Fail-Fast Accounting:** Section 4 (Hop 7) requires failing fast with `FeeScheduleIngestionError` if the fee schedule archive fails to unpivot all 54 jurisdictions or if any code in `CodingHandoff.hcpcs_codes` is neither present in the national DMEPOS fee schedule rows nor explicitly classified under `LOCAL_CONTRACTOR_PRICING` (`unpriced_custom_codes`).

## Architectural Decisions Locked

### 1. Authoritative DMEPOS Fee Schedule Archive & CSV Resolution
In [`src/graph/tier4b_fee_schedule.py`](file:///Users/diesel/Desktop/LAG/.sandcastle/worktrees/agent-plan-20261013T225035-656-0beg/src/graph/tier4b_fee_schedule.py):
- Accept `coding_handoff: CodingHandoff | list[str]` (supporting both the new `CodingHandoff` contract and legacy `list[str]` callers).
- Resolve the DMEPOS fee schedule from `phase4_cms_dmepos_lc_category.csv` / `stage4b_cms_dmepos_lc_category.csv` or directly from `DMEPOS_JAN.csv` inside `phase4_cms_dmepos_fee_schedule_2024.zip` (skipping the 6-line preamble header in `DMEPOS_JAN.csv` to reach `YEAR,JURIS,CATG,HCPCS,MOD,MOD2,...`).
- Filter rows where `CATG.strip() == benefit_category_code` (`"LC"`) and `HCPCS.strip()` is in `target_hcpcs_codes`.

### 2. 54-Jurisdiction Unpivoting & Gap-Code Reconciliation
- Extract all 54 state/territory postal codes (`AL`, `AK`, `AZ`, `AR`, `CA`, `CO`, `CT`, `DE`, `DC`, `FL`, `GA`, `HI`, `ID`, `IL`, `IN`, `IA`, `KS`, `KY`, `LA`, `ME`, `MD`, `MA`, `MI`, `MN`, `MS`, `MO`, `MT`, `NE`, `NV`, `NH`, `NJ`, `NM`, `NY`, `NC`, `ND`, `OH`, `OK`, `OR`, `PA`, `PR`, `RI`, `SC`, `SD`, `TN`, `TX`, `UT`, `VT`, `VA`, `VI`, `WA`, `WV`, `WI`, `WY`, `GU` / all 54 columns in `DMEPOS_JAN.csv`). Verify `len(states) == 54`; otherwise raise `FeeScheduleIngestionError`.
- For each of the 70 standard `LC` codes present in `DMEPOS_JAN.csv`:
  - Parse `f"{state} (NR)"` and `f"{state} (R)"` into `float` rates (raising `FeeScheduleIngestionError` if a value is missing or non-numeric).
  - Emit a `FeeScheduleRateNode` (`id=f"RATE-{hcpcs}-2024-{state}"`, `hcpcs_code=hcpcs`, `state_abbr=state`, `non_rural_rate=nr_rate`, `rural_rate=r_rate`, `pricing_methodology="NATIONAL_FEE_SCHEDULE"`) and wire `(:ProcedureCode)-[:HAS_RATE]->(:FeeScheduleRate)` and `(:FeeScheduleRate)-[:APPLIES_IN_STATE]->(:Jurisdiction)`.
  - Append two `FeeScheduleRecord` entries to `ReimbursementHandoff.records`: one for `rural_designation="NR"` (`rate_usd=nr_rate`) and one for `rural_designation="R"` (`rate_usd=r_rate`), both with `pricing_methodology="NATIONAL_FEE_SCHEDULE"`.
- For the 7 `LC` custom/NOS codes in `CodingHandoff.hcpcs_codes` that are absent from `DMEPOS_JAN.csv` (`A6549`, `A6559`, `A6560`, `A6561`, `A6584`, `A6593`, `A6609`):
  - Verify each code is explicitly flagged as an NOS / custom code eligible for `LOCAL_CONTRACTOR_PRICING` under `pricing_indicator == "40"`. If an unknown code is missing from `DMEPOS_JAN.csv` and is NOT a verified NOS/custom code, raise `FeeScheduleIngestionError`.
  - Record these 7 codes in `ReimbursementHandoff.unpriced_custom_codes = ["A6549", "A6559", "A6560", "A6561", "A6584", "A6593", "A6609"]` and append `FeeScheduleRecord` entries with `rate_usd=None`, `pricing_methodology="LOCAL_CONTRACTOR_PRICING"` across the 54 jurisdictions.
  - Keep `FeeScheduleRateNode` graph nodes strictly representing the `3,780` (`70 * 54`) verified numeric fee schedule rate nodes for `LC` so that no `FeeScheduleRateNode` in Neo4j has `None` dollar amounts and existing numerical graph queries (`non_rural_rate > 0`, `3,780` rate nodes) remain 100% intact.

### 3. Return Contract (`ReimbursementHandoff`)
Return a validated `ReimbursementHandoff`:
- `fee_schedule_release="2024-JAN"`
- `jurisdiction_count=54`
- `records`: list of `FeeScheduleRecord` instances (`70 * 108 = 7,560` national fee schedule records + `7 * 108 = 756` local contractor pricing records = `8,316` records across all 77 codes x 54 jurisdictions x 2 rural/non-rural designations)
- `unpriced_custom_codes=["A6549", "A6559", "A6560", "A6561", "A6584", "A6593", "A6609"]`

## Target Files & Line-Range Edits
- [`src/graph/tier4b_fee_schedule.py`](file:///Users/diesel/Desktop/LAG/.sandcastle/worktrees/agent-plan-20261013T225035-656-0beg/src/graph/tier4b_fee_schedule.py) (lines 142–301):
  - Update `ingest_fee_schedule_tier` signature and implementation to consume `CodingHandoff` (or `list[str]`), support reading both `phase4_cms_dmepos_lc_category.csv` and `phase4_cms_dmepos_fee_schedule_2024.zip` (`DMEPOS_JAN.csv`), validate all 54 jurisdictions, reconcile the 70 national-rate codes and 7 `LOCAL_CONTRACTOR_PRICING` NOS codes, raise `FeeScheduleIngestionError` on any discrepancy, and return `ReimbursementHandoff`.

## Verification Criteria
- Running `ingest_fee_schedule_tier` with the 77-code `CodingHandoff` for `"LTA"` emits 54 `JurisdictionNode`s, 4 DME MAC `MACContractorNode`s, 3,780 `FeeScheduleRateNode`s with verified numeric `non_rural_rate` and `rural_rate`, and returns `ReimbursementHandoff` with `jurisdiction_count=54` and `unpriced_custom_codes=["A6549", "A6559", "A6560", "A6561", "A6584", "A6593", "A6609"]`.
- Passing an empty code list or a corrupted CSV missing state columns raises `FeeScheduleIngestionError`.
