BEGIN TRANSACTION;
CREATE TABLE a2a_task_authorizations (
	id VARCHAR(64) NOT NULL, 
	tenant_id VARCHAR(64) NOT NULL, 
	registration_id VARCHAR(64) NOT NULL, 
	delegation_grant_id VARCHAR(64) NOT NULL, 
	trace_id VARCHAR(64) NOT NULL, 
	task_id VARCHAR(255) NOT NULL, 
	idempotency_key VARCHAR(128) NOT NULL, 
	request_hash VARCHAR(64) NOT NULL, 
	authorization_receipt TEXT NOT NULL, 
	execution_id VARCHAR(64), 
	status VARCHAR(32) NOT NULL, 
	created_at DATETIME NOT NULL, 
	revoked_at DATETIME, 
	PRIMARY KEY (id), 
	FOREIGN KEY(delegation_grant_id) REFERENCES delegation_grants (id) ON DELETE CASCADE, 
	FOREIGN KEY(registration_id) REFERENCES agent_protocol_registrations (id) ON DELETE CASCADE, 
	FOREIGN KEY(tenant_id) REFERENCES tenants (id) ON DELETE CASCADE, 
	CONSTRAINT uq_a2a_task_authorization_idem UNIQUE (tenant_id, idempotency_key), 
	CONSTRAINT uq_a2a_task_registration_task UNIQUE (tenant_id, registration_id, task_id)
);
CREATE TABLE agent_capabilities (
	id INTEGER NOT NULL, 
	workspace VARCHAR(128) NOT NULL, 
	agent VARCHAR(128) NOT NULL, 
	capabilities JSON NOT NULL, 
	authority JSON NOT NULL, 
	cost_score FLOAT NOT NULL, 
	latency_ms FLOAT NOT NULL, 
	available BOOLEAN NOT NULL, 
	metadata JSON NOT NULL, 
	updated_at DATETIME NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT uq_agent_capability UNIQUE (workspace, agent)
);
CREATE TABLE agent_protocol_registrations (
	id VARCHAR(64) NOT NULL, 
	tenant_id VARCHAR(64) NOT NULL, 
	protocol VARCHAR(32) NOT NULL, 
	protocol_version VARCHAR(64) NOT NULL, 
	external_id VARCHAR(512) NOT NULL, 
	agent_id VARCHAR(64), 
	endpoint VARCHAR(2048) NOT NULL, 
	auth_header_name VARCHAR(255), 
	encrypted_auth_value BLOB, 
	manifest JSON NOT NULL, 
	manifest_hash VARCHAR(64) NOT NULL, 
	current_manifest_version INTEGER NOT NULL, 
	status VARCHAR(32) NOT NULL, 
	created_by_key_id VARCHAR(64) NOT NULL, 
	created_at DATETIME NOT NULL, 
	updated_at DATETIME NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(tenant_id) REFERENCES tenants (id) ON DELETE CASCADE, 
	CONSTRAINT uq_protocol_external UNIQUE (tenant_id, protocol, external_id)
);
CREATE TABLE agents (
	id VARCHAR(64) NOT NULL, 
	tenant_id VARCHAR(64) NOT NULL, 
	external_id VARCHAR(255) NOT NULL, 
	name VARCHAR(255) NOT NULL, 
	version VARCHAR(128) NOT NULL, 
	workload_identity VARCHAR(1024) NOT NULL, 
	model VARCHAR(512) NOT NULL, 
	instruction_hash VARCHAR(128) NOT NULL, 
	deployment_digest VARCHAR(255), 
	manifest_hash VARCHAR(64) NOT NULL, 
	allowed_tools JSON NOT NULL, 
	allowed_data_classes JSON NOT NULL, 
	status VARCHAR(32) NOT NULL, 
	metadata_json JSON NOT NULL, 
	created_by_key_id VARCHAR(64) NOT NULL, 
	revoked_by_key_id VARCHAR(64), 
	revocation_reason TEXT, 
	created_at DATETIME NOT NULL, 
	updated_at DATETIME NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(tenant_id) REFERENCES tenants (id) ON DELETE CASCADE, 
	CONSTRAINT uq_agent_external UNIQUE (tenant_id, external_id), 
	CONSTRAINT uq_agent_manifest_hash UNIQUE (tenant_id, manifest_hash)
);
CREATE TABLE alembic_version (
	version_num VARCHAR(32) NOT NULL, 
	CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
);
INSERT INTO "alembic_version" VALUES('05a2a405852d');
CREATE TABLE api_keys (
	id VARCHAR(64) NOT NULL, 
	tenant_id VARCHAR(64) NOT NULL, 
	name VARCHAR(255) NOT NULL, 
	secret_digest VARCHAR(64) NOT NULL, 
	scopes JSON NOT NULL, 
	status VARCHAR(32) NOT NULL, 
	expires_at DATETIME, 
	last_used_at DATETIME, 
	bound_agent_id VARCHAR(64), 
	bound_workload_identity VARCHAR(1024), 
	bound_instance_id VARCHAR(255), 
	bound_principal_type VARCHAR(32), 
	bound_principal_id VARCHAR(255), 
	created_by_key_id VARCHAR(64), 
	created_at DATETIME NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(tenant_id) REFERENCES tenants (id) ON DELETE CASCADE
);
CREATE TABLE approval_votes (
	id VARCHAR(64) NOT NULL, 
	tenant_id VARCHAR(64) NOT NULL, 
	approval_id VARCHAR(64) NOT NULL, 
	key_id VARCHAR(64) NOT NULL, 
	decision VARCHAR(16) NOT NULL, 
	reason TEXT NOT NULL, 
	created_at DATETIME NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(approval_id) REFERENCES approvals (id) ON DELETE CASCADE, 
	FOREIGN KEY(tenant_id) REFERENCES tenants (id) ON DELETE CASCADE, 
	CONSTRAINT uq_approval_vote_key UNIQUE (approval_id, key_id)
);
CREATE TABLE approvals (
	id VARCHAR(64) NOT NULL, 
	tenant_id VARCHAR(64) NOT NULL, 
	trace_id VARCHAR(64) NOT NULL, 
	decision_id VARCHAR(64) NOT NULL, 
	request_hash VARCHAR(64) NOT NULL, 
	requested_by_key_id VARCHAR(64) NOT NULL, 
	status VARCHAR(32) NOT NULL, 
	request_json JSON NOT NULL, 
	required_approvals INTEGER NOT NULL, 
	approval_count INTEGER NOT NULL, 
	decided_by_key_id VARCHAR(64), 
	decision_reason TEXT, 
	created_at DATETIME NOT NULL, 
	decided_at DATETIME, 
	expires_at DATETIME NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(decision_id) REFERENCES decisions (id) ON DELETE CASCADE, 
	FOREIGN KEY(tenant_id) REFERENCES tenants (id) ON DELETE CASCADE
);
CREATE TABLE artifacts (
	id VARCHAR(64) NOT NULL, 
	tenant_id VARCHAR(64) NOT NULL, 
	trace_id VARCHAR(64) NOT NULL, 
	filename VARCHAR(512) NOT NULL, 
	media_type VARCHAR(255) NOT NULL, 
	size_bytes INTEGER NOT NULL, 
	sha256 VARCHAR(64) NOT NULL, 
	encrypted_blob BLOB, 
	storage_key VARCHAR(1024), 
	scan_status VARCHAR(32) NOT NULL, 
	scan_result JSON NOT NULL, 
	quarantined BOOLEAN NOT NULL, 
	created_at DATETIME NOT NULL, 
	expires_at DATETIME NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(tenant_id) REFERENCES tenants (id) ON DELETE CASCADE
);
CREATE TABLE audit_anchor_claims (
	anchor_id VARCHAR(64) NOT NULL, 
	tenant_id VARCHAR(64) NOT NULL, 
	destination VARCHAR(255) NOT NULL, 
	status VARCHAR(32) NOT NULL, 
	priority INTEGER NOT NULL, 
	attempts INTEGER NOT NULL, 
	max_attempts INTEGER NOT NULL, 
	available_at DATETIME NOT NULL, 
	lease_owner VARCHAR(255), 
	lease_expires_at DATETIME, 
	fencing_token INTEGER NOT NULL, 
	created_at DATETIME NOT NULL, 
	processed_at DATETIME, 
	PRIMARY KEY (anchor_id)
);
CREATE TABLE audit_anchors (
	id VARCHAR(64) NOT NULL, 
	tenant_id VARCHAR(64) NOT NULL, 
	sequence INTEGER NOT NULL, 
	chain_head VARCHAR(64) NOT NULL, 
	destination VARCHAR(255) NOT NULL, 
	envelope JSON NOT NULL, 
	receipt JSON NOT NULL, 
	receipt_hash VARCHAR(64) NOT NULL, 
	status VARCHAR(32) NOT NULL, 
	priority INTEGER NOT NULL, 
	attempts INTEGER NOT NULL, 
	max_attempts INTEGER NOT NULL, 
	available_at DATETIME NOT NULL, 
	lease_owner VARCHAR(255), 
	lease_expires_at DATETIME, 
	fencing_token INTEGER NOT NULL, 
	last_error TEXT, 
	previous_anchor_id VARCHAR(64), 
	anchored_at DATETIME NOT NULL, 
	verified_at DATETIME, 
	PRIMARY KEY (id), 
	FOREIGN KEY(tenant_id) REFERENCES tenants (id) ON DELETE CASCADE, 
	CONSTRAINT uq_anchor_sequence_destination UNIQUE (tenant_id, sequence, destination)
);
CREATE TABLE audit_checkpoints (
	id VARCHAR(64) NOT NULL, 
	tenant_id VARCHAR(64) NOT NULL, 
	sequence INTEGER NOT NULL, 
	head_hash VARCHAR(64) NOT NULL, 
	signature TEXT NOT NULL, 
	key_id VARCHAR(128) NOT NULL, 
	created_at DATETIME NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(tenant_id) REFERENCES tenants (id) ON DELETE CASCADE, 
	CONSTRAINT uq_checkpoint_sequence UNIQUE (tenant_id, sequence)
);
CREATE TABLE budget_reservations (
	id VARCHAR(64) NOT NULL, 
	tenant_id VARCHAR(64) NOT NULL, 
	budget_id VARCHAR(64) NOT NULL, 
	trace_id VARCHAR(64) NOT NULL, 
	idempotency_key VARCHAR(128) NOT NULL, 
	amounts JSON NOT NULL, 
	status VARCHAR(32) NOT NULL, 
	expires_at DATETIME NOT NULL, 
	created_at DATETIME NOT NULL, 
	settled_at DATETIME, 
	PRIMARY KEY (id), 
	FOREIGN KEY(budget_id) REFERENCES runtime_budgets (id) ON DELETE CASCADE, 
	FOREIGN KEY(tenant_id) REFERENCES tenants (id) ON DELETE CASCADE, 
	CONSTRAINT uq_budget_reservation_idem UNIQUE (tenant_id, idempotency_key)
);
CREATE TABLE bus_messages (
	id VARCHAR(80) NOT NULL, 
	packet_id VARCHAR(64) NOT NULL, 
	sender VARCHAR(128), 
	receiver VARCHAR(128) NOT NULL, 
	workspace VARCHAR(128) NOT NULL, 
	run_id VARCHAR(128), 
	correlation_id VARCHAR(128), 
	idempotency_key VARCHAR(128), 
	payload_digest VARCHAR(64) NOT NULL, 
	partition_key VARCHAR(128) NOT NULL, 
	ordering_key VARCHAR(128), 
	sequence_no INTEGER, 
	priority INTEGER NOT NULL, 
	status VARCHAR(16) NOT NULL, 
	wire JSON NOT NULL, 
	strategy VARCHAR(64) NOT NULL, 
	estimated_tokens INTEGER NOT NULL, 
	wire_bytes INTEGER NOT NULL, 
	expires_at DATETIME, 
	claimed_at DATETIME, 
	acked_at DATETIME, 
	created_at DATETIME NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT uq_bus_idempotency UNIQUE (workspace, idempotency_key)
);
CREATE TABLE calibration_buckets (
	id INTEGER NOT NULL, 
	workspace VARCHAR(128) NOT NULL, 
	receiver VARCHAR(128) NOT NULL, 
	model VARCHAR(256) NOT NULL, 
	task_family VARCHAR(128) NOT NULL, 
	bucket INTEGER NOT NULL, 
	sample_count INTEGER NOT NULL, 
	predicted_sum FLOAT NOT NULL, 
	observed_sum FLOAT NOT NULL, 
	squared_error_sum FLOAT NOT NULL, 
	updated_at DATETIME NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT uq_calibration_bucket UNIQUE (workspace, receiver, model, task_family, bucket)
);
CREATE TABLE candidates (
	id INTEGER NOT NULL, 
	codebook VARCHAR(128) NOT NULL, 
	canonical VARCHAR(512) NOT NULL, 
	seen_count INTEGER NOT NULL, 
	estimated_savings_bytes INTEGER NOT NULL, 
	max_neighbor_similarity FLOAT NOT NULL, 
	first_seen DATETIME NOT NULL, 
	last_seen DATETIME NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT uq_candidate_cb_canonical UNIQUE (codebook, canonical)
);
CREATE TABLE capabilities (
	id VARCHAR(64) NOT NULL, 
	tenant_id VARCHAR(64) NOT NULL, 
	decision_id VARCHAR(64) NOT NULL, 
	agent_id VARCHAR(64) NOT NULL, 
	trace_id VARCHAR(64) NOT NULL, 
	tool VARCHAR(512) NOT NULL, 
	operation VARCHAR(255) NOT NULL, 
	resources JSON NOT NULL, 
	constraints JSON NOT NULL, 
	request_hash VARCHAR(64) NOT NULL, 
	arguments_hash VARCHAR(64) NOT NULL, 
	token_hash VARCHAR(64) NOT NULL, 
	max_uses INTEGER NOT NULL, 
	use_count INTEGER NOT NULL, 
	status VARCHAR(32) NOT NULL, 
	not_before DATETIME NOT NULL, 
	expires_at DATETIME NOT NULL, 
	created_at DATETIME NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(decision_id) REFERENCES decisions (id) ON DELETE CASCADE, 
	FOREIGN KEY(tenant_id) REFERENCES tenants (id) ON DELETE CASCADE, 
	CONSTRAINT uq_capability_decision UNIQUE (tenant_id, decision_id), 
	UNIQUE (token_hash)
);
CREATE TABLE codebook_releases (
	id VARCHAR(80) NOT NULL, 
	namespace VARCHAR(128) NOT NULL, 
	release VARCHAR(128) NOT NULL, 
	merkle_root VARCHAR(64) NOT NULL, 
	manifest JSON NOT NULL, 
	key_id VARCHAR(128) NOT NULL, 
	signature TEXT NOT NULL, 
	status VARCHAR(16) NOT NULL, 
	created_at DATETIME NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT uq_codebook_release UNIQUE (namespace, release)
);
CREATE TABLE concept_aliases (
	id INTEGER NOT NULL, 
	codebook VARCHAR(128) NOT NULL, 
	alias VARCHAR(512) NOT NULL, 
	concept_id INTEGER NOT NULL, 
	created_at DATETIME NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(concept_id) REFERENCES concepts (id), 
	CONSTRAINT uq_concept_alias UNIQUE (codebook, alias)
);
CREATE TABLE concepts (
	id INTEGER NOT NULL, 
	codebook VARCHAR(128) NOT NULL, 
	canonical VARCHAR(512) NOT NULL, 
	description TEXT NOT NULL, 
	embedding_space VARCHAR(256) NOT NULL, 
	vector JSON NOT NULL, 
	lsh_bucket VARCHAR(32) NOT NULL, 
	seen_count INTEGER NOT NULL, 
	confidence FLOAT NOT NULL, 
	status VARCHAR(32) NOT NULL, 
	version INTEGER NOT NULL, 
	semantic_hash VARCHAR(64) NOT NULL, 
	replacement_id INTEGER, 
	created_at DATETIME NOT NULL, 
	updated_at DATETIME NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(replacement_id) REFERENCES concepts (id), 
	CONSTRAINT uq_concept_codebook_canonical UNIQUE (codebook, canonical)
);
CREATE TABLE contradictions (
	id VARCHAR(80) NOT NULL, 
	workspace VARCHAR(128) NOT NULL, 
	left_fact_id VARCHAR(80) NOT NULL, 
	right_fact_id VARCHAR(80) NOT NULL, 
	status VARCHAR(32) NOT NULL, 
	resolution JSON NOT NULL, 
	created_at DATETIME NOT NULL, 
	resolved_at DATETIME, 
	PRIMARY KEY (id), 
	FOREIGN KEY(left_fact_id) REFERENCES semantic_facts (id), 
	FOREIGN KEY(right_fact_id) REFERENCES semantic_facts (id), 
	CONSTRAINT uq_contradiction_pair UNIQUE (left_fact_id, right_fact_id)
);
CREATE TABLE decisions (
	id VARCHAR(64) NOT NULL, 
	tenant_id VARCHAR(64) NOT NULL, 
	trace_id VARCHAR(64) NOT NULL, 
	agent_id VARCHAR(64) NOT NULL, 
	request_hash VARCHAR(64) NOT NULL, 
	request_json JSON NOT NULL, 
	outcome VARCHAR(32) NOT NULL, 
	risk_score INTEGER NOT NULL, 
	reasons JSON NOT NULL, 
	constraints JSON NOT NULL, 
	enforcement_plan JSON NOT NULL, 
	findings JSON NOT NULL, 
	policy_version VARCHAR(128) NOT NULL, 
	matched_rule TEXT NOT NULL, 
	reason_codes JSON NOT NULL, 
	receipt TEXT NOT NULL, 
	approval_id VARCHAR(64), 
	idempotency_key VARCHAR(128), 
	expires_at DATETIME NOT NULL, 
	created_at DATETIME NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(tenant_id) REFERENCES tenants (id) ON DELETE CASCADE, 
	CONSTRAINT uq_decision_idempotency UNIQUE (tenant_id, idempotency_key)
);
CREATE TABLE delegation_grants (
	id VARCHAR(64) NOT NULL, 
	tenant_id VARCHAR(64) NOT NULL, 
	parent_agent_id VARCHAR(64) NOT NULL, 
	child_agent_id VARCHAR(64) NOT NULL, 
	parent_grant_id VARCHAR(64), 
	trace_id VARCHAR(64) NOT NULL, 
	objective TEXT NOT NULL, 
	allowed_tools JSON NOT NULL, 
	allowed_data_classes JSON NOT NULL, 
	resource_patterns JSON NOT NULL, 
	max_depth INTEGER NOT NULL, 
	max_fanout INTEGER NOT NULL, 
	budget_limits JSON NOT NULL, 
	consumed_fanout INTEGER NOT NULL, 
	consumed_steps INTEGER NOT NULL, 
	consumed_budget JSON NOT NULL, 
	expires_at DATETIME NOT NULL, 
	grant_hash VARCHAR(64) NOT NULL, 
	signature TEXT NOT NULL, 
	status VARCHAR(32) NOT NULL, 
	created_by_key_id VARCHAR(64) NOT NULL, 
	created_at DATETIME NOT NULL, 
	revoked_at DATETIME, 
	PRIMARY KEY (id), 
	FOREIGN KEY(tenant_id) REFERENCES tenants (id) ON DELETE CASCADE
);
CREATE TABLE dispatch_claims (
	outbox_id VARCHAR(64) NOT NULL, 
	tenant_id VARCHAR(64) NOT NULL, 
	priority INTEGER NOT NULL, 
	status VARCHAR(32) NOT NULL, 
	attempts INTEGER NOT NULL, 
	max_attempts INTEGER NOT NULL, 
	available_at DATETIME NOT NULL, 
	lease_owner VARCHAR(255), 
	fencing_token INTEGER NOT NULL, 
	lease_expires_at DATETIME, 
	created_at DATETIME NOT NULL, 
	processed_at DATETIME, 
	PRIMARY KEY (outbox_id)
);
CREATE TABLE events (
	id VARCHAR(64) NOT NULL, 
	tenant_id VARCHAR(64) NOT NULL, 
	trace_id VARCHAR(64) NOT NULL, 
	parent_event_id VARCHAR(64), 
	sequence INTEGER NOT NULL, 
	event_type VARCHAR(128) NOT NULL, 
	payload JSON NOT NULL, 
	previous_hash VARCHAR(64) NOT NULL, 
	event_hash VARCHAR(64) NOT NULL, 
	signature TEXT NOT NULL, 
	key_id VARCHAR(128) NOT NULL, 
	created_at DATETIME NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(tenant_id) REFERENCES tenants (id) ON DELETE CASCADE, 
	UNIQUE (event_hash), 
	CONSTRAINT uq_event_sequence UNIQUE (tenant_id, sequence)
);
CREATE TABLE evidence_objects (
	id VARCHAR(64) NOT NULL, 
	tenant_id VARCHAR(64) NOT NULL, 
	namespace VARCHAR(64) NOT NULL, 
	external_id VARCHAR(255) NOT NULL, 
	media_type VARCHAR(255) NOT NULL, 
	size_bytes INTEGER NOT NULL, 
	sha256 VARCHAR(64) NOT NULL, 
	storage_key VARCHAR(1024) NOT NULL, 
	metadata_json JSON NOT NULL, 
	immutable BOOLEAN NOT NULL, 
	created_at DATETIME NOT NULL, 
	expires_at DATETIME, 
	PRIMARY KEY (id), 
	FOREIGN KEY(tenant_id) REFERENCES tenants (id) ON DELETE CASCADE, 
	CONSTRAINT uq_evidence_object_external UNIQUE (tenant_id, namespace, external_id)
);
CREATE TABLE executions (
	id VARCHAR(64) NOT NULL, 
	tenant_id VARCHAR(64) NOT NULL, 
	trace_id VARCHAR(64) NOT NULL, 
	broker_type VARCHAR(16) NOT NULL, 
	broker_id VARCHAR(64) NOT NULL, 
	decision_id VARCHAR(64), 
	capability_id VARCHAR(64), 
	idempotency_key VARCHAR(128) NOT NULL, 
	request_hash VARCHAR(64) NOT NULL, 
	transformed_request_hash VARCHAR(64) NOT NULL, 
	request_json JSON NOT NULL, 
	controls_applied JSON NOT NULL, 
	state VARCHAR(32) NOT NULL, 
	attempt_count INTEGER NOT NULL, 
	max_attempts INTEGER NOT NULL, 
	priority INTEGER NOT NULL, 
	lease_owner VARCHAR(255), 
	fencing_token INTEGER NOT NULL, 
	next_attempt_at DATETIME, 
	upstream_idempotency_key VARCHAR(128) NOT NULL, 
	response_status_code INTEGER, 
	response_headers JSON, 
	response_body JSON, 
	response_hash VARCHAR(64), 
	last_error_code VARCHAR(128), 
	last_error_message TEXT, 
	reconciliation_status VARCHAR(32) NOT NULL, 
	lease_expires_at DATETIME, 
	created_at DATETIME NOT NULL, 
	updated_at DATETIME NOT NULL, 
	completed_at DATETIME, 
	PRIMARY KEY (id), 
	FOREIGN KEY(tenant_id) REFERENCES tenants (id) ON DELETE CASCADE, 
	CONSTRAINT uq_execution_idempotency UNIQUE (tenant_id, idempotency_key)
);
CREATE TABLE fact_dependencies (
	id INTEGER NOT NULL, 
	parent_fact_id VARCHAR(80) NOT NULL, 
	child_fact_id VARCHAR(80) NOT NULL, 
	relation VARCHAR(64) NOT NULL, 
	created_at DATETIME NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(child_fact_id) REFERENCES semantic_facts (id), 
	FOREIGN KEY(parent_fact_id) REFERENCES semantic_facts (id), 
	CONSTRAINT uq_fact_dependency UNIQUE (parent_fact_id, child_fact_id)
);
CREATE TABLE federation_peers (
	id VARCHAR(80) NOT NULL, 
	workspace VARCHAR(128) NOT NULL, 
	name VARCHAR(128) NOT NULL, 
	base_url VARCHAR(2048) NOT NULL, 
	public_key_b64 TEXT NOT NULL, 
	allowed_namespaces JSON NOT NULL, 
	enabled BOOLEAN NOT NULL, 
	metadata JSON NOT NULL, 
	created_at DATETIME NOT NULL, 
	updated_at DATETIME NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT uq_federation_peer UNIQUE (workspace, name)
);
CREATE TABLE idempotency_records (
	id INTEGER NOT NULL, 
	workspace VARCHAR(128) NOT NULL, 
	operation VARCHAR(128) NOT NULL, 
	"key" VARCHAR(128) NOT NULL, 
	request_hash VARCHAR(64) NOT NULL, 
	response JSON NOT NULL, 
	created_at DATETIME NOT NULL, 
	expires_at DATETIME, 
	PRIMARY KEY (id), 
	CONSTRAINT uq_idempotency_record UNIQUE (workspace, operation, "key")
);
CREATE TABLE incidents (
	id VARCHAR(64) NOT NULL, 
	tenant_id VARCHAR(64) NOT NULL, 
	trace_id VARCHAR(64) NOT NULL, 
	severity VARCHAR(16) NOT NULL, 
	category VARCHAR(128) NOT NULL, 
	title VARCHAR(512) NOT NULL, 
	description TEXT NOT NULL, 
	status VARCHAR(32) NOT NULL, 
	evidence JSON NOT NULL, 
	created_at DATETIME NOT NULL, 
	updated_at DATETIME NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(tenant_id) REFERENCES tenants (id) ON DELETE CASCADE
);
CREATE TABLE information_flow_labels (
	id INTEGER NOT NULL, 
	workspace VARCHAR(128) NOT NULL, 
	object_kind VARCHAR(32) NOT NULL, 
	object_id VARCHAR(128) NOT NULL, 
	label VARCHAR(64) NOT NULL, 
	source_kind VARCHAR(32), 
	source_id VARCHAR(128), 
	created_at DATETIME NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT uq_information_flow_label UNIQUE (workspace, object_kind, object_id, label)
);
CREATE TABLE learned_patterns (
	id INTEGER NOT NULL, 
	codebook VARCHAR(128) NOT NULL, 
	signature VARCHAR(64) NOT NULL, 
	canonical TEXT NOT NULL, 
	concept_id INTEGER NOT NULL, 
	composition JSON NOT NULL, 
	relation_structure JSON NOT NULL, 
	embedding_space VARCHAR(256) NOT NULL, 
	vector JSON NOT NULL, 
	occurrence_count INTEGER NOT NULL, 
	estimated_savings_bytes INTEGER NOT NULL, 
	semantic_variance FLOAT NOT NULL, 
	slot_samples JSON NOT NULL, 
	confidence FLOAT NOT NULL, 
	status VARCHAR(32) NOT NULL, 
	version INTEGER NOT NULL, 
	shadow_samples INTEGER NOT NULL, 
	shadow_success_sum FLOAT NOT NULL, 
	task_success_count INTEGER NOT NULL, 
	task_success_sum FLOAT NOT NULL, 
	use_count INTEGER NOT NULL, 
	utility_score FLOAT NOT NULL, 
	ambiguity_score FLOAT NOT NULL, 
	interoperability_score FLOAT NOT NULL, 
	calibrated_reliability FLOAT NOT NULL, 
	trust_scope VARCHAR(32) NOT NULL, 
	source_diversity INTEGER NOT NULL, 
	dominant_source_share FLOAT NOT NULL, 
	trust_score FLOAT NOT NULL, 
	last_used_at DATETIME, 
	cooling_since DATETIME, 
	created_at DATETIME NOT NULL, 
	updated_at DATETIME NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(concept_id) REFERENCES concepts (id), 
	CONSTRAINT uq_learned_pattern_signature UNIQUE (codebook, signature), 
	CONSTRAINT uq_learned_pattern_concept UNIQUE (concept_id)
);
CREATE TABLE legal_holds (
	id VARCHAR(64) NOT NULL, 
	tenant_id VARCHAR(64) NOT NULL, 
	scope VARCHAR(64) NOT NULL, 
	reason TEXT NOT NULL, 
	status VARCHAR(32) NOT NULL, 
	created_by_key_id VARCHAR(64) NOT NULL, 
	created_at DATETIME NOT NULL, 
	expires_at DATETIME, 
	released_at DATETIME, 
	release_reason TEXT, 
	PRIMARY KEY (id), 
	FOREIGN KEY(tenant_id) REFERENCES tenants (id) ON DELETE CASCADE
);
CREATE TABLE lifecycle_claims (
	job_id VARCHAR(64) NOT NULL, 
	tenant_id VARCHAR(64) NOT NULL, 
	job_type VARCHAR(64) NOT NULL, 
	status VARCHAR(32) NOT NULL, 
	priority INTEGER NOT NULL, 
	attempts INTEGER NOT NULL, 
	max_attempts INTEGER NOT NULL, 
	available_at DATETIME NOT NULL, 
	lease_owner VARCHAR(255), 
	lease_expires_at DATETIME, 
	fencing_token INTEGER NOT NULL, 
	created_at DATETIME NOT NULL, 
	processed_at DATETIME, 
	PRIMARY KEY (job_id)
);
CREATE TABLE memory_records (
	id VARCHAR(64) NOT NULL, 
	tenant_id VARCHAR(64) NOT NULL, 
	external_id VARCHAR(255) NOT NULL, 
	version INTEGER NOT NULL, 
	agent_id VARCHAR(64) NOT NULL, 
	trace_id VARCHAR(64) NOT NULL, 
	source_uri VARCHAR(2048) NOT NULL, 
	source_type VARCHAR(32) NOT NULL, 
	content_hash VARCHAR(64) NOT NULL, 
	encrypted_content BLOB NOT NULL, 
	provenance JSON NOT NULL, 
	data_classes JSON NOT NULL, 
	trust_score INTEGER NOT NULL, 
	status VARCHAR(32) NOT NULL, 
	expires_at DATETIME, 
	created_at DATETIME NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(tenant_id) REFERENCES tenants (id) ON DELETE CASCADE, 
	CONSTRAINT uq_memory_external_version UNIQUE (tenant_id, external_id, version)
);
CREATE TABLE message_audit (
	id INTEGER NOT NULL, 
	packet_id VARCHAR(64) NOT NULL, 
	run_id VARCHAR(128), 
	sender VARCHAR(128), 
	receiver VARCHAR(128), 
	workspace VARCHAR(128) NOT NULL, 
	strategy VARCHAR(64) NOT NULL, 
	cache_hit BOOLEAN NOT NULL, 
	input_bytes INTEGER NOT NULL, 
	output_bytes INTEGER NOT NULL, 
	estimated_tokens INTEGER NOT NULL, 
	budget_tokens INTEGER, 
	atom_count INTEGER NOT NULL, 
	ref_count INTEGER NOT NULL, 
	packet JSON NOT NULL, 
	decisions JSON NOT NULL, 
	provenance JSON NOT NULL, 
	task_success FLOAT, 
	semantic_loss_score FLOAT NOT NULL, 
	original_token_estimate INTEGER NOT NULL, 
	receiver_known_ratio FLOAT NOT NULL, 
	pattern_count INTEGER NOT NULL, 
	ref_bytes_avoided INTEGER NOT NULL, 
	created_at DATETIME NOT NULL, 
	PRIMARY KEY (id)
);
CREATE TABLE model_identities (
	id INTEGER NOT NULL, 
	workspace VARCHAR(128) NOT NULL, 
	receiver VARCHAR(128) NOT NULL, 
	provider VARCHAR(128) NOT NULL, 
	model VARCHAR(256) NOT NULL, 
	model_version VARCHAR(128) NOT NULL, 
	runtime VARCHAR(128) NOT NULL, 
	runtime_version VARCHAR(128) NOT NULL, 
	config_hash VARCHAR(64) NOT NULL, 
	identity_hash VARCHAR(64) NOT NULL, 
	active BOOLEAN NOT NULL, 
	created_at DATETIME NOT NULL, 
	last_seen_at DATETIME NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT uq_model_identity UNIQUE (workspace, receiver, identity_hash)
);
CREATE TABLE ordering_counters (
	id INTEGER NOT NULL, 
	workspace VARCHAR(128) NOT NULL, 
	ordering_key VARCHAR(128) NOT NULL, 
	sequence_no INTEGER NOT NULL, 
	updated_at DATETIME NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT uq_ordering_counter UNIQUE (workspace, ordering_key)
);
CREATE TABLE outbox_messages (
	id VARCHAR(64) NOT NULL, 
	tenant_id VARCHAR(64) NOT NULL, 
	aggregate_type VARCHAR(64) NOT NULL, 
	aggregate_id VARCHAR(64) NOT NULL, 
	message_type VARCHAR(128) NOT NULL, 
	payload JSON NOT NULL, 
	status VARCHAR(32) NOT NULL, 
	attempts INTEGER NOT NULL, 
	max_attempts INTEGER NOT NULL, 
	priority INTEGER NOT NULL, 
	lease_owner VARCHAR(255), 
	fencing_token INTEGER NOT NULL, 
	lease_expires_at DATETIME, 
	last_error TEXT, 
	available_at DATETIME NOT NULL, 
	created_at DATETIME NOT NULL, 
	processed_at DATETIME, 
	PRIMARY KEY (id), 
	FOREIGN KEY(tenant_id) REFERENCES tenants (id) ON DELETE CASCADE
);
CREATE TABLE pattern_candidates (
	id INTEGER NOT NULL, 
	codebook VARCHAR(128) NOT NULL, 
	signature VARCHAR(64) NOT NULL, 
	canonical TEXT NOT NULL, 
	composition JSON NOT NULL, 
	relation_structure JSON NOT NULL, 
	occurrence_count INTEGER NOT NULL, 
	estimated_savings_bytes INTEGER NOT NULL, 
	semantic_variance FLOAT NOT NULL, 
	slot_samples JSON NOT NULL, 
	trust_scope VARCHAR(32) NOT NULL, 
	source_diversity INTEGER NOT NULL, 
	dominant_source_share FLOAT NOT NULL, 
	trust_score FLOAT NOT NULL, 
	first_seen DATETIME NOT NULL, 
	last_seen DATETIME NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT uq_pattern_candidate_signature UNIQUE (codebook, signature)
);
CREATE TABLE pattern_edges (
	id INTEGER NOT NULL, 
	parent_pattern_id INTEGER NOT NULL, 
	child_pattern_id INTEGER NOT NULL, 
	position INTEGER NOT NULL, 
	created_at DATETIME NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(child_pattern_id) REFERENCES learned_patterns (id), 
	FOREIGN KEY(parent_pattern_id) REFERENCES learned_patterns (id), 
	CONSTRAINT uq_pattern_edge UNIQUE (parent_pattern_id, child_pattern_id, position)
);
CREATE TABLE pattern_receiver_metrics (
	id INTEGER NOT NULL, 
	pattern_id INTEGER NOT NULL, 
	workspace VARCHAR(128) NOT NULL, 
	receiver VARCHAR(128) NOT NULL, 
	model VARCHAR(256) NOT NULL, 
	sample_count INTEGER NOT NULL, 
	full_success_sum FLOAT NOT NULL, 
	compressed_success_sum FLOAT NOT NULL, 
	fidelity_sum FLOAT NOT NULL, 
	exact_equivalence_count INTEGER NOT NULL, 
	last_seen_at DATETIME NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(pattern_id) REFERENCES learned_patterns (id), 
	CONSTRAINT uq_pattern_receiver_metric UNIQUE (pattern_id, workspace, receiver, model)
);
CREATE TABLE pattern_source_evidence (
	id INTEGER NOT NULL, 
	codebook VARCHAR(128) NOT NULL, 
	signature VARCHAR(64) NOT NULL, 
	source_hash VARCHAR(64) NOT NULL, 
	trust_score FLOAT NOT NULL, 
	observation_count INTEGER NOT NULL, 
	first_seen DATETIME NOT NULL, 
	last_seen DATETIME NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT uq_pattern_source_evidence UNIQUE (codebook, signature, source_hash)
);
CREATE TABLE pattern_validation_evidence (
	id INTEGER NOT NULL, 
	pattern_id INTEGER NOT NULL, 
	workspace VARCHAR(128) NOT NULL, 
	split VARCHAR(16) NOT NULL, 
	receiver VARCHAR(128) NOT NULL, 
	model_identity_hash VARCHAR(64) NOT NULL, 
	task_family VARCHAR(128) NOT NULL, 
	full_success FLOAT NOT NULL, 
	compressed_success FLOAT NOT NULL, 
	fidelity FLOAT NOT NULL, 
	source_hash VARCHAR(64) NOT NULL, 
	created_at DATETIME NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(pattern_id) REFERENCES learned_patterns (id)
);
CREATE TABLE policy_bundles (
	id VARCHAR(64) NOT NULL, 
	tenant_id VARCHAR(64) NOT NULL, 
	version VARCHAR(128) NOT NULL, 
	document JSON NOT NULL, 
	document_hash VARCHAR(64) NOT NULL, 
	active BOOLEAN NOT NULL, 
	created_by_key_id VARCHAR(64) NOT NULL, 
	created_at DATETIME NOT NULL, 
	activated_at DATETIME, 
	activated_by_key_id VARCHAR(64), 
	activation_reason TEXT, 
	rollout_mode VARCHAR(32) NOT NULL, 
	canary_percentage INTEGER NOT NULL, 
	rollout_salt VARCHAR(64), 
	validation_report JSON NOT NULL, 
	supersedes_policy_id VARCHAR(64), 
	PRIMARY KEY (id), 
	FOREIGN KEY(tenant_id) REFERENCES tenants (id) ON DELETE CASCADE, 
	CONSTRAINT uq_policy_version UNIQUE (tenant_id, version)
);
CREATE TABLE protocol_manifest_versions (
	id VARCHAR(64) NOT NULL, 
	tenant_id VARCHAR(64) NOT NULL, 
	registration_id VARCHAR(64) NOT NULL, 
	version INTEGER NOT NULL, 
	protocol_version VARCHAR(64) NOT NULL, 
	manifest JSON NOT NULL, 
	manifest_hash VARCHAR(64) NOT NULL, 
	source VARCHAR(32) NOT NULL, 
	verification JSON NOT NULL, 
	created_by_key_id VARCHAR(64) NOT NULL, 
	created_at DATETIME NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(registration_id) REFERENCES agent_protocol_registrations (id) ON DELETE CASCADE, 
	FOREIGN KEY(tenant_id) REFERENCES tenants (id) ON DELETE CASCADE, 
	CONSTRAINT uq_protocol_manifest_hash UNIQUE (registration_id, manifest_hash), 
	CONSTRAINT uq_protocol_manifest_version UNIQUE (registration_id, version)
);
CREATE TABLE providers (
	id VARCHAR(64) NOT NULL, 
	tenant_id VARCHAR(64) NOT NULL, 
	name VARCHAR(255) NOT NULL, 
	base_url VARCHAR(2048) NOT NULL, 
	auth_header_name VARCHAR(255) NOT NULL, 
	encrypted_auth_value BLOB NOT NULL, 
	allowed_paths JSON NOT NULL, 
	network_zone VARCHAR(16) NOT NULL, 
	resolved_addresses JSON NOT NULL, 
	status VARCHAR(32) NOT NULL, 
	created_at DATETIME NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(tenant_id) REFERENCES tenants (id) ON DELETE CASCADE, 
	CONSTRAINT uq_provider_name UNIQUE (tenant_id, name)
);
CREATE TABLE quota_counters (
	id INTEGER NOT NULL, 
	workspace VARCHAR(128) NOT NULL, 
	resource VARCHAR(64) NOT NULL, 
	window_start DATETIME NOT NULL, 
	used INTEGER NOT NULL, 
	updated_at DATETIME NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT uq_quota_counter UNIQUE (workspace, resource, window_start)
);
CREATE TABLE rate_limit_buckets (
	identity_hash VARCHAR(64) NOT NULL, 
	window_start INTEGER NOT NULL, 
	request_count INTEGER NOT NULL, 
	updated_at DATETIME NOT NULL, 
	PRIMARY KEY (identity_hash, window_start)
);
CREATE TABLE receiver_knowledge (
	id INTEGER NOT NULL, 
	workspace VARCHAR(128) NOT NULL, 
	receiver VARCHAR(128) NOT NULL, 
	current_state VARCHAR(80), 
	capabilities JSON NOT NULL, 
	updated_at DATETIME NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT uq_receiver_knowledge UNIQUE (workspace, receiver)
);
CREATE TABLE receiver_knowledge_items (
	id INTEGER NOT NULL, 
	workspace VARCHAR(128) NOT NULL, 
	receiver VARCHAR(128) NOT NULL, 
	kind VARCHAR(16) NOT NULL, 
	value VARCHAR(128) NOT NULL, 
	confidence FLOAT NOT NULL, 
	stale_at DATETIME, 
	created_at DATETIME NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT uq_receiver_knowledge_item UNIQUE (workspace, receiver, kind, value)
);
CREATE TABLE reference_grants (
	id INTEGER NOT NULL, 
	ref_id VARCHAR(80) NOT NULL, 
	workspace VARCHAR(128) NOT NULL, 
	owner VARCHAR(128), 
	acl JSON NOT NULL, 
	allowed_paths JSON NOT NULL, 
	tier VARCHAR(16) NOT NULL, 
	provenance JSON NOT NULL, 
	sensitivity JSON NOT NULL, 
	version INTEGER NOT NULL, 
	expires_at DATETIME, 
	invalidated_at DATETIME, 
	created_at DATETIME NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(ref_id) REFERENCES "references" (id), 
	CONSTRAINT uq_reference_grant_owner UNIQUE (ref_id, workspace, owner)
);
CREATE TABLE "references" (
	id VARCHAR(80) NOT NULL, 
	media_type VARCHAR(128) NOT NULL, 
	payload JSON, 
	ciphertext TEXT, 
	byte_size INTEGER NOT NULL, 
	workspace VARCHAR(128) NOT NULL, 
	owner VARCHAR(128), 
	acl JSON NOT NULL, 
	tier VARCHAR(16) NOT NULL, 
	provenance JSON NOT NULL, 
	version INTEGER NOT NULL, 
	expires_at DATETIME, 
	invalidated_at DATETIME, 
	created_at DATETIME NOT NULL, 
	PRIMARY KEY (id)
);
CREATE TABLE reliability_windows (
	id INTEGER NOT NULL, 
	workspace VARCHAR(128) NOT NULL, 
	receiver VARCHAR(128) NOT NULL, 
	model_identity_hash VARCHAR(64) NOT NULL, 
	pattern_id INTEGER, 
	task_family VARCHAR(128) NOT NULL, 
	window_start DATETIME NOT NULL, 
	sample_count INTEGER NOT NULL, 
	fidelity_sum FLOAT NOT NULL, 
	status VARCHAR(16) NOT NULL, 
	drift_score FLOAT NOT NULL, 
	updated_at DATETIME NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(pattern_id) REFERENCES learned_patterns (id), 
	CONSTRAINT uq_reliability_window UNIQUE (workspace, receiver, model_identity_hash, pattern_id, task_family, window_start)
);
CREATE TABLE runtime_budgets (
	id VARCHAR(64) NOT NULL, 
	tenant_id VARCHAR(64) NOT NULL, 
	scope_type VARCHAR(32) NOT NULL, 
	scope_id VARCHAR(255) NOT NULL, 
	limits JSON NOT NULL, 
	consumed JSON NOT NULL, 
	reserved JSON NOT NULL, 
	status VARCHAR(32) NOT NULL, 
	version INTEGER NOT NULL, 
	created_at DATETIME NOT NULL, 
	updated_at DATETIME NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(tenant_id) REFERENCES tenants (id) ON DELETE CASCADE, 
	CONSTRAINT uq_budget_scope UNIQUE (tenant_id, scope_type, scope_id)
);
CREATE TABLE semantic_cache (
	"key" VARCHAR(64) NOT NULL, 
	packet JSON NOT NULL, 
	decisions JSON NOT NULL, 
	codebook_fingerprint VARCHAR(64) NOT NULL, 
	hit_count INTEGER NOT NULL, 
	created_at DATETIME NOT NULL, 
	expires_at DATETIME, 
	PRIMARY KEY ("key")
);
CREATE TABLE semantic_facts (
	id VARCHAR(80) NOT NULL, 
	workspace VARCHAR(128) NOT NULL, 
	subject VARCHAR(256) NOT NULL, 
	predicate VARCHAR(256) NOT NULL, 
	object JSON NOT NULL, 
	epistemic_type VARCHAR(32) NOT NULL, 
	source VARCHAR(256), 
	confidence FLOAT NOT NULL, 
	status VARCHAR(32) NOT NULL, 
	provenance JSON NOT NULL, 
	sensitivity JSON NOT NULL, 
	valid_from DATETIME, 
	valid_until DATETIME, 
	invalidated_at DATETIME, 
	created_at DATETIME NOT NULL, 
	updated_at DATETIME NOT NULL, 
	PRIMARY KEY (id)
);
CREATE TABLE shared_states (
	id VARCHAR(80) NOT NULL, 
	revision INTEGER NOT NULL, 
	payload JSON NOT NULL, 
	parent_id VARCHAR(80), 
	workspace VARCHAR(128) NOT NULL, 
	created_by VARCHAR(128), 
	provenance JSON NOT NULL, 
	created_at DATETIME NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(parent_id) REFERENCES shared_states (id)
);
CREATE TABLE signing_public_keys (
	key_id VARCHAR(128) NOT NULL, 
	algorithm VARCHAR(32) NOT NULL, 
	public_pem TEXT NOT NULL, 
	active BOOLEAN NOT NULL, 
	created_at DATETIME NOT NULL, 
	retired_at DATETIME, 
	PRIMARY KEY (key_id)
);
CREATE TABLE state_checkpoints (
	id VARCHAR(80) NOT NULL, 
	workspace VARCHAR(128) NOT NULL, 
	state_id VARCHAR(80) NOT NULL, 
	revision INTEGER NOT NULL, 
	payload_hash VARCHAR(64) NOT NULL, 
	created_at DATETIME NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(state_id) REFERENCES shared_states (id), 
	CONSTRAINT uq_state_checkpoint_state UNIQUE (workspace, state_id)
);
CREATE TABLE subscriptions (
	id VARCHAR(80) NOT NULL, 
	workspace VARCHAR(128) NOT NULL, 
	agent VARCHAR(128) NOT NULL, 
	concepts JSON NOT NULL, 
	filters JSON NOT NULL, 
	min_confidence FLOAT NOT NULL, 
	active BOOLEAN NOT NULL, 
	created_at DATETIME NOT NULL, 
	PRIMARY KEY (id)
);
CREATE TABLE tenant_key_routes (
	tenant_id VARCHAR(64) NOT NULL, 
	backend VARCHAR(32) NOT NULL, 
	key_id VARCHAR(2048) NOT NULL, 
	historical_key_ids JSON NOT NULL, 
	wrapped_local_key BLOB, 
	status VARCHAR(32) NOT NULL, 
	version INTEGER NOT NULL, 
	created_at DATETIME NOT NULL, 
	rotated_at DATETIME, 
	destruction_requested_at DATETIME, 
	destroyed_at DATETIME, 
	destruction_receipt JSON NOT NULL, 
	PRIMARY KEY (tenant_id), 
	FOREIGN KEY(tenant_id) REFERENCES tenants (id) ON DELETE CASCADE
);
CREATE TABLE tenant_lifecycle_jobs (
	id VARCHAR(64) NOT NULL, 
	tenant_id VARCHAR(64) NOT NULL, 
	job_type VARCHAR(64) NOT NULL, 
	idempotency_key VARCHAR(128) NOT NULL, 
	status VARCHAR(32) NOT NULL, 
	parameters JSON NOT NULL, 
	result JSON NOT NULL, 
	result_storage_key VARCHAR(1024), 
	requested_by_key_id VARCHAR(64) NOT NULL, 
	priority INTEGER NOT NULL, 
	attempt_count INTEGER NOT NULL, 
	max_attempts INTEGER NOT NULL, 
	available_at DATETIME NOT NULL, 
	lease_owner VARCHAR(255), 
	lease_expires_at DATETIME, 
	fencing_token INTEGER NOT NULL, 
	external_effect_started_at DATETIME, 
	reconciliation_status VARCHAR(32) NOT NULL, 
	last_error TEXT, 
	created_at DATETIME NOT NULL, 
	updated_at DATETIME NOT NULL, 
	completed_at DATETIME, 
	PRIMARY KEY (id), 
	FOREIGN KEY(tenant_id) REFERENCES tenants (id) ON DELETE CASCADE, 
	CONSTRAINT uq_lifecycle_job_idempotency UNIQUE (tenant_id, idempotency_key)
);
CREATE TABLE tenants (
	id VARCHAR(64) NOT NULL, 
	name VARCHAR(255) NOT NULL, 
	status VARCHAR(32) NOT NULL, 
	region VARCHAR(64), 
	retention_policy JSON NOT NULL, 
	suspended_at DATETIME, 
	deletion_requested_at DATETIME, 
	deleted_at DATETIME, 
	crypto_erased_at DATETIME, 
	created_at DATETIME NOT NULL, 
	PRIMARY KEY (id)
);
INSERT INTO "tenants" VALUES('ten_compat_001','Compatibility Fixture','active',NULL,'{}',NULL,NULL,NULL,NULL,'2026-08-20 00:00:00');
CREATE TABLE tools (
	id VARCHAR(64) NOT NULL, 
	tenant_id VARCHAR(64) NOT NULL, 
	name VARCHAR(255) NOT NULL, 
	base_url VARCHAR(2048) NOT NULL, 
	auth_header_name VARCHAR(255) NOT NULL, 
	encrypted_auth_value BLOB NOT NULL, 
	allowed_operations JSON NOT NULL, 
	network_zone VARCHAR(16) NOT NULL, 
	resolved_addresses JSON NOT NULL, 
	status VARCHAR(32) NOT NULL, 
	created_at DATETIME NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(tenant_id) REFERENCES tenants (id) ON DELETE CASCADE, 
	CONSTRAINT uq_tool_name UNIQUE (tenant_id, name)
);
CREATE TABLE workload_identity_bindings (
	id VARCHAR(64) NOT NULL, 
	tenant_id VARCHAR(64) NOT NULL, 
	spiffe_id VARCHAR(1024) NOT NULL, 
	agent_id VARCHAR(64) NOT NULL, 
	instance_pattern VARCHAR(255), 
	principal_type VARCHAR(32) NOT NULL, 
	principal_id VARCHAR(255) NOT NULL, 
	scopes JSON NOT NULL, 
	trust_domain VARCHAR(255) NOT NULL, 
	status VARCHAR(32) NOT NULL, 
	created_by_key_id VARCHAR(64) NOT NULL, 
	created_at DATETIME NOT NULL, 
	revoked_at DATETIME, 
	PRIMARY KEY (id), 
	FOREIGN KEY(tenant_id) REFERENCES tenants (id) ON DELETE CASCADE, 
	CONSTRAINT uq_workload_spiffe UNIQUE (tenant_id, spiffe_id)
);
CREATE INDEX ix_agent_capabilities_agent ON agent_capabilities (agent);
CREATE INDEX ix_agent_capabilities_available ON agent_capabilities (available);
CREATE INDEX ix_agent_capabilities_workspace ON agent_capabilities (workspace);
CREATE INDEX ix_agent_capability_available ON agent_capabilities (workspace, available);
CREATE INDEX ix_audit_anchor_claims_available_at ON audit_anchor_claims (available_at);
CREATE INDEX ix_audit_anchor_claims_destination ON audit_anchor_claims (destination);
CREATE INDEX ix_audit_anchor_claims_lease_expires_at ON audit_anchor_claims (lease_expires_at);
CREATE INDEX ix_audit_anchor_claims_lease_owner ON audit_anchor_claims (lease_owner);
CREATE INDEX ix_audit_anchor_claims_status ON audit_anchor_claims (status);
CREATE INDEX ix_audit_anchor_claims_tenant_id ON audit_anchor_claims (tenant_id);
CREATE INDEX ix_bus_messages_correlation_id ON bus_messages (correlation_id);
CREATE INDEX ix_bus_messages_expires_at ON bus_messages (expires_at);
CREATE INDEX ix_bus_messages_idempotency_key ON bus_messages (idempotency_key);
CREATE INDEX ix_bus_messages_ordering_key ON bus_messages (ordering_key);
CREATE INDEX ix_bus_messages_packet_id ON bus_messages (packet_id);
CREATE INDEX ix_bus_messages_partition_key ON bus_messages (partition_key);
CREATE INDEX ix_bus_messages_receiver ON bus_messages (receiver);
CREATE INDEX ix_bus_messages_run_id ON bus_messages (run_id);
CREATE INDEX ix_bus_messages_sender ON bus_messages (sender);
CREATE INDEX ix_bus_messages_status ON bus_messages (status);
CREATE INDEX ix_bus_messages_workspace ON bus_messages (workspace);
CREATE INDEX ix_bus_partition_order ON bus_messages (workspace, partition_key, ordering_key, sequence_no);
CREATE INDEX ix_bus_receiver_status_priority ON bus_messages (workspace, receiver, status, priority);
CREATE INDEX ix_bus_run_created ON bus_messages (run_id, created_at);
CREATE INDEX ix_calibration_buckets_model ON calibration_buckets (model);
CREATE INDEX ix_calibration_buckets_receiver ON calibration_buckets (receiver);
CREATE INDEX ix_calibration_buckets_task_family ON calibration_buckets (task_family);
CREATE INDEX ix_calibration_buckets_workspace ON calibration_buckets (workspace);
CREATE INDEX ix_calibration_lookup ON calibration_buckets (workspace, receiver, model, task_family);
CREATE INDEX ix_candidates_codebook ON candidates (codebook);
CREATE INDEX ix_codebook_release_active ON codebook_releases (namespace, status, created_at);
CREATE INDEX ix_codebook_releases_merkle_root ON codebook_releases (merkle_root);
CREATE INDEX ix_codebook_releases_namespace ON codebook_releases (namespace);
CREATE INDEX ix_codebook_releases_release ON codebook_releases (release);
CREATE INDEX ix_codebook_releases_status ON codebook_releases (status);
CREATE INDEX ix_concepts_codebook ON concepts (codebook);
CREATE INDEX ix_concepts_codebook_count ON concepts (codebook, seen_count);
CREATE INDEX ix_concepts_embedding_space ON concepts (embedding_space);
CREATE INDEX ix_concepts_lsh_bucket ON concepts (lsh_bucket);
CREATE INDEX ix_dispatch_claims_available_at ON dispatch_claims (available_at);
CREATE INDEX ix_dispatch_claims_lease_expires_at ON dispatch_claims (lease_expires_at);
CREATE INDEX ix_dispatch_claims_lease_owner ON dispatch_claims (lease_owner);
CREATE INDEX ix_dispatch_claims_priority ON dispatch_claims (priority);
CREATE INDEX ix_dispatch_claims_status ON dispatch_claims (status);
CREATE INDEX ix_dispatch_claims_tenant_id ON dispatch_claims (tenant_id);
CREATE INDEX ix_federation_peers_name ON federation_peers (name);
CREATE INDEX ix_federation_peers_workspace ON federation_peers (workspace);
CREATE INDEX ix_idempotency_expiry ON idempotency_records (expires_at);
CREATE INDEX ix_idempotency_records_expires_at ON idempotency_records (expires_at);
CREATE INDEX ix_idempotency_records_key ON idempotency_records ("key");
CREATE INDEX ix_idempotency_records_operation ON idempotency_records (operation);
CREATE INDEX ix_idempotency_records_workspace ON idempotency_records (workspace);
CREATE INDEX ix_information_flow_labels_label ON information_flow_labels (label);
CREATE INDEX ix_information_flow_labels_object_id ON information_flow_labels (object_id);
CREATE INDEX ix_information_flow_labels_object_kind ON information_flow_labels (object_kind);
CREATE INDEX ix_information_flow_labels_workspace ON information_flow_labels (workspace);
CREATE INDEX ix_information_flow_object ON information_flow_labels (workspace, object_kind, object_id);
CREATE INDEX ix_lifecycle_claims_available_at ON lifecycle_claims (available_at);
CREATE INDEX ix_lifecycle_claims_job_type ON lifecycle_claims (job_type);
CREATE INDEX ix_lifecycle_claims_lease_expires_at ON lifecycle_claims (lease_expires_at);
CREATE INDEX ix_lifecycle_claims_lease_owner ON lifecycle_claims (lease_owner);
CREATE INDEX ix_lifecycle_claims_status ON lifecycle_claims (status);
CREATE INDEX ix_lifecycle_claims_tenant_id ON lifecycle_claims (tenant_id);
CREATE UNIQUE INDEX ix_message_audit_packet_id ON message_audit (packet_id);
CREATE INDEX ix_message_audit_run_id ON message_audit (run_id);
CREATE INDEX ix_message_audit_workspace ON message_audit (workspace);
CREATE INDEX ix_message_run_created ON message_audit (run_id, created_at);
CREATE INDEX ix_message_sender_receiver ON message_audit (sender, receiver);
CREATE INDEX ix_model_identities_active ON model_identities (active);
CREATE INDEX ix_model_identities_identity_hash ON model_identities (identity_hash);
CREATE INDEX ix_model_identities_receiver ON model_identities (receiver);
CREATE INDEX ix_model_identities_workspace ON model_identities (workspace);
CREATE INDEX ix_model_identity_active ON model_identities (workspace, receiver, active);
CREATE INDEX ix_ordering_counters_ordering_key ON ordering_counters (ordering_key);
CREATE INDEX ix_ordering_counters_workspace ON ordering_counters (workspace);
CREATE INDEX ix_pattern_candidate_rank ON pattern_candidates (codebook, occurrence_count, estimated_savings_bytes);
CREATE INDEX ix_pattern_candidates_codebook ON pattern_candidates (codebook);
CREATE INDEX ix_pattern_candidates_signature ON pattern_candidates (signature);
CREATE INDEX ix_pattern_candidates_trust_scope ON pattern_candidates (trust_scope);
CREATE INDEX ix_pattern_source_evidence_codebook ON pattern_source_evidence (codebook);
CREATE INDEX ix_pattern_source_evidence_signature ON pattern_source_evidence (signature);
CREATE INDEX ix_pattern_source_evidence_source_hash ON pattern_source_evidence (source_hash);
CREATE INDEX ix_pattern_source_signature ON pattern_source_evidence (codebook, signature);
CREATE INDEX ix_quota_counters_resource ON quota_counters (resource);
CREATE INDEX ix_quota_counters_window_start ON quota_counters (window_start);
CREATE INDEX ix_quota_counters_workspace ON quota_counters (workspace);
CREATE INDEX ix_quota_workspace_resource ON quota_counters (workspace, resource, window_start);
CREATE INDEX ix_receiver_knowledge_receiver ON receiver_knowledge (receiver);
CREATE INDEX ix_receiver_knowledge_workspace ON receiver_knowledge (workspace);
CREATE INDEX ix_receiver_item_lookup ON receiver_knowledge_items (workspace, receiver, kind);
CREATE INDEX ix_receiver_knowledge_items_kind ON receiver_knowledge_items (kind);
CREATE INDEX ix_receiver_knowledge_items_receiver ON receiver_knowledge_items (receiver);
CREATE INDEX ix_receiver_knowledge_items_value ON receiver_knowledge_items (value);
CREATE INDEX ix_receiver_knowledge_items_workspace ON receiver_knowledge_items (workspace);
CREATE INDEX ix_references_expires_at ON "references" (expires_at);
CREATE INDEX ix_references_tier ON "references" (tier);
CREATE INDEX ix_references_workspace ON "references" (workspace);
CREATE INDEX ix_fact_source ON semantic_facts (workspace, source);
CREATE INDEX ix_fact_subject_predicate ON semantic_facts (workspace, subject, predicate, status);
CREATE INDEX ix_semantic_facts_epistemic_type ON semantic_facts (epistemic_type);
CREATE INDEX ix_semantic_facts_predicate ON semantic_facts (predicate);
CREATE INDEX ix_semantic_facts_source ON semantic_facts (source);
CREATE INDEX ix_semantic_facts_status ON semantic_facts (status);
CREATE INDEX ix_semantic_facts_subject ON semantic_facts (subject);
CREATE INDEX ix_semantic_facts_workspace ON semantic_facts (workspace);
CREATE INDEX ix_shared_states_workspace ON shared_states (workspace);
CREATE INDEX ix_subscription_workspace_agent ON subscriptions (workspace, agent, active);
CREATE INDEX ix_subscriptions_active ON subscriptions (active);
CREATE INDEX ix_subscriptions_agent ON subscriptions (agent);
CREATE INDEX ix_subscriptions_workspace ON subscriptions (workspace);
CREATE INDEX ix_agent_protocol_registrations_agent_id ON agent_protocol_registrations (agent_id);
CREATE INDEX ix_agent_protocol_registrations_protocol ON agent_protocol_registrations (protocol);
CREATE INDEX ix_agent_protocol_registrations_tenant_id ON agent_protocol_registrations (tenant_id);
CREATE INDEX ix_agents_tenant_id ON agents (tenant_id);
CREATE INDEX ix_api_keys_bound_agent_id ON api_keys (bound_agent_id);
CREATE INDEX ix_api_keys_tenant_id ON api_keys (tenant_id);
CREATE INDEX ix_artifacts_sha256 ON artifacts (sha256);
CREATE INDEX ix_artifacts_tenant_id ON artifacts (tenant_id);
CREATE INDEX ix_artifacts_trace_id ON artifacts (trace_id);
CREATE INDEX ix_anchor_delivery ON audit_anchors (status, available_at, priority);
CREATE INDEX ix_audit_anchors_available_at ON audit_anchors (available_at);
CREATE INDEX ix_audit_anchors_lease_expires_at ON audit_anchors (lease_expires_at);
CREATE INDEX ix_audit_anchors_lease_owner ON audit_anchors (lease_owner);
CREATE INDEX ix_audit_anchors_previous_anchor_id ON audit_anchors (previous_anchor_id);
CREATE INDEX ix_audit_anchors_status ON audit_anchors (status);
CREATE INDEX ix_audit_anchors_tenant_id ON audit_anchors (tenant_id);
CREATE INDEX ix_audit_checkpoints_tenant_id ON audit_checkpoints (tenant_id);
CREATE INDEX ix_concept_aliases_codebook ON concept_aliases (codebook);
CREATE INDEX ix_concept_aliases_concept_id ON concept_aliases (concept_id);
CREATE INDEX ix_contradiction_status ON contradictions (workspace, status);
CREATE INDEX ix_contradictions_left_fact_id ON contradictions (left_fact_id);
CREATE INDEX ix_contradictions_right_fact_id ON contradictions (right_fact_id);
CREATE INDEX ix_contradictions_status ON contradictions (status);
CREATE INDEX ix_contradictions_workspace ON contradictions (workspace);
CREATE INDEX ix_decisions_agent_id ON decisions (agent_id);
CREATE INDEX ix_decisions_approval_id ON decisions (approval_id);
CREATE INDEX ix_decisions_outcome ON decisions (outcome);
CREATE INDEX ix_decisions_tenant_id ON decisions (tenant_id);
CREATE INDEX ix_decisions_trace_id ON decisions (trace_id);
CREATE INDEX ix_delegation_grants_child_agent_id ON delegation_grants (child_agent_id);
CREATE INDEX ix_delegation_grants_parent_agent_id ON delegation_grants (parent_agent_id);
CREATE INDEX ix_delegation_grants_parent_grant_id ON delegation_grants (parent_grant_id);
CREATE INDEX ix_delegation_grants_status ON delegation_grants (status);
CREATE INDEX ix_delegation_grants_tenant_id ON delegation_grants (tenant_id);
CREATE INDEX ix_delegation_grants_trace_id ON delegation_grants (trace_id);
CREATE INDEX ix_events_created_at ON events (created_at);
CREATE INDEX ix_events_event_type ON events (event_type);
CREATE INDEX ix_events_tenant_id ON events (tenant_id);
CREATE INDEX ix_events_tenant_trace_sequence ON events (tenant_id, trace_id, sequence);
CREATE INDEX ix_evidence_objects_namespace ON evidence_objects (namespace);
CREATE INDEX ix_evidence_objects_sha256 ON evidence_objects (sha256);
CREATE INDEX ix_evidence_objects_tenant_id ON evidence_objects (tenant_id);
CREATE INDEX ix_execution_state_updated ON executions (state, updated_at);
CREATE INDEX ix_executions_broker_id ON executions (broker_id);
CREATE INDEX ix_executions_capability_id ON executions (capability_id);
CREATE INDEX ix_executions_decision_id ON executions (decision_id);
CREATE INDEX ix_executions_lease_expires_at ON executions (lease_expires_at);
CREATE INDEX ix_executions_lease_owner ON executions (lease_owner);
CREATE INDEX ix_executions_next_attempt_at ON executions (next_attempt_at);
CREATE INDEX ix_executions_priority ON executions (priority);
CREATE INDEX ix_executions_state ON executions (state);
CREATE INDEX ix_executions_tenant_id ON executions (tenant_id);
CREATE INDEX ix_executions_trace_id ON executions (trace_id);
CREATE INDEX ix_fact_dependencies_child_fact_id ON fact_dependencies (child_fact_id);
CREATE INDEX ix_fact_dependencies_parent_fact_id ON fact_dependencies (parent_fact_id);
CREATE INDEX ix_fact_dependency_parent ON fact_dependencies (parent_fact_id);
CREATE INDEX ix_incidents_severity ON incidents (severity);
CREATE INDEX ix_incidents_status ON incidents (status);
CREATE INDEX ix_incidents_tenant_id ON incidents (tenant_id);
CREATE INDEX ix_incidents_trace_id ON incidents (trace_id);
CREATE INDEX ix_learned_pattern_status ON learned_patterns (codebook, status, occurrence_count);
CREATE INDEX ix_learned_patterns_codebook ON learned_patterns (codebook);
CREATE INDEX ix_learned_patterns_concept_id ON learned_patterns (concept_id);
CREATE INDEX ix_learned_patterns_embedding_space ON learned_patterns (embedding_space);
CREATE INDEX ix_learned_patterns_signature ON learned_patterns (signature);
CREATE INDEX ix_learned_patterns_status ON learned_patterns (status);
CREATE INDEX ix_learned_patterns_trust_scope ON learned_patterns (trust_scope);
CREATE INDEX ix_legal_holds_status ON legal_holds (status);
CREATE INDEX ix_legal_holds_tenant_id ON legal_holds (tenant_id);
CREATE INDEX ix_memory_records_agent_id ON memory_records (agent_id);
CREATE INDEX ix_memory_records_external_id ON memory_records (external_id);
CREATE INDEX ix_memory_records_status ON memory_records (status);
CREATE INDEX ix_memory_records_tenant_id ON memory_records (tenant_id);
CREATE INDEX ix_memory_records_trace_id ON memory_records (trace_id);
CREATE INDEX ix_outbox_messages_aggregate_id ON outbox_messages (aggregate_id);
CREATE INDEX ix_outbox_messages_lease_expires_at ON outbox_messages (lease_expires_at);
CREATE INDEX ix_outbox_messages_lease_owner ON outbox_messages (lease_owner);
CREATE INDEX ix_outbox_messages_priority ON outbox_messages (priority);
CREATE INDEX ix_outbox_messages_status ON outbox_messages (status);
CREATE INDEX ix_outbox_messages_tenant_id ON outbox_messages (tenant_id);
CREATE INDEX ix_policy_bundles_rollout_mode ON policy_bundles (rollout_mode);
CREATE INDEX ix_policy_bundles_tenant_id ON policy_bundles (tenant_id);
CREATE UNIQUE INDEX uq_policy_active_tenant ON policy_bundles (tenant_id) WHERE active = 1;
CREATE INDEX ix_providers_tenant_id ON providers (tenant_id);
CREATE INDEX ix_reference_grant_lookup ON reference_grants (workspace, ref_id);
CREATE INDEX ix_reference_grants_expires_at ON reference_grants (expires_at);
CREATE INDEX ix_reference_grants_owner ON reference_grants (owner);
CREATE INDEX ix_reference_grants_ref_id ON reference_grants (ref_id);
CREATE INDEX ix_reference_grants_tier ON reference_grants (tier);
CREATE INDEX ix_reference_grants_workspace ON reference_grants (workspace);
CREATE INDEX ix_runtime_budgets_scope_id ON runtime_budgets (scope_id);
CREATE INDEX ix_runtime_budgets_tenant_id ON runtime_budgets (tenant_id);
CREATE INDEX ix_state_checkpoint_workspace_created ON state_checkpoints (workspace, created_at);
CREATE INDEX ix_state_checkpoints_payload_hash ON state_checkpoints (payload_hash);
CREATE INDEX ix_state_checkpoints_state_id ON state_checkpoints (state_id);
CREATE INDEX ix_state_checkpoints_workspace ON state_checkpoints (workspace);
CREATE INDEX ix_tenant_key_routes_status ON tenant_key_routes (status);
CREATE INDEX ix_lifecycle_job_delivery ON tenant_lifecycle_jobs (status, available_at, priority);
CREATE INDEX ix_tenant_lifecycle_jobs_available_at ON tenant_lifecycle_jobs (available_at);
CREATE INDEX ix_tenant_lifecycle_jobs_lease_expires_at ON tenant_lifecycle_jobs (lease_expires_at);
CREATE INDEX ix_tenant_lifecycle_jobs_lease_owner ON tenant_lifecycle_jobs (lease_owner);
CREATE INDEX ix_tenant_lifecycle_jobs_status ON tenant_lifecycle_jobs (status);
CREATE INDEX ix_tenant_lifecycle_jobs_tenant_id ON tenant_lifecycle_jobs (tenant_id);
CREATE INDEX ix_tools_tenant_id ON tools (tenant_id);
CREATE INDEX ix_workload_identity_bindings_agent_id ON workload_identity_bindings (agent_id);
CREATE INDEX ix_workload_identity_bindings_status ON workload_identity_bindings (status);
CREATE INDEX ix_workload_identity_bindings_tenant_id ON workload_identity_bindings (tenant_id);
CREATE INDEX ix_workload_identity_bindings_trust_domain ON workload_identity_bindings (trust_domain);
CREATE INDEX ix_a2a_task_authorizations_delegation_grant_id ON a2a_task_authorizations (delegation_grant_id);
CREATE INDEX ix_a2a_task_authorizations_execution_id ON a2a_task_authorizations (execution_id);
CREATE INDEX ix_a2a_task_authorizations_registration_id ON a2a_task_authorizations (registration_id);
CREATE INDEX ix_a2a_task_authorizations_status ON a2a_task_authorizations (status);
CREATE INDEX ix_a2a_task_authorizations_tenant_id ON a2a_task_authorizations (tenant_id);
CREATE INDEX ix_a2a_task_authorizations_trace_id ON a2a_task_authorizations (trace_id);
CREATE INDEX ix_approvals_decision_id ON approvals (decision_id);
CREATE INDEX ix_approvals_status ON approvals (status);
CREATE INDEX ix_approvals_tenant_id ON approvals (tenant_id);
CREATE INDEX ix_approvals_trace_id ON approvals (trace_id);
CREATE INDEX ix_budget_reservations_budget_id ON budget_reservations (budget_id);
CREATE INDEX ix_budget_reservations_status ON budget_reservations (status);
CREATE INDEX ix_budget_reservations_tenant_id ON budget_reservations (tenant_id);
CREATE INDEX ix_budget_reservations_trace_id ON budget_reservations (trace_id);
CREATE INDEX ix_capabilities_agent_id ON capabilities (agent_id);
CREATE INDEX ix_capabilities_decision_id ON capabilities (decision_id);
CREATE INDEX ix_capabilities_tenant_id ON capabilities (tenant_id);
CREATE INDEX ix_capabilities_trace_id ON capabilities (trace_id);
CREATE INDEX ix_pattern_edge_parent ON pattern_edges (parent_pattern_id, position);
CREATE INDEX ix_pattern_edges_child_pattern_id ON pattern_edges (child_pattern_id);
CREATE INDEX ix_pattern_edges_parent_pattern_id ON pattern_edges (parent_pattern_id);
CREATE INDEX ix_pattern_receiver_lookup ON pattern_receiver_metrics (workspace, receiver, model);
CREATE INDEX ix_pattern_receiver_metrics_model ON pattern_receiver_metrics (model);
CREATE INDEX ix_pattern_receiver_metrics_pattern_id ON pattern_receiver_metrics (pattern_id);
CREATE INDEX ix_pattern_receiver_metrics_receiver ON pattern_receiver_metrics (receiver);
CREATE INDEX ix_pattern_receiver_metrics_workspace ON pattern_receiver_metrics (workspace);
CREATE INDEX ix_pattern_validation_evidence_model_identity_hash ON pattern_validation_evidence (model_identity_hash);
CREATE INDEX ix_pattern_validation_evidence_pattern_id ON pattern_validation_evidence (pattern_id);
CREATE INDEX ix_pattern_validation_evidence_receiver ON pattern_validation_evidence (receiver);
CREATE INDEX ix_pattern_validation_evidence_source_hash ON pattern_validation_evidence (source_hash);
CREATE INDEX ix_pattern_validation_evidence_split ON pattern_validation_evidence (split);
CREATE INDEX ix_pattern_validation_evidence_task_family ON pattern_validation_evidence (task_family);
CREATE INDEX ix_pattern_validation_evidence_workspace ON pattern_validation_evidence (workspace);
CREATE INDEX ix_pattern_validation_pattern_split ON pattern_validation_evidence (pattern_id, split, created_at);
CREATE INDEX ix_pattern_validation_receiver_model ON pattern_validation_evidence (workspace, receiver, model_identity_hash);
CREATE INDEX ix_protocol_manifest_versions_registration_id ON protocol_manifest_versions (registration_id);
CREATE INDEX ix_protocol_manifest_versions_tenant_id ON protocol_manifest_versions (tenant_id);
CREATE INDEX ix_reliability_drift ON reliability_windows (workspace, receiver, model_identity_hash, status);
CREATE INDEX ix_reliability_windows_model_identity_hash ON reliability_windows (model_identity_hash);
CREATE INDEX ix_reliability_windows_pattern_id ON reliability_windows (pattern_id);
CREATE INDEX ix_reliability_windows_receiver ON reliability_windows (receiver);
CREATE INDEX ix_reliability_windows_status ON reliability_windows (status);
CREATE INDEX ix_reliability_windows_task_family ON reliability_windows (task_family);
CREATE INDEX ix_reliability_windows_window_start ON reliability_windows (window_start);
CREATE INDEX ix_reliability_windows_workspace ON reliability_windows (workspace);
CREATE INDEX ix_approval_votes_approval_id ON approval_votes (approval_id);
CREATE INDEX ix_approval_votes_tenant_id ON approval_votes (tenant_id);
COMMIT;
