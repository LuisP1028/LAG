"""
Tier 3: Agnostic Administrative Rulemaking & CMS Transmittal Harvester (Hops 3 & 4).

Hop 3: Queries / scans Federal Register Final Rules by statutory authority and subject tokens
       to extract FR document number, citation, docket ID, RIN, and CFR references.
Hop 4: Resolves CMS Change Requests & Transmittals, tracks supersession/rescission notices,
       and extracts operational coding keys (benefit category code, pricing indicator, BETOS code).
"""

from __future__ import annotations
import json
import os
import re
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from src.graph.models import (
    StatutorySectionNode,
    USCSectionNode,
    RegulationNode,
    CFRSectionNode,
    TransmittalNode,
    EdgeProvenance,
    GraphEdge,
    StatutoryHandoff,
    RegulatoryHandoff,
    OperationalHandoff,
    RegulatoryRuleResolutionError,
    OperationalDirectiveMissingError,
)
from src.graph.tier1_legislative import _resolve_corpus_dirs, _tokenize

# Backwards-compatible aliases
Phase3RuleNotFoundError = RegulatoryRuleResolutionError
Phase3DirectiveMissingError = OperationalDirectiveMissingError


def _scan_federal_register_records(corpus_dirs: List[str]) -> Tuple[List[Tuple[str, Dict[str, Any]]], Dict[str, Tuple[str, Dict[str, Any]]]]:
    """
    Scans corpus directories for Federal Register search result lists and individual rule detail JSONs.
    Returns (search_hit_records, detail_records_by_doc_number).
    """
    search_hits: List[Tuple[str, Dict[str, Any]]] = []
    details_by_doc: Dict[str, Tuple[str, Dict[str, Any]]] = {}

    for d in corpus_dirs:
        for fname in sorted(os.listdir(d)):
            if not fname.endswith(".json"):
                continue
            fpath = os.path.join(d, fname)
            try:
                with open(fpath, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except Exception:
                continue
            if not isinstance(data, dict):
                continue

            # Search results payload: {"results": [{"document_number": ..., "type": "Rule", ...}]}
            if isinstance(data.get("results"), list):
                for item in data["results"]:
                    if isinstance(item, dict) and item.get("document_number") and item.get("type") in ("Rule", "Proposed Rule"):
                        search_hits.append((fpath, item))
            # Single document detail payload: {"document_number": ..., "citation": ..., "cfr_references": ...}
            elif data.get("document_number") and ("citation" in data or "cfr_references" in data):
                doc_num = str(data["document_number"]).strip()
                details_by_doc[doc_num] = (fpath, data)

    return search_hits, details_by_doc


def _score_fr_candidate(
    record: Dict[str, Any],
    handoff: StatutoryHandoff,
) -> int:
    """
    Scores a Federal Register rule candidate against the Hop 2 StatutoryHandoff
    (statute heading tokens, section number, and Public Law number).
    """
    doc_type = str(record.get("type", "Rule")).strip()
    if doc_type != "Rule":
        return 0

    agencies = record.get("agencies", [])
    has_cms = False
    for ag in agencies:
        if isinstance(ag, dict):
            slug = str(ag.get("slug", "")).lower()
            name = str(ag.get("name", "")).lower()
            if "medicare" in slug or "medicare" in name:
                has_cms = True
                break
    # If agencies array is present and does not include CMS, reject
    if agencies and not has_cms:
        return 0

    text_blob = " ".join(
        str(record.get(k, "") or "")
        for k in ("title", "abstract", "excerpts", "action", "citation")
    ).upper()

    heading_tokens = _tokenize(handoff.statute_heading)
    sec_num = handoff.statute_section_number.strip().upper()
    pl_num = handoff.public_law_id.replace("PLAW-", "").strip().upper()

    score = 0
    if sec_num and f"SECTION {sec_num}" in text_blob:
        score += 60
    elif sec_num and sec_num in text_blob:
        score += 30

    if pl_num and pl_num in text_blob:
        score += 50

    overlap = sum(1 for tok in heading_tokens if tok in text_blob)
    score += overlap * 25

    return score


def resolve_regulatory_rule(
    handoff: StatutoryHandoff,
    usc_nodes: List[USCSectionNode],
    run_id: str,
    asset_dir: Optional[str] = None,
) -> Tuple[RegulationNode, List[CFRSectionNode], List[GraphEdge], RegulatoryHandoff]:
    """
    Executes Hop 3 (Statutory Authority -> Federal Register Final Rule & CFR Sections).
    """
    now_iso = datetime.now(timezone.utc).isoformat()
    corpus_dirs = _resolve_corpus_dirs(asset_dir)
    if not corpus_dirs:
        raise RegulatoryRuleResolutionError(f"Hop 3 failed: No corpus directories found for {asset_dir}.")

    search_hits, details_by_doc = _scan_federal_register_records(corpus_dirs)
    if not search_hits and not details_by_doc:
        raise RegulatoryRuleResolutionError("Hop 3 failed: 0 Federal Register records found in corpus.")

    scored_docs: List[Tuple[int, str, str, Dict[str, Any]]] = []
    seen_doc_nums = set()

    for fpath, hit in search_hits:
        doc_num = str(hit.get("document_number", "")).strip()
        if not doc_num:
            continue
        merged = dict(hit)
        detail_fpath = fpath
        if doc_num in details_by_doc:
            detail_fpath, det = details_by_doc[doc_num]
            merged.update({k: v for k, v in det.items() if v is not None})
        sc = _score_fr_candidate(merged, handoff)
        if sc > 0:
            scored_docs.append((sc, doc_num, detail_fpath, merged))
            seen_doc_nums.add(doc_num)

    for doc_num, (fpath, det) in details_by_doc.items():
        if doc_num in seen_doc_nums:
            continue
        sc = _score_fr_candidate(det, handoff)
        if sc > 0:
            scored_docs.append((sc, doc_num, fpath, det))

    if not scored_docs:
        raise RegulatoryRuleResolutionError(
            f"Hop 3 failed: 0 CMS Final Rules matched statutory authority '{handoff.statute_heading}' (Sec. {handoff.statute_section_number})."
        )

    scored_docs.sort(key=lambda item: item[0], reverse=True)
    _, best_doc_num, best_fpath, best_rule = scored_docs[0]

    citation = str(best_rule.get("citation", "") or "").strip()
    effective_date = str(best_rule.get("effective_on", "") or handoff.effective_date).strip()

    docket_ids = best_rule.get("docket_ids", []) or []
    docket_id = str(docket_ids[0]).strip() if docket_ids else str(best_rule.get("docket_id", "") or "").strip()

    rins = best_rule.get("regulation_id_numbers", []) or []
    rin = str(rins[0]).strip() if rins else str(best_rule.get("regulation_id_number", "") or "").strip()

    raw_cfr = best_rule.get("cfr_references", []) or []
    cfr_strings: List[str] = []
    cfr_nodes: List[CFRSectionNode] = []
    seen_cfr_pks = set()

    for ref in raw_cfr:
        if isinstance(ref, dict) and ref.get("title") and ref.get("part"):
            t_val = int(ref["title"])
            p_val = str(ref["part"]).strip()
            ref_str = f"{t_val} CFR Part {p_val}"
            c_node = CFRSectionNode(cfr_reference=ref_str, title=t_val, part=p_val)
            if c_node.primary_key not in seen_cfr_pks:
                seen_cfr_pks.add(c_node.primary_key)
                cfr_strings.append(ref_str)
                cfr_nodes.append(c_node)

    if not best_doc_num or not citation or not cfr_nodes:
        raise RegulatoryRuleResolutionError(
            f"Hop 3 failed: Final Rule {best_doc_num} is missing mandatory citation or CFR reference metadata."
        )

    reg_node = RegulationNode(
        citation=citation,
        document_number=best_doc_num,
        effective_date=effective_date,
        cfr_parts=cfr_strings,
        docket_id=docket_id,
        rin=rin,
    )

    edges: List[GraphEdge] = []
    for u_node in usc_nodes:
        prov_usc_reg = EdgeProvenance(
            source_uri=best_fpath,
            selector=f"$.document_number['{best_doc_num}']",
            ingestion_timestamp=now_iso,
            run_id=run_id,
        )
        edges.append(
            GraphEdge(
                source_pk=u_node.primary_key,
                label="AUTHORIZED_BY",
                target_pk=reg_node.primary_key,
                provenance=prov_usc_reg,
            )
        )

    for idx, c_node in enumerate(cfr_nodes):
        prov_reg_cfr = EdgeProvenance(
            source_uri=best_fpath,
            selector=f"$.cfr_references[{idx}]",
            ingestion_timestamp=now_iso,
            run_id=run_id,
        )
        edges.append(
            GraphEdge(
                source_pk=reg_node.primary_key,
                label="CODIFIED_IN",
                target_pk=c_node.primary_key,
                provenance=prov_reg_cfr,
            )
        )

    reg_handoff = RegulatoryHandoff(
        fr_document_number=best_doc_num,
        fr_citation=citation,
        docket_id=docket_id,
        rin=rin,
        cfr_references=cfr_strings,
        effective_date=effective_date,
    )

    return reg_node, cfr_nodes, edges, reg_handoff


def _parse_cms_transmittals(
    corpus_dirs: List[str],
    stat_handoff: StatutoryHandoff,
    reg_handoff: RegulatoryHandoff,
) -> Tuple[str, OperationalHandoff]:
    """
    Scans CMS Transmittal index HTML tables and extracted transmittal directive text
    to identify the active Change Request & Transmittal, superseded transmittals,
    and operational coding keys (benefit_category_code, pricing_indicator_code, betos_code).
    """
    heading_tokens = _tokenize(stat_handoff.statute_heading)
    sec_num = stat_handoff.statute_section_number.strip()

    # 1. Scan HTML Transmittal index tables for matching subject rows
    index_candidates: List[Tuple[int, str, str, str, str]] = []  # (score, fpath, transmittal_num, cr_num, subject)
    row_pattern = re.compile(
        r'<td[^>]*views-field-field-dyna-transmittal-number[^>]*>.*?<a[^>]*>([^<]+)</a>.*?'
        r'<td[^>]*views-field-field-dyna-subject-formatted[^>]*>\s*([^<]+?)\s*</td>.*?'
        r'<td[^>]*views-field-field-dyna-cr-number[^>]*>\s*([0-9]+)\s*</td>',
        flags=re.DOTALL | re.IGNORECASE,
    )

    for d in corpus_dirs:
        for fname in sorted(os.listdir(d)):
            if not fname.endswith(".html"):
                continue
            fpath = os.path.join(d, fname)
            try:
                with open(fpath, "r", encoding="utf-8", errors="replace") as f:
                    html_text = f.read()
            except Exception:
                continue
            for m in row_pattern.finditer(html_text):
                tr_id = m.group(1).strip()
                subj = m.group(2).strip()
                cr_id = m.group(3).strip()
                subj_upper = subj.upper()
                overlap = sum(1 for tok in heading_tokens if tok in subj_upper)
                if overlap > 0:
                    index_candidates.append((overlap, fpath, tr_id, cr_id, subj))

    # 2. Scan extracted transmittal directive text files (.txt) for full operational parameters
    text_directives: List[Tuple[int, str, str]] = []
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
            txt_upper = txt.upper()
            if "CHANGE REQUEST" not in txt_upper and "TRANSMITTAL" not in txt_upper:
                continue
            overlap = sum(1 for tok in heading_tokens if tok in txt_upper)
            if sec_num and f"SECTION {sec_num}" in txt_upper:
                overlap += 3
            if overlap > 0:
                text_directives.append((overlap, fpath, txt))

    if not text_directives:
        raise OperationalDirectiveMissingError(
            f"Hop 4 failed: No CMS Transmittal directive text matched statutory authority '{stat_handoff.statute_heading}'."
        )

    # Sort by (overlap_score, has_rescission_notice, filename) descending so active replacement transmittals win over rescinded ones
    text_directives.sort(
        key=lambda item: (item[0], 1 if "rescinded and replaced" in item[2].lower() else 0, item[1]),
        reverse=True,
    )
    _, best_txt_path, directive_text = text_directives[0]

    # Parse CMS Manual Publication (e.g. "Pub 100-04")
    pub_match = re.search(r"\b(Pub\.?\s*\d+-\d+)\b", directive_text, flags=re.IGNORECASE)
    cms_pub = pub_match.group(1).replace(".", "").strip() if pub_match else ""

    # Parse Change Request Number (e.g. "Change Request <number>" -> "CR<number>")
    cr_match = re.search(r"Change\s+Request\s+(\d+)", directive_text, flags=re.IGNORECASE)
    cr_digits = cr_match.group(1).strip() if cr_match else ""
    if not cr_digits and index_candidates:
        index_candidates.sort(key=lambda item: item[0], reverse=True)
        cr_digits = index_candidates[0][3]
    cr_number = f"CR{cr_digits}" if cr_digits else ""

    # Parse Rescission / Supersession Notice (e.g. "Transmittal <old>, ... is being rescinded and replaced by Transmittal <new>")
    superseded_list: List[str] = []
    replacement_tr_from_notice = ""
    for m_resc in re.finditer(
        r"Transmittal\s+([A-Z0-9]+)[^.\n]{0,120}?is\s+being\s+rescinded\s+and\s+replaced\s+by\s+Transmittal\s+([A-Z0-9]+)",
        directive_text,
        flags=re.IGNORECASE,
    ):
        old_num = m_resc.group(1).strip()
        new_num = m_resc.group(2).strip()
        replacement_tr_from_notice = f"R{new_num}CP" if new_num.isdigit() else new_num
        old_formatted = f"R{old_num}CP" if old_num.isdigit() else old_num
        if old_formatted not in superseded_list:
            superseded_list.append(old_formatted)

    # Parse Active Transmittal Number
    active_tr = replacement_tr_from_notice
    if not active_tr and index_candidates:
        for _, _, tr_id, cr_id, _ in index_candidates:
            if cr_id == cr_digits and tr_id not in superseded_list:
                active_tr = tr_id
                break
    if not active_tr:
        tr_match = re.search(r"Transmittal\s+([A-Z0-9]+)", directive_text, flags=re.IGNORECASE)
        if tr_match:
            raw_tr = tr_match.group(1).strip()
            active_tr = f"R{raw_tr}CP" if raw_tr.isdigit() else raw_tr

    # Parse Effective Date (e.g. "Effective Date: Month Day, Year")
    eff_date = reg_handoff.effective_date
    eff_match = re.search(r"Effective\s+Date:\s*([A-Za-z]+\s+\d{1,2},\s*\d{4})", directive_text, flags=re.IGNORECASE)
    if eff_match:
        try:
            dt = datetime.strptime(eff_match.group(1).strip(), "%B %d, %Y")
            eff_date = dt.strftime("%Y-%m-%d")
        except ValueError:
            pass

    # Parse Operational Coding Filter Keys from the Policy / Business Requirements text:
    # 1. Pricing Indicator Code (e.g. "pricing indicator of '<2-digit-code>'")
    pi_match = re.search(r"pricing\s+indicator\s+(?:of|code)?\s*['\"]?(\d{2})['\"]?", directive_text, flags=re.IGNORECASE)
    pricing_ind = pi_match.group(1).strip() if pi_match else ""

    # 2. BETOS Code (e.g. "Berenson-Eggers Type of Service (BETOS) Code of '<3-char-code>'")
    betos_match = re.search(r"BETOS\)?\s+Code\s+(?:of\s+)?['\"]?([A-Z0-9]{3})['\"]?", directive_text, flags=re.IGNORECASE)
    betos_code = betos_match.group(1).strip().upper() if betos_match else ""

    # 3. Benefit / Payment Category Code (e.g. "payment category indicator for ...: <code > =")
    ben_match = re.search(
        r"payment\s+category\s+indicator[^:]*:\s*([A-Z0-9]{2,4})\s*=",
        directive_text,
        flags=re.IGNORECASE,
    )
    if not ben_match:
        ben_match = re.search(r"benefit\s+category\s+(?:code\s+)?['\"]?([A-Z0-9]{2,4})['\"]?", directive_text, flags=re.IGNORECASE)
    benefit_cat = ben_match.group(1).strip().upper() if ben_match else ""

    if not cr_number or not active_tr or not benefit_cat or not pricing_ind or not betos_code:
        raise OperationalDirectiveMissingError(
            f"Hop 4 failed: Incomplete operational directive keys in {best_txt_path} "
            f"(cr={cr_number}, tr={active_tr}, cat={benefit_cat}, pi={pricing_ind}, betos={betos_code})."
        )

    op_handoff = OperationalHandoff(
        change_request_number=cr_number,
        active_transmittal_number=active_tr,
        superseded_transmittal_numbers=superseded_list,
        cms_manual_publication=cms_pub,
        benefit_category_code=benefit_cat,
        pricing_indicator_code=pricing_ind,
        betos_code=betos_code,
        effective_date=eff_date,
    )
    return best_txt_path, op_handoff


def harvest_regulations(
    handoff: StatutoryHandoff,
    statutory_node: StatutorySectionNode,
    run_id: str,
    asset_dir: Optional[str] = None,
    usc_nodes: Optional[List[USCSectionNode]] = None,
) -> Tuple[RegulationNode, List[CFRSectionNode], TransmittalNode, List[GraphEdge], RegulatoryHandoff, OperationalHandoff]:
    """
    Executes Hop 3 (Statutory Authority -> Final Rule & CFR Sections) and
    Hop 4 (Final Rule & Statutory Mandate -> CMS Change Request & Transmittal).
    """
    now_iso = datetime.now(timezone.utc).isoformat()
    corpus_dirs = _resolve_corpus_dirs(asset_dir)

    if not usc_nodes:
        usc_nodes = [
            USCSectionNode(
                title=statutory_node.title,
                section=statutory_node.section,
                subsections=statutory_node.subsections,
                citation_string=handoff.amended_usc_citations[0] if handoff.amended_usc_citations else f"{statutory_node.title} U.S.C. {statutory_node.section}",
            )
        ]

    reg_node, cfr_nodes, hop3_edges, reg_handoff = resolve_regulatory_rule(
        handoff=handoff,
        usc_nodes=usc_nodes,
        run_id=run_id,
        asset_dir=asset_dir,
    )

    directive_src_path, op_handoff = _parse_cms_transmittals(
        corpus_dirs=corpus_dirs,
        stat_handoff=handoff,
        reg_handoff=reg_handoff,
    )

    transmittal_node = TransmittalNode(
        cr_number=op_handoff.change_request_number,
        transmittal_number=op_handoff.active_transmittal_number,
        benefit_category=op_handoff.benefit_category_code,
        effective_date=op_handoff.effective_date,
        superseded_transmittal_numbers=op_handoff.superseded_transmittal_numbers,
        cms_manual_publication=op_handoff.cms_manual_publication,
        pricing_indicator_code=op_handoff.pricing_indicator_code,
        betos_code=op_handoff.betos_code,
    )

    edges = list(hop3_edges)
    for c_node in cfr_nodes:
        prov_cfr_tr = EdgeProvenance(
            source_uri=directive_src_path,
            selector=f"Transmittal[{op_handoff.active_transmittal_number}]",
            ingestion_timestamp=now_iso,
            run_id=run_id,
        )
        edges.append(
            GraphEdge(
                source_pk=c_node.primary_key,
                label="IMPLEMENTED_BY",
                target_pk=transmittal_node.primary_key,
                provenance=prov_cfr_tr,
            )
        )

    return reg_node, cfr_nodes, transmittal_node, edges, reg_handoff, op_handoff
