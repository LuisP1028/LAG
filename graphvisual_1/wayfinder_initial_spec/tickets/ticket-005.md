# Decision Ticket 005: Master Specification Synthesis and Edits for functional_specification_004.md

**Ticket ID:** `ticket-005.md`  
**Scope:** Specification Compilation & Synthesis  
**Status:** RESOLVED  
**Claimed By:** `wayfinder-graphrag-spec`  
**Blocked By:** `ticket-001.md`, `ticket-002.md`, `ticket-003.md`, `ticket-004.md`

---

## 1. Architectural Question
How must `functional_specification_004.md` be edited to completely replace the obsolete tool-calling/text-to-cypher model with the comprehensive, zero-hallucination GraphRAG specification defined across Tickets 001 through 004?

---

## 2. Decision and Specification Requirements

### 2.1. Exact Sections in `functional_specification_004.md` Targeted for Edits

1. **Document Title & Scope (Section 1):**
   - Retitle to: `# Functional Specification: Browser-Based React Graph Visualization & Hugging Face GraphRAG Architecture`
   - Explicitly define the three coupled pillars:
     1. Interactive Graph Visualization
     2. Hugging Face GraphRAG Engine (Zero bespoke queries, zero Cypher hallucination)
     3. Bidirectional Canvas-Agent Synchronization
2. **Taxonomy & Invariant Definitions (Section 2):**
   - Redefine `{functionality}` around unstructured natural language patient routing and topological subgraph retrieval.
   - Redefine `{correct required outputs}` to mandate zero-hallucination factual synthesis and simultaneous path illumination.
3. **GraphRAG Architecture & Pipeline Stages (Section 4):**
   - Remove tool-calling and Cypher generation clauses.
   - Insert the complete 5-stage GraphRAG pipeline:
     - Stage 1: Entity Anchor Linking (Layperson Vocabulary Normalization)
     - Stage 2: Generalized Topological Subgraph Expansion ($k$-hop neighborhood retrieval)
     - Stage 3: Structured Context Assembly (Factual statements + Edge Provenance)
     - Stage 4: Synthesis & Anti-Hallucination Invariant (`INV-FAIL-FAST`)
     - Stage 5: Mandatory Provenance Citation (`INV-PROVENANCE-COMPLETENESS`)
4. **Synchronization Bus Contract (Section 5):**
   - Update event flow: Canvas clicks seed anchor entities; GraphRAG responses emit active node/edge ID arrays to trigger viewport pan/zoom and path illumination.
5. **Real-World Functional Workflows (Section 6):**
   - Replace generic developer queries with Workflow 1: Real-world patient benefit routing (*"I am from Wisconsin, survived breast cancer, need lymphedema supplies, I'm on Medicare"*).
   - Workflow 2: Clinical Coverage & Diagnosis Bridging (`INV-NO-KEYWORD-BRIDGING`).
   - Workflow 3: Cross-Policy Comparative Lineage (IVIG & LTA omnibus convergence under Public Law 117-328).
6. **Strict Invariants & Performance SLA (Section 7):**
   - **Zero Cypher Generation:** LLM never writes Cypher syntax; 0 syntax errors, 0 retry round-trips.
   - **Zero Orphan Tolerance:** Invariant `INV-UNBROKEN-ANCESTRY` strictly enforced; orphaned entities cause immediate fatal ingestion failure. Unanchored fallback clusters are strictly prohibited.
   - **Sub-Second Latency SLA:** Neo4j topological expansion executes in $<20\text{ms}$; total user prompt to canvas illumination latency $<1.5\text{s}$.
7. **Verification & Acceptance Criteria (Section 8):**
   - Defines measurable test criteria for patient benefit routing, synchronized visual illumination, and provenance completeness.
