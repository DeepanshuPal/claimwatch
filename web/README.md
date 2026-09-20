# Watch My Handle web

Next.js app for Vercel. The free checker runs in the visitor's browser and calls public endpoints directly. There is no checker backend, database, or paid service. Browser CORS restrictions are reported as `unknown`; the UI never turns a failed probe into an `available` result.

## Local

```bash
npm install
npm run dev
```

## Waitlist capture

Formspree is the selected $0 route. Create a free form at https://formspree.io/, then replace `REPLACE_WITH_FORM_ID` in `app/page.tsx`. This ID is public routing metadata, not a secret. Until that one-time setup, the form is intentionally not claimed as operational.

## Deploy

Set Vercel's root directory to `web`. No environment variables are required. The canonical production hostname is `https://watchmyhandle.com` in metadata, sitemap, and robots.
