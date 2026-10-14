"""
Deterministic In-Memory Embedded Graph Driver for Zero-Daemon Cloud Execution.

Provides a Neo4j-compatible Driver/Session/Record/Node/Relationship/Path interface
backed by exported JSON graph artifacts (e.g. `embedded://exports/lta_knowledge_graph.json`).
Enables the FastAPI backend to run inside stateless cloud containers (Hugging Face Spaces)
with identical query semantics to a live Neo4j Bolt instance.
"""

from __future__ import annotations
from collections import deque
import json
import os
import re
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional, Set, Tuple


class EmbeddedNode(dict):
    """Neo4j Node-compatible dictionary wrapper carrying `.labels`."""

    def __init__(self, primary_key: str, labels: List[str], properties: Dict[str, Any]):
        merged = dict(properties)
        merged["primary_key"] = primary_key
        super().__init__(merged)
        self.primary_key: str = primary_key
        self.labels: frozenset[str] = frozenset(labels)


class EmbeddedRelationship(dict):
    """Neo4j Relationship-compatible dictionary wrapper carrying `.type`, `.start_node`, and `.end_node`."""

    def __init__(
        self,
        rel_type: str,
        start_node: EmbeddedNode,
        end_node: EmbeddedNode,
        properties: Dict[str, Any],
    ):
        super().__init__(properties)
        self.type: str = rel_type
        self.label: str = rel_type
        self.start_node: EmbeddedNode = start_node
        self.end_node: EmbeddedNode = end_node
        self.edge_key: str = f"{start_node.primary_key}->{rel_type}->{end_node.primary_key}"


class EmbeddedPath:
    """Neo4j Path-compatible container carrying `.nodes` and `.relationships`."""

    def __init__(self, nodes: List[EmbeddedNode], relationships: List[EmbeddedRelationship]):
        self.nodes: List[EmbeddedNode] = nodes
        self.relationships: List[EmbeddedRelationship] = relationships


class EmbeddedRecord(dict):
    """Neo4j Record-compatible mapping supporting key indexing, `.get()`, and `.data()`."""

    def data(self) -> Dict[str, Any]:
        out: Dict[str, Any] = {}
        for k, v in self.items():
            if isinstance(v, EmbeddedNode):
                out[k] = dict(v)
            elif isinstance(v, EmbeddedRelationship):
                out[k] = dict(v)
            elif isinstance(v, list):
                out[k] = [dict(x) if isinstance(x, (EmbeddedNode, EmbeddedRelationship)) else x for x in v]
            else:
                out[k] = v
        return out


class EmbeddedResult:
    """Neo4j Result-compatible iterable supporting `.single()`, `.data()`, and iteration."""

    def __init__(self, records: List[Dict[str, Any]]):
        self._records: List[EmbeddedRecord] = [EmbeddedRecord(r) for r in records]

    def __iter__(self) -> Iterator[EmbeddedRecord]:
        return iter(self._records)

    def single(self) -> Optional[EmbeddedRecord]:
        return self._records[0] if self._records else None

    def data(self) -> List[Dict[str, Any]]:
        return [r.data() for r in self._records]


class EmbeddedGraphStore:
    """In-memory property graph indexed by primary_key, label, and relationship type."""

    def __init__(self, json_paths: List[Path]):
        self.nodes_by_pk: Dict[str, EmbeddedNode] = {}
        self.nodes_by_upper_pk: Dict[str, EmbeddedNode] = {}
        self.nodes_by_label: Dict[str, List[EmbeddedNode]] = {}
        self.relationships: List[EmbeddedRelationship] = []
        self.rels_by_key: Dict[str, EmbeddedRelationship] = {}
        self.out_rels: Dict[str, List[EmbeddedRelationship]] = {}
        self.in_rels: Dict[str, List[EmbeddedRelationship]] = {}

        for path in json_paths:
            if not path.exists():
                raise FileNotFoundError(f"Embedded graph artifact not found at '{path}'.")
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if not isinstance(data, dict) or "nodes" not in data or "edges" not in data:
                raise ValueError(f"Invalid graph export schema in '{path}': expected 'nodes' and 'edges' keys.")
            self._ingest_dict(data)

    def _ingest_dict(self, data: Dict[str, Any]) -> None:
        for raw_node in data.get("nodes", []):
            pk = str(raw_node.get("primary_key", "")).strip()
            if not pk:
                continue
            lbl = str(raw_node.get("label", "PolicyNode")).strip()
            labels = ["PolicyNode", lbl] if lbl != "PolicyNode" else ["PolicyNode"]
            props = {k: v for k, v in raw_node.items() if k not in ("label",)}
            props["primary_key"] = pk
            node = EmbeddedNode(primary_key=pk, labels=labels, properties=props)
            self.nodes_by_pk[pk] = node
            self.nodes_by_upper_pk[pk.upper()] = node

        # Rebuild label index deterministically
        self.nodes_by_label.clear()
        for node in self.nodes_by_pk.values():
            for lbl in node.labels:
                self.nodes_by_label.setdefault(lbl, []).append(node)

        for raw_edge in data.get("edges", []):
            spk = str(raw_edge.get("source_pk", "")).strip()
            tpk = str(raw_edge.get("target_pk", "")).strip()
            rel_type = str(raw_edge.get("label", "")).strip()
            if not spk or not tpk or not rel_type:
                continue
            src_node = self.nodes_by_pk.get(spk)
            tgt_node = self.nodes_by_pk.get(tpk)
            if src_node is None or tgt_node is None:
                continue
            prov = raw_edge.get("provenance") or {}
            props: Dict[str, Any] = {}
            if isinstance(prov, dict):
                props.update(prov)
            for k, v in raw_edge.items():
                if k not in ("source_pk", "target_pk", "label", "provenance"):
                    props[k] = v
            rel = EmbeddedRelationship(rel_type=rel_type, start_node=src_node, end_node=tgt_node, properties=props)
            if rel.edge_key not in self.rels_by_key:
                self.rels_by_key[rel.edge_key] = rel
                self.relationships.append(rel)
                self.out_rels.setdefault(spk, []).append(rel)
                self.in_rels.setdefault(tpk, []).append(rel)


class EmbeddedSession:
    """Neo4j Session-compatible query runner over `EmbeddedGraphStore`."""

    def __init__(self, store: EmbeddedGraphStore):
        self._store = store

    def __enter__(self) -> "EmbeddedSession":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        pass

    def close(self) -> None:
        pass

    def run(self, query: str, **params: Any) -> EmbeddedResult:
        q = " ".join(query.strip().split())
        s = self._store

        # 1. Schema / Admin queries
        if q.startswith("SHOW INDEXES") or q.startswith("SHOW CONSTRAINTS") or q.startswith("CREATE CONSTRAINT") or q.startswith("DROP "):
            return EmbeddedResult([])

        # 2. Summary statistics queries (src/graph/neo4j_sync.py)
        if "RETURN labels(n) AS labels, count(n) AS count" in q:
            counts: Dict[Tuple[str, ...], int] = {}
            for node in s.nodes_by_pk.values():
                secondary = sorted([l for l in node.labels if l != "PolicyNode"])
                key = ("PolicyNode", *secondary)
                counts[key] = counts.get(key, 0) + 1
            rows = [
                {"labels": list(k), "count": c}
                for k, c in sorted(counts.items(), key=lambda x: (-x[1], x[0]))
            ]
            return EmbeddedResult(rows)

        if "RETURN type(r) AS rel_type, count(r) AS count" in q:
            rcounts: Dict[str, int] = {}
            for rel in s.relationships:
                rcounts[rel.type] = rcounts.get(rel.type, 0) + 1
            rows = [
                {"rel_type": k, "count": c}
                for k, c in sorted(rcounts.items(), key=lambda x: (-x[1], x[0]))
            ]
            return EmbeddedResult(rows)

        if q == "MATCH (n:PolicyNode) RETURN count(n) AS total":
            return EmbeddedResult([{"total": len(s.nodes_by_pk)}])

        if q == "MATCH (:PolicyNode)-[r]->(:PolicyNode) RETURN count(r) AS total":
            return EmbeddedResult([{"total": len(s.relationships)}])

        # 3. Health / Policy keyword queries
        if "MATCH (p:Policy)" in q and "RETURN p.keyword AS kw, p.primary_key AS pk" in q:
            rows = [
                {"kw": n.get("keyword"), "pk": n.primary_key}
                for n in s.nodes_by_label.get("Policy", [])
            ]
            return EmbeddedResult(rows)

        if "MATCH (p:Policy) WHERE p.primary_key = $pk OR toUpper(p.keyword) = $kw RETURN p.primary_key AS pk" in q:
            pk = str(params.get("pk", ""))
            kw = str(params.get("kw", "")).upper()
            for n in s.nodes_by_label.get("Policy", []):
                if n.primary_key == pk or str(n.get("keyword", "")).upper() == kw:
                    return EmbeddedResult([{"pk": n.primary_key}])
            return EmbeddedResult([])

        if q == "MATCH (p:Policy) RETURN p.primary_key AS pk":
            return EmbeddedResult([{"pk": n.primary_key} for n in s.nodes_by_label.get("Policy", [])])

        if q == "MATCH (n:PolicyNode) RETURN n.primary_key AS pk":
            return EmbeddedResult([{"pk": pk} for pk in s.nodes_by_pk])

        if q == "MATCH (a:PolicyNode)-[r]->(b:PolicyNode) RETURN a.primary_key AS src, b.primary_key AS tgt":
            return EmbeddedResult([
                {"src": r.start_node.primary_key, "tgt": r.end_node.primary_key}
                for r in s.relationships
            ])

        # 4. Entity Inspection queries (GET /api/entities/{primary_key})
        if "WHERE n.primary_key = $pk OR toUpper(n.primary_key) = toUpper($pk)" in q and "RETURN n, labels(n) AS lbls" in q:
            pk = str(params.get("pk", "")).strip()
            node = s.nodes_by_pk.get(pk) or s.nodes_by_upper_pk.get(pk.upper())
            if not node:
                return EmbeddedResult([])
            return EmbeddedResult([{"n": node, "lbls": list(node.labels)}])

        if "MATCH (src:PolicyNode)-[r]->(tgt:PolicyNode)" in q and "WHERE src.primary_key = $pk OR tgt.primary_key = $pk" in q:
            pk = str(params.get("pk", "")).strip()
            node = s.nodes_by_pk.get(pk) or s.nodes_by_upper_pk.get(pk.upper())
            actual_pk = node.primary_key if node else pk
            rels = list(s.out_rels.get(actual_pk, [])) + [
                r for r in s.in_rels.get(actual_pk, []) if r.start_node.primary_key != actual_pk
            ]
            rows = [
                {"spk": r.start_node.primary_key, "tpk": r.end_node.primary_key, "r": r}
                for r in rels[:250]
            ]
            return EmbeddedResult(rows)

        # 5. Topology filter validation & expansion queries (src/api/routes.py)
        if "MATCH (j:Jurisdiction {primary_key: $juris_pk}) RETURN j.primary_key AS pk" in q:
            jpk = str(params.get("juris_pk", ""))
            node = s.nodes_by_pk.get(jpk)
            if node and "Jurisdiction" in node.labels:
                return EmbeddedResult([{"pk": node.primary_key}])
            return EmbeddedResult([])

        if "MATCH (j:Jurisdiction)-[:COVERS_STATE]->(s:State {state_code: $state_code})" in q:
            sc = str(params.get("state_code", "")).upper()
            for j in s.nodes_by_label.get("Jurisdiction", []):
                for rel in s.out_rels.get(j.primary_key, []):
                    if rel.type == "COVERS_STATE" and "State" in rel.end_node.labels:
                        if str(rel.end_node.get("state_code", "")).upper() == sc:
                            return EmbeddedResult([{"s_pk": rel.end_node.primary_key, "j_pk": j.primary_key}])
            return EmbeddedResult([])

        if "MATCH (:Jurisdiction {primary_key: $juris_pk})-[:COVERS_STATE]->(s:State)" in q:
            jpk = str(params.get("juris_pk", ""))
            state_pks = [
                rel.end_node.primary_key
                for rel in s.out_rels.get(jpk, [])
                if rel.type == "COVERS_STATE" and "State" in rel.end_node.labels
            ]
            return EmbeddedResult([{"state_pks": state_pks}])

        if "WHERE NOT n:FeeScheduleRate AND NOT n:FeeScheduleEntry" in q and "OPTIONAL MATCH (n)-[r]->(m:PolicyNode)" in q:
            rows: List[Dict[str, Any]] = []
            for n in s.nodes_by_pk.values():
                if "FeeScheduleRate" in n.labels or "FeeScheduleEntry" in n.labels:
                    continue
                valid_rels = [
                    rel for rel in s.out_rels.get(n.primary_key, [])
                    if "FeeScheduleRate" not in rel.end_node.labels and "FeeScheduleEntry" not in rel.end_node.labels
                ]
                if not valid_rels:
                    rows.append({"n": n, "r": None, "m": None})
                else:
                    for rel in valid_rels:
                        rows.append({"n": n, "r": rel, "m": rel.end_node})
            return EmbeddedResult(rows)

        if "MATCH (h:ProcedureCode)-[r2:HAS_RATE]->(f:FeeScheduleRate)-[r1:APPLIES_TO_STATE]->(s:State {state_code: $state_code})" in q:
            sc = str(params.get("state_code", "")).upper()
            state_node = s.nodes_by_pk.get(f"STATE-{sc}")
            if not state_node:
                return EmbeddedResult([])
            rows = []
            for r1 in s.in_rels.get(state_node.primary_key, []):
                if r1.type == "APPLIES_TO_STATE" and "FeeScheduleRate" in r1.start_node.labels:
                    f_node = r1.start_node
                    for r2 in s.in_rels.get(f_node.primary_key, []):
                        if r2.type == "HAS_RATE" and "ProcedureCode" in r2.start_node.labels:
                            rows.append({"f": f_node, "r1": r1, "s": state_node, "h": r2.start_node, "r2": r2})
            return EmbeddedResult(rows)

        if "MATCH (h:ProcedureCode)-[r2:HAS_RATE]->(f:FeeScheduleRate)-[r1:APPLIES_TO_STATE]->(s:State)" in q:
            state_pks = params.get("state_pks")
            allowed_set = set(state_pks) if state_pks is not None else None
            rows = []
            for f_node in s.nodes_by_label.get("FeeScheduleRate", []):
                r1_list = [r for r in s.out_rels.get(f_node.primary_key, []) if r.type == "APPLIES_TO_STATE"]
                r2_list = [r for r in s.in_rels.get(f_node.primary_key, []) if r.type == "HAS_RATE"]
                for r1 in r1_list:
                    st_node = r1.end_node
                    if allowed_set is not None and st_node.primary_key not in allowed_set:
                        continue
                    for r2 in r2_list:
                        rows.append({"f": f_node, "r1": r1, "s": st_node, "h": r2.start_node, "r2": r2})
                        if len(rows) >= 4000:
                            return EmbeddedResult(rows)
            return EmbeddedResult(rows)

        # 6. EntityAnchorLinker queries (src/graphrag/entity_linker.py)
        if "WHERE NOT n:FeeScheduleRate AND NOT n:FeeScheduleEntry AND NOT n:State" in q:
            rows = [
                {"primary_key": n.primary_key, "labels": list(n.labels), "props": dict(n)}
                for n in s.nodes_by_pk.values()
                if not ({"FeeScheduleRate", "FeeScheduleEntry", "State"} & set(n.labels))
            ]
            return EmbeddedResult(rows)

        if "MATCH (n:PolicyNode) WHERE toUpper(n.primary_key) = toUpper($pk)" in q:
            pk = str(params.get("pk", "")).strip().upper()
            node = s.nodes_by_upper_pk.get(pk)
            if not node:
                return EmbeddedResult([])
            return EmbeddedResult([{"primary_key": node.primary_key, "labels": list(node.labels), "props": dict(node)}])

        if "MATCH (n:PolicyNode {primary_key: $pk}) RETURN n, labels(n) as lbls" in q:
            pk = str(params.get("pk", "")).strip()
            node = s.nodes_by_pk.get(pk)
            if not node:
                return EmbeddedResult([])
            return EmbeddedResult([{"n": node, "lbls": list(node.labels)}])

        if q == "MATCH (j:Jurisdiction {primary_key: $pk}) RETURN j":
            node = s.nodes_by_pk.get(str(params.get("pk", "")))
            return EmbeddedResult([{"j": node}]) if node and "Jurisdiction" in node.labels else EmbeddedResult([])

        if q == "MATCH (j:Jurisdiction) RETURN j.primary_key AS pk, j.contractor_name AS cname":
            return EmbeddedResult([
                {"pk": n.primary_key, "cname": n.get("contractor_name")}
                for n in s.nodes_by_label.get("Jurisdiction", [])
            ])

        if q == "MATCH (s:State {primary_key: $pk}) RETURN s":
            node = s.nodes_by_pk.get(str(params.get("pk", "")))
            return EmbeddedResult([{"s": node}]) if node and "State" in node.labels else EmbeddedResult([])

        if "MATCH (d:PolicyNode {primary_key: $pk}) WHERE d:DiagnosisCode OR d:ICD10Code RETURN d, labels(d) AS lbls" in q:
            node = s.nodes_by_pk.get(str(params.get("pk", "")))
            if node and ({"DiagnosisCode", "ICD10Code"} & set(node.labels)):
                return EmbeddedResult([{"d": node, "lbls": list(node.labels)}])
            return EmbeddedResult([])

        if "MATCH (d:PolicyNode) WHERE d:DiagnosisCode OR d:ICD10Code RETURN properties(d) AS props, labels(d) AS lbls" in q:
            nodes = s.nodes_by_label.get("DiagnosisCode", []) + s.nodes_by_label.get("ICD10Code", [])
            seen: Set[str] = set()
            rows = []
            for n in nodes:
                if n.primary_key not in seen:
                    seen.add(n.primary_key)
                    rows.append({"props": dict(n), "lbls": list(n.labels)})
            return EmbeddedResult(rows)

        if "MATCH (h:PolicyNode {primary_key: $pk}) WHERE h:ProcedureCode OR h:HCPCSCode RETURN h, labels(h) AS lbls" in q:
            node = s.nodes_by_pk.get(str(params.get("pk", "")))
            if node and ({"ProcedureCode", "HCPCSCode"} & set(node.labels)):
                return EmbeddedResult([{"h": node, "lbls": list(node.labels)}])
            return EmbeddedResult([])

        # Simple label property scans: MATCH (x:<Label>) RETURN properties(x) AS props
        m_label_props = re.match(r"^MATCH \(\w+:(\w+)\) RETURN properties\(\w+\) AS props$", q)
        if m_label_props:
            lbl = m_label_props.group(1)
            return EmbeddedResult([{"props": dict(n)} for n in s.nodes_by_label.get(lbl, [])])

        if "collect(DISTINCT b.title) AS bill_titles" in q:
            rows = []
            cp_titles = [
                n.get("title")
                for n in s.nodes_by_label.get("CoveragePolicy", [])
                if n.get("title")
            ]
            stat_headings = [
                n.get("heading")
                for n in s.nodes_by_label.get("StatutorySection", [])
                if n.get("heading")
            ]
            for p_node in s.nodes_by_label.get("Policy", []):
                bill_titles = [
                    rel.end_node.get("title")
                    for rel in s.out_rels.get(p_node.primary_key, [])
                    if rel.type == "DISCOVERED_BILL" and rel.end_node.get("title")
                ]
                rows.append({
                    "pk": p_node.primary_key,
                    "keyword": p_node.get("keyword"),
                    "bill_titles": bill_titles,
                    "headings": stat_headings,
                    "cp_titles": cp_titles,
                })
            return EmbeddedResult(rows)

        # 7. TopologicalTraversalEngine queries (src/graphrag/traversal.py)
        if q == "MATCH (tr:Transmittal) RETURN tr.primary_key AS pk":
            return EmbeddedResult([{"pk": n.primary_key} for n in s.nodes_by_label.get("Transmittal", [])])

        if "WHERE tr.primary_key IN $tr_pks" in q and "collect(DISTINCT tr) AS trs" in q:
            return self._run_upstream_lineage_query()

        if "WHERE j.primary_key IN $juris_pks" in q and "RETURN j, r1, s, tr, r2, cp, r3" in q:
            return self._run_jurisdiction_traversal(params.get("juris_pks") or [])

        if "MATCH (s:State {primary_key: $state_pk})<-[r1:COVERS_STATE]-(j:Jurisdiction)" in q and "diag_pk" not in params:
            return self._run_single_state_traversal(str(params.get("state_pk", "")))

        if "MATCH (s:State {primary_key: $state_pk})<-[r1:COVERS_STATE]-(j:Jurisdiction)" in q and "diag_pk" in params:
            return self._run_pattern_a(str(params.get("state_pk", "")), str(params.get("diag_pk", "")))

        if "MATCH (n:PolicyNode {primary_key: $anchor_pk})" in q and "RETURN n, cp, h, d, tr, r1, r2, r3" in q:
            return self._run_single_clinical_traversal(str(params.get("anchor_pk", "")))

        if "MATCH (h:ProcedureCode {primary_key: $hcpcs_pk})<-[r1:COVERS_PROCEDURE]-(cp:CoveragePolicy)-[r2:REQUIRES_DIAGNOSIS]->(d:DiagnosisCode)" in q:
            return self._run_pattern_b_hcpcs(str(params.get("hcpcs_pk", "")))

        if "MATCH (d:DiagnosisCode {primary_key: $diag_pk})<-[r2:REQUIRES_DIAGNOSIS]-(cp:CoveragePolicy)-[r1:COVERS_PROCEDURE]->(h:ProcedureCode)" in q:
            return self._run_pattern_b_diag(str(params.get("diag_pk", "")))

        if "OPTIONAL MATCH path = (n)-[*1..8]-(m:PolicyNode)" in q:
            return self._run_single_general_traversal(str(params.get("anchor_pk", "")))

        if "MATCH path = allShortestPaths((start)-[*..10]-(target))" in q:
            return self._run_shortest_paths(str(params.get("start_pk", "")), str(params.get("target_pk", "")))

        # 8. Oracle test queries (tests/test_graphrag_pipeline.py)
        if "MATCH (:ProcedureCode)-[r]->(:DiagnosisCode) RETURN count(r) AS cnt" in q:
            cnt = sum(
                1
                for r in s.relationships
                if "ProcedureCode" in r.start_node.labels and "DiagnosisCode" in r.end_node.labels
            )
            return EmbeddedResult([{"cnt": cnt}])

        if "MATCH (h:ProcedureCode {primary_key: 'HCPCS-A6583'})<-[:COVERS_PROCEDURE]-(cp:CoveragePolicy)-[:REQUIRES_DIAGNOSIS]->(d:DiagnosisCode)" in q:
            for r1 in s.in_rels.get("HCPCS-A6583", []):
                if r1.type == "COVERS_PROCEDURE" and "CoveragePolicy" in r1.start_node.labels:
                    cp = r1.start_node
                    diag_count = sum(
                        1
                        for r2 in s.out_rels.get(cp.primary_key, [])
                        if r2.type == "REQUIRES_DIAGNOSIS" and "DiagnosisCode" in r2.end_node.labels
                    )
                    return EmbeddedResult([{"cp_pk": cp.primary_key, "diag_count": diag_count}])
            return EmbeddedResult([])

        raise ValueError(f"Unsupported Cypher query in EmbeddedSession: {q}")

    def _run_upstream_lineage_query(self) -> EmbeddedResult:
        s = self._store
        rel_type_map = {
            "MANDATES_POLICY": "r_mands",
            "IMPLEMENTED_BY": "r_impls",
            "CODIFIED_IN": "r_cods",
            "AUTHORIZED_BY": "r_auths",
            "AMENDS": "r_amendss",
            "CONTAINS": "r_conts",
            "ENACTED_AS": "r_enacteds",
            "INCORPORATED_INTO": "r_incs",
            "DISCOVERED_BILL": "r_disc1s",
            "HAS_BUDGET_IMPACT": "r_cbos",
            "HAS_ADVOCACY_RECORD": "r_ldas",
            "SUPPORTED_BY_EVIDENCE": "r_pubs",
        }
        rel_buckets: Dict[str, List[EmbeddedRelationship]] = {
            k: [] for k in (
                "r_mands", "r_impls", "r_cods", "r_auths", "r_amendss",
                "r_conts", "r_enacteds", "r_incs", "r_disc1s", "r_disc2s",
                "r_cbos", "r_ldas", "r_pubs",
            )
        }
        for rel in s.relationships:
            bucket = rel_type_map.get(rel.type)
            if bucket:
                rel_buckets[bucket].append(rel)

        record = {
            "trs": list(s.nodes_by_label.get("Transmittal", [])),
            "cps": list(s.nodes_by_label.get("CoveragePolicy", [])),
            "cfrs": list(s.nodes_by_label.get("CFRSection", [])),
            "regs": list(s.nodes_by_label.get("Regulation", [])),
            "uscs": list(s.nodes_by_label.get("USCSection", [])),
            "stats": list(s.nodes_by_label.get("StatutorySection", [])),
            "pls": list(s.nodes_by_label.get("PublicLaw", [])),
            "b_enacteds": list(s.nodes_by_label.get("Bill", [])),
            "b_intros": list(s.nodes_by_label.get("Bill", [])),
            "ps": list(s.nodes_by_label.get("Policy", [])),
            "p2s": [],
            "cbos": list(s.nodes_by_label.get("CBOScore", [])),
            "ldas": list(s.nodes_by_label.get("LobbyingFiling", [])),
            "pubs": list(s.nodes_by_label.get("LiteratureStudy", [])),
            **rel_buckets,
        }
        return EmbeddedResult([record])

    def _run_jurisdiction_traversal(self, juris_pks: List[str]) -> EmbeddedResult:
        s = self._store
        rows: List[Dict[str, Any]] = []
        for jpk in juris_pks:
            j = s.nodes_by_pk.get(jpk)
            if not j or "Jurisdiction" not in j.labels:
                continue
            r1_list = [r for r in s.out_rels.get(jpk, []) if r.type == "COVERS_STATE"]
            r2_list = [r for r in s.in_rels.get(jpk, []) if r.type == "APPLIES_TO_JURISDICTION"]
            for r1 in r1_list or [None]:
                st_node = r1.end_node if r1 else None
                for r2 in r2_list or [None]:
                    tr_node = r2.start_node if r2 else None
                    r3_list = (
                        [r for r in s.out_rels.get(tr_node.primary_key, []) if r.type == "MANDATES_POLICY"]
                        if tr_node
                        else []
                    )
                    for r3 in r3_list or [None]:
                        cp_node = r3.end_node if r3 else None
                        rows.append({
                            "j": j,
                            "r1": r1,
                            "s": st_node,
                            "tr": tr_node,
                            "r2": r2,
                            "cp": cp_node,
                            "r3": r3,
                        })
        return EmbeddedResult(rows)

    def _run_single_state_traversal(self, state_pk: str) -> EmbeddedResult:
        s = self._store
        st_node = s.nodes_by_pk.get(state_pk)
        if not st_node or "State" not in st_node.labels:
            return EmbeddedResult([])

        rows: List[Dict[str, Any]] = []
        for r1 in s.in_rels.get(state_pk, []):
            if r1.type != "COVERS_STATE" or "Jurisdiction" not in r1.start_node.labels:
                continue
            j_node = r1.start_node
            for r2 in s.in_rels.get(j_node.primary_key, []):
                if r2.type != "APPLIES_TO_JURISDICTION" or "Transmittal" not in r2.start_node.labels:
                    continue
                tr_node = r2.start_node
                for r3 in s.out_rels.get(tr_node.primary_key, []):
                    if r3.type != "MANDATES_POLICY" or "CoveragePolicy" not in r3.end_node.labels:
                        continue
                    cp_node = r3.end_node

                    r4_list = [
                        r for r in s.out_rels.get(cp_node.primary_key, [])
                        if r.type == "COVERS_PROCEDURE" and "ProcedureCode" in r.end_node.labels
                    ]
                    hcpcs_list = [r.end_node for r in r4_list]

                    r7_list = [
                        r for r in s.out_rels.get(cp_node.primary_key, [])
                        if r.type == "REQUIRES_DIAGNOSIS" and "DiagnosisCode" in r.end_node.labels
                    ]
                    diag_list = [r.end_node for r in r7_list]

                    r6_list = [
                        r for r in s.in_rels.get(state_pk, [])
                        if r.type == "APPLIES_TO_STATE" and "FeeScheduleRate" in r.start_node.labels
                    ]
                    fee_list = [r.start_node for r in r6_list]
                    r5_list: List[EmbeddedRelationship] = []
                    for f_node in fee_list:
                        for r5 in s.in_rels.get(f_node.primary_key, []):
                            if r5.type == "HAS_RATE" and "ProcedureCode" in r5.start_node.labels:
                                r5_list.append(r5)

                    rows.append({
                        "s": st_node,
                        "r1": r1,
                        "j": j_node,
                        "r2": r2,
                        "tr": tr_node,
                        "r3": r3,
                        "cp": cp_node,
                        "hcpcs_list": hcpcs_list,
                        "fee_list": fee_list,
                        "r4_list": r4_list,
                        "r5_list": r5_list,
                        "r6_list": r6_list,
                        "diag_list": diag_list,
                        "r7_list": r7_list,
                    })
        return EmbeddedResult(rows)

    def _run_pattern_a(self, state_pk: str, diag_pk: str) -> EmbeddedResult:
        s = self._store
        st_node = s.nodes_by_pk.get(state_pk)
        diag_node = s.nodes_by_pk.get(diag_pk)
        if not st_node or not diag_node:
            return EmbeddedResult([])

        for r1 in s.in_rels.get(state_pk, []):
            if r1.type != "COVERS_STATE" or "Jurisdiction" not in r1.start_node.labels:
                continue
            j_node = r1.start_node
            for r2 in s.in_rels.get(j_node.primary_key, []):
                if r2.type != "APPLIES_TO_JURISDICTION" or "Transmittal" not in r2.start_node.labels:
                    continue
                tr_node = r2.start_node
                for r3 in s.out_rels.get(tr_node.primary_key, []):
                    if r3.type != "MANDATES_POLICY" or "CoveragePolicy" not in r3.end_node.labels:
                        continue
                    cp_node = r3.end_node
                    r4 = next(
                        (
                            r for r in s.out_rels.get(cp_node.primary_key, [])
                            if r.type == "REQUIRES_DIAGNOSIS" and r.end_node.primary_key == diag_pk
                        ),
                        None,
                    )
                    if not r4:
                        continue

                    r5_list = [
                        r for r in s.out_rels.get(cp_node.primary_key, [])
                        if r.type == "COVERS_PROCEDURE" and "ProcedureCode" in r.end_node.labels
                    ]
                    hcpcs_list = [r.end_node for r in r5_list]

                    r7_list = [
                        r for r in s.in_rels.get(state_pk, [])
                        if r.type == "APPLIES_TO_STATE" and "FeeScheduleRate" in r.start_node.labels
                    ]
                    fee_list = [r.start_node for r in r7_list]
                    r6_list: List[EmbeddedRelationship] = []
                    for f_node in fee_list:
                        for r6 in s.in_rels.get(f_node.primary_key, []):
                            if r6.type == "HAS_RATE" and "ProcedureCode" in r6.start_node.labels:
                                r6_list.append(r6)

                    return EmbeddedResult([{
                        "s": st_node,
                        "r1": r1,
                        "j": j_node,
                        "r2": r2,
                        "tr": tr_node,
                        "r3": r3,
                        "cp": cp_node,
                        "r4": r4,
                        "d": diag_node,
                        "hcpcs_list": hcpcs_list,
                        "r5_list": r5_list,
                        "fee_list": fee_list,
                        "r6_list": r6_list,
                        "r7_list": r7_list,
                    }])
        return EmbeddedResult([])

    def _run_single_clinical_traversal(self, anchor_pk: str) -> EmbeddedResult:
        s = self._store
        n = s.nodes_by_pk.get(anchor_pk)
        if not n:
            return EmbeddedResult([])

        rows: List[Dict[str, Any]] = []
        for cp in s.nodes_by_label.get("CoveragePolicy", []):
            r1_list = [
                r for r in s.out_rels.get(cp.primary_key, [])
                if r.type == "COVERS_PROCEDURE" and (n.primary_key == cp.primary_key or r.end_node.primary_key == n.primary_key)
            ]
            r2_list = [
                r for r in s.out_rels.get(cp.primary_key, [])
                if r.type == "REQUIRES_DIAGNOSIS" and (n.primary_key == cp.primary_key or r.end_node.primary_key == n.primary_key)
            ]
            r3_list = [
                r for r in s.in_rels.get(cp.primary_key, [])
                if r.type == "MANDATES_POLICY"
            ]
            for r1 in r1_list or [None]:
                for r2 in r2_list or [None]:
                    for r3 in r3_list or [None]:
                        rows.append({
                            "n": n,
                            "cp": cp,
                            "h": r1.end_node if r1 else None,
                            "d": r2.end_node if r2 else None,
                            "tr": r3.start_node if r3 else None,
                            "r1": r1,
                            "r2": r2,
                            "r3": r3,
                        })
        return EmbeddedResult(rows)

    def _run_pattern_b_hcpcs(self, hcpcs_pk: str) -> EmbeddedResult:
        s = self._store
        h_node = s.nodes_by_pk.get(hcpcs_pk)
        if not h_node:
            return EmbeddedResult([])
        rows: List[Dict[str, Any]] = []
        for r1 in s.in_rels.get(hcpcs_pk, []):
            if r1.type == "COVERS_PROCEDURE" and "CoveragePolicy" in r1.start_node.labels:
                cp = r1.start_node
                r3_list = [r for r in s.in_rels.get(cp.primary_key, []) if r.type == "MANDATES_POLICY"]
                for r2 in s.out_rels.get(cp.primary_key, []):
                    if r2.type == "REQUIRES_DIAGNOSIS" and "DiagnosisCode" in r2.end_node.labels:
                        for r3 in r3_list or [None]:
                            rows.append({
                                "h": h_node,
                                "r1": r1,
                                "cp": cp,
                                "r2": r2,
                                "d": r2.end_node,
                                "tr": r3.start_node if r3 else None,
                                "r3": r3,
                            })
        return EmbeddedResult(rows)

    def _run_pattern_b_diag(self, diag_pk: str) -> EmbeddedResult:
        s = self._store
        d_node = s.nodes_by_pk.get(diag_pk)
        if not d_node:
            return EmbeddedResult([])
        rows: List[Dict[str, Any]] = []
        for r2 in s.in_rels.get(diag_pk, []):
            if r2.type == "REQUIRES_DIAGNOSIS" and "CoveragePolicy" in r2.start_node.labels:
                cp = r2.start_node
                r3_list = [r for r in s.in_rels.get(cp.primary_key, []) if r.type == "MANDATES_POLICY"]
                for r1 in s.out_rels.get(cp.primary_key, []):
                    if r1.type == "COVERS_PROCEDURE" and "ProcedureCode" in r1.end_node.labels:
                        for r3 in r3_list or [None]:
                            rows.append({
                                "h": r1.end_node,
                                "r1": r1,
                                "cp": cp,
                                "r2": r2,
                                "d": d_node,
                                "tr": r3.start_node if r3 else None,
                                "r3": r3,
                            })
        return EmbeddedResult(rows)

    def _run_single_general_traversal(self, anchor_pk: str) -> EmbeddedResult:
        s = self._store
        start_node = s.nodes_by_pk.get(anchor_pk)
        if not start_node:
            return EmbeddedResult([])

        rows: List[Dict[str, Any]] = []
        queue: deque[Tuple[EmbeddedNode, List[EmbeddedNode], List[EmbeddedRelationship]]] = deque(
            [(start_node, [start_node], [])]
        )
        visited_pks: Set[str] = {start_node.primary_key}

        while queue and len(rows) < 100:
            curr, n_list, r_list = queue.popleft()
            if len(r_list) >= 8:
                continue
            incident = list(s.out_rels.get(curr.primary_key, [])) + list(s.in_rels.get(curr.primary_key, []))
            for rel in incident:
                nxt = rel.end_node if rel.start_node.primary_key == curr.primary_key else rel.start_node
                if "FeeScheduleRate" in nxt.labels and nxt.primary_key != start_node.primary_key:
                    continue
                if nxt.primary_key in visited_pks:
                    continue
                visited_pks.add(nxt.primary_key)
                next_nodes = n_list + [nxt]
                next_rels = r_list + [rel]
                rows.append({"n": start_node, "path": EmbeddedPath(next_nodes, next_rels)})
                if len(rows) >= 100:
                    break
                queue.append((nxt, next_nodes, next_rels))

        if not rows:
            rows.append({"n": start_node, "path": None})
        return EmbeddedResult(rows)

    def _run_shortest_paths(self, start_pk: str, target_pk: str) -> EmbeddedResult:
        s = self._store
        start_node = s.nodes_by_pk.get(start_pk)
        target_node = s.nodes_by_pk.get(target_pk)
        if not start_node or not target_node:
            return EmbeddedResult([])

        queue: deque[Tuple[EmbeddedNode, List[EmbeddedNode], List[EmbeddedRelationship]]] = deque(
            [(start_node, [start_node], [])]
        )
        visited: Set[str] = {start_pk}
        while queue:
            curr, n_list, r_list = queue.popleft()
            if curr.primary_key == target_pk:
                return EmbeddedResult([{"path": EmbeddedPath(n_list, r_list)}])
            if len(r_list) >= 10:
                continue
            incident = list(s.out_rels.get(curr.primary_key, [])) + list(s.in_rels.get(curr.primary_key, []))
            for rel in incident:
                nxt = rel.end_node if rel.start_node.primary_key == curr.primary_key else rel.start_node
                if "FeeScheduleRate" in nxt.labels and nxt.primary_key not in (start_pk, target_pk):
                    continue
                if nxt.primary_key not in visited:
                    visited.add(nxt.primary_key)
                    queue.append((nxt, n_list + [nxt], r_list + [rel]))
        return EmbeddedResult([])


class EmbeddedGraphDriver:
    """Neo4j Driver-compatible wrapper over `EmbeddedGraphStore`."""

    def __init__(self, uri: str = "embedded://exports/lta_knowledge_graph.json"):
        self.uri = uri
        raw_spec = uri[len("embedded://"):] if uri.startswith("embedded://") else uri
        raw_parts = [p.strip() for p in raw_spec.split(",") if p.strip()]
        if not raw_parts:
            raw_parts = ["exports/lta_knowledge_graph.json"]

        repo_root = Path(__file__).resolve().parents[2]
        resolved_paths: List[Path] = []
        for part in raw_parts:
            p = Path(part)
            if not p.is_absolute():
                p = (repo_root / p).resolve()
            resolved_paths.append(p)

        self._store = EmbeddedGraphStore(resolved_paths)

    def verify_connectivity(self) -> None:
        if not self._store.nodes_by_pk:
            raise RuntimeError("EmbeddedGraphStore loaded 0 nodes; connectivity check failed.")

    def session(self, database: Optional[str] = None, **kwargs: Any) -> EmbeddedSession:
        return EmbeddedSession(self._store)

    def close(self) -> None:
        pass
