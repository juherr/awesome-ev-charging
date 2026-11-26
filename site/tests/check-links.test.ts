import { mkdirSync, mkdtempSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { dirname, join } from 'node:path';
import { afterEach, describe, expect, it } from 'vitest';
import { checkLinks } from '../scripts/check-links.mjs';

const BASE = '/awesome-ev-charging/';
const temps: string[] = [];
afterEach(() => {
  while (temps.length) rmSync(temps.pop()!, { recursive: true, force: true });
});

function dist(files: Record<string, string>): string {
  const dir = mkdtempSync(join(tmpdir(), 'aec-site-dist-'));
  temps.push(dir);
  for (const [path, content] of Object.entries(files)) {
    mkdirSync(dirname(join(dir, path)), { recursive: true });
    writeFileSync(join(dir, path), content);
  }
  return dir;
}

const page = (body: string) => `<!doctype html><html><body>${body}</body></html>`;

describe('checkLinks', () => {
  it('accepts internal links under the base that resolve to a built file', () => {
    const dir = dist({
      'index.html': page(
        '<a href="/awesome-ev-charging/projects/">p</a><a href="/awesome-ev-charging/projects/?q=x#top">q</a>' +
          '<link href="/awesome-ev-charging/_astro/a.css" rel="stylesheet">',
      ),
      'projects/index.html': page(''),
      '_astro/a.css': '',
    });
    expect(checkLinks(dir, BASE)).toEqual([]);
  });

  it('ignores external links, fragments and mail links', () => {
    const dir = dist({
      'index.html': page(
        '<a href="https://github.com/juherr">g</a><a href="#main">m</a><a href="mailto:a@b.c">e</a>' +
          '<a href="//cdn.example.org/x">c</a>',
      ),
    });
    expect(checkLinks(dir, BASE)).toEqual([]);
  });

  it('flags any href or src whose scheme is not http, https or mailto', () => {
    const dir = dist({
      'index.html': page(
        '<a href="data:text/html,hi">d</a><img src="ftp://example.org/x.png" alt=""><a href="tel:+33100">t</a>',
      ),
    });
    expect(checkLinks(dir, BASE)).toEqual([
      expect.stringMatching(/^index\.html: data:text\/html,hi .*scheme/),
      expect.stringMatching(/^index\.html: ftp:\/\/example\.org\/x\.png .*scheme/),
      expect.stringMatching(/^index\.html: tel:\+33100 .*scheme/),
    ]);
  });

  it('flags javascript: in any case, spacing or encoding the browser accepts', () => {
    const variants = [
      'javascript:alert(1)',
      'JavaScript:alert(1)',
      ' \tjavascript:alert(1)',
      'java\tscript:alert(1)',
      'java&#10;script:alert(1)',
      '&#106;avascript:alert(1)',
      '&#x6A;avascript&colon;alert(1)',
    ];
    const anchors = variants.map((v) => `<a href="${v}">x</a>`).join('');
    const dir = dist({ 'index.html': page(`${anchors}<a href=javascript:alert(2)>u</a>`) });
    const errors = checkLinks(dir, BASE);
    expect(errors).toHaveLength(variants.length + 1);
    for (const error of errors) expect(error).toMatch(/^index\.html: .* has the scheme javascript:/);
  });

  it('flags a root-relative link that escapes the base path', () => {
    const dir = dist({ 'index.html': page('<a href="/projects/">p</a>') });
    expect(checkLinks(dir, BASE)).toEqual([
      expect.stringMatching(/index\.html.*\/projects\/.*base/),
    ]);
  });

  it('flags a document-relative link, which breaks when the page moves', () => {
    const dir = dist({ 'index.html': page('<a href="projects/">p</a>') });
    expect(checkLinks(dir, BASE)).toEqual([expect.stringMatching(/index\.html.*projects\//)]);
  });

  it('flags an internal link to a page that was not built', () => {
    const dir = dist({ 'index.html': page('<a href="/awesome-ev-charging/nowhere/">n</a>') });
    expect(checkLinks(dir, BASE)).toEqual([expect.stringMatching(/nowhere.*not found/)]);
  });

  it('flags a page link without its trailing slash', () => {
    const dir = dist({
      'index.html': page('<a href="/awesome-ev-charging/projects">p</a>'),
      'projects/index.html': page(''),
    });
    expect(checkLinks(dir, BASE)).toEqual([expect.stringMatching(/projects.*not found/)]);
  });

  it('checks nested pages and src attributes too', () => {
    const dir = dist({
      'index.html': page(''),
      'projects/a/b/index.html': page('<img src="/img/x.png" alt="">'),
    });
    expect(checkLinks(dir, BASE)).toEqual([expect.stringMatching(/projects\/a\/b\/index\.html/)]);
  });
});
