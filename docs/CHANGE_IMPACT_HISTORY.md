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

---

## v1.9.14

Summary

Risk-quality bonus evidence-completeness remediation.

Reason

Resolved MG-AUD-008.

Affected Components

- Material Risk Evidence
- Material Quality Scoring
- Discovery Path Ranking
- Scientific Pathway Analysis
- Research Evidence Intelligence
- Comparative Research Intelligence
- Endpoint-Sensitive Research Ranking
- K-Best and K-Shortest Path Ranking
- Weighted Shortest Path
- Discovery Graph Node Quality
- Graph Analytics and Community Importance

Changes

Favorable low-risk and medium-risk quality bonuses now require complete material-element risk evidence.

A material with a calculable risk score but incomplete material-element coverage continues to expose the observed risk score and evidence metadata, but partial evidence no longer qualifies for a favorable risk-quality bonus.

Risk aggregation semantics are unchanged. `risk_profile_coverage` continues to represent material-element coverage rather than composition-weighted coverage or risk-profile dimension completeness. Risk-dimension completeness remains a separate audit concern.

Characterization tests confirmed the pre-remediation defect and the corrected behavior. Scalar and bulk risk evidence semantics remain aligned.

Scientific Changes

LiFePO4 Risk

No change (2.833)

LiFePO4 Risk Evidence Coverage

1.0 (4 of 4 constituent elements covered)

Scientific Usefulness

No change (95.65)

Material Quality Path Contribution

No change (14.65)

Reason

The LiFePO4 → Na/phosphate reference materials checked (material IDs 5–10) all have complete material-element risk evidence (`risk_profile_coverage = 1.0`, `risk_evidence_complete = true`, and no unknown risk elements). The reference workflow therefore remains eligible for the existing favorable risk-quality contribution.

Downstream Impact Discovered During Investigation

Corrected material quality can propagate to scientific usefulness, pathway ranking, scientific pathway quality summaries and confidence explanations, research evidence readiness, comparative explanations, endpoint-sensitive tie-breaking, K-best and equal-hop K-shortest ordering, weighted shortest-path costs, discovery graph node quality, and graph community importance.

No downstream scoring weights were changed; these consumers inherit corrected MaterialQualityService values.

Additional Audit Discoveries

- During MG-AUD-008 dependency inspection, raw formula substring matching was discovered in DiscoveryGraphAnalyticsService community-summary element counting. This was tracked independently as MG-AUD-049 and remediated in the same v1.9.14 development cycle.
- `risk_evidence_complete` represents complete coverage across constituent material elements, not completeness across every risk-profile dimension. Risk-dimension coverage should remain a separate audit finding or refinement.
- Composition-weighted risk coverage was considered but intentionally not introduced because it would constitute a new scientific policy rather than a minimal remediation.

Performance

No additional database queries introduced.

Breaking API

No

Database Backfill

No

Regression Status

- Focused MaterialQualityService tests passed.
- Focused MaterialRiskService characterization tests passed.
- LiFePO4 → Na/phosphate reference workflow verified.
- Full regression suite passed.

---

## v1.9.15

Summary

Multi-element research objective remediation.

Reason

Resolved MG-AUD-009.

Affected Components

- ResearchObjectiveService
- DiscoveryPathRankingService
- ScientificPathwayAnalysisService
- ResearchObjectiveExplorationService
- Scientific pathway response schemas

Changes

Multi-element Objective Support

Research objectives now support multiple avoided and preferred elements throughout deterministic discovery, pathway ranking, and scientific pathway analysis.

Objective Alignment

Objective-alignment scoring now evaluates every requested avoided and preferred element instead of considering only the first element from each objective list.

Scientific Explainability

Scientific pathway responses now expose structured objective satisfaction metadata including:

- requested objective elements
- matched objective elements
- unmatched objective elements
- objective coverage percentages
- overall completion status

Scientific Changes

LiFePO4 Criticality

No change (32.0)

LiFePO4 Risk

No change (2.833)

Scientific Usefulness

Single-element objective

95.65

Multi-element objective (Li, Co → Na, K)

83.15

Reason

Single-element behaviour is preserved.

Multi-element objectives now receive proportional objective-alignment scoring based on the deterministic transition evidence available across the complete pathway.

Performance

No measurable performance impact.

No additional database queries introduced.

Breaking API

No

The new `objective_satisfaction` response object is additive.

Database Backfill

No

Regression Status

Passed

Reference Workflow

Verified

- Single-element objective unchanged.
- Multi-element objective propagation verified.
- Multi-element objective scoring verified.
- Objective explainability verified.
- Full regression suite passed.

Additional Audit Discovery

During implementation of MG-AUD-009, an additional explainability opportunity was identified.

Current objective satisfaction describes deterministic path-wide objective fulfillment.

---

## v1.9.16

Summary

Endpoint-specific research objective evaluation.

Reason

Resolved MG-AUD-050.

Affected Components

- ScientificPathwayAnalysisService
- ResearchObjectiveExplorationService
- Scientific pathway response schemas

Changes

Endpoint Objective Evaluation

Scientific pathway responses now distinguish deterministic path-wide objective
satisfaction from endpoint-specific objective satisfaction.

Endpoint Explainability

Added endpoint-specific objective evaluation including:

- endpoint_matched_avoid_elements
- endpoint_unmatched_avoid_elements
- endpoint_matched_prefer_elements
- endpoint_unmatched_prefer_elements
- endpoint_avoid_coverage
- endpoint_prefer_coverage
- endpoint_overall_coverage
- endpoint_status
- endpoint_interpretation

Scientific Semantics

Path-wide objective satisfaction continues to describe deterministic removal
and introduction events occurring anywhere along the pathway.

Endpoint-specific objective satisfaction evaluates only the final endpoint
material composition.

Scoring

No deterministic scoring changes.

No objective-alignment changes.

No scientific usefulness changes.

No pathway ranking changes.

Scientific Changes

LiFePO4 Criticality

No change (32.0)

LiFePO4 Risk

No change (2.833)

Scientific Usefulness

No change (95.65)

Reason

This remediation improves researcher explainability by distinguishing
path-wide transition evidence from endpoint material composition while
preserving all deterministic scientific scoring.

Performance

No measurable performance impact.

No additional database queries introduced.

Breaking API

No

Endpoint objective fields are additive.

Existing path-wide objective fields remain unchanged.

Database Backfill

No

Regression Status

Passed

Reference Workflow

Verified

- Path-wide objective satisfaction verified.
- Endpoint-specific objective satisfaction verified.
- Characterization tests passed.
- Full regression suite passed.

---

## v1.9.17

Summary

Stable pathway identity and tie-aware comparative research remediation.

Reason

Resolved MG-AUD-051.

Affected Components

- ScientificPathwayAnalysisService
- ComparativeResearchIntelligenceService
- ResearchObjectiveExplorationService
- Scientific pathway response schemas
- Comparative research response schemas

Changes

Stable Pathway Identity

Every scientific pathway now exposes:

- pathway_id
- position
- rank

Ranking Semantics

Competition ranking is preserved while pathway identity is separated from ranking.

Comparative Intelligence

Comparative summaries, pairwise comparisons, and researcher-facing outputs now reference stable pathway identities.

Element Highlights

Comparative element aggregation tracks unique pathway_ids rather than ranks, preserving tied pathways independently.

Scientific Changes

LiFePO4 Criticality

No change (32.0)

LiFePO4 Risk

No change (2.833)

Scientific Usefulness

No change (95.65)

Reason

Architectural and explainability improvement only. Deterministic scoring, ranking, and scientific results remain unchanged.

Performance

No measurable performance impact.

Breaking API

No

New identity fields are additive.

Database Backfill

No

Regression Status

Passed

---

## v1.9.18

Summary

Canonical criticality comparison terminology remediation.

Reason

Resolved MG-AUD-036.

Affected Components

- MaterialSimilarityService
- MaterialRecommendationService
- DiscoveryScoringService
- Similarity and recommendation response schemas
- Similarity, recommendation, scenario recommendation, and discovery APIs

Changes

Criticality Direction Vocabulary

Comparison values derived from `criticality_score` now use explicit
criticality terminology:

- `LOWER_RISK` → `LOWER_CRITICALITY`
- `HIGHER_RISK` → `HIGHER_CRITICALITY`
- `SAME_RISK` → `SAME_CRITICALITY`
- `UNKNOWN` remains unchanged

Schema Validation

Similarity and recommendation response schemas now use one shared constrained
`CriticalityDirection` vocabulary instead of unconstrained strings.

Recommendation Explainability

Human-readable recommendation reasons remain unchanged:

- lower criticality by ...
- higher criticality by ...
- same criticality

Discovery Scoring

Discovery scoring now consumes `LOWER_CRITICALITY` while preserving the
existing 30-point lower-criticality bonus, reasoning path, and score-breakdown
key.

Scientific Changes

LiFePO4 Criticality

No change (32.0)

LiFePO4 Risk

No change (2.833)

Scientific Usefulness

No change (95.65)

Reason

The remediation changes machine-readable terminology only. Criticality
deltas, score weights, bonus eligibility, ranking, and scientific results are
unchanged. Material risk remains a separate evidence and scoring concept.

Performance

No measurable performance impact.

No additional database queries introduced.

Breaking API

Yes

The `criticality_direction` field name and response structure are unchanged,
but three serialized values changed. Clients comparing exact legacy values
must adopt the canonical criticality values.

Database Backfill

No

Regression Status

Passed

Verification

- Similarity delta and direction tests passed.
- Recommendation score and explanation tests passed.
- Discovery lower-criticality bonus regression tests passed.
- Full `pytest -v` suite passed.

Production Verification

Verified against the deployed v1.9.18 APIs:

- `GET /api/v1/materials/5/similar`
- `GET /api/v1/materials/5/recommendations`
- `GET /api/v1/materials/5/recommendations/scenario`
- `GET /api/v1/materials/5/discovery/candidates` with recommendation source
  enabled
- `GET /api/v1/materials/5/discovery/candidates` with recommendation and
  scenario sources enabled

All inspected criticality comparisons used canonical values. Discovery
recommendation candidates retained `lower_criticality` and received the
30-point `lower_criticality_bonus`. No legacy risk-direction values were
observed.

The discovery route defaults `include_recommendations` and
`include_scenarios` to `false` for performance. Family-only responses therefore
do not contain recommendation-derived criticality evidence by design.

Additional Audit Discovery

MG-AUD-052 was opened after production responses exposed scenario explanations
whose wording does not agree with the sign or direction of the numeric
contribution. Examples include a preferred-element bonus followed by `final
scenario penalty -10.0`, and positive score deltas described as penalties.

This follow-up concerns explanation semantics only and does not reopen
MG-AUD-036.

---

## Unreleased (post-v1.9.18)

Summary

Scenario adjustment explanation consistency remediation.

Reason

Resolved MG-AUD-052.

Affected Components

- ScenarioPolicyEvaluator
- Scenario recommendation explanation generation
- Discovery candidate explanation aggregation
- Scenario policy and scenario recommendation API tests

Changes

Direction-Aware Final Adjustment

The final scenario explanation now derives its label from `scenario_delta`:

- positive delta → `final scenario bonus`
- negative delta → `final scenario penalty` using the absolute magnitude
- zero delta → `no final scenario adjustment`

Score-Delta Invariant

Scenario evaluation now exposes and verifies the canonical relationship:

```text
scenario_delta = scenario_score - recommendation_score
```

Explanation Consistency

Preferred-element contributions now produce consistent positive wording, for
example:

```text
contains preferred element Na, bonus 10.0; final scenario bonus 10.0
```

Avoided-element contributions now produce consistent negative wording, for
example:

```text
contains avoided element Li, penalty 20.0; final scenario penalty 20.0
```

The contradictory wording `final scenario penalty -10.0` is no longer
produced.

Scientific Changes

None.

Scenario weights, recommendation scores, scenario scores, discovery scores,
candidate ordering, and ranking policy are unchanged. The remediation corrects
researcher-facing explanation semantics only.

Performance

No measurable performance impact.

No additional database queries introduced.

Breaking API

No.

Response fields and numeric values are unchanged. Only human-readable
`scenario_reason` wording is corrected.

Database Backfill

No.

Regression Status

Passed.

Verification

- Focused ScenarioPolicyEvaluator bonus, penalty, mixed-adjustment, neutral,
  and score-delta invariant tests passed.
- Scenario recommendation API sign-aware explanation assertions passed.
- Full regression suite passed.

Production Verification

Verified against the deployed APIs:

- `GET /api/v1/materials/5/recommendations/scenario` with `element=Li`,
  `avoid_element=Li`, and `prefer_element=Na`
- `GET /api/v1/materials/5/discovery/candidates` with
  `include_recommendations=true&include_scenarios=true`

Production responses confirmed:

- preferred-element candidates expose `scenario_delta: 10.0` and `final
  scenario bonus 10.0`
- the avoided-element candidate exposes `scenario_delta: -20.0` and `final
  scenario penalty 20.0`
- discovery explanations propagate the corrected scenario wording
- the score-delta invariant holds for the inspected candidates
- no contradictory negative-penalty wording remains

Resolution Status

MG-AUD-052 is fully remediated, regression-tested, and production-verified.
The release tag for this post-v1.9.18 change has not yet been recorded.

---

## Unreleased (post-v1.9.18) — MG-AUD-053

Summary

Discovery candidate base-score selection and deterministic tie-ordering
remediation.

Reason

Resolved MG-AUD-053.

Affected Components

- DiscoveryCandidateService candidate-source merge logic
- Discovery candidate result ordering
- Discovery candidate service regression tests

Changes

Base-Score Merge Selection

Candidate-source merging now compares the incoming base score with the
existing candidate's stored base score. It no longer compares an incoming base
score against an existing displayed score that already includes the
source-diversity bonus.

This prevents a stronger incoming source from being incorrectly rejected when
an earlier, weaker source appears larger only because diversity has already
been added.

Deterministic Tie Ordering

Discovery candidates remain ordered by descending `discovery_score`. Exact
score ties are now ordered by ascending `material_id`.

Valid Equal-Evidence Ties

Family-only candidates with identical evidence continue to receive identical
scores. The observed `125.0` ties are intentional:

```text
shared_chemistry            40.0
alkali_substitution         35.0
preferred_element_bonus     25.0
avoided_element_removed     25.0
total                      125.0
```

No unsupported scientific differentiation was introduced.

Scientific Changes

None.

Scoring weights and scientific ranking policy are unchanged. The remediation
corrects source-base selection and provides a stable non-scientific tie-breaker.

Performance

No measurable performance impact.

No additional database queries introduced.

Breaking API

No.

Response fields and score values are unchanged. Exact ties may now have an
explicitly stable order by ascending `material_id`.

Database Backfill

No.

Regression Status

Passed.

Verification

- Focused candidate merge tests passed.
- A stronger incoming base score wins even when the existing displayed total
  is equal because of a diversity bonus.
- A genuine equal-base-score tie retains the existing winning breakdown.
- Score totals continue to equal the sum of their breakdowns.
- Full regression suite passed.

Production Verification

Verified against the deployed discovery candidate endpoint using both enhanced
family/recommendation/scenario aggregation and the default family-only mode.

Production responses confirmed:

- enhanced results remain in descending score order
- every `discovery_score` reconciles with its `score_breakdown`
- three participating source types produce `source_diversity_bonus: 20.0`
- valid family-only `125.0` ties remain unchanged
- tied `125.0` candidates are ordered by material IDs `6, 7, 8, 9, 10`
- tied `-10.0` candidates are ordered by material IDs `1, 2, 3, 4`

Resolution Status

MG-AUD-053 is fully remediated, regression-tested, and production-verified.
The release tag for this post-v1.9.18 change has not yet been recorded.