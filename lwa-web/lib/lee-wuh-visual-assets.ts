export type LeeWuhVisualAssetStatus =
  | "ready-reference"
  | "ready-background"
  | "production-candidate"
  | "fallback";

export type LeeWuhVisualAssetRole =
  | "master-character-world"
  | "world-background"
  | "ui-reference"
  | "character-cutout"
  | "sword-prop"
  | "fallback";

export type LeeWuhVisualAsset = {
  id: string;
  title: string;
  role: LeeWuhVisualAssetRole;
  status: LeeWuhVisualAssetStatus;
  publicPath: string;
  sourcePath?: string;
  useAs: string[];
  doNotUseAs: string[];
  note: string;
};

export const leeWuhVisualAssetPaths = {
  masterCharacterWorld: "/brand/lee-wuh/references/lee-wuh-master-character-world.png",
  emptyWorldBackground: "/brand/lee-wuh/backgrounds/lee-wuh-empty-world-background.png",
  mobileUiReference: "/brand/lee-wuh/ui/lee-wuh-mobile-ui-reference.png",
  characterCutout: "/brand/lee-wuh/lee-wuh-character-transparent.png",
  swordProp: "/brand/lee-wuh/props/lee-wuh-realm-sword.png",
  fallbackHero: "/brand/lee-wuh-hero-16x9.svg",
} as const;

export const leeWuhVisualSourcePaths = {
  masterCharacterWorld: "brand-source/lee-wuh/references/lee-wuh-master-character-world.png",
  emptyWorldBackground: "brand-source/lee-wuh/references/lee-wuh-empty-world-background.png",
  mobileUiReference: "brand-source/lee-wuh/references/lee-wuh-mobile-ui-reference.png",
  characterCutout: "brand-source/lee-wuh/separated-assets/lee-wuh-character-transparent.png",
  swordProp: "brand-source/lee-wuh/separated-assets/lee-wuh-realm-sword.png",
} as const;

export const leeWuhVisualAssets = {
  masterCharacterWorld: {
    id: "lee-wuh-master-character-world",
    title: "Character/world reference",
    role: "master-character-world",
    status: "ready-reference",
    publicPath: leeWuhVisualAssetPaths.masterCharacterWorld,
    sourcePath: leeWuhVisualSourcePaths.masterCharacterWorld,
    useAs: [
      "Master Lee-Wuh character reference",
      "Hero composition reference",
      "Blender and GLB modeling truth",
      "Color, outfit, sword, dreadlock, eye, and aura direction",
    ],
    doNotUseAs: [
      "Permanent flat app background",
      "Only character implementation",
      "Replacement for separated transparent character and sword assets",
    ],
    note:
      "Use this to keep Lee-Wuh visually consistent. Do not paste it into the app as the whole UI.",
  },
  emptyWorldBackground: {
    id: "lee-wuh-empty-world-background",
    title: "Usable background layer",
    role: "world-background",
    status: "ready-background",
    publicPath: leeWuhVisualAssetPaths.emptyWorldBackground,
    sourcePath: leeWuhVisualSourcePaths.emptyWorldBackground,
    useAs: [
      "Homepage and generate world backdrop",
      "Lee-Wuh stage background",
      "Realm, game, and portal environment",
      "Blurred or parallax CSS layer behind functional UI",
    ],
    doNotUseAs: [
      "Small thumbnail only",
      "Foreground character layer",
      "A layer that makes URL input or results unreadable",
    ],
    note:
      "This is the safest live frontend background because it leaves room for real UI and separate character layers.",
  },
  mobileUiReference: {
    id: "lee-wuh-mobile-ui-reference",
    title: "UI reference only",
    role: "ui-reference",
    status: "ready-reference",
    publicPath: leeWuhVisualAssetPaths.mobileUiReference,
    sourcePath: leeWuhVisualSourcePaths.mobileUiReference,
    useAs: [
      "Mobile-first layout reference",
      "Header, credits pill, greeting, input, CTA, card, and bottom-nav direction",
      "Future real React component blueprint",
    ],
    doNotUseAs: [
      "Static screenshot pasted into the app",
      "Replacement for real generate/home components",
      "Fake non-functional UI",
    ],
    note:
      "Treat this as the design target for a real mobile-first route, not as product output.",
  },
  futureCharacterCutout: {
    id: "lee-wuh-character-cutout",
    title: "Transparent character cutout candidate",
    role: "character-cutout",
    status: "production-candidate",
    publicPath: leeWuhVisualAssetPaths.characterCutout,
    sourcePath: leeWuhVisualSourcePaths.characterCutout,
    useAs: [
      "Separate Lee-Wuh foreground layer",
      "Living agent avatar and hover state",
      "Loading, assistant, and guide surface",
      "Future rigging/modeling reference",
    ],
    doNotUseAs: [
      "World background",
      "Sword prop replacement",
      "Final GLB source",
    ],
    note:
      "No-sword/no-aura production candidate is present. It still needs trim, matte, and transparency QA before heavy UI usage.",
  },
  futureSwordProp: {
    id: "lee-wuh-realm-sword-prop",
    title: "Separate Realm Blade prop candidate",
    role: "sword-prop",
    status: "production-candidate",
    publicPath: leeWuhVisualAssetPaths.swordProp,
    sourcePath: leeWuhVisualSourcePaths.swordProp,
    useAs: [
      "Separate sword prop layer",
      "CTA and power-state accent",
      "Game item and Realm Blade reference",
      "Future Blender prop modeling source",
    ],
    doNotUseAs: [
      "Character layer",
      "Only source of Lee-Wuh identity",
      "Claim that a rigged weapon model exists",
    ],
    note:
      "Sword candidate is separated from Lee-Wuh conceptually. Keep it animated, hidden, or exported independently later.",
  },
  fallbackHero: {
    id: "lee-wuh-fallback-hero",
    title: "Fallback hero",
    role: "fallback",
    status: "fallback",
    publicPath: leeWuhVisualAssetPaths.fallbackHero,
    useAs: [
      "Build-safe fallback when any PNG reference is missing",
      "Temporary visual continuity",
    ],
    doNotUseAs: [
      "Final character cutout",
      "Final background layer",
      "Blender source truth",
    ],
    note:
      "Keep this fallback active so missing image files do not break the frontend.",
  },
} as const satisfies Record<string, LeeWuhVisualAsset>;

export const leeWuhReferenceAssets = [
  leeWuhVisualAssets.masterCharacterWorld,
  leeWuhVisualAssets.emptyWorldBackground,
  leeWuhVisualAssets.mobileUiReference,
];

export const leeWuhProductionCandidateAssets = [
  leeWuhVisualAssets.futureCharacterCutout,
  leeWuhVisualAssets.futureSwordProp,
];

export const leeWuhVisualAssetList = [
  ...leeWuhReferenceAssets,
  ...leeWuhProductionCandidateAssets,
  leeWuhVisualAssets.fallbackHero,
];
