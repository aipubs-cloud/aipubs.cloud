# Security Policy

## Supported Versions

The following versions of AIPubs.cloud are currently supported with security updates.

| Version           | Supported |
| ----------------- | :-------: |
| 1.x               |     ✅     |
| 0.x (Pre-release) |     ❌     |

Only the latest stable release receives security updates. Users are encouraged to upgrade to the most recent version as soon as practical.

---

## Reporting a Vulnerability

The AIPubs.cloud team takes security seriously and appreciates responsible disclosure of vulnerabilities.

### Reporting Process

Please **do not disclose security vulnerabilities publicly** until they have been reviewed and addressed.

Report vulnerabilities by one of the following methods:

* **GitHub Security Advisories (preferred)** using the repository's **Report a Vulnerability** feature.
* Email: **[security@aipubs.cloud](mailto:security@aipubs.cloud)**

Include as much information as possible:

* Description of the vulnerability
* Steps to reproduce
* A proof of concept, if available
* Affected version(s)
* Potential impact
* Suggested mitigation (optional)

---

## Response Timeline

Our goal is to respond according to the following schedule:

| Stage                   | Target Time                       |
| ----------------------- | --------------------------------- |
| Initial acknowledgement | Within 72 hours                   |
| Initial assessment      | Within 7 days                     |
| Status updates          | At least every 14 days            |
| Resolution              | As quickly as reasonably possible |

Complex issues may require additional investigation and coordination before a fix is released.

---

## Coordinated Disclosure

If the reported vulnerability is validated, we will:

* Investigate and reproduce the issue.
* Develop and test a fix.
* Publish a security update.
* Credit the reporter (if desired).
* Publish a security advisory describing the issue and its remediation.

We ask reporters to keep vulnerabilities confidential until a fix has been released.

---

## Out of Scope

The following generally do not qualify as security vulnerabilities unless they can be demonstrated to have a meaningful security impact:

* Missing HTTP security headers without exploitability
* Denial-of-service attacks requiring unrealistic resources
* Vulnerabilities in unsupported versions
* Issues caused solely by third-party software that have already been patched upstream
* Social engineering or phishing attacks
* Best-practice recommendations that do not expose an actual security risk

---

## Security Practices

AIPubs.cloud employs multiple layers of security, including:

* GitHub branch protection and code review
* GitHub Actions continuous integration
* Dependency and secret scanning
* Cryptographic hashing of publication artifacts
* RAIP provenance verification
* Static site deployment to minimize server-side attack surface
* Least-privilege access controls where practical

---

## Supported Cryptography

Where cryptographic verification is used, AIPubs.cloud follows modern, industry-standard algorithms and libraries. Deprecated or insecure algorithms are not accepted for new functionality.

---

## Contact

For general questions, use GitHub Discussions or Issues.

For confidential security matters, contact:

**[security@aipubs.cloud](mailto:security@aipubs.cloud)**
