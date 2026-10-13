<!-- wayfinder:task (AFK) -->
# Inventory Exported Node and Edge Fields

Status: resolved

## Question
Which fields does each node label and edge carry in the knowledge graph exports (`exports/lta_knowledge_graph.json`, `exports/ivig_knowledge_graph.json`), and does any node carry `name`, `description`, `source_uri`, or `url`?

## Blocked By
None

## Resolution
Measured by parsing both exports.

- **LTA:** 3,852 nodes and 7,562 edges. **IVIG:** 183 nodes and 289 edges.
- **Labels present in both:** Policy, Bill (2), PublicLaw, StatutorySection, Regulation, ChangeRequest, CoveragePolicy, HCPCSCode (LTA 70, IVIG 5), ICD10Code (3), Jurisdiction (4), State (53), FeeScheduleEntry (LTA 3,710, IVIG 106), LobbyingFiling (2), LiteratureStudy (2).
- **CBOScore:** zero nodes in either export.
- **Node-level fields:**
  - No node carries `name`, `source_uri`, `url` or a `properties` wrapper.
  - Only the 3 ICD10Code nodes per export carry `description`.
- **Node provenance:** nodes carry **no provenance at all**. Provenance exists only on edges.
- **Edge fields:** `source_pk`, `label`, `target_pk`, `provenance{source_uri, selector, ingestion_timestamp, run_id}`.
- **Distinct edge `source_uri` values:**
  - LTA: 8 local asset file paths.
  - IVIG: 7 local asset paths, plus one remote URL (`https://www.cms.gov/medicare-coverage-database/view/article.aspx?articleid=59588`, 9 edges) and one free-text string (`CMS Transmittal 12437 (CR 13217): Home IVIG Fee Schedule`, 212 edges).
