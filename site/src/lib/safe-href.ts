/**
 * External links built from data. `csms.csv` is contributor-supplied, the
 * certificates mirror the OCA registry and the README is edited through pull
 * requests; none of them constrains a URL's scheme, so a `javascript:` or
 * `data:` value would otherwise become a clickable script. Every href derived
 * from data goes through `safeHref`, and a link it refuses renders as plain
 * text.
 */

const ALLOWED = new Set(['http:', 'https:']);

/**
 * `url` when it is an absolute http(s) URL, otherwise null. The scheme is read
 * by the WHATWG parser, which is what the browser runs: it trims leading
 * whitespace and drops tabs and newlines, so `" java\tscript:"` is caught as
 * `javascript:`. Relative and unparseable values are refused too.
 */
export function safeHref(url: string | null | undefined): string | null {
  if (!url) return null;
  let parsed: URL;
  try {
    parsed = new URL(url);
  } catch {
    return null;
  }
  return ALLOWED.has(parsed.protocol) ? url : null;
}
