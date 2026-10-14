# Ticket 002: Backend Graph Topology & Summary Service Alignment

- **Status:** Resolved
- **Claimed by:** wayfinder-read-and-plan
- **Blocked By:** `ticket-001.md`
- **Target Specification:** `functional_specification_015.md` (§3.1 Graph Topology & Summary Service)

## 1. Decision Question

How must `/api/graph/topology` and `/api/graphrag/subgraph` in `src/api/routes.py` be updated to support all 17 entity categories, 54 US states and territories (including `GU`), `FeeScheduleRate` expansion via `HAS_RATE` and `APPLIES_TO_STATE`, deterministic human-readable node display names, and fail-fast HTTP 400 validation?

## 2. Empirical Reconnaissance Findings

1. **Mismatched Node Labels & Relationship Types in `src/api/routes.py` (lines 165–333):**
   - `base_query` (lines 241–247) filters `WHERE NOT n:FeeScheduleEntry` instead of `WHERE NOT n:FeeScheduleRate AND NOT n:FeeScheduleEntry`. When Neo4j contains `FeeScheduleRate` nodes, the default unexpanded topology query returns all `3,710` rate nodes instead of collapsing them.
   - `fee_query` (lines 269–274) and `all_fees_query` (lines 302–314) match `(h:HCPCSCode)-[r2:HAS_FEE_SCHEDULE]->(f:FeeScheduleEntry)-[r1:APPLIES_TO]->(s:State)` instead of the 8-hop schema `(h:ProcedureCode)-[r2:HAS_RATE]->(f:FeeScheduleRate)-[r1:APPLIES_TO_STATE]->(s:State)`.
2. **Broken Display Name Resolution in `convert_node` (`src/api/routes.py` lines 207–213):**
   - `raw_name = props.get("name") or props.get("state_name") or props.get("section") or props.get("title") or pk` fails on 8-hop entities:
     - `CFRSection` has `title: 42` (integer), so `name` resolves to `"42"` instead of `cfr_reference` (`"42 CFR Part 410"`).
     - `StatutorySection` has `section: "1395x"` and `title: 42`, so `name` resolves to `"1395x"` instead of `"Sec. 4133: MEDICARE COVERAGE OF CERTAIN LYMPHEDEMA COMPRESSION TREATMENT ITEMS."`.
     - `USCSection` resolves to `"1395x"` instead of `citation_string` (`"42 U.S.C. 1395x(s)(2)(JJ)"`).
     - `Regulation`, `Transmittal`, `ProcedureCode`, `DiagnosisCode`, `Jurisdiction`, `LobbyingFiling`, and `Policy` lack a `"name"` property and fall back to raw primary keys.
3. **Synthetic Provenance Fallbacks (`src/api/routes.py` lines 226–231):**
   - `convert_edge` injects hardcoded fallback strings (`"verified://cms-policy"`, `"2026-10-13T01:23:54Z"`, `"export-run-001"`).

## 3. Concrete Architectural Decision

1. **Deterministic Display Name Helper (`derive_node_display_name(label: str, pk: str, props: Dict[str, Any]) -> str`):**
   - Implement a shared deterministic display name resolver in `src/api/routes.py` (and `src/graphrag/traversal.py`):
     - `Policy`: `props.get("name") or (f"Policy: {props['keyword']}" if props.get("keyword") else pk)`
     - `Bill`: `f"{props['type'].upper()} {props['number']}: {props['title']}" if props.get("type") and props.get("number") and props.get("title") else (props.get("title") or pk)`
     - `PublicLaw`: `f"Public Law {props['congress']}-{props['number']}" if props.get("congress") and props.get("number") else (props.get("title") or pk)`
     - `StatutorySection`: `f"Sec. {props['statute_section_number']}: {props['heading']}" if props.get("statute_section_number") and props.get("heading") else (props.get("heading") or pk)`
     - `USCSection`: `props.get("citation_string") or pk`
     - `Regulation`: `f"{props['citation']} ({props['docket_id']})" if props.get("citation") and props.get("docket_id") else (props.get("citation") or props.get("document_number") or pk)`
     - `CFRSection`: `props.get("cfr_reference") or pk`
     - `Transmittal`: `f"{props['cr_number']} ({props['transmittal_number']})" if props.get("cr_number") and props.get("transmittal_number") else (props.get("cr_number") or props.get("transmittal_number") or pk)`
     - `CoveragePolicy`: `props.get("title") or props.get("article_id") or pk`
     - `DiagnosisCode`: `f"{props['code']}: {props['description']}" if props.get("code") and props.get("description") else (props.get("code") or pk)`
     - `ProcedureCode`: `f"{props['code']}: {props['short_description']}" if props.get("code") and props.get("short_description") else (props.get("code") or pk)`
     - `FeeScheduleRate`: `f"{props['hcpcs_code']} ({props['state_code']} {'R' if props.get('is_rural') else 'NR'}): ${float(props['fee_amount']):.2f}" if props.get("hcpcs_code") and props.get("state_code") and props.get("fee_amount") is not None else pk`
     - `Jurisdiction`: `f"{props['code']} ({props['contractor_name']})" if props.get("code") and props.get("contractor_name") else (props.get("contractor_name") or pk)`
     - `State`: `props.get("state_name") or props.get("state_code") or pk`
     - `LobbyingFiling`: `f"{props['client_name']} ({props['registrant_name']}, {props['year']})" if props.get("client_name") and props.get("registrant_name") else (props.get("client_name") or pk)`
     - `CBOScore`: `props.get("title") or pk`
     - `LiteratureStudy`: `props.get("title") or pk`
2. **Update `get_graph_topology` in `src/api/routes.py`:**
   - Change `policy_keyword` default to `None` (supporting `"LTA"`, `"ALL"`, or any ingested policy keyword). When `policy_keyword` is provided and `policy_keyword.strip().upper() not in ("", "ALL")`:
     - Normalize `kw = policy_keyword.strip().upper().replace("POLICY-", "")` and verify `MATCH (p:Policy) WHERE p.primary_key = $pk OR toUpper(p.keyword) = $kw RETURN p.primary_key AS pk`. If not found, raise `HTTPException(status_code=400, detail={"error_type": "EntityResolutionError", "message": f"Unrecognized policy keyword '{policy_keyword}'.", "details": {"policy_keyword": policy_keyword}})`.
   - Validate `jurisdiction_filter` and `state_filter` against persisted `:Jurisdiction` and `:State` nodes (which includes all 54 states/territories including `GU`), raising HTTP 400 Bad Request on unrecognized codes.
   - Update `base_query`:
     ```cypher
     MATCH (n:PolicyNode)
     WHERE NOT n:FeeScheduleRate AND NOT n:FeeScheduleEntry
     OPTIONAL MATCH (n)-[r]->(m:PolicyNode)
     WHERE NOT m:FeeScheduleRate AND NOT m:FeeScheduleEntry
     RETURN n, r, m
     ```
   - Update `fee_query` (when `clean_state` is specified):
     ```cypher
     MATCH (h:ProcedureCode)-[r2:HAS_RATE]->(f:FeeScheduleRate)-[r1:APPLIES_TO_STATE]->(s:State {state_code: $state_code})
     RETURN f, r1, s, h, r2
     ```
   - Update `all_fees_query` (when `include_fee_schedules` is True):
     ```cypher
     MATCH (h:ProcedureCode)-[r2:HAS_RATE]->(f:FeeScheduleRate)-[r1:APPLIES_TO_STATE]->(s:State)
     WHERE ($state_pks IS NULL OR s.primary_key IN $state_pks)
     RETURN f, r1, s, h, r2
     LIMIT 4000
     ```
   - In `convert_edge`, read `source_uri`, `selector`, `ingestion_timestamp`, and `run_id` directly from `props` without synthetic default URIs.
3. **Update `get_subgraph_by_anchors` in `src/api/routes.py` (lines 362–466):**
   - Map all 17 canonical labels (`State` -> `"state"`, `DiagnosisCode` -> `"diagnosis"`, `Policy` -> `"policy"`, `ProcedureCode` -> `"hcpcs"`, `Jurisdiction` -> `"jurisdiction"`, `Transmittal` -> `"transmittal"`, `CoveragePolicy` -> `"coveragepolicy"`, and all other labels to `label.lower()`).

## 4. Verification Criteria

- `GET /api/graph/topology` (unexpanded) returns all `165` non-rate nodes across the 16 non-rate entity categories and `173` connecting edges, with zero `FeeScheduleRate` nodes and human-readable `name` attributes on every node.
- `GET /api/graph/topology?state_filter=WI` expands the `70` Wisconsin `FeeScheduleRate` nodes with their `HAS_RATE` and `APPLIES_TO_STATE` edges, scoping `Jurisdiction` to `JURIS-DME-B` and `State` to `STATE-WI`.
- `GET /api/graph/topology?state_filter=GU` returns 200 OK scoped to `STATE-GU` and `JURIS-DME-D`.
- `GET /api/graph/topology?state_filter=INVALID` and `GET /api/graph/topology?jurisdiction_filter=INVALID` return 400 Bad Request.
