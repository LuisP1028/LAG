# Functional Specification: Data Source Audit, Payload Feasibility, and Foreign-Key Handoff Contracts

**Document ID:** `functional_specification_001.md`  
**Status:** Requirements Specification (Pending User Authorization)  
**Implementation Guidance:** Prohibited (DO NOT CODE YET)

---

## 1. Objective and System Boundary

This specification defines the functional requirements for identifying all relevant data sources, reviewing their payloads, and assessing how to perform foreign-key handoffs across the extraction pipeline.

The pipeline takes a single string parameter—a policy keyword (such as `"LTA"`)—as its only runtime input. All downstream records (legislation, statutes, regulations, medical codes, fee schedules, lobbying filings, and clinical citations) must be discovered by chaining explicit foreign keys returned by authoritative APIs.

### Core Rules
* **Autonomous Source Discovery:** The specification defines required capabilities, endpoints, and extraction targets for each phase. Identifying and selecting the most relevant, authoritative datasource that satisfies these requirements is the responsibility of the executing agent during the audit. Pre-baked or hardcoded source assumptions are prohibited.
* **No Pre-Populated Lookups:** Hardcoded bill numbers, public law IDs, U.S. Code sections, procedure codes, or fee schedules are prohibited.
* **Deterministic Matching:** Exact-match lookups only. Fuzzy text matching, probabilistic ranking, and heuristic guesses are prohibited.
* **Fail-Fast Error Handling:** If any phase fails to extract its required downstream foreign key, execution halts immediately with an explicit error. Fallback defaults and silent exception suppression are prohibited.

---

## 2. Phase-by-Phase Functional Requirements and Datasource Capabilities

For each phase, the executing agent must evaluate and identify candidate datasources against the capability requirements, required query operations, and extraction targets specified below.

### 2.1. Phase 1: Legislative Bill Discovery
* **Input:** `keyword` (`string`).
* **Datasource Capability Requirements:**
  * Must be an authoritative repository providing comprehensive legislative tracking and action history across multiple historical congressional sessions.
  * Must support querying by keyword, subject term, or title.
  * Must provide structured action histories, companion/related bill relationships, and final enactment status.
* **Required Query Operations:**
  * Search measures matching the policy keyword across historical sessions.
  * Retrieve detailed action and status history for candidate bills to identify the enacted public law.
* **Extraction Targets:**
  * `target_bill_ids`: Array of composite bill identifiers (`congress: integer`, `type: string`, `number: integer`).
  * `enacted_law_id`: The public law identifier linked to the enacted bill (`congress: integer`, `law_number: integer`).
* **Failure Condition:** If the query yields no enacted public law, Phase 1 halts and Phase 2 does not execute.

### 2.2. Phase 2: Statutory Codification
* **Input:** `enacted_law_id` (from Phase 1).
* **Datasource Capability Requirements:**
  * Must provide official, complete statutory text and markup for enacted public laws.
  * Must support structured legislative markup (such as USLM XML or equivalent schema) that preserves hierarchy (titles, sections, subsections, and amendatory instructions).
* **Required Query Operations:**
  * Retrieve full statutory document markup by public law identifier.
  * Support structural document traversal to isolate the specific section that adds or amends permanent statutory code.
* **Extraction Targets:**
  * `us_code_citations`: Array of codified citations (`title: integer`, `section: string`, `subsections: string[]`, `citation_string: string`).
* **Failure Condition:** If the public law markup does not contain an explicit amendment or addition to the target statutory code, Phase 2 halts and Phase 3 does not execute.

### 2.3. Phase 3: Administrative Rules and Directives
* **Input:** `us_code_citations` (from Phase 2).
* **Datasource Capability Requirements:**
  * Must provide published executive agency rulemaking documents and administrative implementation transmittals/directives.
  * Must support querying regulatory records using statutory authority citations (e.g., U.S. Code sections).
  * Must provide access to rulemaking preambles (for evidentiary/clinical citations), regulatory text (for CFR parts), and administrative directives (for operational instructions).
* **Required Query Operations:**
  * Query published agency Final Rules referencing the statutory citation as legal authority.
  * Query administrative transmittals or change requests operationalizing the rule.
  * Extract bibliographic/evidentiary citations embedded in preambles or regulatory justifications.
* **Extraction Targets:**
  * Regulatory metadata: Rule identifier, affected regulatory code parts, and effective dates.
  * Operational directive identifiers: Administrative transmittal identifiers or change request numbers.
  * `operational_filters`: Administrative classifications (e.g., benefit categories, pricing indicator codes, billing modifiers).
  * `clinical_citations`: External scientific references cited in rulemaking preambles (e.g., PubMed IDs, DOIs).
* **Failure Condition:** If no published final rule or operational directive links back to the statutory citation, Phase 3 halts.

### 2.4. Phase 4: Medical Billing, Coverage, and Fee Schedules
* **Input:** `operational_filters` (from Phase 3).
* **Datasource Capability Requirements:**
  * Must provide standardized procedure coding master datasets, regional fee schedules, and coverage determination policies.
  * Must support filtering procedure codes strictly by operational categories and pricing indicators (without keyword search).
  * Must provide regional pricing breakdowns (payment ceilings/floors, coinsurance splits) and diagnostic eligibility criteria.
* **Required Query Operations:**
  * Retrieve procedure codes matching operational classification filters.
  * Retrieve allowable diagnostic indication codes linked to the authorized coverage policies.
  * Retrieve regional fee schedule allowances and replacement/utilization frequency caps.
* **Extraction Targets:**
  * Procedure codes: HCPCS/CPT codes matching the operational category from Phase 3.
  * Diagnostic criteria: Allowable ICD-10 diagnostic codes linked to the authorized coverage policies.
  * Utilization limits: Quantity and replacement frequency limits.
  * Regional pricing: Jurisdiction-level and state-level payment allowances, coverage shares, and patient coinsurance amounts.
* **Failure Condition:** If operational filters match zero active procedure codes or fee schedule entries, Phase 4 halts.

### 2.5. Phase 5: Advocacy and Evidentiary Context (Parallel Execution)
* **Inputs:**
  * `target_bill_ids` (from Phase 1).
  * `clinical_citations` (from Phase 3).
* **Datasource Capability Requirements:**
  * Must provide registered lobbying disclosure filings, legislative budget impact scores, and peer-reviewed medical literature indexes.
  * Must support querying by bill identifiers for advocacy filings and budget scores.
  * Must support querying by bibliographic/clinical identifiers for peer-reviewed studies.
* **Required Query Operations:**
  * Query lobbying disclosure records matching target bill identifiers.
  * Query formal legislative budget estimates matching target bill identifiers.
  * Query publication metadata matching clinical citations.
* **Extraction Targets:**
  * Lobbying records: Filings matching `target_bill_ids` (registrant, client, issue codes, reported expenditures).
  * Economic estimates: Cost/savings projections matching `target_bill_ids`.
  * Medical literature records: Publication metadata (title, authors, publication date, abstract) matching `clinical_citations`.

---

## 3. Payload Schema and Feasibility Audit Requirements

Before implementing extraction logic, every candidate datasource payload must be audited to determine field availability and extraction mechanics.

### 3.1. Field Access Classification
Every target field within a candidate payload must be audited and classified into one of two access modes:

1. **Direct Path (Native Keys):**
   * The field exists as an explicit key in a JSON object or an attribute/element in an XML node.
   * *Requirement:* Document the exact path (e.g., `json.data.item[].code` or `xml//item/@code`).

2. **Structural Traversal (Markup Elements):**
   * The field is embedded within free-form markup or narrative text (e.g., an amendment block inside an XML document or a clinical citation inside a regulatory preamble).
   * *Requirement:* Document the exact XPath, CSS selector, or node hierarchy required to isolate the element deterministically without using unanchored regex scanning across the full document.

### 3.2. Payload Integrity Verification
The audit must verify:
* **Identifier Sufficiency:** The payload must contain all fields needed to construct the downstream request parameter without external inferences.
* **Schema Consistency:** Document any variations in payload structure across different sessions, calendar years, or issuing sub-agencies.
* **Pagination and Completeness:** Identify whether endpoints paginate results (e.g., cursor tokens, page numbers) and verify that payload bodies contain full records rather than truncated summaries.

---

## 4. Foreign-Key Handoff Contracts

Data must pass between phases through explicit, structured handoff schemas.

| Step | Source Phase | Destination Phase | Parameter Name | Data Type | Structural Example |
|---|---|---|---|---|---|
| 0 → 1 | User Input | Phase 1 | `keyword` | `string` | `"LTA"` |
| 1 → 2 | Phase 1 | Phase 2 | `enacted_law_id` | `object` | `{ "congress": 117, "law_number": 328, "type": "public" }` |
| 1 → 5 | Phase 1 | Phase 5 | `target_bill_ids` | `array[object]` | `[{ "congress": 117, "type": "hr", "number": 3630 }]` |
| 2 → 3 | Phase 2 | Phase 3 | `us_code_citations` | `array[object]` | `[{ "title": 42, "section": "1395x", "subsection": "s(2)(JJ)" }]` |
| 3 → 4 | Phase 3 | Phase 4 | `operational_filters` | `object` | `{ "benefit_category": "<category_id>", "transmittal_id": "<directive_id>" }` |
| 3 → 5 | Phase 3 | Phase 5 | `clinical_citations` | `array[object]` | `[{ "type": "pmid", "id": "<literature_id>" }]` |

### Key Invariants
1. **Immutable Composite Identifiers:** All entities stored or passed between stages must use standardized composite string keys:
   * Bill: `BILL-[congress]-[type]-[number]`
   * Law: `PLAW-[congress]-[number]`
   * Statute: `USC-[title]-[section]-[subsection]`
   * Medical Code: `HCPCS-[code]`
2. **Traceable Lineage:** Every extracted pricing, billing, and evidentiary record must link back through its parent keys to the originating bill record.

---

## 5. Error and Termination Behavior

1. **Immediate Abort on Missing Dependency:**
   * If Phase 1 returns an empty `enacted_law_id`, execution stops. Phase 2 is not called.
   * If Phase 2 returns an empty `us_code_citations` list, execution stops. Phase 3 is not called.
   * If Phase 3 returns an empty `operational_filters` object, execution stops. Phase 4 is not called.
2. **Error Logging Format:**
   When an execution halts, the pipeline must log:
   * Phase number and phase name.
   * Input key received from upstream.
   * Target endpoint queried.
   * HTTP status code and raw response excerpt.
   * Expected field path that was missing or empty.

---

## 6. Audit Deliverables and Acceptance Criteria

The audit phase is complete when the following artifacts are produced:

1. **Datasource Identification Report:** Evaluation and selection of the most relevant, authoritative data sources and endpoints for each phase based on functional criteria.
2. **Sample Payload Repository:** Raw sample JSON and XML payloads saved for each selected endpoint representing each target data structure.
3. **Field Access Matrix:** A mapping table listing every required output field, its parent endpoint, its access classification (Direct Path vs. Structural Traversal), and its exact JSONPath/XPath selector.
4. **Handoff Verification:** Documented dry-run tracing showing that sample data passes through the foreign-key contract from Phase 1 through Phase 5 without manual intervention or fallbacks.
