/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
    "node_modules/flowbite-react/**/*.{js,jsx,ts,tsx}",
  ],
  darkMode: "class",
  theme: {
    extend: {
      fontFamily: {
        display: ["'Cabinet Grotesk'", "'DM Sans'", "sans-serif"],
        body: ["'Instrument Sans'", "'DM Sans'", "sans-serif"],
        mono: ["'JetBrains Mono'", "monospace"],
      },
      colors: {
        forest: { 50:"#f0fdf4", 100:"#dcfce7", 200:"#bbf7d0", 300:"#86efac", 400:"#4ade80", 500:"#22c55e", 600:"#16a34a", 700:"#15803d", 800:"#166534", 900:"#14532d", 950:"#052e16" },
        obsidian: { 50:"#f8fafc", 100:"#f1f5f9", 200:"#e2e8f0", 300:"#cbd5e1", 400:"#94a3b8", 500:"#64748b", 600:"#475569", 700:"#334155", 800:"#1e293b", 900:"#0f172a", 950:"#020617" },
      },
      animation: {
        "fade-up": "fadeUp 0.5s ease-out forwards",
        "pulse-slow": "pulse 3s ease-in-out infinite",
        "scan": "scan 2s linear infinite",
        "float": "float 6s ease-in-out infinite",
      },
      keyframes: {
        fadeUp: { "0%": { opacity: "0", transform: "translateY(16px)" }, "100%": { opacity: "1", transform: "translateY(0)" } },
        scan: { "0%": { transform: "translateY(-100%)" }, "100%": { transform: "translateY(400%)" } },
        float: { "0%,100%": { transform: "translateY(0)" }, "50%": { transform: "translateY(-8px)" } },
      },
    },
  },
  plugins: [require("flowbite/plugin")],
};
