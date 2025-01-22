<!--
    Copyright (c) 2024 Sundsvalls Kommun

    Licensed under the MIT License.
-->

<script lang="ts">
  import type { SecurityLevel } from "@intric/intric-js";
  import { Dialog } from "@intric/ui";

  export let isOpen: Dialog.OpenState;
  export let currentSecurityLevel: SecurityLevel | undefined;
  export let newSecurityLevel: SecurityLevel | undefined;
  export let onConfirm: () => void;
  export let onCancel: () => void;
</script>

<Dialog.Root alert bind:isOpen>
  <Dialog.Content>
    <Dialog.Title>Change Security Level</Dialog.Title>
    <Dialog.Description hidden>Change the security level of the space</Dialog.Description>

    <Dialog.Section>
      <p>
        You are about to change the security level from
        <span class="font-medium">{currentSecurityLevel?.name || "None"}</span>
        to
        <span class="font-medium">{newSecurityLevel?.name || "None"}</span>.
      </p>
    </Dialog.Section>

    <Dialog.Controls let:close>
      <button
        type="button"
        class="rounded-md bg-white px-3 py-2 text-sm font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50"
        on:click={onCancel}
      >
        Cancel
      </button>
      <button
        type="button"
        class="rounded-md bg-blue-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-blue-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-600"
        on:click={onConfirm}
      >
        Confirm Change
      </button>
    </Dialog.Controls>
  </Dialog.Content>
</Dialog.Root>
