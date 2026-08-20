// SPDX-FileCopyrightText: 2026 AIFENCE contributors
// SPDX-License-Identifier: Apache-2.0
package aifence

import (
	"bytes"
	"context"
	"crypto/rand"
	"crypto/tls"
	"encoding/base64"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"mime/multipart"
	"net/http"
	"net/textproto"
	"net/url"
	"strconv"
	"strings"
	"time"
)

const defaultMaxResponseBytes int64 = 16 << 20

type Error struct {
	StatusCode int
	Code       string
	Message    string
	Details    map[string]any
}

func (e *Error) Error() string { return e.Code + ": " + e.Message }

type Options struct {
	HTTPClient       *http.Client
	MaxRetries       int
	MaxResponseBytes int64
}

type Client struct {
	baseURL          *url.URL
	fenceURL         *url.URL
	apiKey           string
	httpClient       *http.Client
	maxRetries       int
	maxResponseBytes int64
}

func NewClient(baseURL, apiKey string, httpClient *http.Client) (*Client, error) {
	return NewClientWithOptions(baseURL, apiKey, Options{HTTPClient: httpClient, MaxRetries: 3})
}

func NewClientWithOptions(baseURL, apiKey string, options Options) (*Client, error) {
	u, err := url.Parse(strings.TrimRight(baseURL, "/"))
	if err != nil {
		return nil, err
	}
	if u.Scheme != "https" || u.Host == "" {
		return nil, errors.New("AIFENCE base URL must be an absolute HTTPS URL")
	}
	if apiKey == "" {
		return nil, errors.New("AIFENCE API key is required")
	}
	if options.MaxRetries < 0 {
		return nil, errors.New("MaxRetries cannot be negative")
	}
	if options.HTTPClient == nil {
		options.HTTPClient = &http.Client{
			Timeout: 30 * time.Second,
			Transport: &http.Transport{
				Proxy:                 http.ProxyFromEnvironment,
				TLSClientConfig:       &tls.Config{MinVersion: tls.VersionTLS12},
				MaxIdleConns:          100,
				MaxIdleConnsPerHost:   20,
				IdleConnTimeout:       90 * time.Second,
				TLSHandshakeTimeout:   10 * time.Second,
				ResponseHeaderTimeout: 30 * time.Second,
			},
			CheckRedirect: func(_ *http.Request, _ []*http.Request) error { return http.ErrUseLastResponse },
		}
	}
	if options.MaxResponseBytes == 0 {
		options.MaxResponseBytes = defaultMaxResponseBytes
	}
	if options.MaxResponseBytes < 1 {
		return nil, errors.New("MaxResponseBytes must be positive")
	}
	fenceURL := *u
	basePath := strings.TrimRight(fenceURL.Path, "/")
	if strings.HasSuffix(basePath, "/guard") {
		basePath = strings.TrimSuffix(basePath, "/guard")
	}
	fenceURL.Path = strings.TrimRight(basePath, "/") + "/v1/fence/submit"
	return &Client{
		baseURL:          u,
		fenceURL:         &fenceURL,
		apiKey:           apiKey,
		httpClient:       options.HTTPClient,
		maxRetries:       options.MaxRetries,
		maxResponseBytes: options.MaxResponseBytes,
	}, nil
}

func (c *Client) CreateAPIKey(ctx context.Context, request any, out any) error {
	return c.doJSON(ctx, http.MethodPost, "/v1/api-keys", request, out, false)
}

func (c *Client) ListAPIKeys(ctx context.Context, out any) error {
	return c.doJSON(ctx, http.MethodGet, "/v1/api-keys", nil, out, true)
}

func (c *Client) RevokeAPIKey(ctx context.Context, keyID, reason string, out any) error {
	return c.doJSON(ctx, http.MethodPost, "/v1/api-keys/"+url.PathEscape(keyID)+"/revoke", map[string]string{"reason": reason}, out, false)
}

func (c *Client) RegisterAgent(ctx context.Context, registration any, out any) error {
	return c.doJSON(ctx, http.MethodPost, "/v1/agents/register", registration, out, false)
}

func (c *Client) GetAgent(ctx context.Context, agentID string, out any) error {
	return c.doJSON(ctx, http.MethodGet, "/v1/agents/"+url.PathEscape(agentID), nil, out, true)
}

func (c *Client) RevokeAgent(ctx context.Context, agentID, reason string, out any) error {
	return c.doJSON(ctx, http.MethodPost, "/v1/agents/"+url.PathEscape(agentID)+"/revoke", map[string]string{"reason": reason}, out, false)
}

func (c *Client) Decide(ctx context.Context, request any, out any) error {
	encoded, err := json.Marshal(request)
	if err != nil {
		return err
	}
	var body map[string]any
	if err := json.Unmarshal(encoded, &body); err != nil {
		return errors.New("decision request must encode as a JSON object")
	}
	if value, ok := body["idempotency_key"].(string); !ok || value == "" {
		idempotencyKey, err := randomID()
		if err != nil {
			return err
		}
		body["idempotency_key"] = idempotencyKey
	}
	return c.doJSON(ctx, http.MethodPost, "/v1/decisions", body, out, true)
}

func (c *Client) GetDecision(ctx context.Context, decisionID string, out any) error {
	return c.doJSON(ctx, http.MethodGet, "/v1/decisions/"+url.PathEscape(decisionID), nil, out, true)
}

// SubmitFence runs the composed Quality -> Guard -> Bus enforcement path.
func (c *Client) SubmitFence(ctx context.Context, request any, out any) error {
	return c.doJSON(ctx, http.MethodPost, c.fenceURL.String(), request, out, false)
}

func (c *Client) IngestEvent(ctx context.Context, event any, out any) error {
	return c.doJSON(ctx, http.MethodPost, "/v1/events", event, out, false)
}

func (c *Client) GetTrace(ctx context.Context, traceID string, out any) error {
	return c.doJSON(ctx, http.MethodGet, "/v1/traces/"+url.PathEscape(traceID), nil, out, true)
}

func (c *Client) ListPolicies(ctx context.Context, out any) error {
	return c.doJSON(ctx, http.MethodGet, "/v1/policies", nil, out, true)
}

func (c *Client) PublishPolicy(ctx context.Context, request any, out any) error {
	encoded, err := json.Marshal(request)
	if err != nil {
		return err
	}
	var body map[string]any
	if err := json.Unmarshal(encoded, &body); err != nil {
		return errors.New("policy request must encode as a JSON object")
	}
	body["activate"] = false
	return c.doJSON(ctx, http.MethodPost, "/v1/policies", body, out, false)
}

func (c *Client) ActivatePolicy(ctx context.Context, policyID, reason string, out any) error {
	return c.doJSON(ctx, http.MethodPost, "/v1/policies/"+url.PathEscape(policyID)+"/activate", map[string]string{"reason": reason}, out, false)
}

func (c *Client) ListApprovals(ctx context.Context, status string, out any) error {
	return c.doJSON(ctx, http.MethodGet, pathWithStatus("/v1/approvals", status), nil, out, true)
}

func (c *Client) GetApproval(ctx context.Context, approvalID string, out any) error {
	return c.doJSON(ctx, http.MethodGet, "/v1/approvals/"+url.PathEscape(approvalID), nil, out, true)
}

func (c *Client) DecideApproval(ctx context.Context, approvalID, decision, reason string, out any) error {
	body := map[string]string{"decision": decision, "reason": reason}
	return c.doJSON(ctx, http.MethodPost, "/v1/approvals/"+url.PathEscape(approvalID)+"/decision", body, out, false)
}

func (c *Client) IssueCapability(ctx context.Context, request any, out any) error {
	return c.doJSON(ctx, http.MethodPost, "/v1/capabilities", request, out, false)
}

func (c *Client) ConsumeCapability(ctx context.Context, request any, out any) error {
	return c.doJSON(ctx, http.MethodPost, "/v1/capabilities/consume", request, out, false)
}

func (c *Client) RevokeCapability(ctx context.Context, capabilityID, reason string, out any) error {
	return c.doJSON(ctx, http.MethodPost, "/v1/capabilities/"+url.PathEscape(capabilityID)+"/revoke", map[string]string{"reason": reason}, out, false)
}

func (c *Client) ScanArtifact(ctx context.Context, traceID, filename, mediaType string, content io.Reader, out any) error {
	var body bytes.Buffer
	writer := multipart.NewWriter(&body)
	if err := writer.WriteField("trace_id", traceID); err != nil {
		return err
	}
	header := make(textproto.MIMEHeader)
	header.Set("Content-Disposition", fmt.Sprintf(`form-data; name="artifact"; filename="%s"`, escapeMultipartFilename(filename)))
	header.Set("Content-Type", mediaType)
	part, err := writer.CreatePart(header)
	if err != nil {
		return err
	}
	if _, err := io.Copy(part, content); err != nil {
		return err
	}
	if err := writer.Close(); err != nil {
		return err
	}
	return c.do(ctx, http.MethodPost, "/v1/artifacts/scan", body.Bytes(), writer.FormDataContentType(), out, false)
}

func (c *Client) GetArtifact(ctx context.Context, artifactID string, out any) error {
	return c.doJSON(ctx, http.MethodGet, "/v1/artifacts/"+url.PathEscape(artifactID), nil, out, true)
}

func (c *Client) DownloadArtifact(ctx context.Context, artifactID string) ([]byte, http.Header, error) {
	response, data, err := c.perform(ctx, http.MethodGet, "/v1/artifacts/"+url.PathEscape(artifactID)+"/content", nil, "", true)
	if err != nil {
		return nil, nil, err
	}
	return data, response.Header.Clone(), nil
}

func (c *Client) ListIncidents(ctx context.Context, status string, out any) error {
	return c.doJSON(ctx, http.MethodGet, pathWithStatus("/v1/incidents", status), nil, out, true)
}

func (c *Client) CreateIncident(ctx context.Context, request any, out any) error {
	return c.doJSON(ctx, http.MethodPost, "/v1/incidents", request, out, false)
}

func (c *Client) GetIncident(ctx context.Context, incidentID string, out any) error {
	return c.doJSON(ctx, http.MethodGet, "/v1/incidents/"+url.PathEscape(incidentID), nil, out, true)
}

func (c *Client) UpdateIncident(ctx context.Context, incidentID, status, reason string, out any) error {
	body := map[string]string{"status": status, "reason": reason}
	return c.doJSON(ctx, http.MethodPost, "/v1/incidents/"+url.PathEscape(incidentID)+"/status", body, out, false)
}

func (c *Client) ListProviders(ctx context.Context, out any) error {
	return c.doJSON(ctx, http.MethodGet, "/v1/providers", nil, out, true)
}

func (c *Client) RegisterProvider(ctx context.Context, request any, out any) error {
	return c.doJSON(ctx, http.MethodPost, "/v1/providers", request, out, false)
}

func (c *Client) RevokeProvider(ctx context.Context, providerID, reason string, out any) error {
	return c.doJSON(ctx, http.MethodPost, "/v1/providers/"+url.PathEscape(providerID)+"/revoke", map[string]string{"reason": reason}, out, false)
}

func (c *Client) InvokeProvider(ctx context.Context, providerID string, request any, out any) error {
	body, err := withIdempotencyKey(request)
	if err != nil {
		return err
	}
	return c.doJSON(ctx, http.MethodPost, "/v1/providers/"+url.PathEscape(providerID)+"/invoke", body, out, true)
}

func (c *Client) ListTools(ctx context.Context, out any) error {
	return c.doJSON(ctx, http.MethodGet, "/v1/tools", nil, out, true)
}

func (c *Client) RegisterTool(ctx context.Context, request any, out any) error {
	return c.doJSON(ctx, http.MethodPost, "/v1/tools", request, out, false)
}

func (c *Client) RevokeTool(ctx context.Context, toolID, reason string, out any) error {
	return c.doJSON(ctx, http.MethodPost, "/v1/tools/"+url.PathEscape(toolID)+"/revoke", map[string]string{"reason": reason}, out, false)
}

func (c *Client) ExecuteTool(ctx context.Context, toolID string, request any, out any) error {
	body, err := withIdempotencyKey(request)
	if err != nil {
		return err
	}
	return c.doJSON(ctx, http.MethodPost, "/v1/tools/"+url.PathEscape(toolID)+"/execute", body, out, true)
}

func (c *Client) VerifyAudit(ctx context.Context, out any) error {
	return c.doJSON(ctx, http.MethodGet, "/v1/audit/verify", nil, out, true)
}

func (c *Client) ListAuditCheckpoints(ctx context.Context, limit int, out any) error {
	values := url.Values{}
	values.Set("limit", strconv.Itoa(limit))
	return c.doJSON(ctx, http.MethodGet, "/v1/audit/checkpoints?"+values.Encode(), nil, out, true)
}

func (c *Client) GetExecution(ctx context.Context, executionID string, out any) error {
	return c.doJSON(ctx, http.MethodGet, "/v1/executions/"+url.PathEscape(executionID), nil, out, true)
}

func (c *Client) ReconcileExecution(ctx context.Context, executionID string, request any, out any) error {
	return c.doJSON(ctx, http.MethodPost, "/v1/executions/"+url.PathEscape(executionID)+"/reconcile", request, out, false)
}

func (c *Client) RecoverStaleExecutions(ctx context.Context, limit int, out any) error {
	values := url.Values{}
	values.Set("limit", strconv.Itoa(limit))
	return c.doJSON(ctx, http.MethodPost, "/v1/executions/recover-stale?"+values.Encode(), nil, out, false)
}

func (c *Client) CreateWorkloadIdentity(ctx context.Context, request any, out any) error {
	return c.doJSON(ctx, http.MethodPost, "/v1/workload-identities", request, out, false)
}

func (c *Client) ListWorkloadIdentities(ctx context.Context, out any) error {
	return c.doJSON(ctx, http.MethodGet, "/v1/workload-identities", nil, out, true)
}

func (c *Client) RevokeWorkloadIdentity(ctx context.Context, bindingID, reason string, out any) error {
	return c.doJSON(ctx, http.MethodPost, "/v1/workload-identities/"+url.PathEscape(bindingID)+"/revoke", map[string]string{"reason": reason}, out, false)
}

func (c *Client) ValidatePolicy(ctx context.Context, document any, out any) error {
	return c.doJSON(ctx, http.MethodPost, "/v1/policies/validate", map[string]any{"document": document}, out, false)
}

func (c *Client) SimulatePolicy(ctx context.Context, document, cases any, out any) error {
	return c.doJSON(ctx, http.MethodPost, "/v1/policies/simulate", map[string]any{"document": document, "cases": cases}, out, false)
}

func (c *Client) DiffPolicy(ctx context.Context, current, proposed, cases any, out any) error {
	return c.doJSON(ctx, http.MethodPost, "/v1/policies/diff", map[string]any{"current_document": current, "proposed_document": proposed, "cases": cases}, out, false)
}

func (c *Client) ReplayPolicy(ctx context.Context, policyID string, limit int, out any) error {
	values := url.Values{}
	values.Set("limit", strconv.Itoa(limit))
	return c.doJSON(ctx, http.MethodPost, "/v1/policies/"+url.PathEscape(policyID)+"/replay?"+values.Encode(), nil, out, false)
}

func (c *Client) CanaryPolicy(ctx context.Context, policyID string, percentage int, reason string, out any) error {
	return c.doJSON(ctx, http.MethodPost, "/v1/policies/"+url.PathEscape(policyID)+"/canary", map[string]any{"percentage": percentage, "reason": reason}, out, false)
}

func (c *Client) ShadowPolicy(ctx context.Context, policyID, reason string, out any) error {
	return c.doJSON(ctx, http.MethodPost, "/v1/policies/"+url.PathEscape(policyID)+"/shadow", map[string]string{"reason": reason}, out, false)
}

func (c *Client) RollbackPolicy(ctx context.Context, policyID, reason string, out any) error {
	return c.doJSON(ctx, http.MethodPost, "/v1/policies/"+url.PathEscape(policyID)+"/rollback", map[string]string{"reason": reason}, out, false)
}

func (c *Client) AnchorAudit(ctx context.Context, destination string, out any) error {
	return c.doJSON(ctx, http.MethodPost, "/v1/audit/anchors", map[string]string{"destination": destination}, out, false)
}

func (c *Client) VerifyAuditAnchor(ctx context.Context, anchorID string, out any) error {
	return c.doJSON(ctx, http.MethodPost, "/v1/audit/anchors/"+url.PathEscape(anchorID)+"/verify", nil, out, false)
}

func (c *Client) AnchorAuditBatch(ctx context.Context, destinations []string, requiredQuorum int, out any) error {
	return c.doJSON(ctx, http.MethodPost, "/v1/audit/anchors/batch", map[string]any{
		"destinations": destinations, "required_quorum": requiredQuorum,
	}, out, false)
}

func (c *Client) AuditAnchorQuorum(ctx context.Context, sequence *int, requiredQuorum *int, out any) error {
	values := url.Values{}
	if sequence != nil {
		values.Set("sequence", strconv.Itoa(*sequence))
	}
	if requiredQuorum != nil {
		values.Set("required_quorum", strconv.Itoa(*requiredQuorum))
	}
	path := "/v1/audit/anchors/quorum"
	if encoded := values.Encode(); encoded != "" {
		path += "?" + encoded
	}
	return c.doJSON(ctx, http.MethodGet, path, nil, out, true)
}

func (c *Client) WriteMemory(ctx context.Context, request any, out any) error {
	return c.doJSON(ctx, http.MethodPost, "/v1/memory", request, out, false)
}

func (c *Client) ReadMemory(ctx context.Context, memoryID string, includeContent bool, out any) error {
	values := url.Values{}
	values.Set("include_content", strconv.FormatBool(includeContent))
	return c.doJSON(ctx, http.MethodGet, "/v1/memory/"+url.PathEscape(memoryID)+"?"+values.Encode(), nil, out, true)
}

func (c *Client) UpdateMemoryStatus(ctx context.Context, memoryID, status, reason string, out any) error {
	return c.doJSON(ctx, http.MethodPost, "/v1/memory/"+url.PathEscape(memoryID)+"/status", map[string]string{"status": status, "reason": reason}, out, false)
}

func (c *Client) CreateDelegation(ctx context.Context, request any, out any) error {
	return c.doJSON(ctx, http.MethodPost, "/v1/delegations", request, out, false)
}

func (c *Client) RevokeDelegation(ctx context.Context, grantID, reason string, out any) error {
	return c.doJSON(ctx, http.MethodPost, "/v1/delegations/"+url.PathEscape(grantID)+"/revoke", map[string]string{"reason": reason}, out, false)
}

func (c *Client) CreateBudget(ctx context.Context, request any, out any) error {
	return c.doJSON(ctx, http.MethodPost, "/v1/budgets", request, out, false)
}

func (c *Client) ReserveBudget(ctx context.Context, budgetID string, request any, out any) error {
	return c.doJSON(ctx, http.MethodPost, "/v1/budgets/"+url.PathEscape(budgetID)+"/reserve", request, out, false)
}

func (c *Client) SettleBudget(ctx context.Context, reservationID string, request any, out any) error {
	return c.doJSON(ctx, http.MethodPost, "/v1/budget-reservations/"+url.PathEscape(reservationID)+"/settle", request, out, false)
}

func (c *Client) RequestTenantLifecycle(ctx context.Context, request any, out any) error {
	return c.doJSON(ctx, http.MethodPost, "/v1/tenant/lifecycle", request, out, false)
}

func (c *Client) GetTenantLifecycle(ctx context.Context, jobID string, out any) error {
	return c.doJSON(ctx, http.MethodGet, "/v1/tenant/lifecycle/"+url.PathEscape(jobID), nil, out, true)
}

func (c *Client) DownloadTenantExport(ctx context.Context, jobID string) ([]byte, string, error) {
	response, data, err := c.perform(ctx, http.MethodGet, "/v1/tenant/lifecycle/"+url.PathEscape(jobID)+"/content", nil, "", true)
	if err != nil {
		return nil, "", err
	}
	return data, response.Header.Get("Content-Type"), nil
}

func (c *Client) ReconcileTenantLifecycle(ctx context.Context, jobID, resolution, reason string, destructionReceipt any, out any) error {
	return c.doJSON(ctx, http.MethodPost, "/v1/tenant/lifecycle/"+url.PathEscape(jobID)+"/reconcile", map[string]any{
		"resolution": resolution, "reason": reason, "destruction_receipt": destructionReceipt,
	}, out, false)
}

func (c *Client) CreateLegalHold(ctx context.Context, request any, out any) error {
	return c.doJSON(ctx, http.MethodPost, "/v1/tenant/legal-holds", request, out, false)
}

func (c *Client) ListLegalHolds(ctx context.Context, out any) error {
	return c.doJSON(ctx, http.MethodGet, "/v1/tenant/legal-holds", nil, out, true)
}

func (c *Client) ReleaseLegalHold(ctx context.Context, holdID, reason string, out any) error {
	return c.doJSON(ctx, http.MethodPost, "/v1/tenant/legal-holds/"+url.PathEscape(holdID)+"/release", map[string]string{"reason": reason}, out, false)
}

func (c *Client) RegisterProtocol(ctx context.Context, request any, out any) error {
	return c.doJSON(ctx, http.MethodPost, "/v1/protocols", request, out, false)
}

func (c *Client) ListProtocolManifestVersions(ctx context.Context, registrationID string, out any) error {
	return c.doJSON(ctx, http.MethodGet, "/v1/protocols/"+url.PathEscape(registrationID)+"/manifest-versions", nil, out, true)
}

func (c *Client) AuthorizeA2A(ctx context.Context, registrationID string, request any, out any) error {
	return c.doJSON(ctx, http.MethodPost, "/v1/protocols/a2a/"+url.PathEscape(registrationID)+"/authorize", request, out, false)
}

func (c *Client) CallMCPTool(ctx context.Context, registrationID string, request any, out any) error {
	return c.doJSON(ctx, http.MethodPost, "/v1/protocols/mcp/"+url.PathEscape(registrationID)+"/tools/call", request, out, true)
}

func (c *Client) RunDispatcher(ctx context.Context, limit int, out any) error {
	values := url.Values{}
	values.Set("limit", strconv.Itoa(limit))
	return c.doJSON(ctx, http.MethodPost, "/v1/dispatch/run?"+values.Encode(), nil, out, false)
}

func (c *Client) doJSON(ctx context.Context, method, path string, body, out any, retryable bool) error {
	var encoded []byte
	var err error
	if body != nil {
		encoded, err = json.Marshal(body)
		if err != nil {
			return err
		}
	}
	return c.do(ctx, method, path, encoded, "application/json", out, retryable)
}

func (c *Client) do(ctx context.Context, method, path string, body []byte, contentType string, out any, retryable bool) error {
	_, data, err := c.perform(ctx, method, path, body, contentType, retryable)
	if err != nil {
		return err
	}
	if out == nil || len(data) == 0 {
		return nil
	}
	if err := json.Unmarshal(data, out); err != nil {
		return fmt.Errorf("decode AIFENCE response: %w", err)
	}
	return nil
}

func (c *Client) perform(ctx context.Context, method, path string, body []byte, contentType string, retryable bool) (*http.Response, []byte, error) {
	attempts := 1
	if retryable {
		attempts = c.maxRetries + 1
	}
	var response *http.Response
	var err error
	for attempt := 0; attempt < attempts; attempt++ {
		var target *url.URL
		if strings.HasPrefix(path, "https://") {
			parsed, parseErr := url.Parse(path)
			if parseErr != nil {
				return nil, nil, parseErr
			}
			target = parsed
		} else {
			resolved := *c.baseURL
			resolved.Path = strings.TrimRight(resolved.Path, "/") + path
			target = &resolved
		}
		req, requestErr := http.NewRequestWithContext(ctx, method, target.String(), bytes.NewReader(body))
		if requestErr != nil {
			return nil, nil, requestErr
		}
		req.Header.Set("Authorization", "Bearer "+c.apiKey)
		req.Header.Set("Accept", "application/json")
		req.Header.Set("User-Agent", "aifence-go/1.0.0-rc.5")
		if len(body) > 0 && contentType != "" {
			req.Header.Set("Content-Type", contentType)
		}
		response, err = c.httpClient.Do(req)
		if err != nil {
			if attempt+1 >= attempts {
				return nil, nil, err
			}
			if err := sleepContext(ctx, backoff(attempt)); err != nil {
				return nil, nil, err
			}
			continue
		}
		if !retryableStatus(response.StatusCode) || attempt+1 >= attempts {
			break
		}
		_, _ = io.Copy(io.Discard, io.LimitReader(response.Body, c.maxResponseBytes+1))
		_ = response.Body.Close()
		if err := sleepContext(ctx, retryDelay(response, attempt)); err != nil {
			return nil, nil, err
		}
	}
	if response == nil {
		return nil, nil, errors.New("AIFENCE request produced no response")
	}
	defer response.Body.Close()
	data, err := io.ReadAll(io.LimitReader(response.Body, c.maxResponseBytes+1))
	if err != nil {
		return nil, nil, err
	}
	if int64(len(data)) > c.maxResponseBytes {
		return nil, nil, errors.New("AIFENCE response exceeds MaxResponseBytes")
	}
	if response.StatusCode < 200 || response.StatusCode >= 300 {
		var envelope struct {
			Error struct {
				Code    string         `json:"code"`
				Message string         `json:"message"`
				Details map[string]any `json:"details"`
			} `json:"error"`
		}
		_ = json.Unmarshal(data, &envelope)
		return response, nil, &Error{
			StatusCode: response.StatusCode,
			Code:       defaultString(envelope.Error.Code, "http_error"),
			Message:    defaultString(envelope.Error.Message, response.Status),
			Details:    envelope.Error.Details,
		}
	}
	return response, data, nil
}

func pathWithStatus(path, status string) string {
	if status == "" {
		return path
	}
	values := url.Values{}
	values.Set("status", status)
	return path + "?" + values.Encode()
}

func retryableStatus(status int) bool {
	return status == http.StatusTooManyRequests || status == http.StatusBadGateway || status == http.StatusServiceUnavailable || status == http.StatusGatewayTimeout
}

func retryDelay(response *http.Response, attempt int) time.Duration {
	if response != nil {
		if seconds, err := strconv.Atoi(response.Header.Get("Retry-After")); err == nil && seconds > 0 {
			if seconds > 60 {
				seconds = 60
			}
			return time.Duration(seconds) * time.Second
		}
	}
	return backoff(attempt)
}

func backoff(attempt int) time.Duration {
	seconds := 1 << attempt
	if seconds > 8 {
		seconds = 8
	}
	return time.Duration(seconds) * time.Second
}

func sleepContext(ctx context.Context, delay time.Duration) error {
	timer := time.NewTimer(delay)
	defer timer.Stop()
	select {
	case <-timer.C:
		return nil
	case <-ctx.Done():
		return ctx.Err()
	}
}

func withIdempotencyKey(request any) (map[string]any, error) {
	encoded, err := json.Marshal(request)
	if err != nil {
		return nil, err
	}
	var body map[string]any
	if err := json.Unmarshal(encoded, &body); err != nil {
		return nil, errors.New("broker request must encode as a JSON object")
	}
	if value, ok := body["idempotency_key"].(string); !ok || value == "" {
		idempotencyKey, err := randomID()
		if err != nil {
			return nil, err
		}
		body["idempotency_key"] = idempotencyKey
	}
	return body, nil
}

func randomID() (string, error) {
	buffer := make([]byte, 24)
	if _, err := rand.Read(buffer); err != nil {
		return "", fmt.Errorf("generate idempotency key: %w", err)
	}
	return "sdk_" + base64.RawURLEncoding.EncodeToString(buffer), nil
}

func escapeMultipartFilename(filename string) string {
	return strings.NewReplacer("\\", "_", `"`, "_", "\r", "_", "\n", "_").Replace(filename)
}

func defaultString(value, fallback string) string {
	if value == "" {
		return fallback
	}
	return value
}
