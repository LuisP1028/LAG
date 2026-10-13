/**
 * Bidirectional Canvas-Agent Synchronization Bus conforming to Ticket 006.
 */

import React, { createContext, useContext, useState, useCallback, useMemo } from 'react';
import type { GraphNode, AnchorEntity, GraphRAGQueryResponse } from '../types/graph';

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
  focusTarget: { x: number; y: number; zoom?: number } | null;
  
  selectNode: (node: GraphNode | null) => void;
  setIlluminatedPath: (response: GraphRAGQueryResponse) => void;
  clearIllumination: () => void;
  setFilterState: (state: string) => void;
  setPolicyKeyword: (keyword: string) => void;
  setIsChatOpen: (open: boolean) => void;
  setFocusTarget: (target: { x: number; y: number; zoom?: number } | null) => void;
}

const GraphSyncContext = createContext<GraphSyncContextType | undefined>(undefined);

export const GraphSyncProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [activeNodePKs, setActiveNodePKs] = useState<Set<string>>(new Set());
  const [activeEdgeKeys, setActiveEdgeKeys] = useState<Set<string>>(new Set());
  const [selectedNode, setSelectedNode] = useState<GraphNode | null>(null);
  const [seededAnchor, setSeededAnchor] = useState<AnchorEntity | null>(null);
  const [isIlluminated, setIsIlluminated] = useState<boolean>(false);
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
      focusTarget,
      selectNode,
      setIlluminatedPath,
      clearIllumination,
      setFilterState,
      setPolicyKeyword,
      setIsChatOpen,
      setFocusTarget,
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
      focusTarget,
      selectNode,
      setIlluminatedPath,
      clearIllumination,
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
