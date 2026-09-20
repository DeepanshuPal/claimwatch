# Watch My Handle web

Next.js app for Vercel. The free checker runs in the visitor's browser and calls public endpoints directly. There is no checker backend, database, or paid service. Browser CORS restrictions are reported as `unknown`; the UI never turns a failed probe into an `available` result.

## Local

```bash
npm install
npm run dev
```

## Waitlist capture

Formspree is the selected $0 route. Create a free form at https://formspree.io/, then replace `REPLACE_WITH_FORM_ID` in `app/page.tsx`. This ID is public routing metadata, not a secret. Until that one-time setup, the form is intentionally not claimed as operational.

## Deploy on GitHub Pages

`.github/workflows/pages.yml` builds and deploys `web/out` on every push to `main`. The workflow sets `GITHUB_PAGES=true`, so Next.js uses `/claimwatch` as `basePath` and `assetPrefix` for the default project URL at `https://deepanshupal.github.io/claimwatch/`.

After `watchmyhandle.com` is attached in the repository's Pages settings, remove the `GITHUB_PAGES` environment variable from the workflow. The same static export then builds at the domain root. The canonical production hostname is already `https://watchmyhandle.com` in metadata, sitemap, and robots.

The site has no runtime server dependency. The checker calls public endpoints from the visitor's browser, and CORS-blocked checks stay `unknown`. The waitlist posts directly to Formspree after its form ID is configured.
