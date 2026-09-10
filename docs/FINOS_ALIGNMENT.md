# AICOS Governance Alignment — FINOS AIGF Candidate Mapping

## Purpose

This document records a bounded, candidate-level mapping between the AICOS governance implementation experiment and the FINOS AI Governance Framework (AIGF).

It does not claim certification, formal conformity, FINOS endorsement, or complete framework coverage.

The governing rule is:

`ClaimStrength <= EvidenceStrength`

## FINOS AIGF Context

The FINOS AI Governance Framework is intended to support the onboarding, development, and operation of AI-based solutions within financial services organisations in a safe, trustworthy, and compliant manner.

Its practical approach includes:

* focusing on bounded use cases;
* leveraging existing technology-risk frameworks;
* applying threat modelling;
* identifying mitigations and controls;
* developing practical governance mechanisms for financial services.

AICOS uses these concepts only as alignment targets where supported by explicit evidence.

## Candidate Alignment Areas

| FINOS AIGF Direction              | AICOS Candidate Mechanism               | Current Evidence Status                                  |
| --------------------------------- | --------------------------------------- | -------------------------------------------------------- |
| Bounded use-case governance       | Synthetic MPK fixture scope             | Implemented / locally executed                           |
| Threat and failure identification | Adversarial fixture set                 | Implemented / locally executed                           |
| Governance controls               | Mandatory gate and authority checks     | Implemented / locally tested                             |
| Control failure handling          | Fail-closed reducer semantics           | Implemented / locally tested                             |
| Evidence traceability             | SHA-256 artifact bindings               | Implemented / locally tested                             |
| Reproducibility                   | Clean-room reproduction contract        | Implemented / first-party locally re-executed            |
| Governance decision trace         | Deterministic Decision Receipt          | Implemented / locally tested                             |
| Falsifiability                    | Evaluator-originated challenge contract | Tooling implemented / external execution not established |
| External review                   | Frozen evaluator handoff                | Prepared / external result not established               |
| Independent validation            | Separate assurance state                | Not established                                          |
| Production operation              | Separate assurance state                | Not established                                          |

## Governance Semantics

AICOS currently enforces several distinctions relevant to practical governance:

`Prediction != Decision`

`Replayability != Evidence`

`Simulation != Proof`

`Testing != Independent Validation`

`External Reproduction != Independent Validation`

`Deterministic Receipt != Evidence Truth`

These distinctions are intended to prevent technical artifacts from being promoted into stronger assurance claims without supporting evidence.

## Threat-Modelling Relationship

The current MPK candidate uses synthetic adversarial cases to exercise governance failures such as:

* evidence tampering;
* policy mutation;
* use of post-decision information;
* authority revocation;
* missing evidence;
* state rollback;
* state forks;
* trust-principal collapse;
* explanation divergence;
* epistemic unknowns;
* hard-failure masking.

These fixtures are bounded implementation tests.

They are not equivalent to a complete FINOS threat model and should not be represented as such.

## Human Authority

The current governance model preserves human-final authority and separates verification from decision authority.

A technically valid artifact does not automatically imply permission to act.

Verification state and decision authority state are therefore treated as separate dimensions.

## External Reproduction Proposal

A related vendor-neutral proposal has been opened in the FINOS AI Governance Framework repository:

**FINOS AIGF Issue #382 — Reproducible Governance Decision Evidence and Falsification Fixture**

https://github.com/finos/ai-governance-framework/issues/382

The proposal asks whether a frozen governance evidence package can be:

1. identity-verified;
2. reproduced by another party;
3. challenged using an evaluator-originated mutation;
4. evaluated against a preregistered safety property;
5. reported using bounded assurance claims.

AICOS CORE MPK v0.2-RC1 is only an initial implementation experiment for this pattern.

## Current Claim Boundary

The following claims are currently permitted:

* implementation candidate exists;
* declared synthetic behavior has local executable evidence;
* deterministic receipt and recomputation tooling have local executable tests;
* external evaluator handoff has been prepared.

The following claims are not currently established:

* FINOS conformity;
* FINOS endorsement;
* independent validation;
* independent verifier implementation;
* regulatory certification;
* production readiness;
* production operation;
* predictive validity;
* business efficacy.

## Change Control

Any future FINOS alignment claim must be supported by:

1. a specific FINOS source or control reference;
2. explicit mapping rationale;
3. implementation evidence where applicable;
4. test or reproduction evidence;
5. conflict and duplication review;
6. versioned promotion into this document.

Alignment by terminology alone is insufficient.

## Contribution Discipline

Where material is contributed upstream to FINOS, FINOS contribution requirements — including DCO sign-off requirements — must be followed.

This repository remains an independent implementation experiment unless and until specific material is accepted through the relevant FINOS governance process.
