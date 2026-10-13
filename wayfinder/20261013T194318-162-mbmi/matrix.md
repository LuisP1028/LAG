# Master Component-to-Edit Matrix (`20261013T194318-162-mbmi`)

**Authoritative Specification:** `functional_specification_009.md`  
**Wayfinder Map:** `wayfinder/20261013T194318-162-mbmi/map.md`

---

## 1. Summary Matrix of Targeted Files and Symbols

| File Path | Line Range | Target Symbol / Block | Linked Tickets | Required Transformation Summary |
| :--- | :--- | :--- | :--- | :--- |
| `src/frontend/src/components/GraphCanvas.tsx` | `31–82` | `renderRef`, `frameActiveSubgraph` | `ticket-001.md`, `ticket-003.md` | Keep `renderRef.current = render` synchronized on every render; update `frameActiveSubgraph` to invoke `renderRef.current()` immediately at `t = 0ms`, call `selection.interrupt()` before starting the 350ms `d3.easeCubicInOut` transition, and attach `.on('end', () => renderRef.current())` for static stabilization. |
| `src/frontend/src/components/GraphCanvas.tsx` | `83–316` | `render` callback (`useCallback`) | `ticket-001.md`, `ticket-002.md` | Non-destructively sync `canvas.width`/`canvas.height` with `devicePixelRatio`; gate `isActive` and `isActiveEdge` on `isIlluminated`; resolve link endpoints via a `nodeByPk` lookup; render active nodes in gold/amber (`#ffb703`) with `rgba(255, 183, 3, 0.45)` radial glow halos and `#f59e0b` inner halo ring; preserve `selectedNode` outer selection ring and `hoveredNode` full opacity (`alpha = 1.0`). |
| `src/frontend/src/components/GraphCanvas.tsx` | `318–396` | `useEffect` hooks (simulation, zoom, resize, reactive redraw, camera framing) | `ticket-001.md`, `ticket-003.md` | Pre-tick simulation (`simulation.tick(1)`) when initial node `(x, y)` coordinates are undefined and invoke `renderRef.current()`; initialize `d3.zoom` once on mount (`[]`) delegating `'zoom'` events to `renderRef.current()`; attach `window` `'resize'` and `ResizeObserver` handlers calling `renderRef.current()`; add reactive redraw `useEffect` (`[render, isIlluminated, activeNodePKs, activeEdgeKeys, selectedNode, hoveredNode]`); place camera framing `useEffect` after simulation/zoom initialization and interrupt transitions + repaint when `isIlluminated` reverts to `false`. |
| `src/frontend/src/components/GraphCanvas.tsx` | `398–546` | `handlePointerDown`, `handlePointerMove`, JSX overlay | `ticket-002.md` | Guard `handlePointerDown` with `if (e.defaultPrevented) return;`; use active scale-aware hit radius in `handlePointerDown` and `handlePointerMove`; render a non-blocking (`pointerEvents: 'none'`) floating hover inspection tooltip when `hoveredNode` is non-null. |
| `src/frontend/src/context/GraphSyncContext.tsx` | `175–280`, `340–399` | `GraphSyncProvider`, `setIlluminatedPath`, `clearIllumination`, `submitInquiry` | `ticket-004.md` | Guard `setIlluminatedPath` so empty `active_node_pks` (`length === 0`) immediately resets `activeNodePKs`, `activeEdgeKeys`, and `isIlluminated = false`; add `latestQueryIdRef = useRef<number>(0)` in `GraphSyncProvider` to allow rapid successive `submitInquiry` calls to execute without being dropped by `isQueryLoading` and to prevent stale in-flight responses from overwriting newer queries or `clearIllumination()`. |
| `src/frontend/src/components/AgentChatDrawer.tsx` | `9–23`, `71–82` | `AgentChatDrawer` close button (`✕`) | `ticket-004.md` | Destructure `clearIllumination` from `useGraphSync()` and invoke `clearIllumination()` when closing the chat drawer (`onClick={() => { clearIllumination(); setIsChatOpen(false); }}`) so closing the chat inquiry immediately reverts `isIlluminated` to `false` and repaints the canvas. |

---

## 2. Detailed Component-by-Component Specifications

### 2.1. `src/frontend/src/components/GraphCanvas.tsx`

#### A. `frameActiveSubgraph` (`lines 39–75`)
- Ensure `frameActiveSubgraph` immediately executes `renderRef.current()` at entry so active amber highlights are painted on the canvas at `t = 0ms` prior to the first transition tick.
- Compute logical viewport dimensions safely using:
  - `const dpr = window.devicePixelRatio || 1;`
  - `const rect = canvas.getBoundingClientRect();`
  - `const width = (canvas.width / dpr) || rect.width || canvas.clientWidth || 900;`
  - `const height = (canvas.height / dpr) || rect.height || canvas.clientHeight || 650;`
- Before starting the D3 zoom transition on `const selection = d3.select(canvas);`, call `selection.interrupt()` to cancel any in-flight camera transition from a prior query.
- Execute:
  ```ts
  if (zoomBehaviorRef.current) {
    selection
      .interrupt()
      .transition()
      .duration(350)
      .ease(d3.easeCubicInOut)
      .call(zoomBehaviorRef.current.transform, targetTransform)
      .on('end', () => {
        renderRef.current();
      });
  }
  ```

#### B. `render` Callback (`lines 84–316`)
1. **Non-Destructive Buffer Dimension Check:**
   - At the start of `render()`, compute `const dpr = window.devicePixelRatio || 1;` and `const rect = canvas.getBoundingClientRect();`.
   - If `rect.width > 0 && rect.height > 0`, compute `const targetW = Math.round(rect.width * dpr);` and `const targetH = Math.round(rect.height * dpr);`. If `canvas.width !== targetW || canvas.height !== targetH`, update `canvas.width = targetW; canvas.height = targetH;`.
2. **Lookup Map & Strict `isIlluminated` Gating:**
   - Build `const nodeByPk = new Map<string, GraphNode>(nodes.map((n) => [n.primary_key, n]));`.
   - In Step 2 (Orbital Blueprint Linework, `line 137`):
     `const isActive = isIlluminated && activeNodePKs.has(node.primary_key);`
   - In Step 3 (Links / Laser Struts, `lines 149–203`):
     - Resolve endpoints whether `link.source` / `link.target` is a `GraphNode` object or a `string` PK:
       ```ts
       const source = typeof link.source === 'object' ? (link.source as GraphNode) : nodeByPk.get(link.source as string);
       const target = typeof link.target === 'object' ? (link.target as GraphNode) : nodeByPk.get(link.target as string);
       if (!source || !target || source.x === undefined || source.y === undefined || target.x === undefined || target.y === undefined) return;
       ```
     - Gate `isActiveEdge` strictly on `isIlluminated`:
       ```ts
       const isActiveEdge =
         isIlluminated &&
         (activeEdgeKeys.has(link.edge_key) ||
           (activeNodePKs.has(source.primary_key) && activeNodePKs.has(target.primary_key)));
       ```
3. **Active Node Amber Fill (`#ffb703`), Radial Glow Halo (`rgba(255, 183, 3, 0.45)`), and Selected Node Ring (`lines 206–309`):**
   - Compute `const isActive = isIlluminated && activeNodePKs.has(node.primary_key);`.
   - Preserve full opacity (`alpha = 1.0`) for active, selected, and hovered nodes:
     ```ts
     let alpha = 1.0;
     if (isIlluminated && !isActive && !isSelected && !isHovered) {
       alpha = CANVAS_PALETTE.inactiveAttenuation;
     }
     ```
   - When `isActive` is `true`, render the active radial glow halo (`rgba(255, 183, 3, 0.45)`) and active halo ring (`CANVAS_PALETTE.activeHalo`):
     ```ts
     if (isActive) {
       ctx.save();
       ctx.fillStyle = 'rgba(255, 183, 3, 0.45)';
       ctx.beginPath();
       ctx.arc(node.x, node.y, radius + 7 / transform.k, 0, Math.PI * 2);
       ctx.fill();
       ctx.strokeStyle = CANVAS_PALETTE.activeHalo;
       ctx.lineWidth = 3.0 / transform.k;
       ctx.beginPath();
       ctx.arc(node.x, node.y, radius + 3.5 / transform.k, 0, Math.PI * 2);
       ctx.stroke();
       ctx.restore();
     }
     ```
   - When `isSelected` is `true`, render a distinctive selection ring and pulse indicator that persists uninterrupted both during and after path illumination:
     ```ts
     if (isSelected) {
       ctx.save();
       ctx.strokeStyle = '#38bdf8';
       ctx.lineWidth = 2.5 / transform.k;
       ctx.setLineDash([4 / transform.k, 3 / transform.k]);
       ctx.beginPath();
       ctx.arc(node.x, node.y, radius + 9 / transform.k, 0, Math.PI * 2);
       ctx.stroke();
       ctx.restore();
     }
     ```
   - Render the base node fill in gold/amber (`#ffb703` / `CANVAS_PALETTE.accentAmber`) when `isActive` is `true`, and `visual.badgeColor` otherwise:
     ```ts
     ctx.beginPath();
     ctx.arc(node.x, node.y, radius, 0, Math.PI * 2);
     ctx.fillStyle = isActive ? CANVAS_PALETTE.accentAmber : visual.badgeColor;
     ctx.fill();
     ```
   - Render node border ring:
     ```ts
     ctx.strokeStyle = isHovered ? '#ffffff' : isActive ? '#fde68a' : 'rgba(255, 255, 255, 0.35)';
     ctx.lineWidth = (isActive || isHovered ? 1.8 : 1.2) / transform.k;
     ctx.stroke();
     ```
   - In Step 5 (Node Captions & Leader Badges, `lines 279–306`), render active node captions with bold typography (`font = "${isActive ? '700 ' : ''}${Math.max(9, Math.min(12, 11 / transform.k))}px \"SF Mono\", \"Fira Code\", monospace"`), high-contrast leader badge background (`rgba(10, 17, 40, 0.92)`), subtle amber leader border when `isActive` (`ctx.strokeStyle = 'rgba(255, 183, 3, 0.45)'`), and `CANVAS_PALETTE.accentAmber` (`#ffb703`) text fill.
4. **Synchronous `renderRef` Binding:**
   - Assign `renderRef.current = render;` synchronously right after `const render = useCallback(...)` as well as in `useEffect(() => { renderRef.current = render; }, [render])`.

#### C. Simulation, Zoom, Resize, Reactive Redraw, and Camera Framing Effects (`lines 318–396`)
1. **D3 Force Simulation Effect (`[nodes, links]`):**
   - After constructing `const simulation = d3.forceSimulation<GraphNode>(nodes)...`, if any node has `x === undefined || y === undefined`, execute `simulation.tick(1);` synchronously so all nodes have initial coordinates and `d3.forceLink` has bound `source`/`target` references, then immediately call `renderRef.current();`.
2. **Mount-Only D3 Zoom Effect (`[]`):**
   - Initialize `d3.zoom<HTMLCanvasElement, unknown>()` once on mount (`useEffect(..., [])`):
     ```ts
     useEffect(() => {
       const canvas = canvasRef.current;
       if (!canvas) return;

       const zoom = d3
         .zoom<HTMLCanvasElement, unknown>()
         .scaleExtent([0.2, 5.0])
         .on('zoom', (event) => {
           transformRef.current = event.transform;
           renderRef.current();
         });

       zoomBehaviorRef.current = zoom;
       d3.select(canvas).call(zoom);

       const dpr = window.devicePixelRatio || 1;
       const rect = canvas.getBoundingClientRect();
       if (rect.width > 0 && rect.height > 0) {
         canvas.width = Math.round(rect.width * dpr);
         canvas.height = Math.round(rect.height * dpr);
       }

       renderRef.current();
     }, []);
     ```
3. **Resize Synchronization Effect (`[]`):**
   - Attach both `window.addEventListener('resize', handleResize)` and a `ResizeObserver` on `canvas` (when `typeof ResizeObserver !== 'undefined'`) that update `canvas.width` and `canvas.height` when dimensions change and invoke `renderRef.current()`.
4. **Reactive Redraw Effect (`[render, isIlluminated, activeNodePKs, activeEdgeKeys, selectedNode, hoveredNode]`):**
   - Immediately execute `render()` synchronously and schedule a `requestAnimationFrame(() => { renderRef.current(); })` with cleanup via `cancelAnimationFrame(rafId)`.
5. **Camera Framing Effect (`[isIlluminated, activeNodePKs, frameActiveSubgraph]`):**
   - Declared *after* the simulation and zoom initialization effects:
     ```ts
     useEffect(() => {
       if (isIlluminated && activeNodePKs.size > 0) {
         frameActiveSubgraph(activeNodePKs);
       } else {
         if (canvasRef.current) {
           d3.select(canvasRef.current).interrupt();
         }
         renderRef.current();
       }
     }, [isIlluminated, activeNodePKs, frameActiveSubgraph]);
     ```

#### D. Pointer Hit-Testing and Hover Tooltip (`lines 398–546`)
- In `handlePointerDown`, return early if `e.defaultPrevented` is `true`.
- In both `handlePointerDown` and `handlePointerMove`, compute the scale-aware node radius matching `render()`:
  ```ts
  const isActive = isIlluminated && activeNodePKs.has(node.primary_key);
  const baseRadius = node.radius || 10;
  const hitRadius = ((isActive ? baseRadius * 1.3 : baseRadius) / Math.max(0.7, Math.min(1.4, transform.k))) + 4 / transform.k;
  ```
- When `hoveredNode` is non-null, render a lightweight non-interactive (`pointerEvents: 'none'`) tooltip badge at the bottom-left of the canvas overlay showing `hoveredNode.label`, `hoveredNode.primary_key`, and `hoveredNode.name`.

---

### 2.2. `src/frontend/src/context/GraphSyncContext.tsx`

1. **Request Sequencing Ref (`line 183`):**
   - Add `useRef` to the React import (`import React, { createContext, useContext, useState, useCallback, useMemo, useRef } from 'react';`).
   - Inside `GraphSyncProvider`, declare `const latestQueryIdRef = useRef<number>(0);`.
2. **Empty Subgraph Guard in `setIlluminatedPath` (`lines 269–273`):**
   ```ts
   const setIlluminatedPath = useCallback((response: GraphRAGQueryResponse) => {
     const nodePks = Array.isArray(response?.active_node_pks) ? response.active_node_pks : [];
     const edgeKeys = Array.isArray(response?.active_edge_keys) ? response.active_edge_keys : [];
     if (nodePks.length === 0) {
       setActiveNodePKs(new Set());
       setActiveEdgeKeys(new Set());
       setIsIlluminated(false);
       return;
     }
     setActiveNodePKs(new Set(nodePks));
     setActiveEdgeKeys(new Set(edgeKeys));
     setIsIlluminated(true);
   }, []);
   ```
3. **Invalidate In-Flight Queries on `clearIllumination` (`lines 275–279`):**
   ```ts
   const clearIllumination = useCallback(() => {
     latestQueryIdRef.current += 1;
     setIsQueryLoading(false);
     setActiveNodePKs(new Set());
     setActiveEdgeKeys(new Set());
     setIsIlluminated(false);
   }, []);
   ```
4. **Rapid Successive Query Support in `submitInquiry` (`lines 340–399`):**
   - Replace `if (!q || isQueryLoading) return;` with `if (!q) return;`.
   - Increment `const queryId = ++latestQueryIdRef.current;` before starting `fetch('/api/graphrag/query', ...)`.
   - When `res` resolves or throws, check `if (queryId !== latestQueryIdRef.current) return;` before calling `setIlluminatedPath(data)` or setting `errorMsg`, and in `finally`, only call `setIsQueryLoading(false)` when `queryId === latestQueryIdRef.current`.

---

### 2.3. `src/frontend/src/components/AgentChatDrawer.tsx`

1. **De-Illuminate When Closing the Chat Inquiry (`lines 10–20`, `71–82`):**
   - Include `clearIllumination` in the destructured values from `useGraphSync()`.
   - Update the close button (`✕`) `onClick` handler (`line 72`) from `onClick={() => setIsChatOpen(false)}` to:
     ```tsx
     onClick={() => {
       clearIllumination();
       setIsChatOpen(false);
     }}
     ```
