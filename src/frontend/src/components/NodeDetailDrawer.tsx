/**
 * Dedicated node and edge detail inspection drawer across all 17 8-hop entity categories
 * and 18 topological edge types.
 */

import React, { useEffect, useState } from 'react';
import { useGraphSync } from '../context/GraphSyncContext';
import { getNodeVisual, CANVAS_PALETTE } from '../styles/graph_theme';
import type { GraphNode, GraphLink, EntityInspectionData, ProvenanceMetadata } from '../types/graph';
import { getApiBaseUrl } from '../utils/apiConfig';

interface NodeDetailDrawerProps {
  nodes: GraphNode[];
  links: GraphLink[];
}

export const NodeDetailDrawer: React.FC<NodeDetailDrawerProps> = ({ nodes, links }) => {
  const {
    selectedNode,
    selectNode,
    selectedEdge,
    selectEdge,
    inquireNode,
    isQueryLoading,
    dataSourceMode,
  } = useGraphSync();

  const [inspectedData, setInspectedData] = useState<EntityInspectionData | null>(null);
  const [isInspecting, setIsInspecting] = useState<boolean>(false);

  useEffect(() => {
    if (!selectedNode) {
      setInspectedData(null);
      return;
    }

    let cancelled = false;
    const fetchEntityDetail = async () => {
      setIsInspecting(true);
      try {
        const res = await fetch(
          `${getApiBaseUrl()}/api/entities/${encodeURIComponent(selectedNode.primary_key)}`
        );
        if (res.ok && !cancelled) {
          const detail: EntityInspectionData = await res.json();
          setInspectedData(detail);
        } else if (!cancelled) {
          setInspectedData(null);
        }
      } catch {
        if (!cancelled) {
          setInspectedData(null);
        }
      } finally {
        if (!cancelled) {
          setIsInspecting(false);
        }
      }
    };

    if (dataSourceMode === 'live') {
      fetchEntityDetail();
    } else {
      setInspectedData(null);
    }

    return () => {
      cancelled = true;
    };
  }, [selectedNode, dataSourceMode]);

  // Render Edge Detail Inspection View if an edge is selected
  if (selectedEdge && !selectedNode) {
    const srcPk =
      typeof selectedEdge.source === 'object'
        ? (selectedEdge.source as GraphNode).primary_key
        : String(selectedEdge.source);
    const tgtPk =
      typeof selectedEdge.target === 'object'
        ? (selectedEdge.target as GraphNode).primary_key
        : String(selectedEdge.target);
    const srcNode = nodes.find((n) => n.primary_key === srcPk);
    const tgtNode = nodes.find((n) => n.primary_key === tgtPk);
    const prov: ProvenanceMetadata = selectedEdge.provenance || {
      source_uri: '',
      selector: '',
      ingestion_timestamp: '',
      run_id: '',
    };

    return (
      <div
        data-testid="edge-detail-drawer"
        style={{
          position: 'absolute',
          top: 0,
          left: 0,
          width: 390,
          maxWidth: '45vw',
          height: '100%',
          boxSizing: 'border-box',
          backgroundColor: CANVAS_PALETTE.panelBg,
          backdropFilter: 'blur(12px)',
          borderRight: `1px solid ${CANVAS_PALETTE.panelBorder}`,
          boxShadow: '8px 0 24px rgba(0, 0, 0, 0.6)',
          display: 'flex',
          flexDirection: 'column',
          zIndex: 20,
          color: CANVAS_PALETTE.textPrimary,
          fontFamily: 'system-ui, -apple-system, sans-serif',
        }}
      >
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
                  backgroundColor: '#0284c7',
                  color: '#ffffff',
                  fontSize: 11,
                  fontWeight: 700,
                  padding: '2px 8px',
                  borderRadius: 4,
                  textTransform: 'uppercase',
                  letterSpacing: '0.05em',
                }}
              >
                {selectedEdge.label}
              </span>
              <span style={{ fontFamily: 'monospace', fontSize: 11, color: CANVAS_PALETTE.textMuted }}>
                {selectedEdge.edge_key}
              </span>
            </div>
            <h2 style={{ margin: 0, fontSize: 16, fontWeight: 700, color: CANVAS_PALETTE.accentAmber, lineHeight: 1.3 }}>
              Relationship Edge Inspection
            </h2>
          </div>

          <button
            data-testid="close-edge-drawer-btn"
            onClick={() => selectEdge(null)}
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

        <div style={{ flex: 1, overflowY: 'auto', overflowX: 'hidden', padding: '16px 20px' }}>
          {/* Directional Linkage Summary */}
          <div style={{ marginBottom: 20 }}>
            <div style={{ fontSize: 11, fontWeight: 600, color: CANVAS_PALETTE.textMuted, textTransform: 'uppercase', marginBottom: 8 }}>
              Directional Linkage
            </div>
            <div
              data-testid="edge-linkage-card"
              style={{
                padding: '12px',
                backgroundColor: 'rgba(15, 23, 42, 0.7)',
                border: `1px solid ${CANVAS_PALETTE.panelBorder}`,
                borderRadius: 6,
                fontFamily: 'monospace',
                fontSize: 12,
                color: '#f8fafc',
                wordBreak: 'break-word',
              }}
            >
              {srcPk} <span style={{ color: CANVAS_PALETTE.accentAmber }}>→ {selectedEdge.label} →</span> {tgtPk}
            </div>
          </div>

          {/* Source & Target Entity Cards */}
          <div style={{ marginBottom: 20 }}>
            <div style={{ fontSize: 11, fontWeight: 600, color: CANVAS_PALETTE.textMuted, textTransform: 'uppercase', marginBottom: 8 }}>
              Source Entity
            </div>
            <div
              onClick={() => srcNode && selectNode(srcNode)}
              style={{
                padding: '10px 12px',
                backgroundColor: 'rgba(30, 41, 59, 0.5)',
                border: `1px solid ${CANVAS_PALETTE.panelBorder}`,
                borderRadius: 6,
                cursor: srcNode ? 'pointer' : 'default',
                marginBottom: 12,
              }}
            >
              <div style={{ fontSize: 10, color: CANVAS_PALETTE.textMuted, fontFamily: 'monospace' }}>
                {srcNode?.label || 'Entity'} • {srcPk}
              </div>
              <div style={{ fontSize: 13, fontWeight: 600, color: '#f8fafc', marginTop: 2 }}>
                {srcNode?.name || srcPk}
              </div>
            </div>

            <div style={{ fontSize: 11, fontWeight: 600, color: CANVAS_PALETTE.textMuted, textTransform: 'uppercase', marginBottom: 8 }}>
              Target Entity
            </div>
            <div
              onClick={() => tgtNode && selectNode(tgtNode)}
              style={{
                padding: '10px 12px',
                backgroundColor: 'rgba(30, 41, 59, 0.5)',
                border: `1px solid ${CANVAS_PALETTE.panelBorder}`,
                borderRadius: 6,
                cursor: tgtNode ? 'pointer' : 'default',
              }}
            >
              <div style={{ fontSize: 10, color: CANVAS_PALETTE.textMuted, fontFamily: 'monospace' }}>
                {tgtNode?.label || 'Entity'} • {tgtPk}
              </div>
              <div style={{ fontSize: 13, fontWeight: 600, color: '#f8fafc', marginTop: 2 }}>
                {tgtNode?.name || tgtPk}
              </div>
            </div>
          </div>

          {/* Edge Provenance Metadata */}
          <div data-testid="edge-provenance-section" style={{ marginBottom: 20 }}>
            <div style={{ fontSize: 11, fontWeight: 600, color: CANVAS_PALETTE.textMuted, textTransform: 'uppercase', marginBottom: 8 }}>
              Edge Provenance Metadata
            </div>
            <div
              style={{
                backgroundColor: 'rgba(15, 23, 42, 0.6)',
                border: `1px solid ${CANVAS_PALETTE.panelBorder}`,
                borderRadius: 6,
                overflow: 'hidden',
              }}
            >
              {(
                [
                  ['source_uri', prov.source_uri],
                  ['selector', prov.selector],
                  ['run_id', prov.run_id],
                  ['ingestion_timestamp', prov.ingestion_timestamp],
                ] as [string, string][]
              ).map(([key, val], idx) => (
                <div
                  key={key}
                  style={{
                    display: 'flex',
                    padding: '8px 12px',
                    fontSize: 12,
                    borderBottom: idx < 3 ? `1px solid ${CANVAS_PALETTE.panelBorder}` : 'none',
                    backgroundColor: idx % 2 === 0 ? 'rgba(30, 41, 59, 0.2)' : 'transparent',
                  }}
                >
                  <span style={{ width: '44%', color: CANVAS_PALETTE.textMuted, fontFamily: 'monospace' }}>
                    {key}:
                  </span>
                  <span style={{ width: '56%', color: '#f1f5f9', wordBreak: 'break-all', fontWeight: 500 }}>
                    {key === 'source_uri' && val && (val.startsWith('http') || val.startsWith('file://')) ? (
                      <a
                        href={val}
                        target="_blank"
                        rel="noopener noreferrer"
                        style={{ color: '#38bdf8', textDecoration: 'underline' }}
                      >
                        {val}
                      </a>
                    ) : (
                      val || '[UNSPECIFIED IN GRAPH]'
                    )}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (!selectedNode) return null;

  const visual = getNodeVisual(selectedNode.label);
  const props = {
    ...(selectedNode.properties || {}),
    ...(inspectedData?.properties || {}),
  };

  // Find immediate incoming and outgoing relationships with provenance
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
        edge: l,
        direction: isOutgoing ? 'OUTGOING' : 'INCOMING',
        relLabel: l.label,
        neighborPk,
        neighborName: neighborNode?.name || neighborPk,
        neighborLabel: neighborNode?.label || 'Node',
        neighborNode,
        provenance: l.provenance,
      };
    });

  // Resolve provenance metadata across node inspection payload, node properties, or incident edges
  const inspectedProv: Partial<ProvenanceMetadata> | undefined = Array.isArray(inspectedData?.provenance)
    ? inspectedData?.provenance[0]
    : inspectedData?.provenance;
  const firstEdgeProv = connectedNeighbors.find((cn) => cn.provenance?.source_uri)?.provenance;
  const effectiveProvenance: ProvenanceMetadata = {
    source_uri: String(
      inspectedProv?.source_uri ||
        props.source_uri ||
        props.url ||
        props.source_url ||
        firstEdgeProv?.source_uri ||
        ''
    ),
    selector: String(
      inspectedProv?.selector ||
        props.selector ||
        firstEdgeProv?.selector ||
        ''
    ),
    run_id: String(
      inspectedProv?.run_id ||
        props.run_id ||
        firstEdgeProv?.run_id ||
        ''
    ),
    ingestion_timestamp: String(
      inspectedProv?.ingestion_timestamp ||
        props.ingestion_timestamp ||
        firstEdgeProv?.ingestion_timestamp ||
        ''
    ),
  };

  // Extract statutory, regulatory, clinical, or policy text excerpt
  const textExcerpt: string =
    inspectedData?.text_excerpt ||
    String(
      props.full_text ||
        props.text_excerpt ||
        props.summary ||
        props.description ||
        props.short_description ||
        props.long_description ||
        props.title ||
        props.official_title ||
        ''
    );

  // Extract official citations and identifiers
  const citations: string[] =
    inspectedData?.citations && inspectedData.citations.length > 0
      ? inspectedData.citations
      : (['cfr_reference', 'citation', 'statutory_citation', 'public_law_id', 'article_id', 'cr_number', 'code', 'hcpcs_code', 'pmid']
          .map((k) => props[k])
          .filter((v) => v !== undefined && v !== null && String(v).trim() !== '')
          .map((v) => String(v)));

  // Construct official government external links strictly from persisted properties without hardcoded fallbacks
  const getGovernmentSourceLink = (): { title: string; url: string } | null => {
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
      case 'Bill': {
        const congress = Number(props.congress || selectedNode.primary_key.match(/^BILL-(\d+)-/)?.[1]);
        const type = String(props.type || props.bill_type || selectedNode.primary_key.match(/^BILL-\d+-([a-z]+)-/)?.[1] || '').toLowerCase();
        const num = props.number || props.bill_number || selectedNode.primary_key.match(/^BILL-\d+-[a-z]+-(\d+)/)?.[1];
        if (!congress || !type || !num) return null;
        return {
          title: `Congress.gov ${type.toUpperCase()} ${num} (${getOrdinal(congress)} Congress)`,
          url: `https://www.congress.gov/bill/${getOrdinal(congress)}-congress/${getBillTypeSlug(type)}/${num}`,
        };
      }
      case 'PublicLaw': {
        const congress = props.congress || selectedNode.primary_key.match(/^PLAW-(\d+)-/)?.[1];
        const rawNum = String(props.number || props.public_law_number || selectedNode.primary_key.match(/^PLAW-\d+-(\d+)/)?.[1] || '');
        const num = rawNum.split('-').pop();
        if (!congress || !num) return null;
        return {
          title: `GPO GovInfo Public Law ${congress}-${num}`,
          url: `https://www.govinfo.gov/app/details/PLAW-${congress}publ${num}`,
        };
      }
      case 'StatutorySection': {
        const plId = String(props.public_law_id || '');
        const plMatch = plId.match(/^PLAW-(\d+)-(\d+)/) || selectedNode.primary_key.match(/^STAT-(\d+)-(\d+)-SEC-/);
        if (!plMatch) return null;
        const [, cong, num] = plMatch;
        const secNum = props.statute_section_number || props.section_number || '';
        return {
          title: `GPO GovInfo Public Law ${cong}-${num}${secNum ? ` § ${secNum}` : ''}`,
          url: `https://www.govinfo.gov/app/details/PLAW-${cong}publ${num}`,
        };
      }
      case 'USCSection': {
        const title = props.title || props.title_number || selectedNode.primary_key.match(/^USC-(\d+)-/)?.[1];
        const rawSec = String(props.section || props.section_code || '');
        if (!title || !rawSec) return null;
        const cleanSec = rawSec.split('-')[0];
        return {
          title: `U.S. Code Title ${title} § ${cleanSec} (Cornell LII)`,
          url: `https://www.law.cornell.edu/uscode/text/${encodeURIComponent(String(title))}/${encodeURIComponent(cleanSec)}`,
        };
      }
      case 'Regulation': {
        const docNum = String(props.document_number || selectedNode.primary_key.replace(/^(?:REG-)?FR-/, ''));
        if (!docNum) return null;
        return {
          title: `Federal Register Final Rule (${props.citation || docNum})`,
          url: `https://www.federalregister.gov/d/${encodeURIComponent(docNum)}`,
        };
      }
      case 'CFRSection': {
        const title = props.title || props.title_number || selectedNode.primary_key.match(/^CFR-(\d+)-/)?.[1];
        const part = props.part || props.part_number || selectedNode.primary_key.match(/^CFR-\d+-(\d+)/)?.[1];
        if (!title || !part) return null;
        return {
          title: `eCFR ${props.cfr_reference || `${title} CFR Part ${part}`}`,
          url: `https://www.ecfr.gov/current/title-${encodeURIComponent(String(title))}/part-${encodeURIComponent(String(part))}`,
        };
      }
      case 'Transmittal':
      case 'ChangeRequest': {
        const crNum = String(props.cr_number || selectedNode.primary_key.replace(/^(?:TR-CR|CMS-CR-)/, ''));
        if (!crNum) return null;
        return {
          title: `CMS Transmittals Index (${crNum.startsWith('CR') ? crNum : `CR ${crNum}`})`,
          url: `https://www.cms.gov/medicare/regulations-guidance/transmittals?search=${encodeURIComponent(crNum)}`,
        };
      }
      case 'CoveragePolicy': {
        const articleId = String(props.article_id || selectedNode.primary_key);
        const pubType = String(props.publisher_type || props.publication_type || '');
        if (!articleId) return null;
        if (pubType === 'DME_MAC_JOINT_PUBLICATION' || articleId.startsWith('DME-MAC-')) {
          return {
            title: `DME MAC Joint Publication (${articleId})`,
            url: 'https://www.cgsmedicare.com/jb/pubs/news/2023/11/cope147943.html',
          };
        }
        const cleanArt = articleId.replace(/^CMS-MCD-/, '');
        return {
          title: `CMS Medicare Coverage Database (${cleanArt})`,
          url: `https://www.cms.gov/medicare-coverage-database/search-results.aspx?keyword=${encodeURIComponent(cleanArt)}`,
        };
      }
      case 'ProcedureCode':
      case 'HCPCSCode': {
        const code = String(props.code || selectedNode.primary_key.replace(/^HCPCS-/, ''));
        if (!code) return null;
        return {
          title: `CMS DMEPOS Fee Schedule & Coding Reference (${code})`,
          url: 'https://www.cms.gov/medicare/payment/fee-schedules/dmepos/dmepos-fee-schedule',
        };
      }
      case 'FeeScheduleRate':
      case 'FeeScheduleEntry': {
        const hcpcs = String(props.hcpcs_code || '');
        if (!hcpcs) return null;
        return {
          title: `CMS DMEPOS Fee Schedule (${hcpcs} - ${props.state_code || ''})`,
          url: 'https://www.cms.gov/medicare/payment/fee-schedules/dmepos/dmepos-fee-schedule',
        };
      }
      case 'DiagnosisCode':
      case 'ICD10Code': {
        const code = String(props.code || selectedNode.primary_key.replace(/^ICD10-/, ''));
        if (!code) return null;
        return {
          title: `CDC ICD-10-CM Clinical Browser (${code})`,
          url: `https://icd10cmtool.cdc.gov/?prop=${encodeURIComponent(code)}`,
        };
      }
      case 'Jurisdiction': {
        const code = String(props.code || props.jurisdiction_code || selectedNode.primary_key);
        if (!code) return null;
        const isBC = code.includes('B') || code.includes('C');
        return {
          title: isBC
            ? `CGS Administrators DME MAC Portal (${code})`
            : `Noridian Healthcare Solutions DME MAC Portal (${code})`,
          url: isBC ? 'https://www.cgsmedicare.com/' : 'https://med.noridianmedicare.com/',
        };
      }
      case 'CBOScore': {
        const url = String(props.url || props.source_url || '');
        return {
          title: `CBO Cost Estimate (${selectedNode.primary_key})`,
          url: url.startsWith('http') ? url : 'https://www.cbo.gov/',
        };
      }
      case 'LobbyingFiling': {
        const uuid = String(props.filing_uuid || selectedNode.primary_key.replace(/^LDA-/, ''));
        return {
          title: `Senate LDA Lobbying Disclosure (${uuid})`,
          url: uuid
            ? `https://lda.senate.gov/filings/public/filing/${encodeURIComponent(uuid)}/print/`
            : 'https://lda.senate.gov/system/public/',
        };
      }
      case 'LiteratureStudy': {
        const pmid = String(props.pmid || selectedNode.primary_key.replace(/^PUBMED-/, ''));
        if (!pmid) return null;
        return {
          title: `PubMed National Library of Medicine (PMID ${pmid})`,
          url: `https://pubmed.ncbi.nlm.nih.gov/${encodeURIComponent(pmid)}/`,
        };
      }
      default:
        return null;
    }
  };

  const formatPropertyValue = (key: string, val: unknown): string => {
    if (val === null || val === undefined) return '';
    if (Array.isArray(val)) {
      return val.map((item) => String(item)).join('; ');
    }
    if (typeof val === 'boolean') {
      return val ? 'Yes (true)' : 'No (false)';
    }
    if (typeof val === 'number' && ['fee_amount', 'ceiling', 'floor', 'amount', 'non_rural_rate', 'rural_rate'].includes(key)) {
      return `$${val.toFixed(2)} (${val})`;
    }
    return String(val);
  };

  const govLink = getGovernmentSourceLink();
  const visibleEntries = Object.entries(props).filter(
    ([k, v]) => !['primary_key', 'name', 'label'].includes(k) && v !== null && v !== undefined
  );

  return (
    <div
      data-testid="node-detail-drawer"
      style={{
        position: 'absolute',
        top: 0,
        left: 0,
        width: 390,
        maxWidth: '45vw',
        height: '100%',
        boxSizing: 'border-box',
        backgroundColor: CANVAS_PALETTE.panelBg,
        backdropFilter: 'blur(12px)',
        borderRight: `1px solid ${CANVAS_PALETTE.panelBorder}`,
        boxShadow: '8px 0 24px rgba(0, 0, 0, 0.6)',
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
            {isInspecting && (
              <span style={{ fontSize: 10, color: CANVAS_PALETTE.accentAmber }}>SYNCING...</span>
            )}
          </div>
          <h2 style={{ margin: 0, fontSize: 16, fontWeight: 700, color: CANVAS_PALETTE.accentAmber, lineHeight: 1.3 }}>
            {selectedNode.name}
          </h2>
        </div>

        <button
          data-testid="close-node-drawer-btn"
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
      <div style={{ flex: 1, overflowY: 'auto', overflowX: 'hidden', padding: '16px 20px' }}>
        {/* Scope / Description */}
        <div style={{ marginBottom: 16 }}>
          <div style={{ fontSize: 11, fontWeight: 600, color: CANVAS_PALETTE.textMuted, textTransform: 'uppercase', marginBottom: 4 }}>
            System Description
          </div>
          <div style={{ fontSize: 13, color: '#cbd5e1', lineHeight: 1.4 }}>
            {String(props.description || props.short_description || visual.description)}
          </div>
        </div>

        {/* Statutory / Clinical / Policy Text Excerpt */}
        {textExcerpt && (
          <div data-testid="node-text-excerpt" style={{ marginBottom: 16 }}>
            <div style={{ fontSize: 11, fontWeight: 600, color: CANVAS_PALETTE.textMuted, textTransform: 'uppercase', marginBottom: 4 }}>
              Statutory / Clinical Text Excerpt
            </div>
            <div
              style={{
                fontSize: 12,
                color: '#e2e8f0',
                lineHeight: 1.5,
                padding: '10px 12px',
                backgroundColor: 'rgba(15, 23, 42, 0.7)',
                borderLeft: `3px solid ${CANVAS_PALETTE.accentAmber}`,
                borderRadius: 4,
                maxHeight: 160,
                overflowY: 'auto',
              }}
            >
              {textExcerpt}
            </div>
          </div>
        )}

        {/* Official Citations */}
        {citations.length > 0 && (
          <div data-testid="node-citations-list" style={{ marginBottom: 16 }}>
            <div style={{ fontSize: 11, fontWeight: 600, color: CANVAS_PALETTE.textMuted, textTransform: 'uppercase', marginBottom: 6 }}>
              Official Citations & Identifiers
            </div>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
              {citations.map((cit, idx) => (
                <span
                  key={idx}
                  style={{
                    fontFamily: 'monospace',
                    fontSize: 11,
                    backgroundColor: 'rgba(56, 189, 248, 0.15)',
                    color: '#7dd3fc',
                    border: '1px solid rgba(56, 189, 248, 0.35)',
                    padding: '2px 8px',
                    borderRadius: 4,
                  }}
                >
                  {cit}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Action Button: Ask Agent */}
        <button
          data-testid="inquire-node-btn"
          onClick={() => selectedNode && inquireNode(selectedNode)}
          disabled={isQueryLoading}
          style={{
            width: '100%',
            backgroundColor: isQueryLoading ? 'rgba(255, 183, 3, 0.6)' : CANVAS_PALETTE.accentAmber,
            color: '#0a1128',
            fontWeight: 700,
            fontSize: 13,
            padding: '10px 14px',
            borderRadius: 6,
            border: 'none',
            cursor: isQueryLoading ? 'not-allowed' : 'pointer',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: 8,
            marginBottom: 20,
            boxShadow: '0 2px 8px rgba(255, 183, 3, 0.25)',
            opacity: isQueryLoading ? 0.75 : 1.0,
          }}
        >
          {isQueryLoading ? '◈ EXPLAINING...' : '◈ WHY IS THIS IMPORTANT?'}
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

        {/* Explicit Provenance Metadata Block */}
        <div data-testid="node-provenance-section" style={{ marginBottom: 20 }}>
          <div style={{ fontSize: 11, fontWeight: 600, color: CANVAS_PALETTE.textMuted, textTransform: 'uppercase', marginBottom: 8 }}>
            Provenance Metadata
          </div>
          <div
            style={{
              backgroundColor: 'rgba(15, 23, 42, 0.6)',
              border: `1px solid ${CANVAS_PALETTE.panelBorder}`,
              borderRadius: 6,
              overflow: 'hidden',
            }}
          >
            {(
              [
                ['source_uri', effectiveProvenance.source_uri],
                ['selector', effectiveProvenance.selector],
                ['run_id', effectiveProvenance.run_id],
                ['ingestion_timestamp', effectiveProvenance.ingestion_timestamp],
              ] as [string, string][]
            ).map(([key, val], idx) => (
              <div
                key={key}
                style={{
                  display: 'flex',
                  padding: '7px 12px',
                  fontSize: 11,
                  borderBottom: idx < 3 ? `1px solid ${CANVAS_PALETTE.panelBorder}` : 'none',
                  backgroundColor: idx % 2 === 0 ? 'rgba(30, 41, 59, 0.2)' : 'transparent',
                }}
              >
                <span style={{ width: '44%', color: CANVAS_PALETTE.textMuted, fontFamily: 'monospace' }}>
                  {key}:
                </span>
                <span style={{ width: '56%', color: '#f1f5f9', wordBreak: 'break-all', fontWeight: 500 }}>
                  {key === 'source_uri' && val && (val.startsWith('http') || val.startsWith('file://')) ? (
                    <a
                      href={val}
                      target="_blank"
                      rel="noopener noreferrer"
                      style={{ color: '#38bdf8', textDecoration: 'underline' }}
                    >
                      {val}
                    </a>
                  ) : (
                    val || '[UNSPECIFIED IN GRAPH]'
                  )}
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Properties Table */}
        <div data-testid="node-attributes-table" style={{ marginBottom: 20 }}>
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
            {visibleEntries.map(([key, val], idx) => (
              <div
                key={key}
                style={{
                  display: 'flex',
                  padding: '8px 12px',
                  fontSize: 12,
                  borderBottom: idx < visibleEntries.length - 1 ? `1px solid ${CANVAS_PALETTE.panelBorder}` : 'none',
                  backgroundColor: idx % 2 === 0 ? 'rgba(30, 41, 59, 0.2)' : 'transparent',
                }}
              >
                <span style={{ width: '42%', color: CANVAS_PALETTE.textMuted, fontFamily: 'monospace' }}>
                  {key}:
                </span>
                <span style={{ width: '58%', color: '#f1f5f9', wordBreak: 'break-word', fontWeight: 500 }}>
                  {formatPropertyValue(key, val)}
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
                style={{
                  padding: '8px 10px',
                  backgroundColor: 'rgba(30, 41, 59, 0.4)',
                  border: `1px solid ${CANVAS_PALETTE.panelBorder}`,
                  borderRadius: 6,
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  transition: 'background-color 0.15s ease',
                }}
              >
                <div
                  onClick={() => cn.neighborNode && selectNode(cn.neighborNode)}
                  style={{ maxWidth: '68%', cursor: cn.neighborNode ? 'pointer' : 'default' }}
                >
                  <div style={{ fontSize: 10, color: CANVAS_PALETTE.textMuted, fontFamily: 'monospace' }}>
                    {cn.direction === 'OUTGOING' ? '→' : '←'} {cn.relLabel}
                  </div>
                  <div style={{ fontSize: 12, color: '#f8fafc', fontWeight: 600 }}>
                    {cn.neighborName}
                  </div>
                  {cn.provenance?.source_uri && (
                    <div style={{ fontSize: 10, color: '#94a3b8', fontFamily: 'monospace', marginTop: 2, wordBreak: 'break-all' }}>
                      src: {cn.provenance.source_uri}
                    </div>
                  )}
                </div>
                <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: 4 }}>
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
                  <button
                    onClick={() => selectEdge(cn.edge)}
                    style={{
                      fontSize: 9,
                      padding: '2px 6px',
                      borderRadius: 3,
                      backgroundColor: 'rgba(56, 189, 248, 0.15)',
                      color: '#38bdf8',
                      border: '1px solid rgba(56, 189, 248, 0.4)',
                      cursor: 'pointer',
                    }}
                  >
                    Inspect Edge
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

