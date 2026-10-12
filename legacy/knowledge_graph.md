# System Architecture & Technical Specification: Lymphedema Treatment Act Knowledge Graph

This specification outlines the architecture, data models, extraction pipelines, and traversal patterns for constructing a deterministic Knowledge Graph (KG) of the **Lymphedema Treatment Act (LTA)** to serve as a grounded retrieval backend for an LLM chatbot.

---

## 1. System Architecture Overview

The knowledge graph models the complete **Policy-to-Adjudication Lifecycle**. Medical coverage does not originate in isolation; it flows across four interconnected layers where each upstream tier establishes the legal or evidentiary authority for the downstream tier.

```
┌────────────────────────────────────────────────────────────────────────┐
│  LAYER 4: Advocacy, Economics & Evidence                               │
│  (Lobbying Disclosures, CBO Cost Estimates, Clinical Literature)       │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ (Advocates for / Justifies)
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│  LAYER 1: Statutory & Legislative Origins                              │
│  (Bills H.R. 3630/H.R. 2617 ──► Public Law 117-328, Sec. 4133)         │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ (Amends / Enacts into Title 42)
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│  LAYER 2: Administrative & Regulatory Execution                        │
│  (CMS-1780-F ──► 42 CFR 410/414 ──► CR 13286 / Transmittal R12471CP)  │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ (Defines / Restricts / Mandates)
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│  LAYER 3: Medical Coding, Adjudication & Pricing                       │
│  (HCPCS A-Codes ──► ICD-10 Indications ──► DMEPOS Fee Schedules)       │
└────────────────────────────────────────────────────────────────────────┘

```

The coding assistant must construct an ETL pipeline that treats data extraction as a **linked list of foreign keys**, eliminating keyword-based web scraping in favor of deterministic API and XML queries.

---

## 2. Graph Ontology (Entity-Relationship Model)

### 2.1 Node Definitions

| Node Label | Core Properties | Primary Data Source |
| --- | --- | --- |
| `Bill` | `bill_id`, `congress`, `type`, `number`, `title`, `introduced_date`, `status` | Congress.gov API (`/bill`) |
| `PublicLaw` | `law_id`, `congress`, `law_number`, `enacted_date`, `title` | GovInfo API (`PLAW` collection) |
| `StatutorySection` | `section_id`, `division`, `title_number`, `section_number`, `heading`, `raw_text` | GovInfo USLM XML |
| `USCodeSection` | `citation`, `title`, `section`, `subparagraph`, `name` | US Code (OLRC / GovInfo) |
| `FederalRule` | `docket_id`, `rin`, `citation_fr`, `title`, `publication_date`, `effective_date` | Federal Register API |
| `CFRSection` | `citation`, `title`, `part`, `section`, `heading` | eCFR API |
| `ChangeRequest` | `cr_number`, `transmittal_number`, `title`, `release_date`, `effective_date` | CMS Transmittals Portal |
| `PolicyArticle` | `article_id`, `title`, `contractor`, `jurisdiction`, `revised_date` | CMS Medicare Coverage DB |
| `HCPCSCode` | `code`, `short_desc`, `long_desc`, `betos`, `pricing_indicator`, `is_custom` | CMS Alpha-Numeric HCPCS |
| `ICD10Code` | `code`, `short_desc`, `long_desc`, `category`, `is_covered` | CDC / CMS ICD-10-CM |
| `FrequencyLimit` | `limit_id`, `item_category`, `max_quantity`, `timeframe_months`, `requires_modifier` | 42 CFR / CR 13286 |
| `FeeSchedule` | `hcpcs_code`, `state`, `floor_rate`, `ceiling_rate`, `year` | CMS DMEPOS Fee Schedule |
| `AdvocacyEntity` | `entity_name`, `entity_type`, `founder`, `lobbying_firm` | Senate LDA Database |
| `ClinicalStudy` | `pmid`, `title`, `authors`, `journal`, `publication_year`, `compression_class` | NCBI PubMed E-utilities |
| `EconomicEstimate` | `report_id`, `agency`, `release_date`, `ten_year_cost_projection` | CBO Catalog |

---

### 2.2 Edge (Relationship) Definitions

| Source Node | Edge Label | Target Node | Edge Attributes | Description |
| --- | --- | --- | --- | --- |
| `Bill` | `PRECEDES` | `Bill` | `session_gap` | Connects historical iterations (111th through 117th Congress). |
| `Bill` | `INCORPORATED_INTO` | `Bill` | `relationship_type` | H.R. 3630 merged into the omnibus vehicle H.R. 2617. |
| `Bill` | `ENACTED_AS` | `PublicLaw` | `approval_date` | H.R. 2617 enacted as Public Law 117-328. |
| `PublicLaw` | `HAS_SECTION` | `StatutorySection` | `division`, `title` | Pinpoints Division FF, Title IV, Section 4133. |
| `StatutorySection` | `AMENDS` | `USCodeSection` | `subparagraph`, `action` | Section 4133 inserts 42 U.S.C. §§ 1395x(s)(2)(JJ) and 1395m(z). |
| `FederalRule` | `IMPLEMENTS` | `USCodeSection` | `regulatory_authority` | CMS-1780-F cites 42 U.S.C. § 1395m(z) as rulemaking mandate. |
| `FederalRule` | `AMENDS_CFR` | `CFRSection` | `amendment_type` | Promulgates changes to 42 CFR §§ 410.36 and 414.214. |
| `FederalRule` | `ISSUES_ORDER` | `ChangeRequest` | `policy_scope` | CMS issues CR 13286 to instruct automated claims engines. |
| `ChangeRequest` | `DIRECTS_POLICY` | `PolicyArticle` | `contractor_type` | Instructs DME MACs to publish local billing guidance. |
| `ChangeRequest` | `ESTABLISHES_CODE` | `HCPCSCode` | `pricing_ind`, `betos` | Activates HCPCS codes A6520–A6608 with BETOS `O1L`. |
| `ChangeRequest` | `ENFORCES_LIMIT` | `FrequencyLimit` | `enforcement_level` | Defines 3 daytime per 6 mos / 2 nighttime per 2 yrs. |
| `HCPCSCode` | `REQUIRES_DIAGNOSIS` | `ICD10Code` | `claim_edit_action` | Automated rejection if diagnosis code is missing. |
| `HCPCSCode` | `HAS_PRICING` | `FeeSchedule` | `jurisdiction` | Links state floor and ceiling payment amounts. |
| `AdvocacyEntity` | `LOBBIED_FOR` | `Bill` | `total_spend`, `filing_id` | Tracks lobbying registrations targeting H.R. 3630. |
| `ClinicalStudy` | `CITED_BY` | `FederalRule` | `footnote_index` | Captures peer-reviewed trials cited in CMS-1780-F preamble. |
| `EconomicEstimate` | `EVALUATES` | `Bill` | `committee` | Links official CBO scorecard to H.R. 3630. |

---

## 3. Ingestion & Discovery Pipeline Specification

The data extraction pipeline operates across five sequential stages. A failure or missing key in an upstream stage must halt that branch of the ingestion graph.

```
       [Stage 1: Congress.gov API]
                   │
                   ▼ (Outputs: P.L. 117-328, Bill IDs)
       [Stage 2: GovInfo USLM XML]
                   │
                   ▼ (Outputs: Section 4133 -> 42 U.S.C. §§ 1395x & 1395m)
       [Stage 3: Federal Register & CMS Engine]
                   │
                   ▼ (Outputs: CMS-1780-F, CR 13286, 42 CFR 410/414)
       [Stage 4: Coding, Pricing & Coverage Index]
                   │
                   ▼ (Outputs: HCPCS A6520-A6608, ICD-10, Fee Schedules)
       [Stage 5: Evidentiary Cross-Referencing]
                   │
                   ▼ (Outputs: PMIDs, CBO Reports, LDA Filings)

```

### 3.1 Stage 1: Legislative Lineage Pipeline

* **Target API:** Congress.gov REST API v3.
* **Endpoint:** `/v3/bill` and `/v3/bill/{congress}/{type}/{number}/relatedbills`.
* **Discovery Protocol:**
1. Query `/bill` with query string `"Lymphedema Treatment Act"` across sessions 111 through 117.
2. Extract historical bill IDs: H.R. 4662 (111th), H.R. 2499 / S. 1362 (112th), H.R. 3877 / S. 1315 (113th), H.R. 1608 / S. 1459 (114th), H.R. 930 / S. 497 (115th), H.R. 1948 / S. 518 (116th), and H.R. 3630 / S. 1315 (117th).
3. Link successive bills chronologically via `PRECEDES` edges.
4. Call `/bill/117/hr/3630/relatedbills` and parse JSON payload for the CRS relation:
* Match `bill.number == 2617` where `relationshipDetails.type == "Related bill"`.
* Create edge: `(:Bill {bill_id: "117-HR3630"}) -[:INCORPORATED_INTO]-> (:Bill {bill_id: "117-HR2617"})`.


5. Call `/bill/117/hr/2617/actions` to locate the final approval action, yielding the public law identifier: `Public Law 117-328`.



### 3.2 Stage 2: Statutory Codification Delta Pipeline

* **Target API:** GovInfo Bulk Data & Package API (`govinfo.gov`).
* **Endpoint:** `/packages/PLAW-117publ328/xml`.
* **Discovery Protocol:**
1. Stream and parse the USLM XML tree for `PLAW-117publ328`.
2. Execute XPath filter: `//section[contains(translate(., 'LYMPHEDEMA', 'lymphedema'), 'lymphedema')]`.
3. Isolate node: `<section identifier="/us/pl/117/328/dFF/tIV/s4133">` (**Division FF, Title IV, Section 4133**).
4. Parse inner amending text and extract statutory targets:
* Patch 1: Identifies Section 1861(s)(2) of the Social Security Act $\rightarrow$ extracts addition of subparagraph `(JJ)`, mapped to **42 U.S.C. § 1395x(s)(2)(JJ)**.
* Patch 2: Identifies Section 1834 of the Social Security Act $\rightarrow$ extracts addition of subsection `(z)`, mapped to **42 U.S.C. § 1395m(z)**.
* Patch 3: Extracts effective date string: `"January 1, 2024"`.


5. Upsert `StatutorySection` and `USCodeSection` nodes; create `AMENDS` edges storing the delta parameters.



### 3.3 Stage 3: Regulatory & Operational Administrative Pipeline

* **Target APIs:** Federal Register REST API (`federalregister.gov/api/v1/`) and CMS Transmittals Index.
* **Discovery Protocol:**
1. Search Federal Register API using the statutory anchors from Stage 2:
* Parameters: `conditions[cfr][title]=42`, `conditions[term]="1395m(z)"`, `conditions[agency_slugs][]=centers-for-medicare-medicaid-services`.


2. Return and parse Final Rule: **CMS-1780-F** (Docket Number: CMS-1780-F; 88 FR 77676; RIN 0938-AV03; Title: *Calendar Year 2024 Home Health Prospective Payment System Rate Update...*).
3. Extract CFR codification changes from rule text:
* **42 CFR § 410.36:** Medical supplies covered under Part B.
* **42 CFR § 414.214:** Payment rules and replacement intervals for lymphedema compression treatment items.


4. Query CMS Change Request index for docket `CMS-1780-F` and keyword `"Lymphedema"`:
* Extract **CR 13286 / Transmittal R12471CP** (*Implementation of New Benefit Category for Lymphedema Compression Treatment Items*).
* Extract **CR 13670 / Transmittal R12725OTN** (*CWF Edits to Prevent Duplicate Payments*).
* Extract **MLN Matters MM13286**.


5. Extract operational constants from Transmittal 12471:
* `HCPCS Pricing Indicator = "40"`
* `BETOS Code = "O1L"`
* `Type of Service (TOS) = "S"`
* `CWF Category = "60"`


6. Construct `FrequencyLimit` nodes:
* Daytime: `max_quantity: 3`, `unit: "per affected body part"`, `interval_months: 6`.
* Nighttime: `max_quantity: 2`, `unit: "per affected body part"`, `interval_months: 24`.
* Bandaging: `max_quantity: null`, `limit_type: "as clinically indicated"`.
* Replacement Override: Requires billing modifier `RA` + medical necessity documentation proving physical change, theft, or irreparable damage.





### 3.4 Stage 4: Medical Coding, Pricing, & Coverage Pipeline

* **Target Datasets:** CMS Alpha-Numeric HCPCS quarterly files, CMS DMEPOS Fee Schedule, and DME MAC Coverage Database.
* **Discovery Protocol:**
1. Ingest CMS Alpha-Numeric master file; filter records where `BETOS == 'O1L'` or `Pricing Indicator == '40'`.
2. Populate `HCPCSCode` nodes across functional categories:
* *Custom Daytime Garments:* `A6515`–`A6518`, `A6520`–`A6529`, `A6553`, `A6555`, `A6556`–`A6564`, `A6574`, `A6576`–`A6577`.
* *Standard Daytime Garments:* `A6530`–`A6541`, `A6552`, `A6554`, `A6578`, `A6583`.
* *Nighttime Garments:* `A6593`–`A6597`, `A6520`.
* *Bandaging & Supplies:* `A6448`–`A6455`, `A6594`–`A6608`.


3. Ingest Joint DME MAC Policy Article: *Lymphedema Compression Treatment Items - Correct Coding and Billing* (e.g., Article A59508 / A59512).
4. Extract mandatory diagnostic edits; link each `HCPCSCode` via `REQUIRES_DIAGNOSIS` to `ICD10Code`:
* `I89.0` (Lymphedema, not elsewhere classified)
* `I97.2` (Postmastectomy lymphedema syndrome)
* `I97.89` (Other postprocedural circulatory disorders)
* `Q82.0` (Hereditary lymphedema)


5. Ingest CMS DMEPOS Fee Schedule text release:
* Filter lines matching codes `A6520` through `A6608`.
* Extract state-specific rural and non-rural payment amounts; create `FeeSchedule` nodes linked via `HAS_PRICING`.





### 3.5 Stage 5: Evidentiary, Economic, & Advocacy Pipeline

* **Target Datasets:** Senate LDA API (`lda.senate.gov`), CBO Reports Archive, and NCBI Entrez API (`eutils.ncbi.nlm.nih.gov`).
* **Discovery Protocol:**
1. **Advocacy Extraction:**
* Query Senate LDA API endpoint `/filings` for `bill_id == "H.R. 3630"` and `issue == "HCR"`.
* Ingest filings for *Lymphedema Advocacy Group* (founded by Heather Ferguson); parse expenditure metrics and target congressional committees.
* Create edge: `(:AdvocacyEntity {name: "Lymphedema Advocacy Group"}) -[:LOBBIED_FOR]-> (:Bill {bill_id: "117-HR3630"})`.


2. **Economic Extraction:**
* Retrieve CBO Cost Estimate for H.R. 3630 (September 2022).
* Parse 10-year direct federal expenditure projections and hospital offset metrics.
* Create edge: `(:EconomicEstimate {report_id: "hr3630-cbo-2022"}) -[:EVALUATES]-> (:Bill {bill_id: "117-HR3630"})`.


3. **Clinical Evidentiary Extraction:**
* Parse bibliographic citations from the preamble of Final Rule CMS-1780-F (Section III, *Scope of Benefit and Compression Gradient Definitions*).
* Extract PubMed IDs (PMIDs) for consensus standards (e.g., International Society of Lymphology consensus on Complete Decongestive Therapy) and compression gradient efficacy studies.
* Fetch study metadata using NCBI Entrez API `/esummary.fcgi?db=pubmed`.
* Create edge: `(:ClinicalStudy {pmid: "..."}) -[:CITED_BY]-> (:FederalRule {docket_id: "CMS-1780-F"})`.





---

## 4. Graph Traversal & Query Resolution Architecture

The graph supports multi-hop Cypher queries that trace clinical scenarios down to regulatory caps and up to statutory origins without full-text document hallucination.

### 4.1 Traversal Pattern: Clinical Benefit & Adjudication Limits

*Goal:* Determine if a specific garment is covered for a specific clinical condition, extract the exact billing code, determine how many items are permitted, and retrieve the governing legal citation.

```
[User Clinical Condition: "Breast Cancer Arm Swelling"]
                      │ (Entity Resolution)
                      ▼
            [ICD-10 Node: I97.2]
                      │
                      ▼ (INCOMING: REQUIRES_DIAGNOSIS)
          [HCPCS Code Node: A6576 / A6577]
                      │
                      ├─────────────────────────────────────────┐
                      ▼ (OUTGOING: HAS_LIMIT)                   ▼ (INCOMING: ESTABLISHES_CODE)
         [FrequencyLimit Node]                        [ChangeRequest Node: CR 13286]
        (3 daytime / 6 months)                                  │
                      │                                         ▼ (INCOMING: ISSUES_ORDER)
                      ▼ (DERIVED_FROM)                [FederalRule Node: CMS-1780-F]
           [CFR Section: 414.214]                               │
                      │                                         ▼ (OUTGOING: IMPLEMENTS)
                      └───────────────────────────────► [USCodeSection: 42 U.S.C. § 1395m(z)]
                                                                │ (INCOMING: AMENDS)
                                                      [StatutorySection: Sec. 4133]
                                                                │ (INCOMING: HAS_SECTION)
                                                      [PublicLaw: P.L. 117-328]

```

#### Traversal Step Sequence:

1. **Entity Resolution:** The user's clinical prompt maps to `(:ICD10Code {code: "I97.2"})`.
2. **Reverse Code Lookup:** Traverse `(:ICD10Code)<-[:REQUIRES_DIAGNOSIS]-(h:HCPCSCode)` to find matching daytime arm sleeves (`A6576` / `A6577`).
3. **Limit Resolution:** Traverse `(h)-[:ENFORCES_LIMIT]->(fl:FrequencyLimit)` to extract the maximum quantity (3 per 6 months) and modifier rule (`RA` required for early replacement).
4. **Authority Verification:** Traverse `(h)<-[:ESTABLISHES_CODE]-(cr:ChangeRequest)<-[:ISSUES_ORDER]-(fr:FederalRule)-[:IMPLEMENTS]->(usc:USCodeSection)<-[:AMENDS]-(ss:StatutorySection)<-[:HAS_SECTION]-(pl:PublicLaw)`.
5. **Context Assembly:** The LLM receives a structured subgraph containing:
* Billing Code: `A6576` / `A6577`
* Allowable Cap: 3 garments per 6 months per affected arm
* Regulatory Authority: 42 CFR § 414.214 / CMS-1780-F
* Statutory Authority: Section 4133 of Public Law 117-328 (42 U.S.C. § 1395m(z)).



---

### 4.2 Traversal Pattern: Policy & Legislative Origin

*Goal:* Explain why a specific rule exists, who lobbied for it, and the economic justification accepted by Congress.

```
[User Query: "Why did Congress pass the LTA and what was the projected cost?"]
                               │
                               ▼
                   [Bill Node: 117-HR3630]
                               │
            ┌──────────────────┴──────────────────┐
            ▼ (INCOMING: LOBBIED_FOR)             ▼ (INCOMING: EVALUATES)
 [AdvocacyEntity: LAG]                 [EconomicEstimate: CBO-2022]
 (Expenditures, Filings)               (10-Year Spending & Offset Data)
            │                                     │
            └──────────────────┬──────────────────┘
                               ▼ (Context Assembly)
                     [LLM Grounded Answer]

```

#### Traversal Step Sequence:

1. **Target Bill Resolution:** Locate `(:Bill {number: "H.R. 3630", congress: 117})`.
2. **Advocacy Retrieval:** Traverse `(b)<-[:LOBBIED_FOR]-(a:AdvocacyEntity)` to extract the 12-year history of the *Lymphedema Advocacy Group*.
3. **Economic Retrieval:** Traverse `(b)<-[:EVALUATES]-(e:EconomicEstimate)` to extract the CBO scorecard demonstrating direct costs offset by reductions in cellulitis hospitalizations.
4. **Context Assembly:** The LLM synthesizes congressional motivation using factual historical and fiscal metrics without fabricating legislative intent.

---

## 5. Engineering Constraints & Validation Rules

When building this knowledge graph, the coding assistant must enforce the following technical constraints:

1. **No Unanchored Codes:** An `HCPCSCode` node must not exist without a corresponding `REQUIRES_DIAGNOSIS` edge to at least one `ICD10Code` and an `ESTABLISHES_CODE` edge from `ChangeRequest` (`CR 13286`).
2. **Explicit Nullability on Limits:** Bandaging supplies (`A6448`–`A6455`, `A6594`–`A6608`) must have `FrequencyLimit.max_quantity = NULL` with `limit_type = "Medical Necessity"`, preventing claim rejections on consumable wrapping.
3. **Primary Key Determinism:**
* `Bill`: Composite key `f"{congress}-{type}-{number}"` (e.g., `"117-HR-3630"`).
* `StatutorySection`: Composite key `f"{law_id}-{division}-{section}"` (e.g., `"PL117-328-DFF-S4133"`).
* `USCodeSection`: Standardized string `f"{title}-USC-{section}-{subparagraph}"` (e.g., `"42-USC-1395m-z"`).
* `HCPCSCode`: Exact 5-character alphanumeric token (e.g., `"A6576"`).


4. **Strict Subgraph Retrieval (Anti-Hallucination):** The retrieval orchestrator must only pass subgraphs to the LLM that form a complete path from the resolved clinical/policy entities to either a `PublicLaw` or a `ClinicalStudy` node. Disconnected nodes must be purged during the graph compaction phase.