import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        // Premium dark-navy enterprise palette
        ink: {
          950: "#070b14",
          900: "#0b1120",
          800: "#111a2e",
          700: "#1a2740",
          600: "#24365a",
        },
        brand: {
          300: "#93b8f4",
          400: "#6d9beb",
          500: "#4a7fe0",
          600: "#3866c4",
        },
        mist: {
          100: "#eef2f8",
          200: "#d9e1ee",
          300: "#b7c4d9",
          400: "#8d9cb8",
          500: "#65758f",
        },
      },
      maxWidth: {
        content: "72rem",
      },
    },
  },
  plugins: [],
};
export default config;
