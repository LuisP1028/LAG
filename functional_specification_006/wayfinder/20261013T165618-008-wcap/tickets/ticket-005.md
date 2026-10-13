# Decision Ticket 005: Integration Test Decision Mapping, Payload Admissibility Governance, and Verification Architecture

**Ticket ID:** `ticket-005.md`  
**Scope:** Integration Test Planning & Verification Architecture  
**Status:** RESOLVED  
**Claimed By:** `wayfinder-test-plan`  
**Blocked By:** `ticket-001.md`, `ticket-002.md`, `ticket-003.md`, `ticket-004.md`  
**Taxonomy Reference:** `LANGUAGE.md`  
**Governing Specification:** `functional_specification_006.md`  

---

## 1. Architectural Question
How must integration testing be specified, bounded, and verified for the four modified visualizer components (`FilterToolbar.tsx`, `GraphSyncContext.tsx`, `GraphCanvas.tsx`, and `NodeDetailDrawer.tsx`) to deterministically validate all requirements in [`functional_specification_006.md`](file:///Users/diesel/Desktop/LAG/functional_specification_006.md) under strict Payload Law (`INV-PAYLOAD-01`), Assertion Law (`INV-ASSERTION-01`), and Zero-Mock Governance without synthesizing payloads or writing executable test code?

---

## 2. Root Cause, Schema Discovery & Payload Admissibility Governance (`INV-PAYLOAD-01`)

### 2.1. Codebase Schema Authority
Test inputs must bind strictly to the concrete TypeScript interfaces and schemas defined in the active codebase:
1. **`FilterToolbarProps`** (`src/frontend/src/components/FilterToolbar.tsx`):
   - `onReloadTopology: (state: string, policy: string) => void;`
2. **`GraphSyncContextType`** (`src/frontend/src/context/GraphSyncContext.tsx`):
   - Active state containers: `activeNodePKs: Set<string>`, `activeEdgeKeys: Set<string>`, `selectedNode: GraphNode | null`, `seededAnchor: AnchorEntity | null`, `isIlluminated: boolean`, `quickPrompts: string[]`, `filterState: string`, `policyKeyword: string`, `isChatOpen: boolean`, `focusTarget: { x: number; y: number; zoom?: number } | null`.
   - Dispatchers: `selectNode`, `setIlluminatedPath`, `clearIllumination`, `setFilterState`, `setPolicyKeyword`, `setIsChatOpen`, `setFocusTarget`.
   - **Deprecated/Removed Symbols:** `physicsFrozen` and `togglePhysicsFrozen` MUST NOT exist in this type contract.
3. **`GraphCanvasProps`** (`src/frontend/src/components/GraphCanvas.tsx`):
   - `nodes: GraphNode[];`
   - `links: GraphLink[];`
   - `loading: boolean;`
4. **`GraphNode` & `NodeProperties`** (`src/frontend/src/types/graph.ts`):
   - `id: string;`
   - `primary_key: string;`
   - `label: string;`
   - `name: string;`
   - `properties: NodeProperties;`
   - `radius: number;`
   - `color: string;`
   - `shape: string;`
   - Optional simulation fields: `x?: number; y?: number; vx?: number; vy?: number; fx?: number | null; fy?: number | null;`
5. **`NodeDetailDrawerProps`** (`src/frontend/src/components/NodeDetailDrawer.tsx`):
   - `nodes: GraphNode[];`
   - `links: GraphLink[];`

### 2.2. Authentic Observed Payloads Ground Truth
Synthetic fixtures, placeholder strings, and mock objects are strictly forbidden (`INV-PAYLOAD-01`). All test payloads for entity nodes and properties are frozen directly from observed Neo4j data captured during reconnaissance in `assets/20261013T165618-008-wcap/neo4j_sample_nodes_10_types.json` and `assets/20261013T165618-008-wcap/neo4j_sample_nodes_14_types.json`:

1. **`CoveragePolicy` Ground Truth:**
   - Source: `assets/20261013T165618-008-wcap/neo4j_sample_nodes_10_types.json` (lines 114–119)
   - Observed Node Properties:
     ```json
     {
       "article_id": "A59508",
       "policy_type": "Joint DME MAC Policy Article",
       "effective_date": "2024-01-01",
       "title": "Standard Documentation Requirements for Lymphedema Compression Treatment Items",
       "primary_key": "CMS-MCD-A59508"
     }
     ```
2. **`PublicLaw` Ground Truth:**
   - Source: `assets/20261013T165618-008-wcap/neo4j_sample_nodes_10_types.json` (lines 33–40)
   - Observed Node Properties:
     ```json
     {
       "number": 328,
       "enacted_date": "2022-12-29",
       "congress": 117,
       "title": "Consolidated Appropriations Act, 2023",
       "primary_key": "PLAW-117-328"
     }
     ```
3. **`Bill` Ground Truth:**
   - Source: `assets/20261013T165618-008-wcap/neo4j_sample_nodes_10_types.json` (lines 22–28)
   - Observed Node Properties:
     ```json
     {
       "number": 3630,
       "congress": 117,
       "introduced_date": "2021-05-28",
       "title": "Lymphedema Treatment Act",
       "type": "hr",
       "primary_key": "BILL-117-hr-3630"
     }
     ```
4. **`Regulation` Ground Truth:**
   - Source: `assets/20261013T165618-008-wcap/neo4j_sample_nodes_10_types.json` (lines 66–81)
   - Observed Node Properties:
     ```json
     {
       "document_number": "2023-24455",
       "citation": "88 FR 77676",
       "effective_date": "2024-01-01",
       "cfr_parts": ["42 CFR 409", "42 CFR 410", "42 CFR 414", "42 CFR 424", "42 CFR 484", "42 CFR 488", "42 CFR 489"],
       "primary_key": "FR-2023-24455"
     }
     ```
5. **`StatutorySection` Ground Truth:**
   - Source: `assets/20261013T165618-008-wcap/neo4j_sample_nodes_10_types.json` (lines 54–61)
   - Observed Node Properties:
     ```json
     {
       "subsections": ["s", "2", "JJ"],
       "heading": "MEDICARE COVERAGE OF CERTAIN LYMPHEDEMA COMPRESSION TREATMENT ITEMS.",
       "section": "1395x",
       "text": "SEC. 4133. MEDICARE COVERAGE OF CERTAIN LYMPHEDEMA COMPRESSION TREATMENT ITEMS.(a) Coverage.—(1) In general.—Section 1861 of the Social Security Act (42 U.S.C. 1395x)...",
       "title": 42,
       "primary_key": "USC-42-1395x-s-2-JJ"
     }
     ```
6. **`ChangeRequest` Ground Truth:**
   - Source: `assets/20261013T165618-008-wcap/neo4j_sample_nodes_10_types.json` (lines 94–100)
   - Observed Node Properties:
     ```json
     {
       "effective_date": "2024-01-01",
       "transmittal_number": "12349",
       "cr_number": "13286",
       "benefit_category": "LC",
       "primary_key": "CMS-CR-13286"
     }
     ```
7. **`Jurisdiction` Ground Truth:**
   - Source: `assets/20261013T165618-008-wcap/neo4j_sample_nodes_10_types.json` (lines 174–185)
   - Observed Node Properties:
     ```json
     {
       "contractor_name": "CGS Administrators",
       "code": "JURIS-DME-B",
       "name": "JURIS-DME-B (CGS)",
       "primary_key": "JURIS-DME-B"
     }
     ```
8. **`HCPCSCode` Ground Truth:**
   - Source: `assets/20261013T165618-008-wcap/neo4j_sample_nodes_10_types.json` (lines 125–130)
   - Observed Node Properties:
     ```json
     {
       "short_description": "Intravenous immune globulin, items and services in home",
       "code": "Q2052",
       "category": "In-Home IVIG Services",
       "primary_key": "HCPCS-Q2052"
     }
     ```
9. **`ICD10Code` Ground Truth:**
   - Source: `assets/20261013T165618-008-wcap/neo4j_sample_nodes_10_types.json` (lines 159–163)
   - Observed Node Properties:
     ```json
     {
       "code": "I97.2",
       "description": "Postmastectomy lymphedema syndrome",
       "primary_key": "ICD10-I97.2"
     }
     ```
10. **`LobbyingFiling` Ground Truth:**
    - Source: `assets/20261013T165618-008-wcap/neo4j_sample_nodes_10_types.json` (lines 197–204)
    - Observed Node Properties:
      ```json
      {
        "amount": 0.0,
        "year": 2015,
        "registrant_name": "Immune Deficiency Foundation Advocacy",
        "filing_uuid": "c8697fc5-7f3b-4861-8a49-d9e6357ad287",
        "primary_key": "LDA-c8697fc5-7f3b-4861-8a49-d9e6357ad287",
        "client_name": "Immune Deficiency Foundation"
      }
      ```
11. **`LiteratureStudy` Ground Truth:**
    - Source: `assets/20261013T165618-008-wcap/neo4j_sample_nodes_14_types.json` (lines 52–59)
    - Observed Node Properties:
      ```json
      {
        "journal": "Pan Afr Med J",
        "pub_year": 2014,
        "title": "[Psychosocial impact of sickle cell disease in the parents of children living in Kinshasa, Democratic Republic of Congo: a qualitative study].",
        "pmid": 25574334,
        "primary_key": "PUBMED-25574334",
        "doi": "10.11604/pamj.2014.19.5.2830"
      }
      ```

---

## 3. Decision & Technical Specifications for Integration Verification

### 3.1. Component Boundary 1: Navigation Toolbar (`FilterToolbar.tsx`)
- **Governing Requirement:** `functional_specification_006.md` Section 4.1.
- **Verification Harness:** Render `FilterToolbar` within a simulated `GraphSyncProvider` container.
- **Admissible Inputs:**
  - `onReloadTopology: vi.fn()`
- **Oracles & Assertions (`INV-ASSERTION-01`):**
  1. The DOM contains the Jurisdiction select element (`<select value={filterState}>`).
  2. The DOM contains the Policy select element (`<select value={policyKeyword}>`).
  3. The DOM contains the GraphRAG Chat toggle button with text content containing `"◈ GRAPHRAG CHAT"`.
  4. When `isIlluminated` is `true`, the DOM contains `"✕ RESET PATH"`.
  5. The DOM contains **zero** button elements with text matching `/FREEZE PHYSICS/i` or `/RESUME PHYSICS/i`.
  6. The DOM contains **zero** elements with title matching `/Toggle force physics simulation/i`.
  7. Selecting a new jurisdiction or policy fires `onReloadTopology` with the exact selected strings.
- **Explicit Error States (`{errors}`):**
  - Presence of any physics toggle button or control in the DOM.
  - Failure of dropdown select events to trigger `onReloadTopology`.

### 3.2. Component Boundary 2: Context State Management (`GraphSyncContext.tsx`)
- **Governing Requirement:** `ticket-001.md` Section 3.2 and `matrix.md` Section 2.2.
- **Verification Harness:** Mount a test consumer component inside `GraphSyncProvider` to extract the context object.
- **Oracles & Assertions (`INV-ASSERTION-01`):**
  1. Object keys of `useGraphSync()` strictly omit `physicsFrozen` (`expect('physicsFrozen' in context).toBe(false)`).
  2. Object keys of `useGraphSync()` strictly omit `togglePhysicsFrozen` (`expect('togglePhysicsFrozen' in context).toBe(false)`).
  3. All operational state properties (`activeNodePKs`, `activeEdgeKeys`, `selectedNode`, `filterState`, `policyKeyword`, `isChatOpen`, `isIlluminated`) are defined and initialized to specified defaults.
- **Explicit Error States (`{errors}`):**
  - Context exposing deprecated `physicsFrozen` or `togglePhysicsFrozen` properties.
  - Runtime exception thrown when mounting provider without physics state.

### 3.3. Component Boundary 3: Canvas Stability & Collapsible HUD Accordion (`GraphCanvas.tsx`)
- **Governing Requirement:** `functional_specification_006.md` Sections 4.2 & 4.3; `ticket-002.md` & `ticket-003.md`.
- **Verification Harness:** Mount `GraphCanvas` within `GraphSyncProvider` supplying authentic observed `nodes` and `links`.
- **Sub-Verification 3A: Collapsible HUD Accordion:**
  - **Initial State (Expanded):**
    - HUD header text contains `"◈ LAG KNOWLEDGE BLUEPRINT HUD"` and `"▲"`.
    - HUD body renders 4 metrics: `"NODES:"`, `"EDGES:"`, `"FPS:"`, and `"STATUS:"`.
    - HUD container style has `pointerEvents: 'auto'`.
  - **Toggle Interaction:**
    - Trigger `click` on the HUD container.
    - Verified State (Collapsed): HUD header renders `"◈ BLUEPRINT HUD"` and `"▼"`.
    - Metric spans (`NODES:`, `EDGES:`, etc.) are removed from the DOM.
    - Click event propagation is stopped (`e.stopPropagation()`), preventing canvas background click handler execution.
    - Triggering a second `click` restores the Expanded State.
  - **Zero Overlap Boundary:**
    - Collapsed HUD bounding box occupies $\le 180\text{px}$ width at `top: 14, left: 14`, ensuring $>400\text{px}$ clearance from `FilterToolbar` at `top: 14, right: 14`.
- **Sub-Verification 3B: Hover & Interaction Stability:**
  - **Simulation Decoupling Oracle:**
    - Inspect the `useEffect` initializing `d3.forceSimulation`.
    - Dependency array strictly contains `[nodes, links]` only.
    - The callback function for `simulation.on('tick')` delegates to mutable `renderRef.current()`.
  - **Hover Invariance:**
    - Simulate pointer movement over a node coordinates.
    - Cursor changes to `'pointer'`.
    - State updates `hoveredNode` without re-triggering simulation setup (`simulationRef.current` identity is preserved).
    - `simulation.alpha()` is not reset, and node velocities (`vx`, `vy`) and positions (`x`, `y`) remain stationary.
  - **Selection Invariance:**
    - Simulate pointer down on a node.
    - `selectNode` is invoked with the clicked node object.
    - Node position does not displace.
- **Explicit Error States (`{errors}`):**
  - Accordion fails to toggle on click.
  - HUD click triggers canvas node deselection.
  - Simulation restarts on pointer move or node click.
  - Node coordinates jump or evade cursor during hover.

### 3.4. Component Boundary 4: Dynamic Government External Links (`NodeDetailDrawer.tsx`)
- **Governing Requirement:** `functional_specification_006.md` Section 4.4; `ticket-004.md`.
- **Verification Harness:** Render `NodeDetailDrawer` within `GraphSyncProvider`, setting `selectedNode` to authentic observed nodes across all entity types.
- **Detailed Oracle Mapping (`INV-ASSERTION-01`):**

| Entity Type | Authentic Node Sample (`primary_key`) | Expected Link Title | Expected Link URL | Strict Exclusion (Error Check) |
|---|---|---|---|---|
| **`CoveragePolicy`** | `CMS-MCD-A59508` | `CMS Medicare Coverage Database (A59508)` | `https://www.cms.gov/medicare-coverage-database/search-results.aspx?keyword=A59508` | Zero "Invalid Article Version" or `/view/article.aspx` pattern |
| **`PublicLaw`** | `PLAW-117-328` | `GPO GovInfo Public Law 117-328` | `https://www.govinfo.gov/app/details/PLAW-117publ328` | Non-templated or mock URL |
| **`Bill`** | `BILL-117-hr-3630` | `Congress.gov HR 3630 (117th Congress)` | `https://www.congress.gov/bill/117th-congress/house-bill/3630` | Static hardcoded bill slug |
| **`Regulation`** | `FR-2023-24455` | `Federal Register Final Rule (88 FR 77676)` | `https://www.federalregister.gov/d/2023-24455` | Unencoded or missing doc number |
| **`StatutorySection`** | `USC-42-1395x-s-2-JJ` | `US Code Title 42 § 1395x (LII)` | `https://www.law.cornell.edu/uscode/text/42/1395x` | Non-canonical or trailing sub-clause in URL path |
| **`ChangeRequest`** | `CMS-CR-13286` | `CMS Transmittals Index (CR 13286)` | `https://www.cms.gov/medicare/regulations-guidance/transmittals?search=13286` | Dead link `/files/document/r13286cp.pdf` |
| **`Jurisdiction` (B/C)** | `JURIS-DME-B` | `CGS Administrators DME MAC Portal (JURIS-DME-B)` | `https://www.cgsmedicare.com/` | `null` or wrong contractor |
| **`Jurisdiction` (A/D)** | `JURIS-DME-A` | `Noridian Healthcare Solutions DME MAC Portal (JURIS-DME-A)` | `https://med.noridianmedicare.com/` | `null` or wrong contractor |
| **`HCPCSCode`** | `HCPCS-Q2052` | `CMS DMEPOS Fee Schedule & Coding Reference (Q2052)` | `https://www.cms.gov/medicare/payment/fee-schedules/dmepos/dmepos-fee-schedule` | `null` or dead link |
| **`ICD10Code`** | `ICD10-I97.2` | `CDC ICD-10-CM Clinical Browser (I97.2)` | `https://icd10cmtool.cdc.gov/?prop=I97.2` | `null` or dead link |
| **`LobbyingFiling`** | `LDA-c8697fc5-7f3b-4861-8a49-d9e6357ad287` | `Senate LDA Lobbying Disclosure Search` | `https://lda.senate.gov/system/public/` | `null` or dead link |
| **`LiteratureStudy`** | `PUBMED-25574334` | `PubMed National Library of Medicine (25574334)` | `https://pubmed.ncbi.nlm.nih.gov/25574334/` | `null` or dead link |

- **Security & Tab Attributes:**
  - All external anchor tags (`<a>`) must have `target="_blank"` and `rel="noopener noreferrer"`.
- **Explicit Error States (`{errors}`):**
  - Returning `null` for any of the 10 specified entity types.
  - Generating static mock URLs that do not reflect node properties.
  - Generating CMS MCD link with `/view/article.aspx?articleid=...` that triggers "Invalid Article Version".
  - Generating dead CMS Change Request PDF link (`r13286cp.pdf`).
  - Missing `rel="noopener noreferrer"` attribute.

---

## 4. Documentation Sufficiency & Evaluation Parameters

Under the strict definitions in [`LANGUAGE.md`](file:///Users/diesel/Desktop/LAG/LANGUAGE.md):
- **`{errors}`**: Explicit failure conditions mapped across DOM regressions, state leaks, simulation jitter, and invalid URL patterns.
- **`{correctness}`**: Exact relational alignment between authentic observed node properties, TypeScript interface definitions, and expected DOM/link outputs.
- **`{functionality}`**: Complete verification planning of an uncluttered, stable visualizer interface with verified external government provenance links.
- **`{correct required outputs}`**: Unambiguous, objectively measurable test assertions documented for every touched component.
- **`{sufficient}`**: The documentation provides 100% schema grounding, authentic observed payloads, explicit expected values, and clear failure criteria. Zero ambiguity remains.
- **`{insufficient}`**: Hand-mocked payloads, speculative fields, or handwritten expected blobs not derived from authentic payloads or schemas. None exist in this plan.

---

## 5. Acceptance Criteria
1. Every component modified in `handoff/20261013T165618-008-wcap/implementer.txt` has a designated verification harness, input schema, authentic payload ground truth, and oracle assertion set.
2. Zero mock objects or synthetic payloads are planned; all node tests bind to authentic observed payloads from `assets/20261013T165618-008-wcap/`.
3. All external link oracles match verified live government endpoints with zero dead links or version error URLs.
4. Exactly zero lines of test execution code, test fixtures, or test scripts have been authored in this session (`INV-BOUNDARY-01`).
