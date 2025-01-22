<!--
    Copyright (c) 2025 Sundsvalls Kommun

    Licensed under the MIT License.
-->

<script lang="ts">
  import type { SecurityLevel } from "@intric/intric-js";
  import { invalidate } from "$app/navigation";
  import { getIntric } from "$lib/core/Intric";
  import { Dropdown, Button, Tooltip } from "@intric/ui";
  import IconKey from "$lib/components/icons/IconKey.svelte";

  export let model: {
    id: string;
    is_locked?: boolean;
    security_level_id?: string | null;
    is_org_enabled?: boolean;
  };
  export let modeltype: "completion" | "embedding";
  export let securityLevels: SecurityLevel[];

  let securityLevel: SecurityLevel | undefined;

  $: if (securityLevels) {
    securityLevel = securityLevels.find((level) => level.id === model.security_level_id);
  }

  const intric = getIntric();

  async function updateCompletionModel(
    completionModel: { id: string },
    update: { security_level_id?: string | null; is_org_enabled?: boolean }
  ) {
    try {
      await intric.models.update({ completionModel, update });
      invalidate("admin:models:load");
    } catch (e) {
      alert(e);
      console.error(e);
    }
  }

  async function updateEmbeddingModel(
    embeddingModel: { id: string },
    update: { security_level_id?: string | null; is_org_enabled?: boolean }
  ) {
    try {
      await intric.models.update({ embeddingModel, update });
      invalidate("admin:models:load");
    } catch (e) {
      alert(e);
      console.error(e);
    }
  }

  async function updateSecurityLevel(levelId: string | null) {
    if (model.is_locked) return;

    const update = {
      security_level_id: levelId || undefined,
      is_org_enabled: model.is_org_enabled ?? false
    };

    if (modeltype === "completion") {
      await updateCompletionModel({ id: model.id }, update);
    } else if (modeltype === "embedding") {
      await updateEmbeddingModel({ id: model.id }, update);
    } else {
      throw new Error("Invalid model type");
    }
  }
</script>

<div>
  {#if securityLevels.length === 0}
    <Tooltip text="Security levels must be created before they can be assigned">
      <span class="text-stone-600 text-sm">No security level</span>
    </Tooltip>
  {:else}
    <Dropdown.Root>
      <Dropdown.Trigger let:trigger asFragment>
        <Button
          is={trigger}
          variant={model.security_level_id ? "primary" : "outlined"}
          class="flex items-center gap-2 text-sm text-stone-600"
          disabled={model.is_locked}
        >
          {#if model.security_level_id && securityLevel}
            <IconKey size="small" />
            <span>{securityLevel.name}</span>
          {:else}
            <span>No security level</span>
          {/if}
        </Button>
      </Dropdown.Trigger>
      <Dropdown.Menu let:item>
        <Button
          is={item}
          on:click={() => updateSecurityLevel(null)}
          class="flex items-center gap-2"
        >
          <span>No security level</span>
        </Button>
        {#each securityLevels as level}
          <Button
            is={item}
            on:click={() => updateSecurityLevel(level.id)}
            class="flex items-center gap-2"
          >
            <IconKey size="small" />
            <span>{level.name}</span>
          </Button>
        {/each}
      </Dropdown.Menu>
    </Dropdown.Root>
  {/if}
</div>
