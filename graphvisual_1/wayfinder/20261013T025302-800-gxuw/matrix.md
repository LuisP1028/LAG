# Master Component-to-Edit Matrix: Browser-Based React Graph Visualization & Hugging Face GraphRAG Architecture

**Run ID:** `20261013T025302-800-gxuw`  
**Governing Specification:** `functional_specification_004.md`  
**Document:** `wayfinder/20261013T025302-800-gxuw/matrix.md`  
**Planning Status:** Planned & Locked  
**Taxonomy Reference:** `LANGUAGE.md`

---

## 1. System Component Overview

The React Graph Visualization and Hugging Face GraphRAG system is organized into nine discrete architectural components satisfying all requirements of `functional_specification_004.md`:

| Component ID | Component Name | Primary Role | Implementation File | Blocked By |
|---|---|---|---|---|
| `COMP-01` | Backend API Server & Lifespan Manager | FastAPI app, CORS, Neo4j connection pool lifespan, standardized error envelopes | `src/api/server.py` | None |
| `COMP-02` | REST Route Controllers | API handlers for health, topology, anchor resolution, and GraphRAG querying | `src/api/routes.py` | `COMP-01` |
| `COMP-03` | Multi-Slot Entity Anchor Linker | Resolves natural language into State, ICD10Code, and Policy anchors with clinical synonyms | `src/graphrag/entity_linker.py` | `COMP-01` |
| `COMP-04` | Generalized Topological Traversal Engine | Executes multi-hop Cypher queries in Neo4j without bespoke coding or Cypher hallucination | `src/graphrag/traversal.py` | `COMP-01`, `COMP-03` |
| `COMP-05` | Structured Context & Provenance Assembler | Serializes graph subgraphs and edge provenance into formatted Markdown blocks | `src/graphrag/context_assembler.py` | `COMP-04` |
| `COMP-06` | Hugging Face LLM Synthesis Client | Integrates Hugging Face Inference API, handles model selection, auth, and anti-hallucination | `src/graphrag/llm_client.py` | `COMP-05` |
| `COMP-07` | React Graph Visualization Canvas & Physics | Force-directed canvas, visual hierarchy, fee schedule clustering, physics controls | `src/frontend/components/GraphCanvas.tsx` | `COMP-02` |
| `COMP-08` | Detail Drawer & Synchronization Bus | Node property inspection, clickable government URLs, and bidirectional event sync | `src/frontend/components/NodeDetailDrawer.tsx` | `COMP-07` |
| `COMP-09` | Verification Oracles & Acceptance Suite | Automated pytest suite validating workflows 1–3, invariants, and latency SLAs | `tests/test_graphrag_pipeline.py` | `COMP-01`–`COMP-08` |

---

## 2. Definitive Master Component-to-Edit Matrix

| Component ID | Target File Path | Target Symbols / Functions | Input Parameters | Output Keys & Artifacts | Transformation & Parsing Logic | Fail-Fast Error Condition (`INV-FAIL-FAST`) |
|---|---|---|---|---|---|---|
| **`COMP-01`** | `src/api/server.py` | `create_app()`, `lifespan(app: FastAPI)`, `get_sync_engine()`, `get_neo4j_session()` | Environment config (`NEO4J_URI`, `NEO4J_USERNAME`, `NEO4J_PASSWORD`, `API_PORT`) | Configured `FastAPI` instance with lifecycle hooks and CORS middleware | Initializes singleton `Neo4jSyncEngine`, verifies database connectivity on startup, registers route routers, handles clean pool closure on shutdown. Maps exceptions to JSON error envelopes. | Failed Neo4j connection on startup raises `RuntimeError` immediately and halts process. |
| **`COMP-02`** | `src/api/routes.py` | `health_check()`, `get_graph_summary()`, `get_graph_topology()`, `resolve_entities()`, `get_subgraph()`, `query_graphrag()` | `Request`, `query: str`, `anchors: list[str]`, `model_id: str`, `state_filter: str` | Typed JSON response payloads matching `ticket-001.md` schemas | Dispatches incoming HTTP requests to `EntityAnchorLinker`, `TopologicalTraversalEngine`, and `HuggingFaceLLMClient`. Implements high-density node summarization toggle for fee schedules. | Invalid input payload or unhandled service exception returns structured HTTP 400/500 envelope. |
| **`COMP-03`** | `src/graphrag/entity_linker.py` | `EntityAnchorLinker`, `resolve_anchors(query_text: str, session: Session)` | `query_text: str`, `session: Session` | `ResolvedAnchors` containing `state_anchor`, `diagnosis_anchor`, `policy_anchor`, `all_anchors` | Parses unstructured text into three slots. Uses lexical matching against indexed `State` entities, clinical synonym table for `ICD10Code`, and phrase mapping for `Policy` roots. | Unrecognized geographic region or ungrounded clinical term raises `EntityResolutionError` immediately. |
| **`COMP-04`** | `src/graphrag/traversal.py` | `TopologicalTraversalEngine`, `extract_connecting_subgraph(anchors, session, max_hops)` | `anchors: ResolvedAnchors`, `session: Session`, `max_hops: int = 3` | `TraversalResult` (`nodes: list[TraversalNode]`, `edges: list[TraversalEdge]`, `active_node_pks`, `active_edge_keys`, `retrieval_ms`) | Executes parameterized Cypher traversal patterns (Pattern A: Patient Routing; Pattern B: Coverage Bridging; Pattern C: Cross-Policy Convergence). Preserves 100% edge provenance metadata. | Broken path or missing required relationship raises `TraversalError`. Any direct HCPCS->ICD10 edge violates `INV-NO-KEYWORD-BRIDGING`. |
| **`COMP-05`** | `src/graphrag/context_assembler.py` | `GraphContextAssembler`, `assemble_context(traversal_result: TraversalResult)` | `traversal_result: TraversalResult` | `AssembledContext` (`markdown_text: str`, `provenance_sources: list[dict]`, `pricing_summary: dict`) | Serializes graph nodes and relationships into 4 structured Markdown blocks: Program Authority, Clinical Eligibility, Covered Items & Allowable Fees, and Data Provenance. Calculates 20% patient coinsurance. | Empty node set or missing required provenance attributes raises `ContextAssemblyError`. |
| **`COMP-06`** | `src/graphrag/llm_client.py` | `HuggingFaceLLMClient`, `synthesize_answer(query_text: str, context: AssembledContext, model_id: Optional[str])` | `query_text: str`, `context: AssembledContext`, `model_id: Optional[str]` | `SynthesizedResponse` (`answer: str`, `model_used: str`, `duration_ms: float`, `citations: list[str]`) | Injects structured Markdown context and anti-hallucination system prompt into Hugging Face Serverless Inference API request (`POST https://api-inference.huggingface.co/models/{model_id}`). Enforces zero extrapolation. | HTTP 401 raises `ModelAuthenticationError`. HTTP 429 raises `ModelRateLimitError`. HTTP 503 surfaces model loading state. |
| **`COMP-07`** | `src/frontend/components/GraphCanvas.tsx` | `GraphCanvas`, `renderNode()`, `renderEdge()`, `handleNodeClick()`, `handlePhysicsToggle()` | `graphData: GraphData`, `activeNodePKs: Set<string>`, `activeEdgeKeys: Set<string>`, `stateFilter: string` | Interactive 2D/3D visual canvas with camera controls | Renders 14 node entity types using persistent visual styling (badge colors, radius, shapes). Renders human-readable captions. Implements fee schedule clustering (<300 nodes active). Highlights active paths in amber with 20% background dimming. | Missing required node properties or invalid geometry parameters logs visualizer error and falls back gracefully. |
| **`COMP-08`** | `src/frontend/components/NodeDetailDrawer.tsx` | `NodeDetailDrawer`, `GraphSyncContext`, `renderGovernmentLink()` | `selectedNode: GraphNode`, `adjacentEdges: list[GraphEdge]` | Flyout drawer and global React synchronization bus | Displays node primary key, title, classification, first-class properties, direct government source URLs (Congress.gov, GPO, Federal Register, CMS MCD), and clickable adjacent neighbors. Emits quick-action prompt events. | Node with missing primary key raises state validation exception. |
| **`COMP-09`** | `tests/test_graphrag_pipeline.py` | `test_patient_benefit_routing_workflow()`, `test_coverage_policy_bridge_oracle()`, `test_cross_policy_convergence_oracle()`, `test_zero_orphan_invariant()`, `test_provenance_completeness()`, `test_fail_fast_boundaries()` | Pytest harness, active Neo4j connection | Assertions verifying 100% acceptance criteria in `functional_specification_004.md` | Executes end-to-end routing queries, verifies exact fee calculation ($290.47 and $58.09), checks unbroken ancestry to root Policy, validates provenance completeness, and verifies sub-second SLAs. | Any assertion failure, orphan node, or latency exceeding SLA causes immediate test suite failure. |

---

## 3. Data Schema & Contract Alignment

### 3.1. Entity Anchor Transfer Contract (`ResolvedAnchors`)
```typescript
interface AnchorEntity {
  slot: "state" | "diagnosis" | "policy";
  primary_key: string;
  matched_text: string;
  entity_type: string;
  label: string;
}

interface ResolvedAnchors {
  state_anchor?: AnchorEntity;
  diagnosis_anchor?: AnchorEntity;
  policy_anchor?: AnchorEntity;
  all_anchors: AnchorEntity[];
}
```

### 3.2. Subgraph Traversal Response Contract (`TraversalResult`)
```typescript
interface TraversalNode {
  primary_key: string;
  label: string;
  name: string;
  properties: Record<string, any>;
}

interface TraversalEdge {
  source_pk: string;
  target_pk: string;
  label: string;
  edge_key: string;
  provenance: {
    source_uri: string;
    selector: string;
    ingestion_timestamp: string;
    run_id: string;
  };
}

interface TraversalResult {
  nodes: TraversalNode[];
  edges: TraversalEdge[];
  active_node_pks: string[];
  active_edge_keys: string[];
  retrieval_ms: number;
}
```

### 3.3. Canvas-Agent Synchronization Contract
```typescript
interface GraphRAGQueryResponse {
  answer: string;
  active_node_pks: string[];
  active_edge_keys: string[];
  anchors: AnchorEntity[];
  provenance_sources: Array<{
    source_uri: string;
    selector: string;
    ingestion_timestamp: string;
    run_id: string;
  }>;
  duration_ms: number;
}
```
