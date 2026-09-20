import type { MetadataRoute } from "next";

export const dynamic = "force-static";

export default function sitemap(): MetadataRoute.Sitemap {
  const base = "https://deepanshupal.github.io/watch-my-handle";
  return ["", "/check", "/pricing", "/docs"].map((path) => ({
    url: base + path,
    lastModified: new Date("2026-09-20"),
    changeFrequency: path === "" ? "weekly" : "monthly",
    priority: path === "" ? 1 : 0.7,
  }));
}
