<script lang="ts" module>
  import { defineMeta } from "@storybook/addon-svelte-csf";
  import { CalendarDate } from "@internationalized/date";
  import * as Input from "./index";

  const timeframe: { start: CalendarDate; end: CalendarDate } = {
    start: new CalendarDate(2025, 6, 1),
    end: new CalendarDate(2025, 6, 30)
  };

  // More on how to set up stories at: https://storybook.js.org/docs/writing-stories
  const { Story } = defineMeta({
    title: "UI/Input/DateRange",
    tags: ["autodocs"]
  });
</script>

<Story name="Default">
  {#snippet template(args)}
    <Input.DateRange {...args}>Select date range</Input.DateRange>
  {/snippet}
</Story>
