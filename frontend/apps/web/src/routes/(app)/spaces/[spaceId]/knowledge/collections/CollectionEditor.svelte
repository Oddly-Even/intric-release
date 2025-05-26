<script lang="ts">
  import { getIntric } from "$lib/core/Intric";
  import SelectEmbeddingModel from "$lib/features/ai-models/components/SelectEmbeddingModel.svelte";
  import { getSpacesManager } from "$lib/features/spaces/SpacesManager";
  import { Dialog, Button, Input } from "@intric/ui";
  import { _ } from "svelte-i18n";

  const intric = getIntric();
  const {
    refreshCurrentSpace,
    state: { currentSpace }
  } = getSpacesManager();

  export let mode: "update" | "create" = "create";
  export let collection: { id: string; name: string } | undefined;
  let collectionName = collection?.name ?? "";
  let embeddingModel: { id: string } | undefined = undefined;

  let isProcessing = false;
  async function editCollection() {
    if (!collection) return;
    isProcessing = true;
    try {
      collection = await intric.groups.update({
        group: { id: collection.id },
        update: { name: collectionName }
      });

      refreshCurrentSpace();
      $showDialog = false;
    } catch (error) {
      alert(error);
      console.error(error);
    }
    isProcessing = false;
  }

  async function createCollection() {
    isProcessing = true;
    try {
      await intric.groups.create({
        spaceId: $currentSpace.id,
        name: collectionName,
        embedding_model: embeddingModel
      });

      refreshCurrentSpace();
      collectionName = "";
      $showDialog = false;
    } catch (error) {
      alert(error);
      console.error(error);
    }
    isProcessing = false;
  }

  export let showDialog: Dialog.OpenState | undefined = undefined;
</script>

<Dialog.Root bind:isOpen={showDialog}>
  {#if mode === "create"}
    <Dialog.Trigger asFragment let:trigger>
      <Button variant="primary" is={trigger}>{$_("app.spaces.knowledge.collections.create")}</Button
      >
    </Dialog.Trigger>
  {/if}

  <Dialog.Content width="medium" form>
    {#if mode === "create"}
      <Dialog.Title>{$_("app.spaces.knowledge.collections.createTitle")}</Dialog.Title>
      <Dialog.Description hidden
        >{$_("app.spaces.knowledge.collections.createTitle")}</Dialog.Description
      >
    {:else}
      <Dialog.Title>{$_("app.spaces.knowledge.collections.editTitle")}</Dialog.Title>
      <Dialog.Description hidden
        >{$_("app.spaces.knowledge.collections.editDescription")}</Dialog.Description
      >
    {/if}

    <Dialog.Section>
      {#if mode === "create"}
        {#if $currentSpace.embedding_models.length < 1}
          <p
            class="label-warning border-label-default bg-label-dimmer text-label-stronger m-4 rounded-md border px-2 py-1 text-sm"
          >
            <span class="font-bold">{$_("app.spaces.knowledge.collections.warning")}</span>
            {$_("app.spaces.knowledge.collections.noEmbeddingModels")}
          </p>
          <div class="border-default border-b"></div>
        {/if}
        <Input.Text
          bind:value={collectionName}
          label={$_("app.spaces.knowledge.collections.name")}
          required
          class="border-default hover:bg-hover-dimmer border-b px-4 py-4"
        ></Input.Text>
        <SelectEmbeddingModel
          hideWhenNoOptions
          bind:value={embeddingModel}
          selectableModels={$currentSpace.embedding_models}
        ></SelectEmbeddingModel>
      {:else}
        <Input.Text
          bind:value={collectionName}
          label={$_("app.spaces.knowledge.collections.name")}
          required
          class="border-default hover:bg-hover-dimmer border-b px-4 py-4"
        ></Input.Text>
      {/if}
    </Dialog.Section>

    <Dialog.Controls let:close>
      <Button is={close}>{$_("app.spaces.knowledge.collections.cancel")}</Button>
      {#if mode === "create"}
        <Button
          variant="primary"
          on:click={createCollection}
          type="submit"
          disabled={isProcessing || $currentSpace.embedding_models.length === 0}
          >{isProcessing
            ? $_("app.spaces.knowledge.collections.creating")
            : $_("app.spaces.knowledge.collections.create")}</Button
        >
      {:else if mode === "update"}
        <Button variant="primary" on:click={editCollection} type="submit"
          >{isProcessing
            ? $_("app.spaces.knowledge.collections.saving")
            : $_("app.spaces.knowledge.collections.save")}</Button
        >
      {/if}
    </Dialog.Controls>
  </Dialog.Content>
</Dialog.Root>
