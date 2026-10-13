/**
 * Type definitions for the GraphRAG visualization canvas and synchronization bus.
 */

export interface NodeProperties {
  primary_key: string;
  name?: string;
  title?: string;
  state_code?: string;
  state_name?: string;
  code?: string;
  description?: string;
  fee_amount?: number;
  is_rural?: boolean;
  transmittal_number?: string;
  benefit_category?: string;
  contractor_name?: string;
  states?: string;
  source_url?: string;
  [key: string]: any;
}

export interface EdgeProvenance {
  source_uri: string;
  selector: string;
  ingestion_timestamp: string;
  run_id: string;
}

export interface GraphNode {
  id: string;
  primary_key: string;
  label: string;
  name: string;
  properties: NodeProperties;
  radius: number;
  color: string;
  shape: string;
  x?: number;
  y?: number;
  vx?: number;
  vy?: number;
  fx?: number | null;
  fy?: number | null;
}

export interface GraphLink {
  source: string | GraphNode;
  target: string | GraphNode;
  label: string;
  edge_key: string;
  provenance: EdgeProvenance;
}

export interface AnchorEntity {
  slot: string;
  primary_key: string;
  matched_text: string;
  entity_type: string;
  label: string;
}

export interface GraphRAGQueryResponse {
  answer: string;
  active_node_pks: string[];
  active_edge_keys: string[];
  anchors: AnchorEntity[];
  provenance_sources: EdgeProvenance[];
  duration_ms: number;
}

export interface GraphSummary {
  total_nodes: number;
  total_edges: number;
  nodes_by_label: { labels: string[]; count: number }[];
  edges_by_type: { rel_type: string; count: number }[];
}
