<script lang="ts">
  import { Button } from "@intric/ui";
  import type { SecurityLevel } from "@intric/intric-js";
  import { getIntric } from "$lib/core/Intric";
  import { invalidate } from "$app/navigation";
  import SecurityLevelDialog from "./SecurityLevelDialog.svelte";
  const intric = getIntric();

  export let securityLevel: SecurityLevel;

  async function deleteSecurityLevel() {
    await intric.securityLevels.deleteSecurityLevel(securityLevel.id);
    invalidate("admin:security-levels:load");
  }
</script>
<div class="flex gap-2">
  <SecurityLevelDialog {securityLevel}></SecurityLevelDialog>
  <Button destructive label="Delete" on:click={deleteSecurityLevel}>
    <span>Delete</span>
  </Button>
</div>
