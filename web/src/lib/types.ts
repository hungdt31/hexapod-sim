export type GaitName = "tripod" | "ripple" | "wave";
export type BackendName = "kinematic" | "mujoco";
export type Vec3 = [number, number, number];

export interface HelloMsg {
  type: "hello";
  robot: {
    body_radius: number;
    lengths: [number, number, number];
    mount_angles_deg: number[];
    stand_height: number;
    foot_radius: number;
    leg_names: string[];
  };
  gaits: Record<GaitName, { beta: number; period: number }>;
  backends: BackendName[];
  control_dt: number;
  broadcast_hz: number;
}

export interface StateMsg {
  type: "state";
  t: number;
  running: boolean;
  gait: GaitName;
  backend: BackendName;
  body: { pos: Vec3; rpy: Vec3; quat: [number, number, number, number] };
  q: Vec3[];
  q_cmd: Vec3[];
  contacts: boolean[];
  swing: boolean[];
  phase: number[];
  feet: Vec3[];
  com: Vec3;
  support: [number, number][];
  stability_margin: number;
  stride: number;
  ik_warn: number;
  command: { vx: number; vy: number; wz: number };
  body_pose: { height: number; roll: number; pitch: number };
  scenario_active: boolean;
}

export interface ErrorMsg {
  type: "error";
  message: string;
}

export type ServerMsg = HelloMsg | StateMsg | ErrorMsg;

export type ClientMsg =
  | { type: "command"; vx: number; vy: number; wz: number }
  | { type: "control"; action: "start" | "pause" | "step" | "reset" }
  | {
      type: "config";
      gait?: GaitName;
      backend?: BackendName;
      body_pose?: { rpy?: Vec3; height?: number };
      swing_height?: number;
    }
  | { type: "scenario"; yaml: string | null };
