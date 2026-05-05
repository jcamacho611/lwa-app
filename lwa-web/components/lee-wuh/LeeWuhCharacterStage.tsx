"use client";

import { useEffect, useRef, useState } from "react";
import * as THREE from "three";
import { GLTFLoader } from "three/examples/jsm/loaders/GLTFLoader.js";

export type LeeWuhStageMood =
  | "idle"
  | "focused"
  | "analyzing"
  | "confident"
  | "victory"
  | "warning";

export type LeeWuhStageVariant = "hero" | "card" | "floating" | "compact";

type LeeWuhCharacterStageProps = {
  mood?: LeeWuhStageMood;
  variant?: LeeWuhStageVariant;
  className?: string;
  glbPath?: string;
  posterPath?: string;
  title?: string;
  message?: string;
  showLabel?: boolean;
};

const moodCopy: Record<LeeWuhStageMood, { label: string; message: string; emoji: string }> = {
  idle: {
    label: "Idle",
    message: "Lee-Wuh is ready to run the signal.",
    emoji: "🦁",
  },
  focused: {
    label: "Focused",
    message: "Lee-Wuh is locked onto the best clip path.",
    emoji: "🎯",
  },
  analyzing: {
    label: "Analyzing",
    message: "Lee-Wuh is scanning hooks, beats, captions, and proof.",
    emoji: "🧠",
  },
  confident: {
    label: "Confident",
    message: "Lee-Wuh found the creator signal.",
    emoji: "⚡",
  },
  victory: {
    label: "Victory",
    message: "Lee-Wuh packaged the win.",
    emoji: "🏆",
  },
  warning: {
    label: "Warning",
    message: "Lee-Wuh needs a real asset or safer source.",
    emoji: "⚠️",
  },
};

function variantClasses(variant: LeeWuhStageVariant) {
  switch (variant) {
    case "hero":
      return "min-h-[460px] rounded-[40px]";
    case "floating":
      return "h-20 w-20 rounded-full";
    case "compact":
      return "min-h-[220px] rounded-[28px]";
    default:
      return "min-h-[320px] rounded-[32px]";
  }
}

export function LeeWuhCharacterStage({
  mood = "idle",
  variant = "card",
  className = "",
  glbPath = "/characters/lee-wuh/lee-wuh.glb",
  posterPath = "/characters/lee-wuh/lee-wuh.poster.png",
  title = "Lee-Wuh",
  message,
  showLabel = true,
}: LeeWuhCharacterStageProps) {
  const mountRef = useRef<HTMLDivElement | null>(null);
  const [mode, setMode] = useState<"loading" | "three" | "poster" | "svg" | "fallback">("loading");

  useEffect(() => {
    if (!mountRef.current || variant === "floating") return;

    let disposed = false;
    const mount = mountRef.current;

    const scene = new THREE.Scene();
    scene.background = null;

    const camera = new THREE.PerspectiveCamera(38, 1, 0.1, 100);
    camera.position.set(0, 1.15, 4.2);

    const renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
    renderer.outputColorSpace = THREE.SRGBColorSpace;

    const resize = () => {
      if (!mount) return;
      const width = Math.max(mount.clientWidth, 1);
      const height = Math.max(mount.clientHeight, 1);
      renderer.setSize(width, height);
      camera.aspect = width / height;
      camera.updateProjectionMatrix();
    };

    mount.innerHTML = "";
    mount.appendChild(renderer.domElement);
    resize();

    const key = new THREE.DirectionalLight(0xf5d88a, 3);
    key.position.set(3, 4, 4);
    scene.add(key);

    const rim = new THREE.DirectionalLight(0x6d3bff, 2);
    rim.position.set(-4, 2, -3);
    scene.add(rim);

    const ambient = new THREE.AmbientLight(0xffffff, 1.3);
    scene.add(ambient);

    const loader = new GLTFLoader();
    let model: THREE.Object3D | null = null;
    let frame = 0;

    loader.load(
      glbPath,
      (gltf) => {
        if (disposed) return;
        model = gltf.scene;
        model.position.set(0, -1.05, 0);
        model.scale.setScalar(1.65);
        scene.add(model);
        setMode("three");
      },
      undefined,
      () => {
        if (!disposed) setMode("poster");
      },
    );

    const animate = () => {
      if (disposed) return;
      frame = requestAnimationFrame(animate);
      if (model) {
        model.rotation.y += mood === "analyzing" ? 0.009 : 0.004;
        model.position.y = -1.05 + Math.sin(Date.now() * 0.0018) * 0.045;
      }
      renderer.render(scene, camera);
    };

    animate();
    window.addEventListener("resize", resize);

    return () => {
      disposed = true;
      cancelAnimationFrame(frame);
      window.removeEventListener("resize", resize);
      renderer.dispose();
      scene.traverse((object) => {
        const mesh = object as THREE.Mesh;
        if (mesh.geometry) mesh.geometry.dispose();
        const material = mesh.material;
        if (Array.isArray(material)) material.forEach((item) => item.dispose());
        else if (material) material.dispose();
      });
      if (mount.contains(renderer.domElement)) mount.removeChild(renderer.domElement);
    };
  }, [glbPath, mood, variant]);

  const copy = moodCopy[mood];

  return (
    <section
      className={`relative overflow-hidden border border-[#C9A24A]/30 bg-[#09090d] shadow-[0_32px_120px_-48px_rgba(201,162,74,0.55)] ${variantClasses(
        variant,
      )} ${className}`}
    >
      <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_26%_18%,rgba(201,162,74,0.25),transparent_34%),radial-gradient(circle_at_78%_8%,rgba(109,59,255,0.2),transparent_32%)]" />

      {variant !== "floating" ? (
        <div ref={mountRef} className="absolute inset-0 z-10" aria-label="Lee-Wuh 3D character stage" />
      ) : null}

      {mode !== "three" || variant === "floating" ? (
        <div className="absolute inset-0 z-20 flex items-center justify-center">
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img
            src={posterPath}
            alt="Lee-Wuh character poster"
            className="h-full w-full object-cover"
            onError={(event) => {
              (event.currentTarget as HTMLImageElement).src = "/brand/lee-wuh-hero-16x9.svg";
              setMode("svg");
            }}
          />
        </div>
      ) : null}

      {mode === "fallback" ? (
        <div className="flex items-center justify-center">
          <img
            src="/brand/lee-wuh/lee-wuh-avatar.png"
            alt="Lee-Wuh mascot"
            className="h-16 w-16 rounded-full object-cover"
            onError={(e) => {
              e.currentTarget.style.display = 'none';
            }}
          />
        </div>
      ) : null}

      {showLabel && variant !== "floating" ? (
        <div className="absolute inset-x-0 bottom-0 z-40 bg-gradient-to-t from-black/95 via-black/55 to-transparent p-5">
          <p className="font-mono text-xs uppercase tracking-[0.24em] text-[#E9C77B]">
            {title}{" // "}{copy.label}
          </p>
          <p className="mt-2 max-w-xl text-sm leading-6 text-[#D8D0BF]">
            {message || copy.message}
          </p>
        </div>
      ) : null}
    </section>
  );
}

export default LeeWuhCharacterStage;
