// Types and calls of the backend API (backend/zen_dashboard/app.py).

export type Settings = Record<string, Record<string, unknown>>;

export interface FieldSchema {
  name: string;
  kind: "bool" | "int" | "float" | "str" | "choice" | "list" | "path" | "json";
  choices: unknown[] | null;
  options: string | null;
  default: unknown;
  description: string;
  controls: string | null;
}

export interface CategorySchema {
  name: string;
  description: string;
  advanced: boolean;
  fields: FieldSchema[];
}

export interface NamedOption {
  name: string;
  description: string;
}

export interface SectorOption extends NamedOption {
  required_sectors: string[];
}

export interface Catalog {
  config_path: string;
  schema: { categories: CategorySchema[] };
  base: Settings;
  options: {
    nodes: string[];
    sectors: SectorOption[];
    energy_systems: string[];
    elements: Record<string, NamedOption[]>;
  };
}

export interface ModelEntry {
  extends: string | null;
  settings: Settings;
}

export interface ModelsDoc {
  defaults: Settings;
  models: Record<string, ModelEntry>;
}

export interface Validation {
  file_error: string | null;
  errors: Record<string, string>;
  // models that are valid settings-wise but cannot be generated
  problems?: Record<string, string>;
  saved?: boolean;
}

export interface TechnologyStructure {
  type: string;
  sectors: string[];
  reference_carrier: string[];
  input_carrier?: string[];
  output_carrier?: string[];
  retrofit_reference_carrier?: string[];
  base_technology?: string;
}

export interface CarrierStructure {
  sectors: string[];
  produced_by: string[];
  consumed_by: string[];
  stored_by: string[];
  transported_by: string[];
}

export interface Structure {
  sectors: Record<string, { description: string; required_sectors: string[]; elements: string[] }>;
  technologies: Record<string, TechnologyStructure>;
  carriers: Record<string, CarrierStructure>;
  carrier_flows: [string, string][];
  nodes: string[];
  missing_carriers: Record<string, string[]>;
  compared_to_base: { added: string[]; removed: string[] };
}

export interface Job {
  id: string;
  model: string;
  status: "queued" | "running" | "done" | "failed" | "cancelled";
  created: number;
  started: number | null;
  finished: number | null;
  returncode: number | null;
  settings_patch: Settings;
  // "reference" for the dataset of the defaults, which is not a model
  kind: "model" | "reference";
}

export interface DatasetInfo {
  name: string;
  modified: number;
  generated: number | null;
  duration: number | null;
  settings_patch: Settings | null;
  size: number;
}

export interface NodeInfo {
  node: string;
  lon: number | null;
  lat: number | null;
}

export interface EdgeInfo {
  edge: string;
  node_from: string;
  node_to: string;
}

export interface DatasetOverview {
  name: string;
  system: Record<string, unknown>;
  nodes: NodeInfo[];
  edges: EdgeInfo[];
  elements: Record<string, string[]>;
  scenarios: Record<string, unknown> | null;
  meta: Record<string, unknown>;
}

export interface AttributeRow {
  name: string;
  default_value: unknown;
  unit: string | null;
  extra: unknown;
  files: string[];
  has_sources: boolean;
}

export interface ElementDetails {
  name: string;
  type: string;
  attributes: AttributeRow[];
  sources: Record<string, string>;
  other_files: string[];
}

export interface AttributeChange {
  // the default value in the reference and in the dataset, if it changed
  default: [unknown, unknown] | null;
  entry_changed: boolean;
  // data files that differ: changed, added or removed
  files: Record<string, "changed" | "added" | "removed">;
}

export const DEFAULTS_REFERENCE = "__defaults__";

export interface ReferenceStatus {
  exists: boolean;
  generated: number | null;
  outdated: boolean;
  // the queued or running generation of the defaults
  job: Job | null;
}

export interface Comparison {
  reference: string | null;
  reference_label: string | null;
  // "<element type>/<element>" of the elements that differ
  elements: Record<string, { status: "changed" | "added"; attributes: Record<string, AttributeChange> }>;
  removed: string[];
}

export interface Series {
  labels: Record<string, string | number>;
  y: (number | null)[];
}

export type DataFile =
  | {
      kind: "series";
      file: string;
      value_name: string;
      rows: number;
      x_dim: string | null;
      x: (number | string)[];
      x_single: { dim: string; value: number | string } | null;
      spatial_dim: string | null;
      group_dims: string[];
      series: Series[];
      truncated: boolean;
    }
  | { kind: "table"; columns: string[]; rows: unknown[][] };

async function request<T>(method: string, url: string, body?: unknown): Promise<T> {
  const response = await fetch(url, {
    method,
    headers: body === undefined ? {} : { "Content-Type": "application/json" },
    body: body === undefined ? undefined : JSON.stringify(body),
  });
  if (!response.ok) {
    let detail = `${response.status} ${response.statusText}`;
    try {
      const data = await response.json();
      if (data.detail) detail = typeof data.detail === "string" ? data.detail : JSON.stringify(data.detail);
    } catch {
      // keep the status text
    }
    throw new Error(detail);
  }
  return response.json() as Promise<T>;
}

const enc = encodeURIComponent;

export const api = {
  catalog: () => request<Catalog>("GET", "/api/catalog"),
  info: () => request<Record<string, string>>("GET", "/api/info"),
  models: () => request<ModelsDoc>("GET", "/api/models"),
  validate: (doc: ModelsDoc) => request<Validation>("POST", "/api/models/validate", doc),
  save: (doc: ModelsDoc) => request<Validation>("PUT", "/api/models", doc),
  structure: (patch: Settings) => request<Structure>("POST", "/api/structure", { patch }),
  generate: (models: string[]) => request<Job[]>("POST", "/api/jobs", { models }),
  jobs: () => request<Job[]>("GET", "/api/jobs"),
  jobLog: (id: string, offset: number) =>
    request<{ job: Job; text: string; offset: number }>("GET", `/api/jobs/${id}/log?offset=${offset}`),
  cancelJob: (id: string) => request<Job>("POST", `/api/jobs/${id}/cancel`),
  datasets: () => request<DatasetInfo[]>("GET", "/api/datasets"),
  dataset: (name: string) => request<DatasetOverview>("GET", `/api/datasets/${enc(name)}`),
  deleteDataset: (name: string) => request<unknown>("DELETE", `/api/datasets/${enc(name)}`),
  downloadUrl: (name: string) => `/api/datasets/${enc(name)}/download`,
  reference: () => request<ReferenceStatus>("GET", "/api/reference"),
  generateReference: () => request<Job>("POST", "/api/reference"),
  compare: (name: string, reference?: string) =>
    request<Comparison>(
      "GET",
      `/api/datasets/${enc(name)}/compare${reference ? `?reference=${enc(reference)}` : ""}`,
    ),
  element: (name: string, type: string, element: string) =>
    request<ElementDetails>("GET", `/api/datasets/${enc(name)}/elements/${enc(type)}/${enc(element)}`),
  // the values of an attribute in every year, i.e. times its yearly variation
  yearly: (name: string, type: string, element: string, attribute: string) =>
    request<(DataFile & { source?: "data" | "default" }) | { kind: "separate" }>(
      "GET",
      `/api/datasets/${enc(name)}/elements/${enc(type)}/${enc(element)}/yearly/${enc(attribute)}`,
    ),
  data: (name: string, type: string, element: string, file: string) =>
    request<DataFile>(
      "GET",
      `/api/datasets/${enc(name)}/elements/${enc(type)}/${enc(element)}/data/${enc(file)}`,
    ),
};
