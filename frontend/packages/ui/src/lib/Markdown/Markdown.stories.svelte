<script lang="ts" module>
  import { defineMeta } from "@storybook/addon-svelte-csf";
  import Markdown from "./Markdown.svelte";

  // More on how to set up stories at: https://storybook.js.org/docs/writing-stories
  const { Story } = defineMeta({
    title: "UI/Markdown",
    tags: ["autodocs"],
    argTypes: {
      source: {
        control: { type: "text" }
      }
    },
    args: {
      source: "# Hello\n\n**This is a test**"
    }
  });
</script>

<Story name="Default">
  {#snippet template(args)}
    <Markdown {...args} />
  {/snippet}
</Story>
