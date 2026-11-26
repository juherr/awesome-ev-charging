/** Site-wide constants shared by the layout and the pages. */

export const SITE_NAME = 'Awesome EV Charging';
export const REPO_URL = 'https://github.com/juherr/awesome-ev-charging';
export const CONTRIBUTING_URL = `${REPO_URL}/blob/main/CONTRIBUTING.md`;

/** The header navigation. `key` is what a page passes as the layout's `current`. */
export const NAV = [
  { key: 'specifications', label: 'Specifications', path: 'specifications/' },
  { key: 'projects', label: 'Developer Tools', path: 'projects/' },
  { key: 'csms', label: 'CSMS Directory', path: 'csms/' },
  { key: 'regulations', label: 'Regulations', path: 'regulations/' },
] as const;

export type NavKey = (typeof NAV)[number]['key'];
