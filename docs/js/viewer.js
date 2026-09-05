import * as THREE from "three";
import { OrbitControls } from "three/addons/controls/OrbitControls.js";
import { GLTFLoader } from "three/addons/loaders/GLTFLoader.js";
import { CSS2DRenderer, CSS2DObject } from "three/addons/renderers/CSS2DRenderer.js";

const MODEL_URL = new URL("../models/solomon_temple.glb", import.meta.url).href;
const LABELS_URL = new URL("../labels.json", import.meta.url).href;

const LEGEND = [
  { name: "Porch (Ulam)", note: "Entrance hall before the nave", color: "#b89a72" },
  { name: "Holy Place (Hekal)", note: "40 × 20 × 30 cubits", color: "#d2c19a" },
  { name: "Holy of Holies (Debir)", note: "Inner 20-cubit cube", color: "#c8a24d" },
  { name: "Jachin & Boaz", note: "South / north bronze pillars", color: "#8c5a22" },
  { name: "Bronze altar", note: "Court, with horns (height reduced)", color: "#8c5a22" },
  { name: "Side chambers", note: "Three stories, 5 / 6 / 7 cubits", color: "#b89a72" },
];

const canvasWrap = document.getElementById("canvas-wrap");
const loaderEl = document.getElementById("loader");
const panel = document.getElementById("panel");
const menuToggle = document.getElementById("menu-toggle");
const legendEl = document.getElementById("legend");
const optCutaway = document.getElementById("opt-cutaway");
const optRoof = document.getElementById("opt-roof");
const optLabels = document.getElementById("opt-labels");
const btnReset = document.getElementById("btn-reset");

legendEl.innerHTML = LEGEND.map(
  (item) =>
    `<li><span class="swatch" style="background:${item.color}"></span><span>${item.name}<small>${item.note}</small></span></li>`
).join("");

menuToggle.addEventListener("click", () => {
  const open = panel.classList.toggle("open");
  menuToggle.setAttribute("aria-expanded", String(open));
});

const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: false });
renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
renderer.setSize(canvasWrap.clientWidth, canvasWrap.clientHeight);
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.05;
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
canvasWrap.appendChild(renderer.domElement);

const labelRenderer = new CSS2DRenderer();
labelRenderer.setSize(canvasWrap.clientWidth, canvasWrap.clientHeight);
labelRenderer.domElement.style.position = "absolute";
labelRenderer.domElement.style.inset = "0";
labelRenderer.domElement.style.pointerEvents = "none";
canvasWrap.appendChild(labelRenderer.domElement);

const scene = new THREE.Scene();
scene.background = new THREE.Color(0x121416);
scene.fog = new THREE.Fog(0x121416, 70, 160);

const camera = new THREE.PerspectiveCamera(
  42,
  canvasWrap.clientWidth / canvasWrap.clientHeight,
  0.1,
  400
);

const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
controls.dampingFactor = 0.06;
controls.maxPolarAngle = Math.PI * 0.49;
controls.minDistance = 6;
controls.maxDistance = 90;
controls.target.set(0, 4.5, -4);

const hemi = new THREE.HemisphereLight(0xc9d4e4, 0x3a3228, 0.72);
scene.add(hemi);

const sun = new THREE.DirectionalLight(0xfff1d6, 1.55);
sun.position.set(28, 42, 18);
sun.castShadow = true;
sun.shadow.mapSize.set(2048, 2048);
sun.shadow.camera.near = 4;
sun.shadow.camera.far = 120;
sun.shadow.camera.left = -40;
sun.shadow.camera.right = 40;
sun.shadow.camera.top = 40;
sun.shadow.camera.bottom = -40;
scene.add(sun);

const fill = new THREE.DirectionalLight(0xa8c0e0, 0.35);
fill.position.set(-24, 18, -12);
scene.add(fill);

const ground = new THREE.Mesh(
  new THREE.CircleGeometry(48, 64),
  new THREE.MeshStandardMaterial({ color: 0x2a2c2f, roughness: 0.95, metalness: 0.0 })
);
ground.rotation.x = -Math.PI / 2;
ground.position.y = -0.02;
ground.receiveShadow = true;
scene.add(ground);

const DEFAULT_CAM = {
  position: new THREE.Vector3(26, 18, 32),
  target: new THREE.Vector3(0, 4.5, -6),
};

function resetCamera() {
  camera.position.copy(DEFAULT_CAM.position);
  controls.target.copy(DEFAULT_CAM.target);
  controls.update();
}

resetCamera();

const templeRoot = new THREE.Group();
scene.add(templeRoot);
const labelRoot = new THREE.Group();
scene.add(labelRoot);

function applyVisibility() {
  const cutaway = optCutaway.checked;
  const showRoof = optRoof.checked;
  templeRoot.traverse((obj) => {
    if (!obj.isMesh) return;
    const extras = obj.userData || {};
    let visible = true;
    if (cutaway && extras.cutaway === true) visible = false;
    if (!showRoof && extras.roof === true) visible = false;
    obj.visible = visible;
  });
  labelRoot.visible = optLabels.checked;
}

optCutaway.addEventListener("change", applyVisibility);
optRoof.addEventListener("change", applyVisibility);
optLabels.addEventListener("change", applyVisibility);
btnReset.addEventListener("click", resetCamera);

function addLabels(entries) {
  for (const entry of entries) {
    const el = document.createElement("div");
    el.className = "label";
    el.textContent = entry.name;
    const obj = new CSS2DObject(el);
    obj.position.set(entry.position[0], entry.position[1], entry.position[2]);
    labelRoot.add(obj);
  }
}

async function load() {
  const loader = new GLTFLoader();
  const [gltf, labels] = await Promise.all([
    loader.loadAsync(MODEL_URL),
    fetch(LABELS_URL).then((r) => {
      if (!r.ok) throw new Error("labels.json missing");
      return r.json();
    }),
  ]);

  gltf.scene.traverse((obj) => {
    if (obj.userData && obj.userData.extras) {
      Object.assign(obj.userData, obj.userData.extras);
    }
    if (obj.isMesh) {
      obj.castShadow = true;
      obj.receiveShadow = true;
      if (obj.material) {
        const mats = Array.isArray(obj.material) ? obj.material : [obj.material];
        for (const mat of mats) {
          if (mat.map) mat.map.colorSpace = THREE.SRGBColorSpace;
          mat.needsUpdate = true;
        }
      }
    }
  });
  templeRoot.add(gltf.scene);
  addLabels(labels);
  applyVisibility();
  loaderEl.classList.add("hide");
}

load().catch((err) => {
  console.error(err);
  loaderEl.innerHTML = `<p>Could not load the temple model.<br><small>${err.message}</small></p>`;
});

function onResize() {
  const w = canvasWrap.clientWidth;
  const h = canvasWrap.clientHeight;
  camera.aspect = w / h;
  camera.updateProjectionMatrix();
  renderer.setSize(w, h);
  labelRenderer.setSize(w, h);
}

window.addEventListener("resize", onResize);

function tick() {
  controls.update();
  renderer.render(scene, camera);
  labelRenderer.render(scene, camera);
  requestAnimationFrame(tick);
}
tick();
