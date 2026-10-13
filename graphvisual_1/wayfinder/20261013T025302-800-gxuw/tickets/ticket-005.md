# Decision Ticket 005: React Browser Graph Canvas, Force-Directed Physics, and High-Density Node Throttling Specification

**Ticket ID:** `ticket-005.md`  
**Scope:** Frontend Visualization Canvas & User Interaction  
**Status:** RESOLVED  
**Claimed By:** `wayfinder-read-and-plan`  
**Blocked By:** `ticket-001.md`

---

## 1. Architectural Question

How must the React graph visualization canvas be engineered to render all 14 node entity types with persistent visual hierarchy, human-readable captions, interactive force physics controls, and high-density node clustering for 3,800+ `:FeeScheduleEntry` nodes to ensure a locked 60 FPS viewport?

---

## 2. Decision and Specification Requirements

### 2.1. Component Architecture
- **Root Directory:** `src/frontend/`
- **Component File Structure:**
  - `src/frontend/components/GraphCanvas.tsx`: Primary graph canvas mounting force-directed rendering.
  - `src/frontend/components/NodeDetailDrawer.tsx`: Dedicated sidebar for inspecting selected node attributes, provenance, and adjacent edges.
  - `src/frontend/components/PhysicsControls.tsx`: Toolbar for play/pause/freeze simulation, zoom-to-fit, and filter toggles.
  - `src/frontend/components/FilterToolbar.tsx`: State jurisdiction selector and policy keyword picker.
  - `src/frontend/styles/graph_theme.ts`: Authoritative color, shape, and size mappings.

### 2.2. Visual Hierarchy and Entity Discrimination
Each of the 14 node types must have deterministic, persistent styling to visually segregate macro federal policies from micro payment rates:

| Entity Label | Badge Color (Hex) | Node Radius | Visual Shape | Caption Format |
|---|---|---|---|---|
| `Policy` | `#7c3aed` (Deep Violet) | 16px | Large Ring | `name` (e.g., "Lymphedema Treatment Act") |
| `Bill` | `#2563eb` (Royal Blue) | 12px | Circle | `name` (e.g., "HR 3630 (117th)") |
| `PublicLaw` | `#1e40af` (Navy) | 14px | Hexagon | `name` (e.g., "PLAW 117-328") |
| `StatutorySection` | `#4f46e5` (Indigo) | 10px | Square | `name` (e.g., "42 U.S.C. § 1395x(s)(2)(JJ)") |
| `Regulation` | `#c2410c` (Rust Orange) | 12px | Diamond | `name` (e.g., "88 FR 77676 (CMS-1784-F)") |
| `ChangeRequest` | `#d97706` (Amber) | 11px | Circle | `name` (e.g., "CMS CR 13286") |
| `CoveragePolicy` | `#059669` (Emerald) | 13px | Double Ring | `name` (e.g., "CMS MCD A59508") |
| `HCPCSCode` | `#0891b2` (Cyan) | 9px | Circle | `primary_key` + short desc (e.g., "A6522: Arm sleeve") |
| `ICD10Code` | `#e11d48` (Rose Red) | 9px | Circle | `primary_key` + short desc (e.g., "I97.2: Postmastectomy") |
| `Jurisdiction` | `#16a34a` (Green) | 12px | Rounded Square | `name` (e.g., "JURIS-DME-B (CGS)") |
| `State` | `#64748b` (Slate) | 8px | Circle | `state_name` (e.g., "Wisconsin") |
| `FeeScheduleEntry`| `#eab308` (Gold) | 6px | Dot | `$fee_amount` (e.g., "$290.47") |
| `LobbyingFiling` | `#9333ea` (Purple) | 8px | Triangle | `registrant_name` |
| `LiteratureStudy` | `#0284c7` (Sky Blue) | 8px | Star | `journal` (e.g., "J Vasc Surg") |

- **Caption Rule:** Labels must render the human-readable `name` property. Raw composite primary keys are strictly prohibited as primary captions to prevent ambiguous contractor confusion.

### 2.3. Force-Directed Physics Controls
- **Simulation Parameters:**
  - Charge strength: `-120`
  - Link distance: `45`
  - Collision radius: `node.radius + 6`
  - Alpha decay: `0.028`
- **Physics Freeze Button:** A toggle button allows the user to immediately pause/lock physics calculations (`alphaTarget(0)`) once layout stabilizes, preventing node jitter during detailed inspection.

### 2.4. High-Density Node Throttling & Clustering
- **The 3,800+ Fee Schedule Challenge:** Rendering all 3,816 `:FeeScheduleEntry` nodes simultaneously degrades frame rates below 20 FPS.
- **Clustering Strategy:**
  1. By default, `:FeeScheduleEntry` nodes are **collapsed** behind their parent `:HCPCSCode` nodes.
  2. The UI provides a **State Filter dropdown** (e.g., "Wisconsin - DME MAC B").
  3. When a state filter is selected, only the ~70 fee schedule nodes for that active state are expanded, maintaining <300 active nodes on the canvas and guaranteeing a steady 60 FPS viewport.

### 2.5. Selection & Detail Inspection Panel
Clicking any node or relationship opens `NodeDetailDrawer`:
- Header: Label badge, primary key, official title/name.
- Properties Table: Complete key-value pairs (effective dates, fee amounts, rural flags, bill titles).
- Government Provenance & Source URLs: Direct, clickable hyperlinks to authoritative government portals:
  - Congress.gov for `Bill` and `PublicLaw`
  - GPO GovInfo for `StatutorySection`
  - Federal Register for `Regulation`
  - CMS MCD for `CoveragePolicy`
  - Senate LDA for `LobbyingFiling`
- Connected Neighbors: List of incoming and outgoing relationships with clickable neighbor pills that re-center the canvas on click.
