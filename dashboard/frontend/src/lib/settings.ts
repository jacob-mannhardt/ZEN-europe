// Resolving the settings of a model the way ZEN-creator's ModelSet does:
// the configuration file's settings, then the defaults of the models file,
// then the models a model extends (furthest ancestor first), then its own
// patch. Nested mappings are merged, any other value (lists included) replaces.

import type { ModelsDoc, Settings } from "./api";

export const DEFAULTS = "__defaults__";

type Obj = Record<string, unknown>;

export function isObject(value: unknown): value is Obj {
  return value !== null && typeof value === "object" && !Array.isArray(value);
}

export function deepMerge<T extends Obj>(base: T, patch: Obj): T {
  const merged: Obj = { ...base };
  for (const [key, value] of Object.entries(patch)) {
    const current = merged[key];
    merged[key] = isObject(value) && isObject(current) ? deepMerge(current, value) : value;
  }
  return merged as T;
}

export function equal(a: unknown, b: unknown): boolean {
  return JSON.stringify(a) === JSON.stringify(b);
}

export function clone<T>(value: T): T {
  return JSON.parse(JSON.stringify(value));
}

/** The models a model is built from, furthest ancestor first, itself last. */
export function lineage(doc: ModelsDoc, name: string): string[] {
  const chain: string[] = [];
  let current: string | null = name;
  while (current && doc.models[current] && !chain.includes(current)) {
    chain.unshift(current);
    current = doc.models[current].extends;
  }
  return chain;
}

/** The settings a model starts from before its own patch is applied. */
export function inheritedSettings(base: Settings, doc: ModelsDoc, name: string): Settings {
  if (name === DEFAULTS) return base;
  let settings = deepMerge(base, doc.defaults ?? {});
  for (const ancestor of lineage(doc, name).slice(0, -1)) {
    settings = deepMerge(settings, doc.models[ancestor].settings ?? {});
  }
  return settings;
}

/** The patch of a model, as ZEN-creator's ModelSet.settings_patch builds it. */
export function settingsPatch(doc: ModelsDoc, name: string): Settings {
  if (name === DEFAULTS) return doc.defaults ?? {};
  let patch: Settings = clone(doc.defaults ?? {});
  for (const model of lineage(doc, name)) {
    patch = deepMerge(patch, doc.models[model].settings ?? {});
  }
  return patch;
}

export function ownPatch(doc: ModelsDoc, name: string): Settings {
  return name === DEFAULTS ? doc.defaults : doc.models[name]?.settings ?? {};
}

/** Set a field in a sparse patch, removing it when it equals the inherited value. */
export function setField(
  patch: Settings,
  category: string,
  field: string,
  value: unknown,
  inherited: unknown,
): void {
  // the list settings (nodes, sectors, elements) are sets, so a list with the
  // inherited values in another order is not a change
  const sameSet =
    Array.isArray(value) && Array.isArray(inherited) && equal([...value].sort(), [...inherited].sort());
  if (sameSet || equal(value, inherited)) {
    removeField(patch, category, field);
    return;
  }
  patch[category] = { ...(patch[category] ?? {}), [field]: value };
}

export function removeField(patch: Settings, category: string, field: string): void {
  if (!patch[category]) return;
  const { [field]: _, ...rest } = patch[category];
  if (Object.keys(rest).length) patch[category] = rest;
  else delete patch[category];
}

export function countFields(patch: Settings | null | undefined): number {
  if (!patch) return 0;
  return Object.values(patch).reduce((n, category) => n + Object.keys(category ?? {}).length, 0);
}

export function formatValue(value: unknown): string {
  if (Array.isArray(value)) return value.length ? value.join(", ") : "[]";
  if (value === null || value === undefined) return "–";
  return String(value);
}
