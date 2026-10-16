// Application state shared by the views.

import {
  api,
  type Catalog,
  type DatasetInfo,
  type Job,
  type ModelsDoc,
  type ReferenceStatus,
  type Structure,
  type Validation,
} from "./api";
import { clone, DEFAULTS } from "./settings";

export type View = "models" | "structure" | "generate" | "data";

export interface DataTarget {
  dataset: string | null;
  elementType: string | null;
  element: string | null;
}

export const app = $state({
  view: "models" as View,
  catalog: null as Catalog | null,
  info: {} as Record<string, string>,
  doc: { defaults: {}, models: {} } as ModelsDoc,
  saved: "",
  selected: DEFAULTS as string,
  validation: { file_error: null, errors: {} } as Validation,
  datasets: [] as DatasetInfo[],
  jobs: [] as Job[],
  data: { dataset: null, elementType: null, element: null } as DataTarget,
  // the dataset of the defaults, which the data explorer compares with
  reference: { exists: false, generated: null, outdated: false, job: null } as ReferenceStatus,
  // the structure of the selected model, with its unsaved changes
  structure: { value: null as Structure | null, error: null as string | null, loading: false },
  error: null as string | null,
  loading: true,
});

export function isDirty(): boolean {
  return JSON.stringify(app.doc) !== app.saved;
}

export async function load(): Promise<void> {
  try {
    const [catalog, doc, info] = await Promise.all([api.catalog(), api.models(), api.info()]);
    app.catalog = catalog;
    app.info = info;
    setSaved(doc);
    app.selected = Object.keys(doc.models)[0] ?? DEFAULTS;
    await Promise.all([refreshDatasets(), refreshJobs()]);
  } catch (error) {
    app.error = `Could not reach the backend: ${(error as Error).message}`;
  } finally {
    app.loading = false;
  }
}

function setSaved(doc: ModelsDoc): void {
  app.doc = clone(doc);
  app.saved = JSON.stringify(app.doc);
}

/** Save the models file. Returns whether it was saved. */
export async function save(): Promise<boolean> {
  const result = await api.save(app.doc);
  app.validation = result;
  if (result.saved) app.saved = JSON.stringify(app.doc);
  return !!result.saved;
}

export async function revert(): Promise<void> {
  setSaved(await api.models());
  if (app.selected !== DEFAULTS && !app.doc.models[app.selected]) {
    app.selected = Object.keys(app.doc.models)[0] ?? DEFAULTS;
  }
}

let structureRequest = 0;

/** Recompute the structure for a settings patch; a newer call wins. */
export async function refreshStructure(patchJson: string): Promise<void> {
  const request = ++structureRequest;
  app.structure.loading = true;
  try {
    const value = await api.structure(JSON.parse(patchJson));
    if (request !== structureRequest) return;
    app.structure.value = value;
    app.structure.error = null;
  } catch (error) {
    if (request === structureRequest) app.structure.error = (error as Error).message;
  } finally {
    if (request === structureRequest) app.structure.loading = false;
  }
}

export async function refreshDatasets(): Promise<void> {
  app.datasets = await api.datasets();
}

export async function refreshJobs(): Promise<void> {
  app.jobs = await api.jobs();
  await refreshReference();
}

export async function refreshReference(): Promise<void> {
  app.reference = await api.reference();
}

/** Generate the dataset of the defaults (again), to compare with. */
export async function generateReference(): Promise<void> {
  await api.generateReference();
  await refreshJobs();
}

/** Save the models file if needed, then queue the generation of models. */
export async function generate(models: string[]): Promise<void> {
  if (isDirty() && !(await save())) {
    throw new Error("The models file has errors, so it was not saved and nothing was generated.");
  }
  await api.generate(models);
  await refreshJobs();
}

/** Why a model cannot be generated right now, if it cannot. */
export function blocker(model: string): string | null {
  return (
    app.validation.file_error ?? app.validation.errors[model] ?? app.validation.problems?.[model] ?? null
  );
}

export function openData(dataset: string, elementType: string | null = null, element: string | null = null): void {
  app.data = { dataset, elementType, element };
  app.view = "data";
}

export function datasetOf(model: string): DatasetInfo | undefined {
  return app.datasets.find((d) => d.name === model);
}

export function latestJob(model: string): Job | undefined {
  return app.jobs.find((job) => job.model === model);
}
