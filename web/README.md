# Watch My Handle web

Static Next.js site deployed on GitHub Pages. The free checker calls the Cloudflare Worker configured by `NEXT_PUBLIC_CHECK_API_URL`, which probes public sources server-side and returns conservative evidence. Blocks, timeouts, and ambiguous absence remain `unknown`; the UI never turns a failed probe into an `available` result.

## Local

```bash
npm install
NEXT_PUBLIC_CHECK_API_URL=https://watch-my-handle-checker.<account>.workers.dev npm run dev
```

## Waitlist capture

Formspree is the selected $0 route. Create a free form on the assistant-operated account, then replace `REPLACE_WITH_FORM_ID` in `app/page.tsx`. The form ID is public routing metadata, not a secret.

## Deploy on GitHub Pages

`.github/workflows/pages.yml` builds and deploys `web/out` on every push to `main`. The workflow sets `GITHUB_PAGES=true`, so Next.js uses `/watch-my-handle` as `basePath` and `assetPrefix` for `https://deepanshupal.github.io/watch-my-handle/`.

Add the Worker origin as the repository variable `NEXT_PUBLIC_CHECK_API_URL`; the workflow passes it into the static build.
