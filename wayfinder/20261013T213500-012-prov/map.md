# Wayfinder Map: Node Detail Field Origin Catalog (`20261013T213500-012-prov`)

## Destination
A verified, field-level catalog stating, for every node label and field, whether the value was extracted from a source document, computed or hardcoded by the graph builder, or produced at runtime. The catalog is delivered as [functional_specification_012.md](../../functional_specification_012.md) and feeds [functional_specification_011.md](../../functional_specification_011.md).

## Notes
- **Skills:** `craft-documentation`, `grilling`, `domain-modeling`. Glossary: `LANGUAGE.md`.
- **Standing rule:** classify only from verified exports and raw assets. Never classify from code paths alone. No implementation.
- **Asset directory:** `CoveragePolicies_and_Jurisdictions Addition/assets/20261012T231057-024-zqga/`

## Decisions so far
- [Inventory Exported Node and Edge Fields](tickets/ticket-001.md) — Nodes carry no provenance and no `name`; only ICD10 has `description`; zero CBOScore nodes.
- [Trace Each Exported Field to Its Graph-Builder Origin](tickets/ticket-002.md) — Most identity fields are builder constants; LTA HCPCS, LTA fees, Regulation, LDA and PubMed are file-read.
- [Verify Raw Asset Files Contain the Values Attributed to Them](tickets/ticket-003.md) — Bill and PublicLaw sources are rate-limit errors, the MCD probe is a 404, IVIG statute text is the LTA section, and the CBO key mismatches.
- [Inventory Runtime Derivations in API and Frontend](tickets/ticket-004.md) — Name, label, edge key, `verified://` provenance, theme description, link builder and duplicate jurisdiction table.

## Open (frontier, HITL)
- [Does a Builder Literal Count as "Dataset" in the Drawer?](tickets/ticket-005.md)
- [Treatment of Edges Whose Cited Source Does Not Contain the Asserted Fact](tickets/ticket-006.md)

## Not yet specified
- Whether nodes should gain their own provenance in the dataset (depends on ticket-005).
- Whether the GraphRAG context assembler's literal defaults (e.g. "Public Law 117-328" and "88 FR 77676, CMS-1784-F" in [context_assembler.py](../../src/graphrag/context_assembler.py#L52-L80)) need the same origin treatment in chat answers.

## Out of scope
- Repairing the builders, re-fetching assets or regenerating exports. This effort catalogs origin; it does not fix the data.
