<script lang="ts" module>
  import { defineMeta } from "@storybook/addon-svelte-csf";
  import * as Label from "./index";

  // More on how to set up stories at: https://storybook.js.org/docs/writing-stories
  const { Story } = defineMeta({
    title: "UI/Label/List",
    tags: ["autodocs"],
    argTypes: {
      content: {
        control: { type: "object" }
      },
      monospaced: {
        control: { type: "boolean" }
      }
    },
    args: {
      content: [
        { label: "Label 1", color: "primary" },
        { label: "Label 2", color: "secondary" }
      ],
      monospaced: false
    }
  });
</script>

<Story name="Default">
  {#snippet template(args)}
    <div class="grid grid-cols-2 gap-2">
      <Label.List {...args} />
    </div>
  {/snippet}
</Story>
