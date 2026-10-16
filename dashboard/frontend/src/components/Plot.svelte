<script lang="ts">
  import { onDestroy } from "svelte";
  import { chrome } from "../lib/palette";

  let { data, layout = {}, height = 380 }: { data: unknown[]; layout?: Record<string, unknown>; height?: number } =
    $props();

  let element: HTMLDivElement;
  let plotly: typeof import("plotly.js-dist-min").default | null = null;

  function baseLayout() {
    const c = chrome();
    const axis = {
      gridcolor: c.grid,
      linecolor: c.axis,
      zerolinecolor: c.axis,
      tickfont: { color: c.muted, size: 11 },
      title: { font: { color: c.ink2, size: 12 } },
      automargin: true,
    };
    return {
      height,
      paper_bgcolor: c.surface,
      plot_bgcolor: c.surface,
      font: { family: 'system-ui, -apple-system, "Segoe UI", sans-serif', color: c.ink, size: 12 },
      margin: { l: 56, r: 16, t: 36, b: 44 },
      xaxis: axis,
      yaxis: axis,
      legend: { font: { color: c.ink2 }, orientation: "h", x: 0, y: 1.02, yanchor: "bottom" },
      hoverlabel: { bgcolor: c.surface, bordercolor: c.axis, font: { color: c.ink } },
      hovermode: "closest",
    };
  }

  function merge(base: Record<string, any>, extra: Record<string, any>) {
    const out: Record<string, any> = { ...base };
    for (const [key, value] of Object.entries(extra)) {
      out[key] =
        value && typeof value === "object" && !Array.isArray(value) && base[key] && typeof base[key] === "object"
          ? { ...base[key], ...value }
          : value;
    }
    return out;
  }

  $effect(() => {
    const traces = data;
    const fullLayout = merge(baseLayout(), layout);
    (async () => {
      plotly ??= (await import("plotly.js-dist-min")).default;
      await plotly.react(element, traces, fullLayout, { responsive: true, displaylogo: false });
    })();
  });

  onDestroy(() => plotly?.purge(element));
</script>

<div class="plot" bind:this={element} style:min-height={`${height}px`}></div>

<style>
  .plot {
    width: 100%;
  }
</style>
