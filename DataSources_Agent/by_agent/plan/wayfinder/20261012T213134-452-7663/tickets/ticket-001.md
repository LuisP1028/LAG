# Decision Ticket 001: Phase 1 Legislative Bill Discovery Datasource Selection, Query Mechanics, and Handoff Payload Schema

**Ticket ID:** `ticket-001.md`  
**Run ID:** `20261012T213134-452-7663`  
**Status:** RESOLVED  
**Claimed By:** `wayfinder-read-and-plan`  
**Blocked By:** None (Root Discovery Node)

---

## 1. Architectural Question
What authoritative legislative data source satisfies Phase 1 capability requirements, what are the exact endpoint operational parameters, and how must the query operations extract composite bill identifiers (`target_bill_ids`) and the enacted public law identifier (`enacted_law_id`) from candidate payloads?

---

## 2. Datasource Evaluation & Candidate Selection

### Evaluated Candidates
1. **Congress.gov REST API v3 (Library of Congress):**
   - *Authority:* Official API maintained by the Library of Congress in partnership with the Senate, House, GPO, and CRS.
   - *Capabilities:* Supports cross-session measure searching by keyword/title, historical action tracking, companion/related bill linking (`/relatedbills`), and direct metadata crosswalk to public laws.
   - *Selection Status:* **SELECTED** as the primary authoritative API for Phase 1.
2. **ProPublica Congress API (Archived / Deprecated):**
   - *Deficiencies:* Third-party intermediary; static snapshots; subject to maintenance lapses.
   - *Selection Status:* REJECTED.
3. **GovInfo API (BILLS collection):**
   - *Capabilities:* Provides raw publication text and bill packages, but lacks cross-session action lineage graphs and related bill network indexing.
   - *Selection Status:* Auxiliary for Phase 2; secondary for Phase 1.

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
| `law.number` | `/v3/bill/{c}/{t}/{n}` | Direct Path | `json.bill.laws[?(@.type=='Public Law')].number` | `string` (`"117-328"`) |
| `law.type` | `/v3/bill/{c}/{t}/{n}` | Direct Path | `json.bill.laws[0].type` | `string` (`"Public Law"`) |
| `related_bill` | `/v3/bill/{c}/{t}/{n}/relatedbills` | Direct Path | `json.relatedBills[].{congress, type, number}` | `array[object]` |

---

## 5. Downstream Handoff Contracts

### 5.1. Contract 1 → 2: `enacted_law_id`
- **Recipient:** Phase 2 (Statutory Codification)
- **Data Type:** `object`
- **Composite Key:** `PLAW-[congress]-[number]` (e.g., `PLAW-117-328`)
- **Payload Schema:**
```json
{
  "congress": 117,
  "law_number": 328,
  "type": "public",
  "composite_id": "PLAW-117-328"
}
```

### 5.2. Contract 1 → 5: `target_bill_ids`
- **Recipient:** Phase 5 (Advocacy and Evidentiary Context)
- **Data Type:** `array[object]`
- **Composite Key:** `BILL-[congress]-[type]-[number]`
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

## 6. Fail-Fast Error and Termination Rules
1. **Empty Query Results:** If querying `/v3/bill?q={keyword}` yields zero records, raise fatal exception `Phase1DiscoveryError("No legislative measures discovered for keyword: " + keyword)` and halt.
2. **Missing Enactment:** If no candidate bill or companion bill contains an enacted public law in `bill.laws`, raise fatal exception `Phase1EnactmentMissingError("No public law enactment found across discovered bills")` and halt immediately. Phase 2 must not be invoked.
