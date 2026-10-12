# Decision Ticket 006: Foreign-Key Pipeline Handoff Contracts, Immutable Composite Key Formats, and Lineage Tracking Architecture

**Ticket ID:** `ticket-006.md`  
**Run ID:** `20261012T213134-452-7663`  
**Status:** RESOLVED  
**Claimed By:** `wayfinder-read-and-plan`  
**Blocked By:** `ticket-001.md`, `ticket-002.md`, `ticket-003.md`, `ticket-004.md`, `ticket-005.md`

---

## 1. Architectural Question
How must foreign-key handoffs be structured, typed, and validated across phases, how are composite primary keys standardized to maintain complete lineage traceability back to originating legislative vehicles, and how must fail-fast termination rules log operational telemetry upon failure?

---

## 2. Immutable Composite Key Standards

All entities discovered or passed between pipeline stages must utilize normalized, deterministic composite keys:

| Entity Type | Composite Identifier Template | Concrete Example | Generation Phase |
|---|---|---|---|
| **Bill** | `BILL-[congress]-[type]-[number]` | `BILL-117-hr-3630` | Phase 1 |
| **Public Law** | `PLAW-[congress]-[number]` | `PLAW-117-328` | Phase 1 |
| **Statute** | `USC-[title]-[section]-[subsection]` | `USC-42-1395x-s(2)(JJ)` | Phase 2 |
| **Regulation** | `CFR-[title]-[part]-[section]` | `CFR-42-414-214` | Phase 3 |
| **Directive** | `CR-[transmittal_number]` | `CR-13286` | Phase 3 |
| **Medical Code** | `HCPCS-[code]` | `HCPCS-A6583` | Phase 4 |
| **Diagnosis** | `ICD10-[code]` | `ICD10-I97.2` | Phase 4 |
| **Clinical Paper** | `PMID-[id]` | `PMID-31454178` | Phase 3 / Phase 5 |

---

## 3. Inter-Phase Foreign-Key Handoff Matrix

| Step | Emitter | Consumer | Contract Parameter | Data Type | Validation Invariant |
|---|---|---|---|---|---|
| **0 → 1** | Runtime User | Phase 1 | `keyword` | `string` | Non-empty ASCII string (`len >= 2`) |
| **1 → 2** | Phase 1 | Phase 2 | `enacted_law_id` | `object` | Must contain integer `congress`, integer `law_number`, type `"public"` |
| **1 → 5** | Phase 1 | Phase 5 | `target_bill_ids` | `array[object]` | Minimum 1 valid composite bill ID |
| **2 → 3** | Phase 2 | Phase 3 | `us_code_citations` | `array[object]` | Minimum 1 valid statutory anchor with Title and Section |
| **3 → 4** | Phase 3 | Phase 4 | `operational_filters` | `object` | Must contain non-empty `pricing_indicator` or `benefit_category` |
| **3 → 5** | Phase 3 | Phase 5 | `clinical_citations` | `array[object]` | Valid bibliographic identifiers (PMID / DOI) |

---

## 4. End-to-End Lineage Tracing Graph

Every terminal billing entity (Phase 4) and evidentiary context node (Phase 5) must carry an unbroken provenance chain:

```
[User Input: keyword="LTA"]
         │
         ▼
[BILL-117-hr-3630 / BILL-117-hr-2617] ─────────────┐
         │                                          │
         ▼                                          │
[PLAW-117-328]                                      │
         │                                          │
         ▼                                          │
[USC-42-1395x-s(2)(JJ) & USC-42-1395m-z]           │
         │                                          │
         ▼                                          │
[CMS-1780-F / CR-13286] ──────────────────┐         │
         │                                │         │
         ▼                                ▼         ▼
[HCPCS-A6583]                     [PMID-31454178] [LDA Filings / CBO Cost]
  - Pricing: WY $148.20             - Clinical Evidence
  - Diagnosis: ICD10-I97.2
  - Cap: 3 / 6 months
```

---

## 5. Fail-Fast Enforcement and Telemetry Protocol

In strict compliance with workspace rules (`RULE[user_global]`), no silent fallbacks, synthetic defaults, or fuzzy matches are permitted.

### Telemetry Error Structure
When any pipeline phase encounters a missing key or broken contract, it must raise a fatal exception and output structured failure telemetry:

```json
{
  "status": "FATAL_ERROR",
  "phase_number": 3,
  "phase_name": "Administrative Rules and Directives",
  "upstream_input_key": {
    "parameter_name": "us_code_citations",
    "value": "USC-42-1395x-s(2)(JJ)"
  },
  "target_endpoint": "https://www.federalregister.gov/api/v1/documents.json?conditions[cfr][title]=42&conditions[term]=1395x(s)(2)(JJ)",
  "http_status_code": 200,
  "raw_response_excerpt": "{\"count\": 0, \"results\": []}",
  "missing_field_path": "json.results[0].document_number",
  "error_message": "Immediate abort: Statutory authority returned 0 administrative rules; cannot operationalize downstream."
}
```
