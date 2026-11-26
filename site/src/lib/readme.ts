/**
 * Editorial pages rendered from the repository README at build time: one
 * `## ` section each, until the next `## ` heading.
 *
 * Heading ids follow GitHub's slugger over the whole README, so an in-README
 * anchor (`#eichrecht`) means the same heading here as on GitHub. Links are
 * rewritten because the site does not ship the repository's files: a relative
 * path goes to the file on GitHub, an anchor into the rendered section stays a
 * page anchor, and any other anchor goes to the README on GitHub.
 */
import GithubSlugger from 'github-slugger';
import { Lexer, Parser, Renderer, type Token, type Tokens } from 'marked';
import { REPO_URL } from './site';

export const README_URL = `${REPO_URL}/blob/main/README.md`;
const BLOB_URL = `${REPO_URL}/blob/main/`;
const RAW_URL = 'https://raw.githubusercontent.com/juherr/awesome-ev-charging/main/';
const EXTERNAL = /^(?:[a-z][a-z0-9+.-]*:|\/\/)/i;

/** Where `href`, found in the README, points once rendered on the site. */
export function rewriteHref(href: string, sectionIds: ReadonlySet<string>, { image = false } = {}): string {
  if (EXTERNAL.test(href)) return href;
  if (href.startsWith('#')) {
    const id = decodeURIComponent(href.slice(1));
    return sectionIds.has(id) ? href : `${README_URL}${href}`;
  }
  const path = href.replace(/^(?:\.\/|\/)+/, '');
  return (image ? RAW_URL : BLOB_URL) + path;
}

export interface SectionHeading {
  /** The heading level on the page: the README's `###` becomes an `h2`. */
  depth: number;
  id: string;
  text: string;
}

export interface RenderedSection {
  html: string;
  /** The section on GitHub, for the "rendered copy" notice. */
  githubUrl: string;
  headings: SectionHeading[];
}

/** The text GitHub slugs: the heading's inline content without its markup. */
function plainText(tokens: Token[]): string {
  return tokens
    .map((t) => {
      const inner = (t as Tokens.Generic).tokens;
      if (inner?.length) return plainText(inner);
      return t.type === 'text' || t.type === 'codespan' || t.type === 'escape' ? (t as Tokens.Text).text : '';
    })
    .join('');
}

function eachToken(tokens: Token[], visit: (t: Token) => void): void {
  for (const t of tokens) {
    visit(t);
    const generic = t as Tokens.Generic;
    if (generic.tokens) eachToken(generic.tokens, visit);
    if (t.type === 'list') for (const item of (t as Tokens.List).items) eachToken(item.tokens, visit);
    if (t.type === 'table') {
      const table = t as Tokens.Table;
      for (const cell of [...table.header, ...table.rows.flat()]) eachToken(cell.tokens, visit);
    }
  }
}

/** Render the README section `## <name>` (its heading excluded) to HTML. */
export function renderReadmeSection(markdown: string, name: string): RenderedSection {
  const tokens = new Lexer({ gfm: true }).lex(markdown);

  // One slugger over every heading of the README, in order, as GitHub does,
  // so a repeated heading gets the same `-1` suffix here as there.
  const slugger = new GithubSlugger();
  const ids = new Map<Token, string>();
  for (const t of tokens) if (t.type === 'heading') ids.set(t, slugger.slug(plainText((t as Tokens.Heading).tokens)));

  const start = tokens.findIndex((t) => t.type === 'heading' && (t as Tokens.Heading).depth === 2 && plainText((t as Tokens.Heading).tokens) === name);
  if (start === -1) throw new Error(`README.md has no "## ${name}" section`);
  let end = tokens.findIndex((t, i) => i > start && t.type === 'heading' && (t as Tokens.Heading).depth <= 2);
  if (end === -1) end = tokens.length;
  const section = tokens.slice(start + 1, end);

  const headings: SectionHeading[] = [];
  for (const t of section) {
    if (t.type !== 'heading') continue;
    const h = t as Tokens.Heading;
    headings.push({ depth: h.depth - 1, id: ids.get(t)!, text: plainText(h.tokens) });
  }
  const sectionIds = new Set(headings.map((h) => h.id));

  eachToken(section, (t) => {
    if (t.type === 'link') (t as Tokens.Link).href = rewriteHref((t as Tokens.Link).href, sectionIds);
    if (t.type === 'image') (t as Tokens.Image).href = rewriteHref((t as Tokens.Image).href, sectionIds, { image: true });
  });

  const renderer = new Renderer();
  const defaultTable = renderer.table.bind(renderer);
  let headingIndex = 0;
  renderer.heading = function ({ tokens: inline }: Tokens.Heading) {
    const { depth, id } = headings[headingIndex++];
    return `<h${depth} id="${id}">${this.parser.parseInline(inline)}</h${depth}>\n`;
  };
  renderer.table = (token: Tokens.Table) => `<div class="table-scroll">${defaultTable(token)}</div>\n`;

  const html = new Parser({ gfm: true, renderer }).parse(section);
  return { html, githubUrl: `${README_URL}#${ids.get(tokens[start])}`, headings };
}
