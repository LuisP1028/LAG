# Master Component-to-Edit Matrix: Dual Jurisdiction and State Governance Architecture

- **Run ID:** `20261013T185957-734-5ytd`
- **Governing Specification:** [`functional_specification_008.md`](file:///Users/diesel/Desktop/LAG/.sandcastle/worktrees/agent-plan-20261013T185957-734-5ytd/functional_specification_008.md)
- **Taxonomy Reference:** [`LANGUAGE.md`](file:///Users/diesel/Desktop/LAG/.sandcastle/worktrees/agent-plan-20261013T185957-734-5ytd/LANGUAGE.md)

---

## 1. Summary Matrix of Targeted Components

| # | Repository-Relative File Path | Line Range | Target Symbols / Structures | Governing Ticket(s) | Requirement Traceability |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | [`src/api/routes.py`](file:///Users/diesel/Desktop/LAG/.sandcastle/worktrees/agent-plan-20261013T185957-734-5ytd/src/api/routes.py#L84-L250) | `L84–L250` | `get_graph_topology` | `ticket-001` | Req 5.2.1 (1, 2, 3, 4), AC 2, 3, 5 |
| 2 | [`src/graphrag/models.py`](file:///Users/diesel/Desktop/LAG/.sandcastle/worktrees/agent-plan-20261013T185957-734-5ytd/src/graphrag/models.py#L58-L65) | `L58–L65` | `GraphRAGQueryRequest` | `ticket-004` | Req 5.3.1, Req 5.3.2 |
| 3 | [`src/graphrag/entity_linker.py`](file:///Users/diesel/Desktop/LAG/.sandcastle/worktrees/agent-plan-20261013T185957-734-5ytd/src/graphrag/entity_linker.py#L15-L404) | `L15–L30`, `L102–L106`, `L231–L255`, `L351–L404` | `STATE_NAME_TO_CODE`, `resolve_anchors`, `_extract_jurisdiction_anchors`, `_extract_state_anchors`, `_extract_state_anchor` | `ticket-004` | Req 5.3.1, Req 5.3.2, AC 6 |
| 4 | [`src/graphrag/traversal.py`](file:///Users/diesel/Desktop/LAG/.sandcastle/worktrees/agent-plan-20261013T185957-734-5ytd/src/graphrag/traversal.py#L77-L376) | `L77–L214`, `L303–L376` | `_execute_single_entity_traversal`, `_execute_single_state_traversal`, `_execute_jurisdiction_traversal`, `_execute_multi_entity_traversal` | `ticket-005` | Req 5.3.1, Req 5.3.2, AC 6 |
| 5 | [`src/graphrag/context_assembler.py`](file:///Users/diesel/Desktop/LAG/.sandcastle/worktrees/agent-plan-20261013T185957-734-5ytd/src/graphrag/context_assembler.py#L70-L165) | `L70–L89`, `L123–L165` | `GraphContextAssembler.assemble_context` (Section 2 & Section 4) | `ticket-005` | Req 5.3.1, Req 5.3.2, AC 6 |
| 6 | [`src/graphrag/pipeline.py`](file:///Users/diesel/Desktop/LAG/.sandcastle/worktrees/agent-plan-20261013T185957-734-5ytd/src/graphrag/pipeline.py#L56-L67) | `L56–L67` | `GraphRAGPipeline.execute_query` | `ticket-005` | Req 5.3.1, Req 5.3.2, AC 6 |
| 7 | [`src/frontend/src/context/GraphSyncContext.tsx`](file:///Users/diesel/Desktop/LAG/.sandcastle/worktrees/agent-plan-20261013T185957-734-5ytd/src/frontend/src/context/GraphSyncContext.tsx#L17-L253) | `L17–L253` | `DME_JURISDICTIONS`, `STATE_TO_JURISDICTION`, `ALL_STATES_SORTED`, `GraphSyncContextType`, `GraphSyncProvider` | `ticket-002` | Req 5.1.1, Req 5.1.2, AC 1, 2, 3, 4, 5 |
| 8 | [`src/frontend/src/components/FilterToolbar.tsx`](file:///Users/diesel/Desktop/LAG/.sandcastle/worktrees/agent-plan-20261013T185957-734-5ytd/src/frontend/src/components/FilterToolbar.tsx#L9-L103) | `L9–L103` | `FilterToolbarProps`, `FilterToolbar` (`JURISDICTION:` and `STATE:` dropdowns) | `ticket-003` | Req 5.1.1, Req 5.1.2, AC 1, 2, 3, 4 |
| 9 | [`src/frontend/src/App.tsx`](file:///Users/diesel/Desktop/LAG/.sandcastle/worktrees/agent-plan-20261013T185957-734-5ytd/src/frontend/src/App.tsx#L16-L110) | `L16–L110` | `MainVisualizer` (`fetchTopology`, `useEffect`, error retry) | `ticket-002`, `ticket-003` | Req 5.1.1, Req 5.1.2, Req 5.2.1, AC 2, 5 |

---

## 2. Granular Component-by-Component Edit Specifications

### Component 1: `src/api/routes.py` (`L84–L250`) — Ticket 001
- **Function:** `get_graph_topology`
- **Changes:**
  1. Add query parameter `jurisdiction_filter: Optional[str] = Query(None, description="CMS DME MAC Jurisdiction ID (e.g. JURIS-DME-B) to filter regional contractor and covered states")`.
  2. Normalize `jurisdiction_filter`:
     - If `jurisdiction_filter` is `None` or `jurisdiction_filter.strip() == ""` or `jurisdiction_filter.strip().upper() == "ALL"`, set `clean_juris = None`.
     - Else normalize `"A"`, `"B"`, `"C"`, `"D"` or `"JURIS-DME-*"` to `JURIS-DME-{letter}` and validate existence in Neo4j (`MATCH (j:Jurisdiction {primary_key: $pk}) RETURN j.primary_key`). If not found, raise `HTTPException(status_code=400, detail={"error_type": "EntityResolutionError", "message": f"Unrecognized DME MAC jurisdiction '{jurisdiction_filter}'.", "details": {"jurisdiction_filter": jurisdiction_filter}})`.
  3. Normalize `state_filter`:
     - If `state_filter` is `None` or `state_filter.strip() == ""` or `state_filter.strip().upper() == "ALL"`, set `clean_state = None`.
     - Else strip `"STATE-"` prefix if present, uppercase to 2-letter code, and query `MATCH (j:Jurisdiction)-[:COVERS_STATE]->(s:State {state_code: $state_code}) RETURN s.primary_key AS s_pk, j.primary_key AS j_pk`. If not found, raise `HTTPException(status_code=400, detail={"error_type": "EntityResolutionError", "message": f"Unrecognized state code '{state_filter}'.", "details": {"state_filter": state_filter}})`.
  4. Apply Multi-Tier Topology Filtering:
     - Determine `allowed_juris_pks: Optional[Set[str]]` and `allowed_state_pks: Optional[Set[str]]`:
       - When `clean_state` is set: `allowed_state_pks = {f"STATE-{clean_state}"}` and `allowed_juris_pks = {parent_juris_pk}`.
       - When `clean_juris` is set and `clean_state` is `None`: query `MATCH (:Jurisdiction {primary_key: $juris_pk})-[:COVERS_STATE]->(s:State) RETURN collect(s.primary_key) AS spks`; set `allowed_juris_pks = {clean_juris}` and `allowed_state_pks = set(spks)`.
       - When both are `None`: `allowed_juris_pks = None`, `allowed_state_pks = None`.
     - Filter non-`FeeScheduleEntry` nodes and edges so that any `Jurisdiction` node not in `allowed_juris_pks` (when set) and any `State` node not in `allowed_state_pks` (when set) is excluded from `nodes_by_pk`, and only edges whose both endpoints are in `nodes_by_pk` are added to `edges_by_key`.
     - When `clean_state` is set, query non-rural `FeeScheduleEntry` nodes (`WHERE f.is_rural = false OR f.is_rural IS NULL`) for `state_code = clean_state` and add `f`, `r1` (`APPLIES_TO`), and `r2` (`HAS_FEE_SCHEDULE`).
     - When `include_fee_schedules` is `True` and `clean_state` is `None`, if `allowed_state_pks` is set, filter `all_fees_query` to `s.primary_key IN $state_pks AND (f.is_rural = false OR f.is_rural IS NULL)`.

### Component 2: `src/graphrag/models.py` (`L58–L65`) — Ticket 004
- **Class:** `GraphRAGQueryRequest`
- **Changes:**
  - Add `jurisdiction_code: Optional[str] = None` field to `GraphRAGQueryRequest`.

### Component 3: `src/graphrag/entity_linker.py` (`L15–L404`) — Ticket 004
- **Class:** `EntityAnchorLinker`
- **Changes:**
  1. In `STATE_NAME_TO_CODE` (`L15–L30`), add `"u.s. virgin islands": "VI"` and `"us virgin islands": "VI"`.
  2. In `resolve_anchors` (`L102–L148`):
     - Replace single `state_anchor = self._extract_state_anchor(clean_text, session)` call with `state_anchors = self._extract_state_anchors(clean_text, session, has_jurisdiction= bool(juris_anchors))` (calling `_extract_jurisdiction_anchors` before `_extract_state_anchors`, or passing `clean_text` and checking jurisdiction matches) so all matched `State` anchors are inserted into `anchors_by_pk` in order of appearance.
  3. In `_extract_jurisdiction_anchors` (`L231–L255`):
     - Match explicit jurisdiction letters A, B, C, D via regex patterns supporting `Jurisdiction A/B/C/D`, `DME MAC A/B/C/D`, `DME MAC Jurisdiction A/B/C/D`, `MAC Jurisdiction A/B/C/D`, and `JURIS-DME-A/B/C/D`.
     - If `"cgs"` / `"cgs administrators"` appears in `text` and neither `JURIS-DME-B` nor `JURIS-DME-C` was matched by explicit letter, resolve and append both `JURIS-DME-B` and `JURIS-DME-C`.
     - If `"noridian"` appears in `text` and neither `JURIS-DME-A` nor `JURIS-DME-D` was matched by explicit letter, resolve and append both `JURIS-DME-A` and `JURIS-DME-D`.
  4. In `_extract_state_anchors` (`L351–L404`):
     - Find all non-overlapping full state name matches across `lower_text` (checking longest state names first so `"west virginia"` claims its span before `"virginia"`), recording `(m.start(), AnchorEntity(...))`.
     - Find all 2-letter uppercase state code matches `\b{code}\b` in `text` for state codes not already matched, skipping ambiguous uppercase English prepositions (`"IN"`, `"OR"`, `"ME"`, `"HI"`, `"OK"`, `"DE"`, `"MA"`, `"PA"`, `"LA"`, `"OH"`) unless preceded by a comma/state separator or explicit state context.
     - Sort matched state anchors by `m.start()` ascending and return the list.
     - Keep `_extract_state_anchor` returning `anchors[0] if anchors else None`.
     - In the `GEO_LOCATION_INDICATORS` fail-fast check, only raise `EntityResolutionError` if zero `State` anchors and zero `Jurisdiction` anchors were found and the candidate does not contain jurisdiction/contractor/policy keywords (`"jurisdiction"`, `"mac"`, `"cgs"`, `"noridian"`, `"medicare"`, `"policy"`).

### Component 4: `src/graphrag/traversal.py` (`L77–L376`) — Ticket 005
- **Class:** `TopologicalTraversalEngine`
- **Changes:**
  1. In `_execute_single_entity_traversal` (`L77–L114`):
     - Add branch `elif anchor.slot == "jurisdiction" or anchor.label == "Jurisdiction":` calling `self._execute_jurisdiction_traversal(jurisdiction_pks=[anchor.primary_key], session=session, nodes_by_pk=nodes_by_pk, edges_by_key=edges_by_key, active_node_pks=active_node_pks, active_edge_keys=active_edge_keys)`.
  2. Add `_execute_jurisdiction_traversal` method:
     - Queries `(j:Jurisdiction)` where `j.primary_key IN $juris_pks`, `OPTIONAL MATCH (j)-[r1:COVERS_STATE]->(s:State)`, `OPTIONAL MATCH (cr:ChangeRequest)-[r2:APPLIES_TO_JURISDICTION]->(j)`, `OPTIONAL MATCH (cr)-[r3:MANDATES_POLICY]->(cp:CoveragePolicy)`, and upstream `Regulation`, `StatutorySection`, `PublicLaw`, `Policy`, `Bill`.
     - Adds all matched nodes and edges to `nodes_by_pk`, `edges_by_key`, `active_node_pks`, and `active_edge_keys`.
  3. Update `_execute_single_state_traversal` (`L115–L213`):
     - Add parameter `target_hcpcs_pks: Optional[List[str]] = None`.
     - When `target_hcpcs_pks` is provided, illuminate each `h_pk` in `target_hcpcs_pks` and its non-rural `FeeScheduleEntry` for `state_pk` in `active_node_pks` and `active_edge_keys` (defaulting to `["HCPCS-A6522"]` when `target_hcpcs_pks` is `None`).
  4. Update `_execute_multi_entity_traversal` (`L303–L376`):
     - Collect `state_anchors = [a for a in anchors.all_anchors if a.slot == "state" or a.label == "State"]`, `juris_anchors = [a for a in anchors.all_anchors if a.slot == "jurisdiction" or a.label == "Jurisdiction"]`, and `hcpcs_anchors = [a for a in anchors.all_anchors if a.slot in ("hcpcs", "hcpcscode") or a.label == "HCPCSCode"]`.
     - If `state_anchors` and `anchors.diagnosis_anchor`: call `_execute_pattern_a` (iterating over all `state_anchors` if `len(state_anchors) >= 2`).
     - If `state_anchors` and not `anchors.diagnosis_anchor`: for each `st_anchor` in `state_anchors`, call `_execute_single_state_traversal(state_pk=st_anchor.primary_key, ..., target_hcpcs_pks=[h.primary_key for h in hcpcs_anchors] if hcpcs_anchors else None)` and return.
     - If `juris_anchors` and not `state_anchors` and not `anchors.diagnosis_anchor`: call `_execute_jurisdiction_traversal(jurisdiction_pks=[j.primary_key for j in juris_anchors], ...)` and return.

### Component 5: `src/graphrag/context_assembler.py` (`L70–L165`) — Ticket 005
- **Class:** `GraphContextAssembler`
- **Changes:**
  1. In Section 2 (`Contractor & Region`, `L75–L88`):
     - Normalize `contractor` so `"CGS Administrators"` becomes `"CGS Administrators, LLC"`.
     - Build a map of `jurisdiction_pk -> List[TraversalNode]` from `COVERS_STATE` edges in `edges` (or matching `State` nodes in `nodes`).
     - For each `Jurisdiction` node `j`, emit `- Regional Claims Contractor: [{j.primary_key}] {j.name} - {contractor}` and, if covered states exist, `- Covered States / Territories ({len(covered)}): ` listing all covered `[STATE-XX] StateName (XX)` sorted by `state_code`.
     - For each `State` node `s`, emit `- Beneficiary State: [{s.primary_key}] {s_name}` (with its governing `Jurisdiction` if connected via `COVERS_STATE`).
  2. In Section 4 (`Fees and Patient Costs`, `L126–L164`):
     - Format the section header with all active state names when `1 <= len(state_nodes) <= 4` (e.g., `California, New York`), `"Regional Overview"` when `len(state_nodes) > 4`, or `state_code or "Overview"` when `state_nodes` is empty.
     - Emit **all** non-rural `A6522` fee entries in `candidate_fees` (`a6522_fees = sorted([f for f in candidate_fees if f.properties.get("hcpcs_code") == "A6522"], key=lambda x: x.properties.get("state_code", ""))`), including the state identifier `(State: [STATE-{st_code}])` on each line so multi-state comparisons include every compared state's `A6522` rate and 20% coinsurance.

### Component 6: `src/graphrag/pipeline.py` (`L56–L67`) — Ticket 005
- **Method:** `GraphRAGPipeline.execute_query`
- **Changes:**
  - Change default `state_code = "WI"` to `state_code = None`, setting `state_code` from `anchors.state_anchor` or `request.state_code` only when present.

### Component 7: `src/frontend/src/context/GraphSyncContext.tsx` (`L17–L253`) — Ticket 002
- **Structures:** `DME_JURISDICTIONS`, `STATE_TO_JURISDICTION`, `ALL_STATES_SORTED`, `GraphSyncContextType`, `GraphSyncProvider`
- **Changes:**
  1. Export `DME_JURISDICTIONS`, `STATE_TO_JURISDICTION`, and `ALL_STATES_SORTED` covering all 4 CMS DME MAC Jurisdictions (`JURIS-DME-A`, `JURIS-DME-B`, `JURIS-DME-C`, `JURIS-DME-D`) and all 53 states/territories.
  2. Add `filterJurisdiction: string`, `availableStates: StateOption[]`, and `setFilterJurisdiction: (jurisdiction: string) => void` to `GraphSyncContextType`.
  3. Initialize `filterJurisdiction` to `""`, `jurisdictionScope` to `""`, and `filterState` to `""`.
  4. Implement `setFilterJurisdiction`: updates `filterJurisdiction` and `jurisdictionScope`, resets `filterState` to `""`, and illuminates the selected `JURIS-DME-*` node and its covered `STATE-*` nodes and `COVERS_STATE` edges (or clears illumination when `""` is selected).
  5. Implement `setFilterState`: updates `filterState`, automatically updates `filterJurisdiction` to `STATE_TO_JURISDICTION[state]` when a state is selected, and illuminates `STATE-${state}` and its parent `JURIS-DME-*`.
  6. Compute `availableStates` via `useMemo`: returns the states of `DME_JURISDICTIONS[jurisdictionScope]` when `jurisdictionScope` is set, or `ALL_STATES_SORTED` when `jurisdictionScope` is `""`.

### Component 8: `src/frontend/src/components/FilterToolbar.tsx` (`L9–L103`) — Ticket 003
- **Component:** `FilterToolbar`
- **Changes:**
  1. Update `FilterToolbarProps` to `onReloadTopology: (state: string, policy: string, jurisdiction: string) => void`.
  2. Render the dedicated `JURISDICTION:` selector with the 5 exact options (`All Jurisdictions (National Overview)`, `Jurisdiction A (Northeast - Noridian)`, `Jurisdiction B (Midwest - CGS)`, `Jurisdiction C (South - CGS)`, `Jurisdiction D (West - Noridian)`).
  3. Render the dedicated `STATE:` selector with `All States (Overview)` and `availableStates.map(st => <option key={st.code} value={st.code}>{st.name} ({st.code})</option>)`.
  4. Wire `handleJurisdictionChange`, `handleStateChange`, and `handlePolicyChange` to synchronize `GraphSyncContext` and invoke `onReloadTopology(state, policy, jurisdiction)`.

### Component 9: `src/frontend/src/App.tsx` (`L16–L110`) — Ticket 002, Ticket 003
- **Component:** `MainVisualizer`
- **Changes:**
  1. Update `fetchTopology` signature to `(stateFilter = '', policy = 'LTA', jurisdictionFilter = '')` and append `jurisdiction_filter` to `URLSearchParams` when `jurisdictionFilter && jurisdictionFilter !== 'ALL'`.
  2. Update initial `useEffect` and retry button to call `fetchTopology('', 'LTA', '')`.
