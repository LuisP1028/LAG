The functional requirement is to perform a **source mapping and schema feasibility audit** before building any extraction scripts: first identifying the exact endpoints/repositories across each phase, and then inspecting their raw response payloads to determine whether each required foreign key exists as a native structured field or requires structural parsing from markup.

---

### 1. Data Source Identification

For each phase in the chain, the system must map the abstract data source to specific authoritative endpoints and formats capable of accepting the upstream handoff key and yielding the next key:

* **Phase 1 (Legislative Discovery):**
* *Role:* Accepts the policy keyword and resolves historical bills, bill actions, and public law enactments.


* *Source Type:* Federal legislative APIs providing bill summaries, related bills, and legislative actions.




* **Phase 2 (Statutory Codification):**
* *Role:* Accepts the enacted public law identifier and provides full statutory text.


* *Source Type:* Government publishing repositories providing bulk legislative markup (specifically USLM XML).




* **Phase 3 (Administrative Rulemaking):**
* *Role:* Accepts U.S. Code anchors and resolves published agency regulations and transmittals.


* *Source Type:* Federal rulemaking registries and agency transmittal/change request repositories.




* **Phase 4 (Medical Coding & Fee Schedules):**
* *Role:* Accepts operational billing/pricing indicators.


* *Source Type:* Alpha-numeric medical coding datasets, fee schedules, and coverage determination registries.




* **Phase 5 (Evidence & Advocacy):**
* *Role:* Accepts bill identifiers and clinical citations.


* *Source Type:* Lobbying disclosure databases, budget score archives, and federal medical library APIs.





---

