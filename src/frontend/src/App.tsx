import React, { useEffect, useState, useCallback, useMemo } from 'react';
import { GraphSyncProvider, useGraphSync } from './context/GraphSyncContext';
import { GraphCanvas } from './components/GraphCanvas';
import { FilterToolbar } from './components/FilterToolbar';
import { NodeDetailDrawer } from './components/NodeDetailDrawer';
import { AgentChatDrawer } from './components/AgentChatDrawer';
import type { GraphNode, GraphLink, DataSourceMode } from './types/graph';
import { getNodeVisual } from './styles/graph_theme';
import { getApiBaseUrl, getPrecomputedRunUrl } from './utils/apiConfig';
import { filterPrecomputedTopology } from './utils/precomputedTopology';

interface RawTopologyNode {
  primary_key: string;
  label: string;
  name?: string;
  properties?: GraphNode['properties'];
}

interface RawTopologyEdge {
  source_pk: string;
  target_pk: string;
  label: string;
  edge_key?: string;
  provenance?: GraphLink['provenance'];
}

interface RawTopologyResponse {
  nodes?: RawTopologyNode[];
  edges?: RawTopologyEdge[];
}

const MainVisualizer: React.FC = () => {
  const [nodes, setNodes] = useState<GraphNode[]>([]);
  const [links, setLinks] = useState<GraphLink[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [fetchError, setFetchError] = useState<string | null>(null);

  const {
    setAvailablePolicies,
    filterState,
    filterJurisdiction,
    policyKeyword,
    filterCategory,
    searchQuery,
    includeFeeSchedules,
    dataSourceMode,
    setDataSourceMode,
    setExecutionStatus,
    backendState,
    setBackendState,
    backendMessage,
    setBackendMessage,
    selectedNode,
    selectedEdge,
    isMobileViewport,
    isChatOpen,
  } = useGraphSync();

  const probeHealth = useCallback(async () => {
    setBackendState('connecting');
    setBackendMessage('Probing local container HTTPS ingress (/api/health)...');
    const coldStartTimer = window.setTimeout(() => {
      setBackendState('cold_starting');
      setBackendMessage(
        'Establishing connection to local Docker container via public HTTPS tunnel. Initializing 8-hop knowledge graph...'
      );
    }, 3000);

    try {
      const res = await fetch(`${getApiBaseUrl()}/api/health`);
      window.clearTimeout(coldStartTimer);
      if (!res.ok) {
        throw new Error(`Backend health probe returned HTTP ${res.status}`);
      }
      const health = await res.json();
      if (health.neo4j_connected !== true) {
        throw new Error(health.detail || 'Backend graph storage reported disconnected state.');
      }
      setBackendState('online');
      setBackendMessage(null);
    } catch (err: unknown) {
      window.clearTimeout(coldStartTimer);
      const msg =
        err instanceof Error ? err.message : 'Unable to reach live backend health endpoint.';
      setBackendState('error');
      setBackendMessage(msg);
    }
  }, [setBackendState, setBackendMessage]);

  const fetchTopology = useCallback(
    async (
      stateFilter = '',
      policy = 'LTA',
      jurisdictionFilter = '',
      includeFeeOverride?: boolean,
      modeOverride?: DataSourceMode
    ) => {
      const activeMode = modeOverride || dataSourceMode;
      const effectiveFeeToggle =
        includeFeeOverride !== undefined ? includeFeeOverride : includeFeeSchedules;

      setLoading(true);
      setFetchError(null);

      try {
        if (activeMode !== 'live') {
          setExecutionStatus('cached');
          const runKey =
            activeMode === 'precomputed_ivig' || policy.toUpperCase() === 'IVIG' ? 'IVIG' : 'LTA';
          const runUrl = getPrecomputedRunUrl(runKey);
          const res = await fetch(runUrl);
          if (!res.ok) {
            throw new Error(
              `Failed to load pre-computed run artifact (${runUrl}): HTTP ${res.status}`
            );
          }
          const exportPayload = await res.json();
          const filtered = filterPrecomputedTopology(exportPayload, {
            stateFilter,
            jurisdictionFilter,
            policyKeyword: policy,
            includeFeeSchedules: effectiveFeeToggle,
          });
          setNodes(filtered.nodes);
          setLinks(filtered.links);
          return;
        }

        setExecutionStatus('executing');
        const params = new URLSearchParams();
        if (jurisdictionFilter && jurisdictionFilter !== 'ALL') {
          params.append('jurisdiction_filter', jurisdictionFilter);
        }
        if (stateFilter && stateFilter !== 'ALL') {
          params.append('state_filter', stateFilter);
        }
        if (policy && policy !== 'ALL') {
          params.append('policy_keyword', policy);
        }
        if (effectiveFeeToggle) {
          params.append('include_fee_schedules', 'true');
        }

        const res = await fetch(`${getApiBaseUrl()}/api/graph/topology?${params.toString()}`);
        if (!res.ok) {
          let errDetail = `Failed to load topology: HTTP ${res.status}`;
          try {
            const errJson = await res.json();
            if (errJson?.detail || errJson?.message) {
              errDetail = String(errJson.detail || errJson.message);
            }
          } catch {
            // Keep HTTP status message
          }
          throw new Error(errDetail);
        }

        const data: RawTopologyResponse = await res.json();

        const transformedNodes: GraphNode[] = (data.nodes || []).map((n) => {
          const visual = getNodeVisual(n.label);
          return {
            id: n.primary_key,
            primary_key: n.primary_key,
            label: n.label,
            name: n.name || n.primary_key,
            properties: n.properties || { primary_key: n.primary_key },
            radius: visual.radius,
            color: visual.badgeColor,
            shape: visual.shape,
          };
        });

        const policyNodes = transformedNodes.filter((n) => n.label === 'Policy');
        if (policyNodes.length > 0) {
          setAvailablePolicies(
            policyNodes.map((pn) => {
              const kw = String(
                pn.properties?.keyword ||
                  pn.properties?.policy_keyword ||
                  pn.primary_key.replace(/^POLICY-/, '')
              );
              return {
                keyword: kw,
                label: pn.name && pn.name !== pn.primary_key ? `${kw} (${pn.name})` : kw,
              };
            })
          );
        }

        const nodePkSet = new Set(transformedNodes.map((n) => n.primary_key));
        const transformedLinks: GraphLink[] = (data.edges || [])
          .filter((e) => nodePkSet.has(e.source_pk) && nodePkSet.has(e.target_pk))
          .map((e) => ({
            source: e.source_pk,
            target: e.target_pk,
            label: e.label,
            edge_key: e.edge_key || `${e.source_pk}->${e.label}->${e.target_pk}`,
            provenance: e.provenance || {
              source_uri: '',
              selector: '',
              ingestion_timestamp: '',
              run_id: '',
            },
          }));

        setNodes(transformedNodes);
        setLinks(transformedLinks);
        setExecutionStatus('idle');
        setBackendState('online');
        setBackendMessage(null);
      } catch (err: unknown) {
        const message = err instanceof Error ? err.message : 'Error loading graph topology.';
        setFetchError(message);
        setExecutionStatus('error');
        if (activeMode === 'live') {
          setBackendState('error');
          setBackendMessage(message);
        }
      } finally {
        setLoading(false);
      }
    },
    [
      dataSourceMode,
      includeFeeSchedules,
      setAvailablePolicies,
      setExecutionStatus,
      setBackendState,
      setBackendMessage,
    ]
  );

  useEffect(() => {
    probeHealth();
    fetchTopology('', 'LTA', '', false, 'live');
  }, [probeHealth, fetchTopology]);

  // Apply interactive Category & Lexical Search filtering deterministically
  const { visibleNodes, visibleLinks } = useMemo(() => {
    const cleanQuery = searchQuery.trim().toLowerCase();
    const filteredNodes = nodes.filter((n) => {
      if (filterCategory && n.label !== filterCategory) {
        return false;
      }
      if (cleanQuery) {
        const matchPk = n.primary_key.toLowerCase().includes(cleanQuery);
        const matchName = n.name.toLowerCase().includes(cleanQuery);
        const matchLabel = n.label.toLowerCase().includes(cleanQuery);
        const matchProps = Object.values(n.properties || {}).some(
          (val) =>
            val !== null &&
            val !== undefined &&
            String(val).toLowerCase().includes(cleanQuery)
        );
        return matchPk || matchName || matchLabel || matchProps;
      }
      return true;
    });

    const visiblePkSet = new Set(filteredNodes.map((n) => n.primary_key));
    const filteredLinks = links.filter((l) => {
      const srcPk =
        typeof l.source === 'object' ? (l.source as GraphNode).primary_key : String(l.source);
      const tgtPk =
        typeof l.target === 'object' ? (l.target as GraphNode).primary_key : String(l.target);
      return visiblePkSet.has(srcPk) && visiblePkSet.has(tgtPk);
    });

    return { visibleNodes: filteredNodes, visibleLinks: filteredLinks };
  }, [nodes, links, filterCategory, searchQuery]);

  const isInspectionOpen = Boolean(selectedNode || selectedEdge);
  const bannerLeftOffset = isMobileViewport
    ? 12
    : isInspectionOpen
      ? 'min(410px, calc(45vw + 20px))'
      : 20;
  const bannerRightOffset = isMobileViewport
    ? 12
    : isChatOpen
      ? 'min(460px, calc(45vw + 20px))'
      : 'auto';
  const bannerBottomOffset = isMobileViewport
    ? isChatOpen
      ? 'calc(76px + env(safe-area-inset-bottom, 0px))'
      : 'calc(14px + env(safe-area-inset-bottom, 0px))'
    : 'calc(20px + env(safe-area-inset-bottom, 0px))';

  const isStatusBannerVisible =
    dataSourceMode === 'live' &&
    (backendState === 'connecting' || backendState === 'cold_starting');
  const isErrorBannerVisible = Boolean(
    fetchError || (backendState === 'error' && dataSourceMode === 'live')
  );
  const isBannerActive = isStatusBannerVisible || isErrorBannerVisible;

  return (
    <div
      data-testid="app-viewport-root"
      style={{
        position: 'relative',
        width: '100%',
        maxWidth: '100vw',
        height: 'var(--app-height, 100dvh)',
        overflow: 'hidden',
      }}
    >
      <FilterToolbar onReloadTopology={fetchTopology} />
      <GraphCanvas
        nodes={visibleNodes}
        links={visibleLinks}
        loading={loading}
        isBannerActive={isBannerActive}
      />
      <NodeDetailDrawer nodes={nodes} links={links} />
      <AgentChatDrawer />

      {/* Cold-Start / Readiness Banner */}
      {isStatusBannerVisible && (
        <div
          data-testid="backend-status-banner"
          style={{
            position: 'absolute',
            bottom: bannerBottomOffset,
            left: bannerLeftOffset,
            right: bannerRightOffset,
            maxWidth: isMobileViewport ? 'calc(100vw - 24px)' : 780,
            boxSizing: 'border-box',
            backgroundColor: 'rgba(15, 23, 42, 0.94)',
            border: '1px solid #38bdf8',
            color: '#e0f2fe',
            padding: isMobileViewport ? '8px 12px' : '10px 16px',
            borderRadius: 6,
            fontSize: isMobileViewport ? 11 : 12,
            fontFamily: 'monospace',
            zIndex: 100,
            boxShadow: '0 4px 12px rgba(0,0,0,0.5)',
            wordBreak: 'break-word',
          }}
        >
          ⟳ {backendMessage || 'Connecting to cloud backend...'}
        </div>
      )}

      {/* Fail-Fast Backend Error Banner with Explicit Pre-Computed Run Switch */}
      {isErrorBannerVisible && (
        <div
          data-testid="backend-error-banner"
          style={{
            position: 'absolute',
            bottom: bannerBottomOffset,
            left: bannerLeftOffset,
            right: bannerRightOffset,
            backgroundColor: 'rgba(225, 29, 72, 0.94)',
            color: '#ffffff',
            padding: isMobileViewport ? '10px 12px' : '12px 16px',
            borderRadius: 6,
            fontSize: isMobileViewport ? 11 : 12,
            fontFamily: 'monospace',
            zIndex: 100,
            boxShadow: '0 4px 12px rgba(0,0,0,0.5)',
            display: 'flex',
            flexWrap: 'wrap',
            alignItems: 'center',
            gap: isMobileViewport ? 8 : 12,
            maxWidth: isMobileViewport ? 'calc(100vw - 24px)' : 780,
            boxSizing: 'border-box',
          }}
        >
          <span
            style={{
              flex: isMobileViewport ? '1 1 100%' : '1 1 auto',
              wordBreak: 'break-word',
              lineHeight: 1.35,
            }}
          >
            ▲ FAIL-FAST ERROR: {fetchError || backendMessage}
          </span>
          <button
            data-testid="retry-backend-btn"
            onClick={() => {
              probeHealth();
              fetchTopology(
                filterState,
                policyKeyword,
                filterJurisdiction,
                includeFeeSchedules,
                dataSourceMode
              );
            }}
            style={{
              background: '#fff',
              color: '#0f172a',
              border: 'none',
              padding: isMobileViewport ? '6px 10px' : '4px 10px',
              minHeight: isMobileViewport ? 32 : 'auto',
              borderRadius: 4,
              cursor: 'pointer',
              fontWeight: 700,
              fontSize: 11,
              whiteSpace: 'nowrap',
              flex: isMobileViewport ? '1 1 auto' : '0 0 auto',
            }}
          >
            Retry Live API
          </button>
          {dataSourceMode === 'live' && (
            <>
              <button
                data-testid="load-precomputed-lta-btn"
                onClick={() => {
                  setDataSourceMode('precomputed_lta');
                  fetchTopology(
                    filterState,
                    'LTA',
                    filterJurisdiction,
                    includeFeeSchedules,
                    'precomputed_lta'
                  );
                }}
                style={{
                  background: '#ffb703',
                  color: '#0a1128',
                  border: 'none',
                  padding: isMobileViewport ? '6px 10px' : '4px 10px',
                  minHeight: isMobileViewport ? 32 : 'auto',
                  borderRadius: 4,
                  cursor: 'pointer',
                  fontWeight: 700,
                  fontSize: 11,
                  whiteSpace: 'nowrap',
                  flex: isMobileViewport ? '1 1 auto' : '0 0 auto',
                }}
              >
                Load Pre-computed LTA Snapshot
              </button>
              <button
                data-testid="load-precomputed-ivig-btn"
                onClick={() => {
                  setDataSourceMode('precomputed_ivig');
                  fetchTopology(
                    filterState,
                    'IVIG',
                    filterJurisdiction,
                    includeFeeSchedules,
                    'precomputed_ivig'
                  );
                }}
                style={{
                  background: '#38bdf8',
                  color: '#0a1128',
                  border: 'none',
                  padding: isMobileViewport ? '6px 10px' : '4px 10px',
                  minHeight: isMobileViewport ? 32 : 'auto',
                  borderRadius: 4,
                  cursor: 'pointer',
                  fontWeight: 700,
                  fontSize: 11,
                  whiteSpace: 'nowrap',
                  flex: isMobileViewport ? '1 1 auto' : '0 0 auto',
                }}
              >
                Load Pre-computed IVIG Snapshot
              </button>
            </>
          )}
        </div>
      )}
    </div>
  );
};

export default function App() {
  return (
    <GraphSyncProvider>
      <MainVisualizer />
    </GraphSyncProvider>
  );
}

