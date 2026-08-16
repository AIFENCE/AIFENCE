<!--
Pack-Version: 4.0.0
Schema-Version: 3
Module: ARTIFACT_CONTRACT
Contract: Native / Mobile App
Module-Version: 1
Control-Plane-Revision: 1.8.8
Last-Updated: 2026-08-10
-->
# Native / Mobile App Production Contract
<!-- id: contract.artifact.native-mobile-app -->

## Platform & Device Contract
Resolve iOS/Android scope, navigation model, system conventions, permissions, offline/network behavior, keyboard/input, safe areas, orientation, deep links, and device capabilities actually required.

## User Jobs & States
Compile each critical mobile task through entry, loading, success, empty, error, permission-denied, interrupted, background/resume, and recovery states where applicable.

## Native Interaction Contract
Prefer platform-appropriate navigation, touch targets, gestures only when discoverable, haptics only when meaningful, and accessible system semantics. Do not make a web page merely fit inside a phone frame.

## Data & Backend Truth
Distinguish local/sample data from real services, authentication, payments, notifications, location, health, camera, and other privileged capabilities. Never imply a working backend or permission grant that does not exist.

## Evidence
Verify at representative compact and large phone sizes, keyboard-visible states, permissions, rotation where supported, interruption/recovery, accessibility, runtime integrity, and platform-specific interaction fidelity.
