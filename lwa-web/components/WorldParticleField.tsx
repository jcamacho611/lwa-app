"use client";

import { useEffect, useRef } from "react";
import type { WorldPhase } from "../lib/world-state";

type WorldParticleFieldProps = {
  phase: WorldPhase;
  variant: "workspace" | "home";
};

type Particle = {
  x: number;
  y: number;
  vx: number;
  vy: number;
  life: number;
  ttl: number;
  size: number;
  hue: number;
  alpha: number;
  anchorX: number;
  anchorY: number;
};

const PHASE_SETTINGS: Record<
  WorldPhase,
  {
    maxParticles: number;
    spawnRate: number;
    speed: number;
    alpha: number;
    hue: [number, number];
  }
> = {
  idle: { maxParticles: 16, spawnRate: 0.35, speed: 0.18, alpha: 0.24, hue: [190, 320] },
  analyzing: { maxParticles: 22, spawnRate: 0.55, speed: 0.24, alpha: 0.3, hue: [190, 315] },
  generating: { maxParticles: 28, spawnRate: 0.8, speed: 0.34, alpha: 0.38, hue: [190, 340] },
  rendering: { maxParticles: 34, spawnRate: 1.1, speed: 0.46, alpha: 0.44, hue: [35, 325] },
  ready: { maxParticles: 18, spawnRate: 0.45, speed: 0.22, alpha: 0.26, hue: [36, 58] },
};

function getAnchors(width: number, height: number) {
  return [
    { x: width * 0.16, y: height * 0.76 },
    { x: width * 0.84, y: height * 0.76 },
    { x: width * 0.5, y: height * 0.56 },
  ];
}

export function WorldParticleField({ phase, variant }: WorldParticleFieldProps) {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas || variant !== "home") {
      return;
    }

    const media = window.matchMedia("(prefers-reduced-motion: reduce)");
    if (media.matches) {
      return;
    }

    const context = canvas.getContext("2d", { alpha: true });
    if (!context) {
      return;
    }

    let animationFrame = 0;
    let width = 0;
    let height = 0;
    let ratio = 1;
    let lastTime = 0;
    const particles: Particle[] = [];

    const resize = () => {
      width = window.innerWidth;
      height = window.innerHeight;
      ratio = Math.min(window.devicePixelRatio || 1, 1.5);
      canvas.width = Math.floor(width * ratio);
      canvas.height = Math.floor(height * ratio);
      canvas.style.width = `${width}px`;
      canvas.style.height = `${height}px`;
      context.setTransform(ratio, 0, 0, ratio, 0, 0);
    };

    const spawnParticle = (settings: (typeof PHASE_SETTINGS)[WorldPhase]) => {
      const anchors = getAnchors(width, height);
      const anchor = anchors[Math.floor(Math.random() * anchors.length)];
      const angle = Math.random() * Math.PI * 2;
      const orbit = 14 + Math.random() * 84;
      const speed = settings.speed * (0.6 + Math.random() * 1.4);
      particles.push({
        x: anchor.x + Math.cos(angle) * orbit,
        y: anchor.y + Math.sin(angle) * orbit,
        vx: Math.cos(angle + Math.PI / 2) * speed,
        vy: Math.sin(angle + Math.PI / 2) * speed,
        life: 0,
        ttl: 1200 + Math.random() * 1800,
        size: 0.7 + Math.random() * 2.1,
        hue: settings.hue[0] + Math.random() * (settings.hue[1] - settings.hue[0]),
        alpha: settings.alpha * (0.55 + Math.random() * 0.8),
        anchorX: anchor.x,
        anchorY: anchor.y,
      });
    };

    const render = (time: number) => {
      const settings = PHASE_SETTINGS[phase];
      const delta = Math.min(34, time - lastTime || 16);
      lastTime = time;

      context.clearRect(0, 0, width, height);
      context.globalCompositeOperation = "lighter";

      const spawnCount = Math.floor(settings.spawnRate);
      for (let index = 0; index < spawnCount; index += 1) {
        if (particles.length < settings.maxParticles) {
          spawnParticle(settings);
        }
      }

      if (Math.random() < settings.spawnRate % 1 && particles.length < settings.maxParticles) {
        spawnParticle(settings);
      }

      for (let index = particles.length - 1; index >= 0; index -= 1) {
        const particle = particles[index];
        particle.life += delta;

        if (particle.life >= particle.ttl) {
          particles.splice(index, 1);
          continue;
        }

        const progress = particle.life / particle.ttl;
        const orbitPull = 0.0009 + (phase === "rendering" ? 0.0018 : 0.0012);
        particle.vx += (particle.anchorX - particle.x) * orbitPull * delta;
        particle.vy += (particle.anchorY - particle.y) * orbitPull * delta;
        particle.x += particle.vx * delta;
        particle.y += particle.vy * delta;

        const fade = progress < 0.18 ? progress / 0.18 : 1 - (progress - 0.18) / 0.82;
        const alpha = Math.max(0, fade) * particle.alpha;
        const radius = particle.size * (phase === "rendering" ? 1.4 : phase === "generating" ? 1.2 : 1);

        context.beginPath();
        context.fillStyle = `hsla(${particle.hue} 96% 72% / ${alpha})`;
        context.shadowColor = `hsla(${particle.hue} 96% 70% / ${alpha * 0.95})`;
        context.shadowBlur = 12;
        context.arc(particle.x, particle.y, radius, 0, Math.PI * 2);
        context.fill();
      }

      context.shadowBlur = 0;
      animationFrame = window.requestAnimationFrame(render);
    };

    resize();
    animationFrame = window.requestAnimationFrame(render);
    window.addEventListener("resize", resize);

    return () => {
      window.cancelAnimationFrame(animationFrame);
      window.removeEventListener("resize", resize);
    };
  }, [phase, variant]);

  return <canvas ref={canvasRef} className="world-particle-canvas" aria-hidden="true" />;
}
