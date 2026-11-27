/**
 * The projects directory's filters, sort and URL parameters, as pure
 * functions: the page renders the default state at build time, and the client
 * script (src/scripts/projects.ts) re-applies them in the browser.
 *
 * Unknown is never "no": a null language or host is its own `unknown` option,
 * and a project with no known version is hidden only once a version is picked.
 */
import { protocolLabel, protocolsIn } from './counts';
import type { Curation, Project } from './data';

/** The fields the directory filters and sorts on. */
export type FilterProject = Pick<
  Project,
  | 'id'
  | 'full_name'
  | 'description'
  | 'topics'
  | 'categories'
  | 'ocpp_versions'
  | 'ocpi_versions'
  | 'language'
  | 'host'
  | 'curation'
  | 'stars'
>;

export type SortKey = 'stars' | 'stars-asc' | 'name';

export interface FilterState {
  /** Free text, matched word by word against name, description and topics. */
  q: string;
  /** A raw `categories[].main` value, e.g. `OCPP` or `iso15118`. */
  protocol: string | null;
  /** A `categories[].sub` value, within `protocol` when one is chosen. */
  category: string | null;
  /** `ocpp-<version>` or `ocpi-<version>`. */
  version: string | null;
  /** A language, or `unknown` for a project whose language is not known. */
  language: string | null;
  /** github | codeberg | other, or `unknown`. */
  host: string | null;
  /** Curation states to show, in curation order. */
  states: Curation[];
  sort: SortKey;
}

export interface Option {
  value: string;
  label: string;
}

/** The option value standing for a null language or host. */
export const UNKNOWN = 'unknown';

export const CURATIONS: readonly Curation[] = ['selection', 'dormant', 'to_refine'];

export const CURATION_LABELS: Record<Curation, string> = {
  selection: 'Selection',
  dormant: 'Dormant',
  to_refine: 'To refine',
};

export const CURATION_HELP: Record<Curation, string> = {
  selection: 'Curated and actively maintained',
  dormant: 'Curated, no recent activity',
  to_refine: 'Discovered, not yet reviewed',
};

export const SORTS: readonly Option[] = [
  { value: 'stars', label: 'Most stars' },
  { value: 'stars-asc', label: 'Fewest stars' },
  { value: 'name', label: 'Name A–Z' },
];

export const HOST_LABELS: Record<string, string> = {
  github: 'GitHub',
  codeberg: 'Codeberg',
  other: 'Other',
  [UNKNOWN]: 'Unknown',
};

const HOST_ORDER = ['github', 'codeberg', 'other', UNKNOWN];

export const DEFAULT_STATE: FilterState = Object.freeze({
  q: '',
  protocol: null,
  category: null,
  version: null,
  language: null,
  host: null,
  states: ['selection'],
  sort: 'stars',
}) as FilterState;

// ---------------------------------------------------------------- URL

function canonicalStates(values: Iterable<string>): Curation[] {
  const wanted = new Set([...values].map((v) => v.trim().replace(/-/g, '_')));
  return CURATIONS.filter((c) => wanted.has(c));
}

function sameStates(a: Curation[], b: Curation[]): boolean {
  return a.length === b.length && a.every((s, i) => s === b[i]);
}

/** The state a query string describes; an unknown or empty value falls back to the default. */
export function parseState(query: string | URLSearchParams): FilterState {
  const params = typeof query === 'string' ? new URLSearchParams(query) : query;
  const text = (key: string) => {
    const value = params.get(key)?.trim();
    return value ? value : null;
  };
  const sort = params.get('sort');
  const state = params.get('state');
  return {
    q: text('q') ?? '',
    protocol: text('protocol'),
    category: text('category'),
    version: text('version'),
    language: text('language'),
    host: text('host'),
    states: state === null ? [...DEFAULT_STATE.states] : canonicalStates(state.split(',')),
    sort: SORTS.some((s) => s.value === sort) ? (sort as SortKey) : DEFAULT_STATE.sort,
  };
}

/** The query string (no `?`) for `state`; empty for the default state. */
export function serialiseState(state: FilterState): string {
  const params = new URLSearchParams();
  const q = state.q.trim();
  if (q) params.set('q', q);
  for (const key of ['protocol', 'category', 'version', 'language', 'host'] as const) {
    const value = state[key];
    if (value) params.set(key, value);
  }
  const states = canonicalStates(state.states);
  if (!sameStates(states, DEFAULT_STATE.states)) params.set('state', states.join(','));
  if (state.sort !== DEFAULT_STATE.sort) params.set('sort', state.sort);
  // A literal comma is valid in a query and keeps `state=selection,dormant` readable.
  return params.toString().replace(/%2C/gi, ',');
}

// ---------------------------------------------------------------- matching

/** The lowercased words of a free-text query; the CSMS directory shares it. */
export function words(q: string): string[] {
  return q.toLowerCase().split(/\s+/).filter(Boolean);
}

function haystack(p: FilterProject): string {
  return [p.full_name, p.description ?? '', ...p.topics].join(' ').toLowerCase();
}

/** `ocpp-1.6` → `['ocpp', '1.6']`; null for a value that is not a version option. */
function splitVersion(value: string): ['ocpp' | 'ocpi', string] | null {
  const match = /^(ocpp|ocpi)-(.+)$/i.exec(value);
  return match ? [match[1].toLowerCase() as 'ocpp' | 'ocpi', match[2]] : null;
}

function inProtocol(p: FilterProject, protocol: string | null): boolean {
  return protocol === null || p.categories.some((c) => c.main === protocol);
}

export function matches(p: FilterProject, state: FilterState): boolean {
  if (!state.states.includes(p.curation)) return false;
  if (state.protocol !== null || state.category !== null) {
    const hit = p.categories.some(
      (c) =>
        (state.protocol === null || c.main === state.protocol) &&
        (state.category === null || c.sub === state.category),
    );
    if (!hit) return false;
  }
  if (state.version !== null) {
    const parsed = splitVersion(state.version);
    if (!parsed) return false;
    const [kind, version] = parsed;
    const versions = kind === 'ocpp' ? p.ocpp_versions : p.ocpi_versions;
    if (!versions?.includes(version)) return false;
  }
  if (state.language !== null && (p.language ?? UNKNOWN) !== state.language) return false;
  if (state.host !== null && (p.host ?? UNKNOWN) !== state.host) return false;
  const terms = words(state.q);
  if (terms.length) {
    const text = haystack(p);
    if (!terms.every((t) => text.includes(t))) return false;
  }
  return true;
}

// ---------------------------------------------------------------- sort

const byName = (a: FilterProject, b: FilterProject) =>
  a.full_name.toLowerCase().localeCompare(b.full_name.toLowerCase(), 'en') || a.id.localeCompare(b.id, 'en');

/** A sorted copy; unknown stars come last whichever the direction. */
export function sortProjects<T extends FilterProject>(projects: readonly T[], sort: SortKey): T[] {
  const copy = [...projects];
  if (sort === 'name') return copy.sort(byName);
  const sign = sort === 'stars' ? -1 : 1;
  return copy.sort((a, b) => {
    if (a.stars === null || b.stars === null) {
      if (a.stars === b.stars) return byName(a, b);
      return a.stars === null ? 1 : -1;
    }
    return sign * (a.stars - b.stars) || byName(a, b);
  });
}

export function applyFilters<T extends FilterProject>(projects: readonly T[], state: FilterState): T[] {
  return sortProjects(
    projects.filter((p) => matches(p, state)),
    state.sort,
  );
}

// ---------------------------------------------------------------- options

export function protocolOptions(projects: readonly FilterProject[]): Option[] {
  const options = protocolsIn(projects).map((p) => ({ value: p.main, label: p.label }));
  if (projects.some((p) => p.categories.some((c) => c.main === 'Other'))) {
    options.push({ value: 'Other', label: 'Other' });
  }
  return options;
}

const alpha = (a: string, b: string) => a.toLowerCase().localeCompare(b.toLowerCase(), 'en') || a.localeCompare(b, 'en');

/** The `sub` values filed under `protocol` (all protocols when null). */
export function categoryOptions(projects: readonly FilterProject[], protocol: string | null): Option[] {
  const subs = new Set<string>();
  for (const p of projects) {
    for (const c of p.categories) {
      if (c.sub !== null && (protocol === null || c.main === protocol)) subs.add(c.sub);
    }
  }
  return [...subs].sort(alpha).map((s) => ({ value: s, label: s }));
}

function compareVersions(a: string, b: string): number {
  const pa = a.split('.');
  const pb = b.split('.');
  for (let i = 0; i < Math.max(pa.length, pb.length); i++) {
    if (pa[i] === undefined) return -1;
    if (pb[i] === undefined) return 1;
    const na = Number(pa[i]);
    const nb = Number(pb[i]);
    const diff = Number.isNaN(na) || Number.isNaN(nb) ? pa[i].localeCompare(pb[i], 'en') : na - nb;
    if (diff) return diff;
  }
  return 0;
}

export function versionLabel(value: string): string {
  const parsed = splitVersion(value);
  return parsed ? `${parsed[0].toUpperCase()} ${parsed[1]}` : value;
}

/**
 * The versions documented by the projects of `protocol`: OCPP versions only
 * under OCPP, OCPI versions only under OCPI, both otherwise.
 */
export function versionOptions(projects: readonly FilterProject[], protocol: string | null): Option[] {
  const kinds = protocol === 'OCPP' ? ['ocpp'] : protocol === 'OCPI' ? ['ocpi'] : ['ocpp', 'ocpi'];
  const options: Option[] = [];
  for (const kind of kinds) {
    const seen = new Set<string>();
    for (const p of projects) {
      if (!inProtocol(p, protocol)) continue;
      for (const v of (kind === 'ocpp' ? p.ocpp_versions : p.ocpi_versions) ?? []) seen.add(v);
    }
    for (const v of [...seen].sort(compareVersions)) {
      const value = `${kind}-${v}`;
      options.push({ value, label: versionLabel(value) });
    }
  }
  return options;
}

export function languageOptions(projects: readonly FilterProject[]): Option[] {
  const languages = new Set<string>();
  let unknown = false;
  for (const p of projects) {
    if (p.language === null) unknown = true;
    else languages.add(p.language);
  }
  const options = [...languages].sort(alpha).map((l) => ({ value: l, label: l }));
  if (unknown) options.push({ value: UNKNOWN, label: 'Unknown' });
  return options;
}

export function hostOptions(projects: readonly FilterProject[]): Option[] {
  const present = new Set<string>(projects.map((p) => p.host ?? UNKNOWN));
  return HOST_ORDER.filter((h) => present.has(h)).map((h) => ({ value: h, label: HOST_LABELS[h] }));
}

// ---------------------------------------------------------------- transitions

/** `state` with another protocol; category and version belong to the old one and are reset. */
export function withProtocol(state: FilterState, protocol: string | null): FilterState {
  if (protocol === state.protocol) return state;
  return { ...state, protocol, category: null, version: null };
}

export type FilterKey = 'q' | 'protocol' | 'category' | 'version' | 'language' | 'host' | 'states';

export interface ActiveFilter {
  key: FilterKey;
  label: string;
}

/** The filters that differ from the default, as removable chips. Sort is not a filter. */
export function activeFilters(state: FilterState): ActiveFilter[] {
  const chips: ActiveFilter[] = [];
  const q = state.q.trim();
  if (q) chips.push({ key: 'q', label: `Search: ${q}` });
  if (state.protocol) chips.push({ key: 'protocol', label: protocolLabel(state.protocol) });
  if (state.category) chips.push({ key: 'category', label: state.category });
  if (state.version) chips.push({ key: 'version', label: versionLabel(state.version) });
  if (state.language) {
    chips.push({ key: 'language', label: `Language: ${state.language === UNKNOWN ? 'Unknown' : state.language}` });
  }
  if (state.host) chips.push({ key: 'host', label: HOST_LABELS[state.host] ?? state.host });
  const states = canonicalStates(state.states);
  if (!sameStates(states, DEFAULT_STATE.states)) {
    chips.push({ key: 'states', label: states.length ? states.map((s) => CURATION_LABELS[s]).join(', ') : 'No state' });
  }
  return chips;
}

/** `state` with one filter back to its default. */
export function withoutFilter(state: FilterState, key: FilterKey): FilterState {
  switch (key) {
    case 'q':
      return { ...state, q: '' };
    case 'protocol':
      return withProtocol(state, null);
    case 'states':
      return { ...state, states: [...DEFAULT_STATE.states] };
    default:
      return { ...state, [key]: null };
  }
}
