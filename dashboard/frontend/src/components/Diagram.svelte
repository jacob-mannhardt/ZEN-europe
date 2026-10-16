<script lang="ts">
  // A mermaid flowchart that can be zoomed, panned and whose nodes can be clicked.
  import mermaid from "mermaid";

  let {
    source,
    onnodeclick,
    height = "auto",
  }: { source: string; onnodeclick?: (id: string) => void; height?: string } = $props();

  let container: HTMLDivElement;
  let canvas: HTMLDivElement;
  let error = $state<string | null>(null);
  let scale = $state(1);
  let tx = $state(0);
  let ty = $state(0);
  let natural = { width: 0, height: 0 };
  let counter = 0;

  const dark = window.matchMedia("(prefers-color-scheme: dark)").matches;
  mermaid.initialize({
    startOnLoad: false,
    theme: dark ? "dark" : "neutral",
    securityLevel: "strict",
    maxTextSize: 500000,
    maxEdges: 5000,
    flowchart: { htmlLabels: true, useMaxWidth: false },
  });

  $effect(() => {
    render(source);
  });

  // a wheel listener has to be registered as non-passive to prevent scrolling
  $effect(() => {
    container.addEventListener("wheel", onWheel, { passive: false });
    return () => container.removeEventListener("wheel", onWheel);
  });

  async function render(text: string) {
    const id = `diagram-${Math.random().toString(36).slice(2)}-${counter++}`;
    try {
      const { svg } = await mermaid.render(id, text);
      error = null;
      canvas.innerHTML = svg;
      const element = canvas.querySelector("svg");
      if (!element) return;
      const box = element.viewBox.baseVal;
      natural = { width: box.width, height: box.height };
      element.setAttribute("width", String(box.width));
      element.setAttribute("height", String(box.height));
      element.style.maxWidth = "none";
      attachClicks(element);
      fit();
    } catch (e) {
      error = (e as Error).message;
      document.getElementById(id)?.remove();
      document.getElementById(`d${id}`)?.remove();
    }
  }

  function attachClicks(svg: SVGSVGElement) {
    if (!onnodeclick) return;
    for (const node of svg.querySelectorAll<SVGGElement>("g.node")) {
      const match = node.id.match(/flowchart-([ct]_[A-Za-z0-9_]+)-\d+$/);
      if (!match) continue;
      node.style.cursor = "pointer";
      node.addEventListener("click", (event) => {
        if (dragged) return;
        event.stopPropagation();
        onnodeclick!(match[1]);
      });
    }
  }

  export function fit() {
    if (!natural.width || !container) return;
    // fit the width, unless that makes the labels illegible; large diagrams
    // are then panned vertically
    const width = container.clientWidth - 16;
    const maxHeight = height === "auto" ? Infinity : container.clientHeight - 16;
    scale = Math.min(1.2, width / natural.width, Math.max(maxHeight / natural.height, 0.8));
    scale = Math.min(scale, width / natural.width);
    tx = Math.max(8, (container.clientWidth - natural.width * scale) / 2);
    ty = 8;
  }

  function zoom(factor: number, cx = container.clientWidth / 2, cy = container.clientHeight / 2) {
    const next = Math.min(8, Math.max(0.05, scale * factor));
    tx = cx - ((cx - tx) * next) / scale;
    ty = cy - ((cy - ty) * next) / scale;
    scale = next;
  }

  function onWheel(event: WheelEvent) {
    if (!event.ctrlKey && height === "auto") return; // let the page scroll small diagrams
    event.preventDefault();
    const rect = container.getBoundingClientRect();
    zoom(event.deltaY < 0 ? 1.15 : 1 / 1.15, event.clientX - rect.left, event.clientY - rect.top);
  }

  let dragging = false;
  let dragged = false;
  let start = { x: 0, y: 0, tx: 0, ty: 0 };

  function onPointerDown(event: PointerEvent) {
    dragging = true;
    dragged = false;
    start = { x: event.clientX, y: event.clientY, tx, ty };
  }

  function onPointerMove(event: PointerEvent) {
    if (!dragging) return;
    const dx = event.clientX - start.x;
    const dy = event.clientY - start.y;
    if (Math.abs(dx) + Math.abs(dy) > 3) {
      dragged = true;
      container.setPointerCapture(event.pointerId);
    }
    tx = start.tx + dx;
    ty = start.ty + dy;
  }

  function onPointerUp() {
    dragging = false;
    setTimeout(() => (dragged = false));
  }

  const displayHeight = $derived(height === "auto" ? `${Math.max(120, natural.height * scale + 16)}px` : height);
</script>

<div class="diagram">
  <div class="controls">
    <button class="small" onclick={() => zoom(1.25)} title="Zoom in">+</button>
    <button class="small" onclick={() => zoom(0.8)} title="Zoom out">−</button>
    <button class="small" onclick={fit} title="Fit to view">Fit</button>
  </div>
  {#if error}<div class="error-box">Could not draw the diagram: {error}</div>{/if}
  <!-- svelte-ignore a11y_no_static_element_interactions -->
  <div
    class="viewport"
    bind:this={container}
    style:height={displayHeight}
    onpointerdown={onPointerDown}
    onpointermove={onPointerMove}
    onpointerup={onPointerUp}
    onpointercancel={onPointerUp}
  >
    <div class="canvas" bind:this={canvas} style:transform={`translate(${tx}px, ${ty}px) scale(${scale})`}></div>
  </div>
</div>

<style>
  .diagram {
    position: relative;
  }

  .controls {
    position: absolute;
    right: 8px;
    top: 8px;
    z-index: 2;
    display: flex;
    gap: 4px;
  }

  .viewport {
    overflow: hidden;
    position: relative;
    border: 1px solid var(--grid);
    border-radius: 6px;
    background: var(--surface);
    cursor: grab;
    touch-action: none;
  }

  .viewport:active {
    cursor: grabbing;
  }

  .canvas {
    transform-origin: 0 0;
    position: absolute;
    left: 0;
    top: 0;
  }
</style>
