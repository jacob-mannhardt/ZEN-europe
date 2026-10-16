<script lang="ts">
  import type { CategorySchema, FieldSchema } from "../lib/api";
  import { app } from "../lib/store.svelte";
  import { deepMerge, DEFAULTS, formatValue, inheritedSettings, lineage, ownPatch, removeField, setField } from "../lib/settings";
  import FieldInput from "./FieldInput.svelte";

  let { name }: { name: string } = $props();

  let query = $state("");
  let onlyChanged = $state(false);
  let collapsed = $state<Record<string, boolean>>({});

  const catalog = $derived(app.catalog!);
  const inherited = $derived(inheritedSettings(catalog.base, app.doc, name));
  const patch = $derived(ownPatch(app.doc, name));
  const effective = $derived(deepMerge(inherited, patch));

  function patchTarget() {
    return name === DEFAULTS ? app.doc.defaults : app.doc.models[name].settings;
  }

  function change(category: string, field: string, value: unknown) {
    setField(patchTarget(), category, field, value, inherited[category]?.[field]);
  }

  function reset(category: string, field: string) {
    removeField(patchTarget(), category, field);
  }

  function isChanged(category: string, field: string): boolean {
    return patch[category] !== undefined && field in patch[category];
  }

  function visibleFields(category: CategorySchema): FieldSchema[] {
    const q = query.trim().toLowerCase();
    return category.fields.filter((f) => {
      if (onlyChanged && !isChanged(category.name, f.name)) return false;
      if (!q) return true;
      return (
        f.name.toLowerCase().includes(q) ||
        f.description.toLowerCase().includes(q) ||
        category.name.includes(q)
      );
    });
  }

  function changedIn(category: CategorySchema): number {
    return Object.keys(patch[category.name] ?? {}).length;
  }

  function isCollapsed(category: CategorySchema): boolean {
    if (query.trim() || onlyChanged) return false;
    return collapsed[category.name] ?? (category.advanced && !changedIn(category));
  }

  // where a value that is not changed here comes from
  function origin(category: string, field: string): string {
    if (name === DEFAULTS) return "";
    const ancestors = lineage(app.doc, name).slice(0, -1).reverse();
    for (const ancestor of ancestors) {
      const settings = app.doc.models[ancestor].settings[category];
      if (settings && field in settings) return `set by ${ancestor}`;
    }
    if (app.doc.defaults[category] && field in app.doc.defaults[category]) return "set by defaults";
    return "";
  }
</script>

<div class="toolbar row">
  <input type="search" placeholder="Search settings and explanations" bind:value={query} />
  <label class="row small">
    <input type="checkbox" bind:checked={onlyChanged} /> Only changed settings
  </label>
</div>

{#each catalog.schema.categories as category}
  {@const fields = visibleFields(category)}
  {#if fields.length}
    <div class="category card">
      <button
        class="category-head ghost"
        onclick={() => (collapsed[category.name] = !isCollapsed(category))}
        aria-expanded={!isCollapsed(category)}
      >
        <span class="chevron">{isCollapsed(category) ? "▸" : "▾"}</span>
        <h3>{category.name}</h3>
        {#if changedIn(category)}<span class="badge changed">{changedIn(category)} changed</span>{/if}
        {#if category.advanced}<span class="badge">advanced</span>{/if}
        <span class="secondary small desc">{category.description}</span>
      </button>

      {#if !isCollapsed(category)}
        <div class="fields">
          {#each fields as field (field.name)}
            {@const changed = isChanged(category.name, field.name)}
            {@const from = origin(category.name, field.name)}
            <div class="field" class:changed>
              <div class="label">
                <div class="row">
                  <code class="field-name">{field.name}</code>
                  {#if changed}
                    <button class="ghost small reset" onclick={() => reset(category.name, field.name)} title="Use the inherited value again">
                      reset
                    </button>
                  {/if}
                </div>
                <div class="secondary small">{field.description}</div>
                {#if changed}
                  <div class="muted small">
                    was <span class="mono">{formatValue(inherited[category.name]?.[field.name])}</span>
                  </div>
                {:else if from}
                  <div class="muted small">{from}</div>
                {/if}
              </div>
              <div class="input">
                <FieldInput
                  {field}
                  category={category.name}
                  value={effective[category.name]?.[field.name]}
                  onchange={(value) => change(category.name, field.name, value)}
                />
              </div>
            </div>
          {/each}
        </div>
      {/if}
    </div>
  {/if}
{/each}

<style>
  .toolbar {
    position: sticky;
    top: -16px;
    z-index: 5;
    background: var(--page);
    padding: 8px 0;
    flex-wrap: wrap;
  }

  .toolbar input[type="search"] {
    width: min(420px, 100%);
  }

  .category {
    overflow: visible;
  }

  .category-head {
    display: flex;
    align-items: baseline;
    gap: 8px;
    width: 100%;
    text-align: left;
    padding: 10px 14px;
    flex-wrap: wrap;
    white-space: normal;
  }

  .chevron {
    width: 12px;
    color: var(--muted);
  }

  .desc {
    flex-basis: 100%;
    padding-left: 20px;
  }

  .fields {
    border-top: 1px solid var(--grid);
  }

  .field {
    display: grid;
    grid-template-columns: minmax(0, 1fr) minmax(220px, 380px);
    gap: 16px;
    padding: 10px 14px 10px 34px;
    border-bottom: 1px solid var(--grid);
    border-left: 3px solid transparent;
  }

  .field:last-child {
    border-bottom: none;
  }

  .field.changed {
    border-left-color: var(--changed);
    background: color-mix(in srgb, var(--changed-wash) 50%, transparent);
  }

  .field-name {
    font-weight: 600;
  }

  .reset {
    color: var(--accent-ink);
  }

  .input {
    display: flex;
    align-items: flex-start;
    min-width: 0;
  }

  @media (max-width: 760px) {
    .field {
      grid-template-columns: 1fr;
      gap: 6px;
      padding-left: 14px;
    }
  }
</style>
