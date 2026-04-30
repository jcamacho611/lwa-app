# Security Policy

## Reporting a Vulnerability

If you discover a security vulnerability in this repository, **do not open a public issue**.

Contact the team directly at: security@lwa.app

Include:
- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Any suggested remediation

We will acknowledge your report within 72 hours and aim to resolve confirmed vulnerabilities within 14 days.

## Secret Handling

- All secrets and API keys must be stored in `.env` files, never committed to git
- `.env`, `.env.local`, `.env.production`, `.env.staging` are all gitignored
- Use `.env.example` (with placeholder values only) to document required variables
- No API keys, tokens, or credentials may appear in frontend bundles or client-side code
- The `NEXT_PUBLIC_` prefix exposes variables to the browser — use it only for non-sensitive public config

## Scope

- No crypto wallet addresses are live in this codebase
- No securities are offered, sold, or solicited through this platform
- Investment and equity discussions require legal review before any communication
- The Whop integration is the only live payment pathway; all others are in development

## Dependencies

Run `npm audit` in `lwa-web/` regularly. Address high and critical findings before deployment.
