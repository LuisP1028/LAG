<!-- wayfinder:task (AFK) -->
# Verify Raw Asset Files Contain the Values Attributed to Them

Status: resolved

## Question
Where the builder reads `.get(key, literal)`, did the raw asset actually contain the key? Do the files cited in edge `source_uri` contain the facts the edges assert?

## Blocked By
- [Trace Each Exported Field to Its Graph-Builder Origin](ticket-002.md)

## Resolution
Inspected `CoveragePolicies_and_Jurisdictions Addition/assets/20261012T231057-024-zqga/`.

| Asset | Measured Content | Consequence |
| :--- | :--- | :--- |
| `stage1_congress_bill_hr3630_sample.json` | Only `{"error":{"code":"OVER_RATE_LIMIT",…}}` | Every LTA Bill field equals the builder literal default. |
| `stage2_govinfo_plaw_117publ328_summary.json` | Only `{"error":{"code":"OVER_RATE_LIMIT",…}}` | Every PublicLaw field equals the builder literal default. |
| `stage2_uslm_plaw_117_328_sec4133.xml` | Headings for sections 4133 (LTA), "PERMANENT IN-HOME BENEFIT FOR IVIG SERVICES." and "ACCESS TO NON-OPIOID…" | **LTA:** `heading` (with trailing period) and `text` are extracted. **IVIG:** `heading` has no trailing period, so it is the literal default; `text` begins "SEC. 4133. … LYMPHEDEMA…", i.e. the LTA section's text. |
| `stage3_federal_register_rule_2023_24455.json` | Contains `document_number` 2023-24455, `citation` 88 FR 77676, `effective_on` 2024-01-01, and 7 `cfr_references` (42 CFR 409–489) | Every Regulation field is extracted. |
| `stage4a_cms_mcd_a59508_web_probe.html` | `<title>404</title>`. It does not contain "A59508", "I89.0" or "A6520". | LTA MANDATES_POLICY, GOVERNS (70) and ALLOWS_DIAGNOSIS (3) edges cite a 404 page. |
| `stage4b_cms_dmepos_lc_category.csv` | Columns `HCPCS, Mod, Mod2, JURIS, CATG, Ceiling, Floor, Description`, plus `XX (NR)` / `XX (R)` state columns. 70 LC rows. The `JURIS` value on LC rows is only `D`. | LTA HCPCS code and description: 0 of 70 mismatches. Fee amount, ceiling and floor are extracted. The CSV holds no jurisdiction-to-state table, yet COVERS_STATE (53) and APPLIES_TO_JURISDICTION (4) edges cite it. |
| `stage5_lda_lobbying_filings_sample.json` | 2 results. Registrant "THE D MAJOR GROUP", client "LYMPHEDEMA ADVOCACY GROUP", year 2015. Income: `null` and `20000.00`. | LTA LDA fields are extracted, except that the first filing's `amount` of `0.0` is a literal default. IVIG registrant and client names do not appear in the file. |
| `stage5_ncbi_pubmed_esummary.json` | uids 25574334 (sickle cell disease, Pan Afr Med J 2014) and 31298495 (RBC transfusion, Pediatr Blood Cancer 2019) | LiteratureStudy fields are extracted. The LTA Tier 3 handoff lists PMIDs 31454178 and 27549490, which are not in the graph; Tier 5 ingests every uid in the file. |
| `stage5_cbo_cost_estimates_congress_gov.json` | Top-level key `cboCostEstimates` (H.R. 3630, url `…/58517`) | The builder reads `costEstimates`, so zero CBOScore nodes are produced. |
