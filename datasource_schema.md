### 2. Payload Schema & Field Feasibility Assessment

Before writing extraction logic, every target payload must be inspected to evaluate **data availability and structural accessibility**. This requires classifying how the target data exists inside the payload:

* **Native Structured Fields (First-Class Keys):**
* Verifying whether the target key is returned as an explicit key-value pair in a JSON response or a dedicated XML tag/attribute.
* *Assessment goal:* If the field is explicit (e.g., a direct public law reference property within a bill's action object), extraction is deterministic and requires only a direct path/pointer.


* **Semi-Structured Markup & Document Trees (Derived Keys):**
* Verifying cases where the information is *not* a clean top-level metadata field, but embedded within structured markup (such as USLM XML sections, preambles, or regulatory footnotes).


* *Assessment goal:* Determining the exact XML node hierarchy, tag conventions (e.g., `<section>`, `<amends>`, `<ref>`), or document structure required to isolate the amendment text and extract statutory citations without heuristic guessing.




* **Payload Completeness & Edge Conditions:**
* Checking if the payload structure changes across different congresses, agencies, or publication years.
* Confirming that the upstream payload contains enough foreign key fidelity to satisfy the handoff contract for the downstream stage.





In short: you want to inspect the raw payloads from the relevant sources to verify where clean fields exist versus where deterministic DOM/XML traversal is needed to isolate our foreign keys before writing any pipeline code.