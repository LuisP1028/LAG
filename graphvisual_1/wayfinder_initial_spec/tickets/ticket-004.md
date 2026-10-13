# Decision Ticket 004: Bidirectional Visual Canvas Synchronization and Active Subgraph Illumination Specification

**Ticket ID:** `ticket-004.md`  
**Scope:** GraphRAG Stage 4 - Canvas-Agent Interaction Bus  
**Status:** RESOLVED  
**Claimed By:** `wayfinder-graphrag-spec`  
**Blocked By:** `ticket-002.md`

---

## 1. Architectural Question
How must the visual React canvas interact with the GraphRAG pipeline so that user actions on the graph seed conversational inquiries, and the exact subgraphs retrieved by GraphRAG illuminate on the canvas within $<500\text{ms}$?

---

## 2. Decision and Specification Requirements

### 2.1. Canvas-to-Agent Event Flow
1. **Interactive Node Click Handlers:**
   - Selecting a node (e.g., `JURIS-DME-B (CGS)` or `CMS-MCD-A59508`) highlights the node on the canvas and populates a context card.
   - Quick-action buttons trigger automated GraphRAG inquiries:
     - *"What states does this contractor cover?"*
     - *"What diagnoses are approved under this coverage policy?"*
     - *"What are the payment rates in my state?"*
2. **Context Seeding:**
   - The selected entity primary key is passed as an immutable anchor to the GraphRAG pipeline, ensuring sub-second execution without free-form search ambiguity.

### 2.2. Agent-to-Canvas Highlighting Bus
1. **Payload Emission:**
   - The GraphRAG retrieval response emits two synchronized payloads:
     1. Textual stream to the chat window (the plain-English synthesized response).
     2. A JSON message to the visualization canvas containing:
        - `active_node_pks`: Array of primary keys in the retrieved subgraph (e.g., `["STATE-WI", "JURIS-DME-B", "CMS-CR-13286", "CMS-MCD-A59508", "ICD10-I97.2", "HCPCS-A6522", "FEE-A6522-WI-NR-2024"]`).
        - `active_edge_keys`: Array of connecting directed edge identifiers.
2. **Visual Canvas State Transition:**
   - **Active Highlight:** Render a glowing aura / bright border around all active nodes in the path.
   - **Background Attenuation:** Dim the opacity of unselected nodes to 20% to eliminate visual clutter.
   - **Camera Interpolation:** Execute smooth camera pan and zoom interpolation (duration: 350ms) to center and frame the illuminated subgraph.
