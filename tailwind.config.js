/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './app/**/*.{ts,tsx,js,jsx}',
    './components/**/*.{ts,tsx,js,jsx}',
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          DEFAULT: '#065f46',
          light: '#e1f5f2',
          dark: '#064e3b',
        },
      },
    },
  },
  plugins: [],
};
