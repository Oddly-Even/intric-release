<script lang="ts" module>
  import { defineMeta } from "@storybook/addon-svelte-csf";
  import * as Input from "./index";

  // More on how to set up stories at: https://storybook.js.org/docs/writing-stories
  const { Story } = defineMeta({
    title: "UI/Input/Files",
    tags: ["autodocs"]
  });
</script>

<Story name="Default">
  {#snippet template(args)}
    <Input.Files {...args} />
  {/snippet}
</Story>
