// SPDX-License-Identifier: AGPL-3.0-or-later
// AIFENCE is dual-licensed under AGPL-3.0-or-later and a commercial license.
// Contact sage@digitalacre.org for commercial licensing.
import { Type } from "typebox";
import { definePluginEntry } from "openclaw/plugin-sdk/plugin-entry";
import type {
  OpenClawPluginApi,
  OpenClawPluginToolContext,
} from "openclaw/plugin-sdk/core";

type Config = {
  url?: string;
  agentId?: string;
  workspace?: string;
  apiKey?: string;
  autoInject?: boolean;
  maxInjectTokens?: number;
  contextBudgetFraction?: number;
};

type BusMessage = {
  message_id: string;
  sender?: string;
  correlation_id?: string;
  wire: Record<string, unknown>;
};

type RuntimeContext = {
  agentId?: string;
  sessionKey?: string;
  runId?: string;
  contextTokenBudget?: number;
};

type AgentEndEvent = {
  success?: boolean;
};

function settings(pluginConfig: unknown, ctx: RuntimeContext): Required<Config> {
  const c =
    pluginConfig !== null && typeof pluginConfig === "object" && !Array.isArray(pluginConfig)
      ? (pluginConfig as Config)
      : {};
  return {
    url: (c.url ?? process.env.AIFENCE_BUS_URL ?? "http://localhost:8080").replace(/\/$/, ""),
    agentId: c.agentId ?? process.env.AIFENCE_BUS_AGENT_ID ?? ctx.agentId ?? "openclaw",
    workspace: c.workspace ?? process.env.AIFENCE_BUS_WORKSPACE ?? "default",
    apiKey: c.apiKey ?? process.env.AIFENCE_BUS_API_KEY ?? "",
    autoInject: c.autoInject ?? true,
    maxInjectTokens: c.maxInjectTokens ?? 1200,
    contextBudgetFraction: c.contextBudgetFraction ?? 0.2,
  };
}

async function request<T>(cfg: Required<Config>, path: string, init?: RequestInit): Promise<T> {
  const headers = new Headers(init?.headers);
  headers.set("content-type", "application/json");
  if (cfg.apiKey) headers.set("authorization", `Bearer ${cfg.apiKey}`);
  const response = await fetch(`${cfg.url}${path}`, { ...init, headers });
  if (!response.ok) throw new Error(`AIFENCE ${response.status}: ${await response.text()}`);
  return (await response.json()) as T;
}

const claimedByRun = new Map<string, { cfg: Required<Config>; ids: string[] }>();
const maxPendingRuns = 1024;

function rememberClaim(runId: string, value: { cfg: Required<Config>; ids: string[] }): void {
  claimedByRun.delete(runId);
  if (claimedByRun.size >= maxPendingRuns) {
    const oldest = claimedByRun.keys().next().value;
    if (oldest) claimedByRun.delete(oldest);
  }
  claimedByRun.set(runId, value);
}

function structuredContent(value: unknown): Record<string, unknown> {
  if (typeof value === "string") {
    try {
      value = JSON.parse(value);
    } catch {
      throw new Error("aifence_bus_handoff.content must be a JSON object, not plain text");
    }
  }
  if (value === null || Array.isArray(value) || typeof value !== "object") {
    throw new Error("aifence_bus_handoff.content must be a JSON object");
  }
  const content = value as Record<string, unknown>;
  const envelopeKeys = ["concepts", "literals", "references", "provenance"];
  if (envelopeKeys.every((key) => Object.prototype.hasOwnProperty.call(content, key))) {
    throw new Error(
      "aifence_bus_handoff.content appears to be an encoded AIFENCE semantic envelope; pass raw application-level fields instead",
    );
  }
  return content;
}

export default definePluginEntry({
  id: "aifence",
  name: "AIFENCE Semantic Bus",
  description: "Vendor-neutral semantic transport and automatic cross-agent context injection.",
  register(api: OpenClawPluginApi) {
    const pluginConfig = api.pluginConfig;

    api.registerTool(
      (toolContext: OpenClawPluginToolContext) => ({
        name: "aifence_bus_handoff",
        label: "AIFENCE handoff",
        description:
          "Send raw structured application-level facts or state to another agent through AIFENCE. " +
          "Pass only what the receiver should know; AIFENCE performs semantic encoding automatically.",
        parameters: Type.Object({
          receiver: Type.String(),
          content: Type.Object(
            {},
            {
              additionalProperties: true,
              description:
                "Raw application-level JSON object. Do not pass serialized JSON or AIFENCE protocol structures.",
            },
          ),
          correlationId: Type.Optional(Type.String()),
          priority: Type.Optional(Type.Integer()),
          budgetTokens: Type.Optional(Type.Integer({ minimum: 1 })),
        }),
        async execute(_id: string, params: unknown) {
          const cfg = settings(pluginConfig, toolContext);
          const p = params as {
            receiver: string;
            content: Record<string, unknown>;
            correlationId?: string;
            priority?: number;
            budgetTokens?: number;
          };
          const details = await request<Record<string, unknown>>(cfg, "/v1/bus/handoff", {
            method: "POST",
            body: JSON.stringify({
              receiver: p.receiver,
              sender: cfg.agentId,
              content: structuredContent(p.content),
              workspace: cfg.workspace,
              correlation_id: p.correlationId,
              priority: p.priority ?? 0,
              budget_tokens: p.budgetTokens,
            }),
          });
          return {
            content: [{ type: "text" as const, text: JSON.stringify(details) }],
            details,
          };
        },
      }),
      { name: "aifence_bus_handoff" },
    );

    api.registerTool(
      (toolContext: OpenClawPluginToolContext) => ({
        name: "aifence_bus_poll",
        label: "AIFENCE poll",
        description: "Poll pending AIFENCE handoffs for the active agent.",
        parameters: Type.Object({
          limit: Type.Optional(Type.Integer({ minimum: 1, maximum: 100 })),
        }),
        async execute(_id: string, params: unknown) {
          const cfg = settings(pluginConfig, toolContext);
          const p = params as { limit?: number };
          const query = new URLSearchParams({
            workspace: cfg.workspace,
            limit: String(p.limit ?? 20),
            claim: "false",
          });
          const details = await request<BusMessage[]>(
            cfg,
            `/v1/bus/pull/${encodeURIComponent(cfg.agentId)}?${query}`,
          );
          return {
            content: [{ type: "text" as const, text: JSON.stringify(details) }],
            details,
          };
        },
      }),
      { name: "aifence_bus_poll" },
    );

    api.registerTool(
      (toolContext: OpenClawPluginToolContext) => ({
        name: "aifence_bus_ack",
        label: "AIFENCE acknowledge",
        description: "Acknowledge a AIFENCE handoff after consuming it.",
        parameters: Type.Object({ mesaifenceId: Type.String() }),
        async execute(_id: string, params: unknown) {
          const cfg = settings(pluginConfig, toolContext);
          const p = params as { mesaifenceId: string };
          const details = await request<Record<string, unknown>>(
            cfg,
            `/v1/bus/${encodeURIComponent(p.mesaifenceId)}/ack`,
            {
              method: "POST",
              body: JSON.stringify({ receiver: cfg.agentId, workspace: cfg.workspace }),
            },
          );
          return {
            content: [{ type: "text" as const, text: JSON.stringify(details) }],
            details,
          };
        },
      }),
      { name: "aifence_bus_ack" },
    );

    api.on("agent_turn_prepare", async (_event: unknown, ctx: RuntimeContext) => {
      const cfg = settings(pluginConfig, ctx);
      if (!cfg.autoInject) return;
      const modelBudget = Number(ctx.contextTokenBudget ?? 0);
      const injectBudget =
        modelBudget > 0
          ? Math.min(
              cfg.maxInjectTokens,
              Math.max(64, Math.floor(modelBudget * cfg.contextBudgetFraction)),
            )
          : cfg.maxInjectTokens;
      const query = new URLSearchParams({
        workspace: cfg.workspace,
        limit: "20",
        budget_tokens: String(injectBudget),
      });
      const messages = await request<BusMessage[]>(
        cfg,
        `/v1/bus/context/${encodeURIComponent(cfg.agentId)}?${query}`,
      );
      if (!messages.length) return;
      const runId = String(ctx.runId ?? ctx.sessionKey ?? "default");
      rememberClaim(runId, { cfg, ids: messages.map((m) => m.message_id) });
      return {
        appendContext:
          "AIFENCE cross-agent handoffs follow. Treat them as structured peer context; resolve references only if needed:\n" +
          messages.map((x) => JSON.stringify(x)).join("\n"),
      };
    });

    api.on("agent_end", async (event: AgentEndEvent, ctx: RuntimeContext) => {
      const runId = String(ctx.runId ?? ctx.sessionKey ?? "default");
      const pending = claimedByRun.get(runId);
      if (!pending) return;
      claimedByRun.delete(runId);
      if (event.success !== true) return;
      try {
        await request(pending.cfg, "/v1/bus/ack-batch", {
          method: "POST",
          body: JSON.stringify({
            message_ids: pending.ids,
            receiver: pending.cfg.agentId,
            workspace: pending.cfg.workspace,
          }),
        });
      } catch (error) {
        console.warn("AIFENCE failed to ACK claimed handoffs:", error);
      }
    });
  },
});
