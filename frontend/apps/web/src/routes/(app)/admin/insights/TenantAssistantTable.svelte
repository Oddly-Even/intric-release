<!--
    Copyright (c) 2024 Sundsvalls Kommun

    Licensed under the MIT License.
-->

<script lang="ts">
  import { IconAssistant } from "@intric/icons/assistant";
  import type { Assistant } from "@intric/intric-js";
  import { Table } from "@intric/ui";
  import { createRender } from "svelte-headless-table";
  import { _ } from "svelte-i18n";

  export let assistants: Assistant[];
  const table = Table.createWithResource(assistants);

  const viewModel = table.createViewModel([
    table.columnPrimary({
      header: $_("app.admin.insights.assistants.table.columns.name"),
      value: (item) => item.name,
      cell: (item) => {
        return createRender(Table.PrimaryCell, {
          label: `${item.value.name} (Space: ${item.value.space_id})`,
          link: `/admin/insights/assistant/${item.value.id}`,
          icon: IconAssistant
        });
      }
    }),
    table.column({
      header: $_("app.admin.insights.assistants.table.columns.logging"),
      accessor: "logging_enabled",
      cell: (item) =>
        item.value
          ? $_("app.admin.insights.assistants.table.logging.enabled")
          : $_("app.admin.insights.assistants.table.logging.disabled"),
      plugins: {
        sort: { getSortValue: (item) => item.logging_enabled ?? 0 }
      }
    })
  ]);

  $: table.update(assistants);
</script>

<Table.Root {viewModel} resourceName="assistant"></Table.Root>
