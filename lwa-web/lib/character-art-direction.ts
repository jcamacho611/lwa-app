import type { GodName } from "./character-controller";

export const SPINE_LAYER_PLAN = [
  "root",
  "body",
  "hip",
  "spine",
  "chest",
  "neck",
  "head",
  "hair_front",
  "hair_back",
  "brow_L",
  "brow_R",
  "eye_white_L",
  "eye_white_R",
  "pupil_L",
  "pupil_R",
  "eyelid_upper_L",
  "eyelid_upper_R",
  "eyelid_lower_L",
  "eyelid_lower_R",
  "mouth_neutral",
  "mouth_open",
  "mouth_small",
  "shoulder_L",
  "shoulder_R",
  "arm_upper_L",
  "arm_lower_L",
  "hand_L",
  "arm_upper_R",
  "arm_lower_R",
  "hand_R",
  "cloth_front",
  "cloth_back",
  "cape",
  "armor_overlay",
  "glow_eye",
  "glow_aura",
  "fx_gold",
  "fx_blue",
  "fx_crimson",
] as const;

type CharacterDirection = {
  silhouette: string;
  emissive: string;
  armor: string;
  aura: string;
  productRole: string;
  layerNotes: string;
  animationNotes: string;
  performanceNotes: string;
};

const DEFAULT_DIRECTION: CharacterDirection = {
  silhouette: "edge-framing mythic guardian",
  emissive: "gold intelligence glow",
  armor: "black robes with restrained gold geometry",
  aura: "low-opacity edge aura",
  productRole: "ambient product companion",
  layerNotes: "separate face, eyes, mouth, hands, robe front, robe back, armor overlay, glow slots",
  animationNotes: "slow idle breathe, alert lean, short speak loop, restrained react",
  performanceNotes: "single atlas, no more than two active characters, suspend off-screen",
};

export const CHARACTER_DIRECTIONS: Partial<Record<GodName, CharacterDirection>> = {
  athena: {
    silhouette: "tall balanced strategist, narrow crown line, clean shoulders, readable face triangle",
    emissive: "silver-blue eyes, thin gold interface rim, low pulse while advising",
    armor: "matte black breastplate, muted gold filigree, layered strategist robe panels",
    aura: "precise blue intelligence haze behind head and shoulders, restrained gold halo edge",
    productRole: "source input, strategy, recommendation",
    layerNotes: "keep head, eyes, brows, mouth, robe panels, hand, shoulder armor, blue eye glow, gold halo as independent Spine slots",
    animationNotes: "idle breath is calm, alert is a subtle head tilt, speak uses small mouth shapes, react sharpens eyes only",
    performanceNotes: "blue glow should be additive but capped; no full-screen aura or particle sheets",
  },
  hades: {
    silhouette: "broad underworld judge, heavy vertical robe fall, dense shoulder mass, low crown shadow",
    emissive: "tight crimson eye burn, muted gold edge light, no decorative neon",
    armor: "black plate under shadow robes, dark crimson lining, sparse gold trim on collar and wrists",
    aura: "low underworld haze anchored below chest, minimal but dangerous",
    productRole: "review, discipline, export truth, low-credit warning",
    layerNotes: "separate hood shadow, eyes, mouth, collar plate, robe front, robe back, hand, crimson eye glow, underworld haze",
    animationNotes: "idle breath is slower than Athena, alert lowers chin, speak is minimal mouth motion, react increases eye burn",
    performanceNotes: "crimson aura stays local to edge silhouette; never bleeds into center product UI",
  },
};

export function getCharacterDirection(god: GodName) {
  return CHARACTER_DIRECTIONS[god] || DEFAULT_DIRECTION;
}
