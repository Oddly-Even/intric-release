<script module>
  import { defineMeta } from "@storybook/addon-svelte-csf";
  import Button from "./Button.svelte";
  import { fn } from "storybook/test";

  // More on how to set up stories at: https://storybook.js.org/docs/writing-stories
  const { Story } = defineMeta({
    title: "UI/Button",
    component: Button,
    tags: ["autodocs"],
    argTypes: {
      variant: {
        control: { type: "select" },
        options: [
          "simple",
          "outlined",
          "primary",
          "primary-outlined",
          "destructive",
          "positive",
          "positive-outlined",
          "on-fill"
        ]
      },
      size: {
        control: { type: "select" },
        options: ["small", "medium", "large"]
      }
    },
    args: {
      onclick: fn()
    }
  });
</script>

<Story name="Simple" args={{ variant: "simple" }}>
  {#snippet template(args)}
    <Button {...args}>Button</Button>
  {/snippet}
</Story>

<Story name="Outlined" args={{ variant: "outlined" }}>
  {#snippet template(args)}
    <Button {...args}>Button</Button>
  {/snippet}
</Story>

<Story name="Primary" args={{ variant: "primary" }}>
  {#snippet template(args)}
    <Button {...args}>Button</Button>
  {/snippet}
</Story>

<Story name="Primary Outlined" args={{ variant: "primary-outlined" }}>
  {#snippet template(args)}
    <Button {...args}>Button</Button>
  {/snippet}
</Story>

<Story name="Destructive" args={{ variant: "destructive" }}>
  {#snippet template(args)}
    <Button {...args}>Button</Button>
  {/snippet}
</Story>

<Story name="Positive" args={{ variant: "positive" }}>
  {#snippet template(args)}
    <Button {...args}>Button</Button>
  {/snippet}
</Story>

<Story name="Positive Outlined" args={{ variant: "positive-outlined" }}>
  {#snippet template(args)}
    <Button {...args}>Button</Button>
  {/snippet}
</Story>

<Story name="On Fill" args={{ variant: "on-fill" }}>
  {#snippet template(args)}
    <Button {...args}>Button</Button>
  {/snippet}
</Story>
