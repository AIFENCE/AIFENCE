<!--
Pack-Version: 4.0.0
Schema-Version: 3
Module: PROFILE_MATRIX
Module-Version: 2
Last-Updated: 2026-08-09
-->

# Semantic Profile Matrix
<!-- id: profile-matrix.root -->

Purpose: canonical semantic classification for every industry. This file separates operating behavior from digital-product behavior, visual/domain behavior, halo strategy, and risk triggers so one classification cannot contaminate every module.

# Resolution Contract
<!-- id: profile-matrix.resolution-contract -->

- `INDUSTRIES.md` is authoritative for canonical industry identity and subindustry taxonomy.
- `PROFILE_MATRIX.md` is authoritative for semantic profile defaults.
- `MANIFEST.md` is authoritative for stable addresses and operations-shard locations.
- Never infer that the Operating, Product, Design, Halo, and Risk profiles must be identical.
- Vertical technology categories may use `Software` as the Operating Profile while retaining their domain-specific Design/Halo profile and risk overlays.
- Canonical risk overlays are **base defaults only**; they MUST NOT be broadened merely because an edge-case subindustry exists under the parent taxonomy.
- When a subindustry is selected, evaluate that exact subindustry plus actual project behavior, users, data, transactions, jurisdiction, and safety context and add any triggered overlays before loading legal/security standards.
- If a user's business model clearly differs from the canonical industry default, preserve the canonical industry identity and override only the affected profile dimension for that project.
- Industries listed in the Mixed-Model Registry require subindustry/business-model resolution before implementation-oriented retrieval.

# Duplicate Subindustry / Business-Model Resolution
<!-- id: profile-matrix.duplicate-subindustry-resolution -->

When the same child label appears under multiple canonical industries, the parent selection MUST be semantic rather than positional.

- Do not select a parent because it appears first in `INDUSTRIES.md`.
- Prefer the most domain-specific canonical identity that directly describes the offering.
- Use the actual customer model and operating model to override individual profile dimensions instead of forcing a broad parent identity.
- Local consumer-service businesses may use Home Services-oriented Product/Design/Halo profiles even when their canonical domain identity is more specific.
- B2B, industrial, municipal, architectural, facilities, or construction contexts may justify different profile overrides for the same service word.
- Preserve risk overlays from the real work performed; a friendlier consumer-facing design profile does not remove physical-safety requirements.

Example: a residential landscaping company should normally preserve `industry.landscaping-and-horticulture` as canonical identity, while a local-service business model may override Product/Design/Halo toward Professional Services / Home Services where appropriate. A landscaping scope embedded in a general contractor, facilities operator, or landscape architecture practice may resolve differently based on project facts.

# Profile Dimensions
<!-- id: profile-matrix.dimensions -->

- **Operating Profile** — role/SOP model and day-to-day organizational behavior.
- **Product Profile** — default digital capability pattern used by `FEATURES.md`.
- **Design Profile** — domain visual/interaction language used by `DESIGN.md`.
- **Halo Profile** — authority, proof, reputation, and expansion strategy used by `HALO.md`.
- **Risk Overlays** — additive triggers for legal, security, safety, privacy, trust, and compliance retrieval.

# Risk Overlay Registry
<!-- id: profile-matrix.risk-overlays -->

| Overlay | Meaning / default retrieval |
|---|---|
| `standard` | Baseline legal/security/accessibility review only; load additional standards when project behavior triggers them. |
| `health-sensitive` | Health/sensitive-data, consent, privacy, access, retention, and clinical-scope review. Key IDs: `legal.50-sensitive-data-standard`, `legal.52-health-data-standard`, `legal.53-hipaa-baa-standard`, `legal.95-consumer-health-data-notice-standard`. |
| `financial-regulated` | Financial-data, payment/transaction, fraud, disclosure, authorization, and regulatory review. Key ID: `legal.96-financial-data-standard` plus applicable payment/subscription/security standards. |
| `legal-regulated` | Qualified legal-review and jurisdiction/scope controls. Key ID: `legal.6-legal-review-trigger-standard`. |
| `education-or-minors` | Education-data, minor/guardian, age, consent, and learner privacy review. Key IDs: `legal.54-childrens-privacy-standard`, `legal.55-age-assurance-standard`, `legal.97-education-data-standard`. |
| `security-identity` | Identity, biometric, authentication, privacy, account-recovery, abuse, and evidence controls. Key IDs include `security.15-identity-standard`, `security.16-authentication-standard`, `legal.51-biometric-data-standard`, `legal.64-identity-verification-standard`. |
| `public-sector` | Government-request, records, accessibility, official-source, procurement, and public-sector security review. Key ID: `legal.100-government-request-standard`. |
| `critical-infrastructure` | High-availability, resilience, incident, recovery, access, and change-control review. Use applicable incident-response, backup/recovery, network, and production-access standards in `SECURITY.md`. |
| `physical-safety` | Safety-critical workflow, EHS, qualified-personnel, inspection, maintenance, warning, and stop-work controls. Load relevant SOPs and legal review triggers. |
| `platform-trust-safety` | User-content/participant integrity, moderation, reporting, fraud/abuse, marketplace, and dispute controls. Key IDs: `legal.24-user-content-standard`, `legal.92-marketplace-standard`, `security.63-abuse-prevention-standard`. |
| `age-restricted` | Age/eligibility, marketing, content/access, and jurisdiction controls. Key IDs: `legal.18-eligibility-standard`, `legal.55-age-assurance-standard`. |
| `automated-decisioning` | AI/automated-decision transparency, evaluation, human oversight, privacy, safety, and policy review. Key IDs: `legal.71-automated-decision-making-standard`, `legal.72-ai-feature-disclosure-standard`. |
| `location-data` | Location-data minimization, consent/notice, retention, sharing, and security review. Key ID: `legal.98-location-data-standard`. |

# Dynamic Risk Resolution
<!-- id: profile-matrix.dynamic-risk-resolution -->

1. Start with the canonical base overlays in the industry row.
2. Inspect the exact selected subindustry and project facts.
3. Add overlays triggered by actual behavior or data: health/clinical/sensitive data → `health-sensitive`; money, credit, insurance, investments, payments, KYC/AML or regulated transactions → `financial-regulated`; legal representation/advice → `legal-regulated`; children/students/education records → `education-or-minors`; identity, biometrics, authentication, surveillance or security evidence → `security-identity`; government/public administration → `public-sector`; safety-critical infrastructure or high-consequence availability → `critical-infrastructure`; physical work, machinery, vehicles, field hazards or EHS workflows → `physical-safety`; user-generated content, multi-party platforms, moderation or disputes → `platform-trust-safety`; restricted-age goods/services → `age-restricted`; AI or automated decisions → `automated-decisioning`; precise location, routing, tracking or movement history → `location-data`.
4. Load only the legal/security/SOP standards required by the resulting overlay set and the creation type.
5. Never remove an applicable project-triggered overlay merely because the canonical parent row lacks it.

# Mixed-Model Registry
<!-- id: profile-matrix.mixed-model-registry -->

These canonical categories intentionally span materially different subindustry/business models. Their matrix row is an orientation default, not permission to skip subindustry resolution.

| Industry | Industry ID | Why exact subindustry/business model matters |
|---|---|---|
| Aerospace & Aviation | `industry.aerospace-and-aviation` | Manufacturing, airline/airport service, charter, maintenance, and drone models coexist. |
| Space Industry | `industry.space-industry` | Manufacturing, communications, launch/service, observation, infrastructure, and tourism models coexist. |
| Defense & Military | `industry.defense-and-military` | Manufacturing, cyber, logistics, intelligence, electronics, and contracting models coexist. |
| Beauty & Personal Care | `industry.beauty-and-personal-care` | Appointment-based services and consumer-product commerce coexist. |
| Fitness & Wellness | `industry.fitness-and-wellness` | Facilities, coaching/services, memberships, and wellness programs coexist. |
| Repair & Maintenance | `industry.repair-and-maintenance` | Automotive, electronics, appliance, industrial, aviation, marine, and building-service models coexist. |
| Landscaping & Horticulture | `industry.landscaping-and-horticulture` | Residential/local services, commercial grounds maintenance, horticultural production, irrigation, tree care, and design-oriented service models coexist. |
| Security | `industry.security` | Physical security services/systems and cybersecurity coexist. |
| Personal Services | `industry.personal-services` | Local services, concierge, creative services, coaching, and matching platforms coexist. |
| Blockchain & Digital Assets | `industry.blockchain-and-digital-assets` | Financial services, infrastructure, analytics, custody, exchanges, and software development coexist. |
| Subscription Services | `industry.subscription-services` | Software, boxes/products, media, and membership subscriptions coexist. |
| Smart Home & IoT | `industry.smart-home-and-iot` | Consumer devices, industrial IoT, mobility, buildings, cities, and software platforms coexist. |
| Mobility | `industry.mobility` | Fleet/vehicle operations, shared mobility, ridesharing, autonomous vehicles, and platforms coexist. |
| Climate & Sustainability | `industry.climate-and-sustainability` | Consulting, software, finance, carbon markets/removal, and climate technology coexist. |
| Rental & Leasing | `industry.rental-and-leasing` | Equipment, vehicle, property, furniture, and electronics rental/leasing models coexist. |
| Consumer Health | `industry.consumer-health` | Consumer products, OTC health, nutrition, and personal health devices coexist. |
| Sleep Industry | `industry.sleep-industry` | Commerce products, sleep technology, and clinical services coexist. |
| Water Industry | `industry.water-industry` | Utilities, treatment, infrastructure, equipment, services, and technology models coexist. |
| Clean Technology | `industry.clean-technology` | Energy, materials, building, recycling, water, and climate-technology models coexist. |

# Industry Matrix
<!-- id: profile-matrix.industries -->

| Industry | Industry ID | Operating Profile | Product Profile | Design Profile | Halo Profile | Risk Overlays |
|---|---|---|---|---|---|---|
| Agriculture & Farming | `industry.agriculture-and-farming` | Agriculture | Operational B2B | Agriculture | Agriculture | `physical-safety` |
| Forestry & Logging | `industry.forestry-and-logging` | Agriculture | Operational B2B | Agriculture | Agriculture | `physical-safety` |
| Fishing & Hunting | `industry.fishing-and-hunting` | Agriculture | Operational B2B | Agriculture | Agriculture | `physical-safety` |
| Mining & Natural Resources | `industry.mining-and-natural-resources` | Manufacturing | Operational B2B | Industrial | Industrial | `physical-safety` |
| Oil, Gas & Petroleum | `industry.oil-gas-and-petroleum` | Energy | Operational B2B | Energy | Energy | `critical-infrastructure`, `physical-safety` |
| Utilities | `industry.utilities` | Energy | Operational B2B | Energy | Energy | `critical-infrastructure`, `physical-safety` |
| Renewable Energy | `industry.renewable-energy` | Energy | Operational B2B | Energy | Energy | `critical-infrastructure`, `physical-safety` |
| Construction | `industry.construction` | Construction | Operational B2B | Industrial | Industrial | `physical-safety` |
| Manufacturing | `industry.manufacturing` | Manufacturing | Operational B2B | Industrial | Industrial | `physical-safety` |
| Automotive | `industry.automotive` | Automotive | Operational B2B | Automotive | Automotive | `physical-safety` |
| Aerospace & Aviation | `industry.aerospace-and-aviation` | Manufacturing | Operational B2B | Industrial | Industrial | `physical-safety` |
| Space Industry | `industry.space-industry` | Manufacturing | Operational B2B | Industrial | Industrial | `physical-safety` |
| Defense & Military | `industry.defense-and-military` | Manufacturing | Operational B2B | Industrial | Industrial | `critical-infrastructure`, `physical-safety` |
| Transportation & Logistics | `industry.transportation-and-logistics` | Logistics | Operational B2B | Logistics | Logistics | `physical-safety`, `location-data` |
| Public Transportation | `industry.public-transportation` | Logistics | Operational B2B | Logistics | Logistics | `physical-safety`, `location-data` |
| Marine & Maritime | `industry.marine-and-maritime` | Logistics | Operational B2B | Logistics | Logistics | `physical-safety` |
| Wholesale Trade | `industry.wholesale-trade` | Logistics | Operational B2B | Logistics | Logistics | `physical-safety` |
| Retail | `industry.retail` | Retail | Commerce | Commerce | Commerce | `standard` |
| E-Commerce | `industry.e-commerce` | Retail | Commerce | Commerce | Commerce | `standard` |
| Consumer Products | `industry.consumer-products` | Retail | Commerce | Commerce | Commerce | `standard` |
| Fashion & Apparel | `industry.fashion-and-apparel` | Retail | Commerce | Commerce | Commerce | `standard` |
| Food & Beverage | `industry.food-and-beverage` | Manufacturing | Operational B2B | Industrial | Industrial | `physical-safety` |
| Restaurants & Food Service | `industry.restaurants-and-food-service` | Restaurant | Restaurant Experience | Restaurant | Restaurant | `physical-safety` |
| Hospitality | `industry.hospitality` | Hospitality | Booking & Guest | Hospitality | Hospitality | `standard` |
| Travel & Tourism | `industry.travel-and-tourism` | Hospitality | Booking & Guest | Travel | Travel | `location-data` |
| Real Estate | `industry.real-estate` | Realestate | Real Estate Experience | Realestate | Realestate | `standard` |
| Financial Services | `industry.financial-services` | Finance | Financial Experience | Finance | Finance | `financial-regulated` |
| Fintech | `industry.fintech` | Finance | Financial Experience | Finance | Finance | `financial-regulated` |
| Insurance | `industry.insurance` | Finance | Financial Experience | Finance | Finance | `financial-regulated` |
| Accounting & Tax | `industry.accounting-and-tax` | Professional | Professional Services | Professional | Professional | `standard` |
| Legal Services | `industry.legal-services` | Legal | Professional Services | Legal | Legal | `legal-regulated` |
| Consulting | `industry.consulting` | Professional | Professional Services | Professional | Professional | `standard` |
| Business Services | `industry.business-services` | Professional | Professional Services | Professional | Professional | `standard` |
| Human Resources | `industry.human-resources` | Professional | Professional Services | Professional | Professional | `standard` |
| Marketing & Advertising | `industry.marketing-and-advertising` | Professional | Professional Services | Professional | Professional | `standard` |
| Sales Services | `industry.sales-services` | Professional | Professional Services | Professional | Professional | `standard` |
| Information Technology | `industry.information-technology` | Software | Software Product | Software | Software | `standard` |
| Software | `industry.software` | Software | Software Product | Software | Software | `standard` |
| Artificial Intelligence | `industry.artificial-intelligence` | Ai | Software Product | Ai | Ai | `automated-decisioning` |
| Data & Analytics | `industry.data-and-analytics` | Software | Software Product | Software | Software | `standard` |
| Cloud Computing | `industry.cloud-computing` | Software | Software Product | Software | Software | `standard` |
| Cybersecurity | `industry.cybersecurity` | Cyber | Software Product | Security | Security | `security-identity` |
| Internet Services | `industry.internet-services` | Software | Software Product | Software | Software | `standard` |
| Telecommunications | `industry.telecommunications` | Telecom | Operational B2B | Telecom | Telecom | `critical-infrastructure`, `physical-safety` |
| Semiconductors | `industry.semiconductors` | Manufacturing | Operational B2B | Industrial | Industrial | `physical-safety` |
| Electronics | `industry.electronics` | Manufacturing | Operational B2B | Industrial | Industrial | `physical-safety` |
| Robotics & Automation | `industry.robotics-and-automation` | Manufacturing | Operational B2B | Industrial | Industrial | `physical-safety` |
| Media | `industry.media` | Media | Content & Media | Media | Media | `standard` |
| Entertainment | `industry.entertainment` | Media | Content & Media | Media | Media | `standard` |
| Gaming | `industry.gaming` | Media | Content & Media | Gaming | Gaming | `platform-trust-safety` |
| Publishing | `industry.publishing` | Media | Content & Media | Media | Media | `standard` |
| Sports | `industry.sports` | Sports | Sports & Membership | Sports | Sports | `physical-safety` |
| Events | `industry.events` | Events | Event Experience | Events | Events | `standard` |
| Education | `industry.education` | Education | Learning Experience | Education | Education | `education-or-minors` |
| EdTech | `industry.edtech` | Software | Software Product | Education | Education | `education-or-minors` |
| Healthcare | `industry.healthcare` | Health | Healthcare Experience | Healthcare | Healthcare | `health-sensitive` |
| HealthTech | `industry.healthtech` | Software | Software Product | Healthcare | Healthcare | `health-sensitive` |
| Pharmaceuticals | `industry.pharmaceuticals` | Manufacturing | Operational B2B | Healthcare | Healthcare | `health-sensitive`, `physical-safety` |
| Biotechnology | `industry.biotechnology` | Science | Scientific & Technical | Science | Science | `standard` |
| Medical Devices | `industry.medical-devices` | Manufacturing | Operational B2B | Healthcare | Healthcare | `health-sensitive`, `physical-safety` |
| Life Sciences | `industry.life-sciences` | Science | Scientific & Technical | Science | Science | `standard` |
| Veterinary & Animal Care | `industry.veterinary-and-animal-care` | Health | Healthcare Experience | Healthcare | Healthcare | `health-sensitive` |
| Beauty & Personal Care | `industry.beauty-and-personal-care` | Retail | Commerce | Commerce | Commerce | `standard` |
| Fitness & Wellness | `industry.fitness-and-wellness` | Sports | Sports & Membership | Sports | Sports | `physical-safety` |
| Home Services | `industry.home-services` | Home Services | Professional Services | Home Services | Home Services | `physical-safety` |
| Repair & Maintenance | `industry.repair-and-maintenance` | Home Services | Professional Services | Home Services | Home Services | `physical-safety` |
| Security | `industry.security` | Professional | Professional Services | Security | Security | `security-identity`, `physical-safety` |
| Environmental Services | `industry.environmental-services` | Professional | Professional Services | Professional | Professional | `standard` |
| Waste Management | `industry.waste-management` | Logistics | Operational B2B | Logistics | Logistics | `physical-safety` |
| Clean Technology | `industry.clean-technology` | Energy | Operational B2B | Energy | Energy | `critical-infrastructure`, `physical-safety` |
| Water Industry | `industry.water-industry` | Energy | Operational B2B | Energy | Energy | `critical-infrastructure`, `physical-safety` |
| Chemicals | `industry.chemicals` | Manufacturing | Operational B2B | Industrial | Industrial | `physical-safety` |
| Materials | `industry.materials` | Manufacturing | Operational B2B | Industrial | Industrial | `physical-safety` |
| Packaging | `industry.packaging` | Manufacturing | Operational B2B | Industrial | Industrial | `physical-safety` |
| Architecture & Design | `industry.architecture-and-design` | Professional | Professional Services | Professional | Professional | `standard` |
| Engineering | `industry.engineering` | Professional | Professional Services | Professional | Professional | `standard` |
| Professional Services | `industry.professional-services` | Professional | Professional Services | Professional | Professional | `standard` |
| Research & Development | `industry.research-and-development` | Science | Scientific & Technical | Science | Science | `standard` |
| Government & Public Sector | `industry.government-and-public-sector` | Government | Public Service | Government | Government | `public-sector` |
| Nonprofits & NGOs | `industry.nonprofits-and-ngos` | Nonprofit | Nonprofit & Community | Nonprofit | Nonprofit | `standard` |
| Religious Organizations | `industry.religious-organizations` | Nonprofit | Nonprofit & Community | Nonprofit | Nonprofit | `standard` |
| Social Services | `industry.social-services` | Nonprofit | Nonprofit & Community | Nonprofit | Nonprofit | `standard` |
| Childcare | `industry.childcare` | Education | Learning Experience | Education | Education | `education-or-minors` |
| Funeral & Death Care | `industry.funeral-and-death-care` | Professional | Professional Services | Professional | Professional | `standard` |
| Personal Services | `industry.personal-services` | Professional | Professional Services | Professional | Professional | `standard` |
| Printing & Promotional Products | `industry.printing-and-promotional-products` | Manufacturing | Operational B2B | Commerce | Commerce | `physical-safety` |
| Photography & Creative Services | `industry.photography-and-creative-services` | Art | Content & Media | Art | Art | `standard` |
| Translation & Language Services | `industry.translation-and-language-services` | Professional | Professional Services | Professional | Professional | `standard` |
| Recruitment & Staffing | `industry.recruitment-and-staffing` | Professional | Professional Services | Professional | Professional | `standard` |
| Franchising | `industry.franchising` | Professional | Professional Services | Professional | Professional | `standard` |
| Licensing | `industry.licensing` | Legal | Professional Services | Legal | Legal | `legal-regulated` |
| Blockchain & Digital Assets | `industry.blockchain-and-digital-assets` | Finance | Financial Experience | Finance | Finance | `financial-regulated` |
| Creator Economy | `industry.creator-economy` | Media | Content & Media | Media | Media | `platform-trust-safety` |
| Social Media | `industry.social-media` | Media | Content & Media | Media | Media | `platform-trust-safety` |
| Marketplaces | `industry.marketplaces` | Marketplace | Marketplace Platform | Marketplace | Marketplace | `platform-trust-safety` |
| Subscription Services | `industry.subscription-services` | Software | Software Product | Software | Software | `standard` |
| Sharing Economy | `industry.sharing-economy` | Marketplace | Marketplace Platform | Marketplace | Marketplace | `platform-trust-safety` |
| Smart Home & IoT | `industry.smart-home-and-iot` | Manufacturing | Software Product | Software | Software | `physical-safety` |
| Mobility | `industry.mobility` | Automotive | Marketplace Platform | Automotive | Automotive | `physical-safety`, `location-data` |
| Electric Vehicles | `industry.electric-vehicles` | Automotive | Operational B2B | Automotive | Automotive | `physical-safety` |
| Battery Industry | `industry.battery-industry` | Manufacturing | Operational B2B | Industrial | Industrial | `physical-safety` |
| Climate & Sustainability | `industry.climate-and-sustainability` | Professional | Professional Services | Professional | Professional | `standard` |
| Agricultural Technology | `industry.agricultural-technology` | Software | Software Product | Agriculture | Agriculture | `standard` |
| Food Technology | `industry.food-technology` | Manufacturing | Operational B2B | Industrial | Industrial | `physical-safety` |
| PropTech | `industry.proptech` | Software | Software Product | Realestate | Realestate | `standard` |
| Construction Technology | `industry.construction-technology` | Software | Software Product | Industrial | Industrial | `standard` |
| LegalTech | `industry.legaltech` | Software | Software Product | Legal | Legal | `legal-regulated` |
| RegTech | `industry.regtech` | Software | Software Product | Software | Software | `standard` |
| Retail Technology | `industry.retail-technology` | Software | Software Product | Commerce | Commerce | `standard` |
| Restaurant Technology | `industry.restaurant-technology` | Software | Software Product | Restaurant | Restaurant | `standard` |
| Travel Technology | `industry.travel-technology` | Software | Software Product | Travel | Travel | `location-data` |
| Advertising Technology | `industry.advertising-technology` | Software | Software Product | Software | Software | `standard` |
| Sales Technology | `industry.sales-technology` | Software | Software Product | Software | Software | `standard` |
| HR Technology | `industry.hr-technology` | Software | Software Product | Software | Software | `standard` |
| Supply Chain Technology | `industry.supply-chain-technology` | Software | Software Product | Logistics | Logistics | `standard` |
| Industrial Technology | `industry.industrial-technology` | Software | Software Product | Industrial | Industrial | `standard` |
| Quantum Technology | `industry.quantum-technology` | Science | Scientific & Technical | Science | Science | `standard` |
| AR/VR/XR | `industry.ar-vr-xr` | Software | Software Product | Software | Software | `standard` |
| 3D Printing | `industry.3d-printing` | Manufacturing | Operational B2B | Industrial | Industrial | `physical-safety` |
| Nanotechnology | `industry.nanotechnology` | Science | Scientific & Technical | Science | Science | `standard` |
| Nuclear Energy | `industry.nuclear-energy` | Energy | Operational B2B | Energy | Energy | `critical-infrastructure`, `physical-safety` |
| Cannabis Industry | `industry.cannabis-industry` | Retail | Commerce | Commerce | Commerce | `age-restricted` |
| Luxury Goods | `industry.luxury-goods` | Luxury | Luxury & Concierge | Luxury | Luxury | `standard` |
| Art & Culture | `industry.art-and-culture` | Art | Content & Media | Art | Art | `standard` |
| Education & Training Services | `industry.education-and-training-services` | Education | Learning Experience | Education | Education | `education-or-minors` |
| Import & Export | `industry.import-and-export` | Logistics | Operational B2B | Logistics | Logistics | `physical-safety` |
| Distribution | `industry.distribution` | Logistics | Operational B2B | Logistics | Logistics | `physical-safety` |
| Storage | `industry.storage` | Logistics | Operational B2B | Logistics | Logistics | `physical-safety` |
| Marine Resources | `industry.marine-resources` | Science | Scientific & Technical | Science | Science | `standard` |
| Geospatial | `industry.geospatial` | Science | Scientific & Technical | Science | Science | `location-data` |
| Testing, Inspection & Certification | `industry.testing-inspection-and-certification` | Science | Scientific & Technical | Science | Science | `standard` |
| Standards & Compliance | `industry.standards-and-compliance` | Professional | Professional Services | Professional | Professional | `standard` |
| Auction Industry | `industry.auction-industry` | Marketplace | Marketplace Platform | Marketplace | Marketplace | `platform-trust-safety` |
| Rental & Leasing | `industry.rental-and-leasing` | Professional | Professional Services | Professional | Professional | `standard` |
| Vending & Automated Retail | `industry.vending-and-automated-retail` | Retail | Commerce | Commerce | Commerce | `standard` |
| Office Services | `industry.office-services` | Professional | Professional Services | Professional | Professional | `standard` |
| Facility Services | `industry.facility-services` | Home Services | Professional Services | Home Services | Home Services | `physical-safety` |
| Uniform & Textile Services | `industry.uniform-and-textile-services` | Professional | Professional Services | Industrial | Industrial | `standard` |
| Pet Industry | `industry.pet-industry` | Retail | Commerce | Commerce | Commerce | `standard` |
| Wedding Industry | `industry.wedding-industry` | Events | Event Experience | Events | Events | `standard` |
| Baby & Parenting | `industry.baby-and-parenting` | Retail | Commerce | Commerce | Commerce | `standard` |
| Senior Economy | `industry.senior-economy` | Health | Healthcare Experience | Healthcare | Healthcare | `health-sensitive` |
| Accessibility Industry | `industry.accessibility-industry` | Professional | Professional Services | Professional | Professional | `standard` |
| Identity & Verification | `industry.identity-and-verification` | Cyber | Software Product | Security | Security | `security-identity` |
| Payments | `industry.payments` | Finance | Financial Experience | Finance | Finance | `financial-regulated` |
| Loyalty & Rewards | `industry.loyalty-and-rewards` | Software | Software Product | Software | Software | `standard` |
| Customer Experience | `industry.customer-experience` | Professional | Professional Services | Professional | Professional | `standard` |
| Knowledge Management | `industry.knowledge-management` | Software | Software Product | Software | Software | `standard` |
| Communications | `industry.communications` | Telecom | Operational B2B | Telecom | Telecom | `critical-infrastructure`, `physical-safety` |
| Postal & Courier | `industry.postal-and-courier` | Logistics | Operational B2B | Logistics | Logistics | `physical-safety` |
| Parking | `industry.parking` | Logistics | Operational B2B | Logistics | Logistics | `physical-safety` |
| Traffic & Road Services | `industry.traffic-and-road-services` | Logistics | Operational B2B | Logistics | Logistics | `physical-safety` |
| Rail | `industry.rail` | Logistics | Operational B2B | Logistics | Logistics | `physical-safety` |
| Cruise Industry | `industry.cruise-industry` | Hospitality | Booking & Guest | Travel | Travel | `standard` |
| Theme Parks & Attractions | `industry.theme-parks-and-attractions` | Hospitality | Booking & Guest | Hospitality | Hospitality | `standard` |
| Recreation | `industry.recreation` | Sports | Sports & Membership | Sports | Sports | `physical-safety` |
| Gambling & Gaming | `industry.gambling-and-gaming` | Hospitality | Booking & Guest | Gaming | Gaming | `platform-trust-safety`, `age-restricted` |
| Adult & Nightlife Entertainment | `industry.adult-and-nightlife-entertainment` | Hospitality | Booking & Guest | Media | Media | `age-restricted` |
| Political & Campaign Services | `industry.political-and-campaign-services` | Professional | Professional Services | Professional | Professional | `standard` |
| Public Relations & Communications | `industry.public-relations-and-communications` | Professional | Professional Services | Telecom | Telecom | `critical-infrastructure` |
| Investor Relations | `industry.investor-relations` | Professional | Professional Services | Professional | Professional | `standard` |
| Intellectual Property | `industry.intellectual-property` | Legal | Professional Services | Realestate | Realestate | `standard` |
| Franchise Services | `industry.franchise-services` | Professional | Professional Services | Professional | Professional | `standard` |
| Entrepreneurship & Startup Services | `industry.entrepreneurship-and-startup-services` | Professional | Professional Services | Professional | Professional | `standard` |
| Coworking & Flexible Offices | `industry.coworking-and-flexible-offices` | Realestate | Real Estate Experience | Realestate | Realestate | `standard` |
| Corporate Governance | `industry.corporate-governance` | Professional | Professional Services | Professional | Professional | `standard` |
| Risk Management | `industry.risk-management` | Professional | Professional Services | Professional | Professional | `standard` |
| Emergency & Disaster Services | `industry.emergency-and-disaster-services` | Professional | Professional Services | Professional | Professional | `standard` |
| Fire & Safety | `industry.fire-and-safety` | Construction | Operational B2B | Industrial | Industrial | `physical-safety` |
| Cleaning & Sanitation | `industry.cleaning-and-sanitation` | Home Services | Professional Services | Home Services | Home Services | `physical-safety` |
| Pest Management | `industry.pest-management` | Home Services | Professional Services | Home Services | Home Services | `physical-safety` |
| Landscaping & Horticulture | `industry.landscaping-and-horticulture` | Agriculture | Operational B2B | Agriculture | Agriculture | `physical-safety` |
| Industrial Services | `industry.industrial-services` | Professional | Professional Services | Industrial | Industrial | `standard` |
| Energy Services | `industry.energy-services` | Energy | Operational B2B | Energy | Energy | `critical-infrastructure`, `physical-safety` |
| Commodity Trading | `industry.commodity-trading` | Finance | Financial Experience | Finance | Finance | `financial-regulated` |
| Precious Metals | `industry.precious-metals` | Luxury | Luxury & Concierge | Luxury | Luxury | `standard` |
| Jewelry & Gemstones | `industry.jewelry-and-gemstones` | Luxury | Luxury & Concierge | Luxury | Luxury | `standard` |
| Furniture | `industry.furniture` | Retail | Commerce | Commerce | Commerce | `standard` |
| Home Furnishings | `industry.home-furnishings` | Retail | Commerce | Commerce | Commerce | `standard` |
| Building Materials | `industry.building-materials` | Manufacturing | Operational B2B | Industrial | Industrial | `physical-safety` |
| Heavy Equipment | `industry.heavy-equipment` | Manufacturing | Operational B2B | Industrial | Industrial | `physical-safety` |
| Machinery | `industry.machinery` | Manufacturing | Operational B2B | Industrial | Industrial | `physical-safety` |
| Measurement & Instrumentation | `industry.measurement-and-instrumentation` | Manufacturing | Operational B2B | Industrial | Industrial | `physical-safety` |
| Optics & Photonics | `industry.optics-and-photonics` | Science | Scientific & Technical | Science | Science | `standard` |
| Printing & Imaging | `industry.printing-and-imaging` | Manufacturing | Operational B2B | Industrial | Industrial | `physical-safety` |
| Audio Industry | `industry.audio-industry` | Media | Content & Media | Media | Media | `standard` |
| Film Production | `industry.film-production` | Media | Content & Media | Media | Media | `standard` |
| Music Industry | `industry.music-industry` | Media | Content & Media | Media | Media | `standard` |
| Podcasting | `industry.podcasting` | Media | Content & Media | Media | Media | `standard` |
| Influencer & Creator Services | `industry.influencer-and-creator-services` | Media | Content & Media | Media | Media | `platform-trust-safety` |
| Books & Literature | `industry.books-and-literature` | Media | Content & Media | Media | Media | `standard` |
| Libraries & Archives | `industry.libraries-and-archives` | Education | Learning Experience | Education | Education | `education-or-minors` |
| Museums | `industry.museums` | Art | Content & Media | Art | Art | `standard` |
| Scientific Services | `industry.scientific-services` | Science | Scientific & Technical | Science | Science | `standard` |
| Meteorology & Weather Services | `industry.meteorology-and-weather-services` | Science | Scientific & Technical | Science | Science | `standard` |
| Ocean & Marine Technology | `industry.ocean-and-marine-technology` | Science | Scientific & Technical | Science | Science | `standard` |
| Defense Technology | `industry.defense-technology` | Software | Software Product | Software | Software | `critical-infrastructure` |
| GovTech | `industry.govtech` | Software | Software Product | Government | Government | `public-sector` |
| Civic & Community Technology | `industry.civic-and-community-technology` | Software | Software Product | Government | Government | `public-sector` |
| Election & Campaign Technology | `industry.election-and-campaign-technology` | Software | Software Product | Government | Government | `public-sector` |
| Religious Technology | `industry.religious-technology` | Software | Software Product | Nonprofit | Nonprofit | `standard` |
| Nonprofit Technology | `industry.nonprofit-technology` | Software | Software Product | Nonprofit | Nonprofit | `standard` |
| Fundraising | `industry.fundraising` | Nonprofit | Nonprofit & Community | Nonprofit | Nonprofit | `standard` |
| Crowdfunding | `industry.crowdfunding` | Marketplace | Marketplace Platform | Marketplace | Marketplace | `platform-trust-safety` |
| Professional Associations | `industry.professional-associations` | Nonprofit | Nonprofit & Community | Nonprofit | Nonprofit | `standard` |
| Certification & Credentialing | `industry.certification-and-credentialing` | Education | Learning Experience | Education | Education | `education-or-minors` |
| Immigration Services | `industry.immigration-services` | Legal | Professional Services | Legal | Legal | `legal-regulated` |
| Relocation Services | `industry.relocation-services` | Professional | Professional Services | Professional | Professional | `location-data` |
| Background Screening | `industry.background-screening` | Professional | Professional Services | Professional | Professional | `standard` |
| Private Investigation | `industry.private-investigation` | Professional | Professional Services | Professional | Professional | `standard` |
| Debt Collection | `industry.debt-collection` | Finance | Financial Experience | Finance | Finance | `financial-regulated` |
| Credit Services | `industry.credit-services` | Finance | Financial Experience | Finance | Finance | `financial-regulated` |
| Mortgage Services | `industry.mortgage-services` | Finance | Financial Experience | Finance | Finance | `financial-regulated` |
| Title & Escrow | `industry.title-and-escrow` | Realestate | Real Estate Experience | Realestate | Realestate | `standard` |
| Procurement | `industry.procurement` | Professional | Professional Services | Professional | Professional | `standard` |
| Auction & Resale | `industry.auction-and-resale` | Retail | Commerce | Commerce | Commerce | `standard` |
| Secondhand & Circular Economy | `industry.secondhand-and-circular-economy` | Retail | Commerce | Commerce | Commerce | `standard` |
| Pawn & Collateral Lending | `industry.pawn-and-collateral-lending` | Finance | Financial Experience | Finance | Finance | `financial-regulated` |
| Self Storage | `industry.self-storage` | Realestate | Real Estate Experience | Realestate | Realestate | `standard` |
| Commercial Laundry | `industry.commercial-laundry` | Home Services | Professional Services | Home Services | Home Services | `physical-safety` |
| Mail & Fulfillment | `industry.mail-and-fulfillment` | Logistics | Operational B2B | Logistics | Logistics | `physical-safety` |
| Packaging & Labeling Services | `industry.packaging-and-labeling-services` | Manufacturing | Operational B2B | Industrial | Industrial | `physical-safety` |
| Quality Assurance | `industry.quality-assurance` | Professional | Professional Services | Professional | Professional | `standard` |
| Software Testing | `industry.software-testing` | Software | Software Product | Software | Software | `standard` |
| IT Staffing | `industry.it-staffing` | Professional | Professional Services | Professional | Professional | `standard` |
| Managed Services | `industry.managed-services` | Software | Software Product | Software | Software | `standard` |
| Data Center Industry | `industry.data-center-industry` | Telecom | Operational B2B | Telecom | Telecom | `critical-infrastructure`, `physical-safety` |
| Domain & Hosting | `industry.domain-and-hosting` | Software | Software Product | Software | Software | `standard` |
| Search & Discovery | `industry.search-and-discovery` | Software | Software Product | Software | Software | `standard` |
| Digital Identity | `industry.digital-identity` | Cyber | Software Product | Security | Security | `security-identity` |
| Privacy Technology | `industry.privacy-technology` | Cyber | Software Product | Security | Security | `security-identity` |
| Fraud & Financial Crime | `industry.fraud-and-financial-crime` | Finance | Financial Experience | Finance | Finance | `financial-regulated`, `security-identity` |
| Geopolitical & Intelligence Services | `industry.geopolitical-and-intelligence-services` | Professional | Professional Services | Professional | Professional | `standard` |
| Corporate Intelligence | `industry.corporate-intelligence` | Professional | Professional Services | Professional | Professional | `standard` |
| Market Research | `industry.market-research` | Professional | Professional Services | Professional | Professional | `standard` |
| Economic Research | `industry.economic-research` | Professional | Professional Services | Professional | Professional | `standard` |
| Ratings & Reviews | `industry.ratings-and-reviews` | Software | Software Product | Software | Software | `standard` |
| Reputation Management | `industry.reputation-management` | Professional | Professional Services | Professional | Professional | `standard` |
| Localization | `industry.localization` | Professional | Professional Services | Professional | Professional | `standard` |
| Accessibility Services | `industry.accessibility-services` | Professional | Professional Services | Professional | Professional | `standard` |
| Transcription & Captioning | `industry.transcription-and-captioning` | Professional | Professional Services | Professional | Professional | `standard` |
| Document Services | `industry.document-services` | Professional | Professional Services | Professional | Professional | `standard` |
| Printing & Mailing | `industry.printing-and-mailing` | Professional | Professional Services | Professional | Professional | `standard` |
| Signage | `industry.signage` | Manufacturing | Operational B2B | Industrial | Industrial | `physical-safety` |
| Outdoor Advertising | `industry.outdoor-advertising` | Professional | Professional Services | Professional | Professional | `standard` |
| Affiliate Marketing | `industry.affiliate-marketing` | Professional | Professional Services | Professional | Professional | `standard` |
| Influencer Marketing | `industry.influencer-marketing` | Media | Content & Media | Media | Media | `standard` |
| Experiential Marketing | `industry.experiential-marketing` | Events | Event Experience | Events | Events | `standard` |
| Promotional Products | `industry.promotional-products` | Retail | Commerce | Commerce | Commerce | `standard` |
| Loyalty Programs | `industry.loyalty-programs` | Retail | Commerce | Commerce | Commerce | `standard` |
| Gift Cards & Prepaid | `industry.gift-cards-and-prepaid` | Retail | Commerce | Commerce | Commerce | `standard` |
| Ticketing | `industry.ticketing` | Events | Event Experience | Events | Events | `standard` |
| Reservation Platforms | `industry.reservation-platforms` | Software | Software Product | Software | Software | `standard` |
| Appointment Services | `industry.appointment-services` | Software | Software Product | Software | Software | `standard` |
| Digital Signatures | `industry.digital-signatures` | Software | Software Product | Legal | Legal | `legal-regulated` |
| Contract Management | `industry.contract-management` | Software | Software Product | Legal | Legal | `legal-regulated` |
| Workflow Automation | `industry.workflow-automation` | Software | Software Product | Software | Software | `standard` |
| Integration Software | `industry.integration-software` | Software | Software Product | Software | Software | `standard` |
| Developer Infrastructure | `industry.developer-infrastructure` | Software | Software Product | Software | Software | `standard` |
| DevOps | `industry.devops` | Software | Software Product | Software | Software | `standard` |
| Observability | `industry.observability` | Software | Software Product | Software | Software | `standard` |
| Database Industry | `industry.database-industry` | Software | Software Product | Software | Software | `standard` |
| Open Source | `industry.open-source` | Software | Software Product | Software | Software | `standard` |
| Enterprise Collaboration | `industry.enterprise-collaboration` | Software | Software Product | Software | Software | `standard` |
| Project Management | `industry.project-management` | Professional | Professional Services | Professional | Professional | `standard` |
| Product Management | `industry.product-management` | Professional | Professional Services | Professional | Professional | `standard` |
| Design Technology | `industry.design-technology` | Software | Software Product | Software | Software | `standard` |
| CAD & Engineering Software | `industry.cad-and-engineering-software` | Software | Software Product | Software | Software | `standard` |
| Digital Twins | `industry.digital-twins` | Software | Software Product | Software | Software | `standard` |
| Simulation | `industry.simulation` | Software | Software Product | Software | Software | `standard` |
| Autonomous Vehicles | `industry.autonomous-vehicles` | Automotive | Operational B2B | Automotive | Automotive | `physical-safety` |
| Navigation | `industry.navigation` | Software | Software Product | Software | Software | `location-data` |
| Fleet Technology | `industry.fleet-technology` | Software | Software Product | Automotive | Automotive | `location-data` |
| Telematics | `industry.telematics` | Software | Software Product | Automotive | Automotive | `location-data` |
| InsurTech | `industry.insurtech` | Software | Software Product | Software | Software | `standard` |
| WealthTech | `industry.wealthtech` | Software | Software Product | Finance | Finance | `financial-regulated` |
| Lending Technology | `industry.lending-technology` | Software | Software Product | Finance | Finance | `financial-regulated` |
| Personal Finance | `industry.personal-finance` | Finance | Financial Experience | Finance | Finance | `financial-regulated` |
| Tax Technology | `industry.tax-technology` | Software | Software Product | Finance | Finance | `financial-regulated` |
| Accounting Technology | `industry.accounting-technology` | Software | Software Product | Finance | Finance | `financial-regulated` |
| Expense Management | `industry.expense-management` | Software | Software Product | Finance | Finance | `financial-regulated` |
| Treasury Technology | `industry.treasury-technology` | Software | Software Product | Finance | Finance | `financial-regulated` |
| Capital Markets Technology | `industry.capital-markets-technology` | Software | Software Product | Finance | Finance | `financial-regulated` |
| Trading | `industry.trading` | Finance | Financial Experience | Finance | Finance | `financial-regulated` |
| Investment Research | `industry.investment-research` | Finance | Financial Experience | Finance | Finance | `financial-regulated` |
| Private Markets | `industry.private-markets` | Finance | Financial Experience | Finance | Finance | `financial-regulated` |
| Asset Servicing | `industry.asset-servicing` | Finance | Financial Experience | Finance | Finance | `financial-regulated` |
| Fund Administration | `industry.fund-administration` | Finance | Financial Experience | Finance | Finance | `financial-regulated` |
| Pensions & Retirement | `industry.pensions-and-retirement` | Finance | Financial Experience | Automotive | Automotive | `standard` |
| Employee Benefits | `industry.employee-benefits` | Professional | Professional Services | Professional | Professional | `standard` |
| Compensation Technology | `industry.compensation-technology` | Software | Software Product | Software | Software | `standard` |
| Equity Management | `industry.equity-management` | Finance | Financial Experience | Finance | Finance | `financial-regulated` |
| Corporate Finance | `industry.corporate-finance` | Finance | Financial Experience | Finance | Finance | `financial-regulated` |
| Mergers & Acquisitions | `industry.mergers-and-acquisitions` | Finance | Financial Experience | Finance | Finance | `financial-regulated` |
| Business Brokerage | `industry.business-brokerage` | Professional | Professional Services | Professional | Professional | `standard` |
| Valuation | `industry.valuation` | Finance | Financial Experience | Finance | Finance | `financial-regulated` |
| Restructuring | `industry.restructuring` | Finance | Financial Experience | Finance | Finance | `financial-regulated` |
| Bankruptcy Services | `industry.bankruptcy-services` | Finance | Financial Experience | Finance | Finance | `financial-regulated` |
| Compliance | `industry.compliance` | Professional | Professional Services | Professional | Professional | `standard` |
| ESG | `industry.esg` | Professional | Professional Services | Professional | Professional | `standard` |
| Carbon Markets | `industry.carbon-markets` | Finance | Financial Experience | Finance | Finance | `financial-regulated` |
| Carbon Removal | `industry.carbon-removal` | Science | Scientific & Technical | Science | Science | `standard` |
| Circular Economy | `industry.circular-economy` | Logistics | Operational B2B | Logistics | Logistics | `physical-safety` |
| Sustainable Fashion | `industry.sustainable-fashion` | Retail | Commerce | Commerce | Commerce | `standard` |
| Green Building | `industry.green-building` | Construction | Operational B2B | Industrial | Industrial | `physical-safety` |
| Smart Cities | `industry.smart-cities` | Government | Public Service | Government | Government | `public-sector` |
| Infrastructure | `industry.infrastructure` | Construction | Operational B2B | Industrial | Industrial | `physical-safety` |
| Infrastructure Investment | `industry.infrastructure-investment` | Finance | Financial Experience | Finance | Finance | `financial-regulated` |
| Project Finance | `industry.project-finance` | Finance | Financial Experience | Finance | Finance | `financial-regulated` |
| Economic Development | `industry.economic-development` | Government | Public Service | Government | Government | `public-sector` |
| International Development | `industry.international-development` | Nonprofit | Nonprofit & Community | Nonprofit | Nonprofit | `standard` |
| Humanitarian Services | `industry.humanitarian-services` | Nonprofit | Nonprofit & Community | Nonprofit | Nonprofit | `standard` |
| Microfinance | `industry.microfinance` | Finance | Financial Experience | Finance | Finance | `financial-regulated` |
| Financial Inclusion | `industry.financial-inclusion` | Finance | Financial Experience | Finance | Finance | `financial-regulated` |
| Community Banking | `industry.community-banking` | Finance | Financial Experience | Finance | Finance | `financial-regulated` |
| Faith-Based Business | `industry.faith-based-business` | Nonprofit | Nonprofit & Community | Nonprofit | Nonprofit | `standard` |
| Funeral Technology | `industry.funeral-technology` | Software | Software Product | Software | Software | `standard` |
| Digital Legacy | `industry.digital-legacy` | Software | Software Product | Software | Software | `standard` |
| Estate Planning | `industry.estate-planning` | Legal | Professional Services | Legal | Legal | `legal-regulated` |
| Trust Services | `industry.trust-services` | Legal | Professional Services | Legal | Legal | `legal-regulated` |
| Family Office Services | `industry.family-office-services` | Professional | Professional Services | Professional | Professional | `standard` |
| Concierge Services | `industry.concierge-services` | Hospitality | Booking & Guest | Hospitality | Hospitality | `standard` |
| Luxury Services | `industry.luxury-services` | Luxury | Luxury & Concierge | Luxury | Luxury | `standard` |
| Yachting | `industry.yachting` | Luxury | Luxury & Concierge | Luxury | Luxury | `standard` |
| Private Aviation | `industry.private-aviation` | Luxury | Luxury & Concierge | Luxury | Luxury | `standard` |
| Art Investment | `industry.art-investment` | Finance | Financial Experience | Luxury | Luxury | `financial-regulated` |
| Collectibles | `industry.collectibles` | Retail | Commerce | Commerce | Commerce | `standard` |
| Antiques | `industry.antiques` | Retail | Commerce | Commerce | Commerce | `standard` |
| Restoration | `industry.restoration` | Home Services | Professional Services | Home Services | Home Services | `physical-safety` |
| Crafts & Handmade Goods | `industry.crafts-and-handmade-goods` | Retail | Commerce | Art | Art | `standard` |
| Hobbies | `industry.hobbies` | Retail | Commerce | Commerce | Commerce | `standard` |
| Outdoor Industry | `industry.outdoor-industry` | Sports | Sports & Membership | Sports | Sports | `physical-safety` |
| Golf | `industry.golf` | Sports | Sports & Membership | Sports | Sports | `physical-safety` |
| Fitness Technology | `industry.fitness-technology` | Software | Software Product | Sports | Sports | `standard` |
| Wearables | `industry.wearables` | Manufacturing | Commerce | Commerce | Commerce | `physical-safety` |
| Consumer Health | `industry.consumer-health` | Health | Commerce | Healthcare | Healthcare | `health-sensitive` |
| Nutrition | `industry.nutrition` | Health | Healthcare Experience | Healthcare | Healthcare | `health-sensitive` |
| Supplements | `industry.supplements` | Manufacturing | Commerce | Healthcare | Healthcare | `health-sensitive`, `physical-safety` |
| Sleep Industry | `industry.sleep-industry` | Retail | Commerce | Commerce | Commerce | `standard` |
| Mental Wellness | `industry.mental-wellness` | Health | Healthcare Experience | Healthcare | Healthcare | `health-sensitive` |
| Behavioral Health | `industry.behavioral-health` | Health | Healthcare Experience | Healthcare | Healthcare | `health-sensitive` |
| Addiction Treatment | `industry.addiction-treatment` | Health | Healthcare Experience | Healthcare | Healthcare | `health-sensitive` |
| Dental Industry | `industry.dental-industry` | Health | Healthcare Experience | Healthcare | Healthcare | `health-sensitive` |
| Vision & Eye Care | `industry.vision-and-eye-care` | Health | Healthcare Experience | Healthcare | Healthcare | `health-sensitive` |
| Hearing Care | `industry.hearing-care` | Health | Healthcare Experience | Healthcare | Healthcare | `health-sensitive` |
| Mobility & Rehabilitation Equipment | `industry.mobility-and-rehabilitation-equipment` | Manufacturing | Operational B2B | Automotive | Automotive | `physical-safety`, `location-data` |
| Prosthetics & Orthotics | `industry.prosthetics-and-orthotics` | Manufacturing | Operational B2B | Healthcare | Healthcare | `health-sensitive`, `physical-safety` |
| Home Healthcare Equipment | `industry.home-healthcare-equipment` | Manufacturing | Operational B2B | Healthcare | Healthcare | `health-sensitive`, `physical-safety` |
| Laboratory Services | `industry.laboratory-services` | Science | Scientific & Technical | Science | Science | `standard` |
| Genetic Testing | `industry.genetic-testing` | Science | Scientific & Technical | Science | Science | `standard` |
| Fertility & Reproductive Health | `industry.fertility-and-reproductive-health` | Health | Healthcare Experience | Healthcare | Healthcare | `health-sensitive` |
| Women's Health | `industry.womens-health` | Health | Healthcare Experience | Healthcare | Healthcare | `health-sensitive` |
| Men's Health | `industry.mens-health` | Health | Healthcare Experience | Healthcare | Healthcare | `health-sensitive` |
| Pediatrics | `industry.pediatrics` | Health | Healthcare Experience | Healthcare | Healthcare | `health-sensitive` |
| Senior Healthcare | `industry.senior-healthcare` | Health | Healthcare Experience | Healthcare | Healthcare | `health-sensitive` |
| Pharmacy | `industry.pharmacy` | Health | Healthcare Experience | Healthcare | Healthcare | `health-sensitive` |
| Drug Distribution | `industry.drug-distribution` | Logistics | Operational B2B | Healthcare | Healthcare | `health-sensitive`, `physical-safety` |
| Clinical Trials | `industry.clinical-trials` | Science | Scientific & Technical | Healthcare | Healthcare | `health-sensitive` |
| Contract Manufacturing | `industry.contract-manufacturing` | Manufacturing | Operational B2B | Industrial | Industrial | `physical-safety` |
| Contract Development & Manufacturing | `industry.contract-development-and-manufacturing` | Manufacturing | Operational B2B | Industrial | Industrial | `physical-safety` |
| Laboratory Equipment | `industry.laboratory-equipment` | Manufacturing | Operational B2B | Science | Science | `physical-safety` |
| Scientific Software | `industry.scientific-software` | Software | Software Product | Science | Science | `standard` |
| Bioinformatics | `industry.bioinformatics` | Science | Scientific & Technical | Science | Science | `standard` |
| Agricultural Sciences | `industry.agricultural-sciences` | Agriculture | Operational B2B | Agriculture | Agriculture | `physical-safety` |
| Seed Industry | `industry.seed-industry` | Agriculture | Operational B2B | Agriculture | Agriculture | `physical-safety` |
| Fertilizers | `industry.fertilizers` | Manufacturing | Operational B2B | Industrial | Industrial | `physical-safety` |
| Agricultural Chemicals | `industry.agricultural-chemicals` | Manufacturing | Operational B2B | Agriculture | Agriculture | `physical-safety` |
| Farm Machinery | `industry.farm-machinery` | Manufacturing | Operational B2B | Agriculture | Agriculture | `physical-safety` |
| Irrigation | `industry.irrigation` | Agriculture | Operational B2B | Agriculture | Agriculture | `physical-safety` |
| Animal Feed | `industry.animal-feed` | Manufacturing | Operational B2B | Industrial | Industrial | `physical-safety` |
| Meat & Poultry | `industry.meat-and-poultry` | Manufacturing | Operational B2B | Industrial | Industrial | `physical-safety` |
| Seafood | `industry.seafood` | Manufacturing | Operational B2B | Industrial | Industrial | `physical-safety` |
| Dairy | `industry.dairy` | Manufacturing | Operational B2B | Industrial | Industrial | `physical-safety` |
| Bakery | `industry.bakery` | Restaurant | Restaurant Experience | Restaurant | Restaurant | `physical-safety` |
| Confectionery | `industry.confectionery` | Manufacturing | Operational B2B | Industrial | Industrial | `physical-safety` |
| Coffee & Tea | `industry.coffee-and-tea` | Restaurant | Restaurant Experience | Restaurant | Restaurant | `physical-safety` |
| Beverage Distribution | `industry.beverage-distribution` | Logistics | Operational B2B | Logistics | Logistics | `physical-safety` |
| Cold Chain | `industry.cold-chain` | Logistics | Operational B2B | Logistics | Logistics | `physical-safety` |
| Restaurant Supply | `industry.restaurant-supply` | Logistics | Operational B2B | Restaurant | Restaurant | `physical-safety` |
| Commercial Kitchens | `industry.commercial-kitchens` | Restaurant | Restaurant Experience | Restaurant | Restaurant | `physical-safety` |
| Hospitality Technology | `industry.hospitality-technology` | Software | Software Product | Hospitality | Hospitality | `standard` |
| Hotel Management | `industry.hotel-management` | Hospitality | Booking & Guest | Hospitality | Hospitality | `standard` |
| Vacation Rentals | `industry.vacation-rentals` | Hospitality | Booking & Guest | Hospitality | Hospitality | `standard` |
| Cruise Travel | `industry.cruise-travel` | Hospitality | Booking & Guest | Travel | Travel | `location-data` |
| Adventure Tourism | `industry.adventure-tourism` | Hospitality | Booking & Guest | Travel | Travel | `standard` |
| Ecotourism | `industry.ecotourism` | Hospitality | Booking & Guest | Travel | Travel | `standard` |
| Medical Tourism | `industry.medical-tourism` | Hospitality | Booking & Guest | Travel | Travel | `health-sensitive` |
| Education Tourism | `industry.education-tourism` | Hospitality | Booking & Guest | Travel | Travel | `standard` |
| Student Housing | `industry.student-housing` | Realestate | Real Estate Experience | Realestate | Realestate | `education-or-minors` |
| Commercial Property | `industry.commercial-property` | Realestate | Real Estate Experience | Realestate | Realestate | `standard` |
| Industrial Property | `industry.industrial-property` | Realestate | Real Estate Experience | Realestate | Realestate | `standard` |
| Real Estate Services | `industry.real-estate-services` | Realestate | Real Estate Experience | Realestate | Realestate | `standard` |
| Property Inspection | `industry.property-inspection` | Construction | Operational B2B | Realestate | Realestate | `physical-safety` |
| Surveying | `industry.surveying` | Construction | Operational B2B | Industrial | Industrial | `physical-safety` |
| Mortgage Technology | `industry.mortgage-technology` | Software | Software Product | Finance | Finance | `financial-regulated` |
| Construction Materials Distribution | `industry.construction-materials-distribution` | Logistics | Operational B2B | Logistics | Logistics | `physical-safety` |
| Building Automation | `industry.building-automation` | Construction | Operational B2B | Industrial | Industrial | `physical-safety` |
| Elevators & Escalators | `industry.elevators-and-escalators` | Construction | Operational B2B | Industrial | Industrial | `physical-safety` |
| Lighting | `industry.lighting` | Manufacturing | Operational B2B | Industrial | Industrial | `physical-safety` |
| Heating & Cooling | `industry.heating-and-cooling` | Construction | Operational B2B | Industrial | Industrial | `physical-safety` |
| Plumbing Industry | `industry.plumbing-industry` | Construction | Operational B2B | Industrial | Industrial | `physical-safety` |
| Electrical Industry | `industry.electrical-industry` | Construction | Operational B2B | Industrial | Industrial | `physical-safety` |
| Roofing Industry | `industry.roofing-industry` | Construction | Operational B2B | Industrial | Industrial | `physical-safety` |
| Flooring Industry | `industry.flooring-industry` | Construction | Operational B2B | Industrial | Industrial | `physical-safety` |
| Paint & Coatings | `industry.paint-and-coatings` | Manufacturing | Operational B2B | Industrial | Industrial | `physical-safety` |
| Glass Industry | `industry.glass-industry` | Manufacturing | Operational B2B | Industrial | Industrial | `physical-safety` |
| Doors & Windows | `industry.doors-and-windows` | Construction | Operational B2B | Energy | Energy | `critical-infrastructure`, `physical-safety` |
| Kitchen & Bath | `industry.kitchen-and-bath` | Construction | Operational B2B | Industrial | Industrial | `physical-safety` |
| Interior Furnishings | `industry.interior-furnishings` | Retail | Commerce | Commerce | Commerce | `standard` |
| Property Restoration | `industry.property-restoration` | Home Services | Professional Services | Realestate | Realestate | `physical-safety` |
| Mold Remediation | `industry.mold-remediation` | Home Services | Professional Services | Media | Media | `physical-safety` |
| Indoor Air Quality | `industry.indoor-air-quality` | Home Services | Professional Services | Home Services | Home Services | `physical-safety` |
| Fire Protection | `industry.fire-protection` | Construction | Operational B2B | Industrial | Industrial | `physical-safety` |
| Workplace Safety | `industry.workplace-safety` | Professional | Professional Services | Professional | Professional | `physical-safety` |
| Personal Protective Equipment | `industry.personal-protective-equipment` | Manufacturing | Operational B2B | Industrial | Industrial | `physical-safety` |
| Uniforms | `industry.uniforms` | Manufacturing | Operational B2B | Industrial | Industrial | `physical-safety` |
| Workwear | `industry.workwear` | Manufacturing | Operational B2B | Industrial | Industrial | `physical-safety` |
| Promotional Apparel | `industry.promotional-apparel` | Retail | Commerce | Commerce | Commerce | `standard` |
| Textiles | `industry.textiles` | Manufacturing | Operational B2B | Industrial | Industrial | `physical-safety` |
| Technical Textiles | `industry.technical-textiles` | Manufacturing | Operational B2B | Industrial | Industrial | `physical-safety` |
| Leather | `industry.leather` | Manufacturing | Operational B2B | Industrial | Industrial | `physical-safety` |
| Footwear | `industry.footwear` | Manufacturing | Operational B2B | Industrial | Industrial | `physical-safety` |
| Jewelry Retail | `industry.jewelry-retail` | Retail | Commerce | Commerce | Commerce | `standard` |
| Eyewear | `industry.eyewear` | Retail | Commerce | Commerce | Commerce | `standard` |
| Sporting Goods | `industry.sporting-goods` | Retail | Commerce | Commerce | Commerce | `standard` |
| Toys & Games | `industry.toys-and-games` | Retail | Commerce | Commerce | Commerce | `standard` |
| Stationery & Office Supplies | `industry.stationery-and-office-supplies` | Retail | Commerce | Commerce | Commerce | `standard` |
| Bookselling | `industry.bookselling` | Retail | Commerce | Commerce | Commerce | `standard` |
| Floristry | `industry.floristry` | Retail | Commerce | Commerce | Commerce | `standard` |
| Gardening | `industry.gardening` | Agriculture | Operational B2B | Agriculture | Agriculture | `physical-safety` |
| Hardware Retail | `industry.hardware-retail` | Retail | Commerce | Commerce | Commerce | `standard` |
| Consumer Appliances | `industry.consumer-appliances` | Manufacturing | Operational B2B | Industrial | Industrial | `physical-safety` |
| Home Electronics | `industry.home-electronics` | Manufacturing | Operational B2B | Industrial | Industrial | `physical-safety` |
| Mobile Devices | `industry.mobile-devices` | Retail | Commerce | Commerce | Commerce | `standard` |
| Computer Hardware | `industry.computer-hardware` | Manufacturing | Operational B2B | Industrial | Industrial | `physical-safety` |
| Computer Retail | `industry.computer-retail` | Retail | Commerce | Commerce | Commerce | `standard` |
| Office Equipment | `industry.office-equipment` | Manufacturing | Operational B2B | Industrial | Industrial | `physical-safety` |
| POS Systems | `industry.pos-systems` | Software | Software Product | Software | Software | `standard` |
| ATM Industry | `industry.atm-industry` | Manufacturing | Operational B2B | Industrial | Industrial | `physical-safety` |
| Cash Management | `industry.cash-management` | Logistics | Operational B2B | Logistics | Logistics | `physical-safety` |
| Armored Transportation | `industry.armored-transportation` | Logistics | Operational B2B | Logistics | Logistics | `physical-safety`, `location-data` |
| Precious Goods Logistics | `industry.precious-goods-logistics` | Logistics | Operational B2B | Logistics | Logistics | `physical-safety` |
| Art Logistics | `industry.art-logistics` | Logistics | Operational B2B | Logistics | Logistics | `physical-safety` |
| Moving & Relocation | `industry.moving-and-relocation` | Logistics | Operational B2B | Logistics | Logistics | `physical-safety`, `location-data` |
| Freight Brokerage | `industry.freight-brokerage` | Logistics | Operational B2B | Logistics | Logistics | `physical-safety` |
| Third-Party Logistics | `industry.third-party-logistics` | Logistics | Operational B2B | Logistics | Logistics | `physical-safety` |
| Fourth-Party Logistics | `industry.fourth-party-logistics` | Logistics | Operational B2B | Logistics | Logistics | `physical-safety` |
| Warehousing Technology | `industry.warehousing-technology` | Software | Software Product | Software | Software | `standard` |
| Material Handling | `industry.material-handling` | Logistics | Operational B2B | Logistics | Logistics | `physical-safety` |
| Industrial Distribution | `industry.industrial-distribution` | Logistics | Operational B2B | Logistics | Logistics | `physical-safety` |
| MRO | `industry.mro` | Logistics | Operational B2B | Logistics | Logistics | `physical-safety` |
| Fasteners | `industry.fasteners` | Manufacturing | Operational B2B | Industrial | Industrial | `physical-safety` |
| Bearings & Motion Control | `industry.bearings-and-motion-control` | Manufacturing | Operational B2B | Industrial | Industrial | `physical-safety` |
| Pumps & Valves | `industry.pumps-and-valves` | Manufacturing | Operational B2B | Industrial | Industrial | `physical-safety` |
| Hydraulics & Pneumatics | `industry.hydraulics-and-pneumatics` | Manufacturing | Operational B2B | Industrial | Industrial | `physical-safety` |
| Industrial Gases | `industry.industrial-gases` | Manufacturing | Operational B2B | Energy | Energy | `critical-infrastructure`, `physical-safety` |
| Welding | `industry.welding` | Manufacturing | Operational B2B | Industrial | Industrial | `physical-safety` |
| Machining | `industry.machining` | Manufacturing | Operational B2B | Industrial | Industrial | `physical-safety` |
| Metal Fabrication | `industry.metal-fabrication` | Manufacturing | Operational B2B | Industrial | Industrial | `physical-safety` |
| Forging & Casting | `industry.forging-and-casting` | Manufacturing | Operational B2B | Industrial | Industrial | `physical-safety` |
| Heat Treatment | `industry.heat-treatment` | Manufacturing | Operational B2B | Industrial | Industrial | `physical-safety` |
| Industrial Coatings | `industry.industrial-coatings` | Manufacturing | Operational B2B | Industrial | Industrial | `physical-safety` |
| Additive Manufacturing | `industry.additive-manufacturing` | Manufacturing | Operational B2B | Industrial | Industrial | `physical-safety` |
| Injection Molding | `industry.injection-molding` | Manufacturing | Operational B2B | Industrial | Industrial | `physical-safety` |
| Plastic Products | `industry.plastic-products` | Manufacturing | Operational B2B | Industrial | Industrial | `physical-safety` |
| Rubber Products | `industry.rubber-products` | Manufacturing | Operational B2B | Industrial | Industrial | `physical-safety` |
| Tire Industry | `industry.tire-industry` | Automotive | Operational B2B | Automotive | Automotive | `physical-safety` |
| Automotive Aftermarket | `industry.automotive-aftermarket` | Automotive | Operational B2B | Automotive | Automotive | `physical-safety` |
| Vehicle Inspection | `industry.vehicle-inspection` | Automotive | Operational B2B | Automotive | Automotive | `physical-safety` |
| Roadside Assistance | `industry.roadside-assistance` | Automotive | Operational B2B | Automotive | Automotive | `physical-safety` |
| Towing | `industry.towing` | Automotive | Operational B2B | Automotive | Automotive | `physical-safety` |
| Car Rental | `industry.car-rental` | Automotive | Operational B2B | Automotive | Automotive | `physical-safety` |
| Truck Rental | `industry.truck-rental` | Automotive | Operational B2B | Automotive | Automotive | `physical-safety` |
| Fleet Leasing | `industry.fleet-leasing` | Automotive | Operational B2B | Automotive | Automotive | `physical-safety`, `location-data` |
| Marine Insurance | `industry.marine-insurance` | Finance | Financial Experience | Finance | Finance | `financial-regulated` |
| Marine Logistics | `industry.marine-logistics` | Logistics | Operational B2B | Logistics | Logistics | `physical-safety` |
| Port Operations | `industry.port-operations` | Logistics | Operational B2B | Logistics | Logistics | `physical-safety` |
| Ship Management | `industry.ship-management` | Logistics | Operational B2B | Logistics | Logistics | `physical-safety` |
| Offshore Energy | `industry.offshore-energy` | Energy | Operational B2B | Energy | Energy | `critical-infrastructure`, `physical-safety` |
| Subsea Services | `industry.subsea-services` | Professional | Professional Services | Professional | Professional | `standard` |
| Rail Infrastructure | `industry.rail-infrastructure` | Construction | Operational B2B | Logistics | Logistics | `critical-infrastructure`, `physical-safety` |
| Rail Equipment | `industry.rail-equipment` | Manufacturing | Operational B2B | Logistics | Logistics | `physical-safety` |
| Bus & Coach | `industry.bus-and-coach` | Logistics | Operational B2B | Logistics | Logistics | `physical-safety` |
| Taxi & Chauffeur | `industry.taxi-and-chauffeur` | Logistics | Operational B2B | Logistics | Logistics | `physical-safety` |
| Micromobility | `industry.micromobility` | Automotive | Operational B2B | Automotive | Automotive | `physical-safety`, `location-data` |
| Bicycle Industry | `industry.bicycle-industry` | Automotive | Operational B2B | Automotive | Automotive | `physical-safety` |
| Motorcycle Industry | `industry.motorcycle-industry` | Automotive | Operational B2B | Automotive | Automotive | `physical-safety` |
| Recreational Vehicles | `industry.recreational-vehicles` | Automotive | Operational B2B | Automotive | Automotive | `physical-safety` |
| Boating | `industry.boating` | Automotive | Operational B2B | Automotive | Automotive | `physical-safety` |
| Camping | `industry.camping` | Sports | Sports & Membership | Sports | Sports | `physical-safety` |
| Ski Industry | `industry.ski-industry` | Sports | Sports & Membership | Sports | Sports | `physical-safety` |
| Adventure Sports | `industry.adventure-sports` | Sports | Sports & Membership | Sports | Sports | `physical-safety` |
| Diving Industry | `industry.diving-industry` | Sports | Sports & Membership | Sports | Sports | `physical-safety` |
| Commercial Diving | `industry.commercial-diving` | Professional | Professional Services | Professional | Professional | `standard` |
| Salvage | `industry.salvage` | Logistics | Operational B2B | Logistics | Logistics | `physical-safety` |
| Recycling | `industry.recycling` | Logistics | Operational B2B | Logistics | Logistics | `physical-safety` |
| Scrap Metal | `industry.scrap-metal` | Logistics | Operational B2B | Logistics | Logistics | `physical-safety` |
| E-Waste | `industry.e-waste` | Logistics | Operational B2B | Logistics | Logistics | `physical-safety` |
| IT Asset Disposition | `industry.it-asset-disposition` | Logistics | Operational B2B | Logistics | Logistics | `physical-safety` |
| Data Destruction | `industry.data-destruction` | Cyber | Software Product | Security | Security | `security-identity` |
| Records Management | `industry.records-management` | Professional | Professional Services | Professional | Professional | `standard` |
| Archiving | `industry.archiving` | Professional | Professional Services | Professional | Professional | `standard` |
| Data Privacy Services | `industry.data-privacy-services` | Cyber | Software Product | Security | Security | `security-identity` |
| Cyber Insurance | `industry.cyber-insurance` | Finance | Financial Experience | Finance | Finance | `financial-regulated` |
| Identity Theft Protection | `industry.identity-theft-protection` | Cyber | Software Product | Security | Security | `security-identity` |
| Forensics | `industry.forensics` | Professional | Professional Services | Professional | Professional | `security-identity` |
| Digital Forensics | `industry.digital-forensics` | Cyber | Software Product | Security | Security | `security-identity` |
| Incident Response | `industry.incident-response` | Cyber | Software Product | Security | Security | `security-identity` |
| Crisis Management | `industry.crisis-management` | Professional | Professional Services | Professional | Professional | `standard` |
| Business Continuity | `industry.business-continuity` | Professional | Professional Services | Professional | Professional | `standard` |
| Disaster Recovery | `industry.disaster-recovery` | Professional | Professional Services | Professional | Professional | `standard` |
| Backup & Recovery | `industry.backup-and-recovery` | Software | Software Product | Software | Software | `standard` |
| Data Recovery | `industry.data-recovery` | Professional | Professional Services | Professional | Professional | `standard` |
| Managed Security | `industry.managed-security` | Cyber | Software Product | Security | Security | `security-identity` |
| Security Operations | `industry.security-operations` | Cyber | Software Product | Security | Security | `security-identity` |
| Threat Intelligence | `industry.threat-intelligence` | Cyber | Software Product | Security | Security | `security-identity` |
| Dark Web Monitoring | `industry.dark-web-monitoring` | Cyber | Software Product | Security | Security | `security-identity` |
| Brand Protection | `industry.brand-protection` | Legal | Professional Services | Legal | Legal | `legal-regulated` |
| Anti-Counterfeiting | `industry.anti-counterfeiting` | Cyber | Software Product | Security | Security | `security-identity` |
| Product Authentication | `industry.product-authentication` | Software | Software Product | Security | Security | `security-identity` |
| Supply Chain Traceability | `industry.supply-chain-traceability` | Logistics | Operational B2B | Logistics | Logistics | `physical-safety` |
| Cold Storage | `industry.cold-storage` | Logistics | Operational B2B | Logistics | Logistics | `physical-safety` |
| Food Safety | `industry.food-safety` | Science | Scientific & Technical | Science | Science | `physical-safety` |
| Agricultural Inspection | `industry.agricultural-inspection` | Science | Scientific & Technical | Agriculture | Agriculture | `standard` |
| Certification Bodies | `industry.certification-bodies` | Professional | Professional Services | Professional | Professional | `standard` |
| Standards Organizations | `industry.standards-organizations` | Professional | Professional Services | Professional | Professional | `standard` |
| Patent Services | `industry.patent-services` | Legal | Professional Services | Legal | Legal | `legal-regulated` |
| Trademark Services | `industry.trademark-services` | Legal | Professional Services | Legal | Legal | `legal-regulated` |
| Licensing Agencies | `industry.licensing-agencies` | Professional | Professional Services | Professional | Professional | `standard` |
| Royalties Management | `industry.royalties-management` | Media | Content & Media | Media | Media | `standard` |
| Rights Management | `industry.rights-management` | Media | Content & Media | Media | Media | `standard` |
| Digital Rights Management | `industry.digital-rights-management` | Software | Software Product | Media | Media | `standard` |
| Anti-Piracy | `industry.anti-piracy` | Media | Content & Media | Media | Media | `standard` |
| Content Moderation | `industry.content-moderation` | Software | Software Product | Software | Software | `platform-trust-safety` |
| Trust & Safety | `industry.trust-and-safety` | Software | Software Product | Software | Software | `physical-safety` |
| Online Communities | `industry.online-communities` | Software | Software Product | Software | Software | `platform-trust-safety` |
| Dating | `industry.dating` | Marketplace | Marketplace Platform | Marketplace | Marketplace | `platform-trust-safety` |
| Social Discovery | `industry.social-discovery` | Software | Software Product | Software | Software | `standard` |
| Messaging | `industry.messaging` | Software | Software Product | Software | Software | `standard` |
| Email | `industry.email` | Software | Software Product | Software | Software | `standard` |
| Email Security | `industry.email-security` | Cyber | Software Product | Security | Security | `security-identity` |
| Domain Security | `industry.domain-security` | Cyber | Software Product | Security | Security | `security-identity` |
| DNS | `industry.dns` | Software | Software Product | Software | Software | `standard` |
| Internet Infrastructure | `industry.internet-infrastructure` | Software | Software Product | Software | Software | `standard` |
| Content Delivery Networks | `industry.content-delivery-networks` | Software | Software Product | Logistics | Logistics | `location-data` |
| Video Technology | `industry.video-technology` | Software | Software Product | Media | Media | `standard` |
| Streaming Technology | `industry.streaming-technology` | Software | Software Product | Media | Media | `standard` |
| Live Streaming | `industry.live-streaming` | Media | Content & Media | Media | Media | `standard` |
| Broadcast Technology | `industry.broadcast-technology` | Telecom | Operational B2B | Telecom | Telecom | `critical-infrastructure`, `physical-safety` |
| Radio | `industry.radio` | Media | Content & Media | Media | Media | `standard` |
| Television | `industry.television` | Media | Content & Media | Media | Media | `standard` |
| Cable & Satellite | `industry.cable-and-satellite` | Telecom | Operational B2B | Telecom | Telecom | `critical-infrastructure`, `physical-safety` |
| Fiber Optics | `industry.fiber-optics` | Telecom | Operational B2B | Telecom | Telecom | `critical-infrastructure`, `physical-safety` |
| Wireless Infrastructure | `industry.wireless-infrastructure` | Telecom | Operational B2B | Telecom | Telecom | `critical-infrastructure`, `physical-safety` |
| Tower Industry | `industry.tower-industry` | Telecom | Operational B2B | Telecom | Telecom | `critical-infrastructure`, `physical-safety` |
| Satellite Industry | `industry.satellite-industry` | Telecom | Operational B2B | Telecom | Telecom | `critical-infrastructure`, `physical-safety` |
| Earth Observation | `industry.earth-observation` | Science | Scientific & Technical | Science | Science | `standard` |
| Navigation Satellites | `industry.navigation-satellites` | Telecom | Operational B2B | Telecom | Telecom | `critical-infrastructure`, `physical-safety`, `location-data` |
| Remote Sensing | `industry.remote-sensing` | Science | Scientific & Technical | Science | Science | `standard` |
| Drone Services | `industry.drone-services` | Professional | Professional Services | Professional | Professional | `standard` |
| Drone Delivery | `industry.drone-delivery` | Logistics | Operational B2B | Logistics | Logistics | `physical-safety`, `location-data` |
| Air Mobility | `industry.air-mobility` | Automotive | Operational B2B | Travel | Travel | `physical-safety`, `location-data` |
| Aviation Technology | `industry.aviation-technology` | Software | Software Product | Travel | Travel | `standard` |
| Air Traffic Management | `industry.air-traffic-management` | Logistics | Operational B2B | Logistics | Logistics | `critical-infrastructure`, `physical-safety` |
| Airport Services | `industry.airport-services` | Logistics | Operational B2B | Travel | Travel | `physical-safety` |
| Ground Handling | `industry.ground-handling` | Logistics | Operational B2B | Logistics | Logistics | `physical-safety` |
| Aircraft Leasing | `industry.aircraft-leasing` | Finance | Financial Experience | Finance | Finance | `financial-regulated` |
| Aircraft Finance | `industry.aircraft-finance` | Finance | Financial Experience | Finance | Finance | `financial-regulated` |
| Aircraft Maintenance | `industry.aircraft-maintenance` | Automotive | Operational B2B | Automotive | Automotive | `physical-safety` |
| Engine Manufacturing | `industry.engine-manufacturing` | Manufacturing | Operational B2B | Industrial | Industrial | `physical-safety` |
| Turbines | `industry.turbines` | Manufacturing | Operational B2B | Industrial | Industrial | `physical-safety` |
| Wind Energy | `industry.wind-energy` | Energy | Operational B2B | Energy | Energy | `critical-infrastructure`, `physical-safety` |
| Solar Energy | `industry.solar-energy` | Energy | Operational B2B | Energy | Energy | `critical-infrastructure`, `physical-safety` |
| Hydropower | `industry.hydropower` | Energy | Operational B2B | Energy | Energy | `critical-infrastructure`, `physical-safety` |
| Geothermal | `industry.geothermal` | Energy | Operational B2B | Energy | Energy | `critical-infrastructure`, `physical-safety` |
| Bioenergy | `industry.bioenergy` | Energy | Operational B2B | Energy | Energy | `critical-infrastructure`, `physical-safety` |
| Hydrogen | `industry.hydrogen` | Energy | Operational B2B | Energy | Energy | `critical-infrastructure`, `physical-safety` |
| Fuel Cells | `industry.fuel-cells` | Energy | Operational B2B | Energy | Energy | `critical-infrastructure`, `physical-safety` |
| Energy Storage | `industry.energy-storage` | Energy | Operational B2B | Energy | Energy | `critical-infrastructure`, `physical-safety` |
| Grid Technology | `industry.grid-technology` | Energy | Operational B2B | Energy | Energy | `critical-infrastructure`, `physical-safety` |
| Power Electronics | `industry.power-electronics` | Manufacturing | Operational B2B | Industrial | Industrial | `physical-safety` |
| Electrical Grid | `industry.electrical-grid` | Energy | Operational B2B | Energy | Energy | `critical-infrastructure`, `physical-safety` |
| Energy Trading | `industry.energy-trading` | Finance | Financial Experience | Finance | Finance | `financial-regulated` |
| Utilities Software | `industry.utilities-software` | Software | Software Product | Energy | Energy | `critical-infrastructure` |
| Metering | `industry.metering` | Energy | Operational B2B | Energy | Energy | `critical-infrastructure`, `physical-safety` |
| Water Metering | `industry.water-metering` | Energy | Operational B2B | Energy | Energy | `critical-infrastructure`, `physical-safety` |
| Leak Detection | `industry.leak-detection` | Energy | Operational B2B | Energy | Energy | `critical-infrastructure`, `physical-safety` |
| Pipeline Industry | `industry.pipeline-industry` | Energy | Operational B2B | Energy | Energy | `critical-infrastructure`, `physical-safety` |
| Pipeline Services | `industry.pipeline-services` | Energy | Operational B2B | Energy | Energy | `critical-infrastructure`, `physical-safety` |
| Oilfield Services | `industry.oilfield-services` | Energy | Operational B2B | Energy | Energy | `critical-infrastructure`, `physical-safety` |
| Drilling | `industry.drilling` | Energy | Operational B2B | Energy | Energy | `critical-infrastructure`, `physical-safety` |
| Geological Services | `industry.geological-services` | Science | Scientific & Technical | Science | Science | `standard` |
| Mining Technology | `industry.mining-technology` | Software | Software Product | Software | Software | `physical-safety` |
| Mineral Processing | `industry.mineral-processing` | Manufacturing | Operational B2B | Industrial | Industrial | `physical-safety` |
| Metallurgy | `industry.metallurgy` | Manufacturing | Operational B2B | Industrial | Industrial | `physical-safety` |
| Steel Industry | `industry.steel-industry` | Manufacturing | Operational B2B | Industrial | Industrial | `physical-safety` |
| Aluminum Industry | `industry.aluminum-industry` | Manufacturing | Operational B2B | Industrial | Industrial | `physical-safety` |
| Copper Industry | `industry.copper-industry` | Manufacturing | Operational B2B | Industrial | Industrial | `physical-safety` |
| Rare Earths | `industry.rare-earths` | Manufacturing | Operational B2B | Industrial | Industrial | `physical-safety` |
| Magnet Industry | `industry.magnet-industry` | Manufacturing | Operational B2B | Industrial | Industrial | `physical-safety` |
| Ceramics | `industry.ceramics` | Manufacturing | Operational B2B | Industrial | Industrial | `physical-safety` |
| Cement | `industry.cement` | Manufacturing | Operational B2B | Industrial | Industrial | `physical-safety` |
| Concrete | `industry.concrete` | Construction | Operational B2B | Industrial | Industrial | `physical-safety` |
| Aggregates | `industry.aggregates` | Manufacturing | Operational B2B | Industrial | Industrial | `physical-safety` |
| Quarrying | `industry.quarrying` | Manufacturing | Operational B2B | Industrial | Industrial | `physical-safety` |
| Stone Industry | `industry.stone-industry` | Manufacturing | Operational B2B | Industrial | Industrial | `physical-safety` |
| Wood Products | `industry.wood-products` | Manufacturing | Operational B2B | Industrial | Industrial | `physical-safety` |
| Paper Industry | `industry.paper-industry` | Manufacturing | Operational B2B | Industrial | Industrial | `physical-safety` |
| Pulp | `industry.pulp` | Manufacturing | Operational B2B | Industrial | Industrial | `physical-safety` |
| Printing Paper | `industry.printing-paper` | Manufacturing | Operational B2B | Industrial | Industrial | `physical-safety` |
| Packaging Paper | `industry.packaging-paper` | Manufacturing | Operational B2B | Industrial | Industrial | `physical-safety` |
| Corrugated Packaging | `industry.corrugated-packaging` | Manufacturing | Operational B2B | Industrial | Industrial | `physical-safety` |
| Flexible Packaging | `industry.flexible-packaging` | Manufacturing | Operational B2B | Industrial | Industrial | `physical-safety` |
| Labels | `industry.labels` | Manufacturing | Operational B2B | Industrial | Industrial | `physical-safety` |
| RFID | `industry.rfid` | Manufacturing | Operational B2B | Industrial | Industrial | `physical-safety` |
| Asset Tracking | `industry.asset-tracking` | Software | Software Product | Software | Software | `standard` |
| Inventory Management | `industry.inventory-management` | Software | Software Product | Software | Software | `standard` |
| Procurement Technology | `industry.procurement-technology` | Software | Software Product | Software | Software | `standard` |
| Spend Management | `industry.spend-management` | Software | Software Product | Software | Software | `standard` |
| Supplier Management | `industry.supplier-management` | Software | Software Product | Software | Software | `standard` |
| Vendor Management | `industry.vendor-management` | Software | Software Product | Software | Software | `standard` |
| Contractor Management | `industry.contractor-management` | Software | Software Product | Software | Software | `standard` |
| Field Service Management | `industry.field-service-management` | Software | Software Product | Software | Software | `standard` |
| Maintenance Software | `industry.maintenance-software` | Software | Software Product | Software | Software | `standard` |
| Enterprise Asset Management | `industry.enterprise-asset-management` | Software | Software Product | Software | Software | `standard` |
| Facilities Software | `industry.facilities-software` | Software | Software Product | Software | Software | `standard` |
| Space Management | `industry.space-management` | Software | Software Product | Software | Software | `standard` |
| Workplace Technology | `industry.workplace-technology` | Software | Software Product | Software | Software | `standard` |
| Remote Work | `industry.remote-work` | Software | Software Product | Software | Software | `standard` |
| Virtual Desktop | `industry.virtual-desktop` | Software | Software Product | Software | Software | `standard` |
| Networking | `industry.networking` | Software | Software Product | Software | Software | `standard` |
| Network Hardware | `industry.network-hardware` | Manufacturing | Operational B2B | Industrial | Industrial | `physical-safety` |
| Storage Technology | `industry.storage-technology` | Software | Software Product | Software | Software | `standard` |
| Memory | `industry.memory` | Manufacturing | Operational B2B | Industrial | Industrial | `physical-safety` |
| Processors | `industry.processors` | Manufacturing | Operational B2B | Industrial | Industrial | `physical-safety` |
| AI Chips | `industry.ai-chips` | Manufacturing | Operational B2B | Industrial | Industrial | `physical-safety` |
| Chip Equipment | `industry.chip-equipment` | Manufacturing | Operational B2B | Industrial | Industrial | `physical-safety` |
| Electronic Design Automation | `industry.electronic-design-automation` | Software | Software Product | Software | Software | `standard` |
| Printed Circuit Boards | `industry.printed-circuit-boards` | Manufacturing | Operational B2B | Industrial | Industrial | `physical-safety` |
| Electronic Components | `industry.electronic-components` | Manufacturing | Operational B2B | Industrial | Industrial | `physical-safety` |
| Sensors | `industry.sensors` | Manufacturing | Operational B2B | Industrial | Industrial | `physical-safety` |
| Industrial Controls | `industry.industrial-controls` | Manufacturing | Operational B2B | Industrial | Industrial | `physical-safety` |
| SCADA | `industry.scada` | Manufacturing | Operational B2B | Industrial | Industrial | `physical-safety` |
| Process Automation | `industry.process-automation` | Manufacturing | Operational B2B | Industrial | Industrial | `physical-safety` |
| Manufacturing Software | `industry.manufacturing-software` | Software | Software Product | Industrial | Industrial | `standard` |
| Product Lifecycle Management | `industry.product-lifecycle-management` | Software | Software Product | Software | Software | `standard` |
| Manufacturing Execution Systems | `industry.manufacturing-execution-systems` | Software | Software Product | Industrial | Industrial | `standard` |
| Enterprise Resource Planning | `industry.enterprise-resource-planning` | Software | Software Product | Software | Software | `standard` |
| Customer Relationship Management | `industry.customer-relationship-management` | Software | Software Product | Software | Software | `standard` |
| Customer Support Software | `industry.customer-support-software` | Software | Software Product | Logistics | Logistics | `standard` |
| Contact Center Technology | `industry.contact-center-technology` | Software | Software Product | Software | Software | `standard` |
| Voice Technology | `industry.voice-technology` | Software | Software Product | Software | Software | `standard` |
| Speech Technology | `industry.speech-technology` | Software | Software Product | Software | Software | `standard` |
| Conversational AI | `industry.conversational-ai` | Ai | Software Product | Ai | Ai | `automated-decisioning` |
| Search Technology | `industry.search-technology` | Software | Software Product | Software | Software | `standard` |
| Recommendation Technology | `industry.recommendation-technology` | Software | Software Product | Software | Software | `standard` |
| Personalization | `industry.personalization` | Software | Software Product | Software | Software | `standard` |
| Marketing Automation | `industry.marketing-automation` | Software | Software Product | Software | Software | `standard` |
| Campaign Management | `industry.campaign-management` | Professional | Professional Services | Professional | Professional | `standard` |
| Analytics Software | `industry.analytics-software` | Software | Software Product | Software | Software | `standard` |
| Web Analytics | `industry.web-analytics` | Software | Software Product | Software | Software | `standard` |
| Product Analytics | `industry.product-analytics` | Software | Software Product | Software | Software | `standard` |
| Mobile Analytics | `industry.mobile-analytics` | Software | Software Product | Software | Software | `standard` |
| Attribution | `industry.attribution` | Software | Software Product | Software | Software | `standard` |
| Ad Measurement | `industry.ad-measurement` | Media | Content & Media | Media | Media | `standard` |
| Audience Measurement | `industry.audience-measurement` | Media | Content & Media | Media | Media | `standard` |
| Consumer Insights | `industry.consumer-insights` | Professional | Professional Services | Professional | Professional | `standard` |
| Survey Technology | `industry.survey-technology` | Software | Software Product | Software | Software | `standard` |
| Polling | `industry.polling` | Professional | Professional Services | Professional | Professional | `standard` |
| Location Analytics | `industry.location-analytics` | Software | Software Product | Software | Software | `location-data` |
| Retail Analytics | `industry.retail-analytics` | Software | Software Product | Commerce | Commerce | `standard` |
| Pricing Technology | `industry.pricing-technology` | Software | Software Product | Software | Software | `standard` |
| Revenue Management | `industry.revenue-management` | Professional | Professional Services | Professional | Professional | `standard` |
| Yield Management | `industry.yield-management` | Professional | Professional Services | Professional | Professional | `standard` |
| Forecasting Software | `industry.forecasting-software` | Software | Software Product | Software | Software | `standard` |
| Planning Software | `industry.planning-software` | Software | Software Product | Software | Software | `standard` |
| FP&A | `industry.fp-and-a` | Finance | Financial Experience | Finance | Finance | `financial-regulated` |
| Budgeting | `industry.budgeting` | Finance | Financial Experience | Finance | Finance | `financial-regulated` |
| Business Intelligence | `industry.business-intelligence` | Software | Software Product | Software | Software | `standard` |
| Data Visualization | `industry.data-visualization` | Software | Software Product | Software | Software | `standard` |
| Data Engineering | `industry.data-engineering` | Software | Software Product | Software | Software | `standard` |
| Data Integration | `industry.data-integration` | Software | Software Product | Software | Software | `standard` |
| Master Data Management | `industry.master-data-management` | Software | Software Product | Software | Software | `standard` |
| Customer Data Platforms | `industry.customer-data-platforms` | Software | Software Product | Software | Software | `standard` |
| Data Governance | `industry.data-governance` | Software | Software Product | Software | Software | `standard` |
| Data Quality | `industry.data-quality` | Software | Software Product | Software | Software | `standard` |
| Data Observability | `industry.data-observability` | Software | Software Product | Software | Software | `standard` |
| Machine Learning Operations | `industry.machine-learning-operations` | Ai | Software Product | Education | Education | `education-or-minors`, `automated-decisioning` |
| AI Infrastructure | `industry.ai-infrastructure` | Ai | Software Product | Ai | Ai | `automated-decisioning` |
| Model Hosting | `industry.model-hosting` | Ai | Software Product | Ai | Ai | `automated-decisioning` |
| Foundation Models | `industry.foundation-models` | Ai | Software Product | Ai | Ai | `automated-decisioning` |
| Generative AI | `industry.generative-ai` | Ai | Software Product | Ai | Ai | `automated-decisioning` |
| Synthetic Media | `industry.synthetic-media` | Ai | Software Product | Media | Media | `standard` |
| Computer Vision | `industry.computer-vision` | Ai | Software Product | Ai | Ai | `automated-decisioning` |
| Machine Vision | `industry.machine-vision` | Ai | Software Product | Ai | Ai | `automated-decisioning` |
| Facial Recognition | `industry.facial-recognition` | Cyber | Software Product | Security | Security | `security-identity` |
| Biometrics | `industry.biometrics` | Cyber | Software Product | Security | Security | `security-identity` |
| Authentication | `industry.authentication` | Cyber | Software Product | Security | Security | `security-identity` |
| Identity & Access Management | `industry.identity-and-access-management` | Cyber | Software Product | Security | Security | `security-identity` |
| Zero Trust | `industry.zero-trust` | Cyber | Software Product | Security | Security | `security-identity` |
| Application Security | `industry.application-security` | Cyber | Software Product | Security | Security | `security-identity` |
| API Security | `industry.api-security` | Cyber | Software Product | Security | Security | `security-identity` |
| Cloud Security | `industry.cloud-security` | Cyber | Software Product | Security | Security | `security-identity` |
| Endpoint Security | `industry.endpoint-security` | Cyber | Software Product | Security | Security | `security-identity` |
| Network Security | `industry.network-security` | Cyber | Software Product | Security | Security | `security-identity` |
| Data Security | `industry.data-security` | Cyber | Software Product | Security | Security | `security-identity` |
| Data Loss Prevention | `industry.data-loss-prevention` | Cyber | Software Product | Events | Events | `standard` |
| Encryption | `industry.encryption` | Cyber | Software Product | Security | Security | `security-identity` |
| Key Management | `industry.key-management` | Cyber | Software Product | Security | Security | `security-identity` |
| Public Key Infrastructure | `industry.public-key-infrastructure` | Cyber | Software Product | Security | Security | `security-identity` |
| Digital Certificates | `industry.digital-certificates` | Cyber | Software Product | Security | Security | `security-identity` |
| Code Security | `industry.code-security` | Cyber | Software Product | Security | Security | `security-identity` |
| Software Supply Chain | `industry.software-supply-chain` | Cyber | Software Product | Logistics | Logistics | `standard` |
| Open-Source Security | `industry.open-source-security` | Cyber | Software Product | Security | Security | `security-identity` |
| Vulnerability Management | `industry.vulnerability-management` | Cyber | Software Product | Security | Security | `security-identity` |
| Patch Management | `industry.patch-management` | Cyber | Software Product | Security | Security | `security-identity` |
| Endpoint Management | `industry.endpoint-management` | Cyber | Software Product | Security | Security | `security-identity` |
| Mobile Device Management | `industry.mobile-device-management` | Cyber | Software Product | Security | Security | `security-identity` |
| Enterprise Mobility | `industry.enterprise-mobility` | Software | Software Product | Automotive | Automotive | `location-data` |
| Workforce Technology | `industry.workforce-technology` | Software | Software Product | Software | Software | `standard` |
| Time Tracking | `industry.time-tracking` | Software | Software Product | Software | Software | `standard` |
| Scheduling Software | `industry.scheduling-software` | Software | Software Product | Software | Software | `standard` |
| Payroll Technology | `industry.payroll-technology` | Software | Software Product | Software | Software | `standard` |
| Global Employment | `industry.global-employment` | Professional | Professional Services | Professional | Professional | `standard` |
| Freelance Economy | `industry.freelance-economy` | Marketplace | Marketplace Platform | Marketplace | Marketplace | `platform-trust-safety` |
| Gig Economy | `industry.gig-economy` | Marketplace | Marketplace Platform | Marketplace | Marketplace | `platform-trust-safety` |
| Labor Marketplaces | `industry.labor-marketplaces` | Marketplace | Marketplace Platform | Marketplace | Marketplace | `platform-trust-safety` |
| Professional Networking | `industry.professional-networking` | Marketplace | Marketplace Platform | Marketplace | Marketplace | `platform-trust-safety` |
| Job Boards | `industry.job-boards` | Marketplace | Marketplace Platform | Marketplace | Marketplace | `platform-trust-safety` |
| Career Services | `industry.career-services` | Professional | Professional Services | Professional | Professional | `standard` |
| Outplacement | `industry.outplacement` | Professional | Professional Services | Industrial | Industrial | `standard` |
| Employee Engagement | `industry.employee-engagement` | Software | Software Product | Software | Software | `standard` |
| Employee Recognition | `industry.employee-recognition` | Software | Software Product | Software | Software | `standard` |
| Corporate Gifts | `industry.corporate-gifts` | Retail | Commerce | Commerce | Commerce | `standard` |
| Incentive Programs | `industry.incentive-programs` | Professional | Professional Services | Professional | Professional | `standard` |
| Sales Compensation | `industry.sales-compensation` | Software | Software Product | Software | Software | `standard` |
| Sales Performance Management | `industry.sales-performance-management` | Software | Software Product | Software | Software | `standard` |
| Revenue Operations | `industry.revenue-operations` | Professional | Professional Services | Professional | Professional | `standard` |
| Customer Success | `industry.customer-success` | Professional | Professional Services | Professional | Professional | `standard` |
| Subscription Management | `industry.subscription-management` | Software | Software Product | Software | Software | `standard` |
| Billing Technology | `industry.billing-technology` | Software | Software Product | Finance | Finance | `financial-regulated` |
| Accounts Receivable | `industry.accounts-receivable` | Finance | Financial Experience | Finance | Finance | `financial-regulated` |
| Accounts Payable | `industry.accounts-payable` | Finance | Financial Experience | Finance | Finance | `financial-regulated` |
| Procure-to-Pay | `industry.procure-to-pay` | Software | Software Product | Software | Software | `standard` |
| Order Management | `industry.order-management` | Software | Software Product | Software | Software | `standard` |
| Returns Management | `industry.returns-management` | Software | Software Product | Software | Software | `standard` |
| Reverse Logistics | `industry.reverse-logistics` | Logistics | Operational B2B | Logistics | Logistics | `physical-safety` |
| Fulfillment Technology | `industry.fulfillment-technology` | Software | Software Product | Logistics | Logistics | `standard` |
| Shipping Technology | `industry.shipping-technology` | Software | Software Product | Logistics | Logistics | `standard` |
| Delivery Technology | `industry.delivery-technology` | Software | Software Product | Logistics | Logistics | `location-data` |
| Route Optimization | `industry.route-optimization` | Software | Software Product | Logistics | Logistics | `location-data` |
| Supply Chain Visibility | `industry.supply-chain-visibility` | Software | Software Product | Logistics | Logistics | `standard` |
| Trade Compliance | `industry.trade-compliance` | Professional | Professional Services | Professional | Professional | `standard` |
| Customs Technology | `industry.customs-technology` | Software | Software Product | Software | Software | `standard` |
| Import Compliance | `industry.import-compliance` | Professional | Professional Services | Logistics | Logistics | `standard` |
| Export Compliance | `industry.export-compliance` | Professional | Professional Services | Logistics | Logistics | `standard` |
| Sanctions Screening | `industry.sanctions-screening` | Software | Software Product | Security | Security | `financial-regulated`, `security-identity` |
| Know Your Customer | `industry.know-your-customer` | Software | Software Product | Security | Security | `financial-regulated`, `security-identity` |
| AML | `industry.aml` | Finance | Financial Experience | Finance | Finance | `financial-regulated` |
| Transaction Monitoring | `industry.transaction-monitoring` | Software | Software Product | Security | Security | `financial-regulated`, `security-identity` |
| Credit Risk | `industry.credit-risk` | Finance | Financial Experience | Finance | Finance | `financial-regulated` |
| Underwriting | `industry.underwriting` | Finance | Financial Experience | Finance | Finance | `financial-regulated` |
| Actuarial Services | `industry.actuarial-services` | Finance | Financial Experience | Finance | Finance | `financial-regulated` |
| Claims Management | `industry.claims-management` | Finance | Financial Experience | Finance | Finance | `financial-regulated` |
| Claims Technology | `industry.claims-technology` | Software | Software Product | Software | Software | `standard` |
| Insurance Distribution | `industry.insurance-distribution` | Finance | Financial Experience | Finance | Finance | `financial-regulated` |
| Insurance Marketplaces | `industry.insurance-marketplaces` | Marketplace | Marketplace Platform | Finance | Finance | `financial-regulated`, `platform-trust-safety` |
| Embedded Insurance | `industry.embedded-insurance` | Finance | Financial Experience | Finance | Finance | `financial-regulated` |
| Embedded Finance | `industry.embedded-finance` | Finance | Financial Experience | Finance | Finance | `financial-regulated` |
| Banking-as-a-Service | `industry.banking-as-a-service` | Finance | Financial Experience | Finance | Finance | `financial-regulated` |
| Payments Infrastructure | `industry.payments-infrastructure` | Finance | Financial Experience | Finance | Finance | `financial-regulated` |
| Merchant Services | `industry.merchant-services` | Finance | Financial Experience | Finance | Finance | `financial-regulated` |
| Card Issuing | `industry.card-issuing` | Finance | Financial Experience | Finance | Finance | `financial-regulated` |
| Corporate Cards | `industry.corporate-cards` | Finance | Financial Experience | Finance | Finance | `financial-regulated` |
| Virtual Cards | `industry.virtual-cards` | Finance | Financial Experience | Finance | Finance | `financial-regulated` |
| Cross-Border Payments | `industry.cross-border-payments` | Finance | Financial Experience | Finance | Finance | `financial-regulated` |
| Remittances | `industry.remittances` | Finance | Financial Experience | Finance | Finance | `financial-regulated` |
| Foreign Exchange | `industry.foreign-exchange` | Finance | Financial Experience | Finance | Finance | `financial-regulated` |
| Digital Wallets | `industry.digital-wallets` | Finance | Financial Experience | Finance | Finance | `financial-regulated` |
| Crypto Infrastructure | `industry.crypto-infrastructure` | Software | Software Product | Software | Software | `financial-regulated` |
| Crypto Custody | `industry.crypto-custody` | Finance | Financial Experience | Finance | Finance | `financial-regulated` |
| Tokenization | `industry.tokenization` | Finance | Financial Experience | Finance | Finance | `financial-regulated` |
| Digital Securities | `industry.digital-securities` | Finance | Financial Experience | Finance | Finance | `financial-regulated` |
| Decentralized Finance | `industry.decentralized-finance` | Finance | Financial Experience | Finance | Finance | `financial-regulated` |
| Stablecoins | `industry.stablecoins` | Finance | Financial Experience | Finance | Finance | `financial-regulated` |
| Blockchain Analytics | `industry.blockchain-analytics` | Software | Software Product | Software | Software | `standard` |
| Web3 Infrastructure | `industry.web3-infrastructure` | Software | Software Product | Software | Software | `standard` |
| NFTs & Digital Collectibles | `industry.nfts-and-digital-collectibles` | Retail | Commerce | Gaming | Gaming | `platform-trust-safety` |
| Metaverse | `industry.metaverse` | Media | Content & Media | Gaming | Gaming | `platform-trust-safety` |
| Virtual Goods | `industry.virtual-goods` | Media | Content & Media | Gaming | Gaming | `platform-trust-safety` |
| Digital Fashion | `industry.digital-fashion` | Retail | Commerce | Commerce | Commerce | `standard` |
| Spatial Computing | `industry.spatial-computing` | Software | Software Product | Software | Software | `standard` |
| 3D Content | `industry.3d-content` | Software | Software Product | Software | Software | `standard` |
| Animation | `industry.animation` | Media | Content & Media | Media | Media | `standard` |
| Visual Effects | `industry.visual-effects` | Media | Content & Media | Media | Media | `standard` |
| Virtual Production | `industry.virtual-production` | Media | Content & Media | Media | Media | `standard` |
| Post-Production | `industry.post-production` | Media | Content & Media | Media | Media | `standard` |
| Audio Production | `industry.audio-production` | Media | Content & Media | Media | Media | `standard` |
| Music Technology | `industry.music-technology` | Software | Software Product | Media | Media | `standard` |
| Creator Tools | `industry.creator-tools` | Software | Software Product | Media | Media | `platform-trust-safety` |
| Creator Monetization | `industry.creator-monetization` | Media | Content & Media | Media | Media | `platform-trust-safety` |
| Digital Products | `industry.digital-products` | Software | Software Product | Software | Software | `standard` |
| Knowledge Commerce | `industry.knowledge-commerce` | Software | Software Product | Software | Software | `standard` |
| Coaching | `industry.coaching` | Professional | Professional Services | Professional | Professional | `standard` |
| Executive Coaching | `industry.executive-coaching` | Professional | Professional Services | Professional | Professional | `standard` |
| Leadership Training | `industry.leadership-training` | Education | Learning Experience | Education | Education | `education-or-minors` |
| Organizational Development | `industry.organizational-development` | Professional | Professional Services | Professional | Professional | `standard` |
| Change Management | `industry.change-management` | Professional | Professional Services | Professional | Professional | `standard` |
| Digital Transformation | `industry.digital-transformation` | Professional | Professional Services | Professional | Professional | `standard` |
| Innovation Consulting | `industry.innovation-consulting` | Professional | Professional Services | Professional | Professional | `standard` |
| Product Development | `industry.product-development` | Professional | Professional Services | Professional | Professional | `standard` |
| Prototyping | `industry.prototyping` | Professional | Professional Services | Professional | Professional | `standard` |
| User Research | `industry.user-research` | Professional | Professional Services | Professional | Professional | `standard` |
| UX/UI | `industry.ux-ui` | Professional | Professional Services | Professional | Professional | `standard` |
| Graphic Design | `industry.graphic-design` | Professional | Professional Services | Professional | Professional | `standard` |
| Branding | `industry.branding` | Professional | Professional Services | Professional | Professional | `standard` |
| Naming | `industry.naming` | Professional | Professional Services | Professional | Professional | `standard` |
| Packaging Design | `industry.packaging-design` | Professional | Professional Services | Industrial | Industrial | `standard` |
| Industrial Design | `industry.industrial-design` | Professional | Professional Services | Industrial | Industrial | `standard` |
| Architecture | `industry.architecture` | Professional | Professional Services | Professional | Professional | `standard` |
| Urban Planning | `industry.urban-planning` | Professional | Professional Services | Professional | Professional | `standard` |
| Landscape Architecture | `industry.landscape-architecture` | Professional | Professional Services | Professional | Professional | `standard` |
| Interior Architecture | `industry.interior-architecture` | Professional | Professional Services | Professional | Professional | `standard` |
| Engineering Services | `industry.engineering-services` | Professional | Professional Services | Professional | Professional | `standard` |
| Testing Laboratories | `industry.testing-laboratories` | Science | Scientific & Technical | Science | Science | `standard` |
| Calibration | `industry.calibration` | Science | Scientific & Technical | Science | Science | `standard` |
| Metrology | `industry.metrology` | Science | Scientific & Technical | Science | Science | `standard` |
| Certification | `industry.certification` | Professional | Professional Services | Professional | Professional | `standard` |
| Inspection | `industry.inspection` | Science | Scientific & Technical | Science | Science | `standard` |
| Nondestructive Testing | `industry.nondestructive-testing` | Science | Scientific & Technical | Science | Science | `standard` |
| Reliability Engineering | `industry.reliability-engineering` | Professional | Professional Services | Professional | Professional | `standard` |
| Failure Analysis | `industry.failure-analysis` | Science | Scientific & Technical | Science | Science | `standard` |
| Quality Control | `industry.quality-control` | Professional | Professional Services | Professional | Professional | `standard` |
| Lean Manufacturing | `industry.lean-manufacturing` | Manufacturing | Operational B2B | Industrial | Industrial | `physical-safety` |
| Operational Excellence | `industry.operational-excellence` | Professional | Professional Services | Professional | Professional | `standard` |
| Process Improvement | `industry.process-improvement` | Professional | Professional Services | Professional | Professional | `standard` |
| Business Process Management | `industry.business-process-management` | Software | Software Product | Software | Software | `standard` |
| Process Mining | `industry.process-mining` | Software | Software Product | Software | Software | `physical-safety` |
| Enterprise Automation | `industry.enterprise-automation` | Software | Software Product | Software | Software | `standard` |
| Document Automation | `industry.document-automation` | Software | Software Product | Software | Software | `standard` |
| Intelligent Document Processing | `industry.intelligent-document-processing` | Software | Software Product | Software | Software | `standard` |
| Knowledge Automation | `industry.knowledge-automation` | Software | Software Product | Software | Software | `standard` |
| Enterprise AI | `industry.enterprise-ai` | Ai | Software Product | Ai | Ai | `automated-decisioning` |
| AI Agents | `industry.ai-agents` | Ai | Software Product | Ai | Ai | `automated-decisioning` |
| Robotic Process Automation | `industry.robotic-process-automation` | Software | Software Product | Industrial | Industrial | `standard` |
| Physical Robotics | `industry.physical-robotics` | Manufacturing | Operational B2B | Industrial | Industrial | `physical-safety` |
| Humanoid Robotics | `industry.humanoid-robotics` | Manufacturing | Operational B2B | Industrial | Industrial | `physical-safety` |
| Warehouse Robotics | `industry.warehouse-robotics` | Manufacturing | Operational B2B | Logistics | Logistics | `physical-safety` |
| Agricultural Robotics | `industry.agricultural-robotics` | Manufacturing | Operational B2B | Agriculture | Agriculture | `physical-safety` |
| Medical Robotics | `industry.medical-robotics` | Manufacturing | Operational B2B | Healthcare | Healthcare | `health-sensitive`, `physical-safety` |
| Surgical Robotics | `industry.surgical-robotics` | Manufacturing | Operational B2B | Industrial | Industrial | `physical-safety` |
| Service Robotics | `industry.service-robotics` | Manufacturing | Operational B2B | Industrial | Industrial | `physical-safety` |
| Cleaning Robots | `industry.cleaning-robots` | Manufacturing | Operational B2B | Industrial | Industrial | `physical-safety` |
| Delivery Robots | `industry.delivery-robots` | Manufacturing | Operational B2B | Logistics | Logistics | `physical-safety`, `location-data` |
| Autonomous Drones | `industry.autonomous-drones` | Manufacturing | Operational B2B | Industrial | Industrial | `physical-safety` |
| Autonomous Maritime | `industry.autonomous-maritime` | Manufacturing | Operational B2B | Industrial | Industrial | `physical-safety` |
| Underwater Robotics | `industry.underwater-robotics` | Science | Scientific & Technical | Industrial | Industrial | `physical-safety` |
| Ocean Robotics | `industry.ocean-robotics` | Science | Scientific & Technical | Industrial | Industrial | `physical-safety` |
| Defense Robotics | `industry.defense-robotics` | Manufacturing | Operational B2B | Industrial | Industrial | `critical-infrastructure`, `physical-safety` |
| Public Safety | `industry.public-safety` | Government | Public Service | Government | Government | `public-sector`, `physical-safety` |
| Emergency Communications | `industry.emergency-communications` | Telecom | Operational B2B | Telecom | Telecom | `critical-infrastructure`, `physical-safety` |
| Alerting & Notification | `industry.alerting-and-notification` | Software | Software Product | Software | Software | `standard` |
| Public Warning Systems | `industry.public-warning-systems` | Telecom | Operational B2B | Telecom | Telecom | `critical-infrastructure`, `physical-safety` |
| Emergency Medical Services | `industry.emergency-medical-services` | Health | Healthcare Experience | Healthcare | Healthcare | `health-sensitive` |
| Medical Transport | `industry.medical-transport` | Logistics | Operational B2B | Healthcare | Healthcare | `health-sensitive`, `physical-safety`, `location-data` |
| Air Ambulance | `industry.air-ambulance` | Logistics | Operational B2B | Logistics | Logistics | `physical-safety` |
| Organ Transport | `industry.organ-transport` | Logistics | Operational B2B | Logistics | Logistics | `physical-safety`, `location-data` |
| Healthcare Logistics | `industry.healthcare-logistics` | Logistics | Operational B2B | Healthcare | Healthcare | `health-sensitive`, `physical-safety` |
| Medical Supply Distribution | `industry.medical-supply-distribution` | Logistics | Operational B2B | Healthcare | Healthcare | `health-sensitive`, `physical-safety` |
| Hospital Equipment | `industry.hospital-equipment` | Manufacturing | Operational B2B | Healthcare | Healthcare | `health-sensitive`, `physical-safety` |
| Hospital Management | `industry.hospital-management` | Health | Healthcare Experience | Healthcare | Healthcare | `health-sensitive` |
| Revenue Cycle Management | `industry.revenue-cycle-management` | Health | Healthcare Experience | Healthcare | Healthcare | `health-sensitive` |
| Medical Billing | `industry.medical-billing` | Health | Healthcare Experience | Healthcare | Healthcare | `health-sensitive` |
| Medical Coding | `industry.medical-coding` | Health | Healthcare Experience | Healthcare | Healthcare | `health-sensitive` |
| Health Insurance Administration | `industry.health-insurance-administration` | Finance | Financial Experience | Healthcare | Healthcare | `health-sensitive`, `financial-regulated` |
| Managed Care | `industry.managed-care` | Health | Healthcare Experience | Healthcare | Healthcare | `health-sensitive` |
| Care Management | `industry.care-management` | Health | Healthcare Experience | Healthcare | Healthcare | `health-sensitive` |
| Population Health | `industry.population-health` | Health | Healthcare Experience | Healthcare | Healthcare | `health-sensitive` |
| Preventive Healthcare | `industry.preventive-healthcare` | Health | Healthcare Experience | Healthcare | Healthcare | `health-sensitive` |
| Occupational Health | `industry.occupational-health` | Health | Healthcare Experience | Healthcare | Healthcare | `health-sensitive` |
| Corporate Health | `industry.corporate-health` | Health | Healthcare Experience | Healthcare | Healthcare | `health-sensitive` |
| School Health | `industry.school-health` | Health | Healthcare Experience | Healthcare | Healthcare | `health-sensitive`, `education-or-minors` |
| Public Health | `industry.public-health` | Health | Healthcare Experience | Healthcare | Healthcare | `health-sensitive` |
| Epidemiology | `industry.epidemiology` | Health | Healthcare Experience | Healthcare | Healthcare | `health-sensitive` |
| Biostatistics | `industry.biostatistics` | Science | Scientific & Technical | Healthcare | Healthcare | `health-sensitive` |
| Medical Education | `industry.medical-education` | Education | Learning Experience | Healthcare | Healthcare | `health-sensitive` |
| Nursing Education | `industry.nursing-education` | Education | Learning Experience | Education | Education | `education-or-minors` |
| Allied Health Education | `industry.allied-health-education` | Education | Learning Experience | Healthcare | Healthcare | `health-sensitive` |
| Vocational Training | `industry.vocational-training` | Education | Learning Experience | Education | Education | `education-or-minors` |
| Apprenticeships | `industry.apprenticeships` | Education | Learning Experience | Education | Education | `education-or-minors` |
| Workforce Development | `industry.workforce-development` | Education | Learning Experience | Education | Education | `education-or-minors` |
| Adult Education | `industry.adult-education` | Education | Learning Experience | Education | Education | `education-or-minors`, `age-restricted` |
| Language Learning | `industry.language-learning` | Education | Learning Experience | Education | Education | `education-or-minors` |
| Tutoring | `industry.tutoring` | Education | Learning Experience | Education | Education | `education-or-minors` |
| Test Preparation | `industry.test-preparation` | Education | Learning Experience | Education | Education | `education-or-minors` |
| Certification Training | `industry.certification-training` | Education | Learning Experience | Education | Education | `education-or-minors` |
| Corporate Learning | `industry.corporate-learning` | Education | Learning Experience | Education | Education | `education-or-minors` |
| Learning Management Systems | `industry.learning-management-systems` | Software | Software Product | Education | Education | `education-or-minors` |
| Student Information Systems | `industry.student-information-systems` | Software | Software Product | Education | Education | `education-or-minors` |
| School Management | `industry.school-management` | Education | Learning Experience | Education | Education | `education-or-minors` |
| Higher Education Technology | `industry.higher-education-technology` | Software | Software Product | Education | Education | `education-or-minors` |
| Admissions Technology | `industry.admissions-technology` | Software | Software Product | Education | Education | `education-or-minors` |
| Education Finance | `industry.education-finance` | Finance | Financial Experience | Finance | Finance | `financial-regulated` |
| Student Loans | `industry.student-loans` | Finance | Financial Experience | Education | Education | `education-or-minors` |
| Scholarships | `industry.scholarships` | Education | Learning Experience | Education | Education | `education-or-minors` |
| Research Funding | `industry.research-funding` | Nonprofit | Nonprofit & Community | Nonprofit | Nonprofit | `standard` |
| Grant Management | `industry.grant-management` | Nonprofit | Nonprofit & Community | Nonprofit | Nonprofit | `standard` |
| Philanthropy | `industry.philanthropy` | Nonprofit | Nonprofit & Community | Nonprofit | Nonprofit | `standard` |
| Donor-Advised Funds | `industry.donor-advised-funds` | Finance | Financial Experience | Finance | Finance | `financial-regulated` |
| Impact Investing | `industry.impact-investing` | Finance | Financial Experience | Finance | Finance | `financial-regulated` |
| Social Enterprise | `industry.social-enterprise` | Nonprofit | Nonprofit & Community | Nonprofit | Nonprofit | `standard` |
| Cooperatives | `industry.cooperatives` | Nonprofit | Nonprofit & Community | Nonprofit | Nonprofit | `standard` |
| Credit Unions | `industry.credit-unions` | Finance | Financial Experience | Finance | Finance | `financial-regulated` |
| Mutual Insurance | `industry.mutual-insurance` | Finance | Financial Experience | Finance | Finance | `financial-regulated` |
| Association Management | `industry.association-management` | Nonprofit | Nonprofit & Community | Nonprofit | Nonprofit | `standard` |
| Membership Organizations | `industry.membership-organizations` | Nonprofit | Nonprofit & Community | Nonprofit | Nonprofit | `standard` |
| Clubs | `industry.clubs` | Hospitality | Booking & Guest | Hospitality | Hospitality | `standard` |
| Country Clubs | `industry.country-clubs` | Hospitality | Booking & Guest | Hospitality | Hospitality | `standard` |
| Private Membership Clubs | `industry.private-membership-clubs` | Hospitality | Booking & Guest | Hospitality | Hospitality | `standard` |
| Coworking Clubs | `industry.coworking-clubs` | Hospitality | Booking & Guest | Hospitality | Hospitality | `standard` |

# Control Plane Hooks
<!-- id: profile-matrix.control-plane-hooks -->

When this module is active, use `CONTROL_INDEX.md` to retrieve only the capability sections relevant to the current decision. Applicable capabilities include:

- **Audience resolution** — `controls/02-project-intake-and-requirement-resolution.md` (BQ-0061–BQ-0065)
- **Duplicate-subindustry disambiguation** — `controls/03-industry-taxonomy-and-business-model-classification.md` (BQ-0086–BQ-0090)
- **Multi-industry businesses** — `controls/03-industry-taxonomy-and-business-model-classification.md` (BQ-0091–BQ-0095)
- **Local-service detection** — `controls/03-industry-taxonomy-and-business-model-classification.md` (BQ-0096–BQ-0100)
- **B2B-vs-B2C distinction** — `controls/03-industry-taxonomy-and-business-model-classification.md` (BQ-0101–BQ-0105)
- **Regulated-industry detection** — `controls/03-industry-taxonomy-and-business-model-classification.md` (BQ-0106–BQ-0110)
- **Ambiguous-classification fallback** — `controls/03-industry-taxonomy-and-business-model-classification.md` (BQ-0111–BQ-0115)
- **Independent-profile dimensions** — `controls/04-semantic-profiles-risk-and-context-overlays.md` (BQ-0121–BQ-0125)
- **Risk-overlay composition** — `controls/04-semantic-profiles-risk-and-context-overlays.md` (BQ-0126–BQ-0130)
- **Profile confidence scores** — `controls/04-semantic-profiles-risk-and-context-overlays.md` (BQ-0131–BQ-0135)
- **Mixed-model businesses** — `controls/04-semantic-profiles-risk-and-context-overlays.md` (BQ-0136–BQ-0140)
- **Audience-specific design profile** — `controls/04-semantic-profiles-risk-and-context-overlays.md` (BQ-0141–BQ-0145)
- **Profile inheritance limits** — `controls/04-semantic-profiles-risk-and-context-overlays.md` (BQ-0146–BQ-0150)
- **Profile override provenance** — `controls/04-semantic-profiles-risk-and-context-overlays.md` (BQ-0151–BQ-0155)
- **Risk-trigger re-evaluation** — `controls/04-semantic-profiles-risk-and-context-overlays.md` (BQ-0156–BQ-0160)

These hooks are routing pointers, not permission to preload the listed shards. Evidence Gates control pass/fail claims.
