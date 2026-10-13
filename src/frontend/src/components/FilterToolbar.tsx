/**
 * Top navigation toolbar for state filtering, policy domain selection, and GraphRAG triggers.
 */

import React from 'react';
import { useGraphSync } from '../context/GraphSyncContext';
import { CANVAS_PALETTE } from '../styles/graph_theme';

interface FilterToolbarProps {
  onReloadTopology: (state: string, policy: string) => void;
}

export const FilterToolbar: React.FC<FilterToolbarProps> = ({ onReloadTopology }) => {
  const {
    filterState,
    setFilterState,
    policyKeyword,
    setPolicyKeyword,
    isIlluminated,
    clearIllumination,
    isChatOpen,
    setIsChatOpen,
    physicsFrozen,
    togglePhysicsFrozen,
  } = useGraphSync();

  const handleStateChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const val = e.target.value;
    setFilterState(val);
    onReloadTopology(val, policyKeyword);
  };

  const handlePolicyChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const val = e.target.value;
    setPolicyKeyword(val);
    onReloadTopology(filterState, val);
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
      {/* State Filter Selector */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
        <span style={{ color: CANVAS_PALETTE.textMuted }}>JURISDICTION:</span>
        <select
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
          <option value="WI">Wisconsin (DME MAC B - CGS)</option>
          <option value="IL">Illinois (DME MAC B - CGS)</option>
          <option value="CA">California (DME MAC D - Noridian)</option>
          <option value="NY">New York (DME MAC A - Noridian)</option>
          <option value="TX">Texas (DME MAC C - CGS)</option>
          <option value="">All States (Fees Collapsed - 60 FPS)</option>
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

      {/* Physics Toggle */}
      <button
        onClick={togglePhysicsFrozen}
        style={{
          backgroundColor: physicsFrozen ? 'rgba(234, 179, 8, 0.2)' : 'rgba(30, 41, 59, 0.8)',
          color: physicsFrozen ? '#facc15' : '#e2e8f0',
          border: `1px solid ${physicsFrozen ? '#facc15' : CANVAS_PALETTE.panelBorder}`,
          borderRadius: 4,
          padding: '4px 10px',
          cursor: 'pointer',
          fontSize: 11,
          fontWeight: 600,
        }}
        title="Toggle force physics simulation"
      >
        {physicsFrozen ? '▶ RESUME PHYSICS' : '⏸ FREEZE PHYSICS'}
      </button>

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
