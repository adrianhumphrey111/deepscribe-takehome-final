/** @type {import('next').NextConfig} */
const nextConfig = {
  // For separate services - frontend will call backend API directly
  // No rewrites needed when using separate App Runner services
  
  // Only use static export for production deployment
  ...(process.env.NODE_ENV === 'production' && {
    output: 'export',
    trailingSlash: true,
    images: {
      unoptimized: true
    },
  }),
  
  // For development, allow rewrites to local Flask server
  ...(process.env.NODE_ENV === 'development' && {
    rewrites: async () => {
      return [
        {
          source: '/api/:path*',
          destination: 'http://127.0.0.1:5328/api/:path*',
        },
      ]
    },
  }),
  
  // Skip TypeScript type checking during build
  typescript: {
    ignoreBuildErrors: true,
  }
}

module.exports = nextConfig
