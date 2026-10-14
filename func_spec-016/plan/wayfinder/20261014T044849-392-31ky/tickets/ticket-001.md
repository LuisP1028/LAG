# Ticket 001: Backend Runtime Persistence & API Endpoint Contracts (`GET /api/health`, `GET /api/entities/{primary_key}`, `GET /api/graph/topology`, `POST /api/graphrag/query`, CORS & Embedded Graph Store)

- **Ticket ID:** `ticket-001`
- **Title:** Backend Runtime Persistence & API Endpoint Contracts (`GET /api/health`, `GET /api/entities/{primary_key}`, `GET /api/graph/topology`, `POST /api/graphrag/query`, CORS & Embedded Graph Store)
- **Status:** Resolved
- **Claimed by:** `wayfinder-read-and-plan`
- **Blocked By:** None
- **Governing Specification:** `functional_specification_016.md` (§4.1 Engine API & Endpoints, §5.1 Success Criteria)

---

## 1. Decision Question

How must the FastAPI backend runtime (`src/api/server.py`, `src/api/routes.py`, `src/api/models.py`, and `src/graph/neo4j_sync.py`) be structured so that it:
1. Exposes all four required endpoint families specified in `functional_specification_016.md` §4.1 (`GET /api/health`, `GET /api/graph/topology`, `GET /api/entities/{primary_key}`, and `POST /api/graphrag/query` / `POST /api/entities/resolve` / `POST /api/graphrag/subgraph`) with deterministic fail-fast validation;
2. Operates identically against both a live Neo4j Bolt instance (`NEO4J_URI=bolt://localhost:7687`) and a cloud Hugging Face Space container without local Neo4j daemon dependencies (`NEO4J_URI=embedded://exports/lta_knowledge_graph.json`); and
3. Enforces explicit CORS headers for the GitHub Pages origin (`https://luisp1028.github.io`) while preserving 100% backward compatibility with existing integration suites (`tests/test_api_endpoints.py` and `tests/test_graphrag_pipeline.py`)?

---

## 2. Codebase & Infrastructure Grounding

1. **`src/api/models.py` (Lines 10–66):**
   - Currently defines `HealthResponse(status="ok", neo4j_connected=True, timestamp=...)`, `TopologyNode`, `TopologyEdge`, `TopologyResponse`, `EntityResolveRequest`, `EntityResolveResponse`, `SubgraphRequest`, `SubgraphResponse`, and `ErrorEnvelope`.
   - `functional_specification_016.md` §4.1 requires the Health & Readiness Endpoint to return a `200 OK` response with runtime health, loaded policy domains, and service uptime, and requires an Entity Inspection Endpoint returning deep contextual provenance and text excerpts for a specified entity primary key.
2. **`src/api/routes.py` (Lines 69–666):**
   - Currently implements `GET /api/health`, `GET /api/graph/summary`, `GET /api/graph/topology`, `POST /api/entities/resolve`, `POST /api/graphrag/subgraph`, and `POST /api/graphrag/query`.
   - `GET /api/entities/{primary_key}` is currently absent from `src/api/routes.py`.
3. **`src/graph/neo4j_sync.py` (Lines 73–341):**
   - `Neo4jSyncEngine` connects to `self.uri` via `GraphDatabase.driver`. In local verification, `NEO4J_URI` is `bolt://localhost:7687` containing the 3,875 nodes and 7,593 edges from `exports/lta_knowledge_graph.json`.
   - Inside a cloud Hugging Face Space Docker container (`ChoppedCheese/lag-policy-engine`), no local `bolt://localhost:7687` Neo4j server runs unless `Neo4jSyncEngine` supports an explicit `embedded://` URI scheme (`NEO4J_URI=embedded://exports/lta_knowledge_graph.json`) backed by an in-memory Cypher-compatible graph driver (`src/graph/embedded_driver.py`) loaded deterministically from the repository's exported JSON graph artifacts.
4. **`src/api/server.py` (Lines 19–110):**
   - Configures `CORSMiddleware` and `lifespan`. On Hugging Face Spaces (`sdk: docker`), container traffic is routed to port `7860` (`PORT` / `API_PORT`).

---

## 3. Locked Architectural Decision

### 3.1 `HealthResponse` and `EntityInspectionResponse` Schemas (`src/api/models.py`)
1. **Extend `HealthResponse` (`src/api/models.py` lines 10–14):**
   - Preserve `status: str = "ok"`, `neo4j_connected: bool = True`, and `timestamp: str` so all assertions in `tests/test_api_endpoints.py` pass unchanged.
   - Add:
     - `loaded_policies: List[str] = Field(default_factory=lambda: ["LTA"], description="Loaded policy domain keywords in the runtime graph")`
     - `uptime_seconds: float = Field(default=0.0, description="Service runtime uptime in seconds")`
     - `storage_backend: str = Field(default="neo4j", description="Active graph storage engine (neo4j or embedded)")`
2. **Add `EntityInspectionResponse` (`src/api/models.py` after `TopologyResponse`):**
   ```python
   class EntityInspectionResponse(BaseModel):
       """Deep contextual provenance, citations, text excerpts, and relationships for a single entity node."""
       primary_key: str = Field(..., description="Deterministic composite primary key")
       label: str = Field(..., description="Canonical 17-category entity label")
       name: str = Field(..., description="Human-readable derived display name")
       properties: Dict[str, Any] = Field(default_factory=dict, description="All native and derived entity attributes")
       text_excerpt: str = Field(default="", description="Statutory, regulatory, or clinical text excerpt")
       citations: List[str] = Field(default_factory=list, description="Official statutory, regulatory, and policy citations")
       provenance: List[Dict[str, Any]] = Field(default_factory=list, description="Deduplicated provenance metadata records (source_uri, selector, run_id, ingestion_timestamp)")
       relationships: List[TopologyEdge] = Field(default_factory=list, description="All incoming and outgoing relationships incident to this entity")
   ```

### 3.2 Health Endpoint & Entity Inspection Endpoint (`src/api/routes.py`)
1. **Track Server Boot Time & Populate `GET /api/health` (`src/api/routes.py` lines 69–75):**
   - Record `_SERVER_BOOT_MONOTONIC = time.monotonic()` at module load time.
   - In `health_check(session: Session = Depends(get_neo4j_session))`:
     - Verify connectivity via `engine.get_driver().verify_connectivity()`.
     - Query `session.run("MATCH (p:Policy) RETURN p.keyword AS kw, p.primary_key AS pk").data()` to extract sorted unique policy keywords (`loaded_policies`, defaulting to `["LTA"]` if only `POLICY-LTA` is present).
     - Compute `uptime_seconds = round(max(0.0, time.monotonic() - _SERVER_BOOT_MONOTONIC), 2)`.
     - Set `storage_backend = "embedded" if str(engine.uri).startswith("embedded://") else "neo4j"`.
     - Return `HealthResponse(status="ok", neo4j_connected=True, loaded_policies=loaded_policies, uptime_seconds=uptime_seconds, storage_backend=storage_backend)`.
2. **Add `GET /api/entities/{primary_key:path}` (`src/api/routes.py`):**
   - Route signature:
     ```python
     @router.get("/entities/{primary_key:path}", response_model=EntityInspectionResponse)
     def inspect_entity(
         primary_key: str,
         session: Session = Depends(get_neo4j_session),
     ) -> EntityInspectionResponse:
     ```
   - Normalize `clean_pk = primary_key.strip()`. If empty, raise `HTTPException(status_code=400, detail={"error_type": "EntityResolutionError", "message": "Entity primary_key must not be empty.", "details": {"primary_key": primary_key}})`.
   - Query the entity node:
     ```cypher
     MATCH (n:PolicyNode)
     WHERE n.primary_key = $pk OR toUpper(n.primary_key) = toUpper($pk)
     RETURN n, labels(n) AS lbls
     ```
   - If not found, fail fast with `HTTPException(status_code=404, detail={"error_type": "EntityResolutionError", "message": f"Entity '{clean_pk}' not found in knowledge graph.", "details": {"primary_key": clean_pk}})`.
   - Extract `props = dict(n)`, `actual_pk = str(props.get("primary_key", clean_pk))`, `label = resolve_label_from_pk_and_labels(actual_pk, list(rec["lbls"] or []))`, and `name = derive_node_display_name(label, actual_pk, props)`.
   - Extract `text_excerpt`: first non-empty string among `props.get("text")`, `props.get("text_excerpt")`, `props.get("long_description")`, `props.get("description")`, `props.get("short_description")`, `props.get("heading")`, `props.get("title")`, or `name`.
   - Extract `citations`: deduplicated list of non-empty strings from `props.get("citation_string")`, `props.get("citation")`, `props.get("cfr_reference")`, `props.get("uslm_section_path")`, `props.get("public_law_id")`, `props.get("docket_id")`, `props.get("rin")`, `props.get("cr_number")`, `props.get("transmittal_number")`, `props.get("article_id")`, plus any list items in `props.get("cfr_parts")` or `props.get("clinical_prerequisites")`.
   - Query incident incoming and outgoing relationships (bounded to 250 edges so high-degree hub nodes return deterministically in <20ms):
     ```cypher
     MATCH (src:PolicyNode)-[r]->(tgt:PolicyNode)
     WHERE src.primary_key = $pk OR tgt.primary_key = $pk
     RETURN src.primary_key AS spk, tgt.primary_key AS tpk, r
     LIMIT 250
     ```
   - Convert each relationship via `convert_edge(r, spk, tpk)` into `TopologyEdge` and collect unique provenance records (`source_uri`, `selector`, `run_id`, `ingestion_timestamp`) into `provenance: List[Dict[str, Any]]`.

### 3.3 Deterministic Embedded Graph Driver (`src/graph/embedded_driver.py` & `src/graph/neo4j_sync.py`)
1. **Create `src/graph/embedded_driver.py`:**
   - Implements `EmbeddedNode`, `EmbeddedRelationship`, `EmbeddedPath`, `EmbeddedRecord`, `EmbeddedResult`, `EmbeddedSession`, and `EmbeddedGraphDriver` adhering to the `neo4j.Driver` / `neo4j.Session` interface used by `src/api/routes.py`, `src/graphrag/entity_linker.py`, `src/graphrag/traversal.py`, and `src/graph/neo4j_sync.py`.
   - Loads one or more exported graph JSON files specified in `embedded://<comma-separated-paths>` (defaulting to `exports/lta_knowledge_graph.json`). If any configured JSON path does not exist or fails JSON parsing, raises `FileNotFoundError` / `ValueError` immediately (fail-fast).
   - Supports all Cypher query patterns executed across `src/api/routes.py`, `src/graphrag/entity_linker.py`, `src/graphrag/traversal.py`, and `src/graph/neo4j_sync.py`:
     - Node lookup by `primary_key` (exact and `toUpper`), by label (`:Policy`, `:Jurisdiction`, `:Transmittal`, `:CoveragePolicy`, `:PublicLaw`, `:Bill`, `:StatutorySection`, `:USCSection`, `:Regulation`, `:CFRSection`, `:CBOScore`, `:LiteratureStudy`, `:State`, `:DiagnosisCode` / `:ICD10Code`, `:ProcedureCode` / `:HCPCSCode`, `:FeeScheduleRate`), and catalog queries (`WHERE NOT n:FeeScheduleRate AND NOT n:FeeScheduleEntry AND NOT n:State`).
     - Topology queries (`base_query`, `fee_query` by `state_code`, `all_fees_query` with `state_pks` and `LIMIT 4000`).
     - Entity inspection relationship query (`WHERE src.primary_key = $pk OR tgt.primary_key = $pk`).
     - Summary statistics queries (`nodes_by_label`, `edges_by_type`, `total_nodes`, `total_edges`).
     - All `TopologicalTraversalEngine` queries: `_ingest_upstream_legal_lineage`, `_execute_jurisdiction_traversal`, `_execute_single_state_traversal`, `_execute_single_clinical_traversal`, `_execute_single_general_traversal`, `allShortestPaths((start)-[*..10]-(target))`, `_execute_pattern_a`, and `_execute_pattern_b`.
2. **Integrate into `Neo4jSyncEngine` (`src/graph/neo4j_sync.py` lines 92–106):**
   - When `self.uri.startswith("embedded://")`:
     - `get_driver()` instantiates `EmbeddedGraphDriver(self.uri)` and calls `self._driver.verify_connectivity()`.
     - `init_schema()` is a deterministic no-op on `EmbeddedGraphDriver` (constraints are enforced by primary-key dictionary indexing in `EmbeddedGraphDriver`).
   - When `self.uri` starts with `bolt://`, `neo4j://`, `bolt+s://`, or `neo4j+s://`:
     - Uses `GraphDatabase.driver(self.uri, auth=(self.username, self.password))` and `verify_connectivity()`, failing fast on connection errors.

### 3.4 CORS & Port Binding (`src/api/server.py`)
1. Update `CORSMiddleware` in `src/api/server.py` (lines 48–60) to explicitly include:
   - `"https://luisp1028.github.io"`
   - `"http://localhost:3000"`
   - `"http://localhost:5173"`
   - `"http://127.0.0.1:3000"`
   - `"http://127.0.0.1:5173"`
   - `"*"` (with `allow_credentials=False` or `allow_origin_regex=r"https://.*\.github\.io|https://.*\.hf\.space|http://localhost:\d+|http://127\.0\.0\.1:\d+"` so browsers accept CORS responses with `Access-Control-Allow-Origin` matching the exact request `Origin` header).
2. In `src/api/server.py` lines 22–28:
   - Read `neo4j_uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")`.
   - Only call `engine.init_schema()` when not using `embedded://`.
3. In `src/api/server.py` line 108:
   - Read `port = int(os.getenv("PORT", os.getenv("API_PORT", "8000")))` so both Hugging Face Spaces (`PORT=7860`) and local runs (`API_PORT=8000`) bind deterministically.

---

## 4. Verification Criteria

- `GET /api/health` returns HTTP 200 with `status="ok"`, `neo4j_connected=True`, `loaded_policies=["LTA"]`, `uptime_seconds >= 0.0`, and `storage_backend` in `{"neo4j", "embedded"}`.
- `GET /api/entities/STAT-117-328-SEC-4133` returns HTTP 200 with `primary_key="STAT-117-328-SEC-4133"`, `label="StatutorySection"`, non-empty `text_excerpt` containing `"SEC. 4133"`, `citations`, `provenance`, and `relationships`.
- `GET /api/entities/NONEXISTENT-999` returns HTTP 404 with standardized `ErrorEnvelope` (`error=True`, `error_type="EntityResolutionError"`).
- All existing tests in `tests/test_api_endpoints.py` pass under both `NEO4J_URI=bolt://localhost:7687` and `NEO4J_URI=embedded://exports/lta_knowledge_graph.json`.
