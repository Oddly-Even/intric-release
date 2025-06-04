<script lang="ts" module>
  import { defineMeta } from "@storybook/addon-svelte-csf";
  import * as Input from "./index";

  // More on how to set up stories at: https://storybook.js.org/docs/writing-stories
  const { Story } = defineMeta({
    title: "UI/Input/RadioSwitch",
    tags: ["autodocs"],
    argTypes: {
      value: {
        control: { type: "boolean" }
      },
      disabled: {
        control: { type: "boolean" }
      }
    },
    args: {
      value: false,
      disabled: false
    }
  });
</script>

<Story name="Default">
  {#snippet template(args)}
    <div class="grid grid-cols-2 gap-2">
      <Input.RadioSwitch {...args}>Label</Input.RadioSwitch>
    </div>
  {/snippet}
</Story>
