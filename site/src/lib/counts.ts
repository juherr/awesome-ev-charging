import type { CsmsProduct, Project } from './data';

export interface Protocol {
  /** The `categories[].main` value, as the export spells it. */
  main: string;
  label: string;
  /** The protocol's full name, or null for a main category the site does not know. */
  name: string | null;
}

/**
 * Display data for the protocol main categories of pipeline.py's
 * CATEGORY_TREE, in its order. `Other` is a bucket, not a protocol.
 */
const KNOWN: Protocol[] = [
  { main: 'OCPP', label: 'OCPP', name: 'Open Charge Point Protocol' },
  { main: 'OCPI', label: 'OCPI', name: 'Open Charge Point Interface' },
  { main: 'iso15118', label: 'ISO 15118', name: 'Vehicle-to-grid communication interface' },
  { main: 'OICP', label: 'OICP', name: 'Open InterCharge Protocol' },
  { main: 'EMIP', label: 'eMIP', name: 'eMobility Protocol Inter-Operation' },
  { main: 'OIOI', label: 'OIOI', name: 'Open InterOperability Interface' },
  { main: 'Eichrecht', label: 'Eichrecht', name: 'German calibration law' },
  { main: 'OpenADR', label: 'OpenADR', name: 'Open Automated Demand Response' },
  { main: 'OSCP', label: 'OSCP', name: 'Open Smart Charging Protocol' },
];

const NOT_A_PROTOCOL = new Set(['Other']);

/** The protocols the projects are filed under: known ones in taxonomy order, then the rest. */
export function protocolsIn(projects: Project[]): Protocol[] {
  const present = new Set(
    projects.flatMap((p) => p.categories.map((c) => c.main)).filter((m) => !NOT_A_PROTOCOL.has(m)),
  );
  const known = KNOWN.filter((p) => present.has(p.main));
  const knownMains = new Set(KNOWN.map((p) => p.main));
  const unknown = [...present]
    .filter((m) => !knownMains.has(m))
    .sort()
    .map((main) => ({ main, label: main, name: null }));
  return [...known, ...unknown];
}

export interface HomeCounts {
  protocols: number;
  selected: number;
  listed: number;
  csmsProducts: number;
  ocaCertificates: number;
}

export function homeCounts(projects: Project[], csms: CsmsProduct[]): HomeCounts {
  return {
    protocols: protocolsIn(projects).length,
    selected: projects.filter((p) => p.curation === 'selection').length,
    listed: projects.length,
    csmsProducts: csms.length,
    ocaCertificates: csms.reduce((sum, product) => sum + product.certificates.length, 0),
  };
}
