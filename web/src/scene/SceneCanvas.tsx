import { useEffect, useRef, type MutableRefObject } from "react";
import { Canvas, useFrame, useThree } from "@react-three/fiber";
import { OrbitControls } from "@react-three/drei";
import * as THREE from "three";
import type { OrbitControls as OrbitControlsImpl } from "three-stdlib";
import type { HelloMsg, StateMsg } from "@/lib/types";
import { Ground } from "./Ground";
import { GroundOverlays } from "./GroundOverlays";
import { Hexapod3D } from "./Hexapod3D";

export type CamPreset = "iso" | "top" | "side";
const OFFSETS: Record<CamPreset, [number, number, number]> = {
  iso: [0.55, 0.36, 0.62],
  top: [0.0001, 1.05, 0.02],
  side: [0, 0.16, 0.85],
};

/** Camera bám theo thân robot; đèn và vùng bóng đổ di chuyển cùng robot. */
function Follow({ stateRef, preset }: { stateRef: MutableRefObject<StateMsg | null>; preset: CamPreset }) {
  const { camera } = useThree();
  const controls = useThree((s) => s.controls) as OrbitControlsImpl | null;
  const last = useRef(new THREE.Vector3(0, 0.06, 0));
  const sun = useRef<THREE.DirectionalLight>(null!);

  useEffect(() => {
    if (!controls) return;
    const o = OFFSETS[preset];
    const t = controls.target;
    camera.position.set(t.x + o[0], o[1], t.z + o[2]);
    controls.update();
  }, [preset, controls, camera]);

  useFrame(() => {
    const st = stateRef.current;
    if (!st || !controls) return;
    const tgt = new THREE.Vector3(st.body.pos[0], 0.06, -st.body.pos[1]);
    if (tgt.distanceTo(last.current) > 1.5) {
      // reset hoặc đổi backend: nhảy thẳng về robot
      controls.target.copy(tgt);
      const o = OFFSETS[preset];
      camera.position.set(tgt.x + o[0], o[1], tgt.z + o[2]);
    } else {
      const d = tgt.clone().sub(last.current);
      camera.position.add(d);
      controls.target.add(d);
    }
    last.current.copy(tgt);
    sun.current.position.set(tgt.x + 0.6, 1.4, tgt.z + 0.35);
    sun.current.target.position.copy(tgt);
    sun.current.target.updateMatrixWorld();
  });

  return (
    <directionalLight
      ref={sun}
      intensity={1.5}
      castShadow
      shadow-mapSize={[1024, 1024]}
      shadow-camera-left={-0.6}
      shadow-camera-right={0.6}
      shadow-camera-top={0.6}
      shadow-camera-bottom={-0.6}
      shadow-camera-near={0.1}
      shadow-camera-far={4}
    />
  );
}

export function SceneCanvas({
  hello,
  stateRef,
  preset,
}: {
  hello: HelloMsg | null;
  stateRef: MutableRefObject<StateMsg | null>;
  preset: CamPreset;
}) {
  return (
    <Canvas
      flat
      shadows={{ type: THREE.BasicShadowMap }}
      dpr={[1, 2]}
      camera={{ fov: 38, near: 0.01, far: 50, position: [0.55, 0.42, 0.62] }}
      gl={{ antialias: true }}
      onCreated={({ gl }) => gl.setClearColor("#FFF8E7")}
    >
      <ambientLight intensity={1.3} />
      <Follow stateRef={stateRef} preset={preset} />
      <OrbitControls makeDefault enableDamping dampingFactor={0.12} minDistance={0.25} maxDistance={3}
        maxPolarAngle={Math.PI * 0.49} target={[0, 0.06, 0]} />
      <Ground />
      <group rotation-x={-Math.PI / 2}>
        <GroundOverlays stateRef={stateRef} />
        {hello && <Hexapod3D robot={hello.robot} stateRef={stateRef} />}
      </group>
    </Canvas>
  );
}
