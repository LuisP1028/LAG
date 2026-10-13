/**
 * Top navigation toolbar for state filtering, policy domain selection, and GraphRAG triggers.
 */

import React from 'react';
import { useGraphSync, STATE_TO_JURISDICTION } from '../context/GraphSyncContext';
import { CANVAS_PALETTE } from '../styles/graph_theme';

interface FilterToolbarProps {
  onReloadTopology: (state: string, policy: string, jurisdiction: string) => void;
}

export const FilterToolbar: React.FC<FilterToolbarProps> = ({ onReloadTopology }) => {
  const {
    filterJurisdiction,
    setFilterJurisdiction,
    filterState,
    setFilterState,
    availableStates,
    policyKeyword,
    setPolicyKeyword,
    isIlluminated,
    clearIllumination,
    isChatOpen,
    setIsChatOpen,
  } = useGraphSync();

  const handleJurisdictionChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const jurisVal = e.target.value;
    setFilterJurisdiction(jurisVal);
    onReloadTopology('', policyKeyword, jurisVal);
  };

  const handleStateChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const stateVal = e.target.value;
    setFilterState(stateVal);
    const parentJuris = stateVal ? (STATE_TO_JURISDICTION[stateVal] || filterJurisdiction) : filterJurisdiction;
    onReloadTopology(stateVal, policyKeyword, parentJuris);
  };

  const handlePolicyChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const val = e.target.value;
    setPolicyKeyword(val);
    onReloadTopology(filterState, val, filterJurisdiction);
  };

  return (
    <div
      style={{
        position: 'absolute',
        top: 14,
        right: 14,
        display: 'flex',
        alignItems: 'center',
        gap: 10,
        zIndex: 10,
        backgroundColor: 'rgba(15, 23, 42, 0.90)',
        backdropFilter: 'blur(8px)',
        border: `1px solid ${CANVAS_PALETTE.panelBorder}`,
        padding: '6px 12px',
        borderRadius: 8,
        boxShadow: '0 4px 16px rgba(0, 0, 0, 0.4)',
        fontFamily: '"SF Mono", "Fira Code", monospace',
        fontSize: 12,
      }}
    >
      {/* Dedicated Jurisdiction Selector (Requirement 5.1.1) */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
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
            padding: '4px 8px',
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

      {/* Dedicated State Selector (Requirement 5.1.2) */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
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
            padding: '4px 8px',
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

      {/* Policy Selector */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
        <span style={{ color: CANVAS_PALETTE.textMuted }}>POLICY:</span>
        <select
          value={policyKeyword}
          onChange={handlePolicyChange}
          style={{
            backgroundColor: 'rgba(30, 41, 59, 0.8)',
            color: '#f8fafc',
            border: `1px solid ${CANVAS_PALETTE.panelBorder}`,
            borderRadius: 4,
            padding: '4px 8px',
            fontSize: 11,
            cursor: 'pointer',
          }}
        >
          <option value="LTA">LTA (Lymphedema)</option>
          <option value="IVIG">IVIG (Immune Globulin)</option>
          <option value="ALL">All (Omnibus Lineage)</option>
        </select>
      </div>

      {/* Clear Illumination Button */}
      {isIlluminated && (
        <button
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
