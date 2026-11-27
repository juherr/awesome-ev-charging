import { cpSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join, resolve } from 'node:path';
import { afterEach, describe, expect, it } from 'vitest';
import { DataError, dataVersion, loadData, resolveDataDir, resolveSchemaDir } from '../src/lib/data';

// vitest runs from site/, like the npm scripts and the mise tasks.
const FIXTURE = resolve('fixtures/data');
const SCHEMAS = resolve('../data/schema');

const temps: string[] = [];
afterEach(() => {
  while (temps.length) rmSync(temps.pop()!, { recursive: true, force: true });
});

/** A writable copy of the fixture directory. */
function copyFixture(): string {
  const dir = mkdtempSync(join(tmpdir(), 'aec-site-data-'));
  temps.push(dir);
  cpSync(FIXTURE, dir, { recursive: true });
  return dir;
}

function edit(dir: string, file: string, change: (json: any) => void): void {
  const path = join(dir, file);
  const json = JSON.parse(readFileSync(path, 'utf-8'));
  change(json);
  writeFileSync(path, JSON.stringify(json));
}

const load = (dataDir: string) => loadData({ dataDir, schemaDir: SCHEMAS });

describe('resolveDataDir', () => {
  it('defaults to ../data relative to the working directory', () => {
    expect(resolveDataDir({}, '/repo/site')).toBe('/repo/data');
  });

  it('honours AEC_DATA_DIR, relative to the working directory', () => {
    expect(resolveDataDir({ AEC_DATA_DIR: 'fixtures/data' }, '/repo/site')).toBe(
      '/repo/site/fixtures/data',
    );
    expect(resolveDataDir({ AEC_DATA_DIR: '/abs/data' }, '/repo/site')).toBe('/abs/data');
  });

  it('ignores an empty AEC_DATA_DIR', () => {
    expect(resolveDataDir({ AEC_DATA_DIR: '' }, '/repo/site')).toBe('/repo/data');
  });
});

describe('resolveSchemaDir', () => {
  it('reads the schemas from the repository, not from the data directory', () => {
    expect(resolveSchemaDir('/repo/site')).toBe('/repo/data/schema');
  });
});

describe('loadData', () => {
  it('loads the fixture export', () => {
    const data = load(FIXTURE);
    expect(data.projects.length).toBeGreaterThan(0);
    expect(data.csms.length).toBeGreaterThan(0);
    expect(data.manifest.payloads.projects?.records).toBe(data.projects.length);
  });

  it('points at issue #98 when projects.json is missing', () => {
    const dir = copyFixture();
    rmSync(join(dir, 'projects.json'));
    expect(() => load(dir)).toThrow(DataError);
    expect(() => load(dir)).toThrow(/projects\.json.*#98|#98.*projects\.json/s);
    expect(() => load(dir)).toThrow(/AEC_DATA_DIR/);
  });

  it('fails clearly when csms.json is missing', () => {
    const dir = copyFixture();
    rmSync(join(dir, 'csms.json'));
    expect(() => load(dir)).toThrow(/csms\.json/);
  });

  it('fails clearly when manifest.json is missing', () => {
    const dir = copyFixture();
    rmSync(join(dir, 'manifest.json'));
    expect(() => load(dir)).toThrow(/manifest\.json/);
  });

  it('refuses a schema major version it was not built for', () => {
    const dir = copyFixture();
    edit(dir, 'projects.json', (j) => (j.schema_version = '2.0'));
    expect(() => load(dir)).toThrow(DataError);
    expect(() => load(dir)).toThrow(/projects\.json.*schema_version 2\.0.*major 1/s);
  });

  it('refuses a payload without a schema_version', () => {
    const dir = copyFixture();
    edit(dir, 'csms.json', (j) => delete j.schema_version);
    expect(() => load(dir)).toThrow(/csms\.json.*schema_version/s);
  });

  it('checks the manifest major version too', () => {
    const dir = copyFixture();
    edit(dir, 'manifest.json', (j) => (j.schema_version = '3.1'));
    expect(() => load(dir)).toThrow(/manifest\.json.*major 1/s);
  });

  it('rejects a record that breaks the schema, naming the file and the field', () => {
    const dir = copyFixture();
    edit(dir, 'projects.json', (j) => (j.projects[0].curation = 'featured'));
    expect(() => load(dir)).toThrow(DataError);
    expect(() => load(dir)).toThrow(/projects\.json.*\/projects\/0\/curation/s);
  });

  it('rejects false where the contract says true or null', () => {
    const dir = copyFixture();
    edit(dir, 'csms.json', (j) => (j.products[0].source_available = false));
    expect(() => load(dir)).toThrow(/csms\.json.*\/products\/0\/source_available/s);
  });

  it('refuses a manifest whose payloads is not an object', () => {
    const dir = copyFixture();
    edit(dir, 'manifest.json', (j) => (j.payloads = []));
    expect(() => load(dir)).toThrow(DataError);
    expect(() => load(dir)).toThrow(/manifest\.json.*payloads must be an object/s);
  });

  it('refuses a manifest entry with a malformed field', () => {
    const dir = copyFixture();
    edit(dir, 'manifest.json', (j) => (j.payloads.csms.records = '287'));
    expect(() => load(dir)).toThrow(/manifest\.json.*payloads\.csms\.records/s);
  });

  it('refuses a manifest without the projects entry', () => {
    const dir = copyFixture();
    edit(dir, 'manifest.json', (j) => delete j.payloads.projects);
    expect(() => load(dir)).toThrow(DataError);
    expect(() => load(dir)).toThrow(/manifest\.json.*no payloads\.projects entry/s);
  });

  it('refuses a manifest checksum that does not match the loaded bytes', () => {
    const dir = copyFixture();
    edit(dir, 'manifest.json', (j) => (j.payloads.csms.sha256 = '0'.repeat(64)));
    expect(() => load(dir)).toThrow(DataError);
    expect(() => load(dir)).toThrow(/csms\.json.*SHA-256.*does not match.*manifest/s);
  });

  it('refuses a payload edited after its manifest entry was written', () => {
    const dir = copyFixture();
    // Still schema-valid, but no longer the bytes the manifest describes.
    edit(dir, 'projects.json', () => {});
    expect(() => load(dir)).toThrow(/projects\.json.*SHA-256.*does not match/s);
  });

  it('refuses a manifest record count that does not match the payload', () => {
    const dir = copyFixture();
    edit(dir, 'manifest.json', (j) => (j.payloads.projects.records += 1));
    expect(() => load(dir)).toThrow(DataError);
    expect(() => load(dir)).toThrow(/projects\.json.*23 records.*manifest.*24/s);
  });

  it('rejects a file that is not JSON', () => {
    const dir = copyFixture();
    writeFileSync(join(dir, 'projects.json'), '{"schema_version": ');
    expect(() => load(dir)).toThrow(/projects\.json.*not valid JSON/s);
  });
});

describe('dataVersion', () => {
  it('shortens each payload checksum', () => {
    const { manifest } = load(FIXTURE);
    const version = dataVersion(manifest);
    expect(version.projects).toBe(manifest.payloads.projects!.sha256.slice(0, 7));
    expect(version.csms).toBe(manifest.payloads.csms!.sha256.slice(0, 7));
  });

  it('says unknown rather than inventing a version for a missing entry', () => {
    expect(dataVersion({ schema_version: '1.0', payloads: {} })).toEqual({
      projects: null,
      csms: null,
    });
  });
});
