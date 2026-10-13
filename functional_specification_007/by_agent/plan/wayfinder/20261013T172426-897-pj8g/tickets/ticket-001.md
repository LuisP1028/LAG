# Decision Ticket 001: Node Detail Action Trigger, Event Workflow, and In-Flight State Management

**Ticket ID:** `ticket-001.md`  
**Scope:** `NodeDetailDrawer.tsx` & `GraphSyncContext.tsx`  
**Status:** RESOLVED  
**Claimed By:** `wayfinder-read-and-plan`  
**Blocked By:** None (Root Decision)  
**Taxonomy Reference:** `LANGUAGE.md`

---

## 1. Architectural Question
How must the node detail drawer (`NodeDetailDrawer.tsx`) and synchronization context (`GraphSyncContext.tsx`) be modified to transform the "INQUIRE IN GRAPHRAG CHAT" button from a passive UI drawer toggle into an active, one-click intelligence trigger that prevents duplicate in-flight submissions while preserving node selection continuity?

---

## 2. Root Cause & Architectural Audit

1. **Passive Button Action:**
   - In `src/frontend/src/components/NodeDetailDrawer.tsx` (lines 244–265), clicking the "INQUIRE IN GRAPHRAG CHAT" button executes only `setIsChatOpen(true)`.
   - The selected node's `primary_key` and contextual attributes are completely discarded.
   - The chat drawer opens with a blank text input, stranding the user without initiating any retrieval or synthesis.

2. **In-Flight Concurrency & Double Submissions:**
   - There is currently no shared state tracking whether a GraphRAG query is actively being processed by the backend.
   - Repeated clicks on the button during a long-running LLM inference request dispatch multiple concurrent HTTP requests, wasting server resources and causing race conditions on canvas illumination.

3. **Selection Continuity:**
   - In `GraphSyncContext.tsx`, `selectedNode` must remain selected and visible in both the detail drawer and on the canvas while the GraphRAG query executes and when illumination renders.

---

## 3. Decision & Technical Specifications

### 3.1. Navigation & Trigger Workflow in `NodeDetailDrawer.tsx`
- **Symbol:** `NodeDetailDrawer`
- **Actions:**
  1. Consume `inquireNode` and `isQueryLoading` from `useGraphSync()`.
  2. Replace the passive `onClick={() => setIsChatOpen(true)}` with an active trigger:
     ```tsx
     onClick={() => inquireNode(selectedNode)}
     disabled={isQueryLoading}
     ```
  3. Update button styling and labels to reflect in-flight loading state:
     - When `isQueryLoading` is true:
       - Text: `◈ INQUIRING...`
       - Cursor: `not-allowed`
       - Opacity: `0.7`
       - Background: `rgba(255, 183, 3, 0.6)`
     - When `isQueryLoading` is false:
       - Text: `◈ INQUIRE IN GRAPHRAG CHAT`
       - Cursor: `pointer`
       - Opacity: `1.0`
       - Background: `CANVAS_PALETTE.accentAmber`

### 3.2. Synchronization Bus Interface in `GraphSyncContext.tsx`
- **Symbol:** `GraphSyncContextType`, `GraphSyncProvider`
- **Actions:**
  1. Add `isQueryLoading: boolean;` to `GraphSyncContextType`.
  2. Add `inquireNode: (node: GraphNode) => Promise<void>;` to `GraphSyncContextType`.
  3. Manage `isQueryLoading` state within `GraphSyncProvider` using `useState<boolean>(false)`.
  4. Implement `inquireNode`:
     - Ensures `selectedNode` remains bound.
     - Sets `isChatOpen(true)`.
     - Delegates query construction and dispatch to the central inquiry engine (Ticket 002 and Ticket 003).

---

## 4. Acceptance Criteria
1. Clicking "INQUIRE IN GRAPHRAG CHAT" on any node opens the chat drawer and immediately dispatches the contextual inquiry.
2. The button transitions to a disabled `◈ INQUIRING...` state immediately upon click, preventing duplicate submissions.
3. The selected node remains highlighted and active on the canvas and in the node detail drawer throughout execution.
4. Upon completion or failure of the query, the button returns to its active enabled state.
