<!--
    Copyright (c) 2024 Sundsvalls Kommun

    Licensed under the MIT License.
-->

<script lang="ts">
  import type { SecurityLevel } from "@intric/intric-js";
  import { invalidate } from "$app/navigation";
  import { getIntric } from "$lib/core/Intric";
  import { Input, Tooltip, Dropdown, Button } from "@intric/ui";

  export let model: { id: string; is_org_enabled?: boolean; is_locked?: boolean, security_level_id?: string };
  export let modeltype: "completion" | "embedding";
  export let securityLevels: SecurityLevel[];

  let securityLevel: SecurityLevel | undefined;

  $: if (securityLevels) {
    securityLevel = securityLevels.find(level => level.id === model.security_level_id);
  }

  const intric = getIntric();

  async function updateCompletionModel(
    completionModel: { id: string },
    update: { is_org_enabled: boolean; security_level_id?: string }
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
    update: { is_org_enabled: boolean; security_level_id?: string }
  ) {
    try {
      await intric.models.update({ embeddingModel, update });
      invalidate("admin:models:load");
    } catch (e) {
      alert(e);
      console.error(e);
    }
  }

  async function updateModel({ next }: { next: boolean }) {
    if (modeltype == "completion") {
      await updateCompletionModel({ id: model.id }, { is_org_enabled: next });
    } else if (modeltype == "embedding") {
      await updateEmbeddingModel({ id: model.id }, { is_org_enabled: next });
    } else {
      console.error("Invalid model type");
    }
  }

  async function updateSecurityLevel(levelId: string | null) {
    if (model.is_org_enabled === undefined) return;
    
    const update = { 
      is_org_enabled: model.is_org_enabled as boolean, 
      security_level_id: levelId || undefined 
    };
    
    if (modeltype == "completion") {
      await updateCompletionModel({ id: model.id }, update);
    } else if (modeltype == "embedding") {
      await updateEmbeddingModel({ id: model.id }, update);
    }
  }

  $: tooltip = model.is_locked
    ? "EU-hosted models are available on request"
    : model.is_org_enabled
      ? "Toggle to disable model"
      : "Toggle to enable model";
</script>

<div class="rounded-lg border border-stone-200 p-3">
  <div class="flex items-center gap-4">
    <Tooltip text={tooltip}>
      <Input.Switch sideEffect={updateModel} value={model.is_org_enabled} disabled={model.is_locked}
      ></Input.Switch>
    </Tooltip>
    <span class="text-sm font-medium text-stone-700">
      {model.is_org_enabled ? "Enabled" : "Disabled"}
    </span>
  </div>
  
  {#if model.is_org_enabled && !model.is_locked}
    <div class="mt-2 border-t border-stone-100 pt-2">
      <div class="text-xs text-stone-500 mb-1">Security Level</div>
      <Dropdown.Root>
        <Dropdown.Trigger let:trigger asFragment>
          <Button is={trigger} variant="simple" class="text-sm text-gray-500 -ml-2">
            {securityLevel?.name || 'Select security level'}
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
  {:else if securityLevel}
    <div class="mt-2 border-t border-stone-100 pt-2">
      <div class="text-xs text-stone-500 mb-1">Security Level</div>
      <span class="text-sm text-gray-500">
        {securityLevel.name}
      </span>
    </div>
  {/if}
</div>
