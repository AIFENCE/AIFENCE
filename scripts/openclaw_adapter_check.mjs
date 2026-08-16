import fs from "node:fs";
import vm from "node:vm";

const source = fs.readFileSync(new URL("../integrations/openclaw/dist/index.js", import.meta.url), "utf8")
  .replace(/^import .*$/gm, "")
  .replace("export default definePluginEntry(", "globalThis.__plugin = definePluginEntry(");

const tools = new Map();
const calls = [];
const context = {
  console,
  process: { env: { SAGE_URL: "http://sage", SAGE_AGENT_ID: "claw-a", SAGE_WORKSPACE: "team" } },
  Headers,
  URLSearchParams,
  encodeURIComponent,
  Type: {
    Object: (properties, options = {}) => ({ type: "object", properties, ...options }),
    String: () => ({ type: "string" }),
    Unknown: () => ({}),
    Optional: (value) => value,
    Integer: (options = {}) => ({ type: "integer", ...options }),
  },
  definePluginEntry: (value) => value,
  fetch: async (_url, init) => {
    calls.push(JSON.parse(init.body));
    return { ok: true, json: async () => ({ ok: true }), text: async () => "" };
  },
};
vm.createContext(context);
vm.runInContext(source, context);
context.__plugin.register({
  registerTool(tool) { tools.set(tool.name, tool); },
  on() {},
});

const handoff = tools.get("sage_handoff");
if (!handoff) throw new Error("sage_handoff not registered");
if (handoff.parameters.properties.content.type !== "object") throw new Error("content schema is not object");

await handoff.execute("1", { receiver: "peer", content: { value: 7 } }, {});
if (calls.at(-1).content.value !== 7) throw new Error("object content changed");
await handoff.execute("2", { receiver: "peer", content: '{"value":8}' }, {});
if (calls.at(-1).content.value !== 8) throw new Error("JSON object string was not normalized");

let plainRejected = false;
try { await handoff.execute("3", { receiver: "peer", content: "plain text" }, {}); }
catch (error) { plainRejected = String(error).includes("JSON object, not plain text"); }
if (!plainRejected) throw new Error("plain text was not rejected");

let envelopeRejected = false;
try {
  await handoff.execute("4", {
    receiver: "peer",
    content: { concepts: [], literals: [], references: [], provenance: {} },
  }, {});
} catch (error) { envelopeRejected = String(error).includes("encoded SAGE semantic envelope"); }
if (!envelopeRejected) throw new Error("semantic envelope was not rejected");

console.log(JSON.stringify({ ok: true, adapter: "openclaw", checks: 5 }));
