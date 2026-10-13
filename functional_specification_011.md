# Functional Specification: Node Detail Provenance Disambiguation (Dataset vs. Derived)

**Document ID:** `functional_specification_011.md`
**Status:** Requirements Specification
**Implementation Guidance:** Strictly Prohibited (DO NOT CODE YET)
**Taxonomy Reference:** [LANGUAGE.md](file:///Users/diesel/Desktop/LAG/LANGUAGE.md)

---

## 1. Objective and Problem Statement

This specification covers the **Node Detail Drawer**, the panel that opens when a user clicks a node on the canvas. Every piece of information in the drawer must be clearly identifiable as either:

1. **Dataset-Sourced:** the value exists in the knowledge graph dataset, either in the exported graph JSON or in the Neo4j node or edge record.
2. **Derived:** the value was not in the dataset. It was built by the application from a fixed pattern, a hardcoded constant, a theme registry or a substitution rule.

### The Problem
The drawer currently mixes dataset values with values built by the application, and nothing tells them apart. A user cannot tell whether a link or description reflects the actual dataset or was constructed by the application. The confirmed cases are:

| Drawer Element | Current Origin | Defect |
| :--- | :--- | :--- |
| **"GOVERNMENT SOURCE PROVENANCE" link (URL and title)** | Built from a fixed URL pattern chosen by node label. Values are pulled from node properties or parsed from the primary key. | Presented as provenance even though it is not the dataset's recorded source. When values are missing, hardcoded defaults are substituted (Congress `117`, law number `328`, bill number `3630`, bill type `hr`, USC title `42`, section `1395x`). This produces believable links to the wrong documents. |
| **Jurisdiction contractor link** | Chosen by checking whether the jurisdiction code contains the letter "B" or "C". | Every code begins with `JURIS-DME-`, which contains "C", so Jurisdictions A and D are misattributed to CGS. |
| **HCPCSCode / LobbyingFiling / CoveragePolicy / ChangeRequest links** | Generic index pages or search-results pages. | Not the document the node came from. |
| **"System Description" text** | The node's `description` property if present; otherwise generic text from the visual theme registry. | Generic theme text is shown in the same place, with the same styling, as dataset text. |
| **Node name (header)** | The node's `name`; otherwise the primary key is substituted. | The substitution is not disclosed. |
| **Node properties ("Entity Attributes")** | The node's properties from the dataset; otherwise a stub containing only the primary key. | The substitution is not disclosed. |
| **Edge provenance** | The edge's dataset provenance; otherwise empty strings are substituted. | Missing provenance looks like present-but-blank provenance. |
| **Edge key** | The dataset edge key; otherwise built from source, label and target. | The substitution is not disclosed. |
| **Connected Neighbors entries** | Neighbor name and label from loaded nodes; otherwise the primary key and the literal `"Node"`. | The substitution is not disclosed. |
| **Backend `source_uri` placeholders** | When missing, the API returns `verified://cms-policy` or `verified://federal-statute`. | A made-up value is presented as if it were a real recorded source. |

### The Desired Solution
1. The drawer shows only what the dataset holds as its authoritative content. Each displayed value carries a visible **origin indicator**.
2. The application never invents a value and presents it as dataset content.
3. When the dataset is missing an expected value, the drawer says so explicitly instead of showing a stand-in.

---

## 2. Taxonomy and Evaluation Parameters

* **`{errors}`:** The drawer throws an exception, renders blank, or crashes when a node is missing optional or expected fields.
* **`{correctness}`:**
  * Every value labeled **Dataset** matches the node or edge record returned by the API exactly, character for character.
  * No value labeled **Dataset** was produced by a pattern, constant, default or substitution.
* **`{functionality}`:** A user can open any node and tell, for every field, whether it comes from the knowledge graph dataset or was produced by the application. External links shown as "source provenance" come only from the dataset.
* **`{correct required outputs}`:** Defined in Section 6.
* **`{sufficient}` / `{insufficient}`:** As defined in LANGUAGE.md.

---

## 3. Definitions

| Term | Meaning |
| :--- | :--- |
| **Dataset Value** | A value present on the node or edge record in the knowledge graph, as returned by the topology API. |
| **Recorded Source** | The node's or edge's `source_uri` provenance value as stored in the dataset. It is unchanged and has not been replaced by a placeholder. |
| **Derived Value** | Any value the application produces that is not present in the dataset record. This includes pattern-built URLs, theme descriptions, primary-key stand-ins, generated edge keys and placeholder strings. |
| **Missing Value** | A field the drawer expects for a node label that is absent or empty on the dataset record. |

---

## 4. Functional Requirements

### 4.1. Origin Indicator on Every Field
1. Every field rendered in the drawer must display an origin indicator. This covers the header name, the description, every property, every link, every neighbor entry and every edge provenance item.
2. There are exactly two indicator states: **DATASET** and **DERIVED**.
3. The two states must be visually distinct and readable at a glance. A user must not need to hover or click to learn a field's origin.
4. A **legend** explaining the two states must be visible in the drawer.

### 4.2. Source Provenance Section (Dataset Only)
1. The section titled "Source Provenance" must display **only** the Recorded Source(s) for the selected node.
2. If the Recorded Source is a web URL, it is shown as a clickable link exactly as stored.
3. If the Recorded Source is a local file path or descriptive text, it is shown exactly as stored. It is not clickable and is not converted into a URL.
4. If the node has no Recorded Source, the section must state **"No recorded source in dataset"**. It must not show any link.
5. The application must never place a pattern-built URL in this section.

### 4.3. Reference Links (Derived, Optional)
1. Lookup links built by the application are permitted only if clearly separated from Source Provenance. Examples are a Congress.gov page for a bill and a PubMed page for a PMID.
2. Such links must appear under a separately titled section, **"Reference Lookups (application-generated)"**, and carry the **DERIVED** indicator.
3. A reference link may be built only when **every** value it requires is present on the dataset record or parsed exactly from the primary key. If any required value is missing, that link must not appear, and the drawer must state which value was missing.
4. Hardcoded default values (for example `117`, `328`, `3630`, `hr`, `42`, `1395x`) must never be used to complete a link.
5. A contractor link for a Jurisdiction node must be chosen from the jurisdiction's actual identity (A, B, C or D) according to the authoritative mapping in [functional_specification_008.md §4](file:///Users/diesel/Desktop/LAG/functional_specification_008.md). It must never come from a substring check.
6. A link must not be labeled as pointing to a specific document if it actually points to a search page or a general index page. Search and index links must be labeled as such, for example "Search CMS Transmittals for CR 13286".

### 4.4. Description
1. If the node has a dataset `description`, it is shown with the **DATASET** indicator.
2. If it does not, the generic text for the node type may be shown only with the **DERIVED** indicator and a caption such as "Generic type description — no description in dataset."

### 4.5. Header Name, Properties, Neighbors and Edges
1. **Header name:** if the dataset has no `name`, the header must say the name is missing. The primary key may be shown alongside, but it must not silently stand in for the name.
2. **Properties:** if the dataset record has no properties, the drawer must state "No properties in dataset". It must not show a stub as if it were data.
3. **Neighbors:** if a neighbor node is not in the currently loaded graph, the entry must state this. It must not show the literal `"Node"` as the label.
4. **Edge provenance:** when an edge has no provenance in the dataset, the drawer must state "No provenance in dataset". It must not show empty fields.
5. **Edge keys:** an edge key built by the application must carry the **DERIVED** indicator.

### 4.6. Backend Source Placeholders
1. The topology and GraphRAG responses must not substitute `verified://…` or any other placeholder for a missing `source_uri`.
2. A missing `source_uri` must be passed through as missing so that the drawer can state it per §4.2.4.
3. In graph construction, `source_uri` is already a required provenance field. A node or edge without it is a data defect and must be reported, not hidden.

---

## 5. Edge Cases

| Case | Required Behavior |
| :--- | :--- |
| Node has a web URL `source_uri` | Shown as a clickable link exactly as stored, marked DATASET. |
| Node has a local file path `source_uri` | Shown exactly as stored, not clickable, marked DATASET. |
| Node has a descriptive-text `source_uri` (e.g. "CMS Transmittal 12437 (CR 13217)…") | Shown exactly as stored, not clickable, marked DATASET. |
| Node has multiple distinct sources | All listed, each marked DATASET. |
| Bill node missing `congress` and the primary key does not parse | No Congress.gov reference link; the drawer states "congress value missing". |
| Jurisdiction A or D selected | Any contractor link points to Noridian, never CGS. |
| Node label not covered by any reference rule | No reference section is shown; Source Provenance still follows §4.2. |
| Node with no properties, no name and no source | Drawer renders without `{errors}`, with explicit "missing" statements for each. |

---

## 6. Acceptance Criteria (`{correct required outputs}`)

1. **No Fabricated Provenance:** For every node in the IVIG and LTA graphs, the Source Provenance section shows either the exact stored `source_uri` or the text "No recorded source in dataset". No pattern-built URL appears there.
2. **Origin Labels Complete:** Every field visible in the drawer carries a DATASET or DERIVED indicator. Zero unlabeled fields.
3. **No Hardcoded Defaults:** The values `117`, `328`, `3630`, `hr`, `42` and `1395x` never appear in a drawer link unless they are present on that node's dataset record or primary key.
4. **Correct Contractor Attribution:** Opening `JURIS-DME-A` or `JURIS-DME-D` never shows a CGS link. Opening `JURIS-DME-B` or `JURIS-DME-C` never shows a Noridian link.
5. **No `verified://` Strings:** No API response and no drawer field contains a `verified://` value.
6. **Missing-Value Transparency:** A node lacking name, description, properties or source displays explicit "missing" statements for each, with zero `{errors}`.
7. **Verifiability:** For any DATASET-labeled field, the displayed value equals the corresponding value in the `/api/graph/topology` response for that node or edge.
