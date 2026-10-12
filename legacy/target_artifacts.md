Building a holistic knowledge graph from first principles requires anchoring every data source to a fundamental legal, operational, clinical, or economic reality.

---

### 1. Legislative Genesis & Political Authority (The Legislative Branch)

*First Principle: No government benefit can exist without a constitutional grant of authority enacted by Congress.*

| Source Name | Owner / Repository | Access Format | Target Artifacts | Extracted Graph Entities |
| --- | --- | --- | --- | --- |
| **Congress.gov REST API v3** | Library of Congress | JSON REST API | Search queries for `"Lymphedema Treatment Act"` across Congresses 111–117; bill relationship endpoints (`/relatedbills`) | `Bill` nodes (H.R. 4662 through H.R. 3630 / S. 1315), `Sponsor` nodes (members of Congress), `Committee` nodes, and `INCORPORATED_INTO` edge pointing to H.R. 2617 |
| **GovInfo BILLS Collection** | U.S. Government Publishing Office (GPO) | Bulk XML / PDF / API | Historical bill text versions (Introduced, Reported in House, Engrossed in House) | `BillVersion` nodes and text diffs showing how the statutory definitions evolved over 12 years |
| **GovInfo PLAW Collection** | GPO | USLM (United States Legislative Markup) XML | Public Law 117-328 (*Consolidated Appropriations Act, 2023*) | `PublicLaw` node (`PLAW-117publ328`) and `StatutorySection` node (**Division FF, Title IV, Section 4133**) |
| **GovInfo CREC Collection (Congressional Record)** | GPO | XML / Text / API | Floor debates, sponsor speeches, and section-by-section explanatory statements for P.L. 117-328 | `LegislativeIntent` nodes linked via `STATED_BY` to congressional sponsors |

---

### 2. Codified Law & Statutory Amendments (The Permanent Codebase)

*First Principle: Enacted bills do not stand alone; they modify the living body of general federal statutory law.*

| Source Name | Owner / Repository | Access Format | Target Artifacts | Extracted Graph Entities |
| --- | --- | --- | --- | --- |
| **Classification Tables** | Office of the Law Revision Counsel (OLRC) | Tabular HTML / Text | Table III (*Statutes at Large to U.S. Code crosswalk*) for Public Law 117-328 | Direct deterministic crosswalk linking Section 4133 to permanent Title 42 citations |
| **GovInfo USCODE Collection** | GPO / OLRC | USLM XML bulk files | Title 42, Chapter 7, Subchapter XVIII (*Medicare*): Sections 1395x and 1395m | `USCodeSection` nodes: **42 U.S.C. § 1395x(s)(2)(JJ)** (Benefit Category) and **42 U.S.C. § 1395m(z)** (Payment Engine) |

---

### 3. Administrative Policy & Rulemaking (The Executive Branch)

*First Principle: Statutes command what must be done; the executive agency must interpret the statute into enforceable regulations.*

| Source Name | Owner / Repository | Access Format | Target Artifacts | Extracted Graph Entities |
| --- | --- | --- | --- | --- |
| **Federal Register API** | National Archives and Records Administration (NARA) | JSON REST API | Search by authority (`1395m(z)`) and agency (`CMS`):<br>

<br>• Proposed Rule: 88 FR 43654<br>

<br>• Final Rule: 88 FR 77676 | `FederalRule` node (**CMS-1780-F**, RIN 0938-AV03), public comment summaries, and legal rationales |
| **Regulations.gov API** | Federal eRulemaking Portal | JSON REST API | Docket `CMS-2023-0112` (public comments submitted on CMS-1780-P) | `StakeholderFeedback` nodes from patient groups and manufacturers that shaped the final replacement caps |
| **Electronic Code of Federal Regulations (eCFR) API** | NARA / GPO | XML / JSON API | Title 42 CFR, Chapter IV, Subchapter B:<br>

<br>• **42 CFR § 410.36**<br>

<br>• **42 CFR § 414.214** | `CFRSection` nodes capturing binding legal definitions (standard-fit vs. custom-fitted) and statutory replacement limits |

---

### 4. Operational Instructions & Claim Systems (The Adjudication Engine)

*First Principle: Policy must be converted into deterministic logic, validation edits, and operational software transmittals for claims engines.*

| Source Name | Owner / Repository | Access Format | Target Artifacts | Extracted Graph Entities |
| --- | --- | --- | --- | --- |
| **CMS Transmittals & Change Requests Portal** | Centers for Medicare & Medicaid Services (CMS) | PDF / Web releases | • **CR 13286 / Transmittal R12471CP** (Core implementation)<br>

<br>• **CR 13670 / Transmittal R12725OTN** (Therapy duplicate edits) | `ChangeRequest` nodes, Common Working File (CWF) category updates (`Category 60`), Type of Service (`S`), and Pricing Indicator (`40`) |
| **Medicare Learning Network (MLN) Matters** | CMS | PDF / HTML | Article **MM13286** | `ProviderGuideline` nodes summarizing billing rules, physician order requirements, and effective dates |
| **Medicare Coverage Database (MCD)** | CMS | Search Portal / XML extracts | Joint DME MAC Policy Articles (Jurisdictions A, B, C, D):<br>

<br>• **Article A59508 / A59512** (*Lymphedema Compression Treatment Items - Correct Coding and Billing*) | `AdjudicationRule` nodes detailing Standard Written Order (SWO) criteria, measurement timelines, and replacement modifier requirements (`RA`) |

---

### 5. Medical Coding, Products, & Pricing (The Commercial & Clinical Registry)

*First Principle: Every medical item billed in healthcare requires a unique alphanumeric token, an authorized clinical indication, and a defined reimbursement rate.*

| Source Name | Owner / Repository | Access Format | Target Artifacts | Extracted Graph Entities |
| --- | --- | --- | --- | --- |
| **Alpha-Numeric HCPCS Release Files** | CMS | CSV / Fixed-Width Text (Quarterly/Annual) | Rows with BETOS `O1L` and Pricing Indicator `40` | Over 70 `HCPCSCode` nodes (**A6520–A6608**), split into standard daytime, custom daytime, nighttime, and bandaging categories |
| **ICD-10-CM Tabular List of Diseases** | CDC National Center for Health Statistics / CMS | XML / Tabular Text | Chapters 9 and 17: Diagnoses `I89.0`, `I97.2`, `I97.89`, and `Q82.0` | `ICD10Code` nodes linked to HCPCS items via `REQUIRES_DIAGNOSIS` edges |
| **DMEPOS Fee Schedule** | CMS | Tabular Text / CSV | State-specific payment files for HCPCS series `A6520–A6608` | `FeeScheduleEntry` nodes capturing state-by-state allowable payment amounts, rural vs. non-rural floors, ceilings, and coinsurance splits |
| **PDAC Product Classification Matrix** | Pricing, Data Analysis, and Coding Contractor (`dmepdac.com`) | Search Portal / Data Tables | Manufacturer product-to-code verification lists | Commercial `MedicalProduct` nodes (brand names, model numbers, manufacturers) mapped to authorized `HCPCSCode` nodes |
| **Biomedical Ontologies (UMLS / BioPortal)** | National Library of Medicine (NLM) | OWL / RRF / Graph formats | • **Foundational Model of Anatomy (FMA)**: Part-whole body sites<br>

<br>• **SNOMED CT**: Clinical findings | `AnatomicalSite` nodes (e.g., upper limb, forearm, lower limb, chest) mapping physical garment coverage to bodily pathology |

---

### 6. Policy Foundations, Economics, & Clinical Science (The Evidentiary Layer)

*First Principle: Government mandates require empirical justification, financial impact modeling, and organized political advocacy to pass.*

| Source Name | Owner / Repository | Access Format | Target Artifacts | Extracted Graph Entities |
| --- | --- | --- | --- | --- |
| **Lobbying Disclosure Act (LDA) Database** | U.S. Senate SOPR / House Office of the Clerk | JSON REST API (`lda.senate.gov`) | Filings under bill ID `H.R. 3630` / `S. 1315` and health issue code `HCR` | `AdvocacyOrganization` nodes (e.g., *Lymphedema Advocacy Group*), registered lobbyists, expenditure totals, and targeted committees |
| **Congressional Budget Office (CBO) Archive** | Congressional Budget Office | PDF / Web Reports | Formal Cost Estimate for H.R. 3630 (September 2022) | `EconomicEstimate` nodes linking direct 10-year federal expenditure projections and hospital cost-offset models |
| **PubMed / Entrez E-utilities API** | National Center for Biotechnology Information (NCBI) | XML / JSON API (`eutils.ncbi.nlm.nih.gov`) | Literature citations and PubMed IDs (PMIDs) extracted from the preamble footnotes of Final Rule CMS-1780-F | `ClinicalStudy` nodes (e.g., International Society of Lymphology consensus guidelines, clinical trials on gradient compression classes) linked via `JUSTIFIES` edges to regulatory coverage limits |