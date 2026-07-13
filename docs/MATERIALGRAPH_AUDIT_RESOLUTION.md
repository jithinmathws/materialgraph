# MaterialGraph Architecture & Implementation Audit Resolution

Version: 1.0
Last Updated: 2026-07-13

---

## Purpose

This document tracks the lifecycle of every finding identified during
MaterialGraph architecture and implementation audits.

Each finding records:

- root cause
- affected components
- remediation
- verification
- scientific impact
- regression testing
- lessons learned

Only findings that complete implementation, testing, and scientific
verification are marked as Resolved.

---

# Finding Status Legend

| Status | Meaning |
|----------|---------|
| Open | Investigation not started |
| In Progress | Remediation underway |
| Verification | Code completed, verification pending |
| Resolved | Fully implemented and verified |
| Deferred | Intentionally postponed |
| Accepted Risk | Known limitation accepted |
| Rejected | Audit finding determined to be invalid |

---

# MG-AUD-001

Title

Materials Project composition fractions discarded on import.

Severity

High

Status

✅ Resolved

Resolution Version

v1.9.7

Affected Components

- MaterialsProjectService
- MaterialImportService
- MaterialCompositionService
- MaterialCriticalityService
- MaterialQualityService
- MaterialElement
- Materials Project import pipeline

Root Cause

Importer discarded normalized composition fractions and persisted
fraction = 1.0 for every element.

Scientific Impact

Stoichiometric weighting was lost.

Materials with repeated elements were treated as equal-weight mixtures.

Resolution

✓ MaterialCandidate preserves normalized composition.

✓ Importer persists normalized fractions.

✓ MaterialCompositionService introduced as canonical implementation.

✓ Existing Materials Project records backfilled.

Regression Verification

✓ Import tests

✓ Composition service tests

✓ Criticality tests

✓ Quality tests

✓ Full test suite

✓ LiFePO4 → Na/phosphate reference workflow

Scientific Changes

LiFePO4 Criticality

36.5 → 32.0

Scientific Usefulness

94.95 → 95.65

Reason

Correct stoichiometric weighting.

Breaking API

No

Database Migration

MaterialElement fractions updated using structured Materials Project
composition.

Lessons Learned

Structured scientific data should always take precedence over inferred
representations.

Related Scientific Principles

Principle 10

Related ADR

ADR-002

---

# MG-AUD-002

Title

Unknown criticality evidence becomes favorable zero.

Severity

High

Status

✅ Resolved

Resolution Version

v1.9.8

Affected Components

- MaterialCriticalityService
- MaterialQualityService
- DiscoveryPathRankingService
- ScientificPathwayService
- RecommendationService
- SimilarityService
- Criticality response model
- Quality scoring pipeline

Root Cause

Unknown criticality evidence could be represented as a favorable numeric
value during downstream processing instead of remaining unknown.

Scientific Impact

Materials with incomplete criticality evidence could receive an
artificially favorable quality contribution.

Resolution

✓ Unknown criticality now returns null instead of numeric zero.

✓ Criticality aggregation excludes unknown evidence from weighted
calculations.

✓ Evidence coverage metadata added.

✓ Unknown elements are explicitly reported.

✓ Quality scoring no longer awards a criticality bonus when evidence is
unknown.

✓ Single and bulk criticality responses are consistent.

Regression Verification

✓ Criticality service tests

✓ Material quality tests

✓ Similarity tests

✓ Recommendation tests

✓ Path ranking tests

✓ Scientific pathway tests

✓ Full regression suite

✓ LiFePO4 → Na/phosphate reference workflow

Scientific Changes

LiFePO4 Criticality

No change (32.0)

Scientific Usefulness

No change (95.65)

Reason

The remediation only affects incomplete or unknown criticality evidence.
Fully evidenced materials remain unchanged.

Breaking API

No

Database Migration

No

Lessons Learned

Unknown scientific evidence must remain unknown. Missing evidence should
never be converted into favorable evidence during downstream scoring.

Related Scientific Principles

Principle 11

Related ADR

ADR-002