# Decision Ticket 005: Canvas Illumination Telemetry, Subgraph API, and Canvas Synchronization Specification

**Ticket ID:** `ticket-005.md`  
**Scope:** API Layer & UI Canvas Synchronization (`src/api/routes.py`, `src/frontend/`)  
**Status:** RESOLVED  
**Claimed By:** `wayfinder-read-and-plan`  
**Blocked By:** `ticket-002.md`, `ticket-003.md`, `ticket-004.md`  

---

## 1. Architectural Question
How must the FastAPI endpoints (`/api/graphrag/subgraph`, `/api/graphrag/query`) and frontend canvas integration be updated to support single-node canvas clicks, single-state queries (`STATE-NY`), and arbitrary multi-anchor inputs while delivering precise active path illumination telemetry?

---

## 2. Technical Audit and Empirical Findings

1. **Current Route Implementation in `src/api/routes.py`:**
   - In `/api/graphrag/subgraph` (lines 270-352):
     - The endpoint accepts a list of string primary keys `req.anchors`.
     - It maps labels to hardcoded slots: `State` -> `"state"`, `ICD10Code` -> `"diagnosis"`, `Policy` -> `"policy"`, `HCPCSCode` -> `"hcpcs"`.
     - It constructs `ResolvedAnchors(state_anchor=..., diagnosis_anchor=..., policy_anchor=..., all_anchors=...)`.
     - When called with a single node (e.g. `["STATE-NY"]` or `["CMS-MCD-A59508"]` from a canvas click), `pipeline.traverser.extract_connecting_subgraph` hits the unhandled `else` branch and raises `TraversalError`, returning HTTP 400.
   - In `/api/graphrag/query` (lines 354-389):
     - Calls `pipeline.execute_query(req, session)`.
     - Maps `EntityResolutionError` to HTTP 400, `ModelAuthenticationError` to HTTP 401, `ModelRateLimitError` to HTTP 429, `ModelInferenceError` to HTTP 502, and `GraphValidationError` to HTTP 500.
2. **Frontend Canvas Synchronization:**
   - In `src/frontend/src/context/GraphSyncContext.tsx`:
     - `setIlluminatedPath(response: GraphRAGQueryResponse)` updates `activeNodePKs` (Set of string primary keys) and `activeEdgeKeys` (Set of string directed edge keys).
     - Node selection via `selectNode` generates contextual quick prompts and seeds the active anchor.
   - In `src/frontend/src/components/GraphCanvas.tsx`:
     - Highlights active nodes and edges in amber/gold (`CANVAS_PALETTE.accentAmber`), dims unselected nodes, and recalculates camera focus.

---

## 3. Concrete Architectural Decision & API Contracts

### 3.1. Generalization of `/api/graphrag/subgraph`
In `src/api/routes.py`:
1. If `req.anchors` is empty, return empty `SubgraphResponse(nodes=[], edges=[], active_node_pks=[], active_edge_keys=[], retrieval_ms=0.0)`.
2. For each primary key in `req.anchors`:
   - Query Neo4j to verify existence across all 14 node types:
     ```cypher
     MATCH (n:PolicyNode {primary_key: $pk})
     RETURN n, labels(n) AS labels
     ```
   - If not found, raise `HTTPException(status_code=404, detail={"error_type": "EntityNotFoundError", "message": f"Entity '{pk}' not found in database."})`.
   - Map each recognized entity to an `AnchorEntity`:
     - `primary_key = pk`
     - `label = [l for l in labels if l != "PolicyNode"][0]`
     - `entity_type = label`
     - `slot = label.lower()`
     - `matched_text = n.get("name") or n.get("title") or pk`
3. Assemble `ResolvedAnchors` with all anchors in `all_anchors` and pass to `pipeline.traverser.extract_connecting_subgraph(resolved, session)`.
4. Return `SubgraphResponse` with traversed `TopologyNode` and `TopologyEdge` objects, active keys, and retrieval timing.

### 3.2. Response Telemetry for `/api/graphrag/query`
The response object `GraphRAGQueryResponse` must return:
- `answer: str`: LLM-synthesized guidance quoting bracketed IDs and rates.
- `active_node_pks: List[str]`: Full list of node primary keys on the traversed connecting path.
- `active_edge_keys: List[str]`: Directed edge keys formatted as `{source_pk}->{label}->{target_pk}`.
- `anchors: List[AnchorEntity]`: All resolved starting pins.
- `provenance_sources: List[Dict[str, Any]]`: Deduplicated edge provenance dictionaries (`source_uri`, `selector`, `ingestion_timestamp`, `run_id`).
- `duration_ms: float`: Total execution time in milliseconds.

### 3.3. Canvas Integration Verification
Ensure that when a user clicks a node (e.g., `STATE-NY` or `CMS-MCD-A59508`) or triggers a quick prompt:
- The backend returns HTTP 200 with the active subgraph.
- The UI canvas highlights active nodes and edges in amber/gold.
- Unrelated nodes are dimmed.
- The assistant drawer displays grounded synthesis without crashes.
