import { init, register } from 'svelte-i18n'

/**
 * Register available locales and initialize i18n
 */

register('en', () => import('./locales/en.json'))
register('sv', () => import('./locales/sv.json'))

const fallbackLocale = 'en'

// Initialize i18n with default locale
// The actual locale will be set in the layout load function
init({
  fallbackLocale,
  initialLocale: fallbackLocale,
})
