/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "../../templates/**/*.html", // all Django templates
    "../../**/templates/**/*.html", // templates inside apps
  ],
  theme: {
    extend: {
      colors: {
        primary: "#261f2c", // your custom color
      },
    },
  },
  plugins: [],
};
