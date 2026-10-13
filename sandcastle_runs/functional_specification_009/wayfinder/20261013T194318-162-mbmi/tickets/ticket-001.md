# Ticket 001: Decouple D3 Zoom Lifecycle from Render Callback and Enforce Synchronous Reactive Canvas Repaint

- **Status:** Resolved
- **Claimed by:** `wayfinder-read-and-plan`
- **Blocked by:** None
- **Target Specification:** `functional_specification_009.md` (Sections 4.1, 5.2, 5.4, 6.1, 6.5)
- **Target Component:** `src/frontend/src/components/GraphCanvas.tsx`

---

## 1. Architectural Question

Why does the HTML5 canvas in `src/frontend/src/components/GraphCanvas.tsx` remain dormant after `activeNodePKs`, `activeEdgeKeys`, and `isIlluminated` update in `GraphSyncContext`, only illuminating after manual user mouse interaction (panning, dragging, or zooming), and how must the D3 zoom and canvas render lifecycles be architected to guarantee immediate, zero-gesture repainting?

---

## 2. Root Cause Analysis (Verified Against Source)

In `src/frontend/src/components/GraphCanvas.tsx`:
1. **`d3.zoom` Bound to Stale `render` Closure (`lines 358–380`):**
   - The `useEffect` initializing `d3.zoom` declares `[render]` as its dependency and binds `.on('zoom', (event) => { transformRef.current = event.transform; render(); })` directly to the `render` closure from that render pass.
2. **Effect Declaration Order Race (`lines 77–81` vs `lines 314–316` & `lines 358–380`):**
   - The camera framing `useEffect` at lines 77–81 (`frameActiveSubgraph(activeNodePKs)`) is declared *before* `useEffect(() => { renderRef.current = render; }, [render])` (lines 314–316) and *before* the `d3.zoom` `useEffect` (lines 358–380).
   - When `setIlluminatedPath` commits `isIlluminated = true` and `activeNodePKs`, React runs the effect at lines 77–81 first. At that moment, `zoomBehaviorRef.current` still points to the *previous* `d3.zoom` instance whose `'zoom'` event handler closes over the *previous* `render` function (`isIlluminated = false`, `activeNodePKs = Set(0)`).
   - Calling `selection.transition().duration(350).ease(d3.easeCubicInOut).call(zoomBehaviorRef.current.transform, targetTransform)` schedules a 350ms D3 transition on the old `d3.zoom` dispatcher.
   - Although line 379 runs the new `render()` synchronously at `t = 0ms`, every subsequent animation frame from `t = 16ms` to `t = 350ms` invokes the old `d3.zoom` listener, overwriting the canvas with the stale unilluminated `render()` closure. Once the transition ends at `t = 350ms` and the force simulation has settled (`alpha < alphaMin`), the canvas remains stuck displaying the unilluminated state until a manual DOM mouse/wheel gesture triggers the new `d3.zoom` instance.
3. **Destructive Buffer Reset on Every State Change (`lines 374–377`):**
   - Because `[render]` updates whenever `hoveredNode`, `selectedNode`, `isIlluminated`, `activeNodePKs`, or `activeEdgeKeys` changes, lines 374–377 repeatedly overwrite `canvas.width` and `canvas.height` and re-bind `d3.select(canvas).call(zoom)` on every state transition.

---

## 3. Locked Architectural Decision

1. **Synchronous `renderRef` Assignment:**
   - Assign `renderRef.current = render;` synchronously in the component body of `GraphCanvas` (in addition to `useEffect`) so `renderRef.current` always references the latest `render` callback with current `isIlluminated`, `activeNodePKs`, `activeEdgeKeys`, `selectedNode`, and `hoveredNode` before any effect or D3 listener executes.
2. **Mount-Only `d3.zoom` Initialization Delegating to `renderRef.current()`:**
   - Initialize `d3.zoom<HTMLCanvasElement, unknown>()` once on mount (`useEffect(..., [])`).
   - Inside `.on('zoom', (event) => { transformRef.current = event.transform; renderRef.current(); })`, always invoke `renderRef.current()` instead of a captured `render` closure.
   - Store the stable instance in `zoomBehaviorRef.current` and attach it once via `d3.select(canvas).call(zoom)`.
3. **Dedicated Reactive Redraw Effect (Settled Simulation Support):**
   - Add an explicit reactive redraw `useEffect` dependent on `[render, isIlluminated, activeNodePKs, activeEdgeKeys, selectedNode, hoveredNode]` that immediately invokes `render()` synchronously and schedules a `requestAnimationFrame(() => renderRef.current())` with cleanup via `cancelAnimationFrame`. This guarantees immediate repainting even when the force simulation has settled (`alpha < alphaMin`).
4. **Non-Destructive Canvas Buffer Sizing & Resize Synchronization:**
   - Inside `render()`, check `canvas.getBoundingClientRect()` and `window.devicePixelRatio || 1`; only mutate `canvas.width` or `canvas.height` when the target pixel dimensions are positive and differ from the current buffer dimensions (`canvas.width !== targetWidth || canvas.height !== targetHeight`).
   - Attach both a `window` `'resize'` listener and a `ResizeObserver` on the canvas element that update buffer dimensions when changed and immediately call `renderRef.current()`.

---

## 4. Verification Criteria

- Updating `activeNodePKs`, `activeEdgeKeys`, or `isIlluminated` triggers an immediate synchronous `render()` call and `requestAnimationFrame` repaint without any mouse or keyboard events.
- `d3.zoom` is initialized once per canvas mount and always invokes `renderRef.current()` during both user gestures and programmatic transitions.
- Resizing the viewport during or after query delivery preserves canvas illumination without clearing state.
