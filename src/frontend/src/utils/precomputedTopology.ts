/**
 * Deterministic Client-Side Pre-Computed Graph Topology Filter & Display Name Resolver.
 *
 * Mirrors the exact filtering, label resolution, and display name derivation logic
 * of `GET /api/graph/topology` (`src/api/routes.py`) for bundled pre-computed
 * 8-hop policy runs (`LTA` and `IVIG`), enabling immediate zero-latency demonstration.
 */

import { STATE_TO_JURISDICTION, DME_JURISDICTIONS } from '../context/GraphSyncContext';
import { getNodeVisual } from '../styles/graph_theme';
import type { EdgeProvenance, GraphLink, GraphNode, NodeProperties } from '../types/graph';

export interface RawExportNode {
  primary_key: string;
  label?: string;
  [key: string]: any;
}

export interface RawExportEdge {
  source_pk: string;
  target_pk: string;
  label: string;
  edge_key?: string;
  provenance?: EdgeProvenance;
}

export interface RawExportGraph {
  node_count?: number;
  edge_count?: number;
  nodes: RawExportNode[];
  edges: RawExportEdge[];
}

export interface PrecomputedFilterOptions {
  policyKeyword?: string;
  stateFilter?: string;
  jurisdictionFilter?: string;
  includeFeeSchedules?: boolean;
}

export function resolveCanonicalLabel(pk: string, rawLabel?: string): string {
  if (rawLabel && rawLabel !== 'PolicyNode') {
    if (rawLabel === 'ChangeRequest') return 'Transmittal';
    if (rawLabel === 'HCPCSCode') return 'ProcedureCode';
    if (rawLabel === 'ICD10Code') return 'DiagnosisCode';
    if (rawLabel === 'FeeScheduleEntry') return 'FeeScheduleRate';
    return rawLabel;
  }
  if (pk.startsWith('FEE-')) return 'FeeScheduleRate';
  if (pk.startsWith('HCPCS-')) return 'ProcedureCode';
  if (pk.startsWith('STATE-')) return 'State';
  if (pk.startsWith('ICD10-')) return 'DiagnosisCode';
  if (pk.startsWith('JURIS-')) return 'Jurisdiction';
  if (pk.startsWith('POLICY-')) return 'Policy';
  if (pk.startsWith('BILL-')) return 'Bill';
  if (pk.startsWith('PLAW-')) return 'PublicLaw';
  if (pk.startsWith('STAT-')) return 'StatutorySection';
  if (pk.startsWith('USC-')) return 'USCSection';
  if (pk.startsWith('REG-FR-') || pk.startsWith('FR-')) return 'Regulation';
  if (pk.startsWith('CFR-')) return 'CFRSection';
  if (pk.startsWith('TR-CR') || pk.startsWith('CMS-CR-')) return 'Transmittal';
  if (pk.startsWith('DME-MAC-') || pk.startsWith('CMS-MCD-')) return 'CoveragePolicy';
  if (pk.startsWith('LDA-')) return 'LobbyingFiling';
  if (pk.startsWith('CBO-')) return 'CBOScore';
  if (pk.startsWith('PUBMED-')) return 'LiteratureStudy';
  return rawLabel || 'PolicyNode';
}

export function deriveDisplayName(label: string, pk: string, props: NodeProperties): string {
  if (label === 'Policy') {
    const kw = props.keyword || props.policy_keyword;
    return String(props.name || (kw ? `Policy: ${kw}` : pk));
  }
  if (label === 'Bill') {
    const bType = props.type || props.bill_type;
    const bNum = props.number || props.bill_number;
    const title = props.title;
    if (bType && bNum && title) {
      return `${String(bType).toUpperCase()} ${bNum}: ${title}`;
    }
    return String(title || pk);
  }
  if (label === 'PublicLaw') {
    const cong = props.congress;
    const num = props.number || props.public_law_number;
    if (cong && num) {
      const numStr = String(num);
      return numStr.includes(`${cong}-`) ? `Public Law ${numStr}` : `Public Law ${cong}-${numStr}`;
    }
    return String(props.title || pk);
  }
  if (label === 'StatutorySection') {
    const secNum = props.statute_section_number || props.section_number;
    const heading = props.heading || props.section_heading;
    if (secNum && heading) {
      return `Sec. ${secNum}: ${heading}`;
    }
    return String(heading || pk);
  }
  if (label === 'USCSection') {
    return String(props.citation_string || props.citation || pk);
  }
  if (label === 'Regulation') {
    const cit = props.citation;
    const docket = props.docket_id;
    if (cit && docket) {
      return `${cit} (${docket})`;
    }
    return String(cit || props.document_number || pk);
  }
  if (label === 'CFRSection') {
    return String(props.cfr_reference || props.citation || pk);
  }
  if (label === 'Transmittal' || label === 'ChangeRequest') {
    const cr = props.cr_number;
    const tr = props.transmittal_number;
    if (cr && tr) {
      return `${cr} (${tr})`;
    }
    return String(cr || tr || pk);
  }
  if (label === 'CoveragePolicy') {
    return String(props.title || props.article_id || pk);
  }
  if (label === 'DiagnosisCode' || label === 'ICD10Code') {
    const code = props.code;
    const desc = props.description;
    if (code && desc) {
      return `${code}: ${desc}`;
    }
    return String(code || pk);
  }
  if (label === 'ProcedureCode' || label === 'HCPCSCode') {
    const code = props.code;
    const sdesc = props.short_description || props.long_description;
    if (code && sdesc) {
      return `${code}: ${sdesc}`;
    }
    return String(code || pk);
  }
  if (label === 'FeeScheduleRate' || label === 'FeeScheduleEntry') {
    const hcpcs = props.hcpcs_code;
    const st = props.state_code;
    const fee = props.fee_amount;
    if (hcpcs && st && fee !== undefined && fee !== null) {
      const rTag = props.is_rural ? 'R' : 'NR';
      return `${hcpcs} (${st} ${rTag}): $${Number(fee).toFixed(2)}`;
    }
    return pk;
  }
  if (label === 'Jurisdiction') {
    const jCode = props.code || props.jurisdiction_code;
    const cname = props.contractor_name;
    if (jCode && cname) {
      return `${jCode} (${cname})`;
    }
    return String(cname || pk);
  }
  if (label === 'State') {
    return String(props.state_name || props.state_code || pk);
  }
  if (label === 'LobbyingFiling') {
    const cli = props.client_name;
    const reg = props.registrant_name;
    const yr = props.year || props.filing_year;
    if (cli && reg) {
      return yr ? `${cli} (${reg}, ${yr})` : `${cli} (${reg})`;
    }
    return String(cli || pk);
  }
  if (label === 'CBOScore' || label === 'LiteratureStudy') {
    return String(props.title || pk);
  }
  return String(props.name || props.title || pk);
}

export function filterPrecomputedTopology(
  rawGraph: RawExportGraph,
  options: PrecomputedFilterOptions = {}
): {
  nodes: GraphNode[];
  links: GraphLink[];
  edges: { source_pk: string; target_pk: string; label: string; edge_key: string; provenance: EdgeProvenance }[];
} {
  if (!rawGraph || !Array.isArray(rawGraph.nodes) || !Array.isArray(rawGraph.edges)) {
    throw new Error('Invalid pre-computed graph payload: expected nodes and edges arrays.');
  }

  const cleanState = (options.stateFilter || '').trim().toUpperCase().replace(/^STATE-/, '');
  const cleanJuris = (options.jurisdictionFilter || '').trim().toUpperCase();
  const includeFees = Boolean(options.includeFeeSchedules);

  if (cleanState && cleanState !== 'ALL' && !STATE_TO_JURISDICTION[cleanState]) {
    throw new Error(`Unrecognized state code '${options.stateFilter}'.`);
  }
  if (cleanJuris && cleanJuris !== 'ALL' && !DME_JURISDICTIONS[cleanJuris]) {
    throw new Error(`Unrecognized DME MAC jurisdiction '${options.jurisdictionFilter}'.`);
  }

  let allowedStatePks: Set<string> | null = null;
  let allowedJurisPks: Set<string> | null = null;

  if (cleanState && cleanState !== 'ALL') {
    allowedStatePks = new Set([`STATE-${cleanState}`]);
    const parentJ = STATE_TO_JURISDICTION[cleanState];
    if (parentJ) {
      allowedJurisPks = new Set([parentJ]);
    }
  } else if (cleanJuris && cleanJuris !== 'ALL') {
    allowedJurisPks = new Set([cleanJuris]);
    const jurisMeta = DME_JURISDICTIONS[cleanJuris];
    if (jurisMeta) {
      allowedStatePks = new Set(jurisMeta.states.map((st) => `STATE-${st.code}`));
    }
  }

  const nodesOut: GraphNode[] = [];
  const allowedNodePks = new Set<string>();
  let feeCount = 0;

  for (const rawNode of rawGraph.nodes) {
    const pk = String(rawNode.primary_key || '');
    if (!pk) continue;
    const canonicalLabel = resolveCanonicalLabel(pk, rawNode.label);
    const props: NodeProperties = { ...rawNode, primary_key: pk };

    const isFeeNode = canonicalLabel === 'FeeScheduleRate' || canonicalLabel === 'FeeScheduleEntry';
    if (isFeeNode) {
      if (cleanState && cleanState !== 'ALL') {
        const nodeState = String(props.state_code || '').toUpperCase();
        if (nodeState !== cleanState) continue;
      } else if (includeFees) {
        if (allowedStatePks && !allowedStatePks.has(`STATE-${String(props.state_code || '').toUpperCase()}`)) {
          continue;
        }
        if (feeCount >= 4000) continue;
        feeCount += 1;
      } else {
        continue;
      }
    } else {
      if (canonicalLabel === 'Jurisdiction' && allowedJurisPks && !allowedJurisPks.has(pk)) {
        continue;
      }
      if (canonicalLabel === 'State' && allowedStatePks && !allowedStatePks.has(pk)) {
        continue;
      }
    }

    const name = deriveDisplayName(canonicalLabel, pk, props);
    const visual = getNodeVisual(canonicalLabel);
    nodesOut.push({
      id: pk,
      primary_key: pk,
      label: canonicalLabel,
      name,
      properties: props,
      radius: visual.radius,
      color: visual.badgeColor,
      shape: visual.shape,
    });
    allowedNodePks.add(pk);
  }

  const edgesOut: { source_pk: string; target_pk: string; label: string; edge_key: string; provenance: EdgeProvenance }[] = [];
  const linksOut: GraphLink[] = [];
  const seenEdgeKeys = new Set<string>();

  for (const rawEdge of rawGraph.edges) {
    const spk = String(rawEdge.source_pk || '');
    const tpk = String(rawEdge.target_pk || '');
    const lbl = String(rawEdge.label || 'RELATED_TO');
    if (!allowedNodePks.has(spk) || !allowedNodePks.has(tpk)) {
      continue;
    }
    const edgeKey = rawEdge.edge_key || `${spk}->${lbl}->${tpk}`;
    if (seenEdgeKeys.has(edgeKey)) continue;
    seenEdgeKeys.add(edgeKey);

    const prov: EdgeProvenance = {
      source_uri: String(rawEdge.provenance?.source_uri || ''),
      selector: String(rawEdge.provenance?.selector || ''),
      ingestion_timestamp: String(rawEdge.provenance?.ingestion_timestamp || ''),
      run_id: String(rawEdge.provenance?.run_id || ''),
    };

    edgesOut.push({
      source_pk: spk,
      target_pk: tpk,
      label: lbl,
      edge_key: edgeKey,
      provenance: prov,
    });
    linksOut.push({
      source: spk,
      target: tpk,
      label: lbl,
      edge_key: edgeKey,
      provenance: prov,
    });
  }

  return { nodes: nodesOut, links: linksOut, edges: edgesOut };
}

