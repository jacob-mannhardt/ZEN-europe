<script lang="ts">
  import { onMount } from "svelte";
  import { api } from "./lib/api";
  import { settingsPatch } from "./lib/settings";
  import {
    app,
    isDirty,
    load,
    refreshDatasets,
    refreshJobs,
    refreshStructure,
    revert,
    save,
    type View,
  } from "./lib/store.svelte";
  import ModelsView from "./views/ModelsView.svelte";
  import StructureView from "./views/StructureView.svelte";
  import GenerateView from "./views/GenerateView.svelte";
  import DataView from "./views/DataView.svelte";

  const tabs: { id: View; label: string }[] = [
    { id: "models", label: "Models" },
    { id: "structure", label: "Structure" },
    { id: "generate", label: "Generate & download" },
    { id: "data", label: "Data explorer" },
  ];

  let saving = $state(false);
  const dirty = $derived(isDirty());
  const errorCount = $derived(
    Object.keys(app.validation.errors).length + (app.validation.file_error ? 1 : 0),
  );
  const activeJobs = $derived(app.jobs.filter((j) => j.status === "queued" || j.status === "running").length);

  onMount(() => {
    // #<view>, or #data/<dataset>/<element type>/<element>
    const [view, dataset, elementType, element] = location.hash.slice(1).split("/").map(decodeURIComponent);
    if (tabs.some((t) => t.id === view)) app.view = view as View;
    if (view === "data" && dataset) app.data = { dataset, elementType: elementType || null, element: element || null };
    load();
  });

  // the tab and the shown element are kept in the URL, so they survive a reload
  $effect(() => {
    const { dataset, elementType, element } = app.data;
    const parts =
      app.view === "data" && dataset ? [app.view, dataset, elementType ?? "", element ?? ""] : [app.view];
    history.replaceState(null, "", "#" + parts.map(encodeURIComponent).join("/").replace(/\/+$/, ""));
  });

  // validate the models file while it is edited
  let validateTimer: ReturnType<typeof setTimeout> | undefined;
  $effect(() => {
    const snapshot = JSON.stringify(app.doc);
    if (!app.catalog) return;
    clearTimeout(validateTimer);
    const validate = async (attempt: number) => {
      try {
        app.validation = await api.validate(JSON.parse(snapshot));
      } catch (error) {
        // a request that did not reach the backend is retried, it says
        // nothing about the models file
        if (error instanceof TypeError && attempt < 3) {
          validateTimer = setTimeout(() => validate(attempt + 1), 2000);
          return;
        }
        app.validation = { file_error: (error as Error).message, errors: {} };
      }
    };
    validateTimer = setTimeout(() => validate(0), 400);
  });

  // keep the structure of the selected model up to date while it is edited
  const patchJson = $derived(JSON.stringify(settingsPatch(app.doc, app.selected)));
  let structureTimer: ReturnType<typeof setTimeout> | undefined;
  $effect(() => {
    const patch = patchJson;
    if (!app.catalog) return;
    clearTimeout(structureTimer);
    structureTimer = setTimeout(() => refreshStructure(patch), 250);
  });

  // follow the jobs while any is queued or running
  $effect(() => {
    if (!activeJobs) return;
    const timer = setInterval(async () => {
      const before = app.jobs.filter((j) => j.status === "done").length;
      await refreshJobs();
      if (app.jobs.filter((j) => j.status === "done").length !== before) await refreshDatasets();
    }, 1500);
    return () => clearInterval(timer);
  });

  async function onSave() {
    saving = true;
    try {
      await save();
    } finally {
      saving = false;
    }
  }

  function onBeforeUnload(event: BeforeUnloadEvent) {
    if (isDirty()) event.preventDefault();
  }
</script>

<svelte:window onbeforeunload={onBeforeUnload} />

<div class="shell">
  <header>
    <div class="brand">
      <strong>ZEN-europe</strong> <span class="muted">model dashboard</span>
    </div>
    <nav>
      {#each tabs as tab}
        <button class="tab" class:active={app.view === tab.id} onclick={() => (app.view = tab.id)}>
          {tab.label}
          {#if tab.id === "generate" && activeJobs}<span class="badge changed">{activeJobs} running</span>{/if}
        </button>
      {/each}
    </nav>
    <div class="spacer"></div>
    {#if app.catalog}
      <div class="row save-area">
        {#if errorCount}
          <span class="badge bad" title="See the models with a red mark">{errorCount} error{errorCount > 1 ? "s" : ""}</span>
        {/if}
        {#if dirty}
          <span class="muted small">Unsaved changes</span>
          <button onclick={revert}>Revert</button>
          <button class="primary" onclick={onSave} disabled={saving || errorCount > 0}>Save models.yaml</button>
        {:else}
          <span class="muted small" title={app.info.models_path}>models.yaml saved</span>
        {/if}
      </div>
    {/if}
  </header>

  <main>
    {#if app.loading}
      <div class="empty">Loading the ZEN-europe settings …</div>
    {:else if app.error}
      <div class="empty">
        <div class="error-box">{app.error}</div>
        <p>Start the backend with <code>python -m zen_dashboard</code> in <code>backend/</code>.</p>
      </div>
    {:else if app.catalog}
      {#if app.view === "models"}
        <ModelsView />
      {:else if app.view === "structure"}
        <StructureView />
      {:else if app.view === "generate"}
        <GenerateView />
      {:else}
        <DataView />
      {/if}
    {/if}
  </main>
</div>

<style>
  .shell {
    display: flex;
    flex-direction: column;
    height: 100%;
  }

  header {
    display: flex;
    align-items: center;
    gap: 16px;
    padding: 0 16px;
    height: 52px;
    background: var(--surface);
    border-bottom: 1px solid var(--border);
    flex-shrink: 0;
  }

  .brand {
    font-size: 15px;
    white-space: nowrap;
  }

  nav {
    display: flex;
    gap: 2px;
    height: 100%;
  }

  .tab {
    border: none;
    border-radius: 0;
    background: transparent;
    border-bottom: 2px solid transparent;
    padding: 0 12px;
    color: var(--ink-2);
    display: flex;
    align-items: center;
    gap: 6px;
  }

  .tab.active {
    color: var(--ink);
    border-bottom-color: var(--accent);
    font-weight: 600;
  }

  main {
    flex: 1;
    min-height: 0;
    overflow: hidden;
  }

  @media (max-width: 900px) {
    header {
      height: auto;
      flex-wrap: wrap;
      padding: 8px 16px;
    }
    nav {
      overflow-x: auto;
      height: 40px;
    }
  }
</style>
