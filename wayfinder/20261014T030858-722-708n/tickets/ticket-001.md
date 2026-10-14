# Ticket 001: 8-Hop Extraction Payload Completeness, Coverage Title Normalization, and Live Neo4j Schema/Sync Reconciliation

- **Status:** Resolved
- **Claimed by:** wayfinder-read-and-plan
- **Blocked By:** None
- **Target Specification:** `functional_specification_015.md` (§2.1 Entity & Relationship Ingestion)

## 1. Decision Question

How must the 8-hop extraction pipeline (`src/graph/tier4a_coverage.py`, `src/graph/tier5_context.py`), exported graph payload (`exports/lta_knowledge_graph.json`), and Neo4j synchronization engine (`src/graph/neo4j_sync.py`) be reconciled so that all 17 entity labels and 18 relationship types are persisted in the live Neo4j database with unique primary key constraints, accurate clinical coverage titles, complete contextual nodes (`LobbyingFiling`, `CBOScore`, `LiteratureStudy`), and zero stale nodes or obsolete shortcut edges?

## 2. Empirical Reconnaissance Findings

1. **Clinical Coverage Title Extraction (`src/graph/tier4a_coverage.py` lines 134–141):**
   - `Extraction/assets/hop5_cgs_joint_mac_cope147943.html` contains two `<h1>` elements:
     - First `<h1>`: `License for Use of "Physicians' Current Procedural Terminology", (CPT) Fourth Edition` (CPT license modal header).
     - Second `<h1>` (and `<title>`): `Lymphedema Compression Treatment Items – Correct Coding and Billing – Revised`.
   - Because `_parse_clinical_coverage_html` used `re.search(r"<h1[^>]*>(.*?)</h1>", ...)`, it captured the CPT license modal header instead of the actual article title.
2. **Tier 5 Contextual Records (`src/graph/tier5_context.py` lines 49–145 & `Extraction/assets/tier5_lda_senate_filings_3630.json`):**
   - `Extraction/assets/hop1_congress_bill_117_hr_3630.json` contains the official CBO cost estimate under `$.bill.cboCostEstimates` (`[{"pubDate": "2022-09-23T20:25:00Z", "title": "H.R. 3630, Lymphedema Treatment Act", "url": "https://www.cbo.gov/publication/58517"}]`), and standalone CBO JSON files use `$.cboCostEstimates`. `enrich_context()` in `src/graph/tier5_context.py` only checked `data.get("costEstimates")`, omitting `CBOScoreNode` (`CBO-58517`) and `HAS_BUDGET_IMPACT`.
   - `Extraction/assets/tier5_lda_senate_filings_3630.json` contained an Akamai 403 HTML response from `lda.gov`, whereas `DataSources_Agent/assets/20261012T213134-452-7663/phase5_lda_lobbying_filings.json` contains the verified Senate LDA JSON payload (`filing_uuid`s `c8697fc5-7f3b-4861-8a49-d9e6357ad287` and `1821a229-8264-40c2-9b04-49169d917adf`).
3. **Live Neo4j Schema & Legacy Data State (`src/graph/neo4j_sync.py`):**
   - The live Neo4j database currently holds `3,971` nodes and `7,795` edges from pre-014 exports (`FeeScheduleEntry`, `HCPCSCode`, `ICD10Code`, `ChangeRequest`, `FR-2023-24455`, `CMS-CR-13286`, `CMS-MCD-A59508`, `USC-42-1395x-s-2-JJ` labeled as `StatutorySection`, 53 `State` nodes missing `STATE-GU`, and obsolete shortcut edges `BILL-117-hr-3630 -[:ENACTED_AS]-> PLAW-117-328`, `TARGETS_BILL`, `MODIFIES_CODE`, `ISSUES_TRANSMITTAL`, `GOVERNS`, `ALLOWS_DIAGNOSIS`, `HAS_FEE_SCHEDULE`, `APPLIES_TO`).
   - Standalone `RANGE` indexes (`bill_pk`, `idx_policy_pk`, `idx_publiclaw_pk`, etc.) exist in Neo4j with `owningConstraint: None`. Creating uniqueness constraints on those labels requires dropping non-constraint range indexes on `primary_key` first.
   - Merging nodes via `apoc.merge.node(['PolicyNode', item.label], {primary_key: item.primary_key}, ...)` when an existing node has `:PolicyNode` with a different secondary label (e.g. `USC-42-1395x-s-2-JJ` having `:StatutorySection` instead of `:USCSection`, or `HCPCS-A6520` having `:HCPCSCode` instead of `:ProcedureCode`) causes a `ConstraintValidationFailed` error on `policy_node_pk` unless stale nodes and legacy-labeled nodes are pruned before merging.

## 3. Concrete Architectural Decision

1. **Fix Publication Title Extraction in `src/graph/tier4a_coverage.py` (lines 134–141):**
   - Extract all `<h1>` tags via `re.findall(r"<h1[^>]*>(.*?)</h1>", chosen_html, flags=re.IGNORECASE | re.DOTALL)` and select the first cleaned heading that does not contain `"LICENSE FOR USE"` or `"CURRENT PROCEDURAL TERMINOLOGY"`. If none matches, use the cleaned `<title>` tag text.
2. **Fix CBO & LDA Extraction in `src/graph/tier5_context.py` (lines 49–145) and `Extraction/assets/tier5_lda_senate_filings_3630.json`:**
   - Copy the verified Senate LDA JSON payload from `DataSources_Agent/assets/20261012T213134-452-7663/phase5_lda_lobbying_filings.json` into `Extraction/assets/tier5_lda_senate_filings_3630.json`.
   - In `src/graph/tier5_context.py`, extract CBO cost estimate lists from `data.get("costEstimates") or data.get("cboCostEstimates") or (data.get("bill", {}).get("cboCostEstimates") if isinstance(data.get("bill"), dict) else None)`. When extracted from a `bill` payload, verify that the bill number/type/congress matches one of `target_bills` before attaching `HAS_BUDGET_IMPACT` from `primary_bill.primary_key` to `CBOScoreNode` (`CBO-58517`).
3. **Upgrade `Neo4jSyncEngine` in `src/graph/neo4j_sync.py` (lines 53–222):**
   - Define `CANONICAL_ENTITY_LABELS = ["Policy", "Bill", "PublicLaw", "StatutorySection", "USCSection", "Regulation", "CFRSection", "Transmittal", "CoveragePolicy", "DiagnosisCode", "ProcedureCode", "FeeScheduleRate", "Jurisdiction", "State", "LobbyingFiling", "CBOScore", "LiteratureStudy"]` and `CANONICAL_REL_TYPES = ["DISCOVERED_BILL", "INCORPORATED_INTO", "ENACTED_AS", "CONTAINS", "AMENDS", "AUTHORIZED_BY", "CODIFIED_IN", "IMPLEMENTED_BY", "MANDATES_POLICY", "REQUIRES_DIAGNOSIS", "COVERS_PROCEDURE", "HAS_RATE", "APPLIES_TO_STATE", "APPLIES_TO_JURISDICTION", "COVERS_STATE", "HAS_ADVOCACY_RECORD", "HAS_BUDGET_IMPACT", "SUPPORTED_BY_EVIDENCE"]`.
   - In `init_schema()`:
     - Query `SHOW INDEXES` and drop any index where `owningConstraint IS NULL`, `entityType == "NODE"`, and `properties == ["primary_key"]` (`DROP INDEX {idx_name} IF EXISTS`).
     - Create `CREATE CONSTRAINT policy_node_pk IF NOT EXISTS FOR (n:PolicyNode) REQUIRE n.primary_key IS UNIQUE`.
     - For every `lbl` in `CANONICAL_ENTITY_LABELS`, create `CREATE CONSTRAINT constraint_{lbl.lower()}_pk IF NOT EXISTS FOR (n:{lbl}) REQUIRE n.primary_key IS UNIQUE`.
   - In `sync_graph_dict(self, graph_dict: Dict[str, Any], batch_size: int = 500, prune_stale: bool = True)`:
     - When `prune_stale=True`:
       - Delete any `PolicyNode` not in `active_pks`: `MATCH (n:PolicyNode) WHERE NOT n.primary_key IN $active_pks DETACH DELETE n`.
       - Delete any `PolicyNode` carrying obsolete labels (`FeeScheduleEntry`, `HCPCSCode`, `ICD10Code`, `ChangeRequest`) or whose existing secondary label does not match its incoming `item.label` so `apoc.merge.node` never hits a constraint conflict on `:PolicyNode(primary_key)`.
       - Delete any relationship whose type is not in `CANONICAL_REL_TYPES` (`MATCH ()-[r]->() WHERE NOT type(r) IN $valid_rel_types DELETE r`) and delete any relationship not in the incoming edge keys (`source_pk + '->' + label + '->' + target_pk`), including any obsolete direct `ENACTED_AS` edge from an introduced bill that was incorporated into an omnibus bill (`MATCH (b:Bill)-[:INCORPORATED_INTO]->(:Bill) MATCH (b)-[r:ENACTED_AS]->(:PublicLaw) DELETE r`).
   - Update `__main__` default file list to `["exports/lta_knowledge_graph.json"]`.
4. **Regenerate `exports/lta_knowledge_graph.json` and Synchronize Live Neo4j:**
   - Run `PropertyGraphEngine(asset_dir="Extraction/assets").run_pipeline(keyword="LTA", run_id="run-lta-015")` and export to `exports/lta_knowledge_graph.json` (`3,875` nodes across all 17 labels, `7,593` edges across all 18 relationship types), then execute `Neo4jSyncEngine().sync_file("exports/lta_knowledge_graph.json")`.

## 4. Verification Criteria

- `exports/lta_knowledge_graph.json` and the live Neo4j database contain `3,875` nodes across all 17 labels (`Policy`: 1, `Bill`: 2, `PublicLaw`: 1, `StatutorySection`: 1, `USCSection`: 4, `Regulation`: 1, `CFRSection`: 7, `Transmittal`: 1, `CoveragePolicy`: 1, `DiagnosisCode`: 4, `ProcedureCode`: 77, `FeeScheduleRate`: 3710, `Jurisdiction`: 4, `State`: 54, `LobbyingFiling`: 2, `CBOScore`: 1, `LiteratureStudy`: 4) and `7,593` edges across all 18 relationship types.
- Re-running `sync_file("exports/lta_knowledge_graph.json")` is idempotent and produces zero duplicate nodes or edges.
