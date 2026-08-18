<!--
Pack-Version: 4.0.0
Schema-Version: 3
Module: TERMINOLOGY
Module-Version: 1
Last-Updated: 2026-08-09
-->

# Terminology and Wording High-Quality Standards
<!-- id: terminology.terminology-and-wording-high-quality-standards -->

Version: 2026-08-09  
Status: Editorial, product, documentation, support, marketing, and policy wording standard  
Scope: Websites, applications, SaaS products, user interfaces, documentation, help centers, marketing, support, legal-adjacent copy, AI-generated content, internal knowledge bases, and customer communications

---

# 1. Purpose
<!-- id: terminology.1-purpose -->

This standard defines how terminology and wording should be selected, written, reviewed, maintained, and governed.

The goal is to make language:

- clear
- precise
- consistent
- concise
- understandable
- inclusive
- accessible
- professional
- trustworthy
- unambiguous
- reusable across channels
- easy for humans and machines to interpret

Terminology quality is not cosmetic.

Poor terminology causes:

- user confusion
- support volume
- inconsistent product behavior
- documentation errors
- legal ambiguity
- translation problems
- accessibility problems
- SEO fragmentation
- AI retrieval errors
- inconsistent analytics
- implementation mistakes

---

# 2. Standards Language
<!-- id: terminology.2-standards-language -->

Use these terms consistently:

- MUST = required
- MUST NOT = prohibited
- SHOULD = expected unless there is a documented reason not to
- SHOULD NOT = generally avoid
- MAY = optional enhancement

---

# 3. Core Terminology Principle
<!-- id: terminology.3-core-terminology-principle -->

One concept SHOULD have one preferred term.

One term SHOULD represent one concept whenever practical.

Avoid:

- multiple labels for the same thing
- one label that means different things in different contexts
- unnecessary synonyms
- informal aliases in formal product surfaces
- terminology that changes between UI, documentation, and support

Example:

Preferred:

`Workspace`

Avoid using all of these interchangeably for the same concept:

- workspace
- project space
- organization area
- account space
- team area

---

# 4. Canonical Term Standard
<!-- id: terminology.4-canonical-term-standard -->

Every important product, business, technical, or policy concept SHOULD have a canonical term.

A canonical term SHOULD define:

- preferred name
- definition
- capitalization
- plural form
- abbreviation
- allowed synonyms
- prohibited synonyms
- audience
- examples
- related concepts

---

# 5. Terminology Record Standard
<!-- id: terminology.5-terminology-record-standard -->

Maintain terminology records in a glossary or terminology database.

Recommended fields:

| Field | Description |
|---|---|
| Preferred Term | Approved wording |
| Definition | Exact meaning |
| Part of Speech | Noun, verb, adjective, etc. |
| Capitalization | Approved capitalization |
| Plural | Approved plural |
| Acronym | Approved abbreviation |
| Allowed Synonyms | Acceptable alternatives |
| Avoid | Disallowed or deprecated wording |
| Audience | User, admin, developer, legal, internal |
| Context | UI, docs, API, marketing, etc. |
| Related Terms | Associated concepts |
| Owner | Responsible team |
| Status | Approved, deprecated, proposed |
| Notes | Exceptions or edge cases |

---

# 6. Terminology Ownership Standard
<!-- id: terminology.6-terminology-ownership-standard -->

Every high-impact term SHOULD have an owner.

Potential owners:

- Product
- Design
- Content Design
- Documentation
- Marketing
- Legal
- Privacy
- Security
- Engineering
- Data
- Support

Ownership prevents terminology drift.

---

# 7. Definition Standard
<!-- id: terminology.7-definition-standard -->

Definitions MUST explain what a term means.

A strong definition SHOULD:

- identify the concept directly
- distinguish it from similar concepts
- avoid circular wording
- avoid unnecessary jargon
- use the preferred term consistently
- state important boundaries

Avoid:

`A workspace is a workspace used for organizing work.`

Prefer:

`A workspace is the top-level area that contains members, projects, settings, and billing for an organization.`

---

# 8. Circular Definition Standard
<!-- id: terminology.8-circular-definition-standard -->

Definitions MUST NOT define a term using the same undefined term.

Avoid:

`Authentication is the process of authenticating a user.`

Prefer:

`Authentication is the process of verifying that a user is who they claim to be.`

---

# 9. Scope Standard
<!-- id: terminology.9-scope-standard -->

Important terminology SHOULD define scope.

Clarify whether a term refers to:

- one user
- all users
- one account
- one organization
- one workspace
- one product
- all products
- a technical system
- a legal entity
- a billing entity
- a geographic region

---

# 10. Audience Standard
<!-- id: terminology.10-audience-standard -->

Terminology SHOULD reflect the audience's knowledge.

Use different wording when necessary for:

- general users
- administrators
- developers
- security teams
- legal teams
- executives
- customers
- internal staff

Do not expose internal implementation terms to users unless those terms help them complete a task.

---

# 11. User-Language Standard
<!-- id: terminology.11-user-language-standard -->

Prefer language users naturally understand.

Use internal terminology only when:

- the term is necessary
- the term is industry-standard
- users are likely to know it
- introducing the term improves consistency

Avoid forcing internal organizational language into customer-facing copy.

---

# 12. Familiarity Standard
<!-- id: terminology.12-familiarity-standard -->

Prefer familiar words over obscure alternatives.

Prefer:

- use
- start
- stop
- help
- change
- buy
- pay
- sign in
- send
- save

Avoid unnecessary replacements such as:

- utilize
- commence
- terminate
- facilitate
- modify
- procure
- remit
- authenticate

unless the technical or legal meaning requires them.

---

# 13. Precision Standard
<!-- id: terminology.13-precision-standard -->

Use the most precise term that remains understandable.

Avoid:

- thing
- stuff
- item
- object
- data
- information
- system
- platform
- tool

when a more specific term is available.

Example:

Avoid:

`Your data will be deleted.`

Prefer:

`Your uploaded files and project history will be deleted.`

---

# 14. Ambiguity Standard
<!-- id: terminology.14-ambiguity-standard -->

Wording MUST avoid ambiguity when a user could reasonably interpret a statement in more than one material way.

Ambiguity is especially unacceptable in:

- pricing
- permissions
- deletion
- billing
- subscriptions
- privacy
- security
- legal rights
- destructive actions
- account ownership
- access control
- data sharing

---

# 15. Pronoun Reference Standard
<!-- id: terminology.15-pronoun-reference-standard -->

Pronouns SHOULD have a clear referent.

Avoid:

`When the admin removes the user from the group, they lose access.`

Better:

`When an admin removes a user from the group, the user loses access.`

---

# 16. This / That / It Standard
<!-- id: terminology.16-this-that-it-standard -->

Avoid ambiguous references such as:

- this
- that
- it
- these
- those
- they

when the referenced subject is not immediately obvious.

Prefer explicit nouns in high-risk instructions.

---

# 17. One Meaning per Term Standard
<!-- id: terminology.17-one-meaning-per-term-standard -->

A term SHOULD NOT be overloaded with multiple unrelated meanings.

If `Account` means:

- login identity
- billing relationship
- customer organization

the product SHOULD rename these concepts.

Possible alternatives:

- User
- Billing Account
- Organization

---

# 18. Synonym Control Standard
<!-- id: terminology.18-synonym-control-standard -->

Synonyms SHOULD be controlled rather than freely varied.

For a core concept:

- select one preferred term
- document approved alternatives
- document prohibited alternatives
- enforce the preferred term across product surfaces

Synonym variation may improve prose, but consistency is more important for product concepts.

---

# 19. Deprecated Term Standard
<!-- id: terminology.19-deprecated-term-standard -->

Deprecated terminology MUST be tracked.

A deprecated term SHOULD include:

- replacement term
- deprecation date
- affected surfaces
- migration owner
- removal status

Do not silently maintain old terminology indefinitely.

---

# 20. Naming Collision Standard
<!-- id: terminology.20-naming-collision-standard -->

Avoid names that conflict with:

- existing product names
- feature names
- technical standards
- common industry meanings
- legal terms
- reserved words
- competitor trademarks
- geographic terms

Perform a naming collision review before launching important terms.

---

# 21. Feature Naming Standard
<!-- id: terminology.21-feature-naming-standard -->

Feature names SHOULD:

- describe the function
- be distinguishable from other features
- be easy to pronounce
- be easy to search
- be easy to translate
- avoid unnecessary cleverness
- avoid internal project codenames

A user SHOULD understand what a feature probably does from its name.

---

# 22. Product Naming Standard
<!-- id: terminology.22-product-naming-standard -->

Product names SHOULD have documented:

- official name
- short name
- capitalization
- punctuation
- article usage
- possessive form
- pluralization policy
- trademark treatment if relevant

---

# 23. Capitalization Standard
<!-- id: terminology.23-capitalization-standard -->

Capitalization MUST be consistent.

Use title case only when the style system requires it.

Use sentence case for most interface text unless a defined brand style says otherwise.

Preferred UI pattern:

`Create workspace`

Avoid:

`Create Workspace`

unless title case is the established interface standard.

---

# 24. Proper Noun Standard
<!-- id: terminology.24-proper-noun-standard -->

Capitalize:

- official product names
- company names
- formal program names
- official feature names when treated as proper nouns
- geographic proper nouns

Do not capitalize common nouns merely to make them appear important.

Avoid:

`Your Account Administrator can access your Data.`

Prefer:

`Your account administrator can access your data.`

---

# 25. Acronym Standard
<!-- id: terminology.25-acronym-standard -->

Spell out an acronym on first meaningful use unless the acronym is universally familiar to the intended audience.

Example:

`single sign-on (SSO)`

Then:

`SSO`

Do not alternate between multiple acronym forms.

---

# 26. Acronym Overload Standard
<!-- id: terminology.26-acronym-overload-standard -->

Avoid excessive acronyms.

If a sentence contains several unfamiliar acronyms, rewrite it.

Do not create acronyms solely to shorten a phrase that appears only a few times.

---

# 27. Abbreviation Standard
<!-- id: terminology.27-abbreviation-standard -->

Abbreviations SHOULD be:

- standard
- understandable
- consistent
- documented

Avoid ambiguous abbreviations such as:

- acct
- auth
- config
- org
- env
- req
- msg

in user-facing language unless the audience expects them.

---

# 28. Plural Standard
<!-- id: terminology.28-plural-standard -->

Define plural forms for important terms.

Examples:

- API → APIs
- FAQ → FAQs
- policy → policies
- category → categories

Avoid apostrophes for ordinary plurals.

---

# 29. Possessive Standard
<!-- id: terminology.29-possessive-standard -->

Use normal possessive grammar.

Examples:

- user's settings
- users' settings
- company's policy
- API's response only when the API itself possesses something

Avoid apostrophes for plurals.

---

# 30. Verb Standard
<!-- id: terminology.30-verb-standard -->

Prefer strong, specific verbs.

Prefer:

- create
- delete
- download
- send
- approve
- reject
- publish
- archive
- restore
- connect
- disconnect

Avoid vague verbs such as:

- perform
- execute
- process
- handle
- manage
- do

when a more precise verb exists.

---

# 31. Action Label Standard
<!-- id: terminology.31-action-label-standard -->

Buttons and action labels SHOULD begin with a verb.

Good:

- Save changes
- Delete account
- Invite member
- Download report
- Retry payment
- View invoice

Avoid vague labels:

- Submit
- Continue
- Proceed
- Okay
- Yes
- Confirm

when a specific action label is practical.

---

# 32. Destructive Action Standard
<!-- id: terminology.32-destructive-action-standard -->

Destructive actions MUST use explicit wording.

Prefer:

`Delete workspace`

Avoid:

`Remove`

if the action permanently deletes data.

Destructive confirmation text SHOULD state the consequence.

---

# 33. Reversible vs Irreversible Standard
<!-- id: terminology.33-reversible-vs-irreversible-standard -->

Terminology MUST distinguish reversible and irreversible actions.

Use separate terms such as:

- archive
- disable
- deactivate
- remove
- disconnect
- revoke
- delete
- permanently delete

Do not use them interchangeably.

---

# 34. Delete Standard
<!-- id: terminology.34-delete-standard -->

Use `delete` only when the item is intended to be removed.

If deletion is delayed or recoverable, clarify:

- moves to trash
- scheduled for deletion
- recoverable for 30 days
- permanently deleted after retention period

---

# 35. Remove Standard
<!-- id: terminology.35-remove-standard -->

Use `remove` when an item or relationship is detached but not necessarily destroyed.

Examples:

- remove member from team
- remove tag
- remove payment method

Do not use `remove` when data is permanently destroyed.

---

# 36. Archive Standard
<!-- id: terminology.36-archive-standard -->

Use `archive` when the item remains stored but becomes inactive or hidden from primary workflows.

State whether archived content:

- remains searchable
- remains billable
- remains accessible
- can be restored

---

# 37. Deactivate Standard
<!-- id: terminology.37-deactivate-standard -->

Use `deactivate` for reversible account or feature disablement.

Do not use `deactivate` as a euphemism for deletion.

---

# 38. Disable Standard
<!-- id: terminology.38-disable-standard -->

Use `disable` for functionality or access that can generally be restored.

Examples:

- disable notifications
- disable API key
- disable account

---

# 39. Revoke Standard
<!-- id: terminology.39-revoke-standard -->

Use `revoke` when withdrawing a permission, authorization, token, credential, or access grant.

Examples:

- revoke API key
- revoke access
- revoke consent

---

# 40. Disconnect Standard
<!-- id: terminology.40-disconnect-standard -->

Use `disconnect` for ending a connection or integration without deleting the underlying external account.

---

# 41. Cancel Standard
<!-- id: terminology.41-cancel-standard -->

Use `cancel` for:

- subscription termination
- scheduled action termination
- transactional abandonment

Do not use `cancel` when an irreversible delete occurs.

---

# 42. Close Account Standard
<!-- id: terminology.42-close-account-standard -->

Avoid `close account` unless the operational meaning is clear.

Clarify whether closing:

- disables login
- cancels billing
- deletes data
- preserves invoices
- preserves legal records

Prefer more precise language when possible.

---

# 43. Sign In / Log In Standard
<!-- id: terminology.43-sign-in-log-in-standard -->

Choose one primary term.

Recommended:

`Sign in`

Use consistently across:

- buttons
- documentation
- emails
- support

Do not alternate between:

- sign in
- log in
- login
- access account

without reason.

Use `login` primarily as a noun or adjective when needed.

---

# 44. Sign Up Standard
<!-- id: terminology.44-sign-up-standard -->

Choose one preferred account-creation phrase.

Recommended options:

- Create account
- Sign up

`Create account` is usually more explicit.

Use the same term across onboarding.

---

# 45. Member / User / Customer Standard
<!-- id: terminology.45-member-user-customer-standard -->

Define these separately.

Example:

- User = individual who uses the product
- Member = user belonging to a workspace
- Customer = person or organization that purchases the service

Do not use them interchangeably if rights differ.

---

# 46. Account / Organization / Workspace Standard
<!-- id: terminology.46-account-organization-workspace-standard -->

These terms MUST have distinct meanings if they coexist.

Example:

- Account = individual login identity
- Organization = customer entity
- Workspace = operational area within an organization

Document the relationship.

---

# 47. Admin Standard
<!-- id: terminology.47-admin-standard -->

Define admin roles explicitly.

Avoid generic `admin` when multiple roles exist.

Prefer:

- organization admin
- workspace admin
- billing admin
- security admin

---

# 48. Owner Standard
<!-- id: terminology.48-owner-standard -->

Use `owner` only when ownership has a defined meaning.

Clarify whether the owner controls:

- billing
- deletion
- permissions
- transfers
- legal account ownership

Do not use `owner` merely as a synonym for admin.

---

# 49. Permission Standard
<!-- id: terminology.49-permission-standard -->

Use `permission` for a specific allowed action.

Examples:

- view
- edit
- delete
- invite
- export

Avoid calling broad user categories `permissions` when they are roles.

---

# 50. Role Standard
<!-- id: terminology.50-role-standard -->

Use `role` for a predefined collection of permissions.

Examples:

- Viewer
- Editor
- Admin

Do not use `role` for individual permission toggles.

---

# 51. Access Standard
<!-- id: terminology.51-access-standard -->

Use `access` to describe ability to enter, view, use, or interact with a resource.

Clarify:

- view access
- edit access
- admin access
- temporary access

when relevant.

---

# 52. Authorization Standard
<!-- id: terminology.52-authorization-standard -->

Use `authorization` for determining what an authenticated subject is permitted to do.

Do not use `authentication` and `authorization` interchangeably.

---

# 53. Authentication Standard
<!-- id: terminology.53-authentication-standard -->

Use `authentication` for verifying identity.

Examples:

- password authentication
- SSO authentication
- MFA

---

# 54. Verification Standard
<!-- id: terminology.54-verification-standard -->

Use `verification` when confirming that information is valid or accurate.

Examples:

- email verification
- identity verification
- payment verification

Do not automatically substitute `authentication`.

---

# 55. Security Terminology Standard
<!-- id: terminology.55-security-terminology-standard -->

Security language MUST be technically accurate.

Distinguish:

- authentication
- authorization
- encryption
- hashing
- tokenization
- anonymization
- pseudonymization
- access control
- monitoring
- logging
- backup
- recovery

Do not simplify these into incorrect equivalents.

---

# 56. Encryption Standard
<!-- id: terminology.56-encryption-standard -->

Use `encrypted` only when encryption is actually applied.

Clarify when necessary:

- encrypted in transit
- encrypted at rest
- end-to-end encrypted

Do not use `encrypted` as a general synonym for secure.

---

# 57. Anonymous Standard
<!-- id: terminology.57-anonymous-standard -->

Use `anonymous` only when data cannot reasonably be linked to an identifiable person under the intended standard.

Avoid calling pseudonymous or de-identified data anonymous without review.

---

# 58. De-Identified Standard
<!-- id: terminology.58-de-identified-standard -->

Use `de-identified` when identifiers have been removed or transformed but legal or technical re-identification considerations may remain.

Do not equate it automatically with anonymous.

---

# 59. Personal Data Standard
<!-- id: terminology.59-personal-data-standard -->

Use the legally appropriate preferred term for the jurisdiction.

Possible terms:

- personal data
- personal information
- personally identifiable information

Do not use them interchangeably in legal content without understanding their definitions.

For general non-legal product wording, `personal information` may be easier for users.

---

# 60. Sensitive Data Standard
<!-- id: terminology.60-sensitive-data-standard -->

Do not use `sensitive data` casually when a jurisdiction-specific legal definition applies.

Where legal precision matters, use the defined statutory term.

---

# 61. Data vs Content Standard
<!-- id: terminology.61-data-vs-content-standard -->

Define:

- data = structured or unstructured information processed by the service
- content = files, text, media, messages, or materials submitted or generated

Do not call all user-provided materials `data` if `content` is clearer.

---

# 62. File / Document / Record Standard
<!-- id: terminology.62-file-document-record-standard -->

Distinguish:

- file = stored digital object
- document = user-recognizable content artifact
- record = stored entry or evidence
- attachment = file connected to another object

Use the term that matches the user's mental model.

---

# 63. Save Standard
<!-- id: terminology.63-save-standard -->

Use `save` when changes are persisted.

Do not label a button `Save` if the action also:

- publishes
- submits
- sends
- charges
- deletes
- creates an irreversible change

Use the actual action.

---

# 64. Submit Standard
<!-- id: terminology.64-submit-standard -->

Use `submit` only when content is sent for processing, review, or approval.

Avoid generic `Submit` if a more specific action exists.

Prefer:

- Send request
- Place order
- Apply
- Create account
- Publish article

---

# 65. Publish Standard
<!-- id: terminology.65-publish-standard -->

Use `publish` when content becomes available to its intended audience.

Clarify visibility when needed:

- publish publicly
- publish to workspace
- publish to team

---

# 66. Draft Standard
<!-- id: terminology.66-draft-standard -->

Use `draft` for content that is not yet published or finalized.

Do not use `draft` if other users can already rely on it as final.

---

# 67. Sync Standard
<!-- id: terminology.67-sync-standard -->

Use `sync` when systems exchange and reconcile state.

Do not use `sync` as a vague synonym for upload, import, backup, or refresh.

---

# 68. Import Standard
<!-- id: terminology.68-import-standard -->

Use `import` when data enters the system from another source.

---

# 69. Export Standard
<!-- id: terminology.69-export-standard -->

Use `export` when data is packaged for use outside the current system.

Clarify:

- file format
- scope
- date range
- permissions
- included data

---

# 70. Download Standard
<!-- id: terminology.70-download-standard -->

Use `download` when transferring a file to the user's device.

Do not use `export` if the action simply downloads an existing file.

---

# 71. Upload Standard
<!-- id: terminology.71-upload-standard -->

Use `upload` when transferring a file from the user's device to the service.

---

# 72. Copy / Duplicate Standard
<!-- id: terminology.72-copy-duplicate-standard -->

Distinguish:

- copy = create or place a copy
- duplicate = create a new equivalent object in the same system

Use the term matching behavior.

---

# 73. Create / Add Standard
<!-- id: terminology.73-create-add-standard -->

Use `create` when making a new standalone object.

Use `add` when inserting something into an existing collection.

Examples:

- Create project
- Add member
- Add payment method

---

# 74. Edit / Update Standard
<!-- id: terminology.74-edit-update-standard -->

Use `edit` when the user modifies content.

Use `update` when the system or user applies new values or versions.

Avoid inconsistent use if both actions are identical.

---

# 75. Change Standard
<!-- id: terminology.75-change-standard -->

Use `change` for user-facing language when it is clearer than `modify`.

Examples:

- Change password
- Change plan
- Change email

---

# 76. Manage Standard
<!-- id: terminology.76-manage-standard -->

Use `manage` only when the destination provides multiple related controls.

Good:

`Manage members`

Avoid:

`Manage password`

if the only action is changing the password.

---

# 77. Settings Standard
<!-- id: terminology.77-settings-standard -->

Use `settings` for user-configurable behavior.

Do not hide primary actions or important legal choices under vague settings menus when they need prominent access.

---

# 78. Preferences Standard
<!-- id: terminology.78-preferences-standard -->

Use `preferences` for personal choices that do not fundamentally control system behavior or permissions.

Examples:

- display preferences
- notification preferences

---

# 79. Configuration Standard
<!-- id: terminology.79-configuration-standard -->

Use `configuration` primarily for technical or administrative audiences.

For general users, prefer:

- settings
- setup
- options

---

# 80. Setup Standard
<!-- id: terminology.80-setup-standard -->

Use `setup` as a noun/adjective and `set up` as a verb.

Examples:

- Setup guide
- Set up your account

---

# 81. Backup Standard
<!-- id: terminology.81-backup-standard -->

Use `backup` only when a recoverable copy exists.

Do not describe replication, syncing, or snapshots as backups unless recovery expectations match.

---

# 82. Restore Standard
<!-- id: terminology.82-restore-standard -->

Use `restore` when returning data or configuration to a prior saved state.

Clarify whether restoration overwrites current data.

---

# 83. Recovery Standard
<!-- id: terminology.83-recovery-standard -->

Use `recovery` for regaining access, data, or service after loss or failure.

Examples:

- account recovery
- disaster recovery
- file recovery

---

# 84. Version Standard
<!-- id: terminology.84-version-standard -->

Use `version` for a specific identifiable state of software, content, API, model, or document.

Where version affects behavior, include the identifier.

---

# 85. Update / Upgrade Standard
<!-- id: terminology.85-update-upgrade-standard -->

Distinguish:

- update = newer revision, often minor or routine
- upgrade = move to a higher edition, tier, or major capability

Avoid using `upgrade` merely as persuasive marketing language if no meaningful tier change occurs.

---

# 86. Free Standard
<!-- id: terminology.86-free-standard -->

Use `free` only when the user does not pay money for the advertised item or service and material conditions are clearly disclosed.

Do not call a trial `free` without clearly stating:

- trial duration
- conversion
- required payment method
- renewal price

---

# 87. Unlimited Standard
<!-- id: terminology.87-unlimited-standard -->

Use `unlimited` only when no meaningful usage limit applies.

If subject to:

- fair-use limits
- throttling
- quotas
- hidden caps
- contractual restrictions

the wording MUST qualify the claim.

---

# 88. Guaranteed Standard
<!-- id: terminology.88-guaranteed-standard -->

Avoid `guaranteed` unless a defined guarantee actually exists.

A guarantee SHOULD specify:

- outcome
- conditions
- duration
- remedy

---

# 89. Secure Standard
<!-- id: terminology.89-secure-standard -->

`Secure` is a broad claim.

Prefer precise statements such as:

- supports MFA
- encrypts data in transit
- uses role-based access controls

Avoid:

`completely secure`

---

# 90. Safe Standard
<!-- id: terminology.90-safe-standard -->

Use `safe` cautiously.

Avoid absolute claims about:

- financial safety
- medical safety
- cybersecurity
- child safety
- physical safety

unless the scope is defined and supportable.

---

# 91. Best Standard
<!-- id: terminology.91-best-standard -->

Avoid unsupported superlatives:

- best
- #1
- leading
- fastest
- safest
- most trusted
- most accurate

Use them only when evidence and comparison scope are clear.

---

# 92. Easy Standard
<!-- id: terminology.92-easy-standard -->

Avoid claiming something is `easy` when difficulty depends on user experience or circumstances.

Prefer concrete wording:

`Takes about three steps`

instead of:

`It's easy.`

---

# 93. Simple Standard
<!-- id: terminology.93-simple-standard -->

Use `simple` when describing structure, not as a judgment about the user's ability.

Prefer:

`Use the three-step setup`

over:

`Setup is simple.`

---

# 94. Obviously / Simply / Just Standard
<!-- id: terminology.94-obviously-simply-just-standard -->

Avoid:

- obviously
- simply
- just
- merely
- clearly

when they minimize user difficulty or hide complexity.

Example:

Avoid:

`Simply configure your DNS records.`

Prefer:

`Add the following DNS records.`

---

# 95. Error Message Standard
<!-- id: terminology.95-error-message-standard -->

Error messages SHOULD explain:

1. what happened
2. why, when known
3. what the user can do next

Avoid:

`Invalid input.`

Prefer:

`Enter a valid email address, such as name@example.com.`

---

# 96. Error Tone Standard
<!-- id: terminology.96-error-tone-standard -->

Do not blame the user.

Avoid:

`You entered the wrong password.`

Prefer:

`The password doesn't match this account.`

---

# 97. Unknown Error Standard
<!-- id: terminology.97-unknown-error-standard -->

When the exact cause is unknown, say so accurately.

Preferred:

`We couldn't save your changes. Try again.`

Avoid fabricated explanations.

---

# 98. Success Message Standard
<!-- id: terminology.98-success-message-standard -->

Success messages SHOULD confirm the completed action.

Examples:

- Changes saved
- Invitation sent
- Subscription canceled
- Report downloaded

Avoid generic:

`Success!`

when the action can be named.

---

# 99. Warning Standard
<!-- id: terminology.99-warning-standard -->

Use warnings only for meaningful risk.

Warnings SHOULD identify:

- risk
- consequence
- action

Do not overuse warning language, or users will ignore it.

---

# 100. Confirmation Standard
<!-- id: terminology.100-confirmation-standard -->

Confirmation dialogs SHOULD state the exact action and consequence.

Example:

`Delete "Q3 Forecast"? This permanently deletes the file for everyone in the workspace.`

Buttons:

- Cancel
- Delete file

---

# 101. Notification Standard
<!-- id: terminology.101-notification-standard -->

Notifications SHOULD state:

- event
- subject
- relevant consequence
- next action if needed

Avoid vague notifications such as:

`Something changed.`

---

# 102. Empty State Standard
<!-- id: terminology.102-empty-state-standard -->

Empty states SHOULD explain:

- what the area contains
- why it is empty
- what the user can do next

---

# 103. Placeholder Standard
<!-- id: terminology.103-placeholder-standard -->

Placeholder text MUST NOT replace labels.

Use placeholders only for:

- examples
- expected format
- optional hints

---

# 104. Form Label Standard
<!-- id: terminology.104-form-label-standard -->

Labels SHOULD describe the requested value.

Prefer:

`Work email`

Avoid:

`Email address input field`

---

# 105. Required Field Standard
<!-- id: terminology.105-required-field-standard -->

Required fields SHOULD be identifiable consistently.

Do not rely only on color.

If most fields are required, MAY label optional fields instead.

---

# 106. Helper Text Standard
<!-- id: terminology.106-helper-text-standard -->

Helper text SHOULD add information not already obvious from the label.

Good:

`Use at least 12 characters.`

Avoid:

`Enter your password here.`

---

# 107. Tooltip Standard
<!-- id: terminology.107-tooltip-standard -->

Tooltips SHOULD explain secondary detail.

Do not hide critical requirements or legal disclosures only in tooltips.

---

# 108. Link Text Standard
<!-- id: terminology.108-link-text-standard -->

Links SHOULD describe their destination or action.

Prefer:

`View billing history`

Avoid:

`Click here`

---

# 109. Navigation Label Standard
<!-- id: terminology.109-navigation-label-standard -->

Navigation labels SHOULD be:

- short
- distinct
- predictable
- user-oriented

Avoid overlapping labels such as:

- Insights
- Analytics
- Reports
- Dashboard

unless each has a clearly different purpose.

---

# 110. Menu Label Standard
<!-- id: terminology.110-menu-label-standard -->

Menu labels SHOULD use nouns for destinations and verbs for actions.

Examples:

Destinations:

- Billing
- Members
- Security

Actions:

- Invite member
- Export data
- Delete workspace

---

# 111. Breadcrumb Standard
<!-- id: terminology.111-breadcrumb-standard -->

Breadcrumb labels SHOULD match page or taxonomy terminology.

Do not introduce alternate names solely in breadcrumbs.

---

# 112. Search Terminology Standard
<!-- id: terminology.112-search-terminology-standard -->

Search labels SHOULD align with the user's concept.

Use:

`Search projects`

if only projects are searchable.

Avoid:

`Search`

when scope is ambiguous.

---

# 113. Filter Standard
<!-- id: terminology.113-filter-standard -->

Filters SHOULD use terms that describe the property being filtered.

Examples:

- Status
- Owner
- Date created
- File type

---

# 114. Sort Standard
<!-- id: terminology.114-sort-standard -->

Sort labels SHOULD define direction or logic.

Examples:

- Newest first
- Oldest first
- Name A–Z
- Highest price

Avoid:

- Ascending
- Descending

for general users unless the context makes the property obvious.

---

# 115. Status Terminology Standard
<!-- id: terminology.115-status-terminology-standard -->

Statuses MUST be mutually understandable.

Example lifecycle:

- Draft
- In review
- Approved
- Published
- Archived

Avoid overlapping statuses:

- Active
- Open
- Live
- Enabled

unless they mean different things.

---

# 116. State vs Status Standard
<!-- id: terminology.116-state-vs-status-standard -->

Use `state` primarily for technical system representations.

Use `status` for user-visible progression or condition.

---

# 117. Active Standard
<!-- id: terminology.117-active-standard -->

Define what `active` means.

Possible meanings:

- enabled
- currently subscribed
- recently used
- online
- published
- available

Do not use `active` without a documented definition.

---

# 118. Pending Standard
<!-- id: terminology.118-pending-standard -->

`Pending` SHOULD identify what is pending.

Prefer:

- Payment pending
- Approval pending
- Invitation pending

instead of only:

`Pending`

when ambiguity exists.

---

# 119. Complete / Completed Standard
<!-- id: terminology.119-complete-completed-standard -->

Use:

- complete = adjective
- completed = past action/status when appropriate

Example:

`Profile complete`

`Payment completed`

---

# 120. Failed Standard
<!-- id: terminology.120-failed-standard -->

Use `failed` when a process attempted and did not succeed.

Provide next action when possible.

---

# 121. Expired Standard
<!-- id: terminology.121-expired-standard -->

Use `expired` when a time-bound validity period ended.

Examples:

- token expired
- trial expired
- card expired

---

# 122. Disabled Standard
<!-- id: terminology.122-disabled-standard -->

Use `disabled` when functionality or access was intentionally turned off.

Do not use `disabled` as a status for people.

---

# 123. Availability Standard
<!-- id: terminology.123-availability-standard -->

Distinguish:

- available
- unavailable
- temporarily unavailable
- sold out
- out of stock
- disabled
- unsupported

Do not use one term for all cases.

---

# 124. Supported Standard
<!-- id: terminology.124-supported-standard -->

Use `supported` when the organization or product officially provides compatibility or assistance.

Do not use it to mean merely technically possible.

---

# 125. Compatible Standard
<!-- id: terminology.125-compatible-standard -->

Use `compatible` when systems can work together.

Compatibility does not imply official support.

---

# 126. Beta Standard
<!-- id: terminology.126-beta-standard -->

Use `beta` only when the release status has a defined meaning.

Beta wording SHOULD explain material limitations where relevant.

---

# 127. Preview Standard
<!-- id: terminology.127-preview-standard -->

Use `preview` for early access intended primarily for evaluation.

Define:

- stability
- support
- data protections
- pricing
- change risk

---

# 128. Experimental Standard
<!-- id: terminology.128-experimental-standard -->

Use `experimental` when functionality may change substantially or has uncertain behavior.

Do not market experimental features as fully production-ready.

---

# 129. Deprecated Standard
<!-- id: terminology.129-deprecated-standard -->

Use `deprecated` when functionality remains available but should no longer be used for new implementations.

State replacement and timeline when possible.

---

# 130. Legacy Standard
<!-- id: terminology.130-legacy-standard -->

Use `legacy` for older systems or behavior still supported for compatibility.

Do not use `legacy` as a vague negative label.

---

# 131. End-of-Life Standard
<!-- id: terminology.131-end-of-life-standard -->

Use `end of life` when official support or availability ends.

Clarify:

- date
- impact
- migration path

---

# 132. Price Terminology Standard
<!-- id: terminology.132-price-terminology-standard -->

Pricing language MUST distinguish:

- price
- fee
- rate
- charge
- tax
- discount
- credit
- refund

Do not call a mandatory fee a tax unless it is actually a tax.

---

# 133. Discount Standard
<!-- id: terminology.133-discount-standard -->

A discount SHOULD specify its comparison basis.

Examples:

- 20% off standard monthly price
- Save $120 per year compared with monthly billing

Avoid misleading reference prices.

---

# 134. Starting At Standard
<!-- id: terminology.134-starting-at-standard -->

Use `starting at` only when a meaningful number of customers can reasonably qualify for the stated starting price.

Disclose material conditions.

---

# 135. From Standard
<!-- id: terminology.135-from-standard -->

Use `from` similarly to `starting at`.

Do not use it to advertise a rare or unavailable price.

---

# 136. Per User / Per Seat Standard
<!-- id: terminology.136-per-user-per-seat-standard -->

Choose one term and define the billing unit.

Do not alternate among:

- user
- member
- seat
- license

if they affect billing differently.

---

# 137. Trial Standard
<!-- id: terminology.137-trial-standard -->

Use `trial` for temporary access before a normal paid or restricted state.

Clarify:

- duration
- included features
- payment requirement
- conversion
- cancellation

---

# 138. Plan Standard
<!-- id: terminology.138-plan-standard -->

Use `plan` for a defined package of pricing and entitlements.

Avoid mixing:

- plan
- package
- tier
- edition

unless they intentionally mean different things.

---

# 139. Tier Standard
<!-- id: terminology.139-tier-standard -->

Use `tier` for a level in a hierarchy when useful.

Example:

- Free
- Pro
- Enterprise

If `plan` is already canonical, avoid unnecessary `tier`.

---

# 140. Billing Cycle Standard
<!-- id: terminology.140-billing-cycle-standard -->

Use explicit periods:

- monthly
- annual
- every 30 days
- calendar month

Do not use vague wording such as:

`regular billing cycle`

when users need exact timing.

---

# 141. Renewal Standard
<!-- id: terminology.141-renewal-standard -->

Use `renew` only when a service or commitment begins another term.

State automatic renewal explicitly where applicable.

---

# 142. Credit Standard
<!-- id: terminology.142-credit-standard -->

Use `credit` when value is applied to an account rather than returned as cash.

Do not call account credit a refund.

---

# 143. Refund Standard
<!-- id: terminology.143-refund-standard -->

Use `refund` when money is returned to the original or another payment method.

Clarify processing time separately.

---

# 144. Tax Standard
<!-- id: terminology.144-tax-standard -->

Use `tax` only for government-imposed tax.

Use `fee` for service charges.

---

# 145. Payment Standard
<!-- id: terminology.145-payment-standard -->

Distinguish:

- payment initiated
- payment processing
- payment completed
- payment failed
- payment refunded
- payment reversed

---

# 146. Date Standard
<!-- id: terminology.146-date-standard -->

Use unambiguous dates.

Preferred international editorial format:

`August 9, 2026`

For machine-readable contexts:

`2026-08-09`

Avoid ambiguous numeric dates such as:

`08/09/26`

unless locale guarantees interpretation.

---

# 147. Time Standard
<!-- id: terminology.147-time-standard -->

Include timezone when time matters across regions.

Example:

`5:00 PM Eastern Time`

or:

`2026-08-09 17:00 UTC`

Avoid:

`at 5 PM`

when users may be in different timezones.

---

# 148. Relative Date Standard
<!-- id: terminology.148-relative-date-standard -->

Avoid relative dates in durable documentation when exact dates are important.

Avoid:

- today
- tomorrow
- yesterday
- next Friday

Prefer exact dates.

---

# 149. Number Standard
<!-- id: terminology.149-number-standard -->

Use numerals for:

- measurements
- prices
- percentages
- dates
- times
- technical values
- counts when precision matters

Editorial prose MAY spell out small numbers when readability improves.

---

# 150. Large Number Standard
<!-- id: terminology.150-large-number-standard -->

Use separators consistently.

Examples:

- 1,000
- 10,000
- 1,000,000

Avoid mixed styles within the same locale.

---

# 151. Decimal Standard
<!-- id: terminology.151-decimal-standard -->

Use the minimum precision needed.

Avoid:

`99.000%`

when:

`99%`

is accurate enough.

---

# 152. Percentage Standard
<!-- id: terminology.152-percentage-standard -->

Use the percent sign with numerals:

`25%`

State the comparison base when material.

---

# 153. Range Standard
<!-- id: terminology.153-range-standard -->

Write ranges unambiguously.

Examples:

- 5–10 minutes
- $20–$30
- 2024–2026

Do not mix inclusive and exclusive meanings without clarification.

---

# 154. Approximation Standard
<!-- id: terminology.154-approximation-standard -->

Use approximation language honestly.

Examples:

- about
- approximately
- typically
- usually
- estimated

Do not present estimates as guarantees.

---

# 155. Maximum / Minimum Standard
<!-- id: terminology.155-maximum-minimum-standard -->

Use explicit terms:

- at least
- at most
- no more than
- no fewer than

Avoid ambiguous combinations.

---

# 156. More Than / At Least Standard
<!-- id: terminology.156-more-than-at-least-standard -->

Distinguish:

- more than 10 = 11+
- at least 10 = 10+

Use mathematically precise wording when thresholds matter.

---

# 157. Less Than / Up To Standard
<!-- id: terminology.157-less-than-up-to-standard -->

Distinguish:

- less than 10 = below 10
- up to 10 = 10 or fewer

---

# 158. Unit Standard
<!-- id: terminology.158-unit-standard -->

Always state units when needed.

Examples:

- 10 MB
- 5 GB
- 30 seconds
- 25 km
- 10 users

Do not assume the user knows the unit.

---

# 159. Storage Unit Standard
<!-- id: terminology.159-storage-unit-standard -->

Choose a standard for:

- KB
- MB
- GB
- TB

Document whether decimal or binary interpretation is used when precision matters.

---

# 160. Currency Standard
<!-- id: terminology.160-currency-standard -->

State currency when ambiguity is possible.

Examples:

- USD 49
- $49 USD
- €49

Do not assume `$` identifies a single currency globally.

---

# 161. Locale Standard
<!-- id: terminology.161-locale-standard -->

Terminology MAY vary by locale when genuine language conventions differ.

Localization SHOULD preserve conceptual consistency, not literal wording.

---

# 162. Translation Standard
<!-- id: terminology.162-translation-standard -->

Translation SHOULD be meaning-based.

Do not require word-for-word translation when it creates unnatural or ambiguous language.

Maintain:

- terminology glossary
- translation memory
- prohibited terms
- product names
- placeholders
- variables

---

# 163. Transcreation Standard
<!-- id: terminology.163-transcreation-standard -->

Marketing MAY use transcreation when literal translation would fail culturally.

Core product terminology SHOULD remain semantically consistent.

---

# 164. String Length Standard
<!-- id: terminology.164-string-length-standard -->

User-interface terminology SHOULD account for localization expansion.

Avoid extremely compressed labels if they cannot be translated clearly.

---

# 165. Variable Standard
<!-- id: terminology.165-variable-standard -->

Dynamic placeholders SHOULD be understandable to translators and writers.

Good:

`Delete {workspace_name}?`

Document variable meaning.

Avoid:

`Delete {0}?`

when localization tooling allows named variables.

---

# 166. Gender Standard
<!-- id: terminology.166-gender-standard -->

Avoid unnecessary gender assumptions.

Prefer:

- they
- the user
- the customer
- the person

when gender is unknown or irrelevant.

---

# 167. Inclusive Language Standard
<!-- id: terminology.167-inclusive-language-standard -->

Use respectful language that describes people accurately.

Avoid wording that:

- stereotypes
- dehumanizes
- stigmatizes
- infantilizes
- uses identity as a negative metaphor

When communities have established terminology preferences, follow context-appropriate and current usage.

---

# 168. Disability Terminology Standard
<!-- id: terminology.168-disability-terminology-standard -->

Use disability-related terminology respectfully and literally.

Avoid disability terms as metaphors for:

- errors
- bad design
- ignorance
- failure

Do not use phrases such as:

- blind spot
- lame
- crippled
- deaf to
- crazy

when a neutral alternative communicates the meaning.

---

# 169. Person-First / Identity-First Standard
<!-- id: terminology.169-person-first-identity-first-standard -->

Do not assume one universal preference.

Use terminology accepted by the relevant community and context.

When referring to a specific person, use the person's stated preference when known.

---

# 170. Age Terminology Standard
<!-- id: terminology.170-age-terminology-standard -->

Avoid patronizing age-based labels.

Prefer specific terms when relevant:

- children
- teens
- adults
- older adults

Use statutory age terms only when legally necessary.

---

# 171. Race / Ethnicity Standard
<!-- id: terminology.171-race-ethnicity-standard -->

Use recognized, respectful terms.

Do not infer race or ethnicity from names, language, or geography without a legitimate basis.

Capitalize identity terms consistently with the chosen editorial standard.

---

# 172. Nationality Standard
<!-- id: terminology.172-nationality-standard -->

Do not use nationality as a proxy for:

- race
- ethnicity
- language
- legal residence
- citizenship

when those distinctions matter.

---

# 173. Immigration Terminology Standard
<!-- id: terminology.173-immigration-terminology-standard -->

Prefer neutral, legally accurate wording.

Avoid dehumanizing nouns.

Prefer:

`undocumented immigrants`

over:

`illegals`

where that description is contextually accurate.

---

# 174. Criminal Justice Terminology Standard
<!-- id: terminology.174-criminal-justice-terminology-standard -->

Use legally accurate status terms.

Distinguish:

- accused
- charged
- convicted
- incarcerated
- formerly incarcerated

Do not describe a person as guilty before conviction unless the legal context supports it.

---

# 175. Health Terminology Standard
<!-- id: terminology.175-health-terminology-standard -->

Use medical terminology accurately.

Avoid:

- diagnosing users casually
- stigmatizing mental-health language
- using disorders as metaphors

Health wording with clinical implications SHOULD receive subject-matter review.

---

# 176. Mental Health Language Standard
<!-- id: terminology.176-mental-health-language-standard -->

Avoid casual metaphors based on mental-health conditions.

Examples to avoid:

- crazy
- insane
- OCD
- bipolar

when describing ordinary preferences, inconsistency, or intensity.

---

# 177. Legal Terminology Standard
<!-- id: terminology.177-legal-terminology-standard -->

Legal terms MUST preserve legal meaning.

Do not replace a legally defined term with a simpler synonym when the substitution changes meaning.

Where needed:

1. use the legal term
2. explain it in plain language

---

# 178. Privacy Terminology Standard
<!-- id: terminology.178-privacy-terminology-standard -->

Privacy language MUST distinguish:

- collect
- use
- process
- disclose
- share
- sell
- transfer
- retain
- delete
- anonymize
- de-identify
- aggregate

These are not interchangeable.

---

# 179. Share Standard
<!-- id: terminology.179-share-standard -->

Use `share` carefully in privacy content.

A legal definition of sharing may differ from ordinary language.

When legally relevant, capitalize or define the statutory term if required by the style.

---

# 180. Sell Standard
<!-- id: terminology.180-sell-standard -->

Do not say `we do not sell data` without verifying the applicable legal definition of sale.

---

# 181. Process Standard
<!-- id: terminology.181-process-standard -->

In privacy/legal contexts, `process` can include collection, storage, use, disclosure, deletion, and other operations.

For general users, explain the specific operation when possible.

---

# 182. Retain Standard
<!-- id: terminology.182-retain-standard -->

Use `retain` when data continues to be stored.

Clarify retention period or criteria when material.

---

# 183. Store Standard
<!-- id: terminology.183-store-standard -->

Use `store` for technical persistence.

Do not imply indefinite retention merely because data is stored.

---

# 184. Collect Standard
<!-- id: terminology.184-collect-standard -->

Use `collect` when information is obtained from a person, device, or another source.

In legal contexts, automated acquisition may still count as collection.

---

# 185. Track Standard
<!-- id: terminology.185-track-standard -->

Use `track` only when behavior or events are actually monitored over time or across contexts.

Do not euphemize tracking as `experience improvement` if tracking is material.

---

# 186. Personalize Standard
<!-- id: terminology.186-personalize-standard -->

Use `personalize` when behavior or content changes based on user-specific data.

Clarify if personalization also involves advertising or profiling.

---

# 187. Profile Standard
<!-- id: terminology.187-profile-standard -->

Use `profile` carefully.

Distinguish:

- user profile = account information
- profiling = analysis or prediction about a person

---

# 188. AI Terminology Standard
<!-- id: terminology.188-ai-terminology-standard -->

AI wording SHOULD distinguish:

- artificial intelligence
- machine learning
- generative AI
- model
- large language model
- agent
- assistant
- automation
- recommendation system
- classifier
- algorithm

Do not call every automated feature AI.

---

# 189. AI Model Standard
<!-- id: terminology.189-ai-model-standard -->

Use `model` for the trained computational system producing predictions or outputs.

Do not use `model` as a synonym for the whole application when the distinction matters.

---

# 190. AI Assistant Standard
<!-- id: terminology.190-ai-assistant-standard -->

Use `assistant` when the system helps a user perform tasks or answer questions.

Do not imply autonomous authority beyond actual capability.

---

# 191. AI Agent Standard
<!-- id: terminology.191-ai-agent-standard -->

Use `agent` only when the system can take goal-directed actions across steps or tools with some degree of autonomy.

Do not call a simple chatbot or single-turn generator an agent merely for marketing.

---

# 192. AI Automation Standard
<!-- id: terminology.192-ai-automation-standard -->

Use `automation` when predefined or model-driven processes execute tasks without continuous manual input.

Distinguish automation from autonomous decision-making.

---

# 193. AI-Generated Standard
<!-- id: terminology.193-ai-generated-standard -->

Use `AI-generated` when output is substantially produced by an AI system.

Use `AI-assisted` when human authorship or control remains primary.

---

# 194. Hallucination Standard
<!-- id: terminology.194-hallucination-standard -->

For technical or expert audiences, `hallucination` MAY describe fabricated or unsupported model output.

For general users, prefer clearer language such as:

`AI-generated answers can be inaccurate or make up information.`

---

# 195. Confidence Standard
<!-- id: terminology.195-confidence-standard -->

Do not use `confidence` for a model score unless the score is actually calibrated or defined.

Prefer:

- model score
- probability
- similarity score
- ranking score

when technically accurate.

---

# 196. Intelligent Standard
<!-- id: terminology.196-intelligent-standard -->

Avoid `intelligent` as an empty marketing adjective.

Use concrete capability descriptions.

---

# 197. Smart Standard
<!-- id: terminology.197-smart-standard -->

Avoid `smart` when it adds no information.

Prefer:

- automated
- adaptive
- predictive
- connected

when accurate.

---

# 198. Automatic Standard
<!-- id: terminology.198-automatic-standard -->

Use `automatic` only when the user does not need to perform the action manually.

Clarify triggers where relevant.

---

# 199. Real-Time Standard
<!-- id: terminology.199-real-time-standard -->

Use `real-time` only when latency is genuinely near-immediate for the intended use.

If updates occur every few minutes, say:

`updates every 5 minutes`

rather than:

`real-time`

---

# 200. Instant Standard
<!-- id: terminology.200-instant-standard -->

Avoid `instant` unless the action is effectively immediate.

Use:

`usually completes within a few seconds`

if that is more accurate.

---

# 201. Live Standard
<!-- id: terminology.201-live-standard -->

Define `live`.

Possible meanings:

- currently broadcasting
- publicly published
- production environment
- continuously updating
- currently active

Do not use it ambiguously.

---

# 202. Dashboard Standard
<!-- id: terminology.202-dashboard-standard -->

Use `dashboard` for a summary view of important metrics, status, or controls.

Do not call every landing page a dashboard.

---

# 203. Analytics Standard
<!-- id: terminology.203-analytics-standard -->

Use `analytics` for systematic analysis of data.

Do not use it as a synonym for reporting when no analysis occurs.

---

# 204. Report Standard
<!-- id: terminology.204-report-standard -->

Use `report` for a structured output summarizing information.

Reports MAY be static or generated.

---

# 205. Insight Standard
<!-- id: terminology.205-insight-standard -->

Avoid `insight` when the content is merely a raw metric.

Use `insight` when interpretation or actionable meaning is provided.

---

# 206. Metric Standard
<!-- id: terminology.206-metric-standard -->

Use `metric` for a measured quantitative value.

Define formula and unit when needed.

---

# 207. KPI Standard
<!-- id: terminology.207-kpi-standard -->

Use `KPI` only for a metric explicitly tied to a key objective.

Not every metric is a KPI.

---

# 208. Conversion Standard
<!-- id: terminology.208-conversion-standard -->

Define conversion according to the business event.

Examples:

- purchase
- signup
- booked demo
- completed application

Do not use `conversion` without a defined event in analytics documentation.

---

# 209. Session Standard
<!-- id: terminology.209-session-standard -->

Define `session` technically.

Do not assume users understand analytics session rules.

---

# 210. Visitor / User Standard
<!-- id: terminology.210-visitor-user-standard -->

Distinguish:

- visitor = person or browser visiting a property
- user = recognized or product-using person/account

Analytics systems may define these differently.

---

# 211. Unique User Standard
<!-- id: terminology.211-unique-user-standard -->

Use `unique user` only if the deduplication method is defined.

Do not imply a perfect count of individual people when identity is device-based or probabilistic.

---

# 212. Customer Standard
<!-- id: terminology.212-customer-standard -->

Use `customer` only for a party with a commercial relationship unless the company intentionally uses a broader definition.

---

# 213. Client Standard
<!-- id: terminology.213-client-standard -->

Choose between `client` and `customer`.

Do not alternate without meaning.

`Client` is often appropriate for professional services.

`Customer` is often appropriate for products and SaaS.

---

# 214. Consumer Standard
<!-- id: terminology.214-consumer-standard -->

Use `consumer` when referring to individuals acting in a personal or household capacity, especially in legal contexts.

Do not use it as a generic synonym for all customers.

---

# 215. Business Standard
<!-- id: terminology.215-business-standard -->

Clarify whether `business` means:

- customer organization
- legal entity
- commercial customer
- company generally

---

# 216. Enterprise Standard
<!-- id: terminology.216-enterprise-standard -->

Use `Enterprise` only if it identifies a defined plan, market segment, or product.

Avoid using `enterprise-grade` without explaining the relevant capabilities.

---

# 217. Small Business Standard
<!-- id: terminology.217-small-business-standard -->

If a business-size category matters, define the criteria.

Avoid vague labels based solely on perception.

---

# 218. Partner Standard
<!-- id: terminology.218-partner-standard -->

Use `partner` carefully.

A commercial integration, reseller, affiliate, vendor, or contractor is not necessarily a legal partnership.

Avoid language that unintentionally suggests a legal partnership.

---

# 219. Vendor Standard
<!-- id: terminology.219-vendor-standard -->

Use `vendor` for an external supplier.

In privacy contexts, classify the vendor's legal data role separately.

---

# 220. Provider Standard
<!-- id: terminology.220-provider-standard -->

Use `provider` when an entity provides a defined service.

Avoid using it as a catch-all when `processor`, `vendor`, or `subprocessor` is legally relevant.

---

# 221. Integration Standard
<!-- id: terminology.221-integration-standard -->

Use `integration` when two systems exchange data or functionality.

Do not call a hyperlink or manual export an integration.

---

# 222. Connector Standard
<!-- id: terminology.222-connector-standard -->

Use `connector` for a specific component that enables a system connection.

Do not use interchangeably with integration unless the relationship is defined.

---

# 223. Plugin Standard
<!-- id: terminology.223-plugin-standard -->

Use `plugin` for an installable or attachable extension when the architecture supports that concept.

Do not alternate among:

- plugin
- extension
- app
- integration
- add-on

without a defined difference.

---

# 224. App Standard
<!-- id: terminology.224-app-standard -->

Define whether `app` means:

- mobile application
- web application
- connected third-party application
- marketplace extension

---

# 225. Platform Standard
<!-- id: terminology.225-platform-standard -->

Use `platform` only when the product actually supports a broader ecosystem, infrastructure, or multi-sided set of capabilities.

Avoid using `platform` as a prestige synonym for product.

---

# 226. Solution Standard
<!-- id: terminology.226-solution-standard -->

Avoid vague `solution` language in product copy.

Prefer the actual product or service name.

---

# 227. Tool Standard
<!-- id: terminology.227-tool-standard -->

Use `tool` for a focused utility.

Do not call a complex platform a tool if that creates confusion.

---

# 228. Service Standard
<!-- id: terminology.228-service-standard -->

Use `service` for functionality delivered to users.

In legal text, define whether `Services` is a defined collective term.

---

# 229. System Standard
<!-- id: terminology.229-system-standard -->

Use `system` only when referring to a technical or operational system.

Avoid vague phrases such as:

`the system will process it`

when a specific product component can be named.

---

# 230. Environment Standard
<!-- id: terminology.230-environment-standard -->

For technical audiences, define:

- development
- staging
- test
- production

Do not assume general users understand environment terminology.

---

# 231. Production Standard
<!-- id: terminology.231-production-standard -->

Use `production` for the live operational environment.

Do not use it as a synonym for published content unless documented.

---

# 232. Sandbox Standard
<!-- id: terminology.232-sandbox-standard -->

Use `sandbox` for a controlled testing environment.

Clarify:

- data persistence
- billing behavior
- production separation
- API differences

---

# 233. API Standard
<!-- id: terminology.233-api-standard -->

Spell out `application programming interface (API)` when needed for nontechnical audiences.

Use `API` consistently afterward.

---

# 234. Endpoint Standard
<!-- id: terminology.234-endpoint-standard -->

Use `endpoint` for a specific API-accessible address or operation.

Do not use `endpoint` for a user's device in documentation unless context clearly distinguishes it.

---

# 235. Request / Response Standard
<!-- id: terminology.235-request-response-standard -->

In API documentation:

- request = message sent to the service
- response = message returned by the service

Use consistently.

---

# 236. Parameter Standard
<!-- id: terminology.236-parameter-standard -->

Distinguish:

- path parameter
- query parameter
- header
- body field

Avoid generic `parameter` when precision helps implementation.

---

# 237. Field Standard
<!-- id: terminology.237-field-standard -->

Use `field` for a named data element in a form, object, or record.

---

# 238. Property Standard
<!-- id: terminology.238-property-standard -->

Use `property` for an attribute of an object or entity when that is the canonical technical term.

Do not alternate freely with field.

---

# 239. Attribute Standard
<!-- id: terminology.239-attribute-standard -->

Use `attribute` where the technical model defines attributes.

Avoid mixing field/property/attribute unless they have distinct meanings.

---

# 240. Object Standard
<!-- id: terminology.240-object-standard -->

Define technical objects in developer documentation.

Do not expose `object` to general users if a concrete noun is available.

---

# 241. Resource Standard
<!-- id: terminology.241-resource-standard -->

Use `resource` for an API or infrastructure entity when appropriate.

Do not use it as vague business language.

---

# 242. Event Standard
<!-- id: terminology.242-event-standard -->

Use `event` for a discrete occurrence recorded or emitted by a system.

Define naming conventions for analytics events.

---

# 243. Event Naming Standard
<!-- id: terminology.243-event-naming-standard -->

Analytics event names SHOULD follow one pattern.

Recommended patterns:

`noun_verb`

or

`object_action`

Examples:

- account_created
- file_uploaded
- subscription_canceled

Do not mix inconsistent forms.

---

# 244. Schema Standard
<!-- id: terminology.244-schema-standard -->

Use `schema` for a formal structure defining data fields and relationships.

Do not use it merely to mean a general format.

---

# 245. Taxonomy Standard
<!-- id: terminology.245-taxonomy-standard -->

Use `taxonomy` for a controlled hierarchical or categorized classification system.

---

# 246. Ontology Standard
<!-- id: terminology.246-ontology-standard -->

Use `ontology` for a formal representation of concepts and relationships.

Do not use taxonomy and ontology interchangeably in technical contexts.

---

# 247. Category Standard
<!-- id: terminology.247-category-standard -->

Use `category` for a broad classification grouping.

Categories SHOULD be mutually understandable and avoid unnecessary overlap.

---

# 248. Tag Standard
<!-- id: terminology.248-tag-standard -->

Use `tag` for a flexible label attached to content or records.

Do not treat tags as hierarchical categories unless the system supports hierarchy.

---

# 249. Label Standard
<!-- id: terminology.249-label-standard -->

Use `label` for display text or classification metadata when applicable.

Do not confuse UI labels with taxonomy tags.

---

# 250. Type Standard
<!-- id: terminology.250-type-standard -->

Use `type` for a defined class or data kind.

Avoid generic `type` if category or format is more precise.

---

# 251. Format Standard
<!-- id: terminology.251-format-standard -->

Use `format` for representation or structure.

Examples:

- PDF
- CSV
- JSON
- date format

---

# 252. Template Standard
<!-- id: terminology.252-template-standard -->

Use `template` for reusable predefined structure or content.

Do not use `template` when users actually create a copy of a completed item.

---

# 253. Example Standard
<!-- id: terminology.253-example-standard -->

Use `example` for illustrative content that is not necessarily recommended.

Do not label required values as examples.

---

# 254. Sample Standard
<!-- id: terminology.254-sample-standard -->

Use `sample` for representative content or data.

Distinguish example vs sample when statistically relevant.

---

# 255. Default Standard
<!-- id: terminology.255-default-standard -->

Use `default` for the initial system-selected value or behavior.

State when users can change it.

---

# 256. Recommended Standard
<!-- id: terminology.256-recommended-standard -->

Use `recommended` when the organization advises a choice but does not require it.

Do not call mandatory behavior recommended.

---

# 257. Required Standard
<!-- id: terminology.257-required-standard -->

Use `required` only when an action or value is mandatory.

---

# 258. Optional Standard
<!-- id: terminology.258-optional-standard -->

Use `optional` only when omission has no hidden consequence that makes it practically mandatory.

---

# 259. Suggested Standard
<!-- id: terminology.259-suggested-standard -->

Use `suggested` for a nonbinding recommendation.

Avoid using it for configuration necessary for proper operation.

---

# 260. Preferred Standard
<!-- id: terminology.260-preferred-standard -->

Use `preferred` when multiple valid choices exist but one is favored.

---

# 261. Supported / Unsupported Standard
<!-- id: terminology.261-supported-unsupported-standard -->

Use:

- supported
- unsupported
- partially supported
- deprecated

with explicit definitions.

Avoid ambiguous:

`not recommended`

when the feature is actually unsupported.

---

# 262. Available Soon Standard
<!-- id: terminology.262-available-soon-standard -->

Avoid vague future wording such as:

- coming soon
- shortly
- soon

unless the uncertainty is intentional.

If a date is known, use the date.

---

# 263. Beta Availability Standard
<!-- id: terminology.263-beta-availability-standard -->

Do not use `available` if users still require approval, waitlist access, or invitation.

Prefer:

- available to selected accounts
- available by request
- available in beta

---

# 264. Estimate Standard
<!-- id: terminology.264-estimate-standard -->

Clearly identify estimates.

Examples:

- estimated delivery
- estimated completion time
- estimated cost

Do not visually present estimates as confirmed values.

---

# 265. Forecast Standard
<!-- id: terminology.265-forecast-standard -->

Use `forecast` for a prediction based on a method or model.

Distinguish forecasts from targets and actuals.

---

# 266. Target Standard
<!-- id: terminology.266-target-standard -->

Use `target` for an intended goal.

Do not present targets as forecasts or guaranteed outcomes.

---

# 267. Actual Standard
<!-- id: terminology.267-actual-standard -->

Use `actual` for observed realized values.

---

# 268. Budget Standard
<!-- id: terminology.268-budget-standard -->

Use `budget` for planned allocation.

Do not confuse budget with forecast.

---

# 269. Status Vocabulary Standard
<!-- id: terminology.269-status-vocabulary-standard -->

Every domain with states SHOULD maintain a controlled vocabulary.

Example:

```text
Draft
In review
Approved
Published
Archived
```

Avoid adding new status words without governance.

---

# 270. Boolean Label Standard
<!-- id: terminology.270-boolean-label-standard -->

For binary settings, name the positive condition when practical.

Better:

`Email notifications`

Toggle:

On / Off

Avoid:

`Disable email notifications`

with an On / Off toggle because the double negative is confusing.

---

# 271. Yes / No Question Standard
<!-- id: terminology.271-yes-no-question-standard -->

Yes/no prompts SHOULD ask one unambiguous question.

Avoid:

`Don't disable notifications?`

---

# 272. Negative Wording Standard
<!-- id: terminology.272-negative-wording-standard -->

Avoid double negatives.

Avoid:

`Do not disable automatic backups.`

Prefer:

`Keep automatic backups enabled.`

---

# 273. Negation Standard
<!-- id: terminology.273-negation-standard -->

Place `not` close to the word or phrase it negates.

---

# 274. Condition Standard
<!-- id: terminology.274-condition-standard -->

State conditions before or immediately after the affected action.

Example:

`If you cancel before August 31, you will not be charged for the next billing period.`

---

# 275. Exception Standard
<!-- id: terminology.275-exception-standard -->

Important exceptions SHOULD be near the general rule.

Do not place a material exception several sections later.

---

# 276. Requirement Standard
<!-- id: terminology.276-requirement-standard -->

Requirements SHOULD use direct modal wording.

Use:

- must
- required
- need to

Avoid vague:

- should probably
- may want to
- ideally

when the requirement is mandatory.

---

# 277. Recommendation Standard
<!-- id: terminology.277-recommendation-standard -->

Recommendations SHOULD use:

- should
- recommended
- we recommend

Do not use `must` unless mandatory.

---

# 278. Possibility Standard
<!-- id: terminology.278-possibility-standard -->

Use `may` to indicate possibility or permission carefully.

In legal text, `may` can imply discretion.

In user instructions, prefer concrete wording when possible.

---

# 279. Ability Standard
<!-- id: terminology.279-ability-standard -->

Distinguish:

- can = capability
- may = permission/possibility

Use this distinction when it improves clarity.

---

# 280. Future Tense Standard
<!-- id: terminology.280-future-tense-standard -->

Prefer present tense for current product behavior.

Prefer:

`The system sends a confirmation email.`

Avoid:

`The system will send a confirmation email.`

unless describing a future event after an action.

---

# 281. Active Voice Standard
<!-- id: terminology.281-active-voice-standard -->

Prefer active voice when the actor matters.

Prefer:

`Admins can delete projects.`

Avoid:

`Projects can be deleted by admins.`

Passive voice MAY be appropriate when the actor is unknown or irrelevant.

---

# 282. Subject Standard
<!-- id: terminology.282-subject-standard -->

Put the subject near the beginning of a sentence.

Long introductory phrases SHOULD NOT delay the main point unnecessarily.

---

# 283. Sentence Length Standard
<!-- id: terminology.283-sentence-length-standard -->

Most user-facing sentences SHOULD be reasonably short.

If a sentence contains:

- multiple conditions
- multiple exceptions
- multiple actions
- several clauses

consider splitting it.

---

# 284. Paragraph Standard
<!-- id: terminology.284-paragraph-standard -->

Each paragraph SHOULD focus on one idea.

Long blocks of text SHOULD be broken into:

- shorter paragraphs
- lists
- steps
- tables

when structure improves understanding.

---

# 285. List Standard
<!-- id: terminology.285-list-standard -->

Use lists when content is naturally enumerable.

List items SHOULD have parallel grammatical structure.

---

# 286. Parallelism Standard
<!-- id: terminology.286-parallelism-standard -->

Items in the same list SHOULD use the same grammatical form.

Good:

- Create an account
- Add members
- Configure billing

Avoid:

- Create an account
- Member invitations
- Billing can be configured

---

# 287. Punctuation Standard
<!-- id: terminology.287-punctuation-standard -->

Punctuation SHOULD clarify meaning, not decorate copy.

Avoid excessive:

- exclamation marks
- ellipses
- em dashes
- semicolons

in user-interface text.

---

# 288. Exclamation Mark Standard
<!-- id: terminology.288-exclamation-mark-standard -->

Use exclamation marks sparingly.

Do not use them for:

- errors
- payment failures
- legal notices
- destructive actions
- security incidents

---

# 289. Ellipsis Standard
<!-- id: terminology.289-ellipsis-standard -->

Use an ellipsis only when:

- text is intentionally omitted
- an action opens a dialog requiring further input, if that UI convention is used

Do not use ellipses as decorative suspense.

---

# 290. Quotation Mark Standard
<!-- id: terminology.290-quotation-mark-standard -->

Use quotation marks consistently.

Quote:

- exact labels
- exact commands
- exact user-entered values when useful

Do not overquote common product terms.

---

# 291. Code Formatting Standard
<!-- id: terminology.291-code-formatting-standard -->

Use code formatting for:

- commands
- filenames
- paths
- API properties
- code values
- literal strings

Do not use code formatting merely for emphasis.

---

# 292. Emphasis Standard
<!-- id: terminology.292-emphasis-standard -->

Use bold sparingly for:

- key actions
- critical distinctions
- important warnings

Do not bold entire paragraphs.

---

# 293. Heading Standard
<!-- id: terminology.293-heading-standard -->

Headings SHOULD:

- describe the section
- use the same terminology as body content
- be concise
- help scanning
- avoid clever wording

---

# 294. Question Heading Standard
<!-- id: terminology.294-question-heading-standard -->

Use questions when the section genuinely answers that question.

Do not force all headings into question form.

---

# 295. Label Consistency Standard
<!-- id: terminology.295-label-consistency-standard -->

A concept SHOULD have the same label in:

- navigation
- page title
- button
- help documentation
- onboarding
- support
- analytics

unless context requires a clearly documented variation.

---

# 296. Searchability Standard
<!-- id: terminology.296-searchability-standard -->

Terminology SHOULD be easy to search.

Avoid:

- stylized spellings users cannot predict
- punctuation-heavy names
- unexplained abbreviations
- arbitrary capitalization

---

# 297. SEO Terminology Standard
<!-- id: terminology.297-seo-terminology-standard -->

Primary topic terms SHOULD match language users actually search for.

Do not sacrifice product terminology consistency solely to insert keyword variants.

Use synonyms in explanatory prose where natural.

---

# 298. GEO / AEO Terminology Standard
<!-- id: terminology.298-geo-aeo-terminology-standard -->

Important facts and definitions SHOULD use explicit nouns and stable terminology.

This improves:

- extraction
- summarization
- citation
- passage retrieval
- answer accuracy

Avoid overly contextual wording that makes a statement meaningless when isolated.

---

# 299. Machine Interpretability Standard
<!-- id: terminology.299-machine-interpretability-standard -->

Terminology SHOULD be structurally consistent enough that automated systems can distinguish:

- entities
- actions
- states
- relationships
- roles
- time
- quantities

---

# 300. Entity Naming Standard
<!-- id: terminology.300-entity-naming-standard -->

Use the same canonical entity name across:

- title
- body copy
- structured data
- metadata
- documentation
- policies

Avoid unexplained short names for important entities.

---

# 301. Taxonomic Consistency Standard
<!-- id: terminology.301-taxonomic-consistency-standard -->

Category labels SHOULD use parallel levels of abstraction.

Avoid a category set such as:

- Software
- Hospitals
- Automotive Parts
- Finance Technology

because the categories mix broad sectors, institutions, products, and subindustries without an explicit hierarchy.

---

# 302. Marketing Terminology Standard
<!-- id: terminology.302-marketing-terminology-standard -->

Marketing MAY be expressive, but core product terminology MUST remain consistent.

Marketing SHOULD NOT rename core actions merely for novelty.

---

# 303. Brand Voice Standard
<!-- id: terminology.303-brand-voice-standard -->

Brand voice SHOULD affect tone, not factual meaning.

Terminology accuracy has priority over personality.

---

# 304. Humor Standard
<!-- id: terminology.304-humor-standard -->

Humor SHOULD NOT appear where users face:

- errors
- security issues
- financial loss
- account deletion
- legal notices
- health issues
- accessibility barriers

---

# 305. Anthropomorphism Standard
<!-- id: terminology.305-anthropomorphism-standard -->

Avoid implying software has human understanding, intention, emotion, or judgment unless clearly used as harmless conversational framing.

Examples requiring caution:

- knows
- understands
- thinks
- feels
- decides

Prefer technically accurate descriptions in high-stakes contexts.

---

# 306. Trust Language Standard
<!-- id: terminology.306-trust-language-standard -->

Trust SHOULD be earned through evidence.

Avoid empty trust claims:

- trusted
- secure
- reliable
- enterprise-grade
- world-class

without supporting information.

---

# 307. Compliance Claim Standard
<!-- id: terminology.307-compliance-claim-standard -->

Use compliance terminology only when verified.

Distinguish:

- compliant with
- designed to support compliance with
- certified under
- audited against
- aligned with

These claims are not equivalent.

---

# 308. Certification Standard
<!-- id: terminology.308-certification-standard -->

Do not use `certified` unless a legitimate certification exists and is current.

---

# 309. Audit Standard
<!-- id: terminology.309-audit-standard -->

Use `audited` only when an audit actually occurred.

State the framework or scope where relevant.

---

# 310. Compliant Standard
<!-- id: terminology.310-compliant-standard -->

Avoid saying a product itself is universally `GDPR compliant`, `HIPAA compliant`, or similarly compliant without qualification and review.

Compliance often depends on configuration, contracts, user behavior, and organizational practices.

---

# 311. Support Standard
<!-- id: terminology.311-support-standard -->

Use `support` carefully.

Distinguish:

- technical support
- customer support
- compatibility support
- maintained feature
- supported configuration

---

# 312. SLA Standard
<!-- id: terminology.312-sla-standard -->

Use `SLA` only for a defined service-level agreement.

Do not call general support targets an SLA unless contractually intended.

---

# 313. Response Time Standard
<!-- id: terminology.313-response-time-standard -->

Distinguish:

- first response time
- resolution time
- update cadence

Do not promise `24-hour support` when only ticket intake is available 24 hours.

---

# 314. Availability / Uptime Standard
<!-- id: terminology.314-availability-uptime-standard -->

Use uptime numbers only with a defined measurement method.

Clarify:

- measurement period
- exclusions
- maintenance
- service scope

---

# 315. Reliability Standard
<!-- id: terminology.315-reliability-standard -->

Use `reliable` as a qualitative descriptor cautiously.

Prefer measurable availability or failure metrics when making strong claims.

---

# 316. Performance Standard
<!-- id: terminology.316-performance-standard -->

Performance claims SHOULD specify metric and conditions.

Avoid:

`2x faster`

without stating:

- compared with what
- tested how
- under what conditions

---

# 317. Benchmark Standard
<!-- id: terminology.317-benchmark-standard -->

Benchmarks SHOULD specify:

- workload
- environment
- hardware
- software version
- dataset
- sample size
- date

---

# 318. Accuracy Standard
<!-- id: terminology.318-accuracy-standard -->

Accuracy claims SHOULD identify:

- metric
- test set
- scope
- limitations

Avoid:

`99% accurate`

without defining what is measured.

---

# 319. Precision / Recall Standard
<!-- id: terminology.319-precision-recall-standard -->

Use technical evaluation terms correctly.

Do not use `precision` as a casual synonym for accuracy in technical model evaluation.

---

# 320. Data Quality Standard
<!-- id: terminology.320-data-quality-standard -->

Define dimensions when claiming data quality:

- completeness
- correctness
- freshness
- consistency
- validity
- uniqueness

---

# 321. Fresh Standard
<!-- id: terminology.321-fresh-standard -->

Use `fresh` or `up to date` only when update cadence is known.

Prefer:

`Updated every 15 minutes`

when possible.

---

# 322. Current Standard
<!-- id: terminology.322-current-standard -->

Do not label information `current` if it may be stale.

Include:

- as-of date
- last updated date
- version

when time sensitivity matters.

---

# 323. Latest Standard
<!-- id: terminology.323-latest-standard -->

Use `latest` only after verifying the most recent relevant version or event.

---

# 324. New Standard
<!-- id: terminology.324-new-standard -->

Avoid `new` in durable documentation.

Use a version or date instead.

---

# 325. Recently Standard
<!-- id: terminology.325-recently-standard -->

Avoid `recently` in durable documentation when an exact date is available.

---

# 326. Soon Standard
<!-- id: terminology.326-soon-standard -->

Avoid `soon` where commitments or expectations matter.

---

# 327. Temporary Standard
<!-- id: terminology.327-temporary-standard -->

If a state is temporary, provide an expected duration when known.

---

# 328. Permanent Standard
<!-- id: terminology.328-permanent-standard -->

Use `permanent` only when reversal is genuinely unavailable or not intended.

---

# 329. Forever Standard
<!-- id: terminology.329-forever-standard -->

Avoid `forever` in policy, retention, storage, or support language.

Use a defined duration.

---

# 330. Always / Never Standard
<!-- id: terminology.330-always-never-standard -->

Avoid absolutes unless they are literally true.

Common risky claims:

- always
- never
- every
- none
- completely
- entirely

---

# 331. Typically / Usually Standard
<!-- id: terminology.331-typically-usually-standard -->

Use these when describing common but non-guaranteed behavior.

If a numeric range exists, prefer the range.

---

# 332. May / Might Standard
<!-- id: terminology.332-may-might-standard -->

Use one term consistently for uncertainty.

Avoid stacking uncertainty:

`may possibly sometimes`

---

# 333. Estimated Time Standard
<!-- id: terminology.333-estimated-time-standard -->

If displaying an estimated time, state:

- estimated
- range or typical value
- factors affecting it where relevant

---

# 334. Legal Time Standard
<!-- id: terminology.334-legal-time-standard -->

Legal deadlines SHOULD use exact wording.

Examples:

- within 30 days
- no later than August 31, 2026
- at least 15 days before renewal

Avoid vague timing.

---

# 335. SLA Time Standard
<!-- id: terminology.335-sla-time-standard -->

Use exact units and starting events.

Example:

`within 4 business hours after ticket submission`

---

# 336. Business Day Standard
<!-- id: terminology.336-business-day-standard -->

Define `business day` when legal or contractual timing depends on it.

---

# 337. Calendar Day Standard
<!-- id: terminology.337-calendar-day-standard -->

Use `calendar day` when weekends and holidays count.

---

# 338. Working Day Standard
<!-- id: terminology.338-working-day-standard -->

Avoid `working day` unless the applicable locale defines it clearly.

Prefer `business day` with definition.

---

# 339. Timezone Naming Standard
<!-- id: terminology.339-timezone-naming-standard -->

Prefer full timezone names or UTC offsets when ambiguity exists.

Avoid abbreviations like `CST`, which can refer to multiple timezones.

---

# 340. Error Code Standard
<!-- id: terminology.340-error-code-standard -->

Error codes SHOULD be:

- stable
- documented
- unique
- searchable
- paired with user-readable messages

---

# 341. Internal Code Name Standard
<!-- id: terminology.341-internal-code-name-standard -->

Internal codenames MUST NOT appear in customer-facing copy unless intentionally adopted as public names.

---

# 342. Placeholder Product Name Standard
<!-- id: terminology.342-placeholder-product-name-standard -->

Never ship placeholders such as:

- Foo
- Bar
- TBD
- Lorem ipsum
- Example Company

into production.

---

# 343. Lorem Ipsum Standard
<!-- id: terminology.343-lorem-ipsum-standard -->

Lorem ipsum SHOULD NOT appear in production or user-visible test environments that can be indexed or shared externally.

---

# 344. TODO Standard
<!-- id: terminology.344-todo-standard -->

`TODO`, `FIXME`, and editorial notes MUST NOT appear in production content.

---

# 345. Broken Variable Standard
<!-- id: terminology.345-broken-variable-standard -->

Unresolved variables MUST NOT ship.

Examples:

- {{first_name}}
- {product}
- %USERNAME%
- undefined
- null

---

# 346. Default Error Fallback Standard
<!-- id: terminology.346-default-error-fallback-standard -->

Do not expose raw:

- stack traces
- database errors
- internal exception names
- server paths

to general users.

---

# 347. Technical Error Translation Standard
<!-- id: terminology.347-technical-error-translation-standard -->

Translate technical failures into user-meaningful language while preserving a diagnostic code for support.

---

# 348. Help Content Terminology Standard
<!-- id: terminology.348-help-content-terminology-standard -->

Help articles MUST use the same labels users see in the product.

Do not document:

`Select Preferences`

if the UI label is:

`Settings`

---

# 349. Screenshot Terminology Standard
<!-- id: terminology.349-screenshot-terminology-standard -->

Screenshots SHOULD be updated when labels materially change.

Do not leave screenshots showing deprecated wording.

---

# 350. Support Script Standard
<!-- id: terminology.350-support-script-standard -->

Support macros SHOULD use canonical terminology.

Support SHOULD NOT invent alternate names to explain the product unless those names are documented aliases.

---

# 351. Sales Terminology Standard
<!-- id: terminology.351-sales-terminology-standard -->

Sales teams SHOULD use the same product names, plan names, and capability definitions as public documentation.

---

# 352. Contract Terminology Standard
<!-- id: terminology.352-contract-terminology-standard -->

Defined terms in contracts MUST match commercial product concepts unless legal distinctions require separate language.

---

# 353. Policy Terminology Standard
<!-- id: terminology.353-policy-terminology-standard -->

Privacy and Terms wording SHOULD use defined terms consistently throughout the document.

Defined terms SHOULD NOT change capitalization or meaning halfway through.

---

# 354. Glossary Publication Standard
<!-- id: terminology.354-glossary-publication-standard -->

Public glossaries SHOULD include terms that users genuinely need to understand.

Do not publish internal jargon merely for search traffic.

---

# 355. Internal Glossary Standard
<!-- id: terminology.355-internal-glossary-standard -->

An internal terminology glossary SHOULD include more detail than the public glossary.

Include:

- disallowed terms
- exceptions
- data-model mappings
- API terminology
- legal mappings
- localization notes

---

# 356. Terminology Change Request Standard
<!-- id: terminology.356-terminology-change-request-standard -->

New or changed terminology SHOULD follow a review process.

Minimum request:

- proposed term
- concept definition
- reason
- alternatives
- affected audiences
- existing conflicting terms
- localization impact
- SEO impact
- legal impact
- migration plan

---

# 357. Terminology Approval Standard
<!-- id: terminology.357-terminology-approval-standard -->

High-impact terminology SHOULD be reviewed by relevant stakeholders.

Potential reviewers:

- Product
- Content Design
- Documentation
- Engineering
- Legal
- Marketing
- Localization
- Accessibility

---

# 358. Migration Standard
<!-- id: terminology.358-migration-standard -->

When a term changes:

1. update glossary
2. update UI
3. update help content
4. update API docs
5. update marketing
6. update legal text where appropriate
7. update analytics taxonomy if needed
8. update translations
9. redirect old help/search terms
10. monitor support confusion

---

# 359. Backward Compatibility Standard
<!-- id: terminology.359-backward-compatibility-standard -->

Technical terminology changes SHOULD preserve compatibility where needed.

Examples:

- API field aliases
- redirects
- deprecation notices
- migration guides

---

# 360. Search Alias Standard
<!-- id: terminology.360-search-alias-standard -->

Deprecated terms MAY remain as search aliases so users can still find the new terminology.

---

# 361. Localization Migration Standard
<!-- id: terminology.361-localization-migration-standard -->

A terminology change MUST propagate to translation memories and glossaries.

Do not leave old translated terms after the source term changes.

---

# 362. Analytics Migration Standard
<!-- id: terminology.362-analytics-migration-standard -->

If terminology corresponds to analytics events or dimensions, determine whether renaming affects:

- dashboards
- historical reports
- data contracts
- downstream integrations

---

# 363. Documentation Version Standard
<!-- id: terminology.363-documentation-version-standard -->

Terminology changes that affect product behavior SHOULD be tied to version or release information where appropriate.

---

# 364. Terminology Linting Standard
<!-- id: terminology.364-terminology-linting-standard -->

Automated linting SHOULD detect:

- deprecated terms
- prohibited wording
- capitalization errors
- inconsistent feature names
- incorrect acronyms
- ambiguous UI verbs
- unsupported superlatives
- placeholder text

---

# 365. Prohibited Wording List Standard
<!-- id: terminology.365-prohibited-wording-list-standard -->

Maintain a controlled list of words that require review.

Example review-required terms:

- guaranteed
- secure
- anonymous
- compliant
- certified
- unlimited
- free
- best
- safest
- instant
- real-time
- never
- always
- completely
- private
- confidential

The presence of these terms does not automatically make copy wrong, but it SHOULD trigger verification.

---

# 366. Ambiguity Lint Standard
<!-- id: terminology.366-ambiguity-lint-standard -->

Automated or editorial review SHOULD flag:

- this
- that
- it
- they
- soon
- currently
- active
- available
- secure
- data
- account

when context could make them ambiguous.

---

# 367. UI Verb Lint Standard
<!-- id: terminology.367-ui-verb-lint-standard -->

Flag generic action labels:

- Submit
- Continue
- Proceed
- Confirm
- Done
- Okay

for review.

---

# 368. Destructive Language Lint Standard
<!-- id: terminology.368-destructive-language-lint-standard -->

Flag destructive actions lacking explicit nouns.

Avoid buttons such as:

- Delete
- Remove
- Reset

without naming the object when context may be unclear.

---

# 369. Readability QA Standard
<!-- id: terminology.369-readability-qa-standard -->

Review copy for:

- sentence complexity
- unfamiliar vocabulary
- undefined acronyms
- ambiguous pronouns
- unnecessary passive voice
- nested conditions
- negative constructions

Readability scores MAY support review but MUST NOT replace editorial judgment.

---

# 370. Terminology QA Checklist
<!-- id: terminology.370-terminology-qa-checklist -->

Before publishing terminology-sensitive content:

- [ ] Preferred terms used
- [ ] Definitions accurate
- [ ] No conflicting synonyms
- [ ] Capitalization consistent
- [ ] Acronyms defined
- [ ] Product names correct
- [ ] Feature names correct
- [ ] Roles distinguished
- [ ] Statuses distinguished
- [ ] Destructive actions explicit
- [ ] Dates unambiguous
- [ ] Units included
- [ ] Claims supportable
- [ ] Legal terms preserved
- [ ] Privacy terms accurate
- [ ] AI terms accurate
- [ ] Inclusive language reviewed
- [ ] Localization impact considered
- [ ] Deprecated terms removed
- [ ] Search aliases considered
- [ ] Help/UI labels match

---

# 371. UI Wording QA Checklist
<!-- id: terminology.371-ui-wording-qa-checklist -->

- [ ] Button names describe actions
- [ ] Navigation names describe destinations
- [ ] Forms have explicit labels
- [ ] Placeholders are not labels
- [ ] Errors explain next steps
- [ ] Success messages name the result
- [ ] Confirmations name consequences
- [ ] Destructive actions distinguish delete/remove/archive
- [ ] Toggles avoid double negatives
- [ ] Empty states explain next steps
- [ ] Status wording is consistent

---

# 372. Marketing Wording QA Checklist
<!-- id: terminology.372-marketing-wording-qa-checklist -->

- [ ] Claims are supportable
- [ ] Superlatives verified
- [ ] "Free" conditions clear
- [ ] "Unlimited" conditions clear
- [ ] Security claims verified
- [ ] Compliance claims verified
- [ ] Performance claims have comparison basis
- [ ] Accuracy claims define metric
- [ ] AI claims describe actual capability
- [ ] Product terminology matches UI/docs
- [ ] No hidden material qualification

---

# 373. Documentation Wording QA Checklist
<!-- id: terminology.373-documentation-wording-qa-checklist -->

- [ ] Terminology matches UI
- [ ] Acronyms defined
- [ ] Steps use exact action labels
- [ ] Examples are clearly examples
- [ ] Requirements are distinguishable from recommendations
- [ ] Versions are named
- [ ] Dates are explicit
- [ ] Technical concepts are defined
- [ ] Deprecated terms identified
- [ ] Screenshots match current wording

---

# 374. Legal / Privacy Wording QA Checklist
<!-- id: terminology.374-legal-privacy-wording-qa-checklist -->

- [ ] Defined terms used consistently
- [ ] Legal meanings preserved
- [ ] Collect/use/share/sell distinctions accurate
- [ ] Retention wording precise
- [ ] Deletion wording matches operations
- [ ] Consent wording clear
- [ ] Rights wording does not overpromise
- [ ] Security wording avoids guarantees
- [ ] AI-data-use wording accurate
- [ ] Material terms are conspicuous

---

# 375. AI-Generated Content QA Checklist
<!-- id: terminology.375-ai-generated-content-qa-checklist -->

- [ ] Terminology matches glossary
- [ ] No invented feature names
- [ ] No invented legal terms
- [ ] No unsupported superlatives
- [ ] No fabricated certainty
- [ ] No inconsistent synonyms
- [ ] Proper nouns correct
- [ ] Acronyms correct
- [ ] Technical terms used accurately
- [ ] Human review completed where risk is high

---

# 376. Terminology Quality Score
<!-- id: terminology.376-terminology-quality-score -->

Use this as an internal QA framework.

## Consistency — 20 points

- Canonical terminology used: 5
- Synonyms controlled: 4
- Capitalization consistent: 3
- Acronyms consistent: 3
- Status/action terms consistent: 5

## Clarity — 20 points

- Terms understandable: 5
- Definitions clear: 5
- Ambiguity minimized: 5
- Pronoun references clear: 2
- Sentence wording direct: 3

## Precision — 20 points

- Correct domain terminology: 5
- Actions accurately named: 4
- States accurately named: 4
- Dates/numbers/units precise: 3
- Legal/privacy/technical distinctions preserved: 4

## User Experience — 15 points

- UI labels actionable: 4
- Error wording useful: 3
- Destructive actions explicit: 3
- Navigation predictable: 2
- Help terminology matches product: 3

## Trust / Claims — 10 points

- No unsupported absolutes: 2
- Marketing claims supportable: 2
- Security wording accurate: 2
- Compliance wording accurate: 2
- AI capability wording accurate: 2

## Inclusion / Accessibility — 10 points

- Inclusive wording: 3
- No stigmatizing metaphors: 2
- Plain language: 2
- Accessible labels: 2
- Localization readiness: 1

## Governance — 5 points

- Glossary maintained: 2
- Owners assigned: 1
- Deprecated terms tracked: 1
- Change process defined: 1

---

# 377. Quality Thresholds
<!-- id: terminology.377-quality-thresholds -->

Internal recommendation:

- 90–100 = excellent terminology quality
- 80–89 = strong
- 70–79 = acceptable but needs consistency work
- 60–69 = weak
- below 60 = terminology system requires remediation

Critical wording failures override the numeric score.

---

# 378. Critical Wording Failures
<!-- id: terminology.378-critical-wording-failures -->

Do not publish if wording:

- materially misstates product behavior
- hides a destructive action
- misstates billing
- misstates privacy practices
- misuses a legal definition
- makes an unsupported security guarantee
- makes an unsupported compliance claim
- uses one term for multiple conflicting concepts
- uses multiple conflicting terms for a critical concept
- contains unresolved placeholders
- contains deprecated terminology in critical workflows
- could reasonably cause a user to take the wrong action

---

# 379. Recommended Terminology Glossary Format
<!-- id: terminology.379-recommended-terminology-glossary-format -->

```md
# Workspace

Preferred term: Workspace

Definition:
The top-level area that contains members, projects, settings, and billing.

Plural:
Workspaces

Allowed:
- workspace

Avoid:
- project space
- organization area
- team account

Related terms:
- Organization
- Member
- Project

Audience:
All users

Owner:
Product
```

---

# 380. Recommended Action Vocabulary
<!-- id: terminology.380-recommended-action-vocabulary -->

```text
Create = make a new object
Add = place something into an existing object or collection
Edit = change existing content
Save = persist changes
Publish = make content available to an audience
Archive = preserve but remove from active use
Restore = return archived/recoverable content
Remove = detach without necessarily destroying
Delete = destroy or schedule destruction
Disable = turn off functionality
Deactivate = turn off an account or state, usually reversibly
Revoke = withdraw permission or authorization
Disconnect = end an integration or connection
Cancel = stop a subscription, transaction, or scheduled action
Export = package data for external use
Download = transfer a file to the user's device
Upload = transfer a file into the service
Import = bring external data into the service
Invite = request that another person join
Approve = grant approval
Reject = deny approval
Retry = attempt the same operation again
```

---

# 381. Recommended Account Vocabulary
<!-- id: terminology.381-recommended-account-vocabulary -->

```text
User = individual who uses the product
Member = user who belongs to a workspace or organization
Customer = person or organization purchasing the product
Account = individual sign-in identity unless otherwise defined
Organization = customer entity
Workspace = collaborative operational area
Owner = role with defined ownership powers
Admin = role with administrative permissions
Role = named group of permissions
Permission = authorization to perform a specific action
```

---

# 382. Recommended Status Vocabulary
<!-- id: terminology.382-recommended-status-vocabulary -->

```text
Draft
Pending
In review
Approved
Rejected
Scheduled
Published
Active
Paused
Disabled
Expired
Canceled
Failed
Completed
Archived
Deleted
```

Only use statuses that have defined lifecycle meanings.

---

# 383. Recommended AI Vocabulary
<!-- id: terminology.383-recommended-ai-vocabulary -->

```text
Artificial intelligence (AI) = broad category of computational systems performing tasks associated with intelligent behavior

Machine learning (ML) = systems that learn patterns from data to make predictions or decisions

Generative AI = AI that produces new content such as text, images, audio, video, or code

Model = trained computational system that produces predictions or outputs

Large language model (LLM) = model trained on large amounts of language data to process and generate text

AI assistant = AI-enabled system designed to help users complete tasks or obtain information

AI agent = system capable of pursuing goals through multiple steps or tools with some degree of autonomous action

AI-generated = output substantially produced by an AI system

AI-assisted = content or work created with meaningful AI support but substantial human direction or authorship remains

Automation = predefined or model-driven execution of tasks without continuous manual control
```

---

# 384. Recommended Privacy Vocabulary
<!-- id: terminology.384-recommended-privacy-vocabulary -->

```text
Collect = obtain information from a person, device, or another source

Use = apply information for a defined purpose

Process = perform one or more operations on information

Store = keep information in a system

Retain = continue storing information for a period

Share = disclose information to another party or make it available, subject to applicable definitions

Sell = transfer information in exchange for consideration when the applicable legal definition is met

Transfer = move or make information available across entities, systems, or jurisdictions

Delete = remove information subject to applicable technical and legal exceptions

De-identify = modify information to reduce or prevent association with an identifiable person

Anonymize = render information non-identifiable under the applicable technical or legal standard

Aggregate = combine information across multiple records or individuals
```

---

# 385. Final Standard
<!-- id: terminology.385-final-standard -->

High-quality terminology should make users think about the task, not the wording.

A strong terminology system:

- gives one name to each important concept
- defines terms clearly
- distinguishes similar actions
- avoids ambiguous labels
- uses precise verbs
- preserves technical and legal meaning
- avoids unsupported claims
- supports accessibility
- supports localization
- supports SEO/GEO/AEO
- stays consistent across UI, documentation, marketing, support, and policy
- has owners
- has governance
- evolves intentionally

The best wording is not the most sophisticated wording.

The best wording is the wording that communicates the correct meaning with the least avoidable ambiguity.

# Control Plane Hooks
<!-- id: terminology.control-plane-hooks -->

When this module is active, use `CONTROL_INDEX.md` to retrieve only the capability sections relevant to the current decision. Applicable capabilities include:

- **Unknown-fact policy** — `controls/02-project-intake-and-requirement-resolution.md` (BQ-0046–BQ-0050)
- **Cognitive-load review** — `controls/14-accessibility-and-inclusive-design.md` (BQ-0551–BQ-0555)
- **Message-hierarchy map** — `controls/15-content-copy-and-terminology.md` (BQ-0561–BQ-0565)
- **Category-language calibration** — `controls/15-content-copy-and-terminology.md` (BQ-0566–BQ-0570)
- **Claim-evidence pairing** — `controls/15-content-copy-and-terminology.md` (BQ-0571–BQ-0575)
- **CTA semantic specificity** — `controls/15-content-copy-and-terminology.md` (BQ-0576–BQ-0580)
- **Content-density control** — `controls/15-content-copy-and-terminology.md` (BQ-0581–BQ-0585)
- **Terminology registry** — `controls/15-content-copy-and-terminology.md` (BQ-0586–BQ-0590)
- **Microcopy state coverage** — `controls/15-content-copy-and-terminology.md` (BQ-0591–BQ-0595)
- **Objection coverage** — `controls/16-conversion-trust-and-business-outcomes.md` (BQ-0611–BQ-0615)
- **Post-conversion clarity** — `controls/16-conversion-trust-and-business-outcomes.md` (BQ-0626–BQ-0630)
- **Data-freshness semantics** — `controls/18-application-logic-data-and-integrations.md` (BQ-0701–BQ-0705)
- **Legal-claim boundary** — `controls/19-security-privacy-and-legal-compliance.md` (BQ-0751–BQ-0755)
- **Entity-consistency standard** — `controls/20-seo-geo-aeo-and-discoverability.md` (BQ-0766–BQ-0770)

These hooks are routing pointers, not permission to preload the listed shards. Evidence Gates control pass/fail claims.
