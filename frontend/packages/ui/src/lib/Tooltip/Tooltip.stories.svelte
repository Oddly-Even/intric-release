<script lang="ts" module>
  import { defineMeta } from "@storybook/addon-svelte-csf";
  import { Tooltip } from "./index";

  // More on how to set up stories at: https://storybook.js.org/docs/writing-stories
  const { Story } = defineMeta({
    title: "UI/Tooltip",
    tags: ["autodocs"],
    argTypes: {
      text: {
        control: { type: "text" }
      },
      placement: {
        control: { type: "select" },
        options: ["left", "bottom", "top", "right"]
      },
      renderInline: {
        control: { type: "boolean" }
      }
    },
    args: {
      text: "New apps and assistants will default to this model",
      placement: "top",
      renderInline: true
    }
  });
</script>

<Story name="Default">
  {#snippet template(args)}
    <Tooltip text={args.text}>
      <div
        class="border-positive-stronger text-positive-stronger flex h-24 items-center justify-center rounded-md border text-center"
      >
        <span>Hover this text to see the tooltip</span>
      </div>
    </Tooltip>
  {/snippet}
</Story>
