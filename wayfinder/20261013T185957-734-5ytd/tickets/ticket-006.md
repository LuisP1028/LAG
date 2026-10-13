# Ticket 006: End-to-End Integration Test Architecture, Payload Admissibility, and Verification Oracles for Dual Jurisdiction and State Governance

- **Ticket ID:** `ticket-006`
- **Status:** `RESOLVED`
- **Claimed by:** `wayfinder-test-plan`
- **Blocked by:** `ticket-001`, `ticket-002`, `ticket-003`, `ticket-004`, `ticket-005`
- **Blocks:** None
- **Governing Specification:** [`functional_specification_008.md`](file:///Users/diesel/Desktop/LAG/.sandcastle/worktrees/agent-plan-20261013T185957-734-5ytd/functional_specification_008.md) (Section 4, Requirements 5.1.1, 5.1.2, 5.2.1, 5.3.1, 5.3.2, Acceptance Criteria 1–6)
- **Taxonomy Reference:** [`LANGUAGE.md`](file:///Users/diesel/Desktop/LAG/.sandcastle/worktrees/agent-plan-20261013T185957-734-5ytd/LANGUAGE.md)

---

## 1. Decision Question

How must the integration test suite verify the 9 modified components in `handoff/20261013T185957-734-5ytd/implementer.txt` and `handoff/20261013T185957-734-5ytd/reviewer.txt` against [`functional_specification_008.md`](file:///Users/diesel/Desktop/LAG/.sandcastle/worktrees/agent-plan-20261013T185957-734-5ytd/functional_specification_008.md) and locked tickets `ticket-001` through `ticket-005` using exclusively real Neo4j database state, authentic codebase schemas, and real component execution with zero mocks or synthesized payloads?

---

## 2. Context & Architectural Boundaries

The implementation of [`functional_specification_008.md`](file:///Users/diesel/Desktop/LAG/.sandcastle/worktrees/agent-plan-20261013T185957-734-5ytd/functional_specification_008.md) spans 9 repository components across two runtime tiers:

1. **Backend API & GraphRAG Tier (Python / FastAPI / Neo4j):**
   - [`src/api/routes.py`](file:///Users/diesel/Desktop/LAG/.sandcastle/worktrees/agent-plan-20261013T185957-734-5ytd/src/api/routes.py#L84-L342) (`get_graph_topology`, `resolve_entities`, `get_subgraph_by_anchors`, `execute_graphrag_query`)
   - [`src/graphrag/models.py`](file:///Users/diesel/Desktop/LAG/.sandcastle/worktrees/agent-plan-20261013T185957-734-5ytd/src/graphrag/models.py#L7-L76) (`AnchorEntity`, `ResolvedAnchors`, `TraversalNode`, `TraversalEdge`, `TraversalResult`, `GraphRAGQueryRequest`, `GraphRAGQueryResponse`)
   - [`src/graphrag/entity_linker.py`](file:///Users/diesel/Desktop/LAG/.sandcastle/worktrees/agent-plan-20261013T185957-734-5ytd/src/graphrag/entity_linker.py#L11-L590) (`EntityAnchorLinker.STATE_NAME_TO_CODE`, `resolve_anchors`, `_extract_jurisdiction_anchors`, `_extract_state_anchors`, `_extract_state_anchor`)
   - [`src/graphrag/traversal.py`](file:///Users/diesel/Desktop/LAG/.sandcastle/worktrees/agent-plan-20261013T185957-734-5ytd/src/graphrag/traversal.py#L18-L801) (`TopologicalTraversalEngine.extract_connecting_subgraph`, `_execute_single_entity_traversal`, `_execute_jurisdiction_traversal`, `_execute_single_state_traversal`, `_execute_multi_entity_traversal`)
   - [`src/graphrag/context_assembler.py`](file:///Users/diesel/Desktop/LAG/.sandcastle/worktrees/agent-plan-20261013T185957-734-5ytd/src/graphrag/context_assembler.py#L7-L239) (`GraphContextAssembler.assemble_context`, `_resolve_contractor_name`, `_format_fee_line`)
   - [`src/graphrag/pipeline.py`](file:///Users/diesel/Desktop/LAG/.sandcastle/worktrees/agent-plan-20261013T185957-734-5ytd/src/graphrag/pipeline.py#L20-L96) (`GraphRAGPipeline.execute_query`)

2. **Frontend Navigation & Bidirectional Sync Bus Tier (TypeScript / React):**
   - [`src/frontend/src/context/GraphSyncContext.tsx`](file:///Users/diesel/Desktop/LAG/.sandcastle/worktrees/agent-plan-20261013T185957-734-5ytd/src/frontend/src/context/GraphSyncContext.tsx#L17-L474) (`StateOption`, `JurisdictionMetadata`, `DME_JURISDICTIONS`, `STATE_TO_JURISDICTION`, `ALL_STATES_SORTED`, `GraphSyncContextType`, `GraphSyncProvider`)
   - [`src/frontend/src/components/FilterToolbar.tsx`](file:///Users/diesel/Desktop/LAG/.sandcastle/worktrees/agent-plan-20261013T185957-734-5ytd/src/frontend/src/components/FilterToolbar.tsx#L9-L184) (`FilterToolbarProps`, `FilterToolbar`)
   - [`src/frontend/src/App.tsx`](file:///Users/diesel/Desktop/LAG/.sandcastle/worktrees/agent-plan-20261013T185957-734-5ytd/src/frontend/src/App.tsx#L10-L154) (`MainVisualizer`, `fetchTopology`)

---

## 3. Locked Architectural Decisions for Integration Testing

### 3.1 Payload Admissibility Decision (`INV-PAYLOAD-01`)

1. **Zero Mocks & Real Producer Grounding:**
   - All backend integration tests must execute against a live Neo4j driver session provisioned by [`Neo4jSyncEngine`](file:///Users/diesel/Desktop/LAG/.sandcastle/worktrees/agent-plan-20261013T185957-734-5ytd/src/graph/neo4j_sync.py#L24-L86) (`bolt://localhost:7687`, database `neo4j`) and FastAPI `TestClient(app)` bound to [`src/api/server.py`](file:///Users/diesel/Desktop/LAG/.sandcastle/worktrees/agent-plan-20261013T185957-734-5ytd/src/api/server.py#L38-L105).
   - No `unittest.mock`, `MagicMock`, `monkeypatch`, synthetic `TraversalResult` objects, or fabricated Neo4j records are permitted anywhere in the integration test suite.
2. **Authentic Codebase Schema Grounding:**
   - Every request and response payload must conform 100% to the active Pydantic models in [`src/api/models.py`](file:///Users/diesel/Desktop/LAG/.sandcastle/worktrees/agent-plan-20261013T185957-734-5ytd/src/api/models.py) and [`src/graphrag/models.py`](file:///Users/diesel/Desktop/LAG/.sandcastle/worktrees/agent-plan-20261013T185957-734-5ytd/src/graphrag/models.py), and the TypeScript interfaces in [`src/frontend/src/context/GraphSyncContext.tsx`](file:///Users/diesel/Desktop/LAG/.sandcastle/worktrees/agent-plan-20261013T185957-734-5ytd/src/frontend/src/context/GraphSyncContext.tsx), [`src/frontend/src/components/FilterToolbar.tsx`](file:///Users/diesel/Desktop/LAG/.sandcastle/worktrees/agent-plan-20261013T185957-734-5ytd/src/frontend/src/components/FilterToolbar.tsx), and [`src/frontend/src/types/graph.ts`](file:///Users/diesel/Desktop/LAG/.sandcastle/worktrees/agent-plan-20261013T185957-734-5ytd/src/frontend/src/types/graph.ts):
     - **`GET /api/graph/topology` Query Parameters:** `policy_keyword: Optional[str]`, `include_fee_schedules: bool`, `jurisdiction_filter: Optional[str]`, `state_filter: Optional[str]`.
     - **`TopologyResponse` (`src/api/models.py`):** `nodes: List[TopologyNode]`, `edges: List[TopologyEdge]`, `total_nodes: int`, `total_edges: int`.
     - **`TopologyNode` (`src/api/models.py`):** `primary_key: str`, `label: str`, `name: str`, `properties: Dict[str, Any]`.
     - **`TopologyEdge` (`src/api/models.py`):** `source_pk: str`, `target_pk: str`, `label: str`, `edge_key: str`, `provenance: Dict[str, Any]` (carrying `source_uri`, `selector`, `ingestion_timestamp`, `run_id`).
     - **`ErrorEnvelope` (`src/api/models.py` & `src/api/server.py`):** `error: bool`, `error_type: str`, `message: str`, `details: Dict[str, Any]`, `timestamp: str`.
     - **`GraphRAGQueryRequest` (`src/graphrag/models.py`):** `query: str`, `model_id: Optional[str]`, `state_code: Optional[str] = None`, `jurisdiction_code: Optional[str] = None`, `primary_key: Optional[str] = None`, `anchor_node_pk: Optional[str] = None`.
     - **`GraphRAGQueryResponse` (`src/graphrag/models.py`):** `answer: str`, `active_node_pks: List[str]`, `active_edge_keys: List[str]`, `anchors: List[AnchorEntity]`, `provenance_sources: List[Dict[str, Any]]`, `duration_ms: float`.
     - **`ResolvedAnchors` (`src/graphrag/models.py`):** `all_anchors: List[AnchorEntity]`, `state_anchor: Optional[AnchorEntity]`, `diagnosis_anchor: Optional[AnchorEntity]`, `policy_anchor: Optional[AnchorEntity]`, `hcpcs_anchor: Optional[AnchorEntity]`, `jurisdiction_anchor: Optional[AnchorEntity]`, `change_request_anchor: Optional[AnchorEntity]`, `coverage_policy_anchor: Optional[AnchorEntity]`.
3. **Observed Sparse & Optional Packing Preservation:**
   - Optional fields (`jurisdiction_filter`, `state_filter`, `state_code`, `jurisdiction_code`, `primary_key`, `anchor_node_pk`) must remain omitted (`None` / `undefined`) when testing default National Overview, regional-only queries, or natural-language-only queries.

---

### 3.2 Component Boundary & Verification Oracle Decisions (`INV-ASSERTION-01`)

#### Boundary 1: Multi-Tier Topology Filtering Contract (`src/api/routes.py`) — Ticket 001 & Requirement 5.2.1
1. **National Overview Mode (`jurisdiction_filter` omitted or `"ALL"`, `state_filter` omitted or `"ALL"`):**
   - **Admissible Input:** `GET /api/graph/topology` and `GET /api/graph/topology?jurisdiction_filter=ALL&state_filter=ALL`.
   - **`{correct required outputs}`:**
     - HTTP status `200`.
     - `total_nodes == 155` (`< 500` macro viewport performance bound per Requirement 5.2.1.4 & Acceptance Criterion 5).
     - Exactly `4` nodes with `label == "Jurisdiction"`: `{"JURIS-DME-A", "JURIS-DME-B", "JURIS-DME-C", "JURIS-DME-D"}`.
     - Exactly `53` nodes with `label == "State"` (all 50 US states + `DC`, `PR`, `VI`).
     - Exactly `0` nodes with `label == "FeeScheduleEntry"`.
     - Exactly `53` edges with `label == "COVERS_STATE"` (`12` from `JURIS-DME-A`, `7` from `JURIS-DME-B`, `17` from `JURIS-DME-C`, `17` from `JURIS-DME-D`).
2. **Jurisdiction-Level Filter Mode (`jurisdiction_filter` provided, `state_filter` omitted):**
   - **Admissible Inputs:**
     - `GET /api/graph/topology?jurisdiction_filter=JURIS-DME-A` (and shorthand `jurisdiction_filter=A`)
     - `GET /api/graph/topology?jurisdiction_filter=JURIS-DME-B` (and shorthand `jurisdiction_filter=B`)
     - `GET /api/graph/topology?jurisdiction_filter=JURIS-DME-C` (and shorthand `jurisdiction_filter=C`)
     - `GET /api/graph/topology?jurisdiction_filter=JURIS-DME-D` (and shorthand `jurisdiction_filter=D`)
   - **`{correct required outputs}`:**
     - HTTP status `200`.
     - Exactly `1` node with `label == "Jurisdiction"`, matching the normalized `JURIS-DME-{A|B|C|D}` primary key.
     - `State` nodes strictly equal to the `COVERS_STATE` states for that jurisdiction:
       - `JURIS-DME-A`: `12` states (`CT`, `DC`, `DE`, `MA`, `MD`, `ME`, `NH`, `NJ`, `NY`, `PA`, `RI`, `VT`), `total_nodes == 111`.
       - `JURIS-DME-B`: `7` states (`IL`, `IN`, `KY`, `MI`, `MN`, `OH`, `WI`), `total_nodes == 106`.
       - `JURIS-DME-C`: `17` states (`AL`, `AR`, `CO`, `FL`, `GA`, `LA`, `MS`, `NC`, `NM`, `OK`, `PR`, `SC`, `TN`, `TX`, `VA`, `VI`, `WV`), `total_nodes == 116`.
       - `JURIS-DME-D`: `17` states (`AK`, `AZ`, `CA`, `HI`, `IA`, `ID`, `KS`, `MO`, `MT`, `ND`, `NE`, `NV`, `OR`, `SD`, `UT`, `WA`, `WY`), `total_nodes == 116`.
     - Includes governing `Policy` (`POLICY-LTA`, `POLICY-IVIG`), `ChangeRequest` (`CMS-CR-13286`, `CMS-CR-13217`), and `CoveragePolicy` (`CMS-MCD-A59508`, `CMS-MCD-A59588`) nodes.
     - Exactly `0` nodes with `label == "FeeScheduleEntry"` when `include_fee_schedules=False`.
     - Every returned `TopologyEdge` has both `source_pk` and `target_pk` present in the returned `nodes` set (zero dangling edges).
3. **State-Level Filter Mode (`state_filter` provided across all 50 US states + territories):**
   - **Admissible Inputs:** `GET /api/graph/topology?state_filter=OH`, `GET /api/graph/topology?state_filter=NY`, `GET /api/graph/topology?state_filter=CA`, `GET /api/graph/topology?state_filter=TX`, `GET /api/graph/topology?state_filter=STATE-FL`, and parameterized verification across all 50 US states.
   - **`{correct required outputs}`:**
     - HTTP status `200`.
     - Exactly `1` `State` node (`STATE-{code}`) and `1` parent `Jurisdiction` node matching the authoritative CMS DME MAC assignment (`OH` -> `JURIS-DME-B`, `NY` -> `JURIS-DME-A`, `CA` -> `JURIS-DME-D`, `TX` -> `JURIS-DME-C`, `FL` -> `JURIS-DME-C`).
     - Exactly `71` non-rural `FeeScheduleEntry` nodes (`properties["state_code"] == code` and `properties.get("is_rural") in (False, None)`), yielding `total_nodes == 171` (`155 < total_nodes < 500`).
     - Every `FeeScheduleEntry` node is linked via `HAS_FEE_SCHEDULE` from its `HCPCSCode` node and `APPLIES_TO` to `STATE-{code}`.
4. **Fail-Fast Validation (`{errors}`):**
   - **Admissible Inputs:** `GET /api/graph/topology?state_filter=ZZ`, `GET /api/graph/topology?jurisdiction_filter=JURIS-INVALID`.
   - **`{errors}` Oracle:** Raises HTTP `400` (`status_code == 400`) with `error_type == "EntityResolutionError"` and `details` identifying the invalid `state_filter` or `jurisdiction_filter`.

---

#### Boundary 2: Multi-State & Regional Contractor Entity Anchor Resolution (`src/graphrag/entity_linker.py` & `src/graphrag/models.py`) — Ticket 004 & Requirements 5.3.1, 5.3.2
1. **Regional Jurisdiction Lexical Resolution:**
   - **Admissible Inputs:**
     - `"What states does Jurisdiction B cover?"`
     - `"What is DME MAC A?"`, `"What is DME MAC C?"`, `"What is Jurisdiction D?"`
     - `"What policies does CGS administer?"`
     - `"Which states does Noridian Healthcare Solutions administer?"`
   - **`{correct required outputs}`:**
     - `"What states does Jurisdiction B cover?"` resolves `jurisdiction_anchor.primary_key == "JURIS-DME-B"` and `"JURIS-DME-B"` in `primary_keys` without raising `EntityResolutionError`.
     - `"What policies does CGS administer?"` resolves both `"JURIS-DME-B"` and `"JURIS-DME-C"` in `primary_keys`.
     - `"Which states does Noridian Healthcare Solutions administer?"` resolves both `"JURIS-DME-A"` and `"JURIS-DME-D"` in `primary_keys`.
     - Prepositional jurisdiction phrases such as `"in Jurisdiction B"` or `"in DME MAC C"` do not trigger false-positive `GEO_LOCATION_INDICATORS` errors.
2. **Multi-State Comparative Resolution & 53-State Coverage:**
   - **Admissible Inputs:**
     - `"Compare allowable rates for A6522 between California and New York."`
     - `"Who administers Medicare Part B DME claims in Texas?"`
     - `"What contractor covers Florida?"`
     - `"Compare lymphedema coverage between West Virginia and Virginia."`
     - `"What is covered in U.S. Virgin Islands and Puerto Rico?"`
   - **`{correct required outputs}`:**
     - `"Compare allowable rates for A6522 between California and New York."` resolves `["STATE-CA", "STATE-NY"]` as state anchors in order of appearance (`state_anchor.primary_key == "STATE-CA"`) alongside `hcpcs_anchor.primary_key == "HCPCS-A6522"`.
     - `"Compare lymphedema coverage between West Virginia and Virginia."` resolves both `"STATE-WV"` and `"STATE-VA"` without overlapping span collision.
     - `"What is covered in U.S. Virgin Islands and Puerto Rico?"` resolves both `"STATE-VI"` and `"STATE-PR"`.
     - Every entry in `EntityAnchorLinker.STATE_NAME_TO_CODE` resolves to an existing `State` node in Neo4j covering all 50 US states + `DC`, `PR`, `VI` (`53` unique state codes).
3. **Fail-Fast Unrecognized Location (`{errors}`):**
   - **Admissible Input:** `"I am from Atlantis and need supplies"`.
   - **`{errors}` Oracle:** Raises `EntityResolutionError` with `details == {"extracted_geo": "Atlantis"}`.

---

#### Boundary 3: Regional Lineage & Cross-Jurisdiction Comparative Traversal and Context Assembly (`src/graphrag/traversal.py`, `src/graphrag/context_assembler.py`, `src/graphrag/pipeline.py`) — Ticket 005 & Requirements 5.3.1, 5.3.2, Acceptance Criterion 6
1. **Single-Jurisdiction & Multi-Jurisdiction Contractor Traversal (`_execute_jurisdiction_traversal`):**
   - **Admissible Inputs:**
     - `ResolvedAnchors` from `"What states does Jurisdiction B cover?"` (`JURIS-DME-B`).
     - `ResolvedAnchors` from `"What policies does CGS administer?"` (`JURIS-DME-B`, `JURIS-DME-C`).
   - **`{correct required outputs}`:**
     - For `JURIS-DME-B`, `extract_connecting_subgraph` returns `JURIS-DME-B`, all 7 covered Midwestern `State` nodes (`STATE-IL`, `STATE-IN`, `STATE-KY`, `STATE-MI`, `STATE-MN`, `STATE-OH`, `STATE-WI`), all 7 `JURIS-DME-B->COVERS_STATE->STATE-*` edges, governing `ChangeRequest` nodes (`CMS-CR-13286`, `CMS-CR-13217`), `CoveragePolicy` nodes (`CMS-MCD-A59508`, `CMS-MCD-A59588`), and upstream `Regulation` (`FR-2023-24455`), `StatutorySection` (`USC-42-1395x-s-2-JJ`), `PublicLaw` (`PLAW-117-328`), and `Policy` (`POLICY-LTA`, `POLICY-IVIG`) nodes in `active_node_pks`.
     - `GraphContextAssembler.assemble_context` Section 2 emits `- Regional Claims Contractor: [JURIS-DME-B] DME MAC Jurisdiction B - CGS Administrators, LLC` and `- Covered States / Territories (7): [STATE-IL] Illinois (IL), [STATE-IN] Indiana (IN), [STATE-KY] Kentucky (KY), [STATE-MI] Michigan (MI), [STATE-MN] Minnesota (MN), [STATE-OH] Ohio (OH), [STATE-WI] Wisconsin (WI)`.
2. **State Administrative Lineage Traversal (`_execute_single_state_traversal`):**
   - **Admissible Inputs:**
     - `ResolvedAnchors` from `"Who administers Medicare Part B DME claims in Texas?"` (`STATE-TX`).
     - `ResolvedAnchors` from `"What contractor covers Florida?"` (`STATE-FL`).
   - **`{correct required outputs}`:**
     - Traverses from `STATE-TX` (or `STATE-FL`) to parent `JURIS-DME-C`, `CMS-CR-13286`, and `CMS-MCD-A59508`.
     - `assemble_context` Section 2 emits `[JURIS-DME-C] DME MAC Jurisdiction C - CGS Administrators, LLC` and `- Beneficiary State: [STATE-TX] Texas (Code: TX, Governing Jurisdiction: [JURIS-DME-C] CGS Administrators, LLC)`.
3. **Cross-Jurisdiction Multi-State & Procedure Rate Comparison (`_execute_multi_entity_traversal` & `assemble_context` Section 4):**
   - **Admissible Input:** `ResolvedAnchors` from `"Compare allowable rates for A6522 between California and New York."` (`STATE-CA`, `STATE-NY`, `HCPCS-A6522`).
   - **`{correct required outputs}`:**
     - `extract_connecting_subgraph` traverses both states via `_execute_single_state_traversal` with `target_hcpcs_pks=["HCPCS-A6522"]`.
     - `active_node_pks` contains `STATE-CA`, `STATE-NY`, `JURIS-DME-D`, `JURIS-DME-A`, `HCPCS-A6522`, `FEE-A6522-CA-NR-2024`, and `FEE-A6522-NY-NR-2024` (and does not pollute `active_node_pks` with unrelated states or `allShortestPaths` noise).
     - `assemble_context` Section 4 header reads `### 4. Fees and Patient Costs (California, New York, 2024)` (or sorted state order) and emits **both** state `A6522` fee lines:
       - `- [FEE-A6522-CA-NR-2024] (State: [STATE-CA]) HCPCS A6522: Allowable Reimbursement = $290.47 (Calculated 20% patient coinsurance = $58.09)`
       - `- [FEE-A6522-NY-NR-2024] (State: [STATE-NY]) HCPCS A6522: Allowable Reimbursement = $290.47 (Calculated 20% patient coinsurance = $58.09)`
4. **Pipeline Default State Code & End-to-End Query Execution (`src/graphrag/pipeline.py` & `POST /api/graphrag/query`):**
   - **Admissible Inputs:**
     - `GraphRAGQueryRequest(query="What states does Jurisdiction B cover?")` (with `state_code=None`, `jurisdiction_code=None`).
     - `GraphRAGQueryRequest(query="Who administers Medicare Part B DME claims in Texas?")`.
     - `GraphRAGQueryRequest(query="Compare allowable rates for A6522 between California and New York.")`.
   - **`{correct required outputs}`:**
     - When `request.state_code` is `None` and no state anchor is in the query, `pipeline.execute_query` passes `state_code=None` (never defaulting to `"WI"`).
     - Live `POST /api/graphrag/query` (when `HF_TOKEN` is configured) or pipeline execution returns `GraphRAGQueryResponse` with non-empty `answer`, verified `anchors`, `active_node_pks`, `active_edge_keys`, and `provenance_sources`.

---

#### Boundary 4: Frontend 50-State & 4-Jurisdiction Registry, Cascading Sync Bus, and Dual Selectors (`src/frontend/src/context/GraphSyncContext.tsx`, `src/frontend/src/components/FilterToolbar.tsx`, `src/frontend/src/App.tsx`) — Tickets 002 & 003, Requirements 5.1.1 & 5.1.2, Acceptance Criteria 1–5
1. **Authoritative Registry Alignment (`GraphSyncContext.tsx`):**
   - **`{correct required outputs}`:**
     - `DME_JURISDICTIONS` defines exactly `JURIS-DME-A` (12 states/territories, Noridian Healthcare Solutions), `JURIS-DME-B` (7 states, CGS Administrators, LLC), `JURIS-DME-C` (17 states/territories, CGS Administrators, LLC), and `JURIS-DME-D` (17 states, Noridian Healthcare Solutions).
     - `ALL_STATES_SORTED` contains all `53` states/territories (including all 50 US states + `DC`, `PR`, `VI`) sorted alphabetically by state name, matching the 53 `State` nodes and `COVERS_STATE` edges in Neo4j 1-for-1.
     - `STATE_TO_JURISDICTION` maps all 53 state codes to their exact parent `JURIS-DME-{A|B|C|D}` identifier (e.g., `STATE_TO_JURISDICTION["OH"] === "JURIS-DME-B"`, `STATE_TO_JURISDICTION["NY"] === "JURIS-DME-A"`, `STATE_TO_JURISDICTION["TX"] === "JURIS-DME-C"`, `STATE_TO_JURISDICTION["CA"] === "JURIS-DME-D"`).
2. **Bidirectional Cascading & Illumination Synchronization (`GraphSyncContext.tsx` & `FilterToolbar.tsx`):**
   - **`{correct required outputs}`:**
     - Initial state: `filterJurisdiction === ""`, `filterState === ""`, `availableStates.length === 53`.
     - `FilterToolbar.tsx` renders two distinct selectors labeled `JURISDICTION:` (`aria-label="JURISDICTION"`, `data-testid="jurisdiction-select"`) and `STATE:` (`aria-label="STATE"`, `data-testid="state-select"`).
     - `JURISDICTION:` selector renders the 5 exact option labels from Requirement 5.1.1.2 (`All Jurisdictions (National Overview)`, `Jurisdiction A (Northeast - Noridian)`, `Jurisdiction B (Midwest - CGS)`, `Jurisdiction C (South - CGS)`, `Jurisdiction D (West - Noridian)`).
     - Selecting `JURIS-DME-B` in `JURISDICTION:` updates `filterJurisdiction` to `"JURIS-DME-B"`, resets `filterState` to `""`, cascades `availableStates` to the 7 Midwestern states (`IL`, `IN`, `KY`, `MI`, `MN`, `OH`, `WI`), illuminates `JURIS-DME-B` and `STATE-IL`..`STATE-WI` plus their `COVERS_STATE` edges, and invokes `onReloadTopology("", policyKeyword, "JURIS-DME-B")`.
     - Selecting `"OH"` in `STATE:` updates `filterState` to `"OH"`, automatically updates `filterJurisdiction` to `"JURIS-DME-B"`, illuminates `STATE-OH`, `JURIS-DME-B`, and `JURIS-DME-B->COVERS_STATE->STATE-OH`, and invokes `onReloadTopology("OH", policyKeyword, "JURIS-DME-B")`.
     - Selecting `"NY"` in `STATE:` updates `filterState` to `"NY"`, automatically updates `filterJurisdiction` to `"JURIS-DME-A"`, and invokes `onReloadTopology("NY", policyKeyword, "JURIS-DME-A")`.
3. **National Overview Initial Load & URL Parameter Construction (`App.tsx`):**
   - **`{correct required outputs}`:**
     - On mount, `App.tsx` invokes `fetchTopology('', 'LTA', '')`, requesting `/api/graph/topology?policy_keyword=LTA` (National Overview with fee schedules collapsed).
     - When `jurisdictionFilter` and/or `stateFilter` are provided, `fetchTopology` appends `jurisdiction_filter` and `state_filter` to `URLSearchParams`.

---

## 4. Sufficiency Certification

- Every planned test input and output field is grounded in active codebase types (`src/api/models.py`, `src/graphrag/models.py`, `src/frontend/src/context/GraphSyncContext.tsx`, `src/frontend/src/components/FilterToolbar.tsx`, `src/frontend/src/App.tsx`) and live Neo4j graph state.
- Zero synthetic fixtures, mock objects, or unmandated expected blobs are used.
- Status: `RESOLVED` and `{sufficient}`.
