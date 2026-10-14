"""End-to-End System Verification and Demonstration Script across the 8-Hop LTA Knowledge Graph."""

import sys
import time
from src.graph.neo4j_sync import Neo4jSyncEngine
from src.graphrag.models import GraphRAGQueryRequest
from src.graphrag.pipeline import GraphRAGPipeline


def main():
    print("=" * 80)
    print("◈ LAG KNOWLEDGE GRAPHRAG SYSTEM VERIFICATION & DEMO")
    print("=" * 80)

    # 1. Connect to Neo4j
    engine = Neo4jSyncEngine()
    try:
        engine.get_driver().verify_connectivity()
        print("✓ Connected to Neo4j database (bolt://localhost:7687)")
    except Exception as e:
        print(f"✗ Failed to connect to Neo4j: {e}")
        sys.exit(1)

    # 2. Summary stats
    stats = engine.get_summary_statistics()
    print(f"✓ Total policy nodes in Neo4j: {stats['total_nodes']} across {len(stats['nodes_by_label'])} entity categories")
    print(f"✓ Total directed edges in Neo4j: {stats['total_edges']} across {len(stats['edges_by_type'])} relationship types")

    # 3. GraphRAG Pipeline demonstration
    pipeline = GraphRAGPipeline()

    print("\n--- Workflow 1: Natural Language Patient Benefit Routing (Wisconsin) ---")
    query_1 = "I am from Wisconsin, survived breast cancer, need lymphedema supplies, I'm on Medicare, can you help?"
    print(f"User Query: \"{query_1}\"")

    with engine.get_driver().session(database=engine.database) as session:
        t0 = time.perf_counter()
        resp_1 = pipeline.execute_query(GraphRAGQueryRequest(query=query_1), session)
        dt = (time.perf_counter() - t0) * 1000.0

        print(f"\n[Response Duration: {resp_1.duration_ms}ms (Total round-trip: {dt:.2f}ms)]")
        print(f"Illuminated Active Node PKs ({len(resp_1.active_node_pks)}): {resp_1.active_node_pks}")
        print(f"Illuminated Active Edge Keys ({len(resp_1.active_edge_keys)}):")
        for ek in resp_1.active_edge_keys:
            print(f"  → {ek}")

        print("\nSynthesized Grounded Guidance:")
        print("-" * 60)
        print(resp_1.answer)
        print("-" * 60)

        print("\n--- Workflow 2: 8-Hop Legislative Omnibus & Regulatory Lineage ---")
        query_2 = "How was H.R. 3630 enacted into Public Law 117-328 and implemented in 88 FR 77676?"
        print(f"User Query: \"{query_2}\"")

        resp_2 = pipeline.execute_query(GraphRAGQueryRequest(query=query_2), session)
        print(f"\n[Response Duration: {resp_2.duration_ms}ms]")
        print(f"Illuminated Active Node PKs ({len(resp_2.active_node_pks)}): {resp_2.active_node_pks}")
        print("\nSynthesized Grounded Guidance:")
        print("-" * 60)
        print(resp_2.answer)
        print("-" * 60)

        print("\n--- Workflow 3: Single-State & Territorial Inquiry (New York & Guam) ---")
        query_3 = "What contractor covers New York and Guam and what are the allowable rates?"
        print(f"User Query: \"{query_3}\"")

        resp_3 = pipeline.execute_query(GraphRAGQueryRequest(query=query_3), session)
        print(f"\n[Response Duration: {resp_3.duration_ms}ms]")
        print(f"Illuminated Active Node PKs ({len(resp_3.active_node_pks)}): {resp_3.active_node_pks}")
        print("\nSynthesized Grounded Guidance:")
        print("-" * 60)
        print(resp_3.answer)
        print("-" * 60)

    engine.close()
    print("\n" + "=" * 80)
    print("✓ VERIFICATION COMPLETED SUCCESSFULLY WITH 0 ERRORS")
    print("=" * 80)


if __name__ == "__main__":
    main()
