// Chart colors: a validated categorical order for highlighted series and a
// single-hue blue ramp for magnitudes (maps), in light and dark mode.

const dark = () => window.matchMedia("(prefers-color-scheme: dark)").matches;

const CATEGORICAL_LIGHT = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#6250d6", "#e34948"];
const CATEGORICAL_DARK = ["#3987e5", "#d95926", "#199e70", "#c98500", "#d55181", "#008300", "#9085e9", "#e66767"];

export const MAX_HIGHLIGHTED = CATEGORICAL_LIGHT.length;

export function categorical(slot: number): string {
  return (dark() ? CATEGORICAL_DARK : CATEGORICAL_LIGHT)[slot % MAX_HIGHLIGHTED];
}

// sequential blue, near zero to high
const RAMP = ["#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5", "#256abf", "#184f95", "#0d366b"];
const RAMP_DARK = ["#184f95", "#1c5cab", "#256abf", "#2a78d6", "#5598e7", "#86b6ef", "#cde2fb"];

export function sequentialScale(): [number, string][] {
  const ramp = dark() ? RAMP_DARK : RAMP;
  return ramp.map((color, i) => [i / (ramp.length - 1), color]);
}

function hexToRgb(hex: string): [number, number, number] {
  const n = parseInt(hex.slice(1), 16);
  return [(n >> 16) & 255, (n >> 8) & 255, n & 255];
}

/** The ramp color at t in [0, 1]. */
export function sequentialColor(t: number): string {
  const ramp = dark() ? RAMP_DARK : RAMP;
  const x = Math.min(1, Math.max(0, t)) * (ramp.length - 1);
  const i = Math.min(ramp.length - 2, Math.floor(x));
  const a = hexToRgb(ramp[i]);
  const b = hexToRgb(ramp[i + 1]);
  const f = x - i;
  return `rgb(${a.map((v, k) => Math.round(v + (b[k] - v) * f)).join(",")})`;
}

export function chrome() {
  const style = getComputedStyle(document.documentElement);
  const get = (name: string) => style.getPropertyValue(name).trim();
  return {
    surface: get("--surface"),
    ink: get("--ink"),
    ink2: get("--ink-2"),
    muted: get("--muted"),
    grid: get("--grid"),
    axis: get("--axis"),
    context: dark() ? "rgba(195,194,183,0.28)" : "rgba(82,81,78,0.22)",
  };
}

// NUTS0 codes to ISO 3166-1 alpha-3, for the country map
export const ISO3: Record<string, string> = {
  AL: "ALB", AT: "AUT", BA: "BIH", BE: "BEL", BG: "BGR", CH: "CHE", CY: "CYP", CZ: "CZE", DE: "DEU",
  DK: "DNK", EE: "EST", EL: "GRC", ES: "ESP", FI: "FIN", FR: "FRA", HR: "HRV", HU: "HUN", IE: "IRL",
  IS: "ISL", IT: "ITA", LI: "LIE", LT: "LTU", LU: "LUX", LV: "LVA", ME: "MNE", MK: "MKD", MT: "MLT",
  NL: "NLD", NO: "NOR", PL: "POL", PT: "PRT", RO: "ROU", RS: "SRB", SE: "SWE", SI: "SVN", SK: "SVK",
  TR: "TUR", UK: "GBR", XK: "XKX",
};
