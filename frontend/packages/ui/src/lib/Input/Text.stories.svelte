<script lang="ts" module>
  import { defineMeta } from "@storybook/addon-svelte-csf";
  import * as Input from "./index";

  // More on how to set up stories at: https://storybook.js.org/docs/writing-stories
  const { Story } = defineMeta({
    title: "UI/Input/Text",
    tags: ["autodocs"],
    argTypes: {
      inputClass: {
        control: { type: "text" }
      },
      labelClass: {
        control: { type: "text" }
      },
      label: {
        control: { type: "text" }
      },
      description: {
        control: { type: "text" }
      },
      value: {
        control: { type: "text" }
      },
      required: {
        control: { type: "boolean" }
      },
      hiddenLabel: {
        control: { type: "boolean" }
      }
    },
    args: {
      inputClass: "",
      labelClass: "",
      label: "Label",
      description: "Description",
      value: "Input message",
      required: false,
      hiddenLabel: false
    }
  });
</script>

<Story name="Default">
  {#snippet template(args)}
    <div class="grid grid-cols-2 gap-2">
      <Input.Text {...args} />
    </div>
  {/snippet}
</Story>
