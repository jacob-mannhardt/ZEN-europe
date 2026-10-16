<script lang="ts">
  import type { FieldSchema, NamedOption } from "../lib/api";
  import { app } from "../lib/store.svelte";
  import MultiSelect from "./MultiSelect.svelte";

  let {
    field,
    category,
    value,
    onchange,
  }: { field: FieldSchema; category: string; value: unknown; onchange: (value: unknown) => void } = $props();

  let invalid = $state(false);

  // the list settings that add elements to the model, and those that remove them
  const ADDS = new Set([
    "set_conversion_technologies",
    "set_storage_technologies",
    "set_transport_technologies",
    "set_retrofitting_technologies",
    "set_carriers",
  ]);
  const REMOVES = new Set(["remove_technologies", "remove_sectors"]);

  // An add setting offers what the model does not contain yet, a remove
  // setting what it contains. The values of the setting itself stay offered,
  // so they can be deselected.
  const listOptions = $derived.by((): NamedOption[] | null => {
    const all = allListOptions;
    const structure = app.structure.value;
    if (!all || !structure || category !== "structure") return all;
    const selected = new Set((value as string[]) ?? []);
    const inModel = (name: string) =>
      field.name === "remove_sectors"
        ? name in structure.sectors
        : name in structure.technologies || name in structure.carriers;
    if (ADDS.has(field.name)) return all.filter((o) => selected.has(o.name) || !inModel(o.name));
    if (REMOVES.has(field.name)) return all.filter((o) => selected.has(o.name) || inModel(o.name));
    return all;
  });

  // the values a list setting picks from
  const allListOptions = $derived.by((): NamedOption[] | null => {
    const options = app.catalog!.options;
    switch (field.options) {
      case "nodes":
        return options.nodes.map((name) => ({ name, description: "" }));
      case "sectors":
        return options.sectors.map((s) => ({
          name: s.name,
          description:
            s.description.split("\n\n")[0] +
            (s.required_sectors.length ? ` Requires: ${s.required_sectors.join(", ")}.` : ""),
        }));
      case "elements":
        return Object.entries(options.elements)
          .flatMap(([type, entries]) => entries.map((e) => ({ ...e, description: `${type.replace("_", " ")}. ${e.description}` })))
          .sort((a, b) => a.name.toLowerCase().localeCompare(b.name.toLowerCase()));
      case null:
        return null;
      default:
        return options.elements[field.options] ?? null;
    }
  });

  function commitNumber(event: Event) {
    const input = event.currentTarget as HTMLInputElement;
    const parsed = Number(input.value);
    invalid = input.value.trim() === "" || !Number.isFinite(parsed) || (field.kind === "int" && !Number.isInteger(parsed));
    if (!invalid) onchange(parsed);
  }

  function commitText(event: Event) {
    onchange((event.currentTarget as HTMLInputElement).value);
  }

  function commitFreeList(event: Event) {
    const text = (event.currentTarget as HTMLInputElement).value;
    onchange(text.split(",").map((s) => s.trim()).filter(Boolean));
  }
</script>

{#if field.kind === "bool"}
  <label class="switch">
    <input type="checkbox" checked={!!value} onchange={(e) => onchange((e.currentTarget as HTMLInputElement).checked)} />
    <span class="track" aria-hidden="true"></span>
    <span class="small">{value ? "on" : "off"}</span>
  </label>
{:else if field.kind === "int" || field.kind === "float"}
  <input
    type="number"
    class:invalid
    step={field.kind === "int" ? 1 : "any"}
    value={value as number}
    onchange={commitNumber}
  />
{:else if field.kind === "choice"}
  <select value={String(value)} onchange={(e) => {
    const choice = field.choices!.find((c) => String(c) === (e.currentTarget as HTMLSelectElement).value);
    onchange(choice);
  }}>
    {#each field.choices ?? [] as choice}<option value={String(choice)}>{String(choice)}</option>{/each}
  </select>
{:else if category === "structure" && field.name === "energy_system"}
  <select value={String(value)} onchange={commitText}>
    {#each app.catalog!.options.energy_systems as option}<option value={option}>{option}</option>{/each}
  </select>
{:else if field.kind === "list" && listOptions}
  <MultiSelect options={listOptions} value={(value as string[]) ?? []} {onchange} />
{:else if field.kind === "list"}
  <input type="text" value={((value as string[]) ?? []).join(", ")} onchange={commitFreeList} placeholder="comma-separated" />
{:else}
  <input type="text" value={value as string} onchange={commitText} />
{/if}

<style>
  input[type="number"],
  input[type="text"],
  select {
    width: 100%;
  }

  input.invalid {
    border-color: var(--critical);
  }

  .switch {
    /* anchors the hidden checkbox, which the browser scrolls to on focus */
    position: relative;
    display: inline-flex;
    align-items: center;
    gap: 8px;
    cursor: pointer;
  }

  .switch input {
    position: absolute;
    left: 0;
    top: 0;
    opacity: 0;
    width: 1px;
    height: 1px;
  }

  .track {
    width: 34px;
    height: 20px;
    border-radius: 10px;
    background: var(--surface-3);
    border: 1px solid var(--border);
    position: relative;
    transition: background 0.15s;
  }

  .track::after {
    content: "";
    position: absolute;
    top: 2px;
    left: 2px;
    width: 14px;
    height: 14px;
    border-radius: 50%;
    background: white;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
    transition: transform 0.15s;
  }

  .switch input:checked + .track {
    background: var(--accent);
  }

  .switch input:checked + .track::after {
    transform: translateX(14px);
  }

  .switch input:focus-visible + .track {
    outline: 2px solid var(--accent);
    outline-offset: 2px;
  }
</style>
