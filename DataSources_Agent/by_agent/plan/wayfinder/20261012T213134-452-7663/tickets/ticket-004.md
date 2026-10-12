# Decision Ticket 004: Phase 4 Medical Billing, Coverage Determination, and Regional Fee Schedule Schema Reconciliation

**Ticket ID:** `ticket-004.md`  
**Run ID:** `20261012T213134-452-7663`  
**Status:** RESOLVED  
**Claimed By:** `wayfinder-read-and-plan`  
**Blocked By:** `ticket-003.md`

---

## 1. Architectural Question
What authoritative datasets provide standardized procedure codes, coverage policies, and regional reimbursement fee schedules, how are procedure codes isolated strictly using `operational_filters` without keyword search, and how are diagnostic criteria and regional pricing reconciled into terminal billing entities?

---

## 2. Datasource Evaluation & Candidate Selection

### Evaluated Candidates
1. **CMS Alpha-Numeric HCPCS Master Release Files:**
   - *Authority:* Official annual/quarterly alphanumeric HCPCS dataset published by CMS.
   - *Capabilities:* Contains all level II healthcare procedure codes with native operational metadata fields (Pricing Indicator, BETOS category, coverage status).
   - *Selection Status:* **SELECTED** as primary master coding repository.
2. **CMS DMEPOS Fee Schedule (Durable Medical Equipment, Prosthetics, Orthotics, and Supplies):**
   - *Authority:* Official CMS state-by-state payment file.
   - *Capabilities:* Tabular dataset providing jurisdictional payment allowances, floors, ceilings, and rural/non-rural payment splits for all covered HCPCS items.
   - *Selection Status:* **SELECTED** as authoritative regional pricing source.
3. **CMS Medicare Coverage Database (MCD) & Joint DME MAC Policy Articles:**
   - *Authority:* Official CMS and DME MAC (Jurisdictions A, B, C, D) coverage determinations.
   - *Capabilities:* Joint Policy Articles (e.g., A59508 / A59512) providing explicit ICD-10 diagnostic indications, utilization/replacement limits, and Standard Written Order (SWO) criteria.
   - *Selection Status:* **SELECTED** for diagnostic criteria and utilization limits.

---

## 3. Endpoint and Dataset Operational Parameters

### 3.1. CMS Alpha-Numeric HCPCS Dataset
- **Format:** CSV / Tabular Fixed-Width text file (CMS Annual Release).
- **Filtering Logic:** Direct row evaluation where `Pricing_Indicator == operational_filters.pricing_indicator` (`40`) AND `BETOS == operational_filters.betos_code` (`O1L`). Zero text matching or keyword filtering permitted.

### 3.2. CMS DMEPOS Regional Fee Schedule File
- **Format:** Tabular text / CSV file (e.g., `DME24_A.txt`).
- **Join Key:** Exact match on `HCPCS` code and `State` (e.g., `WY` for Wyoming).

### 3.3. DME MAC Local Coverage Article (MCD)
- **URL:** `https://www.cms.gov/medicare-coverage-database/view/article.aspx?articleid=59508`
- **Format:** HTML / JSON Policy Article export.

---

## 4. Payload Schema and Field Access Classification

### 4.1. HCPCS & Fee Schedule Record Structure
```json
{
  "hcpcs_code": "A6583",
  "short_description": "Grad comp arm sleeve custom",
  "betos": "O1L",
  "pricing_indicator": "40",
  "fee_schedule": {
    "jurisdiction": "DME MAC Jurisdiction D",
    "state": "WY",
    "allowed_amount": 148.20,
    "medicare_share_80": 118.56,
    "coinsurance_share_20": 29.64
  },
  "coverage_criteria": {
    "policy_article": "A59508",
    "allowable_icd10": ["I89.0", "I97.2", "I97.89", "Q82.0"],
    "frequency_limit": "3 garments per affected limb every 6 months",
    "required_modifiers": ["RA"]
  }
}
```

### 4.2. Field Access Classification
| Target Field | Source Dataset | Access Classification | Exact Selector / Filter | Target Type |
|---|---|---|---|---|
| HCPCS Code | HCPCS Master File | Direct Path | `row['HCPCS'] WHERE row['PI'] == '40' AND row['BETOS'] == 'O1L'` | `string` (`"A6583"`) |
| Description | HCPCS Master File | Direct Path | `row['SHORT_DESC']` | `string` |
| State Fee Allowance | DMEPOS Fee Schedule | Direct Path | `row['FEE_CEILING'] WHERE row['HCPCS'] == code AND row['STATE'] == state` | `float` (`148.20`) |
| Coinsurance (20%) | Fee Schedule Calculation | Derived Key | `allowed_amount * 0.20` | `float` (`29.64`) |
| Qualifying ICD-10 | DME MAC Policy Article | Direct Path / Table | Article section "ICD-10 Codes that Support Medical Necessity" | `array[string]` |
| Replacement Frequency | DME MAC Policy Article | Structural Traversal | Article section "Utilization Guidelines" | `string` |

---

## 5. Downstream Integration Schema (Terminal Adjudication Subgraph)
- **Terminal Node Format:** `HCPCS-[code]` (e.g., `HCPCS-A6583`)
- **Resolved Attributes:**
```json
{
  "composite_id": "HCPCS-A6583",
  "code": "A6583",
  "category": "Daytime Custom Compression Arm Sleeve",
  "allowed_amount_wy": 148.20,
  "coinsurance_amount": 29.64,
  "coinsurance_percentage": 20,
  "medicare_coverage_percentage": 80,
  "replacement_cap": "3 garments per affected limb every 6 months",
  "qualifying_diagnoses": ["I89.0", "I97.2", "I97.89", "Q82.0"],
  "lineage": {
    "transmittal_id": "CR13286",
    "statutory_citation": "USC-42-1395x-s(2)(JJ)",
    "public_law_id": "PLAW-117-328",
    "bill_id": "BILL-117-hr-2617"
  }
}
```

---

## 6. Fail-Fast Error and Termination Rules
1. **Zero Procedure Codes Matched:** If evaluating `operational_filters` against the HCPCS dataset yields zero matching codes, raise fatal exception `Phase4ZeroCodesMatchedError("Operational filters matched zero active procedure codes")` and halt immediately.
2. **Missing Fee Schedule Entry:** If a matched procedure code lacks an active fee schedule entry for the target jurisdiction/state, raise fatal exception `Phase4FeeScheduleMissingError("No fee schedule rate located for code: " + code)` and halt.
