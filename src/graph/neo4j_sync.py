"""
Neo4j Property Graph Synchronization Engine.

Enables continuous synchronization of multi-tier policy knowledge graphs
(e.g., LTA, IVIG) into Neo4j using idempotent MERGE semantics, strictly adhering
to system invariants and enabling rich interactive graph visualization.
"""

from __future__ import annotations
import json
import os
import sys
import time
from typing import Any, Dict, List, Optional, Tuple
from neo4j import GraphDatabase, Driver


DEFAULT_NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
DEFAULT_NEO4J_USER = os.getenv("NEO4J_USERNAME", "neo4j")
DEFAULT_NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "qwertyui")
DEFAULT_NEO4J_DATABASE = os.getenv("NEO4J_DATABASE", "neo4j")


CANONICAL_ENTITY_LABELS: List[str] = [
    "Policy",
    "Bill",
    "PublicLaw",
    "StatutorySection",
    "USCSection",
    "Regulation",
    "CFRSection",
    "Transmittal",
    "CoveragePolicy",
    "DiagnosisCode",
    "ProcedureCode",
    "FeeScheduleRate",
    "Jurisdiction",
    "State",
    "LobbyingFiling",
    "CBOScore",
    "LiteratureStudy",
]

CANONICAL_REL_TYPES: List[str] = [
    "DISCOVERED_BILL",
    "INCORPORATED_INTO",
    "ENACTED_AS",
    "CONTAINS",
    "AMENDS",
    "AUTHORIZED_BY",
    "CODIFIED_IN",
    "IMPLEMENTED_BY",
    "MANDATES_POLICY",
    "REQUIRES_DIAGNOSIS",
    "COVERS_PROCEDURE",
    "HAS_RATE",
    "APPLIES_TO_STATE",
    "APPLIES_TO_JURISDICTION",
    "COVERS_STATE",
    "HAS_ADVOCACY_RECORD",
    "HAS_BUDGET_IMPACT",
    "SUPPORTED_BY_EVIDENCE",
]

LEGACY_ENTITY_LABELS: List[str] = [
    "ChangeRequest",
    "HCPCSCode",
    "ICD10Code",
    "FeeScheduleEntry",
]


class Neo4jSyncEngine:
    """Synchronizes DirectedPropertyGraph instances or JSON exports into Neo4j."""

    ENTITY_LABELS = CANONICAL_ENTITY_LABELS
    RELATIONSHIP_TYPES = CANONICAL_REL_TYPES

    def __init__(
        self,
        uri: str = DEFAULT_NEO4J_URI,
        username: str = DEFAULT_NEO4J_USER,
        password: str = DEFAULT_NEO4J_PASSWORD,
        database: str = DEFAULT_NEO4J_DATABASE,
    ):
        self.uri = uri
        self.username = username
        self.password = password
        self.database = database
        self._driver: Optional[Driver] = None

    def get_driver(self) -> Driver:
        """Lazily initializes and returns the Neo4j driver."""
        if self._driver is None:
            self._driver = GraphDatabase.driver(self.uri, auth=(self.username, self.password))
            self._driver.verify_connectivity()
        return self._driver

    def close(self) -> None:
        """Closes driver connection."""
        if self._driver is not None:
            self._driver.close()
            self._driver = None

    def init_schema(self) -> None:
        """Creates uniqueness constraints across PolicyNode and all 17 canonical entity labels."""
        driver = self.get_driver()
        with driver.session(database=self.database) as session:
            # Drop standalone non-constraint RANGE indexes on primary_key that would collide with uniqueness constraints
            idx_rows = session.run("SHOW INDEXES").data()
            for row in idx_rows:
                idx_name = row.get("name")
                owning_constraint = row.get("owningConstraint")
                entity_type = row.get("entityType")
                props = row.get("properties") or []
                labels_or_types = row.get("labelsOrTypes") or []
                if (
                    idx_name
                    and owning_constraint is None
                    and entity_type == "NODE"
                    and ("primary_key" in props or any(l in LEGACY_ENTITY_LABELS for l in labels_or_types))
                ):
                    session.run(f"DROP INDEX `{idx_name}` IF EXISTS")

            # Drop legacy constraints on obsolete labels or non-PolicyNode labels
            const_rows = session.run("SHOW CONSTRAINTS").data()
            valid_constraint_labels = set(CANONICAL_ENTITY_LABELS) | {"PolicyNode"}
            for row in const_rows:
                cname = row.get("name")
                labels_or_types = row.get("labelsOrTypes") or []
                if cname and any(l not in valid_constraint_labels for l in labels_or_types):
                    session.run(f"DROP CONSTRAINT `{cname}` IF EXISTS")

            # Primary uniqueness constraint across all policy entities
            session.run(
                "CREATE CONSTRAINT policy_node_pk IF NOT EXISTS "
                "FOR (n:PolicyNode) REQUIRE n.primary_key IS UNIQUE"
            )
            # Uniqueness constraints for all 17 canonical entity labels
            for lbl in CANONICAL_ENTITY_LABELS:
                cname = f"constraint_{lbl.lower()}_pk"
                session.run(
                    f"CREATE CONSTRAINT {cname} IF NOT EXISTS "
                    f"FOR (n:{lbl}) REQUIRE n.primary_key IS UNIQUE"
                )

    def purge_graph(self) -> None:
        """Removes all nodes and relationships from the database."""
        driver = self.get_driver()
        with driver.session(database=self.database) as session:
            session.run("MATCH (n) DETACH DELETE n")

    def sync_graph(
        self,
        graph: Any,
        batch_size: int = 500,
        prune_stale: bool = True,
        purge_stale: Optional[bool] = None,
    ) -> Dict[str, Any]:
        """Idempotently syncs a DirectedPropertyGraph instance or dict into Neo4j."""
        graph_dict = graph.to_dict() if hasattr(graph, "to_dict") else graph
        return self.sync_graph_dict(
            graph_dict,
            batch_size=batch_size,
            prune_stale=prune_stale,
            purge_stale=purge_stale,
        )

    def sync_graph_dict(
        self,
        graph_dict: Dict[str, Any],
        batch_size: int = 500,
        prune_stale: bool = True,
        purge_stale: Optional[bool] = None,
    ) -> Dict[str, Any]:
        """Idempotently syncs a graph dictionary into Neo4j."""
        should_prune = purge_stale if purge_stale is not None else prune_stale
        driver = self.get_driver()

        nodes = graph_dict.get("nodes", [])
        edges = graph_dict.get("edges", [])

        # Prepare node records
        node_records: List[Dict[str, Any]] = []
        active_pks: List[str] = []
        for n in nodes:
            pk = n["primary_key"]
            lbl = n.get("label", "PolicyNode")
            props = {k: v for k, v in n.items() if k not in ("primary_key", "label")}
            props["primary_key"] = pk
            node_records.append({
                "label": lbl,
                "primary_key": pk,
                "props": props,
            })
            active_pks.append(pk)

        # Prepare edge records
        edge_records: List[Dict[str, Any]] = []
        active_edge_keys: List[str] = []
        for e in edges:
            spk = e["source_pk"]
            tpk = e["target_pk"]
            lbl = e["label"]
            prov = e.get("provenance", {})
            props: Dict[str, Any] = {}
            if isinstance(prov, dict):
                for k, v in prov.items():
                    props[k] = v
            for k, v in e.items():
                if k not in ("source_pk", "target_pk", "label", "provenance"):
                    props[k] = v
            edge_key = f"{spk}->{lbl}->{tpk}"
            active_edge_keys.append(edge_key)
            edge_records.append({
                "source_pk": spk,
                "target_pk": tpk,
                "label": lbl,
                "props": props,
            })

        start_time = time.time()
        nodes_synced = 0
        edges_synced = 0

        with driver.session(database=self.database) as session:
            if should_prune:
                # Remove non-PolicyNode stray nodes and stale PolicyNodes not in active_pks
                session.run("MATCH (n) WHERE NOT n:PolicyNode DETACH DELETE n")
                session.run(
                    "MATCH (n:PolicyNode) WHERE NOT n.primary_key IN $active_pks DETACH DELETE n",
                    active_pks=active_pks,
                )
                # Remove any PolicyNode carrying legacy labels or mismatched secondary label
                for i in range(0, len(node_records), batch_size):
                    batch = node_records[i : i + batch_size]
                    session.run(
                        """
                        UNWIND $batch AS item
                        MATCH (n:PolicyNode {primary_key: item.primary_key})
                        WHERE NOT item.label IN labels(n) OR size(labels(n)) > 2
                        DETACH DELETE n
                        """,
                        batch=batch,
                    )

        self.init_schema()

        with driver.session(database=self.database) as session:
            # 1. Sync nodes in batches
            node_query = """
            UNWIND $batch AS item
            CALL apoc.merge.node(['PolicyNode', item.label], {primary_key: item.primary_key}, item.props, item.props) YIELD node
            RETURN count(node) AS count
            """
            for i in range(0, len(node_records), batch_size):
                batch = node_records[i : i + batch_size]
                res = session.run(node_query, batch=batch).single()
                nodes_synced += res["count"] if res else len(batch)

            if should_prune:
                # Delete any relationship with non-canonical type or not in active_edge_keys
                session.run(
                    "MATCH ()-[r]->() WHERE NOT type(r) IN $valid_types DELETE r",
                    valid_types=CANONICAL_REL_TYPES,
                )
                session.run(
                    """
                    MATCH (s:PolicyNode)-[r]->(t:PolicyNode)
                    WHERE NOT (s.primary_key + '->' + type(r) + '->' + t.primary_key) IN $active_edge_keys
                    DELETE r
                    """,
                    active_edge_keys=active_edge_keys,
                )
                # Explicitly purge any obsolete shortcut ENACTED_AS edge when an omnibus bill intervened
                session.run(
                    """
                    MATCH (b:Bill)-[:INCORPORATED_INTO]->(:Bill)
                    MATCH (b)-[r:ENACTED_AS]->(:PublicLaw)
                    DELETE r
                    """
                )

            # 2. Sync edges in batches
            edge_query = """
            UNWIND $batch AS edge
            MATCH (s:PolicyNode {primary_key: edge.source_pk})
            MATCH (t:PolicyNode {primary_key: edge.target_pk})
            CALL apoc.merge.relationship(s, edge.label, {}, edge.props, t, edge.props) YIELD rel
            RETURN count(rel) AS count
            """
            for i in range(0, len(edge_records), batch_size):
                batch = edge_records[i : i + batch_size]
                res = session.run(edge_query, batch=batch).single()
                edges_synced += res["count"] if res else len(batch)

        elapsed = time.time() - start_time
        return {
            "nodes_expected": len(nodes),
            "nodes_synced": nodes_synced,
            "edges_expected": len(edges),
            "edges_synced": edges_synced,
            "duration_seconds": round(elapsed, 3),
        }

    def sync_file(
        self,
        json_path: str,
        batch_size: int = 500,
        prune_stale: bool = True,
        purge_stale: Optional[bool] = None,
    ) -> Dict[str, Any]:
        """Loads a JSON file and syncs it into Neo4j."""
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return self.sync_graph_dict(
            data,
            batch_size=batch_size,
            prune_stale=prune_stale,
            purge_stale=purge_stale,
        )

    def get_summary_statistics(self) -> Dict[str, Any]:
        """Queries current node and relationship counts by label and type."""
        driver = self.get_driver()
        with driver.session(database=self.database) as session:
            node_counts = session.run(
                "MATCH (n:PolicyNode) RETURN labels(n) AS labels, count(n) AS count ORDER BY count DESC"
            ).data()
            edge_counts = session.run(
                "MATCH (:PolicyNode)-[r]->(:PolicyNode) RETURN type(r) AS rel_type, count(r) AS count ORDER BY count DESC"
            ).data()
            total_nodes = session.run("MATCH (n:PolicyNode) RETURN count(n) AS total").single()["total"]
            total_edges = session.run("MATCH (:PolicyNode)-[r]->(:PolicyNode) RETURN count(r) AS total").single()["total"]
            return {
                "total_nodes": total_nodes,
                "total_edges": total_edges,
                "nodes_by_label": node_counts,
                "edges_by_type": edge_counts,
            }


if __name__ == "__main__":
    files = sys.argv[1:] if len(sys.argv) > 1 else [
        "exports/lta_knowledge_graph.json",
    ]
    engine = Neo4jSyncEngine()
    try:
        print(f"Connecting to Neo4j at {engine.uri}...")
        for filepath in files:
            print(f"\n--- Syncing {filepath} ---")
            stats = engine.sync_file(filepath)
            print(f"Synced {stats['nodes_synced']} nodes and {stats['edges_synced']} edges in {stats['duration_seconds']}s")

        print("\n=== Neo4j Graph Summary Statistics ===")
        summary = engine.get_summary_statistics()
        print(f"Total PolicyNode count: {summary['total_nodes']}")
        print(f"Total Relationship count: {summary['total_edges']}")
        print("\nTop Node Labels:")
        for row in summary["nodes_by_label"]:
            print(f"  {row['labels']}: {row['count']}")
        print("\nTop Relationship Types:")
        for row in summary["edges_by_type"]:
            print(f"  {row['rel_type']}: {row['count']}")
    finally:
        engine.close()
