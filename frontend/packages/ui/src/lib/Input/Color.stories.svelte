<script module>
  import { defineMeta } from "@storybook/addon-svelte-csf";
  import * as Input from "./index";

  // More on how to set up stories at: https://storybook.js.org/docs/writing-stories
  const { Story } = defineMeta({
    title: "UI/Input/Color",

    tags: ["autodocs"],
    argTypes: {
      value: {
        control: { type: "text" }
      },
      label: {
        control: { type: "text" }
      },
      description: {
        control: { type: "text" }
      },
      required: {
        control: { type: "boolean" }
      }
    },
    args: {
      value: "#000000",
      label: "Color",
      description: "This is a description",
      required: true
    }
  });
</script>

<Story name="Default">
  {#snippet template(args)}
    <Input.Color {...args} />
  {/snippet}
</Story>
