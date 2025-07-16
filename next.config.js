/** @type {import('next').NextConfig} */
const nextConfig = {
  rewrites: async () => {
    return [
      {
        source: '/api/:path*',
        destination:
          process.env.NODE_ENV === 'development'
            ? 'http://127.0.0.1:5328/api/:path*'
            : `${process.env.NEXT_PUBLIC_API_URL}/api/:path*`,
      },
    ]
  },
  // Skip TypeScript type checking during build
  typescript: {
    ignoreBuildErrors: true,
  }
}

module.exports = nextConfig
