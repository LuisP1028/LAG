# Decision Ticket 003: Bidirectional Chat Synchronization Bus and Conversation Thread State Management

**Ticket ID:** `ticket-003.md`  
**Scope:** `src/frontend/src/context/GraphSyncContext.tsx` & `src/frontend/src/components/AgentChatDrawer.tsx`  
**Status:** RESOLVED  
**Claimed By:** `wayfinder-read-and-plan`  
**Blocked By:** `ticket-001.md`, `ticket-002.md`  
**Taxonomy Reference:** `LANGUAGE.md`

---

## 1. Architectural Question
How must conversation state (`messages`, `isQueryLoading`, `errorMsg`), dispatch execution, and telemetry badges be centralized within `GraphSyncContext.tsx` and consumed by `AgentChatDrawer.tsx` to support continuous conversational turns across successive node inquiries while triggering real-time canvas illumination?

---

## 2. Root Cause & Architectural Audit

1. **State Isolation in `AgentChatDrawer.tsx`:**
   - In `AgentChatDrawer.tsx` (lines 32–39), `messages` state is isolated locally inside the drawer component.
   - Sibling components like `NodeDetailDrawer.tsx` cannot append messages or observe the in-flight loading state.
   - To execute an inquiry from `NodeDetailDrawer`, the chat history and dispatch logic must be accessible across the synchronization bus.

2. **Successive Inquiries as Separate Turns:**
   - Section 5.2 mandates: *"If a user clicks a different node and presses 'INQUIRE IN GRAPHRAG CHAT', the system must process the new inquiry as a distinct turn in the conversation thread without clearing prior messages."*
   - Centralizing the message thread ensures prior user prompts and assistant answers persist across successive node selections.

3. **Telemetry & Real-Time Illumination:**
   - Section 4.1 steps 6 & 7 mandate rendering the assistant's answer and telemetry badge (latency ms, illuminated nodes count) and triggering canvas illumination.

---

## 3. Decision & Technical Specifications

### 3.1. Unified State & Dispatch Engine in `GraphSyncContext.tsx`
- **Symbols:** `ChatMessage`, `GraphSyncContextType`, `GraphSyncProvider`
- **Actions:**
  1. Define `ChatMessage` interface:
     ```typescript
     export interface ChatMessage {
       id: string;
       sender: 'user' | 'assistant';
       text: string;
       responsePayload?: GraphRAGQueryResponse;
       timestamp: string;
     }
     ```
  2. Extend `GraphSyncContextType`:
     - `messages: ChatMessage[];`
     - `isQueryLoading: boolean;`
     - `errorMsg: string | null;`
     - `submitInquiry: (queryText: string, anchorPk?: string, modelId?: string) => Promise<void>;`
     - `inquireNode: (node: GraphNode) => Promise<void>;`
  3. Implement `submitInquiry`:
     - Creates user message: `{ id: 'user-${Date.now()}', sender: 'user', text: queryText, timestamp: ... }`.
     - Appends user message to `messages`.
     - Sets `isQueryLoading(true)` and `errorMsg(null)`.
     - Dispatches `fetch('/api/graphrag/query', { method: 'POST', body: JSON.stringify({ query: queryText, model_id, state_code: filterState || 'WI', primary_key: anchorPk }) })`.
     - Parses `GraphRAGQueryResponse`.
     - Invokes `setIlluminatedPath(data)` (illuminating active node PKs and active edge keys).
     - Appends assistant message: `{ id: 'asst-${Date.now()}', sender: 'assistant', text: data.answer, responsePayload: data, timestamp: ... }`.
     - In `catch(err)`: captures error message in `errorMsg` and appends formatted error message to `messages` as required by Section 5.3.
     - In `finally`: sets `isQueryLoading(false)`.
  4. Implement `inquireNode`:
     - Sets `isChatOpen(true)`.
     - Generates prompt text using `constructInquiryPrompt(node)`.
     - Dispatches `submitInquiry(promptText, node.primary_key)`.

### 3.2. Chat Drawer Refactoring (`AgentChatDrawer.tsx`)
- **Symbol:** `AgentChatDrawer`
- **Actions:**
  1. Remove local `messages`, `loading`, and `errorMsg` state definitions.
  2. Consume `messages`, `isQueryLoading`, `errorMsg`, and `submitInquiry` directly from `useGraphSync()`.
  3. Update manual text submission form to invoke `submitInquiry(inputQuery, seededAnchor?.primary_key)`.
  4. Preserve model selection toolbar (`modelId`) and quick prompts.
  5. Render messages list, in-thread loading spinner, error alert, and telemetry badges dynamically from context.

---

## 4. Acceptance Criteria
1. Clicking "INQUIRE IN GRAPHRAG CHAT" opens the drawer and immediately appends the formatted inquiry message with a live timestamp.
2. The loading indicator displays while the backend processes the request.
3. Upon receiving the response, the assistant answer and telemetry badge (latency and illuminated node count) are rendered in the thread.
4. Active nodes and edge keys illuminate immediately on the canvas in amber/gold.
5. Inquiring about successive nodes adds new conversational turns without wiping previous messages.
6. API failures render a clear in-thread error message stating the failure point and clearing the loading state.
