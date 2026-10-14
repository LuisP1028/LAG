"""
Tier 4A: Agnostic Clinical Coverage Guidance & HCPCS Coding Bridge (Hops 5 & 6).

Hop 5: Probes CMS Medicare Coverage Database (MCD) and automatically routes to
       Joint DME MAC Supplier Manual / Correct Coding publications when no standalone
       NCD/LCD exists, parsing HTML coding tables for qualifying ICD-10-CM diagnosis codes.
Hop 6: Filters the CMS Alpha-Numeric HCPCS File (fixed-width 320-char layout) and
       Transmittal attachment tables strictly by operational filter keys (BETOS code and
       pricing indicator code) with zero text-keyword matching.
"""

from __future__ import annotations
import csv
import html
import os
import re
from datetime import datetime, timezone
from typing import Dict, List, Optional, Set, Tuple

from src.graph.models import (
    TransmittalNode,
    CoveragePolicyNode,
    ProcedureCodeNode,
    DiagnosisCodeNode,
    EdgeProvenance,
    GraphEdge,
    StatutoryHandoff,
    OperationalHandoff,
    CoverageHandoff,
    CodingHandoff,
    ClinicalCoverageMissingError,
    CodingTableMismatchError,
)
from src.graph.tier1_legislative import _resolve_corpus_dirs, _tokenize

# Backwards-compatible aliases
Phase4ArticleFetchError = ClinicalCoverageMissingError
Phase4CodingTableMissingError = CodingTableMismatchError

_ICD10_PATTERN = re.compile(r"^[A-TV-Z][0-9][0-9AB](?:\.[0-9A-TV-Z]{1,4})?$")
_HCPCS_PATTERN = re.compile(r"^[A-Z][0-9]{4}$")


def _strip_html_tags(raw_html: str) -> str:
    """Strips HTML tags and unescapes HTML entities."""
    cleaned = re.sub(r"<[^>]+>", " ", raw_html)
    return " ".join(html.unescape(cleaned).split())


def _extract_icd10_from_html_tables(raw_html: str) -> Tuple[List[str], Dict[str, str]]:
    """Extracts qualifying ICD-10-CM codes and descriptions from HTML <table> rows."""
    icd10_map: Dict[str, str] = {}
    qualifying_codes: List[str] = []
    for tr_match in re.finditer(r"<tr[^>]*>(.*?)</tr>", raw_html, flags=re.IGNORECASE | re.DOTALL):
        row_html = tr_match.group(1)
        cells = [
            _strip_html_tags(c)
            for c in re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", row_html, flags=re.IGNORECASE | re.DOTALL)
        ]
        if len(cells) >= 2:
            code_cand = cells[0].strip().upper()
            desc_cand = cells[1].strip()
            if _ICD10_PATTERN.match(code_cand) and code_cand not in icd10_map:
                icd10_map[code_cand] = desc_cand
                qualifying_codes.append(code_cand)
    return qualifying_codes, icd10_map


def _parse_clinical_coverage_html(
    corpus_dirs: List[str],
    stat_handoff: Optional[StatutoryHandoff],
    op_handoff: OperationalHandoff,
) -> Tuple[str, CoverageHandoff, Dict[str, str]]:
    """
    Executes Hop 5 two-stage clinical coverage discovery:
    1. Primary probe of CMS MCD HTML files (detecting HTTP 404 / "Page Not Found" or valid MCD articles).
    2. Secondary route to Joint DME MAC Correct Coding / Supplier Manual HTML publications,
       extracting the publication ID, title, clinical prerequisites, and ICD-10-CM table rows.
    """
    subject_tokens = _tokenize(stat_handoff.statute_heading) if stat_handoff else []

    mcd_candidates: List[Tuple[int, str, str, List[str], Dict[str, str]]] = []
    dme_mac_candidates: List[Tuple[int, str, str, List[str], Dict[str, str]]] = []

    for d in corpus_dirs:
        for fname in sorted(os.listdir(d)):
            if not fname.endswith(".html"):
                continue
            fpath = os.path.join(d, fname)
            try:
                with open(fpath, "r", encoding="utf-8", errors="replace") as f:
                    content = f.read()
            except Exception:
                continue

            title_match = re.search(r"<title[^>]*>(.*?)</title>", content, flags=re.IGNORECASE | re.DOTALL)
            page_title = _strip_html_tags(title_match.group(1)) if title_match else ""

            # Skip 404 / Page Not Found responses (e.g., MCD probe returning 404)
            if "404" in page_title or "PAGE NOT FOUND" in page_title.upper():
                continue

            # Skip CMS Transmittal index pages
            if "views-field-field-dyna-transmittal-number" in content:
                continue

            codes_list, codes_map = _extract_icd10_from_html_tables(content)
            if not codes_list:
                continue

            content_upper = content.upper()
            overlap = sum(1 for tok in subject_tokens if tok in content_upper) if subject_tokens else 1
            if overlap == 0:
                continue

            if "MEDICARE-COVERAGE-DATABASE" in content_upper or "ARTICLEID=" in content_upper:
                mcd_candidates.append((overlap, fpath, content, codes_list, codes_map))
            else:
                dme_mac_candidates.append((overlap, fpath, content, codes_list, codes_map))

    if mcd_candidates:
        mcd_candidates.sort(key=lambda item: item[0], reverse=True)
        _, chosen_fpath, chosen_html, qualifying_codes, icd10_map = mcd_candidates[0]
        publisher_type = "CMS_MCD_LCD"
    elif dme_mac_candidates:
        dme_mac_candidates.sort(key=lambda item: item[0], reverse=True)
        _, chosen_fpath, chosen_html, qualifying_codes, icd10_map = dme_mac_candidates[0]
        publisher_type = "DME_MAC_JOINT_PUBLICATION"
    else:
        raise ClinicalCoverageMissingError(
            "Hop 5 failed: Primary MCD probe returned 404/empty and no secondary Joint DME MAC publication with qualifying ICD-10-CM codes was found."
        )

    # Extract publication title from <h1> or <title>
    h1_match = re.search(r"<h1[^>]*>(.*?)</h1>", chosen_html, flags=re.IGNORECASE | re.DOTALL)
    if h1_match:
        pub_title = _strip_html_tags(h1_match.group(1))
    else:
        t_match = re.search(r"<title[^>]*>(.*?)</title>", chosen_html, flags=re.IGNORECASE | re.DOTALL)
        pub_title = _strip_html_tags(t_match.group(1)) if t_match else "Joint DME MAC Clinical Coverage Guidance"

    # Extract deterministic coverage_guidance_id from canonical URL / filename token / article ID
    guidance_id = ""
    canon_match = re.search(r'<link[^>]+rel=["\']canonical["\'][^>]+href=["\']([^"\']+)["\']', chosen_html, flags=re.IGNORECASE)
    if canon_match:
        url_tail = canon_match.group(1).rstrip("/").split("/")[-1].split(".")[0].upper()
        if url_tail:
            guidance_id = f"DME-MAC-{url_tail}" if publisher_type == "DME_MAC_JOINT_PUBLICATION" else f"CMS-MCD-{url_tail}"
    if not guidance_id:
        base_tokens = re.findall(r"[A-Za-z0-9]+", os.path.basename(chosen_fpath).split(".")[0].upper())
        id_token = base_tokens[-1] if base_tokens else "POLICY"
        guidance_id = f"DME-MAC-{id_token}" if publisher_type == "DME_MAC_JOINT_PUBLICATION" else f"CMS-MCD-{id_token}"

    # Extract clinical prerequisites from bulleted <li> items or coverage paragraphs
    prereqs: List[str] = []
    for li_match in re.finditer(r"<li[^>]*>(.*?)</li>", chosen_html, flags=re.IGNORECASE | re.DOTALL):
        li_text = _strip_html_tags(li_match.group(1))
        if any(w in li_text.lower() for w in ("diagnosis", "prescription", "practitioner", "coverage", "medical necessity")):
            if len(li_text) > 15 and li_text not in prereqs:
                prereqs.append(li_text)
    if not prereqs:
        prereqs.append("Documented qualifying ICD-10-CM diagnosis and clinical prescription required for Medicare coverage.")

    cov_handoff = CoverageHandoff(
        coverage_guidance_id=guidance_id,
        publisher_type=publisher_type,
        publication_title=pub_title,
        qualifying_icd10_codes=qualifying_codes,
        clinical_prerequisites=prereqs[:10],
    )
    return chosen_fpath, cov_handoff, icd10_map


def _extract_hcpcs_by_operational_keys(
    corpus_dirs: List[str],
    op_handoff: OperationalHandoff,
) -> Tuple[str, CodingHandoff]:
    """
    Executes Hop 6: Filters the CMS Alpha-Numeric HCPCS file (fixed-width 320-char layout)
    and/or Transmittal attachment tables strictly by the operational filter keys from Hop 4
    (`betos_code` and `pricing_indicator_code`), supplemented by DMEPOS fee schedule presence
    to classify NATIONAL_FEE_SCHEDULE vs LOCAL_CONTRACTOR_PRICING.
    """
    target_betos = op_handoff.betos_code.strip().upper()
    target_pi = op_handoff.pricing_indicator_code.strip()
    target_cat = op_handoff.benefit_category_code.strip().upper()

    hcpcs_codes: List[str] = []
    descriptions: Dict[str, str] = {}
    pricing_indicators: Dict[str, str] = {}
    source_path = ""

    # 1. Scan fixed-width CMS Alpha-Numeric HCPCS file slices (320-character record layout)
    # Per CMS record layout:
    #   pos 1-5   [0:5]     -> HCPCS Code
    #   pos 11    [10:11]   -> Record Type ('3' = first line of procedure record)
    #   pos 12-91 [11:91]   -> Long Description
    #   pos 92-119 [91:119] -> Short Description
    #   pos 120-121 [119:121] -> Pricing Indicator Code
    #   pos 257-259 [256:259] -> BETOS Code
    for d in corpus_dirs:
        for fname in sorted(os.listdir(d)):
            if not fname.endswith(".txt"):
                continue
            fpath = os.path.join(d, fname)
            try:
                with open(fpath, "r", encoding="utf-8", errors="replace") as f:
                    lines = f.readlines()
            except Exception:
                continue

            matched_in_file = 0
            for line in lines:
                if len(line) < 260:
                    continue
                code_cand = line[0:5].strip().upper()
                rec_type = line[10:11]
                if rec_type != "3" or not _HCPCS_PATTERN.match(code_cand):
                    continue
                pi_val = line[119:121].strip()
                betos_val = line[256:259].strip().upper()

                if betos_val == target_betos and pi_val == target_pi:
                    long_desc = line[11:91].strip()
                    short_desc = line[91:119].strip()
                    if code_cand not in descriptions:
                        hcpcs_codes.append(code_cand)
                        descriptions[code_cand] = long_desc or short_desc
                        pricing_indicators[code_cand] = pi_val
                        matched_in_file += 1
            if matched_in_file > 0 and not source_path:
                source_path = fpath

    # 2. Enrich full long descriptors from the Transmittal attachment table if present
    for d in corpus_dirs:
        for fname in sorted(os.listdir(d)):
            if not fname.endswith(".txt"):
                continue
            fpath = os.path.join(d, fname)
            try:
                with open(fpath, "r", encoding="utf-8", errors="replace") as f:
                    txt = f.read()
            except Exception:
                continue
            if op_handoff.change_request_number.replace("CR", "") not in txt:
                continue
            lines = [ln.strip() for ln in txt.splitlines() if ln.strip()]
            for idx, ln in enumerate(lines):
                if _HCPCS_PATTERN.match(ln) and idx + 1 < len(lines):
                    nxt = lines[idx + 1]
                    if not _HCPCS_PATTERN.match(nxt) and len(nxt) > 10:
                        if ln in descriptions:
                            descriptions[ln] = nxt

    # 3. Check which codes have national fee schedule rows in the DMEPOS fee schedule CSV
    priced_in_dmepos: Set[str] = set()
    for d in corpus_dirs:
        for fname in sorted(os.listdir(d)):
            if not fname.endswith(".csv"):
                continue
            fpath = os.path.join(d, fname)
            try:
                with open(fpath, "r", encoding="utf-8", errors="replace") as f:
                    all_lines = f.readlines()
                header_idx = 0
                for idx, ln in enumerate(all_lines[:15]):
                    if "HCPCS" in ln and "CATG" in ln:
                        header_idx = idx
                        break
                reader = csv.DictReader(all_lines[header_idx:])
                for row in reader:
                    c = (row.get("HCPCS") or "").strip().upper()
                    cat = (row.get("CATG") or "").strip().upper()
                    if c and cat == target_cat:
                        priced_in_dmepos.add(c)
                        if c not in descriptions:
                            hcpcs_codes.append(c)
                            descriptions[c] = (row.get("Description") or "").strip() or f"HCPCS {c}"
                            pricing_indicators[c] = target_pi
                            if not source_path:
                                source_path = fpath
            except Exception:
                continue

    if not hcpcs_codes:
        raise CodingTableMismatchError(
            f"Hop 6 failed: 0 HCPCS procedure codes matched operational filters "
            f"(BETOS='{target_betos}', PricingIndicator='{target_pi}', Category='{target_cat}')."
        )

    hcpcs_codes.sort()
    methodologies: Dict[str, str] = {}
    for code in hcpcs_codes:
        if not _HCPCS_PATTERN.match(code):
            raise CodingTableMismatchError(f"Hop 6 failed: Invalid HCPCS code syntax '{code}'.")
        desc_upper = descriptions.get(code, "").upper()
        is_nos_or_unpriced = (
            (priced_in_dmepos and code not in priced_in_dmepos)
            or "NOT OTHERWISE SPECIFIED" in desc_upper
        )
        methodologies[code] = "LOCAL_CONTRACTOR_PRICING" if is_nos_or_unpriced else "NATIONAL_FEE_SCHEDULE"

    coding_handoff = CodingHandoff(
        benefit_category_code=target_cat,
        betos_code=target_betos,
        hcpcs_codes=hcpcs_codes,
        code_descriptions=descriptions,
        code_pricing_indicators=pricing_indicators,
        pricing_methodologies=methodologies,
    )
    return source_path, coding_handoff


def ingest_coverage_policy(
    handoff: OperationalHandoff,
    change_request_node: TransmittalNode,
    run_id: str,
    asset_dir: Optional[str] = None,
    statutory_handoff: Optional[StatutoryHandoff] = None,
) -> Tuple[CoveragePolicyNode, List[ProcedureCodeNode], List[DiagnosisCodeNode], List[GraphEdge], CoverageHandoff, CodingHandoff]:
    """
    Executes Hop 5 (Clinical Coverage Guidance & Qualifying ICD-10-CM Codes) and
    Hop 6 (Operational-Filtered HCPCS Procedure Codes), establishing the CoveragePolicy
    hub connecting Transmittal -> CoveragePolicy -> DiagnosisCode & ProcedureCode.
    """
    now_iso = datetime.now(timezone.utc).isoformat()
    corpus_dirs = _resolve_corpus_dirs(asset_dir)
    if not corpus_dirs:
        raise ClinicalCoverageMissingError(f"Hops 5 & 6 failed: No corpus directories found for {asset_dir}.")

    cov_src_path, cov_handoff, icd10_map = _parse_clinical_coverage_html(
        corpus_dirs=corpus_dirs,
        stat_handoff=statutory_handoff,
        op_handoff=handoff,
    )

    coding_src_path, coding_handoff = _extract_hcpcs_by_operational_keys(
        corpus_dirs=corpus_dirs,
        op_handoff=handoff,
    )

    coverage_policy_node = CoveragePolicyNode(
        article_id=cov_handoff.coverage_guidance_id,
        title=cov_handoff.publication_title,
        effective_date=handoff.effective_date,
        policy_type=cov_handoff.publisher_type,
        publisher_type=cov_handoff.publisher_type,
        clinical_prerequisites=cov_handoff.clinical_prerequisites,
    )

    edges: List[GraphEdge] = []

    # Edge: Transmittal -[:MANDATES_POLICY]-> CoveragePolicy
    prov_tr_cov = EdgeProvenance(
        source_uri=cov_src_path,
        selector=f"//article[@id='{cov_handoff.coverage_guidance_id}']",
        ingestion_timestamp=now_iso,
        run_id=run_id,
    )
    edges.append(
        GraphEdge(
            source_pk=change_request_node.primary_key,
            label="MANDATES_POLICY",
            target_pk=coverage_policy_node.primary_key,
            provenance=prov_tr_cov,
        )
    )

    # Hop 5 DiagnosisCode nodes and CoveragePolicy -[:REQUIRES_DIAGNOSIS]-> DiagnosisCode edges
    icd10_nodes: List[DiagnosisCodeNode] = []
    for icd_code in cov_handoff.qualifying_icd10_codes:
        desc = icd10_map.get(icd_code, "")
        d_node = DiagnosisCodeNode(code=icd_code, description=desc)
        icd10_nodes.append(d_node)

        prov_diag = EdgeProvenance(
            source_uri=cov_src_path,
            selector=f"//table//tr[td='{icd_code}']",
            ingestion_timestamp=now_iso,
            run_id=run_id,
        )
        edges.append(
            GraphEdge(
                source_pk=coverage_policy_node.primary_key,
                label="REQUIRES_DIAGNOSIS",
                target_pk=d_node.primary_key,
                provenance=prov_diag,
            )
        )

    # Hop 6 ProcedureCode nodes and CoveragePolicy -[:COVERS_PROCEDURE]-> ProcedureCode edges
    hcpcs_nodes: List[ProcedureCodeNode] = []
    for code in coding_handoff.hcpcs_codes:
        desc = coding_handoff.code_descriptions.get(code, "")
        pi_code = coding_handoff.code_pricing_indicators.get(code, handoff.pricing_indicator_code)
        meth = coding_handoff.pricing_methodologies.get(code, "NATIONAL_FEE_SCHEDULE")
        p_node = ProcedureCodeNode(
            code=code,
            short_description=desc[:120],
            long_description=desc,
            category=coding_handoff.benefit_category_code,
            betos_code=coding_handoff.betos_code,
            pricing_indicator=pi_code,
            pricing_methodology=meth,
            is_custom_or_nos=(meth == "LOCAL_CONTRACTOR_PRICING"),
        )
        hcpcs_nodes.append(p_node)

        prov_proc = EdgeProvenance(
            source_uri=coding_src_path,
            selector=f"HCPCS[code='{code}', BETOS='{coding_handoff.betos_code}', PI='{pi_code}']",
            ingestion_timestamp=now_iso,
            run_id=run_id,
        )
        edges.append(
            GraphEdge(
                source_pk=coverage_policy_node.primary_key,
                label="COVERS_PROCEDURE",
                target_pk=p_node.primary_key,
                provenance=prov_proc,
            )
        )

    return coverage_policy_node, hcpcs_nodes, icd10_nodes, edges, cov_handoff, coding_handoff
