# Ticket 004: Deterministic State Synchronization, Empty Subgraph Guard, Rapid Query Sequencing, and Responsive De-Illumination

- **Status:** Resolved
- **Claimed by:** `wayfinder-read-and-plan`
- **Blocked by:** `ticket-001.md`
- **Target Specification:** `functional_specification_009.md` (Sections 4.1.1, 4.3.1, 4.3.2, 5.1, 5.3, 6.1, 6.2)
- **Target Components:**
  - `src/frontend/src/context/GraphSyncContext.tsx`
  - `src/frontend/src/components/AgentChatDrawer.tsx`

---

## 1. Architectural Question

How must `GraphSyncContext.tsx` and `AgentChatDrawer.tsx` manage state transitions for `activeNodePKs`, `activeEdgeKeys`, and `isIlluminated` when handling rapid successive queries, empty subgraph responses (`0` active nodes), and user reset/close actions?

---

## 2. Root Cause Analysis (Verified Against Source)

1. **Empty Subgraph Response Leaves `isIlluminated = true` (`src/frontend/src/context/GraphSyncContext.tsx`, `lines 269–273`):**
   - `setIlluminatedPath` unconditionally sets `setIsIlluminated(true)` even when `response.active_node_pks` is empty (`length === 0`). When `isIlluminated` is `true` and `activeNodePKs` is empty, `GraphCanvas` attenuates all nodes and edges to `0.18` opacity instead of clearing illumination to baseline rendering as required by Section 5.3 (*"Empty Subgraph Response: If a query returns zero active nodes, the canvas must immediately clear any existing illumination and maintain baseline rendering"*).
2. **Rapid Successive Queries Blocked or Vulnerable to Out-of-Order Races (`src/frontend/src/context/GraphSyncContext.tsx`, `lines 340–399`):**
   - `submitInquiry` guards entry with `if (!q || isQueryLoading) return;`, silently dropping rapid successive queries triggered while a previous request is in flight (violating Section 5.1: *"If a user executes multiple queries in rapid succession, each arriving response must immediately overwrite the previous active path and instantly repaint the canvas with the newest active nodes"*).
   - Furthermore, if `clearIllumination()` is triggered while a query is in flight, the arriving response would overwrite the cleared state unless guarded by a request sequence counter.
3. **Closing Chat Inquiry Does Not Revert `isIlluminated` (`src/frontend/src/components/AgentChatDrawer.tsx`, `line 72`):**
   - Section 4.3.1 states: *"When the user clears the search, closes the chat inquiry, or triggers a reset action, `isIlluminated` reverts to false."*
   - Currently, the close button (`✕`) in `AgentChatDrawer.tsx` (`line 72`) only calls `setIsChatOpen(false)` without calling `clearIllumination()`.

---

## 3. Locked Architectural Decision

1. **Empty Subgraph Guard in `setIlluminatedPath` (`src/frontend/src/context/GraphSyncContext.tsx`):**
   - In `setIlluminatedPath(response: GraphRAGQueryResponse)`:
     - Extract `const nodePks = Array.isArray(response?.active_node_pks) ? response.active_node_pks : [];` and `const edgeKeys = Array.isArray(response?.active_edge_keys) ? response.active_edge_keys : [];`.
     - If `nodePks.length === 0`, immediately clear illumination (`setActiveNodePKs(new Set())`, `setActiveEdgeKeys(new Set())`, `setIsIlluminated(false)`).
     - Otherwise, commit `setActiveNodePKs(new Set(nodePks))`, `setActiveEdgeKeys(new Set(edgeKeys))`, and `setIsIlluminated(true)`.
2. **Monotonic Request Sequencing for Rapid Successive Queries (`src/frontend/src/context/GraphSyncContext.tsx`):**
   - Introduce `const latestQueryIdRef = useRef<number>(0);` in `GraphSyncProvider`.
   - Remove the blocking `isQueryLoading` early-return guard from `submitInquiry` (`if (!q) return;`).
   - Increment `const queryId = ++latestQueryIdRef.current;` on each `submitInquiry` invocation and only commit `setIlluminatedPath(data)` / error state / `setIsQueryLoading(false)` if `queryId === latestQueryIdRef.current`.
   - In `clearIllumination()`, also increment `latestQueryIdRef.current += 1` and set `setIsQueryLoading(false)` so an abandoned in-flight request cannot re-illuminate the canvas after a reset.
3. **De-Illumination on Chat Inquiry Close (`src/frontend/src/components/AgentChatDrawer.tsx`):**
   - Destructure `clearIllumination` from `useGraphSync()` in `AgentChatDrawer.tsx`.
   - Update the drawer close button (`✕`) `onClick` handler to invoke `clearIllumination()` alongside `setIsChatOpen(false)`, ensuring that closing the chat inquiry immediately reverts `isIlluminated` to `false` and repaints the canvas to baseline blueprint styling.

---

## 4. Verification Criteria

- Calling `setIlluminatedPath` with `active_node_pks: []` immediately resets `isIlluminated` to `false` and clears `activeNodePKs` and `activeEdgeKeys`.
- Firing multiple queries in rapid succession allows each query to execute and ensures the latest arriving response overwrites previous illumination state without race conditions.
- Clicking `✕ RESET PATH` in `FilterToolbar`, resetting jurisdiction/state filters, or closing the `AgentChatDrawer` immediately reverts `isIlluminated` to `false` and triggers an autonomous canvas repaint.
