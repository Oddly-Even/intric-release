<!--
    Copyright (c) 2024 Sundsvalls Kommun

    Licensed under the MIT License.
-->

<script lang="ts" generics="T extends unknown">
  import { IconChevronDown } from "@intric/icons/chevron-down";
  import Button from "$lib/Button/Button.svelte";
  import { derived, writable } from "svelte/store";
  import { Render, Subscribe } from "svelte-headless-table";
  import { getCardCell, getTableContext } from "./create.js";
  import { cva } from "class-variance-authority";

  const tableContext = getTableContext<T>();
  const { viewModel, displayType, gapX, gapY, layout } = tableContext;
  const { pageRows: rows, tableBodyAttrs, pluginStates } = viewModel;

  export let title: string | undefined | null = undefined;
  export let filterFn: (value: T) => boolean = () => true;

  const open = writable(true);
  // Original is not exposed on the type but present on the store...
  // Keep an eye on this in the future (here we just cast it)
  const filteredRows = derived(rows, (rows) =>
    rows.filter((row) => filterFn((row as unknown as { original: T }).original))
  );

  const { hasPreviousPage, hasNextPage, pageCount, pageIndex } = pluginStates.page;

  const cardLayout = cva("mt-3 pb-4 pl-0.5 pr-4 pt-2", {
    variants: {
      layout: {
        flex: ["flex", "flex-wrap"],
        grid: [
          "grid",
          "grid-cols-1",
          "sm:grid-cols-2",
          "md:grid-cols-3",
          "lg:grid-cols-4",
          "xl:grid-cols-5"
        ]
      }
    }
  });

  const tableCell = cva(
    [
      "whitespace-nowrap",
      "border-b",
      "px-4",
      "pr-8",
      "text-left",
      "font-normal",
      "first-of-type:pr-0",
      "last-of-type:pr-4"
    ],
    {
      variants: {
        primary: {
          true: ["w-full", "max-w-[1px]", "overflow-hidden", "overflow-ellipsis"],
          false: "w-[0%]"
        },
        groupHeader: {
          false: ["border-dimmer"],
          true: ["border-default", "pl-2.5", "py-3.5"]
        }
      },
      defaultVariants: {
        groupHeader: false,
        primary: false
      }
    }
  );
</script>

{#if $filteredRows.length > 0}
  {#if $displayType === "list"}
    <tbody {...$tableBodyAttrs}>
      {#if title}
        <tr>
          <td colspan="99" class={tableCell({ groupHeader: true })}>
            <Button
              on:click={() => ($open = !$open)}
              padding="icon-leading"
              class="font-mono font-medium"
            >
              <div class="flex w-full gap-2">
                <IconChevronDown class="{$open ? 'rotate-0' : '-rotate-90'} w-5 transition-all" />
                <span>{title}</span>
              </div>
            </Button>
          </td>
        </tr>
      {/if}
      {#if $open}
        {#each $filteredRows as row (row.id)}
          <Subscribe rowAttrs={row.attrs()} let:rowAttrs>
            <tr {...rowAttrs} class="hover:bg-hover-dimmer relative h-16">
              {#each row.cells as cell (cell.id)}
                {#if cell.id !== "table-card-key"}
                  <Subscribe attrs={cell.attrs()} let:attrs>
                    <td {...attrs} class={tableCell({ primary: cell.id === "table-primary-key" })}>
                      {#if cell.id === "table-action-key"}
                        <div class="flex items-center justify-end">
                          <Render of={cell.render()} />
                        </div>
                      {:else}
                        <Render of={cell.render()} />
                      {/if}
                    </td>
                  </Subscribe>
                {/if}
              {/each}
            </tr>
          </Subscribe>
        {/each}
      {/if}
    </tbody>
  {:else}
    {#if title}
      <div class="!border-b-default flex border-b pt-4 pb-2 !pl-2.5">
        <Button
          on:click={() => ($open = !$open)}
          padding="icon-leading"
          class="font-mono font-medium"
        >
          <div class="flex w-full gap-2">
            <IconChevronDown class="{$open ? 'rotate-0' : '-rotate-90'} w-5 transition-all" />
            <span>{title}</span>
          </div>
        </Button>
      </div>
    {/if}
    {#if $open}
      <div style="column-gap: {gapX}rem; row-gap: {gapY}rem;" class={cardLayout({ layout })}>
        {#each $filteredRows as row (row.id)}
          {@const cell = getCardCell(row)}
          {#if cell}
            <Render of={cell.render()} />
          {/if}
        {/each}
      </div>
    {/if}
  {/if}
  {#if $pageCount > 1}
    <div
      class="bg-hover-dimmer my-4 flex h-12 w-fit items-center justify-start gap-6 rounded-lg border p-2"
    >
      <Button on:click={() => ($pageIndex -= 1)} disabled={!$hasPreviousPage} variant="outlined"
        >←</Button
      >

      <div class="flex gap-2 font-mono">
        <span>
          {$pageIndex + 1}
        </span>
        <span> / </span>
        <span>
          {$pageCount}
        </span>
      </div>

      <Button on:click={() => ($pageIndex += 1)} disabled={!$hasNextPage} variant="outlined"
        >→</Button
      >
    </div>
  {:else}
    <svelte:element this={$displayType === "list" ? "tbody" : "div"} class="!h-6" />
  {/if}
{:else}
  <svelte:element this={$displayType === "list" ? "tbody" : "div"} />
{/if}
