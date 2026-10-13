# Decision Ticket 003: Multi-Section Structured Context Assembler Specification

**Ticket ID:** `ticket-003.md`  
**Scope:** GraphRAG Stage 3 - Context Assembly (`src/graphrag/context_assembler.py`)  
**Status:** RESOLVED  
**Claimed By:** `wayfinder-read-and-plan`  
**Blocked By:** `ticket-002.md`  

---

## 1. Architectural Question
How must `GraphContextAssembler` format retrieved subgraphs into the five authoritative sections mandated by Section 4.3 of `functional_specification_005.md` without hardcoded fallbacks, dummy values, or state-specific assumptions?

---

## 2. Technical Audit and Empirical Findings

1. **Current Codebase Deficiencies:**
   - In `src/graphrag/context_assembler.py`:
     - Line 28 injects a fallback: `lines.append("- Root Policy: [POLICY-LTA] Lymphedema Treatment Act")` if no Policy node is present.
     - Lines 44-45 inject fallbacks: `contractor = j.properties.get("contractor_name", "CGS Administrators, LLC")` and `states = j.properties.get("states", "WI, IL, IN, KY, MI, MN, OH")`. This misrepresents New York (`JURIS-DME-A`), whose contractor is Noridian Healthcare Solutions.
     - Line 65 injects a hardcoded citation: `42 CFR § 410.36; requires written physician order.`
     - Lines 69-70 hardcode Wisconsin: `state_name = "Wisconsin" if state_code == "WI" else (state_code or "State")`.
     - Section structure currently has only 4 sections instead of the 5 explicit sections mandated by Section 4.3 of the specification.
2. **Empirical Neo4j Node Attributes:**
   - `Jurisdiction` nodes contain `contractor_name` (e.g. `Noridian Healthcare Solutions` for `JURIS-DME-A`, `CGS Administrators, LLC` for `JURIS-DME-B`) and `states` (e.g. `CT, MA, ME, NH, NY, RI, VT` for `JURIS-DME-A`).
   - `FeeScheduleEntry` nodes contain `hcpcs_code`, `state_code`, `fee_amount`, `is_rural`, `year`.
   - `ChangeRequest` nodes contain `transmittal_number` (e.g. `13286`, `13217`) and `benefit_category`.
   - `PublicLaw` nodes contain `name` (e.g. `Public Law 117-328`).
   - `Regulation` nodes contain `name` (e.g. `88 FR 77676, CMS-1784-F`).

---

## 3. Concrete Architectural Decision & Markdown Layout

### 3.1. Elimination of Synthetic Fallbacks
- All fields rendered in the prompt context must derive strictly from the traversed `nodes` and `edges` passed in `TraversalResult`.
- If an entity type is absent from the retrieved subgraph, omit that specific bullet rather than injecting synthetic defaults.

### 3.2. Authoritative Five-Section Assembly Structure
The method `assemble_context(traversal_result: TraversalResult, state_code: Optional[str] = None) -> str` must generate five structured Markdown sections:

#### Section 1: Program Authority
```markdown
### 1. Program & Legal Authority
- Root Policy: [{policy.primary_key}] {policy.name}
- Enacted Public Law: [{plaw.primary_key}] {plaw.name} (e.g., Public Law 117-328)
- Statutory Authority: [{section.primary_key}] {section.name}
- Federal Register Rule: [{reg.primary_key}] {reg.name} (88 FR 77676)
- Operational Change Request: [{cr.primary_key}] Transmittal {cr.transmittal_number} (Benefit Category: {cr.benefit_category})
- Authorizing Coverage Policy: [{cp.primary_key}] {cp.title}
```

#### Section 2: Contractor & Region
```markdown
### 2. Contractor & Region
- Regional Claims Contractor: [{juris.primary_key}] {juris.name} - {juris.contractor_name}
- Covered States / Territory: {juris.states}
- Beneficiary State: [{state.primary_key}] {state.state_name or state.name}
```

#### Section 3: Clinical Criteria
```markdown
### 3. Clinical Criteria
- Permitted Diagnosis: [{diag.primary_key}] ICD-10 {diag.code} - {diag.description}
- Covered Procedure Codes:
  - [{hcpcs.primary_key}] {hcpcs.name} (Description: {hcpcs.description})
```

#### Section 4: Fees and Patient Costs
```markdown
### 4. Fees and Patient Costs ({target_state}, 2024)
- [{fee.primary_key}] HCPCS {fee.hcpcs_code}: Allowable Reimbursement = ${fee.fee_amount:.2f} (Calculated 20% patient coinsurance = ${coinsurance:.2f})
```
- Coinsurance Calculation: `coinsurance = round(float(fee_amount) * 0.20, 2)`.
- If both rural and non-rural fees exist, prioritize non-rural (`is_rural == False`).
- State naming resolves dynamically: use `State` node's `state_name` or `name` property from the retrieved subgraph.

#### Section 5: Data Sources & Provenance
```markdown
### 5. Data Sources & Provenance
- Source Link: {source_uri} (Transmittal / Document: {selector}, Ingestion Run: {run_id}, Timestamp: {ingestion_timestamp})
```
- Extract unique `source_uri` entries from traversed `edges.provenance`.
- Include transmittal references from `ChangeRequest` nodes.
