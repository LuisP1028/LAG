"""Data models for the GraphRAG pipeline and visualization synchronization."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class AnchorEntity(BaseModel):
    """A resolved entity anchor linking user query terms to a knowledge graph entity."""
    slot: str
    primary_key: str
    matched_text: str
    entity_type: str
    label: str


class ResolvedAnchors(BaseModel):
    """Collection of resolved entity anchors across semantic slots."""
    all_anchors: List[AnchorEntity] = Field(default_factory=list)
    state_anchor: Optional[AnchorEntity] = None
    diagnosis_anchor: Optional[AnchorEntity] = None
    policy_anchor: Optional[AnchorEntity] = None
    hcpcs_anchor: Optional[AnchorEntity] = None
    jurisdiction_anchor: Optional[AnchorEntity] = None
    change_request_anchor: Optional[AnchorEntity] = None
    transmittal_anchor: Optional[AnchorEntity] = None
    coverage_policy_anchor: Optional[AnchorEntity] = None

    @property
    def primary_keys(self) -> List[str]:
        return [a.primary_key for a in self.all_anchors]


class TraversalNode(BaseModel):
    """Graph node extracted during topological subgraph expansion."""
    primary_key: str
    label: str
    name: str
    properties: Dict[str, Any] = Field(default_factory=dict)


class TraversalEdge(BaseModel):
    """Directed relationship extracted during topological subgraph expansion."""
    source_pk: str
    target_pk: str
    label: str
    edge_key: str
    provenance: Dict[str, Any] = Field(default_factory=dict)


class TraversalResult(BaseModel):
    """Result of generalized topological subgraph retrieval."""
    nodes: List[TraversalNode] = Field(default_factory=list)
    edges: List[TraversalEdge] = Field(default_factory=list)
    active_node_pks: List[str] = Field(default_factory=list)
    active_edge_keys: List[str] = Field(default_factory=list)
    retrieval_ms: float = 0.0


class GraphRAGQueryRequest(BaseModel):
    """Request payload for conversational GraphRAG synthesis."""
    query: str
    model_id: Optional[str] = "meta-llama/Meta-Llama-3-8B-Instruct"
    state_code: Optional[str] = None
    jurisdiction_code: Optional[str] = None
    primary_key: Optional[str] = None
    anchor_node_pk: Optional[str] = None


class GraphRAGQueryResponse(BaseModel):
    """Response payload containing synthesized answer and visual illumination metadata."""
    answer: str
    active_node_pks: List[str]
    active_edge_keys: List[str]
    anchors: List[AnchorEntity]
    provenance_sources: List[Dict[str, Any]]
    duration_ms: float


def resolve_label_from_pk_and_labels(pk: str, raw_labels: List[str]) -> str:
    """Resolves canonical 17-category label from Neo4j labels or primary_key prefix."""
    labels = [lbl for lbl in raw_labels if lbl != "PolicyNode"]
    if labels:
        return labels[0]
    if pk.startswith("FEE-"):
        return "FeeScheduleRate"
    if pk.startswith("HCPCS-"):
        return "ProcedureCode"
    if pk.startswith("STATE-"):
        return "State"
    if pk.startswith("ICD10-"):
        return "DiagnosisCode"
    if pk.startswith("JURIS-"):
        return "Jurisdiction"
    if pk.startswith("POLICY-"):
        return "Policy"
    if pk.startswith("BILL-"):
        return "Bill"
    if pk.startswith("PLAW-"):
        return "PublicLaw"
    if pk.startswith("STAT-"):
        return "StatutorySection"
    if pk.startswith("USC-"):
        return "USCSection"
    if pk.startswith("REG-FR-") or pk.startswith("FR-"):
        return "Regulation"
    if pk.startswith("CFR-"):
        return "CFRSection"
    if pk.startswith("TR-CR") or pk.startswith("CMS-CR-"):
        return "Transmittal"
    if pk.startswith("DME-MAC-") or pk.startswith("CMS-MCD-"):
        return "CoveragePolicy"
    if pk.startswith("LDA-"):
        return "LobbyingFiling"
    if pk.startswith("CBO-"):
        return "CBOScore"
    if pk.startswith("PUBMED-"):
        return "LiteratureStudy"
    return "PolicyNode"


def derive_node_display_name(
    label: str,
    pk_or_props: Any,
    maybe_props: Optional[Dict[str, Any]] = None,
) -> str:
    """Deterministically derives a human-readable display name from persisted node properties across all 17 entity categories."""
    if maybe_props is None and isinstance(pk_or_props, dict):
        props = pk_or_props
        pk = str(props.get("primary_key", ""))
    else:
        pk = str(pk_or_props or "")
        props = maybe_props or {}

    if label == "Policy":
        kw = props.get("keyword") or props.get("policy_keyword")
        return str(props.get("name") or (f"Policy: {kw}" if kw else pk))
    if label == "Bill":
        b_type = props.get("type") or props.get("bill_type")
        b_num = props.get("number") or props.get("bill_number")
        title = props.get("title")
        if b_type and b_num and title:
            return f"{str(b_type).upper()} {b_num}: {title}"
        return str(title or pk)
    if label == "PublicLaw":
        cong = props.get("congress")
        num = props.get("number") or props.get("public_law_number")
        if cong and num:
            num_str = str(num)
            if f"{cong}-" in num_str:
                return f"Public Law {num_str}"
            return f"Public Law {cong}-{num_str}"
        return str(props.get("title") or pk)
    if label == "StatutorySection":
        sec_num = props.get("statute_section_number") or props.get("section_number")
        heading = props.get("heading") or props.get("section_heading")
        if sec_num and heading:
            return f"Sec. {sec_num}: {heading}"
        return str(heading or pk)
    if label == "USCSection":
        return str(props.get("citation_string") or props.get("citation") or pk)
    if label == "Regulation":
        cit = props.get("citation")
        docket = props.get("docket_id")
        if cit and docket:
            return f"{cit} ({docket})"
        return str(cit or props.get("document_number") or pk)
    if label == "CFRSection":
        return str(props.get("cfr_reference") or props.get("citation") or pk)
    if label in ("Transmittal", "ChangeRequest"):
        cr = props.get("cr_number")
        tr = props.get("transmittal_number")
        if cr and tr:
            return f"{cr} ({tr})"
        return str(cr or tr or pk)
    if label == "CoveragePolicy":
        return str(props.get("title") or props.get("article_id") or pk)
    if label in ("DiagnosisCode", "ICD10Code"):
        code = props.get("code")
        desc = props.get("description")
        if code and desc:
            return f"{code}: {desc}"
        return str(code or pk)
    if label in ("ProcedureCode", "HCPCSCode"):
        code = props.get("code")
        sdesc = props.get("short_description") or props.get("long_description")
        if code and sdesc:
            return f"{code}: {sdesc}"
        return str(code or pk)
    if label in ("FeeScheduleRate", "FeeScheduleEntry"):
        hcpcs = props.get("hcpcs_code")
        st = props.get("state_code")
        fee = props.get("fee_amount")
        if hcpcs and st and fee is not None:
            r_tag = "R" if props.get("is_rural") else "NR"
            return f"{hcpcs} ({st} {r_tag}): ${float(fee):.2f}"
        return pk
    if label == "Jurisdiction":
        j_code = props.get("code") or props.get("jurisdiction_code")
        cname = props.get("contractor_name")
        if j_code and cname:
            return f"{j_code} ({cname})"
        return str(cname or pk)
    if label == "State":
        return str(props.get("state_name") or props.get("state_code") or pk)
    if label == "LobbyingFiling":
        cli = props.get("client_name")
        reg = props.get("registrant_name")
        yr = props.get("year") or props.get("filing_year")
        if cli and reg:
            return f"{cli} ({reg}, {yr})" if yr else f"{cli} ({reg})"
        return str(cli or pk)
    if label == "CBOScore":
        return str(props.get("title") or pk)
    if label == "LiteratureStudy":
        return str(props.get("title") or pk)
    return str(props.get("name") or props.get("title") or pk)

