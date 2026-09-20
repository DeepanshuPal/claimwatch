# Watch My Handle

**Know when a name moves.** Watch My Handle is powered by the open-source `watch-my-handle` CLI that watches domains and handles for availability, ownership changes, and activity changes, then emits webhook or email alerts.

It is for the awkward window between “we want that identity” and “someone remembered to check”: a founder waiting on a domain, a team protecting a brand, or an individual tracking the same handle across platforms.

Watch My Handle is self-hostable and has no required server component. Run it from cron, a $0 GitHub Actions schedule, or any machine that can keep a small JSON state file.

> **Alpha software.** Platform checks are evidence, not a claim guarantee. Confirm availability in the platform or registrar before making decisions.

## What works

| Target | Signal source | Quality | Availability | Ownership/activity |
| --- | --- | --- | --- | --- |
| Domain | RDAP + DNS fallback | Strong registry evidence | Yes, registrar confirmation required | Registry handle and event dates |
| GitHub | Public REST API | Strong | Yes | Numeric account ID, `updated_at` |
| Instagram | Optional Apify actor; raw profile fallback | Stronger with Apify, weak raw | Unknown on absence/throttle | Profile ID/activity when Apify exposes it |
| npm, PyPI, Docker Hub | Public registry APIs | Strong | Yes | Package/user identity; versions where exposed |
| Mastodon | Instance account lookup | Strong when `handle@instance` is supplied | Yes per instance | Instance account ID, last status date |
| YouTube, Reddit, Twitch, Pinterest, Bluesky, Product Hunt, Substack, Medium, dev.to | Public profile endpoints | Best effort | A 404 is a lead; confirm in-platform | Handle only unless source exposes more |
| X, LinkedIn, Threads, Snapchat, Telegram, TikTok | Public profile pages | Weak / frequently challenged | Conservative `unknown` on ambiguous 404 or throttle | Handle only |

Every adapter is conservative. A challenge, rate limit, geo block, login wall, redirect, or ambiguous `404` becomes `unknown`, never a false `available`.

### Instagram: optional Apify backend

Set `APIFY_TOKEN` to use Apify's Instagram Profile Scraper (`apify/instagram-profile-scraper`) for Instagram checks. The actor starts around **$1.60 per 1,000 profiles** and new accounts can use free platform credits first; check current Apify pricing before relying on that number. The token is read only from the environment and must never be committed. Without it, the watch-my-handle CLI uses the public profile fallback and reports `unknown` when Instagram throttles or challenges the request.

## Quickstart

```bash
git clone https://github.com/DeepanshuPal/watch-my-handle.git
cd watch-my-handle
python -m venv .venv
source .venv/bin/activate
pip install -e .
cp watch-my-handle.example.yml watch-my-handle.yml
watch-my-handle --config watch-my-handle.yml --no-alerts
```

The first run emits `first_seen` events and writes `.watch-my-handle/state.json`. Later runs emit only field changes:

- `availability_changed`
- `owner_changed`
- `last_activity_changed`

Remove `--no-alerts` after configuring a transport.

## Configure targets

```yaml
targets:
  - platform: domain
    domain: your-brand.com
  - platform: github
    handle: your-brand
  - platform: x
    handle: your_brand
  - platform: instagram
    handle: your_brand
  - platform: tiktok
    handle: your_brand
```

JSON configs are supported too. The committed example contains **sample data only**.

## Alerts

### Webhook

```yaml
alerts:
  webhook:
    url: "${WATCH_MY_HANDLE_WEBHOOK_URL}"
```

The watch-my-handle CLI sends a JSON body with `source` and an `events` array. Point it at your own service, n8n, or another self-hosted webhook consumer.

### SMTP email

```yaml
alerts:
  smtp:
    host: smtp.example.com
    port: 587
    username: "${SMTP_USERNAME}"
    password: "${SMTP_PASSWORD}"
    from: alerts@example.com
    to: you@example.com
```

Secrets are read from environment variables at runtime. Never commit a filled config or `.env` file.

## Run it for nearly $0

### GitHub Actions (recommended)

Copy the committed `.github/workflows/watch-my-handle.yml`, add your `watch-my-handle.yml`, and configure any optional repository secrets. It runs daily at 06:17 UTC and commits the state file back so change detection survives ephemeral runners. Change the cron to `17 * * * *` for hourly checks. A copy also lives at `docs/watch-my-handle-workflow.yml` for installations where the GitHub token used to publish the watch-my-handle CLI cannot create workflow files.

The workflow uses only GitHub-hosted Actions and the public repository. Normal public-repo usage fits GitHub's free model; platform quotas and policies can change.

### Cron


Cron is enough:

```cron
17 */6 * * * cd /opt/watch-my-handle && .venv/bin/watch-my-handle -c watch-my-handle.yml >> watch-my-handle.log 2>&1
```

A sensible starting cadence is:

- Domains: every 6-24 hours. RDAP data does not need minute-level polling.
- GitHub: every 1-6 hours. Set `GITHUB_TOKEN` for a higher API limit; the checker also works unauthenticated.
- X, Instagram, TikTok: every 12-24 hours with jitter. Faster scraping is brittle and more likely to trigger blocks.

If you run in ephemeral CI, persist `.watch-my-handle/state.json` between runs. Keep permissions read-only by default, pin third-party Actions, and store config secrets in the CI secret store.

## Platform reality, without hand-waving

### Domains

RDAP is free and standardized, but coverage and semantics vary by registry. “No RDAP record + no DNS” is reported as available with an explicit instruction to confirm at a registrar. Watch My Handle does not buy or reserve names.

### GitHub

The public REST endpoint is reliable for whether a profile exists. Unauthenticated requests have a lower rate limit. A token is optional and should be scoped as narrowly as possible; no token is ever stored by the watch-my-handle CLI.

### X

X's official API access and pricing can change. V1 does not require it. The adapter checks the public profile URL, which is cheap but can be challenged and cannot prove dormancy. A future official-API adapter belongs behind the same checker interface.

### Instagram and TikTok

Neither offers a dependable, free, general-purpose username availability API for this use case. Public pages frequently challenge automation. These adapters are best-effort discovery signals. They do not bypass login, CAPTCHA, or platform controls.

## Exit behavior

- `0`: checks completed (individual targets may still be `unknown`)
- `2`: at least one checker returned `error`

Every run prints structured JSON to stdout, so it composes with `jq`, log pipelines, and CI.

## Development

```bash
pip install -e '.[dev]'
ruff check .
pytest -q
```

See [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) for adapter and transport boundaries.

## Hosted site

The static Next.js site is hosted on GitHub Pages at <https://deepanshupal.github.io/watch-my-handle/> with the permanent `/watch-my-handle` base path. The repository now includes a server-side checker Worker (`worker/`) that removes the browser-CORS wall without weakening Watch My Handle's evidence rules. Production proxy and waitlist rollout are paused; the currently deployed site still uses direct browser checks.

See [`docs/STATUS.md`](docs/STATUS.md) for the exact implementation state, completed smoke checks, platform-by-platform findings, known limitations, and release plan.

## Roadmap

- Deploy the tested free-tier Worker and connect the GitHub Pages UI.
- Configure and verify the free Formspree waitlist.
- Run the 18-platform taken/available website-vs-CLI release audit in `audit/`.
- Add opt-in hosted watchlists and alert scheduling after the open-source flow is proven.
- Add more authenticated adapters only where they improve evidence quality without creating false confidence.

## License

MIT. See [`LICENSE`](LICENSE).
