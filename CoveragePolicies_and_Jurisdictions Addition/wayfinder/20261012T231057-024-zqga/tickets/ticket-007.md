# Decision Ticket 007: End-to-End Graph Assembly, Edge Provenance Contract, Idempotent Upserts, and Graph Connectivity Verification

**Ticket ID:** `ticket-007.md`  
**Run ID:** `20261012T231057-024-zqga`  
**Scope:** Cross-Tier Assembly & Invariant Verification  
**Status:** RESOLVED  
**Claimed By:** `wayfinder-read-and-plan`  
**Blocked By:** `ticket-001.md`, `ticket-002.md`, `ticket-003.md`, `ticket-004.md`, `ticket-005.md`, `ticket-006.md`

---

## 1. Architectural Question
How must the graph construction engine assemble, upsert, and validate the complete multi-tier property graph, how is the universal edge provenance contract enforced across all relationship types, and how do post-ingestion graph compaction algorithms certify the five system invariants (`INV-FAIL-FAST`, `INV-NO-KEYWORD-BRIDGING`, `INV-UNBROKEN-ANCESTRY`, `INV-50-STATE-COMPLETENESS`, `INV-IDEMPOTENT-UPSERTS`) and verify against empirical ground-truth payloads?

---

## 2. Complete Graph Schema & Primary Key Directory

The graph architecture unifies 15 discrete vertex labels and 15 explicit edge types:

### 2.1. Master Node Primary Key and Property Directory
| Node Label | Deterministic Primary Key Format | Required Properties (Name: Type) |
|---|---|---|
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

### 2.2. Master Edge Cardinality and Semantic Directory
| Source Node | Edge Label | Target Node | Cardinality | Semantics |
|---|---|---|---|---|
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

---

## 3. Universal Edge Provenance Contract

Every instantiated relationship edge across all 15 edge types must contain four non-nullable attributes:
1. `source_uri` (`string`): The definitive URL or local repository path from which the edge relation was derived.
2. `selector` (`string`): The exact JSONPath, XPath, or CSV column header evaluated to extract the connection.
3. `ingestion_timestamp` (`string`): ISO-8601 UTC timestamp of execution.
4. `run_id` (`string`): Execution run identifier.

---

## 4. Idempotent Upsert Engine (`MERGE` Semantics)

To support continuous hydration across multiple policies without duplicating federal entities:
1. **Node Upsert Contract:** Every vertex is identified strictly by its deterministic composite primary key. Ingestion checks for existing vertices matching the primary key:
   - If not present: `CREATE` vertex with all properties.
   - If present: `UPDATE` non-key properties and append execution metadata without duplicating vertices.
2. **Edge Upsert Contract:** Relationships are uniquely identified by `(source_pk, edge_label, target_pk)`. Re-running an ingestion pass updates the edge's `ingestion_timestamp` and `run_id` without creating duplicate parallel edges.

---

## 5. Post-Ingestion Graph Compaction & Invariant Verification Oracles

The post-ingestion verification engine must enforce five system invariants:

1. **`INV-FAIL-FAST` (Deterministic Dependency Halting):**
   - If any upstream query or parser fails to resolve a required foreign key, execution halts immediately with structured error telemetry.
   - Falling back to heuristic searches, text guessing, synthetic identifiers, or mock files raises fatal exception.
2. **`INV-NO-KEYWORD-BRIDGING`:**
   - All clinical codes (`HCPCSCode`, `ICD10Code`) must be extracted strictly from structured tables in `CoveragePolicy` and filtered CSV categories.
   - Free-text search to identify diagnostic codes is strictly prohibited.
   - Direct edges between `HCPCSCode` and `ICD10Code` are rejected by schema validation.
3. **`INV-UNBROKEN-ANCESTRY` (Graph Compaction):**
   - Every node must maintain a directed, traversable path to the `Policy` root node.
   - Post-ingestion verification performs breadth-first / depth-first search from `POLICY-[keyword]`. Any unreachable node triggers immediate abort and graph rejection.
4. **`INV-50-STATE-COMPLETENESS`:**
   - Ingestion of DMEPOS fee schedules must process all 54 jurisdictions present in the dataset.
   - Collapsing multi-state rate columns into a single state constitutes a schema validation failure.
5. **`INV-IDEMPOTENT-UPSERTS`:**
   - Node creation must execute via deterministic composite primary keys (`MERGE` semantics).
   - Ingesting overlapping policies updates shared federal nodes without duplicating vertices or edges.

---

## 6. Acceptance Verification against Ground-Truth Empirical Assets

Verification against `DataSources_Agent/assets/20261012T213134-452-7663/`:
1. **Keyword Anchor:** Runtime input `"LTA"` creates root vertex `POLICY-LTA`.
2. **Statutory Granularity:** Public Law 117-328 links specifically to `USC-42-1395x-s-2-JJ` via Division FF, Title IV, Section 4133.
3. **Coverage Bridge Conformance:** `CMS-CR-13286` links to `CoveragePolicy` node `CMS-MCD-A59508`. Node `CMS-MCD-A59508` links to `HCPCSCode` nodes and `ICD10Code` nodes. No direct edge exists between `HCPCSCode` and `ICD10Code`.
4. **Geographic Coverage:** Exactly 4 `Jurisdiction` nodes and 54 `State` nodes exist. All non-zero rate cells in `phase4_cms_dmepos_lc_category.csv` are instantiated as `FeeScheduleEntry` nodes mapped to their respective `State` and `HCPCSCode`.
5. **Edge Provenance Completeness:** 100% of edges in the graph contain non-empty `source_uri`, `selector`, `ingestion_timestamp`, and `run_id` properties.
