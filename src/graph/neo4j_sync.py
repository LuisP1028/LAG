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


class Neo4jSyncEngine:
    """Synchronizes DirectedPropertyGraph instances or JSON exports into Neo4j."""

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
        """Creates uniqueness constraints and performance indexes."""
        driver = self.get_driver()
        with driver.session(database=self.database) as session:
            # Primary uniqueness constraint across all policy entities
            session.run(
                "CREATE CONSTRAINT policy_node_pk IF NOT EXISTS "
                "FOR (n:PolicyNode) REQUIRE n.primary_key IS UNIQUE"
            )
            # Create secondary label indexes for fast label-specific matching
            labels = [
                "Policy",
                "Bill",
                "PublicLaw",
                "StatutorySection",
                "Regulation",
                "ChangeRequest",
                "CoveragePolicy",
                "HCPCSCode",
                "ICD10Code",
                "Jurisdiction",
                "State",
                "FeeScheduleEntry",
                "LobbyingFiling",
                "LiteratureStudy",
                "CBOScore",
            ]
            for lbl in labels:
                idx_name = f"idx_{lbl.lower()}_pk"
                session.run(
                    f"CREATE INDEX {idx_name} IF NOT EXISTS "
                    f"FOR (n:{lbl}) ON (n.primary_key)"
                )

    def sync_graph_dict(
        self, graph_dict: Dict[str, Any], batch_size: int = 500
    ) -> Dict[str, Any]:
        """Idempotently syncs a graph dictionary into Neo4j."""
        self.init_schema()
        driver = self.get_driver()

        nodes = graph_dict.get("nodes", [])
        edges = graph_dict.get("edges", [])

        # Prepare node records
        node_records: List[Dict[str, Any]] = []
        for n in nodes:
            pk = n["primary_key"]
            lbl = n.get("label", "PolicyNode")
            props = {k: v for k, v in n.items() if k not in ("primary_key", "label")}
            # Ensure primary_key is included in props
            props["primary_key"] = pk
            node_records.append({
                "label": lbl,
                "primary_key": pk,
                "props": props,
            })

        # Prepare edge records
        edge_records: List[Dict[str, Any]] = []
        for e in edges:
            spk = e["source_pk"]
            tpk = e["target_pk"]
            lbl = e["label"]
            prov = e.get("provenance", {})
            props: Dict[str, Any] = {}
            if isinstance(prov, dict):
                for k, v in prov.items():
                    props[k] = v
            # Add any other edge properties
            for k, v in e.items():
                if k not in ("source_pk", "target_pk", "label", "provenance"):
                    props[k] = v
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
            # 1. Sync nodes in batches
            node_query = """
            UNWIND $batch AS item
            CALL apoc.merge.node(['PolicyNode', item.label], {primary_key: item.primary_key}, item.props) YIELD node
            RETURN count(node) AS count
            """
            for i in range(0, len(node_records), batch_size):
                batch = node_records[i : i + batch_size]
                res = session.run(node_query, batch=batch).single()
                nodes_synced += res["count"] if res else len(batch)

            # 2. Sync edges in batches
            edge_query = """
            UNWIND $batch AS edge
            MATCH (s:PolicyNode {primary_key: edge.source_pk})
            MATCH (t:PolicyNode {primary_key: edge.target_pk})
            CALL apoc.merge.relationship(s, edge.label, {}, edge.props, t) YIELD rel
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

    def sync_file(self, json_path: str, batch_size: int = 500) -> Dict[str, Any]:
        """Loads a JSON file and syncs it into Neo4j."""
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return self.sync_graph_dict(data, batch_size=batch_size)

    def get_summary_statistics(self) -> Dict[str, Any]:
        """Queries current node and relationship counts by label and type."""
        driver = self.get_driver()
        with driver.session(database=self.database) as session:
            node_counts = session.run(
                "MATCH (n:PolicyNode) RETURN labels(n) AS labels, count(n) AS count ORDER BY count DESC"
            ).data()
            edge_counts = session.run(
                "MATCH ()-[r]->() RETURN type(r) AS rel_type, count(r) AS count ORDER BY count DESC"
            ).data()
            total_nodes = session.run("MATCH (n:PolicyNode) RETURN count(n) AS total").single()["total"]
            total_edges = session.run("MATCH ()-[r]->() RETURN count(r) AS total").single()["total"]
            return {
                "total_nodes": total_nodes,
                "total_edges": total_edges,
                "nodes_by_label": node_counts,
                "edges_by_type": edge_counts,
            }


if __name__ == "__main__":
    files = sys.argv[1:] if len(sys.argv) > 1 else [
        "exports/ivig_knowledge_graph.json",
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
        for row in summary["nodes_by_label"][:10]:
            print(f"  {row['labels']}: {row['count']}")
        print("\nTop Relationship Types:")
        for row in summary["edges_by_type"][:10]:
            print(f"  {row['rel_type']}: {row['count']}")
    finally:
        engine.close()
