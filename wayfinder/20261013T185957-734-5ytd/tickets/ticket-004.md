# Ticket 004: Multi-State and Regional Contractor Entity Anchor Resolution (`EntityAnchorLinker`)

- **Ticket ID:** `ticket-004`
- **Status:** `RESOLVED`
- **Claimed by:** `wayfinder-read-and-plan`
- **Blocked by:** None
- **Blocks:** `ticket-005`
- **Governing Specification:** `functional_specification_008.md` (Section 4, Requirement 5.3.1, Requirement 5.3.2, Acceptance Criterion 6)

---

## 1. Decision Question

How must `EntityAnchorLinker` (`src/graphrag/entity_linker.py`) and `GraphRAGQueryRequest` (`src/graphrag/models.py`) be updated so that natural language queries can resolve multiple geographic states simultaneously (for cross-jurisdiction comparisons), resolve regional contractor and DME MAC jurisdiction references accurately across all 4 jurisdictions, and avoid false-positive fail-fast location rejections when regional jurisdiction terms follow prepositions?

---

## 2. Context & Root Cause Analysis

Currently, `src/graphrag/entity_linker.py` exhibits three root-cause defects against `functional_specification_008.md`:
1. **Single-State Early Return (`_extract_state_anchor`, lines 102–105 & 351–388):**
   `_extract_state_anchor` returns immediately upon matching the first state in `sorted(self.STATE_NAME_TO_CODE.keys(), key=len, reverse=True)`. For Requirement 5.3.2's comparative query *"Compare allowable rates for A6522 between California and New York"*, it matches `"california"` (length 10) and returns `STATE-CA`, completely dropping `"new york"` (`STATE-NY`).
2. **Incomplete Contractor & Jurisdiction Lexical Resolution (`_extract_jurisdiction_anchors`, lines 231–255):**
   - Mentioning `"CGS"` or `"CGS Administrators"` without a letter only resolves `JURIS-DME-B` and omits `JURIS-DME-C`.
   - Mentioning `"Noridian"` without a letter only resolves `JURIS-DME-A` and omits `JURIS-DME-D`.
   - Patterns such as `"DME MAC A"`, `"DME MAC B"`, `"DME MAC C"`, `"DME MAC D"`, or `"MAC B"` are not matched unless the word `"jurisdiction"` is used.
3. **Preposition False Positive on Jurisdiction Phrases (`GEO_LOCATION_INDICATORS`, lines 58 & 389–401):**
   If a query contains `"in Jurisdiction B"` or `"in DME MAC C"` with no state name, `GEO_LOCATION_INDICATORS` extracts `"Jurisdiction B"` as an unrecognized geographic state and raises `EntityResolutionError`.

---

## 3. Locked Architectural Decision

### 3.1 Request Schema Extension (`src/graphrag/models.py`)
In `GraphRAGQueryRequest` (`src/graphrag/models.py`, lines 58–65), add optional `jurisdiction_code: Optional[str] = None`:
```python
class GraphRAGQueryRequest(BaseModel):
    """Request payload for conversational GraphRAG synthesis."""
    query: str
    model_id: Optional[str] = "meta-llama/Meta-Llama-3-8B-Instruct"
    state_code: Optional[str] = None
    jurisdiction_code: Optional[str] = None
    primary_key: Optional[str] = None
    anchor_node_pk: Optional[str] = None
```

### 3.2 Multi-State Extraction (`src/graphrag/entity_linker.py`)
1. Add `"u.s. virgin islands": "VI"` and `"us virgin islands": "VI"` to `STATE_NAME_TO_CODE` alongside `"virgin islands": "VI"`.
2. Implement `_extract_state_anchors(self, text: str, session: Session) -> List[AnchorEntity]`:
   - Maintain a list of matched character spans `matched_spans: List[Tuple[int, int]] = []` and a list of `(match_start, AnchorEntity)` tuples.
   - **Step A (Full State Names):** Iterate over `sorted(self.STATE_NAME_TO_CODE.keys(), key=len, reverse=True)` and use `re.finditer(rf"\b{re.escape(state_name)}\b", lower_text)`:
     - If `(m.start(), m.end())` overlaps any span in `matched_spans` (e.g., preventing `"virginia"` from matching inside `"west virginia"`), skip.
     - Otherwise, verify `STATE-{code}` in Neo4j (`MATCH (s:State {primary_key: $pk}) RETURN s`). If present, record `(m.start(), m.end())` in `matched_spans` and append `(m.start(), AnchorEntity(slot="state", primary_key=pk, matched_text=text[m.start():m.end()], entity_type="State", label="State"))`.
   - **Step B (2-Letter Uppercase State Codes):** For any state code not already matched in Step A, search `text` with `re.finditer(rf"\b{code}\b", text)`. Exclude English all-caps preposition collisions (`"IN"`, `"OR"`, `"ME"`, `"HI"`, `"OK"`, `"DE"`, `"MA"`, `"PA"`, `"LA"`, `"OH"`) unless preceded by a state context or comma/comparison token or when not used as an ordinary lowercase/uppercase English word (specifically: if `code in {"IN", "OR", "ME", "HI", "OK"}` and `text.isupper()`, skip; in normal mixed-case queries, `"IN"` only if not at the start of a clause as a preposition, while all unambiguous 2-letter uppercase codes like `"CA"`, `"NY"`, `"TX"`, `"WI"`, `"FL"`, `"IL"`, `"MN"`, `"KY"`, `"MI"`, etc. match directly).
   - Sort all matched state anchors by `match_start` ascending and deduplicate by `primary_key` so `anchors.state_anchor` points to the first state mentioned and `anchors.all_anchors` contains every state mentioned in the query (e.g., both `STATE-CA` and `STATE-NY`).
   - Keep `_extract_state_anchor(self, text: str, session: Session) -> Optional[AnchorEntity]` delegating to `_extract_state_anchors` and returning `res[0] if res else None` for backward compatibility.
3. **Refined Fail-Fast Unrecognized Location Check:**
   - Only trigger the `GEO_LOCATION_INDICATORS` fail-fast check when zero `State` anchors and zero `Jurisdiction` anchors were extracted from `text`.
   - Expand `stopwords` / non-location exclusions in the fail-fast check to ignore jurisdiction and domain terms: `{"home", "yesterday", "scratch", "pain", "now", "today", "here", "there", "medicare", "general", "part b", "jurisdiction a", "jurisdiction b", "jurisdiction c", "jurisdiction d", "dme mac", "cgs", "noridian"}` and any candidate containing `"jurisdiction"` or `"mac"` or `"policy"`.

### 3.3 Comprehensive Jurisdiction & Contractor Extraction (`_extract_jurisdiction_anchors` in `src/graphrag/entity_linker.py`)
Replace `_extract_jurisdiction_anchors` (lines 231–255) with deterministic explicit-region + contractor resolution:
1. **Explicit Jurisdiction Letter Patterns:**
   - `JURIS-DME-A`: `re.compile(r"\b(?:jurisdiction\s*a|dme\s*mac\s*(?:jurisdiction\s*)?a|mac\s*jurisdiction\s*a|juris-dme-a)\b", re.IGNORECASE)`
   - `JURIS-DME-B`: `re.compile(r"\b(?:jurisdiction\s*b|dme\s*mac\s*(?:jurisdiction\s*)?b|mac\s*jurisdiction\s*b|juris-dme-b)\b", re.IGNORECASE)`
   - `JURIS-DME-C`: `re.compile(r"\b(?:jurisdiction\s*c|dme\s*mac\s*(?:jurisdiction\s*)?c|mac\s*jurisdiction\s*c|juris-dme-c)\b", re.IGNORECASE)`
   - `JURIS-DME-D`: `re.compile(r"\b(?:jurisdiction\s*d|dme\s*mac\s*(?:jurisdiction\s*)?d|mac\s*jurisdiction\s*d|juris-dme-d)\b", re.IGNORECASE)`
2. **Contractor Name Resolution (when no explicit Jurisdiction A/B/C/D letter for that contractor was already matched):**
   - If `re.search(r"\bcgs(?:\s+administrators)?\b", text, re.IGNORECASE)` matches and neither `JURIS-DME-B` nor `JURIS-DME-C` was already matched by an explicit letter, resolve and append both `JURIS-DME-B` and `JURIS-DME-C`.
   - If `re.search(r"\bnoridian(?:\s+healthcare(?:\s+solutions)?)?\b", text, re.IGNORECASE)` matches and neither `JURIS-DME-A` nor `JURIS-DME-D` was already matched by an explicit letter, resolve and append both `JURIS-DME-A` and `JURIS-DME-D`.

---

## 4. Verification Criteria (`{correct required outputs}`)

- `resolve_anchors("What states does Jurisdiction B cover?", session)` returns `JURIS-DME-B` in `all_anchors` and `jurisdiction_anchor`.
- `resolve_anchors("What policies does CGS administer?", session)` returns both `JURIS-DME-B` and `JURIS-DME-C` in `all_anchors`.
- `resolve_anchors("Compare allowable rates for A6522 between California and New York.", session)` returns `STATE-CA`, `STATE-NY`, and `HCPCS-A6522` in `all_anchors`.
- `resolve_anchors("Who administers Medicare Part B DME claims in Texas?", session)` returns `STATE-TX` in `all_anchors` and `state_anchor`.
- `resolve_anchors("I am from Atlantis and need supplies", session)` still raises `EntityResolutionError` with `"Atlantis"`.
