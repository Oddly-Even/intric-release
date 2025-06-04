<script lang="ts" module>
  import { defineMeta } from "@storybook/addon-svelte-csf";
  import * as Input from "./index";

  // More on how to set up stories at: https://storybook.js.org/docs/writing-stories
  const { Story } = defineMeta({
    title: "UI/Input/Number",
    tags: ["autodocs"],
    argTypes: {
      value: {
        control: { type: "number" }
      },
      step: {
        control: { type: "number" }
      },
      max: {
        control: { type: "number" }
      },
      min: {
        control: { type: "number" }
      },
      hiddenLabel: {
        control: { type: "boolean" }
      }
    },
    args: {
      value: 0,
      step: 1,
      max: 100,
      min: 0,
      hiddenLabel: false
    }
  });
</script>

<Story name="Default">
  {#snippet template(args)}
    <Input.Number {...args}>Label</Input.Number>
  {/snippet}
</Story>
