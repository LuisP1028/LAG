<!-- wayfinder:grilling (HITL) -->
# Treatment of Edges Whose Cited Source Does Not Contain the Asserted Fact

Status: open

## Question
Some edges carry a `source_uri` pointing at a file that does not contain the relationship the edge asserts:
- TARGETS_BILL and ENACTED_AS cite rate-limit error payloads.
- LTA MANDATES_POLICY, GOVERNS and ALLOWS_DIAGNOSIS cite a 404 HTML page.
- COVERS_STATE and APPLIES_TO_JURISDICTION cite a fee CSV that has no jurisdiction-to-state table.

In the drawer, should these edges' provenance be:
- (a) shown as stored, with an "unverified: cited file does not contain this fact" marker;
- (b) shown as stored, without a marker; or
- (c) treated as a data defect that blocks the graph from loading (fail fast)?

This must be answered by the user.

## Blocked By
- [Verify Raw Asset Files Contain the Values Attributed to Them](ticket-003.md)
