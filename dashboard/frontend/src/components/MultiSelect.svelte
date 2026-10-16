<script lang="ts">
  import type { NamedOption } from "../lib/api";

  let {
    options,
    value,
    onchange,
  }: { options: NamedOption[]; value: string[]; onchange: (value: string[]) => void } = $props();

  let open = $state(false);
  let query = $state("");
  let root: HTMLDivElement;

  const filtered = $derived(
    options.filter(
      (o) =>
        o.name.toLowerCase().includes(query.toLowerCase()) ||
        o.description.toLowerCase().includes(query.toLowerCase()),
    ),
  );
  // values that are not offered, e.g. an element that no longer exists
  const unknown = $derived(value.filter((v) => !options.some((o) => o.name === v)));

  function toggle(name: string) {
    // keep the order of the current list, so that toggling a value back
    // restores the inherited list exactly
    onchange(value.includes(name) ? value.filter((v) => v !== name) : [...value, name]);
  }

  function onWindowClick(event: MouseEvent) {
    if (open && root && !root.contains(event.target as Node)) open = false;
  }
</script>

<svelte:window onclick={onWindowClick} />

<div class="multi" bind:this={root}>
  <button class="summary" onclick={() => (open = !open)} aria-expanded={open}>
    {#if value.length === 0}
      <span class="muted">none</span>
    {:else if value.length === options.length && !unknown.length}
      <span>all {options.length}</span>
    {:else}
      <span class="chips">
        {#each value.slice(0, 8) as v}<span class="chip" class:unknown={unknown.includes(v)}>{v}</span>{/each}
        {#if value.length > 8}<span class="muted small">+{value.length - 8}</span>{/if}
      </span>
    {/if}
    <span class="caret">▾</span>
  </button>

  {#if open}
    <div class="popup card">
      <div class="row popup-head">
        <input type="search" placeholder="Filter" bind:value={query} />
        <button class="small" onclick={() => onchange(options.map((o) => o.name))}>All</button>
        <button class="small" onclick={() => onchange([])}>None</button>
      </div>
      <div class="options">
        {#each filtered as option (option.name)}
          <label class="option" title={option.description}>
            <input type="checkbox" checked={value.includes(option.name)} onchange={() => toggle(option.name)} />
            <span class="option-text">
              <span>{option.name}</span>
              {#if option.description}<span class="muted small">{option.description}</span>{/if}
            </span>
          </label>
        {/each}
        {#each unknown as name}
          <label class="option">
            <input type="checkbox" checked onchange={() => toggle(name)} />
            <span class="option-text"><span>{name}</span><span class="small bad-text">not a known option</span></span>
          </label>
        {/each}
      </div>
    </div>
  {/if}
</div>

<style>
  .multi {
    position: relative;
    width: 100%;
  }

  .summary {
    width: 100%;
    display: flex;
    align-items: center;
    gap: 6px;
    text-align: left;
    white-space: normal;
    min-height: 30px;
  }

  .chips {
    display: flex;
    flex-wrap: wrap;
    gap: 3px;
    flex: 1;
  }

  .chip {
    font-size: 12px;
    background: var(--surface-2);
    border-radius: 4px;
    padding: 0 5px;
  }

  .chip.unknown,
  .bad-text {
    color: var(--critical);
  }

  .caret {
    margin-left: auto;
    color: var(--muted);
  }

  .popup {
    position: absolute;
    right: 0;
    top: calc(100% + 4px);
    z-index: 20;
    width: max(100%, 360px);
    max-width: 90vw;
  }

  .popup-head {
    padding: 8px;
    border-bottom: 1px solid var(--grid);
  }

  .popup-head input {
    flex: 1;
  }

  .options {
    max-height: 320px;
    overflow: auto;
    padding: 4px;
  }

  .option {
    display: flex;
    gap: 8px;
    padding: 4px 6px;
    border-radius: 4px;
    cursor: pointer;
    align-items: flex-start;
  }

  .option:hover {
    background: var(--surface-2);
  }

  .option input {
    margin-top: 3px;
  }

  .option-text {
    display: flex;
    flex-direction: column;
    line-height: 1.3;
  }
</style>
