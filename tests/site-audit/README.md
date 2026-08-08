# AIPubs Site Audit

The site audit is designed to run against either a deployed URL or a local/preview static server.

## Environment

- `MAIN_URL` defaults to `https://aipubs.cloud/`
- `BLOG_URL` defaults to `https://blog.aipubs.cloud/`
- `BLOG_ARTICLE_URL` may point to a specific published article
- `AUDIT_ENV` identifies the target, for example `production`, `preview`, or `local`

## Local usage

Start the site with any static HTTP server, then point the audit at that server:

```bash
MAIN_URL=http://127.0.0.1:4173 AUDIT_ENV=local npm run audit
```

For a separate blog output:

```bash
MAIN_URL=http://127.0.0.1:4173 BLOG_URL=http://127.0.0.1:4174 AUDIT_ENV=local npm run audit
```

The audit must never require source changes just to change its target URL. CI should supply preview URLs through environment variables.

## Production smoke testing

Scheduled CI should continue using the default production hosts. Production failures and preview failures should be reported as separate environments.
