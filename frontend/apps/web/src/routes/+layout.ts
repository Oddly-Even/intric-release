import '$lib/i18n';
import { browser } from '$app/environment';
import { locale, waitLocale } from 'svelte-i18n';
import { PUBLIC_DEFAULT_LOCALE } from "$env/static/public";

export const load = async () => {
  if (browser) {
    locale.set(PUBLIC_DEFAULT_LOCALE);
  }
  await waitLocale();
};
