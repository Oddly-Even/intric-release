import { init, register } from 'svelte-i18n'
import { PUBLIC_DEFAULT_LOCALE } from '$env/static/public'
/**
 * Register available locales and initialize i18n
 */

register('en', () => import('./locales/en.json'))
register('sv', () => import('./locales/sv.json'))

// Initialize i18n without a default locale
// The actual locale will be set in the layout load function
init({
  fallbackLocale: 'en',
  initialLocale: PUBLIC_DEFAULT_LOCALE || 'en'
})
