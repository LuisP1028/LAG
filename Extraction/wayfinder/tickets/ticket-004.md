# Ticket 004: Hop 3 & Hop 4 — Federal Register Final Rule Discovery & CMS Transmittal Supersession / Operational Filter Extraction

## Status
**Locked** — Architectural Decision & Edit Plan

## Context & Problem Statement
[`src/graph/tier3_regulatory.py`](file:///Users/diesel/Desktop/LAG/.sandcastle/worktrees/agent-plan-20261013T225035-656-0beg/src/graph/tier3_regulatory.py) (lines 20–145) currently violates [`functional_specification_013.md`](file:///Users/diesel/Desktop/LAG/.sandcastle/worktrees/agent-plan-20261013T225035-656-0beg/functional_specification_013.md) Section 3 & Section 4 (Hops 3 and 4) in three ways:
1. **Static Federal Register File Open:** `ingest_regulatory_tier` directly opens `stage3_federal_register_rule_2023_24455.json` without querying the Federal Register Search API (`https://www.federalregister.gov/api/v1/documents.json`) or inspecting the search results payload (`phase3_federal_register_search_1395x.json`) using the incoming `StatutoryHandoff` (`statute_section_number`, `amended_usc_citations`, `statute_heading`).
2. **Hardcoded CFR Sections:** Lines 65–70 hardcode `["410.36", "414.1600", "414.1650", "414.1690"]` without extracting the official `cfr_references` array from the Federal Register Final Rule payload (`42 CFR Part 409, 410, 414, 424, 484, 488, 489`) Alongside the policy-specific CFR subparts implemented by the rule.
3. **Hardcoded & Outdated Transmittal Constants:** Lines 114–132 inject hardcoded constants `cr_number="13286"`, `transmittal_number="12349"` (which is inaccurate—the initial transmittal was `R12379CP`, superseded by active transmittal `R12471CP`), and `benefit_category="LC"`, performing zero discovery against CMS Transmittals (`2023-transmittals` / `2024-transmittals`) and failing to emit the separate `RegulatoryHandoff` (Hop 3) and `OperationalHandoff` (Hop 4) contracts.

## Architectural Decisions Locked

### 1. Hop 3: Federal Register Final Rule Search & Metadata Extraction (`discover_final_rule`)
Implement deterministic Hop 3 discovery in [`src/graph/tier3_regulatory.py`](file:///Users/diesel/Desktop/LAG/.sandcastle/worktrees/agent-plan-20261013T225035-656-0beg/src/graph/tier3_regulatory.py):
- **Search Query Construction:** Using `StatutoryHandoff` (`statute_section_number`, `statute_heading`, `amended_usc_citations`), query the Federal Register Search API (`GET https://www.federalregister.gov/api/v1/documents.json?conditions[term]={query_term}&conditions[type][]=RULE&conditions[agencies][]=centers-for-medicare-medicaid-services`) or resolve against the verified search payload (`phase3_federal_register_search_1395x.json`) when matching `1395x` / `Section 4133` / `Section 4134`, and fetch the corresponding document detail (`GET https://www.federalregister.gov/api/v1/documents/{document_number}.json` or `phase3_federal_register_rule_2023_24455.json`).
- **Rule Qualification:** Verify the rule is a Final Rule (`type == "Rule"`) whose `title`, `abstract`, or `body_html`/`mods` references the statutory authority (`1395x` / `Section 4133` / `Section 4134` / `Calendar Year (CY) 2024 Home Health Prospective Payment System Rate Update` `2023-24455`).
- **Field Extraction for `RegulatoryHandoff`:**
  - `fr_document_number`: `rule_data["document_number"]` (`"2023-24455"`)
  - `fr_citation`: `rule_data["citation"]` (`"88 FR 77676"`)
  - `docket_id`: `rule_data["docket_ids"][0]` (`"CMS-1780-F"`)
  - `rin`: `rule_data["regulation_id_numbers"][0]` (`"0938-AV03"` or normalized `"0938-AV03"` from `"0938-AV03 "` after `.strip()`)
  - `cfr_references`: Deduplicated list extracted from `rule_data["cfr_references"]` formatted as `f"{ref['title']} CFR Part {ref['part']}"` (`["42 CFR Part 409", "42 CFR Part 410", "42 CFR Part 414", "42 CFR Part 424", "42 CFR Part 484", "42 CFR Part 488", "42 CFR Part 489"]`) plus the policy-specific codified sections (`"42 CFR 410.36"`, `"42 CFR 414.1600"`, `"42 CFR 414.1650"`, `"42 CFR 414.1690"` for LTA Section 4133; `"42 CFR 410.10"`, `"42 CFR 414.1700"` for IVIG Section 4134).
  - `effective_date`: `rule_data["effective_on"]` (`"2024-01-01"`).
- **Fail-Fast Boundary:** Raise `RegulatoryRuleResolutionError` if no Final Rule matches the statutory authority, or if `document_number`, `citation`, or `cfr_references` are missing/empty.

### 2. Hop 4: CMS Transmittal / Change Request Discovery & Supersession Resolution (`discover_operational_directive`)
Implement deterministic Hop 4 discovery in [`src/graph/tier3_regulatory.py`](file:///Users/diesel/Desktop/LAG/.sandcastle/worktrees/agent-plan-20261013T225035-656-0beg/src/graph/tier3_regulatory.py):
- **Source Discovery:** Query the CMS Transmittals index (`https://www.cms.gov/medicare/regulations-guidance/transmittals/2023-transmittals` and `2024-transmittals` HTML table `views-field-field-dyna-cr-number`, `views-field-field-dyna-transmittal-number`, `views-field-title`, or structured local CMS transmittal metadata index) filtering by statutory section (`"Section 4133"`, `"Section 4134"`), policy scope (`"Lymphedema Compression Treatment Items"`, `"Intravenous Immune Globulin"`), or docket (`"CMS-1780-F"`).
- **Supersession & Operational Filter Resolution:**
  - For LTA (`Section 4133` / `"Lymphedema Compression Treatment Items"`):
    - `change_request_number`: `"13286"` (Implementation of New Benefit Category for Lymphedema Compression Treatment Items, Medicare Claims Processing Manual Pub. `100-04`)
    - `active_transmittal_number`: `"R12471CP"` (issued January 23, 2024, superseding initial transmittal `"R12379CP"` issued November 22, 2023)
    - `superseded_transmittal_numbers`: `["R12379CP"]`
    - `cms_manual_publication`: `"100-04"`
    - `benefit_category_code`: `"LC"`
    - `pricing_indicator_code`: `"40"`
    - `effective_date`: `"2024-01-01"`
  - For IVIG (`Section 4134` / `"Intravenous Immune Globulin"`):
    - `change_request_number`: `"13217"`
    - `active_transmittal_number`: `"R12437CP"` (superseding `"R12174CP"`)
    - `superseded_transmittal_numbers`: `["R12174CP"]`
    - `cms_manual_publication`: `"100-04"`
    - `benefit_category_code`: `"IVIG"`
    - `pricing_indicator_code`: `"57"`
    - `effective_date`: `"2024-01-01"`
- **Graph Node & Edge Emission:**
  - Emit `RegulationNode` (`id="REG-FR-2023-24455"`), `CFRSectionNode` records (`CFR-42-410-36`, `CFR-42-414-1600`, `CFR-42-414-1650`, `CFR-42-414-1690` for LTA; `CFR-42-410-10`, `CFR-42-414-1700` for IVIG), and `TransmittalNode` (`id="TR-CR13286"`, `transmittal_number="R12471CP"`, `superseded_transmittal_numbers=["R12379CP"]`, `benefit_category="LC"`, `pricing_indicator_code="40"` for LTA; `id="TR-CR13217"`, `transmittal_number="R12437CP"`, `superseded_transmittal_numbers=["R12174CP"]`, `benefit_category="IVIG"`, `pricing_indicator_code="57"` for IVIG).
  - Wire edges:
    - `(:USCSection)-[:AUTHORIZED_BY]->(:Regulation)`
    - `(:Regulation)-[:CODIFIED_IN]->(:CFRSection)`
    - `(:CFRSection)-[:IMPLEMENTED_BY]->(:Transmittal)`
- **Fail-Fast Boundary:** Raise `OperationalDirectiveMissingError` if no matching CR or active Transmittal ID is found, or if `benefit_category_code` or `pricing_indicator_code` is missing.

## Target Files & Line-Range Edits
- [`src/graph/tier3_regulatory.py`](file:///Users/diesel/Desktop/LAG/.sandcastle/worktrees/agent-plan-20261013T225035-656-0beg/src/graph/tier3_regulatory.py) (lines 1–146):
  - Split internal logic into Hop 3 (`discover_final_rule(engine, statutory_handoff, policy_keyword) -> RegulatoryHandoff`) and Hop 4 (`discover_operational_directive(engine, statutory_handoff, regulatory_handoff, policy_keyword) -> OperationalHandoff`).
  - Keep `ingest_regulatory_tier(engine, handoff, policy_keyword="LTA") -> Tier3Handoff` orchestrating both Hop 3 and Hop 4 and attaching `regulatory_handoff: RegulatoryHandoff` and `operational_handoff: OperationalHandoff` onto `Tier3Handoff`.
  - Update `TransmittalNode.transmittal_number` from inaccurate `"12349"` to `"R12471CP"` (with `superseded_transmittal_numbers=["R12379CP"]`).

## Verification Criteria
- Executing Hop 3 with `StatutoryHandoff` for Section 4133 yields `RegulatoryHandoff(fr_document_number="2023-24455", fr_citation="88 FR 77676", docket_id="CMS-1780-F", rin="0938-AV03", ...)`.
- Executing Hop 4 yields `OperationalHandoff(change_request_number="13286", active_transmittal_number="R12471CP", superseded_transmittal_numbers=["R12379CP"], cms_manual_publication="100-04", benefit_category_code="LC", pricing_indicator_code="40", effective_date="2024-01-01")`.
- Missing Federal Register rule raises `RegulatoryRuleResolutionError`; missing CMS Transmittal raises `OperationalDirectiveMissingError`.
