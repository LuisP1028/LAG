/**
 * Authoritative color, shape, and size mappings across all 17 8-hop entity categories.
 */

export type NodeShape =
  | 'ring'
  | 'circle'
  | 'hexagon'
  | 'square'
  | 'pentagon'
  | 'diamond'
  | 'octagon'
  | 'double_ring'
  | 'double_REring'
  | 'rounded_square'
  | 'dot'
  | 'triangle'
  | 'star';

export interface NodeVisualConfig {
  badgeColor: string;
  radius: number;
  shape: NodeShape;
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
    description: 'Congressional Legislative Bill',
  },
  PublicLaw: {
    badgeColor: '#1e40af', // Navy
    radius: 15,
    shape: 'hexagon',
    description: 'Enacted Public Law Statute',
  },
  StatutorySection: {
    badgeColor: '#4f46e5', // Indigo
    radius: 12,
    shape: 'square',
    description: 'Public Law Statutory Section (USLM)',
  },
  USCSection: {
    badgeColor: '#6366f1', // Periwinkle Indigo
    radius: 12,
    shape: 'pentagon',
    description: 'Codified United States Code Section',
  },
  Regulation: {
    badgeColor: '#c2410c', // Rust Orange
    radius: 13,
    shape: 'diamond',
    description: 'Federal Register Final Rule',
  },
  CFRSection: {
    badgeColor: '#ea580c', // Bright Orange
    radius: 11,
    shape: 'octagon',
    description: 'Code of Federal Regulations Part/Section',
  },
  Transmittal: {
    badgeColor: '#d97706', // Amber
    radius: 12,
    shape: 'rounded_square',
    description: 'CMS Manual Change Request Transmittal',
  },
  CoveragePolicy: {
    badgeColor: '#059669', // Emerald
    radius: 15,
    shape: 'double_ring',
    description: 'Medicare Coverage Policy / DME MAC Article',
  },
  DiagnosisCode: {
    badgeColor: '#e11d48', // Rose Red
    radius: 10,
    shape: 'triangle',
    description: 'ICD-10-CM Clinical Diagnosis Code',
  },
  ProcedureCode: {
    badgeColor: '#0891b2', // Cyan
    radius: 10,
    shape: 'hexagon',
    description: 'HCPCS Level II Procedure / Supply Code',
  },
  FeeScheduleRate: {
    badgeColor: '#eab308', // Gold
    radius: 6,
    shape: 'dot',
    description: 'DMEPOS State Fee Schedule Rate',
  },
  Jurisdiction: {
    badgeColor: '#16a34a', // Green
    radius: 13,
    shape: 'rounded_square',
    description: 'DME MAC Regional Administrative Contractor',
  },
  State: {
    badgeColor: '#64748b', // Slate
    radius: 9,
    shape: 'circle',
    description: 'US State / Territorial Jurisdiction',
  },
  LobbyingFiling: {
    badgeColor: '#9333ea', // Purple
    radius: 9,
    shape: 'triangle',
    description: 'Senate LDA Lobbying Disclosure Filing',
  },
  CBOScore: {
    badgeColor: '#0d9488', // Teal
    radius: 10,
    shape: 'diamond',
    description: 'Congressional Budget Office Cost Estimate',
  },
  LiteratureStudy: {
    badgeColor: '#0284c7', // Sky Blue
    radius: 9,
    shape: 'star',
    description: 'PubMed Peer-Reviewed Clinical Study',
  },
  // Legacy aliases for backward compatibility
  ChangeRequest: {
    badgeColor: '#d97706',
    radius: 12,
    shape: 'rounded_square',
    description: 'CMS Manual Change Request Transmittal',
  },
  HCPCSCode: {
    badgeColor: '#0891b2',
    radius: 10,
    shape: 'hexagon',
    description: 'HCPCS Level II Procedure / Supply Code',
  },
  ICD10Code: {
    badgeColor: '#e11d48',
    radius: 10,
    shape: 'triangle',
    description: 'ICD-10-CM Clinical Diagnosis Code',
  },
  FeeScheduleEntry: {
    badgeColor: '#eab308',
    radius: 6,
    shape: 'dot',
    description: 'DMEPOS State Fee Schedule Rate',
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

export const NODE_VISUAL_REGISTRY: Record<string, NodeVisualConfig> = {
  Policy: NODE_THEME_REGISTRY.Policy,
  Bill: NODE_THEME_REGISTRY.Bill,
  PublicLaw: NODE_THEME_REGISTRY.PublicLaw,
  StatutorySection: NODE_THEME_REGISTRY.StatutorySection,
  USCSection: NODE_THEME_REGISTRY.USCSection,
  Regulation: NODE_THEME_REGISTRY.Regulation,
  CFRSection: NODE_THEME_REGISTRY.CFRSection,
  Transmittal: NODE_THEME_REGISTRY.Transmittal,
  CoveragePolicy: NODE_THEME_REGISTRY.CoveragePolicy,
  DiagnosisCode: NODE_THEME_REGISTRY.DiagnosisCode,
  ProcedureCode: NODE_THEME_REGISTRY.ProcedureCode,
  FeeScheduleRate: NODE_THEME_REGISTRY.FeeScheduleRate,
  Jurisdiction: NODE_THEME_REGISTRY.Jurisdiction,
  State: NODE_THEME_REGISTRY.State,
  LobbyingFiling: NODE_THEME_REGISTRY.LobbyingFiling,
  CBOScore: NODE_THEME_REGISTRY.CBOScore,
  LiteratureStudy: NODE_THEME_REGISTRY.LiteratureStudy,
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

