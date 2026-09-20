# Project status and next steps

_Last updated: 2026-09-20_

Watch My Handle is open-source first. The repository contains the complete CLI, 18 platform adapters, domain checks, alert transports, the GitHub Pages web app, and a server-side checker proxy implementation. Production rollout of the proxy and waitlist is intentionally paused. The current public site remains on GitHub Pages at <https://deepanshupal.github.io/claimwatch/>; no custom domain is planned for the current phase.

## What is implemented

- CLI checks for domains and 18 platforms.
- Conservative verdicts: blocks, throttles, timeouts, and ambiguous absence return `unknown`, never a false `available` result.
- State comparison for availability, ownership, and activity changes.
- Webhook and SMTP notifications.
- Static Next.js site for GitHub Pages, permanently using the `/claimwatch` base path.
- A minimal Cloudflare Worker in `worker/` that moves the 18 platform probes server-side and avoids browser CORS failures while preserving the same conservative verdict rules.
- Proxy-backed web UI with live-result detail, summary counts, and CLI as the power-user path.
- Formspree-compatible waitlist form slot. No production form ID has been configured yet.
- A versioned production audit protocol and known-taken fixtures in `audit/`.

## Checks completed so far

These are implementation smoke checks from 2026-09-20, run directly through the Worker code against public sources. They prove every adapter executes and returns one of the allowed states. They are **not** the final taken/available ground-truth audit, and they were not run through the production website.

The shared input was `deepanshupal`, except Mastodon, which used `gargron@mastodon.social` because a Mastodon instance is required.

| Platform | Smoke result | Evidence quality / finding |
| --- | --- | --- |
| GitHub | taken | Public API found a record. |
| YouTube | taken | Public profile endpoint responded; ownership not independently verified. |
| LinkedIn | taken | Public profile endpoint responded; ownership not independently verified. |
| Reddit | unknown | Public source returned HTTP 403. No availability claim made. |
| Threads | taken | Public profile endpoint responded; ownership not independently verified. |
| Twitch | taken | Public profile endpoint responded; ownership not independently verified. |
| Pinterest | taken | Public profile endpoint responded; ownership not independently verified. |
| Snapchat | taken | Public profile endpoint responded; ownership not independently verified. |
| Bluesky | available lead | Public API could not resolve the generated `.bsky.social` handle; confirmation is still required. |
| Mastodon | taken | Instance API found the known account. |
| Telegram | taken | Public profile endpoint responded; ownership not independently verified. |
| Product Hunt | unknown | Public source returned HTTP 403. No availability claim made. |
| Substack | taken | Public profile endpoint responded; ownership not independently verified. |
| Medium | unknown | Public source returned HTTP 403. No availability claim made. |
| dev.to | available lead | Public source returned 404; confirmation is still required. |
| npm | available lead | Registry returned 404; confirmation is still required. |
| PyPI | available lead | Registry returned 404; confirmation is still required. |
| Docker Hub | taken | Public API found a record. |

Automated checks completed:

- Worker unit tests cover strong 404, weak 404, success, timeout, Mastodon input, CORS, and all 18 adapters.
- Existing Python test suite passes.
- Next.js production build and TypeScript checks pass with the proxy URL configured.

## Current production state

- Hosting: GitHub Pages at <https://deepanshupal.github.io/claimwatch/>.
- Production base path: `/claimwatch`.
- CLI: ready for use from this repository.
- Browser checker on the currently deployed site: still the older direct-browser version, so CORS can produce many `unknown` results.
- Worker: implemented and tested locally, not deployed.
- Waitlist: UI is present, but no Formspree form ID is configured, so it is not operational.
- Cost incurred: $0.

## Release plan when rollout resumes

1. Deploy `worker/` to Cloudflare Workers on the free plan. No runtime secret or paid service is required.
2. Set the repository variable `NEXT_PUBLIC_CHECK_API_URL` to the deployed Worker origin.
3. Create a free Formspree form, replace `REPLACE_WITH_FORM_ID`, and confirm a test submission arrives.
4. Build and deploy the static site to GitHub Pages. Keep `/claimwatch`; do not buy or configure a domain.
5. Run the release audit in `audit/README.md`:
   - one independently verified taken fixture and one independently verified available fixture for every platform;
   - compare live website and CLI results;
   - treat any false `available` as a release blocker;
   - document justified `unknown` results with the platform-side reason;
   - confirm the Formspree submission, browser console/network state, and phone and desktop layouts.
6. Publish the completed audit table and screenshots with the release notes.

## Known limitations

- Public profile endpoints can return challenges, generic pages, redirects, or throttles. A response alone may prove that a page answered, not who owns it.
- Reddit, Product Hunt, and Medium returned 403 in the first server-side smoke run.
- Mastodon requires `handle@instance`; a bare handle cannot identify the server to query.
- Domain checks use RDAP with DNS fallback and still require registrar confirmation before purchase.
- A 404 is considered an availability lead only on sources where absence is meaningful. The UI always asks the user to confirm before claiming a name.
