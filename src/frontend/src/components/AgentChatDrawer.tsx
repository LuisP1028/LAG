/**
 * Medical Durable Goods Assistant drawer with DeepSeek micro-fact subtitle and bidirectional path illumination.
 */

import React, { useState } from 'react';
import { useGraphSync, DEFAULT_GRAPHRAG_MODEL } from '../context/GraphSyncContext';
import { CANVAS_PALETTE } from '../styles/graph_theme';

export const AgentChatDrawer: React.FC = () => {
  const {
    isChatOpen,
    setIsChatOpen,
    clearIllumination,
    quickPrompts,
    messages,
    isQueryLoading,
    errorMsg,
    submitInquiry,
    seededAnchor,
    microFact,
    isMobileViewport,
    selectedNode,
    selectedEdge,
  } = useGraphSync();

  const [inputQuery, setInputQuery] = useState<string>('');

  if (!isChatOpen) return null;

  const handleSend = async (queryText?: string) => {
    const q = (queryText || inputQuery).trim();
    if (!q || isQueryLoading) return;
    setInputQuery('');
    await submitInquiry(q, seededAnchor?.primary_key, DEFAULT_GRAPHRAG_MODEL);
  };

  return (
    <div
      data-testid="agent-chat-drawer"
      style={{
        position: 'absolute',
        top: 0,
        right: 0,
        left: isMobileViewport ? 0 : 'auto',
        width: isMobileViewport ? '100%' : 440,
        maxWidth: isMobileViewport ? '100vw' : '45vw',
        height: '100%',
        boxSizing: 'border-box',
        backgroundColor: CANVAS_PALETTE.panelBg,
        backdropFilter: 'blur(16px)',
        borderLeft: isMobileViewport ? 'none' : `1px solid ${CANVAS_PALETTE.panelBorder}`,
        boxShadow: '-10px 0 32px rgba(0, 0, 0, 0.7)',
        display: 'flex',
        flexDirection: 'column',
        zIndex: 30,
        color: CANVAS_PALETTE.textPrimary,
        fontFamily: 'system-ui, -apple-system, sans-serif',
      }}
    >
      {/* Header */}
      <div
        style={{
          padding: isMobileViewport
            ? 'calc(14px + env(safe-area-inset-top, 0px)) 16px 12px'
            : '16px 20px',
          borderBottom: `1px solid ${CANVAS_PALETTE.panelBorder}`,
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'flex-start',
          gap: 10,
          flexShrink: 0,
        }}
      >
        <div style={{ minWidth: 0, flex: 1 }}>
          <div
            data-testid="assistant-drawer-title"
            style={{
              color: CANVAS_PALETTE.accentAmber,
              fontWeight: 700,
              fontSize: 14,
              letterSpacing: '0.05em',
            }}
          >
            ◈ Medical Durable Goods Assistant
          </div>
          <div
            data-testid="assistant-micro-fact-subtitle"
            style={{
              fontSize: 11,
              color: CANVAS_PALETTE.textMuted,
              marginTop: 2,
              lineHeight: 1.35,
            }}
          >
            {`Fun fact: ${microFact.replace(/^Fun fact:\s*/i, '')}`}
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: 8, flexShrink: 0 }}>
          {isMobileViewport && (selectedNode || selectedEdge) && (
            <button
              type="button"
              data-testid="mobile-return-to-node-btn"
              onClick={() => setIsChatOpen(false)}
              style={{
                backgroundColor: 'rgba(56, 189, 248, 0.16)',
                color: '#38bdf8',
                border: '1px solid rgba(56, 189, 248, 0.45)',
                borderRadius: 4,
                padding: '4px 8px',
                fontSize: 11,
                fontWeight: 600,
                cursor: 'pointer',
                whiteSpace: 'nowrap',
              }}
              title="Return to Entity Inspection"
            >
              ← Inspect {selectedNode ? selectedNode.primary_key : 'Edge'}
            </button>
          )}
          <button
            data-testid="close-chat-drawer-btn"
            onClick={() => {
              clearIllumination();
              setIsChatOpen(false);
            }}
            style={{
              background: 'none',
              border: 'none',
              color: CANVAS_PALETTE.textMuted,
              cursor: 'pointer',
              fontSize: 18,
              padding: 4,
            }}
          >
            ✕
          </button>
        </div>
      </div>

      {/* Quick Prompts Bar */}
      <div
        style={{
          padding: isMobileViewport ? '8px 14px' : '8px 16px',
          borderBottom: `1px solid ${CANVAS_PALETTE.panelBorder}`,
          display: 'flex',
          gap: 6,
          overflowX: 'auto',
          WebkitOverflowScrolling: 'touch',
          backgroundColor: 'rgba(15, 23, 42, 0.4)',
          flexShrink: 0,
        }}
      >
        {quickPrompts.slice(0, 3).map((prompt, idx) => (
          <button
            key={idx}
            onClick={() => handleSend(prompt)}
            disabled={isQueryLoading}
            style={{
              whiteSpace: 'nowrap',
              backgroundColor: 'rgba(30, 41, 59, 0.8)',
              border: '1px solid rgba(255, 183, 3, 0.3)',
              borderRadius: 12,
              padding: '4px 10px',
              fontSize: 11,
              color: '#f1f5f9',
              cursor: 'pointer',
              flexShrink: 0,
            }}
          >
            {prompt.length > 34 ? prompt.substring(0, 32) + '...' : prompt}
          </button>
        ))}
      </div>

      {/* Messages Thread */}
      <div
        data-testid="agent-chat-messages"
        style={{
          flex: 1,
          minHeight: 0,
          overflowY: 'auto',
          WebkitOverflowScrolling: 'touch',
          padding: isMobileViewport ? '14px 16px' : '16px 20px',
          display: 'flex',
          flexDirection: 'column',
          gap: 14,
        }}
      >
        {messages.map((msg) => (
          <div
            key={msg.id}
            style={{
              alignSelf: msg.sender === 'user' ? 'flex-end' : 'flex-start',
              maxWidth: '92%',
              backgroundColor: msg.sender === 'user' ? '#1e3a8a' : 'rgba(30, 41, 59, 0.7)',
              border: `1px solid ${msg.sender === 'user' ? '#2563eb' : CANVAS_PALETTE.panelBorder}`,
              borderRadius: 8,
              padding: '12px 14px',
              fontSize: 13,
              lineHeight: 1.45,
              wordBreak: 'break-word',
            }}
          >
            {/* Header */}
            <div
              style={{
                display: 'flex',
                justifyContent: 'space-between',
                fontSize: 10,
                color: msg.sender === 'user' ? '#93c5fd' : CANVAS_PALETTE.accentAmber,
                fontWeight: 700,
                marginBottom: 6,
                letterSpacing: '0.04em',
              }}
            >
              <span>{msg.sender === 'user' ? 'USER INQUIRY' : 'GRAPHRAG SYNTHESIS'}</span>
              <span style={{ color: CANVAS_PALETTE.textMuted }}>{msg.timestamp}</span>
            </div>

            {/* Message Body */}
            <div style={{ whiteSpace: 'pre-line', color: '#f8fafc' }}>
              {msg.text}
            </div>

            {/* Response Telemetry Badge */}
            {msg.responsePayload && (
              <div
                style={{
                  marginTop: 10,
                  paddingTop: 8,
                  borderTop: `1px solid ${CANVAS_PALETTE.panelBorder}`,
                  fontSize: 10,
                  fontFamily: '"SF Mono", monospace',
                  color: CANVAS_PALETTE.textMuted,
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  flexWrap: 'wrap',
                  gap: 6,
                }}
              >
                <span>⚡ Latency: <strong style={{ color: '#4ade80' }}>{msg.responsePayload.duration_ms}ms</strong></span>
                <span>◈ <strong style={{ color: CANVAS_PALETTE.accentAmber }}>{msg.responsePayload.active_node_pks.length}</strong> Nodes Illuminated</span>
              </div>
            )}
          </div>
        ))}

        {isQueryLoading && (
          <div
            style={{
              padding: '12px 14px',
              backgroundColor: 'rgba(30, 41, 59, 0.5)',
              borderRadius: 8,
              border: `1px solid ${CANVAS_PALETTE.panelBorder}`,
              fontFamily: 'monospace',
              fontSize: 12,
              color: CANVAS_PALETTE.accentAmber,
            }}
          >
            ◈ Traversing topological subgraph & synthesizing grounded guidance...
          </div>
        )}

        {errorMsg && (
          <div
            style={{
              padding: '10px 14px',
              backgroundColor: 'rgba(225, 29, 72, 0.2)',
              border: '1px solid #fb7185',
              borderRadius: 6,
              color: '#fecdd3',
              fontSize: 12,
              wordBreak: 'break-word',
            }}
          >
            <strong>Error:</strong> {errorMsg}
          </div>
        )}
      </div>

      {/* Input Form */}
      <div
        data-testid="agent-chat-input-bar"
        style={{
          padding: isMobileViewport
            ? '12px 14px calc(16px + env(safe-area-inset-bottom, 0px))'
            : '14px 20px calc(14px + env(safe-area-inset-bottom, 0px))',
          borderTop: `1px solid ${CANVAS_PALETTE.panelBorder}`,
          backgroundColor: 'rgba(10, 17, 40, 0.98)',
          flexShrink: 0,
        }}
      >
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleSend();
          }}
          style={{ display: 'flex', alignItems: 'center', gap: 8, width: '100%' }}
        >
          <input
            type="text"
            data-testid="agent-chat-input"
            value={inputQuery}
            onChange={(e) => setInputQuery(e.target.value)}
            placeholder="Ask Medicare policy question (e.g. Wisconsin breast cancer...)"
            disabled={isQueryLoading}
            style={{
              flex: 1,
              minWidth: 0,
              backgroundColor: 'rgba(30, 41, 59, 0.9)',
              color: '#f8fafc',
              border: `1px solid ${CANVAS_PALETTE.panelBorder}`,
              borderRadius: 6,
              padding: '10px 12px',
              fontSize: isMobileViewport ? 16 : 13,
              outline: 'none',
            }}
          />
          <button
            type="submit"
            data-testid="agent-chat-send-btn"
            disabled={isQueryLoading || !inputQuery.trim()}
            style={{
              backgroundColor: CANVAS_PALETTE.accentAmber,
              color: '#0a1128',
              fontWeight: 700,
              fontSize: 13,
              border: 'none',
              borderRadius: 6,
              padding: '0 16px',
              minHeight: 40,
              flexShrink: 0,
              cursor: isQueryLoading ? 'not-allowed' : 'pointer',
              boxShadow: '0 2px 8px rgba(255, 183, 3, 0.3)',
            }}
          >
            Send
          </button>
        </form>
      </div>
    </div>
  );
};
