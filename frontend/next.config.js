/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  async rewrites() {
    return {
      fallback: [
        {
          source: '/api/v1/:path*',
          destination: 'http://app:8000/api/v1/:path*',
        },
      ],
    }
  },
}

module.exports = nextConfig
