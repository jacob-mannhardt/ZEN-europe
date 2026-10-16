<script lang="ts">
  import { api, type Job } from "../lib/api";
  import { countFields } from "../lib/settings";
  import { app, blocker, datasetOf, generate, isDirty, openData, refreshDatasets, refreshJobs } from "../lib/store.svelte";

  let chosen = $state<Record<string, boolean>>({});
  let message = $state<string | null>(null);
  let busy = $state(false);
  let logJob = $state<string | null>(null);
  let logText = $state("");
  let logOffset = 0;
  let logElement = $state<HTMLPreElement>();

  const modelNames = $derived(Object.keys(app.doc.models));
  const selectedModels = $derived(modelNames.filter((n) => chosen[n]));
  const shownJob = $derived(app.jobs.find((j) => j.id === logJob) ?? app.jobs[0]);
  // the jobs are refreshed while they run, so the log follows the id only
  const shownJobId = $derived(shownJob?.id);

  async function onGenerate(models: string[]) {
    busy = true;
    message = null;
    try {
      await generate(models);
      chosen = {};
      logJob = null;
    } catch (error) {
      message = (error as Error).message;
    } finally {
      busy = false;
    }
  }

  // follow the log of the shown job
  $effect(() => {
    const id = shownJobId;
    if (!id) return;
    logText = "";
    logOffset = 0;
    let stopped = false;
    const poll = async () => {
      try {
        const result = await api.jobLog(id, logOffset);
        if (stopped) return;
        logText += stripAnsi(result.text);
        logOffset = result.offset;
        if (result.text && logElement) {
          const atEnd = logElement.scrollHeight - logElement.scrollTop - logElement.clientHeight < 40;
          if (atEnd) queueMicrotask(() => logElement && (logElement.scrollTop = logElement.scrollHeight));
        }
        if (result.job.status === "queued" || result.job.status === "running") setTimeout(poll, 1000);
      } catch {
        // the job may be gone after a restart of the backend
      }
    };
    poll();
    return () => {
      stopped = true;
    };
  });

  function stripAnsi(text: string): string {
    return text.replace(/\u001b\[[0-9;]*m/g, "");
  }

  async function cancel(job: Job) {
    await api.cancelJob(job.id);
    await refreshJobs();
  }

  async function remove(name: string) {
    if (!confirm(`Delete the generated dataset '${name}' from the workspace?`)) return;
    await api.deleteDataset(name);
    await refreshDatasets();
  }

  function time(seconds: number | null): string {
    return seconds ? new Date(seconds * 1000).toLocaleString() : "–";
  }

  function duration(job: Job): string {
    if (!job.started) return "";
    const end = job.finished ?? Date.now() / 1000;
    const s = Math.round(end - job.started);
    return s < 60 ? `${s} s` : `${Math.floor(s / 60)} min ${s % 60} s`;
  }

  function size(bytes: number): string {
    return bytes > 1e9 ? `${(bytes / 1e9).toFixed(1)} GB` : `${(bytes / 1e6).toFixed(0)} MB`;
  }

  const statusClass: Record<string, string> = { done: "good", failed: "bad", queued: "changed", running: "changed", cancelled: "" };
</script>

<div class="page">
  <section class="card block">
    <div class="row block-head">
      <h3>Generate models</h3>
      <span class="spacer"></span>
      <button onclick={() => (chosen = Object.fromEntries(modelNames.map((n) => [n, true])))}>Select all</button>
      <button class="primary" disabled={!selectedModels.length || busy || selectedModels.some((n) => blocker(n))} onclick={() => onGenerate(selectedModels)}>
        Generate {selectedModels.length || ""} selected
      </button>
    </div>
    <p class="secondary small">
      Each model runs <code>zen-europe --model &lt;name&gt;</code> on the saved models.yaml, one after another, and is
      written to <code>{app.info.output_path}</code>.
      {#if isDirty()}Unsaved changes are saved first.{/if}
      A model usually takes a few seconds; it takes longer when cached sources are downloaded again.
    </p>
    {#if message}<div class="error-box">{message}</div>{/if}
    <table class="data">
      <thead><tr><th></th><th>Model</th><th class="num">Changed settings</th><th>Dataset</th><th></th></tr></thead>
      <tbody>
        {#each modelNames as name}
          {@const dataset = datasetOf(name)}
          <tr>
            <td><input type="checkbox" bind:checked={chosen[name]} aria-label={`Select ${name}`} /></td>
            <td>
              <strong>{name}</strong>
              {#if app.doc.models[name].extends}<span class="muted small"> extends {app.doc.models[name].extends}</span>{/if}
              {#if blocker(name)}<span class="badge bad" title={blocker(name)}>cannot be generated</span>{/if}
            </td>
            <td class="num">{countFields(app.doc.models[name].settings)}</td>
            <td>{dataset ? `generated ${time(dataset.generated ?? dataset.modified)}` : "not generated"}</td>
            <td class="actions">
              <button class="small" disabled={busy || !!blocker(name)} title={blocker(name) ?? ""} onclick={() => onGenerate([name])}>
                {dataset ? "Regenerate" : "Generate"}
              </button>
            </td>
          </tr>
        {/each}
      </tbody>
    </table>
  </section>

  <section class="card block">
    <h3>Jobs</h3>
    {#if app.jobs.length === 0}
      <p class="muted">No model has been generated since the dashboard was started.</p>
    {:else}
      <div class="jobs">
        <div class="job-list">
          {#each app.jobs as job (job.id)}
            <button class="list-button" class:active={shownJob?.id === job.id} onclick={() => (logJob = job.id)}>
              <span>{job.model}</span>
              <span class="spacer"></span>
              <span class="muted small">{duration(job)}</span>
              <span class="badge {statusClass[job.status]}">{job.status}</span>
            </button>
          {/each}
        </div>
        <div class="log">
          {#if shownJob}
            <div class="row">
              <strong>{shownJob.model}</strong>
              <span class="muted small">queued {time(shownJob.created)}</span>
              <span class="spacer"></span>
              {#if shownJob.status === "queued" || shownJob.status === "running"}
                <button class="small danger" onclick={() => cancel(shownJob)}>Cancel</button>
              {:else if shownJob.status === "done" && shownJob.kind === "reference"}
                <span class="muted small">Used to highlight what the models change in the data explorer.</span>
              {:else if shownJob.status === "done"}
                <button class="small" onclick={() => openData(shownJob.model)}>Explore data</button>
              {/if}
            </div>
            <pre bind:this={logElement}>{logText || "Waiting for output …"}</pre>
          {/if}
        </div>
      </div>
    {/if}
  </section>

  <section class="card block">
    <div class="row block-head">
      <h3>Generated datasets</h3>
      <span class="spacer"></span>
      <button class="small" onclick={refreshDatasets}>Refresh</button>
    </div>
    <p class="secondary small">
      A download is a zip with the dataset folder and a <code>config.yaml</code> that points ZEN-garden to it.
    </p>
    {#if app.datasets.length === 0}
      <p class="muted">No dataset has been generated yet.</p>
    {:else}
      <table class="data">
        <thead><tr><th>Dataset</th><th>Generated</th><th class="num">Size</th><th></th></tr></thead>
        <tbody>
          {#each app.datasets as dataset (dataset.name)}
            <tr>
              <td>
                <strong>{dataset.name}</strong>
                {#if !app.doc.models[dataset.name]}<span class="muted small"> (not in models.yaml)</span>{/if}
              </td>
              <td>{time(dataset.generated ?? dataset.modified)}</td>
              <td class="num">{size(dataset.size)}</td>
              <td class="actions">
                <button class="small" onclick={() => openData(dataset.name)}>Explore</button>
                <a class="small download" href={api.downloadUrl(dataset.name)} download>Download zip</a>
                <button class="small ghost danger" onclick={() => remove(dataset.name)}>Delete</button>
              </td>
            </tr>
          {/each}
        </tbody>
      </table>
    {/if}
  </section>
</div>

<style>
  .page {
    overflow: auto;
    height: 100%;
    padding: 16px 24px 48px;
    display: flex;
    flex-direction: column;
    gap: 16px;
    max-width: 1200px;
  }

  .block {
    padding: 14px 16px;
    display: flex;
    flex-direction: column;
    gap: 8px;
  }

  .block-head {
    flex-wrap: wrap;
  }

  .block p {
    margin: 0;
  }

  .actions {
    text-align: right;
    white-space: nowrap;
  }

  .download {
    display: inline-block;
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 2px 8px;
    text-decoration: none;
    margin: 0 4px;
  }

  .jobs {
    display: grid;
    grid-template-columns: 260px 1fr;
    gap: 12px;
    min-height: 260px;
  }

  .job-list {
    display: flex;
    flex-direction: column;
    gap: 2px;
    max-height: 420px;
    overflow: auto;
  }

  .log {
    display: flex;
    flex-direction: column;
    gap: 6px;
    min-width: 0;
  }

  .log pre {
    margin: 0;
    background: var(--surface-2);
    border-radius: 6px;
    padding: 8px 10px;
    font-family: var(--mono);
    font-size: 12px;
    height: 380px;
    overflow: auto;
    white-space: pre-wrap;
    word-break: break-word;
  }

  @media (max-width: 800px) {
    .page {
      padding: 16px;
    }
    .jobs {
      grid-template-columns: 1fr;
    }
  }
</style>
