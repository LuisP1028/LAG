# Functional Specification: Complete Elimination of Synthetic/Mock Identifiers and Enforcement of 100% Verified Real-World Data Across the Knowledge Graph Pipeline

**Document ID:** `functional_specification_010.md`  
**Status:** Requirements Specification  
**Implementation Guidance:** Strictly Prohibited (DO NOT CODE YET)  
**Taxonomy Reference:** [LANGUAGE.md](file:///Users/diesel/Desktop/LAG/LANGUAGE.md)

---

## 1. Objective and Problem Statement

This specification establishes the functional requirements for identifying, completely purging, and replacing all synthetic, mock, or placeholder values across the policy knowledge graph pipeline, database, GraphRAG retrieval engine, and user visualizer interface. The system must enforce a 100% authentic, real-world federal knowledge graph where every entity node, relationship edge, fee schedule, and external hyperlink corresponds directly to verified, authoritative government records.

### The Problem
During early data reconnaissance and pipeline prototyping, external web probes to CMS's Medicare Coverage Database (MCD) returned HTTP 404/503 errors because the database is hosted behind an ASP.NET client-side single-page application without an open unauthenticated REST API. Instead of halting execution under the system's strict fail-fast invariant (`RULE[user_global]`, `INV-FAIL-FAST`), the pipeline incorporated synthetic/mock values:
1. **Fictitious Coverage Policy Identifiers:** The pipeline hardcoded non-existent CMS article identifiers—specifically `A59508` (for Lymphedema / `LTA`) and `A59588` (for Intravenous Immune Globulin / `IVIG`)—into regulatory directives and coverage nodes.
2. **Dead Hyperlinks:** When users view the `CoveragePolicy` node details in the frontend visualizer and click the external reference link, the browser is directed to `https://www.cms.gov/medicare-coverage-database/search-results.aspx?keyword=A59508`, which returns `"Total Results: 0"`.
3. **Static Clinical Arrays:** Covered diagnosis codes (`STANDARD_COVERED_DIAGNOSES`: `I89.0`, `I97.2`, `Q82.0`) were defined as static Python tuples in code rather than verified against official CMS change request transmittals and published LCD/article tables.
4. **Keyword Branching Fallbacks:** Policy discovery relied on static keyword checks (`if clean_kw == "LTA"`) with hardcoded bill numbers rather than authoritative discovery from primary federal registries.

### The Desired Solution
The system must be cleansed of all synthetic, mock, or placeholder artifacts:
1. **Zero Mock Values in Database:** 100% of nodes in Neo4j must represent verified real-world statutory, regulatory, administrative, and clinical entities.
2. **Authoritative Real-World Identifiers:**
   * **For Lymphedema (`LTA`):** Replace fictitious `A59508` with the authoritative CMS/DME MAC coverage and documentation policy:
     * Authoritative Article: **`Article A55426`** (*Standard Documentation Requirements for All Claims Submitted to DME MACs*), or the official CMS Statutory Benefit Policy Portal (`https://www.cms.gov/medicare/payment/fee-schedules/dmepos/lymphedema-compression-treatment-items`).
   * **For IVIG (`IVIG`):** Replace fictitious `A59588` with the verified CMS Medicare Coverage Database Policy Article:
     * Authoritative Article: **`Article A52509`** (*Intravenous Immune Globulin*), governing home IVIG under Medicare Part B (HCPCS `Q2052`).
3. **Live Working External Links:** Every external URL surfaced in node detail drawers must resolve to a valid, live 200 OK government endpoint that displays real policy text, never a zero-result search page.
4. **Authentic Diagnostic & Procedural Linkage:** All ICD-10 diagnostic indications and HCPCS procedure codes must originate from verified federal datasets (CMS DMEPOS Fee Schedule CSV and CMS Change Request directives).
5. **Strict Fail-Fast Enforcement:** In strict accordance with `RULE[user_global]`, if any required downstream foreign key or external entity cannot be resolved against authoritative sources, the pipeline must raise a fatal error (`{errors}`) immediately; synthetic fallbacks and mock data injection are strictly forbidden.

---

## 2. Taxonomy and Evaluation Parameters

All evaluations must adhere strictly to [LANGUAGE.md](file:///Users/diesel/Desktop/LAG/LANGUAGE.md):

* **`{errors}`:** Any occurrence of synthetic, placeholder, or fictitious identifiers (e.g., `A59508`, `A59588`); broken external URLs; 0-result search pages; silent exception handlers; or fallback defaults injecting unverified entities.
* **`{correctness}`:** Every primary key, property, foreign key, and URL corresponds 1-to-1 with verified federal statutory, regulatory, administrative, and clinical datasets.
* **`{functionality}`:** An end-to-end, multi-tier knowledge graph where all entities, relationships, fee schedules, and contextual citations represent 100% verified real-world facts with zero mock values.
* **`{correct required outputs}`:**
  1. Complete removal of `A59508` and `A59588` from all database nodes, models, prompts, linkers, and UI components.
  2. Ingestion and linking of verified real-world coverage policy articles (`A55426` for LTA documentation, `A52509` for IVIG).
  3. External drawer links that open live, authentic CMS policy documentation.
  4. 100% edge provenance traceability back to authoritative federal source files and endpoints.
  5. Immediate fatal halt (`INV-FAIL-FAST`) upon encountering unresolvable entities or unsupported keywords.
* **`{sufficient}`:** Complete specification of real-world data sources, entity replacements, validation rules, and acceptance criteria without implementation code.
* **`{insufficient}`:** Any ambiguity regarding which entities are mock, what real-world sources are authoritative, or how data integrity must be verified.

---

## 3. Comparison: Current Functionality vs. Desired Functionality

| Feature Area | Current Functionality | Desired Functionality |
| :--- | :--- | :--- |
| **Coverage Policy ID (LTA)** | **Mock/Fictitious:** Hardcoded as `A59508` (`CMS-MCD-A59508`), which does not exist in the CMS Medicare Coverage Database. | **Authoritative Real-World:** Governed by DME MAC Policy Article `A55426` (`CMS-MCD-A55426`: *Standard Documentation Requirements for All Claims Submitted to DME MACs*) and the official CMS Statutory Benefit Policy. |
| **Coverage Policy ID (IVIG)** | **Mock/Fictitious:** Hardcoded as `A59588` (`CMS-MCD-A59588`), which does not exist on CMS.gov. | **Authoritative Real-World:** Governed by CMS MCD Policy Article `A52509` (`CMS-MCD-A52509`: *Intravenous Immune Globulin*), which authoritatively governs home IVIG under HCPCS `Q2052`. |
| **External Source URLs** | **Dead Ends:** Point to `search-results.aspx?keyword=A59508` or non-existent article detail pages, yielding HTTP 404 or `"Total Results: 0"`. | **Live & Direct:** Directs users to verified, active CMS documentation pages (e.g. `https://www.cms.gov/medicare-coverage-database/view/article.aspx?articleid=52509` or official CMS DMEPOS benefit policy URLs) returning HTTP 200 with authentic policy text. |
| **Allowable Diagnoses Sourcing** | **Static Fallback:** Sourced from a hardcoded Python array (`STANDARD_COVERED_DIAGNOSES`). | **Authoritative Extraction:** Sourced and verified directly against CMS Change Request directives (CR 13286 / Transmittal R12471CP) and official ICD-10-CM clinical tables. |
| **GraphRAG Entity Linker & Prompts** | Prompts and linking heuristics expect and cite `[CMS-MCD-A59508]`. | Entity linkers and system prompts strictly expect and cite verified real-world primary keys (e.g., `[CMS-MCD-A55426]`, `[CMS-MCD-A52509]`). |
| **Pipeline Invariant Enforcement** | **Silent Mock Injection:** When external scraping fails, mock values are injected to allow downstream graph generation and tests to pass. | **Strict Fail-Fast (`INV-FAIL-FAST`):** If an authoritative payload or document cannot be fetched or verified, execution immediately terminates with structured error telemetry. |
| **Data Integrity Standard** | Partial (~95% real data, but contaminated by mock coverage bridge nodes). | **100% Real-World Data:** Absolute zero tolerance for placeholder, dummy, synthetic, or unverified data in any tier. |

---

## 4. Functional Requirements

### 4.1. Complete Purge of Synthetic Identifiers
1. **Target Identifiers for Complete Removal:**
   * `A59508` and `CMS-MCD-A59508`
   * `A59588` and `CMS-MCD-A59588`
   * Fictitious source paths: `https://www.cms.gov/medicare-coverage-database/view/article.aspx?articleid=59508` and `...articleid=59588`
2. **Purge Scope:**
   * The purge must encompass database records (Neo4j vertices and edges), graph ingestion models, GraphRAG entity linkers, context assemblers, synthesizer system prompts, sample query lists, and frontend component link builders.

---

### 4.2. Authoritative Real-World Entity Substitution

#### 4.2.1. Lymphedema Treatment Act Policy (`LTA`)
* **Authoritative Policy Artifact:**
  * **Document Type:** Joint DME MAC Policy Article & CMS DMEPOS Statutory Coverage Policy.
  * **Authoritative Identifier:** `A55426` (Primary Key: `CMS-MCD-A55426`).
  * **Official Title:** *Standard Documentation Requirements for All Claims Submitted to DME MACs*.
  * **Statutory Implementation Portal:** `https://www.cms.gov/medicare/payment/fee-schedules/dmepos/lymphedema-compression-treatment-items`.
  * **Governing Transmittals:** CMS Change Request 13286 (Transmittal 12349 / R12471CP) and CR 13670 (Transmittal R12725OTN).
* **Coverage Relationships:**
  * `(ChangeRequest:CMS-CR-13286)-[:MANDATES_POLICY]->(CoveragePolicy:CMS-MCD-A55426)`
  * `(CoveragePolicy:CMS-MCD-A55426)-[:GOVERNS]->(HCPCSCode:HCPCS-A6520 through HCPCS-A6589)`
  * `(CoveragePolicy:CMS-MCD-A55426)-[:ALLOWS_DIAGNOSIS]->(ICD10Code:ICD10-I89.0, ICD10-I97.2, ICD10-Q82.0)`

#### 4.2.2. Intravenous Immune Globulin Benefit (`IVIG`)
* **Authoritative Policy Artifact:**
  * **Document Type:** CMS Medicare Coverage Database Joint DME MAC Policy Article.
  * **Authoritative Identifier:** `A52509` (Primary Key: `CMS-MCD-A52509`).
  * **Official Title:** *Billing and Coding: Intravenous Immune Globulin*.
  * **Official CMS MCD URL:** `https://www.cms.gov/medicare-coverage-database/view/article.aspx?articleid=52509`.
  * **Governing Transmittal:** CMS Change Request 13217 (Transmittal 12437).
* **Coverage Relationships:**
  * `(ChangeRequest:CMS-CR-13217)-[:MANDATES_POLICY]->(CoveragePolicy:CMS-MCD-A52509)`
  * `(CoveragePolicy:CMS-MCD-A52509)-[:GOVERNS]->(HCPCSCode:HCPCS-Q2052, HCPCS-J1459, HCPCS-J1561, HCPCS-J1568, HCPCS-J1569)`
  * `(CoveragePolicy:CMS-MCD-A52509)-[:ALLOWS_DIAGNOSIS]->(ICD10Code:ICD10-D80.0, ICD10-D81.9, ICD10-D83.9)`

---

### 4.3. Authoritative Clinical and Procedural Data Requirements
1. **Procedure Codes (`HCPCSCode`):**
   * Must originate directly from the official CMS DMEPOS Fee Schedule dataset (`phase4_cms_dmepos_lc_category.csv` where `CATG == "LC"`).
   * Every procedure code must include its verified CMS description, operational category, and pricing indicator (`40`).
2. **Diagnostic Codes (`ICD10Code`):**
   * Must reflect authentic ICD-10-CM codes authorized under CMS Change Request directives for lymphedema and primary immunodeficiency:
     * `I89.0`: *Lymphedema, not elsewhere classified*
     * `I97.2`: *Postmastectomy lymphedema syndrome*
     * `Q82.0`: *Hereditary lymphedema*
     * `D80.0`: *Hereditary hypogammaglobulinemia*
     * `D81.9`: *Severe combined immunodeficiency, unspecified*
     * `D83.9`: *Common variable immunodeficiency, unspecified*
   * Must include verified clinical descriptions from the National Library of Medicine (NLM) clinical tables.

---

### 4.4. External Hyperlink Integrity
1. **Direct Navigation:**
   * External links displayed in the `NodeDetailDrawer` must lead users directly to verified, operational pages on `cms.gov`, `congress.gov`, `govinfo.gov`, or `pubmed.ncbi.nlm.nih.gov`.
2. **Coverage Policy External Links:**
   * For `CoveragePolicy` nodes with valid article IDs (e.g. `A55426`, `A52509`), the link must point to:
     `https://www.cms.gov/medicare-coverage-database/view/article.aspx?articleid={numeric_article_id}` or the verified CMS MCD search endpoint that returns active, verified policy text.
   * For general statutory policy landing pages, the link must point to the official CMS benefit overview page (`https://www.cms.gov/medicare/payment/fee-schedules/dmepos/lymphedema-compression-treatment-items`).
3. **HTTP Status & Content Validation:**
   * Links must not return HTTP 404, HTTP 503, or `"Total Results: 0"` search outcomes.

---

### 4.5. GraphRAG Traversal and Prompt Realignment
1. **Entity Linking:**
   * The `EntityAnchorLinker` must resolve inquiries about "coverage policy", "article", or specific document numbers to the real-world primary keys (`CMS-MCD-A55426`, `CMS-MCD-A52509`).
2. **Sample Questions in UI:**
   * Sample prompt pills in `GraphSyncContext.tsx` and `AgentChatDrawer.tsx` must be updated:
     * *Current (Mock):* `"What diagnoses are approved under CMS MCD A59508?"`
     * *Desired (Real):* `"What diagnoses are approved under CMS MCD A55426 for Lymphedema?"`
3. **Synthesizer System Prompts:**
   * System instruction templates in `synthesizer.py` must cite `[CMS-MCD-A55426]` and `[CMS-MCD-A52509]` as exemplar bracketed identifiers instead of `[CMS-MCD-A59508]`.

---

### 4.6. Strict Invariant and Fail-Fast Enforcement (`INV-ZERO-MOCK-DATA`)
1. **Prohibition of Synthetic Fallbacks:**
   * The pipeline is strictly prohibited from catching data fetch exceptions and substituting hardcoded mock IDs, fake titles, or simulated URLs (`RULE[user_global]`).
2. **Immediate Fatal Termination:**
   * If a required regulatory document, coverage article, or fee schedule cannot be resolved against authoritative files or endpoints, the pipeline must raise an explicit domain exception (e.g., `Phase4ArticleFetchError`) and halt execution immediately.
3. **Zero-Mock Verification Oracle:**
   * A post-ingestion validation oracle must scan all nodes and edges in Neo4j. If any node contains `A59508`, `A59588`, the word `"mock"`, or an unresolvable URL, the entire graph build is invalidated.

---

## 5. Master Real-World Entity Register

Every node in the final graph must map to an authoritative, verifiable real-world federal artifact:

| Entity Type | Real-World Federal Artifact | Authoritative Primary Key | Source Dataset / Authority |
| :--- | :--- | :--- | :--- |
| **`Policy`** | Legislative/Regulatory Policy Topic | `POLICY-LTA`, `POLICY-IVIG` | Runtime Input Parameter |
| **`Bill`** | Standalone Bill & Enacting Omnibus | `BILL-117-hr-3630`, `BILL-117-hr-2617`, `BILL-117-hr-3808` | Congress.gov REST API v3 / GPO GovInfo |
| **`PublicLaw`** | Enacted Federal Statute | `PLAW-117-328` | GPO GovInfo USLM XML (`PLAW-117publ328.xml`) |
| **`StatutorySection`** | Codified U.S. Code Amendment | `USC-42-1395x-s-2-JJ`, `USC-42-1395x-s-2-Z` | Office of Law Revision Counsel / USLM Section 4133 & 4134 |
| **`Regulation`** | Federal Register Final Rule | `FR-2023-24455` (88 FR 77676) | Federal Register API v1 / National Archives |
| **`ChangeRequest`** | CMS Operational Directive | `CMS-CR-13286`, `CMS-CR-13217` | CMS Transmittals Portal (Transmittals 12349, 12437) |
| **`CoveragePolicy`** | DME MAC Documentation Article | `CMS-MCD-A55426`, `CMS-MCD-A52509` | CMS Medicare Coverage Database / DME MAC Policy Articles |
| **`Jurisdiction`** | DME MAC Regional Contractor | `JURIS-DME-A`, `B`, `C`, `D` | CMS MAC Regional Allocation Rules (Noridian & CGS) |
| **`State`** | U.S. States and Territories | `STATE-AL` through `STATE-WY` (54 Jurisdictions) | CMS DMEPOS Geographic Split Definitions |
| **`FeeScheduleEntry`** | State Reimbursement Allowance | `FEE-{hcpcs}-{state}-{rural/nr}-2024` | CMS DMEPOS Fee Schedule CSV (`CATG == 'LC'`) |
| **`HCPCSCode`** | Medical Procedure Code | `HCPCS-A6520` through `HCPCS-A6589`, `HCPCS-Q2052` | CMS Alpha-Numeric HCPCS Master File / DMEPOS CSV |
| **`ICD10Code`** | Clinical Diagnosis Code | `ICD10-I89.0`, `ICD10-I97.2`, `ICD10-Q82.0` | WHO / CDC ICD-10-CM & CMS Coverage Directives |
| **`LobbyingFiling`** | Congressional Lobbying Disclosure | `LDA-{filing_uuid}` | Senate Office of Public Records (SOPR) / LDA API |
| **`CBOScore`** | 10-Year Scorekeeping Estimate | `CBO-SCORE-HR2617-PL117-328` | Congressional Budget Office Cost Estimates Database |
| **`LiteratureStudy`** | Peer-Reviewed Clinical Trial | `PUBMED-31454178`, `PUBMED-27549490` | National Library of Medicine (NCBI PubMed E-Utilities) |

---

## 6. Edge Cases and Operational Constraints

1. **CMS MCD Client-Side App Scraping Protection:**
   * Because CMS.gov blocks raw automated crawlers and uses client-side rendering for MCD articles, the pipeline must ingest pre-captured, verified federal article payloads from `assets/` rather than attempting brittle live scraping that fails and triggers fallback mocks.
2. **Dual-Jurisdiction Fee Parity:**
   * Rural (`R`) and Non-Rural (`NR`) pricing columns in the CMS DMEPOS CSV must both be extracted for every state without assuming uniform rates.
3. **Statutory vs. National Coverage Disambiguation:**
   * Lymphedema treatment items are a statutory benefit created by Congress under CAA 2023, not an administrative National Coverage Determination (NCD). External documentation and links must reflect this statutory/DME MAC policy governance.

---

## 7. Acceptance and Verification Criteria

The implementation will be certified as complete and verified only when all of the following empirical criteria are satisfied:

1. **Zero Mock Scan:** A codebase-wide and database-wide grep for `A59508`, `A59588`, `59508`, and `59588` returns exactly zero matches in active code, graph vertices, and database indices.
2. **Real Policy Node Presence:**
   * For `POLICY-LTA`, the graph contains a `CoveragePolicy` node with primary key `CMS-MCD-A55426`.
   * For `POLICY-IVIG`, the graph contains a `CoveragePolicy` node with primary key `CMS-MCD-A52509`.
3. **External Link Validity:**
   * Clicking the `CMS Medicare Coverage Database` link in the frontend `NodeDetailDrawer` opens an active CMS page displaying verified documentation content, with zero occurrences of `"Total Results: 0"` or HTTP 404 errors.
4. **GraphRAG Prompt and Traversal Alignment:**
   * Inquiring about *"What diagnoses are approved under CMS MCD A55426?"* correctly anchors to the real policy node, retrieves the connected ICD-10 nodes (`I89.0`, `I97.2`, `Q82.0`), illuminates the path on the canvas, and quotes `[CMS-MCD-A55426]` in the synthesized answer.
5. **Fail-Fast Compliance:**
   * Running the pipeline with an unknown policy keyword (e.g., `POLICY-UNKNOWN`) immediately raises a fatal `Phase1DiscoveryError` without writing default or mock nodes to the database.
6. **All Integration Tests Green:**
   * Existing test suites (`tests/test_graph_pipeline.py`, `tests/test_graphrag_pipeline.py`, `tests/test_api_endpoints.py`) pass with 100% real-world entity validation.
