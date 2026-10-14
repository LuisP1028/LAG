# Ticket 002: Hop 0 & Hop 1 — Dynamic Congress.gov Keyword Discovery & Hybrid Omnibus Related-Bill Lineage

## Status
**Locked** — Architectural Decision & Edit Plan

## Context & Problem Statement
[`src/graph/tier1_legislative.py`](file:///Users/diesel/Desktop/LAG/.sandcastle/worktrees/agent-plan-20261013T225035-656-0beg/src/graph/tier1_legislative.py) (lines 38–157) currently suffers from three architectural defects identified in [`functional_specification_013.md`](file:///Users/diesel/Desktop/LAG/.sandcastle/worktrees/agent-plan-20261013T225035-656-0beg/functional_specification_013.md) Section 3 & Section 4 (Hops 0 and 1):
1. **Hardcoded Keyword Branching:** `ingest_legislative_tier` (lines 67–70, 99–149) branches on `if clean_kw in ("LTA", "LYMPHEDEMA"): ... elif clean_kw == "IVIG": ...` and skips executing an actual Congress.gov search query (`GET /v3/bill`).
2. **Swallowed API Errors & Hardcoded Fallback:** `_fetch_congress_bill` (lines 28–35) catches `Exception` on HTTP 429 (`DEMO_KEY` rate limit) or connection errors and returns `{}` so the caller proceeds to inject hardcoded `H.R. 3630`, `H.R. 2617`, and `PLAW-117-328` nodes.
3. **Missing Hop 0 $\to$ Hop 1 Hybrid Related-Bill Traversal:** Instead of inspecting `bill.laws` and dynamically traversing `GET /v3/bill/{congress}/{type}/{number}/relatedbills` when `laws` is empty (to discover the omnibus enacting vehicle `H.R. 2617` and its `laws[0].number == "117-328"`), the existing code hardcodes the nodes and also creates a direct `Bill-117-hr-3630 -[:ENACTED_AS]-> PLAW-117-328` shortcut edge that violates the specification's omnibus lineage (`BILL-117-hr-3630 -[:INCORPORATED_INTO]-> BILL-117-hr-2617 -[:ENACTED_AS]-> PLAW-117-328`).

## Architectural Decisions Locked

### 1. Hop 0: Dynamic Congress.gov Bill Search & Discovery (`discover_bill_by_keyword`)
Implement deterministic Hop 0 discovery in [`src/graph/tier1_legislative.py`](file:///Users/diesel/Desktop/LAG/.sandcastle/worktrees/agent-plan-20261013T225035-656-0beg/src/graph/tier1_legislative.py):
- **Primary Endpoint Contract:** Query Congress.gov API v3 (`https://api.congress.gov/v3/bill?query={quote(policy_keyword)}&sort=relevancy&format=json&api_key={api_key}`) or local verified Congress.gov empirical cache (`CoveragePolicies_and_Jurisdictions Addition/assets/20261012T231057-024-zqga/stage1_congress_bill_hr3630.json` and `stage1_congress_bill_hr2617.json` / search response index) when operating against the verified asset corpus or when an injectable `http_client` / `asset_dir` is provided.
- **Keyword Expansion & Relevance Ranking:** Normalize `{Policy Keyword}` (trimming whitespace; rejecting empty string with `LegislativeResolutionError`). Support both acronym queries (e.g., `"LTA"`, `"IVIG"`) and full policy phrase queries (e.g., `"Lymphedema Treatment Act"`, `"Intravenous Immune Globulin"`). Score candidate `bills[*]` by matching `title`, `shortTitle`, `policyArea.name`, or introduced advocacy bill metadata, selecting the highest-relevance advocacy bill (`Target_Bill_ID = f"BILL-{congress}-{bill_type.lower()}-{number}"`, e.g., `"BILL-117-hr-3630"` for LTA).
- **Fail-Fast Boundary:** Raise `LegislativeResolutionError` immediately if `policy_keyword` is empty, if the search yields 0 matching candidate bills, or if an unrecoverable API authentication/schema failure occurs.

### 2. Hop 1: Hybrid Direct / Related-Bills Omnibus Lineage Traversal (`resolve_enacted_law`)
Implement deterministic Hop 1 lineage resolution in [`src/graph/tier1_legislative.py`](file:///Users/diesel/Desktop/LAG/.sandcastle/worktrees/agent-plan-20261013T225035-656-0beg/src/graph/tier1_legislative.py):
- **Branch A (Direct Enactment):** Inspect the candidate bill detail (`GET /v3/bill/{congress}/{type}/{number}`). If `bill.laws` is non-empty, extract `laws[0].number` (e.g., `"117-328"`) and `laws[0].type` (`"Public Law"`), setting `enacting_bill_id = introduced_bill_id` and `public_law_id = f"PLAW-{congress}-{law_num.split('-')[-1]}"`. Emit `BillNode` and `PublicLawNode` connected by `(:Bill)-[:ENACTED_AS]->(:PublicLaw)`.
- **Branch B (Omnibus / Related Bill Incorporation):** If `bill.laws` is empty or absent:
  1. Query `GET /v3/bill/{congress}/{type}/{number}/relatedbills` (or read `relatedBills` from the bill detail / verified Congress.gov fixture).
  2. Filter `relatedBills[*]` for vehicles containing `laws[*]` or `latestAction.text` matching `"Became Public Law No: {congress}-{law_seq}"` (e.g., `H.R. 2617`, *Consolidated Appropriations Act, 2023*, `Public Law No: 117-328`, enacted `2022-12-29`).
  3. Set `enacting_bill_id = f"BILL-{rel_congress}-{rel_type.lower()}-{rel_number}"` (`"BILL-117-hr-2617"`) and `public_law_id = f"PLAW-{rel_congress}-{law_seq}"` (`"PLAW-117-328"`).
  4. Emit two `BillNode` records (`BILL-117-hr-3630` and `BILL-117-hr-2617`) and one `PublicLawNode` (`PLAW-117-328`) with strictly linear omnibus edges:
     - `(:Bill {id: "BILL-117-hr-3630"})-[:INCORPORATED_INTO]->(:Bill {id: "BILL-117-hr-2617"})`
     - `(:Bill {id: "BILL-117-hr-2617"})-[:ENACTED_AS]->(:PublicLaw {id: "PLAW-117-328"})`
     *(Do NOT emit the false direct shortcut edge `BILL-117-hr-3630 -[:ENACTED_AS]-> PLAW-117-328` when `introduced_bill_id != enacting_bill_id`.)*
- **Fail-Fast Boundary:** Raise `EnactedLawNotFoundError` if neither Branch A (`bill.laws`) nor Branch B (`relatedBills[*].laws` / `"Became Public Law No:"`) resolves to an enacted Public Law.

### 3. Return Contract (`LegislativeHandoff` / `Tier1Handoff`)
Return a validated `Tier1Handoff` (subclass of `LegislativeHandoff`) containing:
- `policy_keyword`: original keyword (e.g., `"LTA"`)
- `introduced_bill_id`: `"BILL-117-hr-3630"` (and alias `bill_id`)
- `enacting_bill_id`: `"BILL-117-hr-2617"` (and alias `enacting_vehicle_id`)
- `public_law_id`: `"PLAW-117-328"`
- `congress`: `117`
- `enacted_date`: `"2022-12-29"`

## Target Files & Line-Range Edits
- [`src/graph/tier1_legislative.py`](file:///Users/diesel/Desktop/LAG/.sandcastle/worktrees/agent-plan-20261013T225035-656-0beg/src/graph/tier1_legislative.py) (lines 1–158):
  - Replace `_fetch_congress_bill` silent exception suppression with deterministic Congress.gov API + verified empirical fixture resolution (`stage1_congress_bill_hr3630.json`, `stage1_congress_bill_hr2617.json`, and related-bills metadata).
  - Implement `_search_congress_bills(policy_keyword)` (Hop 0) and `_resolve_enacted_law_from_bill(bill_meta)` (Hop 1).
  - Remove the false direct edge `BILL-117-hr-3630 -[:ENACTED_AS]-> PLAW-117-328` on lines 135–140 when `introduced_bill_id != enacting_bill_id`, preserving only `introduced_bill -[:INCORPORATED_INTO]-> enacting_bill -[:ENACTED_AS]-> public_law`.
  - Raise `LegislativeResolutionError` on Hop 0 failures and `EnactedLawNotFoundError` on Hop 1 failures.

## Verification Criteria
- Calling `ingest_legislative_tier(engine, "LTA")` or `ingest_legislative_tier(engine, "Lymphedema Treatment Act")` returns `LegislativeHandoff` with `introduced_bill_id="BILL-117-hr-3630"`, `enacting_bill_id="BILL-117-hr-2617"`, `public_law_id="PLAW-117-328"`, `congress=117`, `enacted_date="2022-12-29"`.
- Calling `ingest_legislative_tier(engine, "")` or an unknown keyword `"NONEXISTENT_POLICY_XYZ"` raises `LegislativeResolutionError`.
- Calling Hop 1 on an un-enacted bill with no enacted related bills raises `EnactedLawNotFoundError`.
