<!--
Pack-Version: 4.0.0
Schema-Version: 3
Module: SECURITY
Module-Version: 1
Last-Updated: 2026-08-09
-->

# Security Strategy, Protocols & High-Quality Standards
<!-- id: security.security-strategy-protocols-and-high-quality-standards -->

Version: 2026-08-09  
Status: Enterprise security baseline and operational security standard  
Scope: Websites, applications, SaaS, APIs, cloud infrastructure, endpoints, identity, data, software development, vendors, AI systems, operations, incident response, business continuity, and security governance

> This document is a defensive security and risk-management framework. It must be adapted to the organization's actual systems, threat model, legal obligations, contracts, data classifications, and industry-specific requirements.

---

# 1. Purpose
<!-- id: security.1-purpose -->

This standard defines a modern security operating model intended to keep systems:

- confidential
- integral
- available
- resilient
- auditable
- recoverable
- least-privileged
- securely configured
- continuously monitored
- safely changeable

Security MUST be designed into architecture and operations rather than added only after deployment.

---

# 2. Reference Framework
<!-- id: security.2-reference-framework -->

The security program SHOULD align its control catalog and governance to recognized current standards.

Primary references:

- NIST Cybersecurity Framework 2.0
- CIS Critical Security Controls v8.1
- OWASP Application Security Verification Standard 5.0.0
- OWASP Top 10:2025
- OWASP SAMM
- NIST Secure Software Development Framework
- applicable regulatory, contractual, and sector-specific controls

Current official reference pages:

- NIST CSF 2.0: https://www.nist.gov/cyberframework
- CIS Controls v8.1: https://www.cisecurity.org/controls/v8-1
- OWASP ASVS: https://owasp.org/www-project-application-security-verification-standard/
- OWASP Top 10: https://owasp.org/www-project-top-ten/
- OWASP SAMM: https://owasp.org/www-project-samm/
- NIST SSDF: https://csrc.nist.gov/Projects/ssdf

---

# 3. Security Functions
<!-- id: security.3-security-functions -->

The security program MUST address the six NIST CSF 2.0 functions:

- Govern
- Identify
- Protect
- Detect
- Respond
- Recover

No function should operate independently from the others.

---

# 4. Security Principles
<!-- id: security.4-security-principles -->

All systems SHOULD follow:

- least privilege
- deny by default
- secure by default
- defense in depth
- zero-trust assumptions where appropriate
- separation of duties
- minimized attack surface
- minimized data collection
- explicit trust boundaries
- strong identity
- secure failure
- auditable actions
- recoverability
- continuous verification
- progressive risk reduction

---

# 5. Governance Standard
<!-- id: security.5-governance-standard -->

Security governance MUST define:

- executive accountability
- security owner
- risk owners
- control owners
- system owners
- data owners
- incident authority
- exception authority
- audit responsibility
- reporting cadence

---

# 6. Security Policy Hierarchy
<!-- id: security.6-security-policy-hierarchy -->

Recommended hierarchy:

```text
Security Policy
  Security Standards
    Security Procedures
      Technical Baselines
        Runbooks
          Evidence
```

Policies define intent.

Standards define required outcomes.

Procedures define how work is performed.

Baselines define approved technical settings.

Runbooks define repeatable operational actions.

Evidence proves execution.

---

# 7. Risk Management Standard
<!-- id: security.7-risk-management-standard -->

Security decisions MUST be risk-based.

Each material risk SHOULD document:

- asset
- threat
- vulnerability
- likelihood
- impact
- existing controls
- residual risk
- owner
- mitigation
- acceptance authority
- review date

---

# 8. Risk Acceptance Standard
<!-- id: security.8-risk-acceptance-standard -->

Residual security risk MUST NOT be silently accepted.

Risk acceptance SHOULD include:

- written justification
- affected systems
- business impact
- compensating controls
- expiration date
- accountable approver

Permanent risk exceptions SHOULD be avoided.

---

# 9. Asset Inventory Standard
<!-- id: security.9-asset-inventory-standard -->

Maintain authoritative inventory for:

- endpoints
- servers
- virtual machines
- containers
- network devices
- cloud resources
- SaaS
- applications
- APIs
- domains
- certificates
- source repositories
- databases
- data stores
- AI models/services
- third-party integrations

Unknown assets SHOULD be treated as unmanaged risk.

---

# 10. Software Inventory Standard
<!-- id: security.10-software-inventory-standard -->

Maintain inventory of:

- operating systems
- applications
- packages
- libraries
- container images
- browser extensions
- SaaS applications
- build tools
- CI/CD integrations

Unauthorized or unsupported software SHOULD be removed or isolated.

---

# 11. Ownership Standard
<!-- id: security.11-ownership-standard -->

Every production asset MUST have:

- owner
- business purpose
- environment
- sensitivity
- lifecycle status
- support status

---

# 12. Data Classification Standard
<!-- id: security.12-data-classification-standard -->

Define a simple classification model.

Example:

```text
Public
Internal
Confidential
Restricted
```

Classification SHOULD control:

- access
- encryption
- retention
- logging
- sharing
- backup
- incident severity
- vendor handling

---

# 13. Data Inventory Standard
<!-- id: security.13-data-inventory-standard -->

Maintain a data inventory that identifies:

- data category
- source
- owner
- systems
- sensitivity
- recipients
- retention
- legal basis where applicable
- deletion process

---

# 14. Data Minimization Standard
<!-- id: security.14-data-minimization-standard -->

Collect and retain only data necessary for a documented purpose.

Do not collect sensitive data merely because it may be useful later.

---

# 15. Identity Standard
<!-- id: security.15-identity-standard -->

Every human and machine identity MUST be uniquely attributable.

Shared credentials SHOULD be prohibited except where technically unavoidable and controlled.

---

# 16. Authentication Standard
<!-- id: security.16-authentication-standard -->

Sensitive systems SHOULD use strong authentication.

Baseline:

- MFA
- phishing-resistant MFA for privileged/high-risk access where practical
- secure credential recovery
- rate limiting
- suspicious-login detection
- session controls

---

# 17. Password Standard
<!-- id: security.17-password-standard -->

When passwords are used:

- allow long passwords
- support password managers
- block known compromised passwords where practical
- do not require arbitrary frequent rotation without risk indication
- store passwords using modern password hashing
- never log plaintext passwords

---

# 18. Privileged Access Standard
<!-- id: security.18-privileged-access-standard -->

Privileged access MUST be:

- minimized
- separately identifiable
- MFA-protected
- logged
- reviewed
- time-bounded where practical

Administrative accounts SHOULD NOT be used for ordinary work.

---

# 19. Least Privilege Standard
<!-- id: security.19-least-privilege-standard -->

Users, services, applications, and workloads SHOULD receive only permissions required for their current function.

Access SHOULD be removed when no longer necessary.

---

# 20. Joiner-Mover-Leaver Protocol
<!-- id: security.20-joiner-mover-leaver-protocol -->

## Joiner

- verify identity
- provision approved role
- require MFA
- provide security training
- record access

## Mover

- review existing permissions
- remove obsolete access
- grant new approved access

## Leaver

- disable access promptly
- revoke active sessions/tokens
- recover assets
- transfer ownership
- preserve required records

---

# 21. Access Review Standard
<!-- id: security.21-access-review-standard -->

Review access periodically.

High-risk access SHOULD be reviewed more frequently.

Review:

- admins
- production access
- customer data access
- financial access
- security tooling
- source code
- cloud consoles
- secrets

---

# 22. Service Account Standard
<!-- id: security.22-service-account-standard -->

Service accounts MUST have:

- defined owner
- limited permissions
- no interactive login unless required
- rotated credentials or workload identity
- monitored usage
- lifecycle controls

---

# 23. Secrets Management Standard
<!-- id: security.23-secrets-management-standard -->

Secrets MUST NOT be stored in:

- source code
- public repositories
- screenshots
- tickets
- chat logs
- client-side code
- plaintext configuration

Use managed secret storage.

---

# 24. Secret Rotation Protocol
<!-- id: security.24-secret-rotation-protocol -->

Rotate secrets:

- on suspected exposure
- on personnel/offboarding events where necessary
- when a vendor requires rotation
- at defined risk-based intervals
- after environment cloning where exposure is possible

---

# 25. Cryptography Standard
<!-- id: security.25-cryptography-standard -->

Use modern, widely reviewed cryptographic algorithms and libraries.

Do not design custom cryptographic protocols without expert review.

---

# 26. Encryption in Transit Standard
<!-- id: security.26-encryption-in-transit-standard -->

Sensitive data SHOULD be encrypted in transit.

Public web services SHOULD use current TLS configurations.

Plaintext management protocols SHOULD be disabled.

---

# 27. Encryption at Rest Standard
<!-- id: security.27-encryption-at-rest-standard -->

Restricted or sensitive data SHOULD be encrypted at rest where risk warrants it.

Key access SHOULD be separated from data access where practical.

---

# 28. Key Management Standard
<!-- id: security.28-key-management-standard -->

Cryptographic keys SHOULD have:

- owner
- purpose
- rotation
- access policy
- backup/recovery
- revocation
- audit logging

---

# 29. Certificate Management Standard
<!-- id: security.29-certificate-management-standard -->

Maintain inventory and automated renewal where practical for:

- TLS certificates
- signing certificates
- client certificates
- internal PKI

Expired certificates SHOULD be prevented through monitoring.

---

# 30. Endpoint Security Standard
<!-- id: security.30-endpoint-security-standard -->

Managed endpoints SHOULD include:

- supported OS
- patching
- disk encryption
- screen lock
- EDR/anti-malware where appropriate
- local firewall
- secure configuration
- device inventory
- remote wipe where appropriate

---

# 31. Mobile Device Standard
<!-- id: security.31-mobile-device-standard -->

Mobile devices accessing sensitive systems SHOULD use:

- device encryption
- supported OS versions
- screen lock
- managed applications where appropriate
- remote revoke/wipe
- limited local storage

---

# 32. Server Security Standard
<!-- id: security.32-server-security-standard -->

Servers SHOULD:

- use hardened images
- minimize installed services
- disable unused ports
- run supported software
- use centralized logging
- use monitored privileged access
- receive timely patches

---

# 33. Secure Configuration Standard
<!-- id: security.33-secure-configuration-standard -->

Create hardened baselines for:

- operating systems
- databases
- cloud services
- browsers
- network devices
- containers
- identity platforms

Configuration drift SHOULD be detectable.

---

# 34. Patch Management Standard
<!-- id: security.34-patch-management-standard -->

Define patch SLAs by severity and exposure.

Emergency actively exploited vulnerabilities SHOULD receive accelerated remediation.

Unpatchable systems require compensating controls and risk acceptance.

---

# 35. Vulnerability Management Standard
<!-- id: security.35-vulnerability-management-standard -->

The vulnerability program SHOULD include:

1. discovery
2. validation
3. prioritization
4. assignment
5. remediation
6. verification
7. exception handling
8. reporting

---

# 36. Vulnerability Prioritization Standard
<!-- id: security.36-vulnerability-prioritization-standard -->

Prioritize using:

- exploitability
- known exploitation
- internet exposure
- asset criticality
- privilege required
- data sensitivity
- reachable attack paths
- compensating controls

Do not prioritize solely by raw CVSS score.

---

# 37. Vulnerability Scanning Standard
<!-- id: security.37-vulnerability-scanning-standard -->

Use appropriate scanning for:

- infrastructure
- cloud
- applications
- dependencies
- containers
- endpoints
- external attack surface

Scanning MUST be authorized.

---

# 38. Penetration Testing Standard
<!-- id: security.38-penetration-testing-standard -->

Penetration tests SHOULD be conducted:

- before major high-risk launches
- periodically for critical systems
- after major architecture changes
- when contractual/regulatory obligations require

Scope and rules of engagement MUST be documented.

---

# 39. Application Security Standard
<!-- id: security.39-application-security-standard -->

Web applications SHOULD use OWASP ASVS 5.0.0 as a security requirements and verification baseline appropriate to risk.

---

# 40. Secure SDLC Standard
<!-- id: security.40-secure-sdlc-standard -->

Security SHOULD exist throughout:

```text
Plan
Design
Build
Test
Release
Operate
Retire
```

---

# 41. Security Requirements Standard
<!-- id: security.41-security-requirements-standard -->

High-risk features MUST define security requirements before implementation.

Examples:

- authentication
- authorization
- encryption
- logging
- abuse controls
- data retention
- privacy
- fraud controls

---

# 42. Threat Modeling Standard
<!-- id: security.42-threat-modeling-standard -->

Threat model material features that involve:

- authentication
- sensitive data
- money
- privileged operations
- external integrations
- AI agents
- file upload
- multi-tenant boundaries
- admin functions

---

# 43. Threat Model Structure
<!-- id: security.43-threat-model-structure -->

Document:

- assets
- actors
- trust boundaries
- entry points
- data flows
- threats
- mitigations
- residual risks

---

# 44. Secure Coding Standard
<!-- id: security.44-secure-coding-standard -->

Developers SHOULD follow secure coding requirements covering:

- input validation
- output encoding
- access control
- authentication
- session management
- secrets
- cryptography
- file handling
- error handling
- logging
- dependency safety

---

# 45. Input Validation Standard
<!-- id: security.45-input-validation-standard -->

Validate untrusted input using allow-lists or strict schemas where practical.

Server-side validation is mandatory for security-sensitive enforcement.

---

# 46. Injection Prevention Standard
<!-- id: security.46-injection-prevention-standard -->

Use parameterized APIs and context-appropriate encoding.

Do not construct executable commands or queries from untrusted input through string concatenation.

---

# 47. Output Encoding Standard
<!-- id: security.47-output-encoding-standard -->

Encode output according to its destination context.

Examples:

- HTML
- attribute
- URL
- JavaScript
- SQL
- shell

---

# 48. Access Control Standard
<!-- id: security.48-access-control-standard -->

Authorization MUST be enforced server-side.

Do not rely on hidden UI controls for authorization.

---

# 49. Object-Level Authorization Standard
<!-- id: security.49-object-level-authorization-standard -->

Every object access SHOULD verify that the acting identity is authorized for the requested resource and action.

---

# 50. Tenant Isolation Standard
<!-- id: security.50-tenant-isolation-standard -->

Multi-tenant systems MUST test tenant boundaries.

Tenant identifiers supplied by clients MUST NOT be trusted as authorization proof.

---

# 51. Session Security Standard
<!-- id: security.51-session-security-standard -->

Sessions SHOULD use:

- secure random identifiers
- secure cookies
- HttpOnly
- SameSite
- TLS
- expiration
- logout invalidation
- reauthentication for sensitive actions

---

# 52. CSRF Standard
<!-- id: security.52-csrf-standard -->

State-changing browser requests MUST use appropriate CSRF defenses when cookie-based authentication can make them vulnerable.

---

# 53. XSS Standard
<!-- id: security.53-xss-standard -->

Prevent XSS with:

- framework-safe rendering
- output encoding
- input handling
- CSP where appropriate
- avoidance of unsafe DOM APIs

---

# 54. Content Security Policy Standard
<!-- id: security.54-content-security-policy-standard -->

Public web applications SHOULD evaluate a CSP.

Prefer:

- explicit sources
- nonces/hashes
- gradual enforcement
- reporting during rollout

---

# 55. HTTP Security Header Standard
<!-- id: security.55-http-security-header-standard -->

Evaluate and configure:

- HSTS
- CSP
- frame protections
- content-type protections
- referrer policy
- permissions policy

---

# 56. File Upload Security Standard
<!-- id: security.56-file-upload-security-standard -->

File uploads SHOULD validate:

- size
- type
- content
- extension
- storage path
- authorization

Uploaded content SHOULD be isolated from application execution.

---

# 57. SSRF Standard
<!-- id: security.57-ssrf-standard -->

Systems making server-side outbound requests SHOULD restrict:

- protocols
- destinations
- redirects
- private/internal address ranges
- metadata endpoints

where relevant.

---

# 58. Deserialization Standard
<!-- id: security.58-deserialization-standard -->

Do not deserialize untrusted data using unsafe native object mechanisms.

Prefer explicit data schemas.

---

# 59. Error Disclosure Standard
<!-- id: security.59-error-disclosure-standard -->

Do not expose:

- stack traces
- secrets
- internal paths
- SQL
- private hostnames
- cloud metadata

to end users.

---

# 60. API Security Standard
<!-- id: security.60-api-security-standard -->

APIs SHOULD implement:

- strong authentication
- authorization
- schema validation
- rate limiting
- abuse prevention
- secure error handling
- versioning
- logging
- inventory

---

# 61. API Inventory Standard
<!-- id: security.61-api-inventory-standard -->

Every production API SHOULD be inventoried with:

- owner
- version
- authentication model
- data sensitivity
- consumers
- lifecycle status

---

# 62. Rate Limiting Standard
<!-- id: security.62-rate-limiting-standard -->

Apply rate limits based on:

- identity
- endpoint
- cost
- abuse risk
- tenant
- IP where useful

Avoid one global limit for all actions.

---

# 63. Abuse Prevention Standard
<!-- id: security.63-abuse-prevention-standard -->

Security design SHOULD account for legitimate functionality being abused.

Examples:

- spam
- scraping
- enumeration
- automated account creation
- invitation abuse
- credential attacks
- resource exhaustion

---

# 64. Bot Management Standard
<!-- id: security.64-bot-management-standard -->

Use risk-based bot defenses that avoid unnecessary harm to accessibility and legitimate automation.

---

# 65. Dependency Security Standard
<!-- id: security.65-dependency-security-standard -->

Software dependencies SHOULD be:

- inventoried
- version-pinned
- scanned
- updated
- license-reviewed
- removed when unused

---

# 66. SBOM Standard
<!-- id: security.66-sbom-standard -->

Critical software SHOULD support a software bill of materials where appropriate.

---

# 67. Package Integrity Standard
<!-- id: security.67-package-integrity-standard -->

Use lockfiles and verified registries.

Protect package-manager credentials and publishing rights.

---

# 68. Supply Chain Security Standard
<!-- id: security.68-supply-chain-security-standard -->

Secure:

- repositories
- CI/CD
- build runners
- package registries
- signing keys
- deployment credentials
- third-party actions/plugins

---

# 69. Source Repository Standard
<!-- id: security.69-source-repository-standard -->

Repositories SHOULD require:

- MFA
- branch protections
- reviewed changes
- least privilege
- secret scanning
- audit logging

---

# 70. Branch Protection Standard
<!-- id: security.70-branch-protection-standard -->

Critical branches SHOULD restrict direct pushes.

Require appropriate:

- review
- CI
- status checks
- signed changes where risk warrants

---

# 71. CI/CD Security Standard
<!-- id: security.71-ci-cd-security-standard -->

CI/CD SHOULD:

- use minimal permissions
- isolate secrets
- pin third-party actions where practical
- scan dependencies
- preserve logs
- restrict production deployment

---

# 72. Build Integrity Standard
<!-- id: security.72-build-integrity-standard -->

Production artifacts SHOULD be reproducible or traceable to:

- source revision
- build
- dependencies
- pipeline
- approver

---

# 73. Artifact Signing Standard
<!-- id: security.73-artifact-signing-standard -->

High-assurance environments SHOULD evaluate signed artifacts and verified provenance.

---

# 74. Deployment Standard
<!-- id: security.74-deployment-standard -->

Production deployments SHOULD use:

- controlled automation
- approval appropriate to risk
- rollback capability
- audit logs
- health checks

---

# 75. Production Access Standard
<!-- id: security.75-production-access-standard -->

Production access MUST be limited to authorized personnel and services.

Direct manual changes SHOULD be minimized.

---

# 76. Cloud Security Standard
<!-- id: security.76-cloud-security-standard -->

Cloud environments SHOULD implement:

- organization/account hierarchy
- IAM boundaries
- centralized logging
- network controls
- encryption
- asset inventory
- secure defaults
- configuration monitoring
- budget/abuse alerts

---

# 77. Cloud Root Account Standard
<!-- id: security.77-cloud-root-account-standard -->

Cloud root/super-admin accounts SHOULD be:

- strongly protected
- rarely used
- MFA-enabled
- monitored
- recovery-tested

---

# 78. Infrastructure-as-Code Standard
<!-- id: security.78-infrastructure-as-code-standard -->

Infrastructure SHOULD be defined as code where practical.

IaC SHOULD receive:

- review
- scanning
- version control
- change history

---

# 79. Container Security Standard
<!-- id: security.79-container-security-standard -->

Containers SHOULD:

- use minimal trusted base images
- run as non-root where possible
- remove unnecessary tools
- scan dependencies
- use immutable deployment
- avoid embedded secrets

---

# 80. Kubernetes Security Standard
<!-- id: security.80-kubernetes-security-standard -->

Kubernetes environments SHOULD control:

- RBAC
- network policies
- admission
- secrets
- pod security
- image provenance
- audit logging
- control-plane access

---

# 81. Network Security Standard
<!-- id: security.81-network-security-standard -->

Networks SHOULD:

- minimize exposed services
- segment high-risk systems
- control east-west access
- log critical traffic
- restrict management interfaces

---

# 82. Firewall Standard
<!-- id: security.82-firewall-standard -->

Firewall rules SHOULD be:

- least-permissive
- documented
- owned
- reviewed
- removed when obsolete

---

# 83. Remote Access Standard
<!-- id: security.83-remote-access-standard -->

Remote administrative access SHOULD use:

- strong authentication
- managed endpoints
- encrypted channels
- limited source paths
- audit logging

---

# 84. DNS Security Standard
<!-- id: security.84-dns-security-standard -->

Protect:

- registrar accounts
- DNS administration
- zone changes
- DNSSEC where appropriate
- monitoring

---

# 85. Domain Security Standard
<!-- id: security.85-domain-security-standard -->

Critical domains SHOULD use:

- registrar MFA
- registry lock where justified
- restricted administrators
- expiration monitoring
- change alerts

---

# 86. Email Security Standard
<!-- id: security.86-email-security-standard -->

Organizations SHOULD configure appropriate:

- SPF
- DKIM
- DMARC
- anti-phishing
- malware filtering
- account protection

---

# 87. SaaS Security Standard
<!-- id: security.87-saas-security-standard -->

SaaS applications SHOULD be inventoried and reviewed for:

- SSO
- MFA
- admin roles
- data access
- integrations
- retention
- offboarding
- audit logs

---

# 88. Shadow IT Standard
<!-- id: security.88-shadow-it-standard -->

Unauthorized services SHOULD be discovered and either:

- approved
- migrated
- restricted
- removed

---

# 89. Logging Standard
<!-- id: security.89-logging-standard -->

Security-relevant systems SHOULD produce useful logs.

Log:

- authentication
- authorization failures
- privileged actions
- administrative changes
- sensitive data exports
- security configuration changes
- critical transactions
- alerts

---

# 90. Log Protection Standard
<!-- id: security.90-log-protection-standard -->

Logs SHOULD be:

- access-controlled
- integrity-protected
- time-synchronized
- retained by policy
- searchable

---

# 91. Sensitive Logging Standard
<!-- id: security.91-sensitive-logging-standard -->

Do not log unnecessarily:

- passwords
- session tokens
- API keys
- private keys
- payment card secrets
- highly sensitive personal data

---

# 92. Detection Standard
<!-- id: security.92-detection-standard -->

Detection engineering SHOULD define:

- threat
- telemetry
- detection logic
- severity
- triage
- false-positive handling
- owner

---

# 93. Security Monitoring Standard
<!-- id: security.93-security-monitoring-standard -->

Monitor:

- identity
- endpoints
- cloud
- network
- applications
- data
- critical SaaS
- external exposure

according to risk.

---

# 94. Alert Standard
<!-- id: security.94-alert-standard -->

Alerts SHOULD be actionable.

Every high-priority alert SHOULD identify:

- affected asset
- reason
- evidence
- severity
- owner
- next action

---

# 95. Incident Response Standard
<!-- id: security.95-incident-response-standard -->

Maintain a documented incident response program.

Phases:

```text
Prepare
Detect
Analyze
Contain
Eradicate
Recover
Learn
```

---

# 96. Incident Severity Standard
<!-- id: security.96-incident-severity-standard -->

Define severity levels.

Example:

```text
SEV-1 Critical
SEV-2 High
SEV-3 Moderate
SEV-4 Low
```

Criteria SHOULD include:

- safety
- data exposure
- customer impact
- financial impact
- privilege
- spread
- regulatory impact

---

# 97. Incident Commander Standard
<!-- id: security.97-incident-commander-standard -->

Major incidents SHOULD have one incident commander responsible for coordination.

Technical investigation and executive decision-making MAY remain separate.

---

# 98. Incident Communication Standard
<!-- id: security.98-incident-communication-standard -->

Incident communication SHOULD define:

- internal channel
- executive updates
- customer communication
- legal/privacy escalation
- regulator notification
- public relations
- status-page use

---

# 99. Evidence Preservation Standard
<!-- id: security.99-evidence-preservation-standard -->

During incidents, preserve relevant:

- logs
- disk/memory evidence
- cloud audit trails
- affected files
- timelines
- tickets
- decisions

Do not destroy evidence through uncontrolled cleanup.

---

# 100. Containment Standard
<!-- id: security.100-containment-standard -->

Containment SHOULD minimize damage while preserving essential business operation and evidence.

---

# 101. Credential Compromise Runbook
<!-- id: security.101-credential-compromise-runbook -->

1. identify affected account
2. disable or restrict account
3. revoke active sessions
4. rotate credentials/tokens
5. review authentication logs
6. inspect privilege changes
7. assess lateral movement
8. notify affected owners
9. restore access securely
10. document lessons

---

# 102. Malware Runbook
<!-- id: security.102-malware-runbook -->

1. isolate affected host
2. preserve evidence
3. identify malware/processes
4. determine scope
5. block indicators
6. remove or reimage
7. rotate exposed credentials
8. verify clean state
9. monitor recurrence
10. document root cause

---

# 103. Data Exposure Runbook
<!-- id: security.103-data-exposure-runbook -->

1. stop ongoing exposure
2. preserve evidence
3. identify data
4. identify affected people/accounts
5. determine access duration
6. determine attacker/access path
7. engage privacy/legal
8. remediate
9. evaluate notifications
10. document timeline

---

# 104. Vulnerability Disclosure Protocol
<!-- id: security.104-vulnerability-disclosure-protocol -->

Maintain a reporting channel for security researchers.

Define:

- scope
- reporting method
- expected behavior
- prohibited testing
- response process
- acknowledgment
- remediation tracking

---

# 105. Security Incident Postmortem Standard
<!-- id: security.105-security-incident-postmortem-standard -->

Postmortems SHOULD be blameless and action-oriented.

Document:

- timeline
- root causes
- contributing factors
- detection gaps
- control gaps
- actions
- owners
- deadlines

---

# 106. Backup Standard
<!-- id: security.106-backup-standard -->

Critical systems SHOULD have backups appropriate to recovery requirements.

Backups SHOULD be:

- automated
- encrypted where necessary
- access-controlled
- monitored
- tested

---

# 107. Backup Isolation Standard
<!-- id: security.107-backup-isolation-standard -->

Critical backups SHOULD resist compromise of production credentials.

Consider immutable/offline protection for high-risk systems.

---

# 108. Recovery Testing Standard
<!-- id: security.108-recovery-testing-standard -->

Backups are not considered reliable until restoration is tested.

---

# 109. RTO/RPO Standard
<!-- id: security.109-rto-rpo-standard -->

Critical services SHOULD define:

- Recovery Time Objective
- Recovery Point Objective

Business owners SHOULD approve them.

---

# 110. Business Continuity Standard
<!-- id: security.110-business-continuity-standard -->

Business continuity SHOULD address:

- loss of facility
- cloud outage
- vendor outage
- identity outage
- network outage
- ransomware
- staff unavailability
- regional disruption

---

# 111. Disaster Recovery Standard
<!-- id: security.111-disaster-recovery-standard -->

Disaster recovery SHOULD include:

- architecture
- data restoration
- infrastructure restoration
- access
- dependencies
- testing
- communication

---

# 112. Vendor Security Standard
<!-- id: security.112-vendor-security-standard -->

Before vendors receive sensitive access or data:

- classify risk
- assess controls
- execute contracts
- define incident notification
- confirm data handling
- confirm subprocessor controls
- plan termination

---

# 113. Vendor Risk Tier Standard
<!-- id: security.113-vendor-risk-tier-standard -->

Example:

```text
Tier 1 Critical
Tier 2 High
Tier 3 Moderate
Tier 4 Low
```

Risk tier SHOULD determine assessment depth.

---

# 114. Vendor Offboarding Standard
<!-- id: security.114-vendor-offboarding-standard -->

When a vendor relationship ends:

- revoke access
- rotate shared secrets
- remove integrations
- recover/delete data
- preserve required records
- update inventory

---

# 115. Security Awareness Standard
<!-- id: security.115-security-awareness-standard -->

All personnel SHOULD receive role-appropriate security education.

Baseline topics:

- phishing
- credentials
- MFA
- sensitive data
- safe sharing
- incident reporting
- device security
- social engineering

---

# 116. Role-Based Security Training Standard
<!-- id: security.116-role-based-security-training-standard -->

Additional training SHOULD apply to:

- developers
- administrators
- finance
- customer support
- executives
- security staff
- data teams

---

# 117. Phishing Resistance Standard
<!-- id: security.117-phishing-resistance-standard -->

Security awareness SHOULD prioritize behavior and reporting over punitive trick campaigns.

---

# 118. Physical Security Standard
<!-- id: security.118-physical-security-standard -->

Physical controls SHOULD protect:

- offices
- server/network rooms
- devices
- media
- visitor access
- restricted areas

---

# 119. Media Disposal Standard
<!-- id: security.119-media-disposal-standard -->

Sensitive media SHOULD be securely erased or destroyed before disposal or reuse.

---

# 120. Privacy-Security Integration Standard
<!-- id: security.120-privacy-security-integration-standard -->

Security and privacy teams SHOULD coordinate on:

- data inventory
- access
- retention
- incidents
- vendors
- sensitive-data architecture
- logging

---

# 121. Payment Security Standard
<!-- id: security.121-payment-security-standard -->

Systems handling payment cards SHOULD minimize card data exposure and use appropriate PCI-compliant providers and architecture where applicable.

---

# 122. Financial Operation Security Standard
<!-- id: security.122-financial-operation-security-standard -->

High-risk financial actions SHOULD use:

- approval controls
- transaction limits
- anomaly detection
- callback/out-of-band verification where appropriate
- audit logs

---

# 123. Fraud Security Standard
<!-- id: security.123-fraud-security-standard -->

Fraud controls SHOULD be separate from but coordinated with cybersecurity.

Monitor:

- account takeover
- fake accounts
- payment abuse
- promotion abuse
- refund abuse
- identity fraud

---

# 124. AI Security Standard
<!-- id: security.124-ai-security-standard -->

AI-enabled systems SHOULD address:

- prompt injection
- data leakage
- excessive agency
- insecure tool use
- unauthorized actions
- untrusted retrieved content
- model/provider risk
- output validation
- auditability

---

# 125. AI Tool Permission Standard
<!-- id: security.125-ai-tool-permission-standard -->

AI agents SHOULD receive the minimum tool permissions required.

High-impact tools SHOULD use:

- explicit authorization
- confirmation
- policy enforcement
- logging
- rate/transaction limits

---

# 126. AI Data Standard
<!-- id: security.126-ai-data-standard -->

Before sending data to an AI provider, determine:

- sensitivity
- purpose
- retention
- training use
- region
- contract terms
- user disclosure
- access

---

# 127. AI Output Standard
<!-- id: security.127-ai-output-standard -->

AI output MUST NOT be treated as trusted input to privileged systems without validation.

---

# 128. AI Prompt Injection Standard
<!-- id: security.128-ai-prompt-injection-standard -->

Treat external documents, websites, messages, and retrieved content as untrusted instructions.

System policy and user authorization MUST remain higher priority than retrieved content.

---

# 129. AI Agent Audit Standard
<!-- id: security.129-ai-agent-audit-standard -->

Agent actions SHOULD log:

- initiating user
- model/system
- requested task
- tools used
- important inputs
- action result
- approvals
- failures

subject to privacy requirements.

---

# 130. Security Metrics Standard
<!-- id: security.130-security-metrics-standard -->

Measure security outcomes, not only activity.

Useful metrics:

- critical asset coverage
- MFA coverage
- privileged access review completion
- patch SLA compliance
- known-exploited vulnerability exposure
- mean time to detect
- mean time to contain
- recovery-test success
- phishing/reporting behavior
- secure-development control coverage

---

# 131. Security Dashboard Standard
<!-- id: security.131-security-dashboard-standard -->

Executive dashboards SHOULD communicate:

- material risks
- incidents
- control health
- overdue remediation
- critical dependencies
- trend

Avoid vanity metrics without risk context.

---

# 132. Security Exception Standard
<!-- id: security.132-security-exception-standard -->

Exceptions SHOULD include:

- requirement
- reason
- risk
- compensating control
- owner
- expiration
- approver

---

# 133. Security Evidence Standard
<!-- id: security.133-security-evidence-standard -->

Controls SHOULD generate evidence.

Examples:

- access review logs
- patch reports
- scan reports
- backup tests
- incident exercises
- security training completion
- code review
- deployment records

---

# 134. Audit Readiness Standard
<!-- id: security.134-audit-readiness-standard -->

Security evidence SHOULD be:

- attributable
- dated
- reproducible
- access-controlled
- retained according to policy

---

# 135. Security Testing Cadence Standard
<!-- id: security.135-security-testing-cadence-standard -->

Define cadence by risk for:

- vulnerability scanning
- access reviews
- backup restore tests
- incident exercises
- penetration testing
- dependency review
- vendor review

---

# 136. Tabletop Exercise Standard
<!-- id: security.136-tabletop-exercise-standard -->

Critical teams SHOULD perform incident tabletop exercises.

Scenarios MAY include:

- ransomware
- data breach
- cloud compromise
- identity provider outage
- vendor compromise
- malicious insider
- destructive AI-agent action

---

# 137. Secure Change Management Standard
<!-- id: security.137-secure-change-management-standard -->

Production security-impacting changes SHOULD be:

- reviewed
- tested
- logged
- reversible where practical

---

# 138. Emergency Change Standard
<!-- id: security.138-emergency-change-standard -->

Emergency changes MAY bypass ordinary workflow only through documented emergency procedure.

Review them after stabilization.

---

# 139. Security Architecture Review Standard
<!-- id: security.139-security-architecture-review-standard -->

Security architecture review SHOULD be triggered by:

- new authentication
- new sensitive data
- new external exposure
- major cloud change
- new vendor
- AI agents/tools
- payment changes
- multi-tenant architecture
- high-impact integrations

---

# 140. Security Design Review Checklist
<!-- id: security.140-security-design-review-checklist -->

- [ ] assets identified
- [ ] trust boundaries identified
- [ ] authentication defined
- [ ] authorization defined
- [ ] sensitive data identified
- [ ] encryption defined
- [ ] logging defined
- [ ] abuse cases considered
- [ ] failure modes considered
- [ ] recovery considered
- [ ] dependencies reviewed

---

# 141. Secure Release Checklist
<!-- id: security.141-secure-release-checklist -->

- [ ] code reviewed
- [ ] tests pass
- [ ] security tests pass
- [ ] dependencies scanned
- [ ] secrets scan clean
- [ ] authorization tested
- [ ] configuration reviewed
- [ ] logging enabled
- [ ] rollback prepared
- [ ] documentation updated

---

# 142. Incident Readiness Checklist
<!-- id: security.142-incident-readiness-checklist -->

- [ ] on-call ownership
- [ ] escalation contacts
- [ ] incident channel
- [ ] severity matrix
- [ ] legal/privacy contacts
- [ ] backup access
- [ ] forensic logging
- [ ] communication templates
- [ ] tabletop performed

---

# 143. Identity Checklist
<!-- id: security.143-identity-checklist -->

- [ ] SSO where appropriate
- [ ] MFA
- [ ] least privilege
- [ ] admin separation
- [ ] joiner/mover/leaver
- [ ] access reviews
- [ ] session revocation
- [ ] service account ownership

---

# 144. Application Security Checklist
<!-- id: security.144-application-security-checklist -->

- [ ] threat model
- [ ] ASVS requirements selected
- [ ] server-side authorization
- [ ] input validation
- [ ] injection prevention
- [ ] session security
- [ ] CSRF controls
- [ ] secure file upload
- [ ] rate limits
- [ ] dependency scanning
- [ ] security headers
- [ ] safe errors
- [ ] audit logging

---

# 145. Cloud Security Checklist
<!-- id: security.145-cloud-security-checklist -->

- [ ] account hierarchy
- [ ] root protection
- [ ] IAM least privilege
- [ ] centralized logs
- [ ] encryption
- [ ] network boundaries
- [ ] asset inventory
- [ ] configuration monitoring
- [ ] backup
- [ ] incident access

---

# 146. Vendor Security Checklist
<!-- id: security.146-vendor-security-checklist -->

- [ ] vendor owner
- [ ] risk tier
- [ ] security assessment
- [ ] privacy/data review
- [ ] contract
- [ ] breach notification
- [ ] subprocessors
- [ ] termination process

---

# 147. AI Security Checklist
<!-- id: security.147-ai-security-checklist -->

- [ ] model/provider identified
- [ ] data sensitivity reviewed
- [ ] prompt injection considered
- [ ] tool permissions minimized
- [ ] output validated
- [ ] actions logged
- [ ] confirmation for high-impact actions
- [ ] training/retention terms reviewed
- [ ] abuse limits
- [ ] incident procedure

---

# 148. 100-Point Security Quality Score
<!-- id: security.148-100-point-security-quality-score -->

## Governance — 10

- security ownership: 2
- risk management: 2
- policies/standards: 2
- exceptions: 2
- evidence/reporting: 2

## Asset & Data — 10

- asset inventory: 3
- software inventory: 2
- data inventory: 2
- classification: 2
- retention/minimization: 1

## Identity — 15

- MFA: 3
- least privilege: 3
- privileged access: 3
- lifecycle: 3
- reviews/service accounts: 3

## Infrastructure — 15

- hardened configuration: 3
- patching: 3
- endpoint/server controls: 3
- cloud/network controls: 3
- backups/recovery: 3

## Application & Supply Chain — 20

- secure SDLC: 4
- threat modeling: 3
- ASVS-aligned controls: 5
- dependencies/SBOM: 3
- CI/CD/repository security: 3
- release integrity: 2

## Detection & Response — 15

- logging: 3
- monitoring/detection: 3
- incident response: 4
- exercises: 2
- postmortems: 3

## Third Parties & AI — 10

- vendor security: 4
- AI security: 3
- data/provider controls: 3

## Awareness & Governance Operations — 5

- training: 2
- role-based training: 1
- metrics: 1
- review cadence: 1

---

# 149. Security Quality Thresholds
<!-- id: security.149-security-quality-thresholds -->

- 90–100 = strong security program
- 80–89 = mature baseline with targeted gaps
- 70–79 = functional but meaningful remediation needed
- 60–69 = elevated risk
- below 60 = major security-program improvement required

Critical control failures override the numerical score.

---

# 150. Critical Security Failures
<!-- id: security.150-critical-security-failures -->

Treat these as urgent:

- no MFA for privileged access
- exposed secrets
- unsupported internet-facing critical systems
- missing server-side authorization
- public sensitive-data exposure
- untested backups for critical systems
- no incident-response capability
- uncontrolled production admin access
- critical known-exploited vulnerabilities left exposed without accepted risk
- unknown ownership for critical systems
- no ability to revoke compromised credentials
- AI agents with broad destructive permissions and no controls

---

# 151. Security Program Operating Cycle
<!-- id: security.151-security-program-operating-cycle -->

Recommended cycle:

```text
Inventory
↓
Classify
↓
Assess Risk
↓
Design Controls
↓
Implement
↓
Verify
↓
Monitor
↓
Respond
↓
Recover
↓
Learn
↓
Improve
```

---

# 152. Final Standard
<!-- id: security.152-final-standard -->

Security quality comes from repeatable controls and operational discipline.

A secure organization should be able to answer:

- What do we have?
- Who owns it?
- What data does it contain?
- Who can access it?
- How is access verified?
- How is it configured?
- How is it patched?
- How is it monitored?
- How would we detect compromise?
- How would we contain it?
- How would we recover?
- What evidence proves the controls work?

Security should make normal operation safer by default and make dangerous operation difficult, visible, and reversible wherever possible.

# Control Plane Hooks
<!-- id: security.control-plane-hooks -->

When this module is active, use `CONTROL_INDEX.md` to retrieve only the capability sections relevant to the current decision. Applicable capabilities include:

- **Regulated-industry detection** — `controls/03-industry-taxonomy-and-business-model-classification.md` (BQ-0106–BQ-0110)
- **Risk-overlay composition** — `controls/04-semantic-profiles-risk-and-context-overlays.md` (BQ-0126–BQ-0130)
- **Form-behavior contract** — `controls/17-front-end-engineering-and-component-implementation.md` (BQ-0661–BQ-0665)
- **Permission-model resolution** — `controls/18-application-logic-data-and-integrations.md` (BQ-0686–BQ-0690)
- **Integration-contract standard** — `controls/18-application-logic-data-and-integrations.md` (BQ-0691–BQ-0695)
- **Import-export integrity** — `controls/18-application-logic-data-and-integrations.md` (BQ-0711–BQ-0715)
- **Auditability requirement** — `controls/18-application-logic-data-and-integrations.md` (BQ-0716–BQ-0720)
- **Threat-trigger routing** — `controls/19-security-privacy-and-legal-compliance.md` (BQ-0721–BQ-0725)
- **Data-classification model** — `controls/19-security-privacy-and-legal-compliance.md` (BQ-0726–BQ-0730)
- **Least-privilege standard** — `controls/19-security-privacy-and-legal-compliance.md` (BQ-0731–BQ-0735)
- **Secret-handling guard** — `controls/19-security-privacy-and-legal-compliance.md` (BQ-0736–BQ-0740)
- **Privacy-by-design routing** — `controls/19-security-privacy-and-legal-compliance.md` (BQ-0741–BQ-0745)
- **Security-evidence gate** — `controls/19-security-privacy-and-legal-compliance.md` (BQ-0756–BQ-0760)
- **Third-party cost ledger** — `controls/21-performance-reliability-and-resource-budgets.md` (BQ-0821–BQ-0825)
- **Operational-risk routing** — `controls/23-jobs-sops-and-operational-systems.md` (BQ-0916–BQ-0920)

These hooks are routing pointers, not permission to preload the listed shards. Evidence Gates control pass/fail claims.
