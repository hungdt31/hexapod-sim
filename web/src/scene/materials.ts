import * as THREE from "three";

export const COLORS = {
  swing: new THREE.Color("#FFD23F"),
  stance: new THREE.Color("#3BCEAC"),
  white: new THREE.Color("#FFFFFF"),
  danger: new THREE.Color("#FF6B6B"),
};

// Toon 3 bậc: shading phẳng kiểu NeoBrutalism
const grad = new THREE.DataTexture(new Uint8Array([110, 190, 255]), 3, 1, THREE.RedFormat);
grad.minFilter = THREE.NearestFilter;
grad.magFilter = THREE.NearestFilter;
grad.needsUpdate = true;

export const toon = (c: THREE.ColorRepresentation) => new THREE.MeshToonMaterial({ color: c, gradientMap: grad });
export const inkOutline = new THREE.MeshBasicMaterial({ color: 0x000000, side: THREE.BackSide });
export const inkSolid = new THREE.MeshBasicMaterial({ color: 0x000000 });
