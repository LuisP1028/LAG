"""FastAPI REST routes for graph topology, entity resolution, and GraphRAG operations."""

import time
from typing import Any, Dict, List, Optional, Set
from fastapi import APIRouter, Depends, HTTPException, Query, status
from neo4j import Session

from src.api.models import (
    EntityInspectionResponse,
    EntityResolveRequest,
    EntityResolveResponse,
    HealthResponse,
    SubgraphRequest,
    SubgraphResponse,
    TopologyEdge,
    TopologyNode,
    TopologyResponse,
)
from src.graph.neo4j_sync import Neo4jSyncEngine
from src.graphrag.entity_linker import EntityAnchorLinker
from src.graphrag.exceptions import (
    EntityResolutionError,
    GraphValidationError,
    ModelAuthenticationError,
    ModelInferenceError,
    ModelRateLimitError,
    TraversalError,
)
from src.graphrag.models import (
    AnchorEntity,
    GraphRAGQueryRequest,
    GraphRAGQueryResponse,
    ResolvedAnchors,
)
from src.graphrag.pipeline import GraphRAGPipeline
from src.graphrag.traversal import TopologicalTraversalEngine

router = APIRouter(prefix="/api")

_SERVER_BOOT_MONOTONIC: float = time.monotonic()

# Singleton dependencies managed during lifespan
_sync_engine: Optional[Neo4jSyncEngine] = None
_pipeline: Optional[GraphRAGPipeline] = None


def set_sync_engine(engine: Neo4jSyncEngine) -> None:
    global _sync_engine, _pipeline
    _sync_engine = engine
    _pipeline = GraphRAGPipeline()


def get_sync_engine() -> Neo4jSyncEngine:
    if _sync_engine is None:
        raise RuntimeError("Neo4jSyncEngine is not initialized.")
    return _sync_engine


def get_pipeline() -> GraphRAGPipeline:
    if _pipeline is None:
        raise RuntimeError("GraphRAGPipeline is not initialized.")
    return _pipeline


def get_neo4j_session():
    """Request-scoped Neo4j session generator dependency."""
    engine = get_sync_engine()
    with engine.get_driver().session(database=engine.database) as session:
        yield session


@router.get("/health", response_model=HealthResponse)
def health_check(session: Session = Depends(get_neo4j_session)):
    """Verifies service health, Neo4j/Embedded connectivity, loaded policy domains, and service uptime."""
    engine = get_sync_engine()
    engine.get_driver().verify_connectivity()
    policy_rows = session.run("MATCH (p:Policy) RETURN p.keyword AS kw, p.primary_key AS pk").data()
    loaded_policies: List[str] = []
    for row in policy_rows:
        kw = row.get("kw") or str(row.get("pk") or "").replace("POLICY-", "")
        if kw and str(kw) not in loaded_policies:
            loaded_policies.append(str(kw))
    if not loaded_policies:
        loaded_policies = ["LTA"]
    uptime_seconds = round(max(0.0, time.monotonic() - _SERVER_BOOT_MONOTONIC), 2)
    storage_backend = "embedded" if str(engine.uri).startswith("embedded://") else "neo4j"
    return HealthResponse(
        status="ok",
        neo4j_connected=True,
        loaded_policies=sorted(loaded_policies),
        uptime_seconds=uptime_seconds,
        storage_backend=storage_backend,
    )


@router.get("/graph/summary")
def get_graph_summary():
    """Returns aggregate summary statistics from the Neo4j knowledge graph."""
    engine = get_sync_engine()
    return engine.get_summary_statistics()


VALID_STATE_CODES: Set[str] = {
    "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "DC", "FL",
    "GA", "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME",
    "MD", "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH",
    "NJ", "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "PR",
    "RI", "SC", "SD", "TN", "TX", "UT", "VT", "VA", "VI", "WA",
    "WV", "WI", "WY", "GU",
}

VALID_JURISDICTION_CODES: Set[str] = {
    "JURIS-DME-A",
    "JURIS-DME-B",
    "JURIS-DME-C",
    "JURIS-DME-D",
}


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


@router.get("/graph/topology", response_model=TopologyResponse)
def get_graph_topology(
    policy_keyword: Optional[str] = Query(None, description="Policy filter (e.g. LTA or ALL)"),
    include_fee_schedules: bool = Query(False, description="Whether to include all 3,700+ fee schedule rate nodes"),
    jurisdiction_filter: Optional[str] = Query(None, description="CMS DME MAC Jurisdiction ID (e.g. JURIS-DME-B) to filter regional contractor and covered states"),
    state_filter: Optional[str] = Query(None, description="2-letter state/territory code (all 54 US jurisdictions including GU) to expand state-specific rates"),
    session: Session = Depends(get_neo4j_session),
):
    """Returns nodes and edges for visualization canvas with smart high-density node clustering."""
    nodes_by_pk: Dict[str, TopologyNode] = {}
    edges_by_key: Dict[str, TopologyEdge] = {}

    # Normalize and validate policy_keyword if provided
    if policy_keyword is not None:
        raw_p = policy_keyword.strip().upper()
        if raw_p and raw_p != "ALL":
            kw = raw_p.replace("POLICY-", "")
            p_rec = session.run(
                "MATCH (p:Policy) WHERE p.primary_key = $pk OR toUpper(p.keyword) = $kw RETURN p.primary_key AS pk",
                pk=f"POLICY-{kw}",
                kw=kw,
            ).single()
            if not p_rec:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={
                        "error_type": "EntityResolutionError",
                        "message": f"Unrecognized policy keyword '{policy_keyword}'.",
                        "details": {"policy_keyword": policy_keyword},
                    },
                )

    # Normalize and validate jurisdiction_filter
    clean_juris: Optional[str] = None
    if jurisdiction_filter is not None:
        raw_j = jurisdiction_filter.strip().upper()
        if raw_j and raw_j != "ALL":
            if raw_j in {"A", "B", "C", "D"}:
                clean_juris = f"JURIS-DME-{raw_j}"
            elif (raw_j.startswith("JURIS-") or raw_j.startswith("DME-")) and not raw_j.startswith("JURIS-DME-"):
                letter = raw_j.replace("JURIS-", "").replace("DME-", "")
                clean_juris = f"JURIS-DME-{letter}"
            else:
                clean_juris = raw_j

            if clean_juris not in VALID_JURISDICTION_CODES:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={
                        "error_type": "EntityResolutionError",
                        "message": f"Unrecognized DME MAC jurisdiction '{jurisdiction_filter}'.",
                        "details": {"jurisdiction_filter": jurisdiction_filter},
                    },
                )

            j_rec = session.run(
                "MATCH (j:Jurisdiction {primary_key: $juris_pk}) RETURN j.primary_key AS pk",
                juris_pk=clean_juris,
            ).single()
            if not j_rec:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={
                        "error_type": "EntityResolutionError",
                        "message": f"Unrecognized DME MAC jurisdiction '{jurisdiction_filter}'.",
                        "details": {"jurisdiction_filter": jurisdiction_filter},
                    },
                )

    # Normalize and validate state_filter across all 54 US states and territories (including GU)
    clean_state: Optional[str] = None
    parent_juris_pk: Optional[str] = None
    if state_filter is not None:
        raw_s = state_filter.strip().upper()
        if raw_s and raw_s != "ALL":
            if raw_s.startswith("STATE-"):
                raw_s = raw_s[len("STATE-"):]
            clean_state = raw_s

            if clean_state not in VALID_STATE_CODES:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={
                        "error_type": "EntityResolutionError",
                        "message": f"Unrecognized state code '{state_filter}'.",
                        "details": {"state_filter": state_filter},
                    },
                )

            s_rec = session.run(
                "MATCH (j:Jurisdiction)-[:COVERS_STATE]->(s:State {state_code: $state_code}) "
                "RETURN s.primary_key AS s_pk, j.primary_key AS j_pk",
                state_code=clean_state,
            ).single()
            if not s_rec:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={
                        "error_type": "EntityResolutionError",
                        "message": f"Unrecognized state code '{state_filter}'.",
                        "details": {"state_filter": state_filter},
                    },
                )
            parent_juris_pk = s_rec["j_pk"]

    # Determine allowed Jurisdiction and State primary keys for multi-tier topology filtering
    allowed_juris_pks: Optional[Set[str]] = None
    allowed_state_pks: Optional[Set[str]] = None
    if clean_state is not None and parent_juris_pk is not None:
        allowed_state_pks = {f"STATE-{clean_state}"}
        allowed_juris_pks = {parent_juris_pk}
    elif clean_juris is not None:
        cov_rec = session.run(
            "MATCH (:Jurisdiction {primary_key: $juris_pk})-[:COVERS_STATE]->(s:State) "
            "RETURN collect(s.primary_key) AS state_pks",
            juris_pk=clean_juris,
        ).single()
        state_pks = cov_rec["state_pks"] if cov_rec and cov_rec["state_pks"] else []
        allowed_juris_pks = {clean_juris}
        allowed_state_pks = set(state_pks)

    def convert_node(rec_node: Any) -> TopologyNode:
        props = dict(rec_node)
        pk = props.get("primary_key", "")
        raw_labels: List[str] = []
        if hasattr(rec_node, "labels"):
            raw_labels = list(rec_node.labels)
        elif "labels" in props and isinstance(props["labels"], list):
            raw_labels = list(props["labels"])

        label = resolve_label_from_pk_and_labels(pk, raw_labels)
        display_name = derive_node_display_name(label, pk, props)
        return TopologyNode(
            primary_key=pk,
            label=label,
            name=display_name,
            properties=props,
        )

    def is_node_allowed(tn: TopologyNode) -> bool:
        if tn.label == "Jurisdiction" and allowed_juris_pks is not None:
            return tn.primary_key in allowed_juris_pks
        if tn.label == "State" and allowed_state_pks is not None:
            return tn.primary_key in allowed_state_pks
        return True

    def convert_edge(rel: Any, spk: str, tpk: str) -> TopologyEdge:
        lbl = rel.type if hasattr(rel, "type") else getattr(rel, "label", "RELATED_TO")
        props = dict(rel) if hasattr(rel, "items") else {}
        edge_key = f"{spk}->{lbl}->{tpk}"
        prov = {
            "source_uri": props.get("source_uri", ""),
            "selector": props.get("selector", ""),
            "ingestion_timestamp": props.get("ingestion_timestamp", ""),
            "run_id": props.get("run_id", ""),
        }
        return TopologyEdge(
            source_pk=spk,
            target_pk=tpk,
            label=lbl,
            edge_key=edge_key,
            provenance=prov,
        )

    # 1. Fetch non-FeeScheduleRate nodes and their edges
    base_query = """
    MATCH (n:PolicyNode)
    WHERE NOT n:FeeScheduleRate AND NOT n:FeeScheduleEntry
    OPTIONAL MATCH (n)-[r]->(m:PolicyNode)
    WHERE NOT m:FeeScheduleRate AND NOT m:FeeScheduleEntry
    RETURN n, r, m
    """
    for row in session.run(base_query):
        n = row.get("n")
        tn = None
        if n:
            tn = convert_node(n)
            if is_node_allowed(tn):
                nodes_by_pk[tn.primary_key] = tn

        m = row.get("m")
        r = row.get("r")
        tm = None
        if m:
            tm = convert_node(m)
            if is_node_allowed(tm):
                nodes_by_pk[tm.primary_key] = tm
        if tn and tm and r and is_node_allowed(tn) and is_node_allowed(tm):
            te = convert_edge(r, tn.primary_key, tm.primary_key)
            edges_by_key[te.edge_key] = te

    # 2. If state_filter is specified, expand that state's FeeScheduleRate nodes and HAS_RATE / APPLIES_TO_STATE edges
    if clean_state:
        fee_query = """
        MATCH (h:ProcedureCode)-[r2:HAS_RATE]->(f:FeeScheduleRate)-[r1:APPLIES_TO_STATE]->(s:State {state_code: $state_code})
        RETURN f, r1, s, h, r2
        """
        for row in session.run(fee_query, state_code=clean_state):
            f = row.get("f")
            s = row.get("s")
            h = row.get("h")
            r1 = row.get("r1")
            r2 = row.get("r2")

            if f:
                tf = convert_node(f)
                nodes_by_pk[tf.primary_key] = tf
            if s:
                ts = convert_node(s)
                nodes_by_pk[ts.primary_key] = ts
            if h:
                th = convert_node(h)
                nodes_by_pk[th.primary_key] = th

            if f and s and r1:
                te1 = convert_edge(r1, f["primary_key"], s["primary_key"])
                edges_by_key[te1.edge_key] = te1
            if h and f and r2:
                te2 = convert_edge(r2, h["primary_key"], f["primary_key"])
                edges_by_key[te2.edge_key] = te2

    # 3. If include_fee_schedules is true and no state_filter, include all (with safety limit 4000)
    elif include_fee_schedules:
        all_fees_query = """
        MATCH (h:ProcedureCode)-[r2:HAS_RATE]->(f:FeeScheduleRate)-[r1:APPLIES_TO_STATE]->(s:State)
        WHERE ($state_pks IS NULL OR s.primary_key IN $state_pks)
        RETURN f, r1, s, h, r2
        LIMIT 4000
        """
        state_pks_param = list(allowed_state_pks) if allowed_state_pks is not None else None
        fee_rows = session.run(all_fees_query, state_pks=state_pks_param)

        for row in fee_rows:
            f = row.get("f")
            s = row.get("s")
            h = row.get("h")
            r1 = row.get("r1")
            r2 = row.get("r2")

            if f:
                tf = convert_node(f)
                nodes_by_pk[tf.primary_key] = tf
            if f and s and r1:
                te1 = convert_edge(r1, f["primary_key"], s["primary_key"])
                edges_by_key[te1.edge_key] = te1
            if h and f and r2:
                te2 = convert_edge(r2, h["primary_key"], f["primary_key"])
                edges_by_key[te2.edge_key] = te2

    node_list = list(nodes_by_pk.values())
    edge_list = list(edges_by_key.values())

    return TopologyResponse(
        nodes=node_list,
        edges=edge_list,
        total_nodes=len(node_list),
        total_edges=len(edge_list),
    )


@router.post("/entities/resolve", response_model=EntityResolveResponse)
def resolve_entities(
    req: EntityResolveRequest,
    session: Session = Depends(get_neo4j_session),
):
    """Resolves natural language text into verified knowledge graph anchors."""
    pipeline = get_pipeline()
    try:
        resolved = pipeline.linker.resolve_anchors(req.query, session)
        return EntityResolveResponse(anchors=resolved.all_anchors)
    except EntityResolutionError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error_type": "EntityResolutionError", "message": exc.message, "details": exc.details},
        )


@router.get("/entities/{primary_key:path}", response_model=EntityInspectionResponse)
def inspect_entity(
    primary_key: str,
    session: Session = Depends(get_neo4j_session),
) -> EntityInspectionResponse:
    """Returns deep contextual provenance, citations, text excerpts, and incident relationships for a single entity."""
    clean_pk = primary_key.strip()
    if not clean_pk:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error_type": "EntityResolutionError",
                "message": "Entity primary_key must not be empty.",
                "details": {"primary_key": primary_key},
            },
        )

    rec = session.run(
        "MATCH (n:PolicyNode) WHERE n.primary_key = $pk OR toUpper(n.primary_key) = toUpper($pk) RETURN n, labels(n) AS lbls",
        pk=clean_pk,
    ).single()
    if not rec:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error_type": "EntityResolutionError",
                "message": f"Entity '{clean_pk}' not found in knowledge graph.",
                "details": {"primary_key": clean_pk},
            },
        )

    node_obj = rec["n"]
    props = dict(node_obj)
    actual_pk = str(props.get("primary_key", clean_pk))
    raw_labels = list(rec["lbls"] or [])
    label = resolve_label_from_pk_and_labels(actual_pk, raw_labels)
    name = derive_node_display_name(label, actual_pk, props)

    text_excerpt = ""
    for candidate_key in (
        "text",
        "text_excerpt",
        "long_description",
        "description",
        "short_description",
        "heading",
        "title",
    ):
        val = props.get(candidate_key)
        if val and str(val).strip():
            text_excerpt = str(val).strip()
            break
    if not text_excerpt:
        text_excerpt = name

    citations: List[str] = []
    for cit_key in (
        "citation_string",
        "citation",
        "cfr_reference",
        "uslm_section_path",
        "public_law_id",
        "docket_id",
        "rin",
        "cr_number",
        "transmittal_number",
        "article_id",
    ):
        cval = props.get(cit_key)
        if cval and str(cval).strip() and str(cval).strip() not in citations:
            citations.append(str(cval).strip())

    for list_key in ("cfr_parts", "clinical_prerequisites", "superseded_transmittal_numbers"):
        lval = props.get(list_key)
        if isinstance(lval, list):
            for item in lval:
                if item and str(item).strip() and str(item).strip() not in citations:
                    citations.append(str(item).strip())

    rel_rows = session.run(
        """
        MATCH (src:PolicyNode)-[r]->(tgt:PolicyNode)
        WHERE src.primary_key = $pk OR tgt.primary_key = $pk
        RETURN src.primary_key AS spk, tgt.primary_key AS tpk, r
        LIMIT 250
        """,
        pk=actual_pk,
    )

    relationships: List[TopologyEdge] = []
    provenance_list: List[Dict[str, Any]] = []
    seen_prov_keys: Set[Tuple[str, str, str, str]] = set()

    for row in rel_rows:
        spk = str(row.get("spk") or "")
        tpk = str(row.get("tpk") or "")
        rel = row.get("r")
        if not spk or not tpk or rel is None:
            continue
        rel_type = rel.type if hasattr(rel, "type") else getattr(rel, "label", "RELATED_TO")
        rel_props = dict(rel) if hasattr(rel, "items") else {}
        edge_key = f"{spk}->{rel_type}->{tpk}"
        prov = {
            "source_uri": str(rel_props.get("source_uri", "")),
            "selector": str(rel_props.get("selector", "")),
            "ingestion_timestamp": str(rel_props.get("ingestion_timestamp", "")),
            "run_id": str(rel_props.get("run_id", "")),
        }
        relationships.append(
            TopologyEdge(
                source_pk=spk,
                target_pk=tpk,
                label=rel_type,
                edge_key=edge_key,
                provenance=prov,
            )
        )
        pkey = (prov["source_uri"], prov["selector"], prov["run_id"], prov["ingestion_timestamp"])
        if any(pkey) and pkey not in seen_prov_keys:
            seen_prov_keys.add(pkey)
            provenance_list.append(prov)

    if not provenance_list and (props.get("source_uri") or props.get("run_id") or props.get("timestamp")):
        provenance_list.append({
            "source_uri": str(props.get("source_uri") or props.get("url") or "exports/lta_knowledge_graph.json"),
            "selector": str(props.get("selector") or f"$.nodes[?(@.primary_key=='{actual_pk}')]"),
            "ingestion_timestamp": str(props.get("ingestion_timestamp") or props.get("timestamp") or ""),
            "run_id": str(props.get("run_id") or ""),
        })

    return EntityInspectionResponse(
        primary_key=actual_pk,
        label=label,
        name=name,
        properties=props,
        text_excerpt=text_excerpt,
        citations=citations,
        provenance=provenance_list,
        relationships=relationships,
    )


@router.post("/graphrag/subgraph", response_model=SubgraphResponse)
def get_subgraph_by_anchors(
    req: SubgraphRequest,
    session: Session = Depends(get_neo4j_session),
):
    """Extracts connecting subgraph between given primary key anchors across all 17 node types."""
    pipeline = get_pipeline()
    if not req.anchors:
        return SubgraphResponse(nodes=[], edges=[], active_node_pks=[], active_edge_keys=[], retrieval_ms=0.0)

    anchors_list: List[AnchorEntity] = []
    state_anchor = None
    diag_anchor = None
    policy_anchor = None
    hcpcs_anchor = None
    jurisdiction_anchor = None
    change_request_anchor = None
    coverage_policy_anchor = None

    for pk in req.anchors:
        rec = session.run("MATCH (n:PolicyNode {primary_key: $pk}) RETURN n, labels(n) as lbls", pk=pk).single()
        if not rec:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error_type": "EntityResolutionError",
                    "message": f"Unresolved primary key '{pk}' not found in knowledge graph.",
                    "details": {"unresolved_token": pk},
                },
            )
        node = rec["n"]
        props = dict(node)
        label = resolve_label_from_pk_and_labels(pk, list(rec["lbls"]))

        slot = label.lower()
        if label == "State":
            slot = "state"
        elif label in ("DiagnosisCode", "ICD10Code"):
            slot = "diagnosis"
        elif label == "Policy":
            slot = "policy"
        elif label in ("ProcedureCode", "HCPCSCode"):
            slot = "hcpcs"
        elif label == "Jurisdiction":
            slot = "jurisdiction"
        elif label in ("Transmittal", "ChangeRequest"):
            slot = "changerequest"
        elif label == "CoveragePolicy":
            slot = "coveragepolicy"

        matched = derive_node_display_name(label, pk, props)
        anchor = AnchorEntity(
            slot=slot,
            primary_key=pk,
            matched_text=str(matched),
            entity_type=label,
            label=label,
        )
        anchors_list.append(anchor)
        if slot == "state" and not state_anchor:
            state_anchor = anchor
        elif slot in ("diagnosis", "icd10code") and not diag_anchor:
            diag_anchor = anchor
        elif slot == "policy" and not policy_anchor:
            policy_anchor = anchor
        elif slot in ("hcpcs", "hcpcscode") and not hcpcs_anchor:
            hcpcs_anchor = anchor
        elif slot == "jurisdiction" and not jurisdiction_anchor:
            jurisdiction_anchor = anchor
        elif slot in ("changerequest", "change_request", "transmittal") and not change_request_anchor:
            change_request_anchor = anchor
        elif slot in ("coveragepolicy", "coverage_policy") and not coverage_policy_anchor:
            coverage_policy_anchor = anchor

    resolved = ResolvedAnchors(
        all_anchors=anchors_list,
        state_anchor=state_anchor,
        diagnosis_anchor=diag_anchor,
        policy_anchor=policy_anchor,
        hcpcs_anchor=hcpcs_anchor,
        jurisdiction_anchor=jurisdiction_anchor,
        change_request_anchor=change_request_anchor,
        transmittal_anchor=change_request_anchor,
        coverage_policy_anchor=coverage_policy_anchor,
    )

    try:
        traversal = pipeline.traverser.extract_connecting_subgraph(resolved, session)
        t_nodes = [
            TopologyNode(primary_key=n.primary_key, label=n.label, name=n.name, properties=n.properties)
            for n in traversal.nodes
        ]
        t_edges = [
            TopologyEdge(source_pk=e.source_pk, target_pk=e.target_pk, label=e.label, edge_key=e.edge_key, provenance=e.provenance)
            for e in traversal.edges
        ]
        return SubgraphResponse(
            nodes=t_nodes,
            edges=t_edges,
            active_node_pks=traversal.active_node_pks,
            active_edge_keys=traversal.active_edge_keys,
            retrieval_ms=traversal.retrieval_ms,
        )
    except TraversalError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error_type": "TraversalError", "message": exc.message, "details": exc.details},
        )


extract_subgraph = get_subgraph_by_anchors


@router.post("/graphrag/query", response_model=GraphRAGQueryResponse)
def execute_graphrag_query(
    req: GraphRAGQueryRequest,
    session: Session = Depends(get_neo4j_session),
):
    """Executes end-to-end GraphRAG answering and synchronized canvas telemetry."""
    pipeline = get_pipeline()
    try:
        response = pipeline.execute_query(req, session)
        return response
    except EntityResolutionError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error_type": "EntityResolutionError", "message": exc.message, "details": exc.details},
        )
    except ModelAuthenticationError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error_type": "ModelAuthenticationError", "message": exc.message, "details": exc.details},
        )
    except ModelRateLimitError as exc:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={"error_type": "ModelRateLimitError", "message": exc.message, "details": exc.details},
        )
    except ModelInferenceError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail={"error_type": "ModelInferenceError", "message": exc.message, "details": exc.details},
        )
    except GraphValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error_type": "GraphValidationError", "message": exc.message, "details": exc.details},
        )
