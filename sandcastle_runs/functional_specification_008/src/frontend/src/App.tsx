import React, { useEffect, useState, useCallback } from 'react';
import { GraphSyncProvider } from './context/GraphSyncContext';
import { GraphCanvas } from './components/GraphCanvas';
import { FilterToolbar } from './components/FilterToolbar';
import { NodeDetailDrawer } from './components/NodeDetailDrawer';
import { AgentChatDrawer } from './components/AgentChatDrawer';
import type { GraphNode, GraphLink } from './types/graph';
import { getNodeVisual } from './styles/graph_theme';

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

  const fetchTopology = useCallback(async (stateFilter = '', policy = 'LTA', jurisdictionFilter = '') => {
    setLoading(true);
    setFetchError(null);
    try {
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

      const res = await fetch(`/api/graph/topology?${params.toString()}`);
      if (!res.ok) {
        throw new Error(`Failed to load topology: HTTP ${res.status}`);
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
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Error loading graph topology.';
      setFetchError(message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchTopology('', 'LTA', '');
  }, [fetchTopology]);

  return (
    <div style={{ position: 'relative', width: '100vw', height: '100vh', overflow: 'hidden' }}>
      <FilterToolbar onReloadTopology={fetchTopology} />
      <GraphCanvas nodes={nodes} links={links} loading={loading} />
      <NodeDetailDrawer nodes={nodes} links={links} />
      <AgentChatDrawer />

      {fetchError && (
        <div
          style={{
            position: 'absolute',
            bottom: 20,
            left: 20,
            backgroundColor: 'rgba(225, 29, 72, 0.9)',
            color: '#ffffff',
            padding: '10px 16px',
            borderRadius: 6,
            fontSize: 12,
            fontFamily: 'monospace',
            zIndex: 100,
            boxShadow: '0 4px 12px rgba(0,0,0,0.5)',
          }}
        >
          {fetchError}
          <button
            onClick={() => fetchTopology('', 'LTA', '')}
            style={{
              marginLeft: 12,
              background: '#fff',
              color: '#000',
              border: 'none',
              padding: '2px 8px',
              borderRadius: 4,
              cursor: 'pointer',
              fontWeight: 700,
            }}
          >
            Retry
          </button>
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
