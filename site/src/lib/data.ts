/**
 * The site's only data source: the committed public JSON export
 * (docs/public-data.md). It is read once at build time, validated against the
 * repository's schemas, and never fetched from the network.
 *
 * `null`, an empty list or a missing entry means unknown, never "no": the
 * types below keep that distinction, and the pages must too.
 */
import { existsSync, readFileSync } from 'node:fs';
import { join, resolve } from 'node:path';
import Ajv2020 from 'ajv/dist/2020.js';

export type Host = 'github' | 'codeberg' | 'other';
export type Curation = 'selection' | 'dormant' | 'to_refine';

export interface Category {
  main: string;
  sub: string | null;
}

export interface Project {
  id: string;
  full_name: string;
  url: string | null;
  host: Host | null;
  description: string | null;
  primary_category: Category | null;
  categories: Category[];
  ocpp_versions: string[] | null;
  ocpi_versions: string[] | null;
  language: string | null;
  license: string | null;
  stars: number | null;
  forks: number | null;
  archived: boolean | null;
  dormant: boolean | null;
  deprecated: true | null;
  curation: Curation;
  pushed_at: string | null;
  updated_at: string | null;
  topics: string[];
  discovered_via: string[];
}

export interface CsmsCertificate {
  number: string;
  ocpp_version: string;
  type: string;
  software_version: string | null;
  date: string | null;
  url: string | null;
}

export interface CsmsDocumentedFeature {
  feature: string;
  source_urls: string[];
}

export interface CsmsProduct {
  id: string;
  name: string;
  company: string | null;
  oca_company_url: string | null;
  website: string | null;
  repo: string | null;
  repo_url: string | null;
  source_available: true | null;
  ocpp_versions: string[] | null;
  certificates: CsmsCertificate[];
  features_certified: string[];
  features_documented: CsmsDocumentedFeature[];
  ocpi: true | null;
  iso15118: true | null;
  eichrecht: true | null;
  api: true | null;
  api_docs: string | null;
  pricing: string | null;
  pricing_url: string | null;
  changelog: string | null;
  hq_country: string | null;
  hq_city: string | null;
  company_founded: string | null;
  first_release: string | null;
  latest_version: string | null;
  latest_version_date: string | null;
  license: string | null;
  deployment: string | null;
  status: string | null;
  notes: string | null;
  sources: string[];
}

export interface ManifestEntry {
  file: string;
  sha256: string;
  records: number;
  inputs: Record<string, string>;
}

export interface Manifest {
  schema_version: string;
  payloads: { projects?: ManifestEntry; csms?: ManifestEntry };
}

export interface SiteData {
  dataDir: string;
  projects: Project[];
  csms: CsmsProduct[];
  manifest: Manifest;
}

export interface LoadOptions {
  /** Directory holding projects.json, csms.json and manifest.json. */
  dataDir: string;
  /** Directory holding projects.schema.json and csms.schema.json. */
  schemaDir: string;
}

/** The only schema major version this site renders. */
export const SCHEMA_MAJOR = 1;

const ISSUE_98 = 'https://github.com/juherr/awesome-ev-charging/issues/98';

/** A data problem that must stop the build, with a message saying what to do. */
export class DataError extends Error {
  override name = 'DataError';
}

/**
 * The data directory: `AEC_DATA_DIR` when set, else `../data`. Both resolve
 * against `cwd`, which is `site/` for the npm scripts and the mise tasks.
 */
export function resolveDataDir(
  env: Record<string, string | undefined> = process.env,
  cwd: string = process.cwd(),
): string {
  return resolve(cwd, env.AEC_DATA_DIR || '../data');
}

/**
 * The schemas always come from the repository's `data/schema/`, whatever the
 * data directory: the fixture is checked against the same contract as the
 * published export.
 */
export function resolveSchemaDir(cwd: string = process.cwd()): string {
  return resolve(cwd, '../data/schema');
}

function readJson(path: string, label: string): any {
  let text: string;
  try {
    text = readFileSync(path, 'utf-8');
  } catch (error) {
    throw new DataError(`Cannot read ${label} at ${path}: ${(error as Error).message}`);
  }
  try {
    return JSON.parse(text);
  } catch (error) {
    throw new DataError(`${label} at ${path} is not valid JSON: ${(error as Error).message}`);
  }
}

function checkMajor(json: any, label: string, path: string): void {
  const version = json?.schema_version;
  if (typeof version !== 'string') {
    throw new DataError(`${label} at ${path} has no schema_version; expected major ${SCHEMA_MAJOR}.`);
  }
  if (Number(version.split('.')[0]) !== SCHEMA_MAJOR) {
    throw new DataError(
      `${label} at ${path} has schema_version ${version}; this site renders major ` +
        `${SCHEMA_MAJOR} only. Update the site for the new contract (docs/public-data.md).`,
    );
  }
}

function validator(schemaDir: string, file: string) {
  const ajv = new Ajv2020({ allErrors: true, strict: true });
  return ajv.compile(readJson(join(schemaDir, file), file));
}

function validate(json: unknown, label: string, path: string, schemaDir: string, schemaFile: string) {
  const check = validator(schemaDir, schemaFile);
  if (check(json)) return;
  const problems = (check.errors ?? [])
    .slice(0, 10)
    .map((e) => `  ${e.instancePath || '/'} ${e.message ?? ''}`.trimEnd())
    .join('\n');
  throw new DataError(`${label} at ${path} does not match ${schemaFile}:\n${problems}`);
}

function payloadPath(dataDir: string, file: string, label: string, hint = ''): string {
  const path = join(dataDir, file);
  if (!existsSync(path)) {
    throw new DataError(`${label} not found in ${dataDir}.${hint}`);
  }
  return path;
}

/** Read and validate the export in `dataDir`; throws a DataError on any problem. */
export function loadData({ dataDir, schemaDir }: LoadOptions): SiteData {
  const projectsPath = payloadPath(
    dataDir,
    'projects.json',
    'projects.json',
    ` It is not published in data/ yet (issue #98: ${ISSUE_98}). ` +
      'Build against the fixture with AEC_DATA_DIR=fixtures/data, or point ' +
      'AEC_DATA_DIR at a directory that holds a render of the export.',
  );
  const csmsPath = payloadPath(dataDir, 'csms.json', 'csms.json');
  const manifestPath = payloadPath(dataDir, 'manifest.json', 'manifest.json');

  const projects = readJson(projectsPath, 'projects.json');
  const csms = readJson(csmsPath, 'csms.json');
  const manifest = readJson(manifestPath, 'manifest.json');

  checkMajor(projects, 'projects.json', projectsPath);
  checkMajor(csms, 'csms.json', csmsPath);
  checkMajor(manifest, 'manifest.json', manifestPath);
  validate(projects, 'projects.json', projectsPath, schemaDir, 'projects.schema.json');
  validate(csms, 'csms.json', csmsPath, schemaDir, 'csms.schema.json');

  return {
    dataDir,
    projects: projects.projects as Project[],
    csms: csms.products as CsmsProduct[],
    manifest: manifest as Manifest,
  };
}

let cached: SiteData | undefined;

/** The build's data, from `AEC_DATA_DIR` (default `../data`), loaded once. */
export function getData(): SiteData {
  cached ??= loadData({ dataDir: resolveDataDir(), schemaDir: resolveSchemaDir() });
  return cached;
}

/** The short form of each payload's SHA-256, or null when the manifest has no entry. */
export function dataVersion(manifest: Manifest): { projects: string | null; csms: string | null } {
  const short = (entry?: ManifestEntry) => (entry ? entry.sha256.slice(0, 7) : null);
  return { projects: short(manifest.payloads.projects), csms: short(manifest.payloads.csms) };
}
