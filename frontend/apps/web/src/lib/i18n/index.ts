import { browser } from '$app/environment'
import { init, register } from 'svelte-i18n'

/**
 * Register available locales and initialize i18n
 */

const defaultLocale = 'en'

register('en', () => import('./locales/en.json'))
register('sv', () => import('./locales/sv.json'))

init({
  fallbackLocale: defaultLocale,
  initialLocale: browser ? window.navigator.language : defaultLocale,
})
