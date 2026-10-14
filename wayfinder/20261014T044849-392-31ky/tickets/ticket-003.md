# Ticket 003: Interactive Engine Graph Canvas: Node Dragging, Category Filtering, Edge Selection & Deep Provenance Inspection (`GraphCanvas.tsx`, `NodeDetailDrawer.tsx`, `GraphSyncContext.tsx`)

- **Ticket ID:** `ticket-003`
- **Title:** Interactive Engine Graph Canvas: Node Dragging, Category Filtering, Edge Selection & Deep Provenance Inspection (`GraphCanvas.tsx`, `NodeDetailDrawer.tsx`, `GraphSyncContext.tsx`)
- **Status:** Resolved
- **Claimed by:** `wayfinder-read-and-plan`
- **Blocked By:** `ticket-001`
- **Governing Specification:** `functional_specification_016.md` (§3.1 Interactive Engine Graph Canvas, §5.1.3 Interactive Showcase Verification)

---

## 1. Decision Question

What exact modifications are required across `src/frontend/src/types/graph.ts`, `src/frontend/src/context/GraphSyncContext.tsx`, `src/frontend/src/components/GraphCanvas.tsx`, and `src/frontend/src/components/NodeDetailDrawer.tsx` to fulfill every interactive canvas requirement in `functional_specification_016.md` §3.1:
1. Panning, zooming, clicking, selecting, **dragging nodes**, and **filtering nodes by entity category** across all 8-hop entity categories;
2. **Selecting any edge** to display its relationship type (`label`), directional linkage (`source_pk -> label -> target_pk`), and provenance metadata (`source_uri`, `selector`, `run_id`, `ingestion_timestamp`); and
3. **Selecting any node** to open a detailed entity inspection panel displaying all native keys, derived keys, statutory/regulatory text excerpts, citations, and complete provenance metadata (`source_uri`, `selector`, `run_id`, `ingestion_timestamp`)?

---

## 2. Codebase Grounding

1. **`src/frontend/src/components/GraphCanvas.tsx` (Lines 553–660):**
   - Currently attaches `d3.zoom` to `canvasRef.current`, and implements `findNodeAtEvent` on `onClick` and `onMouseMove`.
   - Does NOT yet implement node dragging (`fx`/`fy` pointer drag interaction) or edge click hit-testing (`findEdgeAtEvent`).
2. **`src/frontend/src/context/GraphSyncContext.tsx` (Lines 150–180):**
   - Tracks `selectedNode: GraphNode | null`, `filterJurisdiction`, `filterState`, `policyKeyword`.
   - Does NOT yet track `selectedEdge: GraphLink | null`, `selectEdge: (edge: GraphLink | null) => void`, `filterCategory: string`, `setFilterCategory: (category: string) => void`, or `includeFeeSchedules: boolean`.
3. **`src/frontend/src/components/NodeDetailDrawer.tsx` (Lines 15–467):**
   - Currently renders only when `selectedNode` is non-null, showing `System Description`, `Government Source Provenance`, `Entity Attributes`, and `Connected Neighbors` (where only `source_uri` of neighbor edges is shown, omitting `selector`, `run_id`, `ingestion_timestamp`, and omitting a dedicated Edge Inspection view when an edge is selected).

---

## 3. Locked Architectural Decision

### 3.1 Type Definitions (`src/frontend/src/types/graph.ts`)
Add `EntityInspectionData`, `BackendHealthStatus`, and `ExecutionStatus` interfaces to `src/frontend/src/types/graph.ts`:
```typescript
export type ExecutionStatus = 'idle' | 'querying' | 'streaming' | 'completed' | 'error';

export type BackendConnectionState = 'connecting' | 'online' | 'cold_starting' | 'unreachable' | 'error';

export interface EntityInspectionData {
  primary_key: string;
  label: string;
  name: string;
  properties: NodeProperties;
  text_excerpt: string;
  citations: string[];
  provenance: EdgeProvenance[];
  relationships: {
    source_pk: string;
    target_pk: string;
    label: string;
    edge_key: string;
    provenance: EdgeProvenance;
  }[];
}
```

### 3.2 Synchronization Context State (`src/frontend/src/context/GraphSyncContext.tsx`)
Extend `GraphSyncContextType` and `GraphSyncProvider`:
- `selectedEdge: GraphLink | null` and `selectEdge: (edge: GraphLink | null) => void`:
  - Calling `selectEdge(edge)` sets `selectedEdge(edge)` and clears `selectedNode(null)` (or keeps `selectedEdge` focused in `NodeDetailDrawer`).
  - Calling `selectNode(node)` sets `selectedNode(node)` and clears `selectedEdge(null)`.
- `filterCategory: string` (default `""` for all categories) and `setFilterCategory: (category: string) => void`.
- `searchQuery: string` (default `""`) and `setSearchQuery: (q: string) => void`.
- `includeFeeSchedules: boolean` (default `false`) and `setIncludeFeeSchedules: (inc: boolean) => void`.
- `dataSourceMode: 'live' | 'precomputed_lta' | 'precomputed_ivig'` (default `'live'`) and `setDataSourceMode: (mode: 'live' | 'precomputed_lta' | 'precomputed_ivig') => void`.
- `executionStatus: ExecutionStatus` (`'idle' | 'querying' | 'streaming' | 'completed' | 'error'`) and `setExecutionStatus: (status: ExecutionStatus) => void`.
- `backendState: BackendConnectionState` and `backendMessage: string | null`.

### 3.3 Node Dragging & Edge Hit-Testing (`src/frontend/src/components/GraphCanvas.tsx`)
1. **Node Dragging Interaction:**
   - Track `draggedNodeRef = useRef<GraphNode | null>(null)` and `isDraggingRef = useRef<boolean>(false)`.
   - In `d3.zoom` filter (`.filter((event) => ...)`): if `event.type === 'mousedown'` and `findNodeAtRawCoords(event.clientX, event.clientY)` returns a `GraphNode`, suppress canvas pan zoom on that mousedown and initiate node drag:
     - On `onMouseDown`: if a node is under the pointer, set `draggedNodeRef.current = node`, `node.fx = node.x`, `node.fy = node.y`, and `simulationRef.current?.alphaTarget(0.2).restart()`.
     - On `onMouseMove`: if `draggedNodeRef.current` is active, mark `isDraggingRef.current = true`, convert pointer coordinates via `transformRef.current` to graph space, update `draggedNodeRef.current.fx = graphX`, `draggedNodeRef.current.fy = graphY`, `draggedNodeRef.current.x = graphX`, `draggedNodeRef.current.y = graphY`, and call `renderRef.current()`.
     - On `onMouseUp` / `onMouseLeave`: if `draggedNodeRef.current` is active, set `simulationRef.current?.alphaTarget(0)` and clear `draggedNodeRef.current = null`.
2. **Edge Click & Hover Hit-Testing (`findEdgeAtEvent`):**
   - Implement deterministic point-to-segment distance calculation in graph coordinate space for every rendered link `(source.x, source.y) -> (target.x, target.y)`:
     - Compute projection parameter $t = \max(0, \min(1, \frac{(\mathbf{p} - \mathbf{a}) \cdot (\mathbf{b} - \mathbf{a})}{\|\mathbf{b} - \mathbf{a}\|^2}))$ and perpendicular distance $d = \|\mathbf{p} - (\mathbf{a} + t(\mathbf{b} - \mathbf{a}))\|$.
     - If $d \le \frac{6}{\text{transform.k}}$ (6 screen pixels), return the closest `GraphLink`.
   - On canvas click (`handlePointerDown` / `onClick` when not dragging):
     - First check `findNodeAtEvent(e)`. If a node is hit, call `selectNode(hitNode)`.
     - Otherwise check `findEdgeAtEvent(e)`. If an edge is hit, call `selectEdge(hitEdge)`.
     - Otherwise call `selectNode(null)` and `selectEdge(null)`.
   - Highlight `selectedEdge` on the canvas with a cyan/amber selection stroke (`#38bdf8`, `lineWidth = 4.0 / transform.k`) and render its relationship type badge at the edge midpoint.

### 3.4 Deep Entity & Edge Provenance Inspection (`src/frontend/src/components/NodeDetailDrawer.tsx`)
1. **Edge Inspection Mode (when `selectedEdge` is non-null and `selectedNode` is null):**
   - Render a dedicated **Relationship / Edge Inspection Panel** inside `NodeDetailDrawer` (`data-testid="edge-detail-drawer"`):
     - Relationship Type badge (`selectedEdge.label`) and composite `edge_key` (`source_pk -> label -> target_pk`).
     - Directional Linkage card showing Source Entity (`sourceNode.label`, `sourceNode.primary_key`, `sourceNode.name`, clickable to inspect node) $\longrightarrow$ Relationship (`selectedEdge.label`) $\longrightarrow$ Target Entity (`targetNode.label`, `targetNode.primary_key`, `targetNode.name`, clickable to inspect node).
     - Complete Provenance Metadata table displaying all 4 mandatory provenance keys:
       - `source_uri` (rendered as clickable external link when starting with `http`)
       - `selector`
       - `run_id`
       - `ingestion_timestamp`
2. **Deep Entity Node Inspection Mode (when `selectedNode` is non-null):**
   - Fetch deep inspection metadata from `${getApiBaseUrl()}/api/entities/${encodeURIComponent(selectedNode.primary_key)}` when in live backend mode, merging with local node/edge properties.
   - Display dedicated sections in `NodeDetailDrawer` (`data-testid="node-detail-drawer"`):
     - **Statutory / Regulatory / Clinical Text Excerpt:** Displays `text_excerpt` (`props.text`, `props.description`, `props.long_description`, etc.).
     - **Official Citations & Derived Keys:** Displays `citation_string`, `citation`, `cfr_reference`, `uslm_section_path`, `docket_id`, `rin`, `cr_number`, `transmittal_number`, `article_id`.
     - **Native & Derived Entity Attributes:** Full key-value table of all persisted properties.
     - **Complete Provenance Metadata (`source_uri`, `selector`, `run_id`, `ingestion_timestamp`):** Aggregated from the node and its incident edges so every single provenance field (`source_uri`, `selector`, `run_id`, `ingestion_timestamp`) is explicitly visible.
     - **Connected Neighbors & Directional Edges:** Clicking a neighbor node selects that node; clicking a relationship badge selects that edge (`selectEdge`).

---

## 4. Verification Criteria

- Users can pan, zoom, click, select, and drag nodes on `GraphCanvas`.
- Selecting any node opens `NodeDetailDrawer` displaying native keys, derived keys, statutory/regulatory text excerpts, citations, and all 4 provenance metadata fields (`source_uri`, `selector`, `run_id`, `ingestion_timestamp`).
- Selecting any edge on the canvas (or clicking an edge badge in the drawer) opens the Edge Inspection view displaying its relationship type (`label`), directional linkage (`source_pk -> label -> target_pk`), and provenance metadata.
