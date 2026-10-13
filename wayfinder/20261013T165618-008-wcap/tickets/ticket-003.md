# Decision Ticket 003: Canvas Node Hover Interaction Stability & Reactive Dependency Isolation

**Ticket ID:** `ticket-003.md`  
**Scope:** Canvas Event Bus & Force Simulation Lifecycle  
**Status:** RESOLVED  
**Claimed By:** `wayfinder-read-and-plan`  
**Blocked By:** `ticket-001.md`  
**Taxonomy Reference:** `LANGUAGE.md`

---

## 1. Architectural Question
What is the root cause of cursor repulsion and node displacement when hovering or clicking nodes in `GraphCanvas.tsx`, and how must the simulation lifecycle be restructured so nodes remain completely stationary during cursor hover and single-click selection?

---

## 2. Root Cause Analysis & Empirical Discovery

1. **Reactive Dependency Pollution in Simulation Hook:**
   - In `src/frontend/src/components/GraphCanvas.tsx`:
     ```tsx
     // Line 82-310:
     const render = useCallback(() => { ... }, [
       nodes, links, isIlluminated, activeNodePKs, activeEdgeKeys, selectedNode, hoveredNode
     ]);

     // Line 313-348:
     useEffect(() => {
       if (!nodes.length) return;
       const simulation = d3.forceSimulation<GraphNode>(nodes)...
       simulation.on('tick', () => { render(); });
       simulationRef.current = simulation;
       return () => { simulation.stop(); };
     }, [nodes, links, render]); // <--- CRITICAL ROOT CAUSE
     ```
   - Whenever the user hovers over a node:
     1. `handlePointerMove` detects the node under the cursor.
     2. `setHoveredNode(hovered)` is invoked.
     3. State change triggers a re-render of `GraphCanvas`.
     4. Because `render` lists `hoveredNode` in its dependency array, `render` is assigned a new function identity.
     5. Because the simulation `useEffect` lists `render` as a dependency, the effect teardown triggers (`simulation.stop()`).
     6. A brand-new `d3.forceSimulation(nodes)` is instantiated from scratch with default `alpha(1.0)`.
     7. Strong repulsive electrostatic forces (`forceManyBody().strength(-120)`) and collision forces (`forceCollide`) instantly fire, violently pushing the hovered node and its neighbors away from the cursor.
     8. When the cursor moves away, `setHoveredNode(null)` fires, restarting the simulation yet again.
     9. When a user clicks a node, `selectNode` updates `selectedNode`, changing `render` again, restarting the simulation a third time!

2. **Architectural Root-Cause Resolution:**
   - The D3 simulation lifecycle must depend **strictly and exclusively** on actual dataset changes (`nodes` and `links`), NOT on transient UI states (`hoveredNode`, `selectedNode`, `isIlluminated`, `activeNodePKs`, `activeEdgeKeys`).
   - The simulation tick callback must delegate to a mutable reference (`renderRef.current`), keeping the simulation lifecycle independent of render callback identity.
   - Hover and selection state changes will trigger canvas redraws via `renderRef.current()` without perturbing simulation alpha or resetting node velocities (`vx`, `vy`).

---

## 3. Decision & Technical Specifications

### 3.1. Stable Mutable Render Reference Pattern
1. Create a persistent render callback reference:
   ```tsx
   const renderRef = useRef<() => void>(() => {});
   ```
2. Keep `renderRef.current` synchronized with the latest render callback:
   ```tsx
   useEffect(() => {
     renderRef.current = render;
   }, [render]);
   ```
3. Alternatively, invoke `renderRef.current()` directly inside the simulation tick handler:
   ```tsx
   simulation.on('tick', () => {
     renderRef.current();
   });
   ```

### 3.2. Simulation Lifecycle Effect Isolation
- Remove `render` from the dependency array of the simulation `useEffect`:
  ```tsx
  useEffect(() => {
    if (!nodes.length) return;

    const canvas = canvasRef.current;
    if (!canvas) return;
    const width = canvas.clientWidth || 900;
    const height = canvas.clientHeight || 650;

    const simulation = d3
      .forceSimulation<GraphNode>(nodes)
      .force(
        'link',
        d3
          .forceLink<GraphNode, d3.SimulationLinkDatum<GraphNode>>(links as any)
          .id((d) => d.primary_key)
          .distance(45)
      )
      .force('charge', d3.forceManyBody().strength(-120))
      .force(
        'collision',
        d3.forceCollide<GraphNode>().radius((d) => (d.radius || 10) + 6)
      )
      .force('center', d3.forceCenter(width / 2, height / 2).strength(0.08))
      .alphaDecay(0.028)
      .velocityDecay(0.4);

    simulation.on('tick', () => {
      renderRef.current();
    });

    simulationRef.current = simulation;

    return () => {
      simulation.stop();
    };
  }, [nodes, links]); // STRICTLY [nodes, links] ONLY
  ```

### 3.3. Stationary Hover & Selection Interaction Handling
- In `handlePointerMove`:
  ```tsx
  if (hovered !== hoveredNode) {
    setHoveredNode(hovered);
    canvas.style.cursor = hovered ? 'pointer' : 'crosshair';
  }
  ```
- Because `hoveredNode` is part of `render`'s dependencies, the React re-render will update `renderRef.current` and trigger a single canvas redraw (`render()`) that draws the hover halo/border ring.
- Crucially, the simulation remains at rest: `simulation.alpha()` is neither touched nor restarted.
- When `handlePointerDown` selects a node via `selectNode(clicked)`, `selectedNode` updates and repaints without restarting the simulation. Nodes remain completely stationary under the cursor.

---

## 4. Acceptance Criteria
1. Hovering the cursor over any node on the visualizer canvas induces **zero positional displacement** of the hovered node or any neighbor node.
2. The canvas cursor switches to `pointer` when directly over a node's hit radius and reverts to `crosshair` when over background void.
3. Clicking a node selects it immediately on the first click without the node evading the cursor.
4. The D3 force simulation runs only when new data is received (`nodes`, `links`), settling into a resting state (`alpha < alphaMin`) and remaining stationary thereafter.
