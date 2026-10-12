# Decision Ticket 002: Phase 2 Statutory Codification Markup Source Selection, Document Traversal, and Citation Extraction Schema

**Ticket ID:** `ticket-002.md`  
**Run ID:** `20261012T213134-452-7663`  
**Status:** RESOLVED  
**Claimed By:** `wayfinder-read-and-plan`  
**Blocked By:** `ticket-001.md`

---

## 1. Architectural Question
What authoritative repository provides structured statutory text for enacted public laws, how must the document hierarchy be deterministically traversed to isolate amendatory sections, and how must codified statutory citations (`us_code_citations`) be extracted into standardized composite identifiers?

---

## 2. Datasource Evaluation & Candidate Selection

### Evaluated Candidates
1. **GovInfo PLAW Collection (U.S. Government Publishing Office):**
   - *Authority:* Official repository for United States Legislative Markup (USLM XML) governed by GPO and the Office of the Law Revision Counsel (OLRC).
   - *Capabilities:* Official, complete public law text in USLM schema, preserving hierarchical containers (`division`, `title`, `section`, `subsection`) and semantically tagged amendatory instructions (`role="instruction"`, `<quotedContent>`).
   - *Selection Status:* **SELECTED** as primary authoritative repository.
2. **Office of the Law Revision Counsel (OLRC) Classification Tables:**
   - *Authority:* U.S. House of Representatives OLRC Table III (*Statutes at Large to U.S. Code*).
   - *Capabilities:* Tabular crosswalk linking public law sections directly to permanent U.S. Code additions.
   - *Selection Status:* **SELECTED** as the secondary deterministic verification crosswalk.

---

## 3. Endpoint Operational Parameters

### 3.1. GovInfo Bulk USLM XML Endpoint
- **URL:** `https://www.govinfo.gov/bulkdata/PLAW/{congress}/public/PLAW-{congress}publ{law_number}.xml`
- **GovInfo API Alternative:** `https://api.govinfo.gov/packages/PLAW-{congress}publ{law_number}/xml?api_key=[API_KEY]`
- **HTTP Method:** `GET`
- **Headers:**
  - `Accept: text/xml, application/xml`
- **Rate Limits:** Bulk repository has no API key requirement; GovInfo API has 1,000 requests/hour limit.
- **Expected Status Codes:** `200 OK`, `404 Not Found`.

### 3.2. OLRC Classification Tables
- **URL:** `https://uscode.house.gov/classification/tables.shtml`
- **Format:** HTML / Tabular text table III for target congress.

---

## 4. Payload Schema and Document Traversal Logic

### 4.1. USLM XML Schema Structure
```xml
<publicLaw xmlns="http://schemas.gpo.gov/xml/uslm" 
           identifier="/us/pl/117/328" 
           class="publicLaw">
  <meta>
    <docNumber>328</docNumber>
    <congress>117</congress>
  </meta>
  <main>
    <division identifier="/us/pl/117/328/dFF">
      <num value="FF">DIVISION FF—</num>
      <heading>HEALTH AND HUMAN SERVICES EXTENDERS</heading>
      <title identifier="/us/pl/117/328/dFF/tIV">
        <num value="IV">TITLE IV—</num>
        <heading>MEDICARE PROVISIONS</heading>
        <section identifier="/us/pl/117/328/dFF/tIV/s4133">
          <num value="4133">SEC. 4133. </num>
          <heading>MEDICARE COVERAGE FOR LYMPHEDEMA COMPRESSION TREATMENT ITEMS.</heading>
          <subsection identifier="/us/pl/117/328/dFF/tIV/s4133/a" role="instruction">
            <num value="a">(a) </num>
            <heading>Coverage.—</heading>
            <paragraph identifier="/us/pl/117/328/dFF/tIV/s4133/a/1">
              <num value="1">(1) </num>
              <content>Section 1861(s)(2) of the Social Security Act (<ref href="/us/usc/t42/s1395x/s/2">42 U.S.C. 1395x(s)(2)</ref>) is amended...</content>
              <quotedContent>
                <subparagraph value="JJ">
                  <num value="JJ">“(JJ) </num>
                  <content>lymphedema compression treatment items (as defined in subsection (mmm));”</content>
                </subparagraph>
              </quotedContent>
            </paragraph>
          </subsection>
          <subsection identifier="/us/pl/117/328/dFF/tIV/s4133/b" role="instruction">
            <num value="b">(b) </num>
            <heading>Payment.—</heading>
            <content>Section 1834 of the Social Security Act (<ref href="/us/usc/t42/s1395m">42 U.S.C. 1395m</ref>) is amended by adding at the end the following new subsection:...</content>
            <quotedContent>
              <subsection value="z">
                <num value="z">“(z) </num>
                <heading>Payment for Lymphedema Compression Treatment Items.—</heading>
                ...
              </subsection>
            </quotedContent>
          </subsection>
        </section>
      </title>
    </division>
  </main>
</publicLaw>
```

### 4.2. Field Access Classification
| Target Field | Source Element | Access Classification | Exact XPath / Selector | Target Type |
|---|---|---|---|---|
| Section Identifier | `<section>` node | Structural Traversal | `//section[contains(heading, 'LYMPHEDEMA') or contains(., 'lymphedema compression')]` | Node |
| Title Reference | `<ref>` in instruction | Structural Traversal | `.//ref[contains(@href, '/us/usc/t42')]/@href` | `string` (`"/us/usc/t42/s1395x"`) |
| Added Subsection (Coverage) | `<quotedContent>//subparagraph` | Structural Traversal | `.//subsection[@role='instruction'][1]//quotedContent//subparagraph/@value` | `string` (`"JJ"`) |
| Added Subsection (Payment) | `<quotedContent>//subsection` | Structural Traversal | `.//subsection[@role='instruction'][2]//quotedContent//subsection/@value` | `string` (`"z"`) |
| Citation String | Derived from `<ref>` + `<num>` | Structural Traversal | Formatted statutory anchor string | `string` (`"42 U.S.C. 1395x(s)(2)(JJ)"`) |

---

## 5. Downstream Handoff Contracts

### Contract 2 → 3: `us_code_citations`
- **Recipient:** Phase 3 (Administrative Rules and Directives)
- **Data Type:** `array[object]`
- **Composite Key:** `USC-[title]-[section]-[subsection]`
- **Payload Schema:**
```json
[
  {
    "title": 42,
    "section": "1395x",
    "subsection": "s(2)(JJ)",
    "citation_string": "42 U.S.C. 1395x(s)(2)(JJ)",
    "role": "benefit_definition",
    "composite_id": "USC-42-1395x-s(2)(JJ)"
  },
  {
    "title": 42,
    "section": "1395m",
    "subsection": "z",
    "citation_string": "42 U.S.C. 1395m(z)",
    "role": "payment_engine",
    "composite_id": "USC-42-1395m-z"
  }
]
```

---

## 6. Fail-Fast Error and Termination Rules
1. **Document Fetch Failure:** If the USLM XML document cannot be retrieved from GovInfo for `enacted_law_id`, raise fatal exception `Phase2DocumentRetrievalError("Failed to fetch USLM XML for " + enacted_law_id.composite_id)` and halt.
2. **Missing Statutory Amendments:** If document traversal fails to locate an amendatory instruction adding or modifying permanent U.S. Code sections, raise fatal exception `Phase2StatutoryCodificationMissingError("No permanent U.S. Code amendments discovered in public law markup")` and halt immediately. Phase 3 must not be invoked.
