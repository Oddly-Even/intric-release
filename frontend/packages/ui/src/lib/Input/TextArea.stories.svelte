<script lang="ts" module>
  import { defineMeta } from "@storybook/addon-svelte-csf";
  import * as Input from "./index";

  // More on how to set up stories at: https://storybook.js.org/docs/writing-stories
  const { Story } = defineMeta({
    title: "UI/Input/TextArea",
    tags: ["autodocs"],
    argTypes: {
      label: {
        control: { type: "text" }
      },
      description: {
        control: { type: "text" }
      },
      value: {
        control: { type: "text" }
      },
      rows: {
        control: { type: "number" }
      },
      required: {
        control: { type: "boolean" }
      }
    },
    args: {
      label: "Label",
      description: "Description",
      value: "Text area message",
      rows: 4,
      required: false
    }
  });
</script>

<Story name="Default">
  {#snippet template(args)}
    <div class="grid grid-cols-2 gap-2">
      <Input.TextArea {...args} />
    </div>
  {/snippet}
</Story>
