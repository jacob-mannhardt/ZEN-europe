<script lang="ts">
  import DataPlot from "../components/DataPlot.svelte";
  import Markdown from "../components/Markdown.svelte";
  import {
    api,
    type AttributeChange,
    type AttributeRow,
    type Comparison,
    type DataFile,
    type DatasetOverview,
    DEFAULTS_REFERENCE,
    type ElementDetails,
  } from "../lib/api";
  import { sortNames } from "../lib/diagrams";
  import { app, generateReference } from "../lib/store.svelte";

  const TYPES: Record<string, string> = {
    energy_system: "Energy system",
    carrier: "Carriers",
    conversion_technology: "Conversion technologies",
    retrofitting_technology: "Retrofitting technologies",
    storage_technology: "Storage technologies",
    transport_technology: "Transport technologies",
  };

  let overview = $state<DatasetOverview | null>(null);
  let details = $state<ElementDetails | null>(null);
  let attribute = $state<string | null>(null);
  let file = $state<string | null>(null);
  let fileData = $state<DataFile | null>(null);
  let loadingFile = $state(false);
  let error = $state<string | null>(null);
  let query = $state("");
  let onlyData = $state(false);

  // ---------- comparison with a reference dataset ----------
  let comparison = $state<Comparison | null>(null);
  let reference = $state("");
  let comparing = $state(false);
  let onlyChanged = $state(false);

  // a new dataset is compared with the default reference of the backend, a
  // dataset generated without any changed settings
  $effect(() => {
    const name = app.data.dataset;
    // compare again once the defaults have been generated
    void app.reference.generated;
    comparison = null;
    reference = "";
    if (name) compareWith(name, undefined);
  });

  const referenceLabel = $derived(comparison?.reference_label ?? reference);
  const referenceJob = $derived(app.reference.job);

  async function compareWith(name: string, ref: string | undefined) {
    comparing = true;
    try {
      const result = await api.compare(name, ref);
      if (app.data.dataset !== name) return;
      comparison = result;
      reference = result.reference ?? "";
    } catch (e) {
      error = (e as Error).message;
    } finally {
      comparing = false;
    }
  }

  function onReferenceChange(event: Event) {
    const ref = (event.currentTarget as HTMLSelectElement).value;
    comparison = null;
    reference = ref;
    if (ref && app.data.dataset) compareWith(app.data.dataset, ref);
  }

  function elementChange(type: string, name: string) {
    return comparison?.elements[`${type}/${name}`];
  }

  const attributeChanges = $derived<Record<string, AttributeChange>>(
    details ? (elementChange(details.type, details.name)?.attributes ?? {}) : {},
  );
  const isNewElement = $derived(details ? elementChange(details.type, details.name)?.status === "added" : false);
  const change = $derived(attribute ? attributeChanges[attribute] : undefined);

  // the dataset to show: the requested one, else the newest
  $effect(() => {
    if (!app.data.dataset && app.datasets.length) app.data.dataset = app.datasets[0].name;
  });

  $effect(() => {
    const name = app.data.dataset;
    overview = null;
    details = null;
    if (!name) return;
    api
      .dataset(name)
      .then((result) => {
        overview = result;
        // an element given without its type, e.g. from the structure view
        if (app.data.element && !app.data.elementType) {
          app.data.elementType =
            Object.entries(result.elements).find(([, names]) => names.includes(app.data.element!))?.[0] ?? null;
          if (!app.data.elementType) {
            error = `'${app.data.element}' is not part of the dataset '${name}'.`;
            app.data.element = null;
          }
        }
        if (!app.data.element) {
          app.data.elementType = "energy_system";
          app.data.element = "energy_system";
        }
      })
      .catch((e) => (error = (e as Error).message));
  });

  $effect(() => {
    const { dataset, elementType, element } = app.data;
    details = null;
    attribute = null;
    if (!dataset || !elementType || !element || !overview) return;
    api
      .element(dataset, elementType, element)
      .then((result) => {
        details = result;
        error = null;
        expanded = {};
        // only attributes with data files have a panel; the others expand
        // in the table
        selectAttribute(result.attributes.find((a) => a.files.length) ?? null);
      })
      .catch((e) => (error = (e as Error).message));
  });

  // An attribute with a yearly variation is shown in every year: its default
  // value or its data per node times the factor of each year (YEARLY). Data
  // along time cannot be combined with the factor, so then the data and the
  // factor are shown one below the other (BOTH).
  const YEARLY = "__yearly__";
  const BOTH = "__both__";
  let yearlyData = $state<DataFile | null>(null);
  let yearlySource = $state<"data" | "default" | null>(null);
  let separate = $state(false);
  let factorData = $state<DataFile | null>(null);

  async function selectAttribute(row: AttributeRow | null) {
    attribute = row?.name ?? null;
    yearlyData = null;
    yearlySource = null;
    separate = false;
    const { dataset, elementType, element } = app.data;
    if (!row || !dataset || !elementType || !element) return selectFile(null);
    if (!row.files.includes(`${row.name}_yearly_variation`)) return selectFile(row.files[0] ?? null);

    file = null;
    fileData = null;
    loadingFile = true;
    try {
      const result = await api.yearly(dataset, elementType, element, row.name);
      if (attribute !== row.name) return;
      if (result.kind === "separate") {
        separate = true;
        await selectFile(BOTH);
      } else {
        yearlyData = result;
        yearlySource = "source" in result ? (result.source ?? null) : null;
        await selectFile(YEARLY);
      }
    } catch {
      // the files can still be shown on their own
      if (attribute === row.name) await selectFile(row.files[0] ?? null);
    } finally {
      loadingFile = false;
    }
  }

  async function selectFile(name: string | null) {
    file = name;
    fileData = null;
    factorData = null;
    const { dataset, elementType, element } = app.data;
    if (!name || !dataset || !elementType || !element) return;
    if (name === YEARLY) {
      fileData = yearlyData;
      return;
    }
    loadingFile = true;
    try {
      if (name === BOTH) {
        const [data, factor] = await Promise.all([
          api.data(dataset, elementType, element, attribute!),
          api.data(dataset, elementType, element, `${attribute}_yearly_variation`),
        ]);
        if (file === name) [fileData, factorData] = [data, factor];
      } else {
        const result = await api.data(dataset, elementType, element, name);
        if (file === name) fileData = result;
      }
    } catch (e) {
      error = (e as Error).message;
    } finally {
      loadingFile = false;
    }
  }

  // the tabs of an attribute: the combined views first, then every file
  function views(row: AttributeRow): string[] {
    if (yearlyData) return [YEARLY, ...row.files];
    if (separate) return [BOTH, ...row.files];
    return row.files;
  }

  let showSources = $state(false);
  // attributes with only a default value, expanded in the table
  let expanded = $state<Record<string, boolean>>({});

  function selectElement(elementType: string, element: string) {
    app.data.elementType = elementType;
    app.data.element = element;
  }

  const row = $derived(details?.attributes.find((a) => a.name === attribute) ?? null);
  const shownAttributes = $derived(
    details?.attributes.filter(
      (a) => (!onlyData || a.files.length) && (!onlyChanged || a.name in attributeChanges),
    ) ?? [],
  );

  function shownInNav(type: string, name: string): boolean {
    return matches(name) && (!onlyChanged || !!elementChange(type, name));
  }

  function unitOf(row: AttributeRow | null, fileName: string | null): string {
    if (!row) return "";
    if (fileName?.endsWith("_yearly_variation")) return "factor";
    return row.unit ?? "";
  }

  function fileLabel(row: AttributeRow, name: string): string {
    if (name === YEARLY) return "values over the years";
    if (name === BOTH) return "data and yearly variation";
    if (name === row.name) return "data";
    return name.slice(row.name.length + 1).replace(/_/g, " ");
  }

  function format(value: unknown): string {
    if (value === null || value === undefined) return "";
    if (Array.isArray(value)) return value.join(", ");
    if (typeof value === "number") return Number(value.toPrecision(5)).toLocaleString("en-US");
    return String(value);
  }

  function matches(name: string) {
    return name.toLowerCase().includes(query.trim().toLowerCase());
  }
</script>

{#snippet changeNote(change: AttributeChange)}
  <div class="change-box small">
    Differs from <strong>{referenceLabel}</strong>:
    {#if change.default && JSON.stringify(change.default[0]) !== JSON.stringify(change.default[1])}
      default value {format(change.default[0]) || "–"} → {format(change.default[1]) || "–"}{Object.keys(change.files).length ? ";" : "."}
    {:else if change.entry_changed && !Object.keys(change.files).length}
      the entry in attributes.yaml (e.g. its unit) changed.
    {/if}
    {#each Object.entries(change.files) as [f, status], i}
      {i ? ", " : ""}<code>{f}.csv</code> {status === "changed" ? "has other values" : status === "added" ? "is new" : `exists only in ${referenceLabel}`}{i === Object.keys(change.files).length - 1 ? "." : ""}
    {/each}
  </div>
{/snippet}

{#if app.datasets.length === 0}
  <div class="empty">
    No dataset has been generated yet. Configure a model and generate it in
    <button class="ghost" onclick={() => (app.view = "generate")}>Generate &amp; download</button>.
  </div>
{:else}
  <div class="layout">
    <aside>
      <div class="aside-head">
        <label class="small secondary" for="data-dataset">Dataset</label>
        <select id="data-dataset" bind:value={app.data.dataset} onchange={() => { app.data.element = null; app.data.elementType = null; }}>
          {#each app.datasets as dataset}<option value={dataset.name}>{dataset.name}</option>{/each}
        </select>
        <label class="small secondary" for="data-reference">Highlight changes compared to</label>
        <select id="data-reference" value={reference} onchange={onReferenceChange}>
          <option value="">— nothing —</option>
          {#if app.reference.exists}
            <option value={DEFAULTS_REFERENCE}>ZEN-europe defaults</option>
          {/if}
          {#each app.datasets.filter((d) => d.name !== app.data.dataset) as dataset}
            <option value={dataset.name}>{dataset.name}</option>
          {/each}
        </select>
        {#if comparing}
          <span class="muted small">Comparing …</span>
        {:else if comparison?.reference}
          <span class="muted small">
            {Object.keys(comparison.elements).length} elements differ
            {#if comparison.removed.length}· {comparison.removed.length} only in {referenceLabel}{/if}
          </span>
          <label class="row small"><input type="checkbox" bind:checked={onlyChanged} /> only changed</label>
        {/if}
        {#if referenceJob}
          <span class="muted small">
            {referenceJob.status === "running" ? "Generating" : "Queued:"} the ZEN-europe defaults to compare with.
            This usually takes a few seconds.
          </span>
        {:else if !app.reference.exists}
          <span class="muted small">To highlight what differs from the defaults, they have to be generated once.</span>
          <button class="small" onclick={generateReference}>Generate the defaults</button>
        {:else if app.reference.outdated && reference === DEFAULTS_REFERENCE}
          <span class="muted small">The defaults were generated with another version of ZEN-europe or of the configuration.</span>
          <button class="small" onclick={generateReference}>Regenerate the defaults</button>
        {/if}
        <input type="search" placeholder="Filter elements" bind:value={query} />
      </div>
      {#if overview}
        <div class="nav">
          {#if shownInNav("energy_system", "energy_system")}
            {@const c = elementChange("energy_system", "energy_system")}
            <button
              class="list-button"
              class:active={app.data.elementType === "energy_system"}
              onclick={() => selectElement("energy_system", "energy_system")}
            >energy_system{#if c}<span class="spacer"></span><span class="mark changed" title="Differs from {referenceLabel}"></span>{/if}</button>
          {/if}
          {#each Object.entries(overview.elements) as [type, names]}
            {@const shown = sortNames(names).filter((n) => shownInNav(type, n))}
            {#if shown.length}
              <h4>{TYPES[type] ?? type} <span class="muted">{names.length}</span></h4>
              {#each shown as name}
                {@const c = elementChange(type, name)}
                <button
                  class="list-button"
                  class:active={app.data.elementType === type && app.data.element === name}
                  onclick={() => selectElement(type, name)}
                >
                  {name}
                  {#if c}
                    <span class="spacer"></span>
                    {#if c.status === "added"}
                      <span class="badge changed" title="Not in {referenceLabel}">new</span>
                    {:else}
                      <span class="mark changed" title="{Object.keys(c.attributes).length} attributes differ from {referenceLabel}"></span>
                    {/if}
                  {/if}
                </button>
              {/each}
            {/if}
          {/each}
          {#if comparison?.removed.length && !query}
            <h4>Only in {comparison.reference}</h4>
            {#each comparison.removed as key}
              <div class="removed small">{key.split("/")[1]}</div>
            {/each}
          {/if}
        </div>
      {/if}
    </aside>

    <section class="content">
      {#if error}<div class="error-box">{error}</div>{/if}
      {#if overview && details}
        <div class="row head">
          <h2>{details.name}</h2>
          <span class="badge">{TYPES[details.type] ?? details.type}</span>
          <span class="spacer"></span>
          <span class="muted small">{overview.nodes.length} nodes · {overview.edges.length} edges · dataset {overview.name}</span>
        </div>

        <div class="split" class:single={!row || !row.files.length}>
          <div class="attributes card">
            <div class="row attr-head">
              <h3>Attributes</h3>
              <span class="spacer"></span>
              <label class="row small"><input type="checkbox" bind:checked={onlyData} /> only with data files</label>
            </div>
            {#if isNewElement}
              <div class="info-box small">This element is not part of {referenceLabel}.</div>
            {/if}
            <div class="table-scroll">
              <table class="data">
                <thead><tr><th>Attribute</th><th class="num">Default</th><th>Unit</th></tr></thead>
                <tbody>
                  {#each shownAttributes as a (a.name)}
                    {@const c = attributeChanges[a.name]}
                    {@const hasData = a.files.length > 0}
                    {@const expandable = !hasData && (!!c || a.has_sources || !!a.extra)}
                    <tr
                      class:clickable={hasData || expandable}
                      class:selected={hasData && a.name === attribute}
                      class:changed={!!c}
                      title={c ? `Differs from ${referenceLabel}` : undefined}
                      onclick={() => (hasData ? selectAttribute(a) : expandable && (expanded[a.name] = !expanded[a.name]))}
                    >
                      <td>
                        {#if expandable}<span class="caret">{expanded[a.name] ? "▾" : "▸"}</span>{/if}
                        <code>{a.name}</code>
                        {#if a.files.length}<span class="badge" title="Has data files">{a.files.length} file{a.files.length > 1 ? "s" : ""}</span>{/if}
                        {#if c && Object.keys(c.files).length}<span class="badge changed" title="Data files that differ from {referenceLabel}">data changed</span>{/if}
                      </td>
                      <td class="num">
                        {format(a.default_value)}
                        {#if c?.default && JSON.stringify(c.default[0]) !== JSON.stringify(c.default[1])}
                          <div class="muted small">was {format(c.default[0]) || "–"}</div>
                        {/if}
                      </td>
                      <td class="secondary">{a.unit ?? ""}</td>
                    </tr>
                    {#if expandable && expanded[a.name]}
                      <tr class="inline">
                        <td colspan="3">
                          {#if c}{@render changeNote(c)}{/if}
                          {#if a.extra}<pre class="extra">{JSON.stringify(a.extra, null, 2)}</pre>{/if}
                          {#if details.sources[a.name]}<Markdown text={details.sources[a.name]} />{/if}
                        </td>
                      </tr>
                    {/if}
                  {/each}
                </tbody>
              </table>
            </div>
          </div>

          {#if row && row.files.length}
          <div class="detail card">
              <div class="row detail-head">
                <h3><code>{row.name}</code></h3>
                <span class="spacer"></span>
                {#if row.default_value !== null && row.default_value !== undefined}
                  <span class="secondary">default <strong>{format(row.default_value)}</strong> {row.unit ?? ""}</span>
                {/if}
              </div>
              {#if change}{@render changeNote(change)}{/if}
              {#if row.extra}
                <pre class="extra">{JSON.stringify(row.extra, null, 2)}</pre>
              {/if}
              {#if views(row).length > 1}
                <div class="row files" role="tablist">
                  {#each views(row) as f}
                    <button class="small" class:active={f === file} role="tab" aria-selected={f === file} onclick={() => selectFile(f)}>
                      {fileLabel(row, f)}
                      {#if change?.files[f]}<span class="mark changed" title="Differs from {referenceLabel}"></span>{/if}
                    </button>
                  {/each}
                </div>
              {/if}
              {#if loadingFile && !file}
                <div class="empty">Loading …</div>
              {:else if file === BOTH}
                <h4>Data</h4>
                <div class="muted small"><code>{row.name}.csv</code></div>
                {#if loadingFile}
                  <div class="empty">Loading …</div>
                {:else}
                  {#if fileData?.kind === "series"}
                    {#key fileData}
                      <DataPlot data={fileData} unit={row.unit ?? ""} nodes={overview.nodes} edges={overview.edges} />
                    {/key}
                  {/if}
                  <h4>Yearly variation</h4>
                  <div class="muted small">
                    <code>{row.name}_yearly_variation.csv</code> · the factor ZEN-garden multiplies the data with in each year
                  </div>
                  {#if factorData?.kind === "series"}
                    {#key factorData}
                      <DataPlot data={factorData} unit="factor" nodes={overview.nodes} edges={overview.edges} />
                    {/key}
                  {/if}
                {/if}
              {:else if file}
                <div class="muted small">
                  {#if file === YEARLY}
                    {yearlySource === "default" ? "The default value" : `The values of ${row.name}.csv`} times the yearly
                    variation in <code>{row.name}_yearly_variation.csv</code>, as ZEN-garden uses them in each year.
                  {:else}
                    <code>{file}.csv</code>{#if file.endsWith("_yearly_variation")} · the factor ZEN-garden multiplies the value with in each year{/if}
                  {/if}
                </div>
                {#if loadingFile}
                  <div class="empty">Loading …</div>
                {:else if fileData?.kind === "series"}
                  {#key fileData}
                    <DataPlot data={fileData} unit={unitOf(row, file)} nodes={overview.nodes} edges={overview.edges} />
                  {/key}
                {:else if fileData?.kind === "table"}
                  <div class="table-scroll">
                    <table class="data">
                      <thead><tr>{#each fileData.columns as c}<th>{c}</th>{/each}</tr></thead>
                      <tbody>{#each fileData.rows as r}<tr>{#each r as v}<td>{format(v)}</td>{/each}</tr>{/each}</tbody>
                    </table>
                  </div>
                {/if}
              {/if}

              <div class="sources-title">
                {#if details.sources[row.name]}
                  <button class="ghost small" onclick={() => (showSources = !showSources)} aria-expanded={showSources}>
                    {showSources ? "▾" : "▸"} Sources and citations
                  </button>
                  {#if showSources}
                    <Markdown text={details.sources[row.name]} />
                  {/if}
                {:else}
                  <p class="muted small">No source is recorded for this attribute; it keeps the default of ZEN-creator.</p>
                {/if}
              </div>
          </div>
          {/if}
        </div>
      {:else if !error}
        <div class="empty">Loading …</div>
      {/if}
    </section>
  </div>
{/if}

<style>
  .layout {
    display: grid;
    grid-template-columns: 260px 1fr;
    height: 100%;
  }

  aside {
    border-right: 1px solid var(--border);
    background: var(--surface);
    display: flex;
    flex-direction: column;
    min-height: 0;
  }

  .aside-head {
    padding: 12px;
    display: flex;
    flex-direction: column;
    gap: 6px;
    border-bottom: 1px solid var(--border);
  }

  .nav {
    overflow: auto;
    padding: 8px 12px 24px;
  }

  .nav h4 {
    margin: 12px 0 4px 8px;
    font-size: 12px;
    font-weight: 500;
    color: var(--muted);
  }

  .content {
    overflow: auto;
    padding: 16px 24px 48px;
    display: flex;
    flex-direction: column;
    gap: 12px;
  }

  .head {
    flex-wrap: wrap;
  }

  .split {
    display: grid;
    grid-template-columns: minmax(340px, 480px) minmax(0, 1fr);
    gap: 12px;
    align-items: start;
  }

  .attributes {
    position: sticky;
    top: 0;
  }

  .attr-head,
  .detail-head {
    padding: 10px 12px;
    flex-wrap: wrap;
  }

  .table-scroll {
    max-height: calc(100vh - 220px);
    overflow: auto;
  }

  .mark {
    display: inline-block;
    width: 8px;
    height: 8px;
    border-radius: 50%;
    flex-shrink: 0;
    margin-left: 4px;
  }

  .mark.changed {
    background: var(--changed);
  }

  .removed {
    padding: 2px 8px;
    color: var(--muted);
    text-decoration: line-through;
  }

  tr.changed td {
    background: color-mix(in srgb, var(--changed-wash) 60%, transparent);
  }

  tr.changed td:first-child {
    box-shadow: inset 3px 0 0 var(--changed);
  }

  tr.changed.selected td {
    background: var(--accent-wash);
  }

  .split.single {
    grid-template-columns: minmax(340px, 640px);
  }

  .caret {
    display: inline-block;
    width: 12px;
    color: var(--muted);
  }

  tr.inline td {
    background: var(--surface-2);
    display: table-cell;
  }

  tr.inline td > * + * {
    margin-top: 8px;
  }

  .change-box {
    background: var(--changed-wash);
    border-left: 3px solid var(--changed);
    padding: 6px 10px;
    border-radius: 4px;
  }

  .attributes .info-box {
    margin: 0 12px 8px;
  }

  .attributes td:first-child code {
    overflow-wrap: anywhere;
  }

  .attributes td.secondary {
    overflow-wrap: anywhere;
    min-width: 60px;
  }

  .detail {
    padding: 0 14px 14px;
    display: flex;
    flex-direction: column;
    gap: 8px;
    min-width: 0;
  }

  .detail-head {
    padding: 10px 0 0;
  }

  .extra {
    font-family: var(--mono);
    font-size: 12px;
    background: var(--surface-2);
    padding: 8px;
    border-radius: 6px;
    overflow: auto;
    max-height: 240px;
    margin: 0;
  }

  .files {
    flex-wrap: wrap;
  }

  .files button.active {
    background: var(--accent-wash);
    border-color: var(--accent);
  }

  .sources-title {
    margin-top: 12px;
    padding-top: 10px;
    border-top: 1px solid var(--grid);
  }

  @media (max-width: 1100px) {
    .split {
      grid-template-columns: 1fr;
    }
    .attributes {
      position: static;
    }
    .table-scroll {
      max-height: 360px;
    }
  }

  @media (max-width: 800px) {
    .layout {
      grid-template-columns: 1fr;
      grid-template-rows: auto 1fr;
    }
    aside {
      max-height: 35vh;
      border-right: none;
      border-bottom: 1px solid var(--border);
    }
    .content {
      padding: 16px;
    }
  }
</style>
