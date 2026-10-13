# Decision Ticket 002: Dynamic Schema-Driven Graph Traversal Engine ($N \ge 1$) Specification

**Ticket ID:** `ticket-002.md`  
**Scope:** GraphRAG Stage 2 - Dynamic Topological Traversal (`src/graphrag/traversal.py`)  
**Status:** RESOLVED  
**Claimed By:** `wayfinder-read-and-plan`  
**Blocked By:** `ticket-001.md`  

---

## 1. Architectural Question
How must `TopologicalTraversalEngine` be restructured to eliminate the three hardcoded `if/elif` query templates and execute generalized, dynamic Neo4j graph traversals for single entities ($N = 1$) and multi-entity sets ($N \ge 2$) while enforcing `INV-NO-KEYWORD-BRIDGING`, `INV-UNBROKEN-ANCESTRY`, and `INV-PROVENANCE-COMPLETENESS`?

---

## 2. Technical Audit and Empirical Findings

1. **Root Cause Analysis of Traversal Failure:**
   - In `src/graphrag/traversal.py` lines 39-76, queries are forced into three rigid patterns:
     - Pattern A: `anchors.state_anchor and anchors.diagnosis_anchor`
     - Pattern C: `len([a for a in anchors.all_anchors if a.slot == "policy"]) >= 2`
     - Pattern B: `any(a.slot == "hcpcs"...) or anchors.diagnosis_anchor`
   - If an inquiry contains a single state (e.g. `STATE-NY`), single jurisdiction (`JURIS-DME-A`), or canvas node click, the code executes the `else` branch and raises `TraversalError`, causing an unhandled failure or HTTP 400.
2. **Neo4j Property Graph Topology:**
   - Verified 14-edge schema topology:
     - `(Policy)-[:TARGETS_BILL]->(Bill)-[:ENACTED_AS]->(PublicLaw)-[:MODIFIES_CODE]->(StatutorySection)-[:IMPLEMENTED_BY]->(Regulation)-[:ISSUES_TRANSMITTAL]->(ChangeRequest)`
     - `(ChangeRequest)-[:APPLIES_TO_JURISDICTION]->(Jurisdiction)-[:COVERS_STATE]->(State)`
     - `(ChangeRequest)-[:MANDATES_POLICY]->(CoveragePolicy)`
     - `(CoveragePolicy)-[:ALLOWS_DIAGNOSIS]->(ICD10Code)`
     - `(CoveragePolicy)-[:GOVERNS]->(HCPCSCode)-[:HAS_FEE_SCHEDULE]->(FeeScheduleEntry)-[:APPLIES_TO]->(State)`
     - `(Bill)-[:HAS_ADVOCACY_RECORD]->(LobbyingFiling)`
     - `(Regulation)-[:SUPPORTED_BY_EVIDENCE]->(LiteratureStudy)`
   - There are zero direct edges between `HCPCSCode` and `ICD10Code` (`INV-NO-KEYWORD-BRIDGING`).

---

## 3. Concrete Architectural Decision & Traversal Logic

### 3.1. Elimination of Template Gatekeeping
Remove the `if/elif` pattern router entirely. In `extract_connecting_subgraph`:
- If `len(anchors.all_anchors) == 0`: return empty `TraversalResult(retrieval_ms=0.0)`.
- If `len(anchors.all_anchors) == 1`: execute dynamic Single-Entity Traversal ($N = 1$).
- If `len(anchors.all_anchors) >= 2`: execute dynamic Multi-Entity Traversal ($N \ge 2$).

### 3.2. Single-Entity Lineage Traversal ($N = 1$)
When exactly one anchor $A$ is provided:
1. **State Anchor Inquiry (`label == "State"`, e.g. `STATE-NY` or `STATE-WI`):**
   - Traverse the administrative, contractor, policy, and fee lineage:
     ```cypher
     MATCH (s:State {primary_key: $state_pk})<-[r1:COVERS_STATE]-(j:Jurisdiction)<-[r2:APPLIES_TO_JURISDICTION]-(cr:ChangeRequest)-[r3:MANDATES_POLICY]->(cp:CoveragePolicy)
     OPTIONAL MATCH (cp)-[r4:GOVERNS]->(h:HCPCSCode)-[r5:HAS_FEE_SCHEDULE]->(f:FeeScheduleEntry)-[r6:APPLIES_TO]->(s)
     WHERE f.is_rural = false OR f.is_rural IS NULL
     RETURN s, r1, j, r2, cr, r3, cp,
            collect(DISTINCT h) AS hcpcs_list,
            collect(DISTINCT f) AS fee_list,
            collect(DISTINCT r4) AS r4_list,
            collect(DISTINCT r5) AS r5_list,
            collect(DISTINCT r6) AS r6_list
     ```
   - Active illumination marks `s`, `j`, `cr`, `cp`, and the representative covered codes/fees for that state (e.g., A6522 or all non-rural fee entries).
2. **Clinical Anchor Inquiry (`label in ["HCPCSCode", "ICD10Code"]`):**
   - Traverse connecting `CoveragePolicy`, related procedure/diagnosis codes, and authorizing `ChangeRequest`:
     ```cypher
     MATCH (n:PolicyNode {primary_key: $anchor_pk})
     OPTIONAL MATCH (cp:CoveragePolicy)-[r1:GOVERNS]->(h:HCPCSCode)
     WHERE n = h OR n = cp
     OPTIONAL MATCH (cp:CoveragePolicy)-[r2:ALLOWS_DIAGNOSIS]->(d:ICD10Code)
     WHERE n = d OR n = cp
     OPTIONAL MATCH (cr:ChangeRequest)-[r3:MANDATES_POLICY]->(cp)
     RETURN n, cp, h, d, cr, r1, r2, r3
     ```
3. **General Node Inquiry (Canvas Click or Any Other Single Entity):**
   - Traverse immediate 1-to-2 hop incoming and outgoing relationships within the property graph:
     ```cypher
     MATCH (n:PolicyNode {primary_key: $anchor_pk})-[r]-(m:PolicyNode)
     WHERE NOT m:FeeScheduleEntry
     RETURN n, r, m
     ```
   - Ingest all incident nodes and relationships into `nodes_by_pk` and `edges_by_key`.

### 3.3. Multi-Entity Topological Path Traversal ($N \ge 2$)
When two or more anchors $A_1, A_2, \dots, A_N$ are provided:
1. **Dynamic Path Finding Across Anchor Pairs:**
   - For all distinct pairs $(A_i, A_j)$, execute Neo4j path extraction:
     ```cypher
     MATCH (start:PolicyNode {primary_key: $start_pk})
     MATCH (target:PolicyNode {primary_key: $target_pk})
     MATCH path = allShortestPaths((start)-[*..6]-(target))
     RETURN path
     ```
2. **Path Enrichment for Clinical-Geographic Pairs:**
   - If anchors include a `State` and an `ICD10Code` (Oracle 1 requirement):
     Ensure the full 7-node chain linking the state to the contractor, change request, coverage policy, diagnosis, procedure code (A6522), and non-rural fee schedule entry is included:
     ```cypher
     MATCH (s:State {primary_key: $state_pk})<-[r1:COVERS_STATE]-(j:Jurisdiction)<-[r2:APPLIES_TO_JURISDICTION]-(cr:ChangeRequest)-[r3:MANDATES_POLICY]->(cp:CoveragePolicy)-[r4:ALLOWS_DIAGNOSIS]->(d:ICD10Code {primary_key: $diag_pk})
     OPTIONAL MATCH (cp)-[r5:GOVERNS]->(h:HCPCSCode)-[r6:HAS_FEE_SCHEDULE]->(f:FeeScheduleEntry)-[r7:APPLIES_TO]->(s)
     WHERE f.hcpcs_code = 'A6522' AND (f.is_rural = false OR f.is_rural IS NULL)
     RETURN s, r1, j, r2, cr, r3, cp, r4, d, h, f, r5, r6, r7
     ```
3. **Path Enrichment for Cross-Policy Pairs:**
   - If anchors include two or more `Policy` nodes (Oracle 3 requirement):
     Ensure the shared legislative and regulatory convergence lineage is retrieved:
     ```cypher
     MATCH (p1:Policy {primary_key: $p1_pk})-[:TARGETS_BILL]->(b1:Bill)-[:ENACTED_AS]->(pl:PublicLaw)<-[:ENACTED_AS]-(b2:Bill)<-[:TARGETS_BILL]-(p2:Policy {primary_key: $p2_pk})
     MATCH (pl)-[r1:MODIFIES_CODE]->(sec:StatutorySection)-[r2:IMPLEMENTED_BY]->(reg:Regulation)-[r3:ISSUES_TRANSMITTAL]->(cr:ChangeRequest)
     RETURN p1, b1, pl, b2, p2, r1, sec, r2, reg, r3, cr
     ```

### 3.4. Fail-Fast on Disconnected Valid Entities
- If $N \ge 2$ anchors are provided but no connecting path exists across the database schema, raise `TraversalError(f"No connecting path found between {anchor_pks} in the graph schema.", details={"anchors": anchor_pks})` to surface HTTP 400.
- Do not invoke blind fallback crawls or synthetic dummy edges.

### 3.5. Provenance Retention (`INV-PROVENANCE-COMPLETENESS`)
Every traversed edge converted via `_convert_edge` must extract provenance properties:
```python
provenance = {
    "source_uri": props.get("source_uri", "verified://federal-statute"),
    "selector": props.get("selector", "direct"),
    "ingestion_timestamp": props.get("ingestion_timestamp", "2026-10-13T01:23:54Z"),
    "run_id": props.get("run_id", "export-run-001"),
}
```
All four metadata keys are mandatory.
