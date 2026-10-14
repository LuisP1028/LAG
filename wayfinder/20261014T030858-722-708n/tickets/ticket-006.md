# Ticket 006: End-to-End Verification Suite & Demonstration Harness Alignment (`tests/*` and `verify_all.py`)

## 1. Objective & Scope
Align the automated test suites (`tests/test_graph_pipeline.py`, `tests/test_graphrag_pipeline.py`, `tests/test_api_endpoints.py`) and end-to-end verification script (`verify_all.py`) with the 8-hop knowledge graph ontology (`17` entity labels, `18` relationship types, `3,875` nodes, `7,593` edges, `54` US states/territories including `STATE-GU`) and the requirements of `functional_specification_015.md`.

---

## 2. Current Implementation Defects (Grounded in Codebase Audit)

### 2.1 `tests/test_graph_pipeline.py`
1. **Nonexistent `exports/ivig_knowledge_graph.json` & Legacy Labels in `test_neo4j_sync_and_mcp_invariants` (lines 291–325):**
   - Calls `sync_engine.sync_file("exports/ivig_knowledge_graph.json")`, which fails with `FileNotFoundError` because only `exports/lta_knowledge_graph.json` exists.
   - Queries `MATCH (h:HCPCSCode)-[r]-(i:ICD10Code)` instead of `MATCH (h:ProcedureCode)-[r]-(i:DiagnosisCode)`.
2. **Missing Tier 5 Contextual Record Verification & Coverage Title Assertion:**
   - Does not assert that `CoveragePolicyNode.title` is `"Lymphedema Compression Treatment Items – Correct Coding and Billing – Revised"` (free of the CPT license banner), nor that `CBO-58517` (`CBOScoreNode`), `LDA-c8697fc5-7f3b-4861-8a49-d9e6357ad287` / `LDA-1821a229-8264-40c2-9b04-49169d917adf` (`LobbyingFilingNode`), and the 5 `LiteratureStudyNode` entities are present in `graph.nodes`.

### 2.2 `tests/test_graphrag_pipeline.py`
1. **Legacy Primary Keys and Edge Labels (lines 44–57, 73, 82–92, 95–116, 197–226):**
   - `test_oracle_1_patient_benefit_routing` asserts `"CMS-CR-13286"`, `"CMS-MCD-A59508"`, and `"FEE-A6522-WI-NR-2024"` instead of `"TR-CR13286"`, `"DME-MAC-COPE147943"`, and `"FEE-A6522-WI-NR-2026"`.
   - `test_oracle_2_no_keyword_bridging` queries `(:HCPCSCode)-[r]->(:ICD10Code)` and `(h:HCPCSCode {primary_key: 'HCPCS-A6583'})<-[:GOVERNS]-(cp:CoveragePolicy)-[:ALLOWS_DIAGNOSIS]->(d:ICD10Code)` expecting `CMS-MCD-A59508`, instead of `(:ProcedureCode)-[r]->(:DiagnosisCode)` and `(h:ProcedureCode {primary_key: 'HCPCS-A6583'})<-[:COVERS_PROCEDURE]-(cp:CoveragePolicy)-[:REQUIRES_DIAGNOSIS]->(d:DiagnosisCode)` expecting `DME-MAC-COPE147943`.
   - `test_oracle_3_cross_policy_convergence` queries `"How do IVIG and LTA converge under federal law?"` and expects `POLICY-IVIG` and `FR-2023-24455`, whereas the 8-hop graph persists `POLICY-LTA`, `BILL-117-hr-3630`, `BILL-117-hr-2617`, `PLAW-117-328`, `STAT-117-328-SEC-4133`, `USC-42-1395x-s-2-JJ`, `REG-FR-2023-24455`, `CFR-42-410`, `TR-CR13286`, and `DME-MAC-COPE147943`.
   - `test_single_state_query_ny` asserts `"CMS-CR-13286"`, `"CMS-MCD-A59508"`, and `"FEE-A6522-NY-NR-2024"` instead of `"TR-CR13286"`, `"DME-MAC-COPE147943"`, and `"FEE-A6522-NY-NR-2026"`.

### 2.3 `tests/test_api_endpoints.py`
1. **Stale Node/Edge Counts and Legacy Labels (lines 24–53, 82–172):**
   - `test_api_graph_summary` asserts `data["total_nodes"] == 3971` and `data["total_edges"] >= 7700` instead of `data["total_nodes"] == 3875`, `data["total_edges"] == 7593`, `len(data["nodes_by_label"]) == 17`, and `len(data["edges_by_type"]) == 18`.
   - `test_api_graph_topology` checks `FeeScheduleEntry` instead of `FeeScheduleRate` and lacks verification of `state_filter=GU`, `jurisdiction_filter=JURIS-DME-D`, human-readable `name` derivation, and HTTP 400 fail-fast responses on invalid state/jurisdiction codes.
   - `test_api_graphrag_subgraph`, `test_api_graphrag_query`, and `test_api_single_state_and_subgraph` assert `"CMS-MCD-A59508"` and `"CMS-CR-13286"` instead of `"DME-MAC-COPE147943"` and `"TR-CR13286"`.
   - `test_api_graphrag_query_all_14_entity_types` tests only 14 legacy IDs instead of all `17` 8-hop entity categories.

### 2.4 `verify_all.py`
1. **Outdated Cross-Policy Demo Query (lines 52–63):**
   - Queries `"How do IVIG and LTA converge under federal law?"` which fails against the 8-hop LTA graph because `IVIG` is not an ingested policy node.

---

## 3. Target Architecture & Exact File Edits

### 3.1 `tests/test_graph_pipeline.py`
1. Add assertions in `test_hop5_and_hop6_clinical_coverage_and_operational_hcpcs` verifying that `graph.nodes["DME-MAC-COPE147943"].title == "Lymphedema Compression Treatment Items – Correct Coding and Billing – Revised"` and does not contain `"License for Use"`.
2. Add `test_tier5_contextual_sidecars(graph)` verifying that `CBO-58517` (`CBOScoreNode`), `LDA-c8697fc5-7f3b-4861-8a49-d9e6357ad287` and `LDA-1821a229-8264-40c2-9b04-49169d917adf` (`LobbyingFilingNode`), and all 5 `LiteratureStudyNode` entities (`PUBMED-25574334`, `PUBMED-19147992`, `PUBMED-23945581`, `PUBMED-27651153`, `PUBMED-34389291`) and their `HAS_BUDGET_IMPACT`, `HAS_ADVOCACY_RECORD`, and `SUPPORTED_BY_EVIDENCE` edges are present.
3. Update `test_neo4j_sync_and_mcp_invariants` (lines 291–325) to:
   - Synchronize `"exports/lta_knowledge_graph.json"` with `purge_stale=True` and assert `nodes_synced == 3875` and `edges_synced == 7593`.
   - Re-run `sync_file("exports/lta_knowledge_graph.json")` a second time and assert idempotency (`total_nodes == 3875`, `total_edges == 7593`).
   - Verify all 17 node labels and 18 edge types exist in Neo4j, `State` count is `54` (including `STATE-GU`), `Jurisdiction` count is `4`, `MATCH (h:ProcedureCode)-[r]-(i:DiagnosisCode)` is `0`, `MATCH (:Bill {primary_key: 'BILL-117-hr-3630'})-[r:ENACTED_AS]->(:PublicLaw)` is `0`, and zero edges lack provenance attributes.

### 3.2 `tests/test_graphrag_pipeline.py`
1. **`test_oracle_1_patient_benefit_routing`:**
   - Assert `expected_chain` contains `"STATE-WI"`, `"JURIS-DME-B"`, `"TR-CR13286"`, `"DME-MAC-COPE147943"`, `"ICD10-I97.2"`, `"HCPCS-A6522"`, and `"FEE-A6522-WI-NR-2026"`.
   - Assert `FEE-A6522-WI-NR-2026` has `fee_amount == 290.47` and 20% coinsurance `== 58.09`.
   - Assert `resp.answer` contains `"290.47"`, `"58.09"`, and `"DME-MAC-COPE147943"` (or `"TR-CR13286"`).
2. **`test_oracle_2_no_keyword_bridging`:**
   - Assert `MATCH (:ProcedureCode)-[r]->(:DiagnosisCode) RETURN count(r) AS cnt` is `0`.
   - Assert `MATCH (h:ProcedureCode {primary_key: 'HCPCS-A6583'})<-[:COVERS_PROCEDURE]-(cp:CoveragePolicy)-[:REQUIRES_DIAGNOSIS]->(d:DiagnosisCode) RETURN cp.primary_key AS cp_pk, count(d) AS diag_count` returns `cp_pk == "DME-MAC-COPE147943"` and `diag_count == 4`.
3. **`test_oracle_3_omnibus_and_8hop_lineage` (replacing legacy `IVIG` convergence test):**
   - Query `"How was H.R. 3630 enacted into Public Law 117-328 and implemented in 88 FR 77676?"`.
   - Verify `BILL-117-hr-3630`, `BILL-117-hr-2617`, `PLAW-117-328`, `STAT-117-328-SEC-4133`, `USC-42-1395x-s-2-JJ`, `REG-FR-2023-24455`, `CFR-42-410`, `TR-CR13286`, and `DME-MAC-COPE147943` are traversed and grounded in `resp.answer`.
4. **`test_single_state_query_ny` & `test_guam_54th_jurisdiction_query`:**
   - Update `test_single_state_query_ny` to check `"STATE-NY"`, `"JURIS-DME-A"`, `"TR-CR13286"`, `"DME-MAC-COPE147943"`, and `"FEE-A6522-NY-NR-2026"`.
   - Add `test_guam_54th_jurisdiction_query` verifying that `"What DME MAC jurisdiction covers Guam?"` resolves `STATE-GU` and traverses to `JURIS-DME-D` (Noridian Healthcare Solutions).

### 3.3 `tests/test_api_endpoints.py`
1. **`test_api_graph_summary`:**
   - Assert `data["total_nodes"] == 3875`, `data["total_edges"] == 7593`, `len(data["nodes_by_label"]) == 17`, and `len(data["edges_by_type"]) == 18`.
2. **`test_api_graph_topology`:**
   - Verify default topology returns `165` nodes and `173` edges, zero `FeeScheduleRate` nodes, and every node has a human-readable `name` derived from persisted properties (e.g., `DME-MAC-COPE147943` has `name != "DME-MAC-COPE147943"` and `STATE-GU` has `name == "Guam"`).
   - Verify `GET /api/graph/topology?state_filter=WI` and `GET /api/graph/topology?state_filter=GU` return `FeeScheduleRate` nodes scoped to `WI` and `GU` respectively and scope `State` and `Jurisdiction` nodes to the selected state and its governing DME MAC jurisdiction (`JURIS-DME-B` for `WI`, `JURIS-DME-D` for `GU`).
   - Verify `GET /api/graph/topology?state_filter=XX` and `GET /api/graph/topology?jurisdiction_filter=JURIS-DME-Z` return HTTP `400`.
3. **`test_api_entities_resolve`, `test_api_graphrag_subgraph`, `test_api_graphrag_query`, `test_api_single_state_and_subgraph`:**
   - Update expected primary keys to `"TR-CR13286"`, `"DME-MAC-COPE147943"`, and `"FEE-A6522-WI-NR-2026"`, and add explicit resolution checks for `"Guam"` $\to$ `"STATE-GU"` and invalid prefix keys (`"HCPCS-99999"`, `"JURIS-DME-Z"`) returning HTTP `400`.
4. **`test_api_graphrag_query_all_17_entity_types`:**
   - Verify one-click inquiry (`POST /api/graphrag/query` with `primary_key`) across all 17 entity categories:
     `["POLICY-LTA", "BILL-117-hr-3630", "PLAW-117-328", "STAT-117-328-SEC-4133", "USC-42-1395x-s-2-JJ", "REG-FR-2023-24455", "CFR-42-410", "TR-CR13286", "DME-MAC-COPE147943", "ICD10-I97.2", "HCPCS-A6522", "FEE-A6522-WI-NR-2026", "JURIS-DME-B", "STATE-WI", "LDA-c8697fc5-7f3b-4861-8a49-d9e6357ad287", "CBO-58517", "PUBMED-25574334"]`.

### 3.4 `verify_all.py`
Update `verify_all.py` so all 3 demonstration workflows execute cleanly against the 8-hop LTA graph (`Workflow 1`: Wisconsin patient benefit routing; `Workflow 2`: 8-hop legislative omnibus & regulatory lineage for H.R. 3630 $\to$ H.R. 2617 $\to$ P.L. 117-328 $\to$ 88 FR 77676 $\to$ CR 13286; `Workflow 3`: Single-state & territorial inquiry for New York and Guam).

---

## 4. Verification Criteria
1. `pytest tests/test_graph_pipeline.py tests/test_graphrag_pipeline.py tests/test_api_endpoints.py` passes with 100% green results (`0` failures, `0` skips).
2. `/opt/anaconda3/bin/python3 verify_all.py` completes with exit code `0` and `✓ VERIFICATION COMPLETED SUCCESSFULLY WITH 0 ERRORS`.
