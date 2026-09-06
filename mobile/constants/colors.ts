/**
 * Blush Apothecary palette.
 *
 * Use these names directly. They are the only colors the design system
 * recognises. If a screen needs a new shade, add it here, not inline.
 *
 * Old dispensary keys (pine/dispensary/sage/...) are kept as aliases so
 * existing screens keep working — they now point at pink values.
 */
export const colors = {
  // Blush ground
  pine: "#4A1F33",
  dispensary: "#DB2777",
  paper: "#FFF5F7",
  surface: "#FFFFFF",
  sage: "#FCE7EE",
  line: "#F4C6D7",
  amber: "#E893A8",
  oxblood: "#8E2A2A",
  moss: "#F0A6BE",
  slateBlue: "#8A4A64",

  // Friendly aliases — prefer these in new code
  blush: "#FFF5F7",
  petal: "#FCE7EE",
  rose: "#DB2777",
  plum: "#4A1F33",
  peach: "#E893A8",
  glow: "#F472A6",

  // Neutrals (sparse — plum carries hierarchy, petal carries surface)
  white: "#FFFFFF",
  background: "#FFF5F7", // alias of blush — keep for screens that read "background"
  textPrimary: "#4A1F33",
  textSecondary: "#7A4A5E",
  textTertiary: "#B08A99",
};

/**
 * Per-condition accents. Keyed by canonical display name; use
 * `conditionColor(name)` for case-insensitive lookup so backend
 * payload casing cannot silently break the badge color.
 */
export const conditionColors: Record<string, string> = {
  Acne: "#C2185B",
  Carcinoma: "#8E2A2A",
  "Dark Spot": "#8A5A3B",
  Eczema: "#C2703D",
  Keratosis: "#7A5A8A",
  Milia: "#6B8CA8",
  Rosacea: "#E0447C",
};

const CONDITION_COLOR_INDEX: Record<string, string> = Object.fromEntries(
  Object.entries(conditionColors).map(([k, v]) => [k.toLowerCase(), v]),
);

/** Case-insensitive lookup. Falls back to `textSecondary` if unknown. */
export function conditionColor(name: string | null | undefined): string {
  if (!name) return colors.textSecondary;
  return CONDITION_COLOR_INDEX[name.toLowerCase().trim()] ?? colors.textSecondary;
}
