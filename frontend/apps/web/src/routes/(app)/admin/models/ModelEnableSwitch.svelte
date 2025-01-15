<!--
    Copyright (c) 2024 Sundsvalls Kommun

    Licensed under the MIT License.
-->

<script lang="ts">
  import type { SecurityLevel } from "@intric/intric-js";
  import { invalidate } from "$app/navigation";
  import { getIntric } from "$lib/core/Intric";
  import IconKey from "$lib/components/icons/IconKey.svelte";
  import RadioChecked from "$lib/components/icons/RadioChecked.svelte";
  import RadioUnchecked from "$lib/components/icons/RadioUnchecked.svelte";
  import { Dropdown, Button } from "@intric/ui";

  export let model: {
    id: string;
    is_org_enabled?: boolean;
    is_locked?: boolean;
    security_level_id?: string;
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

  async function updateState(state: { enabled: boolean; levelId: string | null }) {
    if (model.is_locked) return;

    const update = {
      is_org_enabled: state.enabled,
      security_level_id: state.levelId || undefined
    };

    if (modeltype === "completion") {
      await updateCompletionModel({ id: model.id }, update);
    } else if (modeltype === "embedding") {
      await updateEmbeddingModel({ id: model.id }, update);
    }
  }

  function getCurrentState() {
    if (!model.is_org_enabled) return "disabled";
    if (model.security_level_id) return `enabled-${model.security_level_id}`;
    return "enabled";
  }
</script>

<div>
  <Dropdown.Root>
    <Dropdown.Trigger let:trigger asFragment>
      <Button
        is={trigger}
        variant="simple"
        class="-ml-2 flex items-center gap-2 text-sm text-stone-600"
        disabled={model.is_locked}
      >
        {#if !model.is_org_enabled}
          <RadioUnchecked size="small" />
          <span>Disabled</span>
        {:else if model.security_level_id && securityLevel}
          <IconKey size="small" />
          <span>{securityLevel.name}</span>
        {:else}
          <RadioChecked size="small" />
          <span>Enabled</span>
        {/if}
      </Button>
    </Dropdown.Trigger>
    <Dropdown.Menu let:item>
      <Button
        is={item}
        on:click={() => updateState({ enabled: false, levelId: null })}
        class="flex items-center gap-2"
      >
        <RadioUnchecked size="small" />
        <span>Disabled</span>
      </Button>
      <Button
        is={item}
        on:click={() => updateState({ enabled: true, levelId: null })}
        class="flex items-center gap-2"
      >
        <RadioChecked size="small" />
        <span>Enabled</span>
      </Button>
      {#if securityLevels.length > 0}
        <div class="mt-2 flex items-center gap-2 px-2 py-1 text-stone-500">
          <span>Enabled on security level</span>
        </div>
        <div class="flex flex-col">
          {#each securityLevels as level}
            <Button
              is={item}
              on:click={() => updateState({ enabled: true, levelId: level.id })}
              class="flex items-center gap-2"
            >
              <IconKey size="small" />
              <span>{level.name}</span>
            </Button>
          {/each}
        </div>
      {/if}
    </Dropdown.Menu>
  </Dropdown.Root>
</div>
