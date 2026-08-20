export type Outcome = "allow" | "allow_with_limits" | "redact_or_transform" | "require_approval" | "deny" | "quarantine_and_terminate";
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
    matched_rule: string;
    reason_codes: string[];
    approval_id: string | null;
    receipt: string;
    expires_at: string;
}
export interface FenceReceipt {
    request_id: string;
    tenant_id: string;
    allowed: boolean;
    final_outcome: string;
    degraded_tiers: string[];
    audit: JsonObject;
    stages: JsonObject;
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
export declare class AifenceError extends Error {
    readonly statusCode: number;
    readonly code: string;
    readonly details: JsonObject;
    constructor(statusCode: number, code: string, message: string, details?: JsonObject);
}
export interface ClientOptions {
    timeoutMs?: number;
    maxRetries?: number;
    maxResponseBytes?: number;
    fetch?: typeof globalThis.fetch;
}
export declare class AifenceClient {
    private readonly apiKey;
    private readonly baseUrl;
    private readonly timeoutMs;
    private readonly maxRetries;
    private readonly maxResponseBytes;
    private readonly fetchImpl;
    constructor(baseUrl: string, apiKey: string, options?: ClientOptions);
    createApiKey(request: JsonObject): Promise<JsonObject>;
    listApiKeys(): Promise<JsonObject[]>;
    revokeApiKey(keyId: string, reason: string): Promise<JsonObject>;
    registerAgent(registration: JsonObject): Promise<JsonObject>;
    getAgent(agentId: string): Promise<JsonObject>;
    revokeAgent(agentId: string, reason: string): Promise<JsonObject>;
    decide(request: JsonObject, idempotencyKey?: `${string}-${string}-${string}-${string}-${string}`): Promise<DecisionResponse>;
    getDecision(decisionId: string): Promise<DecisionResponse>;
    submitFence(request: JsonObject, requestId?: string): Promise<FenceReceipt>;
    ingestEvent(event: JsonObject): Promise<JsonObject>;
    getTrace(traceId: string): Promise<JsonObject[]>;
    listPolicies(): Promise<JsonObject[]>;
    publishPolicy(request: JsonObject): Promise<JsonObject>;
    activatePolicy(policyId: string, reason: string): Promise<JsonObject>;
    listApprovals(status?: string): Promise<JsonObject[]>;
    getApproval(approvalId: string): Promise<JsonObject>;
    decideApproval(approvalId: string, decision: "approved" | "rejected", reason: string): Promise<JsonObject>;
    issueCapability(request: CapabilityIssueRequest): Promise<JsonObject>;
    consumeCapability(request: CapabilityConsumeRequest): Promise<JsonObject>;
    revokeCapability(capabilityId: string, reason: string): Promise<JsonObject>;
    scanArtifact(upload: ArtifactUpload): Promise<JsonObject>;
    getArtifact(artifactId: string): Promise<JsonObject>;
    downloadArtifact(artifactId: string): Promise<BinaryResponse>;
    listIncidents(status?: string): Promise<JsonObject[]>;
    createIncident(request: JsonObject): Promise<JsonObject>;
    getIncident(incidentId: string): Promise<JsonObject>;
    updateIncident(incidentId: string, status: string, reason: string): Promise<JsonObject>;
    listProviders(): Promise<JsonObject[]>;
    registerProvider(request: JsonObject): Promise<JsonObject>;
    revokeProvider(providerId: string, reason: string): Promise<JsonObject>;
    invokeProvider(providerId: string, request: JsonObject, idempotencyKey?: `${string}-${string}-${string}-${string}-${string}`): Promise<JsonObject>;
    listTools(): Promise<JsonObject[]>;
    registerTool(request: JsonObject): Promise<JsonObject>;
    revokeTool(toolId: string, reason: string): Promise<JsonObject>;
    executeTool(toolId: string, request: JsonObject, idempotencyKey?: `${string}-${string}-${string}-${string}-${string}`): Promise<JsonObject>;
    verifyAudit(): Promise<JsonObject>;
    listAuditCheckpoints(limit?: number): Promise<JsonObject[]>;
    getExecution(executionId: string): Promise<JsonObject>;
    reconcileExecution(executionId: string, request: JsonObject): Promise<JsonObject>;
    recoverStaleExecutions(limit?: number): Promise<JsonObject>;
    createWorkloadIdentity(request: JsonObject): Promise<JsonObject>;
    listWorkloadIdentities(): Promise<JsonObject[]>;
    revokeWorkloadIdentity(bindingId: string, reason: string): Promise<JsonObject>;
    validatePolicy(document: JsonObject): Promise<JsonObject>;
    simulatePolicy(document: JsonObject, cases: JsonObject[]): Promise<JsonObject>;
    diffPolicy(currentDocument: JsonObject, proposedDocument: JsonObject, cases?: JsonObject[]): Promise<JsonObject>;
    replayPolicy(policyId: string, limit?: number): Promise<JsonObject>;
    canaryPolicy(policyId: string, percentage: number, reason: string): Promise<JsonObject>;
    shadowPolicy(policyId: string, reason: string): Promise<JsonObject>;
    rollbackPolicy(policyId: string, reason: string): Promise<JsonObject>;
    anchorAudit(destination?: "file" | "webhook"): Promise<JsonObject>;
    verifyAuditAnchor(anchorId: string): Promise<JsonObject>;
    anchorAuditBatch(destinations: string[], requiredQuorum?: number): Promise<JsonObject>;
    auditAnchorQuorum(sequence?: number, requiredQuorum?: number): Promise<JsonObject>;
    writeMemory(request: JsonObject): Promise<JsonObject>;
    readMemory(memoryId: string, includeContent?: boolean): Promise<JsonObject>;
    updateMemoryStatus(memoryId: string, status: string, reason: string): Promise<JsonObject>;
    createDelegation(request: JsonObject): Promise<JsonObject>;
    revokeDelegation(grantId: string, reason: string): Promise<JsonObject>;
    createBudget(request: JsonObject): Promise<JsonObject>;
    reserveBudget(budgetId: string, request: JsonObject): Promise<JsonObject>;
    settleBudget(reservationId: string, request: JsonObject): Promise<JsonObject>;
    requestTenantLifecycle(request: JsonObject): Promise<JsonObject>;
    getTenantLifecycle(jobId: string): Promise<JsonObject>;
    downloadTenantExport(jobId: string): Promise<BinaryResponse>;
    reconcileTenantLifecycle(jobId: string, resolution: "confirmed_destroyed" | "confirmed_not_destroyed", reason: string, destructionReceipt?: JsonObject): Promise<JsonObject>;
    createLegalHold(request: JsonObject): Promise<JsonObject>;
    listLegalHolds(): Promise<JsonObject[]>;
    releaseLegalHold(holdId: string, reason: string): Promise<JsonObject>;
    registerProtocol(request: JsonObject): Promise<JsonObject>;
    listProtocolManifestVersions(registrationId: string): Promise<JsonObject[]>;
    authorizeA2A(registrationId: string, request: JsonObject): Promise<JsonObject>;
    callMCPTool(registrationId: string, request: JsonObject): Promise<JsonObject>;
    runDispatcher(limit?: number): Promise<JsonObject>;
    private requestJson;
    private requestRaw;
    private readBounded;
    private retryDelay;
    private sleep;
    private segment;
    private withQuery;
}
