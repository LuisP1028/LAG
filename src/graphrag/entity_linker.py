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

    def resolve_anchors(self, query_text: str, session: Session) -> ResolvedAnchors:
        """Deterministically extracts state, diagnosis, and policy anchors, validating against Neo4j."""
        clean_text = query_text.strip()
        all_anchors: List[AnchorEntity] = []

        # 1. Slot 1: Geographic State Anchor
        state_anchor = self._extract_state_anchor(clean_text, session)
        if state_anchor:
            all_anchors.append(state_anchor)

        # 2. Slot 2: Clinical Indication Anchor
        diag_anchor = self._extract_diagnosis_anchor(clean_text, session)
        if diag_anchor:
            all_anchors.append(diag_anchor)

        # 3. Slot 3: Policy Domain Anchor(s)
        policy_anchors = self._extract_policy_anchors(clean_text, session)
        all_anchors.extend(policy_anchors)
        primary_policy_anchor = policy_anchors[0] if policy_anchors else None

        # 4. Procedure code anchors (HCPCS) if explicitly cited
        hcpcs_anchors = self._extract_hcpcs_anchors(clean_text, session)
        all_anchors.extend(hcpcs_anchors)

        # Build ResolvedAnchors
        result = ResolvedAnchors(
            state_anchor=state_anchor,
            diagnosis_anchor=diag_anchor,
            policy_anchor=primary_policy_anchor,
            all_anchors=all_anchors,
        )

        return result

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
