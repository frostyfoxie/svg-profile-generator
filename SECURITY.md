# Security Policy

## Reporting a Security Vulnerability

If you discover a security vulnerability in SVG Profile Generator, please report it privately rather than opening a public issue.

When reporting a vulnerability, please include:

* A clear description of the issue
* Steps to reproduce the issue, if possible
* The potential impact
* Any relevant logs, screenshots, or proof-of-concept details

Please do not include personal access tokens, passwords, API keys, or other secrets in a report.

## Personal Access Tokens

SVG Profile Generator supports an optional `PAT_TOKEN` for accessing additional private repository statistics.

Never place a personal access token directly in:

* `profile.json`
* Workflow YAML files
* Source code
* Commit messages
* Issues or pull requests
* Public repository files

Store the token as a GitHub Actions repository secret named:

`PAT_TOKEN`

The action does not require a PAT for public repository statistics. The optional PAT is only needed when additional private repository data is desired.

## Token Security

Use the principle of least privilege when creating a token. A fine-grained personal access token is recommended, with access restricted to only the repositories that need to be included in the statistics.

If a token is accidentally exposed, revoke it immediately and create a new one.

## Supported Versions

Security fixes are generally applied to the latest maintained version of SVG Profile Generator.

| Version        | Supported   |
| -------------- | ----------- |
| v1             | Yes         |
| Older versions | Best effort |

Thank you for helping keep SVG Profile Generator and its users secure.
