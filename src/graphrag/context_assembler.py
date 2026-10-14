"""Structured Context Assembler formatting graph facts and provenance for LLM synthesis."""

from typing import Any, Dict, List, Optional
from src.graphrag.models import TraversalResult


class GraphContextAssembler:
    """Formats verified graph nodes, edges, and provenance into five authoritative sections."""

    @staticmethod
    def _resolve_contractor_name(juris_node: Any) -> str:
        return str(juris_node.properties.get("contractor_name") or juris_node.name or juris_node.primary_key)

    @staticmethod
    def _format_fee_line(fee_node: Any, hcpcs_override: Optional[str] = None) -> str:
        props = fee_node.properties
        h_code = hcpcs_override or props.get("hcpcs_code")
        st_c = props.get("state_code", "")
        state_tag = f" (State: [STATE-{st_c}])" if st_c else ""
        is_rural = bool(props.get("is_rural"))
        rural_label = "Rural" if is_rural else "Non-Rural"
        amt = float(props.get("fee_amount") or 0.0)
        coinsurance = round(amt * 0.20, 2)
        ceiling = float(props.get("ceiling") or amt)
        floor = float(props.get("floor") or 0.0)
        pmeth = props.get("pricing_methodology") or "NATIONAL_FEE_SCHEDULE"
        return (
            f"- [{fee_node.primary_key}]{state_tag} HCPCS {h_code} ({rural_label}, {pmeth}): "
            f"Allowable Reimbursement = ${amt:.2f} "
            f"(Calculated 20% patient coinsurance = ${coinsurance:.2f}, Ceiling = ${ceiling:.2f}, Floor = ${floor:.2f})"
        )

    def assemble_context(
        self,
        traversal_result: TraversalResult,
        state_code: Optional[str] = None,
    ) -> str:
        """Assembles Markdown context divided into five authoritative sections strictly from persisted graph attributes."""
        nodes = traversal_result.nodes
        edges = traversal_result.edges

        lines: List[str] = []

        # ---------------------------------------------------------
        # Section 1: Program & Legal Authority
        # ---------------------------------------------------------
        lines.append("### 1. Program & Legal Authority")

        policies = [n for n in nodes if n.label == "Policy"]
        for p in policies:
            kw = p.properties.get("keyword") or p.properties.get("policy_keyword") or ""
            run_id = p.properties.get("run_id") or ""
            lines.append(f"- Root Policy: [{p.primary_key}] {p.name} (Keyword: {kw}, Run ID: {run_id})")

        bills = [n for n in nodes if n.label == "Bill"]
        for b in bills:
            cong = b.properties.get("congress") or ""
            b_type = str(b.properties.get("type") or b.properties.get("bill_type") or "").upper()
            b_num = b.properties.get("number") or b.properties.get("bill_number") or ""
            title = b.properties.get("title") or b.name
            intro = b.properties.get("introduced_date") or ""
            lines.append(
                f"- Bill: [{b.primary_key}] {cong}th Congress {b_type} {b_num} - {title} (Introduced: {intro})"
            )

        for e in edges:
            if e.label == "INCORPORATED_INTO":
                lines.append(f"- Legislative Omnibus Incorporation: [{e.source_pk}] incorporated into [{e.target_pk}]")

        public_laws = [n for n in nodes if n.label == "PublicLaw"]
        for pl in public_laws:
            cong = pl.properties.get("congress")
            num = pl.properties.get("number") or pl.properties.get("public_law_number")
            pl_num = f"{cong}-{num}" if cong and num and f"{cong}-" not in str(num) else str(num or "")
            title = pl.properties.get("title") or pl.name
            enacted = pl.properties.get("enacted_date") or pl.properties.get("enactment_date") or ""
            lines.append(
                f"- Enacted Public Law: [{pl.primary_key}] Public Law {pl_num} - {title} (Enacted: {enacted})"
            )

        sections = [n for n in nodes if n.label == "StatutorySection"]
        for sec in sections:
            sec_num = sec.properties.get("statute_section_number") or sec.properties.get("section_number") or sec.properties.get("section") or ""
            heading = sec.properties.get("heading") or sec.properties.get("section_heading") or sec.name
            eff = sec.properties.get("effective_date") or ""
            txt = (sec.properties.get("text") or sec.properties.get("text_excerpt") or "")[:240]
            lines.append(
                f"- Statutory Section: [{sec.primary_key}] Section {sec_num} ({heading}) — Effective: {eff} — Excerpt: {txt}"
            )

        usc_sections = [n for n in nodes if n.label == "USCSection"]
        for usc in usc_sections:
            cit = usc.properties.get("citation_string") or usc.properties.get("citation") or usc.name
            subs = usc.properties.get("subsections") or []
            sub_str = ", ".join(str(x) for x in subs) if isinstance(subs, list) else str(subs)
            lines.append(f"- Amended U.S. Code: [{usc.primary_key}] {cit} (Subsections: {sub_str})")

        regs = [n for n in nodes if n.label == "Regulation"]
        for reg in regs:
            cit = reg.properties.get("citation") or reg.name
            doc_num = reg.properties.get("document_number") or ""
            docket = reg.properties.get("docket_id") or ""
            rin = reg.properties.get("rin") or ""
            eff = reg.properties.get("effective_date") or ""
            cfr_parts = reg.properties.get("cfr_parts") or []
            parts_str = ", ".join(str(x) for x in cfr_parts) if isinstance(cfr_parts, list) else str(cfr_parts)
            lines.append(
                f"- Federal Register Final Rule: [{reg.primary_key}] {cit} (Document: {doc_num}, Docket: {docket}, RIN: {rin}, Effective: {eff}, Affected CFR Parts: {parts_str})"
            )

        cfr_sections = [n for n in nodes if n.label == "CFRSection"]
        for cfr in cfr_sections:
            cit = cfr.properties.get("cfr_reference") or cfr.properties.get("citation") or cfr.name
            part = cfr.properties.get("part") or cfr.properties.get("part_number") or ""
            lines.append(f"- Codified CFR Section: [{cfr.primary_key}] {cit} (Part: {part})")

        transmittals = [n for n in nodes if n.label in ("Transmittal", "ChangeRequest")]
        for tr in transmittals:
            cr_num = tr.properties.get("cr_number") or ""
            tr_num = tr.properties.get("transmittal_number") or ""
            manual = tr.properties.get("cms_manual_publication") or tr.properties.get("manual_publication") or ""
            bcat = tr.properties.get("benefit_category") or tr.properties.get("benefit_category_code") or ""
            pind = tr.properties.get("pricing_indicator_code") or ""
            betos = tr.properties.get("betos_code") or ""
            eff = tr.properties.get("effective_date") or ""
            lines.append(
                f"- CMS Transmittal: [{tr.primary_key}] {cr_num} / Transmittal {tr_num} (Manual: {manual}, Benefit Category: {bcat}, Pricing Indicator: {pind}, BETOS: {betos}, Effective: {eff})"
            )

        cov_policies = [n for n in nodes if n.label == "CoveragePolicy"]
        for cp in cov_policies:
            art_id = cp.properties.get("article_id") or cp.primary_key
            pub_type = cp.properties.get("publisher_type") or cp.properties.get("policy_type") or ""
            title = cp.properties.get("title") or cp.name
            eff = cp.properties.get("effective_date") or ""
            prereqs = cp.properties.get("clinical_prerequisites") or []
            prereq_str = "; ".join(str(x) for x in prereqs) if isinstance(prereqs, list) else str(prereqs)
            lines.append(
                f"- Authorizing Coverage Policy: [{cp.primary_key}] {art_id} ({pub_type}) - {title} (Effective: {eff}, Clinical Prerequisites: {prereq_str})"
            )

        cbo_scores = [n for n in nodes if n.label == "CBOScore"]
        for cbo in cbo_scores:
            title = cbo.properties.get("title") or cbo.name
            pub_date = cbo.properties.get("published_date") or cbo.properties.get("publication_date") or ""
            url = cbo.properties.get("url") or ""
            lines.append(
                f"- CBO Cost Estimate: [{cbo.primary_key}] {title} (Published: {pub_date}, URL: {url})"
            )

        filings = [n for n in nodes if n.label == "LobbyingFiling"]
        for lf in filings:
            reg_name = lf.properties.get("registrant_name") or ""
            client = lf.properties.get("client_name") or lf.name
            yr = lf.properties.get("year") or lf.properties.get("filing_year") or ""
            amt = lf.properties.get("amount")
            amt_str = f", Amount: ${float(amt):,.2f}" if amt is not None else ""
            lines.append(
                f"- Lobbying Filing: [{lf.primary_key}] Registrant: {reg_name}, Client: {client} (Year: {yr}{amt_str})"
            )

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
            contractor = self._resolve_contractor_name(j)
            j_code = j.properties.get("code") or j.properties.get("jurisdiction_code") or j.primary_key
            lines.append(f"- Regional Claims Contractor: [{j.primary_key}] {j_code} - {contractor}")

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

        state_nodes = [n for n in nodes if n.label == "State"]
        for s in state_nodes:
            s_name = s.properties.get("state_name") or s.name
            s_code = s.properties.get("state_code") or s.primary_key.replace("STATE-", "")
            parent_j = state_to_juris.get(s.primary_key)
            if parent_j:
                p_contractor = self._resolve_contractor_name(parent_j)
                lines.append(
                    f"- Beneficiary State: [{s.primary_key}] {s_name} (Code: {s_code}, Governing Jurisdiction: [{parent_j.primary_key}] {p_contractor})"
                )
            else:
                lines.append(f"- Beneficiary State: [{s.primary_key}] {s_name} (Code: {s_code})")

        lines.append("")

        # ---------------------------------------------------------
        # Section 3: Clinical & Billing Codes
        # ---------------------------------------------------------
        lines.append("### 3. Clinical & Billing Codes")

        icd10_codes = [n for n in nodes if n.label in ("DiagnosisCode", "ICD10Code")]
        for d in icd10_codes:
            code = d.properties.get("code") or d.primary_key.replace("ICD10-", "")
            desc = d.properties.get("description") or d.name
            lines.append(f"- Qualifying Diagnosis: [{d.primary_key}] ICD-10 {code} - {desc}")

        hcpcs_nodes = [n for n in nodes if n.label in ("ProcedureCode", "HCPCSCode")]
        if hcpcs_nodes:
            lines.append("- Covered Procedure Codes:")
            active_set = set(traversal_result.active_node_pks or [])
            sample_hcpcs: List[Any] = []
            # 1. Include active / queried HCPCS nodes first
            for h in hcpcs_nodes:
                if h.primary_key in active_set and h not in sample_hcpcs:
                    sample_hcpcs.append(h)
            # 2. Ensure A6522 (National Fee Schedule) and A6520 (Local Contractor Pricing) are represented if present
            for target_code in ("HCPCS-A6522", "HCPCS-A6520"):
                tnode = next((h for h in hcpcs_nodes if h.primary_key == target_code), None)
                if tnode and tnode not in sample_hcpcs:
                    sample_hcpcs.append(tnode)
            # 3. Fill up to 6 representative procedure codes
            for h in hcpcs_nodes:
                if h not in sample_hcpcs and len(sample_hcpcs) < 6:
                    sample_hcpcs.append(h)

            for h in sample_hcpcs:
                hp = h.properties
                code = hp.get("code") or h.primary_key.replace("HCPCS-", "")
                sdesc = hp.get("short_description") or h.name
                ldesc = hp.get("long_description") or sdesc
                bcat = hp.get("category") or hp.get("benefit_category") or ""
                betos = hp.get("betos_code") or ""
                pind = hp.get("pricing_indicator") or ""
                pmeth = hp.get("pricing_methodology") or ""
                custom = bool(hp.get("is_custom_or_nos"))
                lines.append(
                    f"  - [{h.primary_key}] HCPCS {code}: {sdesc} "
                    f"(Long Description: {ldesc}, Benefit Category: {bcat}, BETOS: {betos}, "
                    f"Pricing Indicator: {pind}, Pricing Methodology: {pmeth}, Custom/NOS: {custom})"
                )

        studies = [n for n in nodes if n.label == "LiteratureStudy"]
        for st in studies:
            pmid = st.properties.get("pmid") or st.primary_key.replace("PUBMED-", "")
            title = st.properties.get("title") or st.name
            journal = st.properties.get("journal") or ""
            pub_year = st.properties.get("pub_year") or st.properties.get("publication_date") or ""
            lines.append(f"- Supporting Clinical Evidence: [{st.primary_key}] PMID {pmid} - {title} ({journal}, {pub_year})")

        lines.append("")

        # ---------------------------------------------------------
        # Section 4: Reimbursement Rates
        # ---------------------------------------------------------
        if 1 <= len(state_nodes) <= 4:
            target_state = ", ".join(s.properties.get("state_name") or s.name for s in state_nodes)
        elif len(state_nodes) > 4:
            target_state = "Regional Overview"
        elif state_code:
            target_state = state_code
        else:
            target_state = "Overview"

        fees = [n for n in nodes if n.label in ("FeeScheduleRate", "FeeScheduleEntry")]
        schedule_years = sorted({str(f.properties.get("year") or f.properties.get("schedule_year")) for f in fees if f.properties.get("year") or f.properties.get("schedule_year")})
        year_label = ", ".join(schedule_years) if schedule_years else "DMEPOS Fee Schedule"

        lines.append(f"### 4. Reimbursement Rates ({target_state}, {year_label})")

        if fees:
            emitted_fee_pks = set()
            # Emit both Non-Rural and Rural rates for A6522 first
            a6522_fees = sorted(
                [f for f in fees if f.properties.get("hcpcs_code") == "A6522"],
                key=lambda x: (x.properties.get("state_code", ""), bool(x.properties.get("is_rural"))),
            )
            for a6522_fee in a6522_fees:
                emitted_fee_pks.add(a6522_fee.primary_key)
                lines.append(self._format_fee_line(a6522_fee, "A6522"))

            active_set = set(traversal_result.active_node_pks or [])
            for f in sorted(
                fees,
                key=lambda x: (
                    x.properties.get("hcpcs_code", ""),
                    x.properties.get("state_code", ""),
                    bool(x.properties.get("is_rural")),
                ),
            ):
                if f.primary_key in active_set and f.primary_key not in emitted_fee_pks:
                    emitted_fee_pks.add(f.primary_key)
                    lines.append(self._format_fee_line(f))

            count = 0
            for f in sorted(
                fees,
                key=lambda x: (
                    x.properties.get("hcpcs_code", ""),
                    x.properties.get("state_code", ""),
                    bool(x.properties.get("is_rural")),
                ),
            ):
                if f.primary_key not in emitted_fee_pks and count < 6:
                    emitted_fee_pks.add(f.primary_key)
                    lines.append(self._format_fee_line(f))
                    count += 1

        local_priced_codes = [
            h for h in hcpcs_nodes
            if h.properties.get("pricing_methodology") == "LOCAL_CONTRACTOR_PRICING"
            or str(h.properties.get("pricing_indicator")) == "46"
        ]
        if local_priced_codes:
            sample_local = ", ".join(f"[{h.primary_key}] ({h.properties.get('code')})" for h in local_priced_codes[:5])
            lines.append(
                f"- Local Contractor Pricing Notice: {len(local_priced_codes)} covered procedure codes "
                f"(including {sample_local}) carry Pricing Indicator 46 (LOCAL_CONTRACTOR_PRICING) and are priced by the regional DME MAC contractor rather than a fixed national fee schedule dollar amount."
            )
        elif not fees and hcpcs_nodes:
            for h in hcpcs_nodes[:5]:
                lines.append(
                    f"- [{h.primary_key}] HCPCS {h.properties.get('code')}: Pricing Methodology = {h.properties.get('pricing_methodology')} (Pricing Indicator: {h.properties.get('pricing_indicator')})"
                )

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
                sel = prov.get("selector") or ""
                ingest = prov.get("ingestion_timestamp") or ""
                run_id = prov.get("run_id") or ""
                lines.append(f"- Authority Source: {uri} (Selector: {sel}, Ingested: {ingest}, Run ID: {run_id})")

        return "\n".join(lines)
