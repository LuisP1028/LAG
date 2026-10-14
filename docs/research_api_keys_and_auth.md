# Authentication & API Key Research Report

**Date:** 2026-10-13  
**Target:** Legislative & Healthcare Graph Pipeline (`LAG`)  
**Scope:** Hop 0 through Hop 7 Data Ingestion, Neo4j Graph Database, and GraphRAG Synthesis

---

## Executive Summary

- **Local Pipeline Execution (Standard Operation):** **NO external API keys are required.** The repository includes complete official government source documents in `Extraction/assets/` spanning legislative records, USLM statutory XML, Federal Register rules, CMS Transmittals, Joint DME MAC articles, HCPCS tables, and DMEPOS fee schedules.
- **Live Congress.gov API Calls (Hop 0 Live Query):** Optional. If running a brand new policy discovery outside the local corpus, `CONGRESS_API_KEY` (free from [api.data.gov](https://api.data.gov)) is required. Under `DEMO_KEY`, Congress.gov limits traffic to 10 requests/hour (`HTTP 429 OVER_RATE_LIMIT`).
- **GraphRAG Synthesis Layer:** Requires `HF_TOKEN` / `HUGGINGFACE_API_KEY` (already configured in `.env`).
- **Neo4j Database:** Requires local database credentials (`NEO4J_USERNAME` and `NEO4J_PASSWORD` in `.env`).

---

## Detailed Source-by-Source Auth & Key Requirements

| Pipeline Hop | Data Source / System | Authentication / Key Required? | Details & Source Verification |
| :--- | :--- | :--- | :--- |
| **Hop 0 & 1** | **Congress.gov API v3** (`api.congress.gov`) | **Optional for local assets; Yes for live fetching** | - The ingestion pipeline (`src/graph/tier1_legislative.py:L178-187`) first checks local corpus directories (`Extraction/assets/`).<br>- If local assets exist, **no key is queried**.<br>- If live querying without local assets, `CONGRESS_API_KEY` is read from `os.environ`. Unauthenticated or `DEMO_KEY` queries hit an umbrella limit of 10 requests/hr. |
| **Hop 1 & 2** | **GovInfo GPO Bulk Data / USLM XML** (`govinfo.gov/bulkdata/`) | **NO** | GovInfo bulk data repositories and USLM XML files (`PLAW-*.xml`) are public, unauthenticated government publications (`src/graph/tier2_statutory.py`). |
| **Hop 3** | **Federal Register API** (`federalregister.gov/api/v1/`) | **NO** | The Federal Register API v1 is fully open and public; no API key or token is required. |
| **Hop 4** | **CMS Transmittals & Manuals** (`cms.gov`) | **NO** | CMS transmittal PDFs and HTML indexes are public domain government releases; no authentication needed (`src/graph/tier3_regulatory.py`). |
| **Hop 5** | **CMS MCD / DME MAC Portals** (`cms.gov/medicare-coverage-database`, CGS/Noridian) | **NO** | Public coverage database web articles and Joint DME MAC publications; no auth needed (`src/graph/tier4a_coverage.py`). |
| **Hop 6** | **CMS Alpha-Numeric HCPCS** (`cms.gov`) | **NO** | Public quarterly public-use files; parsed from local text/CSV tables (`src/graph/tier4a_coverage.py`). |
| **Hop 7** | **CMS DMEPOS Fee Schedule** (`cms.gov`) | **NO** | Public data releases (`DMEPOS_JAN.csv` / zip); parsed locally (`src/graph/tier4b_fee_schedule.py`). |
| **Tier 5 Sidecars** | **Senate LDA & PubMed** | **NO** | Senate LDA public search and NCBI PubMed E-utilities (`e-summary`) do not require authentication for low-volume academic/public requests. |
| **Persistence** | **Neo4j Database** | **Local DB Auth Only** | Configured in `.env` via `NEO4J_URI=bolt://localhost:7687`, `NEO4J_USERNAME=neo4j`, `NEO4J_PASSWORD=...`. |
| **GraphRAG** | **Hugging Face Inference API** (`router.huggingface.co`) | **YES (Already Configured)** | Uses `HF_TOKEN` in `.env` (`src/graphrag/synthesizer.py:L41-54`). |
