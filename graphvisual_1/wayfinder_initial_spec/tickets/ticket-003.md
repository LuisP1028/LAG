# Decision Ticket 003: Factual Context Assembly, Edge Provenance Formatting, and Prompt Grounding Specification

**Ticket ID:** `ticket-003.md`  
**Scope:** GraphRAG Stage 3 - Context Synthesis & Grounding  
**Status:** RESOLVED  
**Claimed By:** `wayfinder-graphrag-spec`  
**Blocked By:** `ticket-002.md`

---

## 1. Architectural Question
How must the retrieved subgraph and its provenance metadata be transformed into prompt context for Hugging Face open-weight instruction models to ensure 100% grounded answers, zero hallucination of payment rates or legal rules, and clear citations to primary sources?

---

## 2. Decision and Specification Requirements

### 2.1. Deterministic Factual Serialization Format
The retrieved nodes and relationships must be formatted into clean, structured Markdown/triple statements before injection into the prompt:
1. **Administrative Authority Block:**
   ```markdown
   - Program Authority: Medicare Part B DMEPOS
   - Authorizing Policy Article: [CMS-MCD-A59508] "Standard Documentation Requirements for Lymphedema Compression Treatment Items"
   - Operational Transmittal: [CMS-CR-13286] Transmittal 12349
   - Regional Claims Contractor: [JURIS-DME-B] CGS Administrators (Covers: Wisconsin, Illinois, Indiana, Kentucky, Michigan, Minnesota, Ohio)
   ```
2. **Clinical Eligibility Block:**
   ```markdown
   - Authorized Diagnosis: [ICD10-I97.2] Postmastectomy lymphedema syndrome
   - Legal Authority: Governed under 42 CFR § 410.36; requires written physician prescription specifying compression rating.
   ```
3. **Reimbursement & Covered Items Block:**
   ```markdown
   - Covered Items Available in Wisconsin: 70 procedure codes governed by Article A59508
   - Sample Items & Allowable Fees (Wisconsin, Year 2024):
     * [HCPCS-A6520] Glove nighttime: Allowable Fee = $119.54 (Patient 20% coinsurance = $23.91)
     * [HCPCS-A6522] Arm sleeve nighttime: Allowable Fee = $290.47 (Patient 20% coinsurance = $58.09)
     * [HCPCS-A6583] Arm sleeve custom daytime: Allowable Fee = $44.15 (Patient 20% coinsurance = $8.83)
   ```
4. **Mandatory Provenance Citations (`INV-PROVENANCE-COMPLETENESS`):**
   Every block must append direct pointers to the verified primary source payloads:
   - Source: `stage4a_cms_mcd_a59508_web_probe.html`
   - Source: `stage4b_cms_dmepos_lc_category.csv`
   - Source: `stage3_federal_register_rule_2023_24455.json`

### 2.2. Strict Anti-Hallucination Guardrails (`INV-FAIL-FAST`)
- The system prompt must instruct the model: *"You are an authoritative Medicare policy information assistant. Every statement regarding coverage, allowed codes, contractor names, and dollar rates must be derived strictly from the provided factual blocks. Do not extrapolate unlisted payment amounts or invent coverage rules."*
- If the factual context contains no allowable fee for a specific item/state pair, the model must explicitly state that no fee schedule rate is published for that combination.
