<script lang="ts" module>
  import { defineMeta } from "@storybook/addon-svelte-csf";
  import ProgressBar from "./ProgressBar.svelte";

  // More on how to set up stories at: https://storybook.js.org/docs/writing-stories
  const { Story } = defineMeta({
    title: "UI/ProgressBar",
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
</script>

<Story name="Default">
  {#snippet template(args)}
    <ProgressBar {...args} />
  {/snippet}
</Story>
