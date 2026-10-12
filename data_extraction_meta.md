By abstracting away the verbose examples and hardcoded specific identifiers, this document focuses entirely on the **systematic flow of foreign keys** from one layer to the next.

---

# Data Extraction Pipeline: Handoff & Dataflow Architecture

## Overview of the Deterministic Handoff

The extraction pipeline operates sequentially across five phases. It functions as a chain of foreign keys: each stage queries a primary source, extracts relevant entities, and generates explicit **handoff keys**. These keys are passed directly to the next stage as required query parameters. If an upstream stage fails to generate a key, the downstream branches dependent on that key are gracefully halted. This guarantees a deterministic, hallucination-free knowledge graph.

---

### Phase 1: Legislative Genesis

**Objective:** Establish the political and legislative root of the policy.

* **Trigger Input:** Target policy keywords (e.g., search terms representing the Act).
* **Target Data Sources:** Federal legislative APIs (e.g., Congress.gov).
* **Execution Logic:**
1. Query the legislative database using the target keywords across historical congressional sessions.
2. Extract historical and final legislative vehicles (Bills).
3. Trace the lineage of these Bills to identify the final enacted legislation (Public Law).


* **Keys Extracted for Handoff:**
* `Target_Bill_IDs` $\rightarrow$ Handed off to **Phase 5** (to extract lobbying and economic data).
* `Enacted_Law_ID` $\rightarrow$ Handed off to **Phase 2** (to find the codified text).



### Phase 2: Statutory Codification Delta

**Objective:** Identify exactly how the enacted law modifies the permanent federal legal code.

* **Trigger Input:** `Enacted_Law_ID` (Generated in Phase 1).
* **Target Data Sources:** Government publishing APIs providing bulk legislative markup (XML).
* **Execution Logic:**
1. Fetch the bulk XML payload for the specific `Enacted_Law_ID`.
2. Traverse the XML tree to isolate the specific section of the law that authorizes the targeted medical benefit.
3. Parse this isolated text to identify the permanent statutory anchors (e.g., additions to the U.S. Code).


* **Keys Extracted for Handoff:**
* `US_Code_Citations` $\rightarrow$ Handed off to **Phase 3** (as the anchors for administrative rulemaking).



### Phase 3: Administrative & Regulatory Execution

**Objective:** Map how the executive agency translated the statute into operational directives and software logic.

* **Trigger Input:** `US_Code_Citations` (Generated in Phase 2).
* **Target Data Sources:** Federal rulemaking registries and agency transmittal portals.
* **Execution Logic:**
1. Query rulemaking APIs strictly using the `US_Code_Citations` to locate the agency's Final Rule.
2. Parse the Final Rule to extract permanent regulatory codes (CFR) and operational instructions (Change Requests/Transmittals).
3. Parse the preambles and footnotes of these rules to extract bibliographic references used as scientific justification.


* **Keys Extracted for Handoff:**
* `Operational_Filters` (e.g., Pricing Indicators, Benefit Categories, System Modifiers) $\rightarrow$ Handed off to **Phase 4** (to isolate billing items).
* `Clinical_Citations` (e.g., PubMed IDs) $\rightarrow$ Handed off to **Phase 5** (to validate evidentiary justification).



### Phase 4: Medical Coding, Adjudication & Pricing

**Objective:** Isolate the exact universe of actionable medical products, restrictions, and financial reimbursement rates.

* **Trigger Input:** `Operational_Filters` (Generated in Phase 3).
* **Target Data Sources:** Alpha-Numeric medical coding master files, regional fee schedules, and local coverage determination databases.
* **Execution Logic:**
1. Scan massive medical coding datasets and filter **only** for rows matching the `Operational_Filters` (bypassing keyword searches entirely).
2. Ingest coverage policies to map strict diagnostic constraints to this newly isolated universe of medical codes.
3. Merge regional fee schedule files to attach payment floors and ceilings to each specific billing code.


* **Terminal Output:** A fully resolved, mathematically bound subgraph of medical codes, physical replacement limits, prices, and required diagnoses.

### Phase 5: Evidentiary, Economic, & Advocacy Wrapper (Parallel Execution)

**Objective:** Attach the historical, financial, and scientific context to the established graph.

* **Trigger Inputs:**
* `Target_Bill_IDs` (Generated in Phase 1).
* `Clinical_Citations` (Generated in Phase 3).


* **Target Data Sources:** Lobbying disclosure databases, congressional budget archives, and federal medical library APIs.
* **Execution Logic:**
1. Query lobbying and economic APIs strictly using the `Target_Bill_IDs` to retrieve verified advocacy expenditures and federal cost-offset projections.
2. Query medical literature APIs strictly using the `Clinical_Citations` to retrieve the peer-reviewed studies that justify the regulatory caps identified in Phase 3.


* **Terminal Output:** External context nodes directly bridging the gap between clinical/commercial reality and political/economic origins.

---

## Abstract Dataflow Visualization

```text
[PHASE 1: LEGISLATION] 
  Input: Policy Keywords 
  Outputs: 
    ├─> Target_Bill_IDs ──────────────────────────────────────────┐
    └─> Enacted_Law_ID ─┐                                         │
                        │                                         │
[PHASE 2: STATUTE] <────┘                                         │
  Input: Enacted_Law_ID                                           │
  Outputs:                                                        │
    └─> US_Code_Citations ─┐                                      │
                           │                                      │
[PHASE 3: REGULATION] <────┘                                      │
  Input: US_Code_Citations                                        │
  Outputs:                                                        │
    ├─> Clinical_Citations ───────────────────────────────────────┤
    └─> Operational_Filters ─┐                                    │
                             │                                    │
[PHASE 4: ADJUDICATION] <────┘                                    │
  Input: Operational_Filters                                      │
  Outputs: [Final Medical/Pricing Subgraph]                       │
                                                                  │
[PHASE 5: EVIDENCE & ECONOMICS] <─────────────────────────────────┘
  Inputs: Target_Bill_IDs, Clinical_Citations
  Outputs: [Final Advocacy/Economic Subgraph]

```

---

## Pipeline Integrity Constraints

To ensure dataflow fidelity and prevent hallucination when scaling this graph, the pipeline must enforce three strict architectural rules:

1. **Strict Dependency Handoffs:** A downstream stage cannot execute until the prerequisite keys are fully resolved by the upstream stage. No fuzzy matching or fallback guessing is permitted.
2. **Deterministic Primary Keys:** Nodes generated across stages must utilize composite hashes (e.g., `[Congress]-[Type]-[Number]` or `[Title]-[Code]-[Section]`) to prevent edge collisions during data merging.
3. **No Unanchored Entities:** Terminal nodes (like billing codes extracted in Phase 4) must maintain an unbroken bidirectional path up to the originating statutory node from Phase 1. Disconnected, orphaned nodes must be automatically purged during graph compaction.