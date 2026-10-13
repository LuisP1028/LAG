<!-- wayfinder:task (AFK) -->
# Trace Each Exported Field to Its Graph-Builder Origin

Status: resolved

## Question
For every exported node field, does the graph builder (`src/graph/tier*.py`) read the value from a raw asset file, compute it from extracted values, or write a literal constant?

## Blocked By
- [Inventory Exported Node and Edge Fields](ticket-001.md)

## Resolution
Traced line by line.

- [tier1_legislative.py](file:///Users/diesel/Desktop/LAG/src/graph/tier1_legislative.py#L72-L115)
  - The LTA Bill and the PublicLaw use `.get(key, literal)`.
  - The IVIG Bill (H.R. 3808) and H.R. 2617 are pure literals.
- [tier2_statutory.py](file:///Users/diesel/Desktop/LAG/src/graph/tier2_statutory.py#L96-L123)
  - `title=42`, `section="1395x"` and `subsections` are literals.
  - `heading` comes from XML only when the target section is located; otherwise it is a literal default.
  - `text` is the itertext of the located section, or of the root element when the section is not located.
- [tier3_regulatory.py](file:///Users/diesel/Desktop/LAG/src/graph/tier3_regulatory.py#L62-L102)
  - Regulation fields use `.get(key, literal)`.
  - Every ChangeRequest field is a literal chosen by an IVIG/LTA branch.
- [tier4a_coverage.py](file:///Users/diesel/Desktop/LAG/src/graph/tier4a_coverage.py#L36-L144)
  - Every CoveragePolicy field and every ICD10Code is a literal.
  - The IVIG HCPCS codes are literals.
  - The LTA HCPCS `code` and `short_description` are read from the CSV; `category` is a substring heuristic (`"day"` / `"nght"`).
- [tier4b_fee_schedule.py](file:///Users/diesel/Desktop/LAG/src/graph/tier4b_fee_schedule.py#L37-L259)
  - Jurisdictions and States come from the literal `DME_MAC_JURISDICTIONS` table.
  - LTA fees are read from the CSV, except `year=2024`, which is a literal.
  - IVIG fees are literal: `409.84`, `Q2052`, `year=2024`, repeated across every state and rural flag.
- [tier5_context.py](file:///Users/diesel/Desktop/LAG/src/graph/tier5_context.py#L66-L186)
  - The LDA `filing_uuid` and `year` are read from the file. `amount` is the file's income, or `0.0` when absent.
  - The registrant and client are read from the file for LTA, but are literals for IVIG.
  - PubMed fields are read from the file.
  - CBO reads the key `costEstimates`.
- **Pipeline metadata:** Policy `run_id` and `timestamp` and every edge's `ingestion_timestamp` and `run_id`.
- **Builder-authored:** every edge `selector` string.
- **Builder-computed:** primary keys, computed in [models.py](file:///Users/diesel/Desktop/LAG/src/graph/models.py).
- **Export script:** no script that writes `exports/*.json` exists in the repository (searched `*.py` for `knowledge_graph.json` and `export-run`).
