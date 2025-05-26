<script lang="ts">
  import TemplateGallery from "./gallery/TemplateGallery.svelte";
  import { getTemplateController } from "../TemplateController";
  import { formatEmojiTitle } from "$lib/core/formatting/formatEmojiTitle";
  import TemplateIcon from "./TemplateIcon.svelte";
  import { Input } from "@intric/ui";
  import { IconChevronUpDown } from "@intric/icons/chevron-up-down";
  import { IconInfo } from "@intric/icons/info";
  import { IconCopy } from "@intric/icons/copy";
  import { IconFile } from "@intric/icons/file";
  import { getAppContext } from "$lib/core/AppContext";
  import { _ } from "svelte-i18n";

  const {
    state: { name, creationMode, selectedTemplate, showTemplateGallery, hasWizard },
    resourceName
  } = getTemplateController();

  const { featureFlags } = getAppContext();
</script>

<div class="outer relative flex flex-grow flex-col items-start justify-start text-left">
  <div class=" border-default flex w-full flex-col px-10 pb-10 pt-12">
    <h3 class="px-4 pb-1 text-2xl font-extrabold">
      {$_("features.templates.selector.createNew", { values: { resource: resourceName.singular } })}
    </h3>
    <p class="text-secondary max-w-[60ch] pl-4 pr-36">
      {#if featureFlags.showTemplates}
        {$_("features.templates.selector.createNewOrTemplate", {
          values: { resource: resourceName.singular }
        })}
      {:else}
        {$_("features.templates.selector.createNewDescription", {
          values: { resource: resourceName.singular }
        })}
      {/if}
    </p>
    <!-- <div class="h-8"></div> -->
    <div class="border-dimmer mb-2 mt-14 border-t"></div>
    <div class="flex flex-col gap-1 pb-4 pt-6">
      <span class="px-4 pb-1 text-lg font-medium"
        >{$_("features.templates.selector.nameLabel", {
          values: { resource: resourceName.singularCapitalised }
        })}</span
      >
      <Input.Text bind:value={$name} hiddenLabel inputClass="!text-lg !py-6 !px-4" required
        >{$_("features.templates.selector.nameLabel", {
          values: { resource: resourceName.singularCapitalised }
        })}</Input.Text
      >
    </div>
    {#if featureFlags.showTemplates}
      <div class="grid grid-cols-2 gap-4">
        <button
          data-selected={$creationMode === "blank"}
          on:click|preventDefault={() => ($creationMode = "blank")}
          class="selector"
        >
          <div class="flex w-full items-center justify-start gap-2 text-left">
            <IconFile></IconFile>
            <span class="text-dynamic-stronger line-clamp-2">
              {$_("features.templates.selector.createBlank", {
                values: { resource: resourceName.singular }
              })}</span
            >
          </div>
        </button>
        <div class="relative flex">
          <button
            data-selected={$creationMode === "template"}
            on:click|preventDefault={() => {
              if ($creationMode === "template" || $selectedTemplate === null) {
                $showTemplateGallery = true;
              }
              $creationMode = "template";
            }}
            class="selector"
          >
            <div class="flex w-full items-center justify-start gap-2 pr-6 text-left">
              {#if $selectedTemplate}
                <TemplateIcon template={$selectedTemplate}></TemplateIcon>
                <span class="text-dynamic-stronger truncate"
                  >{formatEmojiTitle($selectedTemplate.name)}</span
                >
              {:else}
                <IconCopy></IconCopy>
                {$_("features.templates.selector.startWithTemplate")}
              {/if}
              <div class="flex-grow"></div>
            </div>
          </button>
          <button
            class="border-default text-secondary hover:bg-hover-default absolute right-2 top-[50%] -translate-y-[50%] rounded border p-1"
            on:click|preventDefault={() => {
              $showTemplateGallery = true;
            }}
          >
            <IconChevronUpDown></IconChevronUpDown>
          </button>
        </div>
      </div>

      {#if $hasWizard}
        <p class="text-secondary translate-y-5 p-2 text-center">
          <IconInfo class="inline"></IconInfo>
          {$_("features.templates.selector.hasWizard")}
        </p>
      {/if}

      <TemplateGallery></TemplateGallery>
    {/if}
  </div>
</div>

<style lang="postcss">
  @reference "@intric/ui/styles";
  button.selector {
    @apply border-default text-muted flex h-[3.25rem] flex-grow items-center justify-between overflow-hidden rounded-lg border p-3 pr-2 shadow;
  }

  button:hover.selector {
    @apply border-stronger bg-hover-default text-primary ring-default cursor-pointer ring-2;
  }

  button[data-selected="true"].selector {
    @apply border-accent-default bg-accent-dimmer text-accent-stronger shadow-accent-dimmer ring-accent-default shadow-lg ring-1 focus:outline-offset-4;
  }
</style>
