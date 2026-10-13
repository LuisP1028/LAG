# Decision Ticket 004: Explicit Anchor Transmission Contract and Backend Bypass Architecture

**Ticket ID:** `ticket-004.md`  
**Scope:** `src/graphrag/models.py`, `src/graphrag/entity_linker.py`, `src/graphrag/pipeline.py`, & `src/api/routes.py`  
**Status:** RESOLVED  
**Claimed By:** `wayfinder-read-and-plan`  
**Blocked By:** None (Backend Root Decision)  
**Taxonomy Reference:** `LANGUAGE.md`

---

## 1. Architectural Question
How must the GraphRAG query request model and backend pipeline be modified to receive the explicit primary key identifier (`primary_key`), completely bypass heuristic natural language regex guessing, and guarantee deterministic anchor resolution across all 14 entity types?

---

## 2. Root Cause & Architectural Audit

1. **Missing Request Parameter:**
   - In `src/graphrag/models.py` (lines 58–63), `GraphRAGQueryRequest` only accepts `query`, `model_id`, and `state_code`.
   - The selected node's `primary_key` has no parameter slot in the API payload schema.

2. **Fragile Keyword Regex Extraction:**
   - In `src/graphrag/pipeline.py` (line 44), Stage 1 invokes `self.linker.resolve_anchors(request.query, session)`.
   - `EntityAnchorLinker` scans the query string using regexes (`PK_TOKEN_REGEX`, `CLINICAL_SYNONYMS`, `POLICY_TRIGGERS`).
   - If a prompt uses an entity's formal title (e.g. *"Consolidated Appropriations Act, 2023"*) or an unusual phrase without an isolated regex match, anchor linking yields 0 anchors, causing 0 nodes illuminated or a `TraversalError`.

3. **Explicit Anchor Specification Requirement:**
   - Section 4.3 mandates:
     1. Direct Anchor Binding: Transmitting the entity's `primary_key` as a pre-resolved anchor.
     2. Bypass Keyword Guessing: Direct database lookup using the anchor, bypassing regex heuristics.
     3. Retrieval Guarantee: Guaranteeing non-zero active nodes for all valid database entities.

---

## 3. Decision & Technical Specifications

### 3.1. Request Model Payload Extension (`src/graphrag/models.py`)
- **Symbol:** `GraphRAGQueryRequest`
- **Actions:**
  Extend the model with optional primary key identifier fields:
  ```python
  class GraphRAGQueryRequest(BaseModel):
      """Request payload for conversational GraphRAG synthesis."""
      query: str
      model_id: Optional[str] = "meta-llama/Meta-Llama-3-8B-Instruct"
      state_code: Optional[str] = None
      primary_key: Optional[str] = None
      anchor_node_pk: Optional[str] = None
  ```

### 3.2. Explicit Anchor Resolution (`src/graphrag/entity_linker.py`)
- **Symbol:** `EntityAnchorLinker`
- **Actions:**
  Implement `resolve_explicit_anchor(self, primary_key: str, session: Session) -> ResolvedAnchors`:
  1. Execute deterministic Cypher query:
     ```cypher
     MATCH (n:PolicyNode {primary_key: $pk})
     RETURN n.primary_key AS primary_key, labels(n) AS labels, n.name AS name, n.title AS title
     ```
  2. If record is found:
     - Determine primary label (filtering out `PolicyNode`).
     - Map label to semantic slot (`State` -> `state`, `ICD10Code` -> `diagnosis`, `HCPCSCode` -> `hcpcs`, `CoveragePolicy` -> `coveragepolicy`, `ChangeRequest` -> `changerequest`, `Jurisdiction` -> `jurisdiction`, `Policy` -> `policy`, others -> lowercase label).
     - Construct `AnchorEntity(slot=slot, primary_key=primary_key, matched_text=name, entity_type=label, label=label)`.
     - Return `ResolvedAnchors` containing this anchor in `all_anchors` and the corresponding slot attribute.
  3. If record is not found:
     - Raise `EntityResolutionError(f"Entity '{primary_key}' not found in knowledge graph.")`.

### 3.3. Pipeline Execution Bypass Routing (`src/graphrag/pipeline.py`)
- **Symbol:** `GraphRAGPipeline.execute_query`
- **Actions:**
  Update Stage 1 anchor linking logic:
  ```python
  explicit_pk = request.primary_key or request.anchor_node_pk
  if explicit_pk:
      anchors: ResolvedAnchors = self.linker.resolve_explicit_anchor(explicit_pk, session)
  else:
      anchors: ResolvedAnchors = self.linker.resolve_anchors(request.query, session)
  ```
  - If the resolved anchor is a `State` node, set `state_code` to that state's two-letter code.
  - If `request.state_code` is provided and anchor is not a state, preserve `request.state_code`.

---

## 4. Acceptance Criteria
1. Sending a query with `primary_key: "PLAW-117-328"` resolves directly to the PublicLaw anchor in Neo4j without executing regex guessing.
2. If an invalid primary key is supplied, execution fails fast with `EntityResolutionError` (HTTP 400).
3. The explicit anchor contract functions reliably across all 14 entity types.
