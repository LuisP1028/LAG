# Ticket 003: Hop 2 — Dynamic GovInfo USLM XML Package Resolution & Structural Section/USC Citation Traversal

## Status
**Locked** — Architectural Decision & Edit Plan

## Context & Problem Statement
[`src/graph/tier2_statutory.py`](file:///Users/diesel/Desktop/LAG/.sandcastle/worktrees/agent-plan-20261013T225035-656-0beg/src/graph/tier2_statutory.py) (lines 41–147) currently exhibits the defects documented in [`functional_specification_013.md`](file:///Users/diesel/Desktop/LAG/.sandcastle/worktrees/agent-plan-20261013T225035-656-0beg/functional_specification_013.md) Section 3 & Section 4 (Hop 2):
1. **Ignored Public Law Handoff & Static File Path:** `ingest_statutory_tier` always opens `stage2_uslm_plaw_117_328_sec4133.xml` regardless of `handoff.public_law_id`, only checking `if handoff.public_law_id != "PLAW-117-328"` to raise an error rather than deriving the GovInfo package ID (`PLAW-{congress}publ{law_number}`) from `handoff.public_law_id`.
2. **Hardcoded Section Targeting:** Lines 53–56 hardcode `target_sec_num = "4133"` for `"LTA"` and `"4134"` for `"IVIG"`, rather than structurally traversing `<section>` elements in the USLM XML package (`phase2_govinfo_plaw_117publ328.xml` or `phase2_uslm_plaw_117_328_sec4133.xml`) by matching `<heading>` and `<content>` against the policy scope in `handoff.policy_keyword`.
3. **Incomplete U.S. Code Citation Extraction:** While `phase2_uslm_plaw_117_328_sec4133.xml` contains `<ref href="/us/usc/t42/s1395x">42 U.S.C. 1395x</ref>`, `<ref href="/us/usc/t42/s1395l/a/1">42 U.S.C. 1395l(a)(1)</ref>`, `<ref href="/us/usc/t42/s1395m">42 U.S.C. 1395m</ref>`, and `<ref href="/us/usc/t42/s1395w-3/a/2">42 U.S.C. 1395w-3(a)(2)</ref>` plus `<quotedContent>` adding subparagraph `(JJ)` (`42 U.S.C. 1395x(s)(2)(JJ)`), subsection `(mmm)` (`42 U.S.C. 1395x(mmm)`), subparagraph `(GG)` (`42 U.S.C. 1395l(a)(1)(GG)`), subsection `(z)` (`42 U.S.C. 1395m(z)`), and `"lymphedema compression treatment items"` in `42 U.S.C. 1395w-3(a)(2)(D)`, the current parser only extracts two hardcoded subsection regex patterns (`1395x(s)(2)(JJ)` and `1395x(mmm)`) and misses the full `amended_usc_citations` list and `uslm_section_path` required by `StatutoryHandoff`.

## Architectural Decisions Locked

### 1. Dynamic GovInfo Package Derivation & USLM XML Resolution
In [`src/graph/tier2_statutory.py`](file:///Users/diesel/Desktop/LAG/.sandcastle/worktrees/agent-plan-20261013T225035-656-0beg/src/graph/tier2_statutory.py):
- Parse `handoff.public_law_id` matching `^PLAW-(\d+)-(\d+)$` (raising `StatutorySectionNotFoundError` immediately if malformed) to construct the canonical GovInfo package identifier `f"PLAW-{congress}publ{law_number}"` (e.g., `"PLAW-117publ328"`).
- Resolve the USLM XML document dynamically:
  1. Check local empirical GovInfo packages in `asset_dir` matching `f"*{congress}*{law_number}*.xml"` (preferring the targeted USLM excerpt `phase2_uslm_plaw_117_328_sec4133.xml` / `stage2_uslm_plaw_117_328_sec4133.xml` for fast parsing when it contains the matching `<pLaw>` root, or falling back to streaming `xml.etree.ElementTree.iterparse` over `phase2_govinfo_plaw_117publ328.xml`).
  2. If not present locally, fetch `https://api.govinfo.gov/packages/PLAW-{congress}publ{law_number}/xml?api_key={api_key}` (or `https://www.govinfo.gov/content/pkg/PLAW-{congress}publ{law_number}/xml/PLAW-{congress}publ{law_number}.xml`).
  3. Raise `StatutorySectionNotFoundError` if the XML cannot be resolved or fails XML parsing.

### 2. Structural `<section>` Discovery by Policy Keyword & Heading Semantics
Instead of hardcoding `"4133"` or `"4134"`:
- Derive search tokens from `handoff.policy_keyword` and the introduced bill title fetched in Hop 0 (e.g., `"LTA"` / `"Lymphedema Treatment Act"` $\to$ token `"lymphedema"`; `"IVIG"` / `"Intravenous Immune Globulin"` $\to$ tokens `"intravenous immune globulin"`, `"immune globulin"`).
- Traverse all `<section>` elements in the USLM XML namespace (`http://schemas.gpo.gov/xml/uslm`):
  - Extract `@identifier` (e.g., `"/us/pl/117/328/dFF/tIV/stD/s4133"`), `<num>@value` (`"4133"`), and `<heading>` (`"Medicare coverage of lymphedema compression treatment items"`).
  - Score each `<section>` by keyword token matches in `<heading>` (highest weight) and `<content>` / `<chapeau>`.
  - Select the highest-scoring `<section>`. If no `<section>` matches the policy tokens, raise `StatutorySectionNotFoundError`.

### 3. Complete U.S. Code Citation & Effective Date Extraction
From the matched `<section>` DOM subtree:
- Extract all `<ref href="/us/usc/...">` nodes and combine each base USC citation with its adjacent `<quotedContent>` amended subparagraph/subsection designator where present:
  - For Section 4133 (`LTA`), deterministically extract:
    1. `"42 U.S.C. 1395x(s)(2)(JJ)"` (node ID `"USC-42-1395x-s-2-JJ"`, subsection `"(s)(2)(JJ)"`)
    2. `"42 U.S.C. 1395x(mmm)"` (node ID `"USC-42-1395x-mmm"`, subsection `"(mmm)"`)
    3. `"42 U.S.C. 1395l(a)(1)(GG)"` (node ID `"USC-42-1395l-a-1-GG"`, subsection `"(a)(1)(GG)"`)
    4. `"42 U.S.C. 1395m(z)"` (node ID `"USC-42-1395m-z"`, subsection `"(z)"`)
    5. `"42 U.S.C. 1395w-3(a)(2)(D)"` (node ID `"USC-42-1395w-3-a-2-D"`, subsection `"(a)(2)(D)"`)
  - For Section 4134 (`IVIG`), deterministically extract:
    1. `"42 U.S.C. 1395x(s)(2)(Z)"` (node ID `"USC-42-1395x-s-2-Z"`, subsection `"(s)(2)(Z)"`)
    2. `"42 U.S.C. 1395x(zz)"` (node ID `"USC-42-1395x-zz"`, subsection `"(zz)"`)
    3. `"42 U.S.C. 1395u(o)(8)"` (node ID `"USC-42-1395u-o-8"`, subsection `"(o)(8)"`)
    4. `"42 U.S.C. 1395m(j)(5)(E)"` (node ID `"USC-42-1395m-j-5-E"`, subsection `"(j)(5)(E)"`)
    5. `"42 U.S.C. 1395l(a)(1)(HH)"` (node ID `"USC-42-1395l-a-1-HH"`, subsection `"(a)(1)(HH)"`)
- Extract the statutory effective date from `<date>` elements inside the `Effective Date` subsection (e.g., `<date date="2024-01-01">January 1, 2024</date>` $\to$ `"2024-01-01"`).
- Fail fast with `StatutorySectionNotFoundError` if `amended_usc_citations` is empty.

### 4. Graph Topology & Return Contract (`StatutoryHandoff` / `Tier2Handoff`)
- Emit `StatutorySectionNode` (`id="STAT-117-328-SEC-4133"`) and `USCSectionNode` records for each extracted USC citation, linked via:
  - `(:PublicLaw {id: "PLAW-117-328"})-[:CONTAINS]->(:StatutorySection {id: "STAT-117-328-SEC-4133"})`
  - `(:StatutorySection {id: "STAT-117-328-SEC-4133"})-[:AMENDS]->(:USCSection)`
- Return `Tier2Handoff` (subclass of `StatutoryHandoff`) populated with `public_law_id`, `uslm_section_path`, `statute_section_number`, `statute_heading`, `amended_usc_citations`, `effective_date`, `statutory_section_id`, and `usc_section_ids`.

## Target Files & Line-Range Edits
- [`src/graph/tier2_statutory.py`](file:///Users/diesel/Desktop/LAG/.sandcastle/worktrees/agent-plan-20261013T225035-656-0beg/src/graph/tier2_statutory.py) (lines 1–148):
  - Replace hardcoded `stage2_uslm_plaw_117_328_sec4133.xml` path and hardcoded `"4133"`/`"4134"` branching with dynamic GovInfo package resolution (`PLAW-{congress}publ{number}`), structural `<section>` heading/content matching, full `<ref href="/us/usc/...">` + `<quotedContent>` USC citation extraction, and `<date>` effective date extraction.
  - Raise `StatutorySectionNotFoundError` on all Hop 2 failure conditions.

## Verification Criteria
- Given `LegislativeHandoff` for `"LTA"`, `ingest_statutory_tier` discovers `<section identifier="/us/pl/117/328/dFF/tIV/stD/s4133">`, extracts all 5 amended USC citations (`42 U.S.C. 1395x(s)(2)(JJ)`, `42 U.S.C. 1395x(mmm)`, `42 U.S.C. 1395l(a)(1)(GG)`, `42 U.S.C. 1395m(z)`, `42 U.S.C. 1395w-3(a)(2)(D)`), and sets `effective_date="2024-01-01"`.
- Passing a `LegislativeHandoff` with an unresolvable `public_law_id` or a keyword with no matching USLM `<section>` raises `StatutorySectionNotFoundError`.
