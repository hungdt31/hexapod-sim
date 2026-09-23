import { useMemo } from "react";
import * as THREE from "three";

/** Nền kem, lưới 10 cm viền đen; ô lớn 1 m. */
export function Ground() {
  const tex = useMemo(() => {
    const cv = document.createElement("canvas");
    cv.width = cv.height = 256;
    const g = cv.getContext("2d")!;
    g.fillStyle = "#FFF8E7";
    g.fillRect(0, 0, 256, 256);
    g.strokeStyle = "rgba(0,0,0,0.28)";
    g.lineWidth = 4;
    g.strokeRect(0, 0, 256, 256);
    g.strokeStyle = "rgba(0,0,0,0.10)";
    g.lineWidth = 2;
    g.beginPath();
    g.moveTo(128, 0);
    g.lineTo(128, 256);
    g.moveTo(0, 128);
    g.lineTo(256, 128);
    g.stroke();
    const t = new THREE.CanvasTexture(cv);
    t.wrapS = t.wrapT = THREE.RepeatWrapping;
    t.repeat.set(100, 100);
    t.anisotropy = 8;
    t.colorSpace = THREE.SRGBColorSpace;
    return t;
  }, []);
  // Nền không chịu ánh sáng (giữ đúng màu kem) + một lớp chỉ nhận bóng đổ cứng.
  return (
    <group rotation-x={-Math.PI / 2}>
      <mesh>
        <planeGeometry args={[20, 20]} />
        <meshBasicMaterial map={tex} />
      </mesh>
      <mesh position-z={0.0004} receiveShadow>
        <planeGeometry args={[20, 20]} />
        <shadowMaterial opacity={0.22} />
      </mesh>
    </group>
  );
}
