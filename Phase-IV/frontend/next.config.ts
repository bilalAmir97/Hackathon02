import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  },
  images: {
    unoptimized: true, // Disable image optimization to simplify deployment
  },
  // Ensure proper handling of asset prefixes
  assetPrefix: '',
  basePath: '',
  trailingSlash: false,
  reactStrictMode: true,
  // Enable standalone output for Docker deployment
  output: 'standalone',
};

export default nextConfig;
