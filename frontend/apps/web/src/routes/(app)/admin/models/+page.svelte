<!--
    Copyright (c) 2024 Sundsvalls Kommun

    Licensed under the MIT License.
-->

<script lang="ts">
  import { Page } from "$lib/components/layout/index.js";
  import { setSecurityContext } from "$lib/features/security-classifications/SecurityContext.js";
  import CompletionModelsTable from "./CompletionModelsTable.svelte";
  import EmbeddingModelsTable from "./EmbeddingModelsTable.svelte";
  import TranscriptionModelsTable from "./TranscriptionModelsTable.svelte";
  import { _ } from "svelte-i18n";

  export let data;

  setSecurityContext(data.securityClassifications);
</script>

<svelte:head>
  <title>{$_("app.admin.models.page.title")}</title>
</svelte:head>

<Page.Root>
  <Page.Header>
    <Page.Title title={$_("app.admin.models.page.header.title")}></Page.Title>
    <Page.Tabbar>
      <Page.TabTrigger tab="completion_models"
        >{$_("app.admin.models.page.header.tabs.completion")}</Page.TabTrigger
      >
      <Page.TabTrigger tab="embedding_models"
        >{$_("app.admin.models.page.header.tabs.embedding")}</Page.TabTrigger
      >
      <Page.TabTrigger tab="transcription_models"
        >{$_("app.admin.models.page.header.tabs.transcription")}</Page.TabTrigger
      >
    </Page.Tabbar>
  </Page.Header>
  <Page.Main>
    <Page.Tab id="completion_models">
      <CompletionModelsTable completionModels={data.models.completionModels} />
    </Page.Tab>
    <Page.Tab id="embedding_models">
      <EmbeddingModelsTable embeddingModels={data.models.embeddingModels} />
    </Page.Tab>
    <Page.Tab id="transcription_models">
      <TranscriptionModelsTable transcriptionModels={data.models.transcriptionModels} />
    </Page.Tab>
  </Page.Main>
</Page.Root>
