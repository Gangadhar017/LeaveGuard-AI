# Security Policy

## Supported Versions

| Version | Supported          |
|---------|--------------------|
| latest (`main`) | ✅ Active support |
| older branches  | ❌ Not supported  |

## Reporting a Vulnerability

If you discover a security vulnerability in **LeafGuard AI**, please **do not** open a public
GitHub Issue. Instead, report it privately so we can patch it before disclosure.

### How to Report

1. Email the maintainers directly (see repository owner profile for contact info).
2. Include a clear description of the vulnerability.
3. Provide steps to reproduce, affected versions, and potential impact.
4. If possible, include a suggested fix or mitigation.

### What to Expect

- **Acknowledgement** within 48 hours of your report.
- **Status update** within 7 days with an assessment of severity and planned fix timeline.
- **Credit** in the release notes / CHANGELOG once the fix is shipped (unless you prefer to
  remain anonymous).

## Scope

The following are **in scope** for security reports:

- Remote code execution or arbitrary file write via the upload endpoint.
- Authentication or authorization bypass (if auth is added in future).
- Injection attacks (e.g. NoSQL injection in MongoDB queries).
- Path traversal vulnerabilities.
- Sensitive data exposure (API keys, credentials, PII).

The following are **out of scope**:

- Denial-of-service attacks requiring special network access.
- Issues in third-party dependencies that are already publicly disclosed with an available fix
  (please open a dependency-update PR instead).

## Preferred Languages

We prefer all communications in **English**.
