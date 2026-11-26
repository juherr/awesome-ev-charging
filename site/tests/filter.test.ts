import { describe, expect, it } from 'vitest';
import {
  DEFAULT_STATE,
  activeFilters,
  applyFilters,
  categoryOptions,
  hostOptions,
  languageOptions,
  matches,
  parseState,
  protocolOptions,
  serialiseState,
  sortProjects,
  versionOptions,
  withProtocol,
  withoutFilter,
  type FilterProject,
  type FilterState,
} from '../src/lib/filter';

function project(id: string, over: Partial<FilterProject> = {}): FilterProject {
  return {
    id,
    full_name: id,
    description: null,
    topics: [],
    categories: [{ main: 'OCPP', sub: 'Server' }],
    ocpp_versions: null,
    ocpi_versions: null,
    language: null,
    host: 'github',
    curation: 'selection',
    stars: null,
    ...over,
  };
}

const steve = project('steve-community/steve', {
  description: 'Java OCPP server',
  topics: ['csms', 'ocpp'],
  ocpp_versions: ['1.2', '1.5', '1.6'],
  language: 'Java',
  stars: 1050,
});
const mobility = project('mobilityhouse/ocpp', {
  description: 'Python library',
  categories: [{ main: 'OCPP', sub: 'Libraries' }],
  ocpp_versions: ['1.6', '2.0.1'],
  language: 'Python',
  stars: 900,
});
const tariffs = project('tandemdrive/ocpi-tariffs', {
  description: 'Tariff calculation',
  categories: [{ main: 'OCPI', sub: 'Libraries' }],
  ocpi_versions: ['2.1.1', '2.2.1'],
  language: 'Rust',
  host: 'codeberg',
  stars: null,
});
const iso = project('switchev/iso15118', {
  description: 'ISO 15118 stack',
  categories: [{ main: 'iso15118', sub: 'Plug&Charge' }],
  language: 'Python',
  stars: 200,
});
const legacy = project('legacy-org/ocpp15-client', {
  categories: [{ main: 'OCPP', sub: 'Libraries' }],
  ocpp_versions: ['1.5'],
  language: 'C#',
  curation: 'dormant',
  stars: 10,
});
const refine = project('someone/ocpp-csms-go', {
  ocpp_versions: ['1.6', '2.0.1'],
  language: 'Go',
  curation: 'to_refine',
  stars: 4,
});
const homeAssistant = project('homecharge/ha-ocpp', {
  categories: [
    { main: 'OCPP', sub: 'Server' },
    { main: 'Other', sub: 'Home automation' },
  ],
  ocpp_versions: ['1.6', '2.0.1'],
  host: null,
  stars: 10,
});

const all = [steve, mobility, tariffs, iso, legacy, refine, homeAssistant];
const everyState: FilterState = { ...DEFAULT_STATE, states: ['selection', 'dormant', 'to_refine'] };
const ids = (list: FilterProject[]) => list.map((p) => p.id);
const state = (over: Partial<FilterState>): FilterState => ({ ...DEFAULT_STATE, ...over });

describe('default state', () => {
  it('shows Selection only, most stars first', () => {
    expect(DEFAULT_STATE.states).toEqual(['selection']);
    expect(DEFAULT_STATE.sort).toBe('stars');
    expect(ids(applyFilters(all, DEFAULT_STATE))).toEqual([
      'steve-community/steve',
      'mobilityhouse/ocpp',
      'switchev/iso15118',
      'homecharge/ha-ocpp',
      'tandemdrive/ocpi-tariffs',
    ]);
  });

  it('serialises to an empty query', () => {
    expect(serialiseState(DEFAULT_STATE)).toBe('');
    expect(parseState('')).toEqual(DEFAULT_STATE);
  });
});

describe('URL parameters', () => {
  it('parses every parameter', () => {
    expect(
      parseState(
        '?q=server&protocol=OCPP&category=Server&version=ocpp-1.6&language=Java&host=github&state=dormant,selection&sort=name',
      ),
    ).toEqual({
      q: 'server',
      protocol: 'OCPP',
      category: 'Server',
      version: 'ocpp-1.6',
      language: 'Java',
      host: 'github',
      states: ['selection', 'dormant'],
      sort: 'name',
    });
  });

  it('accepts the raw categories[].main value the home page links to', () => {
    const parsed = parseState('protocol=iso15118');
    expect(parsed.protocol).toBe('iso15118');
    expect(ids(applyFilters(all, parsed))).toEqual(['switchev/iso15118']);
  });

  it('round-trips a full state', () => {
    const full: FilterState = {
      q: 'tariff & co',
      protocol: 'OCPI',
      category: 'Libraries',
      version: 'ocpi-2.2.1',
      language: 'unknown',
      host: 'codeberg',
      states: ['selection', 'to_refine'],
      sort: 'stars-asc',
    };
    expect(parseState(serialiseState(full))).toEqual(full);
    expect(parseState(new URLSearchParams(serialiseState(full)))).toEqual(full);
  });

  it('writes parameters in a stable order and the states in curation order', () => {
    expect(serialiseState(state({ sort: 'name', protocol: 'OCPP', states: ['to_refine', 'selection'] }))).toBe(
      'protocol=OCPP&state=selection,to_refine&sort=name',
    );
  });

  it('keeps an explicitly empty state list', () => {
    const none = state({ states: [] });
    expect(serialiseState(none)).toBe('state=');
    expect(parseState(serialiseState(none))).toEqual(none);
    expect(applyFilters(all, none)).toEqual([]);
  });

  it('ignores unknown values instead of failing', () => {
    expect(parseState('sort=random&state=bogus,dormant&q=%20%20')).toEqual(state({ states: ['dormant'] }));
    expect(parseState('state=to-refine').states).toEqual(['to_refine']);
  });
});

describe('text search', () => {
  it('matches the full name, the description and the topics, case-insensitively', () => {
    expect(ids(applyFilters(all, { ...everyState, q: 'STEVE' }))).toEqual(['steve-community/steve']);
    expect(ids(applyFilters(all, { ...everyState, q: 'tariff' }))).toEqual(['tandemdrive/ocpi-tariffs']);
    expect(ids(applyFilters(all, { ...everyState, q: 'csms' }))).toEqual([
      'steve-community/steve',
      'someone/ocpp-csms-go',
    ]);
  });

  it('requires every word', () => {
    expect(ids(applyFilters(all, { ...everyState, q: 'java server' }))).toEqual(['steve-community/steve']);
    expect(applyFilters(all, { ...everyState, q: 'java tariff' })).toEqual([]);
  });

  it('does not crash on a null description', () => {
    expect(matches(project('a/b'), { ...everyState, q: 'x' })).toBe(false);
  });
});

describe('protocol and category', () => {
  it('lists protocols in taxonomy order, Other last', () => {
    expect(protocolOptions(all)).toEqual([
      { value: 'OCPP', label: 'OCPP' },
      { value: 'OCPI', label: 'OCPI' },
      { value: 'iso15118', label: 'ISO 15118' },
      { value: 'Other', label: 'Other' },
    ]);
  });

  it('matches any of a project’s categories', () => {
    expect(ids(applyFilters(all, { ...everyState, protocol: 'Other' }))).toEqual(['homecharge/ha-ocpp']);
  });

  it('offers the categories of the chosen protocol only', () => {
    expect(categoryOptions(all, 'OCPP')).toEqual([
      { value: 'Libraries', label: 'Libraries' },
      { value: 'Server', label: 'Server' },
    ]);
    expect(categoryOptions(all, 'OCPI')).toEqual([{ value: 'Libraries', label: 'Libraries' }]);
  });

  it('pairs the category with the protocol on the same category entry', () => {
    // ha-ocpp is OCPP > Server and Other > Home automation: not OCPP > Home automation.
    expect(applyFilters(all, { ...everyState, protocol: 'OCPP', category: 'Home automation' })).toEqual([]);
    expect(ids(applyFilters(all, { ...everyState, protocol: 'OCPP', category: 'Libraries' }))).toEqual([
      'mobilityhouse/ocpp',
      'legacy-org/ocpp15-client',
    ]);
  });

  it('resets category and version when the protocol changes', () => {
    const before = state({ protocol: 'OCPP', category: 'Server', version: 'ocpp-1.6', language: 'Java' });
    expect(withProtocol(before, 'OCPI')).toEqual(state({ protocol: 'OCPI', language: 'Java' }));
    expect(withProtocol(before, 'OCPP')).toEqual(before);
  });
});

describe('protocol versions', () => {
  it('labels each version with its protocol and sorts them numerically', () => {
    expect(versionOptions(all, null)).toEqual([
      { value: 'ocpp-1.2', label: 'OCPP 1.2' },
      { value: 'ocpp-1.5', label: 'OCPP 1.5' },
      { value: 'ocpp-1.6', label: 'OCPP 1.6' },
      { value: 'ocpp-2.0.1', label: 'OCPP 2.0.1' },
      { value: 'ocpi-2.1.1', label: 'OCPI 2.1.1' },
      { value: 'ocpi-2.2.1', label: 'OCPI 2.2.1' },
    ]);
  });

  it('follows the chosen protocol', () => {
    expect(versionOptions(all, 'OCPI').map((o) => o.value)).toEqual(['ocpi-2.1.1', 'ocpi-2.2.1']);
    expect(versionOptions(all, 'OCPP').map((o) => o.value)).toEqual([
      'ocpp-1.2',
      'ocpp-1.5',
      'ocpp-1.6',
      'ocpp-2.0.1',
    ]);
    expect(versionOptions(all, 'iso15118')).toEqual([]);
  });

  it('sorts 2.0.1 before 2.1 and 1.10 after 1.6', () => {
    const list = [project('a/b', { ocpp_versions: ['2.1', '1.10', '2.0.1', '1.6'] })];
    expect(versionOptions(list, null).map((o) => o.label)).toEqual([
      'OCPP 1.6',
      'OCPP 1.10',
      'OCPP 2.0.1',
      'OCPP 2.1',
    ]);
  });

  it('hides the projects with no known version once one is picked', () => {
    const picked = { ...everyState, version: 'ocpp-1.6' };
    expect(ids(applyFilters(all, picked))).toEqual([
      'steve-community/steve',
      'mobilityhouse/ocpp',
      'homecharge/ha-ocpp',
      'someone/ocpp-csms-go',
    ]);
    expect(ids(applyFilters(all, { ...everyState, version: 'ocpi-2.1.1' }))).toEqual(['tandemdrive/ocpi-tariffs']);
  });
});

describe('language and host', () => {
  it('derives the languages from the data, Unknown last', () => {
    expect(languageOptions(all)).toEqual([
      { value: 'C#', label: 'C#' },
      { value: 'Go', label: 'Go' },
      { value: 'Java', label: 'Java' },
      { value: 'Python', label: 'Python' },
      { value: 'Rust', label: 'Rust' },
      { value: 'unknown', label: 'Unknown' },
    ]);
  });

  it('filters on an unknown language', () => {
    expect(ids(applyFilters(all, { ...everyState, language: 'unknown' }))).toEqual(['homecharge/ha-ocpp']);
  });

  it('derives the hosts from the data, Unknown last', () => {
    expect(hostOptions(all)).toEqual([
      { value: 'github', label: 'GitHub' },
      { value: 'codeberg', label: 'Codeberg' },
      { value: 'unknown', label: 'Unknown' },
    ]);
    expect(ids(applyFilters(all, { ...everyState, host: 'codeberg' }))).toEqual(['tandemdrive/ocpi-tariffs']);
    expect(ids(applyFilters(all, { ...everyState, host: 'unknown' }))).toEqual(['homecharge/ha-ocpp']);
  });
});

describe('curation state', () => {
  it('is a multi-select', () => {
    expect(ids(applyFilters(all, state({ states: ['dormant', 'to_refine'] })))).toEqual([
      'legacy-org/ocpp15-client',
      'someone/ocpp-csms-go',
    ]);
  });
});

describe('sort', () => {
  it('puts unknown stars last in both directions', () => {
    const list = [tariffs, refine, steve, legacy];
    expect(ids(sortProjects(list, 'stars'))).toEqual([
      'steve-community/steve',
      'legacy-org/ocpp15-client',
      'someone/ocpp-csms-go',
      'tandemdrive/ocpi-tariffs',
    ]);
    expect(ids(sortProjects(list, 'stars-asc'))).toEqual([
      'someone/ocpp-csms-go',
      'legacy-org/ocpp15-client',
      'steve-community/steve',
      'tandemdrive/ocpi-tariffs',
    ]);
  });

  it('sorts by name A–Z, case-insensitively', () => {
    const list = [project('b/x'), project('A/y'), project('a/b')];
    expect(ids(sortProjects(list, 'name'))).toEqual(['a/b', 'A/y', 'b/x']);
  });

  it('breaks star ties by name and leaves its input untouched', () => {
    const list = [project('b/b', { stars: 5 }), project('a/a', { stars: 5 })];
    expect(ids(sortProjects(list, 'stars'))).toEqual(['a/a', 'b/b']);
    expect(ids(list)).toEqual(['b/b', 'a/a']);
  });
});

describe('combinations', () => {
  it('ANDs every filter', () => {
    const s: FilterState = {
      ...everyState,
      protocol: 'OCPP',
      category: 'Server',
      version: 'ocpp-2.0.1',
      language: 'Go',
      host: 'github',
      q: 'csms',
    };
    expect(ids(applyFilters(all, s))).toEqual(['someone/ocpp-csms-go']);
    expect(applyFilters(all, { ...s, states: ['selection'] })).toEqual([]);
  });
});

describe('active filter chips', () => {
  it('lists each active filter with a readable label', () => {
    const s = state({
      q: 'ocpp',
      protocol: 'iso15118',
      category: 'Plug&Charge',
      version: 'ocpp-1.6',
      language: 'unknown',
      host: 'codeberg',
      states: ['selection', 'dormant'],
    });
    expect(activeFilters(s)).toEqual([
      { key: 'q', label: 'Search: ocpp' },
      { key: 'protocol', label: 'ISO 15118' },
      { key: 'category', label: 'Plug&Charge' },
      { key: 'version', label: 'OCPP 1.6' },
      { key: 'language', label: 'Language: Unknown' },
      { key: 'host', label: 'Codeberg' },
      { key: 'states', label: 'Selection, Dormant' },
    ]);
    expect(activeFilters(DEFAULT_STATE)).toEqual([]);
  });

  it('removes one filter, and the protocol takes its category and version along', () => {
    const s = state({ protocol: 'OCPP', category: 'Server', version: 'ocpp-1.6', host: 'github' });
    expect(withoutFilter(s, 'host')).toEqual(state({ protocol: 'OCPP', category: 'Server', version: 'ocpp-1.6' }));
    expect(withoutFilter(s, 'protocol')).toEqual(state({ host: 'github' }));
    expect(withoutFilter(state({ states: ['dormant'] }), 'states')).toEqual(DEFAULT_STATE);
  });
});
