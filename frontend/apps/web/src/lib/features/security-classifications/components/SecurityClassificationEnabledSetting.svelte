<!--
    Copyright (c) 2024 Sundsvalls Kommun

    Licensed under the MIT License.
-->

<script lang="ts">
  import { Button, Dialog, Input } from "@intric/ui";
  import { writable } from "svelte/store";
  import { getSecurityClassificationService } from "../SecurityClassificationsService.svelte";
  import { IntricError } from "@intric/intric-js";
  import { Settings } from "$lib/components/layout";
  import { createAsyncState } from "$lib/core/helpers/createAsyncState.svelte";
  import { _ } from "svelte-i18n";

  const security = getSecurityClassificationService();

  let isEnabled = $derived(security.isSecurityEnabled);
  let showEnableDialog = writable(false);
  let showDisableDialog = writable(false);

  function onValueChange({ current, next }: { current: boolean; next: boolean }) {
    if (current !== next) {
      $showEnableDialog = next;
      $showDisableDialog = !next;
    }
  }

  const enable = createAsyncState(async () => {
    try {
      await security.enable();
      $showEnableDialog = false;
    } catch (e) {
      alert(e instanceof IntricError ? e.getReadableMessage() : String(e));
    }
  });

  const disable = createAsyncState(async () => {
    try {
      await security.disable();
      $showDisableDialog = false;
    } catch (e) {
      alert(e instanceof IntricError ? e.getReadableMessage() : String(e));
    }
  });
</script>

<Settings.Row
  title={$_("app.admin.security.settings.enabled.title")}
  description={$_("app.admin.security.settings.enabled.description")}
>
  <div class="border-default flex h-14 border-b py-2">
    <Input.RadioSwitch
      bind:value={isEnabled}
      sideEffect={onValueChange}
      labelTrue={$_("app.admin.security.settings.enabled.toggle.enable")}
      labelFalse={$_("app.admin.security.settings.enabled.toggle.disable")}
    ></Input.RadioSwitch>
  </div>
</Settings.Row>

<Dialog.Root openController={showEnableDialog}>
  <Dialog.Content>
    <Dialog.Title>{$_("app.admin.security.settings.enabled.dialog.enable.title")}</Dialog.Title>

    <Dialog.Description>
      {$_("app.admin.security.settings.enabled.dialog.enable.description")}
    </Dialog.Description>

    <Dialog.Controls>
      <Button
        onclick={() => {
          isEnabled = security.isSecurityEnabled;
          $showEnableDialog = false;
        }}>{$_("app.admin.security.settings.enabled.dialog.enable.cancel")}</Button
      >
      <Button variant="primary" onclick={enable} disabled={enable.isLoading}
        >{$_("app.admin.security.settings.enabled.dialog.enable.confirm")}</Button
      >
    </Dialog.Controls>
  </Dialog.Content>
</Dialog.Root>

<Dialog.Root openController={showDisableDialog}>
  <Dialog.Content>
    <Dialog.Title>{$_("app.admin.security.settings.enabled.dialog.disable.title")}</Dialog.Title>

    <Dialog.Description>
      {$_("app.admin.security.settings.enabled.dialog.disable.description")}
    </Dialog.Description>

    <Dialog.Controls>
      <Button
        onclick={() => {
          isEnabled = security.isSecurityEnabled;
          $showDisableDialog = false;
        }}>{$_("app.admin.security.settings.enabled.dialog.disable.cancel")}</Button
      >
      <Button variant="destructive" onclick={disable} disabled={disable.isLoading}
        >{$_("app.admin.security.settings.enabled.dialog.disable.confirm")}</Button
      >
    </Dialog.Controls>
  </Dialog.Content>
</Dialog.Root>
