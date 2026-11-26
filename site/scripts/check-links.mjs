#!/usr/bin/env node
// Post-build check of the internal links in dist/: every href/src that is not
// external must be root-relative, sit under the base path, and resolve to a
// built file (a page link needs its trailing slash, `trailingSlash: 'always'`).
// A link written without url() (src/lib/url.ts) fails here.
//
//   node scripts/check-links.mjs [dist] [base]
import { existsSync, readdirSync, readFileSync, statSync } from 'node:fs';
import { join, relative } from 'node:path';
import { fileURLToPath } from 'node:url';

const ATTRIBUTE = /\s(?:href|src)\s*=\s*(?:"([^"]*)"|'([^']*)')/gi;
const EXTERNAL = /^(?:[a-z][a-z0-9+.-]*:|\/\/)/i;

function* htmlFiles(dir) {
  for (const name of readdirSync(dir)) {
    const path = join(dir, name);
    if (statSync(path).isDirectory()) yield* htmlFiles(path);
    else if (name.endsWith('.html')) yield path;
  }
}

/** @returns {string | null} why `link` is broken, or null */
function problem(link, distDir, base) {
  if (link === '' || link.startsWith('#') || EXTERNAL.test(link)) return null;
  if (!link.startsWith('/')) return 'is document-relative; build it with url()';
  if (!link.startsWith(base)) return `is outside the base path ${base}; build it with url()`;
  const path = decodeURIComponent(link.slice(base.length).split(/[?#]/)[0]);
  const target = path === '' || path.endsWith('/') ? join(distDir, path, 'index.html') : join(distDir, path);
  return existsSync(target) && statSync(target).isFile() ? null : 'is not found in the build';
}

/** Every broken internal link in the HTML under `distDir`, one message each. */
export function checkLinks(distDir, base = '/awesome-ev-charging/') {
  const errors = [];
  for (const file of htmlFiles(distDir)) {
    const html = readFileSync(file, 'utf-8');
    for (const match of html.matchAll(ATTRIBUTE)) {
      const link = (match[1] ?? match[2]).replaceAll('&amp;', '&');
      const why = problem(link, distDir, base);
      if (why) errors.push(`${relative(distDir, file)}: ${link} ${why}`);
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
