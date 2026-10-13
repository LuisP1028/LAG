<!-- wayfinder:grilling (HITL) -->
# Does a Builder Literal Count as "Dataset" in the Drawer?

Status: open

## Question
Specification 011 defines DATASET as "exists in the knowledge graph dataset". Many exported values were never in a raw source: they were written as constants inside the graph builder. Examples are every Bill, PublicLaw, ChangeRequest, CoveragePolicy, ICD10Code, Jurisdiction and State field, and every IVIG fee.

Should the drawer:
- (a) keep the binary DATASET / DERIVED and label builder literals DATASET;
- (b) label builder literals DERIVED; or
- (c) adopt the four-class origin taxonomy proposed in specification 012 (SOURCE-EXTRACTED, BUILDER-COMPUTED, BUILDER-LITERAL, RUNTIME-DERIVED, plus PIPELINE-METADATA)?

This must be answered by the user. The agent may not answer on the user's behalf.

## Blocked By
- [Verify Raw Asset Files Contain the Values Attributed to Them](ticket-003.md)
