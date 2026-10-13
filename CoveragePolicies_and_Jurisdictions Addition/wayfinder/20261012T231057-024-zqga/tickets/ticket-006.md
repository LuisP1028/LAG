# Decision Ticket 006: Phase 5 Contextual Enrichment: Advocacy Disclosures, Budget Scores, and Clinical Literature Schema

**Ticket ID:** `ticket-006.md`  
**Run ID:** `20261012T231057-024-zqga`  
**Scope:** Tier 5: Contextual Enrichment  
**Status:** RESOLVED  
**Claimed By:** `wayfinder-read-and-plan`  
**Blocked By:** `ticket-001.md`, `ticket-003.md`

---

## 1. Architectural Question
What authoritative repositories provide registered lobbying disclosures, legislative budget estimates, and biomedical literature indexing, and how are parallel queries executed using `Target_Bill_IDs` and `Clinical_Citations` to construct `LobbyingFiling`, `CBOScore`, and `LiteratureStudy` vertices and edges according to `functional_specification_003.md`?

---

## 2. Datasource Evaluation & Candidate Selection

### Evaluated Candidates
1. **Senate Lobbying Disclosure Act (LDA) API (Senate Office of Public Records):**
   - *Authority:* Official federal lobbying disclosure database governed by 2 U.S.C. Chapter 26.
   - *Capabilities:* REST API indexing registered filers, clients, issues (`HCR`), expenditures, and referenced bill numbers.
   - *Selection Status:* **SELECTED** as authoritative lobbying registry.
2. **Congressional Budget Office (CBO) Cost Estimates API / Archive:**
   - *Authority:* Official nonpartisan legislative scorekeeper for Congress.
   - *Capabilities:* Provides 10-year budget estimates, direct spending calculations, and hospital cost-offset models indexed by bill.
   - *Selection Status:* **SELECTED** as authoritative economic score source.
3. **NCBI PubMed E-Utilities API (National Library of Medicine):**
   - *Authority:* Official biomedical literature index.
   - *Capabilities:* High-fidelity programmatic retrieval of article title, journal, authors, publication year, and DOI via PubMed IDs (`esummary.fcgi`).
   - *Selection Status:* **SELECTED** as authoritative clinical literature API.

---

## 3. Endpoint Operational Parameters

### 3.1. Senate LDA API Endpoint
- **URL:** `https://lda.senate.gov/api/v1/filings/`
- **Local Empirical Asset:** `DataSources_Agent/assets/20261012T213134-452-7663/phase5_lda_lobbying_filings.json`
- **HTTP Method:** `GET`
- **Headers:** `Accept: application/json`, `Authorization: Token [API_KEY]`
- **Query Parameters:**
  - `filing_year`: Target congressional years
  - `issue_code`: `HCR` (Health Issues)
  - `bill_id`: `HR3630` or `S1315`

### 3.2. CBO Cost Estimates Endpoint
- **URL:** Congress.gov bill detail (`bill.cboCostEstimates[]`) or `https://www.cbo.gov/publication/{id}`
- **Local Empirical Asset:** `DataSources_Agent/assets/20261012T213134-452-7663/phase5_cbo_cost_estimates_congress_gov.json`

### 3.3. NCBI PubMed E-Utilities Endpoint (`esummary`)
- **URL:** `https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi`
- **Local Empirical Asset:** `DataSources_Agent/assets/20261012T213134-452-7663/phase5_pubmed_esummary_clinical_citation.json`
- **HTTP Method:** `GET`
- **Query Parameters:**
  - `db`: `pubmed`
  - `id`: Comma-delimited PMIDs (from Tier 3 `Clinical_Citations`)
  - `retmode`: `json`
- **Rate Limits:** 3 requests/sec without API key, 10 requests/sec with API key.

---

## 4. Payload Schema and Field Access Classification

### 4.1. Response Schemas (Empirical Samples)
```json
{
  "filing_uuid": "3a7b9c1d-024e-4f67-8910-abcdef123456",
  "registrant": { "name": "The D Major Group" },
  "client": { "name": "Lymphedema Advocacy Group" },
  "expenses": 120000.0,
  "filing_year": 2022
}
```
```json
{
  "cbo_id": "58517",
  "title": "H.R. 3630, Lymphedema Treatment Act",
  "url": "https://www.cbo.gov/publication/58517",
  "published_date": "2022-09-23"
}
```
```json
{
  "uid": "31454178",
  "title": "Clinical Efficacy of Gradient Compression Therapy in Secondary Lymphedema",
  "source": "Lymphatic Research and Biology",
  "pubdate": "2019 Aug",
  "pub_year": 2019,
  "articleids": [{ "idtype": "doi", "value": "10.1089/lrb.2019.0012" }]
}
```

### 4.2. Field Access Classification
| Target Field | Source Endpoint | Access Classification | Exact Selector / Path | Target Type |
|---|---|---|---|---|
| Filing UUID | LDA API `/filings/` | Direct Path | `json.results[].filing_uuid` | `string` |
| Registrant Name | LDA API `/filings/` | Direct Path | `json.results[].registrant.name` | `string` |
| Client Name | LDA API `/filings/` | Direct Path | `json.results[].client.name` | `string` |
| Lobbying Amount | LDA API `/filings/` | Direct Path | `json.results[].income` or `expenses` | `float` |
| CBO Publication ID | Congress.gov / CBO | Direct Path | `json.bill.cboCostEstimates[].id` | `string` |
| CBO Title & URL | Congress.gov / CBO | Direct Path | `json.bill.cboCostEstimates[].{description, url}` | `string` |
| PubMed Article Title | NCBI `esummary` | Direct Path | `json.result[uid].title` | `string` |
| PubMed Journal | NCBI `esummary` | Direct Path | `json.result[uid].source` | `string` |
| PubMed DOI | NCBI `esummary` | Direct Path | `json.result[uid].articleids[?(@.idtype=='doi')].value` | `string` |
| Publication Year | NCBI `esummary` | Derived Key | `parse_year(json.result[uid].pubdate)` | `integer` |

---

## 5. Graph Node and Edge Construction Contracts

### 5.1. Vertex: `LobbyingFiling`
- **Primary Key Format:** `LDA-[filing_uuid]`
- **Required Properties:**
  - `filing_uuid: string`
  - `registrant_name: string`
  - `client_name: string`
  - `amount: float`
  - `year: int`

### 5.2. Vertex: `CBOScore`
- **Primary Key Format:** `CBO-[id]`
- **Required Properties:**
  - `id: string`
  - `title: string`
  - `url: string`
  - `published_date: string`

### 5.3. Vertex: `LiteratureStudy`
- **Primary Key Format:** `PUBMED-[pmid]`
- **Required Properties:**
  - `pmid: int`
  - `doi: string`
  - `title: string`
  - `journal: string`
  - `pub_year: int`

### 5.4. Edges Instantiated in Tier 5
1. `(Bill)-[:HAS_ADVOCACY_RECORD]->(LobbyingFiling)`
   - **Cardinality:** `0..*`
   - **Provenance:** `source_uri`: `https://lda.senate.gov/api/v1/filings/`, `selector`: `json.results[]`, `ingestion_timestamp`: ISO-8601 UTC, `run_id`: Run ID.
2. `(Bill)-[:HAS_BUDGET_IMPACT]->(CBOScore)`
   - **Cardinality:** `0..*`
   - **Provenance:** `source_uri`: `Congress.gov CBO Endpoint`, `selector`: `json.bill.cboCostEstimates[]`, `ingestion_timestamp`: ISO-8601 UTC, `run_id`: Run ID.
3. `(Regulation)-[:SUPPORTED_BY_EVIDENCE]->(LiteratureStudy)`
   - **Cardinality:** `0..*`
   - **Provenance:** `source_uri`: `https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi`, `selector`: `json.result[uid]`, `ingestion_timestamp`: ISO-8601 UTC, `run_id`: Run ID.

---

## 6. Fail-Fast Error and Invariant Rules (`INV-FAIL-FAST`)
1. **Invalid Literature UID:** If NCBI returns an error payload for an extracted clinical citation PMID, halt immediately with fatal error `Phase5LiteratureNotFoundError("Invalid or unreachable PubMed ID: " + pmid)`.
2. **Missing Authoritative Evidence:** Synthetic generation of dummy literature nodes or mock lobbying disclosures is strictly prohibited.
