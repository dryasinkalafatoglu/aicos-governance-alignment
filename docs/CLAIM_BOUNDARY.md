# AICOS Governance Alignment — Claim Boundary

This document defines the claim boundary for artifacts published in this repository.

## Core Rule

`ClaimStrength <= EvidenceStrength`

No claim may exceed the strength of the evidence that directly supports it.

## Assurance States

The following states must remain distinct:

* Designed
* Implemented
* Tested
* Externally Reproduced
* Independently Evaluated
* Independently Validated
* Production Operational

These states are not interchangeable.

## Explicit Distinctions

`Prediction != Decision`

`Replayability != Evidence`

`Simulation != Proof`

`Testing != Independent Validation`

`External Reproduction != Independent Validation`

`Deterministic Receipt != Evidence Truth`

`Evaluator Identity Disclosure != Independence Proof`

`Production Readiness != Production Operation`

## Current Reference Status

AICOS CORE MPK v0.2-RC1 is currently a frozen implementation candidate with local executable evidence for its declared synthetic scope.

Current status:

* Implementation: established for the declared candidate scope
* Local execution: established
* External reproduction: not established
* External technical review: not established
* Independent validation: not established
* Production operation: not established

## Fail-Closed Principle

Unknown, structurally invalid, incomplete, or unverified evidence must never be silently promoted into a stronger assurance state.

Any future change to this claim boundary must be versioned and supported by explicit evidence.
