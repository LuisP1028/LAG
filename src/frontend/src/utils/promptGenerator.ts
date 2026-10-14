import type { GraphNode } from '../types/graph';

export const constructInquiryPrompt = (node: GraphNode): string => {
  const pk = node.primary_key;
  const rawName =
    node.name ||
    node.properties?.title ||
    node.properties?.state_name ||
    node.properties?.citation_string ||
    node.properties?.citation ||
    node.properties?.cfr_reference ||
    node.properties?.section ||
    pk;
  const name = String(rawName).trim();

  if (name && name !== pk) {
    return `Why is [${pk}] (${name}) important, and what is its role in this policy lineage?`;
  }
  return `Why is [${pk}] important, and what is its role in this policy lineage?`;
};
