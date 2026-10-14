# Functional Specification 020: "Why Is This Important?" Entity Inquiry Trigger, Elimination of Hardcoded Category Prompts, and Straightforward Node Explanation Synthesis

## 1. Objective & Scope

This specification establishes the `{functionality}`, `{correctness}`, and `{correct required outputs}` for refining how operators inquire about inspected knowledge graph entities and how the **Medical Durable Goods Assistant** formulates and answers those inquiries:

1. **Transitioning the Entity Inspection Action Trigger to `"◈ WHY IS THIS IMPORTANT?"`:** Replacing the technical `"◈ INQUIRE IN GRAPHRAG CHAT"` button inside the left-hand entity inspection panel with an intuitive, user-centered action button labeled **`"◈ WHY IS THIS IMPORTANT?"`**.
2. **Elimination of Hardcoded Per-Category Inquiry Prompts:** Removing all category-specific hardcoded prompt templates across the 17 entity categories and replacing them with a **single, unified importance inquiry prompt** that dynamically incorporates the selected node's bracketed primary key (`[PRIMARY_KEY]`) and human-readable display name.
3. **Streamlining Quick-Prompt Suggestions Upon Node Selection:** Replacing multi-branch category-specific hardcoded quick-prompt lists with concise, universal follow-up prompts focused on the selected entity's importance, upstream authority, and downstream patient/coverage impact.
4. **Straightforward Explanation Synthesis:** Ensuring that when a user triggers `"◈ WHY IS THIS IMPORTANT?"` (or submits a node inquiry), the Medical Durable Goods Assistant delivers a clear, straightforward, plain-language explanation of what the queried entity is and why it matters within the Medicare legislative-to-administrative lineage—while strictly preserving zero-hallucination grounding, exact bracketed primary-key citations (`[PRIMARY_KEY]`) for canvas path illumination, official legal citations, and exact fee/coinsurance figures when present in context.

In strict compliance with `@File:LANGUAGE.md` and project governance:
- This document describes exclusively desired behaviors, user-facing labels, prompt inputs, synthesis outputs, constraints, edge cases, and verifiable acceptance criteria.
- It contains zero implementation instructions, code sketches, component breakdowns, or architectural advice.
- The **DO NOT CODE YET** gate is active.

---

## 2. Taxonomy & Evaluation Parameters

All requirements and verification parameters in this specification are governed by the authoritative glossary in `@File:LANGUAGE.md`:

- **`{errors}`:**
  - The left-hand entity inspection panel still renders the legacy button label `"◈ INQUIRE IN GRAPHRAG CHAT"` instead of `"◈ WHY IS THIS IMPORTANT?"`.
  - Clicking `"◈ WHY IS THIS IMPORTANT?"` dispatches one of the legacy category-specific hardcoded multi-part prompts (e.g., `"What is the legislative history, omnibus incorporation, and purpose of..."` or `"What operational instructions, benefit categories, and coverage policies are mandated by..."`) rather than the unified importance prompt.
  - Hardcoded per-category prompt switch tables remain active for node inquiry generation.
  - The assistant responds with ungrounded speculation, omits bracketed primary-key identifiers (`[PRIMARY_KEY]`) needed to illuminate the canvas path, or fails to explain in straightforward terms what the node is and why it is important.
  - Duplicate or overlapping inquiries are dispatched if the user clicks the button while a query is already in flight.
- **`{correctness}`:**
  - Every inspected node across all 17 entity categories renders the action trigger labeled `"◈ WHY IS THIS IMPORTANT?"` in its idle state.
  - Clicking `"◈ WHY IS THIS IMPORTANT?"` deterministically generates a single unified prompt asking what the entity (`[PRIMARY_KEY]` and its resolved display name) is and why it is important in the legislative-to-administrative coverage lineage.
  - The generated inquiry is automatically submitted to the Medical Durable Goods Assistant using the selected node's `primary_key` as the seeded anchor entity and `Qwen/Qwen2.5-7B-Instruct` as the synthesis model.
  - The synthesized response clearly states what the entity is, explains why it is important to the broader policy/coverage chain, cites exact bracketed identifiers (`[PRIMARY_KEY]`) from the assembled graph context, and triggers bidirectional path illumination on the graph canvas.
- **`{functionality}`:**
  - An intuitive, one-click workflow allowing any user—whether a policy analyst, clinician, or patient advocate—to select any node on the canvas, click `"◈ WHY IS THIS IMPORTANT?"`, and immediately receive a clear, grounded explanation of that node's role and significance alongside visual illumination of its connected graph lineage.
- **`{correct required outputs}`:**
  - Exact button labels, unified prompt text structure, quick-prompt behaviors, and synthesized answer requirements defined in Sections 3 through 7.
- **`{sufficient}` / `{insufficient}`:**
  - Complete, unambiguous functional requirements enabling implementation without guesswork or unverified assumptions.

---

## 3. Left-Hand Inspection Panel Action Button (`"◈ WHY IS THIS IMPORTANT?"`)

### 3.1 Idle & Loading Visual States
* **Context:** When any node is selected on the graph canvas (or navigated to via a connected neighbor card), the left-hand inspection panel displays the node's metadata, text excerpt, official citations, and primary action button.
* **Desired Behavior & Outcomes:**
  - **Idle State Label:** When no conversational query is currently in flight, the primary action button inside the node inspection view must display the exact label:
    **`◈ WHY IS THIS IMPORTANT?`**
  - **In-Flight Loading State Label:** While an inquiry is actively executing, the button must transition to a disabled state to prevent duplicate submissions and display a clear active indicator:
    **`◈ EXPLAINING...`** (or **`◈ INQUIRING...`**)
  - **Edge Inspection Exclusion:** When inspecting a directional relationship edge rather than a node, the edge inspection view continues to display source/target entity cards and edge provenance without rendering a node-level inquiry button, until the user clicks either the source or target entity card to inspect that node.

### 3.2 Interaction Workflow
* **Inputs:** User click on **`"◈ WHY IS THIS IMPORTANT?"`** inside the left-hand node inspection panel.
* **Desired Outcomes:**
  1. **Automatic Assistant Drawer Activation:** If the right-hand **Medical Durable Goods Assistant** drawer is currently closed, it must immediately open while the left-hand inspection panel remains open and docked on the left margin.
  2. **Anchor Seeding:** The currently inspected node (`primary_key`, `label`, and display name) must be bound as the active seeded anchor for the inquiry so that subgraph retrieval centers deterministically on that node.
  3. **Unified Inquiry Dispatch:** The unified importance prompt for the selected node must immediately appear as a user message in the assistant conversation history and be transmitted to the backend GraphRAG query endpoint.
  4. **Bidirectional Canvas Illumination:** Upon receiving the assistant's response, all cited nodes and traversed lineage edges must illuminate on the center canvas while non-participating background elements dim.

---

## 4. Elimination of Hardcoded Category Prompts & Unified Inquiry Prompt Contract

### 4.1 Removal of Per-Category Hardcoded Prompt Branches
* **Current Context:** Node inquiry generation previously relied on 17 separate hardcoded prompt templates branched by entity category (`Policy`, `Bill`, `PublicLaw`, `StatutorySection`, `USCSection`, `Regulation`, `CFRSection`, `Transmittal`, `CoveragePolicy`, `DiagnosisCode`, `ProcedureCode`, `FeeScheduleRate`, `Jurisdiction`, `State`, `LobbyingFiling`, `CBOScore`, `LiteratureStudy`).
* **Desired Behavior & Outcomes:**
  - All 17 category-specific hardcoded prompt strings for node inquiry generation must be **completely removed**.
  - The system must not maintain separate hardcoded question wording per entity label when constructing the `"◈ WHY IS THIS IMPORTANT?"` inquiry.

### 4.2 Unified Node Importance Inquiry Prompt
* **Inputs:**
  - Selected node's unique identifier (`primary_key`, e.g., `PLAW-117-328`, `TR-CR13286`, `HCPCS-A6522`, `DME-MAC-COPE147943`).
  - Selected node's resolved human-readable name (derived deterministically from the node's display name or primary title/citation attribute, falling back to `primary_key` only if no distinct title attribute exists).
* **Desired Output Format:**
  - Regardless of which of the 17 entity categories the node belongs to, clicking `"◈ WHY IS THIS IMPORTANT?"` must construct a single, consistent, straightforward inquiry prompt:
    - When the resolved display name differs from `primary_key`:
      **`"Why is [${primary_key}] (${name}) important, and what is its role in this policy lineage?"`**
    - When the resolved display name is identical to `primary_key`:
      **`"Why is [${primary_key}] important, and what is its role in this policy lineage?"`**
* **Key Guarantees:**
  - The prompt always includes the exact bracketed identifier `[${primary_key}]` so deterministic entity linking and anchor resolution succeed with 100% precision.
  - The prompt directly reflects the user's intent when clicking `"◈ WHY IS THIS IMPORTANT?"`, ensuring the chat transcript reads naturally and coherently.

### 4.3 Streamlined Quick-Prompt Suggestions in the Assistant Drawer
* **Context:** The top bar of the Medical Durable Goods Assistant drawer displays clickable quick-prompt chips that update when a node is selected on the canvas.
* **Desired Behavior & Outcomes:**
  - Replace the multi-branch per-category hardcoded quick-prompt switch table upon node selection with a clean, universal set of node-aware quick prompts that work uniformly across any selected entity `[${primary_key}]` (`${name}`), such as:
    1. `"Why is [${primary_key}] (${name}) important, and what is its role in this policy lineage?"`
    2. `"How does [${primary_key}] connect to patient coverage and reimbursement?"`
    3. `"What upstream laws and downstream policies are linked to [${primary_key}]?"`
  - When no node is selected (initial boot or after clearing selection), the default general quick prompts remain available so users can immediately test end-to-end lineage queries.

---

## 5. Straightforward Node Explanation Synthesis Requirements

### 5.1 Plain-Language Clarity Paired with Strict Topological Grounding
* **Objective:** When the user asks why a node is important (or submits any inquiry to the Medical Durable Goods Assistant), the assistant's synthesized response must be immediately understandable to a human reader while retaining full evidentiary rigor.
* **Desired Behavior & Outcomes:**
  1. **Direct, Straightforward Opening Explanation:**
     - The assistant must begin by clearly and concisely explaining **what the queried entity is** and **why it is important** within the legislative-to-administrative chain (for example, explaining that a Public Law establishes Congress's binding statutory mandate, that a CMS Transmittal operationalizes billing instructions for regional contractors, or that an HCPCS code identifies the specific medical item eligible for Medicare reimbursement).
  2. **Explicit Upstream & Downstream Lineage Context:**
     - The explanation must describe how the queried node connects to its immediate and multi-hop neighbors present in the assembled graph context—tracing how authority flows from Congressional legislation (`Bill`, `PublicLaw`, `StatutorySection`, `USCSection`) through agency rulemaking (`Regulation`, `CFRSection`, `Transmittal`) to regional contractor administration (`CoveragePolicy`, `Jurisdiction`, `State`) and clinical/financial execution (`DiagnosisCode`, `ProcedureCode`, `FeeScheduleRate`), or how evidentiary nodes (`LiteratureStudy`, `CBOScore`, `LobbyingFiling`) inform that lineage.
  3. **Mandatory Bracketed Primary-Key Citations (`[PRIMARY_KEY]`):**
     - Every graph entity referenced in the explanation must include its exact bracketed primary key from the context (e.g., `[POLICY-LTA]`, `[PLAW-117-328]`, `[TR-CR13286]`, `[DME-MAC-COPE147943]`, `[JURIS-DME-B]`, `[HCPCS-A6522]`, `[ICD10-I97.2]`, `[STATE-WI]`). This guarantees deterministic extraction of active node keys and immediate visual path illumination on the canvas.
  4. **Mandatory Official Legal Citations & Exact Fee/Coinsurance Arithmetic:**
     - Whenever official legal citations (Public Law numbers, U.S. Code sections, Federal Register citations, CFR sections, CMS Transmittal/CR numbers) are present in the context, the assistant must include them accurately.
     - Whenever fee schedule entries are present in the assembled context, the assistant must explicitly report the exact dollar allowable reimbursement rate and calculated 20% patient coinsurance.
  5. **Zero Extrapolation / Fail-Fast Integrity:**
     - The assistant must rely exclusively on the provided graph context, never inventing unverified coverage rules, unlisted procedure codes, or speculative relationships.

---

## 6. Edge Cases & Boundary Conditions

1. **Node With Identical Name and Primary Key:**
   - If a node's display name is identical to its `primary_key` (or its name attribute is empty), the generated prompt must omit redundant parenthetical repetition (producing `"Why is [PRIMARY_KEY] important, and what is its role in this policy lineage?"` rather than `"Why is [PRIMARY_KEY] (PRIMARY_KEY) important..."`).
2. **Rapid Sequential Node Clicks:**
   - Selecting a node on the canvas updates the left inspection panel and seeds the anchor without firing a chat query until the user explicitly clicks `"◈ WHY IS THIS IMPORTANT?"` (or clicks a quick-prompt chip / submits a chat message).
   - While a query is actively loading (`isQueryLoading === true`), the `"◈ WHY IS THIS IMPORTANT?"` button must remain disabled so rapid double-clicks cannot trigger overlapping requests.
3. **Dual-Drawer Coexistence:**
   - Clicking `"◈ WHY IS THIS IMPORTANT?"` in the left-docked inspection drawer opens the right-docked Medical Durable Goods Assistant drawer without closing or shifting the left-docked inspection drawer. Both drawers remain simultaneously visible and operable on opposite margins of the viewport.

---

## 7. Verification & Acceptance Criteria (`{correct required outputs}`)

The specification is satisfied when all of the following verifiable outcomes hold true:

1. **Button Label Verification:**
   - Selecting any node on the canvas opens the left-hand inspection drawer and renders the primary action button with the exact text **`"◈ WHY IS THIS IMPORTANT?"`**.
   - The legacy string `"INQUIRE IN GRAPHRAG CHAT"` does not appear anywhere in the rendered DOM or compiled frontend bundle.
2. **Elimination of Hardcoded Category Prompt Branches:**
   - The 17-case category switch block in the prompt generator is completely removed and replaced by the single unified importance prompt builder.
   - Node-selection quick prompts in the synchronization context no longer use a multi-branch category switch table.
3. **End-to-End Inquiry & Straightforward Explanation Verification:**
   - Clicking `"◈ WHY IS THIS IMPORTANT?"` on any inspected node opens the right-hand **Medical Durable Goods Assistant** drawer, appends `"Why is [<PRIMARY_KEY>] (<NAME>) important, and what is its role in this policy lineage?"` to the chat, and returns a grounded, straightforward explanation citing exact `[PRIMARY_KEY]` identifiers and illuminating the corresponding subgraph on the canvas.
