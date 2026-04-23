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
  const ambient = new THREE.AmbientLight(0x0d0b1a, 1.2);
  targetScene.add(ambient);

  godLight = new THREE.PointLight(0xd4b26a, 3.5, 80);
  godLight.position.set(0, 25, -10);
  targetScene.add(godLight);

  const rimLeft = new THREE.DirectionalLight(0x1a2a4a, 0.8);
  rimLeft.position.set(-20, 5, 5);
  targetScene.add(rimLeft);

  const rimRight = new THREE.DirectionalLight(0x1a2a4a, 0.8);
  rimRight.position.set(20, 5, 5);
  targetScene.add(rimRight);
}

function addCloudVolume(targetScene: THREE.Scene) {
  clouds = [];
  for (let index = 0; index < 6; index += 1) {
    const material = new THREE.MeshLambertMaterial({
      color: 0x171321,
      transparent: true,
      opacity: 0.34 + index * 0.035,
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
    color: 0x050509,
    metalness: 0.8,
    roughness: 0.4,
  });
  const plane = new THREE.Mesh(geometry, material);
  plane.rotation.x = -Math.PI / 2;
  plane.position.y = -6;
  targetScene.add(plane);

  const templeGeometry = new THREE.PlaneGeometry(34, 12);
  const templeMaterial = new THREE.MeshBasicMaterial({
    color: 0x03030a,
    transparent: true,
    opacity: 0.58,
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
    godLight.intensity = 3.2 + Math.sin(elapsed * Math.PI) * 0.4;
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
  renderer = new THREE.WebGLRenderer({ canvas, antialias: false, alpha: false, powerPreference: "low-power" });
  renderer.setPixelRatio(Math.min(pixelRatio || 1, 1.5));
  renderer.setSize(width, height, false);

  scene = new THREE.Scene();
  scene.background = new THREE.Color(0x040408);
  scene.fog = new THREE.FogExp2(0x0a0814, 0.035);

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
