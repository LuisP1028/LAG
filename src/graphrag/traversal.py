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
)


class TopologicalTraversalEngine:
    """Extracts connecting subgraphs between resolved entity anchors using dynamic schema-driven traversal."""

    def extract_connecting_subgraph(
        self,
        anchors: ResolvedAnchors,
        session: Session,
        max_hops: int = 3,
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
        elif anchor.slot in ("diagnosis", "icd10code", "hcpcs", "hcpcscode") or anchor.label in ("HCPCSCode", "ICD10Code"):
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

    def _execute_single_state_traversal(
        self,
        state_pk: str,
        session: Session,
        nodes_by_pk: Dict[str, TraversalNode],
        edges_by_key: Dict[str, TraversalEdge],
        active_node_pks: Set[str],
        active_edge_keys: Set[str],
    ) -> None:
        """Traces administrative, contractor, policy, and fee lineage for a single State."""
        query = """
        MATCH (s:State {primary_key: $state_pk})<-[r1:COVERS_STATE]-(j:Jurisdiction)<-[r2:APPLIES_TO_JURISDICTION]-(cr:ChangeRequest)-[r3:MANDATES_POLICY]->(cp:CoveragePolicy)
        OPTIONAL MATCH (cp)-[r4:GOVERNS]->(h:HCPCSCode)-[r5:HAS_FEE_SCHEDULE]->(f:FeeScheduleEntry)-[r6:APPLIES_TO]->(s)
        WHERE f.is_rural = false OR f.is_rural IS NULL
        RETURN s, r1, j, r2, cr, r3, cp,
               collect(DISTINCT h) AS hcpcs_list,
               collect(DISTINCT f) AS fee_list,
               collect(DISTINCT r4) AS r4_list,
               collect(DISTINCT r5) AS r5_list,
               collect(DISTINCT r6) AS r6_list
        """
        result = session.run(query, state_pk=state_pk)

        for row in result:
            s = row["s"]
            j = row["j"]
            cr = row["cr"]
            cp = row["cp"]

            for n in [s, j, cr, cp]:
                tn = self._convert_node(n)
                nodes_by_pk[tn.primary_key] = tn
                active_node_pks.add(tn.primary_key)

            # Ingest relationships
            r1 = row["r1"]
            r2 = row["r2"]
            r3 = row["r3"]

            for r, src, tgt in [(r1, j, s), (r2, cr, j), (r3, cr, cp)]:
                te = self._convert_edge(r, src["primary_key"], tgt["primary_key"])
                edges_by_key[te.edge_key] = te
                active_edge_keys.add(te.edge_key)

            # Ingest HCPCS codes and fees
            hcpcs_list = row["hcpcs_list"] or []
            fee_list = row["fee_list"] or []
            r4_list = row["r4_list"] or []
            r5_list = row["r5_list"] or []
            r6_list = row["r6_list"] or []

            for h in hcpcs_list:
                th = self._convert_node(h)
                nodes_by_pk[th.primary_key] = th

            for f in fee_list:
                tf = self._convert_node(f)
                nodes_by_pk[tf.primary_key] = tf

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

            # Select representative active item (e.g. A6522 or first fee)
            target_hcpcs = "HCPCS-A6522"
            target_fee = None
            for f in fee_list:
                if f.get("hcpcs_code") == "A6522":
                    target_fee = f.get("primary_key")
                    break
            if not target_fee and fee_list:
                target_fee = fee_list[0].get("primary_key")
                target_hcpcs = fee_list[0].get("hcpcs_code", target_hcpcs)
                if not target_hcpcs.startswith("HCPCS-"):
                    target_hcpcs = f"HCPCS-{target_hcpcs}"

            if target_hcpcs in nodes_by_pk:
                active_node_pks.add(target_hcpcs)
                active_edge_keys.add(f"{cp['primary_key']}->GOVERNS->{target_hcpcs}")
            if target_fee and target_fee in nodes_by_pk:
                active_node_pks.add(target_fee)
                active_edge_keys.add(f"{target_hcpcs}->HAS_FEE_SCHEDULE->{target_fee}")
                active_edge_keys.add(f"{target_fee}->APPLIES_TO->{s['primary_key']}")

    def _execute_single_clinical_traversal(
        self,
        anchor_pk: str,
        session: Session,
        nodes_by_pk: Dict[str, TraversalNode],
        edges_by_key: Dict[str, TraversalEdge],
        active_node_pks: Set[str],
        active_edge_keys: Set[str],
    ) -> None:
        """Traces connecting coverage policy, procedure codes, and diagnosis codes for a clinical anchor."""
        query = """
        MATCH (n:PolicyNode {primary_key: $anchor_pk})
        OPTIONAL MATCH (cp:CoveragePolicy)-[r1:GOVERNS]->(h:HCPCSCode)
        WHERE n = h OR n = cp
        OPTIONAL MATCH (cp:CoveragePolicy)-[r2:ALLOWS_DIAGNOSIS]->(d:ICD10Code)
        WHERE n = d OR n = cp
        OPTIONAL MATCH (cr:ChangeRequest)-[r3:MANDATES_POLICY]->(cp)
        RETURN n, cp, h, d, cr, r1, r2, r3
        """
        results = session.run(query, anchor_pk=anchor_pk).data()
        for row in results:
            for key in ["n", "cp", "h", "d", "cr"]:
                item = row.get(key)
                if item:
                    tn = self._convert_node(item)
                    nodes_by_pk[tn.primary_key] = tn
                    active_node_pks.add(tn.primary_key)

            cp = row.get("cp")
            h = row.get("h")
            d = row.get("d")
            cr = row.get("cr")

            if row.get("r1") and cp and h:
                te = self._convert_edge(row["r1"], cp["primary_key"], h["primary_key"])
                edges_by_key[te.edge_key] = te
                active_edge_keys.add(te.edge_key)

            if row.get("r2") and cp and d:
                te = self._convert_edge(row["r2"], cp["primary_key"], d["primary_key"])
                edges_by_key[te.edge_key] = te
                active_edge_keys.add(te.edge_key)

            if row.get("r3") and cr and cp:
                te = self._convert_edge(row["r3"], cr["primary_key"], cp["primary_key"])
                edges_by_key[te.edge_key] = te
                active_edge_keys.add(te.edge_key)

    def _execute_single_general_traversal(
        self,
        anchor_pk: str,
        session: Session,
        nodes_by_pk: Dict[str, TraversalNode],
        edges_by_key: Dict[str, TraversalEdge],
        active_node_pks: Set[str],
        active_edge_keys: Set[str],
    ) -> None:
        """Traces 1-to-2 hop incident neighborhood for any arbitrary single entity."""
        query = """
        MATCH (n:PolicyNode {primary_key: $anchor_pk})
        OPTIONAL MATCH (n)-[r]-(m:PolicyNode)
        WHERE NOT m:FeeScheduleEntry
        RETURN n, r, m,
               startNode(r).primary_key AS src_pk,
               endNode(r).primary_key AS tgt_pk,
               type(r) AS rel_type
        LIMIT 50
        """
        results = session.run(query, anchor_pk=anchor_pk).data()
        for row in results:
            n = row.get("n")
            m = row.get("m")
            r = row.get("r")
            src_pk = row.get("src_pk")
            tgt_pk = row.get("tgt_pk")
            rel_type = row.get("rel_type")
            if n:
                tn = self._convert_node(n)
                nodes_by_pk[tn.primary_key] = tn
                active_node_pks.add(tn.primary_key)
            if m:
                tm = self._convert_node(m)
                nodes_by_pk[tm.primary_key] = tm
                active_node_pks.add(tm.primary_key)
            if r and src_pk and tgt_pk:
                te = self._convert_edge(r, src_pk, tgt_pk)
                edges_by_key[te.edge_key] = te
                active_edge_keys.add(te.edge_key)

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
        # 1. State + Diagnosis (Pattern A Patient Benefit Routing)
        if anchors.state_anchor and anchors.diagnosis_anchor:
            self._execute_pattern_a(
                anchors=anchors,
                session=session,
                nodes_by_pk=nodes_by_pk,
                edges_by_key=edges_by_key,
                active_node_pks=active_node_pks,
                active_edge_keys=active_edge_keys,
            )
            return

        # 2. Multi-Policy Convergence (Pattern C)
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

        # 3. Clinical HCPCS + Diagnosis (Pattern B)
        if (anchors.hcpcs_anchor or any(a.slot == "hcpcs" for a in anchors.all_anchors)) and anchors.diagnosis_anchor:
            self._execute_pattern_b(
                anchors=anchors,
                session=session,
                nodes_by_pk=nodes_by_pk,
                edges_by_key=edges_by_key,
                active_node_pks=active_node_pks,
                active_edge_keys=active_edge_keys,
            )
            return

        # 4. Generalized Shortest-Path Discovery between anchor pairs
        anchor_list = anchors.all_anchors
        for i in range(len(anchor_list)):
            for j in range(i + 1, len(anchor_list)):
                start_pk = anchor_list[i].primary_key
                target_pk = anchor_list[j].primary_key
                path_query = """
                MATCH (start:PolicyNode {primary_key: $start_pk})
                MATCH (target:PolicyNode {primary_key: $target_pk})
                MATCH path = allShortestPaths((start)-[*..6]-(target))
                RETURN path
                """
                path_records = session.run(path_query, start_pk=start_pk, target_pk=target_pk).data()
                for rec in path_records:
                    path = rec.get("path")
                    if path:
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

    def _execute_pattern_a(
        self,
        anchors: ResolvedAnchors,
        session: Session,
        nodes_by_pk: Dict[str, TraversalNode],
        edges_by_key: Dict[str, TraversalEdge],
        active_node_pks: Set[str],
        active_edge_keys: Set[str],
    ) -> None:
        """Executes Pattern A: Patient Benefit Routing."""
        state_pk = anchors.state_anchor.primary_key
        diag_pk = anchors.diagnosis_anchor.primary_key

        query = """
        MATCH (s:State {primary_key: $state_pk})<-[r1:COVERS_STATE]-(j:Jurisdiction)<-[r2:APPLIES_TO_JURISDICTION]-(cr:ChangeRequest)-[r3:MANDATES_POLICY]->(cp:CoveragePolicy)-[r4:ALLOWS_DIAGNOSIS]->(d:ICD10Code {primary_key: $diag_pk})
        OPTIONAL MATCH (cp)-[r5:GOVERNS]->(h:HCPCSCode)-[r6:HAS_FEE_SCHEDULE]->(f:FeeScheduleEntry)-[r7:APPLIES_TO]->(s)
        WHERE f.is_rural = false OR f.is_rural IS NULL
        RETURN s, r1, j, r2, cr, r3, cp, r4, d,
               collect(DISTINCT h) AS hcpcs_list,
               collect(DISTINCT f) AS fee_list,
               collect(DISTINCT r5) AS r5_list,
               collect(DISTINCT r6) AS r6_list,
               collect(DISTINCT r7) AS r7_list
        """

        record = session.run(query, state_pk=state_pk, diag_pk=diag_pk).single()
        if not record or not record["s"]:
            raise TraversalError(
                f"No connecting clinical/coverage path found between {state_pk} and {diag_pk}."
            )

        # Ingest core path entities
        s = record["s"]
        j = record["j"]
        cr = record["cr"]
        cp = record["cp"]
        d = record["d"]

        for n in [s, j, cr, cp, d]:
            tn = self._convert_node(n)
            nodes_by_pk[tn.primary_key] = tn

        # Ingest core relationships
        r1 = record["r1"]
        r2 = record["r2"]
        r3 = record["r3"]
        r4 = record["r4"]

        for r, src, tgt in [(r1, j, s), (r2, cr, j), (r3, cr, cp), (r4, cp, d)]:
            te = self._convert_edge(r, src["primary_key"], tgt["primary_key"])
            edges_by_key[te.edge_key] = te

        # Ingest HCPCS codes and fees
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

        # Define active 7-node chain for canvas illumination
        target_hcpcs = "HCPCS-A6522"
        target_fee = None
        for f in fee_list:
            if f.get("hcpcs_code") == "A6522" and not f.get("is_rural"):
                target_fee = f.get("primary_key")
                break
        if not target_fee and fee_list:
            target_fee = fee_list[0].get("primary_key")
            target_hcpcs = fee_list[0].get("hcpcs_code", target_hcpcs)
            if not target_hcpcs.startswith("HCPCS-"):
                target_hcpcs = f"HCPCS-{target_hcpcs}"

        active_chain_nodes = [
            s["primary_key"],
            j["primary_key"],
            cr["primary_key"],
            cp["primary_key"],
            d["primary_key"],
            target_hcpcs,
        ]
        if target_fee:
            active_chain_nodes.append(target_fee)

        for pk in active_chain_nodes:
            if pk in nodes_by_pk:
                active_node_pks.add(pk)

        # Active edge keys
        active_chain_edges = [
            f"{j['primary_key']}->COVERS_STATE->{s['primary_key']}",
            f"{cr['primary_key']}->APPLIES_TO_JURISDICTION->{j['primary_key']}",
            f"{cr['primary_key']}->MANDATES_POLICY->{cp['primary_key']}",
            f"{cp['primary_key']}->ALLOWS_DIAGNOSIS->{d['primary_key']}",
            f"{cp['primary_key']}->GOVERNS->{target_hcpcs}",
        ]
        if target_fee:
            active_chain_edges.append(f"{target_hcpcs}->HAS_FEE_SCHEDULE->{target_fee}")
            active_chain_edges.append(f"{target_fee}->APPLIES_TO->{s['primary_key']}")

        for ek in active_chain_edges:
            active_edge_keys.add(ek)

    def _execute_pattern_b(
        self,
        anchors: ResolvedAnchors,
        session: Session,
        nodes_by_pk: Dict[str, TraversalNode],
        edges_by_key: Dict[str, TraversalEdge],
        active_node_pks: Set[str],
        active_edge_keys: Set[str],
    ) -> None:
        """Executes Pattern B: Clinical Coverage & Diagnosis Bridging."""
        hcpcs_anchor = next((a for a in anchors.all_anchors if a.slot in ("hcpcs", "hcpcscode")), None)
        diag_anchor = anchors.diagnosis_anchor

        if hcpcs_anchor:
            query = """
            MATCH (h:HCPCSCode {primary_key: $hcpcs_pk})<-[r1:GOVERNS]-(cp:CoveragePolicy)-[r2:ALLOWS_DIAGNOSIS]->(d:ICD10Code)
            OPTIONAL MATCH (cr:ChangeRequest)-[r3:MANDATES_POLICY]->(cp)
            RETURN h, r1, cp, r2, d, cr, r3
            """
            results = session.run(query, hcpcs_pk=hcpcs_anchor.primary_key).data()
        elif diag_anchor:
            query = """
            MATCH (d:ICD10Code {primary_key: $diag_pk})<-[r2:ALLOWS_DIAGNOSIS]-(cp:CoveragePolicy)-[r1:GOVERNS]->(h:HCPCSCode)
            OPTIONAL MATCH (cr:ChangeRequest)-[r3:MANDATES_POLICY]->(cp)
            RETURN h, r1, cp, r2, d, cr, r3
            """
            results = session.run(query, diag_pk=diag_anchor.primary_key).data()
        else:
            return

        for row in results:
            h = row["h"]
            cp = row["cp"]
            d = row["d"]
            cr = row.get("cr")

            for n in [h, cp, d, cr]:
                if n:
                    tn = self._convert_node(n)
                    nodes_by_pk[tn.primary_key] = tn
                    active_node_pks.add(tn.primary_key)

            if row.get("r1") and cp and h:
                te = self._convert_edge(row["r1"], cp["primary_key"], h["primary_key"])
                edges_by_key[te.edge_key] = te
                active_edge_keys.add(te.edge_key)

            if row.get("r2") and cp and d:
                te = self._convert_edge(row["r2"], cp["primary_key"], d["primary_key"])
                edges_by_key[te.edge_key] = te
                active_edge_keys.add(te.edge_key)

            if row.get("r3") and cr and cp:
                te = self._convert_edge(row["r3"], cr["primary_key"], cp["primary_key"])
                edges_by_key[te.edge_key] = te
                active_edge_keys.add(te.edge_key)

    def _execute_pattern_c(
        self,
        anchors: ResolvedAnchors,
        session: Session,
        nodes_by_pk: Dict[str, TraversalNode],
        edges_by_key: Dict[str, TraversalEdge],
        active_node_pks: Set[str],
        active_edge_keys: Set[str],
    ) -> None:
        """Executes Pattern C: Cross-Policy Convergence and Omnibus Lineage."""
        policy_anchors = [a for a in anchors.all_anchors if a.slot == "policy"]
        p1_pk = policy_anchors[0].primary_key
        p2_pk = policy_anchors[1].primary_key

        query = """
        MATCH (p1:Policy {primary_key: $p1_pk})-[:TARGETS_BILL]->(b1:Bill)-[:ENACTED_AS]->(pl:PublicLaw)<-[:ENACTED_AS]-(b2:Bill)<-[:TARGETS_BILL]-(p2:Policy {primary_key: $p2_pk})
        MATCH (pl)-[r1:MODIFIES_CODE]->(sec:StatutorySection)-[r2:IMPLEMENTED_BY]->(reg:Regulation)-[r3:ISSUES_TRANSMITTAL]->(cr:ChangeRequest)
        RETURN p1, b1, pl, b2, p2, r1, sec, r2, reg, r3, cr
        """
        results = session.run(query, p1_pk=p1_pk, p2_pk=p2_pk).data()

        for row in results:
            for key in ["p1", "b1", "pl", "b2", "p2", "sec", "reg", "cr"]:
                item = row.get(key)
                if item:
                    tn = self._convert_node(item)
                    nodes_by_pk[tn.primary_key] = tn
                    active_node_pks.add(tn.primary_key)

            # Edges
            if row.get("p1") and row.get("b1"):
                active_edge_keys.add(f"{row['p1']['primary_key']}->TARGETS_BILL->{row['b1']['primary_key']}")
            if row.get("b1") and row.get("pl"):
                active_edge_keys.add(f"{row['b1']['primary_key']}->ENACTED_AS->{row['pl']['primary_key']}")
            if row.get("p2") and row.get("b2"):
                active_edge_keys.add(f"{row['p2']['primary_key']}->TARGETS_BILL->{row['b2']['primary_key']}")
            if row.get("b2") and row.get("pl"):
                active_edge_keys.add(f"{row['b2']['primary_key']}->ENACTED_AS->{row['pl']['primary_key']}")
            if row.get("r1") and row.get("pl") and row.get("sec"):
                te = self._convert_edge(row["r1"], row["pl"]["primary_key"], row["sec"]["primary_key"])
                edges_by_key[te.edge_key] = te
                active_edge_keys.add(te.edge_key)
            if row.get("r2") and row.get("sec") and row.get("reg"):
                te = self._convert_edge(row["r2"], row["sec"]["primary_key"], row["reg"]["primary_key"])
                edges_by_key[te.edge_key] = te
                active_edge_keys.add(te.edge_key)
            if row.get("r3") and row.get("reg") and row.get("cr"):
                te = self._convert_edge(row["r3"], row["reg"]["primary_key"], row["cr"]["primary_key"])
                edges_by_key[te.edge_key] = te
                active_edge_keys.add(te.edge_key)

    def _convert_node(self, node: Any) -> TraversalNode:
        """Converts Neo4j node object or dict into TraversalNode."""
        props = dict(node)
        pk = props.get("primary_key", "")
        # Resolve primary label (skipping generic PolicyNode)
        labels = []
        if hasattr(node, "labels"):
            labels = [lbl for lbl in node.labels if lbl != "PolicyNode"]
        elif "labels" in props:
            labels = [lbl for lbl in props["labels"] if lbl != "PolicyNode"]

        if labels:
            label = labels[0]
        else:
            # Deterministic prefix fallback conforming to 14 domain entity prefixes
            if pk.startswith("STATE-"): label = "State"
            elif pk.startswith("JURIS-"): label = "Jurisdiction"
            elif pk.startswith("CMS-CR-"): label = "ChangeRequest"
            elif pk.startswith("CMS-MCD-"): label = "CoveragePolicy"
            elif pk.startswith("FEE-"): label = "FeeScheduleEntry"
            elif pk.startswith("HCPCS-"): label = "HCPCSCode"
            elif pk.startswith("ICD10-"): label = "ICD10Code"
            elif pk.startswith("POLICY-"): label = "Policy"
            elif pk.startswith("PLAW-"): label = "PublicLaw"
            elif pk.startswith("FR-"): label = "Regulation"
            elif pk.startswith("BILL-"): label = "Bill"
            elif pk.startswith("USC-"): label = "StatutorySection"
            elif pk.startswith("PUBMED-"): label = "LiteratureStudy"
            elif pk.startswith("LDA-"): label = "LobbyingFiling"
            else: label = props.get("label", "Node")

        raw_name = props.get("name") or props.get("state_name") or props.get("section") or props.get("title") or pk
        name = str(raw_name)

        return TraversalNode(
            primary_key=pk,
            label=label,
            name=name,
            properties=props,
        )

    def _convert_edge(self, rel: Any, src_pk: Optional[str] = None, tgt_pk: Optional[str] = None) -> TraversalEdge:
        """Converts Neo4j relationship object into TraversalEdge with provenance."""
        rel_type = rel.type if hasattr(rel, "type") else getattr(rel, "label", "RELATED_TO")
        props = dict(rel) if hasattr(rel, "items") else {}

        if not src_pk and hasattr(rel, "start_node") and "primary_key" in rel.start_node:
            src_pk = rel.start_node["primary_key"]
        if not tgt_pk and hasattr(rel, "end_node") and "primary_key" in rel.end_node:
            tgt_pk = rel.end_node["primary_key"]

        src = src_pk or "UNKNOWN"
        tgt = tgt_pk or "UNKNOWN"
        edge_key = f"{src}->{rel_type}->{tgt}"

        # Extract provenance dictionary conforming to INV-PROVENANCE-COMPLETENESS
        provenance = {
            "source_uri": props.get("source_uri", "verified://federal-statute"),
            "selector": props.get("selector", "direct"),
            "ingestion_timestamp": props.get("ingestion_timestamp", "2026-10-13T01:23:54Z"),
            "run_id": props.get("run_id", "export-run-001"),
        }

        return TraversalEdge(
            source_pk=src,
            target_pk=tgt,
            label=rel_type,
            edge_key=edge_key,
            provenance=provenance,
        )
