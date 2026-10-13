# Decision Ticket 004: Systematic External Government Link Routing & Dynamic Parameter Resolution

**Ticket ID:** `ticket-004.md`  
**Scope:** Node Detail Drawer External Provenance Routing  
**Status:** RESOLVED  
**Claimed By:** `wayfinder-read-and-plan`  
**Blocked By:** None (Independent Component Decision)  
**Taxonomy Reference:** `LANGUAGE.md`

---

## 1. Architectural Question
How must `getGovernmentSourceLink()` in `NodeDetailDrawer.tsx` be re-architected to dynamically construct verified, live government web links for all 10 entity types specified in `functional_specification_006.md` Section 4.4, eliminating dead links, hardcoded mock URLs, and the CMS MCD "Invalid Article Version" error?

---

## 2. Root Cause Analysis & Empirical Discovery

1. **Hardcoded Mock Links:**
   - In `src/frontend/src/components/NodeDetailDrawer.tsx` (lines 47–87), `getGovernmentSourceLink` returned static, hardcoded URLs:
     - `Bill`: Hardcoded to `https://www.congress.gov/bill/117th-congress/house-bill/3630` regardless of bill selected.
     - `PublicLaw`: Hardcoded to `https://www.govinfo.gov/app/details/PLAW-117publ328`.
     - `StatutorySection`: Hardcoded to `USCODE-2022-title42-...-sec1395x`.
     - `Regulation`: Hardcoded to `88 FR 77676 / 2023-24455`.
     - `ChangeRequest`: Hardcoded to `https://www.cms.gov/files/document/r13286cp.pdf` which returns **HTTP 404: Not Found**.
     - `CoveragePolicy`: Hardcoded to `https://www.cms.gov/medicare-coverage-database/view/article.aspx?articleid=59508` which renders **"Invalid Article Version"** because CMS MCD requires an active version or search keyword.
   - Four entity types (`Jurisdiction`, `HCPCSCode`, `ICD10Code`, `LiteratureStudy`) had **no entries** in `getGovernmentSourceLink` and returned `null`.

2. **Empirical Verification of Live Government Endpoints:**
   All target endpoints were empirically verified during reconnaissance:
   - **CMS MCD:** Navigating to `https://www.cms.gov/medicare-coverage-database/search-results.aspx?keyword={articleId}` returns HTTP 200 with zero "Invalid Article Version" errors.
   - **GPO GovInfo:** `https://www.govinfo.gov/app/details/PLAW-{congress}publ{number}` returns HTTP 200 for enacted public laws.
   - **Congress.gov:** `https://www.congress.gov/bill/{congressOrdinal}-congress/{billTypeSlug}/{number}` is the canonical official Congress bill permalink.
   - **Federal Register:** `https://www.federalregister.gov/d/{document_number}` returns HTTP 200 and permanently redirects to the official rule page.
   - **Legal Information Institute (LII):** `https://www.law.cornell.edu/uscode/text/{title}/{section}` returns HTTP 200.
   - **CMS Transmittals Index:** `https://www.cms.gov/medicare/regulations-guidance/transmittals?search={cr_number}` returns HTTP 200, replacing the dead PDF link.
   - **DME MAC Contractors:**
     - Jurisdictions B & C (CGS Administrators): `https://www.cgsmedicare.com/` (HTTP 200).
     - Jurisdictions A & D (Noridian Healthcare Solutions): `https://med.noridianmedicare.com/` (HTTP 200).
   - **CMS DMEPOS Fee Schedule:** `https://www.cms.gov/medicare/payment/fee-schedules/dmepos/dmepos-fee-schedule` returns HTTP 200.
   - **CDC ICD-10-CM Browser:** `https://icd10cmtool.cdc.gov/?prop={code}` returns HTTP 200.
   - **Senate LDA Database:** `https://lda.senate.gov/system/public/` returns HTTP 200.

---

## 3. Decision & Technical Specifications

In `src/frontend/src/components/NodeDetailDrawer.tsx`, rewrite `getGovernmentSourceLink()` into a deterministic router accepting `selectedNode: GraphNode`:

### 3.1. Helper Parsers & Formatters
```tsx
const getOrdinal = (n: number): string => {
  const s = ['th', 'st', 'nd', 'rd'];
  const v = n % 100;
  return n + (s[(v - 20) % 10] || s[v] || s[0]);
};

const getBillTypeSlug = (type: string): string => {
  const clean = (type || '').toLowerCase().replace(/[^a-z]/g, '');
  switch (clean) {
    case 'hr': return 'house-bill';
    case 's': return 'senate-bill';
    case 'hjres': return 'house-joint-resolution';
    case 'sjres': return 'senate-joint-resolution';
    case 'hconres': return 'house-concurrent-resolution';
    case 'sconres': return 'senate-concurrent-resolution';
    case 'hres': return 'house-resolution';
    case 'sres': return 'senate-resolution';
    default: return 'house-bill';
  }
};
```

### 3.2. Detailed Entity Contract Specifications

1. **`CoveragePolicy` (`CMS-MCD-{article_id}`):**
   - **Parameter Extraction:** `props.article_id || selectedNode.primary_key.replace(/^CMS-MCD-/, '')`
   - **Title:** `CMS Medicare Coverage Database (${articleId})`
   - **URL:** `https://www.cms.gov/medicare-coverage-database/search-results.aspx?keyword=${encodeURIComponent(articleId)}`

2. **`PublicLaw` (`PLAW-{congress}-{number}`):**
   - **Parameter Extraction:** `congress = props.congress`, `number = props.number`. If missing from props, parse via regex `PLAW-(\d+)-(\d+)` against `primary_key`.
   - **Title:** `GPO GovInfo Public Law ${congress}-${number}`
   - **URL:** `https://www.govinfo.gov/app/details/PLAW-${congress}publ${number}`

3. **`Bill` (`BILL-{congress}-{type}-{number}`):**
   - **Parameter Extraction:** `congress = props.congress`, `type = props.type`, `number = props.number`. If missing, parse from `BILL-(\d+)-([a-z]+)-(\d+)`.
   - **Title:** `Congress.gov ${type.toUpperCase()} ${number} (${getOrdinal(congress)} Congress)`
   - **URL:** `https://www.congress.gov/bill/${getOrdinal(congress)}-congress/${getBillTypeSlug(type)}/${number}`

4. **`Regulation` (`FR-{document_number}`):**
   - **Parameter Extraction:** `docNum = props.document_number || selectedNode.primary_key.replace(/^FR-/, '')`
   - **Title:** `Federal Register Final Rule (${props.citation || docNum})`
   - **URL:** `https://www.federalregister.gov/d/${encodeURIComponent(docNum)}`

5. **`StatutorySection` (`USC-{title}-{section}`):**
   - **Parameter Extraction:** `title = props.title || 42`, `section = props.section || '1395x'`.
   - **Clean Section:** `cleanSection = section.split('-')[0]` (e.g. `1395x` from `1395x-s-2-JJ`).
   - **Title:** `US Code Title ${title} § ${section} (LII)`
   - **URL:** `https://www.law.cornell.edu/uscode/text/${encodeURIComponent(title)}/${encodeURIComponent(cleanSection)}`

6. **`ChangeRequest` (`CMS-CR-{cr_number}`):**
   - **Parameter Extraction:** `crNum = props.cr_number || selectedNode.primary_key.replace(/^CMS-CR-/, '')`
   - **Title:** `CMS Transmittals Index (CR ${crNum})`
   - **URL:** `https://www.cms.gov/medicare/regulations-guidance/transmittals?search=${encodeURIComponent(crNum)}`

7. **`Jurisdiction` (`JURIS-DME-{A|B|C|D}`):**
   - **Parameter Extraction:** `code = props.code || selectedNode.primary_key`
   - **Branching Logic:**
     - If code contains `'B'` or `'C'`:
       - **Title:** `CGS Administrators DME MAC Portal (${code})`
       - **URL:** `https://www.cgsmedicare.com/`
     - If code contains `'A'` or `'D'`:
       - **Title:** `Noridian Healthcare Solutions DME MAC Portal (${code})`
       - **URL:** `https://med.noridianmedicare.com/`

8. **`HCPCSCode` (`HCPCS-{code}`):**
   - **Parameter Extraction:** `code = props.code || selectedNode.primary_key.replace(/^HCPCS-/, '')`
   - **Title:** `CMS DMEPOS Fee Schedule & Coding Reference (${code})`
   - **URL:** `https://www.cms.gov/medicare/payment/fee-schedules/dmepos/dmepos-fee-schedule`

9. **`ICD10Code` (`ICD10-{code}`):**
   - **Parameter Extraction:** `code = props.code || selectedNode.primary_key.replace(/^ICD10-/, '')`
   - **Title:** `CDC ICD-10-CM Clinical Browser (${code})`
   - **URL:** `https://icd10cmtool.cdc.gov/?prop=${encodeURIComponent(code)}`

10. **`LobbyingFiling` (`LDA-{uuid}`):**
    - **Title:** `Senate LDA Lobbying Disclosure Search`
    - **URL:** `https://lda.senate.gov/system/public/`

11. **`LiteratureStudy` (`PUBMED-{pmid}`):**
    - **Parameter Extraction:** `pmid = props.pmid || selectedNode.primary_key.replace(/^PUBMED-/, '')`
    - **Title:** `PubMed National Library of Medicine (${pmid})`
    - **URL:** `https://pubmed.ncbi.nlm.nih.gov/${encodeURIComponent(pmid)}/`

---

## 4. Acceptance Criteria
1. Clicking the external source link in the detail drawer for every entity type opens a valid, live government web page in a new browser tab (`target="_blank" rel="noopener noreferrer"`).
2. Coverage Policy links navigate directly to live CMS MCD search results without "Invalid Article Version" errors.
3. Change Request links navigate to the live CMS Transmittals search without 404 errors.
4. Procedure code (`HCPCSCode`) and diagnosis code (`ICD10Code`) detail views render active, working government reference links.
5. All 10 entity types dynamically interpolate their exact primary key / attribute properties into the target URL.
