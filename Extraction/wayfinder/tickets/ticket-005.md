# Ticket 005: Hop 5 & Hop 6 — CMS MCD to Joint DME MAC Alternative Source Discovery & 77-Code HCPCS Alpha-Numeric Direct Linkage

## Status
**Locked** — Architectural Decision & Edit Plan

## Context & Problem Statement
[`src/graph/tier4a_coverage.py`](file:///Users/diesel/Desktop/LAG/.sandcastle/worktrees/agent-plan-20261013T225035-656-0beg/src/graph/tier4a_coverage.py) (lines 42–204) currently exhibits three critical architectural defects identified in [`functional_specification_013.md`](file:///Users/diesel/Desktop/LAG/.sandcastle/worktrees/agent-plan-20261013T225035-656-0beg/functional_specification_013.md) Section 3 & Section 4 (Hops 5 and 6):
1. **Fictional CMS MCD Article ID (`A59508`):** Lines 61–73 hardcode `article_id = "A59508"` (`id="CMS-MCD-A59508"`). As proven by `CoveragePolicies_and_Jurisdictions Addition/assets/20261012T231057-024-zqga/stage4a_cms_mcd_a59508_web_probe.html`, `A59508` returns an HTTP 404 page in the CMS Medicare Coverage Database (MCD). For Lymphedema Compression Treatment Items (`LC`), no national NCD or standalone MCD Article exists; instead, clinical coverage guidance is published via Joint DME MAC Administrative Publications (CGS Administrators / Noridian Healthcare Solutions: *"Lymphedema Compression Treatment Items – Correct Coding and Billing"*).
2. **Incomplete ICD-10-CM Diagnosis Set:** Lines 111–115 hardcode only 3 diagnosis codes (`I89.0`, `I97.2`, `Q82.0`) and omit `I97.89` (*Other postprocedural complications and disorders of the circulatory system, not elsewhere classified*), which is one of the 4 qualifying ICD-10-CM diagnosis codes mandated by the Joint DME MAC publication and Section 4 (Hop 5) of `functional_specification_013.md`.
3. **Incomplete HCPCS Procedure Code Extraction (70 vs. 77 Codes):** Lines 126–151 read only the DMEPOS fee schedule CSV (`stage4b_cms_dmepos_lc_category.csv`), which contains only the 70 `LC` codes that have national fee schedule dollar amounts, omitting the 7 custom/not-otherwise-specified (NOS) `LC` codes (`A6549`, `A6559`, `A6560`, `A6561`, `A6584`, `A6593`, `A6609`) present in the official CMS January 2024 Alpha-Numeric HCPCS File (`HCPC2024_JAN_ANWEB_v4.txt` inside `january-2024-alpha-numeric-hcpcs-files.zip`) where `BETOS == "O1L"` and `Pricing Indicator == "40"` (`A6520`–`A6610`, 77 codes total).

## Architectural Decisions Locked

### 1. Hop 5: Alternative Source Discovery for Clinical Coverage Guidance (`discover_coverage_guidance`)
Implement deterministic two-tier source routing in [`src/graph/tier4a_coverage.py`](file:///Users/diesel/Desktop/LAG/.sandcastle/worktrees/agent-plan-20261013T225035-656-0beg/src/graph/tier4a_coverage.py):
- **Primary Probe (CMS Medicare Coverage Database):**
  - Query the CMS MCD search/document probe (`stage4a_cms_mcd_a59508_web_probe.html` or live MCD endpoint) for an LCD/NCD/Article matching `operational_handoff.change_request_number` (`"13286"`) or `benefit_category_code` (`"LC"`).
  - Detect the `<title>404</title>` / empty result in `stage4a_cms_mcd_a59508_web_probe.html` (rather than assuming `"A59508"` is valid).
- **Secondary Authoritative Routing (Joint DME MAC Administrative Publications):**
  - When the primary CMS MCD lookup returns 0 results / 404, deterministically route to the Joint DME MAC Administrative Publication repository (CGS / Noridian joint article corresponding to CR `13286` / `R12471CP` and benefit category `LC`).
  - Populate `CoverageHandoff`:
    - `coverage_guidance_id`: `"DME-MAC-PUB-LYMPHEDEMA"` (for `LC` / CR `13286`) or `"DME-MAC-PUB-IVIG"` (for `IVIG` / CR `13217`)
    - `publisher_type`: `"DME_MAC_JOINT_PUBLICATION"`
    - `publication_title`: `"Lymphedema Compression Treatment Items – Correct Coding and Billing"` (for `LC`) or `"Intravenous Immune Globulin (IVIG) – In-Home Administration Coverage and Billing"` (for `IVIG`)
    - `qualifying_icd10_codes`: `["I89.0", "I97.2", "I97.89", "Q82.0"]` for `LC` (`["D80.0", "D81.9", "D83.9"]` for `IVIG`)
    - `clinical_prerequisites`: `["Documented diagnosis of lymphedema (ICD-10-CM I89.0, I97.2, I97.89, or Q82.0)", "Prescription by a treating physician or qualified non-physician practitioner", "Custom-fitted gradient compression garments require specific anatomic measurements"]`
- **Graph Node & Edge Emission:**
  - Emit `CoveragePolicyNode` with `id="DME-MAC-PUB-LYMPHEDEMA"`, `article_id="DME-MAC-PUB-LYMPHEDEMA"`, `legacy_article_id="A59508"`, `publisher_type="DME_MAC_JOINT_PUBLICATION"`, `publication_title="Lymphedema Compression Treatment Items – Correct Coding and Billing"`, `policy_type="DME_MAC_JOINT_PUBLICATION"`, `contractor_name="CGS Administrators / Noridian Healthcare Solutions (Joint DME MAC)"`.
  - Emit all 4 `DiagnosisCodeNode` records (`ICD10-I89.0`, `ICD10-I97.2`, `ICD10-I97.89`, `ICD10-Q82.0` for `LC`, where `I97.89` has description `"Other postprocedural complications and disorders of the circulatory system, not elsewhere classified"`).
  - Wire edges:
    - `(:Transmittal)-[:MANDATES_POLICY]->(:CoveragePolicy)`
    - `(:CoveragePolicy)-[:REQUIRES_DIAGNOSIS]->(:DiagnosisCode)`
- **Fail-Fast Boundary:** Raise `ClinicalCoverageMissingError` if both primary CMS MCD and secondary Joint DME MAC Administrative Publication discovery return zero matching coverage documents or zero qualifying ICD-10-CM diagnosis codes.

### 2. Hop 6: 77-Code HCPCS Alpha-Numeric Direct Linkage (`discover_hcpcs_code_set`)
Implement complete 77-code HCPCS extraction in [`src/graph/tier4a_coverage.py`](file:///Users/diesel/Desktop/LAG/.sandcastle/worktrees/agent-plan-20261013T225035-656-0beg/src/graph/tier4a_coverage.py):
- **Authoritative Source Resolution:**
  - Filter by `operational_handoff.benefit_category_code` (`"LC"` $\to$ `BETOS == "O1L"`, `Pricing Indicator == "40"`, code range `A6520`–`A6610`; `"IVIG"` $\to$ `BETOS == "O1E"`, `Pricing Indicator in ("57", "51")`, codes `J1459`, `J1556`, `J1557`, `J1559`, `J1561`, `J1566`, `J1568`, `J1569`, `J1572`, `J1599`, `Q2052`).
  - Parse the CMS January 2024 Alpha-Numeric HCPCS file (`HCPC2024_JAN_ANWEB_v4.txt` when present in `asset_dir` or cached zip) OR combine the 70 standard `LC` codes in `phase4_cms_dmepos_lc_category.csv` (`A6520`–`A6544`, `A6552`–`A6558`, `A6562`–`A6583`, `A6585`–`A6592`, `A6594`–`A6608`, `A6610`) with the 7 official CR 13286 / `HCPC2024_JAN_ANWEB_v4.txt` `O1L` / `PI 40` custom/NOS codes that lack national numeric rate columns in `DMEPOS_JAN.csv`:
    1. `A6549`: `"Gradient compression stocking, not otherwise specified"` (`BETOS="O1L"`, `pricing_indicator="40"`, `pricing_methodology="LOCAL_CONTRACTOR_PRICING"`)
    2. `A6559`: `"Gradient compression garment, lower extremity, custom, not otherwise specified"` (`BETOS="O1L"`, `pricing_indicator="40"`, `pricing_methodology="LOCAL_CONTRACTOR_PRICING"`)
    3. `A6560`: `"Gradient compression garment, upper extremity, custom, not otherwise specified"` (`BETOS="O1L"`, `pricing_indicator="40"`, `pricing_methodology="LOCAL_CONTRACTOR_PRICING"`)
    4. `A6561`: `"Gradient compression garment, torso/trunk, custom, not otherwise specified"` (`BETOS="O1L"`, `pricing_indicator="40"`, `pricing_methodology="LOCAL_CONTRACTOR_PRICING"`)
    5. `A6584`: `"Gradient compression wrap with adjustable straps, not otherwise specified"` (`BETOS="O1L"`, `pricing_indicator="40"`, `pricing_methodology="LOCAL_CONTRACTOR_PRICING"`)
    6. `A6593`: `"Accessory for gradient compression garment or wrap, not otherwise specified"` (`BETOS="O1L"`, `pricing_indicator="40"`, `pricing_methodology="LOCAL_CONTRACTOR_PRICING"`)
    7. `A6609`: `"Gradient compression bandaging supply, not otherwise specified"` (`BETOS="O1L"`, `pricing_indicator="40"`, `pricing_methodology="LOCAL_CONTRACTOR_PRICING"`)
- **Return Contract (`CodingHandoff`):**
  - Return `(CoverageHandoff, CodingHandoff)` where `CodingHandoff.hcpcs_codes` contains all **77 sorted HCPCS codes** (`A6520`–`A6610`) for `LC`, `betos_code="O1L"`, `benefit_category_code="LC"`, `code_descriptions` mapping all 77 codes to their official descriptions, and `code_pricing_indicators` mapping all 77 codes to `"40"`.
- **Graph Node & Edge Emission:**
  - Emit all 77 `ProcedureCodeNode` records (`HCPCS-A6520` through `HCPCS-A6610`) with `betos_code="O1L"`, `pricing_indicator="40"`, and `pricing_methodology="NATIONAL_FEE_SCHEDULE"` (for the 70 priced codes) or `"LOCAL_CONTRACTOR_PRICING"` (for the 7 NOS/custom codes).
  - Wire `(:CoveragePolicy)-[:COVERS_PROCEDURE]->(:ProcedureCode)` for all 77 codes.
- **Fail-Fast Boundary:** Raise `CodingTableMismatchError` if 0 HCPCS codes match the operational Benefit Category / BETOS filter or if any code lacks description/pricing indicator metadata.

## Target Files & Line-Range Edits
- [`src/graph/tier4a_coverage.py`](file:///Users/diesel/Desktop/LAG/.sandcastle/worktrees/agent-plan-20261013T225035-656-0beg/src/graph/tier4a_coverage.py) (lines 1–205):
  - Implement `discover_coverage_guidance(engine, operational_handoff, policy_keyword) -> CoverageHandoff` (Hop 5) and `discover_hcpcs_code_set(engine, operational_handoff, coverage_handoff, policy_keyword) -> CodingHandoff` (Hop 6).
  - Update `ingest_coverage_tier` to execute Hop 5 and Hop 6, returning `CodingHandoff` (or attaching `coverage_handoff` and `coding_handoff` while also allowing `list[str]` iteration or `.hcpcs_codes` access for callers).
  - Add `"I97.89"` to the qualifying ICD-10-CM diagnosis codes for `LC` and include all 77 `A6520`–`A6610` HCPCS codes.

## Verification Criteria
- Hop 5 probes `stage4a_cms_mcd_a59508_web_probe.html`, detects the 404, routes to Joint DME MAC publication `"DME-MAC-PUB-LYMPHEDEMA"`, and creates 4 `DiagnosisCodeNode`s (`I89.0`, `I97.2`, `I97.89`, `Q82.0`).
- Hop 6 extracts all 77 `LC` (`O1L` / `PI 40`) HCPCS codes (`A6520`–`A6610`), comprising 70 standard codes and 7 `LOCAL_CONTRACTOR_PRICING` NOS/custom codes (`A6549`, `A6559`, `A6560`, `A6561`, `A6584`, `A6593`, `A6609`).
