import type { Preview, SvelteRenderer } from "@storybook/sveltekit";
import { withThemeByDataAttribute } from "@storybook/addon-themes";
import { init, addMessages, locale } from 'svelte-i18n';
import "../src/app.css";

// Initialize svelte-i18n with mock translations for UI components
const mockTranslations = {
  'ui.dialog.close': 'Close',
  'ui.dialog.cancel': 'Cancel',
  'ui.dialog.confirm': 'Confirm',
  'ui.select.placeholder': 'Select...',
  'ui.select.emptyState': 'No available {resourceName}s',
  'ui.table.filter': 'Filter',
  'ui.table.list': 'List',
  'ui.table.cards': 'Cards',
  'ui.table.filterPlaceholder': 'Filter {resourceName}s...',
  'ui.input.required': '(required)',
  'ui.input.files.dragAndDrop': 'Drag and Drop files or folders here',
  'ui.input.files.or': 'or',
  'ui.input.files.clickToBrowse': 'Click to browse',
  'ui.input.files.dropHere': 'Drop your files here',
  'ui.input.files.clickToSeeTypes': 'Click',
  'ui.input.files.here': 'here',
  'ui.input.files.toSeeTypes': 'to see a list of supported filetypes',
  'ui.input.radioSwitch.true': 'On',
  'ui.input.radioSwitch.false': 'Off'
};

// Add the mock translations and initialize
addMessages('en', mockTranslations);
init({
  fallbackLocale: 'en',
  initialLocale: 'en'
});

// Set the locale
locale.set('en');

const preview: Preview = {
  decorators: [
    withThemeByDataAttribute<SvelteRenderer>({
      themes: {
        light: 'light',
        dark: 'dark',
      },
      defaultTheme: 'light',
      attributeName: 'data-theme',
    }),
  ],
  parameters: {
    controls: {
      matchers: {
        color: /(background|color)$/i,
        date: /Date$/i
      }
    },

    a11y: {
      // 'todo' - show a11y violations in the test UI only
      // 'error' - fail CI on a11y violations
      // 'off' - skip a11y checks entirely
      test: "todo"
    }
  }
};

export default preview;
