import { WorldLayer } from "./WorldLayer";

type WorldEffectsProps = {
  variant: "workspace" | "home";
  eventKind: "scan" | "flare" | "surge";
  eventEpoch: number;
};

export function WorldEffects({ variant, eventKind, eventEpoch }: WorldEffectsProps) {
  return (
    <>
      <WorldLayer className="world-sky" />
      <div className="ai-depth-field" />
      <div className="ai-orb ai-orb-a" />
      <div className="ai-orb ai-orb-b" />
      <div className="ai-orb ai-orb-c" />
      <div className="ai-orb ai-orb-d" />
      <div className="ai-grid" />
      <div className="ai-scan-line" />

      {variant === "home" ? (
        <>
          <WorldLayer className="world-ruins" />
          <WorldLayer className="world-energy-field" />
          <div className="ai-particle-field" />
          <div className="ai-stars" />
          <div className="ai-fog ai-fog-a" />
          <div className="ai-fog ai-fog-b" />
          <div className="ai-beam ai-beam-a" />
          <div className="ai-beam ai-beam-b" />
          <div className="ai-shimmer ai-shimmer-a" />
          <WorldLayer className="world-hud world-hud-primary" />
          <WorldLayer className="world-hud world-hud-secondary" />
          <WorldLayer className="world-foreground-lights" />
          <WorldLayer className="world-foreground-particles" />
          <WorldLayer key={`${eventKind}-${eventEpoch}`} className={`world-event world-event-${eventKind}`} />
        </>
      ) : null}
    </>
  );
}
