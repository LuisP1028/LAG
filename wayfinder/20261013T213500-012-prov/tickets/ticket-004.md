<!-- wayfinder:task (AFK) -->
# Inventory Runtime Derivations in API and Frontend

Status: resolved

## Question
Which values shown in the Node Detail Drawer are produced after the dataset, by the API (`src/api/routes.py`) or the frontend (`src/frontend/src`)?

## Blocked By
- [Inventory Exported Node and Edge Fields](ticket-001.md)

## Resolution

**API — `convert_node` / `convert_edge`** ([routes.py](file:///Users/diesel/Desktop/LAG/src/api/routes.py#L165-L238))
- `name` is the first present value among `name`, `state_name`, `section`, `title` and `primary_key`.
- `label` is inferred from the primary-key prefix when Neo4j labels are absent; otherwise it is the literal `"PolicyNode"`.
- `edge_key` is built as `source->LABEL->target`.
- Missing edge provenance is replaced with literals: `verified://cms-policy`, `direct`, `2026-10-13T01:23:54Z` and `export-run-001`.
- GraphRAG [traversal.py](file:///Users/diesel/Desktop/LAG/src/graphrag/traversal.py#L787-L792) does the same, using `verified://federal-statute`.

**Frontend** ([App.tsx](file:///Users/diesel/Desktop/LAG/src/frontend/src/App.tsx#L58-L86), [NodeDetailDrawer.tsx](file:///Users/diesel/Desktop/LAG/src/frontend/src/components/NodeDetailDrawer.tsx))
- **Name, properties and edges:** a missing name becomes the primary key; missing properties become a `{primary_key}` stub; a missing edge key is rebuilt; missing provenance becomes empty strings.
- **Source link:** `getGovernmentSourceLink` builds a URL pattern per label, filled with literal defaults (`117`, `328`, `3630`, `hr`, `42`, `1395x`). It chooses the Jurisdiction contractor by testing whether the code contains "B" or "C".
- **Description:** "System Description" falls back to the per-label `description` in [graph_theme.ts](file:///Users/diesel/Desktop/LAG/src/frontend/src/styles/graph_theme.ts).
- **Neighbours:** a neighbour's label falls back to `"Node"`.
- **Jurisdiction table:** [GraphSyncContext.tsx](file:///Users/diesel/Desktop/LAG/src/frontend/src/context/GraphSyncContext.tsx#L32-L134) holds `DME_JURISDICTIONS`, a second literal jurisdiction-to-state table independent of the graph.
