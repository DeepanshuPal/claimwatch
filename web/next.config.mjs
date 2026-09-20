/** @type {import('next').NextConfig} */
const projectBasePath = process.env.GITHUB_PAGES === "true" ? "/watch-my-handle" : "";

const nextConfig = {
  output: "export",
  poweredByHeader: false,
  trailingSlash: true,
  basePath: projectBasePath,
  assetPrefix: projectBasePath || undefined,
};

export default nextConfig;
