# Decision Ticket 004: Phase 4A Coverage Policy Ingestion, Medical Coding, and Diagnostic Indication Constraints Schema

**Ticket ID:** `ticket-004.md`  
**Run ID:** `20261012T231057-024-zqga`  
**Scope:** Tier 4A: Coverage Policy & Coding  
**Status:** RESOLVED  
**Claimed By:** `wayfinder-read-and-plan`  
**Blocked By:** `ticket-003.md`

---

## 1. Architectural Question
What authoritative repository provides structured Medicare Coverage Database (MCD) policy articles, how must the article tables be ingested to extract billable procedure codes (`HCPCSCode`) and allowable diagnosis codes (`ICD10Code`), and how must the graph topology enforce the policy bridge (`[:GOVERNS]`, `[:ALLOWS_DIAGNOSIS]`) while strictly prohibiting direct edges between `HCPCSCode` and `ICD10Code` according to `functional_specification_003.md`?

---

## 2. Datasource Evaluation & Candidate Selection

### Evaluated Candidates
1. **CMS Medicare Coverage Database (MCD) Policy Articles:**
   - *Authority:* Official CMS database for Local Coverage Determinations (LCDs), National Coverage Determinations (NCDs), and DME MAC Joint Policy Articles.
   - *Target Document:* Article `A59508` (*Standard Documentation Requirements for Lymphedema Compression Treatment Items*, Joint DME MAC Jurisdictions A, B, C, D).
   - *Capabilities:* Contains official structured tables of covered HCPCS procedure codes, allowable ICD-10-CM diagnostic codes, and equipment classification rules.
   - *Selection Status:* **SELECTED** as the primary authoritative coverage and diagnostic restriction source.
2. **NLM Free-Text Search APIs:**
   - *Deficiencies:* Performs heuristic text matching; explicitly prohibited by `INV-NO-KEYWORD-BRIDGING`.
   - *Selection Status:* REJECTED.

---

## 3. Endpoint and Payload Operational Parameters

### 3.1. CMS MCD Policy Article Endpoint
- **URL:** `https://www.cms.gov/medicare-coverage-database/view/article.aspx?articleid=59508`
- **Format:** HTML / Structured JSON article export.
- **Article ID:** `A59508`
- **Governing Contractors:** DME MAC Jurisdictions A, B, C, D (Noridian Healthcare Solutions & CGS Administrators).
- **Revision Effective Date:** `2024-01-01`
- **Policy Type:** `Article - Joint DME MAC Policy Article`

---

## 4. Payload Schema and Extraction Mechanics

### 4.1. Structured Coding Tables in Article A59508
- **Covered HCPCS Codes Table:**
  - Range: `A6520` through `A6549`, `A6552` through `A6567`, and `S8430`.
  - Properties extracted per code:
    - Code string (e.g., `"A6583"`)
    - Short description (e.g., `"Gradient compression arm sleeve, custom"`)
    - Classification category (e.g., `"Daytime Compression Garment"`)
- **Covered ICD-10-CM Diagnosis Codes Table:**
  - Standard codes: `I89.0` (Lymphedema, not elsewhere classified), `I97.2` (Postmastectomy lymphedema syndrome), `Q82.0` (Hereditary lymphedema).
  - Properties extracted per code:
    - Code string (e.g., `"I97.2"`)
    - Official description (e.g., `"Postmastectomy lymphedema syndrome"`)

### 4.2. Field Access Classification
| Target Field | Source Table / Section | Access Classification | Exact Selector / Expression | Target Type |
|---|---|---|---|---|
| Article Identifier | Article Header | Direct Path | `article.id` -> `"A59508"` | `string` |
| Article Title | Article Header | Direct Path | `article.title` | `string` |
| Covered HCPCS Code | Table: Covered HCPCS | Direct Path | `table[@id='hcpcs_codes']//row/cell[1]` | `string` (`"A6583"`) |
| HCPCS Description | Table: Covered HCPCS | Direct Path | `table[@id='hcpcs_codes']//row/cell[2]` | `string` |
| Covered ICD-10 Code | Table: Covered ICD-10 | Direct Path | `table[@id='icd10_codes']//row/cell[1]` | `string` (`"I97.2"`) |
| ICD-10 Description | Table: Covered ICD-10 | Direct Path | `table[@id='icd10_codes']//row/cell[2]` | `string` |

---

## 5. Graph Node and Edge Construction Contracts

### 5.1. Vertex: `CoveragePolicy`
- **Primary Key Format:** `CMS-MCD-[article_id]` (e.g., `CMS-MCD-A59508`)
- **Required Properties:**
  - `article_id: string` (`"A59508"`)
  - `title: string` (`"Standard Documentation Requirements for Lymphedema Compression Treatment Items"`)
  - `effective_date: string` (`"2024-01-01"`)
  - `policy_type: string` (`"Joint DME MAC Policy Article"`)

### 5.2. Vertex: `HCPCSCode`
- **Primary Key Format:** `HCPCS-[code]` (e.g., `HCPCS-A6583`)
- **Required Properties:**
  - `code: string` (`"A6583"`)
  - `short_description: string` (`"Grad comp arm sleeve custom"`)
  - `category: string` (`"Daytime Compression Garments"`)

### 5.3. Vertex: `ICD10Code`
- **Primary Key Format:** `ICD10-[code]` (e.g., `ICD10-I97.2`)
- **Required Properties:**
  - `code: string` (`"I97.2"`)
  - `description: string` (`"Postmastectomy lymphedema syndrome"`)

### 5.4. Edges Instantiated in Tier 4A
1. `(ChangeRequest)-[:MANDATES_POLICY]->(CoveragePolicy)`
   - **Cardinality:** `1..*`
   - **Semantics:** Connects operational transmittal directive to authoritative coverage policy article.
   - **Edge Provenance:**
     - `source_uri`: `https://www.cms.gov/medicare/regulations-guidance/transmittals/cr13286`
     - `selector`: `directive.policy_article_references`
     - `ingestion_timestamp`: ISO-8601 UTC timestamp
     - `run_id`: Run ID
2. `(CoveragePolicy)-[:GOVERNS]->(HCPCSCode)`
   - **Cardinality:** `1..*`
   - **Semantics:** Defines the billable procedure codes covered under the policy article.
   - **Edge Provenance:**
     - `source_uri`: `https://www.cms.gov/medicare-coverage-database/view/article.aspx?articleid=59508`
     - `selector`: `table#covered_hcpcs_codes`
     - `ingestion_timestamp`: ISO-8601 UTC timestamp
     - `run_id`: Run ID
3. `(CoveragePolicy)-[:ALLOWS_DIAGNOSIS]->(ICD10Code)`
   - **Cardinality:** `1..*`
   - **Semantics:** Defines the eligible diagnosis codes that support medical necessity under the policy.
   - **Edge Provenance:**
     - `source_uri`: `https://www.cms.gov/medicare-coverage-database/view/article.aspx?articleid=59508`
     - `selector`: `table#covered_icd10_codes`
     - `ingestion_timestamp`: ISO-8601 UTC timestamp
     - `run_id`: Run ID

### 5.5. Structural Invariant: Direct Edge Prohibition
- **PROHIBITION:** In strict accordance with Section 3.4 and Section 6 of `functional_specification_003.md`, no direct edge may connect `HCPCSCode` to `ICD10Code` (e.g., `(HCPCSCode)-[:REQUIRES_DIAGNOSIS]->(ICD10Code)` is prohibited).
- **Architectural Rationale:** Medical necessity in Medicare is governed at the policy article level, not via direct unmediated code-to-code edges.

---

## 6. Fail-Fast Error and Invariant Rules (`INV-FAIL-FAST`, `INV-NO-KEYWORD-BRIDGING`)
1. **Article Payload Fetch Failure:** If the article payload for `CMS-MCD-A59508` cannot be loaded, halt immediately with fatal error `Phase4ArticleFetchError("Failed to fetch coverage policy article: A59508")`.
2. **Missing Coding Tables:** If the article payload lacks structured covered HCPCS or ICD-10 tables, halt immediately with fatal error `Phase4CodingTableMissingError("Coverage article A59508 does not contain structured coding tables")`.
3. **Keyword Bridging Prohibition (`INV-NO-KEYWORD-BRIDGING`):** Free-text search to guess diagnosis codes (e.g., querying NLM with `"terms=lymphedema"`) is strictly prohibited. Only codes present in the structured policy table are valid.
