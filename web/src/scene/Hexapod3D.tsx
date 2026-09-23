import { useMemo, useRef, type MutableRefObject } from "react";
import { useFrame } from "@react-three/fiber";
import * as THREE from "three";
import type { HelloMsg, StateMsg } from "@/lib/types";
import { COLORS, inkOutline, inkSolid, toon } from "./materials";

interface LegRefs {
  coxa: THREE.Group;
  femur: THREE.Group;
  tibia: THREE.Group;
  mats: THREE.MeshToonMaterial[];
}

function Link({ len, mat }: { len: number; mat: THREE.Material }) {
  return (
    <group position-x={len / 2}>
      <mesh material={inkOutline}>
        <boxGeometry args={[len + 0.008, 0.029, 0.029]} />
      </mesh>
      <mesh material={mat} castShadow>
        <boxGeometry args={[len, 0.02, 0.02]} />
      </mesh>
    </group>
  );
}

function Joint({ r }: { r: number }) {
  return (
    <mesh material={inkSolid} castShadow>
      <sphereGeometry args={[r, 16, 12]} />
    </mesh>
  );
}

/** Robot trong hệ robot (Z hướng lên); đặt trong group đã xoay −90° quanh X. Góc khớp đọc từ stateRef mỗi frame. */
export function Hexapod3D({ robot, stateRef }: { robot: HelloMsg["robot"]; stateRef: MutableRefObject<StateMsg | null> }) {
  const [l1, l2, l3] = robot.lengths;
  const R = robot.body_radius;
  const angles = useMemo(() => robot.mount_angles_deg.map((d) => (d * Math.PI) / 180), [robot]);
  const body = useRef<THREE.Group>(null!);
  const legs = useRef<LegRefs[]>([]);
  const whiteMat = useMemo(() => toon(COLORS.white), []);
  const plateMat = useMemo(() => toon(COLORS.swing), []);
  const legMats = useMemo(() => angles.map(() => [toon(COLORS.stance), toon(COLORS.stance), toon(COLORS.stance)]), [angles]);

  const hexGeo = useMemo(() => {
    const make = (rad: number, depth: number) => {
      const s = new THREE.Shape();
      angles.forEach((a, i) => (i ? s.lineTo(rad * Math.cos(a), rad * Math.sin(a)) : s.moveTo(rad * Math.cos(a), rad * Math.sin(a))));
      s.closePath();
      const g = new THREE.ExtrudeGeometry(s, { depth, bevelEnabled: false });
      g.translate(0, 0, -depth / 2);
      return g;
    };
    return { inner: make(R * 1.12, 0.034), outer: make(R * 1.19, 0.042) };
  }, [angles, R]);

  const arrowGeo = useMemo(() => {
    const s = new THREE.Shape();
    s.moveTo(0.075, 0);
    s.lineTo(0.02, 0.035);
    s.lineTo(0.02, -0.035);
    s.closePath();
    return new THREE.ExtrudeGeometry(s, { depth: 0.004, bevelEnabled: false });
  }, []);

  useFrame(() => {
    const st = stateRef.current;
    if (!st || !body.current) return;
    // Backend kinematic đặt tâm cầu bàn chân ở z = 0 → nâng robot lên bán kính bàn chân để chân chạm nền.
    const lift = st.backend === "kinematic" ? robot.foot_radius : 0;
    body.current.position.set(st.body.pos[0], st.body.pos[1], st.body.pos[2] + lift);
    const [w, x, y, z] = st.body.quat;
    body.current.quaternion.set(x, y, z, w);
    legs.current.forEach((L, i) => {
      if (!L) return;
      const q = st.q[i];
      L.coxa.rotation.z = q[0];
      L.femur.rotation.y = -q[1];
      L.tibia.rotation.y = -q[2];
      const c = st.contacts[i] ? COLORS.stance : COLORS.swing;
      L.mats.forEach((m) => m.color.copy(c));
    });
  });

  return (
    <group ref={body}>
      <mesh geometry={hexGeo.outer} material={inkOutline} />
      <mesh geometry={hexGeo.inner} material={whiteMat} castShadow />
      <mesh geometry={arrowGeo} material={inkSolid} position-z={0.017} />
      <mesh material={plateMat} position={[-0.03, 0, 0.019]}>
        <boxGeometry args={[0.05, 0.05, 0.004]} />
      </mesh>
      {angles.map((a, i) => (
        <group key={i} position={[R * Math.cos(a), R * Math.sin(a), 0]} rotation-z={a}>
          <group
            ref={(g) => {
              if (g) legs.current[i] = { ...(legs.current[i] ?? {}), coxa: g, mats: legMats[i] } as LegRefs;
            }}
          >
            <Joint r={0.016} />
            <Link len={l1} mat={whiteMat} />
            <group
              position-x={l1}
              ref={(g) => {
                if (g) legs.current[i] = { ...legs.current[i], femur: g };
              }}
            >
              <Joint r={0.014} />
              <Link len={l2} mat={legMats[i][0]} />
              <group
                position-x={l2}
                ref={(g) => {
                  if (g) legs.current[i] = { ...legs.current[i], tibia: g };
                }}
              >
                <Joint r={0.013} />
                <Link len={l3} mat={legMats[i][1]} />
                <group position-x={l3}>
                  <mesh material={inkOutline}>
                    <sphereGeometry args={[robot.foot_radius + 0.0045, 16, 12]} />
                  </mesh>
                  <mesh material={legMats[i][2]} castShadow>
                    <sphereGeometry args={[robot.foot_radius, 16, 12]} />
                  </mesh>
                </group>
              </group>
            </group>
          </group>
        </group>
      ))}
    </group>
  );
}
