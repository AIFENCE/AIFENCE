export class AifenceError extends Error {
    statusCode;
    code;
    details;
    constructor(statusCode, code, message, details = {}) {
        super(`${code}: ${message}`);
        this.statusCode = statusCode;
        this.code = code;
        this.details = details;
        this.name = "AifenceError";
    }
}
const RETRYABLE_STATUS_CODES = new Set([429, 502, 503, 504]);
export class AifenceClient {
    apiKey;
    baseUrl;
    timeoutMs;
    maxRetries;
    maxResponseBytes;
    fetchImpl;
    constructor(baseUrl, apiKey, options = {}) {
        this.apiKey = apiKey;
        if (!baseUrl.startsWith("https://"))
            throw new Error("AIFENCE base URL must use HTTPS");
        if (!apiKey)
            throw new Error("AIFENCE API key is required");
        if ((options.maxRetries ?? 3) < 0)
            throw new Error("maxRetries cannot be negative");
        if ((options.maxResponseBytes ?? 16 * 1024 * 1024) < 1) {
            throw new Error("maxResponseBytes must be positive");
        }
        this.baseUrl = baseUrl.replace(/\/$/, "");
        this.timeoutMs = options.timeoutMs ?? 30_000;
        this.maxRetries = options.maxRetries ?? 3;
        this.maxResponseBytes = options.maxResponseBytes ?? 16 * 1024 * 1024;
        this.fetchImpl = options.fetch ?? globalThis.fetch;
    }
    createApiKey(request) {
        return this.requestJson("POST", "/v1/api-keys", request);
    }
    listApiKeys() {
        return this.requestJson("GET", "/v1/api-keys", undefined, true);
    }
    revokeApiKey(keyId, reason) {
        return this.requestJson("POST", `/v1/api-keys/${this.segment(keyId)}/revoke`, { reason });
    }
    registerAgent(registration) {
        return this.requestJson("POST", "/v1/agents/register", registration);
    }
    getAgent(agentId) {
        return this.requestJson("GET", `/v1/agents/${this.segment(agentId)}`, undefined, true);
    }
    revokeAgent(agentId, reason) {
        return this.requestJson("POST", `/v1/agents/${this.segment(agentId)}/revoke`, { reason });
    }
    decide(request, idempotencyKey = crypto.randomUUID()) {
        return this.requestJson("POST", "/v1/decisions", { ...request, idempotency_key: request.idempotency_key ?? idempotencyKey }, true);
    }
    getDecision(decisionId) {
        return this.requestJson("GET", `/v1/decisions/${this.segment(decisionId)}`, undefined, true);
    }
    submitFence(request, requestId) {
        const headers = requestId ? { "X-Request-ID": requestId } : undefined;
        return this.requestJson("POST", "/v1/fence/submit", request, false, headers);
    }
    ingestEvent(event) {
        return this.requestJson("POST", "/v1/events", event);
    }
    getTrace(traceId) {
        return this.requestJson("GET", `/v1/traces/${this.segment(traceId)}`, undefined, true);
    }
    listPolicies() {
        return this.requestJson("GET", "/v1/policies", undefined, true);
    }
    publishPolicy(request) {
        return this.requestJson("POST", "/v1/policies", { ...request, activate: false });
    }
    activatePolicy(policyId, reason) {
        return this.requestJson("POST", `/v1/policies/${this.segment(policyId)}/activate`, { reason });
    }
    listApprovals(status) {
        return this.requestJson("GET", this.withQuery("/v1/approvals", { status }), undefined, true);
    }
    getApproval(approvalId) {
        return this.requestJson("GET", `/v1/approvals/${this.segment(approvalId)}`, undefined, true);
    }
    decideApproval(approvalId, decision, reason) {
        return this.requestJson("POST", `/v1/approvals/${this.segment(approvalId)}/decision`, { decision, reason });
    }
    issueCapability(request) {
        return this.requestJson("POST", "/v1/capabilities", request);
    }
    consumeCapability(request) {
        return this.requestJson("POST", "/v1/capabilities/consume", request);
    }
    revokeCapability(capabilityId, reason) {
        return this.requestJson("POST", `/v1/capabilities/${this.segment(capabilityId)}/revoke`, { reason });
    }
    async scanArtifact(upload) {
        const form = new FormData();
        form.set("trace_id", upload.traceId);
        form.set("artifact", upload.content, upload.filename);
        return this.requestJson("POST", "/v1/artifacts/scan", form, false, {
            Accept: "application/json",
            "X-Aifence-SDK": "typescript/1.0.0-rc.5",
        });
    }
    getArtifact(artifactId) {
        return this.requestJson("GET", `/v1/artifacts/${this.segment(artifactId)}`, undefined, true);
    }
    async downloadArtifact(artifactId) {
        const { response, content } = await this.requestRaw("GET", `/v1/artifacts/${this.segment(artifactId)}/content`, undefined, true);
        return {
            content,
            contentType: response.headers.get("content-type"),
            contentDisposition: response.headers.get("content-disposition"),
        };
    }
    listIncidents(status) {
        return this.requestJson("GET", this.withQuery("/v1/incidents", { status }), undefined, true);
    }
    createIncident(request) {
        return this.requestJson("POST", "/v1/incidents", request);
    }
    getIncident(incidentId) {
        return this.requestJson("GET", `/v1/incidents/${this.segment(incidentId)}`, undefined, true);
    }
    updateIncident(incidentId, status, reason) {
        return this.requestJson("POST", `/v1/incidents/${this.segment(incidentId)}/status`, { status, reason });
    }
    listProviders() {
        return this.requestJson("GET", "/v1/providers", undefined, true);
    }
    registerProvider(request) {
        return this.requestJson("POST", "/v1/providers", request);
    }
    revokeProvider(providerId, reason) {
        return this.requestJson("POST", `/v1/providers/${this.segment(providerId)}/revoke`, { reason });
    }
    invokeProvider(providerId, request, idempotencyKey = crypto.randomUUID()) {
        return this.requestJson("POST", `/v1/providers/${this.segment(providerId)}/invoke`, { ...request, idempotency_key: request.idempotency_key ?? idempotencyKey }, true);
    }
    listTools() {
        return this.requestJson("GET", "/v1/tools", undefined, true);
    }
    registerTool(request) {
        return this.requestJson("POST", "/v1/tools", request);
    }
    revokeTool(toolId, reason) {
        return this.requestJson("POST", `/v1/tools/${this.segment(toolId)}/revoke`, { reason });
    }
    executeTool(toolId, request, idempotencyKey = crypto.randomUUID()) {
        return this.requestJson("POST", `/v1/tools/${this.segment(toolId)}/execute`, { ...request, idempotency_key: request.idempotency_key ?? idempotencyKey }, true);
    }
    verifyAudit() {
        return this.requestJson("GET", "/v1/audit/verify", undefined, true);
    }
    listAuditCheckpoints(limit = 100) {
        return this.requestJson("GET", this.withQuery("/v1/audit/checkpoints", { limit: String(limit) }), undefined, true);
    }
    getExecution(executionId) {
        return this.requestJson("GET", `/v1/executions/${this.segment(executionId)}`, undefined, true);
    }
    reconcileExecution(executionId, request) {
        return this.requestJson("POST", `/v1/executions/${this.segment(executionId)}/reconcile`, request);
    }
    recoverStaleExecutions(limit = 100) {
        return this.requestJson("POST", this.withQuery("/v1/executions/recover-stale", { limit: String(limit) }));
    }
    createWorkloadIdentity(request) {
        return this.requestJson("POST", "/v1/workload-identities", request);
    }
    listWorkloadIdentities() {
        return this.requestJson("GET", "/v1/workload-identities", undefined, true);
    }
    revokeWorkloadIdentity(bindingId, reason) {
        return this.requestJson("POST", `/v1/workload-identities/${this.segment(bindingId)}/revoke`, { reason });
    }
    validatePolicy(document) {
        return this.requestJson("POST", "/v1/policies/validate", { document });
    }
    simulatePolicy(document, cases) {
        return this.requestJson("POST", "/v1/policies/simulate", { document, cases });
    }
    diffPolicy(currentDocument, proposedDocument, cases = []) {
        return this.requestJson("POST", "/v1/policies/diff", {
            current_document: currentDocument,
            proposed_document: proposedDocument,
            cases,
        });
    }
    replayPolicy(policyId, limit = 100) {
        return this.requestJson("POST", this.withQuery(`/v1/policies/${this.segment(policyId)}/replay`, { limit: String(limit) }));
    }
    canaryPolicy(policyId, percentage, reason) {
        return this.requestJson("POST", `/v1/policies/${this.segment(policyId)}/canary`, { percentage, reason });
    }
    shadowPolicy(policyId, reason) {
        return this.requestJson("POST", `/v1/policies/${this.segment(policyId)}/shadow`, { reason });
    }
    rollbackPolicy(policyId, reason) {
        return this.requestJson("POST", `/v1/policies/${this.segment(policyId)}/rollback`, { reason });
    }
    anchorAudit(destination = "file") {
        return this.requestJson("POST", "/v1/audit/anchors", { destination });
    }
    verifyAuditAnchor(anchorId) {
        return this.requestJson("POST", `/v1/audit/anchors/${this.segment(anchorId)}/verify`);
    }
    anchorAuditBatch(destinations, requiredQuorum = 1) {
        return this.requestJson("POST", "/v1/audit/anchors/batch", {
            destinations,
            required_quorum: requiredQuorum,
        });
    }
    auditAnchorQuorum(sequence, requiredQuorum) {
        const query = {};
        if (sequence !== undefined)
            query.sequence = String(sequence);
        if (requiredQuorum !== undefined)
            query.required_quorum = String(requiredQuorum);
        return this.requestJson("GET", this.withQuery("/v1/audit/anchors/quorum", query), undefined, true);
    }
    writeMemory(request) {
        return this.requestJson("POST", "/v1/memory", request);
    }
    readMemory(memoryId, includeContent = false) {
        return this.requestJson("GET", this.withQuery(`/v1/memory/${this.segment(memoryId)}`, { include_content: String(includeContent) }), undefined, true);
    }
    updateMemoryStatus(memoryId, status, reason) {
        return this.requestJson("POST", `/v1/memory/${this.segment(memoryId)}/status`, { status, reason });
    }
    createDelegation(request) {
        return this.requestJson("POST", "/v1/delegations", request);
    }
    revokeDelegation(grantId, reason) {
        return this.requestJson("POST", `/v1/delegations/${this.segment(grantId)}/revoke`, { reason });
    }
    createBudget(request) {
        return this.requestJson("POST", "/v1/budgets", request);
    }
    reserveBudget(budgetId, request) {
        return this.requestJson("POST", `/v1/budgets/${this.segment(budgetId)}/reserve`, request);
    }
    settleBudget(reservationId, request) {
        return this.requestJson("POST", `/v1/budget-reservations/${this.segment(reservationId)}/settle`, request);
    }
    requestTenantLifecycle(request) {
        return this.requestJson("POST", "/v1/tenant/lifecycle", request);
    }
    getTenantLifecycle(jobId) {
        return this.requestJson("GET", `/v1/tenant/lifecycle/${this.segment(jobId)}`, undefined, true);
    }
    async downloadTenantExport(jobId) {
        const { response, content } = await this.requestRaw("GET", `/v1/tenant/lifecycle/${this.segment(jobId)}/content`, undefined, true);
        return {
            content,
            contentType: response.headers.get("content-type"),
            contentDisposition: response.headers.get("content-disposition"),
        };
    }
    reconcileTenantLifecycle(jobId, resolution, reason, destructionReceipt = {}) {
        return this.requestJson("POST", `/v1/tenant/lifecycle/${this.segment(jobId)}/reconcile`, {
            resolution,
            reason,
            destruction_receipt: destructionReceipt,
        });
    }
    createLegalHold(request) {
        return this.requestJson("POST", "/v1/tenant/legal-holds", request);
    }
    listLegalHolds() {
        return this.requestJson("GET", "/v1/tenant/legal-holds", undefined, true);
    }
    releaseLegalHold(holdId, reason) {
        return this.requestJson("POST", `/v1/tenant/legal-holds/${this.segment(holdId)}/release`, { reason });
    }
    registerProtocol(request) {
        return this.requestJson("POST", "/v1/protocols", request);
    }
    listProtocolManifestVersions(registrationId) {
        return this.requestJson("GET", `/v1/protocols/${this.segment(registrationId)}/manifest-versions`, undefined, true);
    }
    authorizeA2A(registrationId, request) {
        return this.requestJson("POST", `/v1/protocols/a2a/${this.segment(registrationId)}/authorize`, request);
    }
    callMCPTool(registrationId, request) {
        return this.requestJson("POST", `/v1/protocols/mcp/${this.segment(registrationId)}/tools/call`, request);
    }
    runDispatcher(limit = 20) {
        return this.requestJson("POST", this.withQuery("/v1/dispatch/run", { limit: String(limit) }));
    }
    async requestJson(method, path, body, retryable = false, headers) {
        const { content } = await this.requestRaw(method, path, body, retryable, headers);
        if (content.byteLength === 0)
            return undefined;
        try {
            return JSON.parse(new TextDecoder().decode(content));
        }
        catch (error) {
            throw new Error(`AIFENCE returned invalid JSON: ${String(error)}`);
        }
    }
    async requestRaw(method, path, body, retryable = false, headers) {
        const attempts = retryable ? this.maxRetries + 1 : 1;
        let response;
        for (let attempt = 0; attempt < attempts; attempt += 1) {
            const controller = new AbortController();
            const timeout = setTimeout(() => controller.abort(), this.timeoutMs);
            try {
                const requestHeaders = {
                    Authorization: `Bearer ${this.apiKey}`,
                    Accept: "application/json",
                    "X-Aifence-SDK": "typescript/1.0.0-rc.5",
                    ...headers,
                };
                let encodedBody;
                if (body instanceof FormData) {
                    encodedBody = body;
                }
                else if (body !== undefined) {
                    requestHeaders["Content-Type"] = "application/json";
                    encodedBody = JSON.stringify(body);
                }
                const init = {
                    method,
                    headers: requestHeaders,
                    signal: controller.signal,
                    redirect: "error",
                };
                if (encodedBody !== undefined)
                    init.body = encodedBody;
                response = await this.fetchImpl(`${this.baseUrl}${path}`, init);
            }
            catch (error) {
                if (attempt + 1 >= attempts)
                    throw error;
                await this.sleep(this.retryDelay(undefined, attempt));
                continue;
            }
            finally {
                clearTimeout(timeout);
            }
            if (!RETRYABLE_STATUS_CODES.has(response.status) || attempt + 1 >= attempts)
                break;
            await this.sleep(this.retryDelay(response, attempt));
        }
        if (!response)
            throw new Error("AIFENCE request did not produce a response");
        const content = await this.readBounded(response);
        if (!response.ok) {
            let error = {};
            try {
                const payload = JSON.parse(new TextDecoder().decode(content));
                if (typeof payload.error === "object" && payload.error !== null) {
                    error = payload.error;
                }
            }
            catch {
                error = {};
            }
            throw new AifenceError(response.status, String(error.code ?? "http_error"), String(error.message ?? response.statusText), typeof error.details === "object" && error.details !== null
                ? error.details
                : {});
        }
        return { response, content };
    }
    async readBounded(response) {
        const declared = Number(response.headers.get("content-length"));
        if (Number.isFinite(declared) && declared > this.maxResponseBytes) {
            throw new Error("AIFENCE response exceeds maxResponseBytes");
        }
        if (!response.body)
            return new Uint8Array();
        const reader = response.body.getReader();
        const chunks = [];
        let total = 0;
        for (;;) {
            const { done, value } = await reader.read();
            if (done)
                break;
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
    retryDelay(response, attempt) {
        const retryAfter = response?.headers.get("retry-after");
        if (retryAfter !== null && retryAfter !== undefined) {
            const seconds = Number(retryAfter);
            if (Number.isFinite(seconds) && seconds > 0)
                return Math.min(seconds, 60) * 1000;
        }
        return Math.min(2 ** attempt, 8) * 1000;
    }
    sleep(milliseconds) {
        return new Promise((resolve) => setTimeout(resolve, milliseconds));
    }
    segment(value) {
        return encodeURIComponent(value);
    }
    withQuery(path, values) {
        const query = new URLSearchParams();
        for (const [key, value] of Object.entries(values)) {
            if (value !== undefined)
                query.set(key, value);
        }
        const encoded = query.toString();
        return encoded ? `${path}?${encoded}` : path;
    }
}
