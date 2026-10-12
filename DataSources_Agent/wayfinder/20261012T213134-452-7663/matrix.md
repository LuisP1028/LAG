# Master Component-to-Edit Matrix: Zero-Seed Foreign-Key Extraction Pipeline

**Run ID:** `20261012T213134-452-7663`  
**Governing Specification:** `functional_specification_001.md`  
**Document:** `wayfinder/20261012T213134-452-7663/matrix.md`  
**Planning Status:** Planned & Locked

---

## 1. System Component Overview

The extraction pipeline consists of seven modular components that implement the five sequential and parallel execution phases defined in `functional_specification_001.md`, plus shared data contract models and orchestrator telemetry:

| Component ID | Component Name | Primary Role | Implementation File |
|---|---|---|---|
| `COMP-01` | Legislative Bill Discovery Engine | Phase 1 keyword search, bill action lineage, enactment identification | `src/pipeline/phase1_legislative.py` |
| `COMP-02` | Statutory Codification Parser | Phase 2 USLM XML retrieval, DOM traversal, statutory citation extraction | `src/pipeline/phase2_statutory.py` |
| `COMP-03` | Administrative Rulemaking Harvester | Phase 3 Federal Register API querying, directive parsing, clinical citations | `src/pipeline/phase3_regulatory.py` |
| `COMP-04` | Medical Coding & Fee Adjudicator | Phase 4 HCPCS filtering by operational codes, fee calculation, diagnosis joining | `src/pipeline/phase4_adjudication.py` |
| `COMP-05` | Advocacy & Evidentiary Context Client | Phase 5 Senate LDA API querying, CBO cost link extraction, PubMed literature metadata | `src/pipeline/phase5_context.py` |
| `COMP-06` | Foreign-Key Contracts & Identifier Models | Shared immutable composite key schemas, data validation, serialization | `src/pipeline/contracts.py` |
| `COMP-07` | Pipeline Orchestrator & Telemetry Monitor | End-to-end execution coordination, dependency gating, fail-fast error telemetry | `src/pipeline/orchestrator.py` |

---

## 2. Definitive Master Component-to-Edit Matrix

| Component ID | Target File Path | Target Symbols / Functions | Input Parameters | Output Keys & Artifacts | Transformation & Parsing Logic | Fail-Fast Error Condition |
|---|---|---|---|---|---|---|
| **`COMP-06`** | `src/pipeline/contracts.py` | `CompositeBillId`, `EnactedLawId`, `USCodeCitation`, `OperationalFilters`, `ClinicalCitation`, `HCPCSAdjudicationRecord`, `TelemetryError` | Raw entity dictionaries | Validated typed Pydantic models with normalized composite keys | Enforces format invariants: `BILL-[congress]-[type]-[num]`, `PLAW-[c]-[n]`, `USC-[t]-[s]-[sub]`, `HCPCS-[code]`. | Format mismatch or missing required field raises `ContractValidationError`. |
| **`COMP-01`** | `src/pipeline/phase1_legislative.py` | `discover_legislation(keyword: str)`, `_query_congress_api()`, `_resolve_enacted_law()` | `keyword: str` | `target_bill_ids: list[CompositeBillId]`, `enacted_law_id: EnactedLawId` | Calls Congress.gov `/v3/bill?q={keyword}`. Follows bill actions and related bills to locate public law enactment in `bill.laws`. | Empty search results or missing enacted public law raises `Phase1DiscoveryError` or `Phase1EnactmentMissingError`. |
| **`COMP-02`** | `src/pipeline/phase2_statutory.py` | `parse_statutory_codification(law_id: EnactedLawId)`, `_fetch_uslm_xml()`, `_extract_amendments()` | `enacted_law_id: EnactedLawId` | `us_code_citations: list[USCodeCitation]` | Retrieves GovInfo USLM XML package. Deterministic XPath traversal to amendatory `<section>` isolating added Title 42 paragraphs and subsections. | Retrieval failure or missing permanent code additions raises `Phase2DocumentRetrievalError` or `Phase2StatutoryCodificationMissingError`. |
| **`COMP-03`** | `src/pipeline/phase3_regulatory.py` | `harvest_regulations(citations: list[USCodeCitation])`, `_query_federal_register()`, `_extract_clinical_citations()` | `us_code_citations: list[USCodeCitation]` | `operational_filters: OperationalFilters`, `clinical_citations: list[ClinicalCitation]` | Queries Federal Register `/api/v1/documents.json` for Final Rules referencing citation authority. Isolates directive IDs (CR 13286), category flags, and preamble PubMed links. | Zero final rules or missing operational directives raises `Phase3RuleNotFoundError` or `Phase3DirectiveMissingError`. |
| **`COMP-04`** | `src/pipeline/phase4_adjudication.py` | `adjudicate_medical_billing(filters: OperationalFilters, state: str)`, `_filter_hcpcs_master()`, `_calculate_regional_fee()` | `operational_filters: OperationalFilters`, `state: str` (default: `"WY"`) | `adjudication_subgraph: list[HCPCSAdjudicationRecord]` | Reads CMS HCPCS master dataset, filters rows where `PI == 40` and `BETOS == O1L`. Joins state fee schedule, computes 80/20 coinsurance, attaches ICD-10 indication codes. | Zero matching procedure codes or missing fee schedule rate raises `Phase4ZeroCodesMatchedError` or `Phase4FeeScheduleMissingError`. |
| **`COMP-05`** | `src/pipeline/phase5_context.py` | `retrieve_advocacy_and_evidence(bill_ids: list[CompositeBillId], clinical: list[ClinicalCitation])`, `_query_lda()`, `_query_pubmed()` | `target_bill_ids: list[CompositeBillId]`, `clinical_citations: list[ClinicalCitation]` | `advocacy_filings: list[dict]`, `economic_estimates: list[dict]`, `literature_metadata: list[dict]` | Parallel dispatch: queries Senate LDA API by bill number; retrieves CBO score from Congress.gov bill package; queries NCBI Entrez E-utilities `esummary` by PMID. | Malformed PMID or unreachable literature record raises `Phase5LiteratureNotFoundError`. |
| **`COMP-07`** | `src/pipeline/orchestrator.py` | `run_pipeline(keyword: str, state: str)`, `_emit_telemetry()` | `keyword: str`, `state: str` | `PipelineExecutionResult` | Coordinates sequential execution Phase 1 → Phase 2 → Phase 3 → Phase 4, and dispatches Phase 5 in parallel. Catches exceptions and surfaces structured telemetry logs. | Any step failure halts downstream execution immediately, logging HTTP status, endpoint, and missing field path. |

---

## 3. Detailed Component Specifications

### 3.1. `COMP-06`: Foreign-Key Contracts & Data Models (`src/pipeline/contracts.py`)
- **Key Classes:**
  - `CompositeBillId`: Represents a legislative measure (`congress: int`, `type: str`, `number: int`, `composite_id: str`).
  - `EnactedLawId`: Represents enacted public law (`congress: int`, `law_number: int`, `type: str = "public"`, `composite_id: str`).
  - `USCodeCitation`: Represents permanent statutory anchor (`title: int`, `section: str`, `subsection: str`, `citation_string: str`, `composite_id: str`).
  - `OperationalFilters`: Represents administrative classifications (`benefit_category: str`, `pricing_indicator: str`, `type_of_service: str`, `transmittal_id: str`, `betos_code: str`).
  - `ClinicalCitation`: Represents evidentiary citations (`type: str`, `id: str`, `composite_id: str`, `context: str`).
  - `HCPCSAdjudicationRecord`: Represents terminal billing entity (`hcpcs_code: str`, `allowed_amount: float`, `coinsurance_20: float`, `medicare_share_80: float`, `qualifying_icd10: list[str]`, `frequency_limit: str`, `lineage: dict`).

### 3.2. `COMP-01`: Legislative Discovery (`src/pipeline/phase1_legislative.py`)
- **Operational Logic:**
  1. Accepts `keyword` (`str`).
  2. Executes GET request to `https://api.congress.gov/v3/bill` with query param `q={keyword}`.
  3. Iterates over returned measures to extract `BILL-[congress]-[type]-[number]`.
  4. Follows `/actions` and `/relatedbills` endpoints to identify which bill or companion vehicle was enacted into public law.
  5. Extracts `bill.laws` matching `"Public Law"`. Formats `EnactedLawId`.
  6. Emits `target_bill_ids` and `enacted_law_id`.

### 3.3. `COMP-02`: Statutory Codification (`src/pipeline/phase2_statutory.py`)
- **Operational Logic:**
  1. Consumes `enacted_law_id`.
  2. Fetches raw USLM XML from `https://www.govinfo.gov/bulkdata/PLAW/{congress}/public/PLAW-{congress}publ{law_number}.xml`.
  3. Evaluates XPath `//section[contains(heading, 'LYMPHEDEMA')]`.
  4. Parses amendatory subsections to extract the target U.S. Code Title (`42`), Section (`1395x` and `1395m`), and added subsections (`s(2)(JJ)` and `z`).
  5. Emits `us_code_citations`.

### 3.4. `COMP-03`: Administrative Rulemaking (`src/pipeline/phase3_regulatory.py`)
- **Operational Logic:**
  1. Consumes `us_code_citations`.
  2. Queries Federal Register API `/api/v1/documents.json` with conditions `term=1395m(z)` and `agencies[]=centers-for-medicare-medicaid-services`.
  3. Extracts Final Rule document number (`2023-24457`), citation (`88 FR 77676`), and RIN (`0938-AV03`).
  4. Resolves operational change request identifier (`CR 13286`) and classification values (`Category 60`, `PI 40`, `BETOS O1L`).
  5. Scans preamble for PubMed literature hyperlinks/references (`PMID-31454178`).
  6. Emits `operational_filters` and `clinical_citations`.

### 3.5. `COMP-04`: Medical Coding & Fee Adjudication (`src/pipeline/phase4_adjudication.py`)
- **Operational Logic:**
  1. Consumes `operational_filters`.
  2. Reads CMS HCPCS master records, filtering exclusively by `Pricing_Indicator == "40"` and `BETOS == "O1L"`.
  3. Reads CMS DMEPOS fee schedule file for target state (e.g., `"WY"`). Joins on HCPCS code.
  4. Calculates 80% Medicare coverage and 20% patient coinsurance.
  5. Reads DME MAC Local Coverage Article (A59508) to attach diagnostic indication codes (`I89.0`, `I97.2`, `Q82.0`) and utilization replacement limits (3 per limb per 6 months).
  6. Emits terminal adjudication subgraph records with unbroken provenance back to originating bill.

### 3.6. `COMP-05`: Advocacy & Evidentiary Context (`src/pipeline/phase5_context.py`)
- **Operational Logic:**
  1. Consumes `target_bill_ids` and `clinical_citations` in parallel.
  2. Submits queries to Senate LDA API for target bills (`HR3630`, `S1315`), extracting registrant, client, expenditures, and issue codes.
  3. Extracts linked CBO cost estimate URLs and summary scores from Congress.gov bill detail.
  4. Queries NCBI Entrez E-utilities `esummary` endpoint for PubMed ID `31454178`, extracting title, authors, journal, and publication date.
  5. Emits evidentiary and advocacy subgraph records.

### 3.7. `COMP-07`: Orchestrator & Telemetry Monitor (`src/pipeline/orchestrator.py`)
- **Operational Logic:**
  1. Receives initial human input `keyword` (e.g., `"LTA"`).
  2. Enforces sequential gates:
     - If Phase 1 returns empty `enacted_law_id`, abort and log.
     - If Phase 2 returns empty `us_code_citations`, abort and log.
     - If Phase 3 returns empty `operational_filters`, abort and log.
  3. On fatal errors, outputs JSON error telemetry with phase number, input key, queried endpoint, HTTP status, raw response excerpt, and missing field path.

---

## 4. Verification Oracles & Acceptance Evidence

| Verification Target | Input | Expected Output State | Verification Command / Method |
|---|---|---|---|
| Phase 1 Legislation | `"LTA"` | `enacted_law_id == { congress: 117, law_number: 328 }`, `BILL-117-hr-3630` present | Unit test asserting Congress.gov response deserialization |
| Phase 2 Statute | `PLAW-117-328` | Contains `USC-42-1395x-s(2)(JJ)` and `USC-42-1395m-z` | XPath evaluation against live GovInfo PLAW-117publ328 XML |
| Phase 3 Rulemaking | `USC-42-1395m-z` | Document `2023-24457` (88 FR 77676), `PI=40`, `CR13286`, `PMID-31454178` | Federal Register API live query test |
| Phase 4 Coding | `PI=40`, `BETOS=O1L` | Matched codes `A6580`–`A6589`, WY allowed `$148.20`, coinsurance `$29.64` | HCPCS dataset filter & fee schedule join assertion |
| Phase 5 Context | `BILL-117-hr-3630`, `PMID-31454178` | LDA filings resolved, PubMed study metadata title and authors populated | NCBI E-utilities live response validation |
| Pipeline Provenance | `"LTA"` | Terminal code `HCPCS-A6583` links through `CR13286` → `USC-42-1395x` → `PLAW-117-328` → `BILL-117-hr-3630` | Complete graph path assertion |
