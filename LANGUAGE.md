---
name: system-glossary-evaluation-parameters
hostname: local-workspace
description: A comprehensive glossary defining the strict evaluation parameters used for assessing code errors, correctness, functionality, and documentation sufficiency within the system, alongside legislative and healthcare data extraction domain taxonomy.
---

# Evaluation Parameters

## {errors}
- Explicit failure states surfaced during the execution of a component.
- **Qualifiers:** Stack traces, syntax errors, unhandled exceptions, compilation failures, non-zero exit codes, fatal timeouts, or severe warnings that halt execution.

## {correctness}
- The precise, local execution of a specific component, verifying that it performs its designated task without logical flaws, even if no explicit `{errors}` are thrown.
- **Qualifiers:** The code processes data properly, math is accurate, loops terminate as expected, and data types are respected.

## {functionality}
- The broader, global objective or business logic the component is meant to achieve within the larger system.
- **Qualifiers:** Does the outcome solve the user's initial problem? Does it integrate seamlessly with the rest of the app?

## {correct required outputs}
- The exact, literal expected state after a component executes successfully. This must be objectively measurable.
- **Qualifiers:** Specific terminal log messages, exact return values (e.g., true, null), precise file state changes (e.g., "generates a file named data.json containing 5 specific keys"), or specific API response codes (e.g., 200 OK).

## {sufficient}
- The state of documentation where absolutely no ambiguity remains, and the coding assistant can proceed to implementation without guessing or hallucinating context.
- **Qualifiers:** All necessary file structures are provided, dependencies are listed, step-by-step logic is clearly outlined, edge cases are defined, and the `{correct required outputs}` are established.

## {insufficient}
- The state of documentation where critical context is missing, ambiguous, or contradictory, requiring the assistant to make assumptions to write code.
- **Qualifiers:** Missing file schemas, undefined variables, vague instructions (e.g., "make it look better"), missing error-handling parameters, or lack of context regarding how a component interacts with the broader codebase.

# Legislative & Healthcare Data Pipeline Domain Glossary

## {Policy Keyword}
- A single string parameter (e.g., `"LTA"`) representing the policy topic. Serves as the sole runtime human input to the discovery pipeline.

## {Target_Bill_IDs}
- An array of composite bill identifiers (`congress: integer`, `type: string`, `number: integer`) discovered in Phase 1 and handed off to Phase 5 for lobbying and economic context.
- **Composite Format:** `BILL-[congress]-[type]-[number]`

## {Enacted_Law_ID}
- The public law identifier linked to the enacted bill (`congress: integer`, `law_number: integer`) discovered in Phase 1 and handed off to Phase 2 for statutory codification lookup.
- **Composite Format:** `PLAW-[congress]-[number]`

## {US_Code_Citations}
- An array of codified statutory citations (`title: integer`, `section: string`, `subsections: string[]`, `citation_string: string`) extracted in Phase 2 from the enacted public law XML and handed off to Phase 3 as regulatory authority anchors.
- **Composite Format:** `USC-[title]-[section]-[subsection]`

## {Operational_Filters}
- Administrative classifications (e.g., benefit categories, pricing indicator codes, billing modifiers, transmittal IDs) extracted in Phase 3 from agency Final Rules and directives, handed off to Phase 4 for deterministic procedure code isolation.

## {Clinical_Citations}
- External scientific literature references (e.g., PubMed IDs, DOIs) cited in regulatory preambles as evidentiary justifications, extracted in Phase 3 and handed off to Phase 5.

## {HCPCS / CPT Codes}
- Standardized medical procedure codes isolated in Phase 4 strictly by filtering against `Operational_Filters` without keyword search.
- **Composite Format:** `HCPCS-[code]`

## {Direct Path (Native Keys)}
- Fields that exist as explicit, first-class key-value pairs in JSON responses or dedicated attributes/elements in XML nodes. Accessible via direct path pointers (e.g., JSONPath).

## {Structural Traversal (Derived Keys)}
- Fields embedded within semi-structured document trees, markup text, or regulatory preambles. Accessible via deterministic XPath or DOM selectors without unanchored heuristic regex scanning.
