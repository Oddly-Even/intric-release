<script lang="ts" module>
  import { defineMeta } from "@storybook/addon-svelte-csf";
  import * as Table from "./index";
  import { readable, toStore } from "svelte/store";
  // More on how to set up stories at: https://storybook.js.org/docs/writing-stories
  const { Story } = defineMeta({
    title: "UI/Table",
    tags: ["autodocs"]
  });

  const data = readable([
    {
      id: 1,
      name: "John Doe",
      email: "john.doe@example.com"
    },
    {
      id: 2,
      name: "Jane Doe",
      email: "jane.doe@example.com"
    }
  ]);

  const table = Table.createWithStore(data);
</script>

<Story name="Default">
  {#snippet template(args)}
    <Table.Root
      viewModel={table.createViewModel([
        table.column({
          header: "ID",
          accessor: "id"
        }),
        table.column({
          header: "Name",
          accessor: "name"
        }),
        table.column({
          header: "Email",
          accessor: "email"
        })
      ])}
    ></Table.Root>
  {/snippet}
</Story>
