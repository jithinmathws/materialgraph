# MaterialGraph Scientific Change History

---

## v1.9.7

Summary

Composition weighting remediation.

Reason

Resolved MG-AUD-001.

Affected Components

Material import

Criticality

Quality

Discovery

Changes

LiFePO4 Criticality

36.5 → 32.0

Scientific Usefulness

94.95 → 95.65

Reason

Correct stoichiometric weighting.

Breaking API

No

Database Backfill

Yes

Regression Status

Passed

---

## v1.9.8

Summary

Criticality evidence remediation.

Reason

Resolved MG-AUD-002.

Affected Components

Criticality

Quality

Scientific Pathway

Similarity

Recommendation

Changes

Unknown Criticality

null remains unknown

Quality Contribution

Unknown criticality receives no favorable quality bonus.

Scientific Changes

LiFePO4 Criticality

No change (32.0)

Scientific Usefulness

No change (95.65)

Reason

Only incomplete criticality evidence behavior changed.

Breaking API

No

Database Backfill

No

Regression Status

Passed

---

## v1.9.9

Summary

Risk evidence remediation for candidate screening.

Reason

Resolved MG-AUD-003.

Affected Components

Candidate Screening

Candidate Comparison

Material Risk

Changes

Unknown Risk

null remains unknown throughout screening and comparison.

Risk Evidence

Evidence metadata exposed in candidate screening responses.

Performance

Bulk risk loading replaces per-material legacy risk lookups.

Scientific Changes

LiFePO4 Risk

No change (2.833)

LiFePO4 Criticality

No change (32.0)

Scientific Usefulness

No change (95.65)

Reason

Only unknown risk evidence handling changed.

Breaking API

No

Database Backfill

No

Regression Status

Passed

---

## v1.9.10

Summary

Exact element membership remediation.

Reason

Resolved MG-AUD-004.

Affected Components

Discovery Candidate Scoring

Discovery Chain Search

Discovery Warning Generation

Research Objective Exploration

Chemical Formula Membership

Changes

Element Membership

Exact chemical element membership replaces raw formula substring matching.

Candidate Scoring

Preferred and avoided element scoring now uses structured element
membership instead of string matching.

Discovery Chains

Candidate expansion now uses exact element membership during preferred
element filtering.

Research Objective Exploration

Scoring, researcher reasons, and warnings now use exact element
membership.

Warnings

Researcher-facing warnings no longer rely on substring matching.

Scientific Changes

LiFePO4 Criticality

No change (32.0)

LiFePO4 Risk

No change (2.833)

Scientific Usefulness

No change (95.65)

Reason

The Li/Na phosphate reference workflow already used unambiguous element
symbols. The remediation corrects ambiguous element symbol handling
(e.g. N vs Na, S vs Si, C vs Ca) without changing valid scientific
results.

Performance

Structured MaterialElement membership reused where already available.

Formula parsing only used where structured membership is unavailable.

Breaking API

No

Database Backfill

No

Regression Status

Passed

Reference Workflow

Verified

LiFePO4 → Na phosphate objective unchanged.

---

## v1.9.11

Summary

Framework preservation semantic qualification.

Reason

Resolved MG-AUD-005.

Affected Components

Discovery Transition Validation

Substitution Path Analysis

Discovery Chains

Scientific Pathway Analysis

Research Evidence Intelligence

Comparative Research Intelligence

Research Objective Exploration

Changes

Scientific Semantics

Element overlap is now represented explicitly as shared-element continuity.

Transition Metadata

Introduced canonical shared_elements metadata while preserving
preserved_framework as a backward-compatible alias.

Scientific Provenance

Added:

- preservation_basis = "element_overlap"
- structural_preservation_validated = false

Research Evidence

Research-facing explanations now distinguish deterministic
shared-element continuity from experimentally validated structural
preservation.

Scientific Pathway Analysis

Scientific facts now expose explicit preservation provenance and
qualified terminology.

Comparative Intelligence

Comparative element highlights preserve API compatibility while exposing
semantic metadata describing the underlying evidence.

Scientific Changes

LiFePO4 Criticality

No change (32.0)

LiFePO4 Risk

No change (2.833)

Scientific Usefulness

No change (95.65)

Reason

This remediation improves scientific semantics and evidence provenance
without changing deterministic scoring or pathway ranking.

Performance

No measurable performance impact.

Breaking API

No

Database Backfill

No

Regression Status

Passed

Reference Workflow

Verified

LiFePO4 → Na phosphate objective unchanged.

---

## v1.9.12

Summary

Discovery score provenance remediation.

Reason

Resolved MG-AUD-006.

Affected Components

Discovery Candidate Scoring

Discovery Candidate Merging

Discovery Score Explainability

Changes

Score Provenance

Discovery score breakdowns now represent the score provenance that
produced the final discovery score instead of accumulating competing
source scores.

Candidate Merging

Candidate merging now preserves the winning score provenance while
continuing to aggregate contextual discovery evidence such as discovery
paths, explanations, and substitution paths.

Explainability

Discovery score arithmetic is now internally consistent.

For every candidate:

sum(score_breakdown) == discovery_score

Scientific Changes

LiFePO4 Criticality

No change (32.0)

LiFePO4 Risk

No change (2.833)

Scientific Usefulness

No change (95.65)

Reason

This remediation corrects explainability provenance only.

Deterministic scientific scoring and candidate ranking remain unchanged.

Performance

No measurable performance impact.

Breaking API

No

Database Backfill

No

Regression Status

Passed

Reference Workflow

Verified

LiFePO4 → Na phosphate objective unchanged.

---

## v1.9.13

Summary

Discovery source-diversity provenance remediation.

Reason

Resolved MG-AUD-007.

Affected Components

Discovery Candidate Scoring

Discovery Candidate Merging

Discovery Source Diversity

Discovery Score Explainability

Changes

Source Diversity Semantics

Source diversity bonuses are now based on distinct discovery source types
rather than repeated candidate encounters.

Distinct Source Tracking

Candidate merging tracks unique contributing source types internally.

Repeated encounters from the same source no longer increase the source
diversity bonus.

Diversity Bonus

The current deterministic bonus is:

- one distinct source: 0
- two distinct sources: 10
- three distinct sources: 20

Score Provenance

Base discovery score provenance is tracked separately from the accumulated
source diversity bonus.

This prevents an existing aggregate discovery score from being reused as a
base score and receiving the diversity bonus a second time.

Candidate Merging

The winning base score and its score breakdown are preserved while contextual
discovery paths, explanations, and substitution paths continue to aggregate
across candidate encounters.

Internal Provenance

Internal source and base-score provenance fields are removed before candidates
are returned through the public API.

Scientific Changes

LiFePO4 Criticality

No change (32.0)

LiFePO4 Risk

No change (2.833)

Scientific Usefulness

No change (95.65)

Reason

This remediation corrects discovery source-diversity accounting and score
provenance without modifying scientific pathway scoring.

The LiFePO4 → Na/phosphate reference workflow remains unchanged.

Performance

No measurable performance impact.

No additional database queries introduced.

Breaking API

No

Database Backfill

No

Regression Status

Passed

Reference Workflow

Verified

LiFePO4 → Na phosphate objective unchanged.

Scientific usefulness remains 95.65.

