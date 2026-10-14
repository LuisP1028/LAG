"""Deterministic Multi-Slot Entity Anchor Linker resolving queries into graph entry points."""

import re
from typing import Any, Dict, List, Optional, Tuple
from neo4j import Session

from src.graphrag.exceptions import EntityResolutionError
from src.graphrag.models import (
    AnchorEntity,
    ResolvedAnchors,
    derive_node_display_name,
    resolve_label_from_pk_and_labels,
)


class EntityAnchorLinker:
    """Resolves free-form natural language prompts into verified Neo4j entity anchors."""

    # Authoritative 54 Medicare Part B states, districts, and territories mapped to two-letter codes
    STATE_NAME_TO_CODE: Dict[str, str] = {
        "alabama": "AL", "alaska": "AK", "arizona": "AZ", "arkansas": "AR",
        "california": "CA", "colorado": "CO", "connecticut": "CT", "delaware": "DE",
        "district of columbia": "DC", "florida": "FL", "georgia": "GA", "guam": "GU",
        "hawaii": "HI", "idaho": "ID", "illinois": "IL", "indiana": "IN", "iowa": "IA",
        "kansas": "KS", "kentucky": "KY", "louisiana": "LA", "maine": "ME",
        "maryland": "MD", "massachusetts": "MA", "michigan": "MI", "minnesota": "MN",
        "mississippi": "MS", "missouri": "MO", "montana": "MT", "nebraska": "NE",
        "nevada": "NV", "new hampshire": "NH", "new jersey": "NJ", "new mexico": "NM",
        "new york": "NY", "north carolina": "NC", "north dakota": "ND", "ohio": "OH",
        "oklahoma": "OK", "oregon": "OR", "pennsylvania": "PA", "puerto rico": "PR",
        "rhode island": "RI", "south carolina": "SC", "south dakota": "SD",
        "tennessee": "TN", "texas": "TX", "utah": "UT", "vermont": "VT",
        "virginia": "VA", "virgin islands": "VI", "u.s. virgin islands": "VI",
        "us virgin islands": "VI", "washington": "WA",
        "west virginia": "WV", "wisconsin": "WI", "wyoming": "WY",
    }

    US_STATES: Dict[str, Tuple[str, str]] = {
        name: (code, name.title()) for name, code in STATE_NAME_TO_CODE.items()
    }

    # Clinical indication synonym rules mapped to (code, primary_key)
    CLINICAL_SYNONYMS = [
        # Postmastectomy lymphedema syndrome
        (re.compile(r"(breast cancer.*(?:lymphedema|swelling|arm swelling)|(?:lymphedema|swelling|arm swelling).*breast cancer|postmastectomy|post-mastectomy)", re.IGNORECASE), "I97.2", "ICD10-I97.2"),
        # Hereditary lymphedema
        (re.compile(r"(hereditary lymphedema|primary lymphedema|born with lymphedema|milroy)", re.IGNORECASE), "Q82.0", "ICD10-Q82.0"),
        # Secondary / other lymphedema
        (re.compile(r"(secondary lymphedema|swollen limb|leg lymphedema)", re.IGNORECASE), "I89.0", "ICD10-I89.0"),
        # General lymphedema fallback if not matched above
        (re.compile(r"(lymphedema|lymphoedema)", re.IGNORECASE), "I89.0", "ICD10-I89.0"),
        # Hypogammaglobulinemia
        (re.compile(r"(hypogammaglobulinemia|hereditary hypogammaglobulinemia)", re.IGNORECASE), "D80.0", "ICD10-D80.0"),
        # Common variable immunodeficiency
        (re.compile(r"(common variable immunodeficiency|cvid|immune deficiency)", re.IGNORECASE), "D83.9", "ICD10-D83.9"),
    ]

    # Direct HCPCS code regex (5-char alphanumeric starting with a letter)
    HCPCS_REGEX = re.compile(r"\b([A-Z]\d{4})\b", re.IGNORECASE)

    # Location indicator regex to catch unindexed locations
    GEO_LOCATION_INDICATORS = re.compile(r"(?:from|in|live in|resident of|located in)\s+([A-Za-z\s]+?)(?:,|\.|\bneed|\band|\bon|\bfor|\bsurvived|\bwith|\?|$)", re.IGNORECASE)

    # All 18 valid primary key prefixes in the 8-hop ontology
    VALID_PK_PREFIXES = (
        "POLICY-", "BILL-", "PLAW-", "STAT-", "USC-", "REG-FR-", "CFR-",
        "TR-CR", "DME-MAC-", "CMS-MCD-", "ICD10-", "HCPCS-", "FEE-",
        "JURIS-DME-", "STATE-", "LDA-", "CBO-", "PUBMED-",
    )

    # Direct primary key token pattern across all 18 valid prefixes (including Unicode en/em-dash in USC keys)
    PK_TOKEN_REGEX = re.compile(
        r"\b((?:POLICY-|BILL-|PLAW-|STAT-|USC-|REG-FR-|CFR-|TR-CR|DME-MAC-|CMS-MCD-|ICD10-|HCPCS-|FEE-|JURIS-DME-|STATE-|LDA-|CBO-|PUBMED-)[A-Za-z0-9\-_.\u2013\u2014]+)\b",
        re.IGNORECASE,
    )
    EXPLICIT_PK_PATTERN = PK_TOKEN_REGEX

    @staticmethod
    def _normalize_slot(label: str) -> str:
        slot = label.lower()
        if label == "State":
            return "state"
        if label in ("DiagnosisCode", "ICD10Code"):
            return "diagnosis"
        if label == "Policy":
            return "policy"
        if label in ("ProcedureCode", "HCPCSCode"):
            return "hcpcs"
        if label == "Jurisdiction":
            return "jurisdiction"
        if label in ("Transmittal", "ChangeRequest"):
            return "changerequest"
        if label == "CoveragePolicy":
            return "coveragepolicy"
        return slot

    def _load_graph_catalog(self, session: Session) -> List[Dict[str, Any]]:
        """Loads non-rate PolicyNode catalog entries from Neo4j for dynamic lexical resolution."""
        rows = session.run(
            """
            MATCH (n:PolicyNode)
            WHERE NOT n:FeeScheduleRate AND NOT n:FeeScheduleEntry AND NOT n:State
            RETURN n.primary_key AS primary_key, labels(n) AS labels, properties(n) AS props
            """
        ).data()
        return rows

    def resolve_anchors(self, query_text: str, session: Session) -> ResolvedAnchors:
        """Deterministically extracts anchors across all 17 node entity types, validating against Neo4j."""
        clean_text = query_text.strip()
        if not clean_text:
            return ResolvedAnchors()

        anchors_by_pk: Dict[str, AnchorEntity] = {}

        # 1. Direct Primary Key Token Resolution across all 18 prefixes with Fail-Fast validation
        for m in self.PK_TOKEN_REGEX.finditer(clean_text):
            candidate = m.group(1).rstrip(".,;:?)")
            record = session.run(
                "MATCH (n:PolicyNode) WHERE toUpper(n.primary_key) = toUpper($pk) "
                "RETURN n.primary_key AS primary_key, labels(n) AS labels, properties(n) AS props",
                pk=candidate,
            ).single()
            if not record:
                raise EntityResolutionError(
                    f"Unresolved primary key token '{candidate}' not found in knowledge graph.",
                    details={"unresolved_token": candidate},
                )
            actual_pk = record["primary_key"]
            props = dict(record["props"] or {})
            label = resolve_label_from_pk_and_labels(actual_pk, list(record["labels"] or []))
            matched = derive_node_display_name(label, actual_pk, props)
            slot = self._normalize_slot(label)

            anchors_by_pk[actual_pk] = AnchorEntity(
                slot=slot,
                primary_key=actual_pk,
                matched_text=str(matched),
                entity_type=label,
                label=label,
            )

        # Extract Jurisdiction Lexical Anchors early so fail-fast location check knows if a jurisdiction was referenced
        juris_anchors = self._extract_jurisdiction_anchors(clean_text, session)
        has_juris = bool(juris_anchors) or any(a.slot == "jurisdiction" for a in anchors_by_pk.values())

        # 2. Slot 1: Geographic State Anchor(s) across all 54 US states/territories (including GU)
        state_anchors = self._extract_state_anchors(clean_text, session, has_jurisdiction=has_juris)
        for sa in state_anchors:
            if sa.primary_key not in anchors_by_pk:
                anchors_by_pk[sa.primary_key] = sa

        # 3. Slot 2: Clinical Indication / DiagnosisCode Anchor
        diag_anchor = self._extract_diagnosis_anchor(clean_text, session)
        if diag_anchor and diag_anchor.primary_key not in anchors_by_pk:
            anchors_by_pk[diag_anchor.primary_key] = diag_anchor

        # 4. Slot 3: Policy Domain Anchor(s) (dynamically resolved against persisted Policy & legislative titles)
        policy_anchors = self._extract_policy_anchors(clean_text, session)
        for pa in policy_anchors:
            if pa.primary_key not in anchors_by_pk:
                anchors_by_pk[pa.primary_key] = pa

        # 5. ProcedureCode anchors (HCPCS)
        hcpcs_anchors = self._extract_hcpcs_anchors(clean_text, session)
        for ha in hcpcs_anchors:
            if ha.primary_key not in anchors_by_pk:
                anchors_by_pk[ha.primary_key] = ha

        # 6. Jurisdiction Lexical Anchors
        for ja in juris_anchors:
            if ja.primary_key not in anchors_by_pk:
                anchors_by_pk[ja.primary_key] = ja

        # 7. Transmittal / Change Request Lexical Anchors
        cr_anchors = self._extract_change_request_anchors(clean_text, session)
        for ca in cr_anchors:
            if ca.primary_key not in anchors_by_pk:
                anchors_by_pk[ca.primary_key] = ca

        # 8. Coverage Policy Lexical Anchors
        cp_anchors = self._extract_coverage_policy_anchors(clean_text, session)
        for cpa in cp_anchors:
            if cpa.primary_key not in anchors_by_pk:
                anchors_by_pk[cpa.primary_key] = cpa

        # 9. Legislative, Statutory, Regulatory, CFR & Contextual Lexical Anchors
        leg_anchors = self._extract_legislative_anchors(clean_text, session)
        for la in leg_anchors:
            if la.primary_key not in anchors_by_pk:
                anchors_by_pk[la.primary_key] = la

        all_anchors = list(anchors_by_pk.values())

        # Resolve primary slot pointers
        st_a = next((a for a in all_anchors if a.slot == "state"), None)
        dg_a = next((a for a in all_anchors if a.slot in ("diagnosis", "icd10code", "diagnosiscode")), None)
        pl_a = next((a for a in all_anchors if a.slot == "policy"), None)
        hc_a = next((a for a in all_anchors if a.slot in ("hcpcs", "hcpcscode", "procedurecode")), None)
        jr_a = next((a for a in all_anchors if a.slot == "jurisdiction"), None)
        cr_a = next((a for a in all_anchors if a.slot in ("changerequest", "change_request", "transmittal")), None)
        cp_a = next((a for a in all_anchors if a.slot in ("coveragepolicy", "coverage_policy")), None)

        return ResolvedAnchors(
            all_anchors=all_anchors,
            state_anchor=st_a,
            diagnosis_anchor=dg_a,
            policy_anchor=pl_a,
            hcpcs_anchor=hc_a,
            jurisdiction_anchor=jr_a,
            change_request_anchor=cr_a,
            transmittal_anchor=cr_a,
            coverage_policy_anchor=cp_a,
        )

    def resolve_explicit_anchor(self, primary_key: str, session: Session) -> ResolvedAnchors:
        """Deterministically verifies an explicit primary key against Neo4j, bypassing regex extraction."""
        clean_pk = primary_key.strip()
        record = session.run(
            "MATCH (n:PolicyNode) WHERE toUpper(n.primary_key) = toUpper($pk) "
            "RETURN n.primary_key AS primary_key, labels(n) AS labels, properties(n) AS props",
            pk=clean_pk,
        ).single()

        if not record:
            raise EntityResolutionError(
                f"Entity with primary_key '{clean_pk}' not found in knowledge graph.",
                details={"primary_key": clean_pk, "unresolved_token": clean_pk},
            )

        actual_pk = record["primary_key"]
        props = dict(record["props"] or {})
        label = resolve_label_from_pk_and_labels(actual_pk, list(record["labels"] or []))
        matched = derive_node_display_name(label, actual_pk, props)
        slot = self._normalize_slot(label)

        anchor = AnchorEntity(
            slot=slot,
            primary_key=actual_pk,
            matched_text=str(matched),
            entity_type=label,
            label=label,
        )

        resolved = ResolvedAnchors(all_anchors=[anchor])
        if slot == "state":
            resolved.state_anchor = anchor
        elif slot in ("diagnosis", "icd10code", "diagnosiscode"):
            resolved.diagnosis_anchor = anchor
        elif slot == "policy":
            resolved.policy_anchor = anchor
        elif slot in ("hcpcs", "hcpcscode", "procedurecode"):
            resolved.hcpcs_anchor = anchor
        elif slot == "jurisdiction":
            resolved.jurisdiction_anchor = anchor
        elif slot in ("changerequest", "transmittal"):
            resolved.change_request_anchor = anchor
            resolved.transmittal_anchor = anchor
        elif slot == "coveragepolicy":
            resolved.coverage_policy_anchor = anchor

        return resolved

    def _extract_jurisdiction_anchors(self, text: str, session: Session) -> List[AnchorEntity]:
        """Matches Medicare Administrative Contractor names or DME MAC jurisdiction codes, failing fast on invalid jurisdictions."""
        anchors: List[AnchorEntity] = []
        matched_pks = set()

        # Fail-fast check for invalid DME MAC jurisdiction codes (e.g. "Jurisdiction E", "DME MAC Z")
        bad_juris_pattern = re.compile(
            r"\b(?:dme\s*mac\s*(?:jurisdiction\s*)?|jurisdiction\s+)([a-z0-9]+)\b",
            re.IGNORECASE,
        )
        for bm in bad_juris_pattern.finditer(text):
            token = bm.group(1).strip().upper()
            if token not in {"A", "B", "C", "D"} and token not in {"THE", "FOR", "IN", "OF", "AND", "OR", "TO"}:
                if len(token) == 1 or token.isdigit():
                    raise EntityResolutionError(
                        f"Unrecognized DME MAC jurisdiction '{bm.group(0)}'.",
                        details={"unresolved_token": bm.group(0)},
                    )

        explicit_mappings = [
            (re.compile(r"\b(?:jurisdiction\s*a|dme\s*mac\s*(?:jurisdiction\s*)?a|mac\s*(?:jurisdiction\s*)?a|juris-dme-a)\b", re.IGNORECASE), "JURIS-DME-A"),
            (re.compile(r"\b(?:jurisdiction\s*b|dme\s*mac\s*(?:jurisdiction\s*)?b|mac\s*(?:jurisdiction\s*)?b|juris-dme-b)\b", re.IGNORECASE), "JURIS-DME-B"),
            (re.compile(r"\b(?:jurisdiction\s*c|dme\s*mac\s*(?:jurisdiction\s*)?c|mac\s*(?:jurisdiction\s*)?c|juris-dme-c)\b", re.IGNORECASE), "JURIS-DME-C"),
            (re.compile(r"\b(?:jurisdiction\s*d|dme\s*mac\s*(?:jurisdiction\s*)?d|mac\s*(?:jurisdiction\s*)?d|juris-dme-d)\b", re.IGNORECASE), "JURIS-DME-D"),
        ]
        for pattern, pk in explicit_mappings:
            m = pattern.search(text)
            if m:
                rec = session.run("MATCH (j:Jurisdiction {primary_key: $pk}) RETURN j", pk=pk).single()
                if rec:
                    matched_pks.add(pk)
                    anchors.append(
                        AnchorEntity(
                            slot="jurisdiction",
                            primary_key=pk,
                            matched_text=text[m.start():m.end()],
                            entity_type="Jurisdiction",
                            label="Jurisdiction",
                        )
                    )

        # Dynamic contractor name resolution from persisted Jurisdiction nodes
        juris_rows = session.run("MATCH (j:Jurisdiction) RETURN j.primary_key AS pk, j.contractor_name AS cname").data()
        for jrow in juris_rows:
            jpk = jrow.get("pk")
            cname = str(jrow.get("cname") or "")
            if not jpk or jpk in matched_pks or not cname:
                continue
            first_word = cname.split()[0]
            if len(first_word) >= 3:
                cm = re.search(rf"\b{re.escape(first_word)}\b", text, re.IGNORECASE)
                if cm:
                    matched_pks.add(jpk)
                    anchors.append(
                        AnchorEntity(
                            slot="jurisdiction",
                            primary_key=jpk,
                            matched_text=text[cm.start():cm.end()],
                            entity_type="Jurisdiction",
                            label="Jurisdiction",
                        )
                    )

        return anchors

    def _extract_change_request_anchors(self, text: str, session: Session) -> List[AnchorEntity]:
        """Dynamically matches Transmittal / Change Request references against persisted :Transmittal nodes."""
        anchors: List[AnchorEntity] = []
        rows = session.run("MATCH (tr:Transmittal) RETURN properties(tr) AS props").data()
        text_upper = text.upper()
        for row in rows:
            props = row.get("props") or {}
            pk = str(props.get("primary_key") or "")
            cr_num = str(props.get("cr_number") or "").upper()  # e.g. CR13286
            cr_digits = cr_num.replace("CR", "").strip()
            tr_num = str(props.get("transmittal_number") or "").upper()  # e.g. R12471CP
            superseded = [str(s).upper() for s in (props.get("superseded_transmittal_numbers") or [])]

            matched_str: Optional[str] = None
            if cr_digits:
                m_cr = re.search(rf"\b(?:cr|change\s+request|transmittal)\s*[-#]?\s*{re.escape(cr_digits)}\b", text, re.IGNORECASE)
                if m_cr:
                    matched_str = m_cr.group(0)
            if not matched_str and tr_num and tr_num in text_upper:
                matched_str = tr_num
            if not matched_str:
                for sup in superseded:
                    if sup and sup in text_upper:
                        matched_str = sup
                        break

            if matched_str and pk:
                anchors.append(
                    AnchorEntity(
                        slot="changerequest",
                        primary_key=pk,
                        matched_text=matched_str,
                        entity_type="Transmittal",
                        label="Transmittal",
                    )
                )
        return anchors

    def _extract_coverage_policy_anchors(self, text: str, session: Session) -> List[AnchorEntity]:
        """Dynamically matches Coverage Policy or DME MAC / MCD article references against persisted :CoveragePolicy nodes."""
        anchors: List[AnchorEntity] = []
        rows = session.run("MATCH (cp:CoveragePolicy) RETURN properties(cp) AS props").data()
        text_upper = text.upper()
        for row in rows:
            props = row.get("props") or {}
            pk = str(props.get("primary_key") or "")
            art_id = str(props.get("article_id") or "").upper()
            art_suffix = art_id.replace("DME-MAC-", "").replace("CMS-MCD-", "")
            title = str(props.get("title") or "")

            matched_str: Optional[str] = None
            if art_suffix and art_suffix in text_upper:
                matched_str = art_suffix
            elif title and len(title) > 10 and title.lower() in text.lower():
                matched_str = title

            if matched_str and pk:
                anchors.append(
                    AnchorEntity(
                        slot="coveragepolicy",
                        primary_key=pk,
                        matched_text=matched_str,
                        entity_type="CoveragePolicy",
                        label="CoveragePolicy",
                    )
                )
        return anchors

    def _extract_legislative_anchors(self, text: str, session: Session) -> List[AnchorEntity]:
        """Dynamically matches PublicLaw, Bill, StatutorySection, USCSection, Regulation, CFRSection, CBOScore, LobbyingFiling, and LiteratureStudy nodes."""
        anchors: List[AnchorEntity] = []
        text_upper = text.upper()

        # 1. PublicLaw nodes
        pl_rows = session.run("MATCH (pl:PublicLaw) RETURN properties(pl) AS props").data()
        for row in pl_rows:
            props = row.get("props") or {}
            pk = str(props.get("primary_key") or "")
            cong = props.get("congress")
            num = props.get("number") or props.get("public_law_number")
            if pk and cong and num:
                m = re.search(rf"\b(?:public\s+law|p\.?l\.?)\s*{cong}\s*[-–]\s*{num}\b|\b{cong}\s*[-–]\s*{num}\b", text, re.IGNORECASE)
                if m:
                    anchors.append(
                        AnchorEntity(
                            slot="publiclaw",
                            primary_key=pk,
                            matched_text=m.group(0),
                            entity_type="PublicLaw",
                            label="PublicLaw",
                        )
                    )

        # 2. Bill nodes
        bill_rows = session.run("MATCH (b:Bill) RETURN properties(b) AS props").data()
        for row in bill_rows:
            props = row.get("props") or {}
            pk = str(props.get("primary_key") or "")
            b_type = str(props.get("type") or props.get("bill_type") or "").lower()
            b_num = str(props.get("number") or props.get("bill_number") or "")
            if pk and b_num:
                if b_type == "hr":
                    pat = rf"\b(?:h\.?\s*r\.?)\s*{re.escape(b_num)}\b"
                elif b_type == "s":
                    pat = rf"\b(?:s\.?)\s*{re.escape(b_num)}\b"
                else:
                    pat = rf"\b{re.escape(b_type)}\s*{re.escape(b_num)}\b"
                m = re.search(pat, text, re.IGNORECASE)
                if m:
                    anchors.append(
                        AnchorEntity(
                            slot="bill",
                            primary_key=pk,
                            matched_text=m.group(0),
                            entity_type="Bill",
                            label="Bill",
                        )
                    )

        # 3. StatutorySection nodes
        stat_rows = session.run("MATCH (s:StatutorySection) RETURN properties(s) AS props").data()
        for row in stat_rows:
            props = row.get("props") or {}
            pk = str(props.get("primary_key") or "")
            sec_num = str(props.get("statute_section_number") or props.get("section_number") or "")
            uslm = str(props.get("uslm_section_path") or "")
            if pk and sec_num:
                m = re.search(rf"\b(?:section|sec\.?)\s*{re.escape(sec_num)}\b", text, re.IGNORECASE)
                if m:
                    anchors.append(
                        AnchorEntity(
                            slot="statutorysection",
                            primary_key=pk,
                            matched_text=m.group(0),
                            entity_type="StatutorySection",
                            label="StatutorySection",
                        )
                    )
                elif uslm and uslm.lower() in text.lower():
                    anchors.append(
                        AnchorEntity(
                            slot="statutorysection",
                            primary_key=pk,
                            matched_text=uslm,
                            entity_type="StatutorySection",
                            label="StatutorySection",
                        )
                    )

        # 4. USCSection nodes
        usc_rows = session.run("MATCH (u:USCSection) RETURN properties(u) AS props").data()
        for row in usc_rows:
            props = row.get("props") or {}
            pk = str(props.get("primary_key") or "")
            cit = str(props.get("citation_string") or props.get("citation") or "")
            sec = str(props.get("section") or props.get("section_code") or "")
            if pk:
                if cit and cit.lower() in text.lower():
                    anchors.append(
                        AnchorEntity(
                            slot="uscsection",
                            primary_key=pk,
                            matched_text=cit,
                            entity_type="USCSection",
                            label="USCSection",
                        )
                    )
                elif sec and re.search(rf"\b{re.escape(sec)}\b", text, re.IGNORECASE):
                    anchors.append(
                        AnchorEntity(
                            slot="uscsection",
                            primary_key=pk,
                            matched_text=sec,
                            entity_type="USCSection",
                            label="USCSection",
                        )
                    )

        # 5. Regulation nodes
        reg_rows = session.run("MATCH (r:Regulation) RETURN properties(r) AS props").data()
        for row in reg_rows:
            props = row.get("props") or {}
            pk = str(props.get("primary_key") or "")
            cit = str(props.get("citation") or "")
            doc_num = str(props.get("document_number") or "")
            docket = str(props.get("docket_id") or "")
            rin = str(props.get("rin") or "")
            matched_str = None
            for tok in (cit, doc_num, docket, rin):
                if tok and tok.upper() in text_upper:
                    matched_str = tok
                    break
            if matched_str and pk:
                anchors.append(
                    AnchorEntity(
                        slot="regulation",
                        primary_key=pk,
                        matched_text=matched_str,
                        entity_type="Regulation",
                        label="Regulation",
                    )
                )

        # 6. CFRSection nodes
        cfr_rows = session.run("MATCH (c:CFRSection) RETURN properties(c) AS props").data()
        for row in cfr_rows:
            props = row.get("props") or {}
            pk = str(props.get("primary_key") or "")
            cfr_ref = str(props.get("cfr_reference") or "")
            part = str(props.get("part") or props.get("part_number") or "")
            matched_str = None
            if cfr_ref and cfr_ref.upper() in text_upper:
                matched_str = cfr_ref
            elif part and re.search(rf"\b(?:42\s*cfr\s*(?:part\s*)?|cfr\s+part\s+){re.escape(part)}\b", text, re.IGNORECASE):
                matched_str = f"42 CFR Part {part}"
            if matched_str and pk:
                anchors.append(
                    AnchorEntity(
                        slot="cfrsection",
                        primary_key=pk,
                        matched_text=matched_str,
                        entity_type="CFRSection",
                        label="CFRSection",
                    )
                )

        # 7. CBOScore, LobbyingFiling, LiteratureStudy nodes
        cbo_rows = session.run("MATCH (c:CBOScore) RETURN properties(c) AS props").data()
        for row in cbo_rows:
            props = row.get("props") or {}
            pk = str(props.get("primary_key") or "")
            cid = str(props.get("id") or "")
            if pk and cid and re.search(rf"\b(?:cbo\s*)?{re.escape(cid)}\b", text, re.IGNORECASE):
                anchors.append(
                    AnchorEntity(
                        slot="cboscore",
                        primary_key=pk,
                        matched_text=cid,
                        entity_type="CBOScore",
                        label="CBOScore",
                    )
                )

        pub_rows = session.run("MATCH (s:LiteratureStudy) RETURN properties(s) AS props").data()
        for row in pub_rows:
            props = row.get("props") or {}
            pk = str(props.get("primary_key") or "")
            pmid = str(props.get("pmid") or "")
            if pk and pmid and re.search(rf"\b{re.escape(pmid)}\b", text):
                anchors.append(
                    AnchorEntity(
                        slot="literaturestudy",
                        primary_key=pk,
                        matched_text=pmid,
                        entity_type="LiteratureStudy",
                        label="LiteratureStudy",
                    )
                )

        return anchors

    def _extract_state_anchors(
        self,
        text: str,
        session: Session,
        has_jurisdiction: bool = False,
    ) -> List[AnchorEntity]:
        """Matches all state/territory names or 2-letter postal codes (all 54 including GU) and validates in Neo4j."""
        lower_text = text.lower()
        matched_spans: List[Tuple[int, int]] = []
        matched_anchors: List[Tuple[int, AnchorEntity]] = []
        matched_codes = set()

        def spans_overlap(start: int, end: int) -> bool:
            for s, e in matched_spans:
                if not (end <= s or start >= e):
                    return True
            return False

        # Step A: Check full state names first (sorted by length descending so "West Virginia" matches before "Virginia")
        for state_name in sorted(self.STATE_NAME_TO_CODE.keys(), key=len, reverse=True):
            pattern = rf"\b{re.escape(state_name)}\b"
            for m in re.finditer(pattern, lower_text):
                if spans_overlap(m.start(), m.end()):
                    continue
                code = self.STATE_NAME_TO_CODE[state_name]
                pk = f"STATE-{code}"
                record = session.run("MATCH (s:State {primary_key: $pk}) RETURN s", pk=pk).single()
                if record:
                    matched_spans.append((m.start(), m.end()))
                    matched_codes.add(code)
                    matched_anchors.append(
                        (
                            m.start(),
                            AnchorEntity(
                                slot="state",
                                primary_key=pk,
                                matched_text=text[m.start():m.end()],
                                entity_type="State",
                                label="State",
                            ),
                        )
                    )

        # Step B: Check 2-letter uppercase codes with boundaries for codes not already matched
        ambiguous_upper_words = {"IN", "OR", "ME", "HI", "OK"}
        for code in sorted(set(self.STATE_NAME_TO_CODE.values())):
            if code in matched_codes:
                continue
            pattern = rf"\b{code}\b"
            for m in re.finditer(pattern, text):
                if spans_overlap(m.start(), m.end()):
                    continue
                if code in ambiguous_upper_words:
                    if text.isupper():
                        continue
                    after_text = text[m.end():].lstrip()
                    if code in {"IN", "OR"} and after_text and after_text[0].isalpha():
                        continue
                pk = f"STATE-{code}"
                record = session.run("MATCH (s:State {primary_key: $pk}) RETURN s", pk=pk).single()
                if record:
                    matched_spans.append((m.start(), m.end()))
                    matched_codes.add(code)
                    matched_anchors.append(
                        (
                            m.start(),
                            AnchorEntity(
                                slot="state",
                                primary_key=pk,
                                matched_text=m.group(0),
                                entity_type="State",
                                label="State",
                            ),
                        )
                    )

        # Sort by match position ascending and deduplicate by primary_key
        matched_anchors.sort(key=lambda pair: pair[0])
        result_anchors: List[AnchorEntity] = []
        seen_pks = set()
        for _, anchor in matched_anchors:
            if anchor.primary_key not in seen_pks:
                seen_pks.add(anchor.primary_key)
                result_anchors.append(anchor)

        # Fail-fast check: Only trigger when zero State and zero Jurisdiction anchors were resolved
        if not result_anchors and not has_jurisdiction:
            geo_match = self.GEO_LOCATION_INDICATORS.search(text)
            if geo_match:
                candidate = geo_match.group(1).strip()
                cand_lower = candidate.lower()
                stopwords = {
                    "home", "yesterday", "scratch", "pain", "now", "today", "here", "there",
                    "medicare", "general", "part b", "jurisdiction a", "jurisdiction b",
                    "jurisdiction c", "jurisdiction d", "dme mac", "cgs", "noridian",
                }
                non_geo_terms = ("jurisdiction", "mac", "cgs", "noridian", "medicare", "policy", "part b")
                if (
                    cand_lower not in stopwords
                    and len(candidate) > 2
                    and not any(term in cand_lower for term in non_geo_terms)
                ):
                    if cand_lower not in self.STATE_NAME_TO_CODE:
                        raise EntityResolutionError(
                            f"Unrecognized geographic jurisdiction '{candidate}'.",
                            details={"extracted_geo": candidate},
                        )

        return result_anchors

    def _extract_state_anchor(self, text: str, session: Session) -> Optional[AnchorEntity]:
        """Matches first state name or 2-letter postal code and validates in Neo4j."""
        anchors = self._extract_state_anchors(text, session)
        return anchors[0] if anchors else None

    def _extract_diagnosis_anchor(self, text: str, session: Session) -> Optional[AnchorEntity]:
        """Matches clinical terms and ICD-10 codes dynamically against persisted DiagnosisCode nodes in Neo4j."""
        lower_text = text.lower()

        # 1. Direct ICD-10 code format (e.g., "I97.2", "Q82.0", "I97.89")
        direct_match = re.search(r"\b([A-TV-Z]\d{2}(?:\.\d{1,4})?)\b", text)
        if direct_match:
            code_cand = direct_match.group(1).upper()
            pk = f"ICD10-{code_cand}"
            rec = session.run(
                "MATCH (d:PolicyNode {primary_key: $pk}) WHERE d:DiagnosisCode OR d:ICD10Code RETURN d, labels(d) AS lbls",
                pk=pk,
            ).single()
            if rec:
                lbl = "DiagnosisCode" if "DiagnosisCode" in rec["lbls"] else "ICD10Code"
                return AnchorEntity(
                    slot="diagnosis",
                    primary_key=pk,
                    matched_text=direct_match.group(0),
                    entity_type=lbl,
                    label=lbl,
                )

        # 2. Match against persisted DiagnosisCode descriptions
        diag_rows = session.run(
            "MATCH (d:PolicyNode) WHERE d:DiagnosisCode OR d:ICD10Code RETURN properties(d) AS props, labels(d) AS lbls"
        ).data()
        for row in diag_rows:
            props = row.get("props") or {}
            pk = str(props.get("primary_key") or "")
            desc = str(props.get("description") or "").lower()
            if pk and desc and len(desc) > 5 and desc in lower_text:
                lbl = "DiagnosisCode" if "DiagnosisCode" in (row.get("lbls") or []) else "ICD10Code"
                return AnchorEntity(
                    slot="diagnosis",
                    primary_key=pk,
                    matched_text=desc,
                    entity_type=lbl,
                    label=lbl,
                )

        # 3. Match clinical synonym patterns validated against Neo4j
        for pattern, code, pk in self.CLINICAL_SYNONYMS:
            m = pattern.search(lower_text)
            if m:
                rec = session.run(
                    "MATCH (d:PolicyNode {primary_key: $pk}) WHERE d:DiagnosisCode OR d:ICD10Code RETURN d, labels(d) AS lbls",
                    pk=pk,
                ).single()
                if rec:
                    lbl = "DiagnosisCode" if "DiagnosisCode" in rec["lbls"] else "ICD10Code"
                    return AnchorEntity(
                        slot="diagnosis",
                        primary_key=pk,
                        matched_text=text[m.start():m.end()],
                        entity_type=lbl,
                        label=lbl,
                    )

        # 4. Fail-fast check for unindexed medical conditions
        unindexed_conditions = ["diabetes", "hypertension", "asthma", "broken bone", "heart disease", "fracture", "arthritis"]
        for unindexed in unindexed_conditions:
            if re.search(rf"\b{re.escape(unindexed)}\b", lower_text):
                raise EntityResolutionError(
                    f"No authorized Medicare coverage policy found for condition '{unindexed}'.",
                    details={"extracted_condition": unindexed},
                )

        return None

    def _extract_policy_anchors(self, text: str, session: Session) -> List[AnchorEntity]:
        """Dynamically resolves policy domain keywords against persisted Policy nodes and their connected legislative titles/headings."""
        anchors: List[AnchorEntity] = []
        rows = session.run(
            """
            MATCH (p:Policy)
            OPTIONAL MATCH (p)-[:DISCOVERED_BILL]->(b:Bill)
            OPTIONAL MATCH (p)-[:DISCOVERED_BILL]->(:Bill)-[:INCORPORATED_INTO|ENACTED_AS*1..2]->(:PublicLaw)-[:CONTAINS]->(s:StatutorySection)
            OPTIONAL MATCH (:Transmittal)-[:MANDATES_POLICY]->(cp:CoveragePolicy)
            RETURN p.primary_key AS pk,
                   p.keyword AS keyword,
                   collect(DISTINCT b.title) AS bill_titles,
                   collect(DISTINCT s.heading) AS headings,
                   collect(DISTINCT cp.title) AS cp_titles
            """
        ).data()

        stopwords = {"THE", "ACT", "OF", "FOR", "AND", "IN", "TO", "CERTAIN", "MEDICARE", "COVERAGE", "ITEMS", "TREATMENT", "REVISED", "CORRECT", "CODING", "BILLING"}
        for row in rows:
            pk = str(row.get("pk") or "")
            kw = str(row.get("keyword") or "").strip()
            if not pk:
                continue

            matched_str: Optional[str] = None
            if kw:
                m_kw = re.search(rf"\b{re.escape(kw)}\b", text, re.IGNORECASE)
                if m_kw:
                    matched_str = m_kw.group(0)

            if not matched_str:
                candidate_phrases: List[str] = []
                for t in (row.get("bill_titles") or []) + (row.get("headings") or []) + (row.get("cp_titles") or []):
                    if not t:
                        continue
                    t_str = str(t).strip()
                    if len(t_str) > 5:
                        candidate_phrases.append(t_str)
                    for word in re.findall(r"[A-Za-z]{5,}", t_str):
                        if word.upper() not in stopwords:
                            candidate_phrases.append(word)

                for phrase in candidate_phrases:
                    m_ph = re.search(rf"\b{re.escape(phrase)}\b", text, re.IGNORECASE)
                    if m_ph:
                        matched_str = m_ph.group(0)
                        break

            if matched_str:
                anchors.append(
                    AnchorEntity(
                        slot="policy",
                        primary_key=pk,
                        matched_text=matched_str,
                        entity_type="Policy",
                        label="Policy",
                    )
                )
        return anchors

    def _extract_hcpcs_anchors(self, text: str, session: Session) -> List[AnchorEntity]:
        """Extracts explicitly cited 5-character HCPCS codes and validates against persisted ProcedureCode nodes."""
        anchors: List[AnchorEntity] = []
        for match in self.HCPCS_REGEX.finditer(text):
            code = match.group(1).upper()
            pk = f"HCPCS-{code}"
            rec = session.run(
                "MATCH (h:PolicyNode {primary_key: $pk}) WHERE h:ProcedureCode OR h:HCPCSCode RETURN h, labels(h) AS lbls",
                pk=pk,
            ).single()
            if rec:
                lbl = "ProcedureCode" if "ProcedureCode" in rec["lbls"] else "HCPCSCode"
                anchors.append(
                    AnchorEntity(
                        slot="hcpcs",
                        primary_key=pk,
                        matched_text=match.group(0),
                        entity_type=lbl,
                        label=lbl,
                    )
                )
        return anchors

