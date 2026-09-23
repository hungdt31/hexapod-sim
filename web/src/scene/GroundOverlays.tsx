import { useMemo, useRef, type MutableRefObject } from "react";
import { useFrame } from "@react-three/fiber";
import * as THREE from "three";
import type { StateMsg } from "@/lib/types";
import { inkSolid } from "./materials";

const TRAIL_COUNT = 72;

/** Support polygon, hình chiếu CoM và vết chân — vẽ trên mặt đất trong hệ robot. */
export function GroundOverlays({ stateRef }: { stateRef: MutableRefObject<StateMsg | null> }) {
  const poly = useRef<THREE.Mesh>(null!);
  const line = useRef<THREE.Line>(null!);
  const com = useRef<THREE.Group>(null!);
  const trails = useRef<THREE.InstancedMesh>(null!);
  const last = useRef({ key: "", contacts: [true, true, true, true, true, true], idx: 0, t: -1 });
  const dummy = useMemo(() => new THREE.Object3D(), []);
  const lineMat = useMemo(() => new THREE.LineDashedMaterial({ color: 0x000000, dashSize: 0.015, gapSize: 0.01 }), []);
  const lineObj = useMemo(() => new THREE.Line(new THREE.BufferGeometry(), lineMat), [lineMat]);

  useFrame(() => {
    const st = stateRef.current;
    if (!st) return;
    const L = last.current;
    if (st.t < L.t) {
      // reset -> xóa vết chân
      for (let i = 0; i < TRAIL_COUNT; i++) {
        dummy.position.set(0, 0, -1);
        dummy.updateMatrix();
        trails.current.setMatrixAt(i, dummy.matrix);
      }
      trails.current.instanceMatrix.needsUpdate = true;
    }
    L.t = st.t;
    const key = JSON.stringify(st.support);
    if (key !== L.key) {
      L.key = key;
      if (st.support.length >= 3) {
        const s = new THREE.Shape(st.support.map(([x, y]) => new THREE.Vector2(x, y)));
        poly.current.geometry.dispose();
        poly.current.geometry = new THREE.ShapeGeometry(s);
        poly.current.visible = true;
        const pts = [...st.support, st.support[0]].map(([x, y]) => new THREE.Vector3(x, y, 0.0018));
        line.current.geometry.dispose();
        line.current.geometry = new THREE.BufferGeometry().setFromPoints(pts);
        line.current.computeLineDistances();
        line.current.visible = true;
      } else {
        poly.current.visible = false;
        line.current.visible = false;
      }
    }
    com.current.position.set(st.com[0], st.com[1], 0.0025);
    st.contacts.forEach((c, i) => {
      if (c && !L.contacts[i]) {
        dummy.position.set(st.feet[i][0], st.feet[i][1], 0.0012);
        dummy.updateMatrix();
        trails.current.setMatrixAt(L.idx, dummy.matrix);
        trails.current.instanceMatrix.needsUpdate = true;
        L.idx = (L.idx + 1) % TRAIL_COUNT;
      }
    });
    L.contacts = st.contacts.slice();
  });

  const hidden = useMemo(() => {
    const m = new THREE.Matrix4().makeTranslation(0, 0, -1);
    return m;
  }, []);

  return (
    <group>
      <mesh ref={poly} position-z={0.001} visible={false}>
        <shapeGeometry />
        <meshBasicMaterial color="#9FE6D5" transparent opacity={0.6} depthWrite={false} />
      </mesh>
      <primitive object={lineObj} ref={line} />
      <group ref={com}>
        <mesh material={inkSolid}>
          <circleGeometry args={[0.016, 24]} />
        </mesh>
        <mesh position-z={0.0005}>
          <circleGeometry args={[0.011, 24]} />
          <meshBasicMaterial color="#FF6B6B" />
        </mesh>
      </group>
      <instancedMesh
        ref={(m) => {
          if (m && !trails.current) {
            for (let i = 0; i < TRAIL_COUNT; i++) m.setMatrixAt(i, hidden);
            m.instanceMatrix.needsUpdate = true;
          }
          if (m) trails.current = m;
        }}
        args={[undefined, undefined, TRAIL_COUNT]}
        frustumCulled={false}
      >
        <circleGeometry args={[0.009, 16]} />
        <meshBasicMaterial color="#000000" transparent opacity={0.35} depthWrite={false} />
      </instancedMesh>
    </group>
  );
}
