<!--
    Copyright (c) 2024 Sundsvalls Kommun

    Licensed under the MIT License.
-->

<script lang="ts">
  import { IconChevronUpDown } from "@intric/icons/chevron-up-down";
  import { IconSelectedItem } from "@intric/icons/selected-item";
  import { IconSquare } from "@intric/icons/square";
  import { Button, Dialog } from "@intric/ui";
  import { createDropdownMenu } from "@melt-ui/svelte";
  import { getSpacesManager } from "../SpacesManager";
  import { fade, fly } from "svelte/transition";
  import SpaceChip from "./SpaceChip.svelte";
  import CreateSpaceDialog from "./CreateSpaceDialog.svelte";
  import { _ } from "svelte-i18n";

  export let showSelectPrompt = false;

  const spaces = getSpacesManager();
  const {
    state: { currentSpace, accessibleSpaces }
  } = spaces;

  const {
    elements: { trigger, menu, item, overlay, arrow },
    states: { open }
  } = createDropdownMenu({
    forceVisible: true,
    portal: null,
    loop: true,
    positioning: {
      placement: "bottom-start",
      overlap: true,
      overflowPadding: 0
    },
    arrowSize: 12
  });

  let showCreateDialog: Dialog.OpenState;
</script>

{#if $currentSpace.personal && !showSelectPrompt}
  <div
    class="border-default group relative flex h-[4.25rem] w-full items-center justify-start gap-3 border-b-[0.5px] pl-[1.4rem] pr-5 pt-0.5 font-medium"
  >
    <SpaceChip space={$currentSpace}></SpaceChip>
    <span class="text-primary flex-grow truncate pl-0.5 text-left">
      {$_("features.spaces.components.spaceSelector.personal")}
    </span>
  </div>
{:else}
  <Button
    is={[$trigger]}
    unstyled
    label="Change space or create a new one"
    class="border-default hover:bg-accent-dimmer hover:text-accent-stronger font-mediu group relative flex h-[4.25rem] w-full items-center justify-start gap-3 border-b-[0.5px] pl-[1.4rem] pr-5 pt-0.5"
  >
    {#if showSelectPrompt}
      <div
        class="bg-dynamic-dimmer text-dynamic-stronger flex min-h-[1.6rem] min-w-[1.6rem] items-center justify-center rounded-md"
      >
        <IconSquare />
      </div>
      <span class="text-primary flex-grow truncate pl-0.5 text-left"
        >{$_("features.spaces.components.spaceSelector.select")}</span
      >
    {:else}
      <SpaceChip space={$currentSpace}></SpaceChip>
      <span class="text-primary flex-grow truncate pl-0.5 text-left">
        {$currentSpace.name}
      </span>
    {/if}
    <IconChevronUpDown class="text-muted group-hover:text-accent-stronger min-w-6" />
  </Button>
{/if}

<!-- Selector drop down -->
{#if $open}
  <div
    {...$overlay}
    use:overlay
    class="bg-overlay-dimmer fixed inset-0 z-[70]"
    transition:fade={{ duration: 200 }}
  ></div>
  <div
    {...$menu}
    use:menu
    in:fly={{ y: -15, duration: 100 }}
    out:fly={{ y: -5, duration: 200 }}
    class="items bg-primary absolute z-[80] flex min-w-[17rem] -translate-x-0.5 -translate-y-[0.78rem] flex-col rounded-sm p-3 shadow-md"
  >
    <div
      class="border-default text-secondary flex items-baseline justify-between gap-4 border-b pb-2.5 pl-6 pr-3 pt-1 font-mono text-[0.85rem] font-medium tracking-[0.015rem]"
    >
      <a href="/spaces/list" class="hover:underline">{$_("app.spaces.list.title")}</a>
    </div>

    <div class="relative max-h-[50vh] overflow-y-auto">
      {#each $accessibleSpaces as space (space.id)}
        {#if !space.personal}
          <Button
            unstyled
            is={[$item]}
            href="/spaces/{space.id}/overview"
            class="border-default hover:bg-accent-dimmer hover:text-accent-stronger group relative flex h-[4.25rem] w-full items-center justify-start gap-3 border-b pl-5 pr-4 last-of-type:border-b-0"
          >
            <SpaceChip {space}></SpaceChip>

            <span class="flex-grow truncate text-left">
              {space.name}
            </span>
            <div class="text-accent-stronger ml-2 min-w-5">
              {#if space.id === $currentSpace.id && !showSelectPrompt}
                <IconSelectedItem />
              {/if}
            </div>
          </Button>
        {/if}
      {/each}
    </div>
    <Button
      unstyled
      on:click={() => {
        $showCreateDialog = true;
      }}
      is={[$item]}
      class="border-default bg-accent-default text-on-fill hover:bg-accent-stronger mt-1 !justify-center rounded-lg border !py-2 shadow-md focus:outline-offset-4 focus:ring-offset-4"
      >{$_("features.spaces.components.spaceSelector.create")}</Button
    >
    <div {...$arrow} use:arrow class="border-stronger !z-10"></div>
  </div>
{/if}

<CreateSpaceDialog includeTrigger={false} forwardToNewSpace={true} bind:isOpen={showCreateDialog}
></CreateSpaceDialog>

<style>
  .items {
    box-shadow:
      0px 10px 20px -10px rgba(0, 0, 0, 0.5),
      0px 30px 50px 0px rgba(0, 0, 0, 0.2);
  }
</style>
