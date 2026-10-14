# Ticket 003: Dynamic Entity Anchor Resolution & Fail-Fast Token Validation

- **Status:** Resolved
- **Claimed by:** wayfinder-read-and-plan
- **Blocked By:** `ticket-001.md`
- **Target Specification:** `functional_specification_015.md` (§3.2 Dynamic Entity Anchor Resolution)

## 1. Decision Question

How must `EntityAnchorLinker` (`src/graphrag/entity_linker.py`) and `ResolvedAnchors` (`src/graphrag/models.py`) be redesigned to dynamically resolve free-form search terms, citations, codes, all 54 US states/territories, and all 18 canonical primary key prefixes against persisted Neo4j entities without hardcoded bill numbers, document IDs, or single-policy assumptions, while failing fast on invalid jurisdiction codes or nonexistent primary keys?

## 2. Empirical Reconnaissance Findings

1. **Missing 54th Jurisdiction (`GU` Guam):**
   - `EntityAnchorLinker.STATE_NAME_TO_CODE` (`src/graphrag/entity_linker.py` lines 15–31) contains 53 entries and omits `"guam": "GU"`.
2. **Legacy Node Labels & Hardcoded Primary Keys in `src/graphrag/entity_linker.py`:**
   - `_extract_change_request_anchors` (lines 298–316) constructs `CMS-CR-{num}` and queries `:ChangeRequest` instead of querying `:Transmittal` (`TR-CR13286`, `cr_number`, `transmittal_number`).
   - `_extract_coverage_policy_anchors` (lines 318–336) only matches `A\d{5}` and queries `CMS-MCD-{art_id}` instead of matching persisted `:CoveragePolicy` entities (`DME-MAC-COPE147943`, `article_id`, `title`).
   - `_extract_legislative_anchors` (lines 338–390) hardcodes `pk = "FR-2023-24455"` (wrong prefix; 8-hop uses `REG-FR-2023-24455`) and `pk = f"BILL-117-hr-{m.group(1)}"` (hardcoded Congress 117 and chamber `hr`), and does not resolve `StatutorySection` (`STAT-...`), `USCSection` (`USC-...`), `CFRSection` (`CFR-...`), `CBOScore` (`CBO-...`), `LobbyingFiling` (`LDA-...`), or `LiteratureStudy` (`PUBMED-...`).
   - `_extract_diagnosis_anchor` (lines 508–551) queries `:ICD10Code` instead of `:DiagnosisCode`.
   - `_extract_hcpcs_anchors` (lines 572–590) queries `:HCPCSCode` instead of `:ProcedureCode`.
   - `_extract_policy_anchors` (lines 553–570) relies on hardcoded `POLICY-LTA` / `POLICY-IVIG` regex triggers instead of querying persisted `:Policy` nodes and their connected legislative titles.
3. **Missing Fail-Fast on Nonexistent Primary Keys & Invalid Jurisdiction Codes in Free-Form Queries:**
   - In `resolve_anchors`, if a query contains a primary key token with a known prefix (e.g. `HCPCS-Z9999`, `BILL-999-hr-1`, `STATE-ZZ`, `JURIS-DME-Z`, or `NONEXISTENT-PK-9999`) that does not exist in Neo4j, `resolve_anchors` silently skips it instead of raising `EntityResolutionError`.
   - If a query specifies an invalid DME MAC jurisdiction (e.g. `"Jurisdiction E"`, `"DME MAC Z"`), `_extract_jurisdiction_anchors` silently returns `[]` instead of raising `EntityResolutionError`.

## 3. Concrete Architectural Decision

1. **Add `"guam": "GU"` to `STATE_NAME_TO_CODE` (`src/graphrag/entity_linker.py` lines 15–32):**
   - Include `"guam": "GU"` so all 54 US states, districts, and territories (`50 states + DC + PR + VI + GU`) resolve to `STATE-{code}`.
2. **Support All 18 Canonical Primary Key Prefixes with Fail-Fast Validation:**
   - Define `VALID_PK_PREFIXES = ("POLICY-", "BILL-", "PLAW-", "STAT-", "USC-", "REG-FR-", "CFR-", "TR-CR", "DME-MAC-", "CMS-MCD-", "ICD10-", "HCPCS-", "FEE-", "JURIS-DME-", "STATE-", "LDA-", "CBO-", "PUBMED-")`.
   - Update `PK_TOKEN_REGEX` to match explicit primary key tokens across all 18 prefixes (including Unicode en-dash `\u2013` in `USC-42-1395w–3-a-2`):
     `re.compile(r"\b((?:POLICY-|BILL-|PLAW-|STAT-|USC-|REG-FR-|CFR-|TR-CR|DME-MAC-|CMS-MCD-|ICD10-|HCPCS-|FEE-|JURIS-DME-|STATE-|LDA-|CBO-|PUBMED-)[A-Za-z0-9\-_.\u2013\u2014]+)\b", re.IGNORECASE)`.
   - When a token matching `PK_TOKEN_REGEX` is found in `query_text`:
     - Look up `MATCH (n:PolicyNode) WHERE toUpper(n.primary_key) = toUpper($pk) RETURN n.primary_key AS primary_key, labels(n) AS labels, properties(n) AS props`.
     - If no node is found in Neo4j, immediately raise `EntityResolutionError(f"Unresolved primary key token '{candidate}' not found in knowledge graph.", details={"unresolved_token": candidate})`.
   - Also fail fast in `_extract_jurisdiction_anchors` when the query contains an invalid jurisdiction reference such as `r"\b(?:dme\s*mac\s*(?:jurisdiction\s*)?|jurisdiction\s+)([e-z0-9]+)\b"` (excluding valid A, B, C, D), raising `EntityResolutionError(f"Unrecognized DME MAC jurisdiction '{bad_juris}'.", details={"unresolved_token": bad_juris})`.
3. **Dynamic Schema-Driven Lexical Resolution Across All 17 Entity Types:**
   - **Policies (`_extract_policy_anchors`):** Query `MATCH (p:Policy) OPTIONAL MATCH (p)-[:DISCOVERED_BILL]->(b:Bill) OPTIONAL MATCH (p)-[:DISCOVERED_BILL]->(:Bill)-[:INCORPORATED_INTO|ENACTED_AS*1..2]->(:PublicLaw)-[:CONTAINS]->(s:StatutorySection) RETURN p.primary_key AS pk, p.keyword AS keyword, collect(DISTINCT b.title) AS bill_titles, collect(DISTINCT s.heading) AS headings`. Match if `p.keyword` or significant title/heading tokens (e.g. `"lymphedema"`, `"compression"`, `"lta"`, `"lymphedema treatment act"`) appear in `query_text`.
   - **Bills & Public Laws (`_extract_legislative_anchors`):**
     - Query persisted `:PublicLaw` nodes and match `Public Law {congress}-{number}` or `PL {congress}-{number}` or `{congress}-{number}` dynamically against `pl.congress` and `pl.number`.
     - Query persisted `:Bill` nodes and match `{type} {number}` (e.g. `H.R. 3630`, `HR 3630`, `H.R. 2617`, `HR 2617`) or exact bill `title` against persisted `b.type`, `b.number`, and `b.title`.
     - Query persisted `:StatutorySection` nodes and match `Section {statute_section_number}` / `Sec. {statute_section_number}` or `uslm_section_path`.
     - Query persisted `:USCSection` nodes and match `citation_string` or `{title} U.S.C. {section}` / `{section}`.
     - Query persisted `:Regulation` nodes and match `citation` (`88 FR 77676`), `document_number` (`2023-24455`), `docket_id` (`CMS-1780-F`), or `rin` (`0938-AV03`).
     - Query persisted `:CFRSection` nodes and match `cfr_reference` (`42 CFR Part 410`) or `CFR {part}` / `Part {part}`.
     - Query persisted `:CBOScore`, `:LobbyingFiling`, and `:LiteratureStudy` nodes and match CBO IDs (`58517`), LDA client/registrant names or UUIDs, and PubMed PMIDs (`31454178`, `25574334`, etc.).
   - **Transmittals (`_extract_change_request_anchors`):** Query `MATCH (tr:Transmittal) RETURN tr` and match `cr_number` (e.g. `CR13286`, `CR 13286`, `13286`), `transmittal_number` (`R12471CP`), or `superseded_transmittal_numbers` (`R12379CP`).
   - **Coverage Policies (`_extract_coverage_policy_anchors`):** Query `MATCH (cp:CoveragePolicy) RETURN cp` and match `cp.article_id` (or its suffix, e.g. `COPE147943`) or coverage policy references in `query_text`.
   - **Diagnosis Codes (`_extract_diagnosis_anchor`):** Query `MATCH (d:DiagnosisCode) RETURN d` for direct ICD-10 code matches (`I97.2`, `I89.0`, `I97.89`, `Q82.0`), description token matches, and clinical synonym patterns validated against `:DiagnosisCode` in Neo4j.
   - **Procedure Codes (`_extract_hcpcs_anchors`):** Match `\b([A-Z]\d{4})\b` against `MATCH (h:ProcedureCode {primary_key: $pk}) RETURN h`.
4. **Update `ResolvedAnchors` Slot Normalization (`src/graphrag/models.py` & `src/graphrag/entity_linker.py`):**
   - Normalize `DiagnosisCode` -> `slot="diagnosis"`, `ProcedureCode` -> `slot="hcpcs"`, `Transmittal` -> `slot="changerequest"` (and expose `transmittal_anchor` alias on `ResolvedAnchors`), `CoveragePolicy` -> `slot="coveragepolicy"`, `State` -> `slot="state"`, `Jurisdiction` -> `slot="jurisdiction"`, `Policy` -> `slot="policy"`.

## 4. Verification Criteria

- `resolve_anchors` and `resolve_explicit_anchor` resolve all 18 primary key prefixes (`POLICY-`, `BILL-`, `PLAW-`, `STAT-`, `USC-`, `REG-FR-`, `CFR-`, `TR-CR`, `DME-MAC-`, `CMS-MCD-`, `ICD10-`, `HCPCS-`, `FEE-`, `JURIS-DME-`, `STATE-`, `LDA-`, `CBO-`, `PUBMED-`) and all 54 US states/territories (including `"Guam"` / `"GU"` -> `STATE-GU`).
- Queries citing `CR 13286`, `R12471CP`, `88 FR 77676`, `CMS-1780-F`, `Section 4133`, `42 U.S.C. 1395x`, `42 CFR Part 410`, `H.R. 3630`, `H.R. 2617`, `Public Law 117-328`, `COPE147943`, `A6522`, or `I97.2` resolve dynamically against persisted Neo4j entities.
- Any query containing an invalid jurisdiction code or nonexistent primary key raises `EntityResolutionError` (HTTP 400) naming the unresolved token.
