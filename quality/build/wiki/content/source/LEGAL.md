<!--
Pack-Version: 4.0.0
Schema-Version: 3
Module: LEGAL
Module-Version: 1
Last-Updated: 2026-08-09
-->

# Legal Policy Standards for Websites, Apps, SaaS, and Online Services
<!-- id: legal.legal-policy-standards-for-websites-apps-saas-and-online-services -->

Version: 2026-08-09  
Status: General compliance framework and drafting standard  
Scope: Terms of Service, Privacy, Cookies, Data Processing, Consumer Terms, Acceptable Use, IP/DMCA, Accessibility, Security, and related notices

---

# 1. Purpose
<!-- id: legal.1-purpose -->

This standard defines minimum and enhanced requirements for public-facing legal policies and supporting compliance documents.

The goal is to ensure legal documents are:

- accurate
- enforceable where intended
- understandable
- operationally truthful
- jurisdiction-aware
- easy to find
- accessible
- version-controlled
- consistent with product behavior
- consistent with contracts
- consistent with actual data practices
- maintainable as laws and products change

Legal pages MUST NOT be treated as generic boilerplate.

---

# 2. Standards Language
<!-- id: legal.2-standards-language -->

Use these terms consistently:

- MUST = required by this internal standard
- MUST NOT = prohibited by this internal standard
- SHOULD = expected unless there is a documented reason not to do it
- SHOULD NOT = generally avoid
- MAY = optional enhancement
- COUNSEL REVIEW = requires jurisdiction-specific legal review before production use

---

# 3. Core Rule: Legal Text Must Match Reality
<!-- id: legal.3-core-rule-legal-text-must-match-reality -->

Every legal policy MUST accurately reflect actual business and technical practices.

Do not state that:

- data is never shared when vendors receive it
- data is never sold when legally defined "sale" may occur
- tracking is anonymous when identifiers can be linked to users
- data is deleted immediately when backups retain it
- security is guaranteed
- encryption is always used if exceptions exist
- users can cancel anytime if cancellation has restrictions
- refunds are available if they are not
- a service is available in a jurisdiction where it is restricted
- content is reviewed by humans if it is not
- AI is not used if AI materially processes user data
- data is not used for training if any training use occurs
- a company complies with a certification or law when the claim is unsupported

Legal drafting MUST follow verified operational facts.

---

# 4. Legal Document Inventory
<!-- id: legal.4-legal-document-inventory -->

Before drafting, create an inventory of required documents.

Common public documents:

- Terms of Service / Terms and Conditions
- Privacy Policy / Privacy Notice
- Cookie Policy
- Cookie / tracking consent notice
- Notice at Collection
- "Do Not Sell or Share" mechanism where applicable
- privacy rights request page
- Acceptable Use Policy
- Community Guidelines
- Refund Policy
- Cancellation Policy
- Subscription / Auto-Renewal Terms
- Shipping Policy
- Return Policy
- Accessibility Statement
- Copyright / DMCA Policy
- Trademark Policy
- User Content Policy
- AI Usage / AI Feature Notice
- Biometric Privacy Notice
- Consumer Health Data Notice
- Children's Privacy Notice
- Security / Responsible Disclosure Policy
- Marketplace Seller Terms
- Developer / API Terms
- Partner / Affiliate Terms

Common contractual documents:

- Data Processing Addendum
- Controller-Processor Agreement
- Standard Contractual Clauses where applicable
- Business Associate Agreement where HIPAA applies
- Security Addendum
- Service Level Agreement
- Enterprise Terms
- Order Form
- Subprocessor Addendum
- AI/Data Use Addendum
- Confidentiality Agreement
- Vendor Data Protection Terms

Common internal compliance documents:

- records of processing activities
- data inventory
- data flow map
- retention schedule
- privacy impact assessment
- data protection impact assessment
- risk assessment
- vendor register
- subprocessor register
- incident response plan
- breach notification procedure
- privacy request procedure
- consent logs
- cookie inventory
- legal change log
- policy version archive

---

# 5. Applicability Matrix Standard
<!-- id: legal.5-applicability-matrix-standard -->

Do not draft policies until an applicability matrix exists.

The matrix SHOULD identify:

- countries where users reside
- countries where the company is established
- U.S. states where users reside
- physical business locations
- whether goods or services are offered internationally
- whether behavior is monitored internationally
- whether personal data is collected
- whether sensitive data is collected
- whether health data is collected
- whether biometric data is collected
- whether precise geolocation is collected
- whether children or teens may use the service
- whether targeted advertising is used
- whether data is sold or shared under applicable definitions
- whether automated decision-making is used
- whether user-generated content is hosted
- whether recurring billing is used
- whether the service is a marketplace
- whether the service processes customer data as a processor/service provider
- whether the service is regulated by sector-specific law

Each applicable jurisdiction or legal regime SHOULD map to:

- required notice
- required consent
- required user rights
- required contract clauses
- response deadlines
- opt-out requirements
- retention requirements
- security requirements
- breach notification rules
- age requirements
- special data restrictions

---

# 6. Legal Review Trigger Standard
<!-- id: legal.6-legal-review-trigger-standard -->

COUNSEL REVIEW is mandatory before launch when the service involves:

- arbitration
- class-action waiver
- liability limitations for high-risk services
- healthcare
- financial services
- insurance
- legal services
- children
- biometric information
- precise geolocation
- consumer health data
- employment screening
- credit decisions
- automated high-impact decisions
- regulated professional advice
- gambling
- alcohol
- cannabis
- age-restricted products
- user-generated content at scale
- international data transfers
- recurring subscriptions
- marketplace payments
- high-value consumer transactions
- enterprise processing of sensitive data
- government customers
- education records
- student data
- large-scale profiling
- data brokerage

---

# 7. Plain-Language Standard
<!-- id: legal.7-plain-language-standard -->

Legal text SHOULD be written in clear language while preserving legal precision.

Legal documents SHOULD:

- use descriptive headings
- define specialized terms
- use short paragraphs
- use lists for enumerations
- avoid unnecessary archaic language
- distinguish mandatory obligations from examples
- explain important consumer consequences
- place high-impact terms where users will see them

Do not use complexity to obscure material terms.

---

# 8. Layered Notice Standard
<!-- id: legal.8-layered-notice-standard -->

Complex disclosures SHOULD use layered notices.

Recommended structure:

1. short notice at the point of action
2. concise summary of material terms
3. full policy
4. detailed appendices where needed

Examples:

- cookie banner → cookie settings → cookie policy
- checkout disclosure → subscription terms → full Terms
- signup notice → Privacy Policy
- California notice at collection → full Privacy Policy
- AI feature notice → AI terms → Privacy Policy

The short layer MUST NOT contradict or materially omit what the full policy says.

---

# 9. Conspicuousness Standard
<!-- id: legal.9-conspicuousness-standard -->

Material terms MUST be reasonably noticeable before the user is bound.

High-impact terms include:

- price
- recurring charges
- renewal frequency
- cancellation conditions
- refund limitations
- arbitration
- class-action waiver
- automatic renewal
- material data uses
- sale or sharing of data
- sensitive-data processing
- user-content licenses
- significant liability allocations

Do not bury material terms solely in a footer-linked document when affirmative notice or consent is required.

---

# 10. Assent Standard
<!-- id: legal.10-assent-standard -->

When Terms are intended to form a binding contract, the product SHOULD obtain affirmative assent.

Preferred implementation:

- user is presented with a clear notice
- the Terms are linked
- the Privacy Policy is separately linked
- the user takes an affirmative action
- the action communicates agreement
- the acceptance event is recorded

Preferred wording pattern:

`By selecting "Create account," you agree to the Terms of Service and acknowledge the Privacy Policy.`

Do not use pre-checked agreement boxes.

Do not rely solely on passive footer availability for high-value or high-risk contractual terms.

---

# 11. Assent Logging Standard
<!-- id: legal.11-assent-logging-standard -->

For contractual acceptance, retain evidence sufficient to reconstruct assent.

Logs SHOULD include:

- user or account identifier
- date and time
- terms version
- privacy version where acknowledgment is recorded
- locale or country when relevant
- interface or product surface
- acceptance action
- IP address where lawful and necessary
- device/session identifiers where lawful and necessary

Retention of assent evidence SHOULD be aligned with legal and contractual limitation periods.

---

# 12. Version Control Standard
<!-- id: legal.12-version-control-standard -->

Every legal document SHOULD have:

- effective date
- last updated date
- version identifier
- internal owner
- approval record

Maintain prior versions.

Do not overwrite prior terms without retaining an archive.

---

# 13. Change Management Standard
<!-- id: legal.13-change-management-standard -->

Material legal-policy changes MUST be reviewed before deployment.

The review SHOULD determine whether the change requires:

- advance notice
- renewed consent
- renewed contractual assent
- updated notice at collection
- updated cookie consent
- updated subprocessor notice
- customer notification
- regulator notification
- updated app-store disclosure
- updated product UI

A general "we may change these terms at any time" clause MUST NOT be treated as a substitute for legally required notice or consent.

---

# 14. Legal Policy Ownership Standard
<!-- id: legal.14-legal-policy-ownership-standard -->

Assign an owner for each legal document.

Ownership SHOULD include:

- Legal
- Privacy
- Security
- Product
- Engineering
- Marketing
- Customer Support

At least one accountable individual MUST be responsible for keeping each policy accurate.

---

# 15. Terms of Service — Minimum Structure
<!-- id: legal.15-terms-of-service-minimum-structure -->

A general Terms of Service document SHOULD evaluate inclusion of:

- contracting entity
- scope
- definitions
- eligibility
- account registration
- account security
- service description
- license to use the service
- restrictions
- acceptable use
- user content
- intellectual property
- third-party services
- payments
- taxes
- subscriptions
- cancellation
- refunds
- promotions
- service changes
- beta features
- suspension
- termination
- warranties
- disclaimers
- limitation of liability
- indemnification
- governing law
- dispute resolution
- arbitration if applicable
- class-action waiver if applicable
- notices
- assignment
- severability
- waiver
- force majeure where appropriate
- entire agreement
- order of precedence
- changes to terms
- contact information

Not every section applies to every business.

---

# 16. Contracting Entity Standard
<!-- id: legal.16-contracting-entity-standard -->

Terms MUST identify the legal entity forming the contract.

Include where appropriate:

- legal company name
- trade name
- jurisdiction of formation
- business address
- contact method

Do not use only a brand name if the legal contracting entity is different.

---

# 17. Scope Standard
<!-- id: legal.17-scope-standard -->

Terms SHOULD clearly identify:

- websites covered
- apps covered
- products covered
- services covered
- APIs covered
- enterprise services covered
- exclusions
- separate terms that override the general Terms

Avoid ambiguous language such as "all our services" if different products have materially different contractual terms.

---

# 18. Eligibility Standard
<!-- id: legal.18-eligibility-standard -->

Terms SHOULD state who may use the service.

Address:

- minimum age
- authority to contract
- business authority
- prohibited jurisdictions
- sanctions restrictions where applicable
- account eligibility
- organizational users

If users accept Terms on behalf of a company, require representation that they have authority to bind the organization.

---

# 19. Account Standard
<!-- id: legal.19-account-standard -->

Terms SHOULD address:

- account accuracy
- credential confidentiality
- unauthorized access
- account sharing
- organization-admin authority
- account recovery
- responsibility for authorized users

Do not disclaim responsibility for security in a way that conflicts with applicable law.

---

# 20. Service Description Standard
<!-- id: legal.20-service-description-standard -->

Describe the service accurately.

Do not guarantee:

- uptime
- accuracy
- availability
- compatibility
- results
- uninterrupted service

unless the business intends to make that guarantee.

Where service levels are contractually promised, place them in an SLA or equivalent controlled document.

---

# 21. License-to-Use Standard
<!-- id: legal.21-license-to-use-standard -->

Terms SHOULD specify the user's limited right to use the service.

Address:

- scope
- territory
- term
- revocability
- transferability
- sublicensing
- permitted business use
- permitted personal use

The license MUST align with the actual product model.

---

# 22. Acceptable Use Standard
<!-- id: legal.22-acceptable-use-standard -->

Prohibited uses SHOULD be specific enough to enforce consistently.

Common categories:

- unlawful activity
- fraud
- abuse
- harassment
- exploitation
- malware
- credential theft
- unauthorized access
- scraping where prohibited
- circumvention
- spam
- deceptive activity
- IP infringement
- privacy violations
- dangerous activity
- platform manipulation
- account resale
- rate-limit evasion

Separate detailed Acceptable Use Policies MAY be incorporated by reference.

---

# 23. Enforcement Standard
<!-- id: legal.23-enforcement-standard -->

If the service can suspend or terminate users, Terms SHOULD explain:

- grounds for enforcement
- suspension
- termination
- content removal
- investigation
- preservation of evidence
- appeals where offered
- emergency action
- cooperation with lawful process

Enforcement language SHOULD preserve appropriate discretion without being misleading.

---

# 24. User Content Standard
<!-- id: legal.24-user-content-standard -->

If users upload content, define:

- ownership
- license granted to the service
- purpose of the license
- duration
- sublicensing rights
- content moderation
- backups
- deletion
- visibility
- representations by the user
- prohibited content

The user-content license SHOULD be no broader than reasonably necessary for the service unless a broader license is intentional and legally reviewed.

---

# 25. AI Training / Model Improvement Standard
<!-- id: legal.25-ai-training-model-improvement-standard -->

If user content or customer data may be used for AI training, model improvement, evaluation, or human review, this MUST be addressed clearly.

State:

- whether the use occurs
- what data is involved
- whether enterprise data is treated differently
- whether users can opt out
- whether de-identified or aggregated data is used
- whether third-party AI providers receive data
- relevant retention practices

Do not hide material AI training rights inside a generic content license.

---

# 26. Intellectual Property Standard
<!-- id: legal.26-intellectual-property-standard -->

Terms SHOULD identify:

- company IP
- user IP
- third-party IP
- trademarks
- feedback rights
- open-source components where relevant

Feedback clauses SHOULD state what rights the company receives in submitted suggestions.

---

# 27. Third-Party Service Standard
<!-- id: legal.27-third-party-service-standard -->

Where integrations or third-party services are used, Terms SHOULD explain:

- whether third-party terms apply
- whether the company controls the third party
- whether data may be exchanged
- responsibility boundaries
- external-link limitations

The Privacy Policy MUST separately disclose relevant data sharing.

---

# 28. Payment Standard
<!-- id: legal.28-payment-standard -->

Payment terms SHOULD state:

- pricing
- currency
- taxes
- payment timing
- billing method
- failed payments
- authorization
- invoicing
- price changes
- third-party payment processor role

Displayed checkout terms MUST match the Terms.

---

# 29. Subscription Standard
<!-- id: legal.29-subscription-standard -->

Recurring subscriptions MUST disclose material terms clearly before charge authorization.

At minimum:

- price
- billing frequency
- free-trial terms
- trial conversion
- renewal behavior
- duration
- cancellation process
- cancellation effective date
- refund consequences
- price-change process

For U.S. online negative-option plans, workflows should be reviewed against ROSCA and applicable state auto-renewal laws.

---

# 30. Cancellation Standard
<!-- id: legal.30-cancellation-standard -->

Cancellation SHOULD be easy to locate and execute.

The cancellation policy MUST match actual product behavior.

Do not state "cancel anytime" if:

- a minimum term applies
- cancellation is delayed
- cancellation is restricted to certain channels
- fees remain due
- another material limitation exists

Document cancellation events and confirmation.

---

# 31. Refund Standard
<!-- id: legal.31-refund-standard -->

Refund terms SHOULD specify:

- eligibility
- exclusions
- request method
- timing
- prorating
- digital goods treatment
- marketplace treatment
- statutory rights that override policy

A "no refunds" clause MUST NOT purport to eliminate non-waivable consumer rights.

---

# 32. Promotions and Trials Standard
<!-- id: legal.32-promotions-and-trials-standard -->

Promotional terms SHOULD state:

- eligibility
- duration
- conversion price
- renewal behavior
- exclusions
- geographic limitations
- one-per-user rules
- expiration

Free trials MUST NOT obscure automatic conversion into paid subscriptions.

---

# 33. Warranty Disclaimer Standard
<!-- id: legal.33-warranty-disclaimer-standard -->

Warranty disclaimers require COUNSEL REVIEW.

Disclaimers SHOULD:

- use legally appropriate conspicuous formatting
- preserve non-waivable rights
- avoid disclaiming express promises made elsewhere
- avoid internally contradictory marketing claims

Do not promise performance in marketing and disclaim the same promise in Terms.

---

# 34. Limitation of Liability Standard
<!-- id: legal.34-limitation-of-liability-standard -->

Liability limitations require COUNSEL REVIEW.

Review:

- jurisdiction
- consumer vs business use
- exclusion of indirect damages
- liability cap
- carve-outs
- gross negligence
- willful misconduct
- IP obligations
- confidentiality
- data protection
- statutory rights

Do not assume a limitation clause is enforceable everywhere.

---

# 35. Indemnity Standard
<!-- id: legal.35-indemnity-standard -->

Indemnification clauses require COUNSEL REVIEW.

Define:

- triggering claims
- covered losses
- control of defense
- cooperation
- settlement authority
- notice

Consumer indemnities SHOULD receive enhanced scrutiny.

---

# 36. Arbitration Standard
<!-- id: legal.36-arbitration-standard -->

Any arbitration clause requires COUNSEL REVIEW.

If used, evaluate:

- affirmative assent
- conspicuous notice
- arbitration provider
- rules
- venue
- fees
- small-claims carve-out
- opt-out procedure
- mass-arbitration procedures
- class waiver
- jurisdiction restrictions

Do not copy arbitration language from another company's Terms.

---

# 37. Governing Law Standard
<!-- id: legal.37-governing-law-standard -->

Governing-law and forum clauses require jurisdiction review.

Consumer protections may override contractual choice-of-law language.

Do not state that one jurisdiction's law eliminates mandatory protections elsewhere.

---

# 38. Termination Standard
<!-- id: legal.38-termination-standard -->

Terms SHOULD explain:

- user termination
- company termination
- effect on paid amounts
- content access
- data deletion
- surviving provisions
- export windows where offered

Termination language MUST align with privacy and retention obligations.

---

# 39. Privacy Policy — Core Rule
<!-- id: legal.39-privacy-policy-core-rule -->

A Privacy Policy MUST describe actual personal-data practices.

It SHOULD answer:

- who collects the data
- what data is collected
- where data comes from
- why it is used
- legal basis where required
- who receives it
- whether it is sold or shared under applicable law
- whether targeted advertising occurs
- how long it is retained
- where it is processed
- how it is protected
- what rights users have
- how users exercise rights
- how children are handled
- how changes are communicated
- how to contact the organization

---

# 40. Privacy Policy Scope Standard
<!-- id: legal.40-privacy-policy-scope-standard -->

The Privacy Policy MUST define its scope.

State whether it covers:

- websites
- apps
- SaaS
- customer portals
- marketing sites
- events
- sales contacts
- support
- job applicants
- employees
- offline collection
- enterprise end users
- APIs

Use separate notices when audiences or legal obligations differ materially.

---

# 41. Privacy Controller / Business Identity Standard
<!-- id: legal.41-privacy-controller-business-identity-standard -->

Identify the organization responsible for personal data.

Include where applicable:

- controller/business legal name
- address
- privacy contact
- DPO contact
- EU/UK representative
- local representative
- relevant affiliates

Do not make users guess which affiliate controls their data.

---

# 42. Data Category Standard
<!-- id: legal.42-data-category-standard -->

List categories of personal data with sufficient specificity.

Potential categories:

- identifiers
- contact data
- account data
- transaction data
- payment-related data
- device data
- IP address
- browser data
- usage data
- approximate location
- precise location
- communications
- customer-support content
- uploaded content
- professional information
- preferences
- advertising identifiers
- cookie identifiers
- inferences
- biometric data
- health data
- sensitive data

Avoid vague categories such as "other information" without explanation.

---

# 43. Source Standard
<!-- id: legal.43-source-standard -->

State sources of personal data where relevant.

Examples:

- directly from the user
- automatically from the device
- employer or organization
- integrations
- payment processors
- identity providers
- public sources
- data providers
- advertising partners
- affiliates

Under GDPR-like regimes, source disclosure may be required when data is obtained indirectly.

---

# 44. Purpose Standard
<!-- id: legal.44-purpose-standard -->

Map data categories to specific processing purposes.

Purposes MAY include:

- provide the service
- authenticate users
- process payments
- maintain security
- prevent fraud
- provide support
- personalize features
- measure usage
- improve products
- develop products
- train or evaluate AI
- communicate with users
- market services
- comply with law
- enforce agreements

Do not use undefined purposes such as "business purposes" without meaningful detail.

---

# 45. Purpose Limitation Standard
<!-- id: legal.45-purpose-limitation-standard -->

Personal data SHOULD NOT be reused for materially incompatible purposes without additional legal review.

Product teams MUST review new data uses before launch.

A privacy policy's broad wording MUST NOT be treated as unlimited permission to repurpose data.

---

# 46. Data Minimization Standard
<!-- id: legal.46-data-minimization-standard -->

Collect only data reasonably necessary for the intended purpose.

Before adding a new field, event, tracker, or identifier, document:

- purpose
- necessity
- retention
- access
- recipient
- security classification

Under GDPR, data minimization is a core processing principle.

---

# 47. Legal Basis Standard
<!-- id: legal.47-legal-basis-standard -->

Where GDPR or similar law requires a lawful basis, map each purpose to the applicable basis.

Potential bases include:

- consent
- contract
- legal obligation
- vital interests
- public task
- legitimate interests

Do not list every lawful basis generically for every purpose.

Where legitimate interests are relied upon, document the assessment where appropriate.

---

# 48. Consent Standard
<!-- id: legal.48-consent-standard -->

Consent MUST be:

- informed
- specific
- affirmative
- unambiguous where required
- freely given where required
- capable of withdrawal

Do not bundle unrelated consent into mandatory Terms when separate consent is legally required.

Record consent evidence when the organization relies on consent as a legal basis.

---

# 49. Consent Withdrawal Standard
<!-- id: legal.49-consent-withdrawal-standard -->

Withdrawing consent SHOULD be no more difficult than giving it.

Withdrawal MUST:

- be available through a reasonable method
- propagate to relevant systems
- stop future processing dependent solely on that consent
- be logged
- preserve lawful prior processing where applicable

---

# 50. Sensitive Data Standard
<!-- id: legal.50-sensitive-data-standard -->

Sensitive data requires enhanced controls.

Potential sensitive categories include:

- government identifiers
- financial credentials
- precise geolocation
- private communications
- racial or ethnic origin
- religion
- union membership
- genetics
- biometrics used for identification
- health
- sex life
- sexual orientation
- children's data

Identify applicable consent, opt-in, opt-out, limitation, assessment, and security requirements before processing.

---

# 51. Biometric Data Standard
<!-- id: legal.51-biometric-data-standard -->

Biometric processing requires a dedicated review.

Before collecting biometric identifiers or templates, determine:

- jurisdiction
- notice requirement
- consent requirement
- purpose
- retention schedule
- deletion trigger
- vendor access
- security
- prohibition on sale or profit where applicable

A generic Privacy Policy SHOULD NOT be the only compliance control.

---

# 52. Health Data Standard
<!-- id: legal.52-health-data-standard -->

Health-related data requires separate legal classification.

Determine whether:

- HIPAA applies
- the company is a covered entity
- the company is a business associate
- a BAA is required
- consumer-health-data laws apply outside HIPAA
- health data is used for advertising
- health data is inferred rather than directly provided

Do not assume data is unregulated merely because HIPAA does not apply.

---

# 53. HIPAA / BAA Standard
<!-- id: legal.53-hipaa-baa-standard -->

If HIPAA applies, determine whether a written Business Associate Agreement is required.

A BAA SHOULD address required permitted uses, safeguards, breach/security incident obligations, subcontractors, individual-right assistance, return/destruction, and termination rights consistent with applicable HIPAA requirements.

Do not label a contract "HIPAA compliant" without confirming the operational security and privacy program.

---

# 54. Children's Privacy Standard
<!-- id: legal.54-childrens-privacy-standard -->

Determine whether the service is:

- directed to children
- mixed audience
- general audience
- likely to have actual knowledge of child users

For U.S. COPPA coverage, covered operators must implement child-specific privacy requirements, including notice, parental consent where required, parental rights, security, data minimization, and retention/deletion controls.

Do not place responsibility for operator compliance solely on a school, parent, or customer through Terms when the law assigns responsibility to the operator.

---

# 55. Age Assurance Standard
<!-- id: legal.55-age-assurance-standard -->

If age affects legal obligations, the service SHOULD define an age-assurance strategy.

Evaluate:

- self-declaration
- age estimation
- document verification
- parental consent
- privacy impact of age verification
- retention of verification data
- third-party verification vendors

Collect no more age-verification data than necessary.

---

# 56. Data Sharing Standard
<!-- id: legal.56-data-sharing-standard -->

Privacy notices MUST describe material disclosures to third parties.

Common recipient categories:

- hosting providers
- cloud providers
- payment processors
- analytics providers
- advertising partners
- customer-support vendors
- security vendors
- identity providers
- professional advisers
- affiliates
- business transaction parties
- government authorities where legally required

Use categories that users can meaningfully understand.

---

# 57. Processor / Service Provider Classification Standard
<!-- id: legal.57-processor-service-provider-classification-standard -->

Do not call every vendor a processor or service provider.

Classify each recipient based on actual role.

A vendor may act as:

- processor
- service provider
- contractor
- independent controller
- joint controller
- third party

Contract terms and disclosures MUST match the role.

---

# 58. Sale / Sharing Standard
<!-- id: legal.58-sale-sharing-standard -->

Determine whether disclosures constitute:

- sale
- sharing
- targeted advertising
- cross-context behavioral advertising
- consideration-based transfer

Definitions vary by jurisdiction.

Do not use ordinary-language "we do not sell data" without confirming applicable legal definitions.

---

# 59. Global Privacy Control Standard
<!-- id: legal.59-global-privacy-control-standard -->

Where applicable law requires recognition of qualifying opt-out preference signals, the product MUST honor them.

GPC / universal opt-out processing SHOULD be:

- automated
- tested
- documented
- reflected in the Privacy Policy
- applied consistently across relevant trackers and downstream recipients

A user SHOULD NOT need to complete an additional form when a recognized signal is legally sufficient.

---

# 60. California Privacy Standard
<!-- id: legal.60-california-privacy-standard -->

If the CCPA applies, evaluate requirements for:

- notice at collection
- privacy policy disclosures
- rights to know/access
- deletion
- correction
- opt-out of sale/sharing
- limitation of certain sensitive-data uses
- non-discrimination
- authorized agents
- opt-out preference signals
- service-provider/contractor contracts
- retention disclosures
- risk assessments where applicable
- cybersecurity audits where applicable
- automated decisionmaking requirements on the applicable compliance timeline

California's current CCPA regulations took effect January 1, 2026, with some requirements phased later.

---

# 61. Notice at Collection Standard
<!-- id: legal.61-notice-at-collection-standard -->

Where a point-of-collection notice is required, provide it at or before collection.

The notice SHOULD identify:

- categories of personal information
- purposes
- retention information where required
- sale/sharing information where required
- sensitive-data information where required
- link to the full Privacy Policy
- opt-out mechanism where applicable

Do not collect first and disclose later when prior notice is required.

---

# 62. Privacy Rights Standard
<!-- id: legal.62-privacy-rights-standard -->

Privacy notices SHOULD identify applicable rights without overpromising rights that do not exist.

Possible rights include:

- access
- confirmation
- correction
- deletion
- portability
- restriction
- objection
- withdrawal of consent
- opt-out of sale
- opt-out of sharing
- opt-out of targeted advertising
- opt-out of certain profiling
- limitation of sensitive-data use
- appeal
- complaint to a regulator

Rights SHOULD be described by jurisdiction where necessary.

---

# 63. Privacy Request Workflow Standard
<!-- id: legal.63-privacy-request-workflow-standard -->

A rights request system MUST have an operational backend.

Define:

- intake channels
- identity verification
- authorized-agent handling
- request categorization
- deadlines
- extensions
- exemptions
- search procedures
- deletion propagation
- response templates
- appeal process where applicable
- logging
- metrics
- escalation

Do not publish a privacy-right promise the organization cannot operationally fulfill.

---

# 64. Identity Verification Standard
<!-- id: legal.64-identity-verification-standard -->

Request verification SHOULD be proportionate to:

- sensitivity
- risk
- requested action
- existing authentication

Do not collect excessive new identity information merely to process a privacy request.

Opt-out requests SHOULD NOT be subjected to unnecessary verification where law prohibits or does not require it.

---

# 65. Retention Standard
<!-- id: legal.65-retention-standard -->

The Privacy Policy SHOULD explain retention meaningfully.

Avoid only saying:

`We retain data as long as necessary.`

A stronger standard is to provide:

- specific period, or
- criteria used to determine the period, or
- category-based retention table

Internal retention schedules MUST match external disclosures.

---

# 66. Deletion Standard
<!-- id: legal.66-deletion-standard -->

Deletion workflows SHOULD address:

- production systems
- analytics systems
- marketing systems
- vendors
- subprocessors
- backups
- legal holds
- fraud/security records
- financial records
- derived data
- model-training implications where relevant

Privacy text SHOULD explain material exceptions without overstating them.

---

# 67. International Transfer Standard
<!-- id: legal.67-international-transfer-standard -->

If personal data is transferred internationally, identify a valid transfer mechanism where required.

Potential mechanisms MAY include:

- adequacy decisions
- approved standard contractual clauses
- binding corporate rules
- statutory derogations where appropriate

Transfer mechanisms MUST be reviewed for current validity.

Where required, conduct and document transfer-risk assessments and supplementary safeguards.

---

# 68. Security Disclosure Standard
<!-- id: legal.68-security-disclosure-standard -->

Privacy policies SHOULD describe security at an appropriate level.

Good language:

- reasonable administrative safeguards
- technical safeguards
- organizational safeguards
- physical safeguards where relevant

Avoid:

- "100% secure"
- "unhackable"
- guarantees of no breach

Detailed controls belong in security documentation, trust centers, and customer security addenda.

---

# 69. Security Program Standard
<!-- id: legal.69-security-program-standard -->

Policy promises MUST be backed by an actual security program.

Baseline controls SHOULD include:

- least privilege
- MFA
- encryption appropriate to risk
- secure development
- vulnerability management
- logging
- incident response
- vendor management
- backup controls
- retention controls
- employee training
- access reviews

The FTC emphasizes collecting only what is needed, protecting it, and securely disposing of it.

---

# 70. Breach Notification Standard
<!-- id: legal.70-breach-notification-standard -->

Maintain a jurisdiction-based incident-notification matrix.

The incident response process SHOULD identify:

- affected systems
- affected data
- affected individuals
- jurisdiction
- risk
- regulator notification requirements
- individual notification requirements
- contractual notification requirements
- timing
- law-enforcement considerations

Under GDPR, qualifying personal-data breaches can trigger supervisory-authority notification obligations and, in high-risk cases, communication to affected individuals.

---

# 71. Automated Decision-Making Standard
<!-- id: legal.71-automated-decision-making-standard -->

If automated systems make or materially assist decisions that affect people, document:

- decision type
- data inputs
- output
- human involvement
- significance
- profiling
- appeal/review
- legal effects
- opt-out rights
- access rights
- required notices
- risk assessment

High-impact automated decisions require COUNSEL REVIEW.

---

# 72. AI Feature Disclosure Standard
<!-- id: legal.72-ai-feature-disclosure-standard -->

If a product includes AI, determine whether users need disclosure of:

- AI-generated output
- limitations
- human review
- model provider
- data sent to models
- retention
- training use
- automated decisions
- prohibited uses
- accuracy limitations

AI disclosures MUST NOT contradict the Privacy Policy or Terms.

---

# 73. Data Processing Addendum Standard
<!-- id: legal.73-data-processing-addendum-standard -->

A DPA SHOULD define:

- parties
- controller/processor roles
- subject matter
- duration
- nature of processing
- purposes
- data categories
- data subjects
- documented instructions
- confidentiality
- security
- subprocessors
- rights assistance
- DPIA assistance
- breach assistance
- deletion/return
- audit rights
- regulator cooperation
- international transfers
- liability relationship to main agreement
- precedence

Under GDPR, controller-processor relationships require a contract or other binding legal act containing specified protections.

---

# 74. Subprocessor Standard
<!-- id: legal.74-subprocessor-standard -->

Maintain a current subprocessor list where relevant.

For each subprocessor, record:

- legal name
- service
- processing purpose
- data categories
- processing location
- transfer mechanism
- security review
- contract status

If customers have contractual notice or objection rights, maintain an operational notification process.

---

# 75. Vendor Privacy Standard
<!-- id: legal.75-vendor-privacy-standard -->

Before a vendor receives personal data:

- classify role
- conduct risk review
- confirm purpose
- confirm necessity
- review security
- execute required agreement
- record subprocessor use
- assess international transfers
- define deletion
- define incident notification

Do not rely solely on a vendor's public privacy policy for processor obligations.

---

# 76. Cookie Policy Standard
<!-- id: legal.76-cookie-policy-standard -->

A Cookie Policy SHOULD identify:

- what cookies/similar technologies are
- categories used
- purposes
- first-party vs third-party use
- duration
- vendors
- controls
- consent choices
- opt-out mechanisms

The policy MUST match actual deployed trackers.

---

# 77. Cookie Inventory Standard
<!-- id: legal.77-cookie-inventory-standard -->

Maintain a scanner-supported and manually reviewed cookie/tracker inventory.

For each tracker record:

- name
- provider
- domain
- purpose
- category
- duration
- data received
- activation condition
- legal basis where relevant
- opt-out behavior

Unknown trackers SHOULD be investigated before production.

---

# 78. EU / UK Cookie Consent Standard
<!-- id: legal.78-eu-uk-cookie-consent-standard -->

For EU/UK users, non-essential storage or access technologies generally require consent unless an exemption applies.

A high-quality consent interface SHOULD:

- block non-essential trackers before consent
- provide clear purposes
- provide granular choices
- avoid pre-selected optional consent
- make reject reasonably prominent
- make withdrawal easy
- preserve consent evidence
- respect changed choices

Strictly necessary technologies SHOULD be narrowly classified.

---

# 79. Cookie Banner Dark-Pattern Standard
<!-- id: legal.79-cookie-banner-dark-pattern-standard -->

Cookie interfaces MUST NOT use deceptive design.

Avoid:

- hidden reject controls
- misleading button colors
- false urgency
- confusing toggles
- consent walls where invalid
- preselected optional categories
- repeated prompts intended to wear users down
- language that misrepresents consequences

---

# 80. Consent Management Platform Standard
<!-- id: legal.80-consent-management-platform-standard -->

A CMP SHOULD be technically validated.

Test:

- no optional tags before consent where prohibited
- consent state persistence
- rejection state persistence
- revocation
- vendor signaling
- cross-domain behavior
- mobile behavior
- logged consent
- geographic rules
- GPC interaction
- tag-manager interaction

Policy text alone does not create compliance if trackers fire incorrectly.

---

# 81. Marketing Email Standard
<!-- id: legal.81-marketing-email-standard -->

Commercial email programs SHOULD be reviewed for:

- sender identification
- truthful headers
- non-deceptive subjects
- required business identification
- unsubscribe method
- suppression
- vendor responsibility
- jurisdiction-specific consent

U.S. commercial email must be reviewed against CAN-SPAM; other jurisdictions may impose opt-in standards.

---

# 82. SMS / Telephone Marketing Standard
<!-- id: legal.82-sms-telephone-marketing-standard -->

SMS and telephone marketing require separate legal review.

Review:

- consent wording
- proof of consent
- automated dialing or messaging
- marketing purpose
- quiet hours
- revocation
- STOP handling
- reassigned numbers
- national/state do-not-call rules
- vendor behavior

Do not reuse email consent as SMS consent without legal validation.

---

# 83. Consumer Review Standard
<!-- id: legal.83-consumer-review-standard -->

Terms MUST NOT prohibit users from providing lawful honest reviews in violation of applicable consumer-review protections.

Do not use clauses that broadly penalize consumers for negative reviews.

Moderation rules MAY prohibit unlawful, abusive, fraudulent, or irrelevant content.

---

# 84. DMCA / Copyright Safe Harbor Standard
<!-- id: legal.84-dmca-copyright-safe-harbor-standard -->

For U.S. online services seeking Section 512 safe-harbor protection where applicable:

- designate a DMCA agent
- register the agent with the U.S. Copyright Office
- publish current agent contact information
- maintain a notice-and-takedown process
- maintain a counter-notice process
- address repeat infringers where applicable
- keep registration current

Do not publish a DMCA policy without an operational takedown workflow.

---

# 85. Copyright Notice Standard
<!-- id: legal.85-copyright-notice-standard -->

A copyright notice MAY identify:

- copyright owner
- year
- covered content
- permitted uses
- licensing contact

Do not claim copyright ownership over third-party or user-owned material.

---

# 86. Trademark Standard
<!-- id: legal.86-trademark-standard -->

Trademark policies SHOULD distinguish:

- company marks
- third-party marks
- nominative references
- prohibited impersonation
- brand guidelines
- permission requests

Do not state that every use of a trademark requires permission if applicable law permits certain uses.

---

# 87. Accessibility Statement Standard
<!-- id: legal.87-accessibility-statement-standard -->

An Accessibility Statement SHOULD:

- state the accessibility goal
- identify the standard targeted
- provide a contact method
- invite reports of barriers
- explain alternative-access options
- avoid unsupported conformance claims

Internal best-practice target: WCAG 2.2 Level AA unless a specific legal or contractual standard requires otherwise.

---

# 88. Accessibility Legal Standard
<!-- id: legal.88-accessibility-legal-standard -->

Do not state that WCAG 2.2 AA is legally mandated everywhere.

Requirements vary.

For U.S. state and local governments, DOJ Title II rules specify WCAG 2.1 Level AA with compliance timelines based on entity size.

Private-sector obligations require jurisdiction- and sector-specific analysis.

---

# 89. Responsible Disclosure Standard
<!-- id: legal.89-responsible-disclosure-standard -->

A security vulnerability disclosure policy SHOULD state:

- authorized testing scope
- prohibited testing
- reporting channel
- data-handling expectations
- good-faith conditions
- response expectations
- safe-harbor language if offered
- reward status
- confidentiality expectations

Do not promise immunity the organization lacks authority to grant.

---

# 90. Enterprise Customer Privacy Standard
<!-- id: legal.90-enterprise-customer-privacy-standard -->

SaaS providers SHOULD distinguish data roles for:

- account data
- billing data
- customer content
- end-user data
- telemetry
- support data
- product analytics

A provider may be a controller for some data and a processor for other data.

The Privacy Policy and DPA SHOULD reflect these distinctions.

---

# 91. Employee and Applicant Privacy Standard
<!-- id: legal.91-employee-and-applicant-privacy-standard -->

Employment-related data SHOULD have a dedicated notice where required or useful.

Address:

- application data
- background data
- interview notes
- assessment data
- device/security logs
- payroll/benefits
- monitoring
- retention
- sharing
- rights

Do not assume consumer-facing privacy notices fully cover workforce obligations.

---

# 92. Marketplace Standard
<!-- id: legal.92-marketplace-standard -->

Marketplaces SHOULD address:

- platform role
- seller role
- buyer role
- payment processing
- refunds
- prohibited goods
- seller verification
- taxes
- disputes
- user content
- reviews
- fraud
- IP complaints
- removal

Marketplace-specific consumer laws require separate review.

---

# 93. API / Developer Terms Standard
<!-- id: legal.93-api-developer-terms-standard -->

Developer terms SHOULD address:

- API license
- authentication
- rate limits
- security
- caching
- storage
- permitted data use
- prohibited data enrichment
- user consent
- deletion
- branding
- sublicensing
- competitive use
- scraping
- model training
- termination

Privacy restrictions SHOULD survive termination where necessary.

---

# 94. AI / Model API Terms Standard
<!-- id: legal.94-ai-model-api-terms-standard -->

AI service terms SHOULD address where relevant:

- input ownership
- output rights
- output limitations
- prohibited uses
- training use
- retention
- safety restrictions
- high-impact use
- human oversight
- rate limits
- model changes
- third-party content
- IP risks
- evaluation rights
- enterprise data controls

Claims about output ownership require jurisdiction-specific review.

---

# 95. Consumer Health Data Notice Standard
<!-- id: legal.95-consumer-health-data-notice-standard -->

If a service handles consumer health data outside traditional HIPAA coverage, conduct a state-law review.

A dedicated notice MAY be required.

Review:

- health-data definition
- inferred health data
- collection
- sharing
- sale
- consent
- geofencing restrictions
- deletion
- authorization
- rights

Do not assume non-HIPAA health data has no special regulation.

---

# 96. Financial Data Standard
<!-- id: legal.96-financial-data-standard -->

Financial products or services require sector-specific review.

Potential frameworks may include:

- GLBA
- FTC Safeguards Rule
- state financial privacy laws
- consumer credit laws
- payment-card requirements

A general Privacy Policy is not a substitute for required financial privacy notices.

---

# 97. Education Data Standard
<!-- id: legal.97-education-data-standard -->

Education products SHOULD evaluate:

- FERPA
- COPPA
- state student-privacy laws
- school contracts
- parental rights
- school consent
- advertising restrictions
- retention
- deletion
- data ownership

Do not shift statutory operator responsibilities to schools by contract where prohibited.

---

# 98. Location Data Standard
<!-- id: legal.98-location-data-standard -->

Precise geolocation requires enhanced review.

Disclose:

- collection
- granularity
- purpose
- background collection
- recipients
- retention
- advertising use
- user controls

Use precise location only when materially necessary.

---

# 99. Data Broker Standard
<!-- id: legal.99-data-broker-standard -->

If the business may qualify as a data broker, conduct dedicated registration and operational review.

Potential obligations may include:

- registration
- consumer deletion mechanisms
- opt-outs
- disclosure
- security
- reporting

Do not assume a standard Privacy Policy satisfies data-broker-specific law.

---

# 100. Government Request Standard
<!-- id: legal.100-government-request-standard -->

Privacy policies MAY explain lawful government disclosures.

Do not promise:

- never to disclose under legal process
- to notify users in every case
- to challenge every request

Internal procedures SHOULD cover:

- legal validation
- scope minimization
- escalation
- emergency requests
- user notice when lawful
- transparency reporting where appropriate

---

# 101. Business Transfer Standard
<!-- id: legal.101-business-transfer-standard -->

Privacy policies SHOULD address data handling during:

- merger
- acquisition
- financing
- reorganization
- bankruptcy
- asset sale

Material changes in controller or purpose may trigger additional notice or consent obligations.

---

# 102. Data Retention Table Standard
<!-- id: legal.102-data-retention-table-standard -->

Preferred privacy-policy format:

| Data Category | Primary Purpose | Typical Retention | Key Exceptions |
|---|---|---|---|
| Account data | Provide account | Account life + defined period | Legal/security |
| Billing records | Payments/tax | Defined statutory period | Disputes |
| Support records | Support | Defined period | Legal claims |
| Security logs | Fraud/security | Defined period | Incident investigation |
| Marketing data | Marketing | Until opt-out or defined period | Suppression list |

Values MUST reflect actual systems.

---

# 103. Privacy Rights Table Standard
<!-- id: legal.103-privacy-rights-table-standard -->

Where multiple regions apply, consider a jurisdiction table.

Example:

| Region | Key Rights | Request Method | Appeal / Regulator |
|---|---|---|---|
| EEA | Access, correction, erasure, restriction, portability, objection | Privacy portal | DPA complaint |
| California | Know/access, delete, correct, opt-out, limit where applicable | Privacy portal | CPPA/AG rights |
| Colorado | Access, correction, deletion, portability, opt-out | Privacy portal | Appeal where applicable |

The table MUST be kept current.

---

# 104. Policy Link Placement Standard
<!-- id: legal.104-policy-link-placement-standard -->

Public legal links SHOULD be available:

- website footer
- signup
- checkout
- account settings
- mobile app settings
- app-store listing where appropriate

Context-specific notices SHOULD also appear at the relevant collection or consent point.

---

# 105. Contact Standard
<!-- id: legal.105-contact-standard -->

Policies SHOULD provide a monitored contact method.

Potential contacts:

- privacy email
- legal email
- postal address
- privacy portal
- DPO
- accessibility contact
- DMCA agent
- security reporting address

Do not publish an unmonitored mailbox.

---

# 106. Legal Notice Accessibility Standard
<!-- id: legal.106-legal-notice-accessibility-standard -->

Legal documents MUST be usable with assistive technology.

Use:

- semantic headings
- real text
- accessible links
- keyboard navigation
- sufficient contrast
- logical reading order
- accessible forms
- descriptive labels

Do not provide required notices only as inaccessible PDFs.

---

# 107. Localization Standard
<!-- id: legal.107-localization-standard -->

If legal documents are translated:

- use professional legal-quality translation
- preserve defined terms
- preserve links
- preserve jurisdiction clauses
- identify controlling language where lawful
- maintain version parity

Machine translation SHOULD NOT be used without review for legally binding text.

---

# 108. Policy Consistency Standard
<!-- id: legal.108-policy-consistency-standard -->

The following MUST NOT conflict:

- Terms
- Privacy Policy
- Cookie Policy
- DPA
- Security Addendum
- marketing claims
- product UI
- app-store disclosures
- sales contracts
- vendor agreements
- help-center articles

Create a cross-document consistency review before each major release.

---

# 109. Product-to-Policy Review Standard
<!-- id: legal.109-product-to-policy-review-standard -->

Every material product launch SHOULD ask:

- Is new data collected?
- Is a new vendor used?
- Is a new purpose introduced?
- Is AI involved?
- Is data shared?
- Is data sold/shared under law?
- Is new consent required?
- Is a new age group affected?
- Is a new country launched?
- Does retention change?
- Does billing change?
- Does cancellation change?
- Does the Terms scope change?
- Is a new legal document required?

No product feature should rely on a privacy policy change as its only compliance control.

---

# 110. Marketing-to-Legal Review Standard
<!-- id: legal.110-marketing-to-legal-review-standard -->

Marketing SHOULD receive legal review for claims involving:

- privacy
- security
- encryption
- anonymity
- compliance
- certifications
- guarantees
- free trials
- price savings
- cancellation
- refund rights
- AI accuracy
- professional outcomes
- medical outcomes
- financial outcomes

Legal disclaimers cannot reliably cure a materially misleading headline.

---

# 111. Privacy-by-Design Standard
<!-- id: legal.111-privacy-by-design-standard -->

Privacy review SHOULD occur before implementation.

Product requirements SHOULD include:

- data necessity
- purpose
- consent
- notice
- access controls
- minimization
- retention
- deletion
- vendor sharing
- rights handling
- security
- logging

---

# 112. Data Protection Impact Assessment Standard
<!-- id: legal.112-data-protection-impact-assessment-standard -->

Conduct a DPIA or equivalent risk assessment when required or when processing creates elevated risk.

Potential triggers:

- systematic profiling
- large-scale sensitive data
- biometric identification
- location tracking
- children
- automated significant decisions
- novel surveillance
- large-scale monitoring

Document mitigations before launch.

---

# 113. California Risk Assessment Standard
<!-- id: legal.113-california-risk-assessment-standard -->

Covered California businesses SHOULD evaluate the CCPA's 2026 risk-assessment requirements for processing activities presenting significant risk to consumers' privacy.

Do not assume a generic DPIA automatically satisfies every California requirement.

---

# 114. California Automated Decisionmaking Standard
<!-- id: legal.114-california-automated-decisionmaking-standard -->

California's 2025-adopted CCPA regulations became effective January 1, 2026, with automated decisionmaking compliance requirements phased to begin January 1, 2027.

Organizations using qualifying ADMT SHOULD prepare before the applicable date by mapping:

- significant decisions
- ADMT systems
- input data
- notice requirements
- access rights
- opt-out rights
- exceptions
- risk assessments

COUNSEL REVIEW is required.

---

# 115. Security Incident Contract Standard
<!-- id: legal.115-security-incident-contract-standard -->

Enterprise agreements SHOULD define:

- security incident
- personal-data breach
- notification timing
- notification content
- cooperation
- investigation
- remediation
- subprocessor incidents
- regulator communication
- customer communication
- costs where negotiated

Do not promise an incident deadline the security program cannot reliably meet.

---

# 116. Data Deletion Contract Standard
<!-- id: legal.116-data-deletion-contract-standard -->

DPA and enterprise terms SHOULD specify:

- deletion during service
- deletion on termination
- export period
- backups
- legal retention
- certification
- subprocessors

External commitments SHOULD match infrastructure capabilities.

---

# 117. Audit Rights Standard
<!-- id: legal.117-audit-rights-standard -->

Audit clauses SHOULD balance:

- compliance evidence
- security risk
- confidentiality
- cost
- frequency
- scope
- third-party reports
- on-site inspections
- regulator rights

Do not provide unrestricted audit rights that create security or privacy risks unless intentionally negotiated.

---

# 118. Subprocessor Change Standard
<!-- id: legal.118-subprocessor-change-standard -->

If customers have subprocessor notice rights:

- publish current list
- provide notice through agreed channel
- define notice period
- define objection process
- maintain change history

The process MUST be operational, not merely contractual text.

---

# 119. Privacy Request Non-Discrimination Standard
<!-- id: legal.119-privacy-request-non-discrimination-standard -->

Users SHOULD NOT receive unlawful discriminatory treatment for exercising privacy rights.

Review:

- pricing
- access
- account quality
- loyalty programs
- feature restrictions

Any lawful financial incentive program requires separate analysis.

---

# 120. Dark Pattern Standard
<!-- id: legal.120-dark-pattern-standard -->

Legal and privacy interfaces MUST NOT manipulate users into choices they would not otherwise make.

Avoid:

- asymmetric choices
- confirm-shaming
- hidden cancellation
- repeated consent pressure
- confusing toggles
- false scarcity
- disguised advertising
- default opt-in where invalid
- obstructive privacy requests

---

# 121. Records Standard
<!-- id: legal.121-records-standard -->

Maintain evidence of compliance.

Potential records:

- policy versions
- assent logs
- consent logs
- opt-out logs
- GPC processing tests
- privacy request logs
- vendor contracts
- DPAs
- BAAs
- SCCs
- risk assessments
- DPIAs
- security assessments
- cookie scans
- subprocessor records
- legal review approvals
- training records

Retention itself must comply with minimization principles.

---

# 122. Annual Legal Policy Review Standard
<!-- id: legal.122-annual-legal-policy-review-standard -->

At least annually, review:

- Terms
- Privacy Policy
- Cookie Policy
- DPA
- subprocessor list
- cookie inventory
- rights workflow
- cancellation workflow
- refund workflow
- accessibility statement
- DMCA information

High-change businesses SHOULD review more frequently.

California privacy-policy obligations and other laws may impose specific update requirements.

---

# 123. Event-Triggered Review Standard
<!-- id: legal.123-event-triggered-review-standard -->

Review immediately when:

- entering a new jurisdiction
- adding a new data category
- adding sensitive data
- adding advertising
- beginning data sales/sharing
- changing AI training use
- launching a new model/provider
- adding biometrics
- adding children
- adding subscription billing
- changing cancellation
- acquiring a company
- changing legal entity
- adding major vendors
- changing international transfers
- experiencing a material privacy incident

---

# 124. Policy Approval Standard
<!-- id: legal.124-policy-approval-standard -->

Before production publication, obtain sign-off appropriate to the change.

Recommended approval roles:

- Legal
- Privacy
- Product
- Security
- Engineering
- Finance for billing terms
- Marketing for public claims
- Executive owner for material risk

---

# 125. Legal Publication QA Checklist
<!-- id: legal.125-legal-publication-qa-checklist -->

Before publishing:

- [ ] Correct legal entity
- [ ] Correct URLs
- [ ] Correct contact details
- [ ] Effective date included
- [ ] Version saved
- [ ] Terms acceptance mechanism tested
- [ ] Privacy practices verified
- [ ] Vendor list verified
- [ ] Cookie inventory verified
- [ ] Consent behavior tested
- [ ] GPC/UOOM behavior tested where applicable
- [ ] Data rights workflow tested
- [ ] Cancellation workflow tested
- [ ] Refund terms verified
- [ ] Subscription pricing verified
- [ ] Data retention verified
- [ ] International transfer language verified
- [ ] Child-user rules verified
- [ ] AI use verified
- [ ] Accessibility reviewed
- [ ] Cross-document inconsistencies removed
- [ ] Counsel review completed where required

---

# 126. Terms of Service QA Checklist
<!-- id: legal.126-terms-of-service-qa-checklist -->

- [ ] Contracting entity named
- [ ] Scope defined
- [ ] Eligibility defined
- [ ] Account duties defined
- [ ] Service description accurate
- [ ] License defined
- [ ] Acceptable use defined
- [ ] User content rights defined
- [ ] IP rights defined
- [ ] Payments accurate
- [ ] Subscription terms accurate
- [ ] Cancellation accurate
- [ ] Refunds accurate
- [ ] Suspension/termination defined
- [ ] Warranty language reviewed
- [ ] Liability language reviewed
- [ ] Indemnity reviewed
- [ ] Arbitration reviewed if used
- [ ] Governing law reviewed
- [ ] Change process defined
- [ ] Contact information correct
- [ ] Assent evidence retained

---

# 127. Privacy Policy QA Checklist
<!-- id: legal.127-privacy-policy-qa-checklist -->

- [ ] Controller/business identified
- [ ] Scope defined
- [ ] Data categories complete
- [ ] Sources complete
- [ ] Purposes complete
- [ ] Legal bases mapped where required
- [ ] Sensitive data identified
- [ ] AI processing disclosed
- [ ] Sharing disclosed
- [ ] Sale/sharing analysis completed
- [ ] Advertising disclosed
- [ ] Cookies disclosed
- [ ] Retention disclosed
- [ ] Security language accurate
- [ ] International transfers addressed
- [ ] Rights listed
- [ ] Rights request method works
- [ ] Children addressed
- [ ] GPC/UOOM addressed where applicable
- [ ] Automated decision-making addressed where applicable
- [ ] Effective date correct
- [ ] Contact method monitored

---

# 128. Cookie Compliance QA Checklist
<!-- id: legal.128-cookie-compliance-qa-checklist -->

- [ ] Tracker scan completed
- [ ] Unknown trackers investigated
- [ ] Categories accurate
- [ ] Strictly necessary category narrow
- [ ] Optional trackers blocked pre-consent where required
- [ ] Accept works
- [ ] Reject works
- [ ] Granular controls work
- [ ] Withdrawal works
- [ ] Choice persists
- [ ] Consent logs retained appropriately
- [ ] GPC interaction works
- [ ] Cookie Policy matches deployment
- [ ] Tag manager tested
- [ ] Mobile tested
- [ ] Third-party scripts tested

---

# 129. DPA QA Checklist
<!-- id: legal.129-dpa-qa-checklist -->

- [ ] Parties correct
- [ ] Roles correct
- [ ] Processing details complete
- [ ] Instructions defined
- [ ] Confidentiality included
- [ ] Security included
- [ ] Subprocessors addressed
- [ ] Rights assistance addressed
- [ ] Incident assistance addressed
- [ ] DPIA assistance addressed
- [ ] Deletion/return addressed
- [ ] Audit addressed
- [ ] Transfer mechanism addressed
- [ ] SCC modules correct where used
- [ ] Main agreement precedence reviewed
- [ ] Liability alignment reviewed

---

# 130. Subscription QA Checklist
<!-- id: legal.130-subscription-qa-checklist -->

- [ ] Price visible before purchase
- [ ] Billing frequency visible
- [ ] Auto-renewal visible
- [ ] Trial conversion visible
- [ ] Express consent captured
- [ ] Cancellation method simple
- [ ] Cancellation link works
- [ ] Cancellation confirmation sent
- [ ] Charges stop correctly
- [ ] Refund policy matches behavior
- [ ] Price-change workflow reviewed
- [ ] State-specific renewal requirements reviewed

---

# 131. High-Risk Privacy QA Checklist
<!-- id: legal.131-high-risk-privacy-qa-checklist -->

Apply enhanced review if any are true:

- [ ] children
- [ ] health
- [ ] biometrics
- [ ] precise location
- [ ] financial credentials
- [ ] government identifiers
- [ ] sexual orientation
- [ ] race/ethnicity
- [ ] religion
- [ ] union membership
- [ ] genetics
- [ ] private communications
- [ ] automated significant decisions
- [ ] large-scale profiling
- [ ] data brokerage

If checked, require documented risk assessment and COUNSEL REVIEW.

---

# 132. 100-Point Legal Policy Quality Score
<!-- id: legal.132-100-point-legal-policy-quality-score -->

This score is an internal QA framework, not a legal determination.

## Operational Accuracy — 20 points

- Policies match actual product: 5
- Data practices verified: 5
- Billing/cancellation verified: 3
- Vendor practices verified: 3
- Retention verified: 2
- Contact methods operational: 2

## Terms Quality — 15 points

- Entity/scope clear: 3
- Material terms conspicuous: 3
- User rights/obligations clear: 2
- Payment/subscription terms clear: 3
- Risk clauses reviewed: 2
- Assent evidence: 2

## Privacy Quality — 20 points

- Data categories/sources: 3
- Purposes/legal bases: 4
- Sharing/sale/ads: 4
- Rights: 3
- Retention: 2
- Sensitive data: 2
- International transfers: 2

## Consent / Tracking — 10 points

- Cookie inventory: 2
- Prior consent where required: 2
- Reject/withdraw controls: 2
- Consent records: 2
- GPC/UOOM support where applicable: 2

## Contracts / Vendors — 10 points

- Role classification: 2
- DPA/BAA where required: 3
- Subprocessor controls: 2
- Security contract terms: 2
- Transfer mechanism: 1

## User Rights / Operations — 10 points

- Request workflow: 3
- Verification: 2
- Deletion propagation: 2
- Appeals where required: 1
- Deadlines tracked: 2

## Security / Risk — 10 points

- Security program exists: 3
- Incident plan exists: 2
- Risk assessments: 2
- Sensitive-data controls: 2
- Breach matrix: 1

## Accessibility / Governance — 5 points

- Accessible legal pages: 1
- Version control: 1
- Change management: 1
- Annual review: 1
- Legal ownership: 1

---

# 133. Quality Thresholds
<!-- id: legal.133-quality-thresholds -->

Internal recommendation:

- 90–100 = strong publication readiness
- 80–89 = publish only after resolving identified legal gaps
- 70–79 = substantial review required
- 60–69 = weak compliance readiness
- below 60 = do not treat as production-ready

Any critical failure overrides the score.

---

# 134. Critical Publication Failures
<!-- id: legal.134-critical-publication-failures -->

Do not publish or rely on a legal-policy suite as production-ready if:

- the legal entity is wrong
- policies materially misdescribe data practices
- subscription terms misstate charges
- cancellation does not work as represented
- privacy rights channels do not work
- required consent is not collected
- optional trackers fire before required consent
- recognized opt-out signals are ignored where legally required
- sensitive data is undisclosed
- child-data obligations are unaddressed
- required DPA/BAA is missing
- international transfers lack a required lawful mechanism
- material legal terms are intentionally hidden
- clauses claim rights that applicable law prohibits waiving
- documents contain fabricated certifications or compliance claims

---

# 135. Recommended Public Legal Suite
<!-- id: legal.135-recommended-public-legal-suite -->

A typical SaaS / online-service site MAY use:

```text
/legal/terms
/legal/privacy
/legal/cookies
/legal/acceptable-use
/legal/dpa
/legal/subprocessors
/legal/security
/legal/accessibility
/legal/dmca
/legal/refunds
/legal/subscriptions
/privacy/choices
/privacy/request
```

Only publish pages that accurately correspond to the business.

---

# 136. Recommended Terms Outline
<!-- id: legal.136-recommended-terms-outline -->

```md
# Terms of Service

Effective Date: YYYY-MM-DD

## 1. Agreement to Terms
## 2. Contracting Entity
## 3. Eligibility
## 4. Accounts
## 5. Service
## 6. License and Restrictions
## 7. Acceptable Use
## 8. User Content
## 9. Intellectual Property
## 10. Third-Party Services
## 11. Fees and Payment
## 12. Subscriptions and Renewal
## 13. Cancellation and Refunds
## 14. Service Changes
## 15. Suspension and Termination
## 16. Disclaimers
## 17. Limitation of Liability
## 18. Indemnification
## 19. Dispute Resolution
## 20. Governing Law
## 21. Changes to Terms
## 22. General Terms
## 23. Contact
```

This is a drafting structure, not a substitute for jurisdiction-specific legal advice.

---

# 137. Recommended Privacy Policy Outline
<!-- id: legal.137-recommended-privacy-policy-outline -->

```md
# Privacy Policy

Effective Date: YYYY-MM-DD

## 1. Scope
## 2. Who We Are
## 3. Personal Data We Collect
## 4. Sources of Personal Data
## 5. How We Use Personal Data
## 6. Legal Bases
## 7. How We Share Personal Data
## 8. Advertising and Analytics
## 9. Cookies and Similar Technologies
## 10. AI and Automated Processing
## 11. Sensitive Personal Data
## 12. Data Retention
## 13. International Transfers
## 14. Security
## 15. Your Privacy Rights
## 16. California and U.S. State Privacy Rights
## 17. Children's Privacy
## 18. Changes to This Policy
## 19. Contact
```

---

# 138. Recommended Cookie Policy Outline
<!-- id: legal.138-recommended-cookie-policy-outline -->

```md
# Cookie Policy

Effective Date: YYYY-MM-DD

## 1. What Cookies Are
## 2. Technologies We Use
## 3. Strictly Necessary Technologies
## 4. Analytics
## 5. Functional Technologies
## 6. Advertising Technologies
## 7. Third-Party Technologies
## 8. Cookie Duration
## 9. Managing Your Choices
## 10. Global Privacy Control
## 11. Changes
## 12. Contact
```

---

# 139. Recommended DPA Outline
<!-- id: legal.139-recommended-dpa-outline -->

```md
# Data Processing Addendum

## 1. Definitions
## 2. Scope
## 3. Roles
## 4. Processing Instructions
## 5. Confidentiality
## 6. Security
## 7. Subprocessors
## 8. Data Subject Requests
## 9. Compliance Assistance
## 10. Security Incidents
## 11. Deletion and Return
## 12. Audits
## 13. International Transfers
## 14. Liability and Precedence

### Annex I — Processing Details
### Annex II — Security Measures
### Annex III — Subprocessors
### Annex IV — Transfer Mechanism
```

---

# 140. 2026 Legal Maintenance Notes
<!-- id: legal.140-2026-legal-maintenance-notes -->

As of this version date:

- California's updated CCPA regulations are effective January 1, 2026.
- Certain California automated-decisionmaking requirements are phased to begin January 1, 2027.
- California risk-assessment and cybersecurity-audit obligations have phased compliance requirements.
- Colorado requires covered controllers to recognize qualifying universal opt-out mechanisms; GPC is currently the recognized mechanism listed by the Colorado Attorney General.
- COPPA continues to impose child-specific notice, parental-consent, security, minimization, and retention obligations on covered operators, with FTC guidance updated in 2026.
- UK PECR guidance requires consent for cookies/similar technologies unless an exemption applies.
- GDPR transparency requires concise, intelligible notices that identify purposes, legal bases, retention, recipients, transfers, rights, and other required information.
- W3C recommends WCAG 2.2 as the current web-accessibility standard; specific legal requirements may reference different WCAG versions.
- U.S. DOJ Title II web/mobile accessibility requirements for state and local governments use WCAG 2.1 Level AA, with current compliance dates depending on entity size.

These notes are time-sensitive and MUST be revalidated during legal review.

---

# 141. Official Reference Sources
<!-- id: legal.141-official-reference-sources -->

The following official sources informed this standards framework.

## European Union — GDPR

European Commission — Information for individuals:  
https://commission.europa.eu/law/law-topic/data-protection/information-individuals_en

European Commission — Information businesses must give individuals:  
https://commission.europa.eu/law/law-topic/data-protection/rules-business-and-organisations/principles-gdpr/what-information-must-be-given-individuals-whose-data-collected_en

European Commission — GDPR obligations:  
https://commission.europa.eu/law/law-topic/data-protection/information-business-and-organisations/obligations_en

European Commission — Controller / processor obligations:  
https://commission.europa.eu/law/law-topic/data-protection/information-business-and-organisations/obligations/controllerprocessor/can-someone-else-process-data-my-organisations-behalf_en

European Commission — Standard Contractual Clauses:  
https://commission.europa.eu/publications/publications-standard-contractual-clauses-sccs_en

## California — CCPA / CPRA

California Privacy Protection Agency — Laws & Regulations:  
https://cppa.ca.gov/regulations/

California Privacy Protection Agency — 2025 CCPA updates and 2026 effective regulations:  
https://cppa.ca.gov/regulations/ccpa_updates.html

California Attorney General — CCPA:  
https://oag.ca.gov/privacy/ccpa

## Colorado — Privacy / Universal Opt-Out

Colorado Attorney General — Colorado Privacy Act:  
https://coag.gov/resources/colorado-privacy-act/

Colorado Attorney General — Universal Opt-Out / GPC:  
https://coag.gov/opt-out/

## United States — FTC / Consumer Protection

Federal Trade Commission — Data Security:  
https://www.ftc.gov/business-guidance/privacy-security/data-security

Federal Trade Commission — Start with Security:  
https://www.ftc.gov/business-guidance/resources/start-security-guide-business

Federal Trade Commission — COPPA Rule:  
https://www.ftc.gov/legal-library/browse/rules/childrens-online-privacy-protection-rule-coppa

Federal Trade Commission — COPPA Compliance Plan:  
https://www.ftc.gov/business-guidance/resources/childrens-online-privacy-protection-rule-six-step-compliance-plan-your-business

Federal Trade Commission — Restore Online Shoppers' Confidence Act:  
https://www.ftc.gov/legal-library/browse/statutes/restore-online-shoppers-confidence-act

Federal Trade Commission — Online Advertising and Marketing:  
https://www.ftc.gov/business-guidance/advertising-marketing/online-advertising-marketing

## United States — Copyright

U.S. Copyright Office — DMCA Section 512:  
https://www.copyright.gov/512/

U.S. Copyright Office — DMCA Designated Agent Directory:  
https://www.copyright.gov/dmca-directory/

## United States — HIPAA

HHS — Covered Entities and Business Associates:  
https://www.hhs.gov/hipaa/for-professionals/covered-entities/index.html

HHS — Business Associates:  
https://www.hhs.gov/hipaa/for-professionals/privacy/guidance/business-associates/index.html

HHS — Sample Business Associate Agreement Provisions:  
https://www.hhs.gov/hipaa/for-professionals/covered-entities/sample-business-associate-agreement-provisions/index.html

## United Kingdom — Cookies / PECR

Information Commissioner's Office — Cookies and Similar Technologies:  
https://ico.org.uk/for-organisations/direct-marketing-and-privacy-and-electronic-communications/guide-to-pecr/cookies-and-similar-technologies/

## Accessibility

W3C — WCAG 2.2:  
https://www.w3.org/TR/WCAG22/

W3C — WCAG Overview:  
https://www.w3.org/WAI/standards-guidelines/wcag/

U.S. Department of Justice — Title II Web Accessibility Rule:  
https://www.ada.gov/resources/2024-03-08-web-rule/

U.S. Department of Justice — Small Entity Compliance Guide:  
https://www.ada.gov/resources/small-entity-compliance-guide/

---

# 142. Final Standard
<!-- id: legal.142-final-standard -->

A high-quality legal policy system is not a collection of copied templates.

It is a controlled compliance system in which:

- Terms match the commercial relationship
- Privacy disclosures match actual data flows
- consent interfaces match applicable law
- cancellation matches subscription promises
- rights requests work operationally
- vendor contracts match data roles
- security promises match security controls
- accessibility claims are supportable
- legal documents remain versioned and reviewable
- product changes trigger legal review
- jurisdiction-specific requirements are tracked
- counsel reviews high-risk provisions

The strongest legal documents are accurate before they are comprehensive.

A short policy that truthfully describes a well-designed system is safer than a long policy that promises things the organization does not actually do.

# Control Plane Hooks
<!-- id: legal.control-plane-hooks -->

When this module is active, use `CONTROL_INDEX.md` to retrieve only the capability sections relevant to the current decision. Applicable capabilities include:

- **Regulated-industry detection** — `controls/03-industry-taxonomy-and-business-model-classification.md` (BQ-0106–BQ-0110)
- **Risk-overlay composition** — `controls/04-semantic-profiles-risk-and-context-overlays.md` (BQ-0126–BQ-0130)
- **Authenticity safeguards** — `controls/11-imagery-illustration-and-asset-generation.md` (BQ-0426–BQ-0430)
- **Claim-evidence pairing** — `controls/15-content-copy-and-terminology.md` (BQ-0571–BQ-0575)
- **Trust-signal authenticity** — `controls/16-conversion-trust-and-business-outcomes.md` (BQ-0606–BQ-0610)
- **Ethical-conversion guard** — `controls/16-conversion-trust-and-business-outcomes.md` (BQ-0636–BQ-0640)
- **Data-classification model** — `controls/19-security-privacy-and-legal-compliance.md` (BQ-0726–BQ-0730)
- **Privacy-by-design routing** — `controls/19-security-privacy-and-legal-compliance.md` (BQ-0741–BQ-0745)
- **Consent-integrity standard** — `controls/19-security-privacy-and-legal-compliance.md` (BQ-0746–BQ-0750)
- **Legal-claim boundary** — `controls/19-security-privacy-and-legal-compliance.md` (BQ-0751–BQ-0755)
- **Operational-risk routing** — `controls/23-jobs-sops-and-operational-systems.md` (BQ-0916–BQ-0920)

These hooks are routing pointers, not permission to preload the listed shards. Evidence Gates control pass/fail claims.
