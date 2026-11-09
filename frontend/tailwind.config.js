/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        ink: {
          DEFAULT: "#0A0F0D",   // base app background — warm near-black, not pure neutral
          panel: "#111815",     // card/panel surface
          raised: "#161F1B",    // hover/raised surface
          border: "#212B26",    // hairline borders
        },
        signal: {
          DEFAULT: "#D9A441",   // brand accent — radar/warning-light gold, not SaaS blue or clay
          soft: "#E8C578",
        },
        verdict: {
          safe: "#33C17E",
          safeBg: "#12251C",
          suspicious: "#E8A93B",
          suspiciousBg: "#2A2013",
          malicious: "#E15559",
          maliciousBg: "#2A1516",
        },
        ash: {
          50: "#ECEFED",
          200: "#B8C2BD",
          400: "#7C8985",
          600: "#4F5955",
        },
      },
      fontFamily: {
        display: ["'Space Grotesk'", "sans-serif"],
        body: ["'IBM Plex Sans'", "sans-serif"],
        mono: ["'IBM Plex Mono'", "monospace"],
      },
      borderRadius: {
        sm: "4px",
        md: "6px",
        lg: "10px",
      },
      boxShadow: {
        glow: "0 0 0 1px rgba(217,164,65,0.15), 0 8px 24px -8px rgba(217,164,65,0.25)",
      },
      keyframes: {
        scanline: {
          "0%": { transform: "translateY(-100%)" },
          "100%": { transform: "translateY(100%)" },
        },
        pulseDot: {
          "0%, 100%": { opacity: 1 },
          "50%": { opacity: 0.35 },
        },
      },
      animation: {
        scanline: "scanline 2.2s linear infinite",
        pulseDot: "pulseDot 1.6s ease-in-out infinite",
      },
    },
  },
  plugins: [],
};
