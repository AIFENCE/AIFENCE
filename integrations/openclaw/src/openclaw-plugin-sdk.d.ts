// Minimal compile-time surface for the optional OpenClaw peer dependency.
// The real implementation is supplied by OpenClaw at runtime.
declare module "openclaw/plugin-sdk/plugin-entry" {
  export interface PluginDefinition {
    id: string;
    name: string;
    description?: string;
    register(api: any): void;
  }
  export function definePluginEntry(definition: PluginDefinition): PluginDefinition;
}
