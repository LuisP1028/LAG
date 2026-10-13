# Master Component-to-Edit Matrix: Multi-Tier Policy Knowledge Graph Data Pipeline

**Run ID:** `20261012T231057-024-zqga`  
**Governing Specification:** `functional_specification_003.md`  
**Document:** `wayfinder/20261012T231057-024-zqga/matrix.md`  
**Planning Status:** Planned & Locked

---

## 1. System Component Overview

The Policy Knowledge Graph pipeline consists of eight modular components implementing the five dependent tiers, shared property graph schemas, and invariant validation oracles defined in `functional_specification_003.md`:

| Component ID | Component Name | Primary Role | Implementation File |
|---|---|---|---|
| `COMP-01` | Master Graph Data Contracts & Models | Schema definitions for 15 node types, 15 edge types, and edge provenance metadata | `src/graph/models.py` |
| `COMP-02` | Tier 1: Legislative Genesis Engine | Keyword search, bill action lineage, enactment isolation, `Policy`/`Bill`/`PublicLaw` vertices | `src/graph/tier1_legislative.py` |
| `COMP-03` | Tier 2: Statutory Codification Parser | USLM XML retrieval, XPath traversal, Title 42 statutory amendment extraction, `StatutorySection` vertex | `src/graph/tier2_statutory.py` |
| `COMP-04` | Tier 3: Administrative Rulemaking Harvester | Federal Register API query, Final Rule ingestion, Change Request directive extraction, `Regulation`/`ChangeRequest` vertices | `src/graph/tier3_regulatory.py` |
| `COMP-05` | Tier 4A: Coverage Policy & Diagnostic Bridge | Medicare Coverage Database article ingestion, HCPCS procedure codes, ICD-10 diagnosis codes, policy bridge | `src/graph/tier4a_coverage.py` |
| `COMP-06` | Tier 4B: Geographic Fee Schedule Normalizer | CMS DMEPOS CSV unpivoting (108 columns across 54 jurisdictions), 4 DME MAC Jurisdictions, `FeeScheduleEntry` records | `src/graph/tier4b_fee_schedule.py` |
| `COMP-07` | Tier 5: Contextual Enrichment Client | Senate LDA lobbying disclosures, CBO cost estimates, NCBI PubMed biomedical studies | `src/graph/tier5_context.py` |
| `COMP-08` | Graph Storage Engine & Invariant Validator | Directed property graph storage, idempotent upsert (`MERGE`), provenance enforcement, graph compaction validation | `src/graph/engine.py` |

---

## 2. Definitive Master Component-to-Edit Matrix

| Component ID | Target File Path | Target Symbols / Functions | Input Parameters | Output Keys & Artifacts | Transformation & Parsing Logic | Fail-Fast Error Condition |
|---|---|---|---|---|---|---|
| **`COMP-01`** | `src/graph/models.py` | `PolicyNode`, `BillNode`, `PublicLawNode`, `StatutorySectionNode`, `RegulationNode`, `ChangeRequestNode`, `CoveragePolicyNode`, `JurisdictionNode`, `StateNode`, `FeeScheduleEntryNode`, `HCPCSCodeNode`, `ICD10CodeNode`, `LobbyingFilingNode`, `CBOScoreNode`, `LiteratureStudyNode`, `EdgeProvenance`, `GraphEdge` | Raw parsed dictionaries | Validated typed Pydantic models with normalized composite primary keys | Enforces PK format invariants (`POLICY-[keyword]`, `BILL-[c]-[t]-[n]`, `PLAW-[c]-[n]`, `USC-[t]-[s]-[sub]`, `FR-[doc]`, `CMS-CR-[cr]`, `CMS-MCD-[art]`, `JURIS-DME-[code]`, `STATE-[st]`, `FEE-[h]-[s]-[r]-[y]`, `HCPCS-[c]`, `ICD10-[c]`, `LDA-[uuid]`, `CBO-[id]`, `PUBMED-[pmid]`). | Missing mandatory field or PK format mismatch raises `ValidationError`. |
| **`COMP-02`** | `src/graph/tier1_legislative.py` | `discover_legislation(keyword: str, run_id: str)`, `_query_bills()`, `_resolve_enacted_law()` | `keyword: str`, `run_id: str` | `policy_node: PolicyNode`, `bill_nodes: list[BillNode]`, `public_law_node: PublicLawNode`, `edges: list[GraphEdge]`, `handoff: Tier1Handoff` | Queries Congress.gov `/v3/bill?q={keyword}`. Creates root `Policy` node. Inspects `bill.laws` to isolate enacted omnibus vehicle (`PLAW-117-328`) and standalone bills (`HR 3630`). Creates `[:TARGETS_BILL]` and `[:ENACTED_AS]` edges with provenance. | Zero bill search results or missing enacted public law raises `Phase1DiscoveryError` or `Phase1EnactmentMissingError`. |
| **`COMP-03`** | `src/graph/tier2_statutory.py` | `parse_statutory_codification(handoff: Tier1Handoff, run_id: str)`, `_fetch_uslm_xml()`, `_extract_section()` | `handoff: Tier1Handoff`, `run_id: str` | `statutory_node: StatutorySectionNode`, `edges: list[GraphEdge]`, `handoff: Tier2Handoff` | Loads GPO GovInfo USLM XML package. Executes XPath `//division[@id='FF']/title[@id='IV']/section[@id='4133']`. Extracts Title `42`, Section `1395x`, Subsections `["s", "2", "JJ"]`. Creates `[:MODIFIES_CODE]` edge with provenance. | Unloadable XML or failure to isolate statutory amendment section raises `Phase2DocumentRetrievalError` or `Phase2SectionNotFoundError`. |
| **`COMP-04`** | `src/graph/tier3_regulatory.py` | `harvest_regulations(handoff: Tier2Handoff, run_id: str)`, `_query_federal_register()`, `_parse_preamble()` | `handoff: Tier2Handoff`, `run_id: str` | `regulation_node: RegulationNode`, `change_request_node: ChangeRequestNode`, `edges: list[GraphEdge]`, `handoff: Tier3Handoff` | Queries Federal Register `/api/v1/documents.json` with `conditions[term]=1395x(s)(2)(JJ)`. Extracts Final Rule `2023-24455` (88 FR 77676). Parses preamble for Change Request `CR 13286`, transmittal `12349`, benefit category `"LC"`, MCD Article `"A59508"`, and cited PMIDs. Creates `[:IMPLEMENTED_BY]` and `[:ISSUES_TRANSMITTAL]` edges with provenance. | Zero matching Final Rules or missing Change Request/MCD pointers raises `Phase3RuleNotFoundError` or `Phase3DirectiveMissingError`. |
| **`COMP-05`** | `src/graph/tier4a_coverage.py` | `ingest_coverage_policy(handoff: Tier3Handoff, run_id: str)`, `_parse_article()`, `_extract_codes()` | `handoff: Tier3Handoff`, `run_id: str` | `policy_node: CoveragePolicyNode`, `hcpcs_nodes: list[HCPCSCodeNode]`, `icd10_nodes: list[ICD10CodeNode]`, `edges: list[GraphEdge]` | Fetches CMS MCD Article payload for `A59508`. Extracts covered procedure codes (`A6520`–`A6549`, `A6552`–`A6567`, `S8430`) and covered ICD-10 diagnosis codes (`I89.0`, `I97.2`, `Q82.0`). Creates `[:MANDATES_POLICY]`, `[:GOVERNS]`, and `[:ALLOWS_DIAGNOSIS]` edges. Enforces zero direct edges between HCPCS and ICD-10. | Unloadable article or missing structured code tables raises `Phase4ArticleFetchError` or `Phase4CodingTableMissingError`. |
| **`COMP-06`** | `src/graph/tier4b_fee_schedule.py` | `normalize_fee_schedules(handoff: Tier3Handoff, hcpcs_codes: list[HCPCSCodeNode], run_id: str)`, `_unpivot_matrix()` | `handoff: Tier3Handoff`, `hcpcs_codes: list[HCPCSCodeNode]`, `run_id: str` | `jurisdiction_nodes: list[JurisdictionNode]`, `state_nodes: list[StateNode]`, `fee_nodes: list[FeeScheduleEntryNode]`, `edges: list[GraphEdge]` | Filters `phase4_cms_dmepos_lc_category.csv` where `CATG == "LC"`. Instantiates 4 DME MAC Jurisdictions and 54 States. Unpivots 108 columns (NR and R). Where rate > 0.00, instantiates `FeeScheduleEntry`. Creates `[:APPLIES_TO_JURISDICTION]`, `[:COVERS_STATE]`, `[:HAS_FEE_SCHEDULE]`, and `[:APPLIES_TO]` edges with provenance. | Missing CSV, zero matching rows, or failure to unpivot all 54 jurisdictions raises `Phase4FeeScheduleDatasetError` or `Phase4IncompleteJurisdictionError`. |
| **`COMP-07`** | `src/graph/tier5_context.py` | `enrich_context(target_bills: list[BillNode], citations: list[int], run_id: str)`, `_query_lda()`, `_query_cbo()`, `_query_pubmed()` | `target_bills: list[BillNode]`, `citations: list[int]`, `run_id: str` | `filing_nodes: list[LobbyingFilingNode]`, `cbo_nodes: list[CBOScoreNode]`, `study_nodes: list[LiteratureStudyNode]`, `edges: list[GraphEdge]` | Queries Senate LDA API for registered filings on target bills; extracts CBO cost estimates from Congress.gov/CBO archive; queries NCBI PubMed E-Utilities `esummary` for PMIDs (`31454178`). Instantiates context nodes and creates `[:HAS_ADVOCACY_RECORD]`, `[:HAS_BUDGET_IMPACT]`, and `[:SUPPORTED_BY_EVIDENCE]` edges with provenance. | Invalid literature UID or malformed context response raises `Phase5LiteratureNotFoundError`. |
| **`COMP-08`** | `src/graph/engine.py` | `PropertyGraphEngine`, `upsert_node()`, `upsert_edge()`, `validate_invariants(root_keyword: str)`, `export_json()` | `nodes: list[AnyNode]`, `edges: list[GraphEdge]` | `DirectedPropertyGraph`, `ValidationReport` | Maintains directed property graph. Enforces `MERGE` semantics on deterministic PKs. Checks 100% of edges have non-empty provenance (`source_uri`, `selector`, `ingestion_timestamp`, `run_id`). Validates unbroken graph traversal from `POLICY-[keyword]` to every terminal node (`INV-UNBROKEN-ANCESTRY`). Validates 54-state completeness (`INV-50-STATE-COMPLETENESS`). | Broken ancestry, orphan nodes, missing provenance properties, or schema violations raises `GraphValidationError`. |

---

## 3. Detailed Component Architecture and Implementation Specifications

### 3.1. `COMP-01`: Data Contracts & Models (`src/graph/models.py`)
- **Key Classes:**
  - `PolicyNode`: `keyword: str`, `run_id: str`, `timestamp: str`, `primary_key: str = "POLICY-{keyword}"`
  - `BillNode`: `congress: int`, `type: str`, `number: int`, `title: str`, `introduced_date: str`, `primary_key: str = "BILL-{congress}-{type}-{number}"`
  - `PublicLawNode`: `congress: int`, `number: int`, `title: str`, `enacted_date: str`, `primary_key: str = "PLAW-{congress}-{number}"`
  - `StatutorySectionNode`: `title: int`, `section: str`, `subsections: list[str]`, `heading: str`, `text: str`, `primary_key: str = "USC-{title}-{section}-{'-'.join(subsections)}"`
  - `RegulationNode`: `citation: str`, `document_number: str`, `effective_date: str`, `cfr_parts: list[str]`, `primary_key: str = "FR-{document_number}"`
  - `ChangeRequestNode`: `cr_number: str`, `transmittal_number: str`, `benefit_category: str`, `effective_date: str`, `primary_key: str = "CMS-CR-{cr_number}"`
  - `CoveragePolicyNode`: `article_id: str`, `title: str`, `effective_date: str`, `policy_type: str`, `primary_key: str = "CMS-MCD-{article_id}"`
  - `JurisdictionNode`: `code: str`, `contractor_name: str`, `primary_key: str = "JURIS-DME-{code}"`
  - `StateNode`: `state_code: str`, `state_name: str`, `primary_key: str = "STATE-{state_code}"`
  - `FeeScheduleEntryNode`: `hcpcs_code: str`, `state_code: str`, `is_rural: bool`, `fee_amount: float`, `ceiling: float`, `floor: float`, `year: int`, `primary_key: str = "FEE-{hcpcs}-{state}-{'R' if is_rural else 'NR'}-{year}"`
  - `HCPCSCodeNode`: `code: str`, `short_description: str`, `category: str`, `primary_key: str = "HCPCS-{code}"`
  - `ICD10CodeNode`: `code: str`, `description: str`, `primary_key: str = "ICD10-{code}"`
  - `LobbyingFilingNode`: `filing_uuid: str`, `registrant_name: str`, `client_name: str`, `amount: float`, `year: int`, `primary_key: str = "LDA-{filing_uuid}"`
  - `CBOScoreNode`: `id: str`, `title: str`, `url: str`, `published_date: str`, `primary_key: str = "CBO-{id}"`
  - `LiteratureStudyNode`: `pmid: int`, `doi: str`, `title: str`, `journal: str`, `pub_year: int`, `primary_key: str = "PUBMED-{pmid}"`
  - `EdgeProvenance`: `source_uri: str`, `selector: str`, `ingestion_timestamp: str`, `run_id: str`
  - `GraphEdge`: `source_pk: str`, `label: str`, `target_pk: str`, `provenance: EdgeProvenance`

### 3.2. `COMP-02`: Tier 1: Legislative Genesis Engine (`src/graph/tier1_legislative.py`)
- Accepts `keyword: str` and `run_id: str`.
- Instantiates root `PolicyNode` (`POLICY-LTA`).
- Executes GET request to Congress.gov API v3 `/bill?q={keyword}`.
- Traverses matching bills across historical Congresses (111th–117th Congress).
- Traverses related bills and bill actions to locate enacted public law vehicle (`PLAW-117-328` via `HR 2617`).
- Instantiates `BillNode` for standalone vehicles (`HR 3630`, `S 1315`) and omnibus vehicle (`HR 2617`).
- Instantiates `PublicLawNode` for `PLAW-117-328`.
- Instantiates edges:
  - `(Policy)-[:TARGETS_BILL]->(Bill)`
  - `(Bill)-[:ENACTED_AS]->(PublicLaw)`
- Emits handoffs: `Target_Bill_IDs` and `Enacted_Law_ID`.

### 3.3. `COMP-03`: Tier 2: Statutory Codification Parser (`src/graph/tier2_statutory.py`)
- Consumes `Enacted_Law_ID` (`PLAW-117-328`).
- Fetches GovInfo USLM XML package (`PLAW-117publ328.xml`).
- Traverses DOM via XPath `//division[@id='FF']/title[@id='IV']/section[@id='4133']`.
- Parses `<amendingAction>` instruction to isolate amended U.S. Code Title `42`, Section `1395x`, and added Subsections `["s", "2", "JJ"]`.
- Instantiates `StatutorySectionNode` (`USC-42-1395x-s-2-JJ`).
- Instantiates edge: `(PublicLaw)-[:MODIFIES_CODE]->(StatutorySection)` with provenance.
- Emits handoff: `US_Code_Citations`.

### 3.4. `COMP-04`: Tier 3: Administrative Rulemaking Harvester (`src/graph/tier3_regulatory.py`)
- Consumes `US_Code_Citations` (`USC-42-1395x-s-2-JJ`).
- Queries Federal Register API `/api/v1/documents.json` with condition `term=1395x(s)(2)(JJ)`.
- Resolves Final Rule `2023-24455` (88 FR 77676).
- Extracts modified CFR references (`42 CFR § 410.36`).
- Traverses preamble and regulatory text to isolate Change Request `CR 13286`, Transmittal `12349`, Benefit Category `"LC"`, MCD Article pointer `"A59508"`, and footnote PubMed literature citations (`PMID 31454178`).
- Instantiates `RegulationNode` and `ChangeRequestNode`.
- Instantiates edges:
  - `(StatutorySection)-[:IMPLEMENTED_BY]->(Regulation)`
  - `(Regulation)-[:ISSUES_TRANSMITTAL]->(ChangeRequest)`
- Emits handoffs: `Operational_Filters`, `Coverage_Policy_ID`, and `Clinical_Citations`.

### 3.5. `COMP-05`: Tier 4A: Coverage Policy Bridge (`src/graph/tier4a_coverage.py`)
- Consumes `Coverage_Policy_ID` (`CMS-MCD-A59508`).
- Ingests CMS MCD Article `A59508` (*Standard Documentation Requirements for Lymphedema Compression Treatment Items*).
- Extracts metadata and tabular data:
  - Covered HCPCS codes: `A6520`–`A6549`, `A6552`–`A6567`, `S8430`.
  - Covered ICD-10 diagnosis codes: `I89.0`, `I97.2`, `Q82.0`.
- Instantiates `CoveragePolicyNode`, `HCPCSCodeNode`s, and `ICD10CodeNode`s.
- Instantiates edges:
  - `(ChangeRequest)-[:MANDATES_POLICY]->(CoveragePolicy)`
  - `(CoveragePolicy)-[:GOVERNS]->(HCPCSCode)`
  - `(CoveragePolicy)-[:ALLOWS_DIAGNOSIS]->(ICD10Code)`
- Enforces relational constraint: No direct edge between `HCPCSCode` and `ICD10Code`.

### 3.6. `COMP-06`: Tier 4B: Geographic Fee Schedule Normalizer (`src/graph/tier4b_fee_schedule.py`)
- Consumes `Operational_Filters` (`CATG == "LC"`).
- Ingests `phase4_cms_dmepos_lc_category.csv`.
- Filters rows where `CATG == "LC"`.
- Instantiates 4 `JurisdictionNode`s (`JURIS-DME-A`, `JURIS-DME-B`, `JURIS-DME-C`, `JURIS-DME-D`).
- Instantiates 54 `StateNode`s (50 states + DC + PR + VI).
- Creates edges:
  - `(ChangeRequest)-[:APPLIES_TO_JURISDICTION]->(Jurisdiction)` (4 edges)
  - `(Jurisdiction)-[:COVERS_STATE]->(State)` (54 edges across jurisdictions)
- Unpivots the 108 columns (NR and R for each state/territory).
- Where fee amount > `0.00`, instantiates `FeeScheduleEntryNode`.
- Creates edges:
  - `(HCPCSCode)-[:HAS_FEE_SCHEDULE]->(FeeScheduleEntry)`
  - `(FeeScheduleEntry)-[:APPLIES_TO]->(State)`

### 3.7. `COMP-07`: Tier 5: Contextual Enrichment Client (`src/graph/tier5_context.py`)
- Consumes `Target_Bill_IDs` and `Clinical_Citations`.
- Executes parallel queries:
  - Senate LDA API: Retrieves lobbying reports referencing target bills (registrant, client, expenses). Instantiates `LobbyingFilingNode` and edge `(Bill)-[:HAS_ADVOCACY_RECORD]->(LobbyingFiling)`.
  - CBO API / Archive: Retrieves 10-year budget estimates and scores. Instantiates `CBOScoreNode` and edge `(Bill)-[:HAS_BUDGET_IMPACT]->(CBOScore)`.
  - NCBI PubMed E-Utilities `esummary`: Ingests publication metadata for cited PMIDs. Instantiates `LiteratureStudyNode` and edge `(Regulation)-[:SUPPORTED_BY_EVIDENCE]->(LiteratureStudy)`.

### 3.8. `COMP-08`: Graph Engine & Invariant Validator (`src/graph/engine.py`)
- Assembles the complete directed property graph.
- Implements `upsert_node(node)` and `upsert_edge(edge)` enforcing deterministic primary keys and `MERGE` semantics (`INV-IDEMPOTENT-UPSERTS`).
- Performs graph validation pass:
  1. Validates 100% of edges have non-empty `source_uri`, `selector`, `ingestion_timestamp`, and `run_id`.
  2. Traverses from root `POLICY-[keyword]` via BFS/DFS to verify full connectivity; purges or rejects unanchored subgraphs (`INV-UNBROKEN-ANCESTRY`).
  3. Verifies that all 54 jurisdictions are present and populated with fee schedule entries (`INV-50-STATE-COMPLETENESS`).
  4. Verifies zero direct edges exist between `HCPCSCode` and `ICD10Code` (`INV-NO-KEYWORD-BRIDGING`).
  5. Serializes property graph into structured JSON/JSON-LD and export formats.

---

## 4. Verification Oracles & Acceptance Evidence

| Verification Target | Input | Expected Output State | Verification Method |
|---|---|---|---|
| Root Policy Anchor | `"LTA"` | Root vertex `POLICY-LTA` instantiated with execution metadata | Unit test asserting vertex creation and properties |
| Legislative Lineage | `"LTA"` | `BILL-117-hr-3630`, `BILL-117-hr-2617`, `PLAW-117-328` linked via `[:TARGETS_BILL]` and `[:ENACTED_AS]` | Congress.gov API v3 response verification against empirical assets |
| Statutory Granularity | `PLAW-117-328` | Public Law 117-328 links to `USC-42-1395x-s-2-JJ` via Division FF, Title IV, Sec. 4133 | USLM XML XPath traversal verification against `phase2_uslm_plaw_117_328_sec4133.xml` |
| Regulatory Directives | `USC-42-1395x-s-2-JJ` | Linked `FR-2023-24455` (88 FR 77676) and `CMS-CR-13286` (Transmittal 12349, CATG LC) | Federal Register API query verification against empirical assets |
| Coverage Policy Bridge | `CMS-CR-13286` | `CMS-CR-13286` links to `CMS-MCD-A59508`, which links to `HCPCSCode` and `ICD10Code`. Zero direct HCPCS->ICD10 edges. | Relational constraint verification on coverage policy subgraph |
| Geographic Unpivoting | `CATG == "LC"` | Exactly 4 `Jurisdiction` nodes and 54 `State` nodes exist. All non-zero rate cells in `phase4_cms_dmepos_lc_category.csv` are discrete `FeeScheduleEntry` nodes. | CSV unpivoting verification across 108 columns (NR & R) |
| Contextual Enrichment | `BILL-117-hr-3630`, `PMID 31454178` | `LobbyingFiling` (LDA), `CBOScore` (CBO 58517), and `LiteratureStudy` (PMID 31454178) instantiated and linked | Contextual API verification against empirical assets |
| Edge Provenance Completeness | All edges | 100% of edges contain non-empty `source_uri`, `selector`, `ingestion_timestamp`, and `run_id` | Post-ingestion graph validation query asserting edge properties |
| Unbroken Ancestry | Full graph | 100% of terminal nodes maintain an unbroken traversable path back to `POLICY-LTA` | Directed graph reachability search from root vertex |
