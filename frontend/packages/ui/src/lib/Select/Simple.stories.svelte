<script lang="ts" module>
  import { defineMeta } from "@storybook/addon-svelte-csf";
  import * as Select from "./index";
  import { writable } from "svelte/store";
  // More on how to set up stories at: https://storybook.js.org/docs/writing-stories
  const { Story } = defineMeta({
    title: "UI/Select/Simple",
    tags: ["autodocs"],
    argTypes: {
      options: {
        control: { type: "object" }
      },
      value: {
        control: { type: "text" }
      },
      required: {
        control: { type: "boolean" }
      },
      fitViewport: {
        control: { type: "boolean" }
      },
      resourceName: {
        control: { type: "text" }
      }
    },
    args: {
      options: [
        { label: "Light", value: "light" },
        { label: "Dark", value: "dark" },
        { label: "System", value: "system" }
      ],
      value: "light",
      required: false,
      fitViewport: true,
      resourceName: "option"
    }
  });
</script>

<Story name="Default">
  {#snippet template(args)}
    <Select.Simple {...args}></Select.Simple>
  {/snippet}
</Story>
