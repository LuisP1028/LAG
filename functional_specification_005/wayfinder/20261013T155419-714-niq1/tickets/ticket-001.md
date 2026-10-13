# Decision Ticket 001: Generalized 14-Node Entity Anchor Resolution and Fail-Fast Validation Specification

**Ticket ID:** `ticket-001.md`  
**Scope:** GraphRAG Stage 1 - Input Entity Resolution (`src/graphrag/entity_linker.py`, `src/graphrag/models.py`)  
**Status:** RESOLVED  
**Claimed By:** `wayfinder-read-and-plan`  
**Blocked By:** None (Root Decision)  

---

## 1. Architectural Question
How must `EntityAnchorLinker` and associated data models be refactored to dynamically recognize starting pins across all 14 knowledge graph node types (`State`, `Jurisdiction`, `ChangeRequest`, `CoveragePolicy`, `HCPCSCode`, `ICD10Code`, `Policy`, `Bill`, `PublicLaw`, `StatutorySection`, `Regulation`, `FeeScheduleEntry`, `LobbyingFiling`, `LiteratureStudy`) and primary key strings, while preserving fail-fast validation (`EntityResolutionError`) for unindexed entities?

---

## 2. Technical Audit and Empirical Findings

1. **Current Codebase Constraints:**
   - In `src/graphrag/entity_linker.py`, entity resolution is constrained to four specific slots: `State` (via `STATE_NAME_TO_CODE`), clinical synonyms (`CLINICAL_SYNONYMS` -> `ICD10Code`), policies (`POLICY_TRIGGERS` -> `Policy`), and HCPCS codes (`HCPCS_REGEX`).
   - Any query containing only a single entity outside these hardcoded pairings or referencing `Jurisdiction`, `ChangeRequest`, `CoveragePolicy`, `Bill`, `PublicLaw`, `Regulation`, `StatutorySection`, `FeeScheduleEntry`, `LobbyingFiling`, or `LiteratureStudy` is ignored or dropped.
   - The current data model `ResolvedAnchors` in `src/graphrag/models.py` only defines fields for `state_anchor`, `diagnosis_anchor`, and `policy_anchor`, plus a list `all_anchors`.
2. **Neo4j Node Entity Distribution:**
   - Empirical analysis of `exports/lta_knowledge_graph.json` and `exports/ivig_knowledge_graph.json` reveals 3,971 unique nodes across 14 distinct labels.
   - Every node possesses a verified `primary_key` conforming to prefixed patterns:
     - `STATE-[code]` (53 nodes)
     - `JURIS-DME-[A-D]` (4 nodes)
     - `CMS-CR-[number]` (2 nodes)
     - `CMS-MCD-[id]` (2 nodes)
     - `HCPCS-[code]` (75 nodes)
     - `ICD10-[code]` (6 nodes)
     - `POLICY-[keyword]` (2 nodes)
     - `BILL-[congress]-[type]-[number]` (3 nodes)
     - `PLAW-[congress]-[number]` (1 node)
     - `USC-[title]-[section]-[subsections]` (2 nodes)
     - `FR-[year]-[doc_number]` (1 node)
     - `FEE-[code]-[state]-[rural_status]-[year]` (3,816 nodes)
     - `LDA-[guid]` (2 nodes)
     - `PUBMED-[pmid]` (2 nodes)

---

## 3. Concrete Architectural Decision & Interface Contracts

### 3.1. Primary Key Direct Token Resolution
In `EntityAnchorLinker.resolve_anchors`:
1. Extract candidate primary key tokens matching the pattern `\b([A-Z0-9]+-[A-Z0-9\-_.]{2,})\b`.
2. Query Neo4j to verify existence and retrieve the node's primary label:
   ```cypher
   MATCH (n:PolicyNode {primary_key: $pk})
   RETURN n.primary_key AS primary_key, labels(n) AS labels, n.name AS name, n.title AS title
   ```
3. For verified nodes, construct an `AnchorEntity` where:
   - `primary_key = record["primary_key"]`
   - `label = [l for l in record["labels"] if l != "PolicyNode"][0]`
   - `entity_type = label`
   - `slot = label.lower()`
   - `matched_text = record["name"] or record["title"] or candidate_token`

### 3.2. Lexical & Synonym Resolution for All 14 Entity Types
Expand `EntityAnchorLinker` extraction routines:
1. **Jurisdiction Anchor Extraction:**
   - Match contractor names and codes: "Noridian" -> `JURIS-DME-A`, "CGS" / "CGS Administrators" -> `JURIS-DME-B`, "Jurisdiction A" -> `JURIS-DME-A`, "Jurisdiction B" -> `JURIS-DME-B`, "Jurisdiction C" -> `JURIS-DME-C`, "Jurisdiction D" -> `JURIS-DME-D`.
2. **Change Request Anchor Extraction:**
   - Match regex `\b(?:CR|Change Request|Transmittal)\s*([0-9]{4,5})\b` -> resolve to `CMS-CR-$1`.
3. **Coverage Policy Anchor Extraction:**
   - Match regex `\b(?:LCD|Article|Coverage Policy|MCD)?\s*(A\d{5})\b` -> resolve to `CMS-MCD-$1`.
4. **Legislation and Regulation Anchors:**
   - Match `\bPublic Law\s*(\d+)-(\d+)\b` or `\bPL\s*(\d+)-(\d+)\b` -> `PLAW-$1-$2`.
   - Match `\b(\d+)\s*FR\s*(\d+)\b` or `\bCMS-1784-F\b` -> `FR-2023-24455`.
   - Match `\b(?:HR|H\.R\.)\s*(\d+)\b` -> `BILL-117-hr-$1`.
   - Match `\b(?:42\s*CFR|Title\s*42)\s*(?:§\s*)?410\.36\b` or `\b1395x\b` -> `USC-42-1395x...`.
5. **Retain Existing Resolvers:**
   - Retain full 53-state dictionary `STATE_NAME_TO_CODE` and 2-letter postal regex.
   - Retain clinical synonym table for ICD-10 diagnosis resolution.
   - Retain policy trigger table for LTA and IVIG.
   - Retain HCPCS code regex matching.

### 3.3. Multi-Slot Anchor Container (`ResolvedAnchors`)
Refactor `ResolvedAnchors` in `src/graphrag/models.py`:
```python
class ResolvedAnchors(BaseModel):
    all_anchors: List[AnchorEntity] = Field(default_factory=list)
    state_anchor: Optional[AnchorEntity] = None
    diagnosis_anchor: Optional[AnchorEntity] = None
    policy_anchor: Optional[AnchorEntity] = None
    hcpcs_anchor: Optional[AnchorEntity] = None
    jurisdiction_anchor: Optional[AnchorEntity] = None
    change_request_anchor: Optional[AnchorEntity] = None
    coverage_policy_anchor: Optional[AnchorEntity] = None
```
Provide helper property `primary_keys -> List[str]` returning `[a.primary_key for a in all_anchors]`.

### 3.4. Fail-Fast Boundary Enforcement (`INV-FAIL-FAST`)
- If user input references an unrecognized geographic location (e.g., "Atlantis") via `GEO_LOCATION_INDICATORS`, raise `EntityResolutionError(f"Unrecognized geographic jurisdiction '{candidate}'.", details={"extracted_geo": candidate})`.
- If user input references an unindexed medical condition (e.g., "diabetes", "asthma", "hypertension"), raise `EntityResolutionError(f"No authorized Medicare coverage policy found for condition '{unindexed}'.", details={"extracted_condition": unindexed})`.
- If no valid anchors are extracted from the prompt and the prompt is not empty, raise `EntityResolutionError("No recognized domain entities found in prompt.")`.
