export type AifenceWireV2 = {
  v: 2;
  c: string;
  "R"?: unknown;
  "a"?: unknown;
  "b"?: unknown;
  "d"?: unknown;
  "g"?: unknown;
  "i"?: unknown;
  "m"?: unknown;
  "p"?: unknown;
  "r"?: unknown;
  "s"?: unknown;
  "x"?: unknown;
  "z"?: unknown;
};

export const AIFENCE_PROTOCOL = "aifence/0.2" as const;
export const AIFENCE_WIRE_VERSION = 2 as const;
