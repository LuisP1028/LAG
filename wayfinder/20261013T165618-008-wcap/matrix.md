# Master Component-to-Edit Matrix: Visualizer UI Controls, Canvas Stability, and External Government Links

**Governing Specification:** `functional_specification_006.md`  
**Run ID:** `20261013T165618-008-wcap`  
**Planning Status:** Resolved  
**Taxonomy Reference:** `LANGUAGE.md`

---

## 1. Overview and Component Traceability

This matrix maps every functional requirement in `functional_specification_006.md` and every decision ticket in `wayfinder/20261013T165618-008-wcap/tickets/` to the exact file paths, line ranges, symbols, and transformations required.

| Requirement ID | Requirement Summary | Governing Ticket | Target Component File | Symbols Targeted |
|---|---|---|---|---|
| **REQ-4.1** | Remove Physics Toggle Button | `ticket-001.md` | `src/frontend/src/components/FilterToolbar.tsx` | `FilterToolbar` (lines 23–24, 107–122) |
| **REQ-4.1** | Deprecate Physics Frozen State | `ticket-001.md` | `src/frontend/src/context/GraphSyncContext.tsx` | `GraphSyncContextType`, `GraphSyncProvider` (lines 17, 26, 47, 115–117, 129, 137, 150, 156) |
| **REQ-4.2** | Collapsible Blueprint HUD Accordion | `ticket-002.md` | `src/frontend/src/components/GraphCanvas.tsx` | `GraphCanvas` (HUD markup, lines 469–497) |
| **REQ-4.3** | Decouple Simulation Lifecycle from UI State | `ticket-003.md` | `src/frontend/src/components/GraphCanvas.tsx` | `GraphCanvas` (simulation hook, lines 312–360; pointer handlers, lines 427–453) |
| **REQ-4.4** | Dynamic External Government Links (All 10 Types) | `ticket-004.md` | `src/frontend/src/components/NodeDetailDrawer.tsx` | `NodeDetailDrawer` (`getGovernmentSourceLink`, lines 47–87) |

---

## 2. File-by-File Detailed Transformation Specifications

### 2.1. File: `src/frontend/src/components/FilterToolbar.tsx`
- **Component Path:** `[FilterToolbar.tsx](file:///Users/diesel/Desktop/LAG/src/frontend/src/components/FilterToolbar.tsx)`
- **Target Line Range:** Lines 21–25 and lines 106–123

#### Transformation 1: Remove Destructured State
```diff
@@ -21,4 +21,2 @@
     isChatOpen,
     setIsChatOpen,
-    physicsFrozen,
-    togglePhysicsFrozen,
   } = useGraphSync();
```

#### Transformation 2: Remove Physics Toggle Button Element
```diff
@@ -106,18 +104,0 @@
-      {/* Physics Toggle */}
-      <button
-        onClick={togglePhysicsFrozen}
-        style={{
-          backgroundColor: physicsFrozen ? 'rgba(234, 179, 8, 0.2)' : 'rgba(30, 41, 59, 0.8)',
-          color: physicsFrozen ? '#facc15' : '#e2e8f0',
-          border: `1px solid ${physicsFrozen ? '#facc15' : CANVAS_PALETTE.panelBorder}`,
-          borderRadius: 4,
-          padding: '4px 10px',
-          cursor: 'pointer',
-          fontSize: 11,
-          fontWeight: 600,
-        }}
-        title="Toggle force physics simulation"
-      >
-        {physicsFrozen ? '▶ RESUME PHYSICS' : '⏸ FREEZE PHYSICS'}
-      </button>
```

---

### 2.2. File: `src/frontend/src/context/GraphSyncContext.tsx`
- **Component Path:** `[GraphSyncContext.tsx](file:///Users/diesel/Desktop/LAG/src/frontend/src/context/GraphSyncContext.tsx)`
- **Target Line Range:** Lines 17, 26, 47, 115–118, 129, 137, 150, 156

#### Transformation 1: Interface Contract Cleanup
```diff
@@ -16,3 +16,2 @@
   policyKeyword: string;
-  physicsFrozen: boolean;
   isChatOpen: boolean;
@@ -25,3 +24,2 @@
   setPolicyKeyword: (keyword: string) => void;
-  togglePhysicsFrozen: () => void;
   setIsChatOpen: (open: boolean) => void;
```

#### Transformation 2: Provider State and Value Cleanup
```diff
@@ -46,3 +44,2 @@
   const [policyKeyword, setPolicyKeyword] = useState<string>("LTA");
-  const [physicsFrozen, setPhysicsFrozen] = useState<boolean>(false);
   const [isChatOpen, setIsChatOpen] = useState<boolean>(false);
@@ -115,4 +112,0 @@
-  const togglePhysicsFrozen = useCallback(() => {
-    setPhysicsFrozen((prev) => !prev);
-  }, []);
-
@@ -129,2 +123,0 @@
-      physicsFrozen,
@@ -137,2 +130,0 @@
-      togglePhysicsFrozen,
@@ -150,2 +142,0 @@
-      physicsFrozen,
@@ -156,2 +147,0 @@
-      togglePhysicsFrozen,
```

---

### 2.3. File: `src/frontend/src/components/GraphCanvas.tsx`
- **Component Path:** `[GraphCanvas.tsx](file:///Users/diesel/Desktop/LAG/src/frontend/src/components/GraphCanvas.tsx)`
- **Target Line Range:** Lines 27–31, 312–360, 427–453, 468–498

#### Transformation 1: Context Destructuring & Local State
```diff
@@ -27,4 +27,5 @@
     selectedNode,
     selectNode,
-    physicsFrozen,
   } = useGraphSync();
+
+  const [isHudOpen, setIsHudOpen] = useState<boolean>(true);
+  const renderRef = useRef<() => void>(() => {});
```

#### Transformation 2: Decouple Simulation Lifecycle from Render Identity
```diff
@@ -310,2 +311,6 @@
   }, [nodes, links, isIlluminated, activeNodePKs, activeEdgeKeys, selectedNode, hoveredNode]);
 
+  useEffect(() => {
+    renderRef.current = render;
+  }, [render]);
+
   // Set up d3 force simulation
   useEffect(() => {
     if (!nodes.length) return;
@@ -337,3 +342,4 @@
       .force('center', d3.forceCenter(width / 2, height / 2).strength(0.08))
-      .alphaDecay(0.028);
+      .alphaDecay(0.028)
+      .velocityDecay(0.4);
 
     simulation.on('tick', () => {
-      render();
+      renderRef.current();
     });
 
     simulationRef.current = simulation;
 
     return () => {
       simulation.stop();
     };
-  }, [nodes, links, render]);
-
-  // Manage physics freeze toggle
-  useEffect(() => {
-    if (!simulationRef.current) return;
-    if (physicsFrozen) {
-      simulationRef.current.alpha(0);
-      simulationRef.current.stop();
-    } else {
-      simulationRef.current.alpha(0.3).restart();
-    }
-  }, [physicsFrozen]);
+  }, [nodes, links]);
```

#### Transformation 3: Pointer Move Stability
```diff
@@ -448,3 +445,4 @@
     if (hovered !== hoveredNode) {
       setHoveredNode(hovered);
       canvas.style.cursor = hovered ? 'pointer' : 'crosshair';
+      // Redraw is handled reactively by React rendering loop; simulation alpha is unaffected.
     }
```

#### Transformation 4: Collapsible Blueprint HUD Accordion
```diff
@@ -469,29 +467,54 @@
       {/* Blueprint HUD Telemetry Overlay */}
       <div
+        onClick={() => setIsHudOpen((prev) => !prev)}
         style={{
           position: 'absolute',
           top: 14,
           left: 14,
           backgroundColor: 'rgba(10, 17, 40, 0.88)',
           border: '1px solid rgba(255, 183, 3, 0.35)',
-          padding: '8px 14px',
           borderRadius: 4,
           fontFamily: '"SF Mono", "Fira Code", monospace',
           fontSize: 11,
           color: '#e2e8f0',
           boxShadow: '0 4px 16px rgba(0, 0, 0, 0.4)',
-          pointerEvents: 'none',
+          pointerEvents: 'auto',
+          cursor: 'pointer',
           userSelect: 'none',
+          zIndex: 10,
+          transition: 'all 0.2s ease',
         }}
+        title="Click to expand/collapse Blueprint HUD"
       >
-        <div style={{ color: CANVAS_PALETTE.accentAmber, fontWeight: 700, marginBottom: 4, letterSpacing: '0.05em' }}>
-          ◈ LAG KNOWLEDGE BLUEPRINT HUD
-        </div>
-        <div style={{ display: 'flex', gap: 14 }}>
-          <span>NODES: <strong style={{ color: '#38bdf8' }}>{nodes.length}</strong></span>
-          <span>EDGES: <strong style={{ color: '#38bdf8' }}>{links.length}</strong></span>
-          <span>FPS: <strong style={{ color: fps >= 55 ? '#4ade80' : '#f87171' }}>{fps}</strong></span>
-          <span>STATUS: <strong style={{ color: isIlluminated ? CANVAS_PALETTE.accentAmber : '#94a3b8' }}>
-            {isIlluminated ? 'PATH ILLUMINATED' : 'EXPLORATION MODE'}
-          </strong></span>
-        </div>
+        {!isHudOpen ? (
+          <div style={{ padding: '6px 12px', display: 'flex', alignItems: 'center', gap: 8 }}>
+            <span style={{ color: CANVAS_PALETTE.accentAmber, fontWeight: 700, letterSpacing: '0.05em' }}>
+              ◈ BLUEPRINT HUD
+            </span>
+            <span style={{ fontSize: 9, color: '#94a3b8' }}>▼</span>
+          </div>
+        ) : (
+          <>
+            <div
+              style={{
+                padding: '8px 14px 6px 14px',
+                display: 'flex',
+                alignItems: 'center',
+                justifyContent: 'space-between',
+                borderBottom: '1px solid rgba(255, 183, 3, 0.2)',
+                color: CANVAS_PALETTE.accentAmber,
+                fontWeight: 700,
+                letterSpacing: '0.05em',
+              }}
+            >
+              <span>◈ LAG KNOWLEDGE BLUEPRINT HUD</span>
+              <span style={{ fontSize: 9, color: '#94a3b8', marginLeft: 8 }}>▲</span>
+            </div>
+            <div style={{ padding: '8px 14px', display: 'flex', gap: 14 }}>
+              <span>NODES: <strong style={{ color: '#38bdf8' }}>{nodes.length}</strong></span>
+              <span>EDGES: <strong style={{ color: '#38bdf8' }}>{links.length}</strong></span>
+              <span>FPS: <strong style={{ color: fps >= 55 ? '#4ade80' : '#f87171' }}>{fps}</strong></span>
+              <span>STATUS: <strong style={{ color: isIlluminated ? CANVAS_PALETTE.accentAmber : '#94a3b8' }}>
+                {isIlluminated ? 'PATH ILLUMINATED' : 'EXPLORATION MODE'}
+              </strong></span>
+            </div>
+          </>
+        )}
       </div>
```

---

### 2.4. File: `src/frontend/src/components/NodeDetailDrawer.tsx`
- **Component Path:** `[NodeDetailDrawer.tsx](file:///Users/diesel/Desktop/LAG/src/frontend/src/components/NodeDetailDrawer.tsx)`
- **Target Line Range:** Lines 46–88

#### Complete Transformation: Dynamic External Government Link Generator
```diff
@@ -46,42 +46,128 @@
   // Construct official government external links
-  const getGovernmentSourceLink = () => {
-    switch (selectedNode.label) {
-      case 'Bill':
-        return {
-          title: 'Congress.gov Legislative Record',
-          url: 'https://www.congress.gov/bill/117th-congress/house-bill/3630',
-        };
-      case 'PublicLaw':
-        return {
-          title: 'GPO GovInfo Public Law 117-328 (Statutes at Large)',
-          url: 'https://www.govinfo.gov/app/details/PLAW-117publ328',
-        };
-      case 'StatutorySection':
-        return {
-          title: 'US Code GPO Title 42 § 1395x(s)(2)(JJ)',
-          url: 'https://www.govinfo.gov/app/details/USCODE-2022-title42/USCODE-2022-title42-chap7-subchapXVIII-partE-sec1395x',
-        };
-      case 'Regulation':
-        return {
-          title: 'Federal Register Final Rule (88 FR 77676, CMS-1784-F)',
-          url: 'https://www.federalregister.gov/documents/2023/11/16/2023-24455/medicare-and-medicaid-programs-cy-2024-payment-policies-under-the-physician-fee-schedule-and-other',
-        };
-      case 'CoveragePolicy':
-        return {
-          title: 'CMS Medicare Coverage Database (Article A59508)',
-          url: 'https://www.cms.gov/medicare-coverage-database/view/article.aspx?articleid=59508',
-        };
-      case 'ChangeRequest':
-        return {
-          title: 'CMS Change Request 13286 Transmittal',
-          url: 'https://www.cms.gov/files/document/r13286cp.pdf',
-        };
-      case 'LobbyingFiling':
-        return {
-          title: 'Senate LDA Lobbying Disclosure Search',
-          url: 'https://lda.senate.gov/system/public/',
-        };
-      default:
-        return null;
-    }
-  };
+  const getGovernmentSourceLink = () => {
+    const getOrdinal = (n: number): string => {
+      const s = ['th', 'st', 'nd', 'rd'];
+      const v = n % 100;
+      return n + (s[(v - 20) % 10] || s[v] || s[0]);
+    };
+
+    const getBillTypeSlug = (type: string): string => {
+      const clean = (type || '').toLowerCase().replace(/[^a-z]/g, '');
+      switch (clean) {
+        case 'hr': return 'house-bill';
+        case 's': return 'senate-bill';
+        case 'hjres': return 'house-joint-resolution';
+        case 'sjres': return 'senate-joint-resolution';
+        case 'hconres': return 'house-concurrent-resolution';
+        case 'sconres': return 'senate-concurrent-resolution';
+        case 'hres': return 'house-resolution';
+        case 'sres': return 'senate-resolution';
+        default: return 'house-bill';
+      }
+    };
+
+    switch (selectedNode.label) {
+      case 'CoveragePolicy': {
+        const articleId = props.article_id || selectedNode.primary_key.replace(/^CMS-MCD-/, '');
+        return {
+          title: `CMS Medicare Coverage Database (${articleId})`,
+          url: `https://www.cms.gov/medicare-coverage-database/search-results.aspx?keyword=${encodeURIComponent(articleId)}`,
+        };
+      }
+      case 'PublicLaw': {
+        const congress = props.congress || selectedNode.primary_key.match(/PLAW-(\d+)-/)?.[1] || '117';
+        const num = props.number || selectedNode.primary_key.match(/PLAW-\d+-(\d+)/)?.[1] || '328';
+        return {
+          title: `GPO GovInfo Public Law ${congress}-${num}`,
+          url: `https://www.govinfo.gov/app/details/PLAW-${congress}publ${num}`,
+        };
+      }
+      case 'Bill': {
+        const congress = Number(props.congress || selectedNode.primary_key.match(/BILL-(\d+)-/)?.[1] || 117);
+        const type = (props.type || selectedNode.primary_key.match(/BILL-\d+-([a-z]+)-/)?.[1] || 'hr').toLowerCase();
+        const num = props.number || selectedNode.primary_key.match(/BILL-\d+-[a-z]+-(\d+)/)?.[1] || '3630';
+        return {
+          title: `Congress.gov ${type.toUpperCase()} ${num} (${getOrdinal(congress)} Congress)`,
+          url: `https://www.congress.gov/bill/${getOrdinal(congress)}-congress/${getBillTypeSlug(type)}/${num}`,
+        };
+      }
+      case 'Regulation': {
+        const docNum = props.document_number || selectedNode.primary_key.replace(/^FR-/, '');
+        return {
+          title: `Federal Register Final Rule (${props.citation || docNum})`,
+          url: `https://www.federalregister.gov/d/${encodeURIComponent(docNum)}`,
+        };
+      }
+      case 'StatutorySection': {
+        const title = props.title || '42';
+        const rawSec = props.section || selectedNode.primary_key.replace(/^USC-\d+-/, '') || '1395x';
+        const cleanSec = rawSec.split('-')[0];
+        return {
+          title: `US Code Title ${title} § ${cleanSec} (LII)`,
+          url: `https://www.law.cornell.edu/uscode/text/${encodeURIComponent(title)}/${encodeURIComponent(cleanSec)}`,
+        };
+      }
+      case 'ChangeRequest': {
+        const crNum = props.cr_number || selectedNode.primary_key.replace(/^CMS-CR-/, '');
+        return {
+          title: `CMS Transmittals Index (CR ${crNum})`,
+          url: `https://www.cms.gov/medicare/regulations-guidance/transmittals?search=${encodeURIComponent(crNum)}`,
+        };
+      }
+      case 'Jurisdiction': {
+        const code = props.code || selectedNode.primary_key;
+        const isBC = code.includes('B') || code.includes('C');
+        return {
+          title: isBC
+            ? `CGS Administrators DME MAC Portal (${code})`
+            : `Noridian Healthcare Solutions DME MAC Portal (${code})`,
+          url: isBC ? 'https://www.cgsmedicare.com/' : 'https://med.noridianmedicare.com/',
+        };
+      }
+      case 'HCPCSCode': {
+        const code = props.code || selectedNode.primary_key.replace(/^HCPCS-/, '');
+        return {
+          title: `CMS DMEPOS Fee Schedule & Coding Reference (${code})`,
+          url: 'https://www.cms.gov/medicare/payment/fee-schedules/dmepos/dmepos-fee-schedule',
+        };
+      }
+      case 'ICD10Code': {
+        const code = props.code || selectedNode.primary_key.replace(/^ICD10-/, '');
+        return {
+          title: `CDC ICD-10-CM Clinical Browser (${code})`,
+          url: `https://icd10cmtool.cdc.gov/?prop=${encodeURIComponent(code)}`,
+        };
+      }
+      case 'LobbyingFiling': {
+        return {
+          title: 'Senate LDA Lobbying Disclosure Search',
+          url: 'https://lda.senate.gov/system/public/',
+        };
+      }
+      case 'LiteratureStudy': {
+        const pmid = props.pmid || selectedNode.primary_key.replace(/^PUBMED-/, '');
+        return {
+          title: `PubMed National Library of Medicine (${pmid})`,
+          url: `https://pubmed.ncbi.nlm.nih.gov/${encodeURIComponent(pmid)}/`,
+        };
+      }
+      default:
+        return null;
+    }
+  };
```

---

## 3. Verification Criteria
1. Visualizer toolbar renders cleanly without the physics toggle button.
2. Blueprint HUD toggles between collapsed and expanded states without overlapping the toolbar.
3. Canvas nodes remain completely stationary during hover and mouse movement.
4. Single-click node selection reliably opens the node detail drawer on the first click.
5. All 10 entity types render live, valid government URLs that open successfully in a new browser tab with zero 404s and zero "Invalid Article Version" screens.
