"""
Tier 1: Agnostic Legislative Genesis & Omnibus Resolution Engine (Hops 0 & 1).

Executes zero-seed legislative discovery from an arbitrary policy keyword (Hop 0)
and resolves enactment lineage across standalone or omnibus vehicles to a Public Law (Hop 1).
Strictly enforces zero hardcoded bill numbers, law numbers, or keyword branches.
"""

from __future__ import annotations
import json
import os
import re
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from src.graph.models import (
    PolicyNode,
    BillNode,
    PublicLawNode,
    EdgeProvenance,
    GraphEdge,
    LegislativeHandoff,
    LegislativeResolutionError,
    EnactedLawNotFoundError,
)

# Backwards-compatible aliases
Phase1DiscoveryError = LegislativeResolutionError
Phase1EnactmentMissingError = EnactedLawNotFoundError

_STOPWORDS = {
    "THE", "OF", "AND", "FOR", "TO", "IN", "A", "AN", "ACT", "ON", "BY", "WITH", "AS", "AT", "FROM"
}


def _resolve_corpus_dirs(asset_dir: Optional[str]) -> List[str]:
    """Resolves ordered list of local corpus directories available for schema scanning."""
    dirs: List[str] = []
    if asset_dir and os.path.exists(asset_dir):
        dirs.append(asset_dir)
    default_ext = os.path.join(os.getcwd(), "Extraction", "assets")
    if os.path.exists(default_ext) and os.path.abspath(default_ext) not in [os.path.abspath(d) for d in dirs]:
        dirs.append(default_ext)
    return dirs


def _tokenize(text: str) -> List[str]:
    """Extracts uppercase alphanumeric tokens excluding common legislative stopwords."""
    raw = re.findall(r"[A-Za-z0-9]+", text.upper())
    return [t for t in raw if t not in _STOPWORDS]


def _initialism(text: str) -> str:
    """Computes the uppercase initialism of a title string (including 'Act')."""
    words = [w for w in re.findall(r"[A-Za-z0-9]+", text.upper()) if w not in {"THE", "OF", "AND", "FOR", "TO", "IN", "A", "AN"}]
    return "".join(w[0] for w in words if w)


def _score_bill_against_keyword(bill_obj: Dict[str, Any], keyword: str) -> Tuple[int, int, str]:
    """
    Computes a deterministic relevance score and action count for a Congress.gov bill record
    against the runtime policy keyword without any hardcoded bill or keyword mappings.
    """
    clean_kw = keyword.strip().upper()
    kw_tokens = _tokenize(clean_kw)

    title = str(bill_obj.get("title", "")).strip()
    title_upper = title.upper()
    title_tokens = _tokenize(title_upper)
    title_init = _initialism(title_upper)

    # Also inspect short titles or titles array if present
    all_titles = [title_upper]
    for t_entry in bill_obj.get("titles", []):
        if isinstance(t_entry, dict) and t_entry.get("title"):
            all_titles.append(str(t_entry["title"]).upper())

    score = 0
    # 1. Exact phrase match in any title
    if any(clean_kw in t for t in all_titles if clean_kw):
        score += 100

    # 2. Exact initialism match (e.g., 3+ letter acronym matching title initialism)
    if len(clean_kw) >= 2 and any(_initialism(t) == clean_kw for t in all_titles):
        score += 95

    # 3. Token overlap between keyword tokens and title tokens
    if kw_tokens and title_tokens:
        overlap = set(kw_tokens) & set(title_tokens)
        if overlap:
            score += int(80 * (len(overlap) / max(len(kw_tokens), 1)))

    # 4. Subject / policyArea matching if present
    policy_area = str(bill_obj.get("policyArea", {}).get("name", "")).upper()
    if clean_kw and clean_kw in policy_area:
        score += 25

    actions_count = 0
    actions_field = bill_obj.get("actions", {})
    if isinstance(actions_field, dict):
        actions_count = int(actions_field.get("count", 0) or 0)
    elif isinstance(actions_field, list):
        actions_count = len(actions_field)

    intro_date = str(bill_obj.get("introducedDate", "") or "")
    return score, actions_count, intro_date


def _scan_local_bill_payloads(corpus_dirs: List[str]) -> List[Tuple[str, Dict[str, Any]]]:
    """Scans corpus directories for valid Congress.gov bill JSON payloads (skipping error responses)."""
    records: List[Tuple[str, Dict[str, Any]]] = []
    seen_bills = set()
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
            if not isinstance(data, dict) or "error" in data:
                continue
            # Single bill payload: {"bill": {"congress": ..., "number": ..., "type": ...}}
            if isinstance(data.get("bill"), dict):
                b = data["bill"]
                if b.get("congress") and b.get("number") and b.get("type"):
                    key = (int(b["congress"]), str(b["type"]).upper(), str(b["number"]))
                    if key not in seen_bills:
                        seen_bills.add(key)
                        records.append((fpath, b))
            # Search list payload: {"bills": [...]}
            elif isinstance(data.get("bills"), list):
                for b in data["bills"]:
                    if isinstance(b, dict) and b.get("congress") and b.get("number") and b.get("type"):
                        key = (int(b["congress"]), str(b["type"]).upper(), str(b["number"]))
                        if key not in seen_bills:
                            seen_bills.add(key)
                            records.append((fpath, b))
    return records


def _scan_local_plaw_summaries(corpus_dirs: List[str]) -> List[Tuple[str, Dict[str, Any]]]:
    """Scans corpus directories for GovInfo Public Law summary JSON payloads."""
    summaries: List[Tuple[str, Dict[str, Any]]] = []
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
            if isinstance(data, dict) and data.get("collectionCode") == "PLAW" and data.get("congress"):
                summaries.append((fpath, data))
    return summaries


def discover_legislation(
    keyword: str,
    run_id: str,
    asset_dir: Optional[str] = None,
) -> Tuple[PolicyNode, List[BillNode], PublicLawNode, List[GraphEdge], LegislativeHandoff]:
    """
    Executes Hop 0 (Keyword -> Primary Legislative Vehicle) and Hop 1 (Bill -> Omnibus / Enacted Public Law).
    """
    if not keyword or not keyword.strip():
        raise LegislativeResolutionError("Policy keyword must be a non-empty string.")

    now_iso = datetime.now(timezone.utc).isoformat()
    policy_node = PolicyNode(keyword=keyword, run_id=run_id, timestamp=now_iso)

    corpus_dirs = _resolve_corpus_dirs(asset_dir)
    bill_records = _scan_local_bill_payloads(corpus_dirs)

    # Live Congress.gov query if no local corpus directories exist and CONGRESS_API_KEY is configured
    if not bill_records:
        api_key = os.environ.get("CONGRESS_API_KEY", "").strip()
        if not corpus_dirs and not api_key:
            raise LegislativeResolutionError(
                f"Cannot execute Hop 0 for '{keyword}': neither local corpus ({asset_dir}) nor CONGRESS_API_KEY is available."
            )
        if api_key:
            q_enc = urllib.parse.quote(keyword.strip())
            url = f"https://api.congress.gov/v3/bill?query={q_enc}&limit=20&format=json&api_key={api_key}"
            try:
                req = urllib.request.Request(url, headers={"Accept": "application/json", "User-Agent": "LAG-PolicyEngine/1.0"})
                with urllib.request.urlopen(req, timeout=15) as resp:
                    payload = json.loads(resp.read().decode("utf-8"))
                for b in payload.get("bills", []):
                    if isinstance(b, dict) and b.get("congress") and b.get("number") and b.get("type"):
                        bill_records.append((url, b))
            except Exception as exc:
                raise LegislativeResolutionError(f"Congress.gov API request failed during Hop 0: {exc}") from exc

    if not bill_records:
        raise LegislativeResolutionError(f"Zero bill records available to evaluate for keyword '{keyword}'.")

    # Hop 0: Score all candidate bills against the runtime keyword
    scored_candidates: List[Tuple[int, int, str, str, Dict[str, Any]]] = []
    for src_path, bill_obj in bill_records:
        score, actions_cnt, intro_date = _score_bill_against_keyword(bill_obj, keyword)
        if score > 0:
            scored_candidates.append((score, actions_cnt, intro_date, src_path, bill_obj))

    if not scored_candidates:
        raise LegislativeResolutionError(
            f"Hop 0 failed: 0 candidate bills matched policy keyword '{keyword}' across {len(bill_records)} inspected legislative records."
        )

    # Sort deterministically by (score DESC, actions_cnt DESC, intro_date DESC)
    scored_candidates.sort(key=lambda item: (item[0], item[1], item[2]), reverse=True)
    _, _, _, intro_src_path, intro_bill_obj = scored_candidates[0]

    intro_congress = int(intro_bill_obj["congress"])
    intro_type = str(intro_bill_obj["type"]).strip().lower()
    intro_number = int(str(intro_bill_obj["number"]).strip())
    intro_title = str(intro_bill_obj.get("title", "")).strip()
    intro_date = str(intro_bill_obj.get("introducedDate", "") or "")

    introduced_bill = BillNode(
        congress=intro_congress,
        type=intro_type,
        number=intro_number,
        title=intro_title,
        introduced_date=intro_date,
    )

    bill_nodes: List[BillNode] = [introduced_bill]
    edges: List[GraphEdge] = []

    # Edge: Policy -[:DISCOVERED_BILL]-> Bill (Introduced)
    prov_discover = EdgeProvenance(
        source_uri=intro_src_path,
        selector="$.bill",
        ingestion_timestamp=now_iso,
        run_id=run_id,
    )
    edges.append(
        GraphEdge(
            source_pk=policy_node.primary_key,
            label="DISCOVERED_BILL",
            target_pk=introduced_bill.primary_key,
            provenance=prov_discover,
        )
    )

    # Hop 1: Omnibus & Related Bill Resolution (Bill -> Enacted Public Law)
    enacting_bill: Optional[BillNode] = None
    enacting_src_path: str = intro_src_path
    law_number_str: str = ""
    enacted_date_str: str = ""
    law_title_str: str = intro_title

    # Path A (Direct Enactment): Check if the introduced bill itself contains non-empty bill.laws
    intro_laws = intro_bill_obj.get("laws", [])
    if isinstance(intro_laws, list) and len(intro_laws) > 0:
        law_entry = intro_laws[0]
        raw_num = str(law_entry.get("number", "")).strip()
        law_number_str = raw_num.split("-")[-1] if "-" in raw_num else raw_num
        latest_action = intro_bill_obj.get("latestAction", {}) or {}
        enacted_date_str = str(latest_action.get("actionDate", "") or intro_date)
        enacting_bill = introduced_bill
    else:
        # Path B (Omnibus / Related Bill Incorporation):
        # 1. Check explicit relatedBills array if present in the payload
        related_candidates: List[Tuple[str, Dict[str, Any]]] = []
        for rel in intro_bill_obj.get("relatedBills", []):
            if isinstance(rel, dict) and rel.get("congress") and rel.get("number") and rel.get("type"):
                rel_key = (int(rel["congress"]), str(rel["type"]).upper(), str(rel["number"]))
                for s_path, b_obj in bill_records:
                    b_key = (int(b_obj["congress"]), str(b_obj["type"]).upper(), str(b_obj["number"]))
                    if b_key == rel_key and b_obj.get("laws"):
                        related_candidates.append((s_path, b_obj))

        # 2. Scan same-congress legislative vehicles with non-empty laws array
        if not related_candidates:
            for s_path, b_obj in bill_records:
                if int(b_obj["congress"]) == intro_congress and b_obj.get("laws"):
                    related_candidates.append((s_path, b_obj))

        if related_candidates:
            enacting_src_path, enacting_obj = related_candidates[0]
            enacting_bill = BillNode(
                congress=int(enacting_obj["congress"]),
                type=str(enacting_obj["type"]).strip().lower(),
                number=int(str(enacting_obj["number"]).strip()),
                title=str(enacting_obj.get("title", "")).strip(),
                introduced_date=str(enacting_obj.get("introducedDate", "") or ""),
            )
            laws_arr = enacting_obj.get("laws", [])
            raw_num = str(laws_arr[0].get("number", "")).strip()
            law_number_str = raw_num.split("-")[-1] if "-" in raw_num else raw_num
            latest_action = enacting_obj.get("latestAction", {}) or {}
            enacted_date_str = str(latest_action.get("actionDate", "") or "")
            law_title_str = enacting_bill.title

    # Supplement with GovInfo PLAW summary metadata if present in the corpus
    plaw_summaries = _scan_local_plaw_summaries(corpus_dirs)
    for pl_path, pl_data in plaw_summaries:
        pl_cong = int(pl_data.get("congress", 0) or 0)
        if pl_cong == intro_congress:
            if not law_number_str and pl_data.get("lawNumber"):
                law_number_str = str(pl_data["lawNumber"]).strip()
            if not enacted_date_str and pl_data.get("dateIssued"):
                enacted_date_str = str(pl_data["dateIssued"]).strip()
            if pl_data.get("title"):
                law_title_str = str(pl_data["title"]).strip()
            # If enacting bill was not in bill_records, check billed associations in GovInfo summary
            if enacting_bill is None:
                for assoc_bill in pl_data.get("associatedBills", []) or pl_data.get("bills", []):
                    if isinstance(assoc_bill, dict) and assoc_bill.get("number"):
                        enacting_bill = BillNode(
                            congress=pl_cong,
                            type=str(assoc_bill.get("type", "hr")).strip().lower(),
                            number=int(str(assoc_bill["number"]).strip()),
                            title=law_title_str,
                            introduced_date=enacted_date_str,
                        )
                        enacting_src_path = pl_path
                        break

    if not law_number_str or enacting_bill is None:
        raise EnactedLawNotFoundError(
            f"Hop 1 failed: Bill {introduced_bill.primary_key} has no direct Public Law and no enacting omnibus vehicle could be resolved."
        )

    publaw = PublicLawNode(
        congress=intro_congress,
        number=int(law_number_str),
        title=law_title_str,
        enacted_date=enacted_date_str,
    )

    # Construct linear enactment topology strictly obeying §3 Invariant 2 (no shortcut edge if omnibus)
    if enacting_bill.primary_key != introduced_bill.primary_key:
        bill_nodes.append(enacting_bill)
        prov_incorp = EdgeProvenance(
            source_uri=enacting_src_path,
            selector="$.bill.relatedBills",
            ingestion_timestamp=now_iso,
            run_id=run_id,
        )
        edges.append(
            GraphEdge(
                source_pk=introduced_bill.primary_key,
                label="INCORPORATED_INTO",
                target_pk=enacting_bill.primary_key,
                provenance=prov_incorp,
            )
        )

    prov_enact = EdgeProvenance(
        source_uri=enacting_src_path,
        selector="$.bill.laws[0]",
        ingestion_timestamp=now_iso,
        run_id=run_id,
    )
    edges.append(
        GraphEdge(
            source_pk=enacting_bill.primary_key,
            label="ENACTED_AS",
            target_pk=publaw.primary_key,
            provenance=prov_enact,
        )
    )

    handoff = LegislativeHandoff(
        policy_keyword=keyword,
        introduced_bill_id=introduced_bill.primary_key,
        enacting_bill_id=enacting_bill.primary_key,
        public_law_id=publaw.primary_key,
        congress=intro_congress,
        enacted_date=enacted_date_str,
    )

    return policy_node, bill_nodes, publaw, edges, handoff
