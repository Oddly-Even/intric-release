<script module>
  import { defineMeta } from "@storybook/addon-svelte-csf";
  import * as Dialog from "./index";

  // More on how to set up stories at: https://storybook.js.org/docs/writing-stories
  const { Story } = defineMeta({
    title: "UI/Dialog",

    tags: ["autodocs"],
    argTypes: {
      triggerOpen: {
        control: { type: "text" }
      },
      source: {
        control: { type: "text" }
      }
    },
    args: {
      triggerOpen: "Open"
    }
  });
</script>

<Story name="Default">
  {#snippet template(args)}
    <Dialog.Root>
      <Dialog.Trigger>{args.triggerOpen}</Dialog.Trigger>
      <Dialog.Content>
        <Dialog.Title>Dialog Title</Dialog.Title>
        <Dialog.Description>Dialog Description</Dialog.Description>
        <Dialog.Section>Test section</Dialog.Section>
      </Dialog.Content>
    </Dialog.Root>
  {/snippet}
</Story>
