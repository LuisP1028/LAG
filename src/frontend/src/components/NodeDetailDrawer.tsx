/**
 * Dedicated node detail inspection drawer conforming to Ticket 005 Section 2.5.
 */

import React from 'react';
import { useGraphSync } from '../context/GraphSyncContext';
import { getNodeVisual, CANVAS_PALETTE } from '../styles/graph_theme';
import type { GraphNode, GraphLink } from '../types/graph';

interface NodeDetailDrawerProps {
  nodes: GraphNode[];
  links: GraphLink[];
}

export const NodeDetailDrawer: React.FC<NodeDetailDrawerProps> = ({ nodes, links }) => {
  const { selectedNode, selectNode, setIsChatOpen } = useGraphSync();

  if (!selectedNode) return null;

  const visual = getNodeVisual(selectedNode.label);
  const props = selectedNode.properties || {};

  // Find immediate incoming and outgoing relationships
  const connectedNeighbors = links
    .filter((l) => {
      const srcPk = typeof l.source === 'object' ? (l.source as GraphNode).primary_key : l.source;
      const tgtPk = typeof l.target === 'object' ? (l.target as GraphNode).primary_key : l.target;
      return srcPk === selectedNode.primary_key || tgtPk === selectedNode.primary_key;
    })
    .map((l) => {
      const srcPk = typeof l.source === 'object' ? (l.source as GraphNode).primary_key : (l.source as string);
      const tgtPk = typeof l.target === 'object' ? (l.target as GraphNode).primary_key : (l.target as string);
      const isOutgoing = srcPk === selectedNode.primary_key;
      const neighborPk = isOutgoing ? tgtPk : srcPk;
      const neighborNode = nodes.find((n) => n.primary_key === neighborPk);
      return {
        direction: isOutgoing ? 'OUTGOING' : 'INCOMING',
        relLabel: l.label,
        neighborPk,
        neighborName: neighborNode?.name || neighborPk,
        neighborLabel: neighborNode?.label || 'Node',
        neighborNode,
      };
    });

  // Construct official government external links
  const getGovernmentSourceLink = () => {
    const getOrdinal = (n: number): string => {
      const s = ['th', 'st', 'nd', 'rd'];
      const v = n % 100;
      return n + (s[(v - 20) % 10] || s[v] || s[0]);
    };

    const getBillTypeSlug = (type: string): string => {
      const clean = (type || '').toLowerCase().replace(/[^a-z]/g, '');
      switch (clean) {
        case 'hr': return 'house-bill';
        case 's': return 'senate-bill';
        case 'hjres': return 'house-joint-resolution';
        case 'sjres': return 'senate-joint-resolution';
        case 'hconres': return 'house-concurrent-resolution';
        case 'sconres': return 'senate-concurrent-resolution';
        case 'hres': return 'house-resolution';
        case 'sres': return 'senate-resolution';
        default: return 'house-bill';
      }
    };

    switch (selectedNode.label) {
      case 'CoveragePolicy': {
        const articleId = props.article_id || selectedNode.primary_key.replace(/^CMS-MCD-/, '');
        return {
          title: `CMS Medicare Coverage Database (${articleId})`,
          url: `https://www.cms.gov/medicare-coverage-database/search-results.aspx?keyword=${encodeURIComponent(articleId)}`,
        };
      }
      case 'PublicLaw': {
        const congress = props.congress || selectedNode.primary_key.match(/PLAW-(\d+)-/)?.[1] || '117';
        const num = props.number || selectedNode.primary_key.match(/PLAW-\d+-(\d+)/)?.[1] || '328';
        return {
          title: `GPO GovInfo Public Law ${congress}-${num}`,
          url: `https://www.govinfo.gov/app/details/PLAW-${congress}publ${num}`,
        };
      }
      case 'Bill': {
        const congress = Number(props.congress || selectedNode.primary_key.match(/BILL-(\d+)-/)?.[1] || 117);
        const type = (props.type || selectedNode.primary_key.match(/BILL-\d+-([a-z]+)-/)?.[1] || 'hr').toLowerCase();
        const num = props.number || selectedNode.primary_key.match(/BILL-\d+-[a-z]+-(\d+)/)?.[1] || '3630';
        return {
          title: `Congress.gov ${type.toUpperCase()} ${num} (${getOrdinal(congress)} Congress)`,
          url: `https://www.congress.gov/bill/${getOrdinal(congress)}-congress/${getBillTypeSlug(type)}/${num}`,
        };
      }
      case 'Regulation': {
        const docNum = props.document_number || selectedNode.primary_key.replace(/^FR-/, '');
        return {
          title: `Federal Register Final Rule (${props.citation || docNum})`,
          url: `https://www.federalregister.gov/d/${encodeURIComponent(docNum)}`,
        };
      }
      case 'StatutorySection': {
        const title = props.title || '42';
        const rawSec = props.section || selectedNode.primary_key.replace(/^USC-\d+-/, '') || '1395x';
        const cleanSec = rawSec.split('-')[0];
        return {
          title: `US Code Title ${title} § ${cleanSec} (LII)`,
          url: `https://www.law.cornell.edu/uscode/text/${encodeURIComponent(title)}/${encodeURIComponent(cleanSec)}`,
        };
      }
      case 'ChangeRequest': {
        const crNum = props.cr_number || selectedNode.primary_key.replace(/^CMS-CR-/, '');
        return {
          title: `CMS Transmittals Index (CR ${crNum})`,
          url: `https://www.cms.gov/medicare/regulations-guidance/transmittals?search=${encodeURIComponent(crNum)}`,
        };
      }
      case 'Jurisdiction': {
        const code = props.code || selectedNode.primary_key;
        const isBC = code.includes('B') || code.includes('C');
        return {
          title: isBC
            ? `CGS Administrators DME MAC Portal (${code})`
            : `Noridian Healthcare Solutions DME MAC Portal (${code})`,
          url: isBC ? 'https://www.cgsmedicare.com/' : 'https://med.noridianmedicare.com/',
        };
      }
      case 'HCPCSCode': {
        const code = props.code || selectedNode.primary_key.replace(/^HCPCS-/, '');
        return {
          title: `CMS DMEPOS Fee Schedule & Coding Reference (${code})`,
          url: 'https://www.cms.gov/medicare/payment/fee-schedules/dmepos/dmepos-fee-schedule',
        };
      }
      case 'ICD10Code': {
        const code = props.code || selectedNode.primary_key.replace(/^ICD10-/, '');
        return {
          title: `CDC ICD-10-CM Clinical Browser (${code})`,
          url: `https://icd10cmtool.cdc.gov/?prop=${encodeURIComponent(code)}`,
        };
      }
      case 'LobbyingFiling': {
        return {
          title: 'Senate LDA Lobbying Disclosure Search',
          url: 'https://lda.senate.gov/system/public/',
        };
      }
      case 'LiteratureStudy': {
        const pmid = props.pmid || selectedNode.primary_key.replace(/^PUBMED-/, '');
        return {
          title: `PubMed National Library of Medicine (${pmid})`,
          url: `https://pubmed.ncbi.nlm.nih.gov/${encodeURIComponent(pmid)}/`,
        };
      }
      default:
        return null;
    }
  };

  const govLink = getGovernmentSourceLink();

  return (
    <div
      style={{
        position: 'absolute',
        top: 0,
        right: 0,
        width: 380,
        height: '100%',
        backgroundColor: CANVAS_PALETTE.panelBg,
        backdropFilter: 'blur(12px)',
        borderLeft: `1px solid ${CANVAS_PALETTE.panelBorder}`,
        boxShadow: '-8px 0 24px rgba(0, 0, 0, 0.6)',
        display: 'flex',
        flexDirection: 'column',
        zIndex: 20,
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
          alignItems: 'flex-start',
        }}
      >
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 6 }}>
            <span
              style={{
                backgroundColor: visual.badgeColor,
                color: '#ffffff',
                fontSize: 11,
                fontWeight: 700,
                padding: '2px 8px',
                borderRadius: 4,
                textTransform: 'uppercase',
                letterSpacing: '0.05em',
              }}
            >
              {selectedNode.label}
            </span>
            <span style={{ fontFamily: 'monospace', fontSize: 11, color: CANVAS_PALETTE.textMuted }}>
              {selectedNode.primary_key}
            </span>
          </div>
          <h2 style={{ margin: 0, fontSize: 16, fontWeight: 700, color: CANVAS_PALETTE.accentAmber, lineHeight: 1.3 }}>
            {selectedNode.name}
          </h2>
        </div>

        <button
          onClick={() => selectNode(null)}
          style={{
            background: 'none',
            border: 'none',
            color: CANVAS_PALETTE.textMuted,
            cursor: 'pointer',
            fontSize: 18,
            padding: 4,
          }}
          title="Close Drawer"
        >
          ✕
        </button>
      </div>

      {/* Body Content */}
      <div style={{ flex: 1, overflowY: 'auto', padding: '16px 20px' }}>
        {/* Scope / Description */}
        <div style={{ marginBottom: 16 }}>
          <div style={{ fontSize: 11, fontWeight: 600, color: CANVAS_PALETTE.textMuted, textTransform: 'uppercase', marginBottom: 4 }}>
            System Description
          </div>
          <div style={{ fontSize: 13, color: '#cbd5e1', lineHeight: 1.4 }}>
            {props.description || visual.description}
          </div>
        </div>

        {/* Action Button: Ask Agent */}
        <button
          onClick={() => setIsChatOpen(true)}
          style={{
            width: '100%',
            backgroundColor: CANVAS_PALETTE.accentAmber,
            color: '#0a1128',
            fontWeight: 700,
            fontSize: 13,
            padding: '10px 14px',
            borderRadius: 6,
            border: 'none',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: 8,
            marginBottom: 20,
            boxShadow: '0 2px 8px rgba(255, 183, 3, 0.25)',
          }}
        >
          ◈ INQUIRE IN GRAPHRAG CHAT
        </button>

        {/* Government Authority Link */}
        {govLink && (
          <div
            style={{
              padding: '12px 14px',
              backgroundColor: 'rgba(30, 41, 59, 0.6)',
              border: '1px solid rgba(56, 189, 248, 0.3)',
              borderRadius: 6,
              marginBottom: 20,
            }}
          >
            <div style={{ fontSize: 11, fontWeight: 700, color: '#38bdf8', marginBottom: 4 }}>
              GOVERNMENT SOURCE PROVENANCE
            </div>
            <a
              href={govLink.url}
              target="_blank"
              rel="noopener noreferrer"
              style={{
                color: '#7dd3fc',
                fontSize: 12,
                textDecoration: 'underline',
                wordBreak: 'break-word',
              }}
            >
              {govLink.title} ↗
            </a>
          </div>
        )}

        {/* Properties Table */}
        <div style={{ marginBottom: 20 }}>
          <div style={{ fontSize: 11, fontWeight: 600, color: CANVAS_PALETTE.textMuted, textTransform: 'uppercase', marginBottom: 8 }}>
            Entity Attributes
          </div>
          <div
            style={{
              backgroundColor: 'rgba(15, 23, 42, 0.6)',
              border: `1px solid ${CANVAS_PALETTE.panelBorder}`,
              borderRadius: 6,
              overflow: 'hidden',
            }}
          >
            {Object.entries(props)
              .filter(([k]) => !['primary_key', 'name', 'label', 'description'].includes(k))
              .map(([key, val], idx) => (
                <div
                  key={key}
                  style={{
                    display: 'flex',
                    padding: '8px 12px',
                    fontSize: 12,
                    borderBottom: idx < Object.keys(props).length - 1 ? `1px solid ${CANVAS_PALETTE.panelBorder}` : 'none',
                    backgroundColor: idx % 2 === 0 ? 'rgba(30, 41, 59, 0.2)' : 'transparent',
                  }}
                >
                  <span style={{ width: '42%', color: CANVAS_PALETTE.textMuted, fontFamily: 'monospace' }}>
                    {key}:
                  </span>
                  <span style={{ width: '58%', color: '#f1f5f9', wordBreak: 'break-word', fontWeight: 500 }}>
                    {typeof val === 'boolean' ? (val ? 'true' : 'false') : String(val)}
                  </span>
                </div>
              ))}
          </div>
        </div>

        {/* Connected Neighbors */}
        <div>
          <div style={{ fontSize: 11, fontWeight: 600, color: CANVAS_PALETTE.textMuted, textTransform: 'uppercase', marginBottom: 8 }}>
            Connected Neighbors ({connectedNeighbors.length})
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
            {connectedNeighbors.map((cn, i) => (
              <div
                key={i}
                onClick={() => cn.neighborNode && selectNode(cn.neighborNode)}
                style={{
                  padding: '8px 10px',
                  backgroundColor: 'rgba(30, 41, 59, 0.4)',
                  border: `1px solid ${CANVAS_PALETTE.panelBorder}`,
                  borderRadius: 6,
                  cursor: cn.neighborNode ? 'pointer' : 'default',
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  transition: 'background-color 0.15s ease',
                }}
              >
                <div>
                  <div style={{ fontSize: 10, color: CANVAS_PALETTE.textMuted, fontFamily: 'monospace' }}>
                    {cn.direction === 'OUTGOING' ? '→' : '←'} {cn.relLabel}
                  </div>
                  <div style={{ fontSize: 12, color: '#f8fafc', fontWeight: 600 }}>
                    {cn.neighborName}
                  </div>
                </div>
                <span
                  style={{
                    fontSize: 10,
                    padding: '2px 6px',
                    borderRadius: 4,
                    backgroundColor: getNodeVisual(cn.neighborLabel).badgeColor,
                    color: '#fff',
                  }}
                >
                  {cn.neighborLabel}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};
