<script lang="ts">
  import { invalidate } from "$app/navigation";
  import { getIntric } from "$lib/core/Intric";
  import { Button, Dialog, Input } from "@intric/ui";

  const intric = getIntric();

  let newSecurityLevelName = "";
  let newSecurityLevelDescription = "";
  let newSecurityLevelValue = 0;
  let isProcessing = false;
  async function createSecurityLevel() {
    if (newSecurityLevelName === "") return;
    isProcessing = true;

    try {
      const securityLevel = await intric.securityLevels.createSecurityLevel({
        name: newSecurityLevelName,
        description: newSecurityLevelDescription,
        value: newSecurityLevelValue
      });

      invalidate("admin:security-levels:load");
      $showCreateDialog = false;
      newSecurityLevelName = "";
      newSecurityLevelDescription = "";
      newSecurityLevelValue = 0;
    } catch (e) {
      alert("Error creating new security level");
      console.error(e);
    }
    isProcessing = false;
  }

  let showCreateDialog: Dialog.OpenState;
</script>

<Dialog.Root alert bind:isOpen={showCreateDialog}>
  <Dialog.Trigger asFragment let:trigger>
    <Button is={trigger} variant="primary">Create security level</Button>
  </Dialog.Trigger>
  <Dialog.Content wide form>
    <Dialog.Title>Create a new security level</Dialog.Title>

    <Dialog.Section>
      <Input.Text
        bind:value={newSecurityLevelName}
        required
        class="border-b border-stone-100 px-4 py-4 hover:bg-stone-50">Name</Input.Text>
      <Input.Text bind:value={newSecurityLevelDescription} required class="border-b border-stone-100 px-4 py-4 hover:bg-stone-50">Description</Input.Text>
      <Input.Number bind:value={newSecurityLevelValue} required class="border-b border-stone-100 px-4 py-4 hover:bg-stone-50">Value</Input.Number>
    </Dialog.Section>

    <Dialog.Controls let:close>
      <Button is={close}>Cancel</Button>
      <Button
        variant="primary"
        on:click={createSecurityLevel}
        disabled={isProcessing}
        >{isProcessing ? "Creating..." : "Create security level"}</Button
      >
    </Dialog.Controls>
  </Dialog.Content>
</Dialog.Root>
