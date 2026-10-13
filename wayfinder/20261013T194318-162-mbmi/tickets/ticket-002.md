# Ticket 002: Active Node Amber Fill, Radial Glow Halo, Directional Edge Illumination, and Selection/Hover Continuity

- **Status:** Resolved
- **Claimed by:** `wayfinder-read-and-plan`
- **Blocked by:** `ticket-001.md`
- **Target Specification:** `functional_specification_009.md` (Sections 4.1.3, 4.3.2, 4.4.1, 4.4.2, 6.1, 6.4)
- **Target Component:** `src/frontend/src/components/GraphCanvas.tsx`

---

## 1. Architectural Question

How must the canvas rendering loop in `src/frontend/src/components/GraphCanvas.tsx` draw active nodes, radial glow halos, active edges, leader badges, selected node rings, and hover inspections so that every visual element conforms to `functional_specification_009.md`?

---

## 2. Root Cause Analysis (Verified Against Source)

In `src/frontend/src/components/GraphCanvas.tsx`:
1. **Unconditional `activeNodePKs` / `activeEdgeKeys` Checks Without `isIlluminated` Gate (`lines 137, 154–155, 184, 209`):**
   - `const isActive = activeNodePKs.has(node.primary_key)` (lines 137, 209) and `const isActiveEdge = activeEdgeKeys.has(link.edge_key) || ...` (lines 154–155, 184) do not check `isIlluminated`. If `isIlluminated` is set to `false` before sets are cleared, active styling and directional arrows would still render.
2. **Missing Gold/Amber Base Node Fill and Radial Glow Halo (`lines 225–240`):**
   - Section 4.1.3 requires: *"All nodes whose primary keys belong to `activeNodePKs` must immediately render in gold/amber (`#ffb703`) with active radial glow halos (`rgba(255, 183, 3, 0.45)`)."*
   - Currently, line 239 sets `ctx.fillStyle = visual.badgeColor;` unconditionally (never `#ffb703` / `CANVAS_PALETTE.accentAmber` when `isActive`), and lines 226–234 only stroke a single ring with `CANVAS_PALETTE.activeHalo` (`#f59e0b`) without rendering the `rgba(255, 183, 3, 0.45)` radial glow halo.
3. **Selection Ring Collision and Hover Attenuation (`lines 214–234`):**
   - Line 214 attenuates `selectedNode` and `hoveredNode` to `alpha = 0.18` when `isIlluminated && !isActive`, making hovered captions and non-path selected nodes dim during illumination.
   - `isActive` and `isSelected` share the exact same halo stroke at lines 226–234 rather than preserving a distinctive selection ring and pulse effect for `selectedNode` (Section 4.4.1).
   - No floating hover tooltip is rendered for `hoveredNode` to support smooth node inspection during illumination (Section 4.4.2).

---

## 3. Locked Architectural Decision

1. **Strict `isIlluminated` Gating for Nodes and Edges:**
   - Compute `const isActive = isIlluminated && activeNodePKs.has(node.primary_key);` in both orbital linework (`line 137`) and node rendering (`line 209`).
   - In link rendering (`lines 149–203`), resolve `sourceNode` and `targetNode` safely (supporting both `GraphNode` object references and string primary keys via a `nodeMap` lookup so links render accurately even before `d3.forceLink` mutates link endpoints), and compute:
     `const isActiveEdge = isIlluminated && (activeEdgeKeys.has(link.edge_key) || (activeNodePKs.has(sourceNode.primary_key) && activeNodePKs.has(targetNode.primary_key)));`
2. **Gold/Amber Active Node Fill and Radial Glow Halo (`rgba(255, 183, 3, 0.45)`):**
   - When `isActive` is `true`:
     - Render an outer radial glow halo fill/stroke around the node using `rgba(255, 183, 3, 0.45)` at radius `radius + 7 / transform.k` and an inner halo ring using `CANVAS_PALETTE.activeHalo` (`#f59e0b`) with `lineWidth = 3.0 / transform.k` at `radius + 3.5 / transform.k`.
     - Render the base node fill in gold/amber: `ctx.fillStyle = isActive ? CANVAS_PALETTE.accentAmber : visual.badgeColor;` (`#ffb703`).
     - Render elevated leader badge contrast (`rgba(10, 17, 40, 0.92)` with subtle amber border `rgba(255, 183, 3, 0.45)`) and bold active typography in `CANVAS_PALETTE.accentAmber` (`#ffb703`).
3. **Preserved Selection Ring and Hover Inspection Continuity:**
   - Do not attenuate `isSelected` or `isHovered` nodes when `isIlluminated` is `true` (`if (isIlluminated && !isActive && !isSelected && !isHovered) { alpha = CANVAS_PALETTE.inactiveAttenuation; }`).
   - When `isSelected` is `true`, render a distinctive outer selection ring at `radius + 8.5 / transform.k` (dashed/pulsing cyan-white `#38bdf8` / `#ffffff` ring) so the selected node's highlight persists uninterrupted both during and after path illumination.
   - Update pointer hit-testing in `handlePointerDown` and `handlePointerMove` to account for the `1.3x` active node radius scaling and ignore drag-release clicks where `e.defaultPrevented` is `true`.
   - Render a lightweight, non-blocking (`pointerEvents: 'none'`) floating tooltip badge when `hoveredNode` is present, displaying the hovered node's `label`, `primary_key`, and `name`.

---

## 4. Verification Criteria

- Active nodes in `activeNodePKs` immediately render with `#ffb703` (`CANVAS_PALETTE.accentAmber`) fill and `rgba(255, 183, 3, 0.45)` radial glow halos.
- Active edges in `activeEdgeKeys` immediately render with `CANVAS_PALETTE.activeEdge` (`#fbbf24`), `3.5 / transform.k` thickness, and directional amber chevrons.
- Selected nodes retain a distinct outer selection ring during and after illumination, and hovered nodes display crisp captions and tooltip inspection without disrupting the illuminated path.
