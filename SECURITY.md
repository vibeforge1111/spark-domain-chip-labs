# Security policy

## Supported code

Security fixes target the latest commit on the default branch. Older snapshots
may no longer receive patches.

## Private vulnerability reporting

Do not open a public issue for a suspected vulnerability.

Use the repository's **Security** tab and select **Report a vulnerability** when
private vulnerability reporting is available. If that option is unavailable,
contact the repository owners through a private channel published by the
organization. Do not include secrets, personal data, or exploit details in a
public discussion.

Please include:

- the affected commit and surface;
- a minimal reproduction or proof of concept;
- the expected and observed security boundary;
- likely impact and any known prerequisites;
- a suggested mitigation, when available.

Maintainers will validate the report, coordinate remediation and disclosure,
and preserve reporter attribution unless anonymity is requested. Response and
resolution timing depends on severity, reproducibility, and maintainer
availability; this document does not promise a fixed service level.

## Scope

Reports about source generation, subprocess execution, filesystem authority,
MCP request handling, installer behavior, evidence integrity, or accidental
secret exposure are in scope. Vulnerabilities in third-party services should be
reported to their owners unless this repository's integration creates the
security failure.
