# Ticket 005: Regional Jurisdiction Lineage and Cross-Jurisdiction Comparative GraphRAG Traversal & Context Assembly

- **Ticket ID:** `ticket-005`
- **Status:** `RESOLVED`
- **Claimed by:** `wayfinder-read-and-plan`
- **Blocked by:** `ticket-004`
- **Blocks:** None
- **Governing Specification:** `functional_specification_008.md` (Requirement 5.3.1, Requirement 5.3.2, Acceptance Criterion 6)

---

## 1. Decision Question

How must `TopologicalTraversalEngine` (`src/graphrag/traversal.py`), `GraphContextAssembler` (`src/graphrag/context_assembler.py`), and `GraphRAGPipeline` (`src/graphrag/pipeline.py`) traverse and format subgraphs for (1) regional contractor/jurisdiction queries (`JURIS-DME-*` without a state or diagnosis code) and (2) cross-jurisdiction state and procedure rate comparisons (`STATE-CA` + `STATE-NY` + `HCPCS-A6522`)?

---

## 2. Context & Root Cause Analysis

1. **Missing Dedicated Jurisdiction Traversal (`src/graphrag/traversal.py`, lines 87–113 & 303–376):**
   - Single-jurisdiction queries (e.g., *"What states does Jurisdiction B cover?"*, *"What is Jurisdiction B?"*) fall into `_execute_single_general_traversal`, which executes an untyped 1-hop `LIMIT 50` query that misses 2-hop `CoveragePolicy` (`CMS-MCD-A59508`, `CMS-MCD-A59588`) and upstream regulatory/statutory lineage (`FR-2023-24455`, `PLAW-117-328`, `POLICY-LTA`, `POLICY-IVIG`).
   - Multi-jurisdiction contractor queries (e.g., *"What policies does CGS administer?"* anchoring `JURIS-DME-B` and `JURIS-DME-C`) fall into `allShortestPaths`, failing to retrieve the covered states (`COVERS_STATE`) and mandated `CoveragePolicy` articles.
2. **Broken Multi-State & State+HCPCS Comparative Traversal (`src/graphrag/traversal.py`, lines 303–376):**
   - Queries with multiple `State` anchors and/or `State` + `HCPCSCode` anchors without a diagnosis anchor (e.g., *"Compare allowable rates for A6522 between California and New York"*, anchoring `STATE-CA`, `STATE-NY`, `HCPCS-A6522`) fall through to `allShortestPaths((start)-[*..6]-(target))`.
   - Between `HCPCS-A6522` and `STATE-CA`, `allShortestPaths` finds only the 2-hop fee schedule path (`HCPCS-A6522 -> FEE-A6522-CA-* -> STATE-CA`), completely bypassing `JURIS-DME-D` (Noridian), `CMS-CR-13286`, and `CMS-MCD-A59508`.
   - Between `STATE-CA` and `STATE-NY`, `allShortestPaths` traverses 142 4-hop paths across every shared `HCPCSCode`, polluting `active_node_pks`.
3. **Context Assembly Drops Multi-State Fees and Covered State Lists (`src/graphrag/context_assembler.py`, lines 75–88 & 126–160):**
   - In Section 2 (`Contractor & Region`), line 79 checks `states = j.properties.get("states", "")`, which is empty on Neo4j `Jurisdiction` nodes because covered states are represented via `COVERS_STATE` edges.
   - In Section 4 (`Fees and Patient Costs`), line 141 uses `next((f for f in candidate_fees if f.properties.get("hcpcs_code") == "A6522"), None)` and line 153 filters `if h_code != "A6522"`, causing the second state's `A6522` fee entry (`FEE-A6522-NY-NR-2024`) to be silently discarded during cross-state comparisons!

---

## 3. Locked Architectural Decision

### 3.1 Dedicated Jurisdiction Traversal (`src/graphrag/traversal.py`)
1. Add `_execute_jurisdiction_traversal` to `TopologicalTraversalEngine`:
   ```python
   def _execute_jurisdiction_traversal(
       self,
       jurisdiction_pks: List[str],
       session: Session,
       nodes_by_pk: Dict[str, TraversalNode],
       edges_by_key: Dict[str, TraversalEdge],
       active_node_pks: Set[str],
       active_edge_keys: Set[str],
   ) -> None:
   ```
   Execute the Cypher query:
   ```cypher
   MATCH (j:Jurisdiction)
   WHERE j.primary_key IN $juris_pks
   OPTIONAL MATCH (j)-[r1:COVERS_STATE]->(s:State)
   OPTIONAL MATCH (cr:ChangeRequest)-[r2:APPLIES_TO_JURISDICTION]->(j)
   OPTIONAL MATCH (cr)-[r3:MANDATES_POLICY]->(cp:CoveragePolicy)
   OPTIONAL MATCH (reg:Regulation)-[r4:ISSUES_TRANSMITTAL]->(cr)
   OPTIONAL MATCH (sec:StatutorySection)-[r5:IMPLEMENTED_BY]->(reg)
   OPTIONAL MATCH (pl:PublicLaw)-[r6:MODIFIES_CODE]->(sec)
   OPTIONAL MATCH (p:Policy)-[r7:TARGETS_BILL]->(b:Bill)-[r8:ENACTED_AS]->(pl)
   RETURN j, r1, s, cr, r2, cp, r3, reg, r4, sec, r5, pl, r6, p, r7, b, r8
   ```
   - Convert and add all matched nodes (`j`, `s`, `cr`, `cp`, `reg`, `sec`, `pl`, `p`, `b`) and edges (`r1`..`r8`) to `nodes_by_pk`, `edges_by_key`, `active_node_pks`, and `active_edge_keys`.
2. Wire `_execute_jurisdiction_traversal`:
   - In `_execute_single_entity_traversal`: when `anchor.slot == "jurisdiction" or anchor.label == "Jurisdiction"`, call `self._execute_jurisdiction_traversal([anchor.primary_key], ...)`.
   - In `_execute_multi_entity_traversal`: when all anchors are `jurisdiction` anchors (or `jurisdiction` + `policy`/`changerequest`/`coveragepolicy` with no `state` or `diagnosis` anchors), call `self._execute_jurisdiction_traversal([a.primary_key for a in juris_anchors], ...)`.

### 3.2 Multi-State & State+HCPCS Comparative Traversal (`src/graphrag/traversal.py`)
In `_execute_multi_entity_traversal` (`src/graphrag/traversal.py`):
1. Extract `state_anchors = [a for a in anchors.all_anchors if a.slot == "state" or a.label == "State"]` and `hcpcs_anchors = [a for a in anchors.all_anchors if a.slot in ("hcpcs", "hcpcscode") or a.label == "HCPCSCode"]`.
2. When `state_anchors` is non-empty and `anchors.diagnosis_anchor` is `None` (covering both multi-state comparisons like `STATE-CA` + `STATE-NY` + `HCPCS-A6522` and single-state + HCPCS queries like `STATE-WI` + `HCPCS-A6522`):
   - For each `st_anchor` in `state_anchors`, invoke `self._execute_single_state_traversal(state_pk=st_anchor.primary_key, session=session, nodes_by_pk=nodes_by_pk, edges_by_key=edges_by_key, active_node_pks=active_node_pks, active_edge_keys=active_edge_keys, target_hcpcs_pks=[h.primary_key for h in hcpcs_anchors] if hcpcs_anchors else None)`.
   - Enhance `_execute_single_state_traversal` with an optional parameter `target_hcpcs_pks: Optional[List[str]] = None`:
     - When `target_hcpcs_pks` is provided, illuminate every requested `HCPCSCode` in `target_hcpcs_pks` and its corresponding non-rural `FeeScheduleEntry` for `state_pk` in `active_node_pks` and `active_edge_keys` (defaulting to `["HCPCS-A6522"]` when `target_hcpcs_pks` is `None`).
3. Also, if `len(state_anchors) >= 2` and `anchors.diagnosis_anchor` is present, execute `_execute_pattern_a` for each `st_anchor` in `state_anchors` so multi-state clinical routing queries also resolve both states cleanly.

### 3.3 Multi-State & Regional Context Assembly (`src/graphrag/context_assembler.py` & `src/graphrag/pipeline.py`)
1. **Section 2 (`Contractor & Region`) in `src/graphrag/context_assembler.py` (lines 75–88):**
   - Normalize contractor display name: if `"CGS"` in `contractor` and `"LLC"` not in `contractor`, format as `"CGS Administrators, LLC"`.
   - Map `COVERS_STATE` edges in `traversal_result.edges`: for each `Jurisdiction` node `j`, collect all `State` nodes `s` where an edge `j.primary_key -> COVERS_STATE -> s.primary_key` exists (sorted alphabetically by `state_code`).
   - Emit:
     - `- Regional Claims Contractor: [{j.primary_key}] {j_display_name} - {contractor}`
     - If covered states exist in `edges`:
       `- Covered States / Territories ({len(covered_states)}): ` followed by `, ".join(f"[{s.primary_key}] {s.properties.get('state_name') or s.name} ({s.properties.get('state_code')})" for s in covered_states)`
   - For each `State` node `s` in `state_nodes`, also find its parent `Jurisdiction` via `COVERS_STATE` edges and emit:
     `- Beneficiary State: [{s.primary_key}] {s_name} (Code: {s_code}, Governing Jurisdiction: [{parent_j_pk}] {parent_contractor})`
2. **Section 4 (`Fees and Patient Costs`) in `src/graphrag/context_assembler.py` (lines 126–164):**
   - Build header using all present `state_nodes` (e.g., if `1 <= len(state_nodes) <= 4`, join their names `", ".join(...)`; if `> 4`, use `"Regional Overview"`).
   - Include **ALL** non-rural `A6522` fee entries across all traversed states (`a6522_fees = [f for f in candidate_fees if f.properties.get("hcpcs_code") == "A6522"]`), sorted by `state_code`:
     ```python
     for a6522_fee in a6522_fees:
         st_c = a6522_fee.properties.get("state_code", "")
         amt = float(a6522_fee.properties.get("fee_amount", 0.0))
         coinsurance = round(amt * 0.20, 2)
         lines.append(
             f"- [{a6522_fee.primary_key}] (State: [STATE-{st_c}]) HCPCS A6522: Allowable Reimbursement = ${amt:.2f} "
             f"(Calculated 20% patient coinsurance = ${coinsurance:.2f})"
         )
     ```
   - For remaining non-`A6522` candidate fees (up to 6 per state or 8 total), include `[STATE-{st_c}]` alongside the `[{f.primary_key}]` identifier, dollar reimbursement amount, and 20% coinsurance.
3. **Pipeline Default State Code (`src/graphrag/pipeline.py`, lines 56–67):**
   - Replace the hardcoded `state_code = "WI"` default with `state_code = None`, populating `state_code` only when `anchors.state_anchor` or `request.state_code` is present.

---

## 4. Verification Criteria (`{correct required outputs}`)

- Query *"What states does Jurisdiction B cover?"* anchors to `JURIS-DME-B`, retrieves all 7 Midwestern states (`STATE-IL`, `STATE-IN`, `STATE-KY`, `STATE-MI`, `STATE-MN`, `STATE-OH`, `STATE-WI`), and synthesizes an answer naming `CGS Administrators` and all 7 states.
- Query *"Who administers Medicare Part B DME claims in Texas?"* anchors to `STATE-TX`, traverses to `JURIS-DME-C`, and identifies `CGS Administrators` and `CMS-CR-13286`.
- Query *"What contractor covers Florida?"* anchors to `STATE-FL`, traverses to `JURIS-DME-C`, and cites `CGS Administrators` and `CMS-CR-13286`.
- Query *"Compare allowable rates for A6522 between California and New York."* anchors to `HCPCS-A6522`, `STATE-CA`, and `STATE-NY`, includes `JURIS-DME-D`, `JURIS-DME-A`, `FEE-A6522-CA-NR-2024`, and `FEE-A6522-NY-NR-2024` in `active_node_pks`, and reports the fee schedule rates (`$290.47` and `$58.09` coinsurance) for both California and New York.
