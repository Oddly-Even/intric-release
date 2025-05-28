<script lang="ts">
  import { Button } from "@intric/ui";
  import CreateAppBackdrop from "./CreateAppBackdrop.svelte";
  import { getTemplateController } from "../../TemplateController";
  import TemplateSmallPreviewGallery from "../gallery/TemplateSmallPreviewGallery.svelte";
  import { _ } from "svelte-i18n";

  const {
    state: { showCreateDialog }
  } = getTemplateController();
</script>

<div class="flex h-full flex-grow items-center justify-center">
  <div class="max-w-[640px]">
    <div
      class="border-default bg-primary relative mx-1 flex flex-col items-start overflow-clip rounded-2xl border px-10 py-8 text-left shadow-md"
    >
      <span class="font-mono text-sm uppercase">{$_("app.spaces.apps.hint.title")}</span>
      <h3 class="b-1 text-2xl font-extrabold">{$_("app.spaces.apps.hint.getStarted")}</h3>
      <p class="text-secondary max-w-[50ch] pr-48 pt-2">
        {$_("app.spaces.apps.hint.description")}
      </p>
      <Button
        unstyled
        on:click={() => {
          $showCreateDialog = true;
        }}
        class="bg-accent-default text-on-fill hover:bg-accent-stronger -ml-1 mt-8 rounded-lg px-3 py-1.5 text-center"
      >
        {$_("app.spaces.apps.hint.create")}
      </Button>

      <div class="absolute right-0 top-0 h-56 w-80 overflow-hidden">
        <CreateAppBackdrop></CreateAppBackdrop>
      </div>
    </div>
    <div class="h-2"></div>
    <TemplateSmallPreviewGallery></TemplateSmallPreviewGallery>
  </div>
</div>
