<script lang="ts">
  import Diagram from "../components/Diagram.svelte";
  import type { Structure } from "../lib/api";
  import {
    carrierDiagram,
    carrierFlowDiagram,
    idIndex,
    LEGEND,
    sectorDiagram,
    sortNames,
    technologyDiagram,
    TECHNOLOGY_TYPES,
  } from "../lib/diagrams";
  import { DEFAULTS } from "../lib/settings";
  import { app, datasetOf, isDirty, openData } from "../lib/store.svelte";

  type Selection =
    | { kind: "overview" }
    | { kind: "sector"; name: string }
    | { kind: "technology"; name: string }
    | { kind: "carrier"; name: string };

  let selection = $state<Selection>({ kind: "overview" });
  let query = $state("");

  const model = $derived(app.selected);
  // the structure of the selected model is kept up to date by the store
  const structure = $derived<Structure | null>(app.structure.value);
  const error = $derived(app.structure.error);
  const loading = $derived(app.structure.loading);

  // an element that the changed settings removed is no longer shown
  $effect(() => {
    if (!structure) return;
    if (
      (selection.kind === "technology" && !structure.technologies[selection.name]) ||
      (selection.kind === "carrier" && !structure.carriers[selection.name]) ||
      (selection.kind === "sector" && !structure.sectors[selection.name])
    ) {
      selection = { kind: "overview" };
    }
  });

  const index = $derived(structure ? idIndex(structure) : new Map());
  const dataset = $derived(model === DEFAULTS ? undefined : datasetOf(model));

  function onNodeClick(id: string) {
    const element = index.get(id);
    if (element) selection = { kind: element.kind, name: element.name };
  }

  function matches(name: string): boolean {
    return name.toLowerCase().includes(query.trim().toLowerCase());
  }

  function techsOfType(type: string): string[] {
    if (!structure) return [];
    return sortNames(Object.keys(structure.technologies).filter((n) => structure!.technologies[n].type === type && matches(n)));
  }

  function select(kind: "technology" | "carrier" | "sector", name: string) {
    selection = { kind, name };
  }

  function isActive(kind: string, name: string): boolean {
    return selection.kind === kind && "name" in selection && selection.name === name;
  }

  function counts(s: Structure) {
    const types = Object.values(s.technologies).map((t) => t.type);
    return [
      { label: "Countries", value: s.nodes.length },
      { label: "Sectors", value: Object.keys(s.sectors).length },
      { label: "Carriers", value: Object.keys(s.carriers).length },
      ...Object.entries(TECHNOLOGY_TYPES).map(([type, label]) => ({
        label,
        value: types.filter((t) => t === type).length,
      })),
    ];
  }
</script>

{#snippet links(names: string[], kind: "technology" | "carrier" | "sector")}
  {#if names.length === 0}
    <span class="muted">none</span>
  {:else}
    {#each sortNames(names) as name, i}
      {@const known = structure && (kind === "sector" ? structure.sectors[name] : kind === "carrier" ? structure.carriers[name] : structure.technologies[name])}
      {#if i > 0}, {/if}
      {#if known}
        <button class="link" onclick={() => select(kind, name)}>{name}</button>
      {:else}
        <span class="muted" title="Not part of this model">{name}</span>
      {/if}
    {/each}
  {/if}
{/snippet}

{#snippet dataButton(name: string)}
  {#if dataset}
    <button onclick={() => openData(dataset.name, null, name)}>Show data of {name}</button>
  {:else if model !== DEFAULTS}
    <span class="muted small">Generate the model to explore its data.</span>
  {/if}
{/snippet}

<div class="layout">
  <aside>
    <div class="aside-head">
      <label class="small secondary" for="structure-model">Model</label>
      <select id="structure-model" bind:value={app.selected}>
        <option value={DEFAULTS}>defaults (configuration file)</option>
        {#each Object.keys(app.doc.models) as name}<option value={name}>{name}</option>{/each}
      </select>
      {#if isDirty()}<span class="muted small">Includes unsaved changes.</span>{/if}
      <input type="search" placeholder="Filter elements" bind:value={query} />
    </div>
    {#if structure}
      <div class="nav">
        <button class="list-button" class:active={selection.kind === "overview"} onclick={() => (selection = { kind: "overview" })}>
          Overview
        </button>
        <h4>Sectors</h4>
        {#each Object.keys(structure.sectors).filter(matches) as name}
          <button class="list-button" class:active={isActive("sector", name)} onclick={() => select("sector", name)}>{name}</button>
        {/each}
        {#each Object.entries(TECHNOLOGY_TYPES) as [type, label]}
          {@const names = techsOfType(type)}
          {#if names.length}
            <h4>{label}</h4>
            {#each names as name}
              <button class="list-button" class:active={isActive("technology", name)} onclick={() => select("technology", name)}>{name}</button>
            {/each}
          {/if}
        {/each}
        <h4>Carriers</h4>
        {#each sortNames(Object.keys(structure.carriers)).filter(matches) as name}
          <button class="list-button" class:active={isActive("carrier", name)} onclick={() => select("carrier", name)}>{name}</button>
        {/each}
      </div>
    {/if}
  </aside>

  <section class="content">
    {#if error}
      <div class="error-box">The structure of this model cannot be built: {error}</div>
    {/if}
    {#if structure && Object.keys(structure.missing_carriers).length}
      <div class="error-box">
        This model cannot be generated: technologies use carriers that are not part of it.
        {#each Object.entries(structure.missing_carriers) as [carrier, techs]}
          <div><strong>{carrier}</strong> is used by {techs.join(", ")}</div>
        {/each}
      </div>
    {/if}
    {#if loading && !structure}
      <div class="empty">Building the structure …</div>
    {:else if structure}
      {#if selection.kind === "overview"}
        <h2>Structure of {model === DEFAULTS ? "the default configuration" : model}</h2>
        <div class="tiles">
          {#each counts(structure) as tile}
            <div class="tile card"><div class="tile-value">{tile.value}</div><div class="secondary small">{tile.label}</div></div>
          {/each}
        </div>
        {#if structure.compared_to_base.added.length || structure.compared_to_base.removed.length}
          <div class="info-box">
            Compared to the configuration file:
            {#if structure.compared_to_base.removed.length}
              <div><strong>removed</strong> {structure.compared_to_base.removed.join(", ")}</div>
            {/if}
            {#if structure.compared_to_base.added.length}
              <div><strong>added</strong> {structure.compared_to_base.added.join(", ")}</div>
            {/if}
          </div>
        {/if}
        <p class="secondary">
          <strong>Countries:</strong> {structure.nodes.join(", ")}
        </p>
        <h3>Carrier flows</h3>
        <p class="secondary small">
          An arrow from carrier A to carrier B means that at least one technology converts A into B. Click a
          carrier to see its technologies. Ctrl + scroll to zoom, drag to pan.
        </p>
        <Diagram source={carrierFlowDiagram(structure)} onnodeclick={onNodeClick} height="70vh" />
      {:else if selection.kind === "sector"}
        {@const sectorName = selection.name}
        {@const s = structure}
        {@const sector = structure.sectors[sectorName]}
        <h2>Sector {selection.name}</h2>
        <p class="secondary">{sector.description}</p>
        <p><strong>Requires:</strong> {@render links(sector.required_sectors, "sector")}</p>
        <h3>Carrier flows</h3>
        <p class="secondary small">{LEGEND} Dashed elements belong to another sector.</p>
        <Diagram source={sectorDiagram(selection.name, structure)} onnodeclick={onNodeClick} height="60vh" />
        <h3>Technologies</h3>
        <p class="secondary small">Technologies that are also declared by another sector are only part of the model when all of their sectors are included.</p>
        <table class="data">
          <thead><tr><th>Technology</th><th>Type</th><th>Input</th><th>Output</th><th>Also in</th></tr></thead>
          <tbody>
            {#each sortNames(sector.elements.filter((e) => e in s.technologies)) as name}
              {@const tech = structure.technologies[name]}
              <tr>
                <td><button class="link" onclick={() => select("technology", name)}>{name}</button></td>
                <td>{TECHNOLOGY_TYPES[tech.type].split(" ")[0]}</td>
                <td>{@render links(tech.input_carrier ?? tech.reference_carrier, "carrier")}</td>
                <td>{@render links(tech.output_carrier ?? tech.reference_carrier, "carrier")}</td>
                <td>{@render links(tech.sectors.filter((other) => other !== sectorName), "sector")}</td>
              </tr>
            {/each}
          </tbody>
        </table>
      {:else if selection.kind === "technology"}
        {@const techName = selection.name}
        {@const tech = structure.technologies[techName]}
        <div class="row head">
          <h2>{selection.name}</h2>
          <span class="badge">{TECHNOLOGY_TYPES[tech.type]}</span>
          <span class="spacer"></span>
          {@render dataButton(selection.name)}
        </div>
        <p class="secondary small">{LEGEND} The reference carrier, in which the capacity is measured, has a thick border.</p>
        <Diagram source={technologyDiagram(selection.name, structure)} onnodeclick={onNodeClick} />
        <dl>
          <dt>Sectors</dt><dd>{@render links(tech.sectors, "sector")}</dd>
          <dt>Reference carrier</dt><dd>{@render links(tech.reference_carrier, "carrier")}</dd>
          {#if tech.input_carrier}
            <dt>Input carriers</dt><dd>{@render links(tech.input_carrier, "carrier")}</dd>
            <dt>Output carriers</dt><dd>{@render links(tech.output_carrier ?? [], "carrier")}</dd>
          {/if}
          {#if tech.base_technology}
            <dt>Base technology</dt><dd>{@render links([tech.base_technology], "technology")}</dd>
            <dt>Retrofit reference carrier</dt><dd>{@render links(tech.retrofit_reference_carrier ?? [], "carrier")}</dd>
          {/if}
          {#if app.catalog}
            {@const doc = Object.values(app.catalog.options.elements).flat().find((e) => e.name === techName)?.description}
            {#if doc}<dt>Description</dt><dd>{doc}</dd>{/if}
          {/if}
        </dl>
      {:else if selection.kind === "carrier"}
        {@const carrier = structure.carriers[selection.name]}
        <div class="row head">
          <h2>{selection.name}</h2>
          <span class="badge">Carrier</span>
          <span class="spacer"></span>
          {@render dataButton(selection.name)}
        </div>
        <dl>
          <dt>Sectors</dt><dd>{@render links(carrier.sectors, "sector")}</dd>
          <dt>Produced by</dt><dd>{@render links(carrier.produced_by, "technology")}</dd>
          <dt>Consumed by</dt><dd>{@render links(carrier.consumed_by, "technology")}</dd>
          {#if carrier.stored_by.length}<dt>Stored by</dt><dd>{@render links(carrier.stored_by, "technology")}</dd>{/if}
          {#if carrier.transported_by.length}<dt>Transported by</dt><dd>{@render links(carrier.transported_by, "technology")}</dd>{/if}
        </dl>
        <h3>Technologies of {selection.name}</h3>
        <p class="secondary small">{LEGEND}</p>
        <Diagram source={carrierDiagram(selection.name, structure)} onnodeclick={onNodeClick} height="60vh" />
      {/if}
    {/if}
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

  .content p {
    margin: 0;
  }

  .tiles {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
    gap: 8px;
  }

  .tile {
    padding: 10px 14px;
  }

  .tile-value {
    font-size: 24px;
    font-weight: 600;
  }

  .head {
    flex-wrap: wrap;
  }

  dl {
    display: grid;
    grid-template-columns: max-content 1fr;
    gap: 6px 16px;
    margin: 0;
  }

  dt {
    color: var(--ink-2);
    font-weight: 600;
  }

  dd {
    margin: 0;
  }

  .link {
    border: none;
    background: none;
    padding: 0;
    color: var(--accent-ink);
    text-decoration: underline;
    text-decoration-color: color-mix(in srgb, var(--accent-ink) 35%, transparent);
    text-underline-offset: 2px;
  }

  .link:hover {
    background: none !important;
    text-decoration-color: currentColor;
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
