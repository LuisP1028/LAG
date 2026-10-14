# Ticket 004: 8-Hop Subgraph Traversal, Agnostic Context Synthesis, and Grounded Prompt Alignment

## 1. Objective & Scope
Align the GraphRAG topological traversal engine (`src/graphrag/traversal.py`), structured context assembler (`src/graphrag/context_assembler.py`), and grounded LLM synthesizer (`src/graphrag/synthesizer.py`) with the 8-hop knowledge graph ontology (`17` entity labels and `18` relationship types), removing all obsolete shortcut relationships (`TARGETS_BILL`, `MODIFIES_CODE`, `ISSUES_TRANSMITTAL`, `GOVERNS`, `ALLOWS_DIAGNOSIS`, `HAS_FEE_SCHEDULE`, `APPLIES_TO`), obsolete node labels (`ChangeRequest`, `HCPCSCode`, `ICD10Code`, `FeeScheduleEntry`), and static fallback citations (`"Lymphedema Treatment Act"`, `"Public Law 117-328"`, `"42 U.S.C. 1395x"`, `"88 FR 77676, CMS-1784-F"`, `"Standard Documentation Requirements"`).

---

## 2. Current Implementation Defects (Grounded in Codebase Audit)

### 2.1 `src/graphrag/traversal.py`
1. **Obsolete Relationship and Node Labels Across All Traversal Methods:**
   - `_execute_single_entity_traversal` (line 105): Checks `anchor.label in ("HCPCSCode", "ICD10Code")` instead of `("ProcedureCode", "DiagnosisCode", "HCPCSCode", "ICD10Code")`.
   - `_execute_jurisdiction_traversal` (lines 134–145): Queries `(cr:ChangeRequest)-[r2:APPLIES_TO_JURISDICTION]->(j)`, `(reg:Regulation)-[r4:ISSUES_TRANSMITTAL]->(cr)`, `(sec:StatutorySection)-[r5:IMPLEMENTED_BY]->(reg)`, `(pl:PublicLaw)-[r6:MODIFIES_CODE]->(sec)`, and `(p:Policy)-[r7:TARGETS_BILL]->(b:Bill)-[r8:ENACTED_AS]->(pl)`. None of `ChangeRequest`, `ISSUES_TRANSMITTAL`, `MODIFIES_CODE`, `TARGETS_BILL`, or direct standalone-bill `ENACTED_AS` exist in the 8-hop graph.
   - `_execute_single_state_traversal` (lines 191–201, 261–295): Queries `(cr:ChangeRequest)-[r3:MANDATES_POLICY]->(cp:CoveragePolicy)` and `(cp)-[r4:GOVERNS]->(h:HCPCSCode)-[r5:HAS_FEE_SCHEDULE]->(f:FeeScheduleEntry)-[r6:APPLIES_TO]->(s)`, and builds `active_edge_keys` using `GOVERNS`, `HAS_FEE_SCHEDULE`, and `APPLIES_TO` instead of `COVERS_PROCEDURE`, `HAS_RATE`, and `APPLIES_TO_STATE`. Also omits the rural fee schedule node (`is_rural = true`) from `fee_list`, preventing `GraphContextAssembler` from reporting both rural and non-rural rates when present.
   - `_execute_single_clinical_traversal` (lines 307–315): Queries `GOVERNS`, `HCPCSCode`, `ALLOWS_DIAGNOSIS`, `ICD10Code`, and `ChangeRequest` instead of `COVERS_PROCEDURE`, `ProcedureCode`, `REQUIRES_DIAGNOSIS`, `DiagnosisCode`, and `Transmittal` plus upstream legal lineage (`CFRSection`, `Regulation`, `USCSection`, `StatutorySection`, `PublicLaw`, `Bill`, `Policy`).
   - `_execute_single_general_traversal` (lines 355–364): Filters `WHERE NOT m:FeeScheduleEntry` instead of `WHERE NOT m:FeeScheduleRate` and only traverses 1 hop instead of capturing the 8-hop legal/regulatory/clinical lineage for legislative, statutory, regulatory, transmittal, coverage, or contextual anchors.
   - `_execute_multi_entity_traversal` (lines 396–399, 472–477): Checks `a.label == "HCPCSCode"` instead of `a.label in ("ProcedureCode", "HCPCSCode")` and increases shortest-path hop bound only to `*..6` instead of `*..10` for the 8-hop chain.
   - `_execute_pattern_a` (lines 507–517, 609–621): Queries `ChangeRequest`, `ALLOWS_DIAGNOSIS`, `ICD10Code`, `GOVERNS`, `HCPCSCode`, `HAS_FEE_SCHEDULE`, `FeeScheduleEntry`, `APPLIES_TO`, and omits upstream legal authority (`Policy` $\to$ `Bill` $\to$ `Bill` $\to$ `PublicLaw` $\to$ `StatutorySection` $\to$ `USCSection` $\to$ `Regulation` $\to$ `CFRSection` $\to$ `Transmittal`).
   - `_execute_pattern_b` (lines 633–679): Queries `HCPCSCode`, `GOVERNS`, `ALLOWS_DIAGNOSIS`, `ICD10Code`, `ChangeRequest` instead of `ProcedureCode`, `COVERS_PROCEDURE`, `REQUIRES_DIAGNOSIS`, `DiagnosisCode`, `Transmittal`, and upstream legal lineage.
   - `_execute_pattern_c` (lines 690–730): Queries `TARGETS_BILL`, direct `ENACTED_AS`, `MODIFIES_CODE`, `IMPLEMENTED_BY`, `ISSUES_TRANSMITTAL`, `ChangeRequest` instead of the 8-hop legislative/statutory/regulatory/transmittal chain (`DISCOVERED_BILL`, `INCORPORATED_INTO`, `ENACTED_AS`, `CONTAINS`, `AMENDS`, `AUTHORIZED_BY`, `CODIFIED_IN`, `IMPLEMENTED_BY`, `Transmittal`).
   - `_convert_node` (lines 731–770): Maps prefixes to legacy labels (`CMS-CR-` $\to$ `ChangeRequest`, `FEE-` $\to$ `FeeScheduleEntry`, `HCPCS-` $\to$ `HCPCSCode`, `ICD10-` $\to$ `ICD10Code`, `FR-` $\to$ `Regulation`, `USC-` $\to$ `StatutorySection`), lacks `STAT-`, `REG-FR-`, `CFR-`, `TR-CR`, `DME-MAC-`, `CBO-`, and derives `name` via `props.get("name") or props.get("state_name") or props.get("section") or props.get("title") or pk` which falls back to raw `pk` for `Policy`, `PublicLaw`, `StatutorySection`, `USCSection`, `Regulation`, `CFRSection`, `Transmittal`, `DiagnosisCode`, `ProcedureCode`, `FeeScheduleRate`, `Jurisdiction`, and `CBOScore`.
   - `_convert_edge` (lines 772–800): Injects hardcoded synthetic provenance defaults (`"verified://federal-statute"`, `"2026-10-13T01:23:54Z"`, `"export-run-001"`) instead of reading persisted relationship attributes directly.

### 2.2 `src/graphrag/context_assembler.py`
1. **Static Fallback Strings & Missing 8-Hop Entity Categories in Section 1 (`lines 48–92`):**
   - Uses hardcoded fallbacks `"Lymphedema Treatment Act"`, `"Public Law 117-328"`, `"Consolidated Appropriations Act, 2023"`, `"42 U.S.C. 1395x"`, `"88 FR 77676, CMS-1784-F"`, and `"Standard Documentation Requirements"`.
   - Checks `n.label == "ChangeRequest"` instead of `"Transmittal"`.
   - Completely omits `USCSection` (`USC-...`), `CFRSection` (`CFR-...`), and `CBOScore` (`CBO-...`) nodes, and omits rich persisted properties on `Policy` (`policy_keyword`), `Bill` (`congress`, `bill_type`, `bill_number`, `title`, `introduced_date`, and `INCORPORATED_INTO` omnibus link), `PublicLaw` (`public_law_number`, `title`, `enactment_date`), `StatutorySection` (`section_number`, `section_heading`, `text_excerpt`, `effective_date`), `USCSection` (`citation`, `title_number`, `section_code`, `subsections`), `Regulation` (`document_number`, `citation`, `docket_id`, `rin`, `title`, `effective_date`, `cfr_parts`), `CFRSection` (`citation`, `title_number`, `part_number`, `section_title`), `Transmittal` (`cr_number`, `transmittal_number`, `manual_publication`, `benefit_category_code`, `pricing_indicator_code`, `betos_code`, `effective_date`), and `CoveragePolicy` (`article_id`, `publication_type`, `title`, `effective_date`, `clinical_prerequisites`).
2. **Legacy Labels & Missing Metadata in Section 3 (`lines 147–175`):**
   - Checks `n.label == "ICD10Code"` instead of `n.label in ("DiagnosisCode", "ICD10Code")` and `n.label == "HCPCSCode"` instead of `n.label in ("ProcedureCode", "HCPCSCode")`.
   - Does not output `ProcedureCode` properties required by Section 3.3 of `functional_specification_015.md`: `short_description`, `long_description`, `benefit_category`, `betos_code`, `pricing_indicator`, `pricing_methodology` (`NATIONAL_FEE_SCHEDULE` or `LOCAL_CONTRACTOR_PRICING`), and `is_custom_or_nos`.
3. **Legacy Labels & Missing Rural/Local-Contractor Details in Section 4 (`lines 178–221`):**
   - Checks `n.label == "FeeScheduleEntry"` instead of `n.label in ("FeeScheduleRate", "FeeScheduleEntry")`.
   - Hardcodes `(..., 2024)` in the section header instead of reading `schedule_year` from persisted `FeeScheduleRate` nodes.
   - Filters out rural rates (`non_rural_fees = [f for f in fees if not f.properties.get("is_rural")]`) instead of reporting both state-specific non-rural and rural allowable rates with 20% patient coinsurance (`ceiling`, `floor`, `is_rural`, `pricing_methodology`), and fails to note `ProcedureCode` nodes subject to `LOCAL_CONTRACTOR_PRICING` (`pricing_indicator=46`).
4. **Hardcoded Fallback Timestamps in Section 5 (`lines 224–237`):**
   - Uses fallback strings `"2026-10-13T01:23:54Z"` and `"export-run-001"` when formatting edge provenance.

### 2.3 `src/graphrag/synthesizer.py`
1. **Legacy Primary Key Prefixes in `SYSTEM_PROMPT` and `user_content` (`lines 30–39, 68–74`):**
   - `SYSTEM_PROMPT` rule 2 cites `[CMS-MCD-A59508]` and `[CMS-CR-13286]`, which do not exist in the 8-hop graph (`[DME-MAC-COPE147943]` and `[TR-CR13286]` are the persisted keys).
   - `SYSTEM_PROMPT` rule 4 hardcodes `CMS-1784-F` instead of referencing the Federal Register citation and RIN/docket present in the context.

---

## 3. Target Architecture & Exact File Edits

### 3.1 `src/graphrag/traversal.py`

#### A. Shared Upstream Legal Lineage Helper (`_ingest_upstream_legal_lineage`)
Add a helper method `_ingest_upstream_legal_lineage(self, session, nodes_by_pk, edges_by_key, active_node_pks, active_edge_keys)` that traverses and ingests the upstream 8-hop legal and regulatory spine connected to any `Transmittal` or `CoveragePolicy` in `nodes_by_pk`:
```cypher
MATCH (tr:Transmittal)
WHERE tr.primary_key IN $tr_pks
OPTIONAL MATCH (cfr:CFRSection)-[r_impl:IMPLEMENTED_BY]->(tr)
OPTIONAL MATCH (reg:Regulation)-[r_cod:CODIFIED_IN]->(cfr)
OPTIONAL MATCH (usc:USCSection)<-[r_auth:AUTHORIZED_BY]-(reg)
OPTIONAL MATCH (stat:StatutorySection)-[r_amends:AMENDS]->(usc)
OPTIONAL MATCH (pl:PublicLaw)-[r_cont:CONTAINS]->(stat)
OPTIONAL MATCH (b_enacted:Bill)-[r_enacted:ENACTED_AS]->(pl)
OPTIONAL MATCH (b_intro:Bill)-[r_inc:INCORPORATED_INTO]->(b_enacted)
OPTIONAL MATCH (p:Policy)-[r_disc1:DISCOVERED_BILL]->(b_intro)
OPTIONAL MATCH (p2:Policy)-[r_disc2:DISCOVERED_BILL]->(b_enacted)
OPTIONAL MATCH (b_intro)-[r_cbo:HAS_BUDGET_IMPACT]->(cbo:CBOScore)
OPTIONAL MATCH (b_intro)-[r_lda:HAS_ADVOCACY_RECORD]->(lda:LobbyingFiling)
OPTIONAL MATCH (cp:CoveragePolicy)-[r_pub:SUPPORTED_BY_EVIDENCE]->(pub:LiteratureStudy)
WHERE cp.primary_key IN $cp_pks
RETURN tr, cfr, r_impl, reg, r_cod, usc, r_auth, stat, r_amends, pl, r_cont,
       b_enacted, r_enacted, b_intro, r_inc, p, r_disc1, p2, r_disc2,
       cbo, r_cbo, lda, r_lda, cp, pub, r_pub
```
All matched nodes (`Policy`, `Bill`, `PublicLaw`, `StatutorySection`, `USCSection`, `Regulation`, `CFRSection`, `Transmittal`, `CBOScore`, `LobbyingFiling`, `LiteratureStudy`) and their connecting edges (`DISCOVERED_BILL`, `INCORPORATED_INTO`, `ENACTED_AS`, `CONTAINS`, `AMENDS`, `AUTHORIZED_BY`, `CODIFIED_IN`, `IMPLEMENTED_BY`, `HAS_BUDGET_IMPACT`, `HAS_ADVOCACY_RECORD`, `SUPPORTED_BY_EVIDENCE`) are converted via `_convert_node` and `_convert_edge` and added to `nodes_by_pk`, `edges_by_key`, `active_node_pks`, and `active_edge_keys`.

#### B. Rewrite Traversal Queries for 8-Hop Schema
1. **`_execute_single_entity_traversal` (lines 77–123):**
   - Dispatch `anchor.slot in ("diagnosis", "icd10code", "hcpcs", "hcpcscode") or anchor.label in ("ProcedureCode", "DiagnosisCode", "HCPCSCode", "ICD10Code")` to `_execute_single_clinical_traversal`.
2. **`_execute_jurisdiction_traversal` (lines 124–179):**
   - Query:
     ```cypher
     MATCH (j:Jurisdiction)
     WHERE j.primary_key IN $juris_pks
     OPTIONAL MATCH (j)-[r1:COVERS_STATE]->(s:State)
     OPTIONAL MATCH (tr:Transmittal)-[r2:APPLIES_TO_JURISDICTION]->(j)
     OPTIONAL MATCH (tr)-[r3:MANDATES_POLICY]->(cp:CoveragePolicy)
     RETURN j, r1, s, tr, r2, cp, r3
     ```
   - After ingesting `j`, `s`, `tr`, `cp` and `r1`, `r2`, `r3`, invoke `self._ingest_upstream_legal_lineage(...)` so the full legal authority chain (`Policy` $\to$ `Bill` $\to$ `PublicLaw` $\to$ `StatutorySection` $\to$ `USCSection` $\to$ `Regulation` $\to$ `CFRSection` $\to$ `Transmittal` $\to$ `CoveragePolicy`) is included.
3. **`_execute_single_state_traversal` (lines 180–296):**
   - Query:
     ```cypher
     MATCH (s:State {primary_key: $state_pk})<-[r1:COVERS_STATE]-(j:Jurisdiction)<-[r2:APPLIES_TO_JURISDICTION]-(tr:Transmittal)-[r3:MANDATES_POLICY]->(cp:CoveragePolicy)
     OPTIONAL MATCH (cp)-[r4:COVERS_PROCEDURE]->(h:ProcedureCode)
     OPTIONAL MATCH (h)-[r5:HAS_RATE]->(f:FeeScheduleRate)-[r6:APPLIES_TO_STATE]->(s)
     OPTIONAL MATCH (cp)-[r7:REQUIRES_DIAGNOSIS]->(d:DiagnosisCode)
     RETURN s, r1, j, r2, tr, r3, cp,
            collect(DISTINCT h) AS hcpcs_list,
            collect(DISTINCT f) AS fee_list,
            collect(DISTINCT d) AS diag_list,
            collect(DISTINCT r4) AS r4_list,
            collect(DISTINCT r5) AS r5_list,
            collect(DISTINCT r6) AS r6_list,
            collect(DISTINCT r7) AS r7_list
     ```
   - Notice `OPTIONAL MATCH (h)-[r5:HAS_RATE]->(f:FeeScheduleRate)-[r6:APPLIES_TO_STATE]->(s)` is separate from `OPTIONAL MATCH (cp)-[r4:COVERS_PROCEDURE]->(h:ProcedureCode)` so that `ProcedureCode` nodes with `LOCAL_CONTRACTOR_PRICING` (which have no `FeeScheduleRate` nodes) are still returned in `hcpcs_list`, and both rural (`is_rural = true`) and non-rural (`is_rural = false`) `FeeScheduleRate` nodes are returned in `fee_list`.
   - Use `COVERS_PROCEDURE`, `HAS_RATE`, and `APPLIES_TO_STATE` when constructing `active_edge_keys`.
   - Call `self._ingest_upstream_legal_lineage(...)` to include the upstream legal chain.
4. **`_execute_single_clinical_traversal` (lines 297–344):**
   - Query:
     ```cypher
     MATCH (n:PolicyNode {primary_key: $anchor_pk})
     OPTIONAL MATCH (cp:CoveragePolicy)-[r1:COVERS_PROCEDURE]->(h:ProcedureCode)
     WHERE n = h OR n = cp
     OPTIONAL MATCH (cp)-[r2:REQUIRES_DIAGNOSIS]->(d:DiagnosisCode)
     WHERE n = d OR n = cp
     OPTIONAL MATCH (tr:Transmittal)-[r3:MANDATES_POLICY]->(cp)
     RETURN n, cp, h, d, tr, r1, r2, r3
     ```
   - Call `self._ingest_upstream_legal_lineage(...)` so queries about a procedure code, diagnosis code, or coverage policy include the full legal authority chain.
5. **`_execute_single_general_traversal` (lines 345–385):**
   - Query the 1-to-8 hop non-rate neighborhood for any legislative, statutory, regulatory, transmittal, fee, or contextual anchor:
     ```cypher
     MATCH (n:PolicyNode {primary_key: $anchor_pk})
     OPTIONAL MATCH path = (n)-[*1..8]-(m:PolicyNode)
     WHERE ALL(node IN nodes(path) WHERE NOT node:FeeScheduleRate OR node = n)
     RETURN n, path
     LIMIT 100
     ```
   - Ingest `n` and all nodes and relationships along `path` into `nodes_by_pk`, `edges_by_key`, `active_node_pks`, and `active_edge_keys`.
6. **`_execute_pattern_a` (lines 493–622):**
   - Query:
     ```cypher
     MATCH (s:State {primary_key: $state_pk})<-[r1:COVERS_STATE]-(j:Jurisdiction)<-[r2:APPLIES_TO_JURISDICTION]-(tr:Transmittal)-[r3:MANDATES_POLICY]->(cp:CoveragePolicy)-[r4:REQUIRES_DIAGNOSIS]->(d:DiagnosisCode {primary_key: $diag_pk})
     OPTIONAL MATCH (cp)-[r5:COVERS_PROCEDURE]->(h:ProcedureCode)
     OPTIONAL MATCH (h)-[r6:HAS_RATE]->(f:FeeScheduleRate)-[r7:APPLIES_TO_STATE]->(s)
     RETURN s, r1, j, r2, tr, r3, cp, r4, d,
            collect(DISTINCT h) AS hcpcs_list,
            collect(DISTINCT f) AS fee_list,
            collect(DISTINCT r5) AS r5_list,
            collect(DISTINCT r6) AS r6_list,
            collect(DISTINCT r7) AS r7_list
     ```
   - Populate `active_chain_edges` using `COVERS_STATE`, `APPLIES_TO_JURISDICTION`, `MANDATES_POLICY`, `REQUIRES_DIAGNOSIS`, `COVERS_PROCEDURE`, `HAS_RATE`, and `APPLIES_TO_STATE`.
   - Call `self._ingest_upstream_legal_lineage(...)` to include the upstream legal chain.
7. **`_execute_pattern_b` (lines 623–679):**
   - Replace `HCPCSCode`, `GOVERNS`, `ALLOWS_DIAGNOSIS`, `ICD10Code`, `ChangeRequest` with `ProcedureCode`, `COVERS_PROCEDURE`, `REQUIRES_DIAGNOSIS`, `DiagnosisCode`, `Transmittal`, and call `self._ingest_upstream_legal_lineage(...)`.
8. **`_execute_pattern_c` (lines 680–730):**
   - Traverse the 8-hop path from `p1:Policy` and `p2:Policy` through `DISCOVERED_BILL` $\to$ `INCORPORATED_INTO*0..1` $\to$ `ENACTED_AS` $\to$ `PublicLaw` $\to$ `CONTAINS` $\to$ `StatutorySection` $\to$ `AMENDS` $\to$ `USCSection` $\leftarrow$ `AUTHORIZED_BY` $-$ `Regulation` $\to$ `CODIFIED_IN` $\to$ `CFRSection` $\to$ `IMPLEMENTED_BY` $\to$ `Transmittal` $\to$ `MANDATES_POLICY` $\to$ `CoveragePolicy`.
9. **`_convert_node` (lines 731–770) & `_convert_edge` (lines 772–800):**
   - Update `_convert_node` prefix fallback and display name derivation using `derive_node_display_name(label, props)` from `src/api/routes.py` (or identical 17-label derivation logic) so every `TraversalNode.name` is a human-readable string derived from persisted attributes.
   - Update `_convert_edge` to read `source_uri`, `selector`, `ingestion_timestamp`, and `run_id` directly from `props` without hardcoded synthetic default timestamps or URIs.

---

### 3.2 `src/graphrag/context_assembler.py`

Rewrite `GraphContextAssembler.assemble_context` so all 5 sections are synthesized exclusively from persisted node and edge properties without static fallback strings:
1. **`### 1. Program & Legal Authority`:**
   - **Policy (`Policy`):** `- Root Policy: [{p.primary_key}] {p.name} (Keyword: {policy_keyword}, Run ID: {run_id})`
   - **Bills (`Bill`):** `- Bill: [{b.primary_key}] {congress}th Congress {bill_type} {bill_number} - {title} (Introduced: {introduced_date})` plus any `INCORPORATED_INTO` omnibus relationship (`[{src}] incorporated into [{tgt}]`).
   - **Public Laws (`PublicLaw`):** `- Enacted Public Law: [{pl.primary_key}] Public Law {public_law_number} - {title} (Enacted: {enactment_date})`
   - **Statutory Sections (`StatutorySection`):** `- Statutory Section: [{sec.primary_key}] Section {section_number} ({section_heading}) — Effective: {effective_date} — Excerpt: {text_excerpt}`
   - **U.S. Code Sections (`USCSection`):** `- Amended U.S. Code: [{usc.primary_key}] {citation} (Subsections: {', '.join(subsections)})`
   - **Federal Register Rules (`Regulation`):** `- Federal Register Final Rule: [{reg.primary_key}] {citation} (Document: {document_number}, Docket: {docket_id}, RIN: {rin}) - {title} (Effective: {effective_date}, Affected CFR Parts: {', '.join(cfr_parts)})`
   - **CFR Sections (`CFRSection`):** `- Codified CFR Section: [{cfr.primary_key}] {citation} - {section_title}`
   - **Transmittals (`Transmittal`):** `- CMS Transmittal: [{tr.primary_key}] CR {cr_number} / Transmittal {transmittal_number} (Manual: {manual_publication}, Benefit Category: {benefit_category_code}, Pricing Indicator: {pricing_indicator_code}, BETOS: {betos_code}, Effective: {effective_date})`
   - **Coverage Policies (`CoveragePolicy`):** `- Coverage Policy: [{cp.primary_key}] {article_id} ({publication_type}) - {title} (Effective: {effective_date}, Clinical Prerequisites: {'; '.join(clinical_prerequisites)})`
   - **Contextual Records (`CBOScore`, `LobbyingFiling`):**
     - `CBOScore`: `- CBO Cost Estimate: [{cbo.primary_key}] {title} (Published: {publication_date}, Summary: {estimate_summary})`
     - `LobbyingFiling`: `- Lobbying Filing: [{lf.primary_key}] Registrant: {registrant_name}, Client: {client_name} ({filing_year} {filing_period}, Specific Issue: {specific_issue_excerpt})`
2. **`### 2. Contractor & Region`:**
   - Use persisted `j.properties["contractor_name"]` and `j.properties["jurisdiction_code"]` on `Jurisdiction` nodes (without hardcoded contractor name overrides) and list covered `State` nodes (`[STATE-XX] {state_name} ({state_code})`) from `COVERS_STATE` edges.
3. **`### 3. Clinical & Billing Codes`:**
   - **Diagnosis Codes (`DiagnosisCode`):** `- Qualifying Diagnosis: [{d.primary_key}] ICD-10 {code} - {description}`
   - **Procedure Codes (`ProcedureCode`):** List covered `ProcedureCode` nodes (prioritizing active/queried codes plus representative National Fee Schedule and Local Contractor Priced codes) with full attributes:
     `- [{h.primary_key}] HCPCS {code}: {short_description} (Long Description: {long_description}, Benefit Category: {benefit_category}, BETOS: {betos_code}, Pricing Indicator: {pricing_indicator}, Pricing Methodology: {pricing_methodology}, Custom/NOS: {is_custom_or_nos})`
   - **Clinical Evidence (`LiteratureStudy`):** `- Supporting Clinical Evidence: [{st.primary_key}] PMID {pmid} - {title} ({journal}, {publication_date})`
4. **`### 4. Reimbursement Rates`:**
   - Derive schedule year dynamically from persisted `FeeScheduleRate` nodes (`schedule_year`, e.g., `2026`).
   - Emit both non-rural (`is_rural=False`) and rural (`is_rural=True`) state-specific `FeeScheduleRate` lines for prioritized/active HCPCS codes (including `A6522` and queried codes), showing `fee_amount`, calculated 20% patient coinsurance (`round(amt * 0.20, 2)`), `ceiling`, `floor`, `is_rural` label (`Non-Rural` vs `Rural`), and `pricing_methodology`.
   - Explicitly list covered `ProcedureCode` nodes where `pricing_methodology == "LOCAL_CONTRACTOR_PRICING"` (or `pricing_indicator == "46"`), noting that those codes are subject to local DME MAC contractor pricing rather than a national fee schedule dollar amount.
5. **`### 5. Data Sources & Provenance`:**
   - Emit deduplicated provenance entries directly from persisted edge `provenance` dictionaries (`source_uri`, `selector`, `ingestion_timestamp`, `run_id`) without hardcoded fallback timestamps or run IDs.

---

### 3.3 `src/graphrag/synthesizer.py`
Update `SYSTEM_PROMPT` (lines 30–39) and `user_content` (lines 68–74) so example bracketed identifiers reflect the 8-hop ontology prefixes (`[POLICY-...]`, `[BILL-...]`, `[PLAW-...]`, `[STAT-...]`, `[USC-...]`, `[REG-FR-...]`, `[CFR-...]`, `[TR-CR...]`, `[DME-MAC-...]`, `[ICD10-...]`, `[HCPCS-...]`, `[FEE-...]`, `[JURIS-DME-...]`, `[STATE-...]`) and rule 4 instructs quoting official citations directly from the provided `GRAPH CONTEXT` without hardcoding `CMS-1784-F`, `[CMS-MCD-A59508]`, or `[CMS-CR-13286]`.

---

## 4. Verification Criteria
1. Single-entity and multi-entity traversals for `STATE-NY`, `STATE-WI`, `STATE-GU`, `JURIS-DME-A`, `JURIS-DME-D`, `ICD10-I97.2`, `HCPCS-A6522`, `HCPCS-A6520`, `DME-MAC-COPE147943`, `TR-CR13286`, `REG-FR-2023-24455`, `USC-42-1395x-s-2-JJ`, `STAT-117-328-SEC-4133`, `PLAW-117-328`, `BILL-117-hr-3630`, and `POLICY-LTA` return non-empty `TraversalResult` objects containing the 8-hop lineage and zero obsolete edge labels.
2. `GraphContextAssembler.assemble_context` outputs all 5 sections populated exclusively from persisted graph attributes, including `StatutorySection`, `USCSection`, `Regulation`, `CFRSection`, `Transmittal`, `CoveragePolicy`, `DiagnosisCode`, `ProcedureCode` (with BETOS, pricing indicator, and pricing methodology), `FeeScheduleRate` (rural and non-rural rates + 20% coinsurance + local contractor pricing notice), and edge provenance.
