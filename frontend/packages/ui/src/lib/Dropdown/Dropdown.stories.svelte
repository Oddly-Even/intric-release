<script module>
  import { defineMeta } from "@storybook/addon-svelte-csf";
  import * as Dropdown from "./index";
  import { Button } from "../Button";
  import { IconChevronDown } from "@intric/icons/chevron-down";
  import { IconCancel } from "@intric/icons/cancel";

  // More on how to set up stories at: https://storybook.js.org/docs/writing-stories
  const { Story } = defineMeta({
    title: "UI/Dropdown",
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
    <div class="flex w-full gap-[1px]">
      <div
        class="border-positive-stronger bg-positive-default text-on-fill hover:bg-positive-stronger flex w-full cursor-default items-center justify-center rounded-l-lg border"
      >
        Enabled
      </div>
      <Dropdown.Root gutter={2} arrowSize={0} placement="bottom-end">
        <Dropdown.Trigger asFragment let:trigger>
          <Button
            padding="icon"
            variant="positive"
            is={trigger}
            class="!rounded-l-none !rounded-r-lg"><IconChevronDown></IconChevronDown></Button
          >
        </Dropdown.Trigger>
        <Dropdown.Menu let:item>
          <Button is={item} onclick={() => {}} variant="destructive">
            <IconCancel></IconCancel>
            Disable integration</Button
          >
        </Dropdown.Menu>
      </Dropdown.Root>
    </div>
  {/snippet}
</Story>
