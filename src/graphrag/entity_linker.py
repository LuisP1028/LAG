"""Deterministic Multi-Slot Entity Anchor Linker resolving queries into graph entry points."""

import re
from typing import Dict, List, Optional, Tuple
from neo4j import Session

from src.graphrag.exceptions import EntityResolutionError
from src.graphrag.models import AnchorEntity, ResolvedAnchors


class EntityAnchorLinker:
    """Resolves free-form natural language prompts into verified Neo4j entity anchors."""

    # Authoritative 53 Medicare Part B states and territories mapped to two-letter codes
    STATE_NAME_TO_CODE: Dict[str, str] = {
        "alabama": "AL", "alaska": "AK", "arizona": "AZ", "arkansas": "AR",
        "california": "CA", "colorado": "CO", "connecticut": "CT", "delaware": "DE",
        "district of columbia": "DC", "florida": "FL", "georgia": "GA", "hawaii": "HI",
        "idaho": "ID", "illinois": "IL", "indiana": "IN", "iowa": "IA",
        "kansas": "KS", "kentucky": "KY", "louisiana": "LA", "maine": "ME",
        "maryland": "MD", "massachusetts": "MA", "michigan": "MI", "minnesota": "MN",
        "mississippi": "MS", "missouri": "MO", "montana": "MT", "nebraska": "NE",
        "nevada": "NV", "new hampshire": "NH", "new jersey": "NJ", "new mexico": "NM",
        "new york": "NY", "north carolina": "NC", "north dakota": "ND", "ohio": "OH",
        "oklahoma": "OK", "oregon": "OR", "pennsylvania": "PA", "puerto rico": "PR",
        "rhode island": "RI", "south carolina": "SC", "south dakota": "SD",
        "tennessee": "TN", "texas": "TX", "utah": "UT", "vermont": "VT",
        "virginia": "VA", "virgin islands": "VI", "washington": "WA",
        "west virginia": "WV", "wisconsin": "WI", "wyoming": "WY",
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

    # Policy domain triggers
    POLICY_TRIGGERS = [
        (re.compile(r"(lymphedema supplies|compression sleeve|compression garment|daytime sleeve|nighttime wrap|\blta\b|lymphedema treatment act)", re.IGNORECASE), "POLICY-LTA"),
        (re.compile(r"(\bivig\b|intravenous immune globulin|immune globulin|in-home infusion|infusion demonstration)", re.IGNORECASE), "POLICY-IVIG"),
    ]

    # Direct HCPCS code regex
    HCPCS_REGEX = re.compile(r"\b([AQ]\d{4})\b", re.IGNORECASE)

    # Location indicator regex to catch unindexed locations
    GEO_LOCATION_INDICATORS = re.compile(r"(?:from|in|live in|resident of|located in)\s+([A-Za-z\s]+?)(?:,|\.|\bneed|\band|\bon|\bfor|\bsurvived|\bwith|\?|$)", re.IGNORECASE)

    # Direct primary key token pattern
    PK_TOKEN_REGEX = re.compile(r"\b([A-Z0-9]+-[A-Z0-9\-_.]{2,})\b")

    def resolve_anchors(self, query_text: str, session: Session) -> ResolvedAnchors:
        """Deterministically extracts anchors across all 14 node entity types, validating against Neo4j."""
        clean_text = query_text.strip()
        if not clean_text:
            return ResolvedAnchors()

        anchors_by_pk: Dict[str, AnchorEntity] = {}

        # 1. Direct Primary Key Token Resolution
        for m in self.PK_TOKEN_REGEX.finditer(clean_text):
            candidate = m.group(1)
            # Query Neo4j to verify existence across all 14 node types
            record = session.run(
                "MATCH (n:PolicyNode {primary_key: $pk}) "
                "RETURN n.primary_key AS primary_key, labels(n) AS labels, n.name AS name, n.title AS title",
                pk=candidate,
            ).single()
            if record:
                labels = [l for l in record["labels"] if l != "PolicyNode"]
                label = labels[0] if labels else "PolicyNode"
                matched = record["name"] or record["title"] or candidate
                slot = label.lower()
                if slot == "icd10code":
                    slot = "diagnosis"
                elif slot == "hcpcscode":
                    slot = "hcpcs"
                elif slot == "coveragepolicy":
                    slot = "coveragepolicy"
                elif slot == "changerequest":
                    slot = "changerequest"

                anchors_by_pk[candidate] = AnchorEntity(
                    slot=slot,
                    primary_key=candidate,
                    matched_text=str(matched),
                    entity_type=label,
                    label=label,
                )

        # 2. Slot 1: Geographic State Anchor
        state_anchor = self._extract_state_anchor(clean_text, session)
        if state_anchor and state_anchor.primary_key not in anchors_by_pk:
            anchors_by_pk[state_anchor.primary_key] = state_anchor

        # 3. Slot 2: Clinical Indication Anchor
        diag_anchor = self._extract_diagnosis_anchor(clean_text, session)
        if diag_anchor and diag_anchor.primary_key not in anchors_by_pk:
            anchors_by_pk[diag_anchor.primary_key] = diag_anchor

        # 4. Slot 3: Policy Domain Anchor(s)
        policy_anchors = self._extract_policy_anchors(clean_text, session)
        for pa in policy_anchors:
            if pa.primary_key not in anchors_by_pk:
                anchors_by_pk[pa.primary_key] = pa

        # 5. Procedure code anchors (HCPCS)
        hcpcs_anchors = self._extract_hcpcs_anchors(clean_text, session)
        for ha in hcpcs_anchors:
            if ha.primary_key not in anchors_by_pk:
                anchors_by_pk[ha.primary_key] = ha

        # 6. Jurisdiction Lexical Anchors
        juris_anchors = self._extract_jurisdiction_anchors(clean_text, session)
        for ja in juris_anchors:
            if ja.primary_key not in anchors_by_pk:
                anchors_by_pk[ja.primary_key] = ja

        # 7. Change Request Lexical Anchors
        cr_anchors = self._extract_change_request_anchors(clean_text, session)
        for ca in cr_anchors:
            if ca.primary_key not in anchors_by_pk:
                anchors_by_pk[ca.primary_key] = ca

        # 8. Coverage Policy Lexical Anchors
        cp_anchors = self._extract_coverage_policy_anchors(clean_text, session)
        for cpa in cp_anchors:
            if cpa.primary_key not in anchors_by_pk:
                anchors_by_pk[cpa.primary_key] = cpa

        # 9. Legislative & Regulatory Lexical Anchors
        leg_anchors = self._extract_legislative_anchors(clean_text, session)
        for la in leg_anchors:
            if la.primary_key not in anchors_by_pk:
                anchors_by_pk[la.primary_key] = la

        all_anchors = list(anchors_by_pk.values())

        # Resolve primary slot pointers
        st_a = next((a for a in all_anchors if a.slot == "state"), None)
        dg_a = next((a for a in all_anchors if a.slot in ("diagnosis", "icd10code")), None)
        pl_a = next((a for a in all_anchors if a.slot == "policy"), None)
        hc_a = next((a for a in all_anchors if a.slot in ("hcpcs", "hcpcscode")), None)
        jr_a = next((a for a in all_anchors if a.slot == "jurisdiction"), None)
        cr_a = next((a for a in all_anchors if a.slot in ("changerequest", "change_request")), None)
        cp_a = next((a for a in all_anchors if a.slot in ("coveragepolicy", "coverage_policy")), None)

        return ResolvedAnchors(
            all_anchors=all_anchors,
            state_anchor=st_a,
            diagnosis_anchor=dg_a,
            policy_anchor=pl_a,
            hcpcs_anchor=hc_a,
            jurisdiction_anchor=jr_a,
            change_request_anchor=cr_a,
            coverage_policy_anchor=cp_a,
        )

    def _extract_jurisdiction_anchors(self, text: str, session: Session) -> List[AnchorEntity]:
        """Matches Medicare Administrative Contractor names or jurisdiction codes."""
        anchors = []
        mappings = [
            (re.compile(r"\b(?:noridian|jurisdiction\s*a)\b", re.IGNORECASE), "JURIS-DME-A"),
            (re.compile(r"\b(?:cgs(?:\s+administrators)?|jurisdiction\s*b)\b", re.IGNORECASE), "JURIS-DME-B"),
            (re.compile(r"\bjurisdiction\s*c\b", re.IGNORECASE), "JURIS-DME-C"),
            (re.compile(r"\bjurisdiction\s*d\b", re.IGNORECASE), "JURIS-DME-D"),
        ]
        for pattern, pk in mappings:
            m = pattern.search(text)
            if m:
                rec = session.run("MATCH (j:Jurisdiction {primary_key: $pk}) RETURN j", pk=pk).single()
                if rec:
                    node = rec["j"]
                    anchors.append(
                        AnchorEntity(
                            slot="jurisdiction",
                            primary_key=pk,
                            matched_text=text[m.start():m.end()],
                            entity_type="Jurisdiction",
                            label="Jurisdiction",
                        )
                    )
        return anchors

    def _extract_change_request_anchors(self, text: str, session: Session) -> List[AnchorEntity]:
        """Matches Change Request references (e.g. CR 13286, Transmittal 13286)."""
        anchors = []
        pattern = re.compile(r"\b(?:cr|change\s+request|transmittal)\s*([0-9]{4,5})\b", re.IGNORECASE)
        for m in pattern.finditer(text):
            num = m.group(1)
            pk = f"CMS-CR-{num}"
            rec = session.run("MATCH (cr:ChangeRequest {primary_key: $pk}) RETURN cr", pk=pk).single()
            if rec:
                anchors.append(
                    AnchorEntity(
                        slot="changerequest",
                        primary_key=pk,
                        matched_text=m.group(0),
                        entity_type="ChangeRequest",
                        label="ChangeRequest",
                    )
                )
        return anchors

    def _extract_coverage_policy_anchors(self, text: str, session: Session) -> List[AnchorEntity]:
        """Matches Coverage Policy or Article references (e.g. A59508, LCD A59508)."""
        anchors = []
        pattern = re.compile(r"\b(?:lcd|article|coverage\s+policy|mcd)?\s*(A\d{5})\b", re.IGNORECASE)
        for m in pattern.finditer(text):
            art_id = m.group(1).upper()
            pk = f"CMS-MCD-{art_id}"
            rec = session.run("MATCH (cp:CoveragePolicy {primary_key: $pk}) RETURN cp", pk=pk).single()
            if rec:
                anchors.append(
                    AnchorEntity(
                        slot="coveragepolicy",
                        primary_key=pk,
                        matched_text=m.group(0),
                        entity_type="CoveragePolicy",
                        label="CoveragePolicy",
                    )
                )
        return anchors

    def _extract_legislative_anchors(self, text: str, session: Session) -> List[AnchorEntity]:
        """Matches Public Law, Regulation, and Bill citations."""
        anchors = []

        # Public Law: Public Law 117-328 or PL 117-328
        pl_pattern = re.compile(r"\b(?:public\s+law|pl)\s*(\d+)-(\d+)\b", re.IGNORECASE)
        for m in pl_pattern.finditer(text):
            pk = f"PLAW-{m.group(1)}-{m.group(2)}"
            rec = session.run("MATCH (pl:PublicLaw {primary_key: $pk}) RETURN pl", pk=pk).single()
            if rec:
                anchors.append(
                    AnchorEntity(
                        slot="publiclaw",
                        primary_key=pk,
                        matched_text=m.group(0),
                        entity_type="PublicLaw",
                        label="PublicLaw",
                    )
                )

        # Regulation: 88 FR 77676 or CMS-1784-F
        reg_pattern = re.compile(r"\b(?:(\d+)\s*fr\s*(\d+)|cms-1784-f)\b", re.IGNORECASE)
        for m in reg_pattern.finditer(text):
            pk = "FR-2023-24455"
            rec = session.run("MATCH (r:Regulation {primary_key: $pk}) RETURN r", pk=pk).single()
            if rec:
                anchors.append(
                    AnchorEntity(
                        slot="regulation",
                        primary_key=pk,
                        matched_text=m.group(0),
                        entity_type="Regulation",
                        label="Regulation",
                    )
                )

        # Bill: HR 3630 or H.R. 3630
        bill_pattern = re.compile(r"\b(?:hr|h\.r\.)\s*(\d+)\b", re.IGNORECASE)
        for m in bill_pattern.finditer(text):
            pk = f"BILL-117-hr-{m.group(1)}"
            rec = session.run("MATCH (b:Bill {primary_key: $pk}) RETURN b", pk=pk).single()
            if rec:
                anchors.append(
                    AnchorEntity(
                        slot="bill",
                        primary_key=pk,
                        matched_text=m.group(0),
                        entity_type="Bill",
                        label="Bill",
                    )
                )

        return anchors

    def _extract_state_anchor(self, text: str, session: Session) -> Optional[AnchorEntity]:
        """Matches state name or 2-letter postal code and validates in Neo4j."""
        lower_text = text.lower()

        # Check full state names first (sorted by length descending so "District of Columbia" matches before "Columbia")
        for state_name in sorted(self.STATE_NAME_TO_CODE.keys(), key=len, reverse=True):
            pattern = rf"\b{re.escape(state_name)}\b"
            m = re.search(pattern, lower_text)
            if m:
                code = self.STATE_NAME_TO_CODE[state_name]
                pk = f"STATE-{code}"
                # Verify in Neo4j
                record = session.run("MATCH (s:State {primary_key: $pk}) RETURN s", pk=pk).single()
                if record:
                    return AnchorEntity(
                        slot="state",
                        primary_key=pk,
                        matched_text=text[m.start():m.end()],
                        entity_type="State",
                        label="State",
                    )

        # Check 2-letter uppercase codes with boundaries
        for code in self.STATE_NAME_TO_CODE.values():
            pattern = rf"\b{code}\b"
            m = re.search(pattern, text)
            if m:
                pk = f"STATE-{code}"
                record = session.run("MATCH (s:State {primary_key: $pk}) RETURN s", pk=pk).single()
                if record:
                    return AnchorEntity(
                        slot="state",
                        primary_key=pk,
                        matched_text=m.group(0),
                        entity_type="State",
                        label="State",
                    )

        # Fail-fast check: Did the user say "from <Location>" where <Location> is unrecognized?
        geo_match = self.GEO_LOCATION_INDICATORS.search(text)
        if geo_match:
            candidate = geo_match.group(1).strip()
            # If candidate is not a common conversational word
            stopwords = {"home", "yesterday", "scratch", "pain", "now", "today", "here", "there"}
            if candidate.lower() not in stopwords and len(candidate) > 2:
                # If it's not a valid state, fail fast!
                if candidate.lower() not in self.STATE_NAME_TO_CODE:
                    raise EntityResolutionError(
                        f"Unrecognized geographic jurisdiction '{candidate}'.",
                        details={"extracted_geo": candidate}
                    )

        return None

    def _extract_diagnosis_anchor(self, text: str, session: Session) -> Optional[AnchorEntity]:
        """Matches clinical synonyms and validates against ICD10Code in Neo4j."""
        lower_text = text.lower()

        # Check if direct ICD-10 code format is provided (e.g., "I97.2", "Q82.0")
        direct_match = re.search(r"\b([A-Z]\d{2}(?:\.\d{1,2})?)\b", text)
        if direct_match:
            code_cand = direct_match.group(1).upper()
            pk = f"ICD10-{code_cand}"
            rec = session.run("MATCH (d:ICD10Code {primary_key: $pk}) RETURN d", pk=pk).single()
            if rec:
                return AnchorEntity(
                    slot="diagnosis",
                    primary_key=pk,
                    matched_text=direct_match.group(0),
                    entity_type="ICD10Code",
                    label="ICD10Code",
                )

        # Match clinical synonym patterns
        for pattern, code, pk in self.CLINICAL_SYNONYMS:
            m = pattern.search(lower_text)
            if m:
                # Validate in Neo4j
                rec = session.run("MATCH (d:ICD10Code {primary_key: $pk}) RETURN d", pk=pk).single()
                if rec:
                    return AnchorEntity(
                        slot="diagnosis",
                        primary_key=pk,
                        matched_text=text[m.start():m.end()],
                        entity_type="ICD10Code",
                        label="ICD10Code",
                    )

        # Fail-fast check for unindexed medical conditions
        unindexed_conditions = ["diabetes", "hypertension", "asthma", "broken bone", "heart disease", "fracture", "arthritis"]
        for unindexed in unindexed_conditions:
            if re.search(rf"\b{re.escape(unindexed)}\b", lower_text):
                raise EntityResolutionError(
                    f"No authorized Medicare coverage policy found for condition '{unindexed}'.",
                    details={"extracted_condition": unindexed}
                )

        return None

    def _extract_policy_anchors(self, text: str, session: Session) -> List[AnchorEntity]:
        """Matches policy domain keywords and validates against Policy in Neo4j."""
        anchors = []
        for pattern, pk in self.POLICY_TRIGGERS:
            m = pattern.search(text)
            if m:
                rec = session.run("MATCH (p:Policy {primary_key: $pk}) RETURN p", pk=pk).single()
                if rec:
                    anchors.append(
                        AnchorEntity(
                            slot="policy",
                            primary_key=pk,
                            matched_text=text[m.start():m.end()],
                            entity_type="Policy",
                            label="Policy",
                        )
                    )
        return anchors

    def _extract_hcpcs_anchors(self, text: str, session: Session) -> List[AnchorEntity]:
        """Extracts any explicitly cited HCPCS codes (e.g. A6522, Q2052)."""
        anchors = []
        for match in self.HCPCS_REGEX.finditer(text):
            code = match.group(1).upper()
            pk = f"HCPCS-{code}"
            rec = session.run("MATCH (h:HCPCSCode {primary_key: $pk}) RETURN h", pk=pk).single()
            if rec:
                anchors.append(
                    AnchorEntity(
                        slot="hcpcs",
                        primary_key=pk,
                        matched_text=match.group(0),
                        entity_type="HCPCSCode",
                        label="HCPCSCode",
                    )
                )
        return anchors
