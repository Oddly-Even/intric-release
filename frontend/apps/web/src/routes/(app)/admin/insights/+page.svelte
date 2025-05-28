<!--
    Copyright (c) 2024 Sundsvalls Kommun

    Licensed under the MIT License.
-->

<script lang="ts">
  import { IconAssistants } from "@intric/icons/assistants";
  import { IconSession } from "@intric/icons/session";
  import { IconQuestionMark } from "@intric/icons/question-mark";
  import { IconLoadingSpinner } from "@intric/icons/loading-spinner";
  import { Page, Settings } from "$lib/components/layout";
  import { _ } from "svelte-i18n";

  import InteractiveGraph from "./InteractiveGraph.svelte";
  import TenantAssistantTable from "./TenantAssistantTable.svelte";
  import { writable } from "svelte/store";

  export let data;

  let selectedTab = writable<string>();
</script>

<svelte:head>
  <title>{$_("app.admin.insights.page.title")}</title>
</svelte:head>

<Page.Root tabController={selectedTab}>
  <Page.Header>
    <Page.Title title={$_("app.admin.insights.page.header.title")}></Page.Title>
    <Page.Tabbar>
      <Page.TabTrigger tab="overview"
        >{$_("app.admin.insights.page.header.tabs.overview")}</Page.TabTrigger
      >
      <Page.TabTrigger tab="assistants"
        >{$_("app.admin.insights.page.header.tabs.assistants")}</Page.TabTrigger
      >
    </Page.Tabbar>
  </Page.Header>
  <Page.Main>
    <Page.Tab id="overview">
      {#if $selectedTab === "overview"}
        <Settings.Page>
          <Settings.Group title={$_("app.admin.insights.overview.statistics.title")}>
            <Settings.Row
              fullWidth
              title={$_("app.admin.insights.overview.statistics.assistantUsage.title")}
              description={$_("app.admin.insights.overview.statistics.assistantUsage.description")}
            >
              <div class="h-[600px]">
                <div
                  class="relativ border-stronger flex h-full w-full items-stretch overflow-clip rounded-lg border shadow"
                >
                  {#await data.data}
                    <div class="flex h-full w-full items-center justify-center">
                      <div class="flex flex-col items-center justify-center gap-2 pt-3">
                        <IconLoadingSpinner class="animate-spin" />
                        {$_("app.admin.insights.overview.statistics.loading")}
                      </div>
                    </div>
                  {:then loadedData}
                    <InteractiveGraph data={loadedData} timeframe={data.timeframe}
                    ></InteractiveGraph>

                    <div class="border-stronger bg-hover-dimmer flex flex-grow flex-col border-l">
                      <div class="border-stronger flex h-1/3 flex-col justify-between border-b p-6">
                        <div class="flex gap-2">
                          <IconAssistants />
                          {$_("app.admin.insights.overview.statistics.metrics.assistantsCreated")}
                        </div>
                        <span class="self-end text-[2.75rem] font-medium"
                          >{loadedData.assistants.length}</span
                        >
                      </div>

                      <div class="border-stronger flex h-1/3 flex-col justify-between border-b p-6">
                        <div class="flex gap-2">
                          <IconSession />
                          {$_(
                            "app.admin.insights.overview.statistics.metrics.conversationsStarted"
                          )}
                        </div>
                        <span class="self-end text-[2.75rem] font-medium"
                          >{loadedData.sessions.length}</span
                        >
                      </div>

                      <div class="border-stronger flex h-1/3 flex-col justify-between p-6">
                        <div class="flex gap-2">
                          <IconQuestionMark />
                          {$_("app.admin.insights.overview.statistics.metrics.questionsAsked")}
                        </div>
                        <span class="self-end text-[2.75rem] font-medium"
                          >{loadedData.questions.length}</span
                        >
                      </div>
                    </div>
                  {/await}
                </div>
              </div>
            </Settings.Row>
          </Settings.Group>
        </Settings.Page>
      {/if}
    </Page.Tab>
    <Page.Tab id="assistants">
      <TenantAssistantTable assistants={data.assistants} />
    </Page.Tab>
  </Page.Main>
</Page.Root>
