<script module>
  import { defineMeta } from "@storybook/addon-svelte-csf";
  import * as Input from "./index";

  // More on how to set up stories at: https://storybook.js.org/docs/writing-stories
  const { Story } = defineMeta({
    title: "UI/Input/Slider",

    tags: ["autodocs"],
    argTypes: {
      value: {
        control: { type: "number" }
      },
      max: {
        control: { disable: true }
      },
      min: {
        control: { disable: true }
      },
      step: {
        control: { disable: true }
      }
    },
    args: {
      value: 0.5,
      max: 2,
      min: 0,
      step: 0.01
    }
  });
</script>

<Story name="Default">
  {#snippet template(args)}
    <Input.Slider {...args} />
  {/snippet}
</Story>
