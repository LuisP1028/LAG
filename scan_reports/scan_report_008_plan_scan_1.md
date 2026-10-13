# Wayfinder Deterministic Codebase Static Scan, External API Reconnaissance & Empirical Schema Audit Report (`plan-scan-1`)

**Run ID:** `20261013T185957-734-5ytd`  
**Node Role:** `plan-scan-1` (Agent 1)  
**Upstream Seed Specification:** `functional_specification_008.md`  
**Glossary Reference:** `LANGUAGE.md`  

---

## 1. Governing Context

### 1.1 Upstream Functional Specification Consumed
- **Seed Specification File:** `functional_specification_008.md` (*Functional Specification: Dual Jurisdiction and State Governance Architecture*).
- **Core `{functionality}` Required:**
  1. Cleanly separate and synchronize **CMS DME MAC Regional Jurisdictions** (`JURIS-DME-A`, `JURIS-DME-B`, `JURIS-DME-C`, `JURIS-DME-D`) and **Individual Geographic States** (all 50 US states plus DC and territories) across the UI navigation controls, backend topology filtering API (`/api/graph/topology`), and 5-stage GraphRAG pipeline (`/api/graphrag/query`, `/api/graphrag/subgraph`, `/api/entities/resolve`).
  2. Provide two distinct, clearly labeled selectors in the top toolbar: **`JURISDICTION:`** (options: `All Jurisdictions (National Overview)`, `Jurisdiction A (Northeast - Noridian)`, `Jurisdiction B (Midwest - CGS)`, `Jurisdiction C (South - CGS)`, `Jurisdiction D (West - Noridian)`) and **`STATE:`** (options: `All States (Overview)` plus all 50 US States, DC, and territories in alphabetical order), with bidirectional cascading synchronization.
  3. Support independent and combined `jurisdiction_filter` and `state_filter` query parameters on `GET /api/graph/topology`, collapsing `FeeScheduleEntry` nodes at the national and regional macro levels (for 60 FPS canvas performance) while expanding localized non-rural `FeeScheduleEntry` nodes when a specific state is selected.
  4. Enable the GraphRAG pipeline to natively resolve, traverse, assemble context for, and synthesize grounded answers for regional administrative queries (e.g., *"What states does Jurisdiction B cover?"*, *"What policies does CGS administer?"*, *"Who administers Medicare Part B DME claims in Texas?"*) and cross-jurisdiction multi-state comparisons (e.g., *"Compare allowable rates for A6522 between California and New York."*).

### 1.2 Wayfinder Decision Tickets Inspected
- **Wayfinder Run Directory:** `wayfinder/20261013T185957-734-5ytd/`
- **Tickets Inspected:** None (`wayfinder/20261013T185957-734-5ytd/map.md` and `wayfinder/20261013T185957-734-5ytd/tickets/` do not exist prior to initial planning scan).

### 1.3 Taxonomy Alignment (`LANGUAGE.md`)
All assessments in this report strictly bind to the definitions in `LANGUAGE.md`:
- **`{errors}`**: Explicit failure states surfaced during execution (unhandled exceptions, missing fee schedules, disconnected nodes, incorrect contractor-to-state mapping, speculative schemas, or violation of `INV-BOUNDARY-01`).
- **`{correctness}`**: Precise local execution where every state maps strictly to its legally assigned DME MAC contractor, fee schedules load accurate dollar amounts, and regional jurisdiction filters display all constituent states.
- **`{functionality}`**: Seamless exploration of policy data at both the macro regional level (Jurisdictions A, B, C, D) and micro geographic level (all 50 individual States + territories) across the visual canvas and GraphRAG intelligence terminal.
- **`{correct required outputs}`**: Objectively measurable deliverables produced by this scan (Master Component Dependency Cone Register, Candidate External Datasource & Schema Audit Register, 9 raw empirical payloads in `assets/20261013T185957-734-5ytd/`, Explicit Deficiency Register, and atomic handoff manifest `handoff/20261013T185957-734-5ytd/plan-scan-1.txt`).
- **`{sufficient}`**: Zero ambiguity across all dependency cone interfaces, empirical schemas, and deficiency records.
- **`{insufficient}`**: Any scan relying on sampling, ranking, or unverified assumptions.

---

## 2. Master Component Dependency Cone Register

Every codebase component below was statically verified in the local workspace and touches the dependency cone of `functional_specification_008.md`:

### 2.1 Frontend UI, State Synchronization & Visualization Components

1. **`src/frontend/src/components/FilterToolbar.tsx`**
   - **Verbatim Symbols & Interfaces:**
     - `interface FilterToolbarProps { onReloadTopology: (state: string, policy: string) => void; }`
     - `export const FilterToolbar: React.FC<FilterToolbarProps>`
     - `handleStateChange(e: React.ChangeEvent<HTMLSelectElement>): void`
     - `handlePolicyChange(e: React.ChangeEvent<HTMLSelectElement>): void`
   - **Grounding Justification:** Renders the top-right navigation bar. Currently renders a single dropdown labeled `JURISDICTION:` bound to `filterState` with only 5 hardcoded state options (`WI`, `IL`, `CA`, `NY`, `TX`) plus `""` (`All States (Fees Collapsed - 60 FPS)`). Directly touched by Requirements 5.1.1 and 5.1.2.

2. **`src/frontend/src/context/GraphSyncContext.tsx`**
   - **Verbatim Symbols & Interfaces:**
     - `export interface ChatMessage { id: string; sender: 'user' | 'assistant'; text: string; responsePayload?: GraphRAGQueryResponse; timestamp: string; }`
     - `interface GraphSyncContextType` (`activeNodePKs: Set<string>`, `activeEdgeKeys: Set<string>`, `selectedNode: GraphNode | null`, `seededAnchor: AnchorEntity | null`, `isIlluminated: boolean`, `quickPrompts: string[]`, `filterState: string`, `policyKeyword: string`, `isChatOpen: boolean`, `messages: ChatMessage[]`, `isQueryLoading: boolean`, `errorMsg: string | null`, `focusTarget: { x: number; y: number; zoom?: number } | null`, `selectNode`, `setIlluminatedPath`, `clearIllumination`, `setFilterState`, `setPolicyKeyword`, `setIsChatOpen`, `setFocusTarget`, `submitInquiry`, `inquireNode`)
     - `export const GraphSyncProvider: React.FC<{ children: React.ReactNode }>`
     - `export const useGraphSync: () => GraphSyncContextType`
   - **Grounding Justification:** Central React state bus synchronizing toolbar filters, canvas illumination (`activeNodePKs`, `activeEdgeKeys`), contextual quick prompts (`selectNode`), and GraphRAG chat queries (`submitInquiry`). Currently tracks `filterState` (default `"WI"`) but lacks `filterJurisdiction` state and cascading synchronization between Jurisdiction and State selectors.

3. **`src/frontend/src/App.tsx`**
   - **Verbatim Symbols & Interfaces:**
     - `const MainVisualizer: React.FC`
     - `fetchTopology(stateFilter = 'WI', policy = 'LTA'): Promise<void>`
     - `export default function App()`
   - **Grounding Justification:** Owns the `nodes` and `links` state arrays and queries `GET /api/graph/topology`. Currently constructs `URLSearchParams` with only `state_filter` and `policy_keyword`, lacking `jurisdiction_filter` support.

4. **`src/frontend/src/components/GraphCanvas.tsx`**
   - **Verbatim Symbols & Interfaces:**
     - `interface GraphCanvasProps { nodes: GraphNode[]; links: GraphLink[]; loading: boolean; }`
     - `export const GraphCanvas: React.FC<GraphCanvasProps>`
     - `frameActiveSubgraph(targetPKs: Set<string>): void`
     - `render(): void`
   - **Grounding Justification:** HTML5 Canvas D3 force-directed graph renderer (`d3.forceSimulation`) with halftone blueprint shading, orbital rings around `Policy`, `PublicLaw`, and `Jurisdiction` hubs, and active subgraph camera framing (`frameActiveSubgraph`). Consumes `activeNodePKs`, `activeEdgeKeys`, and `isIlluminated` from `useGraphSync()`.

5. **`src/frontend/src/components/NodeDetailDrawer.tsx`**
   - **Verbatim Symbols & Interfaces:**
     - `interface NodeDetailDrawerProps { nodes: GraphNode[]; links: GraphLink[]; }`
     - `export const NodeDetailDrawer: React.FC<NodeDetailDrawerProps>`
     - `getGovernmentSourceLink(): { title: string; url: string } | null`
   - **Grounding Justification:** Displays entity attributes, connected incoming/outgoing neighbors (`COVERS_STATE`, `APPLIES_TO_JURISDICTION`, `APPLIES_TO`, `HAS_FEE_SCHEDULE`), government source links (CGS Portal for Jurisdiction B/C, Noridian Portal for Jurisdiction A/D), and triggers `inquireNode(selectedNode)`.

6. **`src/frontend/src/components/AgentChatDrawer.tsx`**
   - **Verbatim Symbols & Interfaces:**
     - `export const AgentChatDrawer: React.FC`
     - `handleSend(queryText?: string): Promise<void>`
   - **Grounding Justification:** Interactive GraphRAG terminal drawer displaying quick prompts, model selector (`meta-llama/Meta-Llama-3-8B-Instruct`, `mistralai/Mistral-7B-Instruct-v0.3`, `Qwen/Qwen2.5-7B-Instruct`), synthesized answers, latency telemetry (`duration_ms`), and illuminated node count (`active_node_pks.length`).

7. **`src/frontend/src/utils/promptGenerator.ts`**
   - **Verbatim Symbols & Interfaces:**
     - `export const constructInquiryPrompt: (node: GraphNode) => string`
   - **Grounding Justification:** Generates deterministic one-click inquiry prompts for `Jurisdiction` (`"What states and coverage policies are administered by [${pk}] (${name})?"`), `State` (`"What Medicare contractor, coverage policies, and allowable fee schedules apply to [${pk}] (${name})?"`), and all other node labels.

8. **`src/frontend/src/types/graph.ts`**
   - **Verbatim Symbols & Interfaces:**
     - `export interface NodeProperties` (`primary_key: string`, `name?: string`, `title?: string`, `state_code?: string`, `state_name?: string`, `code?: string`, `description?: string`, `fee_amount?: number`, `is_rural?: boolean`, `transmittal_number?: string`, `benefit_category?: string`, `contractor_name?: string`, `states?: string`, `source_url?: string`)
     - `export interface EdgeProvenance`
     - `export interface GraphNode`
     - `export interface GraphLink`
     - `export interface AnchorEntity`
     - `export interface GraphRAGQueryResponse`
     - `export interface GraphSummary`
   - **Grounding Justification:** TypeScript data contracts for frontend graph nodes, edges, anchors, and GraphRAG responses.

9. **`src/frontend/src/styles/graph_theme.ts`**
   - **Verbatim Symbols & Interfaces:**
     - `export interface NodeVisualConfig`
     - `export const NODE_THEME_REGISTRY: Record<string, NodeVisualConfig>`
     - `export const CANVAS_PALETTE`
     - `export function getNodeVisual(label: string): NodeVisualConfig`
   - **Grounding Justification:** Defines visual styling for `Jurisdiction` (`#16a34a`, radius `13`, `rounded_square`), `State` (`#64748b`, radius `9`, `circle`), `FeeScheduleEntry` (`#eab308`, radius `6`, `dot`), and all other entity labels.

### 2.2 Backend FastAPI REST Layer Components

10. **`src/api/routes.py`**
    - **Verbatim Symbols & Interfaces:**
      - `router = APIRouter(prefix="/api")`
      - `set_sync_engine(engine: Neo4jSyncEngine) -> None`
      - `get_sync_engine() -> Neo4jSyncEngine`
      - `get_pipeline() -> GraphRAGPipeline`
      - `get_neo4j_session()`
      - `health_check(session: Session = Depends(get_neo4j_session)) -> HealthResponse` (`GET /api/health`)
      - `get_graph_summary() -> Dict[str, Any]` (`GET /api/graph/summary`)
      - `get_graph_topology(policy_keyword: Optional[str] = Query("LTA"), include_fee_schedules: bool = Query(False), state_filter: Optional[str] = Query(None), session: Session = Depends(get_neo4j_session)) -> TopologyResponse` (`GET /api/graph/topology`)
      - `resolve_entities(req: EntityResolveRequest, session: Session = Depends(get_neo4j_session)) -> EntityResolveResponse` (`POST /api/entities/resolve`)
      - `get_subgraph_by_anchors(req: SubgraphRequest, session: Session = Depends(get_neo4j_session)) -> SubgraphResponse` (`POST /api/graphrag/subgraph`)
      - `execute_graphrag_query(req: GraphRAGQueryRequest, session: Session = Depends(get_neo4j_session)) -> GraphRAGQueryResponse` (`POST /api/graphrag/query`)
    - **Grounding Justification:** Implements `GET /api/graph/topology` and the GraphRAG REST endpoints. Directly touched by Requirement 5.2.1 (`jurisdiction_filter` and `state_filter` multi-tier topology filtering).

11. **`src/api/models.py`**
    - **Verbatim Symbols & Interfaces:**
      - `class HealthResponse(BaseModel)`
      - `class TopologyNode(BaseModel)` (`primary_key: str`, `label: str`, `name: str`, `properties: Dict[str, Any]`)
      - `class TopologyEdge(BaseModel)` (`source_pk: str`, `target_pk: str`, `label: str`, `edge_key: str`, `provenance: Dict[str, Any]`)
      - `class TopologyResponse(BaseModel)` (`nodes: List[TopologyNode]`, `edges: List[TopologyEdge]`, `total_nodes: int`, `total_edges: int`)
      - `class EntityResolveRequest(BaseModel)` (`query: str`)
      - `class EntityResolveResponse(BaseModel)` (`anchors: List[AnchorEntity]`)
      - `class SubgraphRequest(BaseModel)` (`anchors: List[str]`)
      - `class SubgraphResponse(BaseModel)` (`nodes: List[TopologyNode]`, `edges: List[TopologyEdge]`, `active_node_pks: List[str]`, `active_edge_keys: List[str]`, `retrieval_ms: float`)
      - `class ErrorEnvelope(BaseModel)`
    - **Grounding Justification:** Pydantic response/request schemas for the REST API endpoints.

12. **`src/api/server.py`**
    - **Verbatim Symbols & Interfaces:**
      - `lifespan(app: FastAPI)`
      - `create_app() -> FastAPI`
      - `app = create_app()`
      - `http_exception_handler(request: Request, exc: HTTPException)`
      - `graphrag_exception_handler(request: Request, exc: GraphRAGException)`
    - **Grounding Justification:** FastAPI application factory, Neo4j lifespan connection manager, and standardized JSON error envelope handlers.

### 2.3 GraphRAG Retrieval, Traversal, Context Assembly & Synthesis Components

13. **`src/graphrag/entity_linker.py`**
    - **Verbatim Symbols & Interfaces:**
      - `class EntityAnchorLinker`
      - `STATE_NAME_TO_CODE: Dict[str, str]` (53 states/territories mapped to 2-letter postal codes)
      - `CLINICAL_SYNONYMS`, `POLICY_TRIGGERS`, `HCPCS_REGEX`, `GEO_LOCATION_INDICATORS`, `PK_TOKEN_REGEX`
      - `resolve_anchors(self, query_text: str, session: Session) -> ResolvedAnchors`
      - `resolve_explicit_anchor(self, primary_key: str, session: Session) -> ResolvedAnchors`
      - `_extract_jurisdiction_anchors(self, text: str, session: Session) -> List[AnchorEntity]`
      - `_extract_change_request_anchors(self, text: str, session: Session) -> List[AnchorEntity]`
      - `_extract_coverage_policy_anchors(self, text: str, session: Session) -> List[AnchorEntity]`
      - `_extract_legislative_anchors(self, text: str, session: Session) -> List[AnchorEntity]`
      - `_extract_state_anchor(self, text: str, session: Session) -> Optional[AnchorEntity]`
      - `_extract_diagnosis_anchor(self, text: str, session: Session) -> Optional[AnchorEntity]`
      - `_extract_policy_anchors(self, text: str, session: Session) -> List[AnchorEntity]`
      - `_extract_hcpcs_anchors(self, text: str, session: Session) -> List[AnchorEntity]`
    - **Grounding Justification:** Stage 1 of the GraphRAG pipeline. Directly touched by Requirements 5.3.1 and 5.3.2 because `_extract_state_anchor` currently returns only a single `Optional[AnchorEntity]` (failing to extract the second state in multi-state comparisons like *"between California and New York"*), and `_extract_jurisdiction_anchors` maps `"cgs"` only to `JURIS-DME-B` and `"noridian"` only to `JURIS-DME-A`.

14. **`src/graphrag/traversal.py`**
    - **Verbatim Symbols & Interfaces:**
      - `class TopologicalTraversalEngine`
      - `extract_connecting_subgraph(self, anchors: ResolvedAnchors, session: Session, max_hops: int = 3) -> TraversalResult`
      - `_execute_single_entity_traversal(self, anchor: AnchorEntity, session: Session, ...)`
      - `_execute_single_state_traversal(self, state_pk: str, session: Session, ...)`
      - `_execute_single_clinical_traversal(self, anchor_pk: str, session: Session, ...)`
      - `_execute_single_general_traversal(self, anchor_pk: str, session: Session, ...)`
      - `_execute_multi_entity_traversal(self, anchors: ResolvedAnchors, session: Session, ...)`
      - `_execute_pattern_a(self, anchors: ResolvedAnchors, session: Session, ...)`
      - `_execute_pattern_b(self, anchors: ResolvedAnchors, session: Session, ...)`
      - `_execute_pattern_c(self, anchors: ResolvedAnchors, session: Session, ...)`
      - `_convert_node(self, node: Any) -> TraversalNode`
      - `_convert_edge(self, rel: Any, src_pk: Optional[str] = None, tgt_pk: Optional[str] = None) -> TraversalEdge`
    - **Grounding Justification:** Stage 2 of the GraphRAG pipeline. Directly touched by Requirements 5.3.1 and 5.3.2 (regional jurisdiction lineage expansion, edge type preservation, and multi-state / state+HCPCS cross-jurisdiction comparison traversal).

15. **`src/graphrag/context_assembler.py`**
    - **Verbatim Symbols & Interfaces:**
      - `class GraphContextAssembler`
      - `assemble_context(self, traversal_result: TraversalResult, state_code: Optional[str] = None) -> str`
    - **Grounding Justification:** Stage 3 of the GraphRAG pipeline. Formats retrieved nodes and edges into 5 sections (`1. Program & Legal Authority`, `2. Contractor & Region`, `3. Clinical Criteria`, `4. Fees and Patient Costs`, `5. Data Sources & Provenance`). Directly touched by Requirements 5.3.1 and 5.3.2 because Section 4 currently drops additional `A6522` fee nodes across multiple states (`if h_code != "A6522"`).

16. **`src/graphrag/synthesizer.py`**
    - **Verbatim Symbols & Interfaces:**
      - `class HuggingFaceSynthesizer`
      - `DEFAULT_MODEL = "meta-llama/Llama-3.1-8B-Instruct"`
      - `ROUTER_CHAT_URL = "https://router.huggingface.co/v1/chat/completions"`
      - `MODEL_ALIASES: Dict[str, str]`
      - `SYSTEM_PROMPT: str`
      - `synthesize(self, query: str, context: str, model_id: Optional[str] = None) -> str`
      - `_call_hf_inference_api(self, query: str, context: str, model_id: str) -> str`
    - **Grounding Justification:** Stages 4 & 5 of the GraphRAG pipeline. Invokes the Hugging Face Router Chat Completions endpoint to synthesize grounded responses. Directly touched by Requirement 5.3.1 and Acceptance Criterion 6 (ensuring regional/state contractor responses cite both the contractor and governing Change Request / transmittal IDs).

17. **`src/graphrag/pipeline.py`**
    - **Verbatim Symbols & Interfaces:**
      - `class GraphRAGPipeline`
      - `execute_query(self, request: GraphRAGQueryRequest, session: Session) -> GraphRAGQueryResponse`
    - **Grounding Justification:** Orchestrates `EntityAnchorLinker`, `TopologicalTraversalEngine`, `GraphContextAssembler`, and `HuggingFaceSynthesizer`.

18. **`src/graphrag/models.py`**
    - **Verbatim Symbols & Interfaces:**
      - `class AnchorEntity(BaseModel)`
      - `class ResolvedAnchors(BaseModel)` (`all_anchors`, `state_anchor`, `diagnosis_anchor`, `policy_anchor`, `hcpcs_anchor`, `jurisdiction_anchor`, `change_request_anchor`, `coverage_policy_anchor`)
      - `class TraversalNode(BaseModel)`
      - `class TraversalEdge(BaseModel)`
      - `class TraversalResult(BaseModel)`
      - `class GraphRAGQueryRequest(BaseModel)` (`query: str`, `model_id: Optional[str]`, `state_code: Optional[str]`, `primary_key: Optional[str]`, `anchor_node_pk: Optional[str]`)
      - `class GraphRAGQueryResponse(BaseModel)` (`answer: str`, `active_node_pks: List[str]`, `active_edge_keys: List[str]`, `anchors: List[AnchorEntity]`, `provenance_sources: List[Dict[str, Any]]`, `duration_ms: float`)
    - **Grounding Justification:** Pydantic data contracts for GraphRAG anchor resolution, traversal, and query execution.

19. **`src/graphrag/exceptions.py`**
    - **Verbatim Symbols & Interfaces:**
      - `class GraphRAGException(Exception)`
      - `class EntityResolutionError(GraphRAGException)`
      - `class TraversalError(GraphRAGException)`
      - `class ModelInferenceError(GraphRAGException)`
      - `class ModelAuthenticationError(ModelInferenceError)`
      - `class ModelRateLimitError(ModelInferenceError)`
      - `class GraphValidationError(GraphRAGException)`
    - **Grounding Justification:** Fail-fast exception hierarchy for the GraphRAG pipeline.

### 2.4 Knowledge Graph Ingestion, Domain Models & Neo4j Sync Components

20. **`src/graph/tier4b_fee_schedule.py`**
    - **Verbatim Symbols & Interfaces:**
      - `class Phase4FeeScheduleDatasetError(Exception)`
      - `class Phase4IncompleteJurisdictionError(Exception)`
      - `DME_MAC_JURISDICTIONS: Dict[str, Tuple[str, List[Tuple[str, str]]]]`
      - `normalize_fee_schedules(handoff: Tier3Handoff, change_request_node: ChangeRequestNode, hcpcs_nodes: List[HCPCSCodeNode], run_id: str, asset_dir: Optional[str] = None) -> Tuple[List[JurisdictionNode], List[StateNode], List[FeeScheduleEntryNode], List[GraphEdge]]`
    - **Grounding Justification:** Defines the authoritative `DME_MAC_JURISDICTIONS` mapping (`JURIS-DME-A`, `JURIS-DME-B`, `JURIS-DME-C`, `JURIS-DME-D` -> `StateNode` via `COVERS_STATE`) and unpivots the 53-jurisdiction CMS DMEPOS fee schedule CSV into `FeeScheduleEntryNode` records.

21. **`src/graph/tier4a_coverage.py`**
    - **Verbatim Symbols & Interfaces:**
      - `STANDARD_COVERED_DIAGNOSES`, `STANDARD_COVERED_HCPCS`
      - `ingest_coverage_policy(handoff: Tier3Handoff, change_request_node: ChangeRequestNode, run_id: str, asset_dir: Optional[str] = None) -> Tuple[CoveragePolicyNode, List[HCPCSCodeNode], List[ICD10CodeNode], List[GraphEdge]]`
    - **Grounding Justification:** Constructs `CoveragePolicyNode` (`CMS-MCD-A59508`, `CMS-MCD-A59588`), `HCPCSCodeNode`, and `ICD10CodeNode` bridged via `MANDATES_POLICY`, `GOVERNS`, and `ALLOWS_DIAGNOSIS`.

22. **`src/graph/models.py`**
    - **Verbatim Symbols & Interfaces:**
      - `EdgeProvenance`, `GraphEdge`, `BaseNode`, `PolicyNode`, `BillNode`, `PublicLawNode`, `StatutorySectionNode`, `RegulationNode`, `ChangeRequestNode`, `CoveragePolicyNode`, `JurisdictionNode`, `StateNode`, `FeeScheduleEntryNode`, `HCPCSCodeNode`, `ICD10CodeNode`, `LobbyingFilingNode`, `CBOScoreNode`, `LiteratureStudyNode`, `Tier1Handoff`, `Tier2Handoff`, `Tier3Handoff`
    - **Grounding Justification:** Defines deterministic composite primary keys (`JURIS-DME-{code}`, `STATE-{state_code}`, `FEE-{hcpcs}-{state}-{R|NR}-{year}`, `HCPCS-{code}`, `CMS-CR-{cr_number}`, `CMS-MCD-{article_id}`).

23. **`src/graph/engine.py`**
    - **Verbatim Symbols & Interfaces:**
      - `class GraphValidationError(Exception)`
      - `class DirectedPropertyGraph` (`upsert_node`, `upsert_edge`, `to_dict`, `export_json`)
      - `class PropertyGraphEngine` (`run_pipeline`, `validate_invariants`)
    - **Grounding Justification:** Enforces `INV-50-STATE-COMPLETENESS` (4 `JurisdictionNode` instances, 53–56 `StateNode` instances, >0 `FeeScheduleEntryNode` instances) and `INV-UNBROKEN-ANCESTRY`.

24. **`src/graph/neo4j_sync.py`**
    - **Verbatim Symbols & Interfaces:**
      - `class Neo4jSyncEngine` (`get_driver`, `close`, `init_schema`, `sync_graph_dict`, `sync_file`, `get_summary_statistics`)
    - **Grounding Justification:** Synchronizes property graphs into Neo4j (`bolt://localhost:7687`) with uniqueness constraints on `PolicyNode.primary_key` and per-label indexes (`Jurisdiction`, `State`, `FeeScheduleEntry`, etc.).

### 2.5 Verification & Test Suites

25. **`tests/test_api_endpoints.py`**
    - **Verbatim Symbols:** `test_api_health`, `test_api_graph_summary`, `test_api_graph_topology`, `test_api_entities_resolve`, `test_api_graphrag_subgraph`, `test_api_graphrag_query`, `test_api_single_state_and_subgraph`, `test_api_graphrag_query_explicit_anchor_plaw`, `test_api_graphrag_query_all_14_entity_types`, `test_api_graphrag_query_invalid_anchor_fails_fast`.
    - **Grounding Justification:** Integration test suite verifying `/api/graph/topology`, `/api/entities/resolve`, `/api/graphrag/subgraph`, and `/api/graphrag/query`.

26. **`tests/test_graph_pipeline.py`**
    - **Verbatim Symbols:** `test_root_policy_anchor`, `test_statutory_and_regulatory_lineage`, `test_coverage_policy_bridge`, `test_direct_hcpcs_to_icd10_prohibition_raises_error`, `test_50_state_and_jurisdiction_completeness`, `test_edge_provenance_completeness`, `test_unbroken_ancestry_invariant`, `test_idempotent_upserts`, `test_ivig_pipeline_execution_and_invariants`, `test_neo4j_sync_and_mcp_invariants`.
    - **Grounding Justification:** Pipeline invariant verification suite testing `JurisdictionNode`, `StateNode`, and `FeeScheduleEntryNode` generation and Neo4j synchronization.

27. **`tests/test_graphrag_pipeline.py`**
    - **Verbatim Symbols:** `test_oracle_1_patient_benefit_routing`, `test_oracle_2_no_keyword_bridging`, `test_oracle_3_cross_policy_convergence`, `test_oracle_4_zero_orphan_invariant`, `test_oracle_5_edge_provenance_completeness`, `test_oracle_6_fail_fast_error_boundaries`, `test_single_state_query_ny`, `test_latency_benchmark_harness`, `test_single_entity_general_traversal_integrity`.
    - **Grounding Justification:** GraphRAG verification suite validating anchor extraction, traversal subgraphs, context assembly, and LLM synthesis.

---

## 3. Candidate External Datasource & Empirical Schema Audit Register

All candidate external datasources and services were actively probed using read-only operations (`neo4j-cypher` MCP tools, Python `neo4j` driver read sessions, FastAPI `TestClient` GET/read queries, and Hugging Face Router API inference). Unedited ground-truth responses are saved in `assets/20261013T185957-734-5ytd/`.

### 3.1 Neo4j Property Graph Database (`bolt://localhost:7687` / MCP `neo4j-cypher`)
- **Endpoint / URI:** `bolt://localhost:7687` (Database: `neo4j`)
- **Authentication:** `NEO4J_URI`, `NEO4J_USERNAME` (`neo4j`), `NEO4J_PASSWORD` from `.env`.
- **Reachability & Status:** Live, reachable, verified via `get_neo4j_schema` and `read_neo4j_cypher`.
- **Empirical Counts:**
  - `total_nodes`: `3971` (`FeeScheduleEntry`: `3816`, `HCPCSCode`: `75`, `State`: `53`, `ICD10Code`: `6`, `Jurisdiction`: `4`, `Bill`: `3`, `Policy`: `2`, `StatutorySection`: `2`, `ChangeRequest`: `2`, `CoveragePolicy`: `2`, `LobbyingFiling`: `2`, `LiteratureStudy`: `2`, `PublicLaw`: `1`, `Regulation`: `1`).
  - `total_edges`: `7795` (`HAS_FEE_SCHEDULE`: `3816`, `APPLIES_TO`: `3816`, `GOVERNS`: `75`, `COVERS_STATE`: `53`, `APPLIES_TO_JURISDICTION`: `8`, `ALLOWS_DIAGNOSIS`: `6`, `TARGETS_BILL`: `4`, `HAS_ADVOCACY_RECORD`: `4`, `ENACTED_AS`: `3`, `MODIFIES_CODE`: `2`, `IMPLEMENTED_BY`: `2`, `ISSUES_TRANSMITTAL`: `2`, `SUPPORTED_BY_EVIDENCE`: `2`, `MANDATES_POLICY`: `2`).
- **Audited Node & Relationship Schemas in Neo4j:**
  - **`Jurisdiction` (`:PolicyNode:Jurisdiction`, count = 4):**
    - `primary_key` (`STRING`, indexed, non-null): `"JURIS-DME-A"`, `"JURIS-DME-B"`, `"JURIS-DME-C"`, `"JURIS-DME-D"`.
    - `code` (`STRING`, non-null): `"JURIS-DME-A"`, `"JURIS-DME-B"`, `"JURIS-DME-C"`, `"JURIS-DME-D"`.
    - `name` (`STRING`, nullable — present from JSON export sync): `"JURIS-DME-A (Noridian)"`, `"JURIS-DME-B (CGS)"`, `"JURIS-DME-C (CGS)"`, `"JURIS-DME-D (Noridian)"`.
    - `contractor_name` (`STRING`, non-null): `"Noridian Healthcare Solutions"` (A & D), `"CGS Administrators"` (B & C).
    - Outgoing relationships: `(:Jurisdiction)-[:COVERS_STATE]->(:State)` (53 edges total: 12 for A, 7 for B, 17 for C, 17 for D).
    - Incoming relationships: `(:ChangeRequest)-[:APPLIES_TO_JURISDICTION]->(:Jurisdiction)` (8 edges total: `CMS-CR-13286` and `CMS-CR-13217` each connect to all 4 jurisdictions).
  - **`State` (`:PolicyNode:State`, count = 53):**
    - `primary_key` (`STRING`, indexed, non-null): `"STATE-AL"` through `"STATE-WY"`, plus `"STATE-DC"`, `"STATE-PR"`, `"STATE-VI"`.
    - `state_code` (`STRING`, non-null): 2-letter uppercase postal code (e.g., `"WI"`, `"OH"`, `"NY"`, `"CA"`, `"TX"`).
    - `state_name` (`STRING`, non-null): Full state/territory name (e.g., `"Wisconsin"`, `"Ohio"`, `"New York"`, `"California"`, `"Texas"`).
    - Incoming relationships: `(:Jurisdiction)-[:COVERS_STATE]->(:State)` and `(:FeeScheduleEntry)-[:APPLIES_TO]->(:State)`.
  - **`FeeScheduleEntry` (`:PolicyNode:FeeScheduleEntry`, count = 3816):**
    - `primary_key` (`STRING`, indexed, non-null): `"FEE-{HCPCS}-{STATE}-{NR|R}-2024"` (e.g., `"FEE-A6522-CA-NR-2024"`, `"FEE-A6522-NY-NR-2024"`).
    - `hcpcs_code` (`STRING`, non-null): e.g., `"A6522"`, `"Q2052"`.
    - `state_code` (`STRING`, non-null): e.g., `"CA"`, `"NY"`, `"OH"`, `"WI"`.
    - `is_rural` (`BOOLEAN`, non-null): `false` or `true`.
    - `fee_amount` (`FLOAT`, non-null): e.g., `290.47` for `A6522`, `409.84` for `Q2052`.
    - `ceiling` (`FLOAT`, non-null), `floor` (`FLOAT`, non-null), `year` (`INTEGER`, non-null: `2024`), `name` (`STRING`, nullable).
- **Captured Ground-Truth Payload Files:**
  - `assets/20261013T185957-734-5ytd/neo4j_schema_summary.json`
  - `assets/20261013T185957-734-5ytd/neo4j_jurisdictions_states_mapping.json`
  - `assets/20261013T185957-734-5ytd/neo4j_cross_jurisdiction_a6522_ca_ny.json`

### 3.2 CMS DMEPOS Fee Schedule Dataset (`stage4b_cms_dmepos_lc_category.csv`)
- **Dataset Path:** `CoveragePolicies_and_Jurisdictions Addition/assets/20261012T231057-024-zqga/stage4b_cms_dmepos_lc_category.csv`
- **Audited Schema:**
  - `114` columns total:
    - Metadata columns (7): `HCPCS` (`STRING`), `Mod` (`STRING`, nullable/empty), `Mod2` (`STRING`, nullable/empty), `JURIS` (`STRING`), `CATG` (`STRING`: `"LC"`), `Ceiling` (`FLOAT` string), `Floor` (`FLOAT` string).
    - Geographic rate columns (106): 53 pairs of `<STATE> (NR)` and `<STATE> (R)` covering all 50 US states plus `DC`, `PR`, and `VI` (note: Pacific territories `AS`, `GU`, and `MP` do not have rate columns in the CMS DMEPOS CSV).
    - Trailing column (1): `Description` (`STRING`).
  - `70` rows with `CATG == "LC"`.
- **Captured Ground-Truth Payload File:**
  - `assets/20261013T185957-734-5ytd/cms_dmepos_lc_headers_and_a6522_row.json`

### 3.3 FastAPI Topology & GraphRAG Endpoints (`/api/graph/topology`, `/api/graphrag/query`)
- **Probed Endpoints:**
  1. `GET /api/graph/topology` (National overview, HTTP 200 OK): returns `TopologyResponse` (`nodes`: `155`, `edges`: `163`, `total_nodes`: `155`, `total_edges`: `163`).
  2. `GET /api/graph/topology?state_filter=OH` (State-filtered probe, HTTP 200 OK): returns `TopologyResponse` (`nodes`: `227`, `edges`: `307`, `total_nodes`: `227`, `total_edges`: `307`).
  3. `GET /api/graph/topology?jurisdiction_filter=JURIS-DME-B` (Jurisdiction-filtered probe, HTTP 200 OK): returns `TopologyResponse` (`nodes`: `155`, `edges`: `163`, `total_nodes`: `155`, `total_edges`: `163` — `jurisdiction_filter` is currently unimplemented and ignored).
  4. `POST /api/graphrag/query` (GraphRAG + Hugging Face Router API `https://router.huggingface.co/v1/chat/completions`, HTTP 200 OK): returns `GraphRAGQueryResponse` (`answer: str`, `active_node_pks: List[str]`, `active_edge_keys: List[str]`, `anchors: List[AnchorEntity]`, `provenance_sources: List[Dict[str, Any]]`, `duration_ms: float`).
- **Captured Ground-Truth Payload Files:**
  - `assets/20261013T185957-734-5ytd/api_topology_national_sample.json`
  - `assets/20261013T185957-734-5ytd/api_topology_state_oh_sample.json`
  - `assets/20261013T185957-734-5ytd/api_topology_jurisdiction_b_probe.json`
  - `assets/20261013T185957-734-5ytd/api_graphrag_jurisdiction_b_query.json`
  - `assets/20261013T185957-734-5ytd/api_graphrag_state_tx_query.json`

---

## 4. Explicit Deficiency Register

In accordance with `INV-ABSENCE-01`, the following specced behaviors in `functional_specification_008.md` are currently missing or defective in the codebase:

### Deficiency 1: Conflated Single Dropdown & Missing Dedicated `JURISDICTION:` and `STATE:` Selectors (`Requirement 5.1.1`, `Requirement 5.1.2`, `Acceptance Criteria 1, 2, 3, 4`)
- **Affected Components:** `src/frontend/src/components/FilterToolbar.tsx`, `src/frontend/src/context/GraphSyncContext.tsx`, `src/frontend/src/App.tsx`
- **Empirical Finding:**
  1. `FilterToolbar.tsx` (lines 58–80) renders only a single `<select>` labeled `JURISDICTION:` that actually sets `filterState` and lists only 5 states (`WI`, `IL`, `CA`, `NY`, `TX`) plus `""` (`All States (Fees Collapsed - 60 FPS)`). The remaining 45 US states, DC, and territories cannot be selected.
  2. There is no dedicated `JURISDICTION:` selector offering `All Jurisdictions (National Overview)`, `Jurisdiction A (Northeast - Noridian)` (`JURIS-DME-A`), `Jurisdiction B (Midwest - CGS)` (`JURIS-DME-B`), `Jurisdiction C (South - CGS)` (`JURIS-DME-C`), and `Jurisdiction D (West - Noridian)` (`JURIS-DME-D`).
  3. There is no dedicated `STATE:` selector offering `All States (Overview)` and an alphabetical list of all 50 US states (plus DC and territories).
  4. `GraphSyncContext.tsx` lacks `filterJurisdiction` / `setFilterJurisdiction` state and lacks cascading synchronization rules:
     - Selecting a Jurisdiction (`JURIS-DME-A/B/C/D`) does not dynamically filter the `STATE:` selector to only states assigned to that jurisdiction, nor does it highlight the regional contractor node (`JURIS-DME-*`) and its covered states (`COVERS_STATE`) on the canvas.
     - Selecting a State does not automatically update the `JURISDICTION:` selector to reflect the parent regional jurisdiction covering that state.

### Deficiency 2: Missing `jurisdiction_filter` & Unfiltered Subgraph in `GET /api/graph/topology` (`Requirement 5.2.1`, `Acceptance Criteria 2, 3, 4, 5`)
- **Affected Components:** `src/api/routes.py` (`get_graph_topology`), `src/frontend/src/App.tsx` (`fetchTopology`)
- **Empirical Finding:**
  1. `get_graph_topology` (`src/api/routes.py`, lines 84–90) does not accept a `jurisdiction_filter` query parameter (`Optional[str] = Query(None, ...)`). As verified in `assets/20261013T185957-734-5ytd/api_topology_jurisdiction_b_probe.json`, passing `?jurisdiction_filter=JURIS-DME-B` is ignored and returns all 4 jurisdictions and all 53 states (`155` nodes, `163` edges).
  2. When `jurisdiction_filter` is specified (e.g., `JURIS-DME-B` or `B`), the endpoint must filter the regional/geographic tier to return the root policy/legislative/regulatory/change-request/coverage-policy lineage, the targeted regional contractor node (`JURIS-DME-B`), and only the states covered by that contractor via `COVERS_STATE` (with `FeeScheduleEntry` nodes collapsed unless `state_filter` or `include_fee_schedules=True` is also provided).
  3. When `state_filter` is specified (e.g., `OH` or `NY`), `get_graph_topology` currently still executes the unfiltered `base_query` returning all 53 states and all 4 jurisdictions, and its `fee_query` (`src/api/routes.py`, lines 189–193) omits `WHERE f.is_rural = false OR f.is_rural IS NULL`, returning rural fee schedule nodes alongside non-rural nodes instead of restricting to localized non-rural fee schedule entries (`Requirement 5.2.1.3`) and scoping the geographic subgraph to the selected state and its parent regional contractor.
  4. In `get_graph_topology`, the `policy_keyword` parameter (`LTA`, `IVIG`, or `ALL`) is accepted in the function signature but never applied to filter the topology.

### Deficiency 3: Multi-State Anchor Extraction Failure in `EntityAnchorLinker` (`Requirement 5.3.2`)
- **Affected Components:** `src/graphrag/entity_linker.py` (`_extract_state_anchor`, `resolve_anchors`), `src/graphrag/models.py` (`ResolvedAnchors`)
- **Empirical Finding:**
  1. `EntityAnchorLinker._extract_state_anchor` (`src/graphrag/entity_linker.py`, lines 351–388) returns `Optional[AnchorEntity]` and terminates on the first matched state (`return AnchorEntity(...)` at line 365).
  2. For comparative cross-jurisdiction queries such as *"Compare allowable rates for A6522 between California and New York."*, `_extract_state_anchor` returns only `STATE-CA` and drops `STATE-NY`.
  3. Additionally, `_extract_jurisdiction_anchors` (`src/graphrag/entity_linker.py`, lines 231–255) maps `"cgs"` only to `JURIS-DME-B` (omitting `JURIS-DME-C`, which is also CGS Administrators) and `"noridian"` only to `JURIS-DME-A` (omitting `JURIS-DME-D`, which is also Noridian Healthcare Solutions), and does not match `"DME MAC A/B/C/D"` phrasing when `Jurisdiction` is not written out.

### Deficiency 4: Multi-Entity / Cross-Jurisdiction Traversal Crash & Regional Jurisdiction Lineage Gap in `TopologicalTraversalEngine` (`Requirement 5.3.1`, `Requirement 5.3.2`, `Acceptance Criterion 6`)
- **Affected Components:** `src/graphrag/traversal.py` (`_execute_multi_entity_traversal`, `_execute_single_entity_traversal`, `_execute_single_general_traversal`)
- **Empirical Finding:**
  1. **Unhandled `AttributeError` in `_execute_multi_entity_traversal` (line 366):** When a query anchors to `State` + `HCPCSCode` (or multiple `State` anchors + `HCPCSCode`, e.g., `STATE-CA`, `STATE-NY`, `HCPCS-A6522`), execution falls through to step 4 (`allShortestPaths`), which calls `session.run(...).data()`. Because `.data()` converts Neo4j `Path` objects into Python lists, `for n in path.nodes:` raises `AttributeError: 'list' object has no attribute 'nodes'`.
  2. **Missing Cross-Jurisdiction / Multi-State + HCPCS Traversal Pattern:** `TopologicalTraversalEngine` lacks a dedicated traversal branch for `State(s) + HCPCSCode` (and multi-state comparisons) that retrieves each anchored `State`, its parent `Jurisdiction` (`COVERS_STATE`), governing `ChangeRequest` (`APPLIES_TO_JURISDICTION`), `CoveragePolicy` (`MANDATES_POLICY`), `HCPCSCode` (`GOVERNS`), and the state-specific non-rural `FeeScheduleEntry` (`HAS_FEE_SCHEDULE` / `APPLIES_TO`) for each anchored state.
  3. **Incomplete Regional Jurisdiction Lineage & Broken Edge Keys in `_execute_single_general_traversal` (lines 262–302):**
     - When querying a `Jurisdiction` anchor (e.g., *"What states does Jurisdiction B cover?"*, *"What policies does CGS administer?"*, *"What is Jurisdiction B?"*), `_execute_single_entity_traversal` delegates to `_execute_single_general_traversal`.
     - Because `_execute_single_general_traversal` uses `.data()`, `r` is serialized as a tuple without `.type` or `.items()`, causing `_convert_edge` to emit `"RELATED_TO"` (`JURIS-DME-B->RELATED_TO->STATE-IL`) instead of the actual relationship label (`JURIS-DME-B->COVERS_STATE->STATE-IL`) and losing edge provenance (`verified://federal-statute` fallback).
     - Furthermore, `_execute_single_general_traversal` only traverses 1 hop from `Jurisdiction` (reaching `State` and `ChangeRequest`), omitting the 2-hop `CoveragePolicy` (`(cr:ChangeRequest)-[:MANDATES_POLICY]->(cp:CoveragePolicy)`) and `Regulation` (`(reg:Regulation)-[:ISSUES_TRANSMITTAL]->(cr)`).

### Deficiency 5: Multi-State Fee Dropping in `GraphContextAssembler` & Contractor/Transmittal Citation Guidance in `HuggingFaceSynthesizer` (`Requirement 5.3.1`, `Requirement 5.3.2`, `Acceptance Criterion 6`)
- **Affected Components:** `src/graphrag/context_assembler.py` (`assemble_context`), `src/graphrag/synthesizer.py` (`SYSTEM_PROMPT`, `_call_hf_inference_api`), `src/graphrag/pipeline.py` (`execute_query`)
- **Empirical Finding:**
  1. In `GraphContextAssembler.assemble_context` (`src/graphrag/context_assembler.py`, lines 141–160), Section 4 (`Fees and Patient Costs`) selects only the first `A6522` fee via `next((f for f in candidate_fees if f.properties.get("hcpcs_code") == "A6522"), None)` and then explicitly skips all other `A6522` fee entries in the loop (`if h_code != "A6522" and count < 6:`), dropping the second state's `A6522` rate during cross-state comparisons and omitting state identifiers on fee lines when multiple states are present.
  2. In `HuggingFaceSynthesizer` (`src/graphrag/synthesizer.py`, lines 30–39, 68–74), the prompt does not explicitly require citing the governing operational `ChangeRequest` (`[CMS-CR-13286]` / transmittal `12349`) and `CoveragePolicy` (`[CMS-MCD-A59508]`) when answering administrative contractor or state jurisdiction inquiries (as observed in `assets/20261013T185957-734-5ytd/api_graphrag_state_tx_query.json`, where the LLM named `[JURIS-DME-C]` and `CGS Administrators` but omitted `[CMS-CR-13286]` and transmittal `12349`).

### Deficiency 6: Territorial Jurisdiction Coverage & Contractor Name Alignment (`Section 4`, `Requirement 5.1.2`)
- **Affected Components:** `src/graph/tier4b_fee_schedule.py` (`DME_MAC_JURISDICTIONS`), `src/graph/engine.py` (`validate_invariants`), `src/graphrag/entity_linker.py` (`STATE_NAME_TO_CODE`)
- **Empirical Finding:**
  1. Section 4 of `functional_specification_008.md` specifies 20 jurisdictions under `JURIS-DME-D` (17 states plus `American Samoa` (`AS`), `Guam` (`GU`), and `Northern Mariana Islands` (`MP`), totaling 56 jurisdictions across A=12, B=7, C=17, D=20) and lists `"CGS Administrators, LLC"` as the contractor name for Jurisdictions B and C.
  2. Currently, `DME_MAC_JURISDICTIONS["D"]` in `src/graph/tier4b_fee_schedule.py` lists 17 states (omitting `AS`, `GU`, `MP`), `engine.py` line 218 checks `if len(states) not in (53, 54):`, and `STATE_NAME_TO_CODE` in `src/graphrag/entity_linker.py` has 53 entries (omitting `american samoa`, `guam`, `northern mariana islands`). Note that the CMS DMEPOS CSV (`stage4b_cms_dmepos_lc_category.csv`) has rate columns for 53 jurisdictions (50 US states + `DC`, `PR`, `VI`).

---

## 5. Sufficiency & Scan Certification

- **Dependency Cone Completeness:** Every codebase component across `src/frontend/`, `src/api/`, `src/graphrag/`, `src/graph/`, and `tests/` whose interface touches `functional_specification_008.md` has been deterministically scanned and cataloged using verbatim identifiers (`INV-SCAN-01`, `INV-IDENTITY-01`).
- **Empirical Datasource Grounding:** All external datasources and APIs (Neo4j `bolt://localhost:7687`, CMS DMEPOS CSV dataset, FastAPI REST endpoints, and Hugging Face Router API `https://router.huggingface.co/v1/chat/completions`) have been probed using non-mutating read-only requests, with 9 raw ground-truth payload samples saved in `assets/20261013T185957-734-5ytd/` (`INV-PAYLOAD-CAPTURE-01`).
- **Sufficiency Status:** `{sufficient}` for downstream ticket generation and planning.

---

## 6. Handoff Manifest Affirmation

The role handoff manifest at `handoff/20261013T185957-734-5ytd/plan-scan-1.txt` has been atomically overwritten with one repository-relative path per line covering all qualified codebase component files, this scan report (`scan_reports/scan_report_008_plan_scan_1.md`), and all 9 captured ground-truth payload files in `assets/20261013T185957-734-5ytd/`. Seed paths and other run directories were not touched (`INV-MANIFEST-OVERWRITE-01`, `INV-HANDOFF-01`).

---

## 7. Coding Gate Affirmation

**DO NOT CODE YET: Implementation coding gate remains locked. Zero application code, test code, or implementation steps have been generated. Coding waits on an empty frontier and explicit operator authorization.**
