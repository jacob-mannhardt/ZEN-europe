<script lang="ts">
  // A data file of an element: a line chart along time or years, a bar chart
  // for values per node or edge, and a map of the values per node or edge.
  import type { DataFile, EdgeInfo, NodeInfo, Series } from "../lib/api";
  import { categorical, chrome, ISO3, MAX_HIGHLIGHTED, sequentialColor, sequentialScale } from "../lib/palette";
  import Plot from "./Plot.svelte";

  type SeriesFile = Extract<DataFile, { kind: "series" }>;

  let {
    data,
    unit,
    nodes,
    edges,
  }: { data: SeriesFile; unit: string; nodes: NodeInfo[]; edges: EdgeInfo[] } = $props();

  const label = (s: Series) => Object.values(s.labels).join(" · ") || data.value_name;
  const finite = (values: (number | null)[]) => values.filter((v): v is number => v !== null);
  const mean = (values: number[]) => (values.length ? values.reduce((a, b) => a + b, 0) / values.length : NaN);

  // The parent creates this component anew for every file ({#key}), so the
  // initial selections are computed once from the data.

  // ---------- series selection, color follows the series ----------
  function initialSlots(): Record<string, number> {
    // all series if few, else the largest
    const ranked = [...data.series]
      .map((s) => ({ key: label(s), size: Math.abs(mean(finite(s.y))) || 0 }))
      .sort((a, b) => b.size - a.size);
    const initial = data.series.length <= MAX_HIGHLIGHTED ? data.series.map(label) : ranked.slice(0, 5).map((r) => r.key);
    return Object.fromEntries(initial.map((key, i) => [key, i]));
  }

  let slots = $state<Record<string, number>>(initialSlots());
  let showTable = $state(false);
  let seriesQuery = $state("");

  function toggle(key: string) {
    if (key in slots) {
      const { [key]: _, ...rest } = slots;
      slots = rest;
      return;
    }
    const used = new Set(Object.values(slots));
    const free = [...Array(MAX_HIGHLIGHTED).keys()].find((i) => !used.has(i));
    if (free === undefined) return;
    slots = { ...slots, [key]: free };
  }

  const highlighted = $derived(Object.keys(slots).length);

  // ---------- time resolution ----------
  const canAggregateTime = $derived(data.x_dim === "time" && data.x.length > 500);
  let resolution = $state<"raw" | "day" | "week">(initialResolution());

  function initialResolution(): "raw" | "day" {
    return data.x_dim === "time" && data.x.length > 500 ? "day" : "raw";
  }

  function resample(x: (number | string)[], y: (number | null)[]) {
    if (!canAggregateTime || resolution === "raw") return { x, y };
    const size = resolution === "day" ? 24 : 168;
    const outX: number[] = [];
    const outY: (number | null)[] = [];
    for (let i = 0; i < y.length; i += size) {
      const chunk = finite(y.slice(i, i + size));
      outX.push(i / size);
      outY.push(chunk.length ? mean(chunk) : null);
    }
    return { x: outX, y: outY };
  }

  const xTitle = $derived(
    data.x_dim === "time"
      ? resolution === "raw"
        ? "hour of the year"
        : `${resolution} of the year (mean)`
      : (data.x_dim ?? "").replace("_", " "),
  );

  // ---------- line chart ----------
  const lineTraces = $derived.by(() => {
    if (!data.x_dim) return [];
    const c = chrome();
    const many = data.x.length > 2000;
    const type = many ? "scattergl" : "scatter";
    const markers = data.x.length <= 40;
    const context = data.series.filter((s) => !(label(s) in slots));
    const traces: unknown[] = context.map((s, i) => {
      const r = resample(data.x, s.y);
      return {
        type,
        mode: "lines",
        x: r.x,
        y: r.y,
        name: label(s),
        legendgroup: "other",
        showlegend: i === 0,
        legendgrouptitle: undefined,
        line: { color: c.context, width: 1 },
        hovertemplate: `${label(s)}: %{y:.4g}<extra></extra>`,
      };
    });
    if (traces.length) (traces[0] as Record<string, unknown>).name = `other (${context.length})`;
    for (const s of data.series.filter((s) => label(s) in slots)) {
      const r = resample(data.x, s.y);
      const color = categorical(slots[label(s)]);
      traces.push({
        type,
        mode: markers ? "lines+markers" : "lines",
        x: r.x,
        y: r.y,
        name: label(s),
        line: { color, width: 2 },
        marker: { color, size: 8, line: { color: c.surface, width: 2 } },
        hovertemplate: `${label(s)}: %{y:.4g} ${unit}<extra></extra>`,
      });
    }
    return traces;
  });

  // ---------- bar chart (no x dimension) ----------
  const bars = $derived.by(() => {
    if (data.x_dim) return null;
    const rows = data.series
      .map((s) => ({ key: label(s), value: s.y[0] }))
      .sort((a, b) => (b.value ?? -Infinity) - (a.value ?? -Infinity));
    return rows;
  });

  const barTraces = $derived(
    bars
      ? [
          {
            type: "bar",
            x: bars.map((b) => b.key),
            y: bars.map((b) => b.value),
            marker: { color: categorical(0), cornerradius: 4 },
            hovertemplate: `%{x}: %{y:.4g} ${unit}<extra></extra>`,
          },
        ]
      : [],
  );

  // ---------- map ----------
  const coords = $derived(new Map(nodes.filter((n) => n.lon !== null && n.lat !== null).map((n) => [n.node, n])));
  const otherDims = $derived(data.group_dims.filter((d) => d !== data.spatial_dim));
  const mappable = $derived(
    (data.spatial_dim === "node" || data.spatial_dim === "location" || data.spatial_dim === "edge") && coords.size > 0,
  );

  const comboOf = (s: Series) =>
    data.group_dims
      .filter((d) => d !== data.spatial_dim)
      .map((d) => s.labels[d])
      .join(" · ");
  const otherCombos = $derived([...new Set(data.series.map(comboOf))].sort());

  // the map shows the last year by default, or the mean of a time series
  let mapValue = $state(initialMapValue());
  let otherFilter = $state(initialFilter());

  function initialFilter(): string {
    return [...new Set(data.series.map(comboOf))].sort()[0] ?? "";
  }

  function initialMapValue(): string {
    if (!data.x_dim) return "value";
    if (data.x_dim === "time" || data.x.length > 120) return "mean";
    return String(data.x.at(-1));
  }

  const mapOptions = $derived.by(() => {
    if (!data.x_dim) return [{ value: "value", label: "value" }];
    const options = [
      { value: "mean", label: `mean over ${data.x_dim}` },
      { value: "sum", label: `sum over ${data.x_dim}` },
      { value: "max", label: `max over ${data.x_dim}` },
      { value: "min", label: `min over ${data.x_dim}` },
    ];
    if (data.x.length <= 120) options.push(...data.x.map((x) => ({ value: String(x), label: `${data.x_dim} ${x}` })));
    return options;
  });

  function aggregate(s: Series): number | null {
    if (!data.x_dim) return s.y[0];
    const values = finite(s.y);
    if (!values.length) return null;
    switch (mapValue) {
      case "mean":
        return mean(values);
      case "sum":
        return values.reduce((a, b) => a + b, 0);
      case "max":
        return Math.max(...values);
      case "min":
        return Math.min(...values);
      default: {
        const i = data.x.findIndex((x) => String(x) === mapValue);
        return i >= 0 ? s.y[i] : null;
      }
    }
  }

  const mapEntries = $derived.by(() => {
    if (!mappable) return [];
    return data.series
      .filter((s) => comboOf(s) === otherFilter)
      .map((s) => ({ key: String(s.labels[data.spatial_dim!]), value: aggregate(s) }));
  });

  const geo = $derived.by(() => {
    const c = chrome();
    return {
      scope: "europe",
      projection: { type: "mercator" },
      lonaxis: { range: [-12, 34] },
      lataxis: { range: [35, 71.5] },
      showland: true,
      landcolor: c.grid,
      showcountries: true,
      countrycolor: c.surface,
      showocean: false,
      showlakes: false,
      showframe: false,
      coastlinecolor: c.axis,
      bgcolor: c.surface,
    };
  });

  const mapTraces = $derived.by(() => {
    if (!mappable || !mapEntries.length) return [];
    const c = chrome();
    const values = finite(mapEntries.map((e) => e.value));
    const min = Math.min(0, ...values);
    const max = Math.max(...values, min + 1e-12);
    const colorbar = { title: { text: unit, font: { color: c.ink2 } }, tickfont: { color: c.muted }, outlinewidth: 0, thickness: 12 };

    if (data.spatial_dim === "edge") {
      const ends = new Map(edges.map((e) => [e.edge, e]));
      const traces: unknown[] = [];
      const mids: { lon: number; lat: number; text: string; value: number | null }[] = [];
      for (const entry of mapEntries) {
        const edge = ends.get(entry.key);
        const a = edge && coords.get(edge.node_from);
        const b = edge && coords.get(edge.node_to);
        if (!a || !b) continue;
        // each direction is drawn from its origin to the middle of the edge
        const mid = { lon: (a.lon! + b.lon!) / 2, lat: (a.lat! + b.lat!) / 2 };
        const t = entry.value === null ? 0 : (entry.value - min) / (max - min);
        traces.push({
          type: "scattergeo",
          mode: "lines",
          lon: [a.lon, mid.lon],
          lat: [a.lat, mid.lat],
          line: { color: entry.value ? sequentialColor(t) : c.axis, width: entry.value ? 2 + 4 * t : 1 },
          hoverinfo: "skip",
          showlegend: false,
        });
        mids.push({
          lon: (a.lon! + mid.lon) / 2,
          lat: (a.lat! + mid.lat) / 2,
          text: `${entry.key}: ${entry.value === null ? "–" : entry.value.toPrecision(4)} ${unit}`,
          value: entry.value,
        });
      }
      traces.push({
        type: "scattergeo",
        mode: "markers",
        lon: mids.map((m) => m.lon),
        lat: mids.map((m) => m.lat),
        text: mids.map((m) => m.text),
        hovertemplate: "%{text}<extra></extra>",
        marker: {
          size: 8,
          color: mids.map((m) => m.value),
          colorscale: sequentialScale(),
          cmin: min,
          cmax: max,
          showscale: true,
          colorbar,
          line: { color: c.surface, width: 1.5 },
        },
        showlegend: false,
      });
      traces.push({
        type: "scattergeo",
        mode: "text",
        lon: [...coords.values()].map((n) => n.lon),
        lat: [...coords.values()].map((n) => n.lat),
        text: [...coords.keys()],
        textfont: { color: c.ink2, size: 10 },
        hoverinfo: "skip",
        showlegend: false,
      });
      return traces;
    }

    const known = mapEntries.filter((e) => ISO3[e.key]);
    return [
      {
        type: "choropleth",
        locationmode: "ISO-3",
        locations: known.map((e) => ISO3[e.key]),
        z: known.map((e) => e.value),
        text: known.map((e) => e.key),
        zmin: min,
        zmax: max,
        colorscale: sequentialScale(),
        marker: { line: { color: c.surface, width: 1 } },
        colorbar,
        hovertemplate: `%{text}: %{z:.4g} ${unit}<extra></extra>`,
      },
      {
        type: "scattergeo",
        mode: "text",
        lon: known.map((e) => coords.get(e.key)?.lon),
        lat: known.map((e) => coords.get(e.key)?.lat),
        text: known.map((e) => e.key),
        textfont: { color: c.ink, size: 10 },
        hoverinfo: "skip",
        showlegend: false,
      },
    ];
  });

  // ---------- summary table ----------
  const summary = $derived(
    data.series.map((s) => {
      const values = finite(s.y);
      return {
        key: label(s),
        mean: mean(values),
        min: values.length ? Math.min(...values) : NaN,
        max: values.length ? Math.max(...values) : NaN,
        sum: values.reduce((a, b) => a + b, 0),
      };
    }),
  );

  const fmt = (v: number) => (Number.isFinite(v) ? Number(v.toPrecision(4)).toLocaleString("en-US") : "–");
  const visibleSeries = $derived(
    data.series.map(label).filter((key) => key.toLowerCase().includes(seriesQuery.toLowerCase())),
  );
</script>

<div class="data-plot">
  <div class="meta small secondary">
    {data.rows.toLocaleString("en-US")} rows · {data.series.length} series
    {#if data.x_dim}· {data.x.length} values of <code>{data.x_dim}</code>{/if}
    {#if data.group_dims.length}· by <code>{data.group_dims.join(", ")}</code>{/if}
    {#if data.x_single}· all values for <code>{data.x_single.dim}</code> {data.x_single.value}{/if}
    {#if data.truncated}<span class="badge bad">only the first {data.series.length} series are shown</span>{/if}
  </div>

  {#if data.x_dim}
    <div class="controls row">
      {#if canAggregateTime}
        <label class="row small">Resolution
          <select bind:value={resolution}>
            <option value="raw">hourly</option>
            <option value="day">daily mean</option>
            <option value="week">weekly mean</option>
          </select>
        </label>
      {/if}
      {#if data.series.length > 1}
        <span class="small muted">{highlighted} of {MAX_HIGHLIGHTED} series highlighted, the rest in gray</span>
      {/if}
    </div>
    <div class="chart-row">
      <div class="chart">
        <Plot
          data={lineTraces}
          layout={{
            xaxis: { title: { text: xTitle }, tickformat: data.x_dim === "time" ? "" : "d" },
            yaxis: { title: { text: unit } },
            hovermode: data.series.length <= MAX_HIGHLIGHTED ? "x unified" : "closest",
            showlegend: true,
          }}
        />
      </div>
      {#if data.series.length > 1}
        <div class="series-picker">
          <input type="search" placeholder="Filter series" bind:value={seriesQuery} />
          <div class="series-list">
            {#each visibleSeries as key (key)}
              <label class="series" class:on={key in slots}>
                <input
                  type="checkbox"
                  checked={key in slots}
                  disabled={!(key in slots) && highlighted >= MAX_HIGHLIGHTED}
                  onchange={() => toggle(key)}
                />
                <span class="swatch" style:background={key in slots ? categorical(slots[key]) : "transparent"}></span>
                {key}
              </label>
            {/each}
          </div>
        </div>
      {/if}
    </div>
  {:else if bars}
    {#if bars.length === 1}
      <div class="single"><span class="value">{fmt(bars[0].value ?? NaN)}</span> <span class="secondary">{unit}</span></div>
    {:else}
      <Plot data={barTraces} layout={{ yaxis: { title: { text: unit } }, xaxis: { type: "category" }, bargap: 0.25 }} height={320} />
    {/if}
  {/if}

  {#if mappable}
    <div class="map-head row">
      <h4>Map</h4>
      {#if mapOptions.length > 1}
        <select bind:value={mapValue} aria-label="Value shown on the map">
          {#each mapOptions as option}<option value={option.value}>{option.label}</option>{/each}
        </select>
      {/if}
      {#if otherCombos.length > 1}
        <select bind:value={otherFilter} aria-label={`Filter by ${otherDims.join(", ")}`}>
          {#each otherCombos as combo}<option value={combo}>{combo}</option>{/each}
        </select>
      {/if}
      {#if data.spatial_dim === "edge"}
        <span class="muted small">Each direction of an edge is drawn from its origin to the middle.</span>
      {/if}
    </div>
    <Plot data={mapTraces} layout={{ geo, margin: { l: 0, r: 0, t: 0, b: 0 }, hovermode: "closest" }} height={460} />
    <p class="muted small">The country shapes are loaded from cdn.plot.ly, so the map needs an internet connection.</p>
  {/if}

  <button class="ghost small" onclick={() => (showTable = !showTable)}>{showTable ? "▾" : "▸"} Table of the series</button>
  {#if showTable}
    <div class="table-wrap">
      <table class="data">
        <thead>
          <tr><th>Series</th>{#if data.x_dim}<th class="num">Mean</th><th class="num">Min</th><th class="num">Max</th><th class="num">Sum</th>{:else}<th class="num">Value</th>{/if}</tr>
        </thead>
        <tbody>
          {#each summary as row}
            <tr>
              <td>{row.key}</td>
              {#if data.x_dim}
                <td class="num">{fmt(row.mean)}</td><td class="num">{fmt(row.min)}</td><td class="num">{fmt(row.max)}</td><td class="num">{fmt(row.sum)}</td>
              {:else}
                <td class="num">{fmt(row.mean)}</td>
              {/if}
            </tr>
          {/each}
        </tbody>
      </table>
    </div>
  {/if}
</div>

<style>
  .data-plot {
    display: flex;
    flex-direction: column;
    gap: 8px;
  }

  .controls {
    flex-wrap: wrap;
  }

  .chart-row {
    display: grid;
    grid-template-columns: minmax(0, 1fr) 190px;
    gap: 12px;
  }

  .chart-row:has(.chart:only-child) {
    grid-template-columns: 1fr;
  }

  .series-picker {
    display: flex;
    flex-direction: column;
    gap: 4px;
    min-height: 0;
  }

  .series-list {
    max-height: 340px;
    overflow: auto;
    font-size: 12.5px;
  }

  .series {
    display: flex;
    align-items: center;
    gap: 6px;
    padding: 2px 4px;
    border-radius: 4px;
    cursor: pointer;
  }

  .series:hover {
    background: var(--surface-2);
  }

  .swatch {
    width: 10px;
    height: 10px;
    border-radius: 3px;
    border: 1px solid var(--border);
    flex-shrink: 0;
  }

  .single {
    padding: 12px 0;
  }

  .single .value {
    font-size: 28px;
    font-weight: 600;
  }

  .map-head {
    margin-top: 8px;
    flex-wrap: wrap;
  }

  .table-wrap {
    max-height: 360px;
    overflow: auto;
  }

  @media (max-width: 900px) {
    .chart-row {
      grid-template-columns: 1fr;
    }
  }
</style>
