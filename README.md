# AIPubs.cloud

**Open AI Research for Everyone** — a permanent, open-access archive for artificial intelligence research, whitepapers, reproducible experiments, datasets, and open scientific collaboration.

🌐 **Live site:** [www.aipubs.cloud](https://www.aipubs.cloud)

---

## What is AIPubs.cloud?

AIPubs.cloud is an open research publishing platform designed to support the creation, review, preservation, and global distribution of scientific, technical, and interdisciplinary research in artificial intelligence.

Every publication on AIPubs can carry a **RAIP evidence envelope** — a cryptographic provenance record combining:

- **ACF** (Artifact Content Fingerprint) — SHA-256 identity for the exact artifact bytes
- **ALC** (Artifact Lifecycle Chain) — tamper-evident history from draft to published
- **RAIP-SIGN** — cryptographic attestation by authors, reviewers, or the platform

No paywalls. No delays. Open science.

---

## Repository Structure

```
aipubs.cloud/
├── index.html              # Single-page application (all routes)
├── public/                 # Static assets (favicon, robots.txt, sitemap.xml)
├── docs/                   # Platform documentation and whitepapers
│   ├── RAIP_WHITEPAPER.md  # Research Artifact Integrity Protocol specification
│   └── PLATFORM_ENHANCEMENTS.md  # Product backlog
├── research/               # Community research submissions
│   ├── papers/             # Published research papers (Markdown/MDX)
│   ├── datasets/           # Linked or archived datasets
│   ├── experiments/        # Reproducible experiment logs
│   ├── reviews/            # Peer review records
│   └── templates/          # Submission templates
├── feature/                # Feature branches and proposals
├── paper/                  # Paper staging area
├── wrangler.jsonc          # Cloudflare Workers / Pages deployment config
└── .github/                # CI workflows and Dependabot config
```

---

## Quick Start

### View locally

AIPubs.cloud is a static single-page application with no build step required.

```bash
# Clone the repository
git clone https://github.com/aipubs-cloud/aipubs.cloud.git
cd aipubs.cloud

# Open directly in a browser
open index.html

# Or serve with any static file server
npx serve .
# → http://localhost:3000
```

### Deploy to Cloudflare Pages / Workers

```bash
# Install Wrangler
npm install -g wrangler

# Authenticate
wrangler login

# Deploy
wrangler deploy
```

---

## Publishing Research

Publishing on AIPubs uses a Git-backed workflow:

1. **Fork** this repository
2. **Create a branch** — `feature/your-paper-title`
3. **Copy the template** from `research/templates/paper-template.md`
4. **Write your paper** in Markdown, include datasets and code links
5. **Submit a pull request** — your paper enters open peer review
6. **RAIP envelope** is generated automatically upon merge

See [CONTRIBUTING.md](CONTRIBUTING.md) for the full submission guidelines.

---

## Technology

| Layer | Technology |
|---|---|
| Frontend | Vanilla HTML/JS, Tailwind CSS (CDN), Marked.js, KaTeX, Prism.js |
| Icons | Phosphor Icons |
| Hosting | Cloudflare Workers / Pages |
| Provenance | RAIP (Research Artifact Integrity Protocol) |
| CI | GitHub Actions (CodeQL, HTML validation) |

---

## Documentation

- [RAIP Whitepaper](docs/RAIP_WHITEPAPER.md) — Full specification for the provenance protocol
- [Platform Enhancements](docs/PLATFORM_ENHANCEMENTS.md) — Product roadmap and backlog
- [Contributing](CONTRIBUTING.md) — How to contribute research or code
- [Code of Conduct](CODE_OF_CONDUCT.md) — Community standards
- [Changelog](CHANGELOG.md) — Release history

---

## License

This project is licensed under the **Apache License 2.0**. See [LICENSE](LICENSE) for details.

Published research content is released under **CC BY 4.0** unless otherwise noted.

---

## Citation

If you use AIPubs.cloud infrastructure in your research, please cite:

```bibtex
@software{aipubs_cloud,
  title   = {AIpubs.cloud},
  author  = {Paiva, Kevin},
  year    = {2026},
  url     = {https://github.com/aipubs-cloud/aipubs.cloud},
  license = {Apache-2.0}
}
```

Or see [CITATION.cff](CITATION.cff) for the machine-readable citation metadata.