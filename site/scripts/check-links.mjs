#!/usr/bin/env node
// Post-build check of the internal links in dist/: every href/src that is not
// external must be root-relative, sit under the base path once its dot
// segments are resolved, and resolve to a built file inside dist/ (a page link
// needs its trailing slash, `trailingSlash: 'always'`).
// A link written without url() (src/lib/url.ts) fails here. An absolute URL
// must use http:, https: or mailto:, so a `javascript:` or `data:` URL that
// slipped past safeHref (src/lib/safe-href.ts) fails here too.
//
//   node scripts/check-links.mjs [dist] [base]
import { existsSync, readdirSync, readFileSync, statSync } from 'node:fs';
import { isAbsolute, join, relative, sep } from 'node:path';
import { fileURLToPath } from 'node:url';

const ATTRIBUTE = /\s(?:href|src)\s*=\s*(?:"([^"]*)"|'([^']*)'|([^\s"'=<>`]+))/gi;
const SCHEME = /^([a-z][a-z0-9+.-]*):/i;
const ALLOWED_SCHEMES = new Set(['http:', 'https:', 'mailto:']);
const NAMED_ENTITIES = { amp: '&', colon: ':', tab: '\t', newline: '\n', quot: '"', apos: "'", lt: '<', gt: '>' };

/** The attribute value the browser sees: character references decoded. */
function decodeEntities(value) {
  return value.replace(/&(?:#x([0-9a-f]+)|#(\d+)|([a-z]+));?/gi, (whole, hex, dec, name) => {
    if (hex) return String.fromCodePoint(parseInt(hex, 16));
    if (dec) return String.fromCodePoint(parseInt(dec, 10));
    return NAMED_ENTITIES[name.toLowerCase()] ?? whole;
  });
}

/**
 * The lowercased scheme of `url` as the browser's URL parser reads it, or
 * null: leading and trailing C0 controls and spaces are trimmed, and tabs and
 * newlines anywhere are dropped, so `" java\tscript:"` is `javascript:`.
 */
function schemeOf(url) {
  const cleaned = url.replace(/^[\u0000- ]+|[\u0000- ]+$/g, '').replace(/[\t\n\r]/g, '');
  const match = SCHEME.exec(cleaned);
  return match ? `${match[1].toLowerCase()}:` : null;
}

function* htmlFiles(dir) {
  for (const name of readdirSync(dir)) {
    const path = join(dir, name);
    if (statSync(path).isDirectory()) yield* htmlFiles(path);
    else if (name.endsWith('.html')) yield path;
  }
}

/** @returns {string | null} why `link` is broken, or null */
function problem(link, distDir, base) {
  const scheme = schemeOf(link);
  if (scheme) {
    return ALLOWED_SCHEMES.has(scheme) ? null : `has the scheme ${scheme}; only http:, https: and mailto: are allowed`;
  }
  if (link === '' || link.startsWith('#') || link.startsWith('//')) return null;
  if (!link.startsWith('/')) return 'is document-relative; build it with url()';
  // The path the browser requests: dot segments (`..`, `%2e%2e`) resolved,
  // query and fragment dropped. The base is checked on that, not on the raw
  // link, so `/base/../x/` cannot pass for a link under the base.
  const { pathname } = new URL(link, 'http://site.invalid');
  if (!pathname.startsWith(base)) return `is outside the base path ${base}; build it with url()`;
  const path = decodeURIComponent(pathname.slice(base.length));
  const target = path === '' || path.endsWith('/') ? join(distDir, path, 'index.html') : join(distDir, path);
  // An encoded slash (`..%2f`) is no dot segment to the URL parser, but
  // decodes to one on disk.
  const fromDist = relative(distDir, target);
  if (fromDist.split(sep)[0] === '..' || isAbsolute(fromDist)) return 'resolves outside the build';
  return existsSync(target) && statSync(target).isFile() ? null : 'is not found in the build';
}

/** Every broken internal link in the HTML under `distDir`, one message each. */
export function checkLinks(distDir, base = '/awesome-ev-charging/') {
  const errors = [];
  for (const file of htmlFiles(distDir)) {
    const html = readFileSync(file, 'utf-8');
    for (const match of html.matchAll(ATTRIBUTE)) {
      const value = match[1] ?? match[2] ?? match[3];
      const why = problem(decodeEntities(value), distDir, base);
      if (why) errors.push(`${relative(distDir, file)}: ${value} ${why}`);
    }
  }
  return errors;
}

if (process.argv[1] === fileURLToPath(import.meta.url)) {
  const [distDir = 'dist', base = '/awesome-ev-charging/'] = process.argv.slice(2);
  const errors = checkLinks(distDir, base);
  for (const error of errors) console.error(`✗ ${error}`);
  if (errors.length) {
    console.error(`${errors.length} broken internal link(s) in ${distDir}.`);
    process.exit(1);
  }
  console.log(`✓ Internal links in ${distDir} resolve under ${base}.`);
}
