/**
 * Display rules and the light client filter of the CSMS directory, mirroring
 * the columns of csms.md (csms.py `render_row`).
 *
 * Unknown is never "no": a null renders as a dash, and Source available, OCPI
 * and API are only ever "Yes" or unknown. Certified features (proven by an OCA
 * certificate) and documented features (stated by the vendor) stay two lists.
 */
import type { CsmsCertificate, CsmsDocumentedFeature, CsmsProduct } from './data';
import { words } from './filter';
import { UNKNOWN_MARK } from './format';
import { safeHref } from './safe-href';

/** `FEATURE_VOCAB` of csms.py: canonical name → short label, in display order. */
export const FEATURE_LABELS: Readonly<Record<string, string>> = {
  Core: 'Core',
  'Advanced Security': 'Security',
  'Smart Charging': 'Smart Charging',
  'Local Authorization List Management': 'Local Auth',
  Reservation: 'Reservation',
  'Firmware Management': 'Firmware',
  'Remote Trigger': 'Remote Trigger',
  'Advanced Device Management': 'Device Mgmt',
  'Advanced User Interface': 'User Interface',
  'ISO 15118 Support': 'ISO 15118',
  'Plug & Charge': 'Plug & Charge',
  'OCPI Roaming': 'OCPI Roaming',
  Tariffs: 'Tariffs',
  Payments: 'Payments',
  'Token Management': 'Token Mgmt',
  'Load Management': 'Load Mgmt',
  Reporting: 'Reporting',
  'Multi-tenancy': 'Multi-tenancy',
  'White-label': 'White-label',
  'Remote Commands': 'Remote Commands',
};

const OCPI_FEATURE = 'OCPI Roaming';
const YES = 'Yes';

export function featureLabel(feature: string): string {
  return FEATURE_LABELS[feature] ?? feature;
}

/** `1.6` before `2.0.1`; a non-numeric part sorts as 0, as in csms.py. */
function versionKey(version: string): number[] {
  return version.split('.').map((part) => (/^\d+$/.test(part) ? Number(part) : 0));
}

function compareVersions(a: string, b: string): number {
  const [ka, kb] = [versionKey(a), versionKey(b)];
  for (let i = 0; i < Math.max(ka.length, kb.length); i++) {
    const diff = (ka[i] ?? -1) - (kb[i] ?? -1);
    if (diff) return diff;
  }
  return 0;
}

export function ocppCell(p: Pick<CsmsProduct, 'ocpp_versions'>): string {
  return p.ocpp_versions?.length ? [...p.ocpp_versions].sort(compareVersions).join(', ') : UNKNOWN_MARK;
}

/** `1.6 Full (v2.3)`: OCPP version, certificate type, certified software. */
export function certificateLabel(c: CsmsCertificate): string {
  const label = `${c.ocpp_version} ${c.type}`.trim();
  return c.software_version ? `${label} (${c.software_version})` : label;
}

export function sortedCertificates(certs: readonly CsmsCertificate[]): CsmsCertificate[] {
  return [...certs].sort(
    (a, b) =>
      compareVersions(a.ocpp_version, b.ocpp_version) ||
      (a.date ?? '').localeCompare(b.date ?? '') ||
      a.type.localeCompare(b.type),
  );
}

/** The product name links to the vendor's site, or to the repository (http(s) only). */
export function productHref(p: Pick<CsmsProduct, 'website' | 'repo_url'>): string | null {
  return safeHref(p.website) ?? safeHref(p.repo_url);
}

/** The sources of a documented feature that may be linked (http(s) only). */
export function featureLinks(f: CsmsDocumentedFeature): string[] {
  return f.source_urls.map(safeHref).filter((u): u is string => u !== null);
}

/**
 * OCPI is stated on the product or documented as a feature, whose sources it
 * links. A documented feature still attests the Yes when none of its sources
 * may be linked.
 */
export function ocpiCell(
  p: Pick<CsmsProduct, 'ocpi' | 'features_documented'>,
): { label: string; links: string[] } | null {
  const feature = p.features_documented.find((f) => f.feature === OCPI_FEATURE);
  const documented = Boolean(feature?.source_urls.length);
  return p.ocpi || documented ? { label: YES, links: feature ? featureLinks(feature) : [] } : null;
}

/** `api` says an API exists, `api_docs` that its documentation is public. */
export function apiCell(p: Pick<CsmsProduct, 'api' | 'api_docs'>): { label: string; href: string | null } | null {
  return p.api || p.api_docs ? { label: YES, href: safeHref(p.api_docs) } : null;
}

const DEPLOYMENTS: Record<string, string> = {
  saas: 'SaaS',
  'self-hosted': 'Self-hosted',
  both: 'SaaS or self-hosted',
};

export function deploymentLabel(deployment: string | null): string {
  return deployment === null ? UNKNOWN_MARK : (DEPLOYMENTS[deployment] ?? deployment);
}

export function statusLabel(status: string | null): string {
  return status ? status[0].toUpperCase() + status.slice(1) : UNKNOWN_MARK;
}

/**
 * One entry of `sources`: a URL, or `contributor:<login>` — a maintainer's own
 * research, never a URL on its own (docs/public-data.md).
 */
export function sourceRef(source: string): { label: string; href: string | null } {
  const href = safeHref(source);
  if (href) return { label: new URL(href).hostname.replace(/^www\./, ''), href };
  const contributor = /^contributor:(.+)$/.exec(source);
  if (contributor) return { label: `Contributor ${contributor[1]}`, href: `https://github.com/${contributor[1]}` };
  return { label: source, href: null };
}

// ---------------------------------------------------------------- filter

export interface CsmsFilterState {
  q: string;
  /** Only products with at least one OCA certificate. */
  certified: boolean;
  /** Only products whose source is available. */
  source: boolean;
}

export const DEFAULT_CSMS_STATE: CsmsFilterState = Object.freeze({ q: '', certified: false, source: false });

/** What one table row carries for the filter (as data attributes in the page). */
export interface CsmsFilterRow {
  text: string;
  certified: boolean;
  source: boolean;
}

export function csmsSearchText(p: Pick<CsmsProduct, 'name' | 'company'>): string {
  return [p.name, p.company ?? ''].join(' ').toLowerCase();
}

export function matchesCsms(row: CsmsFilterRow, state: CsmsFilterState): boolean {
  if (state.certified && !row.certified) return false;
  if (state.source && !row.source) return false;
  return words(state.q).every((w) => row.text.includes(w));
}

export function parseCsmsState(query: string | URLSearchParams): CsmsFilterState {
  const params = typeof query === 'string' ? new URLSearchParams(query) : query;
  return {
    q: (params.get('q') ?? '').trim(),
    certified: params.get('certified') === '1',
    source: params.get('source') === '1',
  };
}

export function serialiseCsmsState(state: CsmsFilterState): string {
  const params = new URLSearchParams();
  if (state.q.trim()) params.set('q', state.q.trim());
  if (state.certified) params.set('certified', '1');
  if (state.source) params.set('source', '1');
  return params.toString();
}
