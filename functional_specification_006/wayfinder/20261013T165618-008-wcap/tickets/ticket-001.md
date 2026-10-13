# Decision Ticket 001: Removal of Physics Toggle Button & Autonomous Force Simulation Stabilization

**Ticket ID:** `ticket-001.md`  
**Scope:** Navigation Toolbar & Simulation Controls  
**Status:** RESOLVED  
**Claimed By:** `wayfinder-read-and-plan`  
**Blocked By:** None (Root Decision)  
**Taxonomy Reference:** `LANGUAGE.md`

---

## 1. Architectural Question
How must the visualizer navigation toolbar (`FilterToolbar.tsx`) and application state (`GraphSyncContext.tsx`) be modified to completely eliminate the redundant "Freeze Physics" / "Unfreeze" button while ensuring the canvas force simulation naturally stabilizes into an autonomous equilibrium upon loading?

---

## 2. Root Cause & Architectural Audit

1. **Toolbar Visual Clutter:**
   - In `src/frontend/src/components/FilterToolbar.tsx` (lines 107–122), a button bound to `togglePhysicsFrozen` renders either `▶ RESUME PHYSICS` or `⏸ FREEZE PHYSICS`.
   - On smaller viewports, this button consumes critical horizontal space, crowding the `JURISDICTION`, `POLICY`, `RESET PATH`, and `GRAPHRAG CHAT` controls.
   - The user specification mandates complete removal of this button.

2. **Simulation Lifecycle & Auto-Stabilization:**
   - In `src/frontend/src/components/GraphCanvas.tsx` (lines 350–359), a dedicated `useEffect` monitored `physicsFrozen`, imperatively executing `simulation.stop()` or `simulation.restart()`.
   - In D3 force simulations, an autonomous simulation naturally decays its energy via `alphaDecay` until `alpha < alphaMin` (default $0.001$), at which point the simulation loop halts automatically without consuming CPU cycles.
   - With `alphaDecay(0.028)` and an initial restart alpha upon new topology loading, nodes settle into stable coordinates in approximately 120–150 ticks (~2.0 seconds). Manual pause/resume controls are completely redundant.

---

## 3. Decision & Technical Specifications

### 3.1. Navigation Toolbar Modifications (`FilterToolbar.tsx`)
- **Symbol:** `FilterToolbar`
- **Actions:**
  1. Remove lines 107–122 rendering the `<button onClick={togglePhysicsFrozen}>` element.
  2. Remove `physicsFrozen` and `togglePhysicsFrozen` destructuring from `useGraphSync()` at line 23–24.
  3. Retain all other toolbar controls:
     - Jurisdiction Selector (`<select value={filterState} ...>`)
     - Policy Selector (`<select value={policyKeyword} ...>`)
     - Clear Path Button (`{isIlluminated && <button onClick={clearIllumination}> ... }`)
     - Chat Trigger Button (`<button onClick={() => setIsChatOpen(!isChatOpen)}> ... ◈ GRAPHRAG CHAT</button>`)

### 3.2. Synchronization Bus Cleanup (`GraphSyncContext.tsx`)
- **Symbol:** `GraphSyncContextType`, `GraphSyncProvider`
- **Actions:**
  1. Remove `physicsFrozen: boolean;` and `togglePhysicsFrozen: () => void;` from `GraphSyncContextType`.
  2. Remove `const [physicsFrozen, setPhysicsFrozen] = useState<boolean>(false);` and `togglePhysicsFrozen` callback from `GraphSyncProvider`.
  3. Remove `physicsFrozen` and `togglePhysicsFrozen` from the provider value object and `useMemo` dependency array.

### 3.3. Force Simulation Autonomous Stabilization (`GraphCanvas.tsx`)
- **Symbol:** `GraphCanvas`
- **Actions:**
  1. Remove `physicsFrozen` from `useGraphSync()` destructuring (line 29).
  2. Remove the `useEffect` at lines 351–359 that observed `physicsFrozen`.
  3. Configure the force simulation to settle autonomously:
     - `alpha(1)` upon receiving a new set of nodes.
     - `alphaDecay(0.028)` ensuring smooth, predictable convergence to `alphaMin(0.001)`.
     - `velocityDecay(0.4)` to damp oscillations and avoid jitter.

---

## 4. Acceptance Criteria
1. The top navigation toolbar renders exclusively the Jurisdiction dropdown, Policy dropdown, Reset Path button (when illuminated), and GraphRAG Chat trigger.
2. The "Freeze Physics" / "Unfreeze" button is completely absent from the DOM.
3. Upon graph loading or policy/state filter reload, nodes spread out smoothly and settle into stationary positions within 3 seconds.
4. No TypeScript compilation or runtime reference errors occur for removed `physicsFrozen` symbols.
