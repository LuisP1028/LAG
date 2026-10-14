"""
Tier 4B: Agnostic 54-Jurisdiction Fee Schedule Unpivoting & Rate Reconciliation (Hop 7).

Dynamically filters the CMS DMEPOS Fee Schedule CSV by the operational benefit category
code (`benefit_category_code`) and `hcpcs_codes` discovered in Hops 4 & 6, unpivots the
wide state `(NR)` and `(R)` columns into discrete `FeeScheduleRateNode` / `FeeScheduleRecord`
entities across all 54 US jurisdictions, and reconciles NOS/custom codes lacking national
fee schedule rows as `LOCAL_CONTRACTOR_PRICING`.
"""

from __future__ import annotations
import csv
import os
import re
from datetime import datetime, timezone
from typing import Dict, List, Optional, Set, Tuple

from src.graph.models import (
    TransmittalNode,
    ProcedureCodeNode,
    JurisdictionNode,
    StateNode,
    FeeScheduleRateNode,
    EdgeProvenance,
    GraphEdge,
    OperationalHandoff,
    CodingHandoff,
    FeeScheduleRecord,
    ReimbursementHandoff,
    FeeScheduleIngestionError,
)
from src.graph.tier1_legislative import _resolve_corpus_dirs

# Backwards-compatible aliases
Phase4FeeScheduleDatasetError = FeeScheduleIngestionError
Phase4IncompleteJurisdictionError = FeeScheduleIngestionError

# Authoritative CMS DME MAC Regional Contractor Assignments (50 States + DC + PR + VI + GU = 54 Jurisdictions)
DME_MAC_JURISDICTIONS: Dict[str, Tuple[str, List[Tuple[str, str]]]] = {
    "A": (
        "Noridian Healthcare Solutions",
        [
            ("CT", "Connecticut"), ("DE", "Delaware"), ("DC", "District of Columbia"),
            ("ME", "Maine"), ("MD", "Maryland"), ("MA", "Massachusetts"),
            ("NH", "New Hampshire"), ("NJ", "New Jersey"), ("NY", "New York"),
            ("PA", "Pennsylvania"), ("RI", "Rhode Island"), ("VT", "Vermont"),
        ],
    ),
    "B": (
        "CGS Administrators",
        [
            ("IL", "Illinois"), ("IN", "Indiana"), ("KY", "Kentucky"),
            ("MI", "Michigan"), ("MN", "Minnesota"), ("OH", "Ohio"),
            ("WI", "Wisconsin"),
        ],
    ),
    "C": (
        "CGS Administrators",
        [
            ("AL", "Alabama"), ("AR", "Arkansas"), ("CO", "Colorado"),
            ("FL", "Florida"), ("GA", "Georgia"), ("LA", "Louisiana"),
            ("MS", "Mississippi"), ("NM", "New Mexico"), ("NC", "North Carolina"),
            ("OK", "Oklahoma"), ("SC", "South Carolina"), ("TN", "Tennessee"),
            ("TX", "Texas"), ("VA", "Virginia"), ("WV", "West Virginia"),
            ("PR", "Puerto Rico"), ("VI", "Virgin Islands"),
        ],
    ),
    "D": (
        "Noridian Healthcare Solutions",
        [
            ("AK", "Alaska"), ("AZ", "Arizona"), ("CA", "California"),
            ("HI", "Hawaii"), ("ID", "Idaho"), ("IA", "Iowa"),
            ("KS", "Kansas"), ("MO", "Missouri"), ("MT", "Montana"),
            ("NE", "Nebraska"), ("NV", "Nevada"), ("ND", "North Dakota"),
            ("OR", "Oregon"), ("SD", "South Dakota"), ("UT", "Utah"),
            ("WA", "Washington"), ("WY", "Wyoming"), ("GU", "Guam"),
        ],
    ),
}


def _find_dmepos_csv(corpus_dirs: List[str], target_cat: str) -> Tuple[str, str, List[Dict[str, str]], List[str]]:
    """
    Scans corpus directories for a CMS DMEPOS Fee Schedule CSV containing `HCPCS` and `CATG`
    headers and rows matching `CATG == target_cat`.
    Returns (csv_path, release_label, matching_rows, fieldnames).
    """
    for d in corpus_dirs:
        for fname in sorted(os.listdir(d)):
            if not fname.endswith(".csv"):
                continue
            fpath = os.path.join(d, fname)
            try:
                with open(fpath, "r", encoding="utf-8", errors="replace") as f:
                    all_lines = f.readlines()
            except Exception:
                continue

            header_idx = -1
            release_label = "CMS_DMEPOS_2024"
            for idx, ln in enumerate(all_lines[:15]):
                if "DMEPOS FEE SCHEDULE" in ln.upper():
                    release_label = ln.split(",")[0].strip().strip('"')
                if "HCPCS" in ln and "CATG" in ln:
                    header_idx = idx
                    break

            if header_idx == -1:
                continue

            reader = csv.DictReader(all_lines[header_idx:])
            fieldnames = list(reader.fieldnames or [])
            matching_rows: List[Dict[str, str]] = []
            for row in reader:
                code = (row.get("HCPCS") or "").strip().upper()
                cat = (row.get("CATG") or "").strip().upper()
                if code and cat == target_cat:
                    matching_rows.append(row)

            if matching_rows:
                return fpath, release_label, matching_rows, fieldnames

    raise FeeScheduleIngestionError(
        f"Hop 7 failed: No DMEPOS Fee Schedule CSV with CATG == '{target_cat}' found in corpus directories {corpus_dirs}."
    )


def normalize_fee_schedules(
    handoff: OperationalHandoff,
    change_request_node: TransmittalNode,
    hcpcs_nodes: List[ProcedureCodeNode],
    run_id: str,
    asset_dir: Optional[str] = None,
    coding_handoff: Optional[CodingHandoff] = None,
) -> Tuple[List[JurisdictionNode], List[StateNode], List[FeeScheduleRateNode], List[GraphEdge], ReimbursementHandoff]:
    """
    Executes Hop 7: Unpivots the CMS DMEPOS Fee Schedule matrix across all 54 US jurisdictions
    and reconciles national fee schedule rates with local contractor pricing codes.
    """
    now_iso = datetime.now(timezone.utc).isoformat()
    corpus_dirs = _resolve_corpus_dirs(asset_dir)
    if not corpus_dirs:
        raise FeeScheduleIngestionError(f"Hop 7 failed: No corpus directories found for {asset_dir}.")

    target_cat = (
        coding_handoff.benefit_category_code.strip().upper()
        if coding_handoff
        else handoff.benefit_category_code.strip().upper()
    )
    csv_path, release_label, matching_rows, fieldnames = _find_dmepos_csv(corpus_dirs, target_cat)

    # Extract year from release_label or effective_date
    year_match = re.search(r"\b(20\d{2})\b", release_label) or re.search(r"\b(20\d{2})\b", handoff.effective_date)
    schedule_year = int(year_match.group(1)) if year_match else 2024

    jurisdiction_nodes: List[JurisdictionNode] = []
    state_nodes: List[StateNode] = []
    state_lookup: Dict[str, StateNode] = {}
    edges: List[GraphEdge] = []

    # 1. Instantiate 4 DME MAC Jurisdictions & 54 US States/Territories
    for juris_code, (contractor_name, states_list) in DME_MAC_JURISDICTIONS.items():
        j_node = JurisdictionNode(code=f"JURIS-DME-{juris_code}", contractor_name=contractor_name)
        jurisdiction_nodes.append(j_node)

        prov_cr_juris = EdgeProvenance(
            source_uri=csv_path,
            selector=f"CMS MAC Region Allocation Table: Jurisdiction {juris_code}",
            ingestion_timestamp=now_iso,
            run_id=run_id,
        )
        edges.append(
            GraphEdge(
                source_pk=change_request_node.primary_key,
                label="APPLIES_TO_JURISDICTION",
                target_pk=j_node.primary_key,
                provenance=prov_cr_juris,
            )
        )

        for st_code, st_name in states_list:
            if st_code not in state_lookup:
                s_node = StateNode(state_code=st_code, state_name=st_name)
                state_nodes.append(s_node)
                state_lookup[st_code] = s_node

            prov_juris_state = EdgeProvenance(
                source_uri=csv_path,
                selector=f"DME MAC Map: JURIS-{juris_code} -> STATE-{st_code}",
                ingestion_timestamp=now_iso,
                run_id=run_id,
            )
            edges.append(
                GraphEdge(
                    source_pk=j_node.primary_key,
                    label="COVERS_STATE",
                    target_pk=state_lookup[st_code].primary_key,
                    provenance=prov_juris_state,
                )
            )

    if len(state_nodes) != 54:
        raise FeeScheduleIngestionError(
            f"Hop 7 failed: Expected 54 jurisdictions (50 states + DC + PR + VI + GU), instantiated {len(state_nodes)}."
        )

    # 2. Identify all state rate column pairs: `{STATE} (NR)` and `{STATE} (R)`
    state_cols: List[Tuple[str, str, bool]] = []
    csv_jurisdictions: Set[str] = set()
    for col in fieldnames:
        col_strip = col.strip()
        if "(NR)" in col_strip:
            st = col_strip.split("(")[0].strip().upper()
            state_cols.append((col, st, False))
            csv_jurisdictions.add(st)
        elif "(R)" in col_strip:
            st = col_strip.split("(")[0].strip().upper()
            state_cols.append((col, st, True))
            csv_jurisdictions.add(st)

    if not state_cols:
        raise FeeScheduleIngestionError(f"Hop 7 failed: No '(NR)' or '(R)' state columns found in {csv_path}.")

    hcpcs_by_code: Dict[str, ProcedureCodeNode] = {n.code.strip().upper(): n for n in hcpcs_nodes}
    priced_codes: Set[str] = set()
    fee_nodes: List[FeeScheduleRateNode] = []
    handoff_records: List[FeeScheduleRecord] = []

    for row in matching_rows:
        hcpcs_code = (row.get("HCPCS") or "").strip().upper()
        if not hcpcs_code:
            continue
        mod = (row.get("Mod") or "").strip()
        # Only ingest primary rate rows (avoid duplicate modifier rows overwriting base rate)
        if mod and hcpcs_code in priced_codes:
            continue

        priced_codes.add(hcpcs_code)
        raw_ceil = (row.get("Ceiling") or "").replace(",", "").replace("$", "").strip()
        raw_floor = (row.get("Floor") or "").replace(",", "").replace("$", "").strip()
        try:
            ceiling = float(raw_ceil) if raw_ceil else 0.0
        except ValueError:
            ceiling = 0.0
        try:
            floor = float(raw_floor) if raw_floor else 0.0
        except ValueError:
            floor = 0.0

        proc_node = hcpcs_by_code.get(hcpcs_code)
        hcpcs_pk = proc_node.primary_key if proc_node else f"HCPCS-{hcpcs_code}"

        for col_header, st_code, is_rural in state_cols:
            raw_val = (row.get(col_header) or "").replace(",", "").replace("$", "").strip()
            if not raw_val:
                continue
            try:
                fee_val = float(raw_val)
            except ValueError:
                raise FeeScheduleIngestionError(
                    f"Hop 7 failed: Non-numeric rate value '{raw_val}' for HCPCS {hcpcs_code} in column '{col_header}'."
                )

            if fee_val <= 0.0:
                continue

            fee_entry = FeeScheduleRateNode(
                hcpcs_code=hcpcs_code,
                state_code=st_code,
                is_rural=is_rural,
                fee_amount=fee_val,
                ceiling=ceiling,
                floor=floor,
                year=schedule_year,
                pricing_methodology="NATIONAL_FEE_SCHEDULE",
            )
            fee_nodes.append(fee_entry)

            handoff_records.append(
                FeeScheduleRecord(
                    hcpcs_code=hcpcs_code,
                    jurisdiction_postal_code=st_code,
                    rural_designation="R" if is_rural else "NR",
                    rate_usd=fee_val,
                    pricing_methodology="NATIONAL_FEE_SCHEDULE",
                )
            )

            prov_hcpcs_fee = EdgeProvenance(
                source_uri=csv_path,
                selector=f"row[HCPCS='{hcpcs_code}']/col['{col_header}']",
                ingestion_timestamp=now_iso,
                run_id=run_id,
            )
            edges.append(
                GraphEdge(
                    source_pk=hcpcs_pk,
                    label="HAS_RATE",
                    target_pk=fee_entry.primary_key,
                    provenance=prov_hcpcs_fee,
                )
            )

            st_target = state_lookup.get(st_code)
            if st_target:
                prov_fee_state = EdgeProvenance(
                    source_uri=csv_path,
                    selector=f"column['{col_header}']",
                    ingestion_timestamp=now_iso,
                    run_id=run_id,
                )
                edges.append(
                    GraphEdge(
                        source_pk=fee_entry.primary_key,
                        label="APPLIES_TO_STATE",
                        target_pk=st_target.primary_key,
                        provenance=prov_fee_state,
                    )
                )

    # 3. Reconcile all Hop 6 HCPCS codes against DMEPOS fee schedule rows
    unpriced_custom_codes: List[str] = []
    for code, p_node in sorted(hcpcs_by_code.items()):
        if code not in priced_codes:
            # Verify whether the code is a valid custom/NOS code governed by LOCAL_CONTRACTOR_PRICING
            if p_node.pricing_methodology == "LOCAL_CONTRACTOR_PRICING" or p_node.is_custom_or_nos:
                unpriced_custom_codes.append(code)
                handoff_records.append(
                    FeeScheduleRecord(
                        hcpcs_code=code,
                        jurisdiction_postal_code="ALL",
                        rural_designation="NR",
                        rate_usd=None,
                        pricing_methodology="LOCAL_CONTRACTOR_PRICING",
                    )
                )
            else:
                raise FeeScheduleIngestionError(
                    f"Hop 7 failed: HCPCS code {code} is missing from DMEPOS fee schedule and is not classified as LOCAL_CONTRACTOR_PRICING."
                )

    reimb_handoff = ReimbursementHandoff(
        fee_schedule_release=release_label,
        jurisdiction_count=len(state_nodes),
        records=handoff_records,
        unpriced_custom_codes=unpriced_custom_codes,
    )

    return jurisdiction_nodes, state_nodes, fee_nodes, edges, reimb_handoff
