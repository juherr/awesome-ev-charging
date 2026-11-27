import { describe, expect, it } from 'vitest';
import {
  DEFAULT_CSMS_STATE,
  apiCell,
  certificateLabel,
  csmsSearchText,
  deploymentLabel,
  featureLabel,
  featureLinks,
  matchesCsms,
  ocpiCell,
  ocppCell,
  parseCsmsState,
  productHref,
  serialiseCsmsState,
  sortedCertificates,
  sourceRef,
  statusLabel,
} from '../src/lib/csms';
import type { CsmsCertificate } from '../src/lib/data';
import { UNKNOWN_MARK } from '../src/lib/format';

const cert = (over: Partial<CsmsCertificate>): CsmsCertificate => ({
  number: 'OCA.1',
  ocpp_version: '1.6',
  type: 'Full',
  software_version: null,
  date: '2024-01-01',
  url: null,
  ...over,
});

describe('ocppCell', () => {
  it('sorts versions numerically and marks unknown', () => {
    expect(ocppCell({ ocpp_versions: ['2.0.1', '1.6', '1.5'] })).toBe('1.5, 1.6, 2.0.1');
    expect(ocppCell({ ocpp_versions: null })).toBe(UNKNOWN_MARK);
  });
});

describe('certificates', () => {
  it('labels a certificate with its version, type and software', () => {
    expect(certificateLabel(cert({ software_version: 'v1.0.0' }))).toBe('1.6 Full (v1.0.0)');
    expect(certificateLabel(cert({ ocpp_version: '2.0.1', type: 'Core + S' }))).toBe('2.0.1 Core + S');
  });

  it('orders by version, then date, then type', () => {
    const certs = [
      cert({ number: 'c', ocpp_version: '2.0.1', date: '2020-01-01' }),
      cert({ number: 'b', type: 'Security', date: '2023-01-01' }),
      cert({ number: 'a', type: 'Full', date: '2023-01-01' }),
      cert({ number: 'z', date: null }),
    ];
    expect(sortedCertificates(certs).map((c) => c.number)).toEqual(['z', 'a', 'b', 'c']);
  });
});

describe('productHref', () => {
  it('prefers the website, then the repository', () => {
    expect(productHref({ website: 'https://a.example', repo_url: 'https://github.com/a/b' })).toBe('https://a.example');
    expect(productHref({ website: null, repo_url: 'https://github.com/a/b' })).toBe('https://github.com/a/b');
    expect(productHref({ website: null, repo_url: null })).toBeNull();
  });

  it('never links a non-http(s) URL, falling back to the repository', () => {
    expect(productHref({ website: 'javascript:alert(1)', repo_url: null })).toBeNull();
    expect(productHref({ website: null, repo_url: 'data:text/html,x' })).toBeNull();
    expect(productHref({ website: ' JavaScript:alert(1)', repo_url: 'https://github.com/a/b' })).toBe(
      'https://github.com/a/b',
    );
  });
});

describe('data links', () => {
  it('keeps only the http(s) sources of a documented feature', () => {
    expect(featureLinks({ feature: 'Tariffs', source_urls: ['javascript:alert(1)', 'https://a', 'vbscript:x'] })).toEqual([
      'https://a',
    ]);
  });

  it('drops a non-http(s) OCPI source and API docs, keeping the Yes they attest', () => {
    expect(
      ocpiCell({ ocpi: null, features_documented: [{ feature: 'OCPI Roaming', source_urls: ['javascript:alert(1)'] }] }),
    ).toEqual({ label: 'Yes', links: [] });
    expect(apiCell({ api: null, api_docs: 'javascript:alert(1)' })).toEqual({ label: 'Yes', href: null });
  });

  it('does not link a non-http(s) source entry', () => {
    expect(sourceRef('javascript:alert(1)')).toEqual({ label: 'javascript:alert(1)', href: null });
  });
});

describe('ocpiCell', () => {
  it('links the documented OCPI Roaming feature', () => {
    expect(
      ocpiCell({ ocpi: true, features_documented: [{ feature: 'OCPI Roaming', source_urls: ['https://a', 'https://b'] }] }),
    ).toEqual({ label: 'Yes', links: ['https://a', 'https://b'] });
  });

  it('is an unlinked Yes when stated without a feature, and unknown otherwise', () => {
    expect(ocpiCell({ ocpi: true, features_documented: [] })).toEqual({ label: 'Yes', links: [] });
    expect(ocpiCell({ ocpi: null, features_documented: [] })).toBeNull();
  });
});

describe('apiCell', () => {
  it('links public docs, keeps a gated API unlinked, and never says no', () => {
    expect(apiCell({ api: true, api_docs: 'https://docs' })).toEqual({ label: 'Yes', href: 'https://docs' });
    expect(apiCell({ api: null, api_docs: 'https://docs' })).toEqual({ label: 'Yes', href: 'https://docs' });
    expect(apiCell({ api: true, api_docs: null })).toEqual({ label: 'Yes', href: null });
    expect(apiCell({ api: null, api_docs: null })).toBeNull();
  });
});

describe('labels', () => {
  it('names deployments and statuses, unknown when null', () => {
    expect(deploymentLabel('saas')).toBe('SaaS');
    expect(deploymentLabel('self-hosted')).toBe('Self-hosted');
    expect(deploymentLabel('both')).toBe('SaaS or self-hosted');
    expect(deploymentLabel('on-premise')).toBe('on-premise');
    expect(deploymentLabel(null)).toBe(UNKNOWN_MARK);
    expect(statusLabel('active')).toBe('Active');
    expect(statusLabel(null)).toBe(UNKNOWN_MARK);
  });

  it('uses the short labels of FEATURE_VOCAB', () => {
    expect(featureLabel('Advanced Security')).toBe('Security');
    expect(featureLabel('Local Authorization List Management')).toBe('Local Auth');
    expect(featureLabel('Something new')).toBe('Something new');
  });
});

describe('sourceRef', () => {
  it('links a URL, and a contributor to their GitHub profile', () => {
    expect(sourceRef('https://a.example/x')).toEqual({ label: 'a.example', href: 'https://a.example/x' });
    expect(sourceRef('contributor:juherr')).toEqual({ label: 'Contributor juherr', href: 'https://github.com/juherr' });
    expect(sourceRef('a note')).toEqual({ label: 'a note', href: null });
  });
});

describe('filter', () => {
  const row = { text: csmsSearchText({ name: 'SteVe OCPP Pro', company: 'Powerfill Ltd' }), certified: true, source: false };

  it('shows everything by default', () => {
    expect(matchesCsms(row, DEFAULT_CSMS_STATE)).toBe(true);
    expect(matchesCsms({ text: 'x', certified: false, source: false }, DEFAULT_CSMS_STATE)).toBe(true);
  });

  it('matches every word of the query against product and company', () => {
    expect(matchesCsms(row, { ...DEFAULT_CSMS_STATE, q: 'steve powerfill' })).toBe(true);
    expect(matchesCsms(row, { ...DEFAULT_CSMS_STATE, q: 'STEVE' })).toBe(true);
    expect(matchesCsms(row, { ...DEFAULT_CSMS_STATE, q: 'steve citrine' })).toBe(false);
  });

  it('keeps only certified or source-available products when asked', () => {
    expect(matchesCsms(row, { ...DEFAULT_CSMS_STATE, certified: true })).toBe(true);
    expect(matchesCsms(row, { ...DEFAULT_CSMS_STATE, source: true })).toBe(false);
    expect(matchesCsms(row, { q: '', certified: true, source: true })).toBe(false);
  });

  it('round-trips through the URL and drops defaults', () => {
    const state = { q: 'ampeco', certified: true, source: false };
    expect(serialiseCsmsState(state)).toBe('q=ampeco&certified=1');
    expect(parseCsmsState(serialiseCsmsState(state))).toEqual(state);
    expect(serialiseCsmsState(DEFAULT_CSMS_STATE)).toBe('');
    expect(parseCsmsState('?source=1&certified=0&q=%20')).toEqual({ q: '', certified: false, source: true });
  });

  it('reads an entry with no query, as Back may restore, as the defaults', () => {
    expect(parseCsmsState('')).toEqual(DEFAULT_CSMS_STATE);
    expect(parseCsmsState('?')).toEqual(DEFAULT_CSMS_STATE);
  });

  it('ignores parameters it does not own', () => {
    expect(parseCsmsState('?utm_source=x&certified=1&page=2')).toEqual({ ...DEFAULT_CSMS_STATE, certified: true });
  });
});
