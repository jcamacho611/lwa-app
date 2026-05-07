export type LeeWuhAssetKind =
  | "character"
  | "sword"
  | "background"
  | "aura"
  | "combined_reference"
  | "blender_source"
  | "glb_runtime"
  | "spine_source"
  | "ui_reference";

export type LeeWuhAssetStatus = "approved" | "placeholder" | "deprecated";

export type LeeWuhRuntimeSafety = "runtime-safe" | "source-only" | "mixed-layer" | "future-source";

export type LeeWuhAssetRegistryItem = {
  id: string;
  kind: LeeWuhAssetKind;
  title: string;
  description: string;
  publicPath: string;
  sourcePath: string;
  hasCharacter: boolean;
  hasSword: boolean;
  hasAura: boolean;
  transparent: boolean;
  runtimeReady: boolean;
  blenderReady: boolean;
  spineReady: boolean;
  status: LeeWuhAssetStatus;
  acceptedUse: string[];
  rejectionRisk: string;
};

export type LeeWuhAssetValidation = {
  isValid: boolean;
  safety: LeeWuhRuntimeSafety;
  warnings: string[];
};

const canonicalAssetRegistry: LeeWuhAssetRegistryItem[] = [
  {
    id: "lee-wuh-character-transparent",
    kind: "character",
    title: "Lee-Wuh Character Cutout",
    description: "Transparent character layer for the living agent, loading states, and hero overlays.",
    publicPath: "/brand/lee-wuh/lee-wuh-character-transparent.png",
    sourcePath: "brand-source/lee-wuh/separated-assets/lee-wuh-character-transparent.png",
    hasCharacter: true,
    hasSword: false,
    hasAura: false,
    transparent: true,
    runtimeReady: true,
    blenderReady: true,
    spineReady: false,
    status: "approved",
    acceptedUse: [
      "living agent layer",
      "loading state",
      "hero overlay",
      "blender reference",
    ],
    rejectionRisk: "Fails if the sword or aura gets baked back into the character layer.",
  },
  {
    id: "lee-wuh-world-background",
    kind: "background",
    title: "Lee-Wuh World Background",
    description: "Character-free backdrop for the realm, generate shell, and brand atmosphere.",
    publicPath: "/brand/lee-wuh/backgrounds/lee-wuh-world-background.png",
    sourcePath: "brand-source/lee-wuh/separated-assets/lee-wuh-world-background.png",
    hasCharacter: false,
    hasSword: false,
    hasAura: false,
    transparent: false,
    runtimeReady: true,
    blenderReady: false,
    spineReady: false,
    status: "approved",
    acceptedUse: [
      "world backdrop",
      "realm environment",
      "hero background",
      "ui backdrop",
    ],
    rejectionRisk: "Fails if foreground character or sword elements are baked into the layer.",
  },
  {
    id: "lee-wuh-realm-sword",
    kind: "sword",
    title: "Realm Blade Prop",
    description: "Standalone sword prop for animation, CTA accents, and power-state surfaces.",
    publicPath: "/brand/lee-wuh/props/lee-wuh-realm-sword.png",
    sourcePath: "brand-source/lee-wuh/separated-assets/lee-wuh-realm-sword.png",
    hasCharacter: false,
    hasSword: true,
    hasAura: false,
    transparent: true,
    runtimeReady: true,
    blenderReady: true,
    spineReady: false,
    status: "approved",
    acceptedUse: [
      "prop layer",
      "power-state accent",
      "cta accent",
      "weapon reference",
    ],
    rejectionRisk: "Fails if Lee-Wuh's body or aura are merged into the prop.",
  },
  {
    id: "lee-wuh-aura-transparent",
    kind: "aura",
    title: "Lee-Wuh Aura Layer",
    description: "Aura-only layer for stage glow, loading energy, and the living agent edge.",
    publicPath: "/brand/lee-wuh/characters/lee-wuh-transparent-aura.png",
    sourcePath: "brand-source/lee-wuh/cutouts/lee-wuh-transparent-aura.png",
    hasCharacter: false,
    hasSword: false,
    hasAura: true,
    transparent: true,
    runtimeReady: true,
    blenderReady: false,
    spineReady: false,
    status: "approved",
    acceptedUse: [
      "aura layer",
      "loading glow",
      "stage accent",
      "foreground energy",
    ],
    rejectionRisk: "Fails if it becomes a combined character/sword image instead of aura-only.",
  },
  {
    id: "lee-wuh-character-world-reference",
    kind: "combined_reference",
    title: "Character / World Reference",
    description: "Master composition reference for Lee-Wuh proportions, colors, sword placement, and world tone.",
    publicPath: "/brand/lee-wuh/references/lee-wuh-master-character-world.png",
    sourcePath: "brand-source/lee-wuh/references/lee-wuh-master-character-world.png",
    hasCharacter: true,
    hasSword: true,
    hasAura: true,
    transparent: false,
    runtimeReady: false,
    blenderReady: true,
    spineReady: false,
    status: "approved",
    acceptedUse: [
      "master reference",
      "proportion guide",
      "blender modeling truth",
      "asset QA reference",
    ],
    rejectionRisk: "Fails as runtime art because it mixes layers intentionally.",
  },
  {
    id: "lee-wuh-blender-blockout",
    kind: "blender_source",
    title: "Character Blockout Blender File",
    description: "Source Blender file for the character modeling pipeline.",
    publicPath: "/brand-source/lee-wuh/blender/lee-wuh-character-blockout.blend",
    sourcePath: "brand-source/lee-wuh/blender/lee-wuh-character-blockout.blend",
    hasCharacter: true,
    hasSword: false,
    hasAura: false,
    transparent: false,
    runtimeReady: false,
    blenderReady: true,
    spineReady: false,
    status: "approved",
    acceptedUse: [
      "blender source",
      "blockout reference",
      "modeling handoff",
    ],
    rejectionRisk: "Should never be shipped as runtime public art.",
  },
  {
    id: "lee-wuh-mascot-glb",
    kind: "glb_runtime",
    title: "Lee-Wuh Mascot GLB",
    description: "Runtime 3D mascot export for preview and future in-app character scenes.",
    publicPath: "/brand/lee-wuh/3d/lee-wuh-mascot.glb",
    sourcePath: "brand-source/lee-wuh/blender/lee-wuh-character-blockout.blend",
    hasCharacter: true,
    hasSword: false,
    hasAura: false,
    transparent: false,
    runtimeReady: true,
    blenderReady: true,
    spineReady: false,
    status: "approved",
    acceptedUse: [
      "runtime preview",
      "3d character shell",
      "future scene layer",
    ],
    rejectionRisk: "Should stay separated from sword and aura exports.",
  },
  {
    id: "lee-wuh-world-background-glb",
    kind: "glb_runtime",
    title: "World Background GLB",
    description: "Runtime 3D world asset for the backdrop layer and future world scenes.",
    publicPath: "/brand/lee-wuh/backgrounds/lee-wuh-world-background.glb",
    sourcePath: "brand-source/lee-wuh/separated-assets/lee-wuh-world-background.glb",
    hasCharacter: false,
    hasSword: false,
    hasAura: false,
    transparent: false,
    runtimeReady: true,
    blenderReady: true,
    spineReady: false,
    status: "approved",
    acceptedUse: [
      "runtime backdrop",
      "world scene",
      "preview environment",
    ],
    rejectionRisk: "Should not include the character or sword baked into the scene.",
  },
  {
    id: "lee-wuh-realm-sword-glb",
    kind: "glb_runtime",
    title: "Realm Sword GLB",
    description: "Runtime 3D sword export for the prop layer and future weapon states.",
    publicPath: "/brand/lee-wuh/models/weapons/lwa_fantasy_sword_no_aura.glb",
    sourcePath: "brand-source/lee-wuh/models/weapons/lwa_fantasy_sword_no_aura.glb",
    hasCharacter: false,
    hasSword: true,
    hasAura: false,
    transparent: false,
    runtimeReady: true,
    blenderReady: true,
    spineReady: false,
    status: "approved",
    acceptedUse: [
      "runtime weapon",
      "prop preview",
      "future animation shell",
    ],
    rejectionRisk: "Should remain sword-only and not merge with the character body.",
  },
  {
    id: "lee-wuh-spine-source-future",
    kind: "spine_source",
    title: "Future Spine Source",
    description: "Placeholder registry entry for future Spine body-part animation assets.",
    publicPath: "/brand/lee-wuh/spine/lee-wuh-spine-source.json",
    sourcePath: "brand-source/lee-wuh/spine/lee-wuh-spine-source.json",
    hasCharacter: true,
    hasSword: false,
    hasAura: false,
    transparent: false,
    runtimeReady: false,
    blenderReady: false,
    spineReady: true,
    status: "placeholder",
    acceptedUse: [
      "future spine source",
      "body-part animation planning",
    ],
    rejectionRisk: "Not implemented yet. Do not treat as shipping runtime content.",
  },
  {
    id: "lee-wuh-ui-reference",
    kind: "ui_reference",
    title: "Mobile UI Reference",
    description: "Layout reference for the Lee-Wuh mobile surface and generate shell.",
    publicPath: "/brand/lee-wuh/ui/lee-wuh-mobile-ui-reference.png",
    sourcePath: "brand-source/lee-wuh/references/lee-wuh-mobile-ui-reference.png",
    hasCharacter: false,
    hasSword: false,
    hasAura: false,
    transparent: false,
    runtimeReady: false,
    blenderReady: false,
    spineReady: false,
    status: "approved",
    acceptedUse: [
      "layout reference",
      "mobile direction",
      "generate shell planning",
    ],
    rejectionRisk: "Should not be treated as a runtime UI replacement.",
  },
];

function safetyForAsset(asset: LeeWuhAssetRegistryItem): LeeWuhRuntimeSafety {
  if (asset.kind === "blender_source") {
    return "source-only";
  }
  if (asset.kind === "spine_source") {
    return "future-source";
  }
  if (asset.kind === "combined_reference") {
    return "mixed-layer";
  }
  if (asset.runtimeReady) {
    return "runtime-safe";
  }
  return "source-only";
}

export function validateLeeWuhAssetLayerTruth(
  asset: LeeWuhAssetRegistryItem,
): LeeWuhAssetValidation {
  const warnings: string[] = [];

  if (asset.kind === "background") {
    if (asset.hasCharacter) warnings.push("Background asset includes a character layer.");
    if (asset.hasSword) warnings.push("Background asset includes a sword layer.");
    if (asset.hasAura) warnings.push("Background asset includes an aura layer.");
  }

  if (asset.kind === "character" && !asset.transparent) {
    warnings.push("Character asset should be transparent.");
  }

  if (asset.kind === "sword" && asset.hasCharacter) {
    warnings.push("Sword asset should not include the character body.");
  }

  if (asset.kind === "aura" && (asset.hasCharacter || asset.hasSword)) {
    warnings.push("Aura asset should not include character or sword layers.");
  }

  if (asset.kind === "combined_reference" && asset.runtimeReady) {
    warnings.push("Combined reference should not be treated as runtime-safe.");
  }

  if (asset.kind === "blender_source" && asset.runtimeReady) {
    warnings.push("Blender source should not be marked runtime-ready.");
  }

  const safety = safetyForAsset(asset);
  const isValid = warnings.length === 0;

  return { isValid, safety, warnings };
}

export const leeWuhAssetRegistry = canonicalAssetRegistry;

export function getApprovedLeeWuhAssets(): LeeWuhAssetRegistryItem[] {
  return leeWuhAssetRegistry.filter((asset) => asset.status === "approved");
}

export function getLeeWuhAssetsByKind(kind: LeeWuhAssetKind): LeeWuhAssetRegistryItem[] {
  return leeWuhAssetRegistry.filter((asset) => asset.kind === kind);
}

export function getRuntimeReadyLeeWuhAssets(): LeeWuhAssetRegistryItem[] {
  return leeWuhAssetRegistry.filter((asset) => asset.runtimeReady);
}

export function getLeeWuhAssetById(id: string): LeeWuhAssetRegistryItem | null {
  return leeWuhAssetRegistry.find((asset) => asset.id === id) ?? null;
}

