import { describe, expect, it } from 'vitest';
import { homeCounts, protocolLabel, protocolsIn } from '../src/lib/counts';
import type { CsmsProduct, Project } from '../src/lib/data';

function project(id: string, curation: Project['curation'], mains: string[]): Project {
  const categories = mains.map((main) => ({ main, sub: null }));
  return {
    id,
    full_name: id,
    url: null,
    host: null,
    description: null,
    primary_category: categories[0] ?? null,
    categories,
    ocpp_versions: null,
    ocpi_versions: null,
    language: null,
    license: null,
    stars: null,
    forks: null,
    archived: null,
    dormant: null,
    deprecated: null,
    curation,
    pushed_at: null,
    updated_at: null,
    topics: [],
    discovered_via: [],
  };
}

const csms = (id: string, certificates: number) =>
  ({ id, certificates: Array.from({ length: certificates }, () => ({})) }) as unknown as CsmsProduct;

describe('protocolsIn', () => {
  it('lists each protocol main category once, in the taxonomy order', () => {
    const projects = [
      project('a/1', 'selection', ['OCPI']),
      project('a/2', 'selection', ['OCPP', 'Other']),
      project('a/3', 'to_refine', ['iso15118']),
      project('a/4', 'dormant', ['OCPP']),
    ];
    expect(protocolsIn(projects).map((p) => p.main)).toEqual(['OCPP', 'OCPI', 'iso15118']);
  });

  it('leaves Other out: it is not a protocol', () => {
    expect(protocolsIn([project('a/1', 'selection', ['Other'])])).toEqual([]);
  });

  it('gives known protocols their display label and full name', () => {
    const [iso] = protocolsIn([project('a/1', 'selection', ['iso15118'])]);
    expect(iso).toEqual({ main: 'iso15118', label: 'ISO 15118', name: expect.any(String) });
  });

  it('keeps a protocol the site does not know yet, after the known ones', () => {
    const projects = [project('a/1', 'selection', ['NewProto']), project('a/2', 'selection', ['OCPP'])];
    expect(protocolsIn(projects)).toEqual([
      expect.objectContaining({ main: 'OCPP' }),
      { main: 'NewProto', label: 'NewProto', name: null },
    ]);
  });
});

describe('protocolLabel', () => {
  it('labels a known main category and passes an unknown one through', () => {
    expect(protocolLabel('iso15118')).toBe('ISO 15118');
    expect(protocolLabel('EMIP')).toBe('eMIP');
    expect(protocolLabel('Other')).toBe('Other');
  });
});

describe('homeCounts', () => {
  it('counts selected and listed projects, protocols and the CSMS records', () => {
    const projects = [
      project('a/1', 'selection', ['OCPP']),
      project('a/2', 'selection', ['OCPI']),
      project('a/3', 'dormant', ['OCPP']),
      project('a/4', 'to_refine', []),
    ];
    expect(homeCounts(projects, [csms('x', 2), csms('y', 0), csms('z', 1)])).toEqual({
      protocols: 2,
      selected: 2,
      listed: 4,
      csmsProducts: 3,
      ocaCertificates: 3,
    });
  });
});
