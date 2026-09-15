# Security Policy

## Scope

The bundled compositor performs local image reads and writes only. It does not authenticate to external services, transmit source images, or manage credentials. Image generation is performed separately by the host Codex environment.

Potentially sensitive reports include unintended file disclosure, path traversal, output written outside the requested directory, or accidental inclusion of private image content in repository files.

## Reporting

Do not attach private images, access tokens, or personal paths to a public issue. Use GitHub's private vulnerability-reporting interface when it is available for this repository. Otherwise open a minimal public issue asking the maintainer for a private contact route, without including sensitive details.

## Response limits

Repository validation and secret scanning cover the checked-out files only. They do not prove that Git history, third-party image models, or a user's local environment are free of sensitive data.
