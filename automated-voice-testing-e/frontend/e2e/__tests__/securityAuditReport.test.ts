import { describe, expect, it } from 'vitest';
import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';

const REPORT_PATH = resolve(__dirname, '../../../docs/security/SECURITY_AUDIT.md');

describe('security audit report', () => {
  it('documents OWASP, dependency scan, and penetration testing with remediation guidance', () => {
    const contents = readFileSync(REPORT_PATH, 'utf-8');

    expect(contents).toMatch(/# Security Audit Report/);
    expect(contents).toMatch(/## OWASP Top 10 Assessment/);
    expect(contents).toMatch(/## Dependency Vulnerability Scan/);
    expect(contents).toMatch(/## Penetration Testing Summary/);
    expect(contents).toMatch(/Severity:/i);
    expect(contents).toMatch(/Remediation:/i);
    expect(contents).toMatch(/Next Steps/i);
  });
});
