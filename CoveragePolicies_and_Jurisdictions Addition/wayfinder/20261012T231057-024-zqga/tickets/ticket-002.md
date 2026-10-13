# Decision Ticket 002: Phase 2 Statutory Codification Delta and USLM XML Structural Parsing Schema

**Ticket ID:** `ticket-002.md`  
**Run ID:** `20261012T231057-024-zqga`  
**Scope:** Tier 2: Statutory Codification  
**Status:** RESOLVED  
**Claimed By:** `wayfinder-read-and-plan`  
**Blocked By:** `ticket-001.md`

---

## 1. Architectural Question
What authoritative repository provides structured statutory text for enacted public laws, how must the document hierarchy be deterministically traversed to isolate amendatory sections, and how must codified statutory sections (`StatutorySection`) and `[:MODIFIES_CODE]` edges be constructed with complete provenance according to `functional_specification_003.md`?

---

## 2. Datasource Evaluation & Candidate Selection

### Evaluated Candidates
1. **GovInfo Bulk PLAW USLM XML (U.S. Government Publishing Office):**
   - *Authority:* Official repository for United States Legislative Markup (USLM XML) governed by GPO and the Office of the Law Revision Counsel (OLRC).
   - *Capabilities:* Official, complete public law text preserving hierarchical structure (`division`, `title`, `section`, `subsection`) and semantically tagged amendatory instructions (`role="instruction"`, `<amendingAction>`, `<quotedContent>`).
   - *Selection Status:* **SELECTED** as primary authoritative repository for Tier 2.
2. **OLRC U.S. Code Classification Tables (Table III):**
   - *Authority:* U.S. House Office of the Law Revision Counsel Table III (*Statutes at Large to U.S. Code*).
   - *Capabilities:* Tabular crosswalk confirming additions/amendments to Title 42.
   - *Selection Status:* Secondary verification crosswalk.

---

## 3. Endpoint Operational Parameters

### 3.1. GovInfo Bulk USLM XML Endpoint
- **URL:** `https://www.govinfo.gov/bulkdata/PLAW/{congress}/public/PLAW-{congress}publ{law_number}.xml`
- **GovInfo API Alternative:** `https://api.govinfo.gov/packages/PLAW-{congress}publ{law_number}/xml?api_key=[API_KEY]`
- **Local Empirical Asset:** `DataSources_Agent/assets/20261012T213134-452-7663/phase2_uslm_plaw_117_328_sec4133.xml`
- **HTTP Method:** `GET`
- **Headers:**
  - `Accept: text/xml, application/xml`
- **Rate Limits:** Bulk repository has no API key requirement; GovInfo API has 1,000 requests/hour limit.
- **Expected Status Codes:** `200 OK`, `404 Not Found`.

---

## 4. Payload Schema and Document Traversal Logic

### 4.1. USLM XML Document Structure (Empirical Sample: PLAW 117-328 Sec. 4133)
```xml
<section identifier="/us/pl/117/328/dFF/tIV/stD/s4133">
  <num value="4133">SEC. 4133. </num>
  <heading>MEDICARE COVERAGE FOR LYMPHEDEMA COMPRESSION TREATMENT ITEMS.</heading>
  <subsection identifier="/us/pl/117/328/dFF/tIV/stD/s4133/a" role="instruction">
    <num value="a">(a) </num>
    <heading>Coverage.—</heading>
    <paragraph identifier="/us/pl/117/328/dFF/tIV/stD/s4133/a/1">
      <num value="1">(1) </num>
      <content>Section 1861(s)(2) of the Social Security Act (<ref href="/us/usc/t42/s1395x/s/2">42 U.S.C. 1395x(s)(2)</ref>) <amendingAction type="amend">is amended</amendingAction>—
        <quotedContent>
          <subparagraph value="JJ">
            <num value="JJ">“(JJ) </num>
            <content>lymphedema compression treatment items (as defined in subsection (mmm));”</content>
          </subparagraph>
        </quotedContent>
      </content>
    </paragraph>
  </subsection>
</section>
```

### 4.2. Field Access Classification
| Target Field | Source Element | Access Classification | Exact XPath / Selector | Target Type |
|---|---|---|---|---|
| Section Node | `<section>` container | Structural Traversal | `//division[@id='FF']/title[@id='IV']/section[@id='4133']` or `//section[contains(heading, 'LYMPHEDEMA')]` | XML Node |
| Title Reference | `<ref>` in instruction | Structural Traversal | `.//ref[contains(@href, '/us/usc/t42')]/@href` -> `42` | `integer` (`42`) |
| Section Reference | `<ref>` in instruction | Structural Traversal | `substring-after(.//ref/@href, '/s')` -> `"1395x"` | `string` (`"1395x"`) |
| Added Subsection (Coverage) | `<quotedContent>//subparagraph` | Structural Traversal | `["s", "2", "JJ"]` | `array[string]` |
| Heading | `<heading>` node | Direct Path | `string(.//heading[1])` | `string` |
| Statutory Text | `<content>` / `<quotedContent>` | Direct Path | `normalize-space(.//quotedContent)` | `string` |

---

## 5. Graph Node and Edge Construction Contracts

### 5.1. Vertex: `StatutorySection`
- **Primary Key Format:** `USC-[title]-[section]-[subsections]` (e.g., `USC-42-1395x-s-2-JJ`)
- **Required Properties:**
  - `title: int` (`42`)
  - `section: string` (`"1395x"`)
  - `subsections: string[]` (`["s", "2", "JJ"]`)
  - `heading: string` (`"MEDICARE COVERAGE FOR LYMPHEDEMA COMPRESSION TREATMENT ITEMS."`)
  - `text: string` (`"lymphedema compression treatment items (as defined in subsection (mmm));"`)

### 5.2. Edge: `(PublicLaw)-[:MODIFIES_CODE]->(StatutorySection)`
- **Source Node:** `PublicLaw` (`PLAW-117-328`)
- **Target Node:** `StatutorySection` (`USC-42-1395x-s-2-JJ`)
- **Cardinality:** `1..*`
- **Semantics:** Maps public law division/title/section to the amended U.S. Code section.
- **Edge Provenance Contract:**
  - `source_uri`: `https://www.govinfo.gov/bulkdata/PLAW/117/public/PLAW-117publ328.xml`
  - `selector`: `//division[@id='FF']/title[@id='IV']/section[@id='4133']`
  - `ingestion_timestamp`: ISO-8601 UTC timestamp
  - `run_id`: Run ID

---

## 6. Downstream Foreign Key Handoff Contract

### Contract 2 → 3: `US_Code_Citations`
- **Recipient:** Tier 3: Administrative & Regulatory Execution
- **Data Type:** `object` (or array of objects)
- **Composite Format:** `USC-[title]-[section]-[subsections]`
- **Payload Schema:**
```json
{
  "title": 42,
  "section": "1395x",
  "subsections": ["s", "2", "JJ"],
  "citation_string": "42 U.S.C. 1395x(s)(2)(JJ)",
  "composite_id": "USC-42-1395x-s-2-JJ"
}
```

---

## 7. Fail-Fast Error and Invariant Rules (`INV-FAIL-FAST`)
1. **Document Fetch Failure:** If the USLM XML package cannot be loaded for `Enacted_Law_ID`, halt immediately with fatal error `Phase2DocumentRetrievalError("Failed to fetch USLM XML for " + enacted_law_id.composite_id)`.
2. **Missing Section Isolation:** If structural XPath `//division[@id='FF']/title[@id='IV']/section[@id='4133']` or statutory text search fails to match any node, halt immediately with fatal error `Phase2SectionNotFoundError("Failed to isolate statutory section in public law XML")`.
3. **Missing Statutory Citation:** If the amending instruction fails to yield Title `42`, Section `1395x`, and subsection `JJ`, halt immediately with fatal error `Phase2CitationExtractionError("Failed to parse USC citation anchors from amending instruction")`. Tier 3 must not be invoked.
