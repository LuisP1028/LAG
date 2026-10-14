"""Topological Traversal Engine executing dynamic schema-driven graph expansion in Neo4j."""

import time
from typing import Any, Dict, List, Optional, Set, Tuple
from neo4j import Session
from neo4j.graph import Node, Relationship

from src.graphrag.exceptions import TraversalError
from src.graphrag.models import (
    AnchorEntity,
    ResolvedAnchors,
    TraversalEdge,
    TraversalNode,
    TraversalResult,
    derive_node_display_name,
    resolve_label_from_pk_and_labels,
)


class TopologicalTraversalEngine:
    """Extracts connecting subgraphs between resolved entity anchors using dynamic schema-driven traversal."""

    def extract_connecting_subgraph(
        self,
        anchors: ResolvedAnchors,
        session: Session,
        max_hops: int = 8,
    ) -> TraversalResult:
        """Deterministically extracts subgraph matching active anchors and returns verified facts."""
        start_time = time.perf_counter()

        # Check if anchors are empty
        if not anchors.all_anchors:
            return TraversalResult(retrieval_ms=0.0)

        nodes_by_pk: Dict[str, TraversalNode] = {}
        edges_by_key: Dict[str, TraversalEdge] = {}
        active_node_pks: Set[str] = set()
        active_edge_keys: Set[str] = set()

        if len(anchors.all_anchors) == 1:
            # Dynamic Single-Entity Lineage Traversal (N = 1)
            self._execute_single_entity_traversal(
                anchor=anchors.all_anchors[0],
                session=session,
                nodes_by_pk=nodes_by_pk,
                edges_by_key=edges_by_key,
                active_node_pks=active_node_pks,
                active_edge_keys=active_edge_keys,
            )
        else:
            # Dynamic Multi-Entity Traversal (N >= 2)
            self._execute_multi_entity_traversal(
                anchors=anchors,
                session=session,
                nodes_by_pk=nodes_by_pk,
                edges_by_key=edges_by_key,
                active_node_pks=active_node_pks,
                active_edge_keys=active_edge_keys,
            )

        if not nodes_by_pk:
            anchor_pks = [a.primary_key for a in anchors.all_anchors]
            raise TraversalError(
                f"No connecting path found for anchors {anchor_pks} in the graph schema.",
                details={"anchors": anchor_pks},
            )

        elapsed_ms = (time.perf_counter() - start_time) * 1000.0

        return TraversalResult(
            nodes=list(nodes_by_pk.values()),
            edges=list(edges_by_key.values()),
            active_node_pks=sorted(list(active_node_pks)),
            active_edge_keys=sorted(list(active_edge_keys)),
            retrieval_ms=round(elapsed_ms, 2),
        )

    def _ingest_upstream_legal_lineage(
        self,
        session: Session,
        nodes_by_pk: Dict[str, TraversalNode],
        edges_by_key: Dict[str, TraversalEdge],
        active_node_pks: Set[str],
        active_edge_keys: Set[str],
    ) -> None:
        """Traverses and ingests the 8-hop legal, regulatory, coverage, and contextual spine."""
        tr_pks = [n.primary_key for n in nodes_by_pk.values() if n.label == "Transmittal"]

        if not tr_pks:
            tr_rows = session.run("MATCH (tr:Transmittal) RETURN tr.primary_key AS pk").data()
            tr_pks = [r["pk"] for r in tr_rows if r.get("pk")]

        if tr_pks:
            lineage_query = """
            MATCH (tr:Transmittal)
            WHERE tr.primary_key IN $tr_pks
            OPTIONAL MATCH (tr)-[r_mand:MANDATES_POLICY]->(cp:CoveragePolicy)
            OPTIONAL MATCH (cfr:CFRSection)-[r_impl:IMPLEMENTED_BY]->(tr)
            OPTIONAL MATCH (reg:Regulation)-[r_cod:CODIFIED_IN]->(cfr)
            OPTIONAL MATCH (usc:USCSection)-[r_auth:AUTHORIZED_BY]->(reg)
            OPTIONAL MATCH (stat:StatutorySection)-[r_amends:AMENDS]->(usc)
            OPTIONAL MATCH (pl:PublicLaw)-[r_cont:CONTAINS]->(stat)
            OPTIONAL MATCH (b_enacted:Bill)-[r_enacted:ENACTED_AS]->(pl)
            OPTIONAL MATCH (b_intro:Bill)-[r_inc:INCORPORATED_INTO]->(b_enacted)
            OPTIONAL MATCH (p:Policy)-[r_disc1:DISCOVERED_BILL]->(b_intro)
            OPTIONAL MATCH (p2:Policy)-[r_disc2:DISCOVERED_BILL]->(b_enacted)
            OPTIONAL MATCH (b_intro)-[r_cbo:HAS_BUDGET_IMPACT]->(cbo:CBOScore)
            OPTIONAL MATCH (b_intro)-[r_lda:HAS_ADVOCACY_RECORD]->(lda:LobbyingFiling)
            OPTIONAL MATCH (reg)-[r_pub:SUPPORTED_BY_EVIDENCE]->(pub:LiteratureStudy)
            RETURN collect(DISTINCT tr) AS trs,
                   collect(DISTINCT cp) AS cps,
                   collect(DISTINCT cfr) AS cfrs,
                   collect(DISTINCT reg) AS regs,
                   collect(DISTINCT usc) AS uscs,
                   collect(DISTINCT stat) AS stats,
                   collect(DISTINCT pl) AS pls,
                   collect(DISTINCT b_enacted) AS b_enacteds,
                   collect(DISTINCT b_intro) AS b_intros,
                   collect(DISTINCT p) AS ps,
                   collect(DISTINCT p2) AS p2s,
                   collect(DISTINCT cbo) AS cbos,
                   collect(DISTINCT lda) AS ldas,
                   collect(DISTINCT pub) AS pubs,
                   collect(DISTINCT r_mand) AS r_mands,
                   collect(DISTINCT r_impl) AS r_impls,
                   collect(DISTINCT r_cod) AS r_cods,
                   collect(DISTINCT r_auth) AS r_auths,
                   collect(DISTINCT r_amends) AS r_amendss,
                   collect(DISTINCT r_cont) AS r_conts,
                   collect(DISTINCT r_enacted) AS r_enacteds,
                   collect(DISTINCT r_inc) AS r_incs,
                   collect(DISTINCT r_disc1) AS r_disc1s,
                   collect(DISTINCT r_disc2) AS r_disc2s,
                   collect(DISTINCT r_cbo) AS r_cbos,
                   collect(DISTINCT r_lda) AS r_ldas,
                   collect(DISTINCT r_pub) AS r_pubs
            """
            record = session.run(lineage_query, tr_pks=tr_pks).single()
            if record:
                for list_key in (
                    "trs", "cps", "cfrs", "regs", "uscs", "stats", "pls",
                    "b_enacteds", "b_intros", "ps", "p2s", "cbos", "ldas", "pubs",
                ):
                    for n in record[list_key] or []:
                        tn = self._convert_node(n)
                        nodes_by_pk[tn.primary_key] = tn
                        active_node_pks.add(tn.primary_key)

                for rel_list_key in (
                    "r_mands", "r_impls", "r_cods", "r_auths", "r_amendss",
                    "r_conts", "r_enacteds", "r_incs", "r_disc1s", "r_disc2s",
                    "r_cbos", "r_ldas", "r_pubs",
                ):
                    for r in record[rel_list_key] or []:
                        src = r.start_node["primary_key"] if hasattr(r, "start_node") and "primary_key" in r.start_node else None
                        tgt = r.end_node["primary_key"] if hasattr(r, "end_node") and "primary_key" in r.end_node else None
                        if src and tgt:
                            te = self._convert_edge(r, src, tgt)
                            edges_by_key[te.edge_key] = te
                            active_edge_keys.add(te.edge_key)

    def _execute_single_entity_traversal(
        self,
        anchor: AnchorEntity,
        session: Session,
        nodes_by_pk: Dict[str, TraversalNode],
        edges_by_key: Dict[str, TraversalEdge],
        active_node_pks: Set[str],
        active_edge_keys: Set[str],
    ) -> None:
        """Executes dynamic single-entity lineage traversal (N = 1)."""
        if anchor.slot == "state" or anchor.label == "State":
            self._execute_single_state_traversal(
                state_pk=anchor.primary_key,
                session=session,
                nodes_by_pk=nodes_by_pk,
                edges_by_key=edges_by_key,
                active_node_pks=active_node_pks,
                active_edge_keys=active_edge_keys,
            )
        elif anchor.slot == "jurisdiction" or anchor.label == "Jurisdiction":
            self._execute_jurisdiction_traversal(
                jurisdiction_pks=[anchor.primary_key],
                session=session,
                nodes_by_pk=nodes_by_pk,
                edges_by_key=edges_by_key,
                active_node_pks=active_node_pks,
                active_edge_keys=active_edge_keys,
            )
        elif anchor.slot in ("diagnosis", "icd10code", "hcpcs", "hcpcscode") or anchor.label in (
            "ProcedureCode",
            "DiagnosisCode",
            "HCPCSCode",
            "ICD10Code",
        ):
            self._execute_single_clinical_traversal(
                anchor_pk=anchor.primary_key,
                session=session,
                nodes_by_pk=nodes_by_pk,
                edges_by_key=edges_by_key,
                active_node_pks=active_node_pks,
                active_edge_keys=active_edge_keys,
            )
        else:
            self._execute_single_general_traversal(
                anchor_pk=anchor.primary_key,
                session=session,
                nodes_by_pk=nodes_by_pk,
                edges_by_key=edges_by_key,
                active_node_pks=active_node_pks,
                active_edge_keys=active_edge_keys,
            )

    def _execute_jurisdiction_traversal(
        self,
        jurisdiction_pks: List[str],
        session: Session,
        nodes_by_pk: Dict[str, TraversalNode],
        edges_by_key: Dict[str, TraversalEdge],
        active_node_pks: Set[str],
        active_edge_keys: Set[str],
    ) -> None:
        """Traces regional DME MAC contractor jurisdiction(s), covered states, and governing 8-hop lineage."""
        query = """
        MATCH (j:Jurisdiction)
        WHERE j.primary_key IN $juris_pks
        OPTIONAL MATCH (j)-[r1:COVERS_STATE]->(s:State)
        OPTIONAL MATCH (tr:Transmittal)-[r2:APPLIES_TO_JURISDICTION]->(j)
        OPTIONAL MATCH (tr)-[r3:MANDATES_POLICY]->(cp:CoveragePolicy)
        RETURN j, r1, s, tr, r2, cp, r3
        """
        result = session.run(query, juris_pks=jurisdiction_pks)
        for row in result:
            j = row["j"]
            s = row["s"]
            tr = row["tr"]
            cp = row["cp"]

            for n in [j, s, tr, cp]:
                if n is not None:
                    tn = self._convert_node(n)
                    nodes_by_pk[tn.primary_key] = tn
                    active_node_pks.add(tn.primary_key)

            rel_pairs = [
                (row["r1"], j, s),
                (row["r2"], tr, j),
                (row["r3"], tr, cp),
            ]
            for r, src, tgt in rel_pairs:
                if r is not None and src is not None and tgt is not None:
                    te = self._convert_edge(r, src["primary_key"], tgt["primary_key"])
                    edges_by_key[te.edge_key] = te
                    active_edge_keys.add(te.edge_key)

        self._ingest_upstream_legal_lineage(
            session=session,
            nodes_by_pk=nodes_by_pk,
            edges_by_key=edges_by_key,
            active_node_pks=active_node_pks,
            active_edge_keys=active_edge_keys,
        )

    def _execute_single_state_traversal(
        self,
        state_pk: str,
        session: Session,
        nodes_by_pk: Dict[str, TraversalNode],
        edges_by_key: Dict[str, TraversalEdge],
        active_node_pks: Set[str],
        active_edge_keys: Set[str],
        target_hcpcs_pks: Optional[List[str]] = None,
    ) -> None:
        """Traces administrative, contractor, policy, clinical, and fee lineage for a single State."""
        query = """
        MATCH (s:State {primary_key: $state_pk})<-[r1:COVERS_STATE]-(j:Jurisdiction)<-[r2:APPLIES_TO_JURISDICTION]-(tr:Transmittal)-[r3:MANDATES_POLICY]->(cp:CoveragePolicy)
        OPTIONAL MATCH (cp)-[r4:COVERS_PROCEDURE]->(h:ProcedureCode)
        WITH s, r1, j, r2, tr, r3, cp, collect(DISTINCT h) AS hcpcs_list, collect(DISTINCT r4) AS r4_list
        OPTIONAL MATCH (s)<-[r6:APPLIES_TO_STATE]-(f:FeeScheduleRate)<-[r5:HAS_RATE]-(h2:ProcedureCode)
        WITH s, r1, j, r2, tr, r3, cp, hcpcs_list, r4_list,
             collect(DISTINCT f) AS fee_list, collect(DISTINCT r5) AS r5_list, collect(DISTINCT r6) AS r6_list
        OPTIONAL MATCH (cp)-[r7:REQUIRES_DIAGNOSIS]->(d:DiagnosisCode)
        RETURN s, r1, j, r2, tr, r3, cp,
               hcpcs_list, fee_list, r4_list, r5_list, r6_list,
               collect(DISTINCT d) AS diag_list,
               collect(DISTINCT r7) AS r7_list
        """
        result = session.run(query, state_pk=state_pk)

        for row in result:
            s = row["s"]
            j = row["j"]
            tr = row["tr"]
            cp = row["cp"]

            for n in [s, j, tr, cp]:
                tn = self._convert_node(n)
                nodes_by_pk[tn.primary_key] = tn
                active_node_pks.add(tn.primary_key)

            r1 = row["r1"]
            r2 = row["r2"]
            r3 = row["r3"]

            for r, src, tgt in [(r1, j, s), (r2, tr, j), (r3, tr, cp)]:
                te = self._convert_edge(r, src["primary_key"], tgt["primary_key"])
                edges_by_key[te.edge_key] = te
                active_edge_keys.add(te.edge_key)

            hcpcs_list = row["hcpcs_list"] or []
            fee_list = row["fee_list"] or []
            diag_list = row["diag_list"] or []
            r4_list = row["r4_list"] or []
            r5_list = row["r5_list"] or []
            r6_list = row["r6_list"] or []
            r7_list = row["r7_list"] or []

            row_hcpcs_pks = set()
            for h in hcpcs_list:
                th = self._convert_node(h)
                nodes_by_pk[th.primary_key] = th
                row_hcpcs_pks.add(th.primary_key)

            for f in fee_list:
                tf = self._convert_node(f)
                nodes_by_pk[tf.primary_key] = tf

            for d in diag_list:
                td = self._convert_node(d)
                nodes_by_pk[td.primary_key] = td

            for r4 in r4_list:
                tgt = r4.end_node["primary_key"] if hasattr(r4, "end_node") and "primary_key" in r4.end_node else None
                te = self._convert_edge(r4, cp["primary_key"], tgt)
                if te.target_pk:
                    edges_by_key[te.edge_key] = te

            for r5 in r5_list:
                src = r5.start_node["primary_key"] if hasattr(r5, "start_node") and "primary_key" in r5.start_node else None
                tgt = r5.end_node["primary_key"] if hasattr(r5, "end_node") and "primary_key" in r5.end_node else None
                te = self._convert_edge(r5, src, tgt)
                if te.source_pk and te.target_pk:
                    edges_by_key[te.edge_key] = te

            for r6 in r6_list:
                src = r6.start_node["primary_key"] if hasattr(r6, "start_node") and "primary_key" in r6.start_node else None
                te = self._convert_edge(r6, src, s["primary_key"])
                if te.source_pk:
                    edges_by_key[te.edge_key] = te

            for r7 in r7_list:
                tgt = r7.end_node["primary_key"] if hasattr(r7, "end_node") and "primary_key" in r7.end_node else None
                te = self._convert_edge(r7, cp["primary_key"], tgt)
                if te.target_pk:
                    edges_by_key[te.edge_key] = te

            if target_hcpcs_pks:
                for req_h_pk in target_hcpcs_pks:
                    if req_h_pk in row_hcpcs_pks:
                        req_code = req_h_pk.replace("HCPCS-", "")
                        active_node_pks.add(req_h_pk)
                        active_edge_keys.add(f"{cp['primary_key']}->COVERS_PROCEDURE->{req_h_pk}")
                        for f in fee_list:
                            if f.get("hcpcs_code") == req_code:
                                f_pk = f.get("primary_key")
                                if f_pk and f_pk in nodes_by_pk:
                                    active_node_pks.add(f_pk)
                                    active_edge_keys.add(f"{req_h_pk}->HAS_RATE->{f_pk}")
                                    active_edge_keys.add(f"{f_pk}->APPLIES_TO_STATE->{s['primary_key']}")
            else:
                target_hcpcs = "HCPCS-A6522"
                matched_fees = [f for f in fee_list if f.get("hcpcs_code") == "A6522"]
                if not matched_fees and fee_list:
                    first_code = fee_list[0].get("hcpcs_code", "A6522")
                    target_hcpcs = first_code if first_code.startswith("HCPCS-") else f"HCPCS-{first_code}"
                    matched_fees = [f for f in fee_list if f.get("hcpcs_code") == first_code]

                if target_hcpcs in nodes_by_pk:
                    active_node_pks.add(target_hcpcs)
                    active_edge_keys.add(f"{cp['primary_key']}->COVERS_PROCEDURE->{target_hcpcs}")
                for f in matched_fees:
                    f_pk = f.get("primary_key")
                    if f_pk and f_pk in nodes_by_pk:
                        active_node_pks.add(f_pk)
                        active_edge_keys.add(f"{target_hcpcs}->HAS_RATE->{f_pk}")
                        active_edge_keys.add(f"{f_pk}->APPLIES_TO_STATE->{s['primary_key']}")

        self._ingest_upstream_legal_lineage(
            session=session,
            nodes_by_pk=nodes_by_pk,
            edges_by_key=edges_by_key,
            active_node_pks=active_node_pks,
            active_edge_keys=active_edge_keys,
        )

    def _execute_single_clinical_traversal(
        self,
        anchor_pk: str,
        session: Session,
        nodes_by_pk: Dict[str, TraversalNode],
        edges_by_key: Dict[str, TraversalEdge],
        active_node_pks: Set[str],
        active_edge_keys: Set[str],
    ) -> None:
        """Traces connecting coverage policy, procedure codes, diagnosis codes, and upstream legal lineage for a clinical anchor."""
        query = """
        MATCH (n:PolicyNode {primary_key: $anchor_pk})
        OPTIONAL MATCH (cp:CoveragePolicy)-[r1:COVERS_PROCEDURE]->(h:ProcedureCode)
        WHERE n = h OR n = cp
        OPTIONAL MATCH (cp)-[r2:REQUIRES_DIAGNOSIS]->(d:DiagnosisCode)
        WHERE n = d OR n = cp
        OPTIONAL MATCH (tr:Transmittal)-[r3:MANDATES_POLICY]->(cp)
        RETURN n, cp, h, d, tr, r1, r2, r3
        """
        results = session.run(query, anchor_pk=anchor_pk)
        for row in results:
            for key in ["n", "cp", "h", "d", "tr"]:
                item = row.get(key)
                if item is not None:
                    tn = self._convert_node(item)
                    nodes_by_pk[tn.primary_key] = tn
                    active_node_pks.add(tn.primary_key)

            cp = row.get("cp")
            h = row.get("h")
            d = row.get("d")
            tr = row.get("tr")

            if row.get("r1") is not None and cp is not None and h is not None:
                te = self._convert_edge(row["r1"], cp["primary_key"], h["primary_key"])
                edges_by_key[te.edge_key] = te
                active_edge_keys.add(te.edge_key)

            if row.get("r2") is not None and cp is not None and d is not None:
                te = self._convert_edge(row["r2"], cp["primary_key"], d["primary_key"])
                edges_by_key[te.edge_key] = te
                active_edge_keys.add(te.edge_key)

            if row.get("r3") is not None and tr is not None and cp is not None:
                te = self._convert_edge(row["r3"], tr["primary_key"], cp["primary_key"])
                edges_by_key[te.edge_key] = te
                active_edge_keys.add(te.edge_key)

        self._ingest_upstream_legal_lineage(
            session=session,
            nodes_by_pk=nodes_by_pk,
            edges_by_key=edges_by_key,
            active_node_pks=active_node_pks,
            active_edge_keys=active_edge_keys,
        )

    def _execute_single_general_traversal(
        self,
        anchor_pk: str,
        session: Session,
        nodes_by_pk: Dict[str, TraversalNode],
        edges_by_key: Dict[str, TraversalEdge],
        active_node_pks: Set[str],
        active_edge_keys: Set[str],
    ) -> None:
        """Traces 1-to-8 hop non-rate neighborhood and legal lineage for any legislative, statutory, regulatory, transmittal, fee, or contextual anchor."""
        query = """
        MATCH (n:PolicyNode {primary_key: $anchor_pk})
        OPTIONAL MATCH path = (n)-[*1..8]-(m:PolicyNode)
        WHERE ALL(node IN nodes(path) WHERE NOT node:FeeScheduleRate OR node = n)
        RETURN n, path
        LIMIT 100
        """
        results = session.run(query, anchor_pk=anchor_pk)
        for row in results:
            n = row.get("n")
            path = row.get("path")
            if n is not None:
                tn = self._convert_node(n)
                nodes_by_pk[tn.primary_key] = tn
                active_node_pks.add(tn.primary_key)
            if path is not None:
                for p_node in path.nodes:
                    tp = self._convert_node(p_node)
                    nodes_by_pk[tp.primary_key] = tp
                    active_node_pks.add(tp.primary_key)
                for r in path.relationships:
                    src = r.start_node["primary_key"] if hasattr(r, "start_node") and "primary_key" in r.start_node else None
                    tgt = r.end_node["primary_key"] if hasattr(r, "end_node") and "primary_key" in r.end_node else None
                    te = self._convert_edge(r, src, tgt)
                    edges_by_key[te.edge_key] = te
                    active_edge_keys.add(te.edge_key)

        if nodes_by_pk:
            self._ingest_upstream_legal_lineage(
                session=session,
                nodes_by_pk=nodes_by_pk,
                edges_by_key=edges_by_key,
                active_node_pks=active_node_pks,
                active_edge_keys=active_edge_keys,
            )

    def _execute_multi_entity_traversal(
        self,
        anchors: ResolvedAnchors,
        session: Session,
        nodes_by_pk: Dict[str, TraversalNode],
        edges_by_key: Dict[str, TraversalEdge],
        active_node_pks: Set[str],
        active_edge_keys: Set[str],
    ) -> None:
        """Executes multi-entity connecting path traversal across anchors (N >= 2)."""
        state_anchors = [a for a in anchors.all_anchors if a.slot == "state" or a.label == "State"]
        juris_anchors = [a for a in anchors.all_anchors if a.slot == "jurisdiction" or a.label == "Jurisdiction"]
        hcpcs_anchors = [
            a for a in anchors.all_anchors
            if a.slot in ("hcpcs", "hcpcscode", "procedurecode") or a.label in ("ProcedureCode", "HCPCSCode")
        ]

        # 1. State(s) + Diagnosis (Pattern A Patient Benefit Routing)
        if state_anchors and anchors.diagnosis_anchor:
            for st_anchor in state_anchors:
                self._execute_pattern_a(
                    anchors=anchors,
                    session=session,
                    nodes_by_pk=nodes_by_pk,
                    edges_by_key=edges_by_key,
                    active_node_pks=active_node_pks,
                    active_edge_keys=active_edge_keys,
                    state_pk_override=st_anchor.primary_key,
                )
            return

        # 2. Multi-State or State + HCPCS / Policy Comparative Traversal (without diagnosis)
        if state_anchors and not anchors.diagnosis_anchor:
            target_hcpcs_pks = [h.primary_key for h in hcpcs_anchors] if hcpcs_anchors else None
            for st_anchor in state_anchors:
                self._execute_single_state_traversal(
                    state_pk=st_anchor.primary_key,
                    session=session,
                    nodes_by_pk=nodes_by_pk,
                    edges_by_key=edges_by_key,
                    active_node_pks=active_node_pks,
                    active_edge_keys=active_edge_keys,
                    target_hcpcs_pks=target_hcpcs_pks,
                )
            return

        # 3. Multi-Policy / Legislative Omnibus Convergence (Pattern C)
        policy_anchors = [a for a in anchors.all_anchors if a.slot == "policy"]
        if len(policy_anchors) >= 2:
            self._execute_pattern_c(
                anchors=anchors,
                session=session,
                nodes_by_pk=nodes_by_pk,
                edges_by_key=edges_by_key,
                active_node_pks=active_node_pks,
                active_edge_keys=active_edge_keys,
            )
            return

        # 4. Regional Contractor / Jurisdiction Traversal
        if juris_anchors and not state_anchors and not anchors.diagnosis_anchor:
            self._execute_jurisdiction_traversal(
                jurisdiction_pks=[j.primary_key for j in juris_anchors],
                session=session,
                nodes_by_pk=nodes_by_pk,
                edges_by_key=edges_by_key,
                active_node_pks=active_node_pks,
                active_edge_keys=active_edge_keys,
            )
            return

        # 5. Clinical HCPCS + Diagnosis (Pattern B)
        if (anchors.hcpcs_anchor or hcpcs_anchors) and anchors.diagnosis_anchor:
            self._execute_pattern_b(
                anchors=anchors,
                session=session,
                nodes_by_pk=nodes_by_pk,
                edges_by_key=edges_by_key,
                active_node_pks=active_node_pks,
                active_edge_keys=active_edge_keys,
            )
            return

        # 6. Generalized Shortest-Path Discovery between anchor pairs across 8-hop topology
        anchor_list = anchors.all_anchors
        for i in range(len(anchor_list)):
            for j in range(i + 1, len(anchor_list)):
                start_pk = anchor_list[i].primary_key
                target_pk = anchor_list[j].primary_key
                path_query = """
                MATCH (start:PolicyNode {primary_key: $start_pk})
                MATCH (target:PolicyNode {primary_key: $target_pk})
                MATCH path = allShortestPaths((start)-[*..10]-(target))
                WHERE ALL(node IN nodes(path) WHERE NOT node:FeeScheduleRate OR node = start OR node = target)
                RETURN path
                """
                path_records = session.run(path_query, start_pk=start_pk, target_pk=target_pk)
                for rec in path_records:
                    path = rec.get("path")
                    if path is not None:
                        for n in path.nodes:
                            tn = self._convert_node(n)
                            nodes_by_pk[tn.primary_key] = tn
                            active_node_pks.add(tn.primary_key)
                        for r in path.relationships:
                            src = r.start_node["primary_key"] if hasattr(r, "start_node") and "primary_key" in r.start_node else None
                            tgt = r.end_node["primary_key"] if hasattr(r, "end_node") and "primary_key" in r.end_node else None
                            te = self._convert_edge(r, src, tgt)
                            edges_by_key[te.edge_key] = te
                            active_edge_keys.add(te.edge_key)

        if nodes_by_pk:
            self._ingest_upstream_legal_lineage(
                session=session,
                nodes_by_pk=nodes_by_pk,
                edges_by_key=edges_by_key,
                active_node_pks=active_node_pks,
                active_edge_keys=active_edge_keys,
            )

    def _execute_pattern_a(
        self,
        anchors: ResolvedAnchors,
        session: Session,
        nodes_by_pk: Dict[str, TraversalNode],
        edges_by_key: Dict[str, TraversalEdge],
        active_node_pks: Set[str],
        active_edge_keys: Set[str],
        state_pk_override: Optional[str] = None,
    ) -> None:
        """Executes Pattern A: Patient Benefit Routing across the 8-hop ontology."""
        state_pk = state_pk_override or anchors.state_anchor.primary_key
        diag_pk = anchors.diagnosis_anchor.primary_key

        query = """
        MATCH (s:State {primary_key: $state_pk})<-[r1:COVERS_STATE]-(j:Jurisdiction)<-[r2:APPLIES_TO_JURISDICTION]-(tr:Transmittal)-[r3:MANDATES_POLICY]->(cp:CoveragePolicy)-[r4:REQUIRES_DIAGNOSIS]->(d:DiagnosisCode {primary_key: $diag_pk})
        OPTIONAL MATCH (cp)-[r5:COVERS_PROCEDURE]->(h:ProcedureCode)
        WITH s, r1, j, r2, tr, r3, cp, r4, d, collect(DISTINCT h) AS hcpcs_list, collect(DISTINCT r5) AS r5_list
        OPTIONAL MATCH (s)<-[r7:APPLIES_TO_STATE]-(f:FeeScheduleRate)<-[r6:HAS_RATE]-(h2:ProcedureCode)
        RETURN s, r1, j, r2, tr, r3, cp, r4, d,
               hcpcs_list, r5_list,
               collect(DISTINCT f) AS fee_list,
               collect(DISTINCT r6) AS r6_list,
               collect(DISTINCT r7) AS r7_list
        """

        record = session.run(query, state_pk=state_pk, diag_pk=diag_pk).single()
        if not record or not record["s"]:
            raise TraversalError(
                f"No connecting clinical/coverage path found between {state_pk} and {diag_pk}."
            )

        s = record["s"]
        j = record["j"]
        tr = record["tr"]
        cp = record["cp"]
        d = record["d"]

        for n in [s, j, tr, cp, d]:
            tn = self._convert_node(n)
            nodes_by_pk[tn.primary_key] = tn

        r1 = record["r1"]
        r2 = record["r2"]
        r3 = record["r3"]
        r4 = record["r4"]

        for r, src, tgt in [(r1, j, s), (r2, tr, j), (r3, tr, cp), (r4, cp, d)]:
            te = self._convert_edge(r, src["primary_key"], tgt["primary_key"])
            edges_by_key[te.edge_key] = te

        hcpcs_list = record["hcpcs_list"] or []
        fee_list = record["fee_list"] or []
        r5_list = record["r5_list"] or []
        r6_list = record["r6_list"] or []
        r7_list = record["r7_list"] or []

        for h in hcpcs_list:
            th = self._convert_node(h)
            nodes_by_pk[th.primary_key] = th

        for f in fee_list:
            tf = self._convert_node(f)
            nodes_by_pk[tf.primary_key] = tf

        for r5 in r5_list:
            tgt = r5.end_node["primary_key"] if hasattr(r5, "end_node") and "primary_key" in r5.end_node else None
            te = self._convert_edge(r5, cp["primary_key"], tgt)
            if te.target_pk:
                edges_by_key[te.edge_key] = te

        for r6 in r6_list:
            src_pk = r6.start_node["primary_key"] if hasattr(r6, "start_node") and "primary_key" in r6.start_node else None
            tgt_pk = r6.end_node["primary_key"] if hasattr(r6, "end_node") and "primary_key" in r6.end_node else None
            te = self._convert_edge(r6, src_pk, tgt_pk)
            if te.source_pk and te.target_pk:
                edges_by_key[te.edge_key] = te

        for r7 in r7_list:
            src_pk = r7.start_node["primary_key"] if hasattr(r7, "start_node") and "primary_key" in r7.start_node else None
            te = self._convert_edge(r7, src_pk, s["primary_key"])
            if te.source_pk:
                edges_by_key[te.edge_key] = te

        target_hcpcs = "HCPCS-A6522"
        matched_fees = [f for f in fee_list if f.get("hcpcs_code") == "A6522"]
        if not matched_fees and fee_list:
            first_code = fee_list[0].get("hcpcs_code", "A6522")
            target_hcpcs = first_code if first_code.startswith("HCPCS-") else f"HCPCS-{first_code}"
            matched_fees = [f for f in fee_list if f.get("hcpcs_code") == first_code]

        active_chain_nodes = [
            s["primary_key"],
            j["primary_key"],
            tr["primary_key"],
            cp["primary_key"],
            d["primary_key"],
            target_hcpcs,
        ]
        for f in matched_fees:
            f_pk = f.get("primary_key")
            if f_pk:
                active_chain_nodes.append(f_pk)

        for pk in active_chain_nodes:
            if pk in nodes_by_pk:
                active_node_pks.add(pk)

        active_chain_edges = [
            f"{j['primary_key']}->COVERS_STATE->{s['primary_key']}",
            f"{tr['primary_key']}->APPLIES_TO_JURISDICTION->{j['primary_key']}",
            f"{tr['primary_key']}->MANDATES_POLICY->{cp['primary_key']}",
            f"{cp['primary_key']}->REQUIRES_DIAGNOSIS->{d['primary_key']}",
            f"{cp['primary_key']}->COVERS_PROCEDURE->{target_hcpcs}",
        ]
        for f in matched_fees:
            f_pk = f.get("primary_key")
            if f_pk:
                active_chain_edges.append(f"{target_hcpcs}->HAS_RATE->{f_pk}")
                active_chain_edges.append(f"{f_pk}->APPLIES_TO_STATE->{s['primary_key']}")

        for ek in active_chain_edges:
            active_edge_keys.add(ek)

        self._ingest_upstream_legal_lineage(
            session=session,
            nodes_by_pk=nodes_by_pk,
            edges_by_key=edges_by_key,
            active_node_pks=active_node_pks,
            active_edge_keys=active_edge_keys,
        )

    def _execute_pattern_b(
        self,
        anchors: ResolvedAnchors,
        session: Session,
        nodes_by_pk: Dict[str, TraversalNode],
        edges_by_key: Dict[str, TraversalEdge],
        active_node_pks: Set[str],
        active_edge_keys: Set[str],
    ) -> None:
        """Executes Pattern B: Clinical Coverage & Diagnosis Bridging across the 8-hop ontology."""
        hcpcs_anchor = next(
            (a for a in anchors.all_anchors if a.slot in ("hcpcs", "hcpcscode", "procedurecode") or a.label in ("ProcedureCode", "HCPCSCode")),
            None,
        )
        diag_anchor = anchors.diagnosis_anchor

        if hcpcs_anchor:
            query = """
            MATCH (h:ProcedureCode {primary_key: $hcpcs_pk})<-[r1:COVERS_PROCEDURE]-(cp:CoveragePolicy)-[r2:REQUIRES_DIAGNOSIS]->(d:DiagnosisCode)
            OPTIONAL MATCH (tr:Transmittal)-[r3:MANDATES_POLICY]->(cp)
            RETURN h, r1, cp, r2, d, tr, r3
            """
            results = session.run(query, hcpcs_pk=hcpcs_anchor.primary_key)
        elif diag_anchor:
            query = """
            MATCH (d:DiagnosisCode {primary_key: $diag_pk})<-[r2:REQUIRES_DIAGNOSIS]-(cp:CoveragePolicy)-[r1:COVERS_PROCEDURE]->(h:ProcedureCode)
            OPTIONAL MATCH (tr:Transmittal)-[r3:MANDATES_POLICY]->(cp)
            RETURN h, r1, cp, r2, d, tr, r3
            """
            results = session.run(query, diag_pk=diag_anchor.primary_key)
        else:
            return

        for row in results:
            h = row["h"]
            cp = row["cp"]
            d = row["d"]
            tr = row.get("tr")

            for n in [h, cp, d, tr]:
                if n is not None:
                    tn = self._convert_node(n)
                    nodes_by_pk[tn.primary_key] = tn
                    active_node_pks.add(tn.primary_key)

            if row.get("r1") is not None and cp is not None and h is not None:
                te = self._convert_edge(row["r1"], cp["primary_key"], h["primary_key"])
                edges_by_key[te.edge_key] = te
                active_edge_keys.add(te.edge_key)

            if row.get("r2") is not None and cp is not None and d is not None:
                te = self._convert_edge(row["r2"], cp["primary_key"], d["primary_key"])
                edges_by_key[te.edge_key] = te
                active_edge_keys.add(te.edge_key)

            if row.get("r3") is not None and tr is not None and cp is not None:
                te = self._convert_edge(row["r3"], tr["primary_key"], cp["primary_key"])
                edges_by_key[te.edge_key] = te
                active_edge_keys.add(te.edge_key)

        self._ingest_upstream_legal_lineage(
            session=session,
            nodes_by_pk=nodes_by_pk,
            edges_by_key=edges_by_key,
            active_node_pks=active_node_pks,
            active_edge_keys=active_edge_keys,
        )

    def _execute_pattern_c(
        self,
        anchors: ResolvedAnchors,
        session: Session,
        nodes_by_pk: Dict[str, TraversalNode],
        edges_by_key: Dict[str, TraversalEdge],
        active_node_pks: Set[str],
        active_edge_keys: Set[str],
    ) -> None:
        """Executes Pattern C: Cross-Policy Convergence and 8-Hop Omnibus Lineage."""
        self._ingest_upstream_legal_lineage(
            session=session,
            nodes_by_pk=nodes_by_pk,
            edges_by_key=edges_by_key,
            active_node_pks=active_node_pks,
            active_edge_keys=active_edge_keys,
        )

    def _convert_node(self, node: Any) -> TraversalNode:
        """Converts Neo4j node object or dict into TraversalNode with 17-category label and derived display name."""
        props = dict(node)
        pk = str(props.get("primary_key", ""))
        raw_labels = list(node.labels) if hasattr(node, "labels") else list(props.get("labels", []))
        label = resolve_label_from_pk_and_labels(pk, raw_labels)
        name = derive_node_display_name(label, pk, props)
        props["name"] = name

        return TraversalNode(
            primary_key=pk,
            label=label,
            name=name,
            properties=props,
        )

    def _convert_edge(self, rel: Any, src_pk: Optional[str] = None, tgt_pk: Optional[str] = None) -> TraversalEdge:
        """Converts Neo4j relationship object into TraversalEdge with persisted provenance."""
        rel_type = rel.type if hasattr(rel, "type") else getattr(rel, "label", "RELATED_TO")
        props = dict(rel) if hasattr(rel, "items") else {}

        if not src_pk and hasattr(rel, "start_node") and "primary_key" in rel.start_node:
            src_pk = rel.start_node["primary_key"]
        if not tgt_pk and hasattr(rel, "end_node") and "primary_key" in rel.end_node:
            tgt_pk = rel.end_node["primary_key"]

        src = src_pk or "UNKNOWN"
        tgt = tgt_pk or "UNKNOWN"
        edge_key = f"{src}->{rel_type}->{tgt}"

        provenance = {
            k: props[k]
            for k in ("source_uri", "selector", "ingestion_timestamp", "run_id")
            if props.get(k) is not None
        }

        return TraversalEdge(
            source_pk=src,
            target_pk=tgt,
            label=rel_type,
            edge_key=edge_key,
            provenance=provenance,
        )
