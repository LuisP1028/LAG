"""
Tier 5: Agnostic Contextual Enrichment Client (COMP-07).

Ingests Lobbying Disclosure Act (LDA) filings, Congressional Budget Office (CBO)
cost estimates, and PubMed biomedical literature studies purely from structured
JSON payloads in the corpus without hardcoded bill numbers or policy names.
"""

from __future__ import annotations
import json
import os
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from src.graph.models import (
    BillNode,
    RegulationNode,
    LobbyingFilingNode,
    CBOScoreNode,
    LiteratureStudyNode,
    EdgeProvenance,
    GraphEdge,
)
from src.graph.tier1_legislative import _resolve_corpus_dirs


class Phase5LiteratureNotFoundError(Exception):
    """Raised when clinical citations cannot be resolved from literature APIs."""
    pass


def enrich_context(
    target_bills: List[BillNode],
    regulation_node: RegulationNode,
    clinical_citations: Optional[List[int]],
    run_id: str,
    asset_dir: Optional[str] = None,
) -> Tuple[List[LobbyingFilingNode], List[CBOScoreNode], List[LiteratureStudyNode], List[GraphEdge]]:
    """
    Enriches the graph with lobbying, budget, and biomedical context nodes discovered
    by JSON schema inspection across corpus directories.
    """
    now_iso = datetime.now(timezone.utc).isoformat()
    filing_nodes: List[LobbyingFilingNode] = []
    cbo_nodes: List[CBOScoreNode] = []
    study_nodes: List[LiteratureStudyNode] = []
    edges: List[GraphEdge] = []

    corpus_dirs = _resolve_corpus_dirs(asset_dir)
    if not corpus_dirs:
        return filing_nodes, cbo_nodes, study_nodes, edges

    # Primary introduced bill is the first bill in target_bills
    primary_bill = target_bills[0] if target_bills else None
    seen_lda: set[str] = set()
    seen_cbo: set[str] = set()
    seen_pmid: set[int] = set()

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

            # 1. LDA Lobbying Filings schema: {"results": [{"filing_uuid": ..., "registrant": ..., "client": ...}]}
            if primary_bill and isinstance(data.get("results"), list):
                for item in data["results"][:5]:
                    if not isinstance(item, dict):
                        continue
                    uuid = str(item.get("filing_uuid", "") or "").strip()
                    if not uuid or uuid in seen_lda:
                        continue
                    seen_lda.add(uuid)
                    reg_obj = item.get("registrant") if isinstance(item.get("registrant"), dict) else {}
                    cli_obj = item.get("client") if isinstance(item.get("client"), dict) else {}
                    reg_name = str(reg_obj.get("name", "") or "Registered Lobbying Entity").strip()
                    client_name = str(cli_obj.get("name", "") or "Advocacy Client").strip()
                    amount = float(item.get("income") or item.get("expenses") or 0.0)
                    year = int(item.get("filing_year") or 2022)

                    f_node = LobbyingFilingNode(
                        filing_uuid=uuid,
                        registrant_name=reg_name,
                        client_name=client_name,
                        amount=amount,
                        year=year,
                    )
                    filing_nodes.append(f_node)
                    prov_lda = EdgeProvenance(
                        source_uri=fpath,
                        selector=f"$.results[filing_uuid='{uuid}']",
                        ingestion_timestamp=now_iso,
                        run_id=run_id,
                    )
                    edges.append(
                        GraphEdge(
                            source_pk=primary_bill.primary_key,
                            label="HAS_ADVOCACY_RECORD",
                            target_pk=f_node.primary_key,
                            provenance=prov_lda,
                        )
                    )

            # 2. CBO Cost Estimates schema: {"costEstimates": [...]}, {"cboCostEstimates": [...]}, or {"bill": {"cboCostEstimates": [...]}}
            bill_obj = data.get("bill") if isinstance(data.get("bill"), dict) else None
            cbo_list = (
                data.get("costEstimates")
                or data.get("cboCostEstimates")
                or (bill_obj.get("cboCostEstimates") if bill_obj else None)
            )
            if primary_bill and isinstance(cbo_list, list):
                bill_matches = True
                if bill_obj is not None:
                    b_num = str(bill_obj.get("number", "")).strip()
                    b_type = str(bill_obj.get("type", "")).strip().lower()
                    b_cong = int(bill_obj.get("congress") or 0)
                    bill_matches = (
                        str(primary_bill.number) == b_num
                        and primary_bill.type.strip().lower() == b_type
                        and primary_bill.congress == b_cong
                    )
                if bill_matches:
                    selector_prefix = "$.bill.cboCostEstimates" if (bill_obj and "cboCostEstimates" in bill_obj) else (
                        "$.cboCostEstimates" if "cboCostEstimates" in data else "$.costEstimates"
                    )
                    for est in cbo_list:
                        if not isinstance(est, dict):
                            continue
                        cid = str(est.get("id") or est.get("url", "").rstrip("/").split("/")[-1] or "").strip()
                        if not cid or cid in seen_cbo:
                            continue
                        seen_cbo.add(cid)
                        title = str(est.get("title", "") or primary_bill.title).strip()
                        url = str(est.get("url", "") or "").strip()
                        pub_date = str(est.get("pubDate", "") or primary_bill.introduced_date).strip()

                        c_node = CBOScoreNode(
                            id=cid,
                            title=title,
                            url=url,
                            published_date=pub_date,
                        )
                        cbo_nodes.append(c_node)
                        prov_cbo = EdgeProvenance(
                            source_uri=fpath,
                            selector=f"{selector_prefix}[id='{cid}']",
                            ingestion_timestamp=now_iso,
                            run_id=run_id,
                        )
                        edges.append(
                            GraphEdge(
                                source_pk=primary_bill.primary_key,
                                label="HAS_BUDGET_IMPACT",
                                target_pk=c_node.primary_key,
                                provenance=prov_cbo,
                            )
                        )

            # 3. NCBI PubMed ESummary schema: {"result": {"uids": [...], "<pmid>": {...}}}
            res_dict = data.get("result")
            if isinstance(res_dict, dict) and isinstance(res_dict.get("uids"), list):
                for pmid_str in res_dict["uids"]:
                    try:
                        pmid_int = int(pmid_str)
                    except ValueError:
                        continue
                    if pmid_int in seen_pmid:
                        continue
                    seen_pmid.add(pmid_int)

                    article_info: Dict[str, Any] = res_dict.get(str(pmid_str), {})
                    if not isinstance(article_info, dict):
                        continue
                    title = str(article_info.get("title", "") or f"PubMed Study {pmid_int}").strip()
                    journal = str(article_info.get("source", "") or "Peer-Reviewed Biomedical Journal").strip()
                    pub_date_str = str(article_info.get("pubdate", "") or "")
                    year_int = int(pub_date_str[:4]) if len(pub_date_str) >= 4 and pub_date_str[:4].isdigit() else 2020

                    doi = ""
                    for aid in article_info.get("articleids", []) or []:
                        if isinstance(aid, dict) and aid.get("idtype") == "doi":
                            doi = str(aid.get("value", "")).strip()
                            break

                    study_node = LiteratureStudyNode(
                        pmid=pmid_int,
                        doi=doi,
                        title=title,
                        journal=journal,
                        pub_year=year_int,
                    )
                    study_nodes.append(study_node)
                    prov_study = EdgeProvenance(
                        source_uri=fpath,
                        selector=f"$.result['{pmid_str}']",
                        ingestion_timestamp=now_iso,
                        run_id=run_id,
                    )
                    edges.append(
                        GraphEdge(
                            source_pk=regulation_node.primary_key,
                            label="SUPPORTED_BY_EVIDENCE",
                            target_pk=study_node.primary_key,
                            provenance=prov_study,
                        )
                    )

    return filing_nodes, cbo_nodes, study_nodes, edges
