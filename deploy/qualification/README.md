# AIFENCE qualification stack

This stack exercises the RC3 topology with PostgreSQL, three API replicas, three independent dispatch workers, MinIO object storage, ClamAV, and a controlled HTTP CONNECT egress proxy.

Run `deploy/qualification/run.sh`. The stack intentionally uses the staging configuration profile and local envelope/signing keys so it can run without a cloud account. The release gates for a managed KMS/HSM, SPIFFE attestation, public-trust TLS, external audit webhook, backup restoration, Kubernetes disruption, and independent penetration testing remain separate environment-specific gates; they cannot be simulated credibly by a local Compose stack.

The PostgreSQL workflow in `.github/workflows/qualification.yml` independently validates forced RLS, cross-tenant denial, append-only audit triggers, concurrent budget reservation, and concurrent `SKIP LOCKED` dispatcher claims under a non-superuser application role.
