# Decision Ticket 005: Single-Entity Neighborhood Traversal and Canvas Edge Key Reconstruction

**Ticket ID:** `ticket-005.md`  
**Scope:** `src/graphrag/traversal.py` & `src/graphrag/context_assembler.py`  
**Status:** RESOLVED  
**Claimed By:** `wayfinder-read-and-plan`  
**Blocked By:** `ticket-004.md`  
**Taxonomy Reference:** `LANGUAGE.md`

---

## 1. Architectural Question
How must single-entity general traversal (`_execute_single_general_traversal`) in `TopologicalTraversalEngine` be refactored to eliminate corrupted `UNKNOWN->RELATED_TO->UNKNOWN` edge keys, ensure deterministic Cypher relationship projections, and format all 14 entity types within `GraphContextAssembler`?

---

## 2. Root Cause & Architectural Audit

1. **Corrupted Edge Keys in General Traversal:**
   - In `src/graphrag/traversal.py` (lines 278–297), `_execute_single_general_traversal` runs:
     ```cypher
     MATCH (n:PolicyNode {primary_key: $anchor_pk})-[r]-(m:PolicyNode)
     WHERE NOT m:FeeScheduleEntry
     RETURN n, r, m
     LIMIT 50
     ```
   - When `.data()` is called, `r` is serialized to a dictionary, losing the underlying `Relationship` object attributes (`start_node`, `end_node`, `type`).
   - Consequently, `hasattr(r, "start_node")` evaluates to `False`, forcing `src_pk` and `tgt_pk` to `None`.
   - `_convert_edge` assigns `UNKNOWN` to both endpoints, producing the collapsed edge key `UNKNOWN->RELATED_TO->UNKNOWN`.
   - The frontend drops edges with `UNKNOWN` endpoints because they do not match canvas node PKs. Canvas illumination for connected relationships fails completely.

2. **Isolated or 0-Edge Entity Safety:**
   - If an entity has no relationships in a strict `-[r]-` match, `MATCH (n)-[r]-(m)` returns zero rows, causing `nodes_by_pk` to be empty and raising an unhandled `TraversalError`.
   - Changing to `OPTIONAL MATCH` guarantees that the anchor node `n` is always retrieved and illuminated even if it has no incident edges.

3. **Context Assembly Coverage across 14 Node Types:**
   - In `src/graphrag/context_assembler.py`, sections exist for Policies, Laws, Sections, Regulations, CRs, Coverage Policies, Jurisdictions, States, Diagnoses, HCPCS, and Fees.
   - Types such as `Bill`, `LiteratureStudy`, and `LobbyingFiling` lack explicit sections and must be cleanly formatted so LLM synthesis is grounded in their attributes.

---

## 3. Decision & Technical Specifications

### 3.1. Cypher Projection Refactoring in `src/graphrag/traversal.py`
- **Symbol:** `TopologicalTraversalEngine._execute_single_general_traversal`
- **Actions:**
  1. Replace the Cypher query with explicit source, target, and relationship type projections:
     ```cypher
     MATCH (n:PolicyNode {primary_key: $anchor_pk})
     OPTIONAL MATCH (n)-[r]-(m:PolicyNode)
     WHERE NOT m:FeeScheduleEntry
     RETURN n, r, m,
            startNode(r).primary_key AS src_pk,
            endNode(r).primary_key AS tgt_pk,
            type(r) AS rel_type
     LIMIT 50
     ```
  2. Iterate through results:
     - For each row, add `n` to `nodes_by_pk` and `active_node_pks`.
     - If `m` is present, add `m` to `nodes_by_pk` and `active_node_pks`.
     - If `r` and `src_pk` and `tgt_pk` are present:
       - Construct `TraversalEdge` with `source_pk=src_pk`, `target_pk=tgt_pk`, `label=rel_type`, and `edge_key=f"{src_pk}->{rel_type}->{tgt_pk}"`.
       - Add to `edges_by_key` and `active_edge_keys`.

### 3.2. Universal Entity Formatting in `src/graphrag/context_assembler.py`
- **Symbol:** `GraphContextAssembler.assemble_context`
- **Actions:**
  1. In Section 1 (Program & Legal Authority), add formatting for `Bill`:
     ```python
     bills = [n for n in nodes if n.label == "Bill"]
     for b in bills:
         title = b.properties.get("title") or b.name
         lines.append(f"- Introduced Bill: [{b.primary_key}] {title}")
     ```
  2. In Section 3 (Clinical Criteria), add formatting for `LiteratureStudy`:
     ```python
     studies = [n for n in nodes if n.label == "LiteratureStudy"]
     for st in studies:
         title = st.properties.get("title") or st.name
         lines.append(f"- Clinical Study: [{st.primary_key}] {title}")
     ```
  3. In Section 1, add formatting for `LobbyingFiling`:
     ```python
     filings = [n for n in nodes if n.label == "LobbyingFiling"]
     for lf in filings:
         client = lf.properties.get("client_name") or lf.name
         lines.append(f"- Lobbying Filing: [{lf.primary_key}] {client}")
     ```

---

## 4. Acceptance Criteria
1. Single entity traversal for `PLAW-117-328` returns `PLAW-117-328` and its 5 connected neighbors (`BILL-117-hr-2617`, `BILL-117-hr-3630`, `BILL-117-hr-3808`, `USC-42-1395x-s-2-JJ`, `USC-42-1395x-s-2-Z`).
2. All traversed edges contain authentic non-null `src_pk` and `tgt_pk` matching `${src_pk}->${rel_type}->${tgt_pk}` (0 occurrences of `UNKNOWN`).
3. Active edge keys are returned to the frontend and successfully illuminate canvas edges.
4. The synthesized answer generated from the context accurately quotes `[PLAW-117-328]` and its enacted statutory provisions.
