/**
 * Bidirectional Canvas-Agent Synchronization Bus conforming to Ticket 006 and functional_specification_007.
 */

import React, { createContext, useContext, useState, useCallback, useMemo } from 'react';
import type { GraphNode, AnchorEntity, GraphRAGQueryResponse } from '../types/graph';
import { constructInquiryPrompt } from '../utils/promptGenerator';

export interface ChatMessage {
  id: string;
  sender: 'user' | 'assistant';
  text: string;
  responsePayload?: GraphRAGQueryResponse;
  timestamp: string;
}

interface GraphSyncContextType {
  activeNodePKs: Set<string>;
  activeEdgeKeys: Set<string>;
  selectedNode: GraphNode | null;
  seededAnchor: AnchorEntity | null;
  isIlluminated: boolean;
  quickPrompts: string[];
  filterState: string;
  policyKeyword: string;
  isChatOpen: boolean;
  messages: ChatMessage[];
  isQueryLoading: boolean;
  errorMsg: string | null;
  focusTarget: { x: number; y: number; zoom?: number } | null;
  
  selectNode: (node: GraphNode | null) => void;
  setIlluminatedPath: (response: GraphRAGQueryResponse) => void;
  clearIllumination: () => void;
  setFilterState: (state: string) => void;
  setPolicyKeyword: (keyword: string) => void;
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
  const [seededAnchor, setSeededAnchor] = useState<AnchorEntity | null>(null);
  const [isIlluminated, setIsIlluminated] = useState<boolean>(false);
  const [isQueryLoading, setIsQueryLoading] = useState<boolean>(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: 'welcome-1',
      sender: 'assistant',
      text: "Welcome to the LAG Policy GraphRAG Intelligence Terminal. You can ask natural language clinical, geographic, or macro legislative questions, or select any node on the blueprint canvas to seed a targeted inquiry.",
      timestamp: new Date().toLocaleTimeString(),
    },
  ]);
  const [quickPrompts, setQuickPrompts] = useState<string[]>([
    "I am from Wisconsin, survived breast cancer, need lymphedema supplies, I'm on Medicare, can you help?",
    "How do IVIG and LTA converge under federal law?",
    "What diagnoses are approved under CMS MCD A59508?",
    "What is the allowable Medicare reimbursement for A6522 in Wisconsin?",
  ]);
  const [filterState, setFilterState] = useState<string>("WI");
  const [policyKeyword, setPolicyKeyword] = useState<string>("LTA");
  const [isChatOpen, setIsChatOpen] = useState<boolean>(false);
  const [focusTarget, setFocusTarget] = useState<{ x: number; y: number; zoom?: number } | null>(null);

  const selectNode = useCallback((node: GraphNode | null) => {
    setSelectedNode(node);
    if (!node) {
      setSeededAnchor(null);
      return;
    }

    // Seed anchor for GraphRAG
    const anchor: AnchorEntity = {
      slot: node.label.toLowerCase(),
      primary_key: node.primary_key,
      matched_text: node.name,
      entity_type: node.label,
      label: node.label,
    };
    setSeededAnchor(anchor);

    // Contextual Quick-Action Prompts based on selected label
    const prompts: string[] = [];
    switch (node.label) {
      case 'CoveragePolicy':
        prompts.push(`What diagnoses are approved under ${node.name}?`);
        prompts.push(`List all covered HCPCS procedure codes governed by ${node.primary_key}`);
        prompts.push(`What is the governing statutory authority for ${node.primary_key}?`);
        break;
      case 'Jurisdiction':
        prompts.push(`What states does ${node.name} cover?`);
        prompts.push(`Show active change requests for ${node.primary_key}`);
        break;
      case 'HCPCSCode':
        prompts.push(`What is the allowable Medicare reimbursement for ${node.primary_key} in Wisconsin?`);
        prompts.push(`What clinical documentation is required to prescribe ${node.primary_key}?`);
        break;
      case 'Policy':
        prompts.push(`How did ${node.name} converge with IVIG under federal law?`);
        prompts.push(`What Public Law enacted ${node.name}?`);
        break;
      case 'State':
        prompts.push(`What DME MAC jurisdiction covers ${node.name}?`);
        prompts.push(`What are the allowable compression rates in ${node.name}?`);
        break;
      case 'ICD10Code':
        prompts.push(`What coverage policies allow diagnosis ${node.primary_key}?`);
        prompts.push(`Can a patient in Wisconsin get compression garments for ${node.name}?`);
        break;
      default:
        prompts.push(`Explain the legislative and operational lineage of ${node.primary_key}`);
        prompts.push(`What policies connect to ${node.name}?`);
    }
    setQuickPrompts(prompts);
  }, []);

  const setIlluminatedPath = useCallback((response: GraphRAGQueryResponse) => {
    setActiveNodePKs(new Set(response.active_node_pks));
    setActiveEdgeKeys(new Set(response.active_edge_keys));
    setIsIlluminated(true);
  }, []);

  const clearIllumination = useCallback(() => {
    setActiveNodePKs(new Set());
    setActiveEdgeKeys(new Set());
    setIsIlluminated(false);
  }, []);

  const submitInquiry = useCallback(
    async (queryText: string, anchorPk?: string, modelId?: string) => {
      const q = queryText.trim();
      if (!q || isQueryLoading) return;

      setErrorMsg(null);
      const userMsg: ChatMessage = {
        id: `user-${Date.now()}`,
        sender: 'user',
        text: q,
        timestamp: new Date().toLocaleTimeString(),
      };
      setMessages((prev) => [...prev, userMsg]);
      setIsQueryLoading(true);

      try {
        const res = await fetch('/api/graphrag/query', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            query: q,
            model_id: modelId || 'meta-llama/Meta-Llama-3-8B-Instruct',
            state_code: filterState || 'WI',
            primary_key: anchorPk,
          }),
        });

        if (!res.ok) {
          const errData = await res.json().catch(() => ({}));
          throw new Error(errData.message || errData.detail?.message || `API error ${res.status}`);
        }

        const data: GraphRAGQueryResponse = await res.json();
        setIlluminatedPath(data);

        const assistantMsg: ChatMessage = {
          id: `asst-${Date.now()}`,
          sender: 'assistant',
          text: data.answer,
          responsePayload: data,
          timestamp: new Date().toLocaleTimeString(),
        };
        setMessages((prev) => [...prev, assistantMsg]);
      } catch (err: any) {
        const msg = err.message || 'Error executing GraphRAG query.';
        setErrorMsg(msg);
        const errorChatMsg: ChatMessage = {
          id: `err-${Date.now()}`,
          sender: 'assistant',
          text: `Error: ${msg}`,
          timestamp: new Date().toLocaleTimeString(),
        };
        setMessages((prev) => [...prev, errorChatMsg]);
      } finally {
        setIsQueryLoading(false);
      }
    },
    [filterState, isQueryLoading, setIlluminatedPath]
  );

  const inquireNode = useCallback(
    async (node: GraphNode) => {
      setIsChatOpen(true);
      const prompt = constructInquiryPrompt(node);
      await submitInquiry(prompt, node.primary_key);
    },
    [submitInquiry]
  );

  const value = useMemo(
    () => ({
      activeNodePKs,
      activeEdgeKeys,
      selectedNode,
      seededAnchor,
      isIlluminated,
      quickPrompts,
      filterState,
      policyKeyword,
      isChatOpen,
      messages,
      isQueryLoading,
      errorMsg,
      focusTarget,
      selectNode,
      setIlluminatedPath,
      clearIllumination,
      setFilterState,
      setPolicyKeyword,
      setIsChatOpen,
      setFocusTarget,
      submitInquiry,
      inquireNode,
    }),
    [
      activeNodePKs,
      activeEdgeKeys,
      selectedNode,
      seededAnchor,
      isIlluminated,
      quickPrompts,
      filterState,
      policyKeyword,
      isChatOpen,
      messages,
      isQueryLoading,
      errorMsg,
      focusTarget,
      selectNode,
      setIlluminatedPath,
      clearIllumination,
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
