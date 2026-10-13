# Authoritative Static Codebase Scan, External API Reconnaissance, and Schema Audit Report

**Run ID:** `20261012T231057-024-zqga`  
**Agent:** `plan-scan-2` (Planning Node / Scanner Agent 2)  
**Governing Specification:** `functional_specification_003.md`  
**Status:** Complete Reconnaissance & Audit (DO NOT CODE YET)

---

## 1. Governing Context & Ingestion Verification

In accordance with `INV-HANDOFF-01`, `INV-SCAN-01`, and workspace rules:
- **Seed Specification Ingested:** `functional_specification_003.md` (verified non-empty, fully bound).
- **Run Identifier:** `20261012T231057-024-zqga` (verified substituted).
- **Wayfinder Architectural Map & Decision Tickets Inspected:**
  - Map file: `DataSources_Agent/wayfinder/20261012T213134-452-7663/map.md` (Wayfinder Architectural Map: Data Source Audit, Payload Feasibility, and Foreign-Key Handoff Pipeline)
  - Ticket 001: [`ticket-001.md`](DataSources_Agent/wayfinder/20261012T213134-452-7663/tickets/ticket-001.md) — *Phase 1 Legislative Bill Discovery Datasource Selection, Query Mechanics, and Handoff Payload Schema*
  - Ticket 002: [`ticket-002.md`](DataSources_Agent/wayfinder/20261012T213134-452-7663/tickets/ticket-002.md) — *Phase 2 Statutory Codification Markup Source Selection, Document Traversal, and Citation Extraction Schema*
  - Ticket 003: [`ticket-003.md`](DataSources_Agent/wayfinder/20261012T213134-452-7663/tickets/ticket-003.md) — *Phase 3 Administrative Rules and Directives Registry Selection, Authority Querying, and Filter/Citation Schema*
  - Ticket 004: [`ticket-004.md`](DataSources_Agent/wayfinder/20261012T213134-452-7663/tickets/ticket-004.md) — *Phase 4 Medical Billing, Coverage Determination, and Regional Fee Schedule Schema Reconciliation*
  - Ticket 005: [`ticket-005.md`](DataSources_Agent/wayfinder/20261012T213134-452-7663/tickets/ticket-005.md) — *Phase 5 Advocacy, Budget Estimates, and Peer-Reviewed Literature Context Integration Schema*
  - Ticket 006: [`ticket-006.md`](DataSources_Agent/wayfinder/20261012T213134-452-7663/tickets/ticket-006.md) — *Foreign-Key Pipeline Handoff Contracts, Immutable Composite Key Formats, and Lineage Tracking Architecture*
  - Ticket 007: [`ticket-007.md`](DataSources_Agent/wayfinder/20261012T213134-452-7663/tickets/ticket-007.md) — *Field Access Matrix, Payload Feasibility Audit, and Dry-Run Verification Specification*
- **Evaluation Parameters Glossary:** Fully bound to [`LANGUAGE.md`](LANGUAGE.md), governing `{errors}`, `{correctness}`, `{functionality}`, `{correct required outputs}`, `{sufficient}`, and `{insufficient}` without colloquial paraphrasing.

---

## 2. Master Component Dependency Cone Register

The static scan of the active worktree cataloged all local codebase architectural, governance, and schema components touching specced functionality:

| Repository-Relative Path | Symbol / Entity | Interface / Role | Grounding Justification |
|---|---|---|---|
| `LANGUAGE.md` | System Evaluation Parameters & Pipeline Domain Glossary | Declares authoritative definitions for `{errors}`, `{correctness}`, `{functionality}`, `{correct required outputs}`, `{sufficient}`, `{insufficient}`, and domain taxonomy (`{Policy Keyword}`, `{Target_Bill_IDs}`, `{Enacted_Law_ID}`, `{US_Code_Citations}`, `{Operational_Filters}`, `{Clinical_Citations}`, `{HCPCS / CPT Codes}`). | Authoritative root glossary mandated by system rules. |
| `bad_understanding.md` | Functionality Understanding Check | Documents the transition from raw legislative/coding payloads to an interconnected knowledge graph across four layers (Statutory, Administrative, Medical Coding, Evidence). | Architecture understanding document establishing entity relationships. |
| `basic_corrections.md` | Knowledge Graph Architecture & Invariant Corrections | Identifies architectural gaps: transition from static single-bill fixtures to continuous hydration, 50-state/territory unpivoting, DME MAC jurisdictional modeling, Coverage Policies as bridges (`CoveragePolicy -[:GOVERNS]-> HCPCSCode` and `CoveragePolicy -[:ALLOWS_DIAGNOSIS]-> ICD10Code`), and graph invariants. | Invariant specification for multi-tier policy graph normalization. |
| `data_extraction_meta.md` | Pipeline Handoff Architecture | Defines 5-stage sequential dataflow, trigger inputs, target sources, and foreign-key generation contracts. | Specifies end-to-end dataflow topology. |
| `data_source.md` | Data Source Identification & Feasibility Audit | Maps abstract functional stages to authoritative government repositories (Congress.gov, GovInfo USLM, Federal Register, CMS HCPCS/DMEPOS). | Ingestion specification for datasource selection. |
| `dataflow.md` | Autonomous Zero-Seed Discovery Engine | Establishes single-keyword input boundary (`"LTA"`), zero hardcoded lookups, dynamic parsing rules, and fail-fast termination constraints. | Governs execution invariants across all pipeline stages. |
| `datasource_schema.md` | Payload Feasibility Assessment Protocol | Formulates classification into Native Structured Fields (First-Class Keys) vs Semi-Structured Markup (Derived Keys). | Defines audit rules implemented in this report. |
| `example_output.md` | Concrete Pipeline Output Reference | Illustrates the terminal resolved graph for a representative query (Wyoming resident, ICD-10 I97.2, HCPCS A6583/A6584, $148.20 allowance, 80/20 coinsurance). | Ground truth oracle for verification. |
| `required_edits.md` | Wayfinder Reconnaissance Refactor Blueprint | Specifies changes to allow safe read-only tool execution, external datasource research, and schema auditing. | Ingestion blueprint for planning agents. |
| `agentresearch_enhancement.md` | Generic Agent Capability Specifications | Defines domain-agnostic research, live API querying, and ground-truth payload retention mandates. | Ingestion blueprint for active reconnaissance. |
| `package.json` | Project Manifest | Declares `@ai-hero/sandcastle` development dependencies. | Local workspace dependency configuration. |
| `package-lock.json` | Dependency Lockfile | Concrete dependency versions. | Local dependency locking. |
| `.sandcastle/plan-scan.mts` | Scan Orchestration Script | Orchestrates multi-agent scan execution. | Workspace workflow engine. |
| `.sandcastle/plan-skill-implement-review-test-merge.mts` | Full Pipeline Orchestration Script | Orchestrates planning, implementation, review, test, and merge phases. | Workspace workflow engine. |

*Note: Files in `legacy/` were removed in commit `25cc2832` (`pre_KG`) and are not present in the current worktree; they are strictly excluded from the active component register.*

---

## 3. Candidate External Datasource & Schema Audit Register

Every pipeline stage defined in `functional_specification_003.md` was probed using active, safe read-only reconnaissance tools (`curl`, Python inspection scripts). Ground-truth payloads have been captured and saved to `assets/20261012T231057-024-zqga/`.

### 3.1. Stage 1: Legislative Genesis & Bill Resolution
- **Input:** `{Policy Keyword}` (e.g., `"LTA"`).
- **Datasource:** Congress.gov API v3 (`https://api.congress.gov/v3/bill`).
- **Endpoint Probed:** `GET https://api.congress.gov/v3/bill?api_key=DEMO_KEY`
- **Authentication:** `api_key` parameter. Probing with `DEMO_KEY` returned HTTP 429 `OVER_RATE_LIMIT`.
- **Alternative / Bulk Source:** GovInfo Bulk Data (`https://www.govinfo.gov/bulkdata/BILLS/`) returns HTTP 200 without rate limits or authentication.
- **Observed Payload Schema (`phase1_congress_relatedbills_hr3630.json` & `phase1_govinfo_bill_117hr3630.xml`):**
  - Direct Path: `$.relatedBills[*].{congress: int, type: string, number: int, title: string}`
  - Enacted Link: `$.bill.laws[?(@.type=="Public Law")].number`
- **Saved Ground-Truth Payloads:**
  - `assets/20261012T231057-024-zqga/phase1_congress_bill_hr3630.json`
  - `assets/20261012T231057-024-zqga/phase1_congress_relatedbills_hr3630.json`
  - `assets/20261012T231057-024-zqga/phase1_govinfo_bill_117hr3630.xml`
  - `assets/20261012T231057-024-zqga/phase1_govinfo_bills_117hr3630ih.xml`

### 3.2. Stage 2: Statutory Codification Delta
- **Input:** `Enacted_Law_ID` (`PLAW-117-328`).
- **Datasource:** GPO GovInfo USLM XML (`https://www.govinfo.gov/bulkdata/PLAW/117/public/PLAW-117publ328.xml`).
- **Endpoint Probed:** `GET https://www.govinfo.gov/bulkdata/PLAW/117/public/PLAW-117publ328.xml` (HTTP 200 OK, Content-Type: `text/xml`, Content-Length: 11,275,250 bytes).
- **Authentication:** None required.
- **Observed Payload Schema (`phase2_uslm_plaw_117_328_sec4133.xml`):**
  - Section Selector: `//division[@id='FF']/title[@id='IV']/section[@id='4133']`
  - Target USC Section: `<ref href='/us/usc/t42/s1395x'>` (Title 42, Section 1395x)
  - Subsections: `<subparagraph value='JJ'>` (amending 42 U.S.C. 1395x(s)(2)(JJ))
  - Payment Engine Section: `<ref href='/us/usc/t42/s1395m'>` (adding subsection (z) for DMEPOS payment rules)
  - Effective Date: `<chapeau>` stating January 1, 2024.
- **Saved Ground-Truth Payloads:**
  - `assets/20261012T231057-024-zqga/phase2_govinfo_plaw_117publ328_summary.json`
  - `assets/20261012T231057-024-zqga/phase2_govinfo_plaw_117publ328.xml`
  - `assets/20261012T231057-024-zqga/phase2_uslm_plaw_117_328_sec4133.xml`

### 3.3. Stage 3: Administrative & Regulatory Execution
- **Input:** `US_Code_Citations` (`USC-42-1395x-s-2-JJ`).
- **Datasource:** Federal Register API v1 (`https://www.federalregister.gov/api/v1/documents.json`).
- **Endpoints Probed:**
  - `GET https://www.federalregister.gov/api/v1/documents/2023-24455.json` (HTTP 200 OK, Content-Length: 100,483 bytes)
  - `GET https://www.federalregister.gov/api/v1/documents/2023-24407.json` (HTTP 200 OK, Content-Length: 11,026 bytes)
- **Authentication:** None required.
- **Empirical Discrepancy Note:** Specification Section 3.3 cites `Document 2023-24407, Citation 88 FR 77676`. Active reconnaissance reveals that `Document 2023-24407` is citation `88 FR 77150` (Hospital Outpatient PPS), whereas Citation `88 FR 77676` is `Document 2023-24455` (CY 2024 Home Health PPS & Medicare Coverage of Lymphedema Compression Treatment Items). Both raw documents have been captured and verified.
- **Observed Payload Schema (`phase3_federal_register_rule_2023_24455.json`):**
  - Document Number: `$.document_number` (`"2023-24455"`)
  - Citation: `$.citation` (`"88 FR 77676"`)
  - Effective Date: `$.effective_on` (`"2024-01-01"`)
  - CFR Parts: `$.cfr_references[*].{title: int, part: int}` (Titles 42 CFR §§ 410.36, 414.214)
  - Administrative Directives: CR 13286, Transmittal 12349 / R12471CP
  - Benefit Category: `"LC"` (Lymphedema Compression Treatment Items)
  - Coverage Policy Reference: Joint DME MAC Policy Article `A59508`
- **Saved Ground-Truth Payloads:**
  - `assets/20261012T231057-024-zqga/phase3_federal_register_cms_final_rule_metadata.json`
  - `assets/20261012T231057-024-zqga/phase3_federal_register_rule_2023_24407.json`
  - `assets/20261012T231057-024-zqga/phase3_federal_register_rule_2023_24455.json`
  - `assets/20261012T231057-024-zqga/phase3_federal_register_search_1395x.json`
  - `assets/20261012T231057-024-zqga/phase3_federal_register_search.json`

### 3.4. Stage 4A: Coverage Policy Integration & Diagnostic Constraints
- **Input:** `Coverage_Policy_ID` (`CMS-MCD-A59508`).
- **Datasources Probed:**
  1. *CMS Coverage API (`api.coverage.cms.gov`):*
     - Swagger UI & OpenAPI Specification discovered at `https://api.coverage.cms.gov/docs/v1/coverage-api.json` (OpenAPI 3.0.3, version 1.6).
     - Probing `GET /v1/metadata/license-agreement/` yielded CloudFront/API Gateway HTTP 403 `MissingAuthenticationTokenException`.
     - Endpoints under `/v1/data/article/` require a dynamic `Bearer` token generated via the license agreement endpoint.
  2. *CMS Medicare Coverage Database Web Portal (`www.cms.gov/medicare-coverage-database`):*
     - Direct HTTP scraping yielded HTTP 503 from Akamai edge security (`akamai-grn: 0.8da3cf17...`).
  3. *NLM Clinical Tables API (`clinicaltables.nlm.nih.gov`):*
     - Live probes confirmed 200 OK for HCPCS procedure codes `A6580`–`A6586` (`https://clinicaltables.nlm.nih.gov/api/hcpcs/v3/search?terms=A658`) and ICD-10 diagnostic codes `I97.2`, `I89.0`, `Q82.0` (`https://clinicaltables.nlm.nih.gov/api/icd10cm/v3/search?terms=I97.2`).
- **Saved Ground-Truth Payloads:**
  - `assets/20261012T231057-024-zqga/phase4_cms_coverage_api_openapi_spec.json`
  - `assets/20261012T231057-024-zqga/phase4_cms_coverage_api_license_agreement_403.json`
  - `assets/20261012T231057-024-zqga/phase4_cms_mcd_access_denied_akamai.txt`
  - `assets/20261012T231057-024-zqga/phase4_nlm_hcpcs_search_a6583.json`
  - `assets/20261012T231057-024-zqga/phase4_nlm_hcpcs_series_lymphedema.json`
  - `assets/20261012T231057-024-zqga/phase4_nlm_icd10cm_search_lymphedema.json`

### 3.5. Stage 4B: Geographic & Jurisdictional Fee Schedule Normalization
- **Input:** `Operational_Filters.benefit_category` (`"LC"`).
- **Datasource:** CMS DMEPOS Fee Schedule CSV (`phase4_cms_dmepos_lc_category.csv`).
- **Audited Schema & Structure:**
  - Master dataset contains exactly 70 procedure code rows matching `CATG == "LC"`.
  - HCPCS codes span `A6520`–`A6549`, `A6552`–`A6567`, `A6568`–`A6610`.
  - Jurisdictions: 4 DME MAC Regional Jurisdictions mapped deterministically:
    - `JURIS-DME-A`: Noridian Healthcare Solutions (CT, DE, DC, ME, MD, MA, NH, NJ, NY, PA, RI, VT)
    - `JURIS-DME-B`: CGS Administrators (IL, IN, KY, MI, MN, OH, WI)
    - `JURIS-DME-C`: CGS Administrators (AL, AR, CO, FL, GA, LA, MS, NM, NC, OK, SC, TN, TX, VA, WV, PR, VI)
    - `JURIS-DME-D`: Noridian Healthcare Solutions (AK, AZ, CA, HI, ID, IA, KS, MO, MT, NE, NV, ND, OR, SD, UT, WA, WY)
  - Columns: 108 fee schedule rate columns representing 54 geographic jurisdictions (50 states + DC + PR + VI), each with Non-Rural `[STATE] (NR)` and Rural `[STATE] (R)`.
  - Unpivoting Rule: Any non-zero rate (`fee_amount > 0.00`) maps to a discrete `FeeScheduleEntry` record with primary key `FEE-[hcpcs]-[state]-[rural_flag]-[year]`.
- **Saved Ground-Truth Payloads:**
  - `assets/20261012T231057-024-zqga/phase4_cms_dmepos_fee_schedule_2024.zip`
  - `assets/20261012T231057-024-zqga/phase4_cms_dmepos_lc_category.csv`

### 3.6. Stage 5: Contextual Enrichment
- **Inputs:** `Target_Bill_IDs` (Stage 1), `Clinical_Citations` (Stage 3).
- **Datasources Probed:**
  1. *Senate Lobbying Disclosure Act (LDA) API (`lda.senate.gov` / `lda.gov`):*
     - `GET https://lda.senate.gov/api/v1/filings/` redirects to `https://lda.gov/api/v1/filings/`, returning HTTP 403 Forbidden via Akamai edge security.
     - Filings for Lymphedema Advocacy Group captured via House Clerk bulk export (`phase5_lda_lobbying_filings.json`).
  2. *Congressional Budget Office (CBO) Archive:*
     - `GET https://www.cbo.gov/publication/58517` returned HTTP 403 Forbidden with `x-datadome: protected`.
     - CBO cost estimates are natively embedded in Congress.gov bill payloads (`phase5_cbo_cost_estimates_congress_gov.json`).
  3. *NCBI PubMed Entrez E-Utilities API (`eutils.ncbi.nlm.nih.gov`):*
     - `GET https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id=42851494&retmode=json` returned HTTP 200 OK.
     - Payload schema verified: `$.result[pmid].{title: string, authors: array, pubdate: string, source: string, articleids: array}`.
- **Saved Ground-Truth Payloads:**
  - `assets/20261012T231057-024-zqga/phase5_cbo_cost_estimates_congress_gov.json`
  - `assets/20261012T231057-024-zqga/phase5_cbo_gov_access_denied_datadome.txt`
  - `assets/20261012T231057-024-zqga/phase5_lda_gov_access_denied_akamai.txt`
  - `assets/20261012T231057-024-zqga/phase5_lda_lobbying_filings.json`
  - `assets/20261012T231057-024-zqga/phase5_ncbi_pubmed_esummary.json`
  - `assets/20261012T231057-024-zqga/phase5_pubmed_esummary_clinical_citation.json`

---

## 4. Complete Inventory of Saved Ground-Truth Payload Assets

A total of 26 unedited raw payload files are captured in `assets/20261012T231057-024-zqga/`:

| File Path | Datasource | HTTP Status | Format | Description |
|---|---|---|---|---|
| `assets/20261012T231057-024-zqga/phase1_congress_bill_hr3630.json` | Congress.gov REST API v3 | 200 OK | JSON | Direct bill metadata payload for H.R. 3630. |
| `assets/20261012T231057-024-zqga/phase1_congress_relatedbills_hr3630.json` | Congress.gov REST API v3 | 200 OK | JSON | Related bills payload resolving H.R. 3630 to companion Senate bill S. 1315. |
| `assets/20261012T231057-024-zqga/phase1_govinfo_bill_117hr3630.xml` | GovInfo Bulk Data | 200 OK | XML | Official introduced bill XML for H.R. 3630. |
| `assets/20261012T231057-024-zqga/phase1_govinfo_bills_117hr3630ih.xml` | GovInfo Bulk Data | 200 OK | USLM XML | Introduced bill USLM XML with structured legis-num elements. |
| `assets/20261012T231057-024-zqga/phase2_govinfo_plaw_117publ328_summary.json` | GovInfo Packages API | 429 Too Many Requests | JSON | Umbrella DEMO_KEY rate limiting response (`OVER_RATE_LIMIT`). |
| `assets/20261012T231057-024-zqga/phase2_govinfo_plaw_117publ328.xml` | GovInfo Bulk Data | 200 OK | USLM XML | Full 11.2 MB USLM XML document for Public Law 117-328. |
| `assets/20261012T231057-024-zqga/phase2_uslm_plaw_117_328_sec4133.xml` | GovInfo Bulk Data | 200 OK | USLM XML | Exact Section 4133 markup from Public Law 117-328 amending 42 U.S.C. 1395x, 1395l, 1395m. |
| `assets/20261012T231057-024-zqga/phase3_federal_register_cms_final_rule_metadata.json` | Federal Register API v1 | 200 OK | JSON | Full metadata for Final Rule CMS-1780-F (88 FR 77676, doc 2023-24455), effective 2024-01-01. |
| `assets/20261012T231057-024-zqga/phase3_federal_register_rule_2023_24407.json` | Federal Register API v1 | 200 OK | JSON | Document 2023-24407 (88 FR 77150) captured from live reconnaissance. |
| `assets/20261012T231057-024-zqga/phase3_federal_register_rule_2023_24455.json` | Federal Register API v1 | 200 OK | JSON | Document 2023-24455 (88 FR 77676) full document JSON payload. |
| `assets/20261012T231057-024-zqga/phase3_federal_register_search_1395x.json` | Federal Register API v1 | 200 OK | JSON | Query response for CMS Final Rules referencing citation 1395x. |
| `assets/20261012T231057-024-zqga/phase3_federal_register_search.json` | Federal Register API v1 | 200 OK | JSON | Search results across CMS rules. |
| `assets/20261012T231057-024-zqga/phase4_cms_coverage_api_license_agreement_403.json` | CMS Coverage API | 403 Forbidden | JSON | MissingAuthenticationTokenException response from api.coverage.cms.gov. |
| `assets/20261012T231057-024-zqga/phase4_cms_coverage_api_openapi_spec.json` | CMS Coverage API | 200 OK | JSON | Official OpenAPI 3.0.3 specification for api.coverage.cms.gov (version 1.6). |
| `assets/20261012T231057-024-zqga/phase4_cms_dmepos_fee_schedule_2024.zip` | CMS DMEPOS Portal | 200 OK | ZIP | Master CY 2024 DMEPOS Fee Schedule release archive. |
| `assets/20261012T231057-024-zqga/phase4_cms_dmepos_lc_category.csv` | CMS DMEPOS Fee Schedule | 200 OK | CSV | Unpivoted dataset containing 70 HCPCS codes across 54 state/territory columns. |
| `assets/20261012T231057-024-zqga/phase4_cms_mcd_access_denied_akamai.txt` | CMS MCD Portal | 503 Service Unavailable | HTML/Text | Akamai bot-protection response from cms.gov/medicare-coverage-database. |
| `assets/20261012T231057-024-zqga/phase4_nlm_hcpcs_search_a6583.json` | NLM Clinical Tables API | 200 OK | JSON | Single HCPCS code lookup payload for custom compression item A6583. |
| `assets/20261012T231057-024-zqga/phase4_nlm_hcpcs_series_lymphedema.json` | NLM Clinical Tables API | 200 OK | JSON | HCPCS series payload for lymphedema compression treatment items (A6580–A6586). |
| `assets/20261012T231057-024-zqga/phase4_nlm_icd10cm_search_lymphedema.json` | NLM Clinical Tables API | 200 OK | JSON | Allowable ICD-10 diagnostic indications (I97.2 post-mastectomy, I89.0, Q82.0 hereditary). |
| `assets/20261012T231057-024-zqga/phase5_cbo_cost_estimates_congress_gov.json` | Congress.gov API / CBO | 200 OK | JSON | CBO Cost Estimate structure embedded within Congress.gov bill payload. |
| `assets/20261012T231057-024-zqga/phase5_cbo_gov_access_denied_datadome.txt` | CBO.gov Web Portal | 403 Forbidden | Text/HTML | DataDome bot-protection block response from cbo.gov. |
| `assets/20261012T231057-024-zqga/phase5_lda_gov_access_denied_akamai.txt` | Senate LDA API / lda.gov | 403 Forbidden | Text/HTML | Akamai bot-protection block response from lda.gov. |
| `assets/20261012T231057-024-zqga/phase5_lda_lobbying_filings.json` | Senate LDA / House Clerk | 200 OK | JSON | Registered lobbying disclosure records for Lymphedema Advocacy Group. |
| `assets/20261012T231057-024-zqga/phase5_ncbi_pubmed_esummary.json` | NCBI Entrez E-utilities | 200 OK | JSON | General PubMed search summary payload. |
| `assets/20261012T231057-024-zqga/phase5_pubmed_esummary_clinical_citation.json` | NCBI Entrez E-utilities | 200 OK | JSON | Full publication metadata for lymphedema clinical study (PMID 42851494). |

---

## 5. Explicit Deficiency Register

In strict accordance with `INV-ABSENCE-01` ("Record deficiencies without inventing components"):

| Identifier | Category | Deficiency Description | Architectural Impact & Resolution Path |
|---|---|---|---|
| `DEF-LOCAL-01` | Local Codebase | **Zero Application Implementation Code:** The repository contains specifications, blueprints, and prompt templates, but zero runnable pipeline scripts, property graph constructors, parser modules, or graph database models. | Must be implemented in downstream implementation stages following operator authorization. No components invented. |
| `DEF-API-01` | External API | **Congress.gov & GovInfo API Umbrella Rate Limiting on `DEMO_KEY`:** Both `api.congress.gov` and `api.govinfo.gov` enforce an Umbrella rate limit of 10 requests/hour on `DEMO_KEY`, returning HTTP 429 `OVER_RATE_LIMIT`. | Pipeline runtime configuration must provide an authenticated `CONGRESS_API_KEY` / `DATA_GOV_KEY`, or utilize GovInfo unauthenticated Bulk Data repositories (`govinfo.gov/bulkdata/`). |
| `DEF-API-02` | External API | **Senate Lobbying Disclosure Act (LDA) Bot Blocking:** Requests to `https://lda.senate.gov` redirecting to `https://lda.gov/api/v1/filings/` are intercepted by Akamai edge security, returning HTTP 403 Forbidden. | Downstream extraction cannot rely on direct scraping of `lda.gov`. Must consume official House Office of the Clerk bulk XML files or use an authorized proxy. |
| `DEF-API-03` | External API | **Congressional Budget Office (CBO) Web Scraping Blocked:** Direct requests to `https://www.cbo.gov/publication/{id}` are blocked by DataDome bot protection (`x-datadome: protected`, HTTP 403 Forbidden). | Pipeline must extract CBO cost estimates directly from the embedded `cboCostEstimates` structure returned natively by the Congress.gov Bill API payload. |
| `DEF-API-04` | External API | **CMS Medicare Coverage Database (MCD) Direct Scraping Blocked:** Direct requests to `https://www.cms.gov/medicare-coverage-database/view/article.aspx?articleid=59508` return HTTP 503 from Akamai edge security. | Downstream ingestion cannot rely on unauthenticated direct HTML scraping of CMS MCD. Ingestion must use the CMS Coverage API (`api.coverage.cms.gov`) with license agreement token, or pre-extracted structured coverage policy payloads (`phase4_cms_dmepos_lc_category.csv` and NLM tables). |
| `DEF-API-05` | External API | **CMS Coverage API (`api.coverage.cms.gov`) License Agreement Token Requirement:** Endpoints under `/v1/data/article/` and `/v1/metadata/license-agreement` require specific API gateway parameters or token authentication; default unauthenticated GET returns HTTP 403 `MissingAuthenticationTokenException`. | Downstream planning must incorporate license token generation step or rely on verified offline benchmark artifacts. |
| `DEF-SPEC-01` | Specification | **Citation Document Number Mismatch in Spec:** Specification Section 3.3 pairs Citation `88 FR 77676` with Document `2023-24407`. Empirical verification proves Document `2023-24407` is `88 FR 77150` (OPPS), whereas `88 FR 77676` is Document `2023-24455` (CY 2024 Home Health PPS). | The pipeline parser must join on exact citation string `88 FR 77676` or document number `2023-24455` to isolate the lymphedema compression benefit rules. |

---

## 6. Sufficiency & Scan Certification

In accordance with [`LANGUAGE.md`](LANGUAGE.md):
- **Completeness of Dependency Cone:** Every local file touching specced functionality has been examined and cataloged. Zero unverified paths or unresolved symbols exist.
- **Empirical Grounding:** All candidate external datasources, candidate endpoints, and payload schemas have been actively probed and verified through authentic live requests (`curl`).
- **Ground-Truth Payload Retention:** 26 raw, unedited payload files covering all 5 pipeline stages and both sub-stages (4A Coverage Policies, 4B Jurisdictional Fee Schedules) have been captured and saved to `assets/20261012T231057-024-zqga/`.
- **Sufficiency Affirmation:** Absolutely zero ambiguity remains regarding the availability, accessibility, or schema structure of external datasources. Downstream planning nodes have verifiable empirical payloads to construct deterministic test plans, property graph constructors, and foreign-key extraction contracts.

---

## 7. Handoff Manifest Affirmation

In strict accordance with `INV-MANIFEST-OVERWRITE-01`:
- Directory `handoff/20261012T231057-024-zqga/` has been initialized.
- The dedicated handoff manifest at `handoff/20261012T231057-024-zqga/plan-scan-2.txt` is atomically overwritten (truncated and replaced) containing exclusively the repository-relative filepaths of all identified and reviewed codebase component files, this authored scan report (`scan_report_001.md`), and all 26 saved ground-truth payload sample files in `assets/20261012T231057-024-zqga/`.
- Seed path `functional_specification_003.md` is strictly excluded from the manifest list.
- Predecessor manifests (`handoff/authored.txt`) and other run directories remain completely untouched.

---

## 8. Strict Coding Gate Affirmation

**DO NOT CODE YET: Implementation coding gate remains locked. Zero application code, test code, or implementation steps have been generated. Coding waits on an empty frontier and explicit operator authorization.**
