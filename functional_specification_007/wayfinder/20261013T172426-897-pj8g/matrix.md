# Master Component-to-Edit Matrix: Node Detail Contextual Inquire Action and Targeted GraphRAG Execution

**Governing Specification:** `functional_specification_007.md`  
**Run ID:** `20261013T172426-897-pj8g`  
**Planning Status:** Resolved  
**Taxonomy Reference:** `LANGUAGE.md`

---

## 1. Overview and Component Traceability

This matrix maps every functional requirement in `functional_specification_007.md` and every decision ticket in `wayfinder/20261013T172426-897-pj8g/tickets/` to the exact file paths, line ranges, symbols, and transformations required.

| Requirement ID | Requirement Summary | Governing Ticket | Target Component File | Symbols Targeted |
|---|---|---|---|---|
| **REQ-4.1** | One-Click Execution & In-Flight State | `ticket-001.md` | `src/frontend/src/components/NodeDetailDrawer.tsx` | `NodeDetailDrawer` (lines 16, 244–265) |
| **REQ-4.2** | Deterministic Entity Classification Prompts | `ticket-002.md` | `src/frontend/src/utils/promptGenerator.ts` | `constructInquiryPrompt` (New utility) |
| **REQ-4.1 / REQ-5.2** | Centralized Chat Synchronization & Turn History | `ticket-003.md` | `src/frontend/src/context/GraphSyncContext.tsx` | `ChatMessage`, `GraphSyncContextType`, `GraphSyncProvider` |
| **REQ-4.1 / REQ-5.3** | Chat Drawer Telemetry & Context Binding | `ticket-003.md` | `src/frontend/src/components/AgentChatDrawer.tsx` | `AgentChatDrawer` (lines 19–39, 43–94) |
| **REQ-4.3** | Explicit Anchor Model Extension | `ticket-004.md` | `src/graphrag/models.py` | `GraphRAGQueryRequest` (lines 58–63) |
| **REQ-4.3** | Backend Deterministic Anchor Bypass | `ticket-004.md` | `src/graphrag/entity_linker.py` | `EntityAnchorLinker.resolve_explicit_anchor` |
| **REQ-4.3** | Pipeline Direct Anchor Dispatch | `ticket-004.md` | `src/graphrag/pipeline.py` | `GraphRAGPipeline.execute_query` (lines 43–50) |
| **REQ-4.4 / REQ-6.2** | Single-Entity Cypher Traversal & Edge Keys | `ticket-005.md` | `src/graphrag/traversal.py` | `TopologicalTraversalEngine._execute_single_general_traversal` |
| **REQ-6.4** | 14 Entity Context Assembly Coverage | `ticket-005.md` | `src/graphrag/context_assembler.py` | `GraphContextAssembler.assemble_context` |
| **REQ-6.1–6.5** | Automated Test Oracles & Regression Suite | `ticket-006.md` | `tests/test_api_endpoints.py` | `test_api_graphrag_query_explicit_anchor_plaw`, `test_api_graphrag_query_all_14_entity_types` |

---

## 2. File-by-File Detailed Transformation Specifications

### 2.1. File: `src/frontend/src/utils/promptGenerator.ts` (NEW FILE)
- **Component Path:** `[promptGenerator.ts](file:///Users/diesel/Desktop/LAG/src/frontend/src/utils/promptGenerator.ts)`
- **Target Symbol:** `constructInquiryPrompt`
- **Transformation Specification:**
```typescript
import type { GraphNode } from '../types/graph';

export const constructInquiryPrompt = (node: GraphNode): string => {
  const pk = node.primary_key;
  const name = node.name || node.properties?.title || node.properties?.state_name || node.properties?.section || pk;

  switch (node.label) {
    case 'PublicLaw':
      return `Explain the statutory authority and enacted healthcare provisions of [${pk}] (${name}).`;
    case 'Bill':
      return `What is the legislative history and purpose of [${pk}] (${name})?`;
    case 'Regulation':
      return `What policies and administrative instructions are implemented by [${pk}] (${name})?`;
    case 'CoveragePolicy':
      return `What diagnoses and procedure codes are governed by coverage article [${pk}] (${name})?`;
    case 'ChangeRequest':
      return `What operational instructions and benefit categories are mandated by [${pk}] (${name})?`;
    case 'Jurisdiction':
      return `What states and coverage policies are administered by [${pk}] (${name})?`;
    case 'State':
      return `What Medicare contractor, coverage policies, and allowable fee schedules apply to [${pk}] (${name})?`;
    case 'HCPCSCode':
      return `What are the coverage criteria, physician requirements, and allowable rates for [${pk}] (${name})?`;
    case 'ICD10Code':
      return `What coverage policies and durable medical equipment items are authorized for diagnosis [${pk}] (${name})?`;
    case 'Policy':
      return `Explain the legislative, regulatory, and coverage lineage of policy [${pk}] (${name}).`;
    case 'StatutorySection':
      return `What statutory obligations and healthcare provisions are codified in [${pk}] (${name})?`;
    case 'FeeScheduleEntry':
      return `What are the allowable reimbursement rates and jurisdictional terms for [${pk}] (${name})?`;
    case 'LiteratureStudy':
      return `What clinical evidence and findings are documented in study [${pk}] (${name})?`;
    case 'LobbyingFiling':
      return `What lobbying activities, clients, and issues are disclosed in filing [${pk}] (${name})?`;
    default:
      return `Explain the regulatory and operational role of [${pk}] (${name}).`;
  }
};
```

---

### 2.2. File: `src/frontend/src/context/GraphSyncContext.tsx`
- **Component Path:** `[GraphSyncContext.tsx](file:///Users/diesel/Desktop/LAG/src/frontend/src/context/GraphSyncContext.tsx)`
- **Target Line Range:** Lines 6–27, 31–48, 112–150

#### Transformation 1: Interface and Model Extension
```diff
@@ -6,2 +6,10 @@
 import type { GraphNode, AnchorEntity, GraphRAGQueryResponse } from '../types/graph';
+import { constructInquiryPrompt } from '../utils/promptGenerator';
+
+export interface ChatMessage {
+  id: string;
+  sender: 'user' | 'assistant';
+  text: string;
+  responsePayload?: GraphRAGQueryResponse;
+  timestamp: string;
+}
 
 interface GraphSyncContextType {
@@ -17,2 +25,5 @@
   isChatOpen: boolean;
+  messages: ChatMessage[];
+  isQueryLoading: boolean;
+  errorMsg: string | null;
   focusTarget: { x: number; y: number; zoom?: number } | null;
@@ -27,2 +38,4 @@
   setFocusTarget: (target: { x: number; y: number; zoom?: number } | null) => void;
+  submitInquiry: (queryText: string, anchorPk?: string, modelId?: string) => Promise<void>;
+  inquireNode: (node: GraphNode) => Promise<void>;
 }
```

#### Transformation 2: State and Dispatch Implementation in Provider
```diff
@@ -46,2 +59,9 @@
   const [isChatOpen, setIsChatOpen] = useState<boolean>(false);
+  const [isQueryLoading, setIsQueryLoading] = useState<boolean>(false);
+  const [errorMsg, setErrorMsg] = useState<string | null>(null);
+  const [messages, setMessages] = useState<ChatMessage[]>([
+    {
+      id: 'welcome-1',
+      sender: 'assistant',
+      text: "Welcome to the LAG Policy GraphRAG Intelligence Terminal. You can ask natural language clinical, geographic, or macro legislative questions, or select any node on the blueprint canvas to seed a targeted inquiry.",
+      timestamp: new Date().toLocaleTimeString(),
+    },
+  ]);
   const [focusTarget, setFocusTarget] = useState<{ x: number; y: number; zoom?: number } | null>(null);
@@ -111,2 +131,58 @@
 
+  const submitInquiry = useCallback(async (queryText: string, anchorPk?: string, modelId?: string) => {
+    const q = queryText.trim();
+    if (!q || isQueryLoading) return;
+
+    setErrorMsg(null);
+    const userMsg: ChatMessage = {
+      id: `user-${Date.now()}`,
+      sender: 'user',
+      text: q,
+      timestamp: new Date().toLocaleTimeString(),
+    };
+    setMessages((prev) => [...prev, userMsg]);
+    setIsQueryLoading(true);
+
+    try {
+      const res = await fetch('/api/graphrag/query', {
+        method: 'POST',
+        headers: { 'Content-Type': 'application/json' },
+        body: JSON.stringify({
+          query: q,
+          model_id: modelId || 'meta-llama/Meta-Llama-3-8B-Instruct',
+          state_code: filterState || 'WI',
+          primary_key: anchorPk,
+        }),
+      });
+
+      if (!res.ok) {
+        const errData = await res.json().catch(() => ({}));
+        throw new Error(errData.message || errData.detail?.message || `API error ${res.status}`);
+      }
+
+      const data: GraphRAGQueryResponse = await res.json();
+      setIlluminatedPath(data);
+
+      const assistantMsg: ChatMessage = {
+        id: `asst-${Date.now()}`,
+        sender: 'assistant',
+        text: data.answer,
+        responsePayload: data,
+        timestamp: new Date().toLocaleTimeString(),
+      };
+      setMessages((prev) => [...prev, assistantMsg]);
+    } catch (err: any) {
+      const msg = err.message || 'Error executing GraphRAG query.';
+      setErrorMsg(msg);
+    } finally {
+      setIsQueryLoading(false);
+    }
+  }, [filterState, isQueryLoading, setIlluminatedPath]);
+
+  const inquireNode = useCallback(async (node: GraphNode) => {
+    setIsChatOpen(true);
+    const prompt = constructInquiryPrompt(node);
+    await submitInquiry(prompt, node.primary_key);
+  }, [submitInquiry]);
```

---

### 2.3. File: `src/frontend/src/components/NodeDetailDrawer.tsx`
- **Component Path:** `[NodeDetailDrawer.tsx](file:///Users/diesel/Desktop/LAG/src/frontend/src/components/NodeDetailDrawer.tsx)`
- **Target Line Range:** Lines 15–18, 243–266

#### Transformation: Action Button Binding and In-Flight State
```diff
@@ -15,3 +15,3 @@
 export const NodeDetailDrawer: React.FC<NodeDetailDrawerProps> = ({ nodes, links }) => {
-  const { selectedNode, selectNode, setIsChatOpen } = useGraphSync();
+  const { selectedNode, selectNode, inquireNode, isQueryLoading } = useGraphSync();
 
@@ -243,23 +243,24 @@
         {/* Action Button: Ask Agent */}
         <button
-          onClick={() => setIsChatOpen(true)}
+          onClick={() => selectedNode && inquireNode(selectedNode)}
+          disabled={isQueryLoading}
           style={{
             width: '100%',
-            backgroundColor: CANVAS_PALETTE.accentAmber,
+            backgroundColor: isQueryLoading ? 'rgba(255, 183, 3, 0.6)' : CANVAS_PALETTE.accentAmber,
             color: '#0a1128',
             fontWeight: 700,
             fontSize: 13,
             padding: '10px 14px',
             borderRadius: 6,
             border: 'none',
-            cursor: 'pointer',
+            cursor: isQueryLoading ? 'not-allowed' : 'pointer',
             display: 'flex',
             alignItems: 'center',
             justifyContent: 'center',
             gap: 8,
             marginBottom: 20,
             boxShadow: '0 2px 8px rgba(255, 183, 3, 0.25)',
+            opacity: isQueryLoading ? 0.75 : 1.0,
           }}
         >
-          ◈ INQUIRE IN GRAPHRAG CHAT
+          {isQueryLoading ? '◈ INQUIRING...' : '◈ INQUIRE IN GRAPHRAG CHAT'}
         </button>
```

---

### 2.4. File: `src/frontend/src/components/AgentChatDrawer.tsx`
- **Component Path:** `[AgentChatDrawer.tsx](file:///Users/diesel/Desktop/LAG/src/frontend/src/components/AgentChatDrawer.tsx)`
- **Target Line Range:** Lines 10–39, 43–94

#### Transformation: Context State Consumption and Form Submission
```diff
@@ -10,9 +10,2 @@
-interface Message {
-  id: string;
-  sender: 'user' | 'assistant';
-  text: string;
-  responsePayload?: GraphRAGQueryResponse;
-  timestamp: string;
-}
 
 export const AgentChatDrawer: React.FC = () => {
@@ -23,17 +16,9 @@
     quickPrompts,
-    setIlluminatedPath,
-    filterState,
+    messages,
+    isQueryLoading,
+    errorMsg,
+    submitInquiry,
+    seededAnchor,
   } = useGraphSync();
 
   const [inputQuery, setInputQuery] = useState<string>('');
   const [modelId, setModelId] = useState<string>('meta-llama/Meta-Llama-3-8B-Instruct');
-  const [loading, setLoading] = useState<boolean>(false);
-  const [errorMsg, setErrorMsg] = useState<string | null>(null);
-
-  const [messages, setMessages] = useState<Message[]>([
-    {
-      id: 'welcome-1',
-      sender: 'assistant',
-      text: "Welcome to the LAG Policy GraphRAG Intelligence Terminal. You can ask natural language clinical, geographic, or macro legislative questions, or select any node on the blueprint canvas to seed a targeted inquiry.",
-      timestamp: new Date().toLocaleTimeString(),
-    },
-  ]);
 
@@ -43,52 +28,8 @@
-  const handleSend = async (queryText?: string) => {
-    const q = (queryText || inputQuery).trim();
-    if (!q || loading) return;
-
-    setErrorMsg(null);
-    setInputQuery('');
-
-    // Append user message
-    const userMsg: Message = {
-      id: `user-${Date.now()}`,
-      sender: 'user',
-      text: q,
-      timestamp: new Date().toLocaleTimeString(),
-    };
-    setMessages((prev) => [...prev, userMsg]);
-    setLoading(true);
-
-    try {
-      const res = await fetch('/api/graphrag/query', {
-        method: 'POST',
-        headers: { 'Content-Type': 'application/json' },
-        body: JSON.stringify({
-          query: q,
-          model_id: modelId,
-          state_code: filterState || 'WI',
-        }),
-      });
-
-      if (!res.ok) {
-        const errData = await res.json().catch(() => ({}));
-        throw new Error(errData.message || `API error ${res.status}`);
-      }
-
-      const data: GraphRAGQueryResponse = await res.json();
-
-      // Trigger bidirectional canvas illumination!
-      setIlluminatedPath(data);
-
-      const assistantMsg: Message = {
-        id: `asst-${Date.now()}`,
-        sender: 'assistant',
-        text: data.answer,
-        responsePayload: data,
-        timestamp: new Date().toLocaleTimeString(),
-      };
-      setMessages((prev) => [...prev, assistantMsg]);
-    } catch (err: any) {
-      setErrorMsg(err.message || 'Error executing GraphRAG query.');
-    } finally {
-      setLoading(false);
-    }
+  const handleSend = async (queryText?: string) => {
+    const q = (queryText || inputQuery).trim();
+    if (!q || isQueryLoading) return;
+    setInputQuery('');
+    await submitInquiry(q, seededAnchor?.primary_key, modelId);
   };
```

---

### 2.5. File: `src/graphrag/models.py`
- **Component Path:** `[models.py](file:///Users/diesel/Desktop/LAG/src/graphrag/models.py)`
- **Target Line Range:** Lines 58–63

#### Transformation: Add Explicit Anchor Field to Request Model
```diff
@@ -58,6 +58,8 @@
 class GraphRAGQueryRequest(BaseModel):
     """Request payload for conversational GraphRAG synthesis."""
     query: str
     model_id: Optional[str] = "meta-llama/Meta-Llama-3-8B-Instruct"
     state_code: Optional[str] = None
+    primary_key: Optional[str] = None
+    anchor_node_pk: Optional[str] = None
```

---

### 2.6. File: `src/graphrag/entity_linker.py`
- **Component Path:** `[entity_linker.py](file:///Users/diesel/Desktop/LAG/src/graphrag/entity_linker.py)`
- **Target Line Range:** Lines 120–140

#### Transformation: Implement `resolve_explicit_anchor`
```python
    def resolve_explicit_anchor(self, primary_key: str, session: Session) -> ResolvedAnchors:
        """Deterministically verifies an explicit primary key against Neo4j, bypassing regex extraction."""
        clean_pk = primary_key.strip()
        record = session.run(
            "MATCH (n:PolicyNode {primary_key: $pk}) "
            "RETURN n.primary_key AS primary_key, labels(n) AS labels, n.name AS name, n.title AS title",
            pk=clean_pk,
        ).single()

        if not record:
            raise EntityResolutionError(
                f"Entity with primary_key '{clean_pk}' not found in knowledge graph.",
                details={"primary_key": clean_pk},
            )

        labels = [l for l in record["labels"] if l != "PolicyNode"]
        label = labels[0] if labels else "PolicyNode"
        matched = record["name"] or record["title"] or clean_pk

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

        anchor = AnchorEntity(
            slot=slot,
            primary_key=clean_pk,
            matched_text=str(matched),
            entity_type=label,
            label=label,
        )

        resolved = ResolvedAnchors(all_anchors=[anchor])
        if slot == "state":
            resolved.state_anchor = anchor
        elif slot in ("diagnosis", "icd10code"):
            resolved.diagnosis_anchor = anchor
        elif slot == "policy":
            resolved.policy_anchor = anchor
        elif slot in ("hcpcs", "hcpcscode"):
            resolved.hcpcs_anchor = anchor
        elif slot == "jurisdiction":
            resolved.jurisdiction_anchor = anchor
        elif slot == "changerequest":
            resolved.change_request_anchor = anchor
        elif slot == "coveragepolicy":
            resolved.coverage_policy_anchor = anchor

        return resolved
```

---

### 2.7. File: `src/graphrag/pipeline.py`
- **Component Path:** `[pipeline.py](file:///Users/diesel/Desktop/LAG/src/graphrag/pipeline.py)`
- **Target Line Range:** Lines 43–58

#### Transformation: Explicit Anchor Bypass Routing
```diff
@@ -43,4 +43,9 @@
-        # Stage 1: Entity Anchor Linking
-        anchors: ResolvedAnchors = self.linker.resolve_anchors(request.query, session)
+        # Stage 1: Entity Anchor Linking (Explicit Anchor Bypass)
+        explicit_pk = request.primary_key or request.anchor_node_pk
+        if explicit_pk:
+            anchors: ResolvedAnchors = self.linker.resolve_explicit_anchor(explicit_pk, session)
+        else:
+            anchors: ResolvedAnchors = self.linker.resolve_anchors(request.query, session)
 
         # Stage 2: Topological Subgraph Expansion
         traversal_result: TraversalResult = self.traverser.extract_connecting_subgraph(
```

---

### 2.8. File: `src/graphrag/traversal.py`
- **Component Path:** `[traversal.py](file:///Users/diesel/Desktop/LAG/src/graphrag/traversal.py)`
- **Target Line Range:** Lines 270–297

#### Transformation: Exact Cypher Edge Projections & Zero-UNKNOWN Guarantee
```diff
@@ -270,28 +270,30 @@
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
-        MATCH (n:PolicyNode {primary_key: $anchor_pk})-[r]-(m:PolicyNode)
+        MATCH (n:PolicyNode {primary_key: $anchor_pk})
+        OPTIONAL MATCH (n)-[r]-(m:PolicyNode)
         WHERE NOT m:FeeScheduleEntry
-        RETURN n, r, m
+        RETURN n, r, m,
+               startNode(r).primary_key AS src_pk,
+               endNode(r).primary_key AS tgt_pk,
+               type(r) AS rel_type
         LIMIT 50
         """
         results = session.run(query, anchor_pk=anchor_pk).data()
         for row in results:
             n = row.get("n")
             m = row.get("m")
             r = row.get("r")
+            src_pk = row.get("src_pk")
+            tgt_pk = row.get("tgt_pk")
+            rel_type = row.get("rel_type")
             if n:
                 tn = self._convert_node(n)
                 nodes_by_pk[tn.primary_key] = tn
                 active_node_pks.add(tn.primary_key)
             if m:
                 tm = self._convert_node(m)
                 nodes_by_pk[tm.primary_key] = tm
                 active_node_pks.add(tm.primary_key)
-            if r:
-                src = r.start_node["primary_key"] if hasattr(r, "start_node") and "primary_key" in r.start_node else None
-                tgt = r.end_node["primary_key"] if hasattr(r, "end_node") and "primary_key" in r.end_node else None
-                te = self._convert_edge(r, src, tgt)
+            if r and src_pk and tgt_pk:
+                te = self._convert_edge(r, src_pk, tgt_pk)
                 edges_by_key[te.edge_key] = te
                 active_edge_keys.add(te.edge_key)
```

---

### 2.9. File: `src/graphrag/context_assembler.py`
- **Component Path:** `[context_assembler.py](file:///Users/diesel/Desktop/LAG/src/graphrag/context_assembler.py)`
- **Target Line Range:** Lines 36–58, 85–105

#### Transformation: Universal 14-Type Context Formatting
```python
        # In Section 1 (Program & Legal Authority):
        bills = [n for n in nodes if n.label == "Bill"]
        for b in bills:
            title = b.properties.get("title") or b.name
            lines.append(f"- Introduced Bill: [{b.primary_key}] {title}")

        filings = [n for n in nodes if n.label == "LobbyingFiling"]
        for lf in filings:
            client = lf.properties.get("client_name") or lf.name
            lines.append(f"- Lobbying Filing: [{lf.primary_key}] {client}")

        # In Section 3 (Clinical Criteria):
        studies = [n for n in nodes if n.label == "LiteratureStudy"]
        for st in studies:
            title = st.properties.get("title") or st.name
            lines.append(f"- Clinical Study: [{st.primary_key}] {title}")
```

---

### 2.10. File: `tests/test_api_endpoints.py`
- **Component Path:** `[test_api_endpoints.py](file:///Users/diesel/Desktop/LAG/tests/test_api_endpoints.py)`
- **Target Line Range:** End of file (Lines 140+)

#### Transformation: Automated Test Oracles
```python
def test_api_graphrag_query_explicit_anchor_plaw(client):
    """Verifies one-click inquiry with explicit primary_key for PLAW-117-328."""
    payload = {
        "query": "Explain the statutory authority and enacted healthcare provisions of [PLAW-117-328] (Consolidated Appropriations Act, 2023).",
        "primary_key": "PLAW-117-328",
    }
    res = client.post("/api/graphrag/query", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "PLAW-117-328" in data["active_node_pks"]
    assert len(data["active_node_pks"]) >= 6
    assert len(data["active_edge_keys"]) >= 5
    assert all("UNKNOWN" not in ek for ek in data["active_edge_keys"])
    assert "[PLAW-117-328]" in data["answer"]


def test_api_graphrag_query_all_14_entity_types(client):
    """Verifies that one-click inquiry succeeds with >0 illuminated nodes across all 14 entity types."""
    sample_entities = [
        "STATE-WI", "JURIS-DME-B", "CMS-CR-13286", "CMS-MCD-A59508",
        "HCPCS-A6522", "ICD10-I97.2", "FEE-A6522-WI-NR-2024", "POLICY-LTA",
        "PLAW-117-328", "FR-2023-24455", "BILL-117-hr-3630",
        "USC-42-1395x-s-2-JJ", "PUBMED-31841362", "LDA-2023-Q1-001"
    ]
    for pk in sample_entities:
        res = client.post("/api/graphrag/query", json={"query": f"Inquire about [{pk}]", "primary_key": pk})
        assert res.status_code == 200
        data = res.json()
        assert len(data["active_node_pks"]) > 0
        assert pk in data["active_node_pks"]


def test_api_graphrag_query_invalid_anchor_fails_fast(client):
    """Verifies fast-fail HTTP 400 when an invalid primary key is supplied."""
    payload = {
        "query": "Inquire about nonexistent node",
        "primary_key": "NONEXISTENT-PK-9999",
    }
    res = client.post("/api/graphrag/query", json=payload)
    assert res.status_code == 400
```
