# Decision Ticket 002: Collapsible Blueprint HUD Accordion Component Architecture & State Management

**Ticket ID:** `ticket-002.md`  
**Scope:** Frontend Visualizer Telemetry HUD  
**Status:** RESOLVED  
**Claimed By:** `wayfinder-read-and-plan`  
**Blocked By:** None (Independent UI Component Decision)  
**Taxonomy Reference:** `LANGUAGE.md`

---

## 1. Architectural Question
How must the fixed "LAG KNOWLEDGE BLUEPRINT HUD" overlay in `GraphCanvas.tsx` be refactored into a collapsible accordion panel that eliminates visual collision and overlap with the navigation toolbar dropdowns while providing seamless inspection of graph metrics?

---

## 2. Root Cause & Architectural Audit

1. **Fixed Overlay with Zero Interactivity:**
   - In `src/frontend/src/components/GraphCanvas.tsx` (lines 469–497), the HUD overlay is rendered with `pointerEvents: 'none'` and static dimensions (`top: 14, left: 14`).
   - The HUD currently displays the title and four inline metrics (`NODES`, `EDGES`, `FPS`, `STATUS`).
   - On screen widths under 1280px or when multiple toolbars/dropdowns are open, the horizontal width of the expanded HUD collides with the left side of the right-aligned `FilterToolbar`.

2. **Accordion Requirement:**
   - The specification mandates an accordion UI with two distinct states:
     - **Collapsed State:** A compact, low-profile badge displaying `◈ BLUEPRINT HUD [▼]` occupying minimal screen real estate.
     - **Expanded State:** The full telemetry panel showing total nodes, total edges, current FPS counter, and illumination status (`PATH ILLUMINATED` vs `EXPLORATION MODE`), with a collapse indicator `[▲]`.
   - The container must enable `pointerEvents: 'auto'` to receive mouse clicks, while ensuring clicks on the HUD do not bleed through to the canvas underneath (`e.stopPropagation()`).

---

## 3. Decision & Technical Specifications

### 3.1. Local State & Interaction Management (`GraphCanvas.tsx`)
- Introduce local React state inside `GraphCanvas`:
  ```tsx
  const [isHudOpen, setIsHudOpen] = useState<boolean>(true);
  ```
- Toggle function:
  ```tsx
  const toggleHud = (e: React.MouseEvent) => {
    e.stopPropagation();
    setIsHudOpen((prev) => !prev);
  };
  ```

### 3.2. Structural Layout & CSS Specifications
- **Container Positioning:**
  - `position: 'absolute'`
  - `top: 14px, left: 14px`
  - `zIndex: 10`
  - `backgroundColor: 'rgba(10, 17, 40, 0.90)'`
  - `backdropFilter: 'blur(8px)'`
  - `border: '1px solid rgba(255, 183, 3, 0.35)'`
  - `borderRadius: 6px`
  - `fontFamily: '"SF Mono", "Fira Code", monospace'`
  - `fontSize: 11px`
  - `color: '#e2e8f0'`
  - `boxShadow: '0 4px 16px rgba(0, 0, 0, 0.5)'`
  - `pointerEvents: 'auto'`
  - `cursor: 'pointer'`
  - `userSelect: 'none'`
  - `transition: 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)'`

- **Collapsed State Representation (`!isHudOpen`):**
  - Displays a single compact header line:
    ```tsx
    <div
      onClick={toggleHud}
      style={{
        padding: '6px 12px',
        display: 'flex',
        alignItems: 'center',
        gap: 8,
        color: CANVAS_PALETTE.accentAmber,
        fontWeight: 700,
        letterSpacing: '0.05em',
      }}
    >
      <span>◈ BLUEPRINT HUD</span>
      <span style={{ fontSize: 9, color: '#94a3b8' }}>▼</span>
    </div>
    ```

- **Expanded State Representation (`isHudOpen`):**
  - Displays the clickable accordion header:
    ```tsx
    <div
      onClick={toggleHud}
      style={{
        padding: '8px 14px 6px 14px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        borderBottom: '1px solid rgba(255, 183, 3, 0.2)',
        color: CANVAS_PALETTE.accentAmber,
        fontWeight: 700,
        letterSpacing: '0.05em',
      }}
    >
      <span>◈ LAG KNOWLEDGE BLUEPRINT HUD</span>
      <span style={{ fontSize: 9, color: '#94a3b8' }}>▲</span>
    </div>
    ```
  - Displays the telemetry details body:
    ```tsx
    <div style={{ padding: '8px 14px', display: 'flex', gap: 14 }}>
      <span>NODES: <strong style={{ color: '#38bdf8' }}>{nodes.length}</strong></span>
      <span>EDGES: <strong style={{ color: '#38bdf8' }}>{links.length}</strong></span>
      <span>FPS: <strong style={{ color: fps >= 55 ? '#4ade80' : '#f87171' }}>{fps}</strong></span>
      <span>STATUS: <strong style={{ color: isIlluminated ? CANVAS_PALETTE.accentAmber : '#94a3b8' }}>
        {isIlluminated ? 'PATH ILLUMINATED' : 'EXPLORATION MODE'}
      </strong></span>
    </div>
    ```

### 3.3. Zero Collision Guarantee
- When collapsed, the HUD bounding box is $<180\text{px}$ wide and $28\text{px}$ high, positioned at `top: 14, left: 14`.
- The `FilterToolbar` is anchored at `top: 14, right: 14`.
- Across all viewports down to 1024px width, horizontal clearance between the collapsed HUD and the toolbar exceeds 400px, eliminating any visual collision or overlap.

---

## 4. Acceptance Criteria
1. The HUD renders with interactive pointer styling and responds immediately to clicks.
2. Clicking the header toggles smoothly between Collapsed State and Expanded State.
3. In Collapsed State, only the compact badge `◈ BLUEPRINT HUD [▼]` is visible.
4. In Expanded State, all four live metrics (`NODES`, `EDGES`, `FPS`, `STATUS`) render accurately with `[▲]` collapse toggle.
5. Zero visual overlap occurs with top-right toolbar dropdowns or chat triggers.
