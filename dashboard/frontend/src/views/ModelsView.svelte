<script lang="ts">
  import yaml from "js-yaml";
  import SettingsEditor from "../components/SettingsEditor.svelte";
  import { app, blocker, datasetOf, generate, latestJob, openData } from "../lib/store.svelte";
  import { clone, countFields, DEFAULTS, lineage } from "../lib/settings";

  const modelNames = $derived(Object.keys(app.doc.models));
  const selected = $derived(app.selected);
  const isDefaults = $derived(selected === DEFAULTS);
  const entry = $derived(isDefaults ? null : app.doc.models[selected]);

  let newName = $state("");
  let renameTo = $state("");
  let renaming = $state(false);
  let showYaml = $state(false);
  let message = $state<string | null>(null);

  const NAME = /^[A-Za-z0-9][A-Za-z0-9_.-]*$/;

  function uniqueName(base: string): string {
    let name = base;
    let i = 2;
    while (app.doc.models[name]) name = `${base}_${i++}`;
    return name;
  }

  function addModel() {
    const name = uniqueName(newName.trim() || "new_model");
    if (!NAME.test(name)) {
      message = "A model name may only contain letters, digits, '_', '.' and '-'.";
      return;
    }
    app.doc.models[name] = { extends: null, settings: {} };
    app.selected = name;
    newName = "";
    message = null;
  }

  function duplicate() {
    if (!entry) return;
    const name = uniqueName(`${selected}_copy`);
    app.doc.models[name] = clone(entry);
    app.selected = name;
  }

  function extendModel() {
    if (isDefaults) return;
    const name = uniqueName(`${selected}_variant`);
    app.doc.models[name] = { extends: selected, settings: {} };
    app.selected = name;
  }

  function remove() {
    if (!entry || modelNames.length <= 1) return;
    const children = modelNames.filter((n) => app.doc.models[n].extends === selected);
    if (children.length) {
      message = `'${selected}' is extended by ${children.join(", ")}. Change those models first.`;
      return;
    }
    if (!confirm(`Delete model '${selected}' from models.yaml? Its generated dataset is kept.`)) return;
    const index = modelNames.indexOf(selected);
    delete app.doc.models[selected];
    app.selected = Object.keys(app.doc.models)[Math.max(0, index - 1)] ?? DEFAULTS;
  }

  function startRename() {
    renameTo = selected;
    renaming = true;
  }

  function rename() {
    const target = renameTo.trim();
    renaming = false;
    if (!target || target === selected) return;
    if (!NAME.test(target) || app.doc.models[target]) {
      message = `Cannot rename to '${target}': the name is invalid or already used.`;
      return;
    }
    // rebuild the mapping to keep the order of the models
    const models: typeof app.doc.models = {};
    for (const name of modelNames) {
      const model = app.doc.models[name];
      if (model.extends === selected) model.extends = target;
      models[name === selected ? target : name] = model;
    }
    app.doc.models = models;
    app.selected = target;
  }

  // a model cannot extend itself or a model that extends it
  const extendable = $derived(
    modelNames.filter((name) => name !== selected && !lineage(app.doc, name).includes(selected)),
  );

  const yamlPreview = $derived.by(() => {
    if (isDefaults) return yaml.dump({ defaults: { settings: app.doc.defaults } }, { flowLevel: 4 });
    const out: Record<string, unknown> = {};
    if (entry?.extends) out.extends = entry.extends;
    if (entry && countFields(entry.settings)) out.settings = entry.settings;
    return yaml.dump({ [selected]: out }, { flowLevel: 4 });
  });

  async function onGenerate() {
    message = null;
    try {
      await generate([selected]);
      app.view = "generate";
    } catch (error) {
      message = (error as Error).message;
    }
  }

  function status(name: string): { label: string; cls: string } | null {
    const job = latestJob(name);
    if (job?.status === "running") return { label: "generating", cls: "changed" };
    if (job?.status === "queued") return { label: "queued", cls: "changed" };
    if (job?.status === "failed") return { label: "failed", cls: "bad" };
    if (datasetOf(name)) return { label: "generated", cls: "good" };
    return null;
  }
</script>

<div class="layout">
  <aside>
    <div class="aside-section">
      <h4 class="muted">Applies to all models</h4>
      <button class="list-button" class:active={isDefaults} onclick={() => (app.selected = DEFAULTS)}>
        <span>defaults</span>
        <span class="spacer"></span>
        {#if countFields(app.doc.defaults)}<span class="badge changed">{countFields(app.doc.defaults)}</span>{/if}
      </button>
    </div>
    <div class="aside-section grow">
      <h4 class="muted">Models in models.yaml</h4>
      {#each modelNames as name}
        {@const s = status(name)}
        <button class="list-button" class:active={selected === name} onclick={() => (app.selected = name)}>
          {#if app.validation.errors[name]}<span class="dot bad" title="This model has invalid settings"></span>
          {:else if app.validation.problems?.[name]}<span class="dot warn" title="This model cannot be generated"></span>{/if}
          <span class="name">
            {name}
            {#if app.doc.models[name].extends}
              <span class="muted small">extends {app.doc.models[name].extends}</span>
            {/if}
          </span>
          <span class="spacer"></span>
          {#if countFields(app.doc.models[name].settings)}
            <span class="badge changed" title="Settings changed by this model">{countFields(app.doc.models[name].settings)}</span>
          {/if}
          {#if s}<span class="badge {s.cls}">{s.label}</span>{/if}
        </button>
      {/each}
    </div>
    <form class="aside-section new" onsubmit={(e) => { e.preventDefault(); addModel(); }}>
      <input type="text" placeholder="new model name" bind:value={newName} />
      <button type="submit">Add</button>
    </form>
  </aside>

  <section class="editor">
    <div class="editor-head">
      {#if isDefaults}
        <div>
          <h2>Defaults</h2>
          <p class="secondary small">
            Settings applied to every model before its own changes. Unchanged settings keep the value of
            <code>{app.catalog?.config_path}</code>.
          </p>
        </div>
      {:else if entry}
        <div class="title-block">
          {#if renaming}
            <form class="row" onsubmit={(e) => { e.preventDefault(); rename(); }}>
              <!-- svelte-ignore a11y_autofocus -->
              <input type="text" bind:value={renameTo} autofocus onblur={rename} />
            </form>
          {:else}
            <h2>
              {selected}
              <button class="ghost small" onclick={startRename} title="Rename">✎ rename</button>
            </h2>
          {/if}
          <label class="row small secondary">
            Extends
            <select
              value={entry.extends ?? ""}
              onchange={(e) => (entry.extends = (e.currentTarget as HTMLSelectElement).value || null)}
            >
              <option value="">— nothing (start from defaults) —</option>
              {#each extendable as name}<option value={name}>{name}</option>{/each}
            </select>
          </label>
        </div>
        <div class="spacer"></div>
        <div class="row actions">
          <button onclick={() => (app.view = "structure")}>View structure</button>
          {#if datasetOf(selected)}
            <button onclick={() => openData(selected)}>Explore data</button>
            <a class="button-link" href={`/api/datasets/${encodeURIComponent(selected)}/download`}>Download</a>
          {/if}
          <button class="primary" onclick={onGenerate} disabled={!!blocker(selected)} title={blocker(selected) ?? ""}>
            {datasetOf(selected) ? "Regenerate" : "Generate"}
          </button>
          <details class="menu">
            <summary class="button-like">More</summary>
            <div class="menu-items card">
              <button class="ghost" onclick={extendModel}>New model extending this one</button>
              <button class="ghost" onclick={duplicate}>Duplicate</button>
              <button class="ghost danger" onclick={remove} disabled={modelNames.length <= 1}>Delete</button>
            </div>
          </details>
        </div>
      {/if}
    </div>

    {#if message}<div class="error-box">{message}</div>{/if}
    {#if app.validation.file_error}<div class="error-box">{app.validation.file_error}</div>{/if}
    {#if !isDefaults && app.validation.errors[selected]}
      <div class="error-box">{app.validation.errors[selected]}</div>
    {:else if !isDefaults && app.validation.problems?.[selected]}
      <div class="error-box warn">This model can be saved but not generated. {app.validation.problems[selected]}</div>
    {/if}

    <div class="editor-body">
      <SettingsEditor name={selected} />

      <div class="yaml card">
        <button class="ghost yaml-toggle" onclick={() => (showYaml = !showYaml)}>
          {showYaml ? "▾" : "▸"} Entry in models.yaml
        </button>
        {#if showYaml}
          <pre>{yamlPreview}</pre>
          <p class="muted small">
            Saved to <code>{app.info.models_path}</code>. The same datasets can be generated with
            <code>zen-europe --all --models_path {app.info.models_path}</code>.
          </p>
        {/if}
      </div>
    </div>
  </section>
</div>

<style>
  .layout {
    display: grid;
    grid-template-columns: 280px 1fr;
    height: 100%;
  }

  aside {
    border-right: 1px solid var(--border);
    background: var(--surface);
    display: flex;
    flex-direction: column;
    min-height: 0;
  }

  .aside-section {
    padding: 12px;
    border-bottom: 1px solid var(--border);
    display: flex;
    flex-direction: column;
    gap: 2px;
  }

  .aside-section h4 {
    margin-bottom: 4px;
    font-weight: 500;
    font-size: 12px;
  }

  .aside-section.grow {
    flex: 1;
    overflow: auto;
  }

  .aside-section.new {
    flex-direction: row;
    gap: 6px;
  }

  .aside-section.new input {
    flex: 1;
  }

  .name {
    display: flex;
    flex-direction: column;
    line-height: 1.25;
  }

  .name .small {
    font-weight: 400;
  }

  .dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    flex-shrink: 0;
  }

  .dot.bad {
    background: var(--critical);
  }

  .dot.warn {
    background: var(--warning);
  }

  .error-box.warn {
    border-left-color: var(--warning);
    background: var(--changed-wash);
  }

  .editor {
    overflow: auto;
    padding: 16px 24px 48px;
    display: flex;
    flex-direction: column;
    gap: 12px;
  }

  .editor-head {
    display: flex;
    align-items: flex-start;
    gap: 12px;
    flex-wrap: wrap;
  }

  .editor-head p {
    margin: 4px 0 0;
  }

  .title-block {
    display: flex;
    flex-direction: column;
    gap: 6px;
  }

  .title-block h2 {
    display: flex;
    align-items: center;
    gap: 6px;
  }

  .actions {
    flex-wrap: wrap;
  }

  .button-link,
  .button-like {
    border: 1px solid var(--border);
    background: var(--surface);
    border-radius: 6px;
    padding: 5px 12px;
    color: inherit;
    text-decoration: none;
    cursor: pointer;
    list-style: none;
  }

  .button-link:hover,
  .button-like:hover {
    background: var(--surface-2);
  }

  .menu {
    position: relative;
  }

  .menu summary::-webkit-details-marker {
    display: none;
  }

  .menu-items {
    position: absolute;
    right: 0;
    top: calc(100% + 4px);
    z-index: 10;
    display: flex;
    flex-direction: column;
    padding: 4px;
    min-width: 220px;
  }

  .menu-items button {
    text-align: left;
  }

  .editor-body {
    display: flex;
    flex-direction: column;
    gap: 12px;
    max-width: 1100px;
  }

  .yaml {
    padding: 4px 8px;
  }

  .yaml pre {
    margin: 4px 8px;
    font-family: var(--mono);
    font-size: 12.5px;
    overflow: auto;
  }

  .yaml p {
    margin: 4px 8px 8px;
  }

  @media (max-width: 800px) {
    .layout {
      grid-template-columns: 1fr;
      grid-template-rows: auto 1fr;
    }
    aside {
      max-height: 40vh;
      border-right: none;
      border-bottom: 1px solid var(--border);
    }
    .editor {
      padding: 16px;
    }
  }
</style>
