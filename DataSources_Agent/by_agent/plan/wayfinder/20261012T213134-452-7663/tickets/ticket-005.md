# Decision Ticket 005: Phase 5 Advocacy, Budget Estimates, and Peer-Reviewed Literature Context Integration Schema

**Ticket ID:** `ticket-005.md`  
**Run ID:** `20261012T213134-452-7663`  
**Status:** RESOLVED  
**Claimed By:** `wayfinder-read-and-plan`  
**Blocked By:** `ticket-001.md`, `ticket-003.md`

---

## 1. Architectural Question
What authoritative repositories provide registered lobbying disclosures, legislative budget estimates, and peer-reviewed literature indexing, and how must parallel queries be executed using `target_bill_ids` and `clinical_citations` to extract advocacy and evidentiary context?

---

## 2. Datasource Evaluation & Candidate Selection

### Evaluated Candidates
1. **Lobbying Disclosure Act (LDA) API (U.S. Senate SOPR / House Clerk):**
   - *Authority:* Official statutory lobbying disclosure database governed by 2 U.S.C. Chapter 26.
   - *Capabilities:* REST API indexing registered filers, clients, lobbying issues (e.g., `HCR`), reported expenditures, and specific referenced bills.
   - *Selection Status:* **SELECTED** as authoritative lobbying registry.
2. **Congressional Budget Office (CBO) Cost Estimates Repository:**
   - *Authority:* Official nonpartisan legislative scorekeeping agency for Congress.
   - *Capabilities:* Provides formal 10-year budget estimates, direct spending calculations, and hospital cost-offset models indexed by bill number.
   - *Selection Status:* **SELECTED** as authoritative economic score source.
3. **PubMed / Entrez E-utilities API (National Center for Biotechnology Information - NCBI):**
   - *Authority:* Official biomedical literature database governed by the National Library of Medicine (NLM).
   - *Capabilities:* High-fidelity programmatic retrieval of citation metadata, abstracts, and authors via PubMed IDs (PMIDs) or DOIs.
   - *Selection Status:* **SELECTED** as authoritative clinical literature API.

---

## 3. Endpoint Operational Parameters

### 3.1. Lobbying Disclosure Act (LDA) API
- **URL:** `https://lda.senate.gov/api/v1/filings/`
- **HTTP Method:** `GET`
- **Headers:**
  - `Accept: application/json`
  - `Authorization: Token [API_KEY]`
- **Query Parameters:**
  - `filing_year`: Target congressional years
  - `issue_code`: `HCR` (Health Issues)
  - `bill_id`: `HR3630` or `S1315`

### 3.2. CBO Cost Estimates Endpoint
- **URL:** Direct link via Congress.gov bill detail (`bill.cboCostEstimates[].url`) or `https://www.cbo.gov/publication/{id}`
- **Format:** JSON / HTML / PDF

### 3.3. PubMed E-utilities API (`esummary`)
- **URL:** `https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi`
- **HTTP Method:** `GET`
- **Query Parameters:**
  - `db`: `pubmed`
  - `id`: Comma-delimited PMIDs (from Phase 3 `clinical_citations`)
  - `retmode`: `json`
- **Rate Limits:** 3 requests/second without NCBI API key; 10 requests/second with registered key.
- **Expected Status Codes:** `200 OK`.

---

## 4. Payload Schema and Field Access Classification

### 4.1. PubMed E-utilities Sample Payload
```json
{
  "header": { "type": "esummary", "version": "0.3" },
  "result": {
    "uids": ["31454178"],
    "31454178": {
      "uid": "31454178",
      "title": "Clinical Efficacy of Gradient Compression Therapy in Secondary Lymphedema",
      "pubdate": "2019 Aug",
      "source": "Lymphatic Research and Biology",
      "authors": [
        { "name": "Bochner AF", "authtype": "Author" }
      ],
      "articleids": [
        { "idtype": "pubmed", "value": "31454178" },
        { "idtype": "doi", "value": "10.1002/lrb.2019" }
      ]
    }
  }
}
```

### 4.2. Field Access Classification
| Target Field | Source Endpoint | Access Classification | Exact Selector / Path | Target Type |
|---|---|---|---|---|
| Registrant Name | LDA API `/filings/` | Direct Path | `json.results[].registrant.name` | `string` |
| Client Name | LDA API `/filings/` | Direct Path | `json.results[].client.name` | `string` |
| Lobbying Expenses | LDA API `/filings/` | Direct Path | `json.results[].expenses` | `float` |
| CBO Estimated Cost | CBO / Congress.gov | Direct Path | `json.bill.cboCostEstimates[].description` | `string` |
| CBO Publication URL | CBO / Congress.gov | Direct Path | `json.bill.cboCostEstimates[].url` | `string` |
| PubMed Article Title | NCBI `esummary` | Direct Path | `json.result[uid].title` | `string` |
| Authors | NCBI `esummary` | Direct Path | `json.result[uid].authors[].name` | `array[string]` |
| Journal / Source | NCBI `esummary` | Direct Path | `json.result[uid].source` | `string` |
| Publication Date | NCBI `esummary` | Direct Path | `json.result[uid].pubdate` | `string` |

---

## 5. Terminal Output Schemas (Evidentiary Subgraph)

### 5.1. Advocacy Node Schema
```json
{
  "entity_type": "advocacy_filing",
  "linked_bill_id": "BILL-117-hr-3630",
  "registrant": "Lymphedema Advocacy Group",
  "client": "Lymphedema Advocacy Group",
  "issue_code": "HCR",
  "total_expenditures": 120000.00
}
```

### 5.2. Clinical Literature Node Schema
```json
{
  "entity_type": "clinical_evidence",
  "composite_id": "PMID-31454178",
  "pmid": "31454178",
  "doi": "10.1002/lrb.2019",
  "title": "Clinical Efficacy of Gradient Compression Therapy in Secondary Lymphedema",
  "journal": "Lymphatic Research and Biology",
  "publication_date": "2019 Aug",
  "linked_regulatory_rule": "CMS-1780-F"
}
```

---

## 6. Fail-Fast Error and Termination Rules
1. **Clinical Identifier Invalid:** If NCBI returns an invalid UID error for an extracted clinical citation, raise fatal exception `Phase5LiteratureNotFoundError("Invalid or missing PubMed UID: " + clinical_citation.id)` and halt.
2. **Empty Advocacy Response:** If no advocacy filings can be queried for verified target bill IDs, log an explicit warning or raise `Phase5AdvocacyFilingMissingError` if the specification mandates economic scores.
