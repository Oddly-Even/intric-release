<script lang="ts">
  import { IconXMark } from "@intric/icons/x-mark";
  import { Button } from "../Button/index.js";
  import { getDialog } from "./ctx.js";
  import { _ } from "svelte-i18n";

  const {
    elements: { title, close }
  } = getDialog();
</script>

<div class="flex items-center justify-between pb-2">
  <h2 {...$title} use:title class="truncate text-xl font-medium">
    <slot />
  </h2>
  <Button is={[$close]} label={$_("ui.dialog.close")} class="-mr-2" padding="icon">
    <IconXMark />
  </Button>
</div>
