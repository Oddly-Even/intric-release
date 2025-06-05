<script lang="ts" module>
  import { defineMeta } from "@storybook/addon-svelte-csf";
  import * as Label from "./index";

  // More on how to set up stories at: https://storybook.js.org/docs/writing-stories
  const { Story } = defineMeta({
    title: "UI/Label/Single",
    tags: ["autodocs"],
    argTypes: {
      item: {
        control: { type: "object" }
      },
      monospaced: {
        control: { type: "boolean" }
      }
    },
    args: {
      item: {
        label: "Label",
        color: ""
      },
      monospaced: false
    }
  });
</script>

<Story name="Default">
  {#snippet template(args)}
    <Label.Single {...args} />
  {/snippet}
</Story>
