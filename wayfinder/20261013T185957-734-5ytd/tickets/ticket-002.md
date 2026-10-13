# Ticket 002: Authoritative 50-State & 4-Jurisdiction Frontend Registry and Bidirectional Cascading Sync Bus

- **Ticket ID:** `ticket-002`
- **Status:** `RESOLVED`
- **Claimed by:** `wayfinder-read-and-plan`
- **Blocked by:** `ticket-001`
- **Blocks:** `ticket-003`
- **Governing Specification:** `functional_specification_008.md` (Section 4, Requirement 5.1.1, Requirement 5.1.2, Acceptance Criteria 1, 2, 3, 4, 5)

---

## 1. Decision Question

How should the frontend state synchronization bus (`src/frontend/src/context/GraphSyncContext.tsx` and `src/frontend/src/App.tsx`) represent the authoritative CMS DME MAC Jurisdiction-to-State mapping, manage bidirectional cascading between `JURISDICTION` and `STATE` selectors, synchronize canvas topology reloads, and highlight regional contractor subgraphs?

---

## 2. Context & Root Cause Analysis

Currently:
1. `src/frontend/src/context/GraphSyncContext.tsx` tracks only `filterState: string` (defaulting to `"WI"`, line 67) and has no representation of `filterJurisdiction`, no mapping between the 4 CMS DME MAC Jurisdictions (`JURIS-DME-A`, `JURIS-DME-B`, `JURIS-DME-C`, `JURIS-DME-D`) and the 50 US States + territories, and no cascading synchronization logic.
2. `src/frontend/src/App.tsx` (lines 16–25, 67–69) only passes `state_filter` and `policy_keyword` to `/api/graph/topology` and defaults to `fetchTopology('WI', 'LTA')` instead of supporting `jurisdiction_filter` and National Overview (`All Jurisdictions`, `All States`).
3. Selecting a Jurisdiction does not illuminate the regional contractor node (`JURIS-DME-*`) and its covered `State` nodes (`STATE-*`) linked via `COVERS_STATE`.

---

## 3. Locked Architectural Decision

### 3.1 Authoritative Frontend Jurisdiction & State Registry (`src/frontend/src/context/GraphSyncContext.tsx`)
Define and export the authoritative CMS DME MAC mapping constants in `src/frontend/src/context/GraphSyncContext.tsx`:

```ts
export interface StateOption {
  code: string;
  name: string;
  jurisdictionId: string;
}

export interface JurisdictionMetadata {
  id: string;
  label: string;
  shortName: string;
  contractor: string;
  region: string;
  states: { code: string; name: string }[];
}

export const DME_JURISDICTIONS: Record<string, JurisdictionMetadata> = {
  'JURIS-DME-A': {
    id: 'JURIS-DME-A',
    label: 'Jurisdiction A (Northeast - Noridian)',
    shortName: 'Jurisdiction A',
    contractor: 'Noridian Healthcare Solutions',
    region: 'Northeast',
    states: [
      { code: 'CT', name: 'Connecticut' },
      { code: 'DC', name: 'District of Columbia' },
      { code: 'DE', name: 'Delaware' },
      { code: 'MA', name: 'Massachusetts' },
      { code: 'MD', name: 'Maryland' },
      { code: 'ME', name: 'Maine' },
      { code: 'NH', name: 'New Hampshire' },
      { code: 'NJ', name: 'New Jersey' },
      { code: 'NY', name: 'New York' },
      { code: 'PA', name: 'Pennsylvania' },
      { code: 'RI', name: 'Rhode Island' },
      { code: 'VT', name: 'Vermont' },
    ],
  },
  'JURIS-DME-B': {
    id: 'JURIS-DME-B',
    label: 'Jurisdiction B (Midwest - CGS)',
    shortName: 'Jurisdiction B',
    contractor: 'CGS Administrators, LLC',
    region: 'Midwest',
    states: [
      { code: 'IL', name: 'Illinois' },
      { code: 'IN', name: 'Indiana' },
      { code: 'KY', name: 'Kentucky' },
      { code: 'MI', name: 'Michigan' },
      { code: 'MN', name: 'Minnesota' },
      { code: 'OH', name: 'Ohio' },
      { code: 'WI', name: 'Wisconsin' },
    ],
  },
  'JURIS-DME-C': {
    id: 'JURIS-DME-C',
    label: 'Jurisdiction C (South - CGS)',
    shortName: 'Jurisdiction C',
    contractor: 'CGS Administrators, LLC',
    region: 'South',
    states: [
      { code: 'AL', name: 'Alabama' },
      { code: 'AR', name: 'Arkansas' },
      { code: 'CO', name: 'Colorado' },
      { code: 'FL', name: 'Florida' },
      { code: 'GA', name: 'Georgia' },
      { code: 'LA', name: 'Louisiana' },
      { code: 'MS', name: 'Mississippi' },
      { code: 'NC', name: 'North Carolina' },
      { code: 'NM', name: 'New Mexico' },
      { code: 'OK', name: 'Oklahoma' },
      { code: 'PR', name: 'Puerto Rico' },
      { code: 'SC', name: 'South Carolina' },
      { code: 'TN', name: 'Tennessee' },
      { code: 'TX', name: 'Texas' },
      { code: 'VA', name: 'Virginia' },
      { code: 'VI', name: 'U.S. Virgin Islands' },
      { code: 'WV', name: 'West Virginia' },
    ],
  },
  'JURIS-DME-D': {
    id: 'JURIS-DME-D',
    label: 'Jurisdiction D (West - Noridian)',
    shortName: 'Jurisdiction D',
    contractor: 'Noridian Healthcare Solutions',
    region: 'West',
    states: [
      { code: 'AK', name: 'Alaska' },
      { code: 'AZ', name: 'Arizona' },
      { code: 'CA', name: 'California' },
      { code: 'HI', name: 'Hawaii' },
      { code: 'IA', name: 'Iowa' },
      { code: 'ID', name: 'Idaho' },
      { code: 'KS', name: 'Kansas' },
      { code: 'MO', name: 'Missouri' },
      { code: 'MT', name: 'Montana' },
      { code: 'ND', name: 'North Dakota' },
      { code: 'NE', name: 'Nebraska' },
      { code: 'NV', name: 'Nevada' },
      { code: 'OR', name: 'Oregon' },
      { code: 'SD', name: 'South Dakota' },
      { code: 'UT', name: 'Utah' },
      { code: 'WA', name: 'Washington' },
      { code: 'WY', name: 'Wyoming' },
    ],
  },
};

export const STATE_TO_JURISDICTION: Record<string, string> = Object.values(DME_JURISDICTIONS).reduce(
  (acc, juris) => {
    juris.states.forEach((st) => {
      acc[st.code] = juris.id;
    });
    return acc;
  },
  {} as Record<string, string>
);

export const ALL_STATES_SORTED: StateOption[] = Object.values(DME_JURISDICTIONS)
  .flatMap((juris) =>
    juris.states.map((st) => ({
      code: st.code,
      name: st.name,
      jurisdictionId: juris.id,
    }))
  )
  .sort((a, b) => a.name.localeCompare(b.name));
```

### 3.2 Bidirectional Cascading State & Illumination Contract in `GraphSyncContext`
Extend `GraphSyncContextType` and `GraphSyncProvider` in `src/frontend/src/context/GraphSyncContext.tsx`:
- Add state fields:
  - `filterJurisdiction: string` (initialized to `""` for `All Jurisdictions (National Overview)`).
  - `jurisdictionScope: string` (initialized to `""`; set to the selected `JURIS-DME-*` ID when the user explicitly filters by the `JURISDICTION` selector so the `STATE` dropdown cascades to only that jurisdiction's states, and cleared to `""` when `All Jurisdictions` is selected).
  - `filterState: string` (initialized to `""` for `All States (Overview)` so initial load renders the 60 FPS National Overview with fee schedules collapsed, per Acceptance Criterion 5).
  - `availableStates: StateOption[]` computed via `useMemo`:
    - When `jurisdictionScope` is a valid key in `DME_JURISDICTIONS`, returns `DME_JURISDICTIONS[jurisdictionScope].states.map(s => ({ ...s, jurisdictionId: jurisdictionScope })).sort((a, b) => a.name.localeCompare(b.name))`.
    - When `jurisdictionScope` is `""`, returns `ALL_STATES_SORTED` (all 53 states/territories sorted alphabetically by state name).
- Add action methods:
  - `setFilterJurisdiction: (jurisdictionId: string) => void`:
    - Sets `filterJurisdiction` to `jurisdictionId` and `jurisdictionScope` to `jurisdictionId`.
    - Resets `filterState` to `""` (`All States (Overview)`).
    - If `jurisdictionId` is in `DME_JURISDICTIONS`:
      - Highlights the regional contractor node `jurisdictionId` and all covered state nodes `STATE-${st.code}` in `activeNodePKs`, and all `${jurisdictionId}->COVERS_STATE->STATE-${st.code}` edges in `activeEdgeKeys`, with `isIlluminated = true`.
    - If `jurisdictionId` is `""` (`All Jurisdictions`):
      - Calls `clearIllumination()`.
  - `setFilterState: (stateCode: string) => void`:
    - Sets `filterState` to `stateCode`.
    - If `stateCode` is non-empty:
      - Looks up `parentJuris = STATE_TO_JURISDICTION[stateCode] || ""`.
      - Automatically updates `filterJurisdiction` to `parentJuris` so the `JURISDICTION:` selector reflects the governing regional contractor (Requirement 5.1.2.3 & Acceptance Criterion 3).
      - If `jurisdictionScope` was set to a different jurisdiction than `parentJuris`, clears `jurisdictionScope` to `""`.
      - Highlights `STATE-${stateCode}` and `parentJuris` in `activeNodePKs` and `${parentJuris}->COVERS_STATE->STATE-${stateCode}` in `activeEdgeKeys` (`isIlluminated = true`).
    - If `stateCode` is `""` (`All States (Overview)`):
      - If `filterJurisdiction` is set, re-highlights `filterJurisdiction` and all its covered states; otherwise calls `clearIllumination()`.
- Update `submitInquiry` in `src/frontend/src/context/GraphSyncContext.tsx`:
  - Pass `state_code: filterState || undefined` and `jurisdiction_code: filterJurisdiction || undefined` in the `POST /api/graphrag/query` JSON payload (removing the hardcoded `'WI'` fallback when no state is selected).

### 3.3 Topology Fetching Integration (`src/frontend/src/App.tsx`)
Update `fetchTopology` in `src/frontend/src/App.tsx` (lines 16–73):
- Signature: `const fetchTopology = useCallback(async (stateFilter = '', policy = 'LTA', jurisdictionFilter = '') => { ... }, [])`
- Query parameter construction:
  - If `jurisdictionFilter && jurisdictionFilter !== 'ALL'`, append `jurisdiction_filter=${jurisdictionFilter}`.
  - If `stateFilter && stateFilter !== 'ALL'`, append `state_filter=${stateFilter}`.
  - If `policy && policy !== 'ALL'`, append `policy_keyword=${policy}`.
- On initial mount (`useEffect`), call `fetchTopology('', 'LTA', '')` to load the National Overview at 60 FPS with fee schedules collapsed.

---

## 4. Verification Criteria (`{correct required outputs}`)

- Initial load sets `filterJurisdiction = ""`, `filterState = ""`, `availableStates.length === 53` (all 50 US states + DC + PR + VI).
- Calling `setFilterJurisdiction("JURIS-DME-B")` sets `filterJurisdiction = "JURIS-DME-B"`, `filterState = ""`, limits `availableStates` to the 7 Midwestern states (`IL`, `IN`, `KY`, `MI`, `MN`, `OH`, `WI`), and populates `activeNodePKs` with `JURIS-DME-B` and `STATE-IL`..`STATE-WI`.
- Calling `setFilterState("OH")` sets `filterState = "OH"` and automatically updates `filterJurisdiction` to `"JURIS-DME-B"`; subsequently calling `setFilterState("NY")` sets `filterState = "NY"` and automatically updates `filterJurisdiction` to `"JURIS-DME-A"`.
