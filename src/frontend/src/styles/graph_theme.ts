/**
 * Authoritative color, shape, and size mappings conforming to Ticket 005 and visualization.md.
 */

export interface NodeVisualConfig {
  badgeColor: string;
  radius: number;
  shape: 'ring' | 'circle' | 'hexagon' | 'square' | 'diamond' | 'double_ring' | 'rounded_square' | 'dot' | 'triangle' | 'star';
  description: string;
}

export const NODE_THEME_REGISTRY: Record<string, NodeVisualConfig> = {
  Policy: {
    badgeColor: '#7c3aed', // Deep Violet
    radius: 18,
    shape: 'ring',
    description: 'Federal Legislative Policy Domain',
  },
  Bill: {
    badgeColor: '#2563eb', // Royal Blue
    radius: 13,
    shape: 'circle',
    description: 'Congressional Enactment Bill',
  },
  PublicLaw: {
    badgeColor: '#1e40af', // Navy
    radius: 15,
    shape: 'hexagon',
    description: 'Codified Public Law Omnibus',
  },
  StatutorySection: {
    badgeColor: '#4f46e5', // Indigo
    radius: 11,
    shape: 'square',
    description: 'United States Code Statutory Section',
  },
  Regulation: {
    badgeColor: '#c2410c', // Rust Orange
    radius: 13,
    shape: 'diamond',
    description: 'Federal Register Final Rule Regulation',
  },
  ChangeRequest: {
    badgeColor: '#d97706', // Amber
    radius: 12,
    shape: 'circle',
    description: 'CMS Operational Change Request Transmittal',
  },
  CoveragePolicy: {
    badgeColor: '#059669', // Emerald
    radius: 15,
    shape: 'double_ring',
    description: 'CMS Medicare Local Coverage Policy Article',
  },
  HCPCSCode: {
    badgeColor: '#0891b2', // Cyan
    radius: 10,
    shape: 'circle',
    description: 'Standardized Healthcare Procedure Code',
  },
  ICD10Code: {
    badgeColor: '#e11d48', // Rose Red
    radius: 10,
    shape: 'circle',
    description: 'Clinical Indication Diagnosis Code',
  },
  Jurisdiction: {
    badgeColor: '#16a34a', // Green
    radius: 13,
    shape: 'rounded_square',
    description: 'DME MAC Regional Claims Contractor',
  },
  State: {
    badgeColor: '#64748b', // Slate
    radius: 9,
    shape: 'circle',
    description: 'US State / Territorial Jurisdiction',
  },
  FeeScheduleEntry: {
    badgeColor: '#eab308', // Gold
    radius: 6,
    shape: 'dot',
    description: 'Allowable Medicare Part B Fee Schedule Rate',
  },
  LobbyingFiling: {
    badgeColor: '#9333ea', // Purple
    radius: 9,
    shape: 'triangle',
    description: 'Senate LDA Advocacy Filing',
  },
  LiteratureStudy: {
    badgeColor: '#0284c7', // Sky Blue
    radius: 9,
    shape: 'star',
    description: 'Preamble Scientific Evidentiary Citation',
  },
};

export const CANVAS_PALETTE = {
  bgVoid: '#0a1128', // Prussian Navy Void
  gridLines: 'rgba(30, 41, 59, 0.45)', // Blueprint architectural grid
  accentAmber: '#ffb703', // Electric amber
  activeHalo: '#f59e0b', // Glowing active border
  activeEdge: '#fbbf24', // Traversed active edge
  inactiveAttenuation: 0.18, // 20% opacity for non-active elements
  textPrimary: '#f8fafc',
  textMuted: '#94a3b8',
  panelBg: 'rgba(15, 23, 42, 0.92)',
  panelBorder: '#1e293b',
};

export function getNodeVisual(label: string): NodeVisualConfig {
  return (
    NODE_THEME_REGISTRY[label] || {
      badgeColor: '#64748b',
      radius: 9,
      shape: 'circle',
      description: 'Knowledge Graph Entity',
    }
  );
}
