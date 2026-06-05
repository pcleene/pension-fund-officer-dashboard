/** @type {import('tailwindcss').Config} */
export default {
  content: ['./src/**/*.{html,js,svelte,ts}'],
  theme: {
    extend: {
      colors: {
        PensionFund: {
          blue: '#003A70',
          gold: '#C8A965',
          navy: '#002855',
          lightblue: '#E8F4F8',
          gray: '#F5F5F5'
        }
      }
    }
  },
  plugins: []
};
