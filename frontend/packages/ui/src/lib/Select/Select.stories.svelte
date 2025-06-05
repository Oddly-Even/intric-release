<script lang="ts" module>
  import { defineMeta } from "@storybook/addon-svelte-csf";
  import * as Select from "./index";
  import { writable } from "svelte/store";
  // More on how to set up stories at: https://storybook.js.org/docs/writing-stories
  const { Story } = defineMeta({
    title: "UI/Select/Select",
    tags: ["autodocs"],
    argTypes: {
      progress: {
        control: { type: "number" }
      }
    },
    args: {
      progress: 60
    }
  });
  const availableThemes = ["light", "dark", "system"];
  const selected = writable<{ label: string; value: string }>({
    label: "Light",
    value: "light"
  });
</script>

<Story name="Default">
  {#snippet template(args)}
    <Select.Root customStore={selected}>
      <div class="sr-only">
        <Select.Label>Select colour scheme</Select.Label>
      </div>
      <Select.Trigger placeholder="Select theme..."></Select.Trigger>
      <Select.Options>
        {#each availableThemes as theme (theme)}
          <Select.Item value={theme} label={theme}></Select.Item>
        {/each}
      </Select.Options>
    </Select.Root>
  {/snippet}
</Story>
