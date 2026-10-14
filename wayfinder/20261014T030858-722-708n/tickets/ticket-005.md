# Ticket 005: Frontend 17-Category Visual Taxonomy, Node Detail Drawer, and 54-Jurisdiction Filter Alignment

## 1. Objective & Scope
Align the frontend visualization canvas, theme registry, node inspection drawer, filter toolbar, and synchronization context with Section 4 of `functional_specification_015.md`:
1. Render and distinguish all `17` 8-hop entity categories (`Policy`, `Bill`, `PublicLaw`, `StatutorySection`, `USCSection`, `Regulation`, `CFRSection`, `Transmittal`, `CoveragePolicy`, `DiagnosisCode`, `ProcedureCode`, `FeeScheduleRate`, `Jurisdiction`, `State`, `LobbyingFiling`, `CBOScore`, `LiteratureStudy`) with distinct colors, shapes, and type labels.
2. Display all persisted properties in `NodeDetailDrawer.tsx` without omitting `description` or injecting hardcoded fallback identifiers (`'117'`, `'328'`, `'3630'`, `'42'`, `'1395x'`).
3. Support all `54` US states, districts, and territories (including `GU` — Guam under `JURIS-DME-D`) and populate the Policy domain filter dynamically from persisted `Policy` nodes in the graph.

---

## 2. Current Implementation Defects (Grounded in Codebase Audit)

### 2.1 `src/frontend/src/styles/graph_theme.ts` (Lines 5–97)
1. **Missing 8-Hop Entity Categories in `NODE_THEME_REGISTRY`:**
   - Only defines 14 keys using legacy labels (`ChangeRequest`, `HCPCSCode`, `ICD10Code`, `FeeScheduleEntry`).
   - Completely lacks `USCSection`, `CFRSection`, `Transmittal`, `ProcedureCode`, `DiagnosisCode`, `FeeScheduleRate`, and `CBOScore`. Any node with those 7 labels falls back to the generic `#64748b` slate circle (`Knowledge Graph Entity`) in `getNodeVisual()`.

### 2.2 `src/frontend/src/components/GraphCanvas.tsx` (Lines 276–360)
1. **Uniform Circle Rendering Ignoring `visual.shape`:**
   - Lines 277–280 always call `ctx.arc(node.x, node.y, radius, 0, Math.PI * 2)` regardless of `visual.shape`, failing the Section 4.1 requirement to assign and render distinct shapes per entity category.
2. **Always-Visible Hub Labels Missing New Structural Categories:**
   - Line 157 and line 330 check `['Policy', 'PublicLaw', 'Jurisdiction', 'CoveragePolicy']` and omit `Transmittal`, `Regulation`, `USCSection`, and `CFRSection`.

### 2.3 `src/frontend/src/components/NodeDetailDrawer.tsx` (Lines 47–157, 238–240, 312–345)
1. **Hardcoded Fallback Identifiers in `getGovernmentSourceLink()` (Lines 77–109):**
   - `PublicLaw` (lines 78–79): Uses `|| '117'` and `|| '328'`, and reads `props.number` instead of `props.public_law_number`.
   - `Bill` (lines 86–88): Uses `|| 117`, `|| 'hr'`, `|| '3630'`, and reads `props.type` and `props.number` instead of `props.bill_type` and `props.bill_number`.
   - `Regulation` (line 95): Uses `.replace(/^FR-/, '')` instead of `.replace(/^(?:REG-)?FR-/, '')`.
   - `StatutorySection` (lines 101–108): Treats `StatutorySection` as a US Code section with hardcoded fallbacks `'42'` and `'1395x'`, instead of linking `StatutorySection` (`STAT-...`) to GPO GovInfo Public Law (`PLAW-{congress}publ{law}`) and `USCSection` (`USC-...`) to Cornell LII (`props.title_number` and `props.section_code`).
   - Missing cases for `USCSection`, `CFRSection`, `Transmittal`, `ProcedureCode`, `DiagnosisCode`, `FeeScheduleRate`, and `CBOScore`.
   - `CoveragePolicy` (lines 70–75): Strips `^CMS-MCD-` and always links to the CMS MCD search URL even when `publication_type === 'DME_MAC_JOINT_PUBLICATION'` (`DME-MAC-COPE147943`).
2. **Omission of `description` Attribute in Properties Table (Line 313):**
   - Line 313 filters out `description` (`!['primary_key', 'name', 'label', 'description'].includes(k)`), which hides `DiagnosisCode.description` from the Entity Attributes table.
3. **Array Property Formatting (Lines 325–335):**
   - Array attributes (`clinical_prerequisites`, `cfr_parts`, `superseded_transmittal_numbers`, `subsections`) are rendered via `String(val)` which concatenates array elements without spacing or structure.

### 2.4 `src/frontend/src/context/GraphSyncContext.tsx` & `src/frontend/src/components/FilterToolbar.tsx` & `src/frontend/src/utils/promptGenerator.ts`
1. **Missing Guam (`GU`) in `DME_JURISDICTIONS['JURIS-DME-D']` (`GraphSyncContext.tsx` lines 96–121):**
   - `JURIS-DME-D.states` has 17 entries instead of 18 (missing `{ code: 'GU', name: 'Guam' }`), resulting in 53 states in `ALL_STATES_SORTED` instead of 54.
2. **Hardcoded `IVIG` in `FilterToolbar.tsx` ( line 137 ) & `GraphSyncContext.tsx` (lines 194–195, 252):**
   - `FilterToolbar.tsx` hardcodes `<option value="IVIG">IVIG (Immune Globulin)</option>` even when only `POLICY-LTA` is persisted in the database.
   - `GraphSyncContext.tsx` initial `quickPrompts` and `selectNode` reference `IVIG`, `CMS MCD A59508`, `HCPCSCode`, and `ICD10Code`.
3. **Missing 8-Hop Labels in `promptGenerator.ts` (lines 7–38):**
   - Lacks cases for `USCSection`, `CFRSection`, `Transmittal`, `ProcedureCode`, `DiagnosisCode`, `FeeScheduleRate`, and `CBOScore`.

---

## 3. Target Architecture & Exact File Edits

### 3.1 `src/frontend/src/styles/graph_theme.ts`
Expand `NodeVisualConfig['shape']` and `NODE_THEME_REGISTRY` to cover all 17 canonical entity categories with distinct colors, shapes, radii, and descriptions:
- `Policy`: `badgeColor: '#7c3aed'`, `radius: 18`, `shape: 'ring'`, `description: 'Federal Legislative Policy Domain'`
- `Bill`: `badgeColor: '#2563eb'`, `radius: 13`, `shape: 'circle'`, `description: 'Congressional Legislative Bill'`
- `PublicLaw`: `badgeColor: '#1e40af'`, `radius: 15`, `shape: 'hexagon'`, `description: 'Enacted Public Law Statute'`
- `StatutorySection`: `badgeColor: '#4f46e5'`, `radius: 12`, `shape: 'square'`, `description: 'Public Law Statutory Section (USLM)'`
- `USCSection`: `badgeColor: '#6366f1'`, `radius: 12`, `shape: 'pentagon'`, `description: 'Codified United States Code Section'`
- `Regulation`: `badgeColor: '#c2410c'`, `radius: 13`, `shape: 'diamond'`, `description: 'Federal Register Final Rule'`
- `CFRSection`: `badgeColor: '#ea580c'`, `radius: 11`, `shape: 'octagon'`, `description: 'Code of Federal Regulations Part/Section'`
- `Transmittal`: `badgeColor: '#d97706'`, `radius: 12`, `shape: 'rounded_square'`, `description: 'CMS Manual Change Request Transmittal'`
- `CoveragePolicy`: `badgeColor: '#059669'`, `radius: 15`, `shape: 'double_ring'`, `description: 'Medicare Coverage Policy / DME MAC Article'`
- `DiagnosisCode`: `badgeColor: '#e11d48'`, `radius: 10`, `shape: 'triangle'`, `description: 'ICD-10-CM Clinical Diagnosis Code'`
- `ProcedureCode`: `badgeColor: '#0891b2'`, `radius: 10`, `shape: 'hexagon'`, `description: 'HCPCS Level II Procedure / Supply Code'`
- `FeeScheduleRate`: `badgeColor: '#eab308'`, `radius: 6`, `shape: 'dot'`, `description: 'DMEPOS State Fee Schedule Rate'`
- `Jurisdiction`: `badgeColor: '#16a34a'`, `radius: 13`, `shape: 'rounded_square'`, `description: 'DME MAC Regional Administrative Contractor'`
- `State`: `badgeColor: '#64748b'`, `radius: 9`, `shape: 'circle'`, `description: 'US State / Territorial Jurisdiction'`
- `LobbyingFiling`: `badgeColor: '#9333ea'`, `radius: 9`, `shape: 'triangle'`, `description: 'Senate LDA Lobbying Disclosure Filing'`
- `CBOScore`: `badgeColor: '#0d9488'`, `radius: 10`, `shape: 'diamond'`, `description: 'Congressional Budget Office Cost Estimate'`
- `LiteratureStudy`: `badgeColor: '#0284c7'`, `radius: 9`, `shape: 'star'`, `description: 'PubMed Peer-Reviewed Clinical Study'`
(Retain legacy aliases `ChangeRequest`, `HCPCSCode`, `ICD10Code`, `FeeScheduleEntry` mapped to their respective visual configs for backward compatibility.)

### 3.2 `src/frontend/src/components/GraphCanvas.tsx`
1. Implement `drawNodePolygon(ctx, x, y, radius, shape)` supporting `'ring'`, `'circle'`, `'hexagon'`, `'square'`, `'pentagon'`, `'diamond'`, `'octagon'`, `'double_ring'`, `'rounded_square'`, `'dot'`, `'triangle'`, and `'star'`, and invoke it for both the node fill/clip path and border stroke (plus inner concentric ring stroke for `'ring'` and `'double_ring'`).
2. Render non-occluding node captions displaying the entity's derived human-readable `name` and `primary_key` (e.g., `[${node.primary_key}] ${node.name}` when zoomed or active/selected/hovered, or concise `node.name` at overview zoom for key structural hubs `Policy`, `PublicLaw`, `StatutorySection`, `USCSection`, `Regulation`, `CFRSection`, `Transmittal`, `CoveragePolicy`, `Jurisdiction`).

### 3.3 `src/frontend/src/components/NodeDetailDrawer.tsx`
1. **Deterministic Provenance Links (`getGovernmentSourceLink`) Without Fallbacks:**
   - First check if any incident edge on the selected node has an `http://` or `https://` `provenance.source_uri` matching the node's authority; otherwise construct the link strictly from present node attributes (returning `null` if required fields are absent):
     - `Bill`: Requires `props.congress`, `props.bill_type`, and `props.bill_number` $\to$ `https://www.congress.gov/bill/${getOrdinal(Number(props.congress))}-congress/${getBillTypeSlug(String(props.bill_type))}/${props.bill_number}`.
     - `PublicLaw`: Requires `props.congress` and `props.public_law_number` $\to$ `https://www.govinfo.gov/app/details/PLAW-${props.congress}publ${props.public_law_number.split('-').pop()}`.
     - `StatutorySection`: Requires `props.public_law_id` (matching `PLAW-(\d+)-(\d+)`) $\to$ `https://www.govinfo.gov/app/details/PLAW-${c}publ${n}`.
     - `USCSection`: Requires `props.title_number` and `props.section_code` $\to$ `https://www.law.cornell.edu/uscode/text/${props.title_number}/${props.section_code}`.
     - `Regulation`: Requires `props.document_number` $\to$ `https://www.federalregister.gov/d/${props.document_number}`.
     - `CFRSection`: Requires `props.title_number` and `props.part_number` $\to$ `https://www.ecfr.gov/current/title-${props.title_number}/part-${props.part_number}`.
     - `Transmittal`: Requires `props.cr_number` $\to$ `https://www.cms.gov/medicare/regulations-guidance/transmittals?search=${props.cr_number}`.
     - `CoveragePolicy`: Requires `props.article_id`. If `props.publication_type === 'DME_MAC_JOINT_PUBLICATION'`, link to CGS/Noridian DME MAC publication or edge `source_uri`; if `CMS_MCD_LCD`, link to CMS MCD search for `props.article_id`.
     - `ProcedureCode`: Requires `props.code` $\to$ `https://www.cms.gov/medicare/payment/fee-schedules/dmepos/dmepos-fee-schedule`.
     - `FeeScheduleRate`: Requires `props.hcpcs_code` $\to$ `https://www.cms.gov/medicare/payment/fee-schedules/dmepos/dmepos-fee-schedule`.
     - `DiagnosisCode`: Requires `props.code` $\to$ `https://icd10cmtool.cdc.gov/?prop=${encodeURIComponent(String(props.code))}`.
     - `Jurisdiction`: Requires `props.contractor_name` or `props.jurisdiction_code`.
     - `CBOScore`: Uses `props.source_url` if present, else `https://www.cbo.gov/`.
     - `LobbyingFiling`: Uses `props.filing_uuid` $\to$ `https://lda.senate.gov/filings/public/filing/${props.filing_uuid}/print/`.
     - `LiteratureStudy`: Requires `props.pmid` $\to$ `https://pubmed.ncbi.nlm.nih.gov/${props.pmid}/`.
2. **Complete Property Rendering in Entity Attributes Table:**
   - Filter out only internal identity keys `['primary_key', 'name', 'label']` so `description` and all domain properties are rendered.
   - Format array values (`Array.isArray(val)`) as a clean vertical list or semicolon-delimited badges, boolean values as `'Yes'` / `'No'` (`true` / `false`), and currency fields (`fee_amount`, `ceiling`, `floor`) with `$` formatting alongside raw values.
3. **Edge Provenance Display in Connected Topology List:**
   - Include edge provenance metadata (`source_uri`, `selector`) in each connected relationship card when present.

### 3.4 `src/frontend/src/context/GraphSyncContext.tsx`, `src/frontend/src/components/FilterToolbar.tsx`, `src/frontend/src/App.tsx`, `src/frontend/src/utils/promptGenerator.ts`
1. **`GraphSyncContext.tsx`:**
   - Add `{ code: 'GU', name: 'Guam' }` to `DME_JURISDICTIONS['JURIS-DME-D'].states` (sorted alphabetically) so `ALL_STATES_SORTED` has all 54 US states and territories.
   - Add `availablePolicies: { keyword: string; label: string }[]` and `setAvailablePolicies` to `GraphSyncContextType`, initialized with `[{ keyword: 'LTA', label: 'LTA (Lymphedema Treatment Act)' }]` and updated dynamically by `App.tsx` from `Policy` nodes in the topology response.
   - Update initial `quickPrompts` and `selectNode` contextual prompts to use the 17 8-hop labels (`CoveragePolicy`, `Transmittal`, `ProcedureCode`, `DiagnosisCode`, `FeeScheduleRate`, `StatutorySection`, `USCSection`, `Regulation`, `CFRSection`, `PublicLaw`, `Bill`, `Policy`, `Jurisdiction`, `State`, `CBOScore`, `LobbyingFiling`, `LiteratureStudy`) and persisted IDs (`DME-MAC-COPE147943`, `TR-CR13286`, `HCPCS-A6522`).
2. **`FilterToolbar.tsx`:**
   - Render the `POLICY` `<select>` options dynamically from `availablePolicies` in `useGraphSync()` plus `<option value="ALL">All Ingested Policies</option>`, removing the hardcoded `IVIG` option when `POLICY-IVIG` is not present in the graph.
3. **`App.tsx`:**
   - When `fetchTopology` receives `data.nodes`, extract all `Policy` nodes (`n.label === 'Policy'`) and update `availablePolicies` in `GraphSyncContext` using `n.properties.policy_keyword` and `n.name`.
4. **`promptGenerator.ts`:**
   - Add explicit cases for all 17 entity labels (`Policy`, `Bill`, `PublicLaw`, `StatutorySection`, `USCSection`, `Regulation`, `CFRSection`, `Transmittal`, `CoveragePolicy`, `DiagnosisCode`, `ProcedureCode`, `FeeScheduleRate`, `Jurisdiction`, `State`, `LobbyingFiling`, `CBOScore`, `LiteratureStudy`).

---

## 4. Verification Criteria
1. `NODE_THEME_REGISTRY` contains all 17 entity categories with distinct colors, shapes, and descriptions.
2. `DME_JURISDICTIONS` and `ALL_STATES_SORTED` include all 54 US states and territories (`50 states + DC + PR + VI + GU`).
3. `NodeDetailDrawer` displays all persisted properties for any selected node (including `DiagnosisCode.description`, `CoveragePolicy.clinical_prerequisites`, `Transmittal.superseded_transmittal_numbers`, `ProcedureCode.pricing_methodology`, `FeeScheduleRate.fee_amount`/`ceiling`/`floor`/`is_rural`) and constructs external government links strictly from persisted properties without hardcoded fallback strings.
4. `npm run build` in `src/frontend` succeeds with zero TypeScript or Vite bundling errors.
