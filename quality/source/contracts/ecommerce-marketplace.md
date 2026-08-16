<!--
Pack-Version: 4.0.0
Schema-Version: 3
Module: ARTIFACT_CONTRACT
Contract: E-Commerce Marketplace
Module-Version: 2
Control-Plane-Revision: 1.8.8
Last-Updated: 2026-08-09
-->
# E-Commerce / Marketplace Production Contract
<!-- id: contract.artifact.ecommerce-marketplace -->

## User Jobs
<!-- id: contract.artifact.ecommerce-marketplace.user-jobs -->
Users should discover suitable products/offers, compare decision-critical details, understand price/availability/fulfillment truthfully, manage selection/cart, and complete or intentionally simulate checkout with clear expectations.

## Discovery Contract
<!-- id: contract.artifact.ecommerce-marketplace.discovery -->
Resolve categories, search, filtering, sorting, selected-filter state, result counts, no-results recovery, product-card information priority, and mobile filter behavior when applicable.

## Product / Offer Contract
<!-- id: contract.artifact.ecommerce-marketplace.product -->
Resolve media, title, variants/options, price semantics, availability, supplied fulfillment/shipping/returns facts, quantity, primary purchase action, supporting details, and trust information.

## Cart / Checkout Contract
<!-- id: contract.artifact.ecommerce-marketplace.checkout -->
Cart, validation, totals, delivery/contact fields, payment behavior, confirmation, errors, unavailable items, and front-end-only/backend truth must be explicit.

## Responsive & Accessibility
<!-- id: contract.artifact.ecommerce-marketplace.responsive-accessibility -->
Filtering, product media, variant selection, sticky purchase actions, cart summaries, validation, keyboard behavior, and touch targets must adapt intentionally.

## Evidence
<!-- id: contract.artifact.ecommerce-marketplace.evidence -->
Verify discovery→detail→cart/checkout, state behavior, totals/data truth, mobile adaptation, form accessibility, runtime integrity, and visual craft.


## Narrow-Screen Commerce Contract
<!-- id: contract.artifact.ecommerce-marketplace.narrow-screen-commerce -->
Use `RESPONSIVE_COMPOSITION.md` for filter sheets, variant selection, sticky purchase actions, cart/checkout summaries, validation, and keyboard/mobile completion at 320/390 px.

## Acceptance Profile
<!-- id: contract.artifact.ecommerce-marketplace.acceptance -->
Use `quality-floors.profile.ecommerce`. Truthfulness and implementation correctness cannot be averaged away.
