# Decision Ticket 003: Phase 3 Administrative Rules and Directives Registry Selection, Authority Querying, and Filter/Citation Schema

**Ticket ID:** `ticket-003.md`  
**Run ID:** `20261012T213134-452-7663`  
**Status:** RESOLVED  
**Claimed By:** `wayfinder-read-and-plan`  
**Blocked By:** `ticket-002.md`

---

## 1. Architectural Question
What authoritative executive branch rulemaking and administrative directive registries satisfy Phase 3 requirements, how must queries be executed using statutory authority citations (`us_code_citations`), and how are operational filters (`operational_filters`) and clinical citations (`clinical_citations`) extracted?

---

## 2. Datasource Evaluation & Candidate Selection

### Evaluated Candidates
1. **Federal Register API (National Archives and Records Administration - NARA):**
   - *Authority:* Official federal rulemaking publication register.
   - *Capabilities:* Supports querying documents by statutory authority, CFR title, agency, and full text; provides full preambular narratives, citations, RIN numbers, and regulatory text.
   - *Selection Status:* **SELECTED** as primary authoritative rulemaking API.
2. **Electronic Code of Federal Regulations (eCFR) API (NARA / GPO):**
   - *Authority:* Daily updated codified regulations repository.
   - *Capabilities:* Provides point-in-time codified CFR text for 42 CFR Part 410 and Part 414.
   - *Selection Status:* **SELECTED** for verifying codified regulatory text.
3. **CMS Transmittals & Change Requests Portal:**
   - *Authority:* Centers for Medicare & Medicaid Services (CMS) operational instructions.
   - *Capabilities:* Change requests (e.g., CR 13286) and transmittals (e.g., R12471CP) that operationalize rulemaking into claim system edits and classification codes.
   - *Selection Status:* **SELECTED** for operational directives and claim indicator mapping.

---

## 3. Endpoint Operational Parameters

### 3.1. Federal Register Query Endpoint
- **URL:** `https://www.federalregister.gov/api/v1/documents.json`
- **HTTP Method:** `GET`
- **Headers:** `Accept: application/json`
- **Query Parameters:**
  - `conditions[type][]`: `RULE` (Final Rules)
  - `conditions[agencies][]`: `centers-for-medicare-medicaid-services`
  - `conditions[cfr][title]`: `42`
  - `conditions[term]`: `1395m(z)` or `1395x(s)(2)(JJ)`
  - `order`: `newest`
- **Rate Limits:** No authentication required; public rate limits allow up to 1,000 requests per 10 minutes.
- **Expected Status Codes:** `200 OK`, `400 Bad Request`, `429 Too Many Requests`.

### 3.2. Federal Register Document Details & Full Text
- **URL:** `https://www.federalregister.gov/api/v1/documents/{document_number}.json`
- **HTML / Body URL:** `https://www.federalregister.gov/documents/full_text/html/{doc_num}.html`
- **HTTP Method:** `GET`

---

## 4. Payload Schema and Extraction Mechanics

### 4.1. Federal Register Document Payload Schema
```json
{
  "count": 1,
  "results": [
    {
      "title": "Medicare Program; Calendar Year (CY) 2024 Home Health Prospective Payment System (HH PPS) Rate Update...",
      "document_number": "2023-24457",
      "citation": "88 FR 77676",
      "regulation_id_number": "0938-AV03",
      "action": "Final rule.",
      "effective_on": "2024-01-01",
      "cfr_references": [
        { "title": 42, "part": 410 },
        { "title": 42, "part": 414 }
      ],
      "body_html_url": "https://www.federalregister.gov/documents/full_text/html/2023/11/09/2023-24457.html"
    }
  ]
}
```

### 4.2. Field Access Classification
| Target Field | Source Endpoint / Document | Access Classification | Exact Selector / Path | Target Type |
|---|---|---|---|---|
| Rule Identifier | `/api/v1/documents.json` | Direct Path | `json.results[0].document_number` | `string` (`"2023-24457"`) |
| Rule Citation | `/api/v1/documents.json` | Direct Path | `json.results[0].citation` | `string` (`"88 FR 77676"`) |
| RIN | `/api/v1/documents.json` | Direct Path | `json.results[0].regulation_id_number` | `string` (`"0938-AV03"`) |
| Effective Date | `/api/v1/documents.json` | Direct Path | `json.results[0].effective_on` | `string` (`"2024-01-01"`) |
| CFR Parts | `/api/v1/documents.json` | Direct Path | `json.results[0].cfr_references[].part` | `array[integer]` (`[410, 414]`) |
| Transmittal ID | Final Rule text / CR registry | Structural Traversal | Rule body section on implementation directives | `string` (`"CR 13286"`) |
| Operational Categories | CMS CR 13286 transmittal | Direct Path / Table | System classification tables | `object` (Category 60, PI 40) |
| Clinical Citations (PMIDs) | Preamble text / footnotes | Structural Traversal | `//div[@class='preamble']//a[contains(@href, 'pubmed')]` or footnote anchors | `array[object]` |

---

## 5. Downstream Handoff Contracts

### 5.1. Contract 3 → 4: `operational_filters`
- **Recipient:** Phase 4 (Medical Billing, Coverage, and Fee Schedules)
- **Data Type:** `object`
- **Payload Schema:**
```json
{
  "benefit_category": "Category 60",
  "pricing_indicator": "40",
  "type_of_service": "S",
  "transmittal_id": "CR13286",
  "betos_code": "O1L",
  "billing_modifiers": ["RA", "RB"],
  "effective_date": "2024-01-01"
}
```

### 5.2. Contract 3 → 5: `clinical_citations`
- **Recipient:** Phase 5 (Advocacy and Evidentiary Context)
- **Data Type:** `array[object]`
- **Composite Key:** `PMID-[id]` or `DOI-[id]`
- **Payload Schema:**
```json
[
  {
    "type": "pmid",
    "id": "31454178",
    "composite_id": "PMID-31454178",
    "context": "Efficacy of gradient compression in maintaining limb volume and preventing secondary infection"
  }
]
```

---

## 6. Fail-Fast Error and Termination Rules
1. **Rule Query Failure:** If querying the Federal Register API using the statutory citation yields zero final rules, raise fatal exception `Phase3RuleNotFoundError("No Final Rule found referencing statutory authority: " + us_code_citation)` and halt.
2. **Missing Operational Filters:** If no administrative directive or change request linking to operational classifications is resolved, raise fatal exception `Phase3DirectiveMissingError("No operational filters or directives identified")` and halt immediately. Phase 4 must not be invoked.
