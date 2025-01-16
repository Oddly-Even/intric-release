<!--
    Copyright (c) 2024 Sundsvalls Kommun

    Licensed under the MIT License.
-->

<script lang="ts">
  import { getSpacesManager } from "$lib/features/spaces/SpacesManager";
  import type { SecurityLevel } from "@intric/intric-js";
  import { Button, Dropdown } from "@intric/ui";

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
</script>

<div class="flex flex-col gap-4 py-5 pr-6 lg:flex-row lg:gap-12">
  <div class="pl-2 lg:w-2/5">
    <h3 class="pb-1 text-lg font-medium">Space Security Level</h3>
    <p class="text-stone-500">Set the security level for this space and all its resources.</p>
  </div>
  <div class="flex flex-grow items-start gap-2">
    <Dropdown.Root>
      <Dropdown.Trigger let:trigger asFragment>
        <Button is={trigger} variant="simple" class="flex items-center gap-2" disabled={isUpdating}>
          {#if isUpdating}
            Updating...
          {:else}
            {securityLevel?.name || 'Select security level'}
            <div class="i-lucide-chevron-down" />
          {/if}
        </Button>
      </Dropdown.Trigger>
      <Dropdown.Menu let:item>
        <Button is={item} on:click={() => updateSecurityLevel(null)}>
          No security level
        </Button>
        {#each securityLevels as level}
          <Button is={item} on:click={() => updateSecurityLevel(level.id)}>
            {level.name}
          </Button>
        {/each}
      </Dropdown.Menu>
    </Dropdown.Root>
  </div>
</div>
