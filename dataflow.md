The pipeline is designed as an autonomous, zero-seed foreign key discovery engine, not a static query harness populated with pre-known bills, public law numbers, or statutory sections.

The system treats the keyword (such as `"LTA"`) as the **only human input** into the entire process. Everything downstream must be programmatically discovered, extracted, and chained through strict foreign key handoffs without hardcoded lookup tables or pre-baked answers:

### 1. Dynamic Legislative Discovery (Phase 1)

* **Runtime Input:** Solely the policy keyword (e.g., `"LTA"`).


* **Discovery Mechanism:** The pipeline queries legislative databases across congressional sessions to programmatically find all historical and final bills matching the policy, trace their legislative actions and lineage, and determine what public law enacted them.


* **Foreign Key Generation:** It extracts and yields `Target_Bill_IDs` and `Enacted_Law_ID` dynamically from the query results. No bill or law numbers are assumed or hardcoded ahead of time.



### 2. Autonomous Structural Parsing (Phase 2)

* **Trigger:** Consumes whatever `Enacted_Law_ID` was discovered in Phase 1.


* **Parsing Mechanism:** Ingests the raw XML for that law, navigates the document structure, and isolates the specific section adding or amending statutory language.


* **Foreign Key Generation:** Emits `US_Code_Citations` dynamically based on the exact statutory anchors written into the text.



### 3. Downstream Cascade Without Keyword Search (Phases 3, 4, and 5)

* **Rulemaking & Clinical Extraction (Phase 3):** Takes the discovered `US_Code_Citations` to query regulatory registers for the agency's final rules, extracting `Operational_Filters` (benefit categories, billing flags) and `Clinical_Citations` (evidence cited in preambles).


* **Deterministic Adjudication (Phase 4):** Evaluates master coding and fee schedule datasets purely by matching the emitted `Operational_Filters`—completely eliminating fuzzy string matching or manual code hunting.


* **Contextual Enrichment (Phase 5):** Dispatches parallel queries using the discovered `Target_Bill_IDs` (for lobbying disclosures and budget scores) and `Clinical_Citations` (for literature metadata).



### Core Architecture Rule

The pipeline is a deterministic dependency graph. If Phase 1 cannot resolve an `Enacted_Law_ID` from the initial keyword, Phase 2 never runs. If Phase 2 cannot parse the `US_Code_Citations`, Phase 3 halts. The architecture ensures that every single node—from lobbying dollars down to reimbursement rates—is mechanically and provably anchored back to the primary legislative lineage without hallucination or manual intervention.