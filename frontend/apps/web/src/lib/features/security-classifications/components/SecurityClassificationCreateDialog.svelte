<!--
    Copyright (c) 2024 Sundsvalls Kommun

    Licensed under the MIT License.
-->

<script lang="ts">
  import { Button, Dialog, Input } from "@intric/ui";
  import { writable } from "svelte/store";
  import { getSecurityClassificationService } from "../SecurityClassificationsService.svelte";
  import { IntricError } from "@intric/intric-js";
  import { createAsyncState } from "$lib/core/helpers/createAsyncState.svelte";
  import { _ } from "svelte-i18n";

  let name = $state("");
  let description = $state("");
  const showDialog = writable(false);
  const security = getSecurityClassificationService();

  const create = createAsyncState(async () => {
    if (!name) return;
    try {
      await security.createClassification({ name, description });
      $showDialog = false;
      name = "";
      description = "";
    } catch (error) {
      alert(error instanceof IntricError ? error.getReadableMessage() : String(error));
    }
  });
</script>

<Dialog.Root openController={showDialog}>
  <Dialog.Trigger asFragment let:trigger>
    <Button variant="primary" is={trigger}>{$_("app.admin.security.settings.create.button")}</Button
    >
  </Dialog.Trigger>

  <Dialog.Content width="medium" form>
    <Dialog.Title>{$_("app.admin.security.settings.create.title")}</Dialog.Title>

    <Dialog.Section>
      <Input.Text
        bind:value={name}
        label={$_("app.admin.security.settings.create.name.label")}
        description={$_("app.admin.security.settings.create.name.description")}
        required
        class="border-default hover:bg-hover-dimmer border-b p-4"
      ></Input.Text>

      <Input.TextArea
        label={$_("app.admin.security.settings.create.description.label")}
        class="border-default hover:bg-hover-dimmer border-b p-4"
        description={$_("app.admin.security.settings.create.description.description")}
        bind:value={description}
      ></Input.TextArea>
    </Dialog.Section>

    <Dialog.Controls let:close>
      <Button is={close}>{$_("app.admin.security.settings.create.cancel")}</Button>
      <Button variant="primary" onclick={create} type="submit" disabled={create.isLoading}
        >{create.isLoading
          ? $_("app.admin.security.settings.create.creating")
          : $_("app.admin.security.settings.create.confirm")}</Button
      >
    </Dialog.Controls>
  </Dialog.Content>
</Dialog.Root>
