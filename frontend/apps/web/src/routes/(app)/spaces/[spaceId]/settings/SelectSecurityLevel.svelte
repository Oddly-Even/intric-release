<!--
    Copyright (c) 2024 Sundsvalls Kommun

    Licensed under the MIT License.
-->

<script lang="ts">
  import { getSpacesManager } from "$lib/features/spaces/SpacesManager";
  import type { SecurityLevel } from "@intric/intric-js";
  import { Select } from "@intric/ui";
  import { writable, type Writable } from "svelte/store";

  export let securityLevels: SecurityLevel[];

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
</script>

<div class="flex flex-col gap-4 py-5 pr-6 lg:flex-row lg:gap-12">
  <div class="pl-2 lg:w-2/5">
    <h3 class="pb-1 text-lg font-medium">Space Security Level</h3>
    <p class="text-stone-500">Set the security level for this space and all its resources.</p>
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
