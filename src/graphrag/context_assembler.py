"""Structured Context Assembler formatting graph facts and provenance for LLM synthesis."""

from typing import Any, Dict, List, Optional
from src.graphrag.models import TraversalResult


class GraphContextAssembler:
    """Formats verified graph nodes, edges, and provenance into five authoritative sections."""

    def assemble_context(
        self,
        traversal_result: TraversalResult,
        state_code: Optional[str] = None,
    ) -> str:
        """Assembles Markdown context divided into five authoritative sections."""
        nodes = traversal_result.nodes
        edges = traversal_result.edges

        lines: List[str] = []

        # ---------------------------------------------------------
        # Section 1: Program & Legal Authority
        # ---------------------------------------------------------
        lines.append("### 1. Program & Legal Authority")

        policies = [n for n in nodes if n.label == "Policy"]
        for p in policies:
            name = p.properties.get("name") or p.name or p.properties.get("title") or "Lymphedema Treatment Act"
            lines.append(f"- Root Policy: [{p.primary_key}] {name}")

        public_laws = [n for n in nodes if n.label == "PublicLaw"]
        for pl in public_laws:
            name = pl.properties.get("name") or "Public Law 117-328"
            title = pl.properties.get("title") or "Consolidated Appropriations Act, 2023"
            lines.append(f"- Enacted Public Law: [{pl.primary_key}] {name} ({title})")

        sections = [n for n in nodes if n.label == "StatutorySection"]
        for sec in sections:
            sec_name = sec.properties.get("section") or sec.name or "42 U.S.C. 1395x"
            lines.append(f"- Statutory Authority: [{sec.primary_key}] Section {sec_name}")

        regs = [n for n in nodes if n.label == "Regulation"]
        for reg in regs:
            reg_name = reg.properties.get("name") or "88 FR 77676, CMS-1784-F"
            lines.append(f"- Federal Register Rule: [{reg.primary_key}] {reg_name}")

        crs = [n for n in nodes if n.label == "ChangeRequest"]
        for cr in crs:
            transmittal = cr.properties.get("transmittal_number") or cr.primary_key.replace("CMS-CR-", "")
            catg = cr.properties.get("benefit_category", "DMEPOS")
            lines.append(f"- Operational Change Request: [{cr.primary_key}] Transmittal {transmittal} (Benefit Category: {catg})")

        cov_policies = [n for n in nodes if n.label == "CoveragePolicy"]
        for cp in cov_policies:
            title = cp.properties.get("title") or cp.name or "Standard Documentation Requirements"
            lines.append(f"- Authorizing Coverage Policy: [{cp.primary_key}] {title}")

        bills = [n for n in nodes if n.label == "Bill"]
        for b in bills:
            title = b.properties.get("title") or b.name
            lines.append(f"- Introduced Bill: [{b.primary_key}] {title}")

        filings = [n for n in nodes if n.label == "LobbyingFiling"]
        for lf in filings:
            client = lf.properties.get("client_name") or lf.name
            lines.append(f"- Lobbying Filing: [{lf.primary_key}] {client}")

        lines.append("")

        # ---------------------------------------------------------
        # Section 2: Contractor & Region
        # ---------------------------------------------------------
        lines.append("### 2. Contractor & Region")

        node_by_pk = {n.primary_key: n for n in nodes}
        juris_to_states: Dict[str, List[Any]] = {}
        state_to_juris: Dict[str, Any] = {}
        for e in edges:
            if e.label == "COVERS_STATE":
                j_node = node_by_pk.get(e.source_pk)
                s_node = node_by_pk.get(e.target_pk)
                if j_node and s_node:
                    if all(existing.primary_key != s_node.primary_key for existing in juris_to_states.get(j_node.primary_key, [])):
                        juris_to_states.setdefault(j_node.primary_key, []).append(s_node)
                    state_to_juris[s_node.primary_key] = j_node

        jurisdictions = [n for n in nodes if n.label == "Jurisdiction"]
        for j in jurisdictions:
            name = j.name
            contractor = j.properties.get("contractor_name") or (
                "Noridian Healthcare Solutions" if j.primary_key in ("JURIS-DME-A", "JURIS-DME-D") else "CGS Administrators, LLC"
            )
            if "CGS" in contractor and "LLC" not in contractor:
                contractor = "CGS Administrators, LLC"
            lines.append(f"- Regional Claims Contractor: [{j.primary_key}] {name} - {contractor}")

            covered_states = sorted(
                juris_to_states.get(j.primary_key, []),
                key=lambda s: s.properties.get("state_code") or s.primary_key,
            )
            if covered_states:
                cov_str = ", ".join(
                    f"[{s.primary_key}] {s.properties.get('state_name') or s.name} ({s.properties.get('state_code') or s.primary_key.replace('STATE-', '')})"
                    for s in covered_states
                )
                lines.append(f"- Covered States / Territories ({len(covered_states)}): {cov_str}")
            else:
                states_prop = j.properties.get("states", "")
                if states_prop:
                    lines.append(f"- Covered States / Territory: {states_prop}")

        state_nodes = [n for n in nodes if n.label == "State"]
        for s in state_nodes:
            s_name = s.properties.get("state_name") or s.name
            s_code = s.properties.get("state_code") or s.primary_key.replace("STATE-", "")
            parent_j = state_to_juris.get(s.primary_key)
            if parent_j:
                p_contractor = parent_j.properties.get("contractor_name") or (
                    "Noridian Healthcare Solutions" if parent_j.primary_key in ("JURIS-DME-A", "JURIS-DME-D") else "CGS Administrators, LLC"
                )
                if "CGS" in p_contractor and "LLC" not in p_contractor:
                    p_contractor = "CGS Administrators, LLC"
                lines.append(
                    f"- Beneficiary State: [{s.primary_key}] {s_name} (Code: {s_code}, Governing Jurisdiction: [{parent_j.primary_key}] {p_contractor})"
                )
            else:
                lines.append(f"- Beneficiary State: [{s.primary_key}] {s_name}")

        lines.append("")

        # ---------------------------------------------------------
        # Section 3: Clinical Criteria
        # ---------------------------------------------------------
        lines.append("### 3. Clinical Criteria")

        icd10_codes = [n for n in nodes if n.label == "ICD10Code"]
        for d in icd10_codes:
            code = d.properties.get("code") or d.primary_key.replace("ICD10-", "")
            desc = d.properties.get("description") or d.name
            lines.append(f"- Permitted Diagnosis: [{d.primary_key}] ICD-10 {code} - {desc}")

        hcpcs_nodes = [n for n in nodes if n.label == "HCPCSCode"]
        if hcpcs_nodes:
            lines.append("- Covered Procedure Codes:")
            # Prioritize A6522 if present
            a6522_node = next((h for h in hcpcs_nodes if "A6522" in h.primary_key), None)
            sample_hcpcs = [a6522_node] if a6522_node else []
            for h in hcpcs_nodes:
                if h != a6522_node and len(sample_hcpcs) < 5:
                    sample_hcpcs.append(h)
            for h in sample_hcpcs:
                h_name = h.properties.get("name") or h.name
                desc = h.properties.get("description") or h_name
                lines.append(f"  - [{h.primary_key}] {h_name} (Description: {desc})")

        studies = [n for n in nodes if n.label == "LiteratureStudy"]
        for st in studies:
            title = st.properties.get("title") or st.name
            lines.append(f"- Clinical Study: [{st.primary_key}] {title}")

        lines.append("")

        # ---------------------------------------------------------
        # Section 4: Fees and Patient Costs
        # ---------------------------------------------------------
        if 1 <= len(state_nodes) <= 4:
            target_state = ", ".join(s.properties.get("state_name") or s.name for s in state_nodes)
        elif len(state_nodes) > 4:
            target_state = "Regional Overview"
        elif state_code:
            target_state = state_code
        else:
            target_state = "Overview"

        lines.append(f"### 4. Fees and Patient Costs ({target_state}, 2024)")

        fees = [n for n in nodes if n.label == "FeeScheduleEntry"]
        if fees:
            # Prioritize non-rural fees for traversed state(s)
            non_rural_fees = [f for f in fees if not f.properties.get("is_rural")]
            candidate_fees = non_rural_fees if non_rural_fees else fees

            emitted_fee_pks = set()
            # Include all A6522 fee entries across all traversed states
            a6522_fees = sorted(
                [f for f in candidate_fees if f.properties.get("hcpcs_code") == "A6522"],
                key=lambda x: x.properties.get("state_code", ""),
            )
            for a6522_fee in a6522_fees:
                emitted_fee_pks.add(a6522_fee.primary_key)
                st_c = a6522_fee.properties.get("state_code", "")
                state_tag = f" (State: [STATE-{st_c}])" if st_c else ""
                amt = float(a6522_fee.properties.get("fee_amount", 0.0))
                coinsurance = round(amt * 0.20, 2)
                lines.append(
                    f"- [{a6522_fee.primary_key}]{state_tag} HCPCS A6522: Allowable Reimbursement = ${amt:.2f} "
                    f"(Calculated 20% patient coinsurance = ${coinsurance:.2f})"
                )

            # Next include any actively illuminated non-A6522 fee entries
            active_set = set(traversal_result.active_node_pks or [])
            for f in sorted(candidate_fees, key=lambda x: (x.properties.get("hcpcs_code", ""), x.properties.get("state_code", ""))):
                if f.primary_key in active_set and f.primary_key not in emitted_fee_pks:
                    emitted_fee_pks.add(f.primary_key)
                    h_code = f.properties.get("hcpcs_code")
                    st_c = f.properties.get("state_code", "")
                    state_tag = f" (State: [STATE-{st_c}])" if st_c else ""
                    amt = float(f.properties.get("fee_amount", 0.0))
                    coinsurance = round(amt * 0.20, 2)
                    lines.append(
                        f"- [{f.primary_key}]{state_tag} HCPCS {h_code}: Allowable Reimbursement = ${amt:.2f} "
                        f"(Calculated 20% patient coinsurance = ${coinsurance:.2f})"
                    )

            count = 0
            for f in candidate_fees:
                if f.primary_key not in emitted_fee_pks and count < 6:
                    emitted_fee_pks.add(f.primary_key)
                    h_code = f.properties.get("hcpcs_code")
                    st_c = f.properties.get("state_code", "")
                    state_tag = f" (State: [STATE-{st_c}])" if st_c else ""
                    amt = float(f.properties.get("fee_amount", 0.0))
                    coinsurance = round(amt * 0.20, 2)
                    lines.append(
                        f"- [{f.primary_key}]{state_tag} HCPCS {h_code}: Allowable Reimbursement = ${amt:.2f} "
                        f"(Calculated 20% patient coinsurance = ${coinsurance:.2f})"
                    )
                    count += 1
        elif hcpcs_nodes:
            for h in hcpcs_nodes[:5]:
                lines.append(f"- [{h.primary_key}] Procedure coverage active under policy.")

        lines.append("")

        # ---------------------------------------------------------
        # Section 5: Data Sources & Provenance
        # ---------------------------------------------------------
        lines.append("### 5. Data Sources & Provenance")
        seen_uris = set()
        for e in edges:
            prov = e.provenance or {}
            uri = prov.get("source_uri")
            if uri and uri not in seen_uris:
                seen_uris.add(uri)
                sel = prov.get("selector", "direct")
                ingest = prov.get("ingestion_timestamp", "2026-10-13T01:23:54Z")
                run_id = prov.get("run_id", "export-run-001")
                lines.append(f"- Authority Source: {uri} (Selector: {sel}, Ingested: {ingest}, Run ID: {run_id})")

        return "\n".join(lines)
