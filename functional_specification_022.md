# Functional Specification 022: Mobile Bottom Bar Occlusion Elimination, Dynamic Safe-Area Viewport Containment, and Non-Occluding Responsive Panel Ergonomics for the LAG Policy Engine Showcase

## 1. Objective & Scope

This specification defines the `{functionality}`, `{correctness}`, and `{correct required outputs}` required to eliminate all bottom bar and viewport occlusions on mobile and touch devices for the **LAG Policy Engine Showcase** (`https://luisp1028.github.io/lag-policy-engine-showcase/`).

Currently, on mobile viewports (iOS Safari, Android Chrome, and mobile web browsers with dynamic bottom address/navigation bars and hardware home-indicator safe areas), the visualizer exhibits severe bottom-edge clipping, mutual panel occlusion, and bottom-bar display collisions across five distinct surfaces:
1. **Dynamic Mobile Browser Bottom Chrome & Hardware Safe-Area Clipping:** Relying on static `100vh` viewport sizing without dynamic viewport units (`dvh`) or hardware safe-area inset clearances (`env(safe-area-inset-bottom)`) causes the lower edge of the visualizer—including the bottom of the **Medical Durable Goods Assistant** chat input bar, the lower scroll region of the **Node & Edge Detail Inspection Drawer**, and the bottom status/error banners—to be submerged and occluded behind the mobile browser's bottom toolbar and the device's OS home indicator bar.
2. **Bottom Fail-Fast Error & Readiness Banner Horizontal Overflow & Clipping:** On mobile screens, the bottom-anchored `backend-error-banner` and `backend-status-banner` use a single-row un-wrapped horizontal layout (`white-space: nowrap` buttons, `left: min(410px, calc(45vw + 20px))` offset when an inspection drawer is open, and `bottom: 20px` without safe-area offset), forcing the `"Retry Live API"`, `"Load Pre-computed LTA Snapshot"`, and `"Load Pre-computed IVIG Snapshot"` action buttons off the right edge of the mobile screen or directly behind the mobile browser bottom bar.
3. **Medical Durable Goods Assistant Bottom Input Bar & Drawer Footprint Occlusion:** On mobile viewports, constraining the right-hand **Medical Durable Goods Assistant** (`AgentChatDrawer`) to `maxWidth: 45vw` (~`168px`–`175px` on a `375px`–`390px` phone) crushes the bottom chat input form (`input` + `"Send"` button), quick-prompt chips, and message bubbles into an unusable vertical sliver while its bottom input bar sits flush against the occluded browser bottom edge without safe-area padding or mobile zoom prevention (`font-size >= 16px` on mobile text inputs to prevent iOS Safari auto-zoom displacement).
4. **Left-Hand Node & Edge Detail Inspection Drawer Mobile Footprint & Bottom Content Clipping:** On mobile viewports, constraining the left-hand inspection drawer (`NodeDetailDrawer`) to `maxWidth: 45vw` (~`168px`–`175px`) truncates statutory citations, provenance tables, and `"Connected Neighbors"` cards at the bottom of the scroll container, while opening both the left inspection drawer (`45vw`) and the right assistant drawer (`45vw`) simultaneously leaves only `10vw` (~`37px`) of center canvas and causes bottom banners and tooltips to collide with both drawers.
5. **Bottom Canvas Hover/Touch Tooltips & Top Toolbar Mobile Viewport Intrusion:** The bottom-docked `node-hover-tooltip` and `edge-hover-tooltip` (`bottom: 16px`) collide with the bottom status/error banners and mobile browser chrome, while the multi-row top `FilterToolbar` expands vertically over a large portion of the mobile screen, pushing interactive canvas space into the occluded bottom region.

In strict compliance with `@File:LANGUAGE.md` and project rules:
- This document specifies exclusively desired behaviors, viewport geometry boundaries, non-occlusion invariants, responsive layout states, edge cases, and objectively measurable acceptance criteria.
- It contains zero implementation instructions, code snippets, CSS syntax prescriptions, or architectural advice.
- The **DO NOT CODE YET** gate is active.

---

## 2. Domain & Glossary Alignment

All requirements and verification criteria in this specification strictly adopt the authoritative taxonomy in `@File:LANGUAGE.md`:

- **`{errors}`:** Explicit failure states or visual/interactive occlusions surfaced on mobile or desktop viewports.
  - **Qualifiers:**
    - Any bottom-anchored UI control—including the **Medical Durable Goods Assistant** message input field and `"Send"` button, the bottom of the **Node & Edge Detail Inspection Drawer** scroll view, the `backend-status-banner`, the `backend-error-banner` (`"Retry Live API"`, `"Load Pre-computed LTA Snapshot"`, `"Load Pre-computed IVIG Snapshot"`), or the `node-hover-tooltip` / `edge-hover-tooltip`—being clipped, submerged beneath the mobile browser's bottom navigation/address bar, or overlapping the OS hardware home indicator (`safe-area-inset-bottom`).
    - Any horizontal overflow (`scrollWidth > clientWidth`) of the root viewport or bottom banners that pushes interactive buttons outside the visible mobile screen bounds (`0 <= left < right <= window.innerWidth`).
    - Crushing either the left inspection drawer or the right assistant drawer into a narrow `45vw` sliver (`< 280px` width) on mobile viewports (`<= 768px`), rendering text, tables, or the bottom chat input form illegible or occluded.
    - Simultaneous full-height side-by-side drawer collisions on narrow mobile viewports (`<= 768px`) where opening `"◈ WHY IS THIS IMPORTANT?"` leaves both drawers competing for the same mobile screen width or occluding each other's close (`✕`) and action controls.
    - iOS Safari / mobile browser automatic viewport zoom-in triggered upon focusing text inputs (`SEARCH NODES`, `LIVE API HTTPS URL`, or the assistant chat input) that shifts the bottom bar off-screen.
    - Any regression to desktop (`> 1024px`) layout contracts established in Functional Specifications 019, 020, and 021 (left-docked inspection drawer, right-docked Medical Durable Goods Assistant, concurrent dual-drawer desktop operation, and zero Blueprint HUD / zero `"MODEL:"` selector).
- **`{correctness}`:** The precise, deterministic layout and interactive execution of every visual component across mobile (`<= 768px`), tablet (`769px`–`1024px`), and desktop (`> 1024px`) viewports without clipping, overflow, or occlusion.
  - **Qualifiers:** Every interactive control, drawer footer, input form, and status/error banner remains 100% within the visible dynamic viewport bounds (`window.visualViewport` / dynamic viewport height minus safe-area insets) with zero overlap between active interactive layers.
- **`{functionality}`:** The global objective of enabling mobile and desktop users visiting `https://luisp1028.github.io/lag-policy-engine-showcase/` to seamlessly filter the 8-hop Medicare knowledge graph, inspect nodes and edges, trigger `"◈ WHY IS THIS IMPORTANT?"`, read grounded `Qwen/Qwen2.5-7B-Instruct` syntheses, and interact with bottom banners and chat inputs without any bottom-bar display occlusion.
- **`{correct required outputs}`:** The exact, objectively measurable bounding-box coordinates, viewport containment invariants, safe-area clearances, and responsive state transitions defined in Sections 3 through 8.
- **`{sufficient}` / `{insufficient}`:** Complete, unambiguous functional specification where zero ambiguity remains and no arbitrary fallbacks or unverified assumptions are permitted.

---

## 3. Dynamic Mobile Viewport & Hardware Safe-Area Containment

### 3.1 Full-Screen Dynamic Viewport Height Adaptation
* **Context:** Mobile browsers dynamically expand and retract their top and bottom toolbars (URL bar, tab bar, navigation controls). Using static viewport height units (`100vh`) sizes the application container to the largest possible viewport height, causing the bottom `50px`–`90px` of the application to be hidden behind the browser's bottom bar when the toolbar is visible.
* **Desired Behavior & Outcomes:**
  - The application root container, canvas wrapper, left inspection drawer, and right assistant drawer must dynamically size their vertical height to the **actual visible dynamic viewport height** at all times on mobile devices.
  - Whenever the mobile browser's bottom address/navigation bar expands, retracts, or when the on-screen virtual keyboard opens or closes, the application's bottom boundary must immediately conform to the visible viewport bottom edge with zero vertical page scrolling and zero submerged content.
  - The HTML document viewport configuration must explicitly declare support for full safe-area edge-to-edge rendering (`viewport-fit=cover`) so that device safe-area environment insets are accurately reported by the mobile OS.

### 3.2 Hardware Safe-Area Bottom Clearance (`safe-area-inset-bottom`)
* **Desired Behavior & Outcomes:**
  - Every UI surface anchored to or reaching the bottom edge of the screen must incorporate a dedicated bottom safe-area clearance equal to at least the device's OS bottom safe-area inset plus a clean visual margin:
    1. **Medical Durable Goods Assistant Bottom Input Bar:** The bottom chat input form container must include bottom padding that clears the OS home indicator bar so the text input and `"Send"` button never sit underneath the home gesture bar.
    2. **Node & Edge Detail Inspection Drawer Scroll Container:** The scrollable body of the inspection drawer must include bottom safe-area clearance so the final items in `"Connected Neighbors"`, `"Entity Attributes"`, and `"Edge Provenance Metadata"` can be scrolled completely into view above the bottom safe-area zone.
    3. **Bottom Status & Fail-Fast Error Banners (`backend-status-banner` & `backend-error-banner`):** The bottom offset of all bottom-floating banners must be elevated above the OS bottom safe-area inset (and above any active mobile bottom sheet/drawer bar) so they are never clipped at the bottom of the screen.
    4. **Canvas Node & Edge Tooltips (`node-hover-tooltip` & `edge-hover-tooltip`):** The bottom offset of canvas tooltips must respect the bottom safe-area clearance and must never overlap an active bottom status/error banner.

---

## 4. Non-Occluding Bottom Banners & Tooltip Coordination on Mobile

### 4.1 Responsive Multi-Line Wrapping & Viewport Containment for Bottom Banners
* **Inputs:** Active `backend-status-banner` (during cold start / health probe) or active `backend-error-banner` (when live API is unreachable or returns a fail-fast error).
* **Desired Behavior & Outcomes:**
  - **Strict Horizontal Viewport Containment:** On all viewport widths (including `320px`–`430px` mobile phones), both `backend-status-banner` and `backend-error-banner` must be strictly contained within the horizontal viewport (`boundingClientRect.left >= 8px` and `boundingClientRect.right <= window.innerWidth - 8px`).
  - **Elimination of Off-Screen Left Offset on Mobile:** On mobile viewports (`<= 768px`), opening a node or edge inspection view must **not** push the `backend-status-banner` or `backend-error-banner` horizontally off-screen via desktop side-drawer offsets (`left: min(410px, calc(45vw + 20px))`). Instead, the banner must remain horizontally centered or full-width within the mobile viewport with symmetric horizontal margins (`12px`–`16px`).
  - **Responsive Action Button Wrapping:** Inside `backend-error-banner`, the error message text (`▲ FAIL-FAST ERROR: ...`) and the three action buttons (`"Retry Live API"`, `"Load Pre-computed LTA Snapshot"`, `"Load Pre-computed IVIG Snapshot"`) must wrap cleanly across multiple rows on narrow viewports so that all three buttons remain 100% visible, unclipped, and easily tappable (minimum touch target height `>= 32px`) without horizontal overflow.

### 4.2 Mutual Non-Occlusion Between Bottom Banners, Tooltips, and Active Drawers
* **Desired Behavior & Outcomes:**
  - **Banner vs. Tooltip Priority:** If both a bottom banner (`backend-status-banner` or `backend-error-banner`) and a canvas tooltip (`node-hover-tooltip` or `edge-hover-tooltip`) are active simultaneously, they must not render on top of each other at the same vertical coordinate. The tooltip must either dock above the banner with a clear vertical gap (`>= 8px`) or be suppressed on touch-only viewports when the full node/edge inspection drawer is already open.
  - **Banner vs. Open Mobile Drawer Coordination:** When the **Medical Durable Goods Assistant** or **Node & Edge Detail Inspection Drawer** is open on a mobile viewport, a bottom status/error banner must not silently cover and block the assistant's `"Send"` button or input box without a way for the user to interact with the banner or dismiss/resolve the state. Specifically:
    - If `backend-error-banner` is active, its snapshot fallback buttons (`"Load Pre-computed LTA Snapshot"` / `"Load Pre-computed IVIG Snapshot"`) and `"Retry Live API"` button must remain accessible and tappable at the top of the visual hierarchy (`z-index` above background layers), or positioned so they never permanently trap the chat input bar.

---

## 5. Responsive Mobile Ergonomics for the Inspection & Assistant Drawers

### 5.1 Preservation of Desktop Dual-Drawer Architecture (`> 768px`)
* **Desktop & Large Tablet Invariant:**
  - On viewports wider than `768px`, the exact layout architecture from Functional Specifications 019 and 020 must remain completely unchanged:
    - **Node & Edge Detail Inspection Drawer:** Docks flush left (`left: 0`, `top: 0`, `height: 100%`, width `390px` capped at `45vw` on tablets), with `border-right` and rightward drop shadow.
    - **Medical Durable Goods Assistant Drawer:** Docks flush right (`right: 0`, `top: 0`, `height: 100%`, width `440px` capped at `45vw` on tablets), with `border-left` and leftward drop shadow.
    - **Concurrent Dual-Drawer Operation on Desktop:** Both drawers can remain open simultaneously on opposite sides of the desktop viewport without closing each other.

### 5.2 Mobile Viewport Drawer Presentation & Elimination of `45vw` Sliver Crushing (`<= 768px`)
* **Context:** On mobile phones (`320px`–`768px` width), capping drawers at `45vw` forces a `375px` phone to render a `168px`-wide inspection drawer and a `168px`-wide chat drawer. At `168px` width, the bottom chat input box (`Ask Medicare policy question...`) and `"Send"` button collide and clip, table keys/values become unreadable, and having both drawers open leaves a `37px` unusable slit in the middle.
* **Desired Behavior & Outcomes on Mobile (`<= 768px`):**
  1. **Readable Full-Width / Bottom-Sheet Mobile Footprint:**
     - On mobile viewports (`<= 768px`), when either the **Node & Edge Detail Inspection Drawer** (`node-detail-drawer` / `edge-detail-drawer`) or the **Medical Durable Goods Assistant** (`agent-chat-drawer`) is open, it must span the **full usable width of the mobile viewport (`100vw` / `100%`)** (rendered either as a full-width mobile drawer or an ergonomic mobile bottom sheet occupying `75dvh`–`100dvh` anchored cleanly to the bottom of the dynamic viewport).
     - Neither drawer may be crushed to `45vw` on viewports `<= 768px`.
  2. **Clean Mobile Handoff Between Inspection and Assistant Drawers:**
     - Because a mobile viewport (`<= 768px`) cannot legibly display two side-by-side `390px`+ drawers simultaneously without mutual occlusion:
       - When the user is viewing a node in the mobile **Node Detail Drawer** and taps **`"◈ WHY IS THIS IMPORTANT?"`**, the **Medical Durable Goods Assistant** drawer must immediately come to the foreground at full mobile width (`100%`), seed the selected node's `[PRIMARY_KEY]` anchor, and dispatch the unified importance inquiry—without the left inspection drawer occluding half of the assistant drawer or blocking the bottom chat input bar.
       - While on mobile (`<= 768px`), the user must be able to effortlessly switch back to the inspected node's details (or close the assistant drawer via `✕` to reveal the underlying canvas/inspection state, or tap the toolbar toggle) with zero overlapping drawer text or occluded bottom bars.
       - Conversely, tapping a node or edge on the canvas on mobile (`<= 768px`) must bring the **Node / Edge Detail Drawer** cleanly into view without being hidden behind an unclosed full-screen chat overlay.
  3. **Unoccluded Mobile Assistant Bottom Input Form:**
     - Inside the **Medical Durable Goods Assistant** on mobile (`<= 768px`), the bottom input form (`form` containing the text `input` and `"Send"` submit button) must remain pinned inside the visible bottom boundary of the drawer above the mobile browser's bottom bar and OS safe-area inset.
     - The text input field must have an effective font size of at least `16px` on mobile viewports (`<= 768px`) so that tapping the input on iOS Safari / mobile browsers **never triggers automatic page zoom-in** that pushes the `"Send"` button or bottom bar off-screen.
     - Both the text input and the `"Send"` button must fit completely within the mobile viewport width with zero horizontal clipping.

---

## 6. Mobile Top Toolbar (`FilterToolbar`) Compactness & Non-Occlusion

### 6.1 Preventing Top Toolbar Vertical Takeover on Mobile
* **Context:** On mobile viewports (`<= 768px`), `FilterToolbar` currently positions itself at `left: isInspectionOpen ? 'min(404px, calc(45vw + 14px))' : 14` and wraps 9 separate filter/control groups vertically without a compact mobile layout, consuming up to `50%`–`60%` of the vertical screen height or getting crushed to the right when a node is selected.
* **Desired Behavior & Outcomes on Mobile (`<= 768px`):**
  - **Full Horizontal Span on Mobile:** On mobile viewports (`<= 768px`), `FilterToolbar` must anchor across the top of the viewport (`left: 8px` to `14px`, `right: 8px` to `14px`) rather than shifting right by `45vw + 14px` when a node is selected.
  - **Compact Mobile Footprint & Collapsible/Scrollable Filter Controls:**
    - On mobile viewports (`<= 768px`), the top toolbar must remain compact so that the primary interactive canvas and bottom controls are never starved of vertical viewport space.
    - Primary actions—including the execution status indicator (`execution-status-badge`), the **`"◈ GRAPHRAG CHAT"`** toggle button (`graphrag-chat-toggle`), `"✕ RESET PATH"` (`reset-path-btn` when illuminated), and a compact filter access mechanism (or horizontally scrollable / collapsible filter strip)—must remain accessible without the toolbar occluding more than `25%` of the mobile viewport height in its default state.
    - All existing `data-testid` attributes (`filter-toolbar`, `run-mode-select`, `api-url-config-btn`, `jurisdiction-select`, `state-select`, `policy-select`, `category-select`, `node-search-input`, `fee-schedule-toggle`, `execution-status-badge`, `reset-path-btn`, `graphrag-chat-toggle`) must remain accessible in the DOM for deterministic interaction and automated verification.

---

## 7. Touch Interaction & Edge Cases on Mobile Viewports

1. **Touch Tap Selection on Canvas (`GraphCanvas`):**
   - Tapping a node or edge on a mobile touch screen must deterministically select that node or edge and open its inspection view without leaving a stuck hover tooltip (`node-hover-tooltip` / `edge-hover-tooltip`) occluding the bottom of the screen.
2. **Orientation Change & Dynamic Browser Bar Resize (`portrait` ↔ `landscape`):**
   - Rotating a mobile device between portrait and landscape or scrolling/toggling the mobile browser's bottom toolbar must immediately recalculate canvas dimensions (`syncCanvasDimensions`) and drawer heights without leaving a white/void gap or clipped bottom bar.
3. **Long Statutory Excerpts & Neighbor Lists on Mobile:**
   - Scrolling to the very bottom of `NodeDetailDrawer` or `EdgeDetailDrawer` on a mobile viewport (`375x667` or `390x844`) must reveal the final neighbor card and its `"Inspect Edge"` button completely above the bottom edge of the viewport with at least `16px` + `env(safe-area-inset-bottom)` of bottom breathing room.
4. **Virtual Keyboard Appearance in Assistant Chat:**
   - When the user focuses the assistant chat input on mobile, the input bar and `"Send"` button must remain visible above the keyboard, and dismissing the keyboard must restore the drawer bottom bar cleanly above the browser's bottom bar.

---

## 8. End-to-End Acceptance Criteria (`{correct required outputs}`)

The implementation will be evaluated as `{sufficient}` and meeting `{correctness}` and `{functionality}` only when all of the following criteria are objectively verified across both mobile (`375x667` iPhone SE, `390x844` iPhone 14/15, `360x800` Android) and desktop (`1440x900`) viewports:

1. **Zero Bottom-Bar Viewport Clipping on Mobile (`375x667` & `390x844`):**
   - The root container, `GraphCanvas`, `NodeDetailDrawer`, and `AgentChatDrawer` use dynamic viewport height sizing (`100dvh` with `100vh` fallback) and `viewport-fit=cover` safe-area support.
   - Zero interactive elements at the bottom of the screen extend beyond `window.innerHeight` (`boundingClientRect.bottom <= window.innerHeight`) or `window.innerWidth` (`boundingClientRect.right <= window.innerWidth` and `boundingClientRect.left >= 0`).
2. **Unoccluded Assistant Chat Bottom Input Bar on Mobile:**
   - When `AgentChatDrawer` (`data-testid="agent-chat-drawer"`) is open on a `375x667` or `390x844` mobile viewport, its width spans the full mobile viewport (`>= 350px`, not crushed to `45vw`), and the bottom chat input field and `"Send"` button are 100% visible, unclipped (`boundingClientRect.bottom <= window.innerHeight`), and padded above `env(safe-area-inset-bottom)`.
   - The chat input font size on mobile (`<= 768px`) is at least `16px` to prevent iOS Safari auto-zoom displacement.
3. **Unoccluded Node & Edge Detail Drawer on Mobile:**
   - Selecting any node or edge on a `375x667` or `390x844` mobile viewport opens `node-detail-drawer` / `edge-detail-drawer` at readable mobile width (`>= 350px`, not crushed to `45vw`).
   - The `"◈ WHY IS THIS IMPORTANT?"` button (`data-testid="inquire-node-btn"`) and the bottom-most `"Connected Neighbors"` cards are 100% reachable and unoccluded.
   - Clicking `"◈ WHY IS THIS IMPORTANT?"` on mobile cleanly transitions focus to the **Medical Durable Goods Assistant** drawer without the two drawers overlapping or occluding each other's bottom controls.
4. **Unoccluded & Responsive Bottom Status/Error Banners on Mobile:**
   - When `backend-error-banner` or `backend-status-banner` is rendered on a `375x667` mobile viewport (whether or not a node is selected), its bounding box satisfies `0 <= left` and `right <= 375` and `bottom <= 667`, with all three action buttons (`retry-backend-btn`, `load-precomputed-lta-btn`, `load-precomputed-ivig-btn`) wrapped cleanly inside the viewport and 100% clickable.
5. **Zero Desktop Regression (`1440x900`):**
   - On desktop viewports (`1440x900`), the left-docked `NodeDetailDrawer` (`390px` width, `left: 0`) and right-docked `AgentChatDrawer` (`440px` width, `right: 0`) continue to operate concurrently side-by-side when `"◈ WHY IS THIS IMPORTANT?"` is clicked, preserving 100% of Functional Specifications 019, 020, and 021 contracts.
