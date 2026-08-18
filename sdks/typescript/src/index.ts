// SPDX-FileCopyrightText: 2026 AIFENCE contributors
// SPDX-License-Identifier: Apache-2.0
export type Outcome =
  | "allow"
  | "allow_with_limits"
  | "redact_or_transform"
  | "require_approval"
  | "deny"
  | "quarantine_and_terminate";

export type JsonObject = Record<string, unknown>;

export interface Finding {
  detector: string;
  category: string;
  severity: "info" | "low" | "medium" | "high" | "critical";
  confidence: number;
  evidence: string;
  attributes: JsonObject;
}

export interface DecisionResponse {
  decision_id: string;
  trace_id: string;
  outcome: Outcome;
  risk_score: number;
  reasons: string[];
  constraints: JsonObject;
  findings: Finding[];
  policy_version: string;
  approval_id: string | null;
  receipt: string;
  expires_at: string;
}

export interface CapabilityIssueRequest {
  decision_id: string;
  lifetime_seconds?: number;
}

export interface CapabilityConsumeRequest {
  token: string;
  agent_id: string;
  trace_id: string;
  tool: string;
  operation: string;
  resource: string;
  execution: JsonObject;
}

export interface ArtifactUpload {
  traceId: string;
  filename: string;
  mediaType: string;
  content: Blob;
}

export interface BinaryResponse {
  content: Uint8Array;
  contentType: string | null;
  contentDisposition: string | null;
}

export class AifenceError extends Error {
  constructor(
    readonly statusCode: number,
    readonly code: string,
    message: string,
    readonly details: JsonObject = {},
  ) {
    super(`${code}: ${message}`);
    this.name = "AifenceError";
  }
}

export interface ClientOptions {
  timeoutMs?: number;
  maxRetries?: number;
  maxResponseBytes?: number;
  fetch?: typeof globalThis.fetch;
}

const RETRYABLE_STATUS_CODES = new Set([429, 502, 503, 504]);

export class AifenceClient {
  private readonly baseUrl: string;
  private readonly timeoutMs: number;
  private readonly maxRetries: number;
  private readonly maxResponseBytes: number;
  private readonly fetchImpl: typeof globalThis.fetch;

  constructor(baseUrl: string, private readonly apiKey: string, options: ClientOptions = {}) {
    if (!baseUrl.startsWith("https://")) throw new Error("AIFENCE base URL must use HTTPS");
    if (!apiKey) throw new Error("AIFENCE API key is required");
    if ((options.maxRetries ?? 3) < 0) throw new Error("maxRetries cannot be negative");
    if ((options.maxResponseBytes ?? 16 * 1024 * 1024) < 1) {
      throw new Error("maxResponseBytes must be positive");
    }
    this.baseUrl = baseUrl.replace(/\/$/, "");
    this.timeoutMs = options.timeoutMs ?? 30_000;
    this.maxRetries = options.maxRetries ?? 3;
    this.maxResponseBytes = options.maxResponseBytes ?? 16 * 1024 * 1024;
    this.fetchImpl = options.fetch ?? globalThis.fetch;
  }

  createApiKey(request: JsonObject): Promise<JsonObject> {
    return this.requestJson("POST", "/v1/api-keys", request);
  }

  listApiKeys(): Promise<JsonObject[]> {
    return this.requestJson("GET", "/v1/api-keys", undefined, true);
  }

  revokeApiKey(keyId: string, reason: string): Promise<JsonObject> {
    return this.requestJson("POST", `/v1/api-keys/${this.segment(keyId)}/revoke`, {reason});
  }

  registerAgent(registration: JsonObject): Promise<JsonObject> {
    return this.requestJson("POST", "/v1/agents/register", registration);
  }

  getAgent(agentId: string): Promise<JsonObject> {
    return this.requestJson("GET", `/v1/agents/${this.segment(agentId)}`, undefined, true);
  }

  revokeAgent(agentId: string, reason: string): Promise<JsonObject> {
    return this.requestJson("POST", `/v1/agents/${this.segment(agentId)}/revoke`, {reason});
  }

  decide(request: JsonObject, idempotencyKey = crypto.randomUUID()): Promise<DecisionResponse> {
    return this.requestJson(
      "POST",
      "/v1/decisions",
      {...request, idempotency_key: request.idempotency_key ?? idempotencyKey},
      true,
    );
  }

  getDecision(decisionId: string): Promise<DecisionResponse> {
    return this.requestJson("GET", `/v1/decisions/${this.segment(decisionId)}`, undefined, true);
  }

  ingestEvent(event: JsonObject): Promise<JsonObject> {
    return this.requestJson("POST", "/v1/events", event);
  }

  getTrace(traceId: string): Promise<JsonObject[]> {
    return this.requestJson("GET", `/v1/traces/${this.segment(traceId)}`, undefined, true);
  }

  listPolicies(): Promise<JsonObject[]> {
    return this.requestJson("GET", "/v1/policies", undefined, true);
  }

  publishPolicy(request: JsonObject): Promise<JsonObject> {
    return this.requestJson("POST", "/v1/policies", {...request, activate: false});
  }

  activatePolicy(policyId: string, reason: string): Promise<JsonObject> {
    return this.requestJson("POST", `/v1/policies/${this.segment(policyId)}/activate`, {reason});
  }

  listApprovals(status?: string): Promise<JsonObject[]> {
    return this.requestJson("GET", this.withQuery("/v1/approvals", {status}), undefined, true);
  }

  getApproval(approvalId: string): Promise<JsonObject> {
    return this.requestJson("GET", `/v1/approvals/${this.segment(approvalId)}`, undefined, true);
  }

  decideApproval(
    approvalId: string,
    decision: "approved" | "rejected",
    reason: string,
  ): Promise<JsonObject> {
    return this.requestJson(
      "POST",
      `/v1/approvals/${this.segment(approvalId)}/decision`,
      {decision, reason},
    );
  }

  issueCapability(request: CapabilityIssueRequest): Promise<JsonObject> {
    return this.requestJson("POST", "/v1/capabilities", request);
  }

  consumeCapability(request: CapabilityConsumeRequest): Promise<JsonObject> {
    return this.requestJson("POST", "/v1/capabilities/consume", request);
  }

  revokeCapability(capabilityId: string, reason: string): Promise<JsonObject> {
    return this.requestJson(
      "POST",
      `/v1/capabilities/${this.segment(capabilityId)}/revoke`,
      {reason},
    );
  }

  async scanArtifact(upload: ArtifactUpload): Promise<JsonObject> {
    const form = new FormData();
    form.set("trace_id", upload.traceId);
    form.set("artifact", upload.content, upload.filename);
    return this.requestJson("POST", "/v1/artifacts/scan", form, false, {
      Accept: "application/json",
      "X-Aifence-SDK": "typescript/1.0.0-rc.5",
    });
  }

  getArtifact(artifactId: string): Promise<JsonObject> {
    return this.requestJson("GET", `/v1/artifacts/${this.segment(artifactId)}`, undefined, true);
  }

  async downloadArtifact(artifactId: string): Promise<BinaryResponse> {
    const {response, content} = await this.requestRaw(
      "GET",
      `/v1/artifacts/${this.segment(artifactId)}/content`,
      undefined,
      true,
    );
    return {
      content,
      contentType: response.headers.get("content-type"),
      contentDisposition: response.headers.get("content-disposition"),
    };
  }

  listIncidents(status?: string): Promise<JsonObject[]> {
    return this.requestJson("GET", this.withQuery("/v1/incidents", {status}), undefined, true);
  }

  createIncident(request: JsonObject): Promise<JsonObject> {
    return this.requestJson("POST", "/v1/incidents", request);
  }

  getIncident(incidentId: string): Promise<JsonObject> {
    return this.requestJson("GET", `/v1/incidents/${this.segment(incidentId)}`, undefined, true);
  }

  updateIncident(incidentId: string, status: string, reason: string): Promise<JsonObject> {
    return this.requestJson(
      "POST",
      `/v1/incidents/${this.segment(incidentId)}/status`,
      {status, reason},
    );
  }

  listProviders(): Promise<JsonObject[]> {
    return this.requestJson("GET", "/v1/providers", undefined, true);
  }

  registerProvider(request: JsonObject): Promise<JsonObject> {
    return this.requestJson("POST", "/v1/providers", request);
  }

  revokeProvider(providerId: string, reason: string): Promise<JsonObject> {
    return this.requestJson("POST", `/v1/providers/${this.segment(providerId)}/revoke`, {reason});
  }

  invokeProvider(
    providerId: string,
    request: JsonObject,
    idempotencyKey = crypto.randomUUID(),
  ): Promise<JsonObject> {
    return this.requestJson(
      "POST",
      `/v1/providers/${this.segment(providerId)}/invoke`,
      {...request, idempotency_key: request.idempotency_key ?? idempotencyKey},
      true,
    );
  }

  listTools(): Promise<JsonObject[]> {
    return this.requestJson("GET", "/v1/tools", undefined, true);
  }

  registerTool(request: JsonObject): Promise<JsonObject> {
    return this.requestJson("POST", "/v1/tools", request);
  }

  revokeTool(toolId: string, reason: string): Promise<JsonObject> {
    return this.requestJson("POST", `/v1/tools/${this.segment(toolId)}/revoke`, {reason});
  }

  executeTool(
    toolId: string,
    request: JsonObject,
    idempotencyKey = crypto.randomUUID(),
  ): Promise<JsonObject> {
    return this.requestJson(
      "POST",
      `/v1/tools/${this.segment(toolId)}/execute`,
      {...request, idempotency_key: request.idempotency_key ?? idempotencyKey},
      true,
    );
  }

  verifyAudit(): Promise<JsonObject> {
    return this.requestJson("GET", "/v1/audit/verify", undefined, true);
  }

  listAuditCheckpoints(limit = 100): Promise<JsonObject[]> {
    return this.requestJson(
      "GET",
      this.withQuery("/v1/audit/checkpoints", {limit: String(limit)}),
      undefined,
      true,
    );
  }

  getExecution(executionId: string): Promise<JsonObject> {
    return this.requestJson(
      "GET",
      `/v1/executions/${this.segment(executionId)}`,
      undefined,
      true,
    );
  }

  reconcileExecution(executionId: string, request: JsonObject): Promise<JsonObject> {
    return this.requestJson(
      "POST",
      `/v1/executions/${this.segment(executionId)}/reconcile`,
      request,
    );
  }

  recoverStaleExecutions(limit = 100): Promise<JsonObject> {
    return this.requestJson(
      "POST",
      this.withQuery("/v1/executions/recover-stale", {limit: String(limit)}),
    );
  }

  createWorkloadIdentity(request: JsonObject): Promise<JsonObject> {
    return this.requestJson("POST", "/v1/workload-identities", request);
  }

  listWorkloadIdentities(): Promise<JsonObject[]> {
    return this.requestJson("GET", "/v1/workload-identities", undefined, true);
  }

  revokeWorkloadIdentity(bindingId: string, reason: string): Promise<JsonObject> {
    return this.requestJson("POST", `/v1/workload-identities/${this.segment(bindingId)}/revoke`, {reason});
  }

  validatePolicy(document: JsonObject): Promise<JsonObject> {
    return this.requestJson("POST", "/v1/policies/validate", {document});
  }

  simulatePolicy(document: JsonObject, cases: JsonObject[]): Promise<JsonObject> {
    return this.requestJson("POST", "/v1/policies/simulate", {document, cases});
  }

  diffPolicy(currentDocument: JsonObject, proposedDocument: JsonObject, cases: JsonObject[] = []): Promise<JsonObject> {
    return this.requestJson("POST", "/v1/policies/diff", {
      current_document: currentDocument,
      proposed_document: proposedDocument,
      cases,
    });
  }

  replayPolicy(policyId: string, limit = 100): Promise<JsonObject> {
    return this.requestJson("POST", this.withQuery(`/v1/policies/${this.segment(policyId)}/replay`, {limit: String(limit)}));
  }

  canaryPolicy(policyId: string, percentage: number, reason: string): Promise<JsonObject> {
    return this.requestJson("POST", `/v1/policies/${this.segment(policyId)}/canary`, {percentage, reason});
  }

  shadowPolicy(policyId: string, reason: string): Promise<JsonObject> {
    return this.requestJson("POST", `/v1/policies/${this.segment(policyId)}/shadow`, {reason});
  }

  rollbackPolicy(policyId: string, reason: string): Promise<JsonObject> {
    return this.requestJson("POST", `/v1/policies/${this.segment(policyId)}/rollback`, {reason});
  }

  anchorAudit(destination: "file" | "webhook" = "file"): Promise<JsonObject> {
    return this.requestJson("POST", "/v1/audit/anchors", {destination});
  }

  verifyAuditAnchor(anchorId: string): Promise<JsonObject> {
    return this.requestJson("POST", `/v1/audit/anchors/${this.segment(anchorId)}/verify`);
  }

  anchorAuditBatch(destinations: string[], requiredQuorum = 1): Promise<JsonObject> {
    return this.requestJson("POST", "/v1/audit/anchors/batch", {
      destinations,
      required_quorum: requiredQuorum,
    });
  }

  auditAnchorQuorum(sequence?: number, requiredQuorum?: number): Promise<JsonObject> {
    const query: Record<string, string> = {};
    if (sequence !== undefined) query.sequence = String(sequence);
    if (requiredQuorum !== undefined) query.required_quorum = String(requiredQuorum);
    return this.requestJson("GET", this.withQuery("/v1/audit/anchors/quorum", query), undefined, true);
  }

  writeMemory(request: JsonObject): Promise<JsonObject> {
    return this.requestJson("POST", "/v1/memory", request);
  }

  readMemory(memoryId: string, includeContent = false): Promise<JsonObject> {
    return this.requestJson("GET", this.withQuery(`/v1/memory/${this.segment(memoryId)}`, {include_content: String(includeContent)}), undefined, true);
  }

  updateMemoryStatus(memoryId: string, status: string, reason: string): Promise<JsonObject> {
    return this.requestJson("POST", `/v1/memory/${this.segment(memoryId)}/status`, {status, reason});
  }

  createDelegation(request: JsonObject): Promise<JsonObject> {
    return this.requestJson("POST", "/v1/delegations", request);
  }

  revokeDelegation(grantId: string, reason: string): Promise<JsonObject> {
    return this.requestJson("POST", `/v1/delegations/${this.segment(grantId)}/revoke`, {reason});
  }

  createBudget(request: JsonObject): Promise<JsonObject> {
    return this.requestJson("POST", "/v1/budgets", request);
  }

  reserveBudget(budgetId: string, request: JsonObject): Promise<JsonObject> {
    return this.requestJson("POST", `/v1/budgets/${this.segment(budgetId)}/reserve`, request);
  }

  settleBudget(reservationId: string, request: JsonObject): Promise<JsonObject> {
    return this.requestJson("POST", `/v1/budget-reservations/${this.segment(reservationId)}/settle`, request);
  }

  requestTenantLifecycle(request: JsonObject): Promise<JsonObject> {
    return this.requestJson("POST", "/v1/tenant/lifecycle", request);
  }

  getTenantLifecycle(jobId: string): Promise<JsonObject> {
    return this.requestJson("GET", `/v1/tenant/lifecycle/${this.segment(jobId)}`, undefined, true);
  }

  async downloadTenantExport(jobId: string): Promise<BinaryResponse> {
    const {response, content} = await this.requestRaw(
      "GET", `/v1/tenant/lifecycle/${this.segment(jobId)}/content`, undefined, true,
    );
    return {
      content,
      contentType: response.headers.get("content-type"),
      contentDisposition: response.headers.get("content-disposition"),
    };
  }

  reconcileTenantLifecycle(
    jobId: string,
    resolution: "confirmed_destroyed" | "confirmed_not_destroyed",
    reason: string,
    destructionReceipt: JsonObject = {},
  ): Promise<JsonObject> {
    return this.requestJson("POST", `/v1/tenant/lifecycle/${this.segment(jobId)}/reconcile`, {
      resolution,
      reason,
      destruction_receipt: destructionReceipt,
    });
  }

  createLegalHold(request: JsonObject): Promise<JsonObject> {
    return this.requestJson("POST", "/v1/tenant/legal-holds", request);
  }

  listLegalHolds(): Promise<JsonObject[]> {
    return this.requestJson("GET", "/v1/tenant/legal-holds", undefined, true);
  }

  releaseLegalHold(holdId: string, reason: string): Promise<JsonObject> {
    return this.requestJson("POST", `/v1/tenant/legal-holds/${this.segment(holdId)}/release`, {reason});
  }

  registerProtocol(request: JsonObject): Promise<JsonObject> {
    return this.requestJson("POST", "/v1/protocols", request);
  }

  listProtocolManifestVersions(registrationId: string): Promise<JsonObject[]> {
    return this.requestJson(
      "GET", `/v1/protocols/${this.segment(registrationId)}/manifest-versions`, undefined, true,
    );
  }

  authorizeA2A(registrationId: string, request: JsonObject): Promise<JsonObject> {
    return this.requestJson("POST", `/v1/protocols/a2a/${this.segment(registrationId)}/authorize`, request);
  }

  callMCPTool(registrationId: string, request: JsonObject): Promise<JsonObject> {
    return this.requestJson("POST", `/v1/protocols/mcp/${this.segment(registrationId)}/tools/call`, request);
  }

  runDispatcher(limit = 20): Promise<JsonObject> {
    return this.requestJson("POST", this.withQuery("/v1/dispatch/run", {limit: String(limit)}));
  }

  private async requestJson<T>(
    method: string,
    path: string,
    body?: unknown,
    retryable = false,
    headers?: Record<string, string>,
  ): Promise<T> {
    const {content} = await this.requestRaw(method, path, body, retryable, headers);
    if (content.byteLength === 0) return undefined as T;
    try {
      return JSON.parse(new TextDecoder().decode(content)) as T;
    } catch (error) {
      throw new Error(`AIFENCE returned invalid JSON: ${String(error)}`);
    }
  }

  private async requestRaw(
    method: string,
    path: string,
    body?: unknown,
    retryable = false,
    headers?: Record<string, string>,
  ): Promise<{response: Response; content: Uint8Array}> {
    const attempts = retryable ? this.maxRetries + 1 : 1;
    let response: Response | undefined;
    for (let attempt = 0; attempt < attempts; attempt += 1) {
      const controller = new AbortController();
      const timeout = setTimeout(() => controller.abort(), this.timeoutMs);
      try {
        const requestHeaders: Record<string, string> = {
          Authorization: `Bearer ${this.apiKey}`,
          Accept: "application/json",
          "X-Aifence-SDK": "typescript/1.0.0-rc.5",
          ...headers,
        };
        let encodedBody: BodyInit | undefined;
        if (body instanceof FormData) {
          encodedBody = body;
        } else if (body !== undefined) {
          requestHeaders["Content-Type"] = "application/json";
          encodedBody = JSON.stringify(body);
        }
        const init: RequestInit = {
          method,
          headers: requestHeaders,
          signal: controller.signal,
          redirect: "error",
        };
        if (encodedBody !== undefined) init.body = encodedBody;
        response = await this.fetchImpl(`${this.baseUrl}${path}`, init);
      } catch (error) {
        if (attempt + 1 >= attempts) throw error;
        await this.sleep(this.retryDelay(undefined, attempt));
        continue;
      } finally {
        clearTimeout(timeout);
      }
      if (!RETRYABLE_STATUS_CODES.has(response.status) || attempt + 1 >= attempts) break;
      await this.sleep(this.retryDelay(response, attempt));
    }
    if (!response) throw new Error("AIFENCE request did not produce a response");
    const content = await this.readBounded(response);
    if (!response.ok) {
      let error: JsonObject = {};
      try {
        const payload = JSON.parse(new TextDecoder().decode(content)) as JsonObject;
        if (typeof payload.error === "object" && payload.error !== null) {
          error = payload.error as JsonObject;
        }
      } catch {
        error = {};
      }
      throw new AifenceError(
        response.status,
        String(error.code ?? "http_error"),
        String(error.message ?? response.statusText),
        typeof error.details === "object" && error.details !== null
          ? (error.details as JsonObject)
          : {},
      );
    }
    return {response, content};
  }

  private async readBounded(response: Response): Promise<Uint8Array> {
    const declared = Number(response.headers.get("content-length"));
    if (Number.isFinite(declared) && declared > this.maxResponseBytes) {
      throw new Error("AIFENCE response exceeds maxResponseBytes");
    }
    if (!response.body) return new Uint8Array();
    const reader = response.body.getReader();
    const chunks: Uint8Array[] = [];
    let total = 0;
    for (;;) {
      const {done, value} = await reader.read();
      if (done) break;
      total += value.byteLength;
      if (total > this.maxResponseBytes) {
        await reader.cancel("response too large");
        throw new Error("AIFENCE response exceeds maxResponseBytes");
      }
      chunks.push(value);
    }
    const content = new Uint8Array(total);
    let offset = 0;
    for (const chunk of chunks) {
      content.set(chunk, offset);
      offset += chunk.byteLength;
    }
    return content;
  }

  private retryDelay(response: Response | undefined, attempt: number): number {
    const retryAfter = response?.headers.get("retry-after");
    if (retryAfter !== null && retryAfter !== undefined) {
      const seconds = Number(retryAfter);
      if (Number.isFinite(seconds) && seconds > 0) return Math.min(seconds, 60) * 1000;
    }
    return Math.min(2 ** attempt, 8) * 1000;
  }

  private sleep(milliseconds: number): Promise<void> {
    return new Promise((resolve) => setTimeout(resolve, milliseconds));
  }

  private segment(value: string): string {
    return encodeURIComponent(value);
  }

  private withQuery(path: string, values: Record<string, string | undefined>): string {
    const query = new URLSearchParams();
    for (const [key, value] of Object.entries(values)) {
      if (value !== undefined) query.set(key, value);
    }
    const encoded = query.toString();
    return encoded ? `${path}?${encoded}` : path;
  }
}
