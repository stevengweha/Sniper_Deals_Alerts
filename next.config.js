/** @type {import('next').NextConfig} */
const nextConfig = {
  typescript: {
    // Cela ignorera les erreurs de type lors du build Vercel
    ignoreBuildErrors: true,
  },
  eslint: {
    // Cela ignorera les erreurs de linting lors du build Vercel
    ignoreDuringBuilds: true,
  },
}

module.exports = nextConfig