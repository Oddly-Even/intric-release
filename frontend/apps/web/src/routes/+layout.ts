import '$lib/i18n';
import { browser } from '$app/environment';
import { locale, waitLocale } from 'svelte-i18n';

export const load = async (event) => {
  const { environment } = event.data;

  if (browser) {
    locale.set(environment.defaultLocale);
  }
  await waitLocale();

  return {
    environment
  };
};
