/**
 * Top navigation toolbar for state filtering, dynamic policy domain selection,
 * entity category filtering, lexical node search, fee schedule toggle,
 * pre-computed run switching, and GraphRAG execution status telemetry.
 */

import React, { useState } from 'react';
import { useGraphSync, STATE_TO_JURISDICTION } from '../context/GraphSyncContext';
import { CANVAS_PALETTE, NODE_VISUAL_REGISTRY } from '../styles/graph_theme';
import type { DataSourceMode } from '../types/graph';
import { getApiBaseUrl, setRuntimeApiBaseUrl } from '../utils/apiConfig';

interface FilterToolbarProps {
  onReloadTopology: (
    state: string,
    policy: string,
    jurisdiction: string,
    includeFeeSchedules?: boolean,
    modeOverride?: DataSourceMode
  ) => void;
}

const CANONICAL_CATEGORIES = Object.keys(NODE_VISUAL_REGISTRY);

export const FilterToolbar: React.FC<FilterToolbarProps> = ({ onReloadTopology }) => {
  const [showApiConfig, setShowApiConfig] = useState<boolean>(false);
  const [customApiUrl, setCustomApiUrl] = useState<string>(() => getApiBaseUrl());

  const {
    filterJurisdiction,
    setFilterJurisdiction,
    filterState,
    setFilterState,
    filterCategory,
    setFilterCategory,
    searchQuery,
    setSearchQuery,
    includeFeeSchedules,
    setIncludeFeeSchedules,
    availableStates,
    availablePolicies,
    policyKeyword,
    setPolicyKeyword,
    dataSourceMode,
    setDataSourceMode,
    executionStatus,
    backendState,
    isIlluminated,
    clearIllumination,
    isChatOpen,
    setIsChatOpen,
    selectedNode,
    selectedEdge,
  } = useGraphSync();

  const handleApplyApiUrl = (e: React.FormEvent) => {
    e.preventDefault();
    setRuntimeApiBaseUrl(customApiUrl);
    setDataSourceMode('live');
    setShowApiConfig(false);
    onReloadTopology(filterState, policyKeyword, filterJurisdiction, includeFeeSchedules, 'live');
  };

  const handleDataSourceModeChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const mode = e.target.value as DataSourceMode;
    setDataSourceMode(mode);
    const nextPolicy =
      mode === 'precomputed_ivig' ? 'IVIG' : mode === 'precomputed_lta' ? 'LTA' : policyKeyword;
    if (nextPolicy !== policyKeyword) {
      setPolicyKeyword(nextPolicy);
    }
    onReloadTopology(filterState, nextPolicy, filterJurisdiction, includeFeeSchedules, mode);
  };

  const handleJurisdictionChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const jurisVal = e.target.value;
    setFilterJurisdiction(jurisVal);
    onReloadTopology('', policyKeyword, jurisVal, includeFeeSchedules, dataSourceMode);
  };

  const handleStateChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const stateVal = e.target.value;
    setFilterState(stateVal);
    const parentJuris = stateVal ? (STATE_TO_JURISDICTION[stateVal] || filterJurisdiction) : filterJurisdiction;
    onReloadTopology(stateVal, policyKeyword, parentJuris, includeFeeSchedules, dataSourceMode);
  };

  const handlePolicyChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const val = e.target.value;
    setPolicyKeyword(val);
    onReloadTopology(filterState, val, filterJurisdiction, includeFeeSchedules, dataSourceMode);
  };

  const handleFeeToggle = (e: React.ChangeEvent<HTMLInputElement>) => {
    const checked = e.target.checked;
    setIncludeFeeSchedules(checked);
    onReloadTopology(filterState, policyKeyword, filterJurisdiction, checked, dataSourceMode);
  };

  const getStatusBadgeStyle = (): { label: string; bg: string; border: string; color: string } => {
    switch (executionStatus) {
      case 'executing':
        return {
          label: '● EXECUTING PIPELINE',
          bg: 'rgba(255, 183, 3, 0.2)',
          border: '#ffb703',
          color: '#ffd166',
        };
      case 'cached':
        return {
          label: '◆ CACHED SNAPSHOT',
          bg: 'rgba(56, 189, 248, 0.2)',
          border: '#38bdf8',
          color: '#7dd3fc',
        };
      case 'error':
        return {
          label: '▲ EXECUTION ERROR',
          bg: 'rgba(225, 29, 72, 0.25)',
          border: '#fb7185',
          color: '#fda4af',
        };
      case 'idle':
      default:
        return {
          label: backendState === 'online' ? '● READY (LIVE API)' : '○ STANDBY',
          bg: 'rgba(16, 185, 129, 0.15)',
          border: '#10b981',
          color: '#6ee7b7',
        };
    }
  };

  const statusBadge = getStatusBadgeStyle();
  const isInspectionOpen = Boolean(selectedNode || selectedEdge);

  return (
    <div
      data-testid="filter-toolbar"
      style={{
        position: 'absolute',
        top: 14,
        right: 14,
        left: isInspectionOpen ? 'min(404px, calc(45vw + 14px))' : 14,
        display: 'flex',
        flexWrap: 'wrap',
        alignItems: 'center',
        justifyContent: 'flex-end',
        gap: 8,
        zIndex: 10,
        backgroundColor: 'rgba(15, 23, 42, 0.92)',
        backdropFilter: 'blur(8px)',
        border: `1px solid ${CANVAS_PALETTE.panelBorder}`,
        padding: '6px 12px',
        borderRadius: 8,
        boxShadow: '0 4px 16px rgba(0, 0, 0, 0.4)',
        fontFamily: '"SF Mono", "Fira Code", monospace',
        fontSize: 11,
      }}
    >
      {/* Execution Mode / Pre-computed Run Selector */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 5 }}>
        <span style={{ color: CANVAS_PALETTE.textMuted }}>SOURCE:</span>
        <select
          aria-label="RUN SOURCE"
          data-testid="run-mode-select"
          value={dataSourceMode}
          onChange={handleDataSourceModeChange}
          style={{
            backgroundColor: 'rgba(30, 41, 59, 0.9)',
            color: '#f8fafc',
            border: `1px solid ${CANVAS_PALETTE.panelBorder}`,
            borderRadius: 4,
            padding: '4px 6px',
            fontSize: 11,
            cursor: 'pointer',
          }}
        >
          <option value="live">Live Container API (Public HTTPS)</option>
          <option value="precomputed_lta">Pre-computed Run: LTA (3,875 Nodes)</option>
          <option value="precomputed_ivig">Pre-computed Run: IVIG (8-Hop Chain)</option>
        </select>
        <button
          type="button"
          data-testid="api-url-config-btn"
          onClick={() => {
            setCustomApiUrl(getApiBaseUrl());
            setShowApiConfig((prev) => !prev);
          }}
          style={{
            backgroundColor: 'rgba(30, 41, 59, 0.9)',
            color: '#38bdf8',
            border: `1px solid ${CANVAS_PALETTE.panelBorder}`,
            borderRadius: 4,
            padding: '4px 6px',
            fontSize: 10,
            cursor: 'pointer',
            fontWeight: 600,
          }}
          title="Configure Live HTTPS Tunnel URL"
        >
          ⚙ URL
        </button>
      </div>

      {showApiConfig && (
        <form
          onSubmit={handleApplyApiUrl}
          style={{ display: 'flex', alignItems: 'center', gap: 4 }}
        >
          <input
            type="text"
            aria-label="LIVE API HTTPS URL"
            data-testid="api-url-input"
            placeholder="https://*.trycloudflare.com"
            value={customApiUrl}
            onChange={(e) => setCustomApiUrl(e.target.value)}
            style={{
              backgroundColor: 'rgba(15, 23, 42, 0.95)',
              color: '#f8fafc',
              border: '1px solid #38bdf8',
              borderRadius: 4,
              padding: '4px 8px',
              fontSize: 11,
              width: 220,
              outline: 'none',
            }}
          />
          <button
            type="submit"
            data-testid="api-url-apply-btn"
            style={{
              backgroundColor: '#38bdf8',
              color: '#0f172a',
              border: 'none',
              borderRadius: 4,
              padding: '4px 8px',
              fontSize: 10,
              fontWeight: 700,
              cursor: 'pointer',
            }}
          >
            Connect
          </button>
        </form>
      )}

      {/* Dedicated Jurisdiction Selector */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 5 }}>
        <span style={{ color: CANVAS_PALETTE.textMuted }}>JURISDICTION:</span>
        <select
          aria-label="JURISDICTION"
          data-testid="jurisdiction-select"
          value={filterJurisdiction}
          onChange={handleJurisdictionChange}
          style={{
            backgroundColor: 'rgba(30, 41, 59, 0.8)',
            color: '#f8fafc',
            border: `1px solid ${CANVAS_PALETTE.panelBorder}`,
            borderRadius: 4,
            padding: '4px 6px',
            fontSize: 11,
            cursor: 'pointer',
          }}
        >
          <option value="">All Jurisdictions (National Overview)</option>
          <option value="JURIS-DME-A">Jurisdiction A (Northeast - Noridian)</option>
          <option value="JURIS-DME-B">Jurisdiction B (Midwest - CGS)</option>
          <option value="JURIS-DME-C">Jurisdiction C (South - CGS)</option>
          <option value="JURIS-DME-D">Jurisdiction D (West - Noridian)</option>
        </select>
      </div>

      {/* Dedicated State Selector (54 US States & Territories) */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 5 }}>
        <span style={{ color: CANVAS_PALETTE.textMuted }}>STATE:</span>
        <select
          aria-label="STATE"
          data-testid="state-select"
          value={filterState}
          onChange={handleStateChange}
          style={{
            backgroundColor: 'rgba(30, 41, 59, 0.8)',
            color: '#f8fafc',
            border: `1px solid ${CANVAS_PALETTE.panelBorder}`,
            borderRadius: 4,
            padding: '4px 6px',
            fontSize: 11,
            cursor: 'pointer',
          }}
        >
          <option value="">All States (Overview)</option>
          {availableStates.map((st) => (
            <option key={st.code} value={st.code}>
              {st.name} ({st.code})
            </option>
          ))}
        </select>
      </div>

      {/* Dynamic Policy Selector populated from persisted Policy nodes */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 5 }}>
        <span style={{ color: CANVAS_PALETTE.textMuted }}>POLICY:</span>
        <select
          aria-label="POLICY"
          data-testid="policy-select"
          value={policyKeyword}
          onChange={handlePolicyChange}
          style={{
            backgroundColor: 'rgba(30, 41, 59, 0.8)',
            color: '#f8fafc',
            border: `1px solid ${CANVAS_PALETTE.panelBorder}`,
            borderRadius: 4,
            padding: '4px 6px',
            fontSize: 11,
            cursor: 'pointer',
          }}
        >
          {availablePolicies.map((pol) => (
            <option key={pol.keyword} value={pol.keyword}>
              {pol.label}
            </option>
          ))}
          <option value="ALL">All Ingested Policies</option>
        </select>
      </div>

      {/* Entity Category Filter across all 17 categories */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 5 }}>
        <span style={{ color: CANVAS_PALETTE.textMuted }}>CATEGORY:</span>
        <select
          aria-label="CATEGORY"
          data-testid="category-select"
          value={filterCategory}
          onChange={(e) => setFilterCategory(e.target.value)}
          style={{
            backgroundColor: 'rgba(30, 41, 59, 0.8)',
            color: '#f8fafc',
            border: `1px solid ${CANVAS_PALETTE.panelBorder}`,
            borderRadius: 4,
            padding: '4px 6px',
            fontSize: 11,
            cursor: 'pointer',
          }}
        >
          <option value="">All 17 Categories</option>
          {CANONICAL_CATEGORIES.map((cat) => (
            <option key={cat} value={cat}>
              {cat}
            </option>
          ))}
        </select>
      </div>

      {/* Lexical Node Search Input */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 5 }}>
        <input
          type="text"
          aria-label="SEARCH NODES"
          data-testid="node-search-input"
          placeholder="Search PK, code, title..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          style={{
            backgroundColor: 'rgba(30, 41, 59, 0.9)',
            color: '#f8fafc',
            border: `1px solid ${CANVAS_PALETTE.panelBorder}`,
            borderRadius: 4,
            padding: '4px 8px',
            fontSize: 11,
            width: 150,
            outline: 'none',
          }}
        />
        {searchQuery && (
          <button
            data-testid="clear-search-btn"
            onClick={() => setSearchQuery('')}
            style={{
              background: 'none',
              border: 'none',
              color: CANVAS_PALETTE.textMuted,
              cursor: 'pointer',
              fontSize: 11,
              padding: '0 4px',
            }}
            title="Clear search"
          >
            ✕
          </button>
        )}
      </div>

      {/* Fee Schedule Expansion Toggle */}
      <label
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: 4,
          color: CANVAS_PALETTE.textPrimary,
          cursor: 'pointer',
          fontSize: 11,
          userSelect: 'none',
        }}
      >
        <input
          type="checkbox"
          data-testid="fee-schedule-toggle"
          checked={includeFeeSchedules || Boolean(filterState)}
          onChange={handleFeeToggle}
          style={{ cursor: 'pointer' }}
        />
        <span>FEE RATES</span>
      </label>

      {/* Execution Status Badge */}
      <div
        data-testid="execution-status-badge"
        style={{
          backgroundColor: statusBadge.bg,
          border: `1px solid ${statusBadge.border}`,
          color: statusBadge.color,
          padding: '3px 8px',
          borderRadius: 4,
          fontSize: 10,
          fontWeight: 700,
          letterSpacing: '0.03em',
        }}
      >
        {statusBadge.label}
      </div>

      {/* Clear Illumination Button */}
      {isIlluminated && (
        <button
          data-testid="reset-path-btn"
          onClick={clearIllumination}
          style={{
            backgroundColor: 'rgba(225, 29, 72, 0.2)',
            color: '#fb7185',
            border: '1px solid #fb7185',
            borderRadius: 4,
            padding: '4px 10px',
            cursor: 'pointer',
            fontSize: 11,
            fontWeight: 600,
          }}
        >
          ✕ RESET PATH
        </button>
      )}

      {/* Chat Drawer Toggle */}
      <button
        data-testid="graphrag-chat-toggle"
        onClick={() => setIsChatOpen(!isChatOpen)}
        style={{
          backgroundColor: CANVAS_PALETTE.accentAmber,
          color: '#0a1128',
          border: 'none',
          borderRadius: 4,
          padding: '5px 12px',
          cursor: 'pointer',
          fontSize: 11,
          fontWeight: 700,
          display: 'flex',
          alignItems: 'center',
          gap: 6,
          boxShadow: '0 2px 8px rgba(255, 183, 3, 0.3)',
        }}
      >
        ◈ GRAPHRAG CHAT
      </button>
    </div>
  );
};

