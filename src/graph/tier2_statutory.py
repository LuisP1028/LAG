"""
Tier 2: Agnostic Statutory Codification & USLM XML Parser (Hop 2).

Resolves the USLM XML for the enacted Public Law dynamically from the Hop 1 handoff,
performs semantic token scoring across all <section> elements to locate the target
statutory provision, and extracts codified U.S. Code citations and effective dates
purely from USLM XML tags (<ref href="/us/usc/...">, <quotedContent>, <date>).
"""

from __future__ import annotations
import os
import re
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from typing import List, Optional, Tuple

from src.graph.models import (
    PublicLawNode,
    StatutorySectionNode,
    USCSectionNode,
    EdgeProvenance,
    GraphEdge,
    LegislativeHandoff,
    StatutoryHandoff,
    StatutorySectionNotFoundError,
)
from src.graph.tier1_legislative import _resolve_corpus_dirs, _tokenize, _initialism

# Backwards-compatible aliases
Phase2DocumentRetrievalError = StatutorySectionNotFoundError
Phase2SectionNotFoundError = StatutorySectionNotFoundError

_MONTH_MAP = {
    "JANUARY": "01", "FEBRUARY": "02", "MARCH": "03", "APRIL": "04",
    "MAY": "05", "JUNE": "06", "JULY": "07", "AUGUST": "08",
    "SEPTEMBER": "09", "OCTOBER": "10", "NOVEMBER": "11", "DECEMBER": "12",
}


def _strip_namespaces(root: ET.Element) -> None:
    """Strips XML namespace prefixes in-place for uniform tag traversal."""
    for elem in root.iter():
        if "}" in elem.tag:
            elem.tag = elem.tag.split("}", 1)[1]


def _load_uslm_sections(corpus_dirs: List[str], congress: int, law_number: int) -> List[Tuple[str, ET.Element]]:
    """
    Scans corpus directories for USLM XML files matching the Public Law package
    (PLAW-{congress}publ{law_number} or {congress}_{law_number}) and extracts all <section> elements.
    """
    sections: List[Tuple[str, ET.Element]] = []
    seen_identifiers = set()
    pl_patterns = [
        f"{congress}publ{law_number}".lower(),
        f"{congress}_{law_number}".lower(),
        f"{congress}-{law_number}".lower(),
    ]

    for d in corpus_dirs:
        for fname in sorted(os.listdir(d)):
            if not fname.endswith(".xml"):
                continue
            fname_lower = fname.lower()
            if not any(pat in fname_lower for pat in pl_patterns):
                continue

            fpath = os.path.join(d, fname)
            try:
                with open(fpath, "r", encoding="utf-8", errors="replace") as f:
                    xml_text = f.read().strip()
            except Exception:
                continue

            # Parse full XML document or isolated <section> blocks
            parsed_roots: List[ET.Element] = []
            try:
                root = ET.fromstring(xml_text)
                _strip_namespaces(root)
                parsed_roots.append(root)
            except Exception:
                # Extract top-level <section ...>...</section> blocks if document is a slice
                for match in re.finditer(r"<section\b.*?</section>", xml_text, flags=re.DOTALL):
                    try:
                        sec_el = ET.fromstring(match.group(0))
                        _strip_namespaces(sec_el)
                        parsed_roots.append(sec_el)
                    except Exception:
                        continue

            for r in parsed_roots:
                if r.tag == "section" and (r.attrib.get("identifier") or r.find("heading") is not None):
                    ident = r.attrib.get("identifier", "") or "".join(r.itertext())[:80]
                    if ident not in seen_identifiers:
                        seen_identifiers.add(ident)
                        sections.append((fpath, r))
                else:
                    # Only inspect top-level statutory sections (those with @identifier starting with /us/pl/)
                    for sec in r.iter("section"):
                        ident = sec.attrib.get("identifier", "")
                        if ident.startswith("/us/pl/") and ident not in seen_identifiers:
                            seen_identifiers.add(ident)
                            sections.append((fpath, sec))

    return sections


def _score_section(sec_elem: ET.Element, keyword: str, bill_titles: List[str]) -> int:
    """
    Scores a USLM <section> element against the policy keyword and discovered bill title tokens.
    """
    heading_elem = sec_elem.find("heading")
    heading_text = (heading_elem.text or "").strip().upper() if heading_elem is not None else ""
    chapeau_texts = " ".join((c.text or "") for c in sec_elem.iter("chapeau")).upper()
    full_text = "".join(sec_elem.itertext()).upper()

    search_phrases = [keyword.strip().upper()] + [t.strip().upper() for t in bill_titles if t.strip()]
    token_pool = set()
    for phrase in search_phrases:
        for tok in _tokenize(phrase):
            token_pool.add(tok)

    score = 0
    for phrase in search_phrases:
        if not phrase:
            continue
        if phrase in heading_text:
            score += 100
        elif _initialism(heading_text) == phrase and len(phrase) >= 2:
            score += 90
        if phrase in chapeau_texts or phrase in full_text:
            score += 40

    heading_tokens = set(_tokenize(heading_text))
    body_tokens = set(_tokenize(full_text))

    if token_pool:
        h_overlap = token_pool & heading_tokens
        b_overlap = token_pool & body_tokens
        score += len(h_overlap) * 35
        score += len(b_overlap) * 15

    return score


def _extract_usc_citations(sec_elem: ET.Element) -> List[Tuple[int, str, List[str], str]]:
    """
    Extracts codified United States Code citations and amended/added subsection paths
    from USLM <ref href="/us/usc/...">, in-text subsection instructions ('in subsection (s)(2)'),
    and <quotedContent> hierarchies.
    Returns list of tuples: (title_num, section_code, subsections_list, formatted_citation_string).
    """
    citations: List[Tuple[int, str, List[str], str]] = []
    seen_cites = set()

    # Find all <ref href="/us/usc/t{title}/s{sec}..."> elements
    usc_refs: List[Tuple[int, str, List[str]]] = []
    for ref in sec_elem.iter("ref"):
        href = ref.attrib.get("href", "").strip()
        if href.startswith("/us/usc/"):
            parts = [p for p in href.split("/") if p]
            if len(parts) >= 4 and parts[2].startswith("t") and parts[3].startswith("s"):
                try:
                    t_num = int(parts[2][1:])
                except ValueError:
                    continue
                s_code = parts[3][1:]
                sub_parts = parts[4:]
                usc_refs.append((t_num, s_code, sub_parts))

    # Extract in-text 'in subsection (a)(b)...' path if the first USC ref is a bare section reference
    full_sec_text = " ".join(sec_elem.itertext())
    in_sub_match = re.search(r"in\s+subsection\s+(\([A-Za-z0-9]+\)(?:\([A-Za-z0-9]+\))*)", full_sec_text)
    in_sub_tokens: List[str] = []
    if in_sub_match:
        in_sub_tokens = re.findall(r"\(([A-Za-z0-9]+)\)", in_sub_match.group(1))

    # Inspect <quotedContent> inside subsections to see if a new subparagraph/clause is being added
    quoted_nums: List[str] = []
    for qc in sec_elem.iter("quotedContent"):
        for child in qc:
            num_el = child.find("num")
            if num_el is not None:
                val = num_el.attrib.get("value", "").strip()
                if not val and num_el.text:
                    val = re.sub(r"[^A-Za-z0-9]", "", num_el.text.strip())
                if val and val not in quoted_nums:
                    quoted_nums.append(val)

    for idx, (t_num, s_code, sub_parts) in enumerate(usc_refs):
        subs = list(sub_parts)
        if idx == 0:
            if not subs and in_sub_tokens:
                subs.extend(in_sub_tokens)
            if quoted_nums and quoted_nums[0] not in subs:
                subs.append(quoted_nums[0])
        sub_str = "".join(f"({sp})" for sp in subs)
        cite_str = f"{t_num} U.S.C. {s_code}{sub_str}"
        if cite_str not in seen_cites:
            seen_cites.add(cite_str)
            citations.append((t_num, s_code, subs, cite_str))

    return citations


def _extract_effective_date(sec_elem: ET.Element, default_date: str) -> str:
    """
    Extracts the statutory effective date from USLM <date date="YYYY-MM-DD"> tags
    or textual 'apply to ... on or after Month Day, Year' clauses.
    """
    for date_el in sec_elem.iter("date"):
        iso_attr = date_el.attrib.get("date", "").strip()
        if re.match(r"^\d{4}-\d{2}-\d{2}$", iso_attr):
            return iso_attr

    full_text = " ".join(sec_elem.itertext())
    match = re.search(
        r"(?:on or after|effective|beginning on)\s+([A-Za-z]+)\s+(\d{1,2}),\s*(\d{4})",
        full_text,
        flags=re.IGNORECASE,
    )
    if match:
        month_name = match.group(1).upper()
        day_int = int(match.group(2))
        year_str = match.group(3)
        if month_name in _MONTH_MAP:
            return f"{year_str}-{_MONTH_MAP[month_name]}-{day_int:02d}"

    return default_date


def parse_statutory_codification(
    handoff: LegislativeHandoff,
    public_law_node: PublicLawNode,
    run_id: str,
    asset_dir: Optional[str] = None,
    bill_titles: Optional[List[str]] = None,
) -> Tuple[StatutorySectionNode, List[USCSectionNode], List[GraphEdge], StatutoryHandoff]:
    """
    Executes Hop 2 (Public Law -> Statutory Section & U.S. Code Citations).
    """
    now_iso = datetime.now(timezone.utc).isoformat()
    corpus_dirs = _resolve_corpus_dirs(asset_dir)
    if not corpus_dirs:
        raise StatutorySectionNotFoundError(f"Hop 2 failed: No corpus directories found for {asset_dir}.")

    sections = _load_uslm_sections(corpus_dirs, public_law_node.congress, public_law_node.number)
    if not sections:
        raise StatutorySectionNotFoundError(
            f"Hop 2 failed: USLM XML for Public Law {public_law_node.primary_key} not found or contained 0 <section> nodes."
        )

    titles_to_match = list(bill_titles or [])
    scored_sections: List[Tuple[int, str, ET.Element]] = []
    for fpath, sec_el in sections:
        sc = _score_section(sec_el, handoff.policy_keyword, titles_to_match)
        if sc > 0:
            scored_sections.append((sc, fpath, sec_el))

    if not scored_sections:
        raise StatutorySectionNotFoundError(
            f"Hop 2 failed: 0 <section> nodes in {public_law_node.primary_key} matched policy keyword '{handoff.policy_keyword}'."
        )

    scored_sections.sort(key=lambda item: item[0], reverse=True)
    _, best_fpath, best_sec = scored_sections[0]

    uslm_path = best_sec.attrib.get("identifier", "").strip()
    num_el = best_sec.find("num")
    sec_num = ""
    if num_el is not None:
        sec_num = num_el.attrib.get("value", "").strip()
        if not sec_num and num_el.text:
            sec_num = re.sub(r"[^0-9A-Za-z]", "", num_el.text.strip())
    if not sec_num and uslm_path:
        last_seg = uslm_path.split("/")[-1]
        sec_num = last_seg[1:] if last_seg.startswith("s") else last_seg

    heading_el = best_sec.find("heading")
    heading_str = (heading_el.text or "").strip() if heading_el is not None else ""
    raw_text = " ".join("".join(best_sec.itertext()).split())

    usc_tuples = _extract_usc_citations(best_sec)
    if not usc_tuples:
        raise StatutorySectionNotFoundError(
            f"Hop 2 failed: Statutory section {sec_num} ({uslm_path}) contains 0 extractable U.S. Code citations."
        )

    effective_date = _extract_effective_date(best_sec, handoff.enacted_date)
    primary_title, primary_sec_code, primary_subs, _ = usc_tuples[0]

    statutory_node = StatutorySectionNode(
        title=primary_title,
        section=primary_sec_code,
        subsections=primary_subs,
        heading=heading_str,
        text=raw_text[:500],
        public_law_id=public_law_node.primary_key,
        uslm_section_path=uslm_path,
        statute_section_number=sec_num,
        effective_date=effective_date,
    )

    edges: List[GraphEdge] = []
    prov_pl_to_stat = EdgeProvenance(
        source_uri=best_fpath,
        selector=uslm_path or f"//section[@num='{sec_num}']",
        ingestion_timestamp=now_iso,
        run_id=run_id,
    )
    edges.append(
        GraphEdge(
            source_pk=public_law_node.primary_key,
            label="CONTAINS",
            target_pk=statutory_node.primary_key,
            provenance=prov_pl_to_stat,
        )
    )

    usc_nodes: List[USCSectionNode] = []
    amended_citations: List[str] = []
    for t_num, s_code, subs, cite_str in usc_tuples:
        amended_citations.append(cite_str)
        usc_node = USCSectionNode(
            title=t_num,
            section=s_code,
            subsections=subs,
            citation_string=cite_str,
        )
        usc_nodes.append(usc_node)
        prov_stat_to_usc = EdgeProvenance(
            source_uri=best_fpath,
            selector=f"{uslm_path}//ref[@href='/us/usc/t{t_num}/s{s_code}']",
            ingestion_timestamp=now_iso,
            run_id=run_id,
        )
        edges.append(
            GraphEdge(
                source_pk=statutory_node.primary_key,
                label="AMENDS",
                target_pk=usc_node.primary_key,
                provenance=prov_stat_to_usc,
            )
        )

    next_handoff = StatutoryHandoff(
        public_law_id=public_law_node.primary_key,
        uslm_section_path=uslm_path,
        statute_section_number=sec_num,
        statute_heading=heading_str,
        amended_usc_citations=amended_citations,
        effective_date=effective_date,
    )

    return statutory_node, usc_nodes, edges, next_handoff
