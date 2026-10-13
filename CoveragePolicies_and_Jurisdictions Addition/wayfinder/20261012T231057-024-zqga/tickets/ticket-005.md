# Decision Ticket 005: Phase 4B Geographic Fee Schedule Normalization, Multi-State Unpivoting, and Jurisdictional Topology Schema

**Ticket ID:** `ticket-005.md`  
**Run ID:** `20261012T231057-024-zqga`  
**Scope:** Tier 4B: Geographic Fee Schedule Normalization  
**Status:** RESOLVED  
**Claimed By:** `wayfinder-read-and-plan`  
**Blocked By:** `ticket-003.md`, `ticket-004.md`

---

## 1. Architectural Question
How must the CMS DMEPOS multi-state fee schedule dataset (`phase4_cms_dmepos_lc_category.csv`) be unpivoted across all 54 jurisdictions (108 rate columns), how are the 4 standard DME MAC Jurisdictions mapped to States, and how are `Jurisdiction`, `State`, and `FeeScheduleEntry` nodes and edges constructed with complete provenance according to `functional_specification_003.md`?

---

## 2. Datasource Evaluation & Candidate Selection

### Evaluated Candidates
1. **CMS DMEPOS Fee Schedule Public Use Dataset (`phase4_cms_dmepos_lc_category.csv`):**
   - *Authority:* Official state-by-state pricing matrix published by CMS for Durable Medical Equipment, Prosthetics, Orthotics, and Supplies.
   - *Capabilities:* Contains all 54 geographic jurisdictions (50 states + DC + PR + VI) with Rural `(R)` and Non-Rural `(NR)` payment rates for category `"LC"`.
   - *Selection Status:* **SELECTED** as the authoritative pricing source.
2. **CMS DME MAC Regional Jurisdiction Map:**
   - *Authority:* Official CMS administrative contractor allocations.
   - *Allocation:*
     - `JURIS-DME-A`: Noridian Healthcare Solutions (CT, DE, DC, ME, MD, MA, NH, NJ, NY, PA, RI, VT)
     - `JURIS-DME-B`: CGS Administrators (IL, IN, KY, MI, MN, OH, WI)
     - `JURIS-DME-C`: CGS Administrators (AL, AR, CO, FL, GA, LA, MS, NM, NC, OK, SC, TN, TX, VA, WV, PR, VI)
     - `JURIS-DME-D`: Noridian Healthcare Solutions (AK, AZ, CA, HI, ID, IA, KS, MO, MT, NE, NV, ND, OR, SD, UT, WA, WY)
   - *Selection Status:* **SELECTED** for geographic and jurisdictional graph topology.

---

## 3. Dataset Operational Parameters and Filtering Logic

### 3.1. DMEPOS CSV File Specification
- **Local Empirical Asset:** `DataSources_Agent/assets/20261012T213134-452-7663/phase4_cms_dmepos_lc_category.csv`
- **Filtering Logic:** Direct row matching on `CATG == operational_filters.benefit_category` (`"LC"`).
- **Header Columns:** `HCPCS,Mod,Mod2,JURIS,CATG,Ceiling,Floor` followed by 108 state fee columns (`AL (NR),AL (R),...VI (NR),VI (R)`) and `Description`.

### 3.2. Multi-State Column Unpivoting Transformation
For every row where `CATG == "LC"`:
1. Extract `HCPCS` code, `Ceiling` (float), and `Floor` (float).
2. Iterate through each of the 54 state/territory prefixes:
   - Read Non-Rural fee: `[STATE] (NR)` -> `fee_amount`, `is_rural = False`.
   - Read Rural fee: `[STATE] (R)` -> `fee_amount`, `is_rural = True`.
3. Filter condition: Where `fee_amount > 0.00`, instantiate a discrete `FeeScheduleEntry` record.
4. Composite Primary Key: `FEE-[hcpcs]-[state]-[rural_flag]-[year]`, where `rural_flag` is `"R"` if `is_rural` else `"NR"`, and `year` is `2024`.

---

## 4. Graph Node Specifications

### 4.1. Vertex: `Jurisdiction` (4 Nodes)
- **Primary Key Format:** `JURIS-DME-[A|B|C|D]`
- **Required Properties:**
  - `code: string` (`"JURIS-DME-A"`, `"JURIS-DME-B"`, `"JURIS-DME-C"`, `"JURIS-DME-D"`)
  - `contractor_name: string` (`"Noridian Healthcare Solutions"` or `"CGS Administrators"`)

### 4.2. Vertex: `State` (54 Nodes)
- **Primary Key Format:** `STATE-[state_code]` (e.g., `STATE-WY`, `STATE-PR`, `STATE-DC`)
- **Required Properties:**
  - `state_code: string` (Two-letter postal code, e.g., `"WY"`)
  - `state_name: string` (Full official name, e.g., `"Wyoming"`)

### 4.3. Vertex: `FeeScheduleEntry`
- **Primary Key Format:** `FEE-[hcpcs]-[state]-[rural_flag]-[year]` (e.g., `FEE-A6583-WY-NR-2024`)
- **Required Properties:**
  - `hcpcs_code: string` (`"A6583"`)
  - `state_code: string` (`"WY"`)
  - `is_rural: bool` (`false`)
  - `fee_amount: float` (`148.20`)
  - `ceiling: float` (`148.20`)
  - `floor: float` (`148.20`)
  - `year: int` (`2024`)

---

## 5. Edge Specifications and Graph Topology

1. `(ChangeRequest)-[:APPLIES_TO_JURISDICTION]->(Jurisdiction)`
   - **Source:** `CMS-CR-13286`
   - **Target:** `JURIS-DME-A`, `JURIS-DME-B`, `JURIS-DME-C`, `JURIS-DME-D`
   - **Cardinality:** `1..4`
   - **Semantics:** Associates national Medicare transmittal directive with the four regional contractor jurisdictions.
   - **Provenance:** `source_uri`: `CR13286`, `selector`: `jurisdiction_mapping`, `ingestion_timestamp`: ISO-8601 UTC, `run_id`: Run ID.
2. `(Jurisdiction)-[:COVERS_STATE]->(State)`
   - **Source:** `Jurisdiction`
   - **Target:** `State` (Assigned 12, 7, 17, or 18 states per jurisdiction)
   - **Cardinality:** `1..*`
   - **Semantics:** Maps contractor jurisdiction to each assigned state/territory.
   - **Provenance:** `source_uri`: `CMS DME MAC Regional Directory`, `selector`: `jurisdiction_state_assignment`, `ingestion_timestamp`: ISO-8601 UTC, `run_id`: Run ID.
3. `(HCPCSCode)-[:HAS_FEE_SCHEDULE]->(FeeScheduleEntry)`
   - **Source:** `HCPCSCode` (`HCPCS-A6583`)
   - **Target:** `FeeScheduleEntry` (`FEE-A6583-WY-NR-2024`)
   - **Cardinality:** `1..*`
   - **Semantics:** Attaches discrete pricing records across states to the procedure code.
   - **Provenance:** `source_uri`: `phase4_cms_dmepos_lc_category.csv`, `selector`: `CSV row HCPCS=A6583`, `ingestion_timestamp`: ISO-8601 UTC, `run_id`: Run ID.
4. `(FeeScheduleEntry)-[:APPLIES_TO]->(State)`
   - **Source:** `FeeScheduleEntry` (`FEE-A6583-WY-NR-2024`)
   - **Target:** `State` (`STATE-WY`)
   - **Cardinality:** `1..1`
   - **Semantics:** Links fee record to target geographic entity.
   - **Provenance:** `source_uri`: `phase4_cms_dmepos_lc_category.csv`, `selector`: `column:WY (NR)`, `ingestion_timestamp`: ISO-8601 UTC, `run_id`: Run ID.

---

## 6. Fail-Fast Error and Invariant Rules (`INV-50-STATE-COMPLETENESS`, `INV-FAIL-FAST`)
1. **50-State Completeness Invariant (`INV-50-STATE-COMPLETENESS`):**
   - The unpivoting algorithm must process all 54 jurisdictions present in the dataset.
   - Collapsing rates to a single state (e.g., only Wyoming) or omitting Puerto Rico/Virgin Islands constitutes a schema validation failure.
2. **Missing Fee Schedule File:** If `phase4_cms_dmepos_lc_category.csv` is missing or contains zero rows matching `CATG == "LC"`, halt immediately with fatal error `Phase4FeeScheduleDatasetError("No rows found for category: LC")`.
3. **Missing State Association:** Any `FeeScheduleEntry` that cannot be mapped to an instantiated `State` node raises fatal error `Phase4OrphanFeeRecordError`.
