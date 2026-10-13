# Ticket 003: Synchronized Camera Viewport Framing and Rapid Query Transition Interruption

- **Status:** Resolved
- **Claimed by:** `wayfinder-read-and-plan`
- **Blocked by:** `ticket-001.md`, `ticket-002.md`
- **Target Specification:** `functional_specification_009.md` (Sections 4.2.1, 4.2.2, 4.2.3, 4.3.2, 5.1, 6.2, 6.3)
- **Target Component:** `src/frontend/src/components/GraphCanvas.tsx`

---

## 1. Architectural Question

How must `frameActiveSubgraph` and its triggering `useEffect` in `src/frontend/src/components/GraphCanvas.tsx` be ordered and coordinated with D3 force simulation initialization and D3 zoom transitions so that camera framing, intermediate animation frames, static stabilization, rapid successive queries, and de-illumination execute in unified synchronization?

---

## 2. Root Cause Analysis (Verified Against Source)

In `src/frontend/src/components/GraphCanvas.tsx`:
1. **`frameActiveSubgraph` Effect Runs Before Simulation Initializes Node Coordinates (`lines 77–81` vs `lines 319–355`):**
   - `useEffect` for `frameActiveSubgraph` (lines 77–81) is declared *above* the `d3.forceSimulation(nodes)` `useEffect` (lines 319–355).
   - When `nodes` are loaded or reloaded from `/api/graph/topology`, `App.tsx` creates `GraphNode` objects with `x: undefined, y: undefined`. Because the framing effect runs before `d3.forceSimulation(nodes)` assigns initial `x` and `y` positions, `nodes.filter((n) => targetPKs.has(n.primary_key) && n.x !== undefined && n.y !== undefined)` returns an empty array `[]` and aborts camera framing.
2. **No Transition Interruption on Rapid Successive Queries or De-Illumination (`lines 70–73`):**
   - `selection.transition().duration(350)...` is called without first calling `selection.interrupt()`, allowing overlapping transitions when queries arrive in rapid succession or when illumination is cleared mid-transition.
   - No `.on('end', ...)` stabilization callback is attached to guarantee a final crisp render frame when the 350ms interpolation completes.

---

## 3. Locked Architectural Decision

1. **Pre-Tick Initial Simulation Coordinates & Effect Ordering:**
   - In the `d3.forceSimulation` `useEffect` (`lines 319–355`), immediately run `simulation.tick(1)` when any node lacks `x` or `y` coordinates and call `renderRef.current()` so initial coordinates and link object references are synchronously established on mount and topology reload.
   - Place the camera framing `useEffect` *after* the `d3.forceSimulation` and `d3.zoom` initialization `useEffect` hooks so `zoomBehaviorRef.current` and node `(x, y)` coordinates are always initialized prior to `frameActiveSubgraph`.
2. **Unified Illumination Repaint + Interrupted D3 Transition + Static Stabilization:**
   - Inside `frameActiveSubgraph(targetPKs)`:
     - Immediately call `renderRef.current()` at `t = 0ms` so active nodes and edges are visibly illuminated before the first transition tick.
     - Compute the bounding box across `matchedNodes` using fallback logical dimensions `const width = (canvas.width / dpr) || canvas.clientWidth || 900;` and `const height = (canvas.height / dpr) || canvas.clientHeight || 650;`.
     - Call `selection.interrupt()` before starting `.transition().duration(350).ease(d3.easeCubicInOut).call(zoomBehaviorRef.current.transform, targetTransform).on('end', () => { renderRef.current(); })`.
     - Because `zoomBehaviorRef.current` delegates every `'zoom'` tick to `renderRef.current()`, every intermediate frame over the 350ms transition renders the active path in full gold/amber illumination, and `.on('end')` guarantees final frame stabilization.
3. **Immediate Transition Interruption and Repaint on De-Illumination:**
   - In the framing `useEffect`, when `!isIlluminated || activeNodePKs.size === 0`, call `d3.select(canvas).interrupt()` (if `canvasRef.current` exists) and immediately invoke `renderRef.current()` to repaint the canvas to its baseline blueprint state.

---

## 4. Verification Criteria

- Submitting a query or clicking "INQUIRE IN GRAPHRAG CHAT" immediately illuminates the subgraph at `t = 0ms`, smoothly interpolates the camera over 350ms with every intermediate frame illuminated, and stabilizes on the final frame.
- Rapid successive queries cleanly interrupt any in-flight camera transition and immediately frame and illuminate the newest subgraph.
- Clearing illumination immediately interrupts any active transition and repaints the canvas to baseline styling.
