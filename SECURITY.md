# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| latest  | :white_check_mark: |

## Reporting a Vulnerability

If you discover a security vulnerability in this project, please report it responsibly.

**DO NOT** open a public GitHub issue for security vulnerabilities.

### How to Report

1. **Email**: Send a description to the maintainers via GitHub DM or the repository's private disclosure channel.
2. **Include**:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact assessment
   - Suggested fix (if available)

### What to Expect

- **Acknowledgment**: We will acknowledge receipt within 48 hours.
- **Assessment**: We will investigate and validate the report within 5 business days.
- **Resolution**: Critical vulnerabilities will be patched as soon as possible. We will coordinate disclosure timing with the reporter.
- **Credit**: Unless you prefer otherwise, we will credit reporters in the release notes.

## Security Best Practices

- Keep dependencies up to date
- Review all pull requests for security implications
- Use environment variables for secrets (never commit them)
- Follow least-privilege principles for API access
- Enable branch protection rules on the main branch

## Scope

This security policy applies to the latest version of the codebase on the default branch. Older versions are not actively maintained for security patches.
