# Decision Ticket 001: Phase 1 Legislative Genesis, Bill Resolution, and Root Policy Ingestion Schema

**Ticket ID:** `ticket-001.md`  
**Run ID:** `20261012T231057-024-zqga`  
**Scope:** Tier 1: Legislative Origins  
**Status:** RESOLVED  
**Claimed By:** `wayfinder-read-and-plan`  
**Blocked By:** None (Root Discovery Node)

---

## 1. Architectural Question
What authoritative legislative data source satisfies Tier 1 capability requirements, what are the exact endpoint operational parameters, and how must the query operations instantiate the root `Policy` node, extract composite bill identifiers (`Target_Bill_IDs`), isolate the enacted public law identifier (`Enacted_Law_ID`), and construct property graph vertices and edges according to `functional_specification_003.md`?

---

## 2. Datasource Evaluation & Candidate Selection

### Evaluated Candidates
1. **Congress.gov REST API v3 (Library of Congress):**
   - *Authority:* Official API maintained by the Library of Congress in partnership with the Senate, House, GPO, and CRS.
   - *Capabilities:* Supports cross-session measure searching by keyword/title, historical action tracking, companion/related bill linking (`/relatedbills`), and direct metadata crosswalk to public laws via `bill.laws`.
   - *Selection Status:* **SELECTED** as the primary authoritative API for Tier 1.
2. **ProPublica Congress API (Archived / Deprecated):**
   - *Deficiencies:* Third-party intermediary; static snapshots; subject to maintenance lapses.
   - *Selection Status:* REJECTED.
3. **GovInfo API (BILLS collection):**
   - *Capabilities:* Provides raw publication text and bill packages, but lacks cross-session action lineage graphs and related bill network indexing.
   - *Selection Status:* Secondary for Tier 2; auxiliary for Tier 1.

---

## 3. Endpoint Operational Parameters

### 3.1. Bill Search Endpoint
- **URL:** `https://api.congress.gov/v3/bill`
- **HTTP Method:** `GET`
- **Headers:**
  - `Accept: application/json`
  - `X-API-KEY: [API_KEY]` (or query parameter `api_key=[API_KEY]`)
- **Query Parameters:**
  - `q`: Policy keyword (e.g., `LTA` or `Lymphedema Treatment Act`)
  - `limit`: `250` (maximum pagination batch size)
  - `offset`: `0`
  - `sort`: `updateDate+desc`
  - `format`: `json`
- **Rate Limits:** 1,000 requests per hour for registered keys (30 requests/hour for DEMO_KEY).
- **Expected Status Codes:** `200 OK`, `403 Forbidden` (invalid key / rate limit), `404 Not Found`.

### 3.2. Bill Detail & Action Lineage Endpoints
- **URL:** `https://api.congress.gov/v3/bill/{congress}/{billType}/{billNum}`
- **Actions URL:** `https://api.congress.gov/v3/bill/{congress}/{billType}/{billNum}/actions`
- **Related Bills URL:** `https://api.congress.gov/v3/bill/{congress}/{billType}/{billNum}/relatedbills`
- **HTTP Method:** `GET`
- **Headers / Auth:** Same as Bill Search.

---

## 4. Payload Schema and Field Access Classification

### 4.1. Response Payload Schema (`/v3/bill/{congress}/{billType}/{billNum}`)
```json
{
  "bill": {
    "congress": 117,
    "type": "HR",
    "number": "2617",
    "title": "Consolidated Appropriations Act, 2023",
    "originChamber": "House",
    "introducedDate": "2021-04-16",
    "laws": [
      {
        "number": "117-328",
        "type": "Public Law"
      }
    ],
    "actions": {
      "count": 48,
      "url": "https://api.congress.gov/v3/bill/117/hr/2617/actions?format=json"
    },
    "relatedBills": {
      "count": 52,
      "url": "https://api.congress.gov/v3/bill/117/hr/2617/relatedbills?format=json"
    }
  }
}
```

### 4.2. Field Access Classification
| Target Field | Source Endpoint | Access Classification | Exact Selector / Path | Target Type |
|---|---|---|---|---|
| `bill.congress` | `/v3/bill` or `/v3/bill/{c}/{t}/{n}` | Direct Path | `json.bills[].congress` | `integer` |
| `bill.type` | `/v3/bill` or `/v3/bill/{c}/{t}/{n}` | Direct Path | `json.bills[].type` | `string` (lowercase) |
| `bill.number` | `/v3/bill` or `/v3/bill/{c}/{t}/{n}` | Direct Path | `json.bills[].number` | `integer` |
| `bill.title` | `/v3/bill/{c}/{t}/{n}` | Direct Path | `json.bill.title` | `string` |
| `bill.introducedDate` | `/v3/bill/{c}/{t}/{n}` | Direct Path | `json.bill.introducedDate` | `string` (YYYY-MM-DD) |
| `law.number` | `/v3/bill/{c}/{t}/{n}` | Direct Path | `json.bill.laws[?(@.type=='Public Law')].number` | `string` (`"117-328"`) |
| `law.type` | `/v3/bill/{c}/{t}/{n}` | Direct Path | `json.bill.laws[0].type` | `string` (`"Public Law"`) |
| `related_bill` | `/v3/bill/{c}/{t}/{n}/relatedbills` | Direct Path | `json.relatedBills[].{congress, type, number}` | `array[object]` |

---

## 5. Graph Node and Edge Construction Contracts

### 5.1. Vertex: `Policy` (Root Node)
- **Primary Key:** `POLICY-[keyword]` (e.g., `POLICY-LTA`)
- **Required Properties:**
  - `keyword: string` (e.g., `"LTA"`)
  - `run_id: string` (Execution run identifier, e.g., `"20261012T231057-024-zqga"`)
  - `timestamp: string` (ISO-8601 UTC timestamp of execution)

### 5.2. Vertex: `Bill`
- **Primary Key:** `BILL-[congress]-[type]-[number]` (e.g., `BILL-117-hr-3630`, `BILL-117-hr-2617`)
- **Required Properties:**
  - `congress: int` (e.g., `117`)
  - `type: string` (e.g., `"hr"`)
  - `number: int` (e.g., `3630`)
  - `title: string` (e.g., `"Lymphedema Treatment Act"`)
  - `introduced_date: string` (e.g., `"2021-05-28"`)

### 5.3. Vertex: `PublicLaw`
- **Primary Key:** `PLAW-[congress]-[number]` (e.g., `PLAW-117-328`)
- **Required Properties:**
  - `congress: int` (e.g., `117`)
  - `number: int` (e.g., `328`)
  - `title: string` (e.g., `"Consolidated Appropriations Act, 2023"`)
  - `enacted_date: string` (e.g., `"2022-12-29"`)

### 5.4. Edges Instantiated in Tier 1
1. `(Policy)-[:TARGETS_BILL]->(Bill)`
   - **Cardinality:** `1..*`
   - **Semantics:** Links runtime search parameter to discovered advocacy and omnibus bills.
   - **Edge Provenance:**
     - `source_uri`: `https://api.congress.gov/v3/bill?q={keyword}`
     - `selector`: `json.bills[]`
     - `ingestion_timestamp`: ISO-8601 UTC timestamp
     - `run_id`: Run ID
2. `(Bill)-[:ENACTED_AS]->(PublicLaw)`
   - **Cardinality:** `1..1`
   - **Semantics:** Connects passed enacting vehicle to public law statute.
   - **Edge Provenance:**
     - `source_uri`: `https://api.congress.gov/v3/bill/{c}/{t}/{n}`
     - `selector`: `json.bill.laws[?(@.type=='Public Law')]`
     - `ingestion_timestamp`: ISO-8601 UTC timestamp
     - `run_id`: Run ID

---

## 6. Downstream Foreign Key Handoff Contracts

### 6.1. Handoff Contract 1 → 2: `Enacted_Law_ID`
- **Recipient:** Tier 2: Statutory Codification
- **Data Type:** `object`
- **Composite Format:** `PLAW-[congress]-[number]`
- **Payload Schema:**
```json
{
  "congress": 117,
  "law_number": 328,
  "composite_id": "PLAW-117-328"
}
```

### 6.2. Handoff Contract 1 → 5: `Target_Bill_IDs`
- **Recipient:** Tier 5: Contextual Enrichment
- **Data Type:** `array[object]`
- **Composite Format:** `BILL-[congress]-[type]-[number]`
- **Payload Schema:**
```json
[
  {
    "congress": 117,
    "type": "hr",
    "number": 3630,
    "composite_id": "BILL-117-hr-3630"
  },
  {
    "congress": 117,
    "type": "s",
    "number": 1315,
    "composite_id": "BILL-117-s-1315"
  },
  {
    "congress": 117,
    "type": "hr",
    "number": 2617,
    "composite_id": "BILL-117-hr-2617"
  }
]
```

---

## 7. Fail-Fast Error and Invariant Rules (`INV-FAIL-FAST`)
1. **Empty Query Results:** If querying `/v3/bill?q={keyword}` returns zero records, halt immediately with fatal error `Phase1DiscoveryError("No legislative measures discovered for keyword: " + keyword)`.
2. **Missing Enactment:** If neither the direct matched bills nor their companion/related vehicles contain an enacted public law in `bill.laws`, halt immediately with fatal error `Phase1EnactmentMissingError("No public law enactment found across discovered bills for keyword: " + keyword)`.
3. **Strict Prohibition:** Falling back to hardcoded bill numbers or mock public laws is strictly prohibited.
