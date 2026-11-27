import { describe, expect, it } from 'vitest';
import {
  UNKNOWN_MARK,
  cardMeta,
  correctionUrl,
  discoveredViaText,
  formatCount,
  formatDate,
  sourceHref,
  sourceLabel,
  versionsSummary,
} from '../src/lib/format';

const base = { ocpp_versions: null, ocpi_versions: null, language: null, stars: null };

describe('formatCount', () => {
  it('groups thousands and marks unknown', () => {
    expect(formatCount(1050)).toBe('1,050');
    expect(formatCount(0)).toBe('0');
    expect(formatCount(null)).toBe(UNKNOWN_MARK);
  });
});

describe('formatDate', () => {
  it('keeps the date part of an ISO timestamp', () => {
    expect(formatDate('2026-06-30T12:00:00Z')).toBe('2026-06-30');
    expect(formatDate(null)).toBe(UNKNOWN_MARK);
  });
});

describe('versionsSummary', () => {
  it('joins both protocols, and null when neither is known', () => {
    expect(versionsSummary({ ocpp_versions: ['1.6', '2.0.1'], ocpi_versions: ['2.2.1'] })).toBe(
      'OCPP 1.6, 2.0.1 · OCPI 2.2.1',
    );
    expect(versionsSummary({ ocpp_versions: null, ocpi_versions: ['2.1.1'] })).toBe('OCPI 2.1.1');
    expect(versionsSummary({ ocpp_versions: [], ocpi_versions: null })).toBeNull();
  });
});

describe('cardMeta', () => {
  it('lists versions, language and stars', () => {
    expect(cardMeta({ ...base, ocpp_versions: ['1.6'], language: 'Go', stars: 1200 })).toBe(
      'OCPP 1.6 · Go · 1,200 stars',
    );
  });

  it('shows unknown as a dash, never as "no"', () => {
    expect(cardMeta(base)).toBe('Versions — · Language — · Stars —');
    expect(cardMeta(base)).not.toMatch(/\bno\b/i);
  });

  it('says "1 star"', () => {
    expect(cardMeta({ ...base, stars: 1 })).toBe('Versions — · Language — · 1 star');
  });
});

describe('sourceLabel', () => {
  it('names the host it links to', () => {
    expect(sourceLabel('github')).toBe('View source on GitHub');
    expect(sourceLabel('codeberg')).toBe('View source on Codeberg');
    expect(sourceLabel('other')).toBe('View source');
    expect(sourceLabel(null)).toBe('View source');
  });
});

describe('sourceHref', () => {
  it('links the upstream repository only over http(s)', () => {
    expect(sourceHref({ url: 'https://github.com/a/b' })).toBe('https://github.com/a/b');
    expect(sourceHref({ url: 'javascript:alert(1)' })).toBeNull();
    expect(sourceHref({ url: null })).toBeNull();
  });
});

describe('discoveredViaText', () => {
  it('says in words how ingest found the repo', () => {
    expect(discoveredViaText(['readme', 'starred-list', 'topic'])).toBe(
      'Found through a link in the curated README, a curated GitHub stars list and a GitHub topic match.',
    );
    expect(discoveredViaText(['codeberg'])).toBe('Found through the Codeberg listing.');
    expect(discoveredViaText(['manual', 'topic'])).toBe('Found through a manual addition and a GitHub topic match.');
  });

  it('passes an unexpected source through and says when none is known', () => {
    expect(discoveredViaText(['gitlab-search'])).toBe('Found through gitlab-search.');
    expect(discoveredViaText([])).toBe('How it was found is unknown.');
  });
});

describe('correctionUrl', () => {
  it('opens an issue on the awesome list, titled after the project', () => {
    expect(correctionUrl('steve-community/steve')).toBe(
      'https://github.com/juherr/awesome-ev-charging/issues/new?title=Correction%3A+steve-community%2Fsteve',
    );
  });
});
