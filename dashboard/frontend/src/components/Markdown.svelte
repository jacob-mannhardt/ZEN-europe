<script lang="ts">
  import { marked } from "marked";

  let { text }: { text: string } = $props();

  // sources.md is written by ZEN-creator from the dataset metadata; escape any
  // HTML in it and render only the markdown
  function escape(value: string): string {
    return value.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
  }

  const html = $derived(marked.parse(escape(text), { async: false }) as string);
</script>

<div class="markdown">{@html html}</div>

<style>
  .markdown {
    font-size: 13px;
    line-height: 1.5;
    overflow-wrap: anywhere;
  }

  .markdown :global(p) {
    margin: 0 0 8px;
  }

  .markdown :global(ul) {
    margin: 0 0 8px;
    padding-left: 20px;
  }

  .markdown :global(hr) {
    border: none;
    border-top: 1px solid var(--grid);
    margin: 10px 0;
  }
</style>
