/**
 * Internal links. The site is served under a base path (GitHub Pages project
 * site), so every internal href goes through `url()`; a link written as a bare
 * `/projects/` would point outside the site. `scripts/check-links.mjs` fails
 * the build check on one that slipped through.
 */

/** `path` resolved under `base`. A leading slash is relative to the base. */
export function joinBase(base: string, path: string): string {
  if (/^[a-z][a-z0-9+.-]*:/i.test(path) || path.startsWith('//')) {
    throw new Error(`url() takes a path inside the site, not an absolute URL: ${path}`);
  }
  const prefix = base.endsWith('/') ? base : `${base}/`;
  return prefix + path.replace(/^\/+/, '');
}

/** An internal link. Pass the trailing slash of a page (`trailingSlash: 'always'`). */
export function url(path: string): string {
  return joinBase(import.meta.env.BASE_URL, path);
}

/** The page of a project, from its `id` (the lowercased `owner/name`). */
export function projectPath(id: string): string {
  return url(`projects/${id}/`);
}
