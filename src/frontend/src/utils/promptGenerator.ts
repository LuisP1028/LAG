import type { GraphNode } from '../types/graph';

export const constructInquiryPrompt = (node: GraphNode): string => {
  const pk = node.primary_key;
  const name = node.name || node.properties?.title || node.properties?.state_name || node.properties?.section || pk;

  switch (node.label) {
    case 'PublicLaw':
      return `Explain the statutory authority and enacted healthcare provisions of [${pk}] (${name}).`;
    case 'Bill':
      return `What is the legislative history and purpose of [${pk}] (${name})?`;
    case 'Regulation':
      return `What policies and administrative instructions are implemented by [${pk}] (${name})?`;
    case 'CoveragePolicy':
      return `What diagnoses and procedure codes are governed by coverage article [${pk}] (${name})?`;
    case 'ChangeRequest':
      return `What operational instructions and benefit categories are mandated by [${pk}] (${name})?`;
    case 'Jurisdiction':
      return `What states and coverage policies are administered by [${pk}] (${name})?`;
    case 'State':
      return `What Medicare contractor, coverage policies, and allowable fee schedules apply to [${pk}] (${name})?`;
    case 'HCPCSCode':
      return `What are the coverage criteria, physician requirements, and allowable rates for [${pk}] (${name})?`;
    case 'ICD10Code':
      return `What coverage policies and durable medical equipment items are authorized for diagnosis [${pk}] (${name})?`;
    case 'Policy':
      return `Explain the legislative, regulatory, and coverage lineage of policy [${pk}] (${name}).`;
    case 'StatutorySection':
      return `What statutory obligations and healthcare provisions are codified in [${pk}] (${name})?`;
    case 'FeeScheduleEntry':
      return `What are the allowable reimbursement rates and jurisdictional terms for [${pk}] (${name})?`;
    case 'LiteratureStudy':
      return `What clinical evidence and findings are documented in study [${pk}] (${name})?`;
    case 'LobbyingFiling':
      return `What lobbying activities, clients, and issues are disclosed in filing [${pk}] (${name})?`;
    default:
      return `Explain the regulatory and operational role of [${pk}] (${name}).`;
  }
};
