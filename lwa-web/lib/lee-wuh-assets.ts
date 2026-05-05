export type LeeWuhAssetKind = "character" | "background" | "prop" | "reference";

export type LeeWuhAssetStatus = "ready" | "placeholder" | "needs-replacement";

export type LeeWuhAsset = {
  id: string;
  kind: LeeWuhAssetKind;
  title: string;
  description: string;
  publicPath: string;
  sourcePath: string;
  expectedUse: string[];
  status: LeeWuhAssetStatus;
};

export const leeWuhAssetFallback = "/brand/lee-wuh-hero-16x9.svg";

export const leeWuhExpectedPublicPaths = {
  character: "/brand/lee-wuh/lee-wuh-character-transparent.png",
  background: "/brand/lee-wuh/backgrounds/lee-wuh-world-background.png",
  sword: "/brand/lee-wuh/props/lee-wuh-realm-sword.png",
};

export const leeWuhExpectedSourcePaths = {
  character: "brand-source/lee-wuh/separated-assets/lee-wuh-character-transparent.png",
  background: "brand-source/lee-wuh/separated-assets/lee-wuh-world-background.png",
  sword: "brand-source/lee-wuh/separated-assets/lee-wuh-realm-sword.png",
};

export const leeWuhReferencePaths = {
  main: "brand-source/lee-wuh/references/lee-wuh-main-reference.png",
  turnaround: "brand-source/lee-wuh/references/lee-wuh-turnaround-reference.png",
  threeDReady: "brand-source/lee-wuh/references/lee-wuh-3d-ready-reference.png",
};

export const leeWuhSeparatedAssets: LeeWuhAsset[] = [
  {
    id: "lee-wuh-character-transparent",
    kind: "character",
    title: "Lee-Wuh Character Cutout",
    description:
      "Transparent character-only asset used for the living agent, loading states, hero overlays, game avatar, and Blender/model reference.",
    publicPath: leeWuhExpectedPublicPaths.character,
    sourcePath: leeWuhExpectedSourcePaths.character,
    expectedUse: [
      "Floating living agent",
      "Homepage hero overlay",
      "Loading/processing state",
      "Game avatar reference",
      "Blender modeling reference",
    ],
    status: "needs-replacement",
  },
  {
    id: "lee-wuh-world-background",
    kind: "background",
    title: "Lee-Wuh World Background",
    description:
      "Character-free environment layer used behind the frontend, realm/game pages, Company OS atmosphere, and animated video-like page background.",
    publicPath: leeWuhExpectedPublicPaths.background,
    sourcePath: leeWuhExpectedSourcePaths.background,
    expectedUse: [
      "World backdrop",
      "Realm/game environment",
      "Hero background",
      "Animated CSS/video-like background",
      "Marketplace atmosphere",
    ],
    status: "needs-replacement",
  },
  {
    id: "lee-wuh-realm-sword",
    kind: "prop",
    title: "Realm Blade Sword Prop",
    description:
      "Transparent sword-only prop used for animation, UI badges, power states, game items, loading effects, and Blender prop modeling.",
    publicPath: leeWuhExpectedPublicPaths.sword,
    sourcePath: leeWuhExpectedSourcePaths.sword,
    expectedUse: [
      "Game item prop",
      "CTA hover effect",
      "Realm portal visual",
      "Blender weapon reference",
      "Marketplace badge/icon",
    ],
    status: "needs-replacement",
  },
];

export const leeWuhProductionTargets = [
  {
    title: "Layered frontend composition",
    detail:
      "Use background as the base, character cutout as animated foreground, and sword as a separate prop layer.",
  },
  {
    title: "Living agent behavior",
    detail:
      "The character layer should breathe, hover, blink, react to clicks, and open a speech/options panel.",
  },
  {
    title: "Blender modeling source",
    detail:
      "Use separated character and sword references to model Lee-Wuh as a rigged GLB later.",
  },
  {
    title: "Fallback-safe app shell",
    detail:
      "The app must build even before the final PNG assets are committed.",
  },
];

export const leeWuhBlenderNextSteps = [
  "Replace placeholder paths with final separated transparent PNGs.",
  "Use the character and sword references for Blender blockout proportions and prop modeling.",
  "Export an optimized GLB only after the static separated layers are stable.",
  "Keep SVG/PNG fallback behavior active when GLB or production PNGs are missing.",
];
