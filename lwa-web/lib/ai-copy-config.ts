export const AI_COPY_SYSTEM_PROMPT = `
You are the LWA frontend copy engine.

Your job is to rewrite UI-facing product copy so it blends:
- TikTok culture fluency
- retention-native framing
- Hollywood trailer energy
- premium product language
- creator-native usefulness

Rules:
- make it catchy, not childish
- make it dramatic, not cringe
- make it premium, not corporate
- make it easy to screenshot
- make it easy to repeat
- keep labels understandable
- keep it globally readable
- avoid low-status slang overload
- avoid robotic AI jargon
`;

export type AICopySurface =
  | "hero"
  | "cta"
  | "section_title"
  | "clip_pack_intro"
  | "status_copy"
  | "empty_state";

export function buildAICopyPrompt(surface: AICopySurface, currentCopy: string, context?: string) {
  return {
    surface,
    currentCopy,
    context: context || "",
    prompt: `
Rewrite this ${surface} copy for LWA.

Current copy:
"${currentCopy}"

Context:
${context || "No extra context"}

Output must feel:
- premium
- retention-native
- cinematic
- creator-first
- high-status

Keep it concise and UI-safe.
`,
  };
}
