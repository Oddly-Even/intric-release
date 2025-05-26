<!--
    Copyright (c) 2024 Sundsvalls Kommun

    Licensed under the MIT License.
-->

<script lang="ts">
  import { Settings } from "$lib/components/layout";
  import type { StorageSpaceList, StorageUsageSummary } from "@intric/intric-js";
  import StorageOverviewBar from "./StorageOverviewBar.svelte";
  import StorageTable from "./StorageTable.svelte";
  import { _ } from "svelte-i18n";

  type Props = {
    spaces: StorageSpaceList[];
    storageStats: StorageUsageSummary;
  };

  const { spaces, storageStats }: Props = $props();
</script>

<Settings.Page>
  <Settings.Group title={$_("app.admin.usage.storage.overview")}>
    <StorageOverviewBar {storageStats}></StorageOverviewBar>
  </Settings.Group>
  <Settings.Group title={$_("app.admin.usage.storage.details")}>
    <Settings.Row
      title={$_("app.admin.usage.storage.publicSpaces")}
      description={$_("app.admin.usage.storage.publicSpacesDescription")}
      fullWidth
    >
      <StorageTable {spaces} />
    </Settings.Row>
  </Settings.Group>
</Settings.Page>
