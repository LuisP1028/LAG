# functional_specification_006: Sandcastle Run Archive

**Run ID:** `20261013T165618-008-wcap`  
**Governing Specification:** [`functional_specification_006.md`](functional_specification_006.md)  
**Pipeline Phases Completed:** ALL — Wayfinder Planning (`plan`), Active Reconnaissance 1 (`plan-scan-1`), Active Reconnaissance 2 (`plan-scan-2`), Implementation (`implement`), Review (`review`), Integration Test Planning (`tester`), and Local Repository Join (`merger`)  
**Archive Created At:** 2026-10-13  
**Status:** Successfully completed and merged into `main` (Commit `2f59f08`)  

---

## 1. Executive Summary

During the autonomous execution of `.sandcastle/plan-skill-implement-review-test-merge.mts` seeded with `functional_specification_006.md`:
1. **`plan`** completed successfully on branch `agent/plan-20261013T165618-008-wcap` (commit `926bdd0`), generating 4 feature decision tickets (`ticket-001.md` through `ticket-004.md`), an architectural roadmap (`map.md`), a master component-to-edit matrix (`matrix.md`), and the handoff manifest.
2. **`plan-scan-1`** completed successfully on branch `agent/plan-scan-1-20261013T165618-008-wcap` (commit `b99d896`), capturing 23 empirical payloads (statutory text, public laws, DME MAC contractor headers, CMS transmittals, NLM lookups, and Neo4j node attributes) and authoring `scan_report_001.md`.
3. **`plan-scan-2`** completed successfully on branch `agent/plan-scan-2-20261013T165618-008-wcap` (commit `59e6618`), capturing 12 empirical payloads (MCD error redirects, CMS transmittals headers, federal register rule responses) and authoring `scan_report_006_plan_scan_2.md`.
4. Both scanner branches merged cleanly into the plan branch (`a9b9048` and `493869c`).
5. **`implement`** completed successfully (commit `171c839`), applying the required code changes:
   - Removed redundant "FREEZE PHYSICS" / "UNFREEZE" button from `FilterToolbar.tsx` and context.
   - Converted the Blueprint HUD into a collapsible accordion panel in `GraphCanvas.tsx`.
   - Stabilized cursor hover over nodes to eliminate movement/repulsion in `GraphCanvas.tsx`.
   - Audited and updated dynamic external links across all 10 entity types in `NodeDetailDrawer.tsx`.
6. **`review`** completed successfully (commit `4bb5a72`), certifying changes.
7. **`tester`** completed successfully (commit `2f59f08`), generating integration test decision ticket `ticket-005.md` and `test-matrix.md`.
8. **`merger`** joined the complete 8-commit history into `main`.

---

## 2. Directory Structure and Inventory

```text
functional_specification_006/
├── README.md                                          # This archive catalog & execution log
├── functional_specification_006.md                    # Root functional specification
├── scan_report_001.md                                 # Top-level scan report output from scan-1
├── code_edits/                                        # Captured modified source components & git diff
│   ├── FilterToolbar.tsx
│   ├── GraphCanvas.tsx
│   ├── NodeDetailDrawer.tsx
│   ├── GraphSyncContext.tsx
│   └── implementer_code_changes.diff                  # Git patch of implementation commit 171c839
├── wayfinder/20261013T165618-008-wcap/
│   ├── map.md                                        # Master execution graph and ticket registry
│   ├── matrix.md                                     # Component-to-ticket allocation matrix
│   ├── test-matrix.md                                # Integration test verification matrix
│   └── tickets/
│       ├── ticket-001.md                             # Phase 1: Removal of Physics Toggle Button
│       ├── ticket-002.md                             # Phase 2: Collapsible Blueprint HUD Accordion
│       ├── ticket-003.md                             # Phase 3: Canvas Node Hover Stability
│       ├── ticket-004.md                             # Phase 4: Systematic External Link Audit & Resolution
│       └── ticket-005.md                             # Phase 5: Integration Test Decision Set
├── scan_reports/
│   ├── scan_report_001_plan_scan_1.md                # Scan report from plan-scan-1
│   └── scan_report_006_plan_scan_2.md                # Scan report from plan-scan-2
├── handoff/20261013T165618-008-wcap/
│   ├── plan-scan-1.txt                               # Asset manifest from plan-scan-1
│   ├── plan-scan-2.txt                               # Asset manifest from plan-scan-2
│   ├── wayfinder-read-and-plan.txt                   # Manifest from wayfinder planner
│   ├── implementer.txt                               # Manifest of files modified by implementer
│   ├── implementer-status.txt                        # Status log of required edits
│   ├── reviewer.txt                                  # Reviewer affirmation manifest
│   └── test-plan.txt                                 # Test plan handoff manifest
├── assets/20261013T165618-008-wcap/                   # Empirical payloads captured during reconnaissance (35 files)
│   ├── cgs_dme_headers.txt
│   ├── change_request_cms_transmittals_2024.html
│   ├── change_request_cms_transmittals_index.html
│   ├── change_request_dead_link_probe_r13286cp.txt
│   ├── cms_mcd_invalid_version_error_probe.html
│   ├── cms_mcd_search_results_a59508.html
│   ├── cms_transmittals_headers.txt
│   ├── cornell_lii_usc_42_1395x_headers.txt
│   ├── coverage_policy_cms_mcd_active_article_a55426.html
│   ├── coverage_policy_cms_mcd_invalid_version_redirect.txt
│   ├── coverage_policy_cms_mcd_search_results_a59508.html
│   ├── federal_register_rule_2023_24455.json
│   ├── govinfo_plaw_117publ328_headers.txt
│   ├── hcpcs_cms_dmepos_fee_schedule.html
│   ├── hcpcs_nlm_search_a6522.json
│   ├── hcpcs_nlm_search_q2052.json
│   ├── icd10_cdc_browser_tool.html
│   ├── icd10_nlm_search_i890.json
│   ├── icd10_nlm_search_i972.json
│   ├── jurisdiction_cgs_dme_mac_jb.html
│   ├── jurisdiction_noridian_dme_mac_jadme.html
│   ├── lobbying_filing_sopr_lda_c8697fc5.html
│   ├── neo4j_node_labels_and_counts.json
│   ├── neo4j_relationship_types_and_counts.json
│   ├── neo4j_sample_nodes_10_types.json
│   ├── neo4j_sample_nodes_14_types.json
│   ├── neo4j_summary_statistics.json
│   ├── nlm_hcpcs_search_a6522.json
│   ├── nlm_icd10cm_search_i972.json
│   ├── noridian_dme_headers.txt
│   ├── public_law_govinfo_plaw117publ328_details.html
│   ├── regulation_federal_register_rule_2023_24455.json
│   ├── senate_lda_headers.txt
│   └── statutory_section_cornell_lii_42usc1395x.html
├── by_agent/                                         # Isolated stage outputs
│   ├── plan/                                         # Commit 926bdd0 outputs
│   ├── plan-scan-1/                                  # Commit b99d896 outputs
│   ├── plan-scan-2/                                  # Commit 59e6618 outputs
│   ├── implement/                                    # Commit 171c839 outputs
│   ├── review/                                       # Commit 4bb5a72 outputs
│   └── tester/                                       # Commit 2f59f08 outputs
└── logs/                                             # Execution logs from .sandcastle/logs/
    ├── 20261013T165618-008-wcap-plan.log
    ├── 20261013T165618-008-wcap-plan-scan-1.log
    ├── 20261013T165618-008-wcap-plan-scan-2.log
    ├── 20261013T165618-008-wcap-implement.log
    ├── 20261013T165618-008-wcap-review.log
    ├── 20261013T165618-008-wcap-tester.log
    └── 20261013T165618-008-wcap-merger.log
```
