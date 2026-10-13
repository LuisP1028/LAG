# Decision Ticket 002: Generalized Topological Subgraph Expansion and Neighborhood Traversal Specification

**Ticket ID:** `ticket-002.md`  
**Scope:** GraphRAG Stage 2 - Graph Topology Retrieval  
**Status:** RESOLVED  
**Claimed By:** `wayfinder-graphrag-spec`  
**Blocked By:** `ticket-001.md`

---

## 1. Architectural Question
How must the graph retrieval engine traverse the knowledge graph between resolved anchors without generating bespoke Cypher queries for every anticipated user question, while strictly preserving system invariants (`INV-UNBROKEN-ANCESTRY`, `INV-NO-KEYWORD-BRIDGING`, and `INV-50-STATE-COMPLETENESS`)?

---

## 2. Decision and Specification Requirements

### 2.1. Generalized $k$-Hop Connecting Subgraph Extraction
Rather than attempting to guess specialized Cypher queries, the system must execute a single, generalized topological path discovery algorithm:
1. **Target Endpoints:** Identified anchors from Stage 1:
   - Source: `{State: S, ICD10Code: D, Policy: P}`
2. **Topological Join Contracts:**
   The traversal engine extracts the intersection subgraph linking:
   - **Contractor & Administrative Lineage:**
     $$(S) \longleftarrow [\text{:COVERS\_STATE}] - (J: \text{Jurisdiction}) \longleftarrow [\text{:APPLIES\_TO\_JURISDICTION}] - (CR: \text{ChangeRequest}) \longrightarrow [\text{:MANDATES\_POLICY}] \longrightarrow (CP: \text{CoveragePolicy})$$
   - **Clinical Indication Authority (`INV-NO-KEYWORD-BRIDGING`):**
     $$(CP) \longrightarrow [\text{:ALLOWS\_DIAGNOSIS}] \longrightarrow (D)$$
   - **Covered Items & Pricing Integration:**
     $$(CP) \longrightarrow [\text{:GOVERNS}] \longrightarrow (H: \text{HCPCSCode}) \longrightarrow [\text{:HAS\_FEE\_SCHEDULE}] \longrightarrow (F: \text{FeeScheduleEntry}) \longrightarrow [\text{:APPLIES\_TO}] \longrightarrow (S)$$
   - **Legislative Ancestry (Macro Inquiries):**
     $$(P) \longrightarrow [\text{:TARGETS\_BILL}] \longrightarrow (B) \longrightarrow [\text{:ENACTED\_AS}] \longrightarrow (PL) \longrightarrow [\text{:MODIFIES\_CODE}] \longrightarrow (SEC) \longrightarrow [\text{:IMPLEMENTED\_BY}] \longrightarrow (REG) \longrightarrow [\text{:ISSUES\_TRANSMITTAL}] \longrightarrow (CR)$$

### 2.2. Performance Constraints
- Subgraph retrieval across up to 3 hops must complete within $<25\text{ms}$ in Neo4j.
- The returned entity set must explicitly package:
  - `nodes`: Array of complete node records with all attributes (`primary_key`, `name`, `fee_amount`, `effective_date`).
  - `edges`: Array of directed edge records with complete provenance metadata (`source_uri`, `selector`, `ingestion_timestamp`, `run_id`).
