<!--
Pack-Version: 4.0.0
Schema-Version: 3
Module: SEO_GEO_AEO
Module-Version: 1
Last-Updated: 2026-08-09
-->

# SEO / GEO / AEO High-Quality Standards
<!-- id: search.seo-geo-aeo-high-quality-standards -->

Version: 2026-08-09

Purpose: A practical quality standard for creating, reviewing, and publishing web content that is discoverable in traditional search, useful in answer engines, and citation-ready for generative search systems.

---

# 1. Definitions
<!-- id: search.1-definitions -->

## SEO — Search Engine Optimization

SEO is the practice of making content easy for search engines to discover, crawl, index, understand, rank, and present to users.

## GEO — Generative Engine Optimization

GEO is the practice of making content easy for generative search and AI systems to discover, interpret, verify, cite, summarize, and use as a supporting source.

GEO does not replace SEO. Strong technical SEO, useful content, clear entities, verifiable claims, and crawlability are the foundation of generative-search visibility.

## AEO — Answer Engine Optimization

AEO is the practice of structuring content so search engines, assistants, voice systems, and AI answer engines can identify and extract accurate direct answers to user questions.

AEO does not mean writing only short answers. The goal is to provide an immediately useful answer followed by sufficient evidence, context, nuance, and supporting detail.

---

# 2. Standards Language
<!-- id: search.2-standards-language -->

Use these terms consistently:

- MUST = required for publication
- MUST NOT = prohibited
- SHOULD = expected unless there is a documented reason not to do it
- SHOULD NOT = generally avoid
- MAY = optional enhancement

---

# 3. Core Quality Principles
<!-- id: search.3-core-quality-principles -->

Every publishable page MUST:

- Serve a clear user intent.
- Focus on a primary topic.
- Provide useful information that is materially better than a thin summary.
- Be understandable without requiring the reader to infer essential facts.
- Make important information available as readable text.
- Be crawlable and indexable when intended for discovery.
- Use accurate titles and headings.
- Avoid deceptive optimization tactics.
- Avoid unsupported factual claims.
- Distinguish fact from opinion, estimate, interpretation, and speculation.
- Clearly identify important entities such as people, companies, products, places, and organizations.
- Use consistent terminology for the same entity.
- Provide sufficient context for dates, numbers, measurements, and comparisons.
- Be maintained when the subject is time-sensitive.
- Provide a good mobile and desktop experience.
- Use structured data only when it accurately represents visible page content.
- Prioritize user value over keyword density, word count, or artificial optimization formulas.

---

# 4. Search Intent Standard
<!-- id: search.4-search-intent-standard -->

Before creating a page, define:

- Primary query or topic
- Primary user intent
- Secondary intents
- Audience
- Desired user outcome
- Conversion or business outcome, if applicable

Common intent classes:

- Informational
- Navigational
- Commercial investigation
- Transactional
- Local
- Comparison
- Troubleshooting
- Definition
- How-to
- Research
- Current-status
- Recommendation
- Decision support

A page SHOULD satisfy one dominant intent.

A page MAY satisfy closely related secondary intents.

A page SHOULD NOT combine unrelated intents merely to capture more keywords.

---

# 5. Topic Focus Standard
<!-- id: search.5-topic-focus-standard -->

Each indexable URL MUST have a clearly identifiable primary topic.

The following SHOULD align:

- URL
- HTML title
- H1
- opening paragraph
- primary body content
- structured data
- internal anchor text
- image context
- page purpose

Avoid pages that mix unrelated subjects.

Create separate pages when distinct subjects have different search intent or require independent explanation.

---

# 6. URL Standard
<!-- id: search.6-url-standard -->

URLs SHOULD:

- Be readable.
- Be stable.
- Be descriptive.
- Use lowercase where practical.
- Use hyphens between words.
- Avoid unnecessary parameters.
- Avoid session IDs.
- Avoid meaningless numeric identifiers when a descriptive slug is practical.
- Reflect logical site hierarchy without becoming excessively deep.

Example:

`/seo/technical-seo/canonical-tags/`

Avoid:

`/page?id=849203&ref=x2/`

A canonical content item SHOULD have one preferred URL.

Duplicate or substantially equivalent URLs SHOULD use:

- redirects when appropriate, or
- canonical signals when duplication must remain accessible.

---

# 7. Crawlability Standard
<!-- id: search.7-crawlability-standard -->

Pages intended for search visibility MUST:

- Return an appropriate successful HTTP response.
- Be accessible to the intended search crawler.
- Not be accidentally blocked by robots.txt.
- Not be blocked by authentication unless intentionally private.
- Not require unsupported user interaction to reveal all important content.
- Allow access to critical CSS, JavaScript, images, and other resources needed to render or understand the page.

Critical content SHOULD be available in the initial rendered experience.

Important factual information SHOULD NOT exist only inside:

- canvas graphics
- images
- video
- client-side widgets
- hover states
- inaccessible accordions
- downloadable files

when a textual version can reasonably be provided.

---

# 8. Indexability Standard
<!-- id: search.8-indexability-standard -->

Indexable pages MUST NOT contain an unintended `noindex`.

Pages intentionally excluded from search SHOULD use the correct index-control method.

Do not use robots.txt as a substitute for `noindex`.

If a crawler must read a `noindex` directive, the crawler must be allowed to crawl the page.

Indexable pages SHOULD:

- have a canonical URL
- be internally linked
- appear in an XML sitemap when appropriate
- avoid soft-404 behavior
- avoid redirect chains
- avoid conflicting canonical signals

---

# 9. Sitemap Standard
<!-- id: search.9-sitemap-standard -->

XML sitemaps SHOULD:

- contain canonical URLs only
- contain indexable URLs only
- exclude redirects
- exclude 4xx and 5xx URLs
- exclude duplicate URLs
- use accurate modification dates when supplied
- be refreshed as content changes
- be submitted to relevant webmaster platforms

Large sites SHOULD split sitemaps logically when helpful.

---

# 10. Internal Linking Standard
<!-- id: search.10-internal-linking-standard -->

Every important page SHOULD have at least one crawlable internal link from another relevant page.

Internal links SHOULD:

- use descriptive anchor text
- connect semantically related content
- support a logical information hierarchy
- help users continue their task
- avoid excessive repetition
- avoid generic anchors when a descriptive anchor is practical

Prefer:

`technical SEO audit checklist`

over:

`click here`

Orphan pages SHOULD NOT be published intentionally unless there is a specific reason.

---

# 11. Navigation Standard
<!-- id: search.11-navigation-standard -->

Primary navigation SHOULD reflect the site's major user-facing topics.

Breadcrumbs SHOULD be used on deeper sites when they help users understand hierarchy.

Navigation MUST:

- work on mobile
- be keyboard accessible
- avoid deceptive links
- distinguish navigation from advertising

---

# 12. HTML Title Standard
<!-- id: search.12-html-title-standard -->

Every indexable page MUST have a unique, descriptive `<title>`.

The title SHOULD:

- accurately describe the page
- clearly communicate the main topic
- differentiate the page from other pages
- place the most meaningful information early
- be concise enough to remain understandable if truncated

The title MUST NOT:

- misrepresent the content
- repeat keywords unnaturally
- use boilerplate so heavily that pages become indistinguishable
- contain claims unsupported by the page

Do not treat a fixed character count as a ranking rule.

---

# 13. H1 Standard
<!-- id: search.13-h1-standard -->

Each page SHOULD have one clear primary H1 representing the page's main subject.

The H1 SHOULD:

- match user intent
- be descriptive
- be understandable out of context
- align closely with the title without requiring exact duplication

Do not use headings solely for visual styling.

---

# 14. Heading Hierarchy Standard
<!-- id: search.14-heading-hierarchy-standard -->

Use headings to represent document structure.

Recommended hierarchy:

- H1 = primary page topic
- H2 = major sections
- H3 = subsections
- H4+ = deeper subdivisions when necessary

Headings SHOULD:

- be descriptive
- summarize the section below
- use natural language
- make the page skimmable
- expose important subtopics and questions

Avoid empty headings and keyword-stuffed headings.

---

# 15. Meta Description Standard
<!-- id: search.15-meta-description-standard -->

Important indexable pages SHOULD have a unique meta description.

A meta description SHOULD:

- summarize the page accurately
- communicate the primary benefit or answer
- distinguish the page from competing results
- use natural language
- encourage qualified clicks without clickbait

Meta descriptions are not guaranteed to be displayed exactly as written.

Do not rely on meta descriptions to compensate for weak page content.

---

# 16. Opening Answer Standard
<!-- id: search.16-opening-answer-standard -->

For informational, definition, comparison, troubleshooting, and how-to pages, the opening section SHOULD answer the primary question quickly.

Recommended pattern:

1. Direct answer
2. Essential qualifier or condition
3. Supporting explanation
4. Evidence or examples
5. Deeper detail

The user SHOULD NOT need to read a long introduction before learning the core answer.

---

# 17. Answer Block Standard
<!-- id: search.17-answer-block-standard -->

Important questions SHOULD have a self-contained answer block.

A strong answer block:

- repeats enough context to make sense independently
- directly answers the question
- identifies the subject explicitly
- avoids unnecessary pronouns
- defines specialized terms
- includes necessary qualifiers
- avoids promotional filler
- avoids unsupported certainty

---

# 18. Question Heading Standard
<!-- id: search.18-question-heading-standard -->

Use question-form headings when users genuinely search or think in question form.

Examples:

- What is technical SEO?
- How does canonicalization work?
- When should a page use noindex?
- What is the difference between SEO and GEO?

Do not turn every heading into a question artificially.

---

# 19. Definition Standard
<!-- id: search.19-definition-standard -->

Important concepts SHOULD be explicitly defined.

A definition SHOULD:

- name the concept
- state what it is
- distinguish it from adjacent concepts when confusion is likely
- avoid circular definitions
- avoid unexplained jargon

When acronyms are used, spell them out on first meaningful use.

---

# 20. Entity Clarity Standard
<!-- id: search.20-entity-clarity-standard -->

Important entities MUST be clearly named.

For people, organizations, products, locations, standards, and services:

- use the canonical or commonly recognized name
- avoid ambiguous pronouns where citation context matters
- maintain naming consistency
- include necessary disambiguating details
- state relationships explicitly

---

# 21. Entity Consistency Standard
<!-- id: search.21-entity-consistency-standard -->

Site-wide entity information SHOULD remain consistent across:

- homepage
- About page
- contact information
- author pages
- product pages
- organization schema
- local profiles
- social profiles
- external citations where controllable

Important facts such as company name, address, phone, founding date, product name, and executive names SHOULD NOT conflict between pages.

---

# 22. Factual Claim Standard
<!-- id: search.22-factual-claim-standard -->

Every material factual claim SHOULD be:

- accurate
- current enough for the topic
- specific
- independently understandable
- supported by evidence when the claim is not common knowledge

Claims involving the following require especially strong sourcing:

- statistics
- medical information
- legal information
- financial information
- scientific findings
- product specifications
- prices
- regulations
- dates
- public officeholders
- safety guidance
- comparative performance

---

# 23. Source Quality Standard
<!-- id: search.23-source-quality-standard -->

Prefer sources in this order when appropriate:

1. Primary source
2. Official documentation
3. Government or standards body
4. Original research
5. Peer-reviewed research
6. Direct company documentation
7. Highly reputable secondary source
8. Specialist publication
9. Other sources with clear provenance

Do not cite a source merely because it ranks highly.

The source must actually support the claim.

---

# 24. Citation Standard
<!-- id: search.24-citation-standard -->

When external evidence materially supports the page, citations SHOULD be provided near the relevant claim.

Citations SHOULD:

- identify the source clearly
- point to the original source where practical
- avoid citation laundering
- avoid citing a source that cites another source when the original is available
- distinguish primary from secondary evidence
- remain accessible
- use descriptive anchor text

For important statistics, include:

- value
- unit
- subject
- geography if relevant
- time period
- source
- methodology or limitation when material

---

# 25. Originality Standard
<!-- id: search.25-originality-standard -->

High-quality content SHOULD add original value.

Examples:

- first-party data
- original research
- expert analysis
- direct testing
- real examples
- proprietary datasets
- practical frameworks
- calculations
- decision criteria
- comparisons
- diagrams
- photographs
- interviews
- case studies
- implementation detail
- firsthand experience

A page SHOULD NOT exist merely to paraphrase pages that already rank.

---

# 26. Information Gain Standard
<!-- id: search.26-information-gain-standard -->

A page SHOULD contribute at least one meaningful element that is not obvious from generic summaries.

Possible information gain:

- new evidence
- better synthesis
- clearer explanation
- a useful taxonomy
- practical implementation steps
- original examples
- exceptions and edge cases
- updated facts
- expert interpretation
- structured comparison
- troubleshooting guidance
- calculations
- decision support

---

# 27. Completeness Standard
<!-- id: search.27-completeness-standard -->

Content SHOULD cover the information necessary to fulfill the primary intent.

Completeness does not mean maximum length.

Include:

- direct answer
- relevant definitions
- necessary context
- important conditions
- major alternatives
- limitations
- next steps when applicable

Exclude:

- filler
- repetition
- unrelated history
- boilerplate inserted only to increase word count

---

# 28. Concision Standard
<!-- id: search.28-concision-standard -->

Use the shortest wording that preserves accuracy, context, and usefulness.

Avoid:

- throat-clearing introductions
- repeated conclusions
- redundant headings
- keyword variations added solely for search engines
- generic statements that add no information

A short complete page can outperform a long incomplete page.

---

# 29. Readability Standard
<!-- id: search.29-readability-standard -->

Content SHOULD:

- use clear sentences
- define technical language
- keep paragraphs focused
- use lists for genuinely list-like information
- use tables for meaningful comparisons
- use examples for abstract concepts
- keep important conclusions easy to locate

Do not oversimplify to the point of losing accuracy.

---

# 30. Evidence-to-Claim Proximity Standard
<!-- id: search.30-evidence-to-claim-proximity-standard -->

Evidence SHOULD appear close to the claim it supports.

Avoid placing all sources at the bottom without indicating which claim each source supports.

For long pages, cite evidence at section level or claim level where practical.

---

# 31. Dates and Freshness Standard
<!-- id: search.31-dates-and-freshness-standard -->

Time-sensitive content MUST make its temporal context clear.

Use explicit dates when ambiguity is possible.

Include:

- publication date when useful
- last updated date when meaningful
- effective date for rules or regulations
- data period for statistics
- version number for software or standards when relevant

Do not change an "updated" date unless the content was materially reviewed or changed.

---

# 32. Maintenance Standard
<!-- id: search.32-maintenance-standard -->

Pages covering changing topics SHOULD have a review schedule.

High-change topics MAY require frequent review:

- software
- laws
- regulations
- pricing
- product specifications
- search engine documentation
- public officials
- medical guidance
- financial rules
- event information

Stale claims SHOULD be corrected, removed, or clearly marked as historical.

---

# 33. Author and Responsibility Standard
<!-- id: search.33-author-and-responsibility-standard -->

Pages where expertise materially affects trust SHOULD identify the responsible author, reviewer, or organization.

Useful author information MAY include:

- full name
- role
- relevant experience
- credentials
- subject expertise
- links to other work

Do not invent credentials.

Do not create fake reviewer profiles.

---

# 34. About and Contact Standard
<!-- id: search.34-about-and-contact-standard -->

Commercial and professional sites SHOULD make organizational identity easy to verify.

Provide where relevant:

- organization name
- About page
- contact method
- physical address for location-dependent businesses
- support information
- editorial policy
- corrections policy
- privacy policy
- terms
- ownership disclosures
- affiliate or sponsorship disclosures

---

# 35. Transparency Standard
<!-- id: search.35-transparency-standard -->

Content MUST disclose material relationships that may affect interpretation.

Examples:

- affiliate relationships
- sponsorship
- paid placement
- product samples
- conflicts of interest
- AI-assisted production where disclosure is required by policy or editorial standards

Editorial claims SHOULD remain distinguishable from advertising.

---

# 36. AI-Generated Content Standard
<!-- id: search.36-ai-generated-content-standard -->

AI-assisted content MUST meet the same accuracy, originality, usefulness, and editorial standards as human-created content.

AI MUST NOT be used to mass-produce low-value pages intended primarily to manipulate search or generative systems.

AI-assisted pages SHOULD undergo human review when:

- the subject is high stakes
- claims require verification
- sources may have changed
- nuanced expertise is required
- the content affects purchasing or financial decisions
- legal or medical accuracy matters

The production method is less important than the resulting quality and compliance.

---

# 37. Keyword Standard
<!-- id: search.37-keyword-standard -->

Keywords SHOULD be treated as indicators of user language and intent, not quotas.

Use important terms naturally in:

- title
- H1
- opening section
- relevant headings
- body copy
- image alt text when genuinely descriptive
- internal anchor text
- metadata

Do not use arbitrary keyword-density targets.

Do not repeat exact-match phrases unnaturally.

Use synonyms and related terminology where they improve clarity.

---

# 38. Semantic Coverage Standard
<!-- id: search.38-semantic-coverage-standard -->

A page SHOULD include the concepts necessary to explain its topic accurately.

Semantic coverage MAY include:

- definitions
- components
- causes
- effects
- steps
- alternatives
- examples
- entities
- measurements
- risks
- exceptions
- related terms

Semantic coverage MUST remain relevant to the page intent.

---

# 39. Topical Architecture Standard
<!-- id: search.39-topical-architecture-standard -->

Sites SHOULD organize related content into coherent topic areas.

A topic area MAY include:

- primary guide
- supporting subtopic pages
- comparison pages
- glossary or definitions
- troubleshooting pages
- case studies
- tools
- original research

Internal linking SHOULD make relationships between these pages clear.

Do not create dozens of near-duplicate pages for trivial keyword variations.

---

# 40. Cannibalization Standard
<!-- id: search.40-cannibalization-standard -->

Multiple pages SHOULD NOT compete for the same intent without a clear reason.

When substantial overlap exists:

- consolidate content
- differentiate intent
- redirect obsolete pages
- update internal links
- review canonical signals

---

# 41. Structured Data Standard
<!-- id: search.41-structured-data-standard -->

Structured data MUST:

- represent visible page content accurately
- use appropriate schema vocabulary
- avoid fabricated values
- avoid misleading ratings or reviews
- use valid syntax
- match the page's actual entity and purpose

JSON-LD is generally preferred for Google implementations where supported.

Structured data SHOULD be validated before deployment.

Structured data MAY help machines understand content but does not guarantee rankings, rich results, citations, or generative inclusion.

---

# 42. Structured Data Selection Standard
<!-- id: search.42-structured-data-selection-standard -->

Use only schema types that accurately fit the content.

Common useful types include, when applicable:

- Organization
- WebSite
- Article
- BlogPosting
- BreadcrumbList
- Product
- Offer
- LocalBusiness
- Person
- Event
- VideoObject
- Dataset
- SoftwareApplication
- Recipe
- JobPosting
- ProfilePage
- QAPage
- FAQPage where appropriate and supported

Do not add schema merely because a type exists.

Do not assume all Schema.org types generate search features.

---

# 43. Organization Identity Standard
<!-- id: search.43-organization-identity-standard -->

Organizations SHOULD provide clear machine-readable identity information where appropriate.

Useful properties MAY include:

- name
- legal name
- URL
- logo
- contact details
- address
- sameAs
- founding date
- parent organization
- brand

Values MUST match visible and verifiable information.

---

# 44. Person / Author Entity Standard
<!-- id: search.44-person-author-entity-standard -->

Author or profile pages MAY use Person or ProfilePage markup when appropriate.

Useful information MAY include:

- name
- role
- organization
- expertise
- works
- sameAs links
- image

Do not use schema to claim credentials or affiliations that are not true.

---

# 45. Image Standard
<!-- id: search.45-image-standard -->

Images SHOULD:

- add informational or visual value
- be high quality
- appear near relevant text
- have descriptive filenames where practical
- use accurate alt text when alt text is appropriate
- specify dimensions to reduce layout shift
- be compressed efficiently
- use modern formats where appropriate
- remain crawlable when intended for search

Alt text MUST describe the image's purpose, not stuff keywords.

Decorative images SHOULD use appropriate empty alt handling.

---

# 46. Video Standard
<!-- id: search.46-video-standard -->

Video pages SHOULD provide enough textual context for users and machines to understand the subject.

Where relevant, provide:

- descriptive title
- description
- transcript
- chapters
- captions
- thumbnail
- upload date
- duration
- relevant structured data

Important information SHOULD NOT exist exclusively in video.

---

# 47. Accessibility Standard
<!-- id: search.47-accessibility-standard -->

Pages SHOULD conform to modern accessibility practices.

At minimum:

- meaningful semantic HTML
- keyboard-accessible controls
- visible focus states
- labeled form fields
- descriptive buttons
- accessible navigation
- appropriate ARIA where native HTML is insufficient
- text alternatives for meaningful images
- sufficient contrast
- logical reading order

Accessibility improves user experience and may also improve machine understanding of interactive pages.

---

# 48. Core Web Vitals Standard
<!-- id: search.48-core-web-vitals-standard -->

Target "good" Core Web Vitals using real-user data when available:

- LCP: 2.5 seconds or less
- INP: less than 200 milliseconds
- CLS: less than 0.1

Performance work SHOULD prioritize real user experience, not score chasing.

---

# 49. Page Experience Standard
<!-- id: search.49-page-experience-standard -->

Pages SHOULD:

- use HTTPS
- work well on mobile
- avoid intrusive interstitials
- avoid excessive ads that obscure content
- make primary content easy to distinguish
- load predictably
- keep controls stable during interaction
- avoid unnecessary layout shifts
- avoid broken functionality

---

# 50. Mobile Standard
<!-- id: search.50-mobile-standard -->

Mobile pages MUST contain the important content available to users.

Mobile experiences SHOULD maintain:

- content parity
- metadata parity
- structured-data parity
- internal-link accessibility
- image accessibility
- functional navigation

Do not hide essential content from mobile users.

---

# 51. JavaScript Standard
<!-- id: search.51-javascript-standard -->

JavaScript MAY be used, but critical content SHOULD remain reliably renderable and discoverable.

Validate:

- server response
- rendered HTML
- crawl access
- canonical tags
- meta robots
- internal links
- structured data
- lazy-loaded content

Important metadata SHOULD NOT be generated inconsistently.

---

# 52. HTTP Status Standard
<!-- id: search.52-http-status-standard -->

Use HTTP status codes accurately.

Typical expectations:

- 200 = successful page
- 301/308 = permanent redirect
- 302/307 = temporary redirect
- 404/410 = unavailable or removed content
- 5xx = server failure

Do not return 200 for pages that are functionally missing.

---

# 53. Redirect Standard
<!-- id: search.53-redirect-standard -->

Redirects SHOULD:

- go directly to the final destination
- avoid chains
- avoid loops
- preserve user intent
- point to the most relevant replacement

Mass redirects to an unrelated homepage SHOULD be avoided.

---

# 54. Canonical Standard
<!-- id: search.54-canonical-standard -->

Canonical signals SHOULD be consistent.

A canonical page SHOULD normally:

- self-canonicalize
- be indexable
- return 200
- be internally linked
- appear in the sitemap
- contain the preferred content

Avoid canonicalizing unrelated pages together.

---

# 55. International SEO Standard
<!-- id: search.55-international-seo-standard -->

For multilingual or multi-regional sites:

- provide high-quality localized content
- use stable regional URLs
- implement hreflang correctly where appropriate
- include self-referencing hreflang
- avoid automatic redirects that prevent users or crawlers from accessing versions
- maintain equivalent page intent across language alternates

Machine translation SHOULD be reviewed when quality matters.

---

# 56. Local SEO Standard
<!-- id: search.56-local-seo-standard -->

Local businesses SHOULD keep core business information accurate and consistent.

Important information includes:

- business name
- address
- phone
- opening hours
- service area
- category
- website
- products or services
- location-specific information

Location pages MUST provide genuine location-specific value.

Do not create doorway pages for locations where the business has no meaningful presence or service differentiation.

---

# 57. Ecommerce Standard
<!-- id: search.57-ecommerce-standard -->

Product pages SHOULD clearly expose:

- product name
- description
- price
- currency
- availability
- condition when relevant
- variants
- shipping information
- return information
- images
- reviews when authentic
- manufacturer or brand
- identifiers such as GTIN/MPN when available

Product information SHOULD remain consistent between visible content, feeds, structured data, and merchant systems.

---

# 58. Review Standard
<!-- id: search.58-review-standard -->

Reviews MUST be authentic.

Do not:

- fabricate reviews
- hide negative reviews selectively in a deceptive manner
- mark up reviews that do not exist visibly
- aggregate ratings inaccurately
- present editorial claims as customer reviews

Review methodology SHOULD be disclosed for editorial product comparisons.

---

# 59. Comparison Page Standard
<!-- id: search.59-comparison-page-standard -->

Comparison pages SHOULD state:

- what is being compared
- criteria
- measurement basis
- important differences
- limitations
- who each option is best for
- date or version when products change frequently

Tables SHOULD contain meaningful comparable attributes rather than filler.

---

# 60. Recommendation Page Standard
<!-- id: search.60-recommendation-page-standard -->

Recommendations SHOULD explain why each item is recommended.

Where relevant, disclose:

- selection criteria
- testing method
- research method
- commercial relationships
- limitations
- audience fit
- alternatives

Avoid unsupported "best" claims.

---

# 61. How-To Standard
<!-- id: search.61-how-to-standard -->

How-to content SHOULD include:

- clear objective
- prerequisites
- steps in correct order
- warnings where necessary
- expected result
- troubleshooting
- version or platform when relevant

Each step SHOULD be actionable and independently understandable.

---

# 62. Troubleshooting Standard
<!-- id: search.62-troubleshooting-standard -->

Troubleshooting pages SHOULD structure solutions around:

1. symptom
2. likely causes
3. diagnostic checks
4. solutions
5. verification
6. escalation path

Do not bury the likely fix under long generic explanation.

---

# 63. FAQ Standard
<!-- id: search.63-faq-standard -->

FAQ sections SHOULD contain genuine user questions.

Answers SHOULD:

- be direct
- be self-contained
- avoid duplicate wording
- provide enough context to stand alone
- link to deeper pages when necessary

FAQ schema should only be used where it is appropriate, accurate, visible, and supported.

FAQ content SHOULD exist because users need it, not merely to generate schema.

---

# 64. AEO Direct-Answer Standard
<!-- id: search.64-aeo-direct-answer-standard -->

For important user questions, provide an extractable answer.

Internal quality target:

- answer the question in the first 1–3 sentences when practical
- name the subject explicitly
- avoid introductory filler
- include the key condition or exception
- follow with supporting depth

This is an editorial quality target, not a search-engine ranking formula.

---

# 65. AEO Answer Completeness Standard
<!-- id: search.65-aeo-answer-completeness-standard -->

A direct answer SHOULD be understandable when extracted from its surrounding page.

Include necessary:

- subject
- action
- condition
- unit
- timeframe
- comparison basis

Avoid references such as:

- "this"
- "it"
- "they"
- "the above"

when the referent would be unclear outside the section.

---

# 66. AEO Format Selection Standard
<!-- id: search.66-aeo-format-selection-standard -->

Use the format that best matches the question.

Use:

- paragraph for definitions
- ordered list for steps
- unordered list for options
- table for comparisons
- equation for calculations
- timeline for chronology
- FAQ for discrete questions
- decision tree for conditional choices

Do not force all information into paragraphs.

---

# 67. AEO Calculation Standard
<!-- id: search.67-aeo-calculation-standard -->

For calculations:

- state the formula
- define variables
- show units
- provide an example
- state rounding rules
- note assumptions

Answers involving numeric outputs SHOULD be reproducible.

---

# 68. AEO Voice Readability Standard
<!-- id: search.68-aeo-voice-readability-standard -->

Important answers SHOULD remain understandable when read aloud.

Avoid:

- unexplained abbreviations
- excessive parenthetical detail
- ambiguous symbols
- overly long sentences
- context-dependent references

This improves usability for voice assistants and accessibility.

---

# 69. GEO Citation-Readiness Standard
<!-- id: search.69-geo-citation-readiness-standard -->

Content intended to be useful as a generative source SHOULD make important facts easy to verify.

Citation-ready content:

- states facts explicitly
- names entities
- includes dates where relevant
- identifies the source or method
- avoids vague attribution
- separates facts from opinion
- provides stable URLs
- provides enough surrounding context to avoid misquotation

---

# 70. GEO Standalone Statement Standard
<!-- id: search.70-geo-standalone-statement-standard -->

Important claims SHOULD stand on their own.

Prefer explicit, context-rich claims over vague statements whose subject is only clear from surrounding text.

---

# 71. GEO Provenance Standard
<!-- id: search.71-geo-provenance-standard -->

Original data or research SHOULD disclose provenance.

Include, when relevant:

- who collected the data
- collection date
- sample size
- methodology
- geography
- definitions
- exclusions
- calculation method
- update cadence
- limitations

Original statistics without methodology SHOULD NOT be presented as authoritative evidence.

---

# 72. GEO Source Attribution Standard
<!-- id: search.72-geo-source-attribution-standard -->

When synthesizing external information:

- identify the primary source where possible
- avoid unattributed claims
- avoid "experts say" without identifying experts
- avoid "studies show" without identifying the study
- use explicit source names
- keep citations close to claims

Generative systems are more likely to use information confidently when provenance is clear and independently verifiable.

---

# 73. GEO Entity Relationship Standard
<!-- id: search.73-geo-entity-relationship-standard -->

Important relationships SHOULD be written explicitly.

Examples:

- company → product
- person → role
- product → manufacturer
- location → organization
- study → institution
- standard → standards body

Avoid relying solely on design or page layout to imply relationships.

---

# 74. GEO Query Fan-Out Readiness Standard
<!-- id: search.74-geo-query-fan-out-readiness-standard -->

Content SHOULD anticipate useful subquestions around the primary topic.

For a major topic, consider covering:

- definition
- mechanism
- requirements
- alternatives
- comparisons
- cost
- limitations
- risks
- implementation
- examples
- troubleshooting
- related concepts

These sections SHOULD remain useful independently.

Do not create artificial subtopics merely to increase page breadth.

---

# 75. GEO Passage Quality Standard
<!-- id: search.75-geo-passage-quality-standard -->

Each major section SHOULD have:

- a clear heading
- a clear subject
- a direct opening statement
- supporting evidence
- enough context to stand alone
- minimal unnecessary dependency on previous sections

This makes individual passages easier to retrieve and interpret.

---

# 76. GEO Source Differentiation Standard
<!-- id: search.76-geo-source-differentiation-standard -->

A page SHOULD make it easy to distinguish:

- original findings
- sourced facts
- interpretation
- opinion
- forecast
- recommendation
- sponsored content

Do not present predictions as established facts.

---

# 77. GEO Machine Access Standard
<!-- id: search.77-geo-machine-access-standard -->

If the goal includes visibility in AI search systems, relevant crawlers SHOULD be permitted intentionally.

Crawler policy SHOULD be decided intentionally rather than copied from a generic robots.txt file.

Training crawlers and search/discovery crawlers SHOULD be treated as separate controls when providers expose separate user-agents.

---

# 78. GEO robots.txt Standard
<!-- id: search.78-geo-robots-txt-standard -->

Maintain a documented crawler policy.

Do not assume all AI crawlers use the same user-agent.

Revalidate crawler documentation periodically.

---

# 79. GEO AI-Specific File Standard
<!-- id: search.79-geo-ai-specific-file-standard -->

Do not depend on non-standard AI-specific files as a prerequisite for generative visibility.

Experimental files MAY be published if useful operationally, but they MUST NOT replace:

- crawlability
- indexing
- internal links
- structured content
- strong source quality
- standard metadata
- structured data where appropriate

---

# 80. GEO Structured Data Standard
<!-- id: search.80-geo-structured-data-standard -->

Structured data SHOULD support entity and page understanding, but MUST reflect visible content.

There is no universal "GEO schema."

Do not invent unsupported schema properties.

Do not assume schema alone causes generative citation.

---

# 81. GEO Accessibility and Agent Readiness Standard
<!-- id: search.81-geo-accessibility-and-agent-readiness-standard -->

Interactive sites SHOULD use semantic HTML and accessible controls.

Where appropriate:

- label buttons
- label forms
- expose state changes
- use native controls first
- apply ARIA when necessary
- make interactive actions understandable without visual guessing

This benefits humans, assistive technology, and automated agents.

---

# 82. GEO Freshness Standard
<!-- id: search.82-geo-freshness-standard -->

For time-sensitive facts, expose freshness clearly.

Useful signals include:

- visible updated date
- accurate sitemap modification time
- version number
- effective date
- current availability
- current price
- current officeholder or role
- current product specification

Freshness signals MUST be truthful.

---

# 83. GEO Verifiability Standard
<!-- id: search.83-geo-verifiability-standard -->

A claim SHOULD be independently verifiable whenever practical.

High-quality pages make verification easy through:

- source links
- methodology
- author identity
- organization identity
- original documents
- data tables
- version history
- correction notes

---

# 84. GEO Citation Target Standard
<!-- id: search.84-geo-citation-target-standard -->

Do not optimize for a specific citation count.

Instead, optimize for:

- factual usefulness
- originality
- authority
- clarity
- passage independence
- source transparency
- crawl access
- technical reliability

Citation selection remains system-dependent and is not guaranteed.

---

# 85. Anti-Manipulation Standard
<!-- id: search.85-anti-manipulation-standard -->

MUST NOT use:

- hidden text
- cloaking
- doorway pages
- scraped content without added value
- mass-generated low-value pages
- fake authors
- fake expertise
- fake reviews
- fabricated citations
- misleading structured data
- expired-domain abuse
- link schemes
- keyword stuffing
- machine-generated gibberish
- pages created solely to manipulate AI answers
- false claims of authority
- deceptive redirects

Optimization must not depend on misleading users or machines.

---

# 86. Link Quality Standard
<!-- id: search.86-link-quality-standard -->

Outbound links SHOULD support the user's task.

Use external links when they:

- provide evidence
- identify a primary source
- enable verification
- offer necessary official documentation
- provide useful next steps

Do not avoid useful external links solely because they may send users elsewhere.

---

# 87. Backlink / Authority Standard
<!-- id: search.87-backlink-authority-standard -->

Authority SHOULD be earned through value, not manufactured.

Preferred methods include:

- original research
- useful tools
- strong reference content
- public data
- expert commentary
- industry participation
- legitimate PR
- partnerships
- high-quality resources

Avoid paid or exchanged links intended primarily to manipulate rankings.

---

# 88. Digital PR Standard
<!-- id: search.88-digital-pr-standard -->

Digital PR SHOULD create real informational value.

Good assets include:

- research
- datasets
- surveys
- expert analysis
- visualizations
- public tools
- industry reports
- transparent methodology

Do not manufacture controversy or false statistics for links.

---

# 89. Brand Mention Standard
<!-- id: search.89-brand-mention-standard -->

Brand visibility across credible independent sources MAY strengthen entity recognition and user trust.

Prioritize:

- accurate mentions
- consistent naming
- reputable publications
- relevant industry sources
- official directories where appropriate
- genuine expert participation

Do not spam forums, directories, or communities for mentions.

---

# 90. Content Update Standard
<!-- id: search.90-content-update-standard -->

When updating a page:

- verify facts again
- update outdated examples
- update screenshots when necessary
- update citations
- remove dead links
- refresh structured data
- review title and headings
- preserve useful historical context when relevant

Do not change dates solely to simulate freshness.

---

# 91. Editorial Review Standard
<!-- id: search.91-editorial-review-standard -->

Before publication, a reviewer SHOULD verify:

- factual accuracy
- source support
- search intent
- title/H1 alignment
- direct answer quality
- entity clarity
- internal links
- external citations
- structured data
- spelling and grammar
- accessibility
- mobile rendering
- crawl/index settings
- canonical URL
- page speed risks
- conversion path

---

# 92. High-Stakes Content Standard
<!-- id: search.92-high-stakes-content-standard -->

Medical, legal, financial, safety, and other high-stakes content MUST receive stronger review.

High-stakes pages SHOULD:

- use authoritative sources
- state jurisdiction or applicability
- include review dates
- identify qualified reviewers when appropriate
- disclose limitations
- avoid unsupported diagnosis or individualized guarantees
- distinguish general information from professional advice

---

# 93. Editorial Correction Standard
<!-- id: search.93-editorial-correction-standard -->

Sites publishing factual content SHOULD have a correction process.

Material corrections SHOULD:

- be made promptly
- update affected claims
- update sources
- note the correction when transparency requires it
- avoid silently preserving known inaccuracies

---

# 94. Content Pruning Standard
<!-- id: search.94-content-pruning-standard -->

Low-value pages SHOULD be improved, consolidated, redirected, noindexed, or removed based on user value and site architecture.

Do not prune solely because a page has low traffic.

Evaluate:

- usefulness
- uniqueness
- search demand
- link value
- conversion role
- topical role
- freshness
- duplication

---

# 95. Pagination Standard
<!-- id: search.95-pagination-standard -->

Paginated content SHOULD:

- use crawlable URLs
- expose navigation links
- avoid infinite-scroll-only discovery
- maintain stable canonical behavior
- provide access to important items

Do not canonicalize all paginated pages to page one when each contains unique items that need discovery.

---

# 96. Faceted Navigation Standard
<!-- id: search.96-faceted-navigation-standard -->

Large catalog sites SHOULD control crawl expansion caused by filters and sorting.

Decide intentionally which facets deserve indexable landing pages.

Low-value combinations SHOULD NOT create unlimited crawlable URLs.

---

# 97. Search Results Page Standard
<!-- id: search.97-search-results-page-standard -->

Internal search result pages SHOULD generally not be used as substitutes for curated landing pages.

Pages intended for organic discovery SHOULD provide stable, purposeful content rather than arbitrary query results.

---

# 98. Taxonomy Standard
<!-- id: search.98-taxonomy-standard -->

Categories SHOULD:

- have clear definitions
- avoid excessive overlap
- use consistent naming
- reflect user language
- support logical browsing
- avoid creating empty or near-empty archive pages

Subcategories SHOULD be distinct enough to justify separate pages.

---

# 99. Glossary Standard
<!-- id: search.99-glossary-standard -->

Glossary pages SHOULD provide real definitions, not one-sentence keyword placeholders.

A strong glossary entry MAY include:

- definition
- context
- example
- related terms
- distinction from similar concepts
- authoritative source

---

# 100. Content Template Standard
<!-- id: search.100-content-template-standard -->

Templates MAY standardize quality but MUST NOT cause pages to become near-duplicates.

Templates SHOULD preserve room for:

- unique data
- local details
- examples
- evidence
- expert commentary
- actual differences

---

# 101. Programmatic SEO Standard
<!-- id: search.101-programmatic-seo-standard -->

Programmatic pages MUST provide unique user value at scale.

Each page SHOULD contain meaningful differentiated data or functionality.

Do not generate pages solely by swapping:

- city names
- product names
- keywords
- job titles
- industries

without unique value.

---

# 102. AI / Programmatic Publishing Gate
<!-- id: search.102-ai-programmatic-publishing-gate -->

Automated page generation MUST have controls for:

- factual validation
- duplication
- hallucinations
- missing values
- broken links
- canonicalization
- indexability
- structured data
- formatting
- policy compliance
- minimum information value

Publishing at scale increases the need for stricter QA, not weaker QA.

---

# 103. Technical Monitoring Standard
<!-- id: search.103-technical-monitoring-standard -->

Monitor at minimum:

- crawl errors
- server errors
- robots.txt changes
- noindex changes
- canonical changes
- sitemap errors
- structured data errors
- Core Web Vitals
- broken internal links
- redirect chains
- orphan pages
- index coverage
- template regressions

---

# 104. SEO Measurement Standard
<!-- id: search.104-seo-measurement-standard -->

Measure performance using outcomes relevant to the business.

Potential metrics:

- qualified organic visits
- search impressions
- clicks
- click-through rate
- indexed pages
- ranking visibility
- non-brand visibility
- conversions
- revenue
- leads
- assisted conversions
- engagement
- return visitors

Do not judge SEO solely by rank position.

---

# 105. GEO Measurement Standard
<!-- id: search.105-geo-measurement-standard -->

Where data is available, track:

- AI-search referral traffic
- generative-search impressions
- citations or source appearances
- brand mentions in AI results
- landing pages receiving AI traffic
- query categories producing AI traffic
- conversions from AI referrals

Treat manual citation tracking cautiously because generative answers vary by:

- query wording
- location
- time
- model
- personalization
- retrieval state

---

# 106. AEO Measurement Standard
<!-- id: search.106-aeo-measurement-standard -->

Potential AEO indicators include:

- featured snippet presence
- answer-box visibility
- People Also Ask visibility
- voice-answer inclusion where measurable
- clicks from question queries
- long-tail query impressions
- answer-section engagement
- conversions from informational entry pages

Do not optimize for zero-click visibility without considering business value.

---

# 107. Conversion Quality Standard
<!-- id: search.107-conversion-quality-standard -->

SEO, GEO, and AEO success SHOULD ultimately support meaningful user outcomes.

Examples:

- purchase
- lead
- signup
- consultation
- download
- support resolution
- successful information retrieval
- qualified referral
- product adoption

Traffic without useful outcomes is not sufficient evidence of quality.

---

# 108. 100-Point Page Quality Score
<!-- id: search.108-100-point-page-quality-score -->

Use this as an internal QA framework, not as a search-engine ranking formula.

## Technical SEO — 20 points

- Crawlable: 3
- Indexable: 3
- Correct canonical: 2
- Successful HTTP status: 2
- Mobile usable: 2
- Core Web Vitals / performance: 3
- Internal links: 2
- Sitemap inclusion when appropriate: 1
- Structured data valid when applicable: 2

## Content Quality — 25 points

- Satisfies primary intent: 5
- Accurate: 5
- Complete: 4
- Original information gain: 4
- Clear and readable: 3
- Updated appropriately: 2
- No filler or manipulation: 2

## Authority / Trust — 15 points

- Claims supported: 4
- High-quality sources: 3
- Author or organization identity: 2
- Transparent methodology: 2
- Disclosures where relevant: 2
- Corrections / accountability: 2

## AEO — 15 points

- Direct primary answer: 4
- Self-contained answer sections: 3
- Strong question / heading structure: 2
- Appropriate lists / tables / steps: 2
- Definitions explicit: 2
- Numeric answers reproducible: 2

## GEO — 20 points

- Entities explicit: 3
- Claims independently understandable: 3
- Citation-ready facts: 4
- Provenance clear: 3
- Passage-level clarity: 2
- Current dates / versions: 2
- AI-search crawl access intentionally configured: 2
- Content easily available as text: 1

## UX / Accessibility — 5 points

- Accessible semantic structure: 2
- Main content easy to find: 1
- No disruptive UX: 1
- Useful navigation: 1

---

# 109. Quality Thresholds
<!-- id: search.109-quality-thresholds -->

Internal recommendation:

- 90–100 = Excellent / publication-ready
- 80–89 = Strong / publish with minor improvements
- 70–79 = Acceptable but needs improvement
- 60–69 = Weak
- Below 60 = Do not publish as an important indexable page

Critical failures override the numeric score.

---

# 110. Critical Publication Failures
<!-- id: search.110-critical-publication-failures -->

Do not publish an important indexable page if any of these are true:

- primary content is factually unreliable
- page is accidentally noindexed
- page is blocked from intended crawlers
- canonical points to the wrong page
- page returns an inappropriate error status
- page has no clear purpose
- important claims are fabricated
- structured data is deceptive
- content is copied without meaningful value
- page exists primarily to manipulate search systems
- unsafe high-stakes guidance is unreviewed
- page materially misrepresents the organization, author, product, or source

---

# 111. Minimum Publish Checklist
<!-- id: search.111-minimum-publish-checklist -->

Before publishing, confirm:

- [ ] Clear primary intent
- [ ] One primary topic
- [ ] Unique title
- [ ] Clear H1
- [ ] Direct opening answer where appropriate
- [ ] Useful section structure
- [ ] Accurate facts
- [ ] Sources verified
- [ ] Entities explicitly named
- [ ] Dates and versions included where relevant
- [ ] Original value present
- [ ] No unnecessary filler
- [ ] Relevant internal links
- [ ] Useful external citations
- [ ] Canonical correct
- [ ] Indexing directive correct
- [ ] robots.txt access intentional
- [ ] Sitemap status correct
- [ ] Structured data accurate
- [ ] Images optimized
- [ ] Mobile experience tested
- [ ] Accessibility checked
- [ ] Performance checked
- [ ] No deceptive SEO/GEO/AEO tactics
- [ ] Conversion or next action is clear when relevant

---

# 112. Enhanced GEO Checklist
<!-- id: search.112-enhanced-geo-checklist -->

For important reference-quality pages:

- [ ] The main entity is named in the first section
- [ ] Important facts can stand alone when quoted
- [ ] Statistics include dates and sources
- [ ] Research includes methodology
- [ ] Claims distinguish fact from opinion
- [ ] Important statements avoid ambiguous pronouns
- [ ] Each major section has a descriptive heading
- [ ] Page is focused on one primary topic
- [ ] Original evidence or meaningful information gain is present
- [ ] Source links are close to claims
- [ ] Page has a stable canonical URL
- [ ] Page is accessible to intended AI-search crawlers
- [ ] No dependence on non-standard AI markup
- [ ] Structured data matches visible content
- [ ] Organization / author identity is verifiable
- [ ] Last-reviewed or updated date is meaningful
- [ ] Important content is available as text

---

# 113. Enhanced AEO Checklist
<!-- id: search.113-enhanced-aeo-checklist -->

For answer-focused pages:

- [ ] Primary question is explicit
- [ ] Primary answer appears quickly
- [ ] Answer can be understood independently
- [ ] Definitions are concise and accurate
- [ ] Steps use ordered lists
- [ ] Comparisons use tables when useful
- [ ] Units and assumptions are stated
- [ ] Important exceptions are included
- [ ] Question headings use natural user language
- [ ] Supporting context follows the direct answer
- [ ] No unnecessary introductory filler
- [ ] Related questions are genuinely useful
- [ ] Answers are readable aloud
- [ ] Citations support material factual claims

---

# 114. Enhanced SEO Checklist
<!-- id: search.114-enhanced-seo-checklist -->

For important organic-search pages:

- [ ] Search intent validated
- [ ] Title aligned with intent
- [ ] H1 aligned with title
- [ ] URL descriptive
- [ ] Canonical self-references where appropriate
- [ ] Page indexable
- [ ] Page crawlable
- [ ] Internal links exist
- [ ] Sitemap includes page when appropriate
- [ ] Meta description useful
- [ ] Headings logical
- [ ] Content unique
- [ ] Search-relevant terminology natural
- [ ] Images optimized
- [ ] Structured data valid when applicable
- [ ] Mobile rendering works
- [ ] Core Web Vitals monitored
- [ ] No spam-policy violations

---

# 115. Recommended Page Blueprint
<!-- id: search.115-recommended-page-blueprint -->

```md
# Clear Primary Topic / Question

Direct answer in 1–3 sentences.

Short context or qualification.

## Key Takeaways

- Important point
- Important point
- Important point

## What Is [Topic]?

Clear definition.

## How [Topic] Works

Explanation.

## Requirements / Criteria

Specific requirements.

## Examples

Concrete examples.

## Common Mistakes

Practical failure modes.

## Frequently Asked Questions

### Question?

Direct answer.

## Sources

Primary and authoritative references.
```

---

# 116. Final Standard
<!-- id: search.116-final-standard -->

The strongest SEO/GEO/AEO content is:

- technically accessible
- intent-aligned
- accurate
- original
- structured
- entity-clear
- answer-ready
- citation-ready
- source-transparent
- updated
- accessible
- useful to humans first

SEO helps content become discoverable.

AEO helps content become directly answerable.

GEO helps content become understandable, verifiable, and usable by generative systems.

All three should operate as one quality system rather than separate optimization tricks.

# Control Plane Hooks
<!-- id: seo-geo-aeo.control-plane-hooks -->

When this module is active, use `CONTROL_INDEX.md` to retrieve only the capability sections relevant to the current decision. Applicable capabilities include:

- **Search-intent mapping** — `controls/20-seo-geo-aeo-and-discoverability.md` (BQ-0761–BQ-0765)
- **Entity-consistency standard** — `controls/20-seo-geo-aeo-and-discoverability.md` (BQ-0766–BQ-0770)
- **Structured-data eligibility** — `controls/20-seo-geo-aeo-and-discoverability.md` (BQ-0771–BQ-0775)
- **Answerability design** — `controls/20-seo-geo-aeo-and-discoverability.md` (BQ-0776–BQ-0780)
- **Local-discovery guard** — `controls/20-seo-geo-aeo-and-discoverability.md` (BQ-0781–BQ-0785)
- **Metadata uniqueness** — `controls/20-seo-geo-aeo-and-discoverability.md` (BQ-0786–BQ-0790)
- **Internal-link intent** — `controls/20-seo-geo-aeo-and-discoverability.md` (BQ-0791–BQ-0795)
- **Discoverability QA** — `controls/20-seo-geo-aeo-and-discoverability.md` (BQ-0796–BQ-0800)

These hooks are routing pointers, not permission to preload the listed shards. Evidence Gates control pass/fail claims.
