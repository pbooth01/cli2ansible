/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  async rewrites() {
    return {
      fallback: [
        {
          source: '/api/:path*',
          destination: 'http://app:8000/:path*',
        },
      ],
    }
  },
}

module.exports = nextConfig
