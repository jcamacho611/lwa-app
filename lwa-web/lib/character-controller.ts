"use client";

export type GodName = "zeus" | "athena" | "hades" | "anubis" | "celestial" | "hermes";
export type CharacterState = "breathe" | "alert" | "speak" | "react";
export type CharacterSide = "left" | "right";

export type LWACharacterEvent = {
  side?: CharacterSide;
  god?: GodName;
  state?: CharacterState;
  speech?: string;
  trigger?: string;
};

const LWA_CHARACTER_EVENT = "lwa:character";

function getRendererName() {
  const canvas = document.createElement("canvas");
  const gl = canvas.getContext("webgl");
  if (!gl) return "";
  return String(gl.getParameter(gl.RENDERER) || "");
}

export function isHighEndDevice(): boolean {
  if (typeof navigator === "undefined") return false;
  const cores = navigator.hardwareConcurrency || 2;
  const isMobile = /Mobi|Android|iPhone|iPad|iPod/i.test(navigator.userAgent);
  const renderer = getRendererName();
  return cores >= 4 && !isMobile && !renderer.includes("SwiftShader");
}

export class GodCharacter {
  private currentState: CharacterState = "breathe";
  private suspended = false;
  private runtime: "spine" | "css" = "css";

  constructor(
    readonly name: GodName,
    readonly side: CharacterSide,
    private skelPath?: string,
  ) {}

  async load(canvas?: HTMLCanvasElement) {
    if (!canvas || !this.skelPath || !isHighEndDevice()) {
      this.runtime = "css";
      return this.runtime;
    }

    try {
      await import("@esotericsoftware/spine-webgl");
      this.runtime = "spine";
    } catch {
      this.runtime = "css";
    }

    this.playAnimation("breathe", true);
    return this.runtime;
  }

  setState(state: CharacterState) {
    if (this.currentState === state) return;
    this.currentState = state;
    if (!this.suspended) {
      this.playAnimation(state, state === "breathe");
    }
  }

  onUserAction() {
    this.setState("alert");
  }

  onGenerating() {
    this.setState("react");
  }

  onSpeak() {
    this.setState("speak");
  }

  onIdle() {
    this.setState("breathe");
  }

  suspend() {
    this.suspended = true;
  }

  resume() {
    this.suspended = false;
    this.playAnimation(this.currentState, this.currentState === "breathe");
  }

  getState() {
    return this.currentState;
  }

  getRuntime() {
    return this.runtime;
  }

  private playAnimation(name: CharacterState, loop: boolean) {
    if (process.env.NODE_ENV !== "production") {
      console.debug(`[LWA ${this.name}] ${this.runtime}:${name}:${loop ? "loop" : "once"}`);
    }
  }
}

export class CharacterManager {
  readonly left = new GodCharacter("athena", "left", "/brand-source/chars/athena.skel");
  readonly right = new GodCharacter("hades", "right", "/brand-source/chars/hades.skel");

  onGenerationStart() {
    this.left.onGenerating();
    this.right.onGenerating();
    emitLWACharacterEvent({ state: "react", trigger: "generation_start" });
  }

  onGenerationComplete() {
    this.left.onIdle();
    this.right.onIdle();
    emitLWACharacterEvent({ state: "breathe", trigger: "generation_complete" });
  }

  onUserAction() {
    this.left.onUserAction();
    this.right.onUserAction();
    emitLWACharacterEvent({ state: "alert", trigger: "user_action" });
  }
}

export function emitLWACharacterEvent(detail: LWACharacterEvent) {
  if (typeof window === "undefined") return;
  window.dispatchEvent(new CustomEvent<LWACharacterEvent>(LWA_CHARACTER_EVENT, { detail }));
}

export function addLWACharacterListener(listener: (event: LWACharacterEvent) => void) {
  if (typeof window === "undefined") return () => undefined;
  const handler = (event: Event) => listener((event as CustomEvent<LWACharacterEvent>).detail);
  window.addEventListener(LWA_CHARACTER_EVENT, handler);
  return () => window.removeEventListener(LWA_CHARACTER_EVENT, handler);
}
