# Functional Specification 019: Left-Hand Docking Architecture, Elimination of Blueprint HUD, Model Selector Removal, and Hugging Face DeepSeek-Powered Medical Durable Goods Assistant

## 1. Objective & Scope

This specification establishes the `{functionality}`, `{correctness}`, and `{correct required outputs}` for four coordinated visualizer ergonomics, interface refinement, and intelligence delivery initiatives:
1. **Transitioning the Node & Edge Detail Inspection Drawer** from its right-hand viewport docking to a **permanent left-hand docking position** on the interactive graph visualization interface.
2. **Completely removing the `"LAG KNOWLEDGE BLUEPRINT HUD"` overlay** from the canvas viewport, eliminating redundant floating telemetry cards, removing collision surfaces in the upper-left quadrant, and dedicating the entire upper visualizer region to clean force-directed graph exploration.
3. **Removing the `"MODEL:"` selection control** from the conversational assistant drawer while establishing **`Qwen2.5-7B-Instruct`** (`Qwen/Qwen2.5-7B-Instruct`) as the permanent, authoritative default synthesis model across all conversational inquiries.
4. **Rebranding the conversational assistant to `"Medical Durable Goods Assistant"`** and replacing the static subtitle (`"Zero-Hallucination Topological Synthesis"`) with an **LLM-generated dynamic micro-fact** derived directly from knowledge graph data (strictly under 15 words), synthesized using a **dedicated Hugging Face DeepSeek model node** (e.g. `deepseek-ai/DeepSeek-R1` / `deepseek-ai/DeepSeek-V3` or compatible distilled variant on the Hugging Face Router/Inference API) authenticated with an independent, dedicated Hugging Face user access token (`HF_DEEPSEEK_TOKEN`).

The collective outcome is a balanced, minimalist, zero-distraction visualizer and intelligence environment:
- **Left-Hand Viewport Margin:** Dedicated to deep entity inspection, regulatory/statutory text excerpts, official government authority hyperlinks, edge directional linkages, and hop connectivity.
- **Right-Hand Viewport Margin:** Dedicated to the **Medical Durable Goods Assistant**, featuring an active dynamic micro-fact banner summarizing an authoritative graph relationship in under 15 words, quick prompts, query input, and execution telemetry badges—free from unnecessary model selection dropdowns.
- **Upper Canvas Viewport:** Completely clean and unobstructed following the removal of the floating Blueprint HUD overlay, allowing node clusters and top-level legislative anchors to render without visual overlap or pointer-event obstruction.
- **Dual Hugging Face Tiered Intelligence Architecture:**
  - **Inquiry & Path Synthesis Engine:** Executes against `Qwen2.5-7B-Instruct` using the primary Hugging Face token (`ACT-KG-` / `HF_TOKEN`), guaranteeing rigorous grounding and exact coinsurance arithmetic for multi-hop user inquiries.
  - **Graph Micro-Fact Generator:** Executes against a dedicated **Hugging Face DeepSeek model endpoint** (`deepseek-ai/...`) using a separate, isolated Hugging Face token (`HF_DEEPSEEK_TOKEN`), generating concise, authoritative graph fact snippets under 15 words to illuminate live graph context.
- **Center Canvas:** Remains fully interactive between both panels, allowing operators to simultaneously inspect structured entity details on the left and converse with the assistant on the right without visual collisions or drawer occlusion.

In strict compliance with `@File:LANGUAGE.md` and project governance:
- This document describes exclusively desired behaviors, visual outcomes, boundary constraints, collision rules, inputs, outputs, and verifiable acceptance criteria.
- It contains zero implementation instructions, CSS rule prescriptions, code sketches, or architectural advice.
- The **DO NOT CODE YET** gate is active.

---

## 2. Taxonomy & Evaluation Parameters

All requirements and verification parameters in this specification are governed by the authoritative glossary in `@File:LANGUAGE.md`:

- **`{errors}`:** 
  - The inspection drawer renders anchored to the right margin or off-screen.
  - The inspection drawer visually overlaps, clips, or renders unclickable node hover tooltips or system status banners.
  - The drawer blocks canvas drag, pan, or zoom events that occur outside its physical left-docked footprint.
  - The Blueprint HUD card, accordion toggle, FPS counter, or `"◈ LAG KNOWLEDGE BLUEPRINT HUD"` banner is still present or rendered anywhere in the canvas DOM.
  - The `"MODEL:"` label, dropdown, or model selector bar is still visible or rendered inside the conversational chat drawer.
  - The assistant title displays `"HUGGING FACE GRAPHRAG ASSISTANT"` instead of `"Medical Durable Goods Assistant"`.
  - The subtitle displays static text (e.g. `"Zero-Hallucination Topological Synthesis"`) or an LLM-generated micro-fact exceeding 15 words.
  - Hardcoded Hugging Face API keys or cross-credential contamination: using the primary `ACT-KG-` / `HF_TOKEN` for the micro-fact DeepSeek inference call, or committing raw tokens to git.
  - Silent degradation or unhandled exception upon missing `HF_DEEPSEEK_TOKEN`: failing silently or freezing drawer rendering rather than failing fast or displaying an explicit, grounded fallback state.
- **`{correctness}`:** 
  - Clicking any node or directional edge immediately opens the inspection drawer flush against the left boundary of the visualizer viewport (`0px` left offset).
  - The drawer's interior visual elevation, border styling, and drop shadow project rightward into the canvas area rather than leftward.
  - The upper-left quadrant of the canvas is completely clear of floating HUD overlay elements.
  - All 17 node entity categories and 18 relationship edge types render complete native attributes, derived attributes, text excerpts, official citations, verified government hyperlinks, and neighbor hop lists with 100% attribute fidelity.
  - Submitting any query from the chat drawer or via `"◈ INQUIRE IN GRAPHRAG CHAT"` deterministically routes with `model_id: "Qwen/Qwen2.5-7B-Instruct"` using `HF_TOKEN`.
  - The dynamic micro-fact generated by the Hugging Face DeepSeek model is an accurate statement about an entity or relationship present in the active graph topology and contains strictly between 1 and 14 words inclusive.
- **`{functionality}`:** 
  - A responsive, uncluttered visualizer layout where entity inspection on the left and Medical Durable Goods Assistant dialogue on the right operate concurrently and independently without stacking or mutual occlusion.
  - An unobstructed canvas viewport free from redundant floating HUD telemetry panels.
  - A branded, production-grade assistant interface presenting live, LLM-generated graph insights alongside streamlined query interactions.
- **`{correct required outputs}`:** 
  - Explicit physical coordinate boundaries, responsive width limits, z-index elevation hierarchy, micro-fact word count boundaries, and API payload contracts specified in Sections 3 through 8.
- **`{sufficient}` / `{insufficient}`:** 
  - Complete, unambiguous behavioral requirements that allow a coding assistant to execute the layout transition, HUD elimination, model selection removal, assistant rebranding, and Hugging Face DeepSeek micro-fact integration without making arbitrary assumptions.

---

## 3. Physical Layout & Docking Specifications

### 3.1 Left-Hand Margin Docking
* **Inputs:** 
  - User click event on an entity node circle or label badge on the canvas.
  - User click event on a directional relationship link or edge label on the canvas.
  - User click event on a connected neighbor card within an open inspection view.
* **Desired Behavior & Outcomes:**
  - The inspection drawer must anchor flush to the **left edge** of the viewport (`left: 0`).
  - It must extend continuously from the top edge of the canvas viewport (immediately beneath or flush with the top control toolbar) down to the bottom viewport boundary, occupying full available vertical height (`100%` height).
  - The panel must present a fixed, readable width on standard desktop displays (between `380px` and `420px`) that ensures structured property tables, long statutory citations, and multi-line text excerpts remain legible without horizontal scrolling.
  - On constrained viewports (such as tablets or split-screen windows narrower than `1024px`), the drawer must constrain its width to not exceed `45%` of the total viewport width, ensuring that at least `55%` of the interactive graph canvas remains visible and operable.

### 3.2 Visual Projection & Elevation Hierarchy
* **Desired Behavior & Outcomes:**
  - Because the panel is anchored to the left, its structural boundary line must separate it from the canvas along its **right vertical border** (border-right facing the canvas interior).
  - Its depth elevation drop shadow must cast rightward into the graph canvas area (e.g., positive horizontal shadow projection), providing clear visual separation against dark blueprint background void colors and force-directed node clusters.
  - The internal scroll container must support smooth vertical scrolling for extensive attribute lists and long legal excerpts while strictly preventing horizontal page jitter.

---

## 4. Complete Elimination of the Blueprint HUD Telemetry Overlay

### 4.1 HUD Removal Rationale & Behavioral Scope
* **Current Context:** 
  - The canvas renders a floating, collapsible card labeled `"◈ LAG KNOWLEDGE BLUEPRINT HUD"` docked at `top: 14px, left: 14px`.
  - When expanded, it displays `NODES: {count}`, `EDGES: {count}`, `FPS: {fps}`, and `STATUS: {state}`.
  - This overlay introduces visual clutter, partially overlaps top toolbar elements on smaller screens, and directly conflicts with the left-hand margin where the inspection drawer docks. Furthermore, node and edge counts are already communicated through toolbar status badges, filter metrics, and API health endpoints.
* **Desired Behavior & Outcomes:**
  - The **`"LAG KNOWLEDGE BLUEPRINT HUD"` overlay must be completely removed** from the canvas interface.
  - Zero HUD components, floating cards, accordion expand/collapse toggles, or telemetry label bars may render over the canvas in the DOM.
  - All mouse and pointer interactions across the entire upper-left region of the canvas must pass directly and smoothly to the underlying D3 graph canvas for panning, node dragging, and canvas selection.
  - The canvas layout must be entirely unencumbered by upper-left overlay collisions.

---

## 5. Overlay Layering & Coexistence Rules

With the Blueprint HUD removed, the remaining canvas overlays must coordinate cleanly with the left-docked inspection drawer:

### 5.1 Interaction with Node & Edge Hover Tooltips
* **Current Context:** When the user hovers the cursor over a node or edge on the canvas, a transient summary tooltip appears near the bottom-left canvas margin.
* **Desired Behavior:**
  - While the inspection drawer is open, hover tooltips triggered on the remaining visible canvas must position themselves in the open canvas space (offset to the right of the drawer's right boundary) or dock above the drawer boundary, ensuring tooltip text is never clipped or hidden beneath the left-docked panel.
  - Hovering over elements inside the inspection drawer itself (such as neighbor cards, action buttons, or external links) must not trigger canvas-level hover tooltips.

### 5.2 Interaction with Fail-Fast Backend Error & Status Banners
* **Current Context:** System connection alerts, readiness indicators, and fail-fast backend error banners appear anchored near the bottom-left of the screen (`bottom: 20px, left: 20px`).
* **Desired Behavior:**
  - When a fail-fast error banner or cold-start readiness alert is active, it must remain fully legible and interactive.
  - If the inspection drawer is open simultaneously with an error banner, the banner must display at an elevated layer (`z-index` higher than the drawer) or dynamically reposition along the bottom edge to avoid obscuring drawer action buttons (such as the `"◈ INQUIRE IN GRAPHRAG CHAT"` trigger).
  - Users must retain the ability to click `"Retry Live API"` and snapshot buttons on the error banner without obstruction from the drawer.

---

## 6. Dual-Panel Concurrent Operation (Left Inspection + Right Chat)

### 6.1 Independent Lifecycle & Non-Interference
* **Desired Behavior & Outcomes:**
  - The left-hand inspection drawer and the right-hand conversational assistant drawer must have completely independent lifecycle states:
    1. Opening the left inspection drawer must **not** force-close the right chat drawer.
    2. Opening the right chat drawer must **not** force-close the left inspection drawer.
    3. Closing the left inspection drawer (via the `"✕"` button or canvas background click) must **not** dismiss or reset active chat dialogues or query streaming on the right.
    4. Closing the right chat drawer must **not** deselect the currently inspected node or close the left inspection drawer.
  - When both panels are simultaneously open on a standard desktop display (`>= 1280px` width):
    - The left panel occupies the left margin (`~390px`).
    - The right panel occupies the right margin (`~440px`).
    - The center region (at least `450px` wide) displays the force-directed graph canvas, with nodes, edges, and illuminated paths clearly visible and operable.

### 6.2 One-Click Inquire Handoff Interaction
* **Desired Behavior & Outcomes:**
  - The left inspection drawer contains the primary action button: `"◈ INQUIRE IN GRAPHRAG CHAT"`.
  - When an operator clicks this button in the left drawer:
    1. The right-hand conversational chat drawer must immediately open (if currently closed).
    2. The target node's identity and primary key must be seeded into the chat context as the inquiry anchor.
    3. The left inspection drawer must remain open and visible in its left-docked position, allowing the operator to cross-reference the entity's statutory citations and native attributes while the language model synthesizes the answer on the right.

---

## 7. Removal of `"MODEL:"` Selector & Authoritative Default Model Specification

### 7.1 Complete Elimination of the `"MODEL:"` UI Section
* **Current Behavior:** 
  - The conversational assistant drawer renders a dedicated sub-toolbar between the header and quick prompts containing the label `"MODEL:"` and an interactive `<select>` dropdown offering `Llama-3-8B-Instruct`, `Mistral-7B-Instruct-v0.3`, and `Qwen2.5-7B-Instruct`.
  - This sub-toolbar consumes vertical screen space, introduces unnecessary cognitive load for operators seeking domain answers, and exposes model options that do not perform uniformly on granular 8-hop fee schedule arithmetic.
* **Desired Behavior:**
  - The entire `"MODEL:"` selection toolbar (including the `"MODEL:"` label, surrounding wrapper container, and dropdown element) must be **completely removed** from the chat drawer UI.
  - The conversational drawer interface must transition seamlessly from the drawer header directly into the quick prompts bar and message history.
  - End users must have zero exposed model selection dropdowns or manual model switching options in the UI.

### 7.2 Default Model Enforcement: `Qwen2.5-7B-Instruct`
* **Authoritative Identifier:** `Qwen/Qwen2.5-7B-Instruct`
* **Desired Behavior & Invariants:**
  - All conversational GraphRAG synthesis queries dispatched from the web frontend—whether triggered via:
    1. The free-form text input box in the chat drawer,
    2. Any of the pre-set quick prompt buttons, or
    3. The one-click `"◈ INQUIRE IN GRAPHRAG CHAT"` button from the left-docked inspection drawer
    must automatically and deterministically specify `model_id: "Qwen/Qwen2.5-7B-Instruct"`.
  - In the synchronization context (`GraphSyncContext`) and backend request dispatcher, the default model parameter must be bound exclusively to `Qwen/Qwen2.5-7B-Instruct`.
  - If a query request is received by the backend without an explicit `model_id` field, the backend runtime must default to `Qwen/Qwen2.5-7B-Instruct` (or its canonical operational identifier `Qwen/Qwen2.5-72B-Instruct` under router aliases) rather than falling back to Llama-3 or Mistral.

---

## 8. Medical Durable Goods Assistant Rebranding & Hugging Face DeepSeek Micro-Fact Subtitle

### 8.1 Header Rebranding
* **Current Text:** `◈ HUGGING FACE GRAPHRAG ASSISTANT`
* **Required New Text:** `◈ Medical Durable Goods Assistant`
* **Desired Behavior:**
  - The top title of the right-hand conversational drawer must clearly display the branded title `"Medical Durable Goods Assistant"`.
  - The styling must preserve the authoritative amber accent color (`CANVAS_PALETTE.accentAmber`), bold weight, and legible letter-spacing.

### 8.2 Dynamic Micro-Fact Subtitle Specification
* **Current Subtitle:** `Zero-Hallucination Topological Synthesis` (static string).
* **Desired Behavior:**
  - Replace the static subtitle with a **dynamically generated micro-fact** describing an authoritative, verified truth from the knowledge graph.
  - **Strict Word Count Constraint:** The micro-fact must strictly contain **under 15 words** (1 to 14 words inclusive). It must be punchy, precise, and easily readable at a glance without text truncation or awkward multi-line wrapping.
  - **Subject Matter Content:** The snippet must state a concrete fact grounded in the graph, such as legislative enactment, coverage policy boundaries, statutory codification, or reimbursement standards (e.g., *"Public Law 117-328 mandates Medicare Part B coverage for compression garments."* or *"DME MAC Jurisdiction B administers Medicare claims across Illinois and Wisconsin."*).

### 8.3 Dedicated Hugging Face DeepSeek Model Node & Credential Isolation
* **Architectural Separation:**
  - Micro-fact generation must execute through a dedicated **Hugging Face DeepSeek model endpoint** (e.g., `deepseek-ai/DeepSeek-R1`, `deepseek-ai/DeepSeek-V3`, or a compatible official distilled DeepSeek model hosted on the Hugging Face Router/Inference API).
  - This node is architecturally decoupled from the multi-hop user inquiry synthesis pipeline (which remains powered by `Qwen2.5-7B-Instruct`).
* **Hugging Face Token Type & Isolation:**
  - The operator must create a **Hugging Face User Access Token** (Fine-Grained or classic Read token with `Inference` permissions) generated from [Hugging Face Access Tokens Settings](https://huggingface.co/settings/tokens).
  - The token is provisioned to the backend runtime via an independent environment variable: **`HF_DEEPSEEK_TOKEN`**.
  - **Zero Credential Conflation:** The system must strictly preserve the existing primary `ACT-KG-` / `HF_TOKEN` credential exclusively for the Qwen multi-hop synthesis engine. The `HF_DEEPSEEK_TOKEN` must be dedicated exclusively to the micro-fact generator.
  - **Zero Leakage:** Neither token may be committed to git, Docker image layers, or browser-side client bundles; all inference calls execute server-side within the container.
* **Fail-Fast & Offline Resilience:**
  - If `HF_DEEPSEEK_TOKEN` is omitted or the Hugging Face DeepSeek endpoint encounters an outage, the system must not crash or halt drawer rendering.
  - If in-flight micro-fact generation fails or exceeds timeout boundaries, the subtitle must gracefully display a deterministic, verified default graph micro-fact (e.g., *"Public Law 117-328 codifies Medicare compression garment benefits."* — 8 words) while logging an explicit telemetry notice.

---

## 9. Functional Inspection Requirements Preserved

The left-docked drawer must preserve 100% of the functional content and interaction contracts established across all 17 entity categories and 18 relationship types:

1. **Header Block:**
   - Entity category badge with assigned domain color palette.
   - Canonical display name and bracketed primary key identifier.
   - Distinct close button (`✕`) that deselects the active entity and dismisses the drawer.
2. **Contextual Action:**
   - One-click GraphRAG inquiry action (`"◈ INQUIRE IN GRAPHRAG CHAT"`), with active loading and disabled states during in-flight synthesis.
3. **Verified Government Authority Link:**
   - Property-driven external hyperlink routing deterministically to official primary sources (Congress.gov, GPO GovInfo, Federal Register, Cornell LII, CMS Transmittals, CMS MCD, CDC Clinical Browser, Noridian, CGS, Senate LDA, or CBO).
4. **Complete Legal & Administrative Text Excerpt:**
   - Full statutory language, regulatory preambles, or clinical descriptions formatted in a dedicated quote container.
5. **Complete Extracted Property Tables:**
   - Direct Path (Native Keys) and Structural Traversal (Derived Keys) rendered in alternating key-value rows with formatted dollar values for fee rates.
6. **Provenance Metadata Block:**
   - All 4 verified audit fields: `source_uri`, `selector`, `run_id`, and `ingestion_timestamp`.
7. **Connected Neighbors / Hop Exploration:**
   - Categorized list of immediate incoming and outgoing relationships displaying directional arrows (`→` / `←`), relationship labels, neighbor names, and category badges.
   - Clicking any neighbor card immediately jumps focus and updates the left-hand drawer to inspect that neighbor node.
8. **Edge / Relationship Inspection Mode:**
   - When an edge is selected, the left-hand drawer must render relationship label, directional path (`source -> label -> target`), clickable source and target entity cards, and full edge provenance metadata.

---

## 10. End-to-End Acceptance Criteria

The implementation will be evaluated as `{sufficient}` and meeting `{correctness}` and `{functionality}` only when all of the following criteria are objectively verified:

1. **Left-Hand Viewport Docking:**
   - Selecting any node or edge causes the inspection drawer to slide in or appear docked flush against the left boundary (`left = 0`).
   - The right margin of the visualizer viewport remains completely open for canvas viewing and the right-hand chat drawer.
2. **Visual Separation & Shadow Orientation:**
   - The drawer displays its dividing border along its right edge (`border-right`), with its drop shadow cast rightward onto the canvas.
3. **Complete Elimination of Blueprint HUD Telemetry Overlay:**
   - Zero Blueprint HUD overlay elements, toggles, or floating cards exist in the DOM or render over the canvas.
   - Panning and zooming in the upper-left quadrant of the canvas is completely unhindered by pointer-event barriers.
4. **Overlay Coexistence:**
   - Canvas hover tooltips and fail-fast error banners remain legible, reachable, and unclipped when the left drawer is open.
5. **Dual-Drawer Concurrency:**
   - An operator can open both the left inspection drawer (by clicking a node) and the right chat drawer (by clicking `"◈ INQUIRE IN GRAPHRAG CHAT"` or the toolbar chat button) simultaneously. Both panels render without visual overlapping on desktop viewports.
6. **Complete Elimination of `"MODEL:"` UI Section:**
   - In the right-hand conversational assistant drawer, zero `"MODEL:"` text, sub-toolbars, or `<select>` dropdowns are rendered in the DOM.
   - The header connects cleanly to the quick prompts bar without dead space or layout gaps.
7. **Enforcement of Default Model `Qwen2.5-7B-Instruct`:**
   - All outgoing network requests to `POST /api/graphrag/query` carry `"model_id": "Qwen/Qwen2.5-7B-Instruct"`.
   - Synthesized answers verify grounded execution using the `Qwen/Qwen2.5-7B-Instruct` pipeline without runtime errors.
8. **Rebranding to "Medical Durable Goods Assistant":**
   - The drawer title displays `"◈ Medical Durable Goods Assistant"` with zero references to `"HUGGING FACE GRAPHRAG ASSISTANT"`.
9. **Hugging Face DeepSeek Micro-Fact Generation & Word Count Compliance:**
   - The subtitle displays an LLM-generated graph fact strictly under 15 words.
   - The micro-fact is generated via a dedicated Hugging Face DeepSeek model endpoint (`deepseek-ai/...`) using an isolated `HF_DEEPSEEK_TOKEN` Hugging Face User Access Token.
   - The primary `ACT-KG-` Hugging Face credential remains completely dedicated to Qwen query synthesis with zero credential leakage.
10. **Full Inspection Fidelity:**
   - All 17 node categories and 18 edge types render their complete headers, badges, native/derived attributes, text excerpts, government authority links, provenance metadata, and neighbor navigation in the left-docked panel without missing fields or layout distortion.
11. **Zero Code Generation Gate:**
   - Zero application code, CSS files, or test suites are modified or created during the specification authoring stage.
