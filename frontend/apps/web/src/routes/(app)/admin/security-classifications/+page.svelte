<!--
    Copyright (c) 2024 Sundsvalls Kommun

    Licensed under the MIT License.
-->

<script lang="ts">
  import { Page, Settings } from "$lib/components/layout";
  import MultipleModelsClassificationDialog from "$lib/features/security-classifications/components/MultipleModelsClassificationDialog.svelte";
  import SecurityClassificationEnabledSetting from "$lib/features/security-classifications/components/SecurityClassificationEnabledSetting.svelte";
  import SecurityClassificationListSetting from "$lib/features/security-classifications/components/SecurityClassificationListSetting.svelte";
  import { initSecurityClassificationService } from "$lib/features/security-classifications/SecurityClassificationsService.svelte.js";
  import { _ } from "svelte-i18n";

  const { data } = $props();

  initSecurityClassificationService(data.intric, data.securityClassifications);
  // Using a JS string so we can have a newline in this
  const description =
    "Select a security classification for all of you organisation's models.\nModels will be available in spaces with the same or lower classification.";
</script>

<svelte:head>
  <title>{$_("app.admin.security.page.title")}</title>
</svelte:head>

<Page.Root>
  <Page.Header>
    <Page.Title title={$_("app.admin.security.page.header.title")}></Page.Title>
  </Page.Header>
  <Page.Main>
    <Settings.Page>
      <Settings.Group title={$_("app.admin.security.settings.general.title")}>
        <SecurityClassificationEnabledSetting></SecurityClassificationEnabledSetting>
      </Settings.Group>
      <Settings.Group title={$_("app.admin.security.settings.configuration.title")}>
        <SecurityClassificationListSetting></SecurityClassificationListSetting>

        <Settings.Row
          title={$_("app.admin.security.settings.configuration.classifyModels.title")}
          description={$_("app.admin.security.settings.configuration.classifyModels.description")}
          fullWidth
        >
          <div class="grid gap-4">
            <MultipleModelsClassificationDialog
              models={data.models.completionModels}
              type="completionModel"
            ></MultipleModelsClassificationDialog>
            <MultipleModelsClassificationDialog
              models={data.models.embeddingModels}
              type="embeddingModel"
            ></MultipleModelsClassificationDialog>
            <MultipleModelsClassificationDialog
              models={data.models.transcriptionModels}
              type="transcriptionModel"
            ></MultipleModelsClassificationDialog>
          </div>
        </Settings.Row>
      </Settings.Group>
    </Settings.Page>
  </Page.Main>
</Page.Root>
