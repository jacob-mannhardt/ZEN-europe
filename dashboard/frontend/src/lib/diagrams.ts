// Mermaid flowcharts of the carrier flows, as on the model structure pages of
// the ZEN-europe documentation (docs/model_structure_docs.py).

import type { Structure } from "./api";

export const TECHNOLOGY_TYPES: Record<string, string> = {
  conversion_technology: "Conversion technologies",
  retrofitting_technology: "Retrofitting technologies",
  storage_technology: "Storage technologies",
  transport_technology: "Transport technologies",
};

const NODE_SHAPES: Record<string, string> = {
  carrier: "stadium",
  conversion_technology: "rect",
  retrofitting_technology: "notch-rect",
  storage_technology: "cyl",
  transport_technology: "lean-r",
};

export const LEGEND =
  "Rounded nodes are carriers, boxes are conversion technologies, boxes with a cut corner are " +
  "retrofitting technologies, cylinders are storage technologies and parallelograms are transport " +
  "technologies. A retrofitting technology shares a box with the technology it retrofits.";

/** A mermaid id for an element, e.g. c_electricity or t_run_of_river_hydro. */
export function nodeId(name: string, type: string): string {
  return (type === "carrier" ? "c_" : "t_") + name.replace(/[^A-Za-z0-9_]/g, "_");
}

export function sortNames(names: Iterable<string>): string[] {
  return [...names].sort((a, b) => a.toLowerCase().localeCompare(b.toLowerCase()));
}

function nodeLines(
  name: string,
  type: string,
  ownElements: string[] | null,
  highlight: string[],
): string[] {
  const id = nodeId(name, type);
  const lines = [`  ${id}@{ shape: ${NODE_SHAPES[type]}, label: "${name}" }`];
  if (ownElements && !ownElements.includes(name)) lines.push(`  class ${id} external`);
  if (highlight.includes(name)) lines.push(`  class ${id} highlight`);
  return lines;
}

/** The carrier flows of technologies, with their input and output carriers. */
export function flowDiagram(
  techNames: string[],
  structure: Structure,
  carriers: string[] = [],
  ownElements: string[] | null = null,
  highlight: string[] = [],
): string {
  const technologies = structure.technologies;
  const nodes = new Map<string, string>(carriers.map((c) => [c, "carrier"]));
  const retrofits = new Map<string, string[]>();
  const edges: string[] = [];

  for (const name of techNames) {
    const tech = technologies[name];
    nodes.set(name, tech.type);
    const t = nodeId(name, tech.type);
    if (tech.input_carrier) {
      for (const c of tech.input_carrier) {
        if (!nodes.has(c)) nodes.set(c, "carrier");
        edges.push(`${nodeId(c, "carrier")} --> ${t}`);
      }
      for (const c of tech.output_carrier ?? []) {
        if (!nodes.has(c)) nodes.set(c, "carrier");
        edges.push(`${t} --> ${nodeId(c, "carrier")}`);
      }
    } else {
      for (const c of tech.reference_carrier) {
        if (!nodes.has(c)) nodes.set(c, "carrier");
        edges.push(`${nodeId(c, "carrier")} <--> ${t}`);
      }
    }
    const base = tech.base_technology;
    if (base && technologies[base]) retrofits.set(base, [...(retrofits.get(base) ?? []), name]);
  }

  const lines = [
    "flowchart LR",
    "  classDef external stroke-dasharray: 4 4,fill:transparent",
    "  classDef highlight stroke-width:3px",
  ];
  const nested = new Set([...retrofits.values()].flat());
  for (const [node, type] of nodes) {
    if (!nested.has(node) && !retrofits.has(node)) lines.push(...nodeLines(node, type, ownElements, highlight));
  }
  // a technology and its retrofits share a box
  for (const [base, names] of retrofits) {
    const group = `g_${nodeId(base, "technology")}`;
    lines.push(`  subgraph ${group} [" "]`);
    lines.push(...nodeLines(base, technologies[base].type, ownElements, highlight));
    for (const name of names) lines.push(...nodeLines(name, nodes.get(name)!, ownElements, highlight));
    lines.push("  end");
    if (ownElements && !ownElements.includes(base)) lines.push(`  style ${group} stroke-dasharray: 4 4`);
  }
  return [...lines, ...edges.map((e) => `  ${e}`)].join("\n");
}

/** The carriers that are converted into each other. */
export function carrierFlowDiagram(structure: Structure): string {
  const lines = ["flowchart LR"];
  for (const name of sortNames(Object.keys(structure.carriers))) {
    lines.push(...nodeLines(name, "carrier", null, []));
  }
  for (const [source, target] of structure.carrier_flows) {
    lines.push(`  ${nodeId(source, "carrier")} --> ${nodeId(target, "carrier")}`);
  }
  return lines.join("\n");
}

export function sectorDiagram(name: string, structure: Structure): string {
  const sector = structure.sectors[name];
  const techs = sortNames(sector.elements.filter((e) => e in structure.technologies));
  const carriers = sector.elements.filter((e) => e in structure.carriers);
  return flowDiagram(techs, structure, carriers, sector.elements);
}

export function technologyDiagram(name: string, structure: Structure): string {
  return flowDiagram([name], structure, [], null, structure.technologies[name].reference_carrier);
}

/** A carrier with every technology that produces, consumes, stores or transports it. */
export function carrierDiagram(name: string, structure: Structure): string {
  const carrier = structure.carriers[name];
  const techs = sortNames(
    new Set([...carrier.produced_by, ...carrier.consumed_by, ...carrier.stored_by, ...carrier.transported_by]),
  );
  return flowDiagram(techs, structure, [name], null, [name]);
}

/** Map the mermaid ids of a structure back to element names. */
export function idIndex(structure: Structure): Map<string, { name: string; kind: "carrier" | "technology" }> {
  const index = new Map<string, { name: string; kind: "carrier" | "technology" }>();
  for (const name of Object.keys(structure.carriers)) index.set(nodeId(name, "carrier"), { name, kind: "carrier" });
  for (const name of Object.keys(structure.technologies))
    index.set(nodeId(name, "technology"), { name, kind: "technology" });
  return index;
}
