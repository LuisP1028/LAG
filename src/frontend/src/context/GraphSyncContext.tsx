/**
 * Bidirectional Canvas-Agent Synchronization Bus across all 17 8-hop entity categories and 54 US jurisdictions.
 */

import React, { createContext, useContext, useState, useCallback, useMemo, useRef, useEffect } from 'react';
import type {
  GraphNode,
  GraphLink,
  AnchorEntity,
  GraphRAGQueryResponse,
  ExecutionStatus,
  BackendConnectionState,
  DataSourceMode,
  MicroFactResponse,
} from '../types/graph';
import { constructInquiryPrompt } from '../utils/promptGenerator';
import { getApiBaseUrl } from '../utils/apiConfig';

export const DEFAULT_GRAPHRAG_MODEL = 'Qwen/Qwen2.5-7B-Instruct';
export const DEFAULT_GRAPH_MICRO_FACT =
  'Public Law 117-328 codifies Medicare compression garment benefits.';

export interface ChatMessage {
  id: string;
  sender: 'user' | 'assistant';
  text: string;
  responsePayload?: GraphRAGQueryResponse;
  timestamp: string;
}

export interface StateOption {
  code: string;
  name: string;
  jurisdictionId: string;
}

export interface PolicyOption {
  keyword: string;
  label: string;
}

export interface JurisdictionMetadata {
  id: string;
  label: string;
  shortName: string;
  contractor: string;
  region: string;
  states: { code: string; name: string }[];
}

export const DME_JURISDICTIONS: Record<string, JurisdictionMetadata> = {
  'JURIS-DME-A': {
    id: 'JURIS-DME-A',
    label: 'Jurisdiction A (Northeast - Noridian)',
    shortName: 'Jurisdiction A',
    contractor: 'Noridian Healthcare Solutions',
    region: 'Northeast',
    states: [
      { code: 'CT', name: 'Connecticut' },
      { code: 'DC', name: 'District of Columbia' },
      { code: 'DE', name: 'Delaware' },
      { code: 'MA', name: 'Massachusetts' },
      { code: 'MD', name: 'Maryland' },
      { code: 'ME', name: 'Maine' },
      { code: 'NH', name: 'New Hampshire' },
      { code: 'NJ', name: 'New Jersey' },
      { code: 'NY', name: 'New York' },
      { code: 'PA', name: 'Pennsylvania' },
      { code: 'RI', name: 'Rhode Island' },
      { code: 'VT', name: 'Vermont' },
    ],
  },
  'JURIS-DME-B': {
    id: 'JURIS-DME-B',
    label: 'Jurisdiction B (Midwest - CGS)',
    shortName: 'Jurisdiction B',
    contractor: 'CGS Administrators, LLC',
    region: 'Midwest',
    states: [
      { code: 'IL', name: 'Illinois' },
      { code: 'IN', name: 'Indiana' },
      { code: 'KY', name: 'Kentucky' },
      { code: 'MI', name: 'Michigan' },
      { code: 'MN', name: 'Minnesota' },
      { code: 'OH', name: 'Ohio' },
      { code: 'WI', name: 'Wisconsin' },
    ],
  },
  'JURIS-DME-C': {
    id: 'JURIS-DME-C',
    label: 'Jurisdiction C (South - CGS)',
    shortName: 'Jurisdiction C',
    contractor: 'CGS Administrators, LLC',
    region: 'South',
    states: [
      { code: 'AL', name: 'Alabama' },
      { code: 'AR', name: 'Arkansas' },
      { code: 'CO', name: 'Colorado' },
      { code: 'FL', name: 'Florida' },
      { code: 'GA', name: 'Georgia' },
      { code: 'LA', name: 'Louisiana' },
      { code: 'MS', name: 'Mississippi' },
      { code: 'NC', name: 'North Carolina' },
      { code: 'NM', name: 'New Mexico' },
      { code: 'OK', name: 'Oklahoma' },
      { code: 'PR', name: 'Puerto Rico' },
      { code: 'SC', name: 'South Carolina' },
      { code: 'TN', name: 'Tennessee' },
      { code: 'TX', name: 'Texas' },
      { code: 'VA', name: 'Virginia' },
      { code: 'VI', name: 'U.S. Virgin Islands' },
      { code: 'WV', name: 'West Virginia' },
    ],
  },
  'JURIS-DME-D': {
    id: 'JURIS-DME-D',
    label: 'Jurisdiction D (West - Noridian)',
    shortName: 'Jurisdiction D',
    contractor: 'Noridian Healthcare Solutions',
    region: 'West',
    states: [
      { code: 'AK', name: 'Alaska' },
      { code: 'AZ', name: 'Arizona' },
      { code: 'CA', name: 'California' },
      { code: 'GU', name: 'Guam' },
      { code: 'HI', name: 'Hawaii' },
      { code: 'IA', name: 'Iowa' },
      { code: 'ID', name: 'Idaho' },
      { code: 'KS', name: 'Kansas' },
      { code: 'MO', name: 'Missouri' },
      { code: 'MT', name: 'Montana' },
      { code: 'ND', name: 'North Dakota' },
      { code: 'NE', name: 'Nebraska' },
      { code: 'NV', name: 'Nevada' },
      { code: 'OR', name: 'Oregon' },
      { code: 'SD', name: 'South Dakota' },
      { code: 'UT', name: 'Utah' },
      { code: 'WA', name: 'Washington' },
      { code: 'WY', name: 'Wyoming' },
    ],
  },
};

export const STATE_TO_JURISDICTION: Record<string, string> = Object.values(DME_JURISDICTIONS).reduce(
  (acc, juris) => {
    juris.states.forEach((st) => {
      acc[st.code] = juris.id;
    });
    return acc;
  },
  {} as Record<string, string>
);

export const ALL_STATES_SORTED: StateOption[] = Object.values(DME_JURISDICTIONS)
  .flatMap((juris) =>
    juris.states.map((st) => ({
      code: st.code,
      name: st.name,
      jurisdictionId: juris.id,
    }))
  )
  .sort((a, b) => a.name.localeCompare(b.name));

interface GraphSyncContextType {
  activeNodePKs: Set<string>;
  activeEdgeKeys: Set<string>;
  selectedNode: GraphNode | null;
  selectedEdge: GraphLink | null;
  seededAnchor: AnchorEntity | null;
  isIlluminated: boolean;
  quickPrompts: string[];
  filterJurisdiction: string;
  filterState: string;
  filterCategory: string;
  searchQuery: string;
  includeFeeSchedules: boolean;
  dataSourceMode: DataSourceMode;
  executionStatus: ExecutionStatus;
  backendState: BackendConnectionState;
  backendMessage: string | null;
  availableStates: StateOption[];
  availablePolicies: PolicyOption[];
  policyKeyword: string;
  isChatOpen: boolean;
  messages: ChatMessage[];
  isQueryLoading: boolean;
  errorMsg: string | null;
  focusTarget: { x: number; y: number; zoom?: number } | null;
  microFact: string;
  isMobileViewport: boolean;

  selectNode: (node: GraphNode | null) => void;
  selectEdge: (edge: GraphLink | null) => void;
  setIlluminatedPath: (response: GraphRAGQueryResponse) => void;
  clearIllumination: () => void;
  setFilterJurisdiction: (jurisdiction: string) => void;
  setFilterState: (state: string) => void;
  setFilterCategory: (category: string) => void;
  setSearchQuery: (query: string) => void;
  setIncludeFeeSchedules: (include: boolean) => void;
  setDataSourceMode: (mode: DataSourceMode) => void;
  setExecutionStatus: (status: ExecutionStatus) => void;
  setBackendState: (state: BackendConnectionState) => void;
  setBackendMessage: (msg: string | null) => void;
  setPolicyKeyword: (keyword: string) => void;
  setAvailablePolicies: (policies: PolicyOption[]) => void;
  setIsChatOpen: (open: boolean) => void;
  setFocusTarget: (target: { x: number; y: number; zoom?: number } | null) => void;
  submitInquiry: (queryText: string, anchorPk?: string, modelId?: string) => Promise<void>;
  inquireNode: (node: GraphNode) => Promise<void>;
}

const GraphSyncContext = createContext<GraphSyncContextType | undefined>(undefined);

export const GraphSyncProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [activeNodePKs, setActiveNodePKs] = useState<Set<string>>(new Set());
  const [activeEdgeKeys, setActiveEdgeKeys] = useState<Set<string>>(new Set());
  const [selectedNode, setSelectedNode] = useState<GraphNode | null>(null);
  const [selectedEdge, setSelectedEdge] = useState<GraphLink | null>(null);
  const [seededAnchor, setSeededAnchor] = useState<AnchorEntity | null>(null);
  const [isIlluminated, setIsIlluminated] = useState<boolean>(false);
  const [isQueryLoading, setIsQueryLoading] = useState<boolean>(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const latestQueryIdRef = useRef<number>(0);
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: 'welcome-1',
      sender: 'assistant',
      text: "Welcome to the Medical Durable Goods Assistant. You can ask natural language clinical, geographic, or macro legislative questions, or select any node on the blueprint canvas to seed a targeted inquiry.",
      timestamp: new Date().toLocaleTimeString(),
    },
  ]);
  const [quickPrompts, setQuickPrompts] = useState<string[]>([
    "I am from Wisconsin, survived breast cancer, need lymphedema supplies, I'm on Medicare, can you help?",
    "How was H.R. 3630 enacted into Public Law 117-328 and implemented in 88 FR 77676?",
    "What diagnoses are approved under DME-MAC-COPE147943?",
    "What is the allowable Medicare reimbursement for A6522 in Wisconsin?",
  ]);
  const [filterJurisdiction, setFilterJurisdictionState] = useState<string>("");
  const [jurisdictionScope, setJurisdictionScope] = useState<string>("");
  const [filterState, setFilterStateState] = useState<string>("");
  const [filterCategory, setFilterCategory] = useState<string>("");
  const [searchQuery, setSearchQuery] = useState<string>("");
  const [includeFeeSchedules, setIncludeFeeSchedules] = useState<boolean>(false);
  const [dataSourceMode, setDataSourceMode] = useState<DataSourceMode>('live');
  const [executionStatus, setExecutionStatus] = useState<ExecutionStatus>('idle');
  const [backendState, setBackendState] = useState<BackendConnectionState>('connecting');
  const [backendMessage, setBackendMessage] = useState<string | null>(null);
  const [policyKeyword, setPolicyKeyword] = useState<string>("LTA");
  const [availablePolicies, setAvailablePolicies] = useState<PolicyOption[]>([
    { keyword: 'LTA', label: 'LTA (Lymphedema Treatment Act)' },
    { keyword: 'IVIG', label: 'IVIG (Medicare IVIG Access Enhancement Act)' },
  ]);
  const [isChatOpen, setIsChatOpen] = useState<boolean>(false);
  const [focusTarget, setFocusTarget] = useState<{ x: number; y: number; zoom?: number } | null>(null);
  const [microFact, setMicroFact] = useState<string>(DEFAULT_GRAPH_MICRO_FACT);
  const [isMobileViewport, setIsMobileViewport] = useState<boolean>(() =>
    typeof window !== 'undefined' ? window.innerWidth <= 768 : false
  );

  useEffect(() => {
    if (typeof window === 'undefined') return;

    const syncViewportMetrics = () => {
      const vw = window.innerWidth;
      const vh = window.visualViewport?.height || window.innerHeight;
      setIsMobileViewport(vw <= 768);
      if (vh > 0 && typeof document !== 'undefined') {
        document.documentElement.style.setProperty('--app-height', `${Math.round(vh)}px`);
      }
    };

    syncViewportMetrics();
    window.addEventListener('resize', syncViewportMetrics);
    window.addEventListener('orientationchange', syncViewportMetrics);
    const vv = window.visualViewport;
    if (vv) {
      vv.addEventListener('resize', syncViewportMetrics);
      vv.addEventListener('scroll', syncViewportMetrics);
    }

    return () => {
      window.removeEventListener('resize', syncViewportMetrics);
      window.removeEventListener('orientationchange', syncViewportMetrics);
      if (vv) {
        vv.removeEventListener('resize', syncViewportMetrics);
        vv.removeEventListener('scroll', syncViewportMetrics);
      }
    };
  }, []);

  useEffect(() => {
    let cancelled = false;
    const fetchMicroFact = async () => {
      if (dataSourceMode !== 'live') {
        setMicroFact(DEFAULT_GRAPH_MICRO_FACT);
        return;
      }
      try {
        const params = new URLSearchParams();
        if (policyKeyword) params.append('policy_keyword', policyKeyword);
        if (filterState) params.append('state_code', filterState);
        if (selectedNode?.primary_key) params.append('primary_key', selectedNode.primary_key);

        const res = await fetch(`${getApiBaseUrl()}/api/graphrag/micro-fact?${params.toString()}`);
        if (!res.ok) {
          throw new Error(`HTTP ${res.status}`);
        }
        const payload: MicroFactResponse = await res.json();
        if (cancelled) return;
        const factText = (payload?.micro_fact || '').trim();
        const words = factText ? factText.split(/\s+/) : [];
        if (words.length >= 1 && words.length < 15) {
          setMicroFact(factText);
        } else {
          console.warn(
            '[Telemetry Notice] Micro-fact exceeded 14-word boundary; using verified default graph micro-fact.'
          );
          setMicroFact(DEFAULT_GRAPH_MICRO_FACT);
        }
      } catch (err) {
        if (!cancelled) {
          console.warn(
            '[Telemetry Notice] DeepSeek micro-fact endpoint unavailable; displaying verified default graph micro-fact.',
            err
          );
          setMicroFact(DEFAULT_GRAPH_MICRO_FACT);
        }
      }
    };

    fetchMicroFact();
    return () => {
      cancelled = true;
    };
  }, [dataSourceMode, policyKeyword, filterState, selectedNode]);

  const availableStates = useMemo<StateOption[]>(() => {
    if (jurisdictionScope && DME_JURISDICTIONS[jurisdictionScope]) {
      return DME_JURISDICTIONS[jurisdictionScope].states
        .map((st) => ({
          code: st.code,
          name: st.name,
          jurisdictionId: jurisdictionScope,
        }))
        .sort((a, b) => a.name.localeCompare(b.name));
    }
    return ALL_STATES_SORTED;
  }, [jurisdictionScope]);

  const selectEdge = useCallback((edge: GraphLink | null) => {
    setSelectedEdge(edge);
    if (edge) {
      setSelectedNode(null);
      setSeededAnchor(null);
      if (typeof window !== 'undefined' && window.innerWidth <= 768) {
        setIsChatOpen(false);
      }
    }
  }, []);

  const selectNode = useCallback((node: GraphNode | null) => {
    setSelectedNode(node);
    if (node) {
      setSelectedEdge(null);
      if (typeof window !== 'undefined' && window.innerWidth <= 768) {
        setIsChatOpen(false);
      }
    }
    if (!node) {
      setSeededAnchor(null);
      return;
    }

    const anchor: AnchorEntity = {
      slot: node.label.toLowerCase(),
      primary_key: node.primary_key,
      matched_text: node.name,
      entity_type: node.label,
      label: node.label,
    };
    setSeededAnchor(anchor);

    const prompts: string[] = [
      constructInquiryPrompt(node),
      `How does [${node.primary_key}] connect to patient coverage and reimbursement?`,
      `What upstream laws and downstream policies are linked to [${node.primary_key}]?`,
    ];
    setQuickPrompts(prompts);
  }, []);

  const setIlluminatedPath = useCallback((response: GraphRAGQueryResponse) => {
    const nodePks = Array.isArray(response?.active_node_pks) ? response.active_node_pks : [];
    const edgeKeys = Array.isArray(response?.active_edge_keys) ? response.active_edge_keys : [];
    if (nodePks.length === 0) {
      setActiveNodePKs(new Set());
      setActiveEdgeKeys(new Set());
      setIsIlluminated(false);
      return;
    }
    setActiveNodePKs(new Set(nodePks));
    setActiveEdgeKeys(new Set(edgeKeys));
    setIsIlluminated(true);
  }, []);

  const clearIllumination = useCallback(() => {
    latestQueryIdRef.current += 1;
    setIsQueryLoading(false);
    setExecutionStatus('idle');
    setActiveNodePKs(new Set());
    setActiveEdgeKeys(new Set());
    setIsIlluminated(false);
  }, []);

  const illuminateJurisdiction = useCallback(
    (jurisdictionId: string) => {
      const juris = jurisdictionId ? DME_JURISDICTIONS[jurisdictionId] : undefined;
      if (!juris) {
        clearIllumination();
        return;
      }
      setActiveNodePKs(
        new Set<string>([
          jurisdictionId,
          ...juris.states.map((st) => `STATE-${st.code}`),
        ])
      );
      setActiveEdgeKeys(
        new Set<string>(
          juris.states.map((st) => `${jurisdictionId}->COVERS_STATE->STATE-${st.code}`)
        )
      );
      setIsIlluminated(true);
    },
    [clearIllumination]
  );

  const setFilterJurisdiction = useCallback(
    (jurisdictionId: string) => {
      setFilterJurisdictionState(jurisdictionId);
      setJurisdictionScope(jurisdictionId);
      setFilterStateState("");
      illuminateJurisdiction(jurisdictionId);
    },
    [illuminateJurisdiction]
  );

  const setFilterState = useCallback(
    (stateCode: string) => {
      setFilterStateState(stateCode);
      if (stateCode) {
        const parentJuris = STATE_TO_JURISDICTION[stateCode] || "";
        if (parentJuris) {
          setFilterJurisdictionState(parentJuris);
        }
        setJurisdictionScope((prev) => (prev && prev !== parentJuris ? "" : prev));

        const nodes = new Set<string>([`STATE-${stateCode}`]);
        const edges = new Set<string>();
        if (parentJuris) {
          nodes.add(parentJuris);
          edges.add(`${parentJuris}->COVERS_STATE->STATE-${stateCode}`);
        }
        setActiveNodePKs(nodes);
        setActiveEdgeKeys(edges);
        setIsIlluminated(true);
      } else {
        illuminateJurisdiction(filterJurisdiction);
      }
    },
    [illuminateJurisdiction, filterJurisdiction]
  );

  const submitInquiry = useCallback(
    async (queryText: string, anchorPk?: string, modelId?: string) => {
      const q = queryText.trim();
      if (!q) return;

      const queryId = ++latestQueryIdRef.current;
      setErrorMsg(null);
      setExecutionStatus('querying');
      const userMsg: ChatMessage = {
        id: `user-${Date.now()}-${queryId}`,
        sender: 'user',
        text: q,
        timestamp: new Date().toLocaleTimeString(),
      };
      setMessages((prev) => [...prev, userMsg]);
      setIsQueryLoading(true);

      try {
        const apiBase = getApiBaseUrl();
        const res = await fetch(`${apiBase}/api/graphrag/query`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            query: q,
            model_id: modelId || DEFAULT_GRAPHRAG_MODEL,
            state_code: filterState || undefined,
            jurisdiction_code: filterJurisdiction || undefined,
            primary_key: anchorPk,
          }),
        });

        setExecutionStatus('streaming');

        if (!res.ok) {
          const errData = await res.json().catch(() => ({}));
          throw new Error(errData.message || errData.detail?.message || `API error ${res.status}`);
        }

        const data: GraphRAGQueryResponse = await res.json();
        if (queryId !== latestQueryIdRef.current) return;

        setBackendState('online');
        setBackendMessage(null);
        setExecutionStatus('completed');
        setIlluminatedPath(data);

        const assistantMsg: ChatMessage = {
          id: `asst-${Date.now()}-${queryId}`,
          sender: 'assistant',
          text: data.answer,
          responsePayload: data,
          timestamp: new Date().toLocaleTimeString(),
        };
        setMessages((prev) => [...prev, assistantMsg]);
      } catch (err: unknown) {
        if (queryId !== latestQueryIdRef.current) return;
        const msg = err instanceof Error ? err.message : 'Error executing GraphRAG query.';
        setErrorMsg(msg);
        setExecutionStatus('error');
        const errorChatMsg: ChatMessage = {
          id: `err-${Date.now()}-${queryId}`,
          sender: 'assistant',
          text: `Error: ${msg}`,
          timestamp: new Date().toLocaleTimeString(),
        };
        setMessages((prev) => [...prev, errorChatMsg]);
      } finally {
        if (queryId === latestQueryIdRef.current) {
          setIsQueryLoading(false);
        }
      }
    },
    [filterState, filterJurisdiction, setIlluminatedPath]
  );

  const inquireNode = useCallback(
    async (node: GraphNode) => {
      setIsChatOpen(true);
      const prompt = constructInquiryPrompt(node);
      await submitInquiry(prompt, node.primary_key, DEFAULT_GRAPHRAG_MODEL);
    },
    [submitInquiry]
  );

  const value = useMemo(
    () => ({
      activeNodePKs,
      activeEdgeKeys,
      selectedNode,
      selectedEdge,
      seededAnchor,
      isIlluminated,
      quickPrompts,
      filterJurisdiction,
      filterState,
      filterCategory,
      searchQuery,
      includeFeeSchedules,
      dataSourceMode,
      executionStatus,
      backendState,
      backendMessage,
      availableStates,
      availablePolicies,
      policyKeyword,
      isChatOpen,
      messages,
      isQueryLoading,
      errorMsg,
      focusTarget,
      microFact,
      isMobileViewport,
      selectNode,
      selectEdge,
      setIlluminatedPath,
      clearIllumination,
      setFilterJurisdiction,
      setFilterState,
      setFilterCategory,
      setSearchQuery,
      setIncludeFeeSchedules,
      setDataSourceMode,
      setExecutionStatus,
      setBackendState,
      setBackendMessage,
      setPolicyKeyword,
      setAvailablePolicies,
      setIsChatOpen,
      setFocusTarget,
      submitInquiry,
      inquireNode,
    }),
    [
      activeNodePKs,
      activeEdgeKeys,
      selectedNode,
      selectedEdge,
      seededAnchor,
      isIlluminated,
      quickPrompts,
      filterJurisdiction,
      filterState,
      filterCategory,
      searchQuery,
      includeFeeSchedules,
      dataSourceMode,
      executionStatus,
      backendState,
      backendMessage,
      availableStates,
      availablePolicies,
      policyKeyword,
      isChatOpen,
      messages,
      isQueryLoading,
      errorMsg,
      focusTarget,
      microFact,
      isMobileViewport,
      selectNode,
      selectEdge,
      setIlluminatedPath,
      clearIllumination,
      setFilterJurisdiction,
      setFilterState,
      submitInquiry,
      inquireNode,
    ]
  );

  return <GraphSyncContext.Provider value={value}>{children}</GraphSyncContext.Provider>;
};

export const useGraphSync = (): GraphSyncContextType => {
  const context = useContext(GraphSyncContext);
  if (!context) {
    throw new Error('useGraphSync must be used within a GraphSyncProvider');
  }
  return context;
};
