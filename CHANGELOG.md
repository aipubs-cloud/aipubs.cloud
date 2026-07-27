# Changelog

All notable changes to AIpubs.cloud are documented here.

---

# Version 1.1.0

## Site & Infrastructure Improvements

Added:

- Open Graph and Twitter Card meta tags for social sharing
- Canonical URL tag
- Favicon link in `<head>`
- Mobile navigation menu (hamburger) for small screens
- Hash-based URL routing with History API — pages are now bookmarkable and browser back/forward works
- `public/robots.txt` — SEO crawl instructions and sitemap reference
- `public/sitemap.xml` — all primary routes listed for search indexers
- `404.html` — custom not-found page for Cloudflare Pages
- `research/templates/paper-template.md` — structured Markdown template for new paper submissions
- Dynamic copyright year in footer (no longer hardcoded to 2024)
- Clipboard API BibTeX copy button with visual feedback on paper view
- Real GitHub and documentation links in footer (replacing `href="#"` placeholders)

Fixed:

- Removed duplicate Tailwind CSS typography CDN script (was loaded twice)
- Replaced deprecated `marked.setOptions({ highlight })` with `marked.use({ renderer })` API
- `feature/new-publication-system/readme.md` placeholder replaced with real feature overview

Updated:

- `README.md` — expanded from a single-line title to a full project README with setup instructions, structure overview, deployment guide, and citation
- `CITATION.cff` — fixed `YOUR_USERNAME` placeholder to the real repository URL
- `CONTRIBUTING.md` — no changes; confirmed complete

---

# Version 1.0.0

## Initial Release

Added:

- Initial repository structure
- Open source licensing
- Community guidelines
- Security policy
- Citation metadata
- Research organization framework

---

Future releases will document:

- Website improvements
- Publication features
- Research tools
- Infrastructure updates