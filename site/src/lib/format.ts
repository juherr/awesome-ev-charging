/**
 * Display strings for project records. Every helper renders a null as
 * unknown (a dash), never as "no".
 */
import type { Host, Project } from './data';
import { HOST_LABELS } from './filter';
import { safeHref } from './safe-href';
import { REPO_URL } from './site';

export const UNKNOWN_MARK = '—';

const NUMBER = new Intl.NumberFormat('en-US');

export function formatCount(n: number | null): string {
  return n === null ? UNKNOWN_MARK : NUMBER.format(n);
}

/** The `YYYY-MM-DD` part of an ISO timestamp. */
export function formatDate(iso: string | null): string {
  return iso === null ? UNKNOWN_MARK : iso.slice(0, 10);
}

/** `OCPP 1.6, 2.0.1 · OCPI 2.2.1`, or null when no version is known. */
export function versionsSummary(p: Pick<Project, 'ocpp_versions' | 'ocpi_versions'>): string | null {
  const parts = [
    p.ocpp_versions?.length ? `OCPP ${p.ocpp_versions.join(', ')}` : null,
    p.ocpi_versions?.length ? `OCPI ${p.ocpi_versions.join(', ')}` : null,
  ].filter((s): s is string => s !== null);
  return parts.length ? parts.join(' · ') : null;
}

/** The one-line meta of a directory card: versions · language · stars. */
export function cardMeta(p: Pick<Project, 'ocpp_versions' | 'ocpi_versions' | 'language' | 'stars'>): string {
  const stars = p.stars === null ? `Stars ${UNKNOWN_MARK}` : `${formatCount(p.stars)} ${p.stars === 1 ? 'star' : 'stars'}`;
  return [versionsSummary(p) ?? `Versions ${UNKNOWN_MARK}`, p.language ?? `Language ${UNKNOWN_MARK}`, stars].join(' · ');
}

export function hostLabel(host: Host | null): string {
  return HOST_LABELS[host ?? 'unknown'];
}

/** The link to the canonical upstream repository, null unless it is http(s). */
export function sourceHref(p: Pick<Project, 'url'>): string | null {
  return safeHref(p.url);
}

/** The label of the link to the canonical upstream repository. */
export function sourceLabel(host: Host | null): string {
  return host === 'github' || host === 'codeberg' ? `View source on ${HOST_LABELS[host]}` : 'View source';
}

/** The discovery sources of docs/public-data.md (`discovered_via`), in words. */
const DISCOVERY: Record<string, string> = {
  topic: 'a GitHub topic match',
  manual: 'a manual addition',
  readme: 'a link in the curated README',
  'starred-list': 'a curated GitHub stars list',
  codeberg: 'the Codeberg listing',
};

function sentenceList(items: string[]): string {
  if (items.length <= 1) return items.join('');
  return `${items.slice(0, -1).join(', ')} and ${items[items.length - 1]}`;
}

export function discoveredViaText(sources: string[]): string {
  if (!sources.length) return 'How it was found is unknown.';
  return `Found through ${sentenceList(sources.map((s) => DISCOVERY[s] ?? s))}.`;
}

/** A new issue on the awesome list, to correct what it says about a project. */
export function correctionUrl(fullName: string): string {
  return `${REPO_URL}/issues/new?${new URLSearchParams({ title: `Correction: ${fullName}` })}`;
}
