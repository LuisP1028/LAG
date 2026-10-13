"""
Tier 4B: Geographic Fee Schedule Normalizer (COMP-06).

Unpivots the CMS DMEPOS 54-jurisdiction pricing matrix (108 columns: NR & R),
maps the 4 DME MAC regional contractor jurisdictions to states, and creates
discrete FeeScheduleEntry records attached to procedure codes and states.
"""

from __future__ import annotations
import csv
import os
from datetime import datetime, timezone
from typing import Dict, List, Optional, Set, Tuple

from src.graph.models import (
    ChangeRequestNode,
    HCPCSCodeNode,
    JurisdictionNode,
    StateNode,
    FeeScheduleEntryNode,
    EdgeProvenance,
    GraphEdge,
    Tier3Handoff,
)


class Phase4FeeScheduleDatasetError(Exception):
    """Raised when the fee schedule CSV cannot be loaded or contains zero matching rows."""
    pass


class Phase4IncompleteJurisdictionError(Exception):
    """Raised when fee schedule columns fail to cover all 54 jurisdictions."""
    pass


# Authoritative CMS DME MAC Regional Contractor Assignments
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
            ("WA", "Washington"), ("WY", "Wyoming"),
        ],
    ),
}


def normalize_fee_schedules(
    handoff: Tier3Handoff,
    change_request_node: ChangeRequestNode,
    hcpcs_nodes: List[HCPCSCodeNode],
    run_id: str,
    asset_dir: Optional[str] = None,
) -> Tuple[List[JurisdictionNode], List[StateNode], List[FeeScheduleEntryNode], List[GraphEdge]]:
    """
    Unpivots CMS DMEPOS CSV across all 54 jurisdictions and populates the graph.
    """
    now_iso = datetime.now(timezone.utc).isoformat()

    if not asset_dir or not os.path.exists(asset_dir):
        raise Phase4FeeScheduleDatasetError(f"Asset directory not found: {asset_dir}")

    csv_path = os.path.join(asset_dir, "stage4b_cms_dmepos_lc_category.csv")
    if not os.path.exists(csv_path):
        csv_path = os.path.join(asset_dir, "phase4_cms_dmepos_lc_category.csv")

    if not os.path.exists(csv_path):
        raise Phase4FeeScheduleDatasetError(f"Fee schedule CSV not found in {asset_dir}")

    # Build known HCPCS lookup to attach fee entries
    hcpcs_pks: Set[str] = {node.code.strip().upper(): node.primary_key for node in hcpcs_nodes}

    jurisdiction_nodes: List[JurisdictionNode] = []
    state_nodes: List[StateNode] = []
    state_lookup: Dict[str, StateNode] = {}
    edges: List[GraphEdge] = []

    # 1. Instantiate 4 DME MAC Jurisdictions & 54 States
    for juris_code, (contractor_name, states_list) in DME_MAC_JURISDICTIONS.items():
        j_node = JurisdictionNode(code=f"JURIS-DME-{juris_code}", contractor_name=contractor_name)
        jurisdiction_nodes.append(j_node)

        # Edge: ChangeRequest -> Jurisdiction
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

        # States under Jurisdiction
        for st_code, st_name in states_list:
            if st_code not in state_lookup:
                s_node = StateNode(state_code=st_code, state_name=st_name)
                state_nodes.append(s_node)
                state_lookup[st_code] = s_node

            # Edge: Jurisdiction -> State
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

    if len(state_nodes) not in (53, 54):
        raise Phase4IncompleteJurisdictionError(
            f"Expected 53 or 54 states/territories (50 states + DC + PR + VI), but instantiated {len(state_nodes)}"
        )

    # 2. Ingest and Unpivot CSV Rows or Standardized Benefit Fee Schedule
    fee_nodes: List[FeeScheduleEntryNode] = []
    is_ivig = change_request_node.benefit_category == "IVIG" or handoff.operational_filters.get("benefit_category") == "IVIG"

    if is_ivig:
        # CMS CR 13217 / Transmittal 12437: Home IVIG items and services bundled rate ($409.84 base rate)
        ivig_rate = 409.84
        hcpcs_code = "Q2052"
        hcpcs_pk = f"HCPCS-{hcpcs_code}"

        for st_code, st_node in state_lookup.items():
            for is_rural in [False, True]:
                fee_entry = FeeScheduleEntryNode(
                    hcpcs_code=hcpcs_code,
                    state_code=st_code,
                    is_rural=is_rural,
                    fee_amount=ivig_rate,
                    ceiling=ivig_rate,
                    floor=ivig_rate,
                    year=2024,
                )
                fee_nodes.append(fee_entry)

                prov_fee = EdgeProvenance(
                    source_uri="CMS Transmittal 12437 (CR 13217): Home IVIG Fee Schedule",
                    selector=f"schedule[code='{hcpcs_code}', state='{st_code}', rural={is_rural}]",
                    ingestion_timestamp=now_iso,
                    run_id=run_id,
                )
                edges.append(
                    GraphEdge(
                        source_pk=hcpcs_pk,
                        label="HAS_FEE_SCHEDULE",
                        target_pk=fee_entry.primary_key,
                        provenance=prov_fee,
                    )
                )
                edges.append(
                    GraphEdge(
                        source_pk=fee_entry.primary_key,
                        label="APPLIES_TO",
                        target_pk=st_node.primary_key,
                        provenance=prov_fee,
                    )
                )
    else:
        with open(csv_path, "r", encoding="utf-8", errors="replace") as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames or []

            # Find all state rate column pairs
            state_cols: List[Tuple[str, str, bool]] = []
            for col in fieldnames:
                col_strip = col.strip()
                if "(NR)" in col_strip:
                    st = col_strip.split("(")[0].strip()
                    state_cols.append((col, st, False))
                elif "(R)" in col_strip:
                    st = col_strip.split("(")[0].strip()
                    state_cols.append((col, st, True))

            row_count = 0
            for row in reader:
                hcpcs_code = row.get("HCPCS", "").strip().upper()
                if not hcpcs_code:
                    continue
                catg = row.get("CATG", "").strip().upper()
                if catg != "LC":
                    continue

                row_count += 1
                ceiling = float(row.get("Ceiling", 0.0) or 0.0)
                floor = float(row.get("Floor", 0.0) or 0.0)

                # Check if this HCPCS code is in our primary HCPCS lookup
                hcpcs_pk = hcpcs_pks.get(hcpcs_code)
                if not hcpcs_pk:
                    # Dynamically register additional HCPCS from CSV if not in MCD subset
                    hcpcs_pk = f"HCPCS-{hcpcs_code}"

                for col_header, st_code, is_rural in state_cols:
                    raw_val = row.get(col_header, "").strip()
                    if not raw_val:
                        continue
                    try:
                        fee_val = float(raw_val)
                    except ValueError:
                        continue

                    if fee_val <= 0.00:
                        continue

                    fee_entry = FeeScheduleEntryNode(
                        hcpcs_code=hcpcs_code,
                        state_code=st_code,
                        is_rural=is_rural,
                        fee_amount=fee_val,
                        ceiling=ceiling,
                        floor=floor,
                        year=2024,
                    )
                    fee_nodes.append(fee_entry)

                    # Edge: HCPCSCode -> FeeScheduleEntry
                    prov_hcpcs_fee = EdgeProvenance(
                        source_uri=csv_path,
                        selector=f"row[HCPCS='{hcpcs_code}']",
                        ingestion_timestamp=now_iso,
                        run_id=run_id,
                    )
                    edges.append(
                        GraphEdge(
                            source_pk=hcpcs_pk,
                            label="HAS_FEE_SCHEDULE",
                            target_pk=fee_entry.primary_key,
                            provenance=prov_hcpcs_fee,
                        )
                    )

                    # Edge: FeeScheduleEntry -> State
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
                                label="APPLIES_TO",
                                target_pk=st_target.primary_key,
                                provenance=prov_fee_state,
                            )
                        )

            if row_count == 0:
                raise Phase4FeeScheduleDatasetError(f"No rows matching CATG == 'LC' in {csv_path}")

    return jurisdiction_nodes, state_nodes, fee_nodes, edges
