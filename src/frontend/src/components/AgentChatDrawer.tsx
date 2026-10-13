/**
 * Hugging Face GraphRAG conversational assistant drawer with bidirectional path illumination.
 */

import React, { useState } from 'react';
import { useGraphSync } from '../context/GraphSyncContext';
import { CANVAS_PALETTE } from '../styles/graph_theme';

export const AgentChatDrawer: React.FC = () => {
  const {
    isChatOpen,
    setIsChatOpen,
    quickPrompts,
    messages,
    isQueryLoading,
    errorMsg,
    submitInquiry,
    seededAnchor,
  } = useGraphSync();

  const [inputQuery, setInputQuery] = useState<string>('');
  const [modelId, setModelId] = useState<string>('meta-llama/Meta-Llama-3-8B-Instruct');

  if (!isChatOpen) return null;

  const handleSend = async (queryText?: string) => {
    const q = (queryText || inputQuery).trim();
    if (!q || isQueryLoading) return;
    setInputQuery('');
    await submitInquiry(q, seededAnchor?.primary_key, modelId);
  };

  return (
    <div
      style={{
        position: 'absolute',
        top: 0,
        right: 0,
        width: 440,
        height: '100%',
        backgroundColor: CANVAS_PALETTE.panelBg,
        backdropFilter: 'blur(16px)',
        borderLeft: `1px solid ${CANVAS_PALETTE.panelBorder}`,
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
          padding: '16px 20px',
          borderBottom: `1px solid ${CANVAS_PALETTE.panelBorder}`,
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
        }}
      >
        <div>
          <div style={{ color: CANVAS_PALETTE.accentAmber, fontWeight: 700, fontSize: 14, letterSpacing: '0.05em' }}>
            ◈ HUGGING FACE GRAPHRAG ASSISTANT
          </div>
          <div style={{ fontSize: 11, color: CANVAS_PALETTE.textMuted, marginTop: 2 }}>
            Zero-Hallucination Topological Synthesis
          </div>
        </div>

        <button
          onClick={() => setIsChatOpen(false)}
          style={{
            background: 'none',
            border: 'none',
            color: CANVAS_PALETTE.textMuted,
            cursor: 'pointer',
            fontSize: 18,
          }}
        >
          ✕
        </button>
      </div>

      {/* Model Selection Toolbar */}
      <div
        style={{
          padding: '10px 20px',
          backgroundColor: 'rgba(10, 17, 40, 0.65)',
          borderBottom: `1px solid ${CANVAS_PALETTE.panelBorder}`,
          display: 'flex',
          alignItems: 'center',
          gap: 8,
          fontSize: 11,
          fontFamily: '"SF Mono", monospace',
        }}
      >
        <span style={{ color: CANVAS_PALETTE.textMuted }}>MODEL:</span>
        <select
          value={modelId}
          onChange={(e) => setModelId(e.target.value)}
          style={{
            flex: 1,
            backgroundColor: 'rgba(30, 41, 59, 0.8)',
            color: '#f8fafc',
            border: `1px solid ${CANVAS_PALETTE.panelBorder}`,
            borderRadius: 4,
            padding: '4px 6px',
            fontSize: 11,
            cursor: 'pointer',
          }}
        >
          <option value="meta-llama/Meta-Llama-3-8B-Instruct">Llama-3-8B-Instruct</option>
          <option value="mistralai/Mistral-7B-Instruct-v0.3">Mistral-7B-Instruct-v0.3</option>
          <option value="Qwen/Qwen2.5-7B-Instruct">Qwen2.5-7B-Instruct</option>
        </select>
      </div>

      {/* Quick Prompts Bar */}
      <div
        style={{
          padding: '8px 16px',
          borderBottom: `1px solid ${CANVAS_PALETTE.panelBorder}`,
          display: 'flex',
          gap: 6,
          overflowX: 'auto',
          backgroundColor: 'rgba(15, 23, 42, 0.4)',
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
            }}
          >
            {prompt.length > 34 ? prompt.substring(0, 32) + '...' : prompt}
          </button>
        ))}
      </div>

      {/* Messages Thread */}
      <div style={{ flex: 1, overflowY: 'auto', padding: '16px 20px', display: 'flex', flexDirection: 'column', gap: 14 }}>
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
            }}
          >
            <strong>Error:</strong> {errorMsg}
          </div>
        )}
      </div>

      {/* Input Form */}
      <div
        style={{
          padding: '14px 20px',
          borderTop: `1px solid ${CANVAS_PALETTE.panelBorder}`,
          backgroundColor: 'rgba(10, 17, 40, 0.95)',
        }}
      >
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleSend();
          }}
          style={{ display: 'flex', gap: 8 }}
        >
          <input
            type="text"
            value={inputQuery}
            onChange={(e) => setInputQuery(e.target.value)}
            placeholder="Ask Medicare policy question (e.g. Wisconsin breast cancer...)"
            disabled={isQueryLoading}
            style={{
              flex: 1,
              backgroundColor: 'rgba(30, 41, 59, 0.9)',
              color: '#f8fafc',
              border: `1px solid ${CANVAS_PALETTE.panelBorder}`,
              borderRadius: 6,
              padding: '10px 14px',
              fontSize: 13,
              outline: 'none',
            }}
          />
          <button
            type="submit"
            disabled={isQueryLoading || !inputQuery.trim()}
            style={{
              backgroundColor: CANVAS_PALETTE.accentAmber,
              color: '#0a1128',
              fontWeight: 700,
              fontSize: 13,
              border: 'none',
              borderRadius: 6,
              padding: '0 16px',
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
