# Ticket 003: Dual Jurisdiction and State Navigation Selectors (`FilterToolbar.tsx`)

- **Ticket ID:** `ticket-003`
- **Status:** `RESOLVED`
- **Claimed by:** `wayfinder-read-and-plan`
- **Blocked by:** `ticket-001`, `ticket-002`
- **Blocks:** None
- **Governing Specification:** `functional_specification_008.md` (Requirement 5.1.1, Requirement 5.1.2, Acceptance Criteria 1, 2, 3, 4)

---

## 1. Decision Question

How must `FilterToolbar` (`src/frontend/src/components/FilterToolbar.tsx`) be structured to render two distinct, clearly labeled navigation dropdowns (`JURISDICTION:` and `STATE:`), display the exact specified options, and synchronize cascading selections with `GraphSyncContext` and `onReloadTopology`?

---

## 2. Context & Root Cause Analysis

Currently, `src/frontend/src/components/FilterToolbar.tsx` (lines 9–80):
1. Renders a single `<select>` labeled `JURISDICTION:` that is actually bound to `filterState` and lists only 5 hardcoded states (`WI`, `IL`, `CA`, `NY`, `TX`) plus an `All States` option.
2. Omits the remaining 45 US states and territories (`DC`, `PR`, `VI`).
3. Provides no control to select CMS DME MAC Jurisdictions (`JURIS-DME-A`, `JURIS-DME-B`, `JURIS-DME-C`, `JURIS-DME-D`).
4. Defines `onReloadTopology: (state: string, policy: string) => void` without a `jurisdiction` parameter.

---

## 3. Locked Architectural Decision

### 3.1 Props Interface (`src/frontend/src/components/FilterToolbar.tsx`)
Update `FilterToolbarProps`:
```ts
interface FilterToolbarProps {
  onReloadTopology: (state: string, policy: string, jurisdiction: string) => void;
}
```

### 3.2 Dedicated `JURISDICTION:` Selector (Requirement 5.1.1)
1. **Control Label:** `<span>` with text `JURISDICTION:`.
2. **Select Element:** `aria-label="JURISDICTION"` and `data-testid="jurisdiction-select"`, bound to `value={filterJurisdiction}` and `onChange={handleJurisdictionChange}`.
3. **Options (exact values and labels per Requirement 5.1.1.2):**
   - `<option value="">All Jurisdictions (National Overview)</option>`
   - `<option value="JURIS-DME-A">Jurisdiction A (Northeast - Noridian)</option>`
   - `<option value="JURIS-DME-B">Jurisdiction B (Midwest - CGS)</option>`
   - `<option value="JURIS-DME-C">Jurisdiction C (South - CGS)</option>`
   - `<option value="JURIS-DME-D">Jurisdiction D (West - Noridian)</option>`
4. **Selection Handler (`handleJurisdictionChange`):**
   ```ts
   const handleJurisdictionChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
     const jurisVal = e.target.value;
     setFilterJurisdiction(jurisVal);
     onReloadTopology('', policyKeyword, jurisVal);
   };
   ```

### 3.3 Dedicated `STATE:` Selector (Requirement 5.1.2)
1. **Control Label:** `<span>` with text `STATE:`.
2. **Select Element:** `aria-label="STATE"` and `data-testid="state-select"`, bound to `value={filterState}` and `onChange={handleStateChange}`.
3. **Options (Requirement 5.1.2.2):**
   - Default overview option: `<option value="">All States (Overview)</option>`
   - Dynamic state options mapped from `availableStates` (provided by `useGraphSync()`, sorted alphabetically by state name, and dynamically filtered to the selected jurisdiction's states when a jurisdiction is selected via `JURISDICTION:`):
     ```tsx
     {availableStates.map((st) => (
       <option key={st.code} value={st.code}>
         {st.name} ({st.code})
       </option>
     ))}
     ```
4. **Selection Handler (`handleStateChange`):**
   ```ts
   const handleStateChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
     const stateVal = e.target.value;
     setFilterState(stateVal);
     const parentJuris = stateVal ? (STATE_TO_JURISDICTION[stateVal] || filterJurisdiction) : filterJurisdiction;
     onReloadTopology(stateVal, policyKeyword, parentJuris);
   };
   ```

### 3.4 Policy Selector Handler (`handlePolicyChange`)
Update `handlePolicyChange` to pass `filterJurisdiction` as the third argument:
```ts
const handlePolicyChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
  const val = e.target.value;
  setPolicyKeyword(val);
  onReloadTopology(filterState, val, filterJurisdiction);
};
```

---

## 4. Verification Criteria (`{correct required outputs}`)

- Toolbar renders both `JURISDICTION:` and `STATE:` labels and `<select>` controls.
- `JURISDICTION:` dropdown contains the 5 exact options specified in Requirement 5.1.1.2.
- `STATE:` dropdown contains `All States (Overview)` plus all 53 states/territories in alphabetical order when `All Jurisdictions` is active, and narrows to the 7 Midwestern states (`IL`, `IN`, `KY`, `MI`, `MN`, `OH`, `WI`) when `Jurisdiction B` is selected.
- Selecting `OH` in `STATE:` updates `JURISDICTION:` value to `"JURIS-DME-B"` and triggers `onReloadTopology("OH", policyKeyword, "JURIS-DME-B")`.
