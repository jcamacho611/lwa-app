/// <reference lib="webworker" />

import * as THREE from "three";

type InitMessage = {
  type: "init";
  canvas: OffscreenCanvas;
  width: number;
  height: number;
  pixelRatio: number;
};

type ResizeMessage = {
  type: "resize";
  width: number;
  height: number;
  pixelRatio: number;
};

type VisibilityMessage = {
  type: "visibility";
  hidden: boolean;
};

type DestroyMessage = {
  type: "destroy";
};

type WorkerMessage = InitMessage | ResizeMessage | VisibilityMessage | DestroyMessage;

type AnimationHandle = number | ReturnType<typeof setTimeout>;

const workerScope = self as unknown as DedicatedWorkerGlobalScope & {
  requestAnimationFrame?: (callback: FrameRequestCallback) => number;
  cancelAnimationFrame?: (handle: number) => void;
};

let renderer: THREE.WebGLRenderer | null = null;
let scene: THREE.Scene | null = null;
let camera: THREE.PerspectiveCamera | null = null;
let godLight: THREE.PointLight | null = null;
let clouds: THREE.Mesh[] = [];
let animationHandle: AnimationHandle | null = null;
let hidden = false;
let disposed = false;
const clock = new THREE.Clock();

const SCENE_TONES = {
  ambient: 0xf4ebff,
  core: 0xb39bff,
  rim: 0xf5bdd8,
  cloud: 0xd8cbf3,
  ground: 0xf2e9fb,
  temple: 0xc6b4ec,
  fog: 0xf6efff,
};

function scheduleFrame(callback: () => void): AnimationHandle {
  if (workerScope.requestAnimationFrame) {
    return workerScope.requestAnimationFrame(callback);
  }
  return setTimeout(callback, 1000 / 30);
}

function cancelFrame(handle: AnimationHandle | null) {
  if (handle == null) return;
  if (typeof handle === "number" && workerScope.cancelAnimationFrame) {
    workerScope.cancelAnimationFrame(handle);
    return;
  }
  clearTimeout(handle as ReturnType<typeof setTimeout>);
}

function addCelestialLight(targetScene: THREE.Scene) {
  const ambient = new THREE.AmbientLight(SCENE_TONES.ambient, 1.08);
  targetScene.add(ambient);

  godLight = new THREE.PointLight(SCENE_TONES.core, 2.2, 80);
  godLight.position.set(0, 25, -10);
  targetScene.add(godLight);

  const rimLeft = new THREE.DirectionalLight(SCENE_TONES.rim, 0.65);
  rimLeft.position.set(-20, 5, 5);
  targetScene.add(rimLeft);

  const rimRight = new THREE.DirectionalLight(SCENE_TONES.rim, 0.52);
  rimRight.position.set(20, 5, 5);
  targetScene.add(rimRight);
}

function addCloudVolume(targetScene: THREE.Scene) {
  clouds = [];
  for (let index = 0; index < 6; index += 1) {
    const material = new THREE.MeshLambertMaterial({
      color: SCENE_TONES.cloud,
      transparent: true,
      opacity: 0.08 + index * 0.018,
      depthWrite: false,
    });
    const geometry = new THREE.PlaneGeometry(60 + index * 10, 18 + index * 2);
    const mesh = new THREE.Mesh(geometry, material);
    mesh.position.set((index - 2.5) * 7, 6 + index * 2.5, -18 - index * 8);
    mesh.rotation.x = -0.1;
    mesh.rotation.z = (index % 2 === 0 ? -1 : 1) * 0.04;
    mesh.userData.speed = 0.006 + index * 0.0013;
    clouds.push(mesh);
    targetScene.add(mesh);
  }
}

function addGroundPlane(targetScene: THREE.Scene) {
  const geometry = new THREE.PlaneGeometry(120, 44);
  const material = new THREE.MeshStandardMaterial({
    color: SCENE_TONES.ground,
    metalness: 0.08,
    roughness: 0.92,
    transparent: true,
    opacity: 0.12,
  });
  const plane = new THREE.Mesh(geometry, material);
  plane.rotation.x = -Math.PI / 2;
  plane.position.y = -6;
  targetScene.add(plane);

  const templeGeometry = new THREE.PlaneGeometry(34, 12);
  const templeMaterial = new THREE.MeshBasicMaterial({
    color: SCENE_TONES.temple,
    transparent: true,
    opacity: 0.08,
    depthWrite: false,
  });
  const temple = new THREE.Mesh(templeGeometry, templeMaterial);
  temple.position.set(0, -0.8, -50);
  targetScene.add(temple);
}

function renderFrame() {
  if (disposed || hidden || !renderer || !scene || !camera) return;

  animationHandle = scheduleFrame(renderFrame);
  const elapsed = clock.getElapsedTime();

  if (godLight) {
    godLight.intensity = 2.05 + Math.sin(elapsed * Math.PI) * 0.26;
  }

  for (const cloud of clouds) {
    cloud.position.x += Number(cloud.userData.speed || 0);
    if (cloud.position.x > 42) {
      cloud.position.x = -42;
    }
  }

  renderer.render(scene, camera);
}

function init({ canvas, width, height, pixelRatio }: InitMessage) {
  disposed = false;
  hidden = false;
  renderer = new THREE.WebGLRenderer({ canvas, antialias: false, alpha: true, powerPreference: "low-power" });
  renderer.setPixelRatio(Math.min(pixelRatio || 1, 1.5));
  renderer.setSize(width, height, false);
  renderer.setClearColor(0x000000, 0);

  scene = new THREE.Scene();
  scene.background = null;
  scene.fog = new THREE.FogExp2(SCENE_TONES.fog, 0.018);

  camera = new THREE.PerspectiveCamera(60, width / Math.max(height, 1), 0.1, 200);
  camera.position.set(0, 2, 18);

  addCelestialLight(scene);
  addCloudVolume(scene);
  addGroundPlane(scene);

  clock.start();
  renderFrame();
}

function resize({ width, height, pixelRatio }: ResizeMessage) {
  if (!renderer || !camera) return;
  renderer.setPixelRatio(Math.min(pixelRatio || 1, 1.5));
  renderer.setSize(width, height, false);
  camera.aspect = width / Math.max(height, 1);
  camera.updateProjectionMatrix();
}

function setVisibility({ hidden: nextHidden }: VisibilityMessage) {
  hidden = nextHidden;
  if (hidden) {
    cancelFrame(animationHandle);
    animationHandle = null;
    return;
  }
  if (!animationHandle) {
    renderFrame();
  }
}

function destroy() {
  disposed = true;
  cancelFrame(animationHandle);
  animationHandle = null;
  for (const cloud of clouds) {
    cloud.geometry.dispose();
    const material = cloud.material;
    if (Array.isArray(material)) {
      material.forEach((item) => item.dispose());
    } else {
      material.dispose();
    }
  }
  clouds = [];
  renderer?.dispose();
  renderer = null;
  scene = null;
  camera = null;
  godLight = null;
}

workerScope.addEventListener("message", (event: MessageEvent<WorkerMessage>) => {
  const message = event.data;
  if (message.type === "init") init(message);
  if (message.type === "resize") resize(message);
  if (message.type === "visibility") setVisibility(message);
  if (message.type === "destroy") destroy();
});
