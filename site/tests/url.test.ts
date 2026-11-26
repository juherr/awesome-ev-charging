import { describe, expect, it } from 'vitest';
import { joinBase, projectPath, url } from '../src/lib/url';

describe('joinBase', () => {
  const base = '/awesome-ev-charging/';

  it('prefixes a relative path with the base', () => {
    expect(joinBase(base, 'projects/')).toBe('/awesome-ev-charging/projects/');
  });

  it('treats a leading slash as relative to the base, not the host', () => {
    expect(joinBase(base, '/csms/')).toBe('/awesome-ev-charging/csms/');
  });

  it('returns the base itself for the home page', () => {
    expect(joinBase(base, '')).toBe('/awesome-ev-charging/');
    expect(joinBase(base, '/')).toBe('/awesome-ev-charging/');
  });

  it('accepts a base without its trailing slash', () => {
    expect(joinBase('/awesome-ev-charging', 'projects/')).toBe('/awesome-ev-charging/projects/');
  });

  it('works at the domain root', () => {
    expect(joinBase('/', 'projects/')).toBe('/projects/');
  });

  it('keeps a query string and a fragment', () => {
    expect(joinBase(base, 'projects/?protocol=OCPP#list')).toBe(
      '/awesome-ev-charging/projects/?protocol=OCPP#list',
    );
  });

  it('does not add a trailing slash the caller left out', () => {
    expect(joinBase(base, 'favicon.svg')).toBe('/awesome-ev-charging/favicon.svg');
  });

  it('refuses an absolute URL, which must not be rebased', () => {
    expect(() => joinBase(base, 'https://github.com/juherr')).toThrow(/absolute/);
    expect(() => joinBase(base, '//example.org/x')).toThrow(/absolute/);
  });
});

describe('url', () => {
  it('uses import.meta.env.BASE_URL', () => {
    expect(url('projects/')).toBe(joinBase(import.meta.env.BASE_URL, 'projects/'));
  });
});

describe('projectPath', () => {
  it('maps an id to its two-segment page path with a trailing slash', () => {
    expect(projectPath('steve-community/steve')).toBe(url('projects/steve-community/steve/'));
  });

  it('keeps a dot in the repository name as part of the path', () => {
    expect(projectPath('owner/lib.js')).toBe(url('projects/owner/lib.js/'));
  });
});
