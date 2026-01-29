/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: "class", // ✅ Enables manual theme toggling via 'dark' class on <html>
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // 🛡️ Forensic Semantic Palette
        forensic: {
          indigo: "#6366f1", // Primary engine color
          rose: "#f43f5e",   // Critical threat / Alert color
          emerald: "#10b981", // Safe traffic / Success color
          amber: "#f59e0b",   // Warning / Standby color
          slate: {
            950: "#020617",   // Ultra-dark NOC background
          }
        }
      },
      boxShadow: {
        // 🔹 Dashboard Shadow Architecture
        'glow-indigo': '0 20px 50px rgba(79, 70, 229, 0.1)',
        'glow-dark': '0 25px 60px rgba(0, 0, 0, 0.7)',
        'inner-dark': 'inset 0 2px 4px 0 rgba(0, 0, 0, 0.5)',
      },
      animation: {
        // 🚀 Custom Entrance Interactions
        'slow-fade': 'fadeIn 1s ease-in-out',
        'staggered-rise': 'slideUp 0.7s ease-out forwards',
        'pulse-glow': 'pulseGlow 2s infinite',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { transform: 'translateY(20px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        pulseGlow: {
          '0%, 100%': { opacity: '1', transform: 'scale(1)' },
          '50%': { opacity: '0.7', transform: 'scale(1.05)' },
        }
      }
    },
  },
  plugins: [
    require("tailwindcss-animate"), // Enables the 'animate-in' classes you're using
  ],
};