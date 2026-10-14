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
    """Isolated section of Public Law enacted by Congress."""
    title: int = 42
    section: str = ""
    subsections: List[str] = Field(default_factory=list)
    heading: str = ""
    text: str = ""
    public_law_id: str = ""
    uslm_section_path: str = ""
    statute_section_number: str = ""
    effective_date: str = ""

    def __init__(self, **data: Any):
        super().__init__(**data)
        self.label = "StatutorySection"
        if not self.primary_key:
            if self.public_law_id and self.statute_section_number:
                pl_clean = self.public_law_id.replace("PLAW-", "").strip()
                self.primary_key = f"STAT-{pl_clean}-SEC-{self.statute_section_number.strip()}"
            else:
                subs = "-".join(self.subsections) if self.subsections else ""
                sub_suffix = f"-{subs}" if subs else ""
                self.primary_key = f"USC-{self.title}-{self.section}{sub_suffix}"


class USCSectionNode(BaseNode):
    """Codified United States Code section amended by a Public Law section."""
    title: int
    section: str
    subsections: List[str] = Field(default_factory=list)
    citation_string: str

    def __init__(self, **data: Any):
        super().__init__(**data)
        self.label = "USCSection"
        if not self.primary_key:
            subs = "-".join(self.subsections) if self.subsections else ""
            sub_suffix = f"-{subs}" if subs else ""
            self.primary_key = f"USC-{self.title}-{self.section}{sub_suffix}"


class RegulationNode(BaseNode):
    """Administrative Final Rule published in the Federal Register."""
    citation: str
    document_number: str
    effective_date: str
    cfr_parts: List[str]
    docket_id: str = ""
    rin: str = ""

    def __init__(self, **data: Any):
        super().__init__(**data)
        self.label = "Regulation"
        if not self.primary_key:
            self.primary_key = f"REG-FR-{self.document_number}"


class CFRSectionNode(BaseNode):
    """Code of Federal Regulations part or section codified by a Final Rule."""
    cfr_reference: str
    title: int = 42
    part: str = ""

    def __init__(self, **data: Any):
        super().__init__(**data)
        self.label = "CFRSection"
        if not self.primary_key:
            clean_ref = (
                self.cfr_reference.strip()
                .upper()
                .replace("CFR PART", "")
                .replace("CFR", "")
                .replace(".", "-")
            )
            tokens = [t for t in clean_ref.split() if t]
            self.primary_key = f"CFR-{'-'.join(tokens)}"


class ChangeRequestNode(BaseNode):
    """Operational directive/transmittal issued by CMS."""
    cr_number: str
    transmittal_number: str
    benefit_category: str
    effective_date: str
    superseded_transmittal_numbers: List[str] = Field(default_factory=list)
    cms_manual_publication: str = ""
    pricing_indicator_code: str = ""
    betos_code: str = ""

    def __init__(self, **data: Any):
        super().__init__(**data)
        if not self.label:
            self.label = "Transmittal"
        if not self.primary_key:
            clean_cr = self.cr_number.replace("CR", "").strip()
            self.primary_key = f"TR-CR{clean_cr}"


class TransmittalNode(ChangeRequestNode):
    """Operational Claims Directive (Change Request & Transmittal) node."""
    pass


class CoveragePolicyNode(BaseNode):
    """Clinical coverage guidance from CMS MCD or Joint DME MAC Publication."""
    article_id: str
    title: str
    effective_date: str = ""
    policy_type: str = ""
    publisher_type: str = ""
    clinical_prerequisites: List[str] = Field(default_factory=list)

    def __init__(self, **data: Any):
        super().__init__(**data)
        self.label = "CoveragePolicy"
        if not self.primary_key:
            art_clean = self.article_id.strip().upper()
            if art_clean.startswith(("DME-MAC-", "CMS-MCD-")):
                self.primary_key = art_clean
            else:
                self.primary_key = f"CMS-MCD-{art_clean}"


class JurisdictionNode(BaseNode):
    """Regional Medicare Administrative Contractor (DME MAC) jurisdiction."""
    code: str
    contractor_name: str

    def __init__(self, **data: Any):
        super().__init__(**data)
        self.label = "Jurisdiction"
        if not self.primary_key:
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
        if not self.primary_key:
            self.primary_key = f"STATE-{self.state_code.strip().upper()}"


class FeeScheduleEntryNode(BaseNode):
    """Discrete fee schedule rate entry for a specific HCPCS code and state."""
    hcpcs_code: str
    state_code: str
    is_rural: bool
    fee_amount: Optional[float] = None
    ceiling: float = 0.0
    floor: float = 0.0
    year: int = 2024
    pricing_methodology: str = "NATIONAL_FEE_SCHEDULE"

    def __init__(self, **data: Any):
        super().__init__(**data)
        if not self.label:
            self.label = "FeeScheduleRate"
        if not self.primary_key:
            r_flag = "R" if self.is_rural else "NR"
            h = self.hcpcs_code.strip().upper()
            s = self.state_code.strip().upper()
            self.primary_key = f"FEE-{h}-{s}-{r_flag}-{self.year}"


class FeeScheduleRateNode(FeeScheduleEntryNode):
    """Geographic reimbursement rate node."""
    pass


class HCPCSCodeNode(BaseNode):
    """Healthcare Common Procedure Coding System procedure code."""
    code: str
    short_description: str
    long_description: str = ""
    category: str = ""
    betos_code: str = ""
    pricing_indicator: str = ""
    pricing_methodology: str = "NATIONAL_FEE_SCHEDULE"
    is_custom_or_nos: bool = False

    def __init__(self, **data: Any):
        super().__init__(**data)
        if not self.label:
            self.label = "ProcedureCode"
        if not self.primary_key:
            self.primary_key = f"HCPCS-{self.code.strip().upper()}"


class ProcedureCodeNode(HCPCSCodeNode):
    """Standardized medical procedure code node."""
    pass


class ICD10CodeNode(BaseNode):
    """International Classification of Diseases, 10th Revision diagnosis code."""
    code: str
    description: str

    def __init__(self, **data: Any):
        super().__init__(**data)
        if not self.label:
            self.label = "DiagnosisCode"
        if not self.primary_key:
            self.primary_key = f"ICD10-{self.code.strip().upper()}"


class DiagnosisCodeNode(ICD10CodeNode):
    """Qualifying ICD-10-CM diagnosis code node."""
    pass


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


# ============================================================================
# Strict Fail-Fast Exception Hierarchy (functional_specification_014.md §4)
# ============================================================================

class PolicyTraversalError(Exception):
    """Base exception for all fail-fast policy traversal errors."""
    pass


class LegislativeResolutionError(PolicyTraversalError):
    """Hop 0 failure: 0 search hits, authentication failure, or no candidate bill."""
    pass


class EnactedLawNotFoundError(PolicyTraversalError):
    """Hop 1 failure: un-enacted bill with no omnibus link to a Public Law."""
    pass


class StatutorySectionNotFoundError(PolicyTraversalError):
    """Hop 2 failure: USLM XML missing, unparseable, no matching section, or 0 USC citations."""
    pass


class RegulatoryRuleResolutionError(PolicyTraversalError):
    """Hop 3 failure: 0 matching CMS Final Rules or missing mandatory metadata."""
    pass


class OperationalDirectiveMissingError(PolicyTraversalError):
    """Hop 4 failure: CR or active Transmittal missing, or operational filter codes unextractable."""
    pass


class ClinicalCoverageMissingError(PolicyTraversalError):
    """Hop 5 failure: no coverage guidance or qualifying diagnosis codes resolved."""
    pass


class CodingTableMismatchError(PolicyTraversalError):
    """Hop 6 failure: 0 HCPCS codes match operational filters or invalid HCPCS syntax."""
    pass


class FeeScheduleIngestionError(PolicyTraversalError):
    """Hop 7 failure: unpivoting failure across 54 jurisdictions or unmapped codes."""
    pass


# ============================================================================
# Typed Handoff Data Contracts Between Pipeline Stages (§2 Hops 0–7)
# ============================================================================

class LegislativeHandoff(BaseModel):
    """Hop 1 output contract handing off legislative enactment lineage to Hop 2."""
    policy_keyword: str
    introduced_bill_id: str
    enacting_bill_id: str
    public_law_id: str
    congress: int
    enacted_date: str


class StatutoryHandoff(BaseModel):
    """Hop 2 output contract handing off codified statutory authority to Hop 3."""
    public_law_id: str
    uslm_section_path: str
    statute_section_number: str
    statute_heading: str
    amended_usc_citations: List[str]
    effective_date: str


class RegulatoryHandoff(BaseModel):
    """Hop 3 output contract handing off Final Rule metadata to Hop 4."""
    fr_document_number: str
    fr_citation: str
    docket_id: str
    rin: str
    cfr_references: List[str]
    effective_date: str


class OperationalHandoff(BaseModel):
    """Hop 4 output contract handing off CR/Transmittal and operational filters to Hops 5 & 6."""
    change_request_number: str
    active_transmittal_number: str
    superseded_transmittal_numbers: List[str]
    cms_manual_publication: str
    benefit_category_code: str
    pricing_indicator_code: str
    betos_code: str
    effective_date: str


class CoverageHandoff(BaseModel):
    """Hop 5 output contract handing off clinical coverage guidance and ICD-10 codes."""
    coverage_guidance_id: str
    publisher_type: str
    publication_title: str
    qualifying_icd10_codes: List[str]
    clinical_prerequisites: List[str]


class CodingHandoff(BaseModel):
    """Hop 6 output contract handing off operational-filtered HCPCS codes to Hop 7."""
    benefit_category_code: str
    betos_code: str
    hcpcs_codes: List[str]
    code_descriptions: dict[str, str]
    code_pricing_indicators: dict[str, str]
    pricing_methodologies: dict[str, str]


class FeeScheduleRecord(BaseModel):
    """Single geographic fee schedule entry for an HCPCS code, jurisdiction, and rurality."""
    hcpcs_code: str
    jurisdiction_postal_code: str
    rural_designation: str
    rate_usd: Optional[float] = None
    pricing_methodology: str


class ReimbursementHandoff(BaseModel):
    """Hop 7 output contract containing the complete 54-jurisdiction fee schedule matrix."""
    fee_schedule_release: str
    jurisdiction_count: int
    records: List[FeeScheduleRecord]
    unpriced_custom_codes: List[str]


# Legacy aliases for backward compatibility
Tier1Handoff = LegislativeHandoff
Tier2Handoff = StatutoryHandoff
Tier3Handoff = OperationalHandoff

