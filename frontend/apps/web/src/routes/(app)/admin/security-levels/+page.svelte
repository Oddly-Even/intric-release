<!--
    Copyright (c) 2024 Sundsvalls Kommun

    Licensed under the MIT License.
-->

<script lang="ts">
  import { Page } from "$lib/components/layout/index.js";
  import SecurityLevelsTable from "./SecurityLevelsTable.svelte";
  import CreateSecurityLevel from "./CreateSecurityLevel.svelte";
  export let data;

</script>

<svelte:head>
  <title>Intric.ai – Admin – Security Levels</title>
</svelte:head>


<Page.Root>
  <Page.Header>
    <Page.Title>Security levels</Page.Title>
    <CreateSecurityLevel></CreateSecurityLevel>
  </Page.Header>
  <Page.Main>
    <SecurityLevelsTable securityLevels={data.securityLevels} />
  </Page.Main>
</Page.Root>
