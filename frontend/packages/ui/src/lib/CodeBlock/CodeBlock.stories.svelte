<script module>
  import { defineMeta } from "@storybook/addon-svelte-csf";
  import CodeBlock from "./CodeBlock.svelte";

  // More on how to set up stories at: https://storybook.js.org/docs/writing-stories
  const { Story } = defineMeta({
    title: "UI/CodeBlock",
    component: CodeBlock,
    tags: ["autodocs"],
    argTypes: {
      source: {
        control: { type: "text" }
      }
    },
    args: {
      source: "console.log('Hello, world!');"
    }
  });
</script>

<Story name="Javascript">
  {#snippet template(args)}
    <CodeBlock source={args.source} />
  {/snippet}
</Story>
