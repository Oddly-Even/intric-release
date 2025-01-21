<!--
    Copyright (c) 2024 Sundsvalls Kommun

    Licensed under the MIT License.
-->

<script lang="ts">
  import { getSpacesManager } from "$lib/features/spaces/SpacesManager";
  import type { CompletionModel, EmbeddingModel, SecurityLevel } from "@intric/intric-js";
  import { Select } from "@intric/ui";
  import { writable, type Writable } from "svelte/store";

  export let securityLevels: SecurityLevel[];
  export let embeddingModels: EmbeddingModel[];
  export let completionModels: CompletionModel[];

  const {
    state: { currentSpace },
    updateSpace,
    refreshCurrentSpace
  } = getSpacesManager();

  let securityLevel: SecurityLevel | undefined;
  $: if (securityLevels) {
    securityLevel = securityLevels.find(level => level.id === $currentSpace.security_level?.id);
  }

  let isUpdating = false;
  async function updateSecurityLevel(levelId: string | null) {
    try {
      isUpdating = true;
      await updateSpace({ security_level_id: levelId });
      await refreshCurrentSpace();
    } catch (e) {
      console.error("Error updating security level", e);
      alert("Failed to update security level");
    } finally {
      isUpdating = false;
    }
  }

  let securityLevelStore: Writable<{ value: SecurityLevel | undefined; label: string }>;

  securityLevelStore = writable({
    value: securityLevel,
    label: securityLevel?.name || "No security level"
  });

  $: if (securityLevel !== $securityLevelStore.value && !isUpdating) {
    $securityLevelStore = {
      value: securityLevel,
      label: securityLevel?.name || "No security level"
    };
  }

  $: if (isUpdating) {
    $securityLevelStore = {
      ...$securityLevelStore,
      label: "Updating..."
    };
  } else if ($securityLevelStore.label === "Updating...") {
    $securityLevelStore = {
      ...$securityLevelStore,
      label: $securityLevelStore.value?.name || "No security level"
    };
  }

  securityLevelStore.subscribe((state) => {
    if (!isUpdating && state.value !== securityLevel) {
      updateSecurityLevel(state.value?.id ?? null);
    }
  });

  function hasModelWithIncompatibleSecurityLevel<T extends { id: string }>(
    spaceModels: Array<T>,
    allModels: Array<{ id: string; security_level_id?: string | null }>,
    currentSecurityLevel: SecurityLevel
  ): boolean {
    return spaceModels.some(spaceModel => {
      const model = allModels.find(m => m.id === spaceModel.id);
      if (!model) return false;
      const modelSecurityLevel = securityLevels.find(level => level.id === model.security_level_id)?.value ?? 0;
      return modelSecurityLevel < currentSecurityLevel.value;
    });
  }

  function hasIncompatibleModels(currentSecurityLevel: SecurityLevel): boolean {
    if (!currentSecurityLevel) return false;

    return (
      hasModelWithIncompatibleSecurityLevel($currentSpace.completion_models, completionModels, currentSecurityLevel) ||
      hasModelWithIncompatibleSecurityLevel($currentSpace.embedding_models, embeddingModels, currentSecurityLevel)
    );
  }
</script>

<div class="flex flex-col gap-4 py-5 pr-6 lg:flex-row lg:gap-12">
  <div class="pl-2 pr-12 lg:w-2/5">
    <h3 class="pb-1 text-lg font-medium">Security Level</h3>
    <p class="text-stone-500">Set the security level for this space and all its resources.</p>
    {#if securityLevel && hasIncompatibleModels(securityLevel)}
      <p class="mt-2.5 rounded-md border border-amber-500 bg-amber-50 px-2 py-1 text-sm text-amber-800">
        <span class="font-bold">Warning:&nbsp;</span>Some AI models don't meet the selected security level and will be unavailable.
      </p>
    {/if}
  </div>
  <div class="flex-grow">
    <Select.Root
      customStore={securityLevelStore}
      class="relative w-full border-b border-stone-100 px-4 py-4 hover:bg-stone-50 z-50"
    >
      <Select.Label>Security level</Select.Label>
      <Select.Trigger placeholder="Select..."></Select.Trigger>
      <Select.Options>
        <Select.Item value={undefined} label="No security level">
          <div class="flex w-full items-center justify-between py-1">
            <span>No security level</span>
          </div>
        </Select.Item>
        {#each securityLevels as level}
          <Select.Item value={level} label={level.name}>
            <div class="flex w-full items-center justify-between py-1">
              <span>{level.name}</span>
            </div>
          </Select.Item>
        {/each}
      </Select.Options>
    </Select.Root>
  </div>
</div>
