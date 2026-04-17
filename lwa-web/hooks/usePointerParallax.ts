"use client";

import { RefObject, useEffect } from "react";

type PointerParallaxOptions = {
  rotate?: number;
  shiftSmall?: number;
  shiftMedium?: number;
  shiftLarge?: number;
};

export function usePointerParallax<T extends HTMLElement>(
  ref: RefObject<T>,
  options: PointerParallaxOptions = {},
) {
  useEffect(() => {
    const node = ref.current;
    if (!node || typeof window === "undefined") {
      return;
    }

    const media = window.matchMedia("(prefers-reduced-motion: reduce)");
    const rotate = options.rotate ?? 8;
    const shiftSmall = options.shiftSmall ?? 8;
    const shiftMedium = options.shiftMedium ?? 16;
    const shiftLarge = options.shiftLarge ?? 24;

    const reset = () => {
      node.style.setProperty("--rx", "0deg");
      node.style.setProperty("--ry", "0deg");
      node.style.setProperty("--px-sm", "0px");
      node.style.setProperty("--py-sm", "0px");
      node.style.setProperty("--px-md", "0px");
      node.style.setProperty("--py-md", "0px");
      node.style.setProperty("--px-lg", "0px");
      node.style.setProperty("--py-lg", "0px");
    };

    reset();

    if (media.matches) {
      return;
    }

    let frame = 0;

    const handleMove = (event: MouseEvent) => {
      cancelAnimationFrame(frame);
      frame = window.requestAnimationFrame(() => {
        const rect = node.getBoundingClientRect();
        const x = (event.clientX - rect.left) / rect.width - 0.5;
        const y = (event.clientY - rect.top) / rect.height - 0.5;

        node.style.setProperty("--rx", `${-y * rotate}deg`);
        node.style.setProperty("--ry", `${x * rotate}deg`);
        node.style.setProperty("--px-sm", `${x * shiftSmall}px`);
        node.style.setProperty("--py-sm", `${y * shiftSmall}px`);
        node.style.setProperty("--px-md", `${x * shiftMedium}px`);
        node.style.setProperty("--py-md", `${y * shiftMedium}px`);
        node.style.setProperty("--px-lg", `${x * shiftLarge}px`);
        node.style.setProperty("--py-lg", `${y * shiftLarge}px`);
      });
    };

    const handleLeave = () => reset();

    node.addEventListener("mousemove", handleMove);
    node.addEventListener("mouseleave", handleLeave);

    return () => {
      cancelAnimationFrame(frame);
      node.removeEventListener("mousemove", handleMove);
      node.removeEventListener("mouseleave", handleLeave);
    };
  }, [ref, options.rotate, options.shiftSmall, options.shiftMedium, options.shiftLarge]);
}
