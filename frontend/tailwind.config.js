/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        bg:      'var(--c-bg)',
        surface: 'var(--c-surface)',
        green:   'rgb(var(--c-green) / <alpha-value>)',
        cyan:    'rgb(var(--c-cyan) / <alpha-value>)',
        orange:  'rgb(var(--c-orange) / <alpha-value>)',
        red:     'rgb(var(--c-red) / <alpha-value>)',
        muted:   'rgb(var(--c-muted) / <alpha-value>)',
        sub:     'rgb(var(--c-sub) / <alpha-value>)',
        primary: 'rgb(var(--c-primary) / <alpha-value>)',
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
        mono: ['"JetBrains Mono"', 'monospace'],
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4,0,0.6,1) infinite',
        'fade-in':    'fadeIn 0.4s ease forwards',
      },
      keyframes: {
        fadeIn: {
          '0%':   { opacity: '0', transform: 'translateY(8px)' },
          '100%': { opacity: '1', transform: 'none' },
        },
      },
    },
  },
  plugins: [],
}
