# Changelog

All notable changes to the framework. Versioning rules and compatibility notes: `docs/VERSIONING.md`.
This project follows [Semantic Versioning](https://semver.org/) as defined there.

## [1.1.0] - 2026-10-08

First standalone release; a minor, backward-compatible upgrade of the 1.0.0 baseline.

### Added
- Three specialist review agents: `database-architect` (design review before implementation, only when
  database structures change), `backend-reviewer`, `frontend-reviewer` (engineering review **and** design
  conformance).
- Standard Review Report and severity rules (HIGH blocks progression and commit; MEDIUM must be resolved
  before commit unless the authorised human explicitly accepts an exception; LOW may be fixed or logged as
  debt); PASS WITH CHANGES does not by itself authorise commit; reviewers must not certify tests they did
  not execute; senior-level reviewer expertise applied against the project's selected readability profile.
- The 20-step vertical-slice workflow, with review-and-correction loops per layer and "all mandatory
  reviews before commit".
- "Independent Judgment — Evidence Over Agreement" expanded to seven points and applied to every agent.
- Reusable bootstrap and adoption material: templates for project-specific configuration, prompts to
  bootstrap a new project, adopt the framework in an existing project and upgrade between versions, a
  versioning/compatibility/update/rollback guide, and a validator (`scripts/validate.py`).

### Changed
- Design conformance moved from a separate mandatory gate into the `frontend-reviewer`; the `design` agent
  keeps consultation, interpretation and handoff and remains the authoritative description of the
  conformance method.
- The general `reviewer` is now cross-cutting/integration only.
- Project criticality and code-readability profiles are configuration chosen by each project (templates),
  not fixed in the policy.

### Unchanged
- Independent `qa`; `security` (risk-based); human/Product Owner acceptance and deployment-authorisation
  gates; forward-only adoption.

## [1.0.0] - 2026-10-07

Baseline, numbered retroactively (no version was recorded when it was first adopted). Frontend, Backend and
Reviewer agents alongside the Design, QA, Security and DevOps agents; Definition of Ready/Done;
change-risk classification; technology and dependency governance; ADR/RFC process; migration,
observability and reliability guidance; technical-debt register; project status log; forward-only
adoption.
