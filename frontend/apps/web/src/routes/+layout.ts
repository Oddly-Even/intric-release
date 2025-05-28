import '$lib/i18n';
import { browser } from '$app/environment';
import { locale, waitLocale } from 'svelte-i18n';
import { env } from "$env/dynamic/public";


export const load = async () => {
  if (browser) {
    locale.set(env.PUBLIC_DEFAULT_LOCALE);
  }
  await waitLocale();
};
