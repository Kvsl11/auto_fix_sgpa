/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  darkMode: "class",
  theme: {
    extend: {
      fontFamily: { sans: ["Inter", "system-ui", "sans-serif"], mono: ["JetBrains Mono", "ui-monospace", "monospace"] },
      colors: {
        brand: {
          50: "#eefaf8", 100: "#d4f1ec", 200: "#ade3da", 300: "#7bcdc1", 400: "#56b3a7",
          500: "#43948c", 600: "#357771", 700: "#2e6862", 800: "#26504c", 900: "#1f413e",
        },
      },
      keyframes: { "fade-in": { from: { opacity: 0, transform: "translateY(4px)" }, to: { opacity: 1, transform: "none" } } },
      animation: { "fade-in": "fade-in .25s ease-out" },
    },
  },
  plugins: [],
};
