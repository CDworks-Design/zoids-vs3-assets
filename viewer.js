import * as THREE from 'three';
import { GLTFLoader } from './vendor/three-0.170.0/loaders/GLTFLoader.js';
import { OrbitControls } from './vendor/three-0.170.0/controls/OrbitControls.js';

function disposeObject(root) {
  const textures = new Set(), materials = new Set(), geometries = new Set();
  root?.traverse(node => {
    if (node.geometry) geometries.add(node.geometry);
    for (const material of Array.isArray(node.material) ? node.material : node.material ? [node.material] : []) {
      materials.add(material);
      for (const value of Object.values(material)) if (value?.isTexture) textures.add(value);
    }
    node.skeleton?.dispose();
  });
  for (const texture of textures) { texture.source?.data?.close?.(); texture.dispose(); }
  for (const material of materials) material.dispose();
  for (const geometry of geometries) geometry.dispose();
}

export class ModelViewer {
  constructor(container, { capture = false, onContextLost = () => {}, onFinished = () => {} } = {}) {
    this.container = container;
    this.renderer = new THREE.WebGLRenderer({ antialias: true, alpha: false, preserveDrawingBuffer: capture });
    this.renderer.setPixelRatio(capture ? 1 : Math.min(window.devicePixelRatio || 1, 2));
    this.renderer.outputColorSpace = THREE.SRGBColorSpace;
    this.renderer.toneMapping = THREE.ACESFilmicToneMapping;
    this.renderer.toneMappingExposure = 1.15;
    this.renderer.domElement.setAttribute('aria-label', 'Rendered model');
    this.renderer.domElement.addEventListener('webglcontextlost', e => { e.preventDefault(); if (!this.disposed) onContextLost(); });
    container.append(this.renderer.domElement);
    this.scene = new THREE.Scene();
    this.scene.background = new THREE.Color('#0c1724');
    this.camera = new THREE.PerspectiveCamera(34, 4 / 3, .01, 200);
    this.scene.add(new THREE.HemisphereLight(0xe1efff, 0x1a293d, 2.8));
    const key = new THREE.DirectionalLight(0xe9f5ff, 3.3); key.position.set(5, 8, 6); this.scene.add(key);
    const rim = new THREE.DirectionalLight(0x69adff, 2); rim.position.set(-5, 3, -4); this.scene.add(rim);
    const fill = new THREE.DirectionalLight(0xffffff, 1); fill.position.set(-3, 2, 5); this.scene.add(fill);
    this.grid = new THREE.GridHelper(12, 24, 0x294764, 0x172c40);
    this.grid.material.transparent = true; this.grid.material.opacity = .42; this.scene.add(this.grid);
    this.controls = new OrbitControls(this.camera, this.renderer.domElement);
    this.controls.enableDamping = true; this.controls.dampingFactor = .09;
    this.controls.enablePan = true; this.controls.minDistance = 1; this.controls.maxDistance = 18;
    this.controls.maxPolarAngle = Math.PI * .96;
    this.loader = new GLTFLoader();
    this.clock = new THREE.Clock(); this.onFinished = onFinished;
    this.disposed = false; this.request = 0;
    this.resize = new ResizeObserver(() => this.setSize()); this.resize.observe(container);
    this.home(); this.setSize();
    this.renderer.setAnimationLoop(() => {
      if (this.disposed) return;
      const delta = Math.min(this.clock.getDelta(), .05);
      this.mixer?.update(delta); this.controls.update(); this.render();
    });
  }
  setSize(width = this.container.clientWidth, height = this.container.clientHeight) {
    if (!width || !height || this.disposed) return;
    this.renderer.setSize(width, height, false);
    this.camera.aspect = width / height; this.camera.updateProjectionMatrix(); this.render();
  }
  home() {
    this.controls.target.set(0, 0, 0);
    this.camera.position.set(4.5, 2.6, 5.2); this.camera.zoom = 1;
    this.camera.updateProjectionMatrix(); this.controls.update();
  }
  orbit(dx, dy = 0) {
    const vector = this.camera.position.clone().sub(this.controls.target);
    const sphere = new THREE.Spherical().setFromVector3(vector);
    sphere.theta += dx; sphere.phi = THREE.MathUtils.clamp(sphere.phi + dy, .05, Math.PI - .05);
    this.camera.position.copy(this.controls.target).add(new THREE.Vector3().setFromSpherical(sphere));
    this.controls.update(); this.render();
  }
  zoom(factor) {
    const offset = this.camera.position.clone().sub(this.controls.target);
    offset.setLength(THREE.MathUtils.clamp(offset.length() * factor, 1, 18));
    this.camera.position.copy(this.controls.target).add(offset); this.controls.update();
  }
  async load(path, onProgress = () => {}) {
    const request = ++this.request;
    this.abort?.abort(); this.abort = new AbortController();
    this.clear();
    const response = await fetch(path, { signal: this.abort.signal });
    if (!response.ok) throw new Error(`Model download failed (${response.status}).`);
    const length = Number(response.headers.get('content-length'));
    let buffer;
    if (response.body && length) {
      const reader = response.body.getReader(), chunks = []; let loaded = 0;
      while (true) { const { done, value } = await reader.read(); if (done) break; chunks.push(value); loaded += value.length; onProgress(Math.min(95, Math.round(loaded / length * 95))); }
      const data = new Uint8Array(loaded); let offset = 0;
      for (const chunk of chunks) { data.set(chunk, offset); offset += chunk.length; }
      buffer = data.buffer;
    } else buffer = await response.arrayBuffer();
    const gltf = await this.loader.parseAsync(buffer, '');
    if (this.disposed || request !== this.request) { disposeObject(gltf.scene); throw new DOMException('Model selection changed', 'AbortError'); }
    const presentation = new THREE.Group();
    presentation.rotation.x = Math.PI / 2;
    presentation.add(gltf.scene); presentation.updateMatrixWorld(true);
    const bounds = new THREE.Box3().setFromObject(presentation, true);
    const center = bounds.getCenter(new THREE.Vector3()), size = bounds.getSize(new THREE.Vector3());
    const scale = 3.5 / Math.max(size.x, size.y, size.z, .001);
    if (![center.x, center.y, center.z, scale].every(Number.isFinite)) { disposeObject(gltf.scene); throw new Error('Model bounds are invalid.'); }
    this.model = gltf.scene;
    // Presentation transforms live in a parent group; the source GLB is never edited.
    this.modelGroup = new THREE.Group();
    this.modelGroup.add(presentation); this.modelGroup.scale.setScalar(scale);
    this.modelGroup.position.copy(center).multiplyScalar(-scale);
    this.scene.add(this.modelGroup);
    this.grid.position.y = -size.y * scale / 2 - .035;
    this.poses = [];
    this.model.traverse(node => this.poses.push([node, node.position.clone(), node.quaternion.clone(), node.scale.clone()]));
    this.clips = gltf.animations;
    this.mixer = new THREE.AnimationMixer(this.model);
    this.mixer.addEventListener('finished', this.onFinished);
    this.home(); this.render(); onProgress(100);
    return { clips: this.clips.map(c => ({ name: c.name, duration: c.duration })), bounds: size.toArray() };
  }
  play(index) {
    this.stop(); const clip = this.clips?.[index]; if (!clip) return;
    const action = this.mixer.clipAction(clip); action.setLoop(THREE.LoopOnce, 1);
    action.clampWhenFinished = true; action.reset().play(); this.clock.getDelta();
  }
  stop() {
    this.mixer?.stopAllAction();
    for (const [node, position, rotation, scale] of this.poses || []) { node.position.copy(position); node.quaternion.copy(rotation); node.scale.copy(scale); }
    this.model?.updateMatrixWorld(true); this.render();
  }
  clear() {
    this.mixer?.stopAllAction();
    if (this.model) { this.mixer?.uncacheRoot(this.model); disposeObject(this.model); }
    if (this.modelGroup) this.scene.remove(this.modelGroup);
    this.model = this.modelGroup = this.mixer = null; this.poses = []; this.clips = [];
  }
  render() { if (!this.disposed) this.renderer.render(this.scene, this.camera); }
  picture() {
    this.render();
    return new Promise((resolve, reject) => this.renderer.domElement.toBlob(blob => blob ? resolve(blob) : reject(new Error('Thumbnail encoding failed')), 'image/webp', .9));
  }
  dispose() {
    if (this.disposed) return;
    this.abort?.abort(); ++this.request; this.clear();
    this.resize.disconnect(); this.controls.dispose();
    this.renderer.setAnimationLoop(null); this.grid.geometry.dispose(); this.grid.material.dispose();
    this.disposed = true; this.renderer.dispose(); this.renderer.forceContextLoss(); this.renderer.domElement.remove();
  }
}
