# Claimwatch checker Worker

A minimal Cloudflare Worker proxy for the 18 checks shown on Watch My Handle. It sends live public-source requests from the server so browser CORS does not turn the entire result set into `unknown`.

Honesty is the invariant: only dependable 404/API-negative signals become `available`. Throttling, challenges, timeouts, and ambiguous 404s remain `unknown`. A result is evidence, not a guarantee; users must confirm before claiming a name.

## Deploy on Cloudflare's free plan

```bash
npm install
npm test
npx wrangler login
npm run deploy
```

The only endpoint is `GET /check?platform=github&name=example`; `/health` reports the adapter count and deployed version. No API secret is required at runtime. CORS is restricted to the GitHub Pages origin, the planned custom domain, and local development.

After deployment, set `NEXT_PUBLIC_CHECK_API_URL` to the returned `workers.dev` origin for the web build.
