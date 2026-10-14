import type { GraphNode } from '../types/graph';

export const constructInquiryPrompt = (node: GraphNode): string => {
  const pk = node.primary_key;
  const name =
    node.name ||
    node.properties?.title ||
    node.properties?.state_name ||
    node.properties?.citation_string ||
    node.properties?.citation ||
    node.properties?.cfr_reference ||
    node.properties?.section ||
    pk;

  switch (node.label) {
    case 'Policy':
      return `Explain the legislative, regulatory, and coverage lineage of policy [${pk}] (${name}).`;
    case 'Bill':
      return `What is the legislative history, omnibus incorporation, and purpose of [${pk}] (${name})?`;
    case 'PublicLaw':
      return `Explain the statutory authority and enacted healthcare provisions of [${pk}] (${name}).`;
    case 'StatutorySection':
      return `What statutory obligations and U.S. Code amendments are enacted by [${pk}] (${name})?`;
    case 'USCSection':
      return `What statutory provisions and Federal Register regulations are authorized under [${pk}] (${name})?`;
    case 'Regulation':
      return `What CFR sections and operational instructions are implemented by Final Rule [${pk}] (${name})?`;
    case 'CFRSection':
      return `What regulatory rules and CMS transmittals codify and implement [${pk}] (${name})?`;
    case 'Transmittal':
    case 'ChangeRequest':
      return `What operational instructions, benefit categories, and coverage policies are mandated by [${pk}] (${name})?`;
    case 'CoveragePolicy':
      return `What diagnoses and procedure codes are governed by coverage article [${pk}] (${name})?`;
    case 'DiagnosisCode':
    case 'ICD10Code':
      return `What coverage policies and durable medical equipment items are authorized for diagnosis [${pk}] (${name})?`;
    case 'ProcedureCode':
    case 'HCPCSCode':
      return `What are the coverage criteria, pricing methodology, and allowable rates for [${pk}] (${name})?`;
    case 'FeeScheduleRate':
    case 'FeeScheduleEntry':
      return `What are the allowable reimbursement rates, patient coinsurance, and jurisdictional terms for [${pk}] (${name})?`;
    case 'Jurisdiction':
      return `What states and coverage policies are administered by [${pk}] (${name})?`;
    case 'State':
      return `What Medicare contractor, coverage policies, and allowable fee schedules apply to [${pk}] (${name})?`;
    case 'LobbyingFiling':
      return `What lobbying activities, clients, and legislative issues are disclosed in filing [${pk}] (${name})?`;
    case 'CBOScore':
      return `What budgetary impact and legislative cost estimates are documented in [${pk}] (${name})?`;
    case 'LiteratureStudy':
      return `What clinical evidence and findings are documented in study [${pk}] (${name})?`;
    default:
      return `Explain the regulatory and operational role of [${pk}] (${name}).`;
  }
};
