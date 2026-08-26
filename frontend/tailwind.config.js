/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        ink: { DEFAULT: '#0d1117', soft: '#161b22', line: '#232b36' },
        accent: { DEFAULT: '#6ea8fe', dim: '#3d6fd4', glow: '#a5c8ff' },
        mint: '#5ddba6',
        amber: '#f0b849',
        rose: '#f0757d',
      },
      fontFamily: {
        sans: ['Inter', 'ui-sans-serif', 'system-ui', 'sans-serif'],
        mono: ['ui-monospace', 'SFMono-Regular', 'Menlo', 'monospace'],
      },
    },
  },
  plugins: [],
}
