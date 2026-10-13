"""FastAPI REST routes for graph topology, entity resolution, and GraphRAG operations."""

import time
from typing import Any, Dict, List, Optional, Set
from fastapi import APIRouter, Depends, HTTPException, Query, status
from neo4j import Session

from src.api.models import (
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
    """Verifies service health and Neo4j connectivity."""
    engine = get_sync_engine()
    engine.get_driver().verify_connectivity()
    return HealthResponse()


@router.get("/graph/summary")
def get_graph_summary():
    """Returns aggregate summary statistics from the Neo4j knowledge graph."""
    engine = get_sync_engine()
    return engine.get_summary_statistics()


@router.get("/graph/topology", response_model=TopologyResponse)
def get_graph_topology(
    policy_keyword: Optional[str] = Query("LTA", description="Policy filter (LTA, IVIG, or all)"),
    include_fee_schedules: bool = Query(False, description="Whether to include all 3,800+ fee schedule nodes"),
    state_filter: Optional[str] = Query(None, description="2-letter state code (e.g. WI) to expand state-specific fees"),
    session: Session = Depends(get_neo4j_session),
):
    """Returns nodes and edges for visualization canvas with smart high-density node clustering."""
    nodes_by_pk: Dict[str, TopologyNode] = {}
    edges_by_key: Dict[str, TopologyEdge] = {}

    def convert_node(rec_node: Any) -> TopologyNode:
        props = dict(rec_node)
        pk = props.get("primary_key", "")
        labels = []
        if hasattr(rec_node, "labels"):
            labels = [lbl for lbl in rec_node.labels if lbl != "PolicyNode"]
        elif "labels" in props:
            labels = [lbl for lbl in props["labels"] if lbl != "PolicyNode"]

        if labels:
            label = labels[0]
        elif pk.startswith("FEE-"):
            label = "FeeScheduleEntry"
        elif pk.startswith("HCPCS-"):
            label = "HCPCSCode"
        elif pk.startswith("STATE-"):
            label = "State"
        elif pk.startswith("ICD10-"):
            label = "ICD10Code"
        elif pk.startswith("JURIS-"):
            label = "Jurisdiction"
        elif pk.startswith("POLICY-"):
            label = "Policy"
        elif pk.startswith("BILL-"):
            label = "Bill"
        elif pk.startswith("PLAW-"):
            label = "PublicLaw"
        elif pk.startswith("USC-"):
            label = "StatutorySection"
        elif pk.startswith("FR-"):
            label = "Regulation"
        elif pk.startswith("CMS-CR-"):
            label = "ChangeRequest"
        elif pk.startswith("CMS-MCD-"):
            label = "CoveragePolicy"
        elif pk.startswith("LDA-"):
            label = "LobbyingFiling"
        elif pk.startswith("PUBMED-"):
            label = "LiteratureStudy"
        else:
            label = "PolicyNode"

        raw_name = props.get("name") or props.get("state_name") or props.get("section") or props.get("title") or pk
        return TopologyNode(
            primary_key=pk,
            label=label,
            name=str(raw_name),
            properties=props,
        )

    def convert_edge(rel: Any, spk: str, tpk: str) -> TopologyEdge:
        lbl = rel.type if hasattr(rel, "type") else getattr(rel, "label", "RELATED_TO")
        props = dict(rel) if hasattr(rel, "items") else {}
        edge_key = f"{spk}->{lbl}->{tpk}"
        prov = {
            "source_uri": props.get("source_uri", "verified://cms-policy"),
            "selector": props.get("selector", "direct"),
            "ingestion_timestamp": props.get("ingestion_timestamp", "2026-10-13T01:23:54Z"),
            "run_id": props.get("run_id", "export-run-001"),
        }
        return TopologyEdge(
            source_pk=spk,
            target_pk=tpk,
            label=lbl,
            edge_key=edge_key,
            provenance=prov,
        )

    # 1. Fetch non-FeeScheduleEntry nodes and their edges
    base_query = """
    MATCH (n:PolicyNode)
    WHERE NOT n:FeeScheduleEntry
    OPTIONAL MATCH (n)-[r]->(m:PolicyNode)
    WHERE NOT m:FeeScheduleEntry
    RETURN n, r, m
    """
    for row in session.run(base_query):
        n = row.get("n")
        if n:
            tn = convert_node(n)
            nodes_by_pk[tn.primary_key] = tn

        m = row.get("m")
        r = row.get("r")
        if m:
            tm = convert_node(m)
            nodes_by_pk[tm.primary_key] = tm
        if n and m and r:
            te = convert_edge(r, n["primary_key"], m["primary_key"])
            edges_by_key[te.edge_key] = te

    # 2. If state_filter is specified, expand that state's fee schedule nodes (~70 nodes)
    if state_filter:
        clean_state = state_filter.strip().upper()
        fee_query = """
        MATCH (f:FeeScheduleEntry)-[r1:APPLIES_TO]->(s:State {state_code: $state_code})
        MATCH (h:HCPCSCode)-[r2:HAS_FEE_SCHEDULE]->(f)
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
        MATCH (h:HCPCSCode)-[r2:HAS_FEE_SCHEDULE]->(f:FeeScheduleEntry)-[r1:APPLIES_TO]->(s:State)
        RETURN f, r1, s, h, r2
        LIMIT 4000
        """
        for row in session.run(all_fees_query):
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


@router.post("/graphrag/subgraph", response_model=SubgraphResponse)
def get_subgraph_by_anchors(
    req: SubgraphRequest,
    session: Session = Depends(get_neo4j_session),
):
    """Extracts connecting subgraph between given primary key anchors across all 14 node types."""
    pipeline = get_pipeline()
    if not req.anchors:
        return SubgraphResponse(nodes=[], edges=[], active_node_pks=[], active_edge_keys=[], retrieval_ms=0.0)

    # Reconstruct ResolvedAnchors from PK list across all 14 node types
    anchors_list: List[AnchorEntity] = []
    state_anchor = None
    diag_anchor = None
    policy_anchor = None
    hcpcs_anchor = None
    jurisdiction_anchor = None
    change_request_anchor = None
    coverage_policy_anchor = None

    for pk in req.anchors:
        # Check node in Neo4j across all 14 node types
        rec = session.run("MATCH (n:PolicyNode {primary_key: $pk}) RETURN n, labels(n) as lbls", pk=pk).single()
        if not rec:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"error_type": "EntityNotFoundError", "message": f"Entity '{pk}' not found in database."},
            )
        node = rec["n"]
        lbls = [l for l in rec["lbls"] if l != "PolicyNode"]
        label = lbls[0] if lbls else "Node"

        slot = label.lower()
        if label == "State":
            slot = "state"
        elif label == "ICD10Code":
            slot = "diagnosis"
        elif label == "Policy":
            slot = "policy"
        elif label == "HCPCSCode":
            slot = "hcpcs"
        elif label == "Jurisdiction":
            slot = "jurisdiction"
        elif label == "ChangeRequest":
            slot = "changerequest"
        elif label == "CoveragePolicy":
            slot = "coveragepolicy"

        matched = node.get("name") or node.get("title") or pk
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
        elif slot in ("changerequest", "change_request") and not change_request_anchor:
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
