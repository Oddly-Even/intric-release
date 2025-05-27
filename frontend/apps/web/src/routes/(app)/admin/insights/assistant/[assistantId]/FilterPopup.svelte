<!--
    Copyright (c) 2024 Sundsvalls Kommun

    Licensed under the MIT License.
-->

<script lang="ts">
  import { IconFilter } from "@intric/icons/filter";
  import { Button, Dialog, Input } from "@intric/ui";
  import type { CalendarDate } from "@internationalized/date";
  import { _ } from "svelte-i18n";

  export let includeFollowups: boolean;
  export let dateRange: { start: CalendarDate; end: CalendarDate };
  export let onUpdate:
    | ((
        includeFollowups: boolean,
        dateRange: { start: CalendarDate; end: CalendarDate }
      ) => Promise<void>)
    | undefined = undefined;

  let isOpen: Dialog.OpenState;

  async function update() {
    try {
      await onUpdate?.(includeFollowups, dateRange);
      $isOpen = false;
    } catch (error) {
      alert(error);
    }
  }
</script>

<Dialog.Root bind:isOpen>
  <Dialog.Trigger asFragment let:trigger>
    <Button variant="primary" is={trigger}>
      <IconFilter />
      {$_("app.admin.insights.filter.settings")}</Button
    >
  </Dialog.Trigger>

  <Dialog.Content width="medium" form>
    <Dialog.Title>{$_("app.admin.insights.filter.title")}</Dialog.Title>

    <Dialog.Section>
      <Input.DateRange
        bind:value={dateRange}
        class="border-default hover:bg-hover-dimmer border-b px-4 py-4"
        >{$_("app.admin.insights.filter.timeframe")}</Input.DateRange
      >
      <Input.Switch
        bind:value={includeFollowups}
        class="border-default hover:bg-hover-dimmer border-b px-4 py-4"
        >{$_("app.admin.insights.filter.includeFollowups")}</Input.Switch
      >
    </Dialog.Section>

    <Dialog.Controls let:close>
      <Button is={close}>{$_("app.admin.insights.filter.cancel")}</Button>

      <Button variant="primary" on:click={update}>{$_("app.admin.insights.filter.update")}</Button>
    </Dialog.Controls>
  </Dialog.Content>
</Dialog.Root>
