<script lang="ts">
  import { Page, Settings } from "$lib/components/layout";
  import { getSpacesManager } from "$lib/features/spaces/SpacesManager.js";

  import { Button, Input, Tooltip } from "@intric/ui";
  import { afterNavigate, beforeNavigate } from "$app/navigation";

  import { initAssistantEditor } from "$lib/features/assistants/AssistantEditor.js";
  import { fade } from "svelte/transition";

  import AssistantSettingsAttachments from "./AssistantSettingsAttachments.svelte";
  import SelectAIModelV2 from "$lib/features/ai-models/components/SelectAIModelV2.svelte";
  import SelectBehaviourV2 from "$lib/features/ai-models/components/SelectBehaviourV2.svelte";
  import SelectKnowledgeV2 from "$lib/features/knowledge/components/SelectKnowledgeV2.svelte";
  import PromptVersionDialog from "$lib/features/prompts/components/PromptVersionDialog.svelte";
  import dayjs from "dayjs";
  import PublishingSetting from "$lib/features/publishing/components/PublishingSetting.svelte";
  import { page } from "$app/state";
  import { getChatQueryParams } from "$lib/features/chat/getChatQueryParams.js";
  import { _ } from "svelte-i18n";

  export let data;

  const {
    state: { currentSpace },
    refreshCurrentSpace
  } = getSpacesManager();

  const {
    state: { resource, update, currentChanges, isSaving },
    saveChanges,
    discardChanges
  } = initAssistantEditor({
    assistant: data.assistant,
    intric: data.intric,
    onUpdateDone() {
      refreshCurrentSpace("applications");
    }
  });

  let cancelUploadsAndClearQueue: () => void;

  beforeNavigate((navigate) => {
    if (
      $currentChanges.hasUnsavedChanges &&
      !confirm($_("app.spaces.assistants.edit.discardChanges"))
    ) {
      navigate.cancel();
      return;
    }
    // Discard changes that have been made, this is only important so we delete uploaded
    // files that have not been saved to the assistant
    discardChanges();
  });

  let showSavesChangedNotice = false;

  let previousRoute = `/spaces/${$currentSpace.routeId}/chat/?${getChatQueryParams({ chatPartner: data.assistant, tab: "chat" })}`;
  afterNavigate(({ from }) => {
    if (page.url.searchParams.get("next") === "default") return;
    if (from) previousRoute = from.url.toString();
  });
</script>

<svelte:head>
  <title
    >{$_("app.spaces.page.title.space", {
      values: {
        spaceName: data.currentSpace.personal
          ? $_("app.navigation.personal")
          : data.currentSpace.name
      }
    })} – {$resource.name}</title
  >
</svelte:head>

<Page.Root>
  <Page.Header>
    <Page.Title
      parent={{
        title: $resource.name,
        href: `/spaces/${$currentSpace.routeId}/chat/?${getChatQueryParams({ chatPartner: data.assistant, tab: "chat" })}`
      }}
      title={$_("app.spaces.assistants.edit.title")}
    ></Page.Title>

    <Page.Flex>
      {#if $currentChanges.hasUnsavedChanges}
        <Button
          variant="destructive"
          disabled={$isSaving}
          on:click={() => {
            cancelUploadsAndClearQueue();
            discardChanges();
          }}>{$_("app.spaces.assistants.edit.discardAll")}</Button
        >

        <Button
          variant="positive"
          class="w-32"
          on:click={async () => {
            cancelUploadsAndClearQueue();
            await saveChanges();
            showSavesChangedNotice = true;
            setTimeout(() => {
              showSavesChangedNotice = false;
            }, 5000);
          }}
          >{$isSaving
            ? $_("app.spaces.assistants.edit.saving")
            : $_("app.spaces.assistants.edit.save")}</Button
        >
      {:else}
        {#if showSavesChangedNotice}
          <p class="text-positive-stronger px-4" transition:fade>
            {$_("app.spaces.assistants.edit.saved")}
          </p>
        {/if}
        <Button variant="primary" class="w-32" href={previousRoute}
          >{$_("app.spaces.assistants.edit.done")}</Button
        >
      {/if}
    </Page.Flex>
  </Page.Header>

  <Page.Main>
    <Settings.Page>
      <Settings.Group title={$_("app.spaces.assistants.edit.general")}>
        <Settings.Row
          title={$_("app.spaces.assistants.edit.name")}
          description={$_("app.spaces.assistants.edit.nameDescription")}
          hasChanges={$currentChanges.diff.name !== undefined}
          revertFn={() => {
            discardChanges("name");
          }}
          let:aria
        >
          <input
            type="text"
            {...aria}
            bind:value={$update.name}
            class="border-default bg-primary ring-default rounded-lg border px-3 py-2 shadow focus-within:ring-2 hover:ring-2 focus-visible:ring-2"
          />
        </Settings.Row>

        <Settings.Row
          title={$_("app.spaces.assistants.edit.description")}
          description={$_("app.spaces.assistants.edit.descriptionDescription")}
          hasChanges={$currentChanges.diff.description !== undefined}
          revertFn={() => {
            discardChanges("description");
          }}
          let:aria
        >
          <textarea
            placeholder={$_("app.spaces.assistants.edit.descriptionPlaceholder", {
              values: { name: $update.name }
            })}
            {...aria}
            bind:value={$update.description}
            class="border-default bg-primary ring-default placeholder:text-muted min-h-24 rounded-lg border px-3 py-2 shadow focus-within:ring-2 hover:ring-2 focus-visible:ring-2"
          ></textarea>
        </Settings.Row>
      </Settings.Group>

      <Settings.Group title={$_("app.spaces.assistants.edit.instructions")}>
        <Settings.Row
          title={$_("app.spaces.assistants.edit.prompt")}
          description={$_("app.spaces.assistants.edit.promptDescription")}
          hasChanges={$currentChanges.diff.prompt !== undefined}
          revertFn={() => {
            discardChanges("prompt");
          }}
          fullWidth
          let:aria
        >
          <div slot="toolbar" class="text-secondary">
            <PromptVersionDialog
              title={$_("app.spaces.assistants.edit.promptHistory", {
                values: { name: $resource.name }
              })}
              loadPromptVersionHistory={() => {
                return data.intric.assistants.listPrompts({ id: data.assistant.id });
              }}
              onPromptSelected={(prompt) => {
                const restoredDate = dayjs(prompt.created_at).format("YYYY-MM-DD HH:mm");
                $update.prompt.text = prompt.text;
                $update.prompt.description = $_("app.spaces.assistants.edit.promptRestored", {
                  values: { date: restoredDate }
                });
              }}
            ></PromptVersionDialog>
          </div>
          <textarea
            rows={4}
            {...aria}
            bind:value={$update.prompt.text}
            on:change={() => {
              $update.prompt.description = "";
            }}
            class="border-default bg-primary ring-default min-h-24 rounded-lg border px-6 py-4 text-lg shadow focus-within:ring-2 hover:ring-2 focus-visible:ring-2"
          ></textarea>
        </Settings.Row>

        <Settings.Row
          title={$_("app.spaces.assistants.edit.attachments")}
          description={$_("app.spaces.assistants.edit.attachmentsDescription")}
          hasChanges={$currentChanges.diff.attachments !== undefined}
          revertFn={() => {
            cancelUploadsAndClearQueue();
            discardChanges("attachments");
          }}
        >
          <AssistantSettingsAttachments bind:cancelUploadsAndClearQueue
          ></AssistantSettingsAttachments>
        </Settings.Row>

        <Settings.Row
          title={$_("app.spaces.assistants.edit.knowledge")}
          description={$_("app.spaces.assistants.edit.knowledgeDescription")}
          hasChanges={$currentChanges.diff.groups !== undefined ||
            $currentChanges.diff.websites !== undefined ||
            $currentChanges.diff.integration_knowledge_list !== undefined}
          revertFn={() => {
            discardChanges("groups");
            discardChanges("websites");
            discardChanges("integration_knowledge_list");
          }}
        >
          <SelectKnowledgeV2
            bind:selectedWebsites={$update.websites}
            bind:selectedCollections={$update.groups}
            bind:selectedIntegrationKnowledge={$update.integration_knowledge_list}
          ></SelectKnowledgeV2>
        </Settings.Row>
      </Settings.Group>

      <Settings.Group title={$_("app.spaces.assistants.edit.aiSettings")}>
        <Settings.Row
          title={$_("app.spaces.assistants.edit.completionModel")}
          description={$_("app.spaces.assistants.edit.completionModelDescription")}
          hasChanges={$currentChanges.diff.completion_model !== undefined}
          revertFn={() => {
            discardChanges("completion_model");
          }}
          let:aria
        >
          <SelectAIModelV2
            bind:selectedModel={$update.completion_model}
            availableModels={$currentSpace.completion_models}
            {aria}
          ></SelectAIModelV2>
        </Settings.Row>

        <Settings.Row
          title={$_("app.spaces.assistants.edit.modelBehaviour")}
          description={$_("app.spaces.assistants.edit.modelBehaviourDescription")}
          hasChanges={$currentChanges.diff.completion_model_kwargs !== undefined}
          revertFn={() => {
            discardChanges("completion_model_kwargs");
          }}
          let:aria
        >
          <SelectBehaviourV2 bind:kwArgs={$update.completion_model_kwargs} {aria}
          ></SelectBehaviourV2>
        </Settings.Row>
      </Settings.Group>

      {#if data.assistant.permissions?.some((permission) => permission === "insight_toggle" || permission === "publish")}
        <Settings.Group title={$_("app.spaces.assistants.edit.publishing")}>
          {#if data.assistant.permissions?.includes("publish")}
            <Settings.Row
              title={$_("app.spaces.assistants.edit.status")}
              description={$_("app.spaces.assistants.edit.statusDescription")}
            >
              <PublishingSetting
                endpoints={data.intric.assistants}
                resource={data.assistant}
                hasUnsavedChanges={$currentChanges.hasUnsavedChanges}
              />
            </Settings.Row>
          {/if}

          <Settings.Row
            hasChanges={$currentChanges.diff.insight_enabled !== undefined}
            revertFn={() => {
              discardChanges("insight_enabled");
            }}
            title={$_("app.spaces.assistants.edit.insights")}
            description={$_("app.spaces.assistants.edit.insightsDescription")}
          >
            <div class="border-default flex h-14 border-b py-2">
              <Tooltip
                text={data.assistant.permissions?.includes("insight_toggle")
                  ? undefined
                  : $_("app.spaces.assistants.edit.insightsPermission")}
                class="w-full"
              >
                <Input.RadioSwitch
                  bind:value={$update.insight_enabled}
                  labelTrue={$_("app.spaces.assistants.edit.enableInsights")}
                  labelFalse={$_("app.spaces.assistants.edit.disableInsights")}
                  disabled={!data.assistant.permissions?.includes("insight_toggle")}
                ></Input.RadioSwitch>
              </Tooltip>
            </div>
          </Settings.Row>
        </Settings.Group>
      {/if}

      <div class="min-h-24"></div>
    </Settings.Page>
  </Page.Main>
</Page.Root>
