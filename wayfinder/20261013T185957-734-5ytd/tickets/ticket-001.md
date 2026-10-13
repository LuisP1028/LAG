# Ticket 001: Multi-Tier Graph Topology Filtering Contract (`/api/graph/topology`)

- **Ticket ID:** `ticket-001`
- **Status:** `RESOLVED`
- **Claimed by:** `wayfinder-read-and-plan`
- **Blocked by:** None
- **Blocks:** `ticket-002`, `ticket-003`
- **Governing Specification:** `functional_specification_008.md` (Section 4, Requirement 5.2.1, Acceptance Criteria 2, 3, 5)

---

## 1. Decision Question

How must `GET /api/graph/topology` in `src/api/routes.py` filter and assemble graph nodes and edges when `jurisdiction_filter` and/or `state_filter` query parameters are supplied, while maintaining 60 FPS macro viewport rendering in the National Overview and failing fast on unrecognized filter codes?

---

## 2. Context & Root Cause Analysis

Currently, `get_graph_topology` in `src/api/routes.py` (lines 84–250):
1. Accepts only `policy_keyword`, `include_fee_schedules`, and `state_filter`. It lacks the `jurisdiction_filter` query parameter mandated by Requirement 5.2.1.1.
2. Executes an unfiltered `base_query` (`MATCH (n:PolicyNode) WHERE NOT n:FeeScheduleEntry ...`) that always returns all 4 `Jurisdiction` nodes and all 53 `State` nodes even when a specific state is selected.
3. Cannot filter the graph topology to a single regional CMS DME MAC contractor (`JURIS-DME-A`, `JURIS-DME-B`, `JURIS-DME-C`, or `JURIS-DME-D`) and its constituent `COVERS_STATE` states.
4. When `state_filter` is provided (lines 187–217), it matches `(f:FeeScheduleEntry)-[r1:APPLIES_TO]->(s:State {state_code: $state_code})` without filtering `f.is_rural = false` and without scoping the returned `State` and `Jurisdiction` nodes to the selected state and its parent regional contractor.

---

## 3. Locked Architectural Decision

### 3.1 Endpoint Signature (`src/api/routes.py`)
Update `get_graph_topology` signature (lines 84–90) to accept both `jurisdiction_filter` and `state_filter`:
```python
@router.get("/graph/topology", response_model=TopologyResponse)
def get_graph_topology(
    policy_keyword: Optional[str] = Query("LTA", description="Policy filter (LTA, IVIG, or all)"),
    include_fee_schedules: bool = Query(False, description="Whether to include all 3,800+ fee schedule nodes"),
    jurisdiction_filter: Optional[str] = Query(None, description="CMS DME MAC Jurisdiction ID (e.g. JURIS-DME-B) to filter regional contractor and covered states"),
    state_filter: Optional[str] = Query(None, description="2-letter state code (e.g. WI, OH, NY) to expand state-specific non-rural fees"),
    session: Session = Depends(get_neo4j_session),
):
```

### 3.2 Parameter Normalization & Fail-Fast Validation
1. **Normalize `jurisdiction_filter`:**
   - Treat `None`, `""`, or case-insensitive `"ALL"` as no jurisdiction filter (`clean_juris = None`).
   - Otherwise, strip whitespace and uppercase:
     - If value is in `{"A", "B", "C", "D"}`, normalize to `f"JURIS-DME-{val}"`.
     - If value starts with `"JURIS-"` or `"DME-"` but not `"JURIS-DME-"`, normalize to `f"JURIS-DME-{val.replace('JURIS-', '').replace('DME-', '')}"`.
     - Verify the `Jurisdiction` node exists in Neo4j:
       `MATCH (j:Jurisdiction {primary_key: $juris_pk}) RETURN j.primary_key AS pk`.
       If no record exists, raise `HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"error_type": "EntityResolutionError", "message": f"Unrecognized DME MAC jurisdiction '{jurisdiction_filter}'.", "details": {"jurisdiction_filter": jurisdiction_filter}})`.
2. **Normalize `state_filter`:**
   - Treat `None`, `""`, or case-insensitive `"ALL"` as no state filter (`clean_state = None`).
   - Otherwise, strip whitespace, uppercase, and strip leading `"STATE-"` prefix if present to obtain the 2-letter postal code `clean_state` (e.g., `"OH"`, `"NY"`, `"WI"`).
   - Verify the `State` node and its parent `Jurisdiction` exist in Neo4j:
     `MATCH (j:Jurisdiction)-[:COVERS_STATE]->(s:State {state_code: $state_code}) RETURN s.primary_key AS s_pk, j.primary_key AS j_pk`.
     If no record exists, raise `HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"error_type": "EntityResolutionError", "message": f"Unrecognized state code '{state_filter}'.", "details": {"state_filter": state_filter}})`.

### 3.3 Multi-Tier Filtering Behavior
1. **Mode 1 — State-Level Filter (`clean_state` is present):**
   - Resolve `target_state_pk = f"STATE-{clean_state}"` and its parent `parent_juris_pk` from `(j:Jurisdiction)-[:COVERS_STATE]->(s:State {state_code: $state_code})`.
   - Fetch all non-`FeeScheduleEntry` nodes and edges where:
     - Any node with label `State` must have `primary_key == target_state_pk`.
     - Any node with label `Jurisdiction` must have `primary_key == parent_juris_pk`.
     - All other non-`FeeScheduleEntry` nodes (`Policy`, `Bill`, `PublicLaw`, `StatutorySection`, `Regulation`, `ChangeRequest`, `CoveragePolicy`, `HCPCSCode`, `ICD10Code`, `LobbyingFiling`, `LiteratureStudy`, `CBOScore`) and their interconnecting edges are included.
   - Expand localized non-rural `FeeScheduleEntry` nodes for `clean_state`:
     ```cypher
     MATCH (f:FeeScheduleEntry)-[r1:APPLIES_TO]->(s:State {state_code: $state_code})
     WHERE f.is_rural = false OR f.is_rural IS NULL
     MATCH (h:HCPCSCode)-[r2:HAS_FEE_SCHEDULE]->(f)
     RETURN f, r1, s, h, r2
     ```
   - Resulting node count for any single state is `155 - 52 - 3 + 71 = 171` nodes (which is `> 155` base nodes and `< 500`, satisfying both Requirement 5.2.1.3 and existing topology density bounds).

2. **Mode 2 — Jurisdiction-Level Filter (`clean_juris` is present and `clean_state` is `None`):**
   - Query the covered state primary keys for `clean_juris`:
     `MATCH (j:Jurisdiction {primary_key: $juris_pk})-[:COVERS_STATE]->(s:State) RETURN collect(s.primary_key) AS state_pks`.
   - Fetch all non-`FeeScheduleEntry` nodes and edges where:
     - Any node with label `Jurisdiction` must have `primary_key == clean_juris`.
     - Any node with label `State` must have `primary_key IN state_pks`.
     - All other non-`FeeScheduleEntry` nodes (`Policy`, `Bill`, `PublicLaw`, `StatutorySection`, `Regulation`, `ChangeRequest`, `CoveragePolicy`, `HCPCSCode`, `ICD10Code`, `LobbyingFiling`, `LiteratureStudy`, `CBOScore`) and their edges connecting included nodes are returned.
   - `FeeScheduleEntry` nodes remain collapsed (0 fee schedule nodes) unless `include_fee_schedules=True` is explicitly passed, in which case only non-rural `FeeScheduleEntry` nodes applying to `state_pks` are expanded.

3. **Mode 3 — National Overview (`clean_juris` is `None` and `clean_state` is `None`):**
   - Returns all non-`FeeScheduleEntry` nodes (all 4 `Jurisdiction` nodes, all 53 `State` nodes, and all legislative/regulatory/clinical nodes = 155 nodes) and their edges.
   - `FeeScheduleEntry` nodes remain collapsed unless `include_fee_schedules=True` is explicitly passed.

---

## 4. Verification Criteria (`{correct required outputs}`)

- `GET /api/graph/topology` (or `?jurisdiction_filter=ALL&state_filter=ALL`) returns HTTP 200 with all 4 `Jurisdiction` nodes, all 53 `State` nodes, and 0 `FeeScheduleEntry` nodes (`total_nodes == 155 < 500`).
- `GET /api/graph/topology?jurisdiction_filter=JURIS-DME-B` returns HTTP 200 with `JURIS-DME-B` as the sole `Jurisdiction` node, the 7 Midwestern states (`IL`, `IN`, `KY`, `MI`, `MN`, `OH`, `WI`) as the sole `State` nodes, governing `ChangeRequest` (`CMS-CR-13286`, `CMS-CR-13217`) and `CoveragePolicy` (`CMS-MCD-A59508`, `CMS-MCD-A59588`) nodes, and 0 `FeeScheduleEntry` nodes.
- `GET /api/graph/topology?state_filter=OH` returns HTTP 200 with `STATE-OH` as the sole `State` node, `JURIS-DME-B` as the sole `Jurisdiction` node, and 71 non-rural `FeeScheduleEntry` nodes with `state_code == "OH"` (`total_nodes == 171 > 155`).
- `GET /api/graph/topology?state_filter=ZZ` or `GET /api/graph/topology?jurisdiction_filter=JURIS-INVALID` returns HTTP 400 with `error_type == "EntityResolutionError"`.
