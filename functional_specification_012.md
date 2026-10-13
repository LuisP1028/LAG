# Functional Specification: Field-Level Origin Catalog for Node Details (Source vs. Builder vs. Runtime)

**Document ID:** `functional_specification_012.md`
**Status:** Requirements Specification
**Implementation Guidance:** Strictly Prohibited (DO NOT CODE YET)
**Taxonomy Reference:** [LANGUAGE.md](file:///Users/diesel/Desktop/LAG/LANGUAGE.md)
**Parent Specification:** [functional_specification_011.md](file:///Users/diesel/Desktop/LAG/functional_specification_011.md)
**Planning Map:** [wayfinder/20261013T213500-012-prov/map.md](file:///Users/diesel/Desktop/LAG/wayfinder/20261013T213500-012-prov/map.md)

---

## 1. Objective and Problem Statement

Specification 011 requires every Node Detail Drawer field to be labeled **DATASET** or **DERIVED**. This specification supplies the authoritative, verified catalog that those labels depend on. For every node label and every field, it states where the value actually originates.

### The Problem
Investigation (wayfinder tickets 001–004) shows that "present in the exported dataset" does **not** mean "taken from a source document":

1. **Exports contain constants.** Many exported values were written as constants inside the graph builder (`src/graph/tier*.py`) and were never read from a raw source. Examples:
   - Every Bill, PublicLaw, ChangeRequest, CoveragePolicy, ICD10Code, Jurisdiction and State field.
   - Every IVIG HCPCS and IVIG fee value.
2. **Some source files hold nothing usable.** The Bill and PublicLaw source files contain only `OVER_RATE_LIMIT` error payloads. The CoveragePolicy source file is an HTTP 404 page.
3. **Nodes have no provenance.** Only edges carry `source_uri`, so nothing in the dataset records where a node's own field values came from.
4. **More values are added after the dataset**, by the API and the frontend (catalogued in §5).

A binary DATASET / DERIVED label applied to the export would therefore label builder constants as DATASET. That is exactly the ambiguity the user is trying to remove.

### The Desired Solution
1. Every value shown in the drawer is attributed to exactly one **Origin Class** (§3), according to the catalog in §4 and §5.
2. The drawer visibly communicates that Origin Class per field, per specification 011 §4.1.
3. Where the catalog records a defect (§6), the drawer exposes it to the user and does not hide it.

> [!IMPORTANT]
> Whether the drawer shows all five Origin Classes or collapses them into 011's binary labels is an **open user decision**: [Does a Builder Literal Count as "Dataset" in the Drawer?](file:///Users/diesel/Desktop/LAG/wayfinder/20261013T213500-012-prov/tickets/ticket-005.md). This specification is written for the five-class outcome. §7 defines the mapping if the binary outcome is chosen.

---

## 2. Taxonomy and Evaluation Parameters

* **`{errors}`:** The drawer fails to render, or renders a field without an Origin Class, for any node in either export.
* **`{correctness}`:** Every field's displayed Origin Class equals the class assigned in §4 or §5 for that label, field and policy.
* **`{functionality}`:** A user can determine, for any field of any node, whether a human-readable source document supplied it, the builder computed it, the builder hardcoded it, or the API or frontend produced it at display time.
* **`{correct required outputs}`:** §8.
* **`{sufficient}` / `{insufficient}`:** As defined in LANGUAGE.md.

---

## 3. Origin Classes

| Origin Class | Definition | Verifiable By |
| :--- | :--- | :--- |
| **SOURCE-EXTRACTED** | Present in the export **and** present, with an equal value, in the raw asset file read by the builder. | Opening the asset file and locating the value. |
| **BUILDER-COMPUTED** | Present in the export. Computed deterministically from SOURCE-EXTRACTED or BUILDER-LITERAL inputs, e.g. composite primary keys or a category heuristic. | Re-applying the stated rule to its inputs. |
| **BUILDER-LITERAL** | Present in the export. Written as a constant in builder code, either directly or as a `.get(key, default)` default because the source lacked the key. | Locating the constant in `src/graph/tier*.py`. |
| **PIPELINE-METADATA** | Present in the export. Describes the build run rather than the policy domain (run id, timestamps, the runtime policy keyword). | Matching the run that produced the export. |
| **RUNTIME-DERIVED** | **Not** present in the export. Produced by the API or the frontend at request or display time. | Absent from the export node or edge record. |

A field takes exactly one class. When a builder expression can yield either a source value or a default, the class is determined by **what actually occurred in the current exports**, as verified in ticket 003. It is not determined by what the code could yield.

---

## 4. Node Field Catalog (Exported Fields)

Notation: **SRC** = SOURCE-EXTRACTED, **CMP** = BUILDER-COMPUTED, **LIT** = BUILDER-LITERAL, **META** = PIPELINE-METADATA. "Both" means LTA and IVIG exports agree.

Asset directory, abbreviated **`A/`**: `CoveragePolicies_and_Jurisdictions Addition/assets/20261012T231057-024-zqga/`

### 4.1 Policy
| Field | Class | Basis |
| :--- | :--- | :--- |
| `primary_key` | CMP | `POLICY-{keyword}` |
| `keyword` | META | Runtime pipeline input (LANGUAGE.md `{Policy Keyword}`) |
| `run_id`, `timestamp` | META | Build run |

### 4.2 Bill (both; nodes BILL-117-hr-3630, BILL-117-hr-3808, BILL-117-hr-2617)
| Field | Class | Basis |
| :--- | :--- | :--- |
| `congress`, `type`, `number`, `title`, `introduced_date` | **LIT** (all three bills) | H.R. 3630: the source `A/stage1_congress_bill_hr3630_sample.json` is an `OVER_RATE_LIMIT` error, so `.get` defaults were used. H.R. 3808 and H.R. 2617: pure constants. |
| `primary_key` | CMP | From LIT inputs |

### 4.3 PublicLaw (both)
| Field | Class | Basis |
| :--- | :--- | :--- |
| `congress`, `number`, `title`, `enacted_date` | **LIT** | The source `A/stage2_govinfo_plaw_117publ328_summary.json` is an `OVER_RATE_LIMIT` error. |
| `primary_key` | CMP | From LIT inputs |

### 4.4 StatutorySection
| Field | LTA | IVIG | Basis |
| :--- | :--- | :--- | :--- |
| `title` (42), `section` (1395x), `subsections` | LIT | LIT | Constants |
| `heading` | **SRC** | **LIT** | LTA: matches the XML `<heading>`, including its trailing period. IVIG: the default constant (no trailing period); the IVIG section was not located. |
| `text` | **SRC** | **SRC — mismatched** | IVIG `text` is the section 4133 (lymphedema) text, not the IVIG section. See defect D-04. |
| `primary_key` | CMP | CMP | From LIT inputs |

### 4.5 Regulation (both)
| Field | Class | Basis |
| :--- | :--- | :--- |
| `citation`, `document_number`, `effective_date`, `cfr_parts` | **SRC** | All present in `A/stage3_federal_register_rule_2023_24455.json` |
| `primary_key` | CMP | |

### 4.6 ChangeRequest (both)
| Field | Class | Basis |
| :--- | :--- | :--- |
| `cr_number`, `transmittal_number`, `benefit_category`, `effective_date` | **LIT** | IVIG/LTA branch constants in tier 3 |
| `primary_key` | CMP | |

### 4.7 CoveragePolicy (both)
| Field | Class | Basis |
| :--- | :--- | :--- |
| `article_id`, `title`, `effective_date`, `policy_type` | **LIT** | Constants in tier 4a. The LTA probe file is a 404 page. |
| `primary_key` | CMP | |

### 4.8 HCPCSCode
| Field | LTA (70 nodes) | IVIG (5 nodes) | Basis |
| :--- | :--- | :--- | :--- |
| `code`, `short_description` | **SRC** | **LIT** | LTA: CSV `HCPCS` / `Description` columns, 0 of 70 mismatches. IVIG: constants. |
| `category` | **CMP** | **LIT** | LTA: substring heuristic on the description (6 "Nighttime…", 64 "Lymphedema Compression Item"). IVIG: constants. |
| `primary_key` | CMP | CMP | |

### 4.9 ICD10Code (both)
| Field | Class | Basis |
| :--- | :--- | :--- |
| `code`, `description` | **LIT** | Constants in tier 4a |
| `primary_key` | CMP | |

### 4.10 Jurisdiction (both)
| Field | Class | Basis |
| :--- | :--- | :--- |
| `code`, `contractor_name` | **LIT** | Constant `DME_MAC_JURISDICTIONS` table in tier 4b |
| `primary_key` | CMP | |

### 4.11 State (both)
| Field | Class | Basis |
| :--- | :--- | :--- |
| `state_code`, `state_name` | **LIT** | Constant `DME_MAC_JURISDICTIONS` table in tier 4b |
| `primary_key` | CMP | |

### 4.12 FeeScheduleEntry
| Field | LTA (3,710) | IVIG (106) | Basis |
| :--- | :--- | :--- | :--- |
| `hcpcs_code` | SRC | LIT | LTA: CSV row. IVIG: constant `Q2052`. |
| `state_code`, `is_rural` | SRC | LIT | LTA: CSV column header `XX (NR)` / `XX (R)`. IVIG: iterated over the constant state table. |
| `fee_amount`, `ceiling`, `floor` | SRC | LIT | LTA: CSV cells. IVIG: constant `409.84` for all three. |
| `year` | LIT | LIT | Constant `2024` |
| `primary_key` | CMP | CMP | |

### 4.13 LobbyingFiling
| Field | LTA | IVIG | Basis |
| :--- | :--- | :--- | :--- |
| `filing_uuid`, `year` | SRC | SRC | `A/stage5_lda_lobbying_filings_sample.json` |
| `registrant_name`, `client_name` | SRC | **LIT** | IVIG: the constants "Immune Deficiency Foundation Advocacy" / "Immune Deficiency Foundation", which are absent from the file. |
| `amount` | SRC for filing `1821a229…` (20000.0); **LIT** for filing `c8697fc5…` (0.0) | Same | Source `income` is `null` for `c8697fc5…`, so the default `0.0` was used. |
| `primary_key` | CMP | CMP | |

### 4.14 LiteratureStudy (both)
| Field | Class | Basis |
| :--- | :--- | :--- |
| `pmid`, `doi`, `title`, `journal`, `pub_year` | **SRC** | `A/stage5_ncbi_pubmed_esummary.json`. See defect D-07 on selection. |
| `primary_key` | CMP | |

### 4.15 CBOScore
No nodes exist in either export (defect D-08). Nothing to classify.

### 4.16 Edges (all labels, both)
| Field | Class | Basis |
| :--- | :--- | :--- |
| `source_pk`, `target_pk`, `label` | CMP | Builder wiring |
| `provenance.source_uri` | **SRC pointer** — stored as written, but see defect D-05 | A file path, URL or free text recorded by the builder |
| `provenance.selector` | LIT | A builder-authored string. Some are not resolvable paths, e.g. `"preamble.directives"` and `"CMS MAC Region Allocation Table: Jurisdiction A"`. |
| `provenance.ingestion_timestamp`, `provenance.run_id` | META | |

---

## 5. Runtime-Derived Values (Not in the Export)

Every item below is **RUNTIME-DERIVED** and must be presented as such wherever the drawer shows it.

| Value | Producer | Rule |
| :--- | :--- | :--- |
| Drawer header **name** | API `convert_node` | First present value among `name`, `state_name`, `section`, `title` and `primary_key`. Resulting display per label: Bill, PublicLaw, CoveragePolicy and LiteratureStudy → `title`; State → `state_name`; StatutorySection → `section` ("1395x"); every other label → `primary_key`. |
| Node **label**, when Neo4j labels are absent | API | Primary-key prefix inference; otherwise the literal `"PolicyNode"` |
| **edge_key** | API, and frontend fallback | `source->LABEL->target` |
| Edge provenance when absent from the record | API / GraphRAG traversal | Literals `verified://cms-policy` or `verified://federal-statute`, `direct`, `2026-10-13T01:23:54Z`, `export-run-001` |
| Edge provenance when absent from the API response | Frontend | Empty strings |
| **Properties stub** | Frontend | `{primary_key}` when properties are absent |
| **System Description** | Frontend | Per-label theme text, except ICD10Code, whose dataset `description` exists |
| **Government Source Provenance link** | Frontend | Per-label URL pattern with literal defaults, and a substring contractor choice |
| Neighbour label fallback | Frontend | Literal `"Node"` |
| Jurisdiction and state dropdown data | Frontend | `DME_JURISDICTIONS`, a second constant table independent of the graph |

---

## 6. Catalogued Defects the Drawer Must Not Conceal

| ID | Defect | Required Drawer Behavior |
| :--- | :--- | :--- |
| D-01 | Bill and PublicLaw source files are rate-limit errors; all their fields are LIT. | These fields display as LIT, never as source-extracted. |
| D-02 | The CoveragePolicy source file is a 404 page; all fields are LIT. | As D-01. |
| D-03 | ChangeRequest, ICD10Code, Jurisdiction, State, IVIG HCPCS and IVIG fee values are constants. The IVIG LobbyingFiling nodes reuse the two filing UUIDs whose source client is "LYMPHEDEMA ADVOCACY GROUP", but carry constant IVIG registrant and client names. | As D-01. |
| D-04 | IVIG StatutorySection `text` is the LTA section's text. | `text` displays a mismatch notice stating that its heading and text refer to different sections. |
| D-05 | Edges cite sources that do not contain the asserted fact (rate-limit errors, a 404 page, and a CSV with no jurisdiction table). | Governed by the open decision [Treatment of Edges Whose Cited Source Does Not Contain the Asserted Fact](file:///Users/diesel/Desktop/LAG/wayfinder/20261013T213500-012-prov/tickets/ticket-006.md). Until it is decided, provenance is shown exactly as stored. |
| D-06 | Nodes carry no provenance of their own. | The drawer's Source Provenance section (011 §4.2) states "No node-level source recorded in dataset". It may list the `source_uri` values of the node's incident edges, each labeled as **edge** provenance. |
| D-07 | LiteratureStudy nodes are every uid in the PubMed file. The LTA Tier 3 handoff PMIDs (31454178, 27549490) are absent from the graph. | Fields display as SRC. No claim of relevance to the policy is made by the drawer. |
| D-08 | CBO file key `cboCostEstimates` does not match the read key `costEstimates`, so zero CBOScore nodes exist. | No drawer behavior; recorded for completeness. |
| D-09 | No export-writing script exists in the repository. | No drawer behavior; recorded so that PIPELINE-METADATA cannot be reproduced from the repository. |

---

## 7. Mapping to Specification 011 Binary Labels (Only if the Binary Option Is Chosen)

| Origin Class | 011 label under option (a) "literal = dataset" | 011 label under option (b) "literal = derived" |
| :--- | :--- | :--- |
| SOURCE-EXTRACTED | DATASET | DATASET |
| BUILDER-COMPUTED | DATASET | DERIVED |
| BUILDER-LITERAL | DATASET | DERIVED |
| PIPELINE-METADATA | DATASET | DATASET |
| RUNTIME-DERIVED | DERIVED | DERIVED |

---

## 8. Acceptance Criteria (`{correct required outputs}`)

1. **Catalog Coverage:** For every node in both exports (4,035 nodes in total), every field displayed in the drawer shows an Origin Class equal to the class in §4 or §5. Zero unclassified fields.
2. **Policy-Specific Classes:** Where §4 assigns different classes per policy (StatutorySection `heading`, HCPCSCode, FeeScheduleEntry, LobbyingFiling), opening the LTA node and the IVIG node shows the differing classes as specified.
3. **Per-Value Classes:** LobbyingFiling `c8697fc5…` shows `amount` as LIT. LobbyingFiling `1821a229…` shows `amount` as SRC.
4. **Runtime Labeling:** The drawer header name for any Jurisdiction, HCPCSCode, FeeScheduleEntry, ICD10Code, ChangeRequest, Regulation, Policy or LobbyingFiling node is marked RUNTIME-DERIVED (the primary key used as a stand-in name).
5. **Defect Visibility:** Opening the IVIG StatutorySection shows the D-04 mismatch notice. Opening any node shows the D-06 statement in Source Provenance.
6. **No Reclassification Drift:** If an export is regenerated, any field whose origin changes must be re-verified against its raw asset before its class is changed. Classes are never inferred from builder code paths alone.
