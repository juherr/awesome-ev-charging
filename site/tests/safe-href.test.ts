import { describe, expect, it } from 'vitest';
import { safeHref } from '../src/lib/safe-href';

describe('safeHref', () => {
  it('keeps an absolute http or https URL as given', () => {
    expect(safeHref('https://example.com/docs?a=1#x')).toBe('https://example.com/docs?a=1#x');
    expect(safeHref('http://example.com')).toBe('http://example.com');
    expect(safeHref('HTTPS://EXAMPLE.COM/')).toBe('HTTPS://EXAMPLE.COM/');
  });

  it.each([
    'javascript:alert(1)',
    'JavaScript:alert(1)',
    'JAVASCRIPT:alert(1)',
    '  javascript:alert(1)',
    '\njavascript:alert(1)',
    'java\tscript:alert(1)',
    'java\nscript:alert(1)',
    'data:text/html,<script>alert(1)</script>',
    'vbscript:msgbox(1)',
    'file:///etc/passwd',
    'mailto:someone@example.com',
  ])('refuses the non-http(s) scheme of %j', (value) => {
    expect(safeHref(value)).toBeNull();
  });

  it.each(['/projects/', 'example.com', '//example.com/x', '#anchor', 'https://', 'http://[::1', ''])(
    'refuses the relative or unparseable %j',
    (value) => {
      expect(safeHref(value)).toBeNull();
    },
  );

  it('refuses null and undefined', () => {
    expect(safeHref(null)).toBeNull();
    expect(safeHref(undefined)).toBeNull();
  });
});
