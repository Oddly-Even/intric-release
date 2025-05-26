<script lang="ts">
  import { getSpacesManager } from "$lib/features/spaces/SpacesManager";
  import TemplateSelector from "$lib/features/templates/components/TemplateSelector.svelte";
  import TemplateWizard from "$lib/features/templates/components/wizard/TemplateWizard.svelte";
  import { getTemplateController } from "$lib/features/templates/TemplateController";
  import { Button, Dialog, Input } from "@intric/ui";
  import CreateAssistantBackdrop from "./CreateAssistantBackdrop.svelte";
  import { goto } from "$app/navigation";
  import { _ } from "svelte-i18n";

  const {
    state: { currentSpace },
    refreshCurrentSpace
  } = getSpacesManager();

  const {
    createOrContinue,
    resetForm,
    state: { currentStep, createButtonLabel, creationMode, showCreateDialog }
  } = getTemplateController();

  let openAssistantAfterCreation = true;
  let userTouchedToggle = false;

  function disableEditorOnTemplate(creationMode: "blank" | "template") {
    if (userTouchedToggle) return;
    openAssistantAfterCreation = creationMode === "blank";
  }

  $: disableEditorOnTemplate($creationMode);
</script>

<Dialog.Root openController={showCreateDialog} on:close={resetForm}>
  <Dialog.Trigger asFragment let:trigger>
    {#if $$slots.default}
      <slot {trigger}></slot>
    {:else}
      <Button is={trigger} variant="primary">{$_("app.spaces.assistants.create")}</Button>
    {/if}
  </Dialog.Trigger>

  <Dialog.Content width="dynamic" form>
    {#if $currentSpace.completion_models.length < 1}
      <p
        class="label-warning border-label-default bg-label-dimmer text-label-stronger m-4 rounded-md border px-2 py-1 text-sm"
      >
        <span class="font-bold">{$_("app.spaces.assistants.warning")}</span>
        {$_("app.spaces.assistants.noCompletionModels")}
      </p>
      <div class="border-dimmer border-b"></div>
    {/if}

    <Dialog.Section class="relative -mb-0.5 mt-2">
      {#if $currentStep === "wizard"}
        <TemplateWizard></TemplateWizard>
      {:else}
        <TemplateSelector></TemplateSelector>
        <div class="absolute right-0 top-0 h-52 w-72 overflow-hidden">
          <CreateAssistantBackdrop></CreateAssistantBackdrop>
        </div>
      {/if}
    </Dialog.Section>

    <Dialog.Controls let:close>
      <Input.Switch
        bind:value={openAssistantAfterCreation}
        sideEffect={() => {
          userTouchedToggle = true;
        }}
        class="flex-row-reverse p-2"
        >{$_("app.spaces.assistants.openEditorAfterCreation")}</Input.Switch
      >
      <div class="flex-grow"></div>

      {#if $currentStep === "wizard"}
        <Button
          on:click={() => {
            $currentStep = "start";
          }}>{$_("app.spaces.assistants.back")}</Button
        >
      {:else}
        <Button is={close}>{$_("app.spaces.assistants.cancel")}</Button>
      {/if}
      <Button
        variant="primary"
        class="w-40"
        on:click={() => {
          createOrContinue({
            onResourceCreated: ({ id }) => {
              refreshCurrentSpace();
              $showCreateDialog = false;
              resetForm();
              if (openAssistantAfterCreation) {
                goto(`/spaces/${$currentSpace.routeId}/assistants/${id}/edit?next=default`);
              }
            }
          });
        }}>{$createButtonLabel}</Button
      >
    </Dialog.Controls>
  </Dialog.Content>
</Dialog.Root>
