/** @type {import('next').NextConfig} */
const nextConfig = {
  // Enable TypeScript checking
  typescript: {
    ignoreBuildErrors: false,
  },
  eslint: {
    ignoreDuringBuilds: false,
  },
  // Disable minification for debugging
  swcMinify: false,
  compiler: {
    removeConsole: false,
  },
  // Add webpack config to disable minification
  webpack: (config, { dev, isServer }) => {
    if (!dev) {
      config.optimization.minimize = false;
    }
    return config;
  },
}

module.exports = nextConfig
