# Functional Specification: Multi-Tier Policy Knowledge Graph Data Pipeline and Schema Normalization

**Document ID:** `functional_specification_003.md`  
**Status:** Requirements Specification  
**Implementation Guidance:** Strictly Prohibited (DO NOT CODE YET)  
**Taxonomy Reference:** Authoritative definitions defined in `LANGUAGE.md`

---

## 1. Technical Scope and Objective

This specification defines the functional requirements for a deterministic data pipeline that ingests a single policy search parameter (`{Policy Keyword}`, e.g., `"LTA"`), queries authoritative federal legislative, regulatory, and healthcare billing data sources, and constructs a directed property graph.

The system must resolve five dependent tiers:
1. **Legislative Origins:** Tracking standalone advocacy bills to enacted omnibus public laws.
2. **Statutory Codification:** Isolating public law sections and mapping their text to amended United States Code provisions.
3. **Administrative Directives:** Mapping statutory provisions to Federal Register Final Rules, Code of Federal Regulations (CFR) citations, and CMS Change Requests.
4. **Clinical Coverage and Pricing:**
   - Ingesting CMS Medicare Coverage Database (MCD) policy articles to establish the explicit legal link between procedure codes and covered diagnosis codes.
   - Unpivoting multi-state fee schedule matrices into a relational model of regional contractor jurisdictions, states, and discrete reimbursement records.
5. **Contextual Enrichment:** Ingesting lobbying disclosures, Congressional Budget Office (CBO) cost scores, and peer-reviewed clinical citations.

---

## 2. Taxonomy and Evaluation Parameters

All system evaluations must conform strictly to [LANGUAGE.md](file:///Users/diesel/Desktop/LAG/LANGUAGE.md):

* **`{errors}`:** Execution termination triggered by an HTTP non-200 response, unparseable XML/JSON payload, missing mandatory foreign key, or schema validation failure.
* **`{correctness}`:** The verified execution of data transformations, XML/JSON parsing, CSV column unpivoting, and relational key assignments according to this specification.
* **`{functionality}`:** The deterministic assembly of a directed graph connecting an input keyword to its terminal pricing, coverage, and context nodes without heuristic fallback logic.
* **`{correct required outputs}`:** A directed property graph adhering to the schemas in Section 4, where every terminal node connects to the root policy, all 54 jurisdictions in the fee schedule are unpivoted, and all edges contain provenance metadata.
* **`{sufficient}`:** Complete specification of all node fields, data types, relationship labels, payload extraction selectors, and error conditions.
* **`{insufficient}`:** Any ambiguity requiring assumptions regarding data types, extraction paths, schema normalization, or error handling.

---

## 3. Pipeline Stages & Transformation Requirements

```
[Stage 1: Legislation]
  Runtime Input: policy_keyword (e.g. "LTA")
  Source: Congress.gov API v3 (/bill)
  Outputs: Target_Bill_IDs, Enacted_Law_ID
      │
      ▼
[Stage 2: Statute]
  Input: Enacted_Law_ID (e.g. PLAW-117-328)
  Source: GPO GovInfo USLM XML
  Outputs: US_Code_Citations (Title, Section, Subsections)
      │
      ▼
[Stage 3: Regulation]
  Input: US_Code_Citations (e.g. 42 U.S.C. § 1395x(s)(2)(JJ))
  Source: Federal Register API v1, CMS Transmittal Portal
  Outputs: Regulation citation, Change Request ID, Benefit Category, Coverage Policy ID
      │
      ├─────────────────────────────────────────────┐
      ▼                                             ▼
[Stage 4A: Coverage Policy & Coding]          [Stage 4B: Geographic Fee Schedule]
  Input: Coverage Policy ID (e.g. A59508)        Input: Benefit Category (LC)
  Source: CMS MCD (Policy Article)              Source: CMS DMEPOS Fee Schedule CSV
  Outputs:                                      Outputs:
   - CoveragePolicy node                         - 4 DME MAC Jurisdiction nodes
   - HCPCSCode nodes                             - 54 State/Territory nodes
   - ICD10Code nodes                             - FeeScheduleEntry records (rate, R/NR)
   - [:GOVERNS] and [:ALLOWS_DIAGNOSIS] edges    - [:HAS_FEE_SCHEDULE] and [:APPLIES_TO] edges
      │                                             │
      └──────────────────────┬──────────────────────┘
                             │
                             ▼
[Stage 5: Parallel Contextual Enrichment]
  Inputs: Target_Bill_IDs, Clinical_Citations (PMIDs)
  Sources: Senate LDA API, CBO API, NCBI PubMed API
  Outputs: LobbyingFiling nodes, CBOScore nodes, LiteratureStudy nodes
```

### 3.1. Stage 1: Legislative Genesis & Bill Resolution
* **Input:** A string scalar `{Policy Keyword}` (e.g., `"LTA"`).
* **Source:** Congress.gov API v3 (`/v3/bill`).
* **Processing:**
  1. Query bills by keyword across historical Congresses (e.g., 111th through 117th Congress).
  2. For each matching record, extract `congress` (integer), `type` (string, e.g., `"hr"`), and `number` (integer).
  3. Inspect `bill.laws` array within each record to detect public law enactment.
  4. Isolate the enacted omnibus vehicle (e.g., Public Law 117-328) and historical standalone vehicles (e.g., H.R. 3630).
* **Emitted Foreign Keys:**
  * `Target_Bill_IDs`: List of composite strings `BILL-[congress]-[type]-[number]`.
  * `Enacted_Law_ID`: Composite string `PLAW-[congress]-[law_number]`.

### 3.2. Stage 2: Statutory Codification Delta
* **Input:** `Enacted_Law_ID` from Stage 1.
* **Source:** GPO GovInfo USLM XML package.
* **Processing:**
  1. Load the USLM XML document for the specified public law.
  2. Execute structural XPath search to isolate the specific amendment section (e.g., `//division[@id='FF']/title[@id='IV']/section[@id='4133']`).
  3. Parse the amending instruction `<amendingAction>` to extract:
     - Target Title of the United States Code (integer, e.g., `42`).
     - Target Section (string, e.g., `"1395x"`).
     - Target Subsections (array of strings, e.g., `["s", "2", "JJ"]`).
     - Plain-text statutory definition and effective date.
* **Emitted Foreign Keys:**
  * `US_Code_Citations`: Composite string `USC-[title]-[section]-[subsections]`.

### 3.3. Stage 3: Administrative & Regulatory Execution
* **Input:** `US_Code_Citations` from Stage 2.
* **Sources:** Federal Register API v1 (`/api/v1/documents.json`), CMS Transmittal Portal.
* **Processing:**
  1. Query Federal Register documents citing the statutory authority (`42 U.S.C. 1395x(s)(2)(JJ)`).
  2. Ingest the Final Rule payload (e.g., Document `2023-24407`, Citation `88 FR 77676`).
  3. Extract modified Code of Federal Regulations references (`42 CFR § 410.36`).
  4. Parse preamble and regulatory citations for:
     - CMS Change Request identifier (e.g., `CR 13286`, Transmittal `12349`).
     - Benefit Category code (e.g., `"LC"`).
     - Cited PubMed literature identifiers (PMIDs) in regulatory footnotes.
     - Reference pointer to the operational Medicare Coverage Database Policy Article (e.g., `"A59508"`).
* **Emitted Foreign Keys:**
  * `Operational_Filters`: `{ benefit_category: "LC", transmittal_id: "12349", cr_number: "13286" }`.
  * `Coverage_Policy_ID`: Composite string `CMS-MCD-A59508`.
  * `Clinical_Citations`: List of integer PubMed IDs.

### 3.4. Stage 4A: Coverage Policy Integration & Diagnostic Constraints
* **Input:** `Coverage_Policy_ID` (`CMS-MCD-A59508`) from Stage 3.
* **Source:** CMS Medicare Coverage Database (MCD) Policy Article payload.
* **Processing:**
  1. Fetch the raw article payload for `A59508` (Joint DME MAC Policy Article: *Standard Documentation Requirements for Lymphedema Compression Treatment Items*).
  2. Extract metadata: Article ID (`"A59508"`), Title, Revision Effective Date, Governing Contractor IDs (DME MACs).
  3. Locate the table of **Covered HCPCS Codes**:
     - Extract procedure codes: `A6520`–`A6549`, `A6552`–`A6567`, and `S8430`.
     - Extract short descriptions and equipment classification categories.
  4. Locate the table of **Covered ICD-10-CM Codes**:
     - Extract diagnostic codes (e.g., `I89.0`, `I97.2`, `Q82.0`).
     - Extract official code descriptions.
  5. Enforce relational constraint:
     - Create edge `(CoveragePolicy)-[:GOVERNS]->(HCPCSCode)`.
     - Create edge `(CoveragePolicy)-[:ALLOWS_DIAGNOSIS]->(ICD10Code)`.
     - **Prohibition:** No direct edge may connect `HCPCSCode` to `ICD10Code`.

### 3.5. Stage 4B: Geographic & Jurisdictional Fee Schedule Normalization
* **Input:** `Operational_Filters.benefit_category` (`"LC"`) from Stage 3.
* **Sources:** CMS DMEPOS Fee Schedule CSV (`phase4_cms_dmepos_lc_category.csv`), CMS DME MAC Regional Map.
* **Processing:**
  1. Filter master DMEPOS dataset to rows matching `CATG == "LC"`.
  2. Parse row header metadata: `HCPCS` (string), `Mod` (string, nullable), `Mod2` (string, nullable), `Ceiling` (float), `Floor` (float), `Description` (string).
  3. Map the 4 standard DME MAC Jurisdictions:
     - `JURIS-DME-A`: Noridian Healthcare Solutions (CT, DE, DC, ME, MD, MA, NH, NJ, NY, PA, RI, VT).
     - `JURIS-DME-B`: CGS Administrators (IL, IN, KY, MI, MN, OH, WI).
     - `JURIS-DME-C`: CGS Administrators (AL, AR, CO, FL, GA, LA, MS, NM, NC, OK, SC, TN, TX, VA, WV, PR, VI).
     - `JURIS-DME-D`: Noridian Healthcare Solutions (AK, AZ, CA, HI, ID, IA, KS, MO, MT, NE, NV, ND, OR, SD, UT, WA, WY).
  4. Unpivot the 108 state pricing columns:
     - For each of the 54 jurisdictions (50 states + DC + PR + VI):
       - Read Non-Rural fee column: `[STATE] (NR)`.
       - Read Rural fee column: `[STATE] (R)`.
     - Where a fee value is greater than `0.00`, instantiate a discrete `FeeScheduleEntry` record.
  5. Instantiate graph topology:
     - `(ChangeRequest)-[:APPLIES_TO_JURISDICTION]->(Jurisdiction)`
     - `(Jurisdiction)-[:COVERS_STATE]->(State)`
     - `(HCPCSCode)-[:HAS_FEE_SCHEDULE]->(FeeScheduleEntry)`
     - `(FeeScheduleEntry)-[:APPLIES_TO]->(State)`

### 3.6. Stage 5: Contextual Enrichment
* **Inputs:** `Target_Bill_IDs` (Stage 1), `Clinical_Citations` (Stage 3).
* **Sources:** Senate Lobbying Disclosure Act (LDA) API, CBO Cost Estimates API, NCBI PubMed E-Utilities API.
* **Processing:**
  1. Query Senate LDA API using `Target_Bill_IDs` to retrieve registered lobbying reports referencing the bill.
  2. Query CBO API using `Target_Bill_IDs` to extract 10-year cost estimates and baseline scores.
  3. Query NCBI PubMed E-Utilities API using PMIDs from `Clinical_Citations` to extract article title, journal, publication date, authors, and DOI.
* **Instantiate graph topology:**
  - `(Bill)-[:HAS_ADVOCACY_RECORD]->(LobbyingFiling)`
  - `(Bill)-[:HAS_BUDGET_IMPACT]->(CBOScore)`
  - `(Regulation)-[:SUPPORTED_BY_EVIDENCE]->(LiteratureStudy)`

---

## 4. Graph Schema & Structural Specifications

### 4.1. Node Specifications

| Node Label | Deterministic Primary Key Format | Required Properties (Name: Type) |
| :--- | :--- | :--- |
| **`Policy`** | `POLICY-[keyword]` | `keyword: string`, `run_id: string`, `timestamp: string` |
| **`Bill`** | `BILL-[congress]-[type]-[number]` | `congress: int`, `type: string`, `number: int`, `title: string`, `introduced_date: string` |
| **`PublicLaw`** | `PLAW-[congress]-[number]` | `congress: int`, `number: int`, `title: string`, `enacted_date: string` |
| **`StatutorySection`** | `USC-[title]-[section]-[subsections]` | `title: int`, `section: string`, `subsections: string[]`, `heading: string`, `text: string` |
| **`Regulation`** | `FR-[document_number]` | `citation: string`, `document_number: string`, `effective_date: string`, `cfr_parts: string[]` |
| **`ChangeRequest`** | `CMS-CR-[cr_number]` | `cr_number: string`, `transmittal_number: string`, `benefit_category: string`, `effective_date: string` |
| **`CoveragePolicy`** | `CMS-MCD-[article_id]` | `article_id: string`, `title: string`, `effective_date: string`, `policy_type: string` |
| **`Jurisdiction`** | `JURIS-DME-[A\|B\|C\|D]` | `code: string`, `contractor_name: string` |
| **`State`** | `STATE-[state_code]` | `state_code: string`, `state_name: string` |
| **`FeeScheduleEntry`** | `FEE-[hcpcs]-[state]-[rural_flag]-[year]` | `hcpcs_code: string`, `state_code: string`, `is_rural: bool`, `fee_amount: float`, `ceiling: float`, `floor: float`, `year: int` |
| **`HCPCSCode`** | `HCPCS-[code]` | `code: string`, `short_description: string`, `category: string` |
| **`ICD10Code`** | `ICD10-[code]` | `code: string`, `description: string` |
| **`LobbyingFiling`** | `LDA-[filing_uuid]` | `filing_uuid: string`, `registrant_name: string`, `client_name: string`, `amount: float`, `year: int` |
| **`CBOScore`** | `CBO-[id]` | `id: string`, `title: string`, `url: string`, `published_date: string` |
| **`LiteratureStudy`** | `PUBMED-[pmid]` | `pmid: int`, `doi: string`, `title: string`, `journal: string`, `pub_year: int` |

### 4.2. Edge Specifications & Cardinality

| Source Node | Edge Label | Target Node | Cardinality | Semantics |
| :--- | :--- | :--- | :--- | :--- |
| `Policy` | `[:TARGETS_BILL]` | `Bill` | `1..*` | Links policy keyword to legislative vehicles |
| `Bill` | `[:ENACTED_AS]` | `PublicLaw` | `1..1` | Connects passed bill to public law statute |
| `PublicLaw` | `[:MODIFIES_CODE]` | `StatutorySection` | `1..*` | Maps public law division/section to USC citation |
| `StatutorySection` | `[:IMPLEMENTED_BY]` | `Regulation` | `1..*` | Maps statutory authority to agency final rule |
| `Regulation` | `[:ISSUES_TRANSMITTAL]` | `ChangeRequest` | `1..*` | Connects rule to operational instructions |
| `ChangeRequest` | `[:MANDATES_POLICY]` | `CoveragePolicy` | `1..*` | Links directive to coverage determination article |
| `ChangeRequest` | `[:APPLIES_TO_JURISDICTION]`| `Jurisdiction` | `1..4` | Associates transmittal with DME MAC jurisdictions |
| `Jurisdiction` | `[:COVERS_STATE]` | `State` | `1..*` | Maps MAC jurisdiction to assigned states |
| `CoveragePolicy` | `[:GOVERNS]` | `HCPCSCode` | `1..*` | Defines billable procedure codes covered |
| `CoveragePolicy` | `[:ALLOWS_DIAGNOSIS]` | `ICD10Code` | `1..*` | Defines eligible diagnosis codes covered |
| `HCPCSCode` | `[:HAS_FEE_SCHEDULE]` | `FeeScheduleEntry`| `1..*` | Attaches pricing records to procedure code |
| `FeeScheduleEntry`| `[:APPLIES_TO]` | `State` | `1..1` | Associates pricing record with target state |
| `Bill` | `[:HAS_ADVOCACY_RECORD]` | `LobbyingFiling` | `0..*` | Links bill to lobbying disclosure filings |
| `Bill` | `[:HAS_BUDGET_IMPACT]` | `CBOScore` | `0..*` | Links bill to official CBO score records |
| `Regulation` | `[:SUPPORTED_BY_EVIDENCE]`| `LiteratureStudy` | `0..*` | Connects regulatory preamble to clinical studies |

### 4.3. Edge Provenance Contract

Every edge in the graph must contain four non-nullable properties:
1. `source_uri` (`string`): File path or API URL from which the edge was derived.
2. `selector` (`string`): Exact XPath, JSONPath, or CSV column header used to extract the relation.
3. `ingestion_timestamp` (`string`): ISO-8601 UTC timestamp of extraction.
4. `run_id` (`string`): Execution run identifier.

---

## 5. System Invariants & Failure Criteria

1. **`INV-FAIL-FAST` (Deterministic Dependency Halting):**
   * If any upstream query or parser fails to resolve a required foreign key (e.g., Stage 2 cannot isolate the statutory section XML node, or Stage 3 cannot extract the MCD Article reference), execution halts immediately with an explicit `{errors}` record.
   * Falling back to heuristic searches, text guessing, synthetic identifiers, or mock files is strictly prohibited.
2. **`INV-NO-KEYWORD-BRIDGING`:**
   * All clinical codes (`HCPCSCode`, `ICD10Code`) must be extracted strictly from structured tables in `CoveragePolicy` and filtered CSV categories.
   * Free-text queries (e.g., executing NLM text search `terms=lymphedema`) to identify diagnostic codes are prohibited.
3. **`INV-UNBROKEN-ANCESTRY` (Graph Compaction):**
   * Every node must maintain a directed, traversable path to the `Policy` root node.
   * A post-ingestion validation pass must verify full graph connectivity and reject any unanchored subgraphs.
4. **`INV-50-STATE-COMPLETENESS`:**
   * Ingestion of DMEPOS fee schedules must process all 54 jurisdictions present in the dataset.
   * Collapsing multi-state rate columns into a single state constitutes a schema validation failure.
5. **`INV-IDEMPOTENT-UPSERTS`:**
   * Node creation must execute via deterministic composite primary keys (`MERGE` semantics).
   * Ingesting overlapping policies must update shared federal nodes without duplicating vertices or creating duplicate edges.

---

## 6. Acceptance & Verification Criteria (`{correct required outputs}`)

The implementation satisfies requirements if and only if it verifies against the empirical dataset in `DataSources_Agent/assets/20261012T213134-452-7663/` with the following outcomes:

1. **Keyword Anchor:** The query parameter `"LTA"` creates root node `POLICY-LTA`.
2. **Statutory Granularity:** Public Law 117-328 links specifically to `USC-42-1395x-s-2-JJ` via Division FF, Title IV, Section 4133.
3. **Coverage Bridge Conformance:** `CMS-CR-13286` links to `CoveragePolicy` node `CMS-MCD-A59508`. Node `CMS-MCD-A59508` links to `HCPCSCode` nodes and `ICD10Code` nodes. No direct edge exists between `HCPCSCode` and `ICD10Code`.
4. **Geographic Coverage:** Exactly 4 `Jurisdiction` nodes and 54 `State` nodes exist. All non-zero rate cells in `phase4_cms_dmepos_lc_category.csv` are instantiated as `FeeScheduleEntry` nodes mapped to their respective `State` and `HCPCSCode`.
5. **Edge Provenance Completeness:** 100% of edges in the graph contain non-empty `source_uri`, `selector`, `ingestion_timestamp`, and `run_id` properties.
6. **Zero Code Rule:** This document contains pure functional specifications. No implementation source files, migrations, or application code may be written until this specification is approved.
