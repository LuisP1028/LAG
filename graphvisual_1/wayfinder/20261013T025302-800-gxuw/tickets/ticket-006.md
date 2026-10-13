# Decision Ticket 006: Bidirectional Canvas-Agent Synchronization Bus and Path Illumination Specification

**Ticket ID:** `ticket-006.md`  
**Scope:** Canvas-Agent Interaction Bus & Real-Time Synchronization  
**Status:** RESOLVED  
**Claimed By:** `wayfinder-read-and-plan`  
**Blocked By:** `ticket-004.md`, `ticket-005.md`

---

## 1. Architectural Question

How must the React client synchronize state bidirectionally between the visual graph canvas and the GraphRAG chat interface so that user clicks on the canvas immediately seed conversational anchors, and the exact subgraphs returned by GraphRAG illuminate and frame within $<500\text{ms}$?

---

## 2. Decision and Specification Requirements

### 2.1. Synchronization Bus Architecture
- **State Store:** `src/frontend/context/GraphSyncContext.tsx`
- **Bus Mechanism:** React Context Provider exposing unified state and dispatch actions:
  ```typescript
  interface GraphSyncState {
    activeNodePKs: Set<string>;
    activeEdgeKeys: Set<string>;
    selectedNode: GraphNode | null;
    seededAnchor: AnchorEntity | null;
    isIlluminated: boolean;
    quickPrompts: string[];
  }
  ```

### 2.2. Canvas-to-Agent Event Flow
1. **Node Selection Handler:**
   - When a user clicks a node on the canvas:
     - Dispatches `SELECT_CANVAS_NODE({ node })`.
     - Populates `seededAnchor` with `{ slot: "entity", primary_key: node.primary_key, entity_type: node.label }`.
     - Opens `NodeDetailDrawer`.
2. **Contextual Quick-Action Prompts:**
   - The chat interface dynamically generates quick-action query pills tailored to the selected node label:
     - For `CoveragePolicy`:
       - *"What diagnoses are approved under this coverage policy?"*
       - *"List all covered HCPCS procedure codes"*
       - *"What is the governing statutory authority?"*
     - For `Jurisdiction`:
       - *"What states does this DME MAC contractor cover?"*
       - *"Show active change requests for this contractor"*
     - For `HCPCSCode`:
       - *"What is the allowable Medicare reimbursement for this code in Wisconsin?"*
       - *"What clinical documentation is required to prescribe this item?"*
     - For `Policy`:
       - *"How did this policy converge with IVIG under federal law?"*
       - *"What Public Law enacted this program?"*

### 2.3. Agent-to-Canvas Highlighting Bus
1. **GraphRAG Subgraph Emission:**
   - Upon completion of a GraphRAG query, the backend returns:
     ```json
     {
       "active_node_pks": ["STATE-WI", "JURIS-DME-B", "CMS-CR-13286", "CMS-MCD-A59508", "ICD10-I97.2", "HCPCS-A6522", "FEE-A6522-WI-NR-2024"],
       "active_edge_keys": [
         "JURIS-DME-B->COVERS_STATE->STATE-WI",
         "CMS-CR-13286->APPLIES_TO_JURISDICTION->JURIS-DME-B",
         "CMS-CR-13286->MANDATES_POLICY->CMS-MCD-A59508",
         "CMS-MCD-A59508->ALLOWS_DIAGNOSIS->ICD10-I97.2",
         "CMS-MCD-A59508->GOVERNS->HCPCS-A6522",
         "HCPCS-A6522->HAS_FEE_SCHEDULE->FEE-A6522-WI-NR-2024",
         "FEE-A6522-WI-NR-2024->APPLIES_TO->STATE-WI"
       ]
     }
     ```
2. **Synchronized Visual State Transitions:**
   - **Path Illumination:**
     - Nodes in `active_node_pks` receive an active visual highlight: outer pulsating halo (stroke color `#f59e0b`, width 4px), node radius expanded by 25%.
     - Edges in `active_edge_keys` render in bright amber (`#fbbf24`), stroke width boosted to 3.5px with directional arrow animation.
   - **Background Attenuation:**
     - All nodes and edges not in the active subgraph drop to 20% opacity (`rgba(..., 0.20)`), immediately drawing visual focus to the traversed path.
   - **Camera Framing & Interpolation:**
     - The canvas computes the 2D bounding box encompassing all coordinates in `active_node_pks`.
     - Executes smooth camera zoom and pan interpolation over a duration of 350ms with cubic ease-in-out easing.
   - **Total Latency Constraint:** Path illumination and camera positioning must complete within $<500\text{ms}$ of receiving the backend payload.
