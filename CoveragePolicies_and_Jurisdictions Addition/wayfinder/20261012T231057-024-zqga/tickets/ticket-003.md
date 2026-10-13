# Decision Ticket 003: Phase 3 Administrative Rulemaking, Regulatory Execution, and Directive Extraction Schema

**Ticket ID:** `ticket-003.md`  
**Run ID:** `20261012T231057-024-zqga`  
**Scope:** Tier 3: Administrative Directives  
**Status:** RESOLVED  
**Claimed By:** `wayfinder-read-and-plan`  
**Blocked By:** `ticket-002.md`

---

## 1. Architectural Question
What authoritative executive branch rulemaking registries and administrative directive portals satisfy Tier 3 requirements, how must queries be executed using statutory authority citations (`US_Code_Citations`), and how are the `Regulation` node, `ChangeRequest` node, operational filters (`Operational_Filters`), coverage policy pointer (`Coverage_Policy_ID`), and clinical literature citations (`Clinical_Citations`) constructed according to `functional_specification_003.md`?

---

## 2. Datasource Evaluation & Candidate Selection

### Evaluated Candidates
1. **Federal Register REST API v1 (National Archives and Records Administration - NARA):**
   - *Authority:* Official federal rulemaking publication register.
   - *Capabilities:* Querying documents by statutory authority term, CFR title/part, agency (CMS), and publication type (`RULE`); provides preambles, citations, RIN numbers, and full text HTML.
   - *Selection Status:* **SELECTED** as primary authoritative rulemaking API.
2. **Electronic Code of Federal Regulations (eCFR) API:**
   - *Authority:* Official daily updated repository of codified federal regulations.
   - *Capabilities:* Point-in-time regulatory text for Title 42 CFR § 410.36.
   - *Selection Status:* Auxiliary validation source for CFR references.
3. **CMS Transmittals & Change Requests Portal:**
   - *Authority:* Centers for Medicare & Medicaid Services operational directives.
   - *Capabilities:* Ingesting operational transmittals (CR 13286, Transmittal 12349) that establish benefit category (`"LC"`), billing requirements, and policy article cross-references.
   - *Selection Status:* **SELECTED** as authoritative operational directive source.

---

## 3. Endpoint Operational Parameters

### 3.1. Federal Register Query Endpoint
- **URL:** `https://www.federalregister.gov/api/v1/documents.json`
- **Local Empirical Asset:** `DataSources_Agent/assets/20261012T213134-452-7663/phase3_federal_register_cms_final_rule_metadata.json`
- **HTTP Method:** `GET`
- **Headers:** `Accept: application/json`
- **Query Parameters:**
  - `conditions[type][]`: `RULE` (Final Rules)
  - `conditions[agencies][]`: `centers-for-medicare-medicaid-services`
  - `conditions[cfr][title]`: `42`
  - `conditions[term]`: `1395x(s)(2)(JJ)` (or statutory section anchor)
  - `order`: `newest`
- **Rate Limits:** Public API allows up to 1,000 requests per 10 minutes without authentication.
- **Expected Status Codes:** `200 OK`, `429 Too Many Requests`.

### 3.2. Federal Register Document Details
- **URL:** `https://www.federalregister.gov/api/v1/documents/{document_number}.json`
- **Full Text HTML URL:** `https://www.federalregister.gov/documents/full_text/html/{doc_num}.html`

---

## 4. Payload Schema and Extraction Mechanics

### 4.1. Federal Register Response Schema (Empirical Sample: Doc 2023-24455 / 2023-24407)
```json
{
  "count": 1,
  "results": [
    {
      "document_number": "2023-24455",
      "citation": "88 FR 77676",
      "title": "Medicare Program; Calendar Year (CY) 2024 Home Health Prospective Payment System Rate Update...",
      "action": "Final rule.",
      "effective_on": "2024-01-01",
      "cfr_references": [
        { "title": 42, "part": 410 },
        { "title": 42, "part": 414 }
      ],
      "body_html_url": "https://www.federalregister.gov/documents/full_text/html/2023/11/13/2023-24455.html"
    }
  ]
}
```

### 4.2. Field Access Classification
| Target Field | Source Endpoint / Text | Access Classification | Exact Selector / Path | Target Type |
|---|---|---|---|---|
| Document Number | `/api/v1/documents.json` | Direct Path | `json.results[0].document_number` | `string` (`"2023-24455"`) |
| Citation | `/api/v1/documents.json` | Direct Path | `json.results[0].citation` | `string` (`"88 FR 77676"`) |
| Effective Date | `/api/v1/documents.json` | Direct Path | `json.results[0].effective_on` | `string` (`"2024-01-01"`) |
| CFR Parts | `/api/v1/documents.json` | Direct Path | `json.results[0].cfr_references[].part` | `string[]` (`["42 CFR 410.36", "42 CFR 414.214"]`) |
| Change Request ID | Rule Preamble / Directives | Structural Traversal | Text match `CR 13286` / Transmittal `12349` | `string` (`"13286"`) |
| Transmittal Number | Rule Preamble / Directives | Structural Traversal | Text match Transmittal `12349` | `string` (`"12349"`) |
| Benefit Category | Directive payload / Preamble | Structural Traversal | Category code `"LC"` (Lymphedema Compression) | `string` (`"LC"`) |
| Coverage Policy ID | Directive payload / Footnotes | Structural Traversal | Reference to MCD Article `"A59508"` | `string` (`"CMS-MCD-A59508"`) |
| PubMed IDs (PMIDs) | Rule Preamble Footnotes | Structural Traversal | Footnote links containing `pubmed/` or PMID numbers | `integer[]` (`[31454178]`) |

---

## 5. Graph Node and Edge Construction Contracts

### 5.1. Vertex: `Regulation`
- **Primary Key Format:** `FR-[document_number]` (e.g., `FR-2023-24455`)
- **Required Properties:**
  - `citation: string` (`"88 FR 77676"`)
  - `document_number: string` (`"2023-24455"`)
  - `effective_date: string` (`"2024-01-01"`)
  - `cfr_parts: string[]` (`["42 CFR 410.36", "42 CFR 414.214"]`)

### 5.2. Vertex: `ChangeRequest`
- **Primary Key Format:** `CMS-CR-[cr_number]` (e.g., `CMS-CR-13286`)
- **Required Properties:**
  - `cr_number: string` (`"13286"`)
  - `transmittal_number: string` (`"12349"`)
  - `benefit_category: string` (`"LC"`)
  - `effective_date: string` (`"2024-01-01"`)

### 5.3. Edges Instantiated in Tier 3
1. `(StatutorySection)-[:IMPLEMENTED_BY]->(Regulation)`
   - **Cardinality:** `1..*`
   - **Semantics:** Maps statutory authority to agency final rule.
   - **Edge Provenance:**
     - `source_uri`: `https://www.federalregister.gov/api/v1/documents.json?conditions[term]=1395x(s)(2)(JJ)`
     - `selector`: `json.results[0]`
     - `ingestion_timestamp`: ISO-8601 UTC timestamp
     - `run_id`: Run ID
2. `(Regulation)-[:ISSUES_TRANSMITTAL]->(ChangeRequest)`
   - **Cardinality:** `1..*`
   - **Semantics:** Connects final rule to operational transmittal/change request directive.
   - **Edge Provenance:**
     - `source_uri`: `https://www.cms.gov/medicare/regulations-guidance/transmittals`
     - `selector`: `preamble.implementation_directives.cr13286`
     - `ingestion_timestamp`: ISO-8601 UTC timestamp
     - `run_id`: Run ID

---

## 6. Downstream Foreign Key Handoff Contracts

### 6.1. Handoff Contract 3 → 4A: `Coverage_Policy_ID`
- **Recipient:** Tier 4A: Coverage Policy Integration & Diagnostic Constraints
- **Data Type:** `string`
- **Composite Format:** `CMS-MCD-[article_id]` (e.g., `CMS-MCD-A59508`)

### 6.2. Handoff Contract 3 → 4B: `Operational_Filters`
- **Recipient:** Tier 4B: Geographic Fee Schedule Normalization
- **Data Type:** `object`
- **Payload Schema:**
```json
{
  "benefit_category": "LC",
  "transmittal_id": "12349",
  "cr_number": "13286"
}
```

### 6.3. Handoff Contract 3 → 5: `Clinical_Citations`
- **Recipient:** Tier 5: Contextual Enrichment
- **Data Type:** `array[int]`
- **Payload Schema:** `[31454178]`

---

## 7. Fail-Fast Error and Invariant Rules (`INV-FAIL-FAST`)
1. **Missing Final Rule:** If querying the Federal Register API using `US_Code_Citations` yields zero matching Final Rules, halt immediately with fatal error `Phase3RuleNotFoundError("No Final Rule found referencing statutory authority: " + us_code_citation)`.
2. **Missing Change Request / Policy Article Reference:** If the regulatory payload fails to yield Change Request `CR 13286` or MCD Policy Article pointer `A59508`, halt immediately with fatal error `Phase3DirectiveMissingError("Missing required operational directive or MCD article reference")`.
3. **No Synthetic Fallbacks:** Speculative insertion of artificial change requests or unreferenced policy articles is strictly forbidden.
