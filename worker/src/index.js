const VERSION = "1.0.0";
const TIMEOUT_MS = 8000;

const adapters = {
  github: { url: n => `https://api.github.com/users/${q(n)}`, mode: "strong", accept: "application/vnd.github+json" },
  youtube: { url: n => `https://www.youtube.com/@${q(n)}`, mode: "trusted404" },
  linkedin: { url: n => `https://www.linkedin.com/in/${q(n)}`, mode: "weak" },
  reddit: { url: n => `https://www.reddit.com/user/${q(n)}/about.json`, mode: "trusted404", accept: "application/json" },
  threads: { url: n => `https://www.threads.net/@${q(n)}`, mode: "weak" },
  twitch: { url: n => `https://www.twitch.tv/${q(n)}`, mode: "trusted404" },
  pinterest: { url: n => `https://www.pinterest.com/${q(n)}/`, mode: "trusted404" },
  snapchat: { url: n => `https://www.snapchat.com/add/${q(n)}`, mode: "weak" },
  bluesky: { url: n => `https://public.api.bsky.app/xrpc/com.atproto.identity.resolveHandle?handle=${q(`${n}.bsky.social`)}`, mode: "bluesky", accept: "application/json" },
  mastodon: { special: "mastodon" },
  telegram: { url: n => `https://t.me/${q(n)}`, mode: "weak" },
  producthunt: { url: n => `https://www.producthunt.com/@${q(n)}`, mode: "trusted404" },
  substack: { url: n => `https://${q(n)}.substack.com/`, mode: "trusted404" },
  medium: { url: n => `https://medium.com/@${q(n)}`, mode: "trusted404" },
  devto: { url: n => `https://dev.to/${q(n)}`, mode: "trusted404" },
  npm: { url: n => `https://registry.npmjs.org/${q(n)}`, mode: "strong", accept: "application/json" },
  pypi: { url: n => `https://pypi.org/pypi/${q(n)}/json`, mode: "strong", accept: "application/json" },
  dockerhub: { url: n => `https://hub.docker.com/v2/users/${q(n)}/`, mode: "strong", accept: "application/json" }
};

const allowedOrigins = new Set([
  "https://deepanshupal.github.io",
  "http://localhost:3000"
]);

function q(value) { return encodeURIComponent(value); }
function cleanName(value) { return String(value || "").trim().toLowerCase().replace(/^@/, "").replace(/[^a-z0-9_.@-]/g, "").slice(0, 128); }
function cors(origin) {
  const allowed = allowedOrigins.has(origin) ? origin : "https://deepanshupal.github.io";
  return { "Access-Control-Allow-Origin": allowed, "Access-Control-Allow-Methods": "GET, OPTIONS", "Access-Control-Allow-Headers": "Content-Type", "Access-Control-Max-Age": "86400", Vary: "Origin" };
}
function result(platform, status, detail, url) { return { platform, label: platform, status, detail, url, checkedAt: new Date().toISOString() }; }

export async function checkPlatform(platform, rawName, fetcher = fetch) {
  const name = cleanName(rawName);
  const adapter = adapters[platform];
  if (!adapter || !name) return result(platform, "unknown", !adapter ? "Unsupported platform." : "Enter a valid name.");
  if (adapter.special === "mastodon") {
    if (!name.includes("@")) return result(platform, "unknown", "Mastodon needs handle@instance so the correct server can be queried.");
    const [handle, instance] = name.split("@");
    if (!handle || !instance || !/^[a-z0-9.-]+$/.test(instance)) return result(platform, "unknown", "Use a valid handle@instance value.");
    return probe(platform, `https://${instance}/api/v1/accounts/lookup?acct=${q(handle)}`, "strong", "application/json", fetcher);
  }
  return probe(platform, adapter.url(name), adapter.mode, adapter.accept, fetcher);
}

async function probe(platform, url, mode, accept = "text/html,application/json", fetcher = fetch) {
  try {
    const response = await fetcher(url, {
      headers: { Accept: accept, "User-Agent": "Watch-My-Handle/1.0 (+https://github.com/DeepanshuPal/watch-my-handle)" },
      redirect: "follow",
      signal: AbortSignal.timeout(TIMEOUT_MS)
    });
    if (response.status === 404) {
      if (mode === "strong" || mode === "trusted404") return result(platform, "available", "Public source returned 404. Confirm in-platform before claiming.", url);
      return result(platform, "unknown", "The source returned 404, but this platform does not expose a dependable availability signal.", url);
    }
    if (mode === "bluesky" && response.status === 400) return result(platform, "available", "Bluesky could not resolve this handle. Confirm before claiming.", url);
    if (response.ok) return result(platform, "taken", mode === "strong" || mode === "bluesky" ? "Public API found a matching record." : "Public profile endpoint responded. Ownership is not verified.", url);
    return result(platform, "unknown", `Public source returned HTTP ${response.status}; it may be throttling or challenging requests.`, url);
  } catch (error) {
    const timedOut = error?.name === "TimeoutError" || error?.name === "AbortError";
    return result(platform, "unknown", timedOut ? "Public source timed out. No availability claim was made." : "Public source blocked or failed. No availability claim was made.", url);
  }
}

export default {
  async fetch(request) {
    const origin = request.headers.get("Origin") || "";
    const headers = cors(origin);
    if (request.method === "OPTIONS") return new Response(null, { status: 204, headers });
    const url = new URL(request.url);
    if (url.pathname === "/health") return Response.json({ ok: true, service: "watch-my-handle-checker", version: VERSION, platforms: Object.keys(adapters).length }, { headers });
    if (request.method !== "GET" || url.pathname !== "/check") return Response.json({ error: "Not found" }, { status: 404, headers });
    const platform = url.searchParams.get("platform") || "";
    const name = url.searchParams.get("name") || "";
    if (!adapters[platform]) return Response.json({ error: "Unsupported platform", platforms: Object.keys(adapters) }, { status: 400, headers });
    if (!cleanName(name)) return Response.json({ error: "A valid name is required" }, { status: 400, headers });
    return Response.json(await checkPlatform(platform, name), { headers: { ...headers, "Cache-Control": "public, max-age=60" } });
  }
};
