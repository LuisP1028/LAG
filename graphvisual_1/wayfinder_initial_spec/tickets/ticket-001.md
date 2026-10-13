# Decision Ticket 001: Entity Anchor Linking and Layperson Vocabulary Normalization Specification

**Ticket ID:** `ticket-001.md`  
**Scope:** GraphRAG Stage 1 - Input Entity Resolution  
**Status:** RESOLVED  
**Claimed By:** `wayfinder-graphrag-spec`  
**Blocked By:** None (Root Decision)

---

## 1. Architectural Question
How must the system deterministically resolve unstructured natural language inputs from real-world patients, clinicians, and researchers (e.g., *"I am from Wisconsin, survived breast cancer, need lymphedema supplies, I'm on Medicare"*) into precise graph entry points without probabilistic guessing or fragile hardcoded regex rules?

---

## 2. Decision and Specification Requirements

### 2.1. Deterministic Multi-Slot Entity Resolution
The system must parse unstructured natural language into three orthogonal domain slots:
1. **Geographic Entity Anchor (`State`):**
   - Matches state names, state abbreviations, and territorial designations against the indexed `State` entities (`STATE-[state_code]`).
   - Example: `"Wisconsin"` $\rightarrow$ `STATE-WI`.
2. **Clinical Indication Anchor (`ICD10Code`):**
   - Maps clinical lay terms and medical histories to formal ICD-10-CM diagnosis codes using indexed lexical matching on `code` and `description`.
   - Examples:
     - `"breast cancer"` + `"lymphedema"` / `"swelling"` $\rightarrow$ `ICD10-I97.2` (*Postmastectomy lymphedema syndrome*).
     - `"primary lymphedema"` / `"born with lymphedema"` $\rightarrow$ `ICD10-Q82.0` (*Hereditary lymphedema*).
     - `"lymphedema"` $\rightarrow$ `ICD10-I89.0` (*Lymphedema, not elsewhere classified*).
     - `"hypogammaglobulinemia"` / `"immune deficiency"` $\rightarrow$ `ICD10-D80.0` / `ICD10-D83.9`.
3. **Policy & Benefit Domain Anchor (`Policy`):**
   - Maps requested items or services to root policy keywords:
     - `"compression sleeve"`, `"lymphedema wrap"`, `"compression garment"` $\rightarrow$ `POLICY-LTA`.
     - `"intravenous immune globulin"`, `"IVIG in-home"`, `"immune infusion"` $\rightarrow$ `POLICY-IVIG`.

### 2.2. Failure & Ambiguity Handling (`INV-FAIL-FAST`)
- If a user prompt contains a geographic entity that cannot be resolved to any of the 54 Medicare states or territories, the resolution stage must immediately report the unrecognized jurisdiction rather than defaulting to an arbitrary state.
- If a prompt specifies a clinical condition with no coverage pathway in the database, the system must report that no authorizing policy article exists in Medicare Part B.
