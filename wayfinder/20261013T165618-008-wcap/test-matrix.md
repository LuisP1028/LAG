# Authoritative Integration Test Matrix: Visualizer UI Controls, Canvas Stability, and External Government Links

**Governing Specification:** `functional_specification_006.md`  
**Governing Tickets:** `ticket-001.md`, `ticket-002.md`, `ticket-003.md`, `ticket-004.md`, `ticket-005.md`  
**Run ID:** `20261013T165618-008-wcap`  
**Planning Status:** Resolved Frontier  
**Taxonomy Reference:** `LANGUAGE.md`  
**Payload Law Certification:** Authentic Observed Payloads Only (`INV-PAYLOAD-01`, Zero Synthetic Mocks)  
**Boundary Gate:** Implementation Coding Gate Locked (DO NOT CODE YET, `INV-BOUNDARY-01`)  

---

## 1. Master Component-to-Test Mapping Matrix

This matrix establishes the definitive verification specification for each component modified in `handoff/20261013T165618-008-wcap/implementer.txt`.

| Test ID | Target Component | Schema / Contract | Ground-Truth Payload Source | Input Boundary | Expected Output Oracles (`{correct required outputs}`) | Explicit Failure Boundary (`{errors}`) |
|---|---|---|---|---|---|---|
| **INT-TOOLBAR-01** | `FilterToolbar.tsx` | `FilterToolbarProps` | Codebase component interface | `onReloadTopology: vi.fn()` within `GraphSyncProvider` | 1. Jurisdiction `<select>` renders with current value.<br>2. Policy `<select>` renders with current value.<br>3. GraphRAG chat button renders with `"◈ GRAPHRAG CHAT"`.<br>4. Reset Path button renders only when `isIlluminated` is true. | Physics button exists in DOM (`/FREEZE PHYSICS/i` or `/RESUME PHYSICS/i`); title attribute contains "Toggle force physics simulation". |
| **INT-TOOLBAR-02** | `FilterToolbar.tsx` | `FilterToolbarProps` | Codebase component interface | Change events on `<select>` elements | Selecting state "CA" invokes `onReloadTopology("CA", "LTA")`. Selecting policy "IVIG" invokes `onReloadTopology("WI", "IVIG")`. | Callback not fired; arguments incorrect; state unsynchronized. |
| **INT-CONTEXT-01** | `GraphSyncContext.tsx` | `GraphSyncContextType` | TypeScript interface contract | Consumer component mounting `useGraphSync()` | 1. Property `physicsFrozen` is strictly `undefined` / absent (`expect('physicsFrozen' in ctx).toBe(false)`).<br>2. Property `togglePhysicsFrozen` is strictly `undefined` / absent.<br>3. Active states (`activeNodePKs`, `filterState`, etc.) are initialized. | Any reference to `physicsFrozen` or `togglePhysicsFrozen` resolves or throws undefined error at runtime. |
| **INT-CANVAS-01** | `GraphCanvas.tsx` | `GraphCanvasProps` | `neo4j_sample_nodes_10_types.json` | Authentic observed nodes & links | 1. Blueprint HUD renders initially in expanded state: title contains `"◈ LAG KNOWLEDGE BLUEPRINT HUD"` and `"▲"`.<br>2. HUD displays 4 metrics: `"NODES:"`, `"EDGES:"`, `"FPS:"`, `"STATUS:"`.<br>3. HUD container has `pointerEvents: 'auto'`. | HUD missing; metrics missing; HUD rendered with `pointerEvents: 'none'`. |
| **INT-CANVAS-02** | `GraphCanvas.tsx` | `GraphCanvasProps` | `neo4j_sample_nodes_10_types.json` | User clicks HUD container | 1. HUD toggles to Collapsed State: displays `"◈ BLUEPRINT HUD"` and `"▼"`.<br>2. Telemetry metrics body is hidden/removed.<br>3. `e.stopPropagation()` called; canvas background click is NOT triggered.<br>4. Second click restores Expanded State. | HUD fails to toggle; metrics remain visible in collapsed state; click propagates to canvas deselection. |
| **INT-CANVAS-03** | `GraphCanvas.tsx` | `GraphCanvasProps` | Codebase AST / simulation hook | Simulation `useEffect` hook definition | Simulation `useEffect` dependency array strictly contains `[nodes, links]` only. Simulation tick callback delegates to `renderRef.current()`. | Dependency array contains `render`, `hoveredNode`, `selectedNode`, or other transient UI state. |
| **INT-CANVAS-04** | `GraphCanvas.tsx` | `GraphCanvasProps` | `neo4j_sample_nodes_10_types.json` | Pointer move over node coordinates | 1. Canvas cursor switches from `crosshair` to `pointer`.<br>2. Simulation is NOT re-instantiated (`simulationRef.current` identity unchanged).<br>3. `simulation.alpha()` is not reset.<br>4. Node coordinates (`x`, `y`) remain stationary. | Simulation restarts; node positions jitter or repel away from cursor; cursor fails to change. |
| **INT-CANVAS-05** | `GraphCanvas.tsx` | `GraphCanvasProps` | `neo4j_sample_nodes_10_types.json` | Pointer click on node coordinates | 1. Context `selectNode` is invoked with the clicked node on first click.<br>2. Node detail drawer receives node.<br>3. Simulation remains at rest. | Node evasive movement prevents click; multiple clicks required; simulation restarts. |
| **INT-DRAWER-01** | `NodeDetailDrawer.tsx` | `CoveragePolicy` Node | `assets/20261013T165618-008-wcap/neo4j_sample_nodes_10_types.json` (`CMS-MCD-A59508`) | `selectedNode` with `label: 'CoveragePolicy'` | Link Title: `CMS Medicare Coverage Database (A59508)`<br>Link URL: `https://www.cms.gov/medicare-coverage-database/search-results.aspx?keyword=A59508`<br>`target="_blank"`<br>`rel="noopener noreferrer"` | URL targets `/view/article.aspx` (CMS "Invalid Article Version" error); dead link; null link. |
| **INT-DRAWER-02** | `NodeDetailDrawer.tsx` | `PublicLaw` Node | `assets/20261013T165618-008-wcap/neo4j_sample_nodes_10_types.json` (`PLAW-117-328`) | `selectedNode` with `label: 'PublicLaw'` | Link Title: `GPO GovInfo Public Law 117-328`<br>Link URL: `https://www.govinfo.gov/app/details/PLAW-117publ328`<br>`target="_blank"`<br>`rel="noopener noreferrer"` | Missing or non-canonical URL; missing congress/number interpolation. |
| **INT-DRAWER-03** | `NodeDetailDrawer.tsx` | `Bill` Node | `assets/20261013T165618-008-wcap/neo4j_sample_nodes_10_types.json` (`BILL-117-hr-3630`) | `selectedNode` with `label: 'Bill'` | Link Title: `Congress.gov HR 3630 (117th Congress)`<br>Link URL: `https://www.congress.gov/bill/117th-congress/house-bill/3630`<br>`target="_blank"`<br>`rel="noopener noreferrer"` | Hardcoded bill number; bad ordinal formatting; missing bill type slug conversion. |
| **INT-DRAWER-04** | `NodeDetailDrawer.tsx` | `Regulation` Node | `assets/20261013T165618-008-wcap/neo4j_sample_nodes_10_types.json` (`FR-2023-24455`) | `selectedNode` with `label: 'Regulation'` | Link Title: `Federal Register Final Rule (88 FR 77676)`<br>Link URL: `https://www.federalregister.gov/d/2023-24455`<br>`target="_blank"`<br>`rel="noopener noreferrer"` | Unencoded document number; missing citation fallback; null link. |
| **INT-DRAWER-05** | `NodeDetailDrawer.tsx` | `StatutorySection` Node | `assets/20261013T165618-008-wcap/neo4j_sample_nodes_10_types.json` (`USC-42-1395x-s-2-JJ`) | `selectedNode` with `label: 'StatutorySection'` | Link Title: `US Code Title 42 § 1395x (LII)`<br>Link URL: `https://www.law.cornell.edu/uscode/text/42/1395x`<br>`target="_blank"`<br>`rel="noopener noreferrer"` | Inclusion of subsection suffix in Cornell LII URL path (triggers 404); hardcoded mock URL. |
| **INT-DRAWER-06** | `NodeDetailDrawer.tsx` | `ChangeRequest` Node | `assets/20261013T165618-008-wcap/neo4j_sample_nodes_10_types.json` (`CMS-CR-13286`) | `selectedNode` with `label: 'ChangeRequest'` | Link Title: `CMS Transmittals Index (CR 13286)`<br>Link URL: `https://www.cms.gov/medicare/regulations-guidance/transmittals?search=13286`<br>`target="_blank"`<br>`rel="noopener noreferrer"` | Linking to dead PDF `/files/document/r13286cp.pdf` (returns HTTP 404). |
| **INT-DRAWER-07** | `NodeDetailDrawer.tsx` | `Jurisdiction` Node | `assets/20261013T165618-008-wcap/neo4j_sample_nodes_10_types.json` (`JURIS-DME-B`) | `selectedNode` with `label: 'Jurisdiction'`, code contains 'B' | Link Title: `CGS Administrators DME MAC Portal (JURIS-DME-B)`<br>Link URL: `https://www.cgsmedicare.com/`<br>`target="_blank"`<br>`rel="noopener noreferrer"` | Routing to Noridian portal for Jurisdiction B/C; null link. |
| **INT-DRAWER-08** | `NodeDetailDrawer.tsx` | `Jurisdiction` Node | `assets/20261013T165618-008-wcap/neo4j_sample_nodes_10_types.json` (`JURIS-DME-A`) | `selectedNode` with `label: 'Jurisdiction'`, code contains 'A' | Link Title: `Noridian Healthcare Solutions DME MAC Portal (JURIS-DME-A)`<br>Link URL: `https://med.noridianmedicare.com/`<br>`target="_blank"`<br>`rel="noopener noreferrer"` | Routing to CGS portal for Jurisdiction A/D; null link. |
| **INT-DRAWER-09** | `NodeDetailDrawer.tsx` | `HCPCSCode` Node | `assets/20261013T165618-008-wcap/neo4j_sample_nodes_10_types.json` (`HCPCS-Q2052`) | `selectedNode` with `label: 'HCPCSCode'` | Link Title: `CMS DMEPOS Fee Schedule & Coding Reference (Q2052)`<br>Link URL: `https://www.cms.gov/medicare/payment/fee-schedules/dmepos/dmepos-fee-schedule`<br>`target="_blank"`<br>`rel="noopener noreferrer"` | Null link; unencoded procedure code. |
| **INT-DRAWER-10** | `NodeDetailDrawer.tsx` | `ICD10Code` Node | `assets/20261013T165618-008-wcap/neo4j_sample_nodes_10_types.json` (`ICD10-I97.2`) | `selectedNode` with `label: 'ICD10Code'` | Link Title: `CDC ICD-10-CM Clinical Browser (I97.2)`<br>Link URL: `https://icd10cmtool.cdc.gov/?prop=I97.2`<br>`target="_blank"`<br>`rel="noopener noreferrer"` | Null link; missing query parameter `prop`. |
| **INT-DRAWER-11** | `NodeDetailDrawer.tsx` | `LobbyingFiling` Node | `assets/20261013T165618-008-wcap/neo4j_sample_nodes_10_types.json` (`LDA-c8697fc5-...`) | `selectedNode` with `label: 'LobbyingFiling'` | Link Title: `Senate LDA Lobbying Disclosure Search`<br>Link URL: `https://lda.senate.gov/system/public/`<br>`target="_blank"`<br>`rel="noopener noreferrer"` | Null link; dead link. |
| **INT-DRAWER-12** | `NodeDetailDrawer.tsx` | `LiteratureStudy` Node | `assets/20261013T165618-008-wcap/neo4j_sample_nodes_14_types.json` (`PUBMED-25574334`) | `selectedNode` with `label: 'LiteratureStudy'` | Link Title: `PubMed National Library of Medicine (25574334)`<br>Link URL: `https://pubmed.ncbi.nlm.nih.gov/25574334/`<br>`target="_blank"`<br>`rel="noopener noreferrer"` | Null link; missing trailing slash; bad PMID. |

---

## 2. Admissible Test Fixtures (Frozen Authentic Observed Payloads)

Per `INV-PAYLOAD-01`, these fixtures represent the exact, frozen JSON representations captured from live systems during reconnaissance:

### 2.1. Observed Topology Subgraph Fixture (`assets/20261013T165618-008-wcap/neo4j_sample_nodes_10_types.json`)
```json
[
  {
    "id": "BILL-117-hr-3630",
    "primary_key": "BILL-117-hr-3630",
    "label": "Bill",
    "name": "Lymphedema Treatment Act",
    "properties": {
      "number": 3630,
      "congress": 117,
      "introduced_date": "2021-05-28",
      "title": "Lymphedema Treatment Act",
      "type": "hr",
      "primary_key": "BILL-117-hr-3630"
    },
    "radius": 14,
    "color": "#38bdf8",
    "shape": "circle",
    "x": 300,
    "y": 250
  },
  {
    "id": "PLAW-117-328",
    "primary_key": "PLAW-117-328",
    "label": "PublicLaw",
    "name": "Consolidated Appropriations Act, 2023",
    "properties": {
      "number": 328,
      "enacted_date": "2022-12-29",
      "congress": 117,
      "title": "Consolidated Appropriations Act, 2023",
      "primary_key": "PLAW-117-328"
    },
    "radius": 16,
    "color": "#facc15",
    "shape": "circle",
    "x": 450,
    "y": 250
  }
]
```

### 2.2. Observed Directed Links Fixture
```json
[
  {
    "source": "BILL-117-hr-3630",
    "target": "PLAW-117-328",
    "label": "ENACTED_AS",
    "edge_key": "ENACTED_AS:BILL-117-hr-3630->PLAW-117-328",
    "provenance": {
      "source_uri": "https://www.congress.gov/bill/117th-congress/house-bill/3630",
      "selector": "govinfo_plaw_117publ328",
      "ingestion_timestamp": "2026-10-13T01:23:54.891942+00:00",
      "run_id": "20261013T165618-008-wcap"
    }
  }
]
```

---

## 3. Verification Protocol & Execution Laws

### 3.1. Zero-Mock Governance (`INV-PAYLOAD-01`)
1. No synthetic JSON payloads or fabricated node records may be used.
2. Incomplete or optional schema properties (e.g. absent `subsections` or absent `cfr_parts`) must be evaluated as observed sparse packing; tests must not fill them with fake data.
3. Every test fixture must trace back to verified JSON artifacts in `assets/20261013T165618-008-wcap/`.

### 3.2. Assertion Exactness Law (`INV-ASSERTION-01`)
1. Assertions must test exact strings, URLs, and properties prescribed by `functional_specification_006.md` and `matrix.md`.
2. Tests must explicitly assert the negative condition (absence of physics freeze buttons, absence of `physicsFrozen` in context, absence of "Invalid Article Version" link paths).

### 3.3. Coding Gate Affirmation (`INV-BOUNDARY-01`)
- **Status:** **LOCKED**.
- **Affirmation:** This test matrix defines the complete decision space and oracle set for downstream test authoring. Absolutely zero test execution code, test runner configurations, or test scripts have been generated in this session.
