# Ticket 005: End-to-End Integration Test Architecture, Payload Admissibility Governance, and Zero-Gesture Canvas Illumination Verification Oracles

- **Status:** Resolved
- **Claimed by:** `wayfinder-test-plan`
- **Blocked by:** `ticket-001.md`, `ticket-002.md`, `ticket-003.md`, `ticket-004.md`
- **Target Specification:** `functional_specification_009.md` (Sections 1, 2, 3, 4.1, 4.2, 4.3, 4.4, 5.1, 5.2, 5.3, 5.4, 6.1–6.5)
- **Target Components:**
  - `src/frontend/src/components/GraphCanvas.tsx`
  - `src/frontend/src/context/GraphSyncContext.tsx`
  - `src/frontend/src/components/AgentChatDrawer.tsx`

---

## 1. Architectural Question

How must integration tests verify that `GraphCanvas.tsx`, `GraphSyncContext.tsx`, and `AgentChatDrawer.tsx` satisfy all immediate reactive redraw, amber node/edge illumination, synchronized camera framing, responsive de-illumination, selection/hover continuity, and edge-case error boundary requirements of `functional_specification_009.md` using exclusively authentic codebase schemas and real API/producer payloads with zero synthetic mocks?

---

## 2. Schema Grounding & Payload Admissibility Resolution (`INV-PAYLOAD-01`)

All integration test inputs and state payloads are strictly constrained to the following authentic codebase schemas and real producers. Any hand-synthesized fixture, dummy JSON blob, renamed field, or artificially populated optional property is classified as an `{error}` and renders the test `{insufficient}`.

1. **Topological Graph Input Schema (`src/frontend/src/types/graph.ts` & `src/api/models.py`):**
   - **Backend Producer:** `GET /api/graph/topology` (default `policy_keyword="LTA"`, optional `jurisdiction_filter`, `state_filter`, `include_fee_schedules`) returning `TopologyResponse` (`nodes: List[TopologyNode]`, `edges: List[TopologyEdge]`, `total_nodes: int`, `total_edges: int`).
   - **Frontend Schema Binding:** Transformed strictly through the `App.tsx` topology pipeline into:
     - `GraphNode`: `id: string`, `primary_key: string`, `label: string`, `name: string`, `properties: NodeProperties`, `radius: number`, `color: string`, `shape: string`, and optional D3 simulation coordinates `x?: number`, `y?: number`, `vx?: number`, `vy?: number`, `fx?: number | null`, `fy?: number | null`.
     - `GraphLink`: `source: string | GraphNode`, `target: string | GraphNode`, `label: string`, `edge_key: string`, `provenance: EdgeProvenance` (`source_uri: string`, `selector: string`, `ingestion_timestamp: string`, `run_id: string`).
   - **Optional Packing Preservation:** When nodes are ingested from `/api/graph/topology`, simulation fields (`x`, `y`, `vx`, `vy`, `fx`, `fy`) are initially omitted (`undefined`) and must only be populated by the real `d3.forceSimulation` tick lifecycle in `GraphCanvas.tsx`. Sparse optional properties in `NodeProperties` (`title`, `state_code`, `state_name`, `code`, `description`, `fee_amount`, `is_rural`, `transmittal_number`, `benefit_category`, `contractor_name`, `states`, `source_url`) must never be synthetically backfilled.

2. **GraphRAG Query & Subgraph Synchronization Schema (`src/frontend/src/types/graph.ts` & `src/graphrag/models.py`):**
   - **Backend Producer:** `POST /api/graphrag/query` accepting `GraphRAGQueryRequest` (`query: str`, `model_id?: string`, `state_code?: string`, `jurisdiction_code?: string`, `primary_key?: string`, `anchor_node_pk?: string`) and returning `GraphRAGQueryResponse`:
     - `answer: string`
     - `active_node_pks: string[]`
     - `active_edge_keys: string[]`
     - `anchors: AnchorEntity[]` (`slot: string`, `primary_key: string`, `matched_text: string`, `entity_type: string`, `label: string`)
     - `provenance_sources: EdgeProvenance[]`
     - `duration_ms: number`
   - **Admissible Canonical Query Inputs (Verified Live Against Neo4j in `tests/test_api_endpoints.py` & `tests/test_graphrag_pipeline.py`):**
     - Patient benefit routing query: `"I am from Wisconsin, survived breast cancer, need lymphedema supplies, I'm on Medicare, can you help?"` (yields active path containing `"STATE-WI"`, `"JURIS-DME-B"`, `"CMS-CR-13286"`, `"CMS-MCD-A59508"`, `"ICD10-I97.2"`, `"HCPCS-A6522"`, `"FEE-A6522-WI-NR-2024"` and `>= 7` active edges).
     - Cross-policy convergence query: `"How do IVIG and LTA converge under federal law?"` (yields active path containing `"POLICY-LTA"`, `"POLICY-IVIG"`, `"PLAW-117-328"`, `"FR-2023-24455"`).
     - Single-state query: `"What are the allowable compression rates in New York?"` (yields active path containing `"STATE-NY"`, `"JURIS-DME-A"`, `"CMS-MCD-A59508"`).
     - One-click node inquiry (`inquireNode`): `constructInquiryPrompt(node)` with `primary_key: "PLAW-117-328"` (yields `"PLAW-117-328"` and `>= 6` active nodes, `>= 5` active edges).
     - Empty active-node boundary: `POST /api/graphrag/subgraph` with `{"anchors": []}` or `GraphRAGQueryResponse` carrying `active_node_pks: []` and `active_edge_keys: []`.

3. **Synchronization Context & Visual Theme Contracts (`src/frontend/src/context/GraphSyncContext.tsx` & `src/frontend/src/styles/graph_theme.ts`):**
   - `GraphSyncContextType` state fields: `activeNodePKs: Set<string>`, `activeEdgeKeys: Set<string>`, `isIlluminated: boolean`, `selectedNode: GraphNode | null`, `seededAnchor: AnchorEntity | null`, `isChatOpen: boolean`, `messages: ChatMessage[]`, `isQueryLoading: boolean`, `errorMsg: string | null`, `filterJurisdiction: string`, `filterState: string`, `policyKeyword: string`.
   - `CANVAS_PALETTE` visual constants: `bgVoid: '#0a1128'`, `gridLines: 'rgba(30, 41, 59, 0.45)'`, `accentAmber: '#ffb703'`, `activeHalo: '#f59e0b'`, `activeEdge: '#fbbf24'`, `inactiveAttenuation: 0.18`, `textPrimary: '#f8fafc'`, `textMuted: '#94a3b8'`, `panelBg: 'rgba(15, 23, 42, 0.92)'`, `panelBorder: '#1e293b'`.

---

## 3. Locked Integration Verification Decisions (`INV-ASSERTION-01`)

1. **Oracle 1 — Zero-Gesture Immediate Reactive Redraw & Amber Visual Illumination (`functional_specification_009.md` Sections 4.1, 5.2, 6.1, 6.4):**
   - **Boundary:** `GraphSyncProvider` + `GraphCanvas` + `AgentChatDrawer` / `NodeDetailDrawer`.
   - **Condition:** When `setIlluminatedPath` or `submitInquiry` / `inquireNode` commits a non-empty `active_node_pks` and `active_edge_keys` payload, including when the D3 force simulation has already settled (`alpha < alphaMin`), zero `mousemove`, `mousedown`, `wheel`, or drag events may be dispatched on the canvas.
   - **Required Asserted Outputs (`{correct required outputs}`):**
     - `isIlluminated` transitions immediately to `true`, `activeNodePKs` contains the exact primary keys from `active_node_pks`, and `activeEdgeKeys` contains the exact keys from `active_edge_keys`.
     - The Blueprint HUD status indicator in `GraphCanvas` immediately updates from `'EXPLORATION MODE'` (`#94a3b8`) to `'PATH ILLUMINATED'` (`#ffb703`).
     - The HTML5 2D rendering context executes an immediate repaint (`render()` synchronously and on the next animation frame via `renderRef.current()`) wherein:
       - Every active node (`activeNodePKs.has(node.primary_key)`) is drawn at `globalAlpha = 1.0` with an outer radial glow halo fill of `'rgba(255, 183, 3, 0.45)'`, an inner halo stroke of `'#f59e0b'` (`CANVAS_PALETTE.activeHalo`), a base circle fill of `'#ffb703'` (`CANVAS_PALETTE.accentAmber`), a border stroke of `'#fde68a'`, and a leader caption badge with `'rgba(10, 17, 40, 0.92)'` background, `'rgba(255, 183, 3, 0.45)'` border, bold `700` font weight, and `'#ffb703'` text fill.
       - Every active relationship edge (`activeEdgeKeys.has(link.edge_key)` or connecting two active endpoints) is drawn at `globalAlpha = 1.0` with stroke `'#fbbf24'` (`CANVAS_PALETTE.activeEdge`), line width `3.5 / transform.k`, and a directional chevron filled with `'#ffb703'`.
       - Non-active, non-selected, non-hovered nodes and non-active edges are attenuated to `globalAlpha = 0.18` (`CANVAS_PALETTE.inactiveAttenuation`).

2. **Oracle 2 — Synchronized Camera Viewport Framing & Decoupled D3 Zoom Closure (`functional_specification_009.md` Sections 4.2, 6.3, 6.5):**
   - **Boundary:** `GraphCanvas` (`d3.forceSimulation`, `d3.zoom`, `frameActiveSubgraph`, `renderRef`).
   - **Condition:** Topology nodes loaded with initial `x: undefined, y: undefined` are passed into `GraphCanvas`, followed by path illumination.
   - **Required Asserted Outputs (`{correct required outputs}`):**
     - `d3.forceSimulation` synchronously pre-ticks (`simulation.tick(1)`) so all `GraphNode` instances possess numeric `(x, y)` coordinates prior to `frameActiveSubgraph` execution.
     - `d3.zoom` is initialized once on mount and delegates every `'zoom'` event to `renderRef.current()`, never to a stale pre-illumination `render` closure.
     - `frameActiveSubgraph` paints the illuminated state immediately at `t = 0ms`, interrupts any prior transition, interpolates the viewport transform over `350ms` (`d3.easeCubicInOut`) to center and fit the active subgraph bounding box (`0.6 <= scale <= 2.5`), renders every intermediate transition frame with `isIlluminated === true` and active amber styling, and executes a final stabilization render on transition `'end'`.

3. **Oracle 3 — Zero-Gesture Responsive De-Illumination Across All Reset Triggers (`functional_specification_009.md` Sections 4.3, 6.2):**
   - **Boundary:** `GraphSyncContext` + `FilterToolbar` (`✕ RESET PATH` and filter reset) + `AgentChatDrawer` (`✕` close button) + `GraphCanvas`.
   - **Condition:** While a path is illuminated (`isIlluminated === true`), the user either clicks `✕ RESET PATH` in `FilterToolbar`, resets the jurisdiction filter to `""` (All Jurisdictions), or clicks the `✕` close button in `AgentChatDrawer`, with zero canvas mouse gestures.
   - **Required Asserted Outputs (`{correct required outputs}`):**
     - `clearIllumination()` executes immediately: `isIlluminated` reverts to `false`, `activeNodePKs.size === 0`, `activeEdgeKeys.size === 0`, and `isQueryLoading === false`.
     - Any in-flight D3 zoom transition on the canvas is immediately interrupted (`d3.select(canvas).interrupt()`).
     - `GraphCanvas` immediately repaints to baseline blueprint mode: Blueprint HUD displays `'EXPLORATION MODE'`, nodes render at `globalAlpha = 1.0` using their domain `visual.badgeColor` from `NODE_THEME_REGISTRY` without amber glow halos, and edges render at baseline `globalAlpha = 0.55` with `'rgba(71, 85, 105, 0.6)'` stroke.

4. **Oracle 4 — Preserved Node Selection Ring and Hover Inspection Continuity (`functional_specification_009.md` Sections 4.4.1, 4.4.2):**
   - **Boundary:** `GraphCanvas` + `NodeDetailDrawer` + `GraphSyncContext`.
   - **Condition:** A node is selected (`selectNode(node)`) before or during active path illumination, and pointer hover (`onMouseMove`) moves across active and non-active nodes while `isIlluminated === true`.
   - **Required Asserted Outputs (`{correct required outputs}`):**
     - The selected node retains `globalAlpha = 1.0` (never attenuated to `0.18` even if not in `activeNodePKs`) and renders its distinctive outer dashed selection ring (`strokeStyle = '#38bdf8'`, `lineWidth = 2.5 / transform.k`, radius `radius + 9 / transform.k`).
     - Hovering over any node during illumination preserves `isIlluminated === true` and `activeNodePKs` intact, renders the hovered node at `globalAlpha = 1.0` with a `'#ffffff'` border ring, and renders the non-blocking (`pointerEvents: 'none'`) floating tooltip (`data-testid="node-hover-tooltip"`) displaying the authentic `hoveredNode.label`, `hoveredNode.primary_key`, and `hoveredNode.name`.
     - Drag-release gestures (`e.defaultPrevented === true`) do not clear or overwrite `selectedNode`.

5. **Oracle 5 — Error Boundaries: Rapid Successive Queries, Empty Subgraph Response, and Resize Continuity (`functional_specification_009.md` Sections 5.1, 5.3, 5.4):**
   - **Boundary:** `GraphSyncContext` (`submitInquiry`, `setIlluminatedPath`, `clearIllumination`, `latestQueryIdRef`) + `GraphCanvas` (`syncCanvasDimensions`, `ResizeObserver`, `window` `'resize'`).
   - **Required Asserted Outputs (`{correct required outputs}`):**
     - **Rapid Successive Queries (Section 5.1):** Invoking `submitInquiry(queryA)` followed immediately by `submitInquiry(queryB)` while `queryA` is still in flight does not drop `queryB`. When responses resolve (in order or out of order), `latestQueryIdRef` guarantees that only `queryB`'s `GraphRAGQueryResponse` commits to `activeNodePKs`, `activeEdgeKeys`, and `messages`, and `GraphCanvas` interrupts `queryA`'s camera transition to frame and illuminate `queryB`'s subgraph. Furthermore, if `clearIllumination()` is called while a query is in flight, the late response is discarded and cannot re-illuminate the canvas.
     - **Empty Subgraph Response (Section 5.3):** Passing a `GraphRAGQueryResponse` with `active_node_pks: []` to `setIlluminatedPath` while the canvas is illuminated immediately sets `isIlluminated = false`, clears `activeNodePKs` and `activeEdgeKeys`, and repaints the canvas to baseline `1.0` node opacity rather than leaving all nodes dimmed at `0.18` opacity.
     - **Canvas Resize Continuity (Section 5.4):** Dispatching a `window` `'resize'` event or `ResizeObserver` callback during or after query delivery updates `canvas.width` and `canvas.height` to `Math.round(rect.width * dpr)` and `Math.round(rect.height * dpr)` and immediately invokes `renderRef.current()` so the illuminated path remains painted on the resized buffer without requiring user interaction.

---

## 4. Explicit Error States (`{errors}`)

Any of the following states during test execution must immediately fail the verification suite as an `{error}`:
- Canvas nodes in `activeNodePKs` remain drawn with `visual.badgeColor` instead of `'#ffb703'` or lack the `'rgba(255, 183, 3, 0.45)'` radial glow halo after query resolution without a manual mouse gesture.
- D3 zoom transition ticks overwrite the illuminated canvas with a stale `isIlluminated = false` closure.
- `setIlluminatedPath` with `active_node_pks: []` sets `isIlluminated = true` or attenuates baseline nodes to `0.18` opacity.
- Rapid successive `submitInquiry` calls drop the second query due to `isQueryLoading` or allow an earlier query response to overwrite a newer query or a subsequent `clearIllumination()` reset.
- Closing `AgentChatDrawer` (`✕`) leaves `isIlluminated === true` or fails to trigger an immediate baseline repaint.
- Any test uses a mocked/synthesized payload containing fields not defined in `src/frontend/src/types/graph.ts`, `src/api/models.py`, or `src/graphrag/models.py`.
