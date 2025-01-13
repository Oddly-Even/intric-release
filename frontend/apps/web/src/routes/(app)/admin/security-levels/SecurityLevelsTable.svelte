<script lang="ts">
    import { Table } from "@intric/ui";
    import { onMount } from "svelte";
    import type { SecurityLevel } from "@intric/intric-js";

    export let securityLevels: SecurityLevel[] = [];

    const table = Table.createWithResource(securityLevels);

    const viewModel = table.createViewModel([
        table.column({ accessor: "name", header: "Name" }),
        table.column({ accessor: "value", header: "Value" }),
        table.column({ accessor: "description", header: "Description" }),
    ]);

    // onMount(async () => {
    //     // TODO: Fetch security levels from API
    //     const response = await fetch('/api/admin/security-levels');
    //     securityLevels = await response.json();
    //     console.log(securityLevels);
    // });

    // async function handleAddLevel() {
    //     // TODO: Implement add security level
    // }

    // async function handleEditLevel(id: number) {
    //     // TODO: Implement edit security level
    // }

    // async function handleDeleteLevel(id: number) {
    //     // TODO: Implement delete security level
    // }

    $: table.update(securityLevels);
</script>

<Table.Root {viewModel} resourceName="security-level" displayAs="list">
  <Table.Group />
</Table.Root>
