"""
Master Graph Data Contracts and Domain Entity Models.

Defines typed Pydantic models for all 15 node types, edge provenance,
graph edges, and inter-tier handoff contracts.
"""

from __future__ import annotations
from typing import Any, List, Optional
from pydantic import BaseModel, Field, model_validator


class EdgeProvenance(BaseModel):
    """Provenance tracking contract mandated for every graph edge."""
    source_uri: str = Field(..., description="Exact file path or URL of source data")
    selector: str = Field(..., description="XPath, JSONPath, or column header selector")
    ingestion_timestamp: str = Field(..., description="ISO-8601 UTC timestamp of ingestion")
    run_id: str = Field(..., description="Unique pipeline execution identifier")

    @model_validator(mode="after")
    def validate_non_empty(self) -> EdgeProvenance:
        for field_name in ["source_uri", "selector", "ingestion_timestamp", "run_id"]:
            val = getattr(self, field_name)
            if not val or not str(val).strip():
                raise ValueError(f"EdgeProvenance field '{field_name}' must be non-empty string.")
        return self


class GraphEdge(BaseModel):
    """Directed edge connecting two nodes with mandatory provenance."""
    source_pk: str = Field(..., description="Primary key of source node")
    label: str = Field(..., description="Relationship label, e.g. TARGETS_BILL, GOVERNS")
    target_pk: str = Field(..., description="Primary key of target node")
    provenance: EdgeProvenance = Field(..., description="Auditable provenance metadata")

    @model_validator(mode="after")
    def validate_no_direct_hcpcs_to_icd10(self) -> GraphEdge:
        if self.source_pk.startswith("HCPCS-") and self.target_pk.startswith("ICD10-"):
            raise ValueError(
                f"Direct edge between HCPCSCode and ICD10Code is strictly prohibited by INV-NO-KEYWORD-BRIDGING. "
                f"Edge attempted: ({self.source_pk})-[:{self.label}]->({self.target_pk}). "
                f"Codes must be bridged via CoveragePolicy."
            )
        return self


class BaseNode(BaseModel):
    """Base model for all graph nodes enforcing primary key computation."""
    primary_key: str = Field(default="", description="Deterministic composite primary key")
    label: str = Field(default="", description="Graph node label")


class PolicyNode(BaseNode):
    """Root policy entity anchoring runtime keyword and execution metadata."""
    keyword: str
    run_id: str
    timestamp: str

    def __init__(self, **data: Any):
        super().__init__(**data)
        self.label = "Policy"
        clean_kw = self.keyword.strip().upper()
        self.primary_key = f"POLICY-{clean_kw}"


class BillNode(BaseNode):
    """Legislative vehicle introduced in Congress."""
    congress: int
    type: str
    number: int
    title: str
    introduced_date: str

    def __init__(self, **data: Any):
        super().__init__(**data)
        self.label = "Bill"
        clean_type = self.type.strip().lower()
        self.primary_key = f"BILL-{self.congress}-{clean_type}-{self.number}"


class PublicLawNode(BaseNode):
    """Enacted statute enacted by Congress."""
    congress: int
    number: int
    title: str
    enacted_date: str

    def __init__(self, **data: Any):
        super().__init__(**data)
        self.label = "PublicLaw"
        self.primary_key = f"PLAW-{self.congress}-{self.number}"


class StatutorySectionNode(BaseNode):
    """Isolated section of Public Law codified into United States Code."""
    title: int
    section: str
    subsections: List[str]
    heading: str
    text: str

    def __init__(self, **data: Any):
        super().__init__(**data)
        self.label = "StatutorySection"
        subs = "-".join(self.subsections) if self.subsections else ""
        sub_suffix = f"-{subs}" if subs else ""
        self.primary_key = f"USC-{self.title}-{self.section}{sub_suffix}"


class RegulationNode(BaseNode):
    """Administrative Final Rule published in the Federal Register."""
    citation: str
    document_number: str
    effective_date: str
    cfr_parts: List[str]

    def __init__(self, **data: Any):
        super().__init__(**data)
        self.label = "Regulation"
        self.primary_key = f"FR-{self.document_number}"


class ChangeRequestNode(BaseNode):
    """Operational directive/transmittal issued by CMS."""
    cr_number: str
    transmittal_number: str
    benefit_category: str
    effective_date: str

    def __init__(self, **data: Any):
        super().__init__(**data)
        self.label = "ChangeRequest"
        self.primary_key = f"CMS-CR-{self.cr_number}"


class CoveragePolicyNode(BaseNode):
    """Local or Joint Coverage Determination / Policy Article in CMS MCD."""
    article_id: str
    title: str
    effective_date: str
    policy_type: str

    def __init__(self, **data: Any):
        super().__init__(**data)
        self.label = "CoveragePolicy"
        art_clean = self.article_id.strip().upper()
        self.primary_key = f"CMS-MCD-{art_clean}"


class JurisdictionNode(BaseNode):
    """Regional Medicare Administrative Contractor (DME MAC) jurisdiction."""
    code: str
    contractor_name: str

    def __init__(self, **data: Any):
        super().__init__(**data)
        self.label = "Jurisdiction"
        c = self.code.strip()
        if not c.startswith("JURIS-DME-"):
            clean_code = f"JURIS-DME-{c.replace('JURIS-', '').replace('DME-', '')}"
        else:
            clean_code = c
        self.primary_key = clean_code


class StateNode(BaseNode):
    """Geographic State or Territory under Medicare jurisdiction."""
    state_code: str
    state_name: str

    def __init__(self, **data: Any):
        super().__init__(**data)
        self.label = "State"
        self.primary_key = f"STATE-{self.state_code.strip().upper()}"


class FeeScheduleEntryNode(BaseNode):
    """Discrete fee schedule rate entry for a specific HCPCS code and state."""
    hcpcs_code: str
    state_code: str
    is_rural: bool
    fee_amount: float
    ceiling: float
    floor: float
    year: int

    def __init__(self, **data: Any):
        super().__init__(**data)
        self.label = "FeeScheduleEntry"
        r_flag = "R" if self.is_rural else "NR"
        h = self.hcpcs_code.strip().upper()
        s = self.state_code.strip().upper()
        self.primary_key = f"FEE-{h}-{s}-{r_flag}-{self.year}"


class HCPCSCodeNode(BaseNode):
    """Healthcare Common Procedure Coding System procedure code."""
    code: str
    short_description: str
    category: str

    def __init__(self, **data: Any):
        super().__init__(**data)
        self.label = "HCPCSCode"
        self.primary_key = f"HCPCS-{self.code.strip().upper()}"


class ICD10CodeNode(BaseNode):
    """International Classification of Diseases, 10th Revision diagnosis code."""
    code: str
    description: str

    def __init__(self, **data: Any):
        super().__init__(**data)
        self.label = "ICD10Code"
        self.primary_key = f"ICD10-{self.code.strip().upper()}"


class LobbyingFilingNode(BaseNode):
    """Lobbying Disclosure Act (LDA) report filed with Congress."""
    filing_uuid: str
    registrant_name: str
    client_name: str
    amount: float
    year: int

    def __init__(self, **data: Any):
        super().__init__(**data)
        self.label = "LobbyingFiling"
        self.primary_key = f"LDA-{self.filing_uuid.strip()}"


class CBOScoreNode(BaseNode):
    """Congressional Budget Office formal score or cost estimate."""
    id: str
    title: str
    url: str
    published_date: str

    def __init__(self, **data: Any):
        super().__init__(**data)
        self.label = "CBOScore"
        self.primary_key = f"CBO-{self.id.strip()}"


class LiteratureStudyNode(BaseNode):
    """Peer-reviewed biomedical literature cited in regulatory justification."""
    pmid: int
    doi: str
    title: str
    journal: str
    pub_year: int

    def __init__(self, **data: Any):
        super().__init__(**data)
        self.label = "LiteratureStudy"
        self.primary_key = f"PUBMED-{self.pmid}"


# Handoff Data Contracts Between Pipeline Stages
class Tier1Handoff(BaseModel):
    target_bill_ids: List[str]
    enacted_law_id: str
    enacted_bill_id: str


class Tier2Handoff(BaseModel):
    enacted_law_id: str
    us_code_citations: str
    title: int
    section: str
    subsections: List[str]


class Tier3Handoff(BaseModel):
    us_code_citations: str
    operational_filters: dict[str, Any]
    coverage_policy_id: str
    clinical_citations: List[int]
