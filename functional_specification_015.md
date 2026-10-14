# Functional Specification 015: End-to-End Agnostic Graph Persistence, Retrieval, and Visualization Alignment

## 1. Objective & Scope

This specification defines the `{functionality}` required for `{correctness}` and `{sufficient}` alignment across three layers of the system:
1. The live Neo4j graph database.
2. The backend retrieval and context synthesis services.
3. The frontend visualization canvas and inspection drawer.

The upstream extraction pipeline generates an 8-hop knowledge graph directly from official government records (statutes, regulations, transmittals, coverage articles, billing codes, fee schedules, and geographic jurisdictions) without hardcoded seeds. The persistence layer, API endpoints, and user interface must faithfully store, query, and present these entities and relationships dynamically. 

Any hardcoded policy identifiers, static fallback text, unmapped entity categories, or outdated shortcut relationships in the database, API responses, or UI constitute `{errors}` and make the system `{insufficient}`.

---

## 2. Graph Persistence & Synchronization Requirements

### 2.1 Entity & Relationship Ingestion
* **Input:** Serialized knowledge graph payloads produced by the 8-hop extraction pipeline for an ingested policy domain.
* **Desired Behavior & Outcomes:**
  - Synchronize the live graph database with the complete 8-hop node and edge topology.
  - Persist all entity types with unique constraints on their primary keys:
    1. **Policy (`POLICY-...`):** Runtime policy keyword, run ID, and ingestion timestamp.
    2. **Bill (`BILL-...`):** Standalone bills and omnibus vehicles, including Congress number, bill type, bill number, official title, and introduced date.
    3. **Public Law (`PLAW-...`):** Congress number, public law number, official title, and enactment date.
    4. **Statutory Section (`STAT-...`):** Public Law ID, USLM XML hierarchy path, section number, section heading, text excerpt, and effective date.
    5. **U.S. Code Section (`USC-...`):** Title number, section code, subsection hierarchy, and formatted citation string.
    6. **Federal Register Final Rule (`REG-FR-...`):** Document number, citation (volume and page), docket ID, Regulation Identifier Number (RIN), effective date, and affected CFR parts.
    7. **CFR Section (`CFR-...`):** CFR reference string, title number, and part number.
    8. **Transmittal (`TR-CR...`):** Change Request (CR) number, active transmittal number, superseded transmittal numbers, CMS manual publication, benefit category code, pricing indicator code, BETOS code, and effective date.
    9. **Coverage Policy (`DME-MAC-...` or `CMS-MCD-...`):** Policy/article ID, publisher classification (`CMS_MCD_LCD` or `DME_MAC_JOINT_PUBLICATION`), title, effective date, and clinical prerequisite criteria.
    10. **Diagnosis Code (`ICD10-...`):** ICD-10-CM code and official clinical description.
    11. **Procedure Code (`HCPCS-...`):** 5-character HCPCS code, short and long descriptions, benefit category, BETOS code, pricing indicator, pricing methodology (`NATIONAL_FEE_SCHEDULE` or `LOCAL_CONTRACTOR_PRICING`), and custom/NOS flag.
    12. **Fee Schedule Rate (`FEE-...`):** HCPCS code, state postal code, rurality flag, allowable fee amount in USD, ceiling, floor, schedule year, and pricing methodology.
    13. **Administrative Contractor (`JURIS-DME-...`):** DME MAC jurisdiction code and contractor name.
    14. **Jurisdiction / State (`STATE-...`):** All 54 US states, districts, and territories (`50 states + DC + PR + VI + GU`) with two-letter postal code and full name.
    15. **Contextual Records (`LDA-...`, `CBO-...`, `PUBMED-...`):** Lobbying filings, CBO score reports, and PubMed citations linked to their legislative or regulatory anchors.
  - Persist all relationship types with complete provenance metadata (`source_uri`, `selector`, `ingestion_timestamp`, `run_id`):
    - `DISCOVERED_BILL`, `INCORPORATED_INTO`, `ENACTED_AS`, `CONTAINS`, `AMENDS`, `AUTHORIZED_BY`, `CODIFIED_IN`, `IMPLEMENTED_BY`, `MANDATES_POLICY`, `REQUIRES_DIAGNOSIS`, `COVERS_PROCEDURE`, `HAS_RATE`, `APPLIES_TO_STATE`, `APPLIES_TO_JURISDICTION`, `COVERS_STATE`, `HAS_ADVOCACY_RECORD`, `HAS_BUDGET_IMPACT`, and `SUPPORTED_BY_EVIDENCE`.
* **Constraints & Invariants:**
  - Remove stale nodes and obsolete shortcut edges (e.g. direct `ENACTED_AS` links from an un-enacted standalone bill to a Public Law when an omnibus bill intervened).
  - Ingestion must be idempotent: re-running ingestion with the same payload must not create duplicate nodes or edges.

---

## 3. Backend Retrieval & Context Services

### 3.1 Graph Topology & Summary Service
* **Inputs:** Optional filters for policy domain, DME MAC jurisdiction, and state/territory (supporting all 54 jurisdictions including `GU`), plus a flag to expand fee schedule rates.
* **Desired Behavior & `{correct required outputs}`:**
  - Default query (rates unexpanded): Return the core policy topology across all non-rate entity types, including connecting edges and provenance metadata.
  - Each returned node must include its entity label, primary key, a human-readable display name derived from persisted properties (e.g. citation, title, transmittal number, or code), and its full attribute dictionary.
  - State filter query: Return the state-specific `FeeScheduleRate` nodes with their `HAS_RATE` and `APPLIES_TO_STATE` edges, scoping contractor and state nodes to the selected state and its governing DME MAC jurisdiction.
  - Jurisdiction filter query: Scope contractor and state nodes to the specified DME MAC jurisdiction.
* **Fail-Fast Behavior:** Unrecognized state codes or jurisdiction codes must return a 400 Bad Request error rather than an empty or partial graph.

### 3.2 Dynamic Entity Anchor Resolution
* **Inputs:** Free-form text query or an explicit entity primary key.
* **Desired Behavior & `{correct required outputs}`:**
  - Resolve candidate search terms, citations, codes, and location names dynamically against persisted graph entities.
  - Recognize all 54 US states and territories as valid geographic anchors.
  - Support explicit primary key lookup across all valid prefixes (`POLICY-`, `BILL-`, `PLAW-`, `STAT-`, `USC-`, `REG-FR-`, `CFR-`, `TR-CR`, `DME-MAC-`, `CMS-MCD-`, `ICD10-`, `HCPCS-`, `FEE-`, `JURIS-DME-`, `STATE-`, `LDA-`, `CBO-`, `PUBMED-`).
  - Rely on ingested titles, keywords, citations, and identifiers rather than hardcoded bill numbers, document IDs, or single-policy assumptions.
* **Fail-Fast Behavior:** If a query specifies an invalid jurisdiction code or a nonexistent primary key, return an explicit error identifying the unresolved token.

### 3.3 Subgraph Traversal & Context Synthesis
* **Inputs:** Resolved entity anchors from a user query or node selection.
* **Desired Behavior & `{correct required outputs}`:**
  - Traverse the full relationship chain:
    `DISCOVERED_BILL` $\to$ `INCORPORATED_INTO` $\to$ `ENACTED_AS` $\to$ `CONTAINS` $\to$ `AMENDS` $\to$ `AUTHORIZED_BY` $\to$ `CODIFIED_IN` $\to$ `IMPLEMENTED_BY` $\to$ `MANDATES_POLICY` $\to$ `REQUIRES_DIAGNOSIS` / `COVERS_PROCEDURE` $\to$ `HAS_RATE` $\to$ `APPLIES_TO_STATE`.
  - Assemble structured context exclusively from the traversed node and edge attributes, without static fallback titles or hardcoded citations.
  - The assembled context must present:
    1. **Legal Authority:** Root policy keyword, bill history, enacting Public Law, specific statutory section details, amended U.S. Code sections, Federal Register rule details, codified CFR parts, CMS transmittal details, and clinical coverage policy guidance.
    2. **Contractor & Region:** Governing DME MAC contractor and covered jurisdictions.
    3. **Clinical & Billing Codes:** Qualifying ICD-10 diagnosis codes and covered HCPCS procedure codes (including BETOS, pricing indicator, and pricing methodology).
    4. **Reimbursement Rates:** State-specific rural and non-rural rates with patient coinsurance, noting any codes subject to local contractor pricing.
    5. **Provenance:** Source URLs and document selectors recorded on edges.

---

## 4. Frontend Visualization & Node Inspection

### 4.1 Visual Taxonomy for All Entity Categories
* **Desired Behavior & `{correct required outputs}`:**
  - Render and distinguish all entity categories on the graph canvas (`Policy`, `Bill`, `PublicLaw`, `StatutorySection`, `USCSection`, `Regulation`, `CFRSection`, `Transmittal`, `CoveragePolicy`, `DiagnosisCode`, `ProcedureCode`, `FeeScheduleRate`, `Jurisdiction`, `State`, `LobbyingFiling`, `CBOScore`, `LiteratureStudy`).
  - Assign distinct colors, shapes, and clear type labels to each category.
  - Display actual entity names and primary keys in node labels and tooltips, without generic placeholder text.

### 4.2 Node Detail Drawer
* **Desired Behavior & `{correct required outputs}`:**
  - Display all persisted properties for the selected node without omission:
    - **Bills:** Congress, type, number, title, introduced date, and related bill relationships.
    - **Statutory & USC Sections:** Public Law ID, section number, USLM path, heading, effective date, and citation string.
    - **Regulations & CFR Sections:** Document number, citation, docket ID, RIN, effective date, and CFR references.
    - **Transmittals:** CR number, active transmittal number, superseded transmittals, manual publication, category code, and effective date.
    - **Coverage Policies:** Article ID, title, publisher type, effective date, and clinical prerequisites.
    - **Procedure Codes (HCPCS):** Code, short/long descriptions, category, BETOS, pricing indicator, and pricing methodology.
    - **Diagnosis Codes (ICD-10):** Code and clinical description.
    - **Fee Schedule Rates:** HCPCS code, state code, rural status, allowable fee, ceiling, floor, year, and pricing methodology.
  - Construct external government links dynamically from node attributes (e.g. Congress.gov, Federal Register, eCFR, CMS MCD, PubMed). If required attributes are missing, omit the link rather than substituting fallback IDs.

### 4.3 Interactive Filter Controls
* **Desired Behavior & `{correct required outputs}`:**
  - Populate the state filter with all 54 US jurisdictions (`50 states + DC + PR + VI + GU`).
  - Populate policy and domain selectors dynamically from entities available in the graph database.

---

## 5. Acceptance Criteria

The system will be considered `{sufficient}` and free of `{errors}` when the following criteria are met:

1. **Topology & Ingestion Integrity:** The graph ingestion pipeline builds the multi-hop policy-to-reimbursement structure, establishing nodes and relationships across statutory authorities, regulations, transmittals, coverage policies, billing codes, and geographic jurisdictions.
2. **Dynamic Resolution & Resilient Fallback Handling:** Backend retrieval services and frontend UI dynamically resolve entity identifiers, metadata, and external reference links from ingested node attributes, avoiding invalid synthetic links or stale defaults.
3. **Multi-Hop Traversal & Context Synthesis:** Graph search and node detail queries successfully traverse the connected policy graph and assemble structured context citing persisted node properties and valid primary keys.
4. **Automated Verification:** Relevant unit, integration, and pipeline test suites pass cleanly, validating core ingestion, graph queries, and API response contracts.