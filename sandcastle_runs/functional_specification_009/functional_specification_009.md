# Functional Specification: Immediate Synchronous Visualizer Illumination and Zero-Latency Canvas State Synchronization

**Document ID:** `functional_specification_009.md`  
**Status:** Requirements Specification  
**Implementation Guidance:** Strictly Prohibited (DO NOT CODE YET)  
**Taxonomy Reference:** [LANGUAGE.md](file:///Users/diesel/Desktop/LAG/LANGUAGE.md)

---

## 1. Objective and Problem Statement

This specification defines the functional requirements for eliminating latent canvas repainting and guaranteeing instantaneous visual synchronization between the GraphRAG query execution lifecycle and the HTML5 graph visualizer canvas.

### The Problem
Currently, after a user executes a GraphRAG query (either through a natural language prompt in the chat drawer or via the one-click "INQUIRE IN GRAPHRAG CHAT" action), the visualizer canvas exhibits a passive rendering delay:
1. **Dormant Canvas State:** The API response arrives, telemetry badges populate in the chat drawer (e.g., showing *11 Nodes Illuminated*), but the canvas does not light up. The nodes and edges remain dark in their default dormant blueprint state.
2. **Forced User Interaction:** The illuminated nodes and amber path highlights only appear after the user manually moves or adjusts the canvas (e.g., panning, dragging, zooming, or nudging the viewport).
3. **Degraded User Experience:** This latency creates a false impression of system failure or zero-node retrieval (`0 Nodes Illuminated`), breaking user trust and disrupting the one-click intelligence workflow established in `functional_specification_007.md`.

### The Desired Solution
The application must guarantee **immediate, zero-latency visual illumination**:
1. **Active Reactive Redraw:** As soon as query results are received and active node identifiers and edge keys are committed to state, the visualizer canvas must immediately and automatically redraw without requiring any user gestures.
2. **Instantaneous Amber Illumination:** Active nodes, glowing halo rings, connecting relationship edges, and node leader badges must illuminate on screen simultaneously with the arrival of the assistant answer.
3. **Seamless Viewport Framing:** The camera viewport transition framing the active subgraph must execute in perfect coordination with the visual illumination.
4. **Instantaneous De-Illumination:** When illumination is cleared or reset, the canvas must immediately return to its baseline appearance without requiring manual nudging.

---

## 2. Taxonomy and Evaluation Parameters

All evaluations must adhere strictly to [LANGUAGE.md](file:///Users/diesel/Desktop/LAG/LANGUAGE.md):

* **`{errors}`:** The canvas displays stale or unilluminated state after query resolution; active nodes remain dark until manual user interaction; canvas fails to redraw upon state commit; camera transitions decouple from visual highlights; or canvas rendering freezes.
* **`{correctness}`:** State transitions in active node identifiers (`activeNodePKs`), edge keys (`activeEdgeKeys`), or illumination flags (`isIlluminated`) immediately produce an exact visual update on the canvas, accurately rendering node colors, glow halos, line weights, and leader badges.
* **`{functionality}`:** A completely responsive visual synchronization system where every graph state transition (query illumination, clearing illumination, node selection, or filtering) is visually reflected on screen in real time without requiring manual user interaction to force a repaint.
* **`{correct required outputs}`:**
  1. Instantaneous illumination of active nodes in gold/amber upon query response arrival.
  2. Instantaneous illumination of active relationship edges connecting the retrieved path.
  3. Automatic smooth camera transition centering and framing the illuminated subgraph.
  4. Instantaneous clearing of illuminated highlights when the illumination state is reset.
  5. Zero requirement for manual mouse movement, dragging, clicking, or zooming to trigger the display of query results.
* **`{sufficient}`:** Complete specification of rendering lifecycles, event workflows, visual state transitions, and acceptance criteria without implementation instructions or code.
* **`{insufficient}`:** Any ambiguity regarding redraw triggers, state dependencies, or user interaction prerequisites.

---

## 3. Comparison: Current Behavior vs. Desired Behavior

| Feature Area | Current Functionality | Desired Functionality |
| :--- | :--- | :--- |
| **Post-Query Visual Response** | **Latent / Dormant:** Query finishes, chat displays results, but canvas nodes remain unlit until user manually pans or drags the canvas. | **Instantaneous / Active:** Query finishes, chat displays results, and canvas immediately illuminates active nodes and edges with zero delay. |
| **Interaction Prerequisite** | **Manual trigger required:** The user must physically interact with the canvas (drag, zoom, pan) to force a repaint cycle. | **Zero interaction required:** The canvas automatically redraws upon receiving state updates; user does not need to touch the mouse or keyboard. |
| **Visualizer State Synchronization** | Canvas rendering is decoupled from context state updates; canvas only repaints on simulation physics ticks or user mouse events. | Canvas rendering is tightly bound to state transitions; updates to `activeNodePKs`, `activeEdgeKeys`, or `isIlluminated` immediately execute a repaint. |
| **Viewport Framing Coordination** | Camera framing animation runs asynchronously without forcing immediate node highlight repainting. | Camera translation and visual highlight rendering execute in unified synchronization. |
| **Illumination Clearing** | Clearing illumination leaves highlighted nodes visible until the user moves the canvas again. | Clearing illumination immediately repaints the canvas back to its baseline non-highlighted state. |
| **User Perception** | Confusing: Users believe queries failed or returned no paths until they accidentally drag the canvas. | Seamless: One-click inquiry immediately highlights the path, delivers the answer, and frames the view. |

---

## 4. Functional Requirements

### 4.1. Immediate Reactive Redraw
1. **Trigger Condition:**
   * Whenever `activeNodePKs`, `activeEdgeKeys`, or `isIlluminated` changes in application state, the canvas must execute an immediate visual repaint cycle.
2. **Zero Interaction Dependency:**
   * The visual update must occur autonomously without waiting for user-initiated events (such as `mousemove`, `mousedown`, `wheel`, or viewport drag).
3. **Visual Elements Illuminated Immediately:**
   * All nodes whose primary keys belong to `activeNodePKs` must immediately render in gold/amber (`#ffb703`) with active radial glow halos (`rgba(255, 183, 3, 0.45)`).
   * All relationship edges whose keys belong to `activeEdgeKeys` must immediately render with active stroke color, increased line thickness, and amber contrast.
   * Node captions and leader badges for active nodes must immediately render with elevated contrast and active typography.

---

### 4.2. Synchronized Viewport Framing
1. **Coordinated Camera Motion:**
   * When an illuminated path is received, the viewport transition that centers and zooms to fit the active subgraph must begin immediately.
2. **Continuous Render During Transition:**
   * During any automated camera transition (e.g., cubic interpolation over 350ms), every intermediate animation frame must display the active nodes and edges in their fully illuminated state.
3. **Static Stabilization:**
   * When the camera reaches its final bounding frame, the final rendered frame must preserve complete illumination and high-contrast leader badges.

---

### 4.3. Responsive De-Illumination
1. **Immediate Reset:**
   * When the user clears the search, closes the chat inquiry, or triggers a reset action, `isIlluminated` reverts to false.
2. **Autonomous Repaint on Clear:**
   * The canvas must immediately repaint all nodes and edges back to their baseline blueprint styling (dark blue background, slate borders, muted edges) without requiring manual canvas movement.

---

## 4.4. Preserved Selection and Hover Continuity
1. **Selected Node Highlighting:**
   * If a node is currently selected in the detail drawer, its distinctive selection ring and pulse effect must persist uninterrupted during and after path illumination.
2. **Hover Interaction During Illumination:**
   * Hovering over nodes while the canvas is illuminated must continue to function smoothly, providing tooltips and node inspection without disrupting the illuminated path.

---

## 5. Error Boundaries and Edge Cases

1. **Rapid Successive Queries:**
   * If a user executes multiple queries in rapid succession, each arriving response must immediately overwrite the previous active path and instantly repaint the canvas with the newest active nodes.
2. **Simulation Settled State:**
   * In situations where the force simulation has already settled and stopped ticking (`alpha < alphaMin`), external state changes must still force an immediate canvas redraw rather than relying on physics ticks.
3. **Empty Subgraph Response:**
   * If a query returns zero active nodes, the canvas must immediately clear any existing illumination and maintain baseline rendering without throwing render errors or visual artifacts.
4. **Canvas Resizing During Query Delivery:**
   * If a window or panel resize event coincides with query completion, the canvas must resize its buffer and render the illuminated path accurately at the new dimensions.

---

## 6. Acceptance Criteria

The implementation will be considered complete and `{sufficient}` when:

1. **Zero-Gesture Illumination:** Submitting any query (via chat drawer prompt or one-click "INQUIRE IN GRAPHRAG CHAT") causes the target nodes and connecting paths to illuminate in amber/gold **immediately** upon query completion, without requiring any mouse movement or canvas adjustment.
2. **Zero-Gesture De-Illumination:** Triggering a clear or reset action immediately un-illuminates the canvas without requiring user interaction.
3. **Seamless Viewport Framing:** The camera smoothly zooms and centers on the illuminated subgraph while displaying the active amber highlights throughout the motion.
4. **High-Density Node Visibility:** Active node captions and leader badges are immediately visible upon query receipt.
5. **Frame Rate Stability:** Immediate repainting maintains smooth 60 FPS visualizer performance without freezing or stuttering.
