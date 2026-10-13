# Decision Ticket 002: Deterministic Entity Classification Prompt Construction Engine

**Ticket ID:** `ticket-002.md`  
**Scope:** `src/frontend/src/utils/promptGenerator.ts` & Context Integration  
**Status:** RESOLVED  
**Claimed By:** `wayfinder-read-and-plan`  
**Blocked By:** `ticket-001.md`  
**Taxonomy Reference:** `LANGUAGE.md`

---

## 1. Architectural Question
How must inquiry prompts be deterministically constructed from the selected node's label, primary key, and title to strictly satisfy Section 4.2 and guarantee comprehensive coverage across all 14 knowledge graph entity types?

---

## 2. Root Cause & Architectural Audit

1. **Missing Query Synthesis on Action Trigger:**
   - Currently, no automated prompt construction mechanism exists when an entity is selected.
   - When a user clicks "INQUIRE IN GRAPHRAG CHAT", the input query is left empty, requiring manual user typing.
   - If a user manually types a broad title without quoting the primary key (such as *"Consolidated Appropriations Act, 2023"*), the regex entity linker fails to extract the primary key `PLAW-117-328`, leading to 0 nodes illuminated.

2. **Classification-Specific Semantics:**
   - Different entity types require distinct statutory, regulatory, clinical, or payment questions.
   - A single generic prompt fails to provide relevant context for LLM synthesis.
   - Section 4.2 of `functional_specification_007.md` defines exact templates for key entity types and mandates support across all 14 entity types.

---

## 3. Decision & Technical Specifications

### 3.1. Prompt Construction Utility (`src/frontend/src/utils/promptGenerator.ts`)
- **Symbol:** `constructInquiryPrompt(node: GraphNode): string`
- **Actions:**
  1. Extract and sanitize entity attributes:
     - `primaryKey`: `node.primary_key`
     - `displayName`: `node.name || node.properties?.title || node.properties?.state_name || node.properties?.section || node.primary_key`
  2. Implement exhaustive label mapping conforming to Section 4.2:
     - `PublicLaw`: `"Explain the statutory authority and enacted healthcare provisions of [${primaryKey}] (${displayName})."`
     - `Bill`: `"What is the legislative history and purpose of [${primaryKey}] (${displayName})?"`
     - `Regulation`: `"What policies and administrative instructions are implemented by [${primaryKey}] (${displayName})?"`
     - `CoveragePolicy`: `"What diagnoses and procedure codes are governed by coverage article [${primaryKey}] (${displayName})?"`
     - `ChangeRequest`: `"What operational instructions and benefit categories are mandated by [${primaryKey}] (${displayName})?"`
     - `Jurisdiction`: `"What states and coverage policies are administered by [${primaryKey}] (${displayName})?"`
     - `State`: `"What Medicare contractor, coverage policies, and allowable fee schedules apply to [${primaryKey}] (${displayName})?"`
     - `HCPCSCode`: `"What are the coverage criteria, physician requirements, and allowable rates for [${primaryKey}] (${displayName})?"`
     - `ICD10Code`: `"What coverage policies and durable medical equipment items are authorized for diagnosis [${primaryKey}] (${displayName})?"`
     - `Policy`: `"Explain the legislative, regulatory, and coverage lineage of policy [${primaryKey}] (${displayName})."`
     - `StatutorySection`: `"What statutory obligations and healthcare provisions are codified in [${primaryKey}] (${displayName})?"`
     - `FeeScheduleEntry`: `"What are the allowable reimbursement rates and jurisdictional terms for [${primaryKey}] (${displayName})?"`
     - `LiteratureStudy`: `"What clinical evidence and findings are documented in study [${primaryKey}] (${displayName})?"`
     - `LobbyingFiling`: `"What lobbying activities, clients, and issues are disclosed in filing [${primaryKey}] (${displayName})?"`
     - `Default`: `"Explain the regulatory and operational role of [${primaryKey}] (${displayName})."`
  3. Ensure the bracketed `[${primaryKey}]` token is always included verbatim in the inquiry text.

---

## 4. Acceptance Criteria
1. For every node label, `constructInquiryPrompt(node)` returns the exact template specified in Section 4.2.
2. The bracketed primary key token `[primary_key]` is present in 100% of generated inquiry prompts.
3. All 14 entity types are mapped deterministically with zero unhandled cases.
