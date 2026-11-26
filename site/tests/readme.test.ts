import { readFileSync } from 'node:fs';
import { join } from 'node:path';
import { describe, expect, it } from 'vitest';
import { README_URL, renderReadmeSection, rewriteHref } from '../src/lib/readme';

const README = `# Title

## Contents

- [Spec](#specifications)

## Specifications

Intro with a [vendored file](docs/third-party-assets.md) and an [issue](https://github.com/x/y/issues/new).

### OCPP (Open Charge Point Protocol)

- [2.1](./ocpp/OCPP-2.1) and the [annex](#ocpp-open-charge-point-protocol)
- See [elsewhere](#eichrecht-libraries) and [the CSMS list](csms.md#directory)
- ![badge](img/badge.svg)
- [root file](/legacy-projects.md)

#### Modules

| Module | Link |
| --- | --- |
| Locations | [2.1.1][loc] |

[loc]: https://example.org/loc

### eMI³ (eMobility ICT Interoperability)

Text.

## Regulation & Standards Bodies

### Modules

Second heading of the same name.

## Tools and Resources

### Eichrecht libraries
`;

describe('rewriteHref', () => {
  const anchors = new Set(['ocpp']);

  it('keeps external and mail links', () => {
    expect(rewriteHref('https://example.org/a', anchors)).toBe('https://example.org/a');
    expect(rewriteHref('mailto:a@b.c', anchors)).toBe('mailto:a@b.c');
    expect(rewriteHref('//cdn.example.org/x', anchors)).toBe('//cdn.example.org/x');
  });

  it('keeps an anchor of the rendered section on the page', () => {
    expect(rewriteHref('#ocpp', anchors)).toBe('#ocpp');
  });

  it('sends any other README anchor to the README on GitHub', () => {
    expect(rewriteHref('#elsewhere', anchors)).toBe(`${README_URL}#elsewhere`);
  });

  it('points relative and root-relative paths at the file on GitHub', () => {
    const blob = 'https://github.com/juherr/awesome-ev-charging/blob/main/';
    expect(rewriteHref('ocpp/OCPP-2.1', anchors)).toBe(`${blob}ocpp/OCPP-2.1`);
    expect(rewriteHref('./csms.md#x', anchors)).toBe(`${blob}csms.md#x`);
    expect(rewriteHref('/legacy-projects.md', anchors)).toBe(`${blob}legacy-projects.md`);
  });

  it('serves a relative image from raw.githubusercontent.com', () => {
    expect(rewriteHref('img/a.svg', anchors, { image: true })).toBe(
      'https://raw.githubusercontent.com/juherr/awesome-ev-charging/main/img/a.svg',
    );
  });
});

describe('renderReadmeSection', () => {
  const spec = renderReadmeSection(README, 'Specifications');

  it('renders only the section, without its own heading', () => {
    expect(spec.html).toContain('Intro with a');
    expect(spec.html).toContain('Text.');
    expect(spec.html).not.toContain('<h2 id="specifications"');
    expect(spec.html).not.toContain('Second heading of the same name');
    expect(spec.html).not.toContain('Contents');
  });

  it('shifts headings up one level and gives them the GitHub ids', () => {
    expect(spec.html).toContain('<h2 id="ocpp-open-charge-point-protocol">OCPP (Open Charge Point Protocol)</h2>');
    expect(spec.html).toContain('<h3 id="modules">Modules</h3>');
    expect(spec.html).toContain('<h2 id="emi-emobility-ict-interoperability">');
    expect(spec.headings.map((h) => h.id)).toEqual([
      'ocpp-open-charge-point-protocol',
      'modules',
      'emi-emobility-ict-interoperability',
    ]);
  });

  it('numbers a repeated heading the way GitHub does, across the whole README', () => {
    const regulations = renderReadmeSection(README, 'Regulation & Standards Bodies');
    expect(regulations.html).toContain('<h2 id="modules-1">Modules</h2>');
  });

  it('rewrites links: section anchors stay, others and files go to GitHub', () => {
    expect(spec.html).toContain('href="#ocpp-open-charge-point-protocol"');
    expect(spec.html).toContain(`href="${README_URL}#eichrecht-libraries"`);
    expect(spec.html).toContain('href="https://github.com/juherr/awesome-ev-charging/blob/main/docs/third-party-assets.md"');
    expect(spec.html).toContain('href="https://github.com/juherr/awesome-ev-charging/blob/main/ocpp/OCPP-2.1"');
    expect(spec.html).toContain('href="https://github.com/juherr/awesome-ev-charging/blob/main/csms.md#directory"');
    expect(spec.html).toContain('href="https://github.com/juherr/awesome-ev-charging/blob/main/legacy-projects.md"');
    expect(spec.html).toContain('src="https://raw.githubusercontent.com/juherr/awesome-ev-charging/main/img/badge.svg"');
    expect(spec.html).toContain('href="https://github.com/x/y/issues/new"');
  });

  it('resolves reference-style links and wraps tables in a scroll box', () => {
    expect(spec.html).toContain('href="https://example.org/loc"');
    expect(spec.html).toMatch(/<div class="table-scroll"><table>[\s\S]*<\/table>\s*<\/div>/);
  });

  it('links the section on GitHub by its README anchor', () => {
    expect(spec.githubUrl).toBe(`${README_URL}#specifications`);
    expect(renderReadmeSection(README, 'Regulation & Standards Bodies').githubUrl).toBe(
      `${README_URL}#regulation--standards-bodies`,
    );
  });

  it('renders a link or image with a non-http(s) URL as plain text', () => {
    const md = `## Specifications

A [x](javascript:alert(1)) and [y](JavaScript:alert(2) "t") and [z](data:text/html,hi) and ![pic](javascript:alert(3)) and [ok](https://example.org/ok).
`;
    const { html } = renderReadmeSection(md, 'Specifications');
    expect(html).not.toMatch(/javascript:|data:/i);
    expect(html).toContain('A x and y and z and pic and');
    expect(html).toContain('<a href="https://example.org/ok">ok</a>');
  });

  it('renders raw HTML, block and inline, as text', () => {
    const md = `## Specifications

<div onclick="alert(1)"><a href="javascript:alert(2)">x</a></div>

Inline <img src=x onerror="alert(3)"> and <A HREF="javascript:alert(4)">y</A> here.
`;
    const { html } = renderReadmeSection(md, 'Specifications');
    expect(html).not.toMatch(/<(?:div|a|img)\b/i);
    expect(html).toContain('&lt;div onclick=&quot;alert(1)&quot;&gt;');
    expect(html).toContain('Inline &lt;img src=x onerror=&quot;alert(3)&quot;&gt; and');
  });

  it('fails on a missing section', () => {
    expect(() => renderReadmeSection(README, 'Nope')).toThrow(/Nope/);
  });

  it('renders both sections of the real README with no relative link left', () => {
    const real = readFileSync(join(process.cwd(), '..', 'README.md'), 'utf-8');
    for (const name of ['Specifications', 'Regulation & Standards Bodies']) {
      const { html } = renderReadmeSection(real, name);
      const links = [...html.matchAll(/\s(?:href|src)="([^"]*)"/g)].map((m) => m[1]);
      expect(links.length).toBeGreaterThan(10);
      // Raw HTML renders as text; the real sections carry none, so none shows.
      expect(html).not.toContain('&lt;');
      for (const link of links) expect(link).toMatch(/^(?:https?:|mailto:|#)/);
    }
  });
});
