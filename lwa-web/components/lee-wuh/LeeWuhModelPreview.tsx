"use client";

import { useEffect, useRef, useState } from "react";
import * as THREE from "three";
import { GLTFLoader } from "three/examples/jsm/loaders/GLTFLoader.js";

type LeeWuhModelPreviewProps = {
  className?: string;
};

const MODEL_PATH = "/brand/lee-wuh/3d/lee-wuh-mascot.glb";
const FALLBACK_IMAGE = "/brand/lee-wuh-hero-16x9.svg";

export function LeeWuhModelPreview({ className = "" }: LeeWuhModelPreviewProps) {
  const mountRef = useRef<HTMLDivElement | null>(null);
  const [failed, setFailed] = useState(false);
  const [loaded, setLoaded] = useState(false);

  useEffect(() => {
    const mount = mountRef.current;

    if (!mount || failed) {
      return;
    }

    let frameId = 0;
    let disposed = false;

    const width = mount.clientWidth || 640;
    const height = mount.clientHeight || 460;

    const scene = new THREE.Scene();
    scene.background = new THREE.Color("#05030a");

    const camera = new THREE.PerspectiveCamera(35, width / height, 0.1, 100);
    camera.position.set(0, 1.2, 5);

    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
    renderer.setSize(width, height);
    renderer.outputColorSpace = THREE.SRGBColorSpace;
    mount.appendChild(renderer.domElement);

    const ambient = new THREE.AmbientLight("#ffffff", 1.4);
    scene.add(ambient);

    const key = new THREE.DirectionalLight("#f5d06f", 2.1);
    key.position.set(3, 4, 5);
    scene.add(key);

    const rim = new THREE.DirectionalLight("#7c3cff", 1.6);
    rim.position.set(-4, 2, -3);
    scene.add(rim);

    const loader = new GLTFLoader();
    const group = new THREE.Group();
    scene.add(group);

    loader.load(
      MODEL_PATH,
      (gltf) => {
        if (disposed) return;

        const model = gltf.scene;
        const box = new THREE.Box3().setFromObject(model);
        const size = new THREE.Vector3();
        const center = new THREE.Vector3();

        box.getSize(size);
        box.getCenter(center);

        model.position.sub(center);

        const maxAxis = Math.max(size.x, size.y, size.z) || 1;
        model.scale.setScalar(2.8 / maxAxis);

        group.add(model);
        setLoaded(true);
      },
      undefined,
      () => {
        setFailed(true);
      }
    );

    const onResize = () => {
      if (!mount) return;

      const nextWidth = mount.clientWidth || 640;
      const nextHeight = mount.clientHeight || 460;

      camera.aspect = nextWidth / nextHeight;
      camera.updateProjectionMatrix();
      renderer.setSize(nextWidth, nextHeight);
    };

    window.addEventListener("resize", onResize);

    const animate = () => {
      group.rotation.y += 0.006;
      renderer.render(scene, camera);
      frameId = window.requestAnimationFrame(animate);
    };

    animate();

    return () => {
      disposed = true;
      window.cancelAnimationFrame(frameId);
      window.removeEventListener("resize", onResize);

      scene.traverse((object) => {
        if (object instanceof THREE.Mesh) {
          object.geometry?.dispose();

          const materials = Array.isArray(object.material)
            ? object.material
            : [object.material];

          materials.forEach((material) => material.dispose());
        }
      });

      renderer.dispose();

      if (renderer.domElement.parentNode) {
        renderer.domElement.parentNode.removeChild(renderer.domElement);
      }
    };
  }, [failed]);

  return (
    <section
      className={[
        "relative overflow-hidden rounded-[2rem] border border-[#c9a24a33] bg-black/80 p-5 shadow-2xl shadow-purple-950/30",
        className,
      ].join(" ")}
    >
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_20%,rgba(124,58,237,0.28),transparent_42%),radial-gradient(circle_at_50%_100%,rgba(201,162,74,0.18),transparent_45%)]" />

      <div className="relative mb-4 flex items-center justify-between gap-4">
        <div>
          <p className="text-xs uppercase tracking-[0.35em] text-[#c9a24a]">
            Blender GLB Preview
          </p>
          <h2 className="mt-2 text-2xl font-black text-white">
            Lee-Wuh 3D Blockout
          </h2>
        </div>

        <span className="rounded-full border border-purple-400/30 bg-purple-500/10 px-3 py-1 text-xs font-bold uppercase tracking-[0.2em] text-purple-100">
          {failed ? "Fallback" : loaded ? "Live GLB" : "Loading"}
        </span>
      </div>

      <div className="relative min-h-[420px] overflow-hidden rounded-[1.5rem] border border-white/10 bg-[#05030a]">
        {failed ? (
          <img
            src={FALLBACK_IMAGE}
            alt="Lee-Wuh fallback artwork"
            className="h-full min-h-[420px] w-full object-cover"
          />
        ) : (
          <>
            {!loaded ? (
              <div className="absolute inset-0 z-10 grid place-items-center text-sm font-bold uppercase tracking-[0.25em] text-purple-100">
                Loading Lee-Wuh...
              </div>
            ) : null}
            <div ref={mountRef} className="h-[420px] w-full" />
          </>
        )}
      </div>

      <p className="relative mt-4 text-sm leading-6 text-white/65">
        Source model: <code>{MODEL_PATH}</code>. This is the first Blender blockout,
        not the final sculpt or rig.
      </p>
    </section>
  );
}
