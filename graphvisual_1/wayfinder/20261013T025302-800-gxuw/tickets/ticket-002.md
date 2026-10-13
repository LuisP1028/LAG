# Decision Ticket 002: Multi-Slot Entity Anchor Resolution and Clinical Synonym Normalization Specification

**Ticket ID:** `ticket-002.md`  
**Scope:** GraphRAG Stage 1: Input Entity Resolution  
**Status:** RESOLVED  
**Claimed By:** `wayfinder-read-and-plan`  
**Blocked By:** `ticket-001.md`

---

## 1. Architectural Question

How must the system deterministically resolve free-form, unstructured natural language patient, clinical, and policy queries (such as *"I am from Wisconsin, survived breast cancer, need lymphedema supplies, I'm on Medicare, can you help?"*) into verified graph entry points without probabilistic guessing or hallucinated entity keys?

---

## 2. Decision and Specification Requirements

### 2.1. Component Location and Interface
- **Module:** `src/graphrag/entity_linker.py`
- **Class:** `EntityAnchorLinker`
- **Primary Function Signature:**
  ```python
  def resolve_anchors(self, query_text: str, session: Session) -> ResolvedAnchors:
      ...
  ```
- **Data Models:**
  ```python
  class AnchorEntity(BaseModel):
      slot: str  # "state" | "diagnosis" | "policy"
      primary_key: str
      matched_text: str
      entity_type: str
      label: str

  class ResolvedAnchors(BaseModel):
      state_anchor: Optional[AnchorEntity] = None
      diagnosis_anchor: Optional[AnchorEntity] = None
      policy_anchor: Optional[AnchorEntity] = None
      all_anchors: List[AnchorEntity] = []
  ```

### 2.2. Deterministic Multi-Slot Extraction Rules

The entity linker inspects query text across three orthogonal semantic slots:

1. **Slot 1: Geographic State Anchor (`State`)**
   - Matches state full names (e.g., `"Wisconsin"`, `"wisconsin"`) or state 2-letter postal codes (e.g., `"WI"`, `"in WI"`, `"from WI"`) against the 54 valid Medicare jurisdictions (`State` nodes).
   - Validates existence against `(s:State {primary_key: $pk})` in Neo4j.
   - Deterministic Key Format: `STATE-{UPPER_TWO_LETTER_CODE}` (e.g., `STATE-WI`).

2. **Slot 2: Clinical Indication Anchor (`ICD10Code`)**
   - Resolves clinical terminology through a deterministic synonym map backed by indexed exact match queries on `ICD10Code.code` and `ICD10Code.description`:
     - `"breast cancer"` + (`"lymphedema"` | `"swelling"` | `"arm swelling"`) $\rightarrow$ `ICD10-I97.2` (*Postmastectomy lymphedema syndrome*)
     - (`"hereditary lymphedema"` | `"primary lymphedema"` | `"born with lymphedema"` | `"milroy"`) $\rightarrow$ `ICD10-Q82.0` (*Hereditary lymphedema*)
     - (`"lymphedema"` | `"swollen limb"` | `"leg lymphedema"`) $\rightarrow$ `ICD10-I89.0` (*Lymphedema, not elsewhere classified*)
     - (`"hypogammaglobulinemia"` | `"hereditary hypogammaglobulinemia"`) $\rightarrow$ `ICD10-D80.0`
     - (`"common variable immunodeficiency"` | `"CVID"` | `"immune deficiency"`) $\rightarrow$ `ICD10-D83.9`
   - Deterministic Key Format: `ICD10-{CODE}` (e.g., `ICD10-I97.2`).

3. **Slot 3: Policy Domain Anchor (`Policy`)**
   - Maps requested clinical supplies or program keywords to root policy nodes:
     - (`"lymphedema supplies"` | `"compression sleeve"` | `"compression garment"` | `"daytime sleeve"` | `"nighttime wrap"` | `"LTA"`) $\rightarrow$ `POLICY-LTA`
     - (`"IVIG"` | `"intravenous immune globulin"` | `"immune globulin"` | `"in-home infusion"`) $\rightarrow$ `POLICY-IVIG`
   - Deterministic Key Format: `POLICY-{KEYWORD}` (e.g., `POLICY-LTA`).

### 2.3. Empirical Resolution Validation
For the patient prompt:
> *"I am from Wisconsin, survived breast cancer, need lymphedema supplies, I'm on Medicare, can you help?"*
The linker emits:
```json
{
  "state_anchor": {
    "slot": "state",
    "primary_key": "STATE-WI",
    "matched_text": "Wisconsin",
    "entity_type": "State",
    "label": "State"
  },
  "diagnosis_anchor": {
    "slot": "diagnosis",
    "primary_key": "ICD10-I97.2",
    "matched_text": "breast cancer ... lymphedema",
    "entity_type": "ICD10Code",
    "label": "ICD10Code"
  },
  "policy_anchor": {
    "slot": "policy",
    "primary_key": "POLICY-LTA",
    "matched_text": "lymphedema supplies",
    "entity_type": "Policy",
    "label": "Policy"
  }
}
```

### 2.4. Fail-Fast Error Boundaries (`INV-FAIL-FAST`)
- If the user provides a geographic location that cannot be matched to any of the 54 states/territories in Neo4j, the linker immediately raises `EntityResolutionError(f"Unrecognized geographic jurisdiction '{extracted_geo}'.")`.
- If the user specifies a medical condition that does not resolve to an indexed ICD-10 diagnosis code or has zero coverage policies in the database, the linker raises `EntityResolutionError(f"No authorized Medicare coverage policy found for condition '{extracted_condition}'.")`.
- Under no circumstances may the system default to an arbitrary state (e.g., defaulting to DC or California) or an arbitrary code.
