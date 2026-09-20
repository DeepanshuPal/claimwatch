import test from "node:test";
import assert from "node:assert/strict";
import worker, { checkPlatform } from "../src/index.js";

const response = status => async () => new Response("{}", { status });

test("strong 404 is available", async () => assert.equal((await checkPlatform("github", "unused", response(404))).status, "available"));
test("strong 200 is taken", async () => assert.equal((await checkPlatform("npm", "react", response(200))).status, "taken"));
test("weak 404 stays unknown", async () => assert.equal((await checkPlatform("linkedin", "unused", response(404))).status, "unknown"));
test("timeout stays unknown", async () => assert.equal((await checkPlatform("github", "x", async () => { throw Object.assign(new Error(), { name: "TimeoutError" }); })).status, "unknown"));
test("mastodon without instance stays unknown", async () => assert.equal((await checkPlatform("mastodon", "alice", response(200))).status, "unknown"));
test("health exposes all 18 adapters", async () => {
  const r = await worker.fetch(new Request("https://worker.test/health", { headers: { Origin: "https://deepanshupal.github.io" } }));
  const body = await r.json();
  assert.equal(body.platforms, 18);
  assert.equal(r.headers.get("Access-Control-Allow-Origin"), "https://deepanshupal.github.io");
});
