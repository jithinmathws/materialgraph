# MaterialGraph Architecture & Implementation Audit Resolution

Version: 1.5
Last Updated: 2026-07-22

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

# MG-AUD-015

Title

Objective alignment used path-wide transition events instead of endpoint
composition.

Severity

High

Status

✅ Resolved

Resolution Version

Post-v1.9.18

Affected Components

- DiscoveryPathRankingService
- ScientificPathwayAnalysisService integration expectations
- Discovery path-ranking tests
- Scientific pathway-analysis tests
- Discovery transition and traversal explanation rendering

Root Cause

Discovery path ranking accumulated the union of `removed_elements` and
`introduced_elements` across all transitions and used those event sets to
award objective-alignment credit.

Transition events describe what happened somewhere along a pathway. They do
not establish the composition of the final material. A preferred element could
be introduced and later removed, or an avoided element could be removed and
later reintroduced, while the path still received objective credit.

Scientific Impact

Path scientific-usefulness scores could overstate endpoint objective
satisfaction. This could affect path ordering and researcher interpretation,
particularly for multi-hop paths and multi-element objectives.

Usefulness explanations compounded the issue by presenting transition events
without separately stating whether the endpoint satisfied the requested avoid
and prefer constraints.

Resolution

✓ Objective alignment now evaluates the final material's composition.

✓ Structured endpoint `elements` are authoritative whenever the field is
present, including when explicitly empty.

✓ When structured elements are absent, the canonical exact chemical-formula
parser evaluates `formula` or `pretty_formula`.

✓ Unavailable or explicitly empty endpoint composition earns no objective
credit.

✓ Avoid and prefer sides retain their established proportional policy. Each
side contributes at most `12.5`, preserving the maximum two-sided objective
weight of `25.0`.

✓ Transition-event evidence remains available but is no longer treated as
endpoint satisfaction.

✓ Usefulness explanations now distinguish:

- removals and introductions occurring during the path;
- avoided elements excluded from or retained by the endpoint;
- preferred elements present in or absent from the endpoint; and
- unavailable endpoint-composition evidence.

✓ Unicode path separators in discovery explanations were standardized to
ASCII `->` to render consistently in PowerShell, terminals, logs, and API
clients.

Regression Verification

✓ Preferred element introduced and later removed receives no endpoint credit.

✓ Avoided element removed and later reintroduced receives no endpoint credit.

✓ Complete single-element avoid/prefer satisfaction receives `25.0`.

✓ Partial multi-element satisfaction receives proportional credit.

✓ Missing endpoint composition receives `0.0`.

✓ Explicit structured `elements` take precedence over formula fallback.

✓ Explanation tests separate path events from endpoint outcomes and cover
endpoint reversals, partial satisfaction, and unavailable evidence.

✓ Existing semantic and scientific pathway-analysis tests were updated to use
endpoint-composition expectations.

✓ Full regression suite passed.

Development Endpoint Verification

The discovery path endpoint was verified for material 5 and target material 7
with `avoid_element=Li` and `prefer_element=Na`.

Verified path:

``` text
LiFePO4 -> Na3Fe3(PO4)4
```

The endpoint `Na3Fe3(PO4)4` excludes Li and contains Na. The response returned:

``` text
objective_alignment: 25.0
scientific_usefulness_score: 99.47
```

The usefulness reason independently reported:

- Li removal and Na introduction during the path;
- Li exclusion and Na presence at the endpoint;
- Fe-O-P shared-element continuity; and
- alkali-substitution transition logic.

The score breakdown reconciled:

``` text
30.0 + 25.0 + 20.0 + 10.0 + 14.47 = 99.47
```

Production Verification

Pending. Development endpoint behavior and the full automated test suite are
verified; production deployment was not part of this remediation check.

Scientific Changes

Yes. Objective alignment now represents final-material composition instead of
path-wide event occurrence. Valid paths whose endpoints already satisfied the
objective retain their expected credit. Reversed or incomplete endpoint
outcomes may receive lower scores.

Breaking API

No structural API change.

Numeric objective-alignment and scientific-usefulness scores may change for
paths whose transition-event history differs from final endpoint composition.
Human-readable usefulness wording is more explicit. Unicode arrows in
discovery explanation text now render as ASCII `->`.

Database Migration

No.

Lessons Learned

Transition events, path continuity, and endpoint composition are distinct
scientific concepts and must not share one scoring proxy.

Explanations should identify both the evidence scope and the material state
that supports a numeric score.

Structured composition evidence must remain authoritative, while formula
parsing should be an exact fallback rather than substring matching.

Related Findings

MG-AUD-004

MG-AUD-014

MG-AUD-050

Related Scientific Principles

Principle 10

Principle 11

Related ADR

ADR-002

---

# MG-AUD-014

Title

Preservation could be satisfied by union across transitions.

Severity

High

Status

Verification

Resolution Version

Post-v1.9.18 remediation (release tag pending)

Affected Components

- ResearchObjectiveService preservation evaluation
- ScientificPathwayAnalysisService shared-element facts
- Research-objective and scientific-pathway regression tests

Root Cause

Research-objective preservation accumulated transition evidence with a union.
Different transitions could therefore collectively contain all requested
elements even when those elements were not shared continuously through every
hop.

Scientific pathway analysis already intended to compute an intersection, but
it read only the compatibility field `preserved_framework`, ignored the
authoritative `shared_elements` field, and omitted transitions that lacked
evidence. These behaviors could overstate path-wide continuity.

Scientific Impact

A multi-hop pathway could satisfy a preservation constraint without continuous
evidence for every requested element. Research filtering, objective
satisfaction, and explanations could therefore report stronger path-wide
continuity than the transitions established.

Resolution

✓ Replaced union aggregation with intersection across every transition.

✓ Made `shared_elements` authoritative whenever present, including when
explicitly empty.

✓ Retained `preserved_framework` only as a compatibility fallback when
`shared_elements` is absent.

✓ Required every transition to participate; missing evidence contributes an
empty set.

✓ Defined zero-transition paths as not establishing non-empty preservation
requirements.

✓ Aligned scientific pathway facts with the same path-wide semantics.

Regression Verification

✓ All 26 focused research-service tests passed.

✓ The full regression suite passed.

✓ Regression coverage rejects union-only preservation, empty paths, missing
transition evidence, and fallback from an explicitly empty primary field.

Local Endpoint Verification

✓ A two-hop objective pathway reported transition evidence
`{Fe, O, P}` followed by `{Fe, Na, O, P}`.

✓ The response and chain explanation correctly reported their path-wide
intersection as `Fe-O-P` shared-element continuity.

✓ Compatibility fields retained `preservation_basis: element_overlap` and
`structural_preservation_validated: false`.

Pending Verification

The correction has been recorded as resolved on the production EC2
endpoint.

Scientific Changes

Yes. Preservation now means continuous shared-element evidence across every
transition rather than collective occurrence anywhere in the path.

Breaking API

No. Existing response fields retain their shape, although affected objective
results and explanations may change when a path previously passed only through
union semantics.

Database Migration

No.

Lessons Learned

Path-wide continuity is an all-hop invariant. Evidence aliases must have clear
precedence, and missing or empty primary evidence must not silently recover a
stronger claim from a compatibility field.

Related Findings

MG-AUD-005

MG-AUD-011

MG-AUD-013

---

# MG-AUD-037 — Recommendation Reasons Mix Contributors and Context

Priority

P1

Status

✅ Resolved

Resolution Version

Post-v1.9.18 remediation (release tag pending)

Affected Components

- MaterialRecommendationService score explanation generation
- Discovery candidate explanations propagated from recommendations
- Recommendation-service regression tests

Problem

`recommendation_reason` combined score contributors and contextual facts
without distinguishing their roles.

Criticality comparisons were included regardless of whether
`prefer_lower_criticality` affected the score. Shared elements and
applications appeared alongside recommendation bonuses even though they are
already components of `similarity_score`. The 5-point
low-energy-above-hull contribution was omitted from the explanation.

Root Cause

`_build_recommendation_reason()` did not receive
`prefer_lower_criticality`, so it could not determine whether criticality was
an active score contributor or contextual comparison data.

The explanation also flattened the similarity basis and additional
recommendation contributions into one undifferentiated list. Its wording did
not expose that shared-element and shared-application evidence had already
been incorporated into the similarity score.

Investigation

Repository-wide dependency tracing confirmed that:

- shared elements and applications contribute to `similarity_score`;
- `similarity_score` is the base recommendation score;
- criticality contributes only when `prefer_lower_criticality` is enabled;
- stability contributes 10 points;
- energy above hull contributes 5 points when
  `energy_above_hull <= 0.01`;
- the schema treats `recommendation_reason` as an opaque string;
- no frontend or downstream consumer parses its wording; and
- discovery forwards the reason unchanged as an explanation component.

Resolution

✓ Passed `prefer_lower_criticality` into
`_build_recommendation_reason()`.

✓ Labelled shared elements and applications as the `similarity basis`, avoiding
the appearance of independent or duplicate recommendation bonuses.

✓ Included lower or higher criticality among active contributors only when the
criticality preference affects scoring.

✓ Retained a non-scoring criticality comparison under `context` when the
preference is disabled.

✓ Added `low energy above hull` when the exact scoring threshold,
`energy_above_hull <= 0.01`, is satisfied.

✓ Preserved stability wording and the final recommendation score.

Regression Verification

✓ Recommendation-service tests passed (`11 passed`).

✓ New regression coverage verifies non-scoring criticality context, the
low-energy contribution, and the labelled similarity basis.

✓ The full regression suite passed locally.

Local Endpoint Verification

✓ `GET /api/v1/materials/5/recommendations` with
`prefer_lower_criticality=true` showed criticality as an active contributor.

✓ The same endpoint with `prefer_lower_criticality=false` removed criticality
from scoring and retained it only after `context:`.

✓ Shared-element and shared-application evidence appeared under
`similarity basis:`.

✓ Stability and qualifying low energy above hull appeared as active
contributors.

✓ Displayed scores reconciled with the explanations. Representative disabled
preference results were:

```text
130 similarity + 10 stability + 5 low energy = 145
110 similarity + 10 stability + 5 low energy = 125
```

Scientific Changes

No scientific values, scoring weights, thresholds, or ranking policies
changed. The remediation improves explanation provenance and prevents
contextual evidence from being mistaken for an active score contribution.

Breaking API

No. Response fields and serialized numeric values are unchanged.
Human-readable `recommendation_reason` wording is clearer.

Database Migration

No.

Production Verification

✓ Production verification passed on 2026-07-23 for material 5 with both
`prefer_lower_criticality=true` and `prefer_lower_criticality=false`.

✓ With the preference enabled, criticality appeared as an active contributor
and the displayed score reconciled with similarity, criticality, stability, and
low-energy contributions.

✓ With the preference disabled, criticality did not affect the score and
appeared only under `context`; representative scores reconciled as
`130 + 10 + 5 = 145` and `110 + 10 + 5 = 125`.

Lessons Learned

Human-readable explanations must preserve score provenance. Evidence that
forms a composite base score should be labelled as that score's basis, optional
policy contributions must follow their activation flags, and contextual facts
must not be presented as if they changed the result.

Related Findings

MG-AUD-034

MG-AUD-035

MG-AUD-036

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

---

# MG-AUD-036

Title

Criticality comparison directions use general risk terminology.

Severity

Medium

Status

✅ Resolved

Resolution Version

v1.9.18

Affected Components

- MaterialSimilarityService
- MaterialRecommendationService
- DiscoveryScoringService
- Similarity response schemas
- Recommendation and scenario recommendation response schemas
- Material neighbor routes
- Discovery candidate scoring

Root Cause

Comparisons calculated exclusively from `criticality_score` were labelled as
`LOWER_RISK`, `HIGHER_RISK`, and `SAME_RISK`.

These values predated the platform's explicit separation of material
criticality from `risk_score`. The legacy labels therefore became
scientifically ambiguous and inconsistent with the quantity being compared.

Scientific Impact

No numeric scientific defect was present. Criticality deltas, similarity
scores, recommendation scores, discovery scores, and rankings were calculated
correctly.

The machine-readable API vocabulary was semantically inaccurate and could
cause consumers to interpret a criticality comparison as a general material
risk comparison.

Resolution

✓ Replaced legacy direction values with canonical criticality values:

- `LOWER_CRITICALITY`
- `HIGHER_CRITICALITY`
- `SAME_CRITICALITY`
- `UNKNOWN`

✓ Added one shared constrained `CriticalityDirection` schema vocabulary.

✓ Applied the shared vocabulary to similarity, recommendation, and scenario
recommendation response contracts.

✓ Updated recommendation explanation branches while preserving existing
researcher-facing wording.

✓ Updated DiscoveryScoringService atomically so the existing 30-point
lower-criticality bonus remains eligible for lower-criticality candidates.

✓ Corrected the route description from "lower criticality risk" to "lower
criticality."

✓ Preserved the independent material-risk and material-quality pipelines.

Characterization Verification

Before remediation

- Negative criticality delta produced `LOWER_RISK`.
- Positive criticality delta produced `HIGHER_RISK`.
- Zero criticality delta produced `SAME_RISK`.
- Unknown criticality produced `UNKNOWN`.
- Discovery scoring used `LOWER_RISK` as the control signal for its 30-point
  lower-criticality bonus.

After remediation

- Negative criticality delta produces `LOWER_CRITICALITY`.
- Positive criticality delta produces `HIGHER_CRITICALITY`.
- Zero criticality delta produces `SAME_CRITICALITY`.
- Unknown criticality continues to produce `UNKNOWN`.
- Discovery scoring uses `LOWER_CRITICALITY` and awards the same 30-point
  bonus.

Regression Verification

✓ Similarity delta, rounding, unknown-evidence, and direction tests

✓ Recommendation score and explanation tests

✓ Discovery lower-criticality bonus and score-breakdown tests

✓ Full `pytest -v` regression suite

Production Endpoint Verification

✓ `GET /api/v1/materials/5/similar`

✓ `GET /api/v1/materials/5/recommendations`

✓ `GET /api/v1/materials/5/recommendations/scenario`

✓ `GET /api/v1/materials/5/discovery/candidates` with
`include_recommendations=true`

✓ `GET /api/v1/materials/5/discovery/candidates` with
`include_recommendations=true&include_scenarios=true`

Production responses used `LOWER_CRITICALITY` consistently and exposed no
legacy `LOWER_RISK`, `HIGHER_RISK`, or `SAME_RISK` comparison values.

Discovery candidates sourced from the recommendation engine retained the
`lower_criticality` reasoning path and received
`lower_criticality_bonus: 30.0`. With scenario aggregation enabled, merged
source provenance and the expected source-diversity contribution were also
present.

The default discovery-candidate request intentionally excludes recommendation
and scenario sources for performance. Its lack of criticality evidence is
therefore expected and does not indicate a failure of this remediation.

Scientific Changes

LiFePO4 Criticality

No change (32.0)

LiFePO4 Risk

No change (2.833)

Scientific Usefulness

No change (95.65)

Reason

The remediation changes terminology and schema validation only. Numeric
criticality calculations, risk calculations, score weights, bonus eligibility,
ranking, and researcher-facing explanations remain unchanged.

Performance Improvements

✓ No measurable performance impact.

✓ No additional database queries introduced.

Breaking API

Yes.

The `criticality_direction` field name and JSON structure remain unchanged,
but three exact serialized values changed. Clients comparing legacy string
values must migrate to the canonical criticality vocabulary.

Database Migration

No.

Lessons Learned

Machine-readable scientific vocabulary must name the exact quantity being
compared. Criticality and material risk are separate concepts and should not
share ambiguous direction labels.

Schema constraints should encode finite response vocabularies so semantic
drift cannot pass validation unnoticed.

Related Scientific Principles

Principle 10

Principle 11

Related ADR

ADR-002

---

# MG-AUD-011

Title

Framework explanations overstated available evidence.

Severity

High

Status

✅ Resolved

Affected Components

- MaterialFamilyService explanation generation
- Discovery candidate explanations propagated from family evidence
- Discovery traversal path reasoning
- Material-family API description

Root Cause

Composition-based element overlap was described with structural wording such as `shares phosphate framework`, `shares oxide chemistry`, and path chemistry preservation. The implementation had not validated bonding, crystallographic structure, site equivalence, or framework preservation.

Resolution

✓ Replaced phosphate-framework claims with phosphorus-and-oxygen composition evidence.

✓ Added an explicit statement that structural framework similarity is not validated.

✓ Replaced oxide-chemistry claims with oxygen-membership evidence and an explicit statement that oxide structure similarity is not validated.

✓ Reworded traversal path reasoning to describe shared elemental overlap and state that structural preservation is not validated.

✓ Preserved compatibility fields such as `preserved_framework` where they remain qualified by `preservation_basis: element_overlap` and `structural_preservation_validated: false`.

Regression Verification

✓ Material-family explanation tests passed.

✓ Discovery traversal explanation tests passed.

✓ Full regression suite passed.

Production Verification

✓ Family responses no longer claim `shares phosphate framework`.

✓ Discovery candidate explanations describe composition evidence and explicitly qualify missing structural validation.

✓ Path reasoning reports shared elemental overlap and explicitly states that structural preservation is not validated.

✓ Candidate admission, scoring, ranking, transition types, and compatibility fields remained unchanged.

Scientific Changes

Explanation semantics only. No scientific scoring weights, ranking policy, candidate admission, or pathway generation changed.

Breaking API

No.

Database Migration

No.

Lessons Learned

Element membership and overlap must not be presented as structural, bonding, framework, or mechanistic evidence without independent validation.

---

# MG-AUD-052

Title

Scenario explanation labels beneficial score contributions as penalties.

Severity

Medium

Status

✅ Resolved

Resolution Version

Post-v1.9.18 remediation (release tag pending)

Affected Components

- Scenario recommendation scoring
- Scenario explanation generation
- Discovery candidate explanation aggregation

Root Cause

`ScenarioPolicyEvaluator` calculated `scenario_delta` correctly as the
difference between the scenario and recommendation scores. However, final
explanation assembly separately calculated `recommendation_score - score` and
always labelled the result as a penalty. Beneficial contributions could
therefore be described as negative penalties even when their numeric delta was
positive.

Observed Behavior Before Remediation

Production endpoint verification for v1.9.18 exposed explanations such as:

- `contains preferred element Na, bonus 10.0; final scenario penalty -10.0`
- a positive scenario score delta accompanied by wording that describes the
  contribution as a negative penalty

Scientific Impact

The numeric score and ranking were correct, but the researcher-facing
explanation can communicate the opposite direction of the applied
contribution. This weakens deterministic explainability and may cause API
consumers to misinterpret whether a scenario improved or penalized a
candidate.

Resolution

✓ Established the canonical invariant:

```text
scenario_delta = scenario_score - recommendation_score
```

✓ Made final explanation wording direction-aware:

- positive delta → `final scenario bonus <delta>`
- negative delta → `final scenario penalty <absolute delta>`
- zero delta → `no final scenario adjustment`

✓ Preserved all scenario weights, numeric scores, and ranking behavior.

✓ Confirmed that discovery candidate explanations propagate the corrected
scenario reason when scenario aggregation is enabled.

Regression Verification

✓ Preferred-element bonus produces a positive delta and bonus wording.

✓ Avoided-element penalty produces a negative delta and penalty wording.

✓ Combined bonus and penalty reports the direction of the net adjustment.

✓ Zero adjustment produces neutral wording.

✓ `scenario_delta` equals rounded `scenario_score - recommendation_score`.

✓ Scenario recommendation API assertions validate wording against delta sign.

✓ Full regression suite passed.

Production Endpoint Verification

✓ `GET /api/v1/materials/5/recommendations/scenario` with `element=Li`,
`avoid_element=Li`, and `prefer_element=Na`

✓ `GET /api/v1/materials/5/discovery/candidates` with
`include_recommendations=true&include_scenarios=true`

Production responses confirmed the corrected positive case:

```text
scenario_delta: 10.0
contains preferred element Na, bonus 10.0; final scenario bonus 10.0
```

Production responses also confirmed the corrected negative case:

```text
scenario_delta: -20.0
contains avoided element Li, penalty 20.0; final scenario penalty 20.0
```

The discovery response propagated the repaired explanation wording. The former
contradiction `final scenario penalty -10.0` was not present.

Scientific Changes

None.

The remediation changes explanation semantics only. Recommendation scores,
scenario scores, discovery scores, score weights, candidate ordering, and
ranking policy remain unchanged.

Performance Improvements

✓ No measurable performance impact.

✓ No additional database queries introduced.

Breaking API

No.

Response structure and numeric values remain unchanged. Human-readable
`scenario_reason` text is corrected.

---

# MG-AUD-053

Title

Discovery candidate source merging compares incompatible score stages and
exact ties lack an explicit deterministic ordering rule.

Severity

Medium

Status

✅ Resolved

Resolution Version

Post-v1.9.18 remediation (release tag pending)

Affected Components

- DiscoveryCandidateService candidate-source merge logic
- Discovery candidate result ordering
- Candidate-service regression tests

Root Cause

The source merge compared an incoming base score with the existing candidate's
displayed `discovery_score`. The displayed value could already include a
source-diversity bonus, so the two values represented different scoring stages.
A weaker existing base could therefore prevent a stronger incoming base from
becoming the winning score provenance.

Additionally, result sorting used only `discovery_score`. Although Python's
sort is stable, the order of equal-scoring candidates depended on upstream
insertion order rather than an explicit public deterministic rule.

Investigation Finding

The observed family-only `125.0` ties are valid. Candidates with identical
recognized family relations and identical objective evidence should receive
equal scores. This finding does not justify changing scientific weights or
inventing differentiation unsupported by available evidence.

Scientific Impact

The merge defect could preserve the wrong source breakdown and understate the
strongest base evidence for a candidate. The ordering issue could make exact
ties less reproducible across changes in upstream encounter order. Neither
issue requires a change to scientific scoring policy.

Resolution

✓ Compare `adjusted_score` with the stored `_base_discovery_score`, not with a
displayed score that includes source diversity.

✓ Reapply the source-diversity bonus only after selecting the winning base
score and updating participating source identities.

✓ Sort by descending `discovery_score` and then ascending `material_id`.

✓ Preserve the existing breakdown for genuine equal-base-score encounters.

✓ Preserve valid equal-evidence family-only ties.

Regression Verification

✓ A stronger incoming base score wins when an existing displayed total is
equal only because of its diversity bonus.

✓ A `105.0` incoming base replaces an existing `100.0` base even when the
existing displayed total is `110.0`.

✓ A genuine equal-base-score tie retains the existing winning breakdown.

✓ The displayed score equals the winning base plus the current diversity
bonus.

✓ Every candidate score equals the sum of its score breakdown.

✓ Focused tests and the full regression suite passed.

Production Endpoint Verification

✓ Enhanced discovery request with recommendation and scenario aggregation.

✓ Default family-only discovery request.

Production responses confirmed:

- scores remain ordered from highest to lowest
- enhanced candidates reconcile exactly with their score breakdowns
- candidates observed through family, recommendation, and scenario sources
  receive `source_diversity_bonus: 20.0`
- valid `125.0` equal-evidence ties remain
- tied `125.0` candidates use ascending material IDs `6, 7, 8, 9, 10`
- tied `-10.0` candidates use ascending material IDs `1, 2, 3, 4`

Scientific Changes

None.

Family scoring weights, objective bonuses and penalties, and scientific
ranking policy remain unchanged. `material_id` is used only as a deterministic
non-scientific tie-breaker after exact score equality.

Performance Improvements

✓ No measurable performance impact.

✓ No additional database queries introduced.

Breaking API

No.

Response structure and score values are unchanged. The order of exact ties is
now explicitly deterministic.

Database Backfill Required

No.

Resolution Summary

MG-AUD-053 is fully remediated, regression-tested, and production-verified.
The release tag for this post-v1.9.18 change has not yet been recorded.

Database Migration

No.

Lessons Learned

Researcher-facing explanations must derive direction labels from the same
canonical delta exposed by the API. A numeric sign and its natural-language
description should never be calculated independently.

Relationship to MG-AUD-036

This is an independent explanation defect discovered during production
verification. It does not invalidate the completed criticality-direction
remediation.

---

# MG-AUD-003

Title

Candidate screening uses legacy unknown-risk-as-zero semantics.

Severity

High

Status

✅ Resolved

Resolution Version

v1.9.9

Affected Components

- CandidateScreeningService
- CandidateComparisonService
- MaterialRiskService
- CandidateScreeningResult
- CandidateComparisonResult

Root Cause

Candidate screening relied on the legacy numeric risk API, allowing unknown
risk evidence to be represented as a favorable numeric zero during screening
and comparison.

Scientific Impact

Candidates with incomplete risk evidence could be interpreted as having lower
risk than fully characterized materials.

Resolution

✓ Candidate screening migrated to evidence-aware bulk risk signals.

✓ Unknown risk remains null instead of numeric zero.

✓ Risk evidence metadata exposed in screening responses.

✓ Candidate comparison now compares risk only when both candidates have known
risk evidence.

✓ Unknown risk is explicitly reported instead of being interpreted as low risk.

✓ Bulk risk loading replaces per-material legacy risk lookups.

Regression Verification

✓ Candidate screening tests

✓ Candidate comparison tests

✓ Risk service tests

✓ Material quality tests

✓ Full regression suite

✓ Candidate screening endpoint verification

✓ Candidate comparison endpoint verification

✓ LiFePO4 → Na/phosphate reference workflow

Scientific Changes

LiFePO4 Risk

No change (2.833)

LiFePO4 Criticality

No change (32.0)

Scientific Usefulness

No change (95.65)

Reason

Only unknown risk evidence semantics changed. Fully characterized materials
retain identical scientific scores and rankings.

Performance Improvements

✓ Bulk risk signal loading replaces per-material legacy risk queries.

Breaking API

No

Database Migration

No

Lessons Learned

Scientific uncertainty must be represented explicitly. Unknown evidence should
never be interpreted as favorable evidence during screening or comparison.

Related Scientific Principles

Principle 11

Related ADR

ADR-002

---

# MG-AUD-004

Title

Formula substring matching used instead of exact chemical element
membership.

Severity

High

Status

✅ Resolved

Resolution Version

v1.9.10

Affected Components

- DiscoveryScoringService
- DiscoveryCandidateService
- DiscoveryChainService
- DiscoveryWarningService
- ResearchObjectiveExplorationService

Root Cause

Multiple discovery services determined preferred and avoided element
membership using raw string matching against chemical formulas.

Examples included:

- N matching Na
- S matching Si
- C matching Ca

Scientific Impact

Ambiguous chemical element symbols could:

- incorrectly award preferred element bonuses
- incorrectly remove avoided element penalties
- admit incorrect discovery chains
- generate incorrect researcher explanations
- generate incorrect researcher warnings

Resolution

✓ Discovery candidate scoring now uses structured MaterialElement
membership.

✓ Discovery chain expansion now uses exact element membership.

✓ Discovery warnings now use canonical chemical element parsing.

✓ Research objective exploration scoring, explanations, and warnings now
use exact element membership.

✓ Existing chemical_formula utilities reused as the canonical parser
where structured membership is unavailable.

Regression Verification

✓ Discovery scoring tests

✓ Discovery chain tests

✓ Discovery warning tests

✓ Research objective exploration tests

✓ Chemical formula membership tests

✓ Full regression suite

✓ LiFePO4 → Na/phosphate reference workflow

Scientific Changes

LiFePO4 Criticality

No change (32.0)

LiFePO4 Risk

No change (2.833)

Scientific Usefulness

No change (95.65)

Reason

The reference workflow already used exact, unambiguous element symbols.
The remediation affects only ambiguous symbol comparisons while
preserving valid scientific rankings.

Performance Improvements

✓ Structured MaterialElement membership reused where available.

✓ Existing canonical formula parser reused elsewhere.

✓ No additional database queries introduced.

Breaking API

No

Database Migration

No

Lessons Learned

Chemical formulas are structured scientific data.

Scientific reasoning must compare exact chemical element symbols rather
than raw string fragments.

Unknown or ambiguous representations must never influence scientific
reasoning.

Related Scientific Principles

Principle 10

Principle 11

Related ADR

ADR-002

---

# MG-AUD-005

Title

Element overlap represented as validated framework preservation.

Severity

High

Status

✅ Resolved

Resolution Version

v1.9.11

Affected Components

- DiscoveryTransitionValidator
- DiscoverySubstitutionPathService
- DiscoveryChainService
- DiscoveryPathRankingService
- ScientificPathwayAnalysisService
- ResearchEvidenceIntelligenceService
- ComparativeResearchIntelligenceService
- ResearchObjectiveExplorationService
- Discovery response schemas
- Scientific pathway schemas

Root Cause

Shared chemical element overlap was exposed and described as framework
preservation even though the deterministic engine does not validate
crystallographic framework continuity.

Scientific Impact

Researcher-facing explanations could overstate the available scientific
evidence by implying validated structural preservation rather than
deterministic element continuity.

Resolution

✓ Introduced canonical shared_elements metadata.

✓ Preserved preserved_framework as a backward-compatible compatibility
alias.

✓ Added preservation_basis metadata.

✓ Added structural_preservation_validated metadata.

✓ Qualified researcher-facing explanations throughout the discovery and
research layers.

✓ Distinguished deterministic evidence from experimental validation.

Regression Verification

✓ Transition validation tests

✓ Substitution path tests

✓ Scientific pathway tests

✓ Research evidence tests

✓ Comparative intelligence tests

✓ Full regression suite

✓ LiFePO4 → Na/phosphate reference workflow

Scientific Changes

LiFePO4 Criticality

No change (32.0)

LiFePO4 Risk

No change (2.833)

Scientific Usefulness

No change (95.65)

Reason

The remediation corrects scientific semantics and evidence provenance
without modifying deterministic scoring or pathway ranking.

Performance Improvements

✓ Existing transition metadata reused.

✓ No additional database queries introduced.

✓ API compatibility preserved through legacy aliases.

Breaking API

No

Database Migration

No

Lessons Learned

Deterministic compositional evidence and validated structural evidence
represent different scientific claims.

Research systems should communicate the strongest claim supported by the
available evidence and explicitly qualify inferred relationships.

Related Scientific Principles

Principle 10

Principle 11

Related ADR

ADR-002

---

# MG-AUD-006

Title

Discovery score breakdown does not represent discovery score provenance.

Severity

Medium

Status

✅ Resolved

Resolution Version

v1.9.12

Affected Components

- DiscoveryCandidateService
- DiscoveryScoringService
- Discovery candidate responses

Root Cause

Discovery candidates merged competing score breakdowns additively while
the final discovery score retained only the highest scoring candidate
encounter plus source diversity bonuses.

As a result, score_breakdown could report contributions that were not
part of the final discovery score.

Scientific Impact

Researcher-facing score explanations could misrepresent which discovery
source actually determined the reported discovery score.

Although numeric scores remained correct, the explainability layer was
internally inconsistent.

Resolution

✓ Candidate merging now preserves the score breakdown corresponding to
the winning score provenance.

✓ Discovery paths continue to aggregate contextual evidence from all
contributing discovery sources.

✓ Explanations continue to aggregate contextual reasoning.

✓ Substitution paths continue to populate when discovered through later
candidate encounters.

✓ Discovery score arithmetic is now internally consistent.

Regression Verification

✓ Candidate merge characterization tests

✓ Discovery scoring tests

✓ Discovery candidate endpoint tests

✓ Discovery chain tests

✓ Full regression suite

✓ LiFePO4 → Na/phosphate reference workflow

Scientific Changes

LiFePO4 Criticality

No change (32.0)

LiFePO4 Risk

No change (2.833)

Scientific Usefulness

No change (95.65)

Reason

This remediation corrects explainability provenance without modifying
scientific scoring or candidate ranking.

Performance Improvements

✓ No measurable performance impact.

✓ No additional database queries introduced.

Breaking API

No

Database Migration

No

Lessons Learned

Scientific provenance should explain exactly how a reported score was
derived.

Contextual discovery evidence and scoring provenance represent different
types of information and should not be merged into the same arithmetic
explanation.

Related Scientific Principles

Principle 10

Principle 11

Related ADR

ADR-002

---

# MG-AUD-007

Title

Discovery source diversity bonus can be inflated by repeated candidate
encounters and aggregate-score reuse.

Severity

Medium

Status

✅ Resolved

Resolution Version

v1.9.13

Affected Components

- DiscoveryCandidateService
- DiscoveryScoringService
- Discovery candidate responses
- Discovery candidate merge logic
- Discovery source-diversity scoring

Root Cause

Candidate merging did not maintain explicit provenance for the distinct
discovery source types contributing to a candidate.

Repeated encounters could therefore influence source-diversity accounting
without a canonical distinct-source set.

During remediation, aggregate discovery scores that already included a
source-diversity bonus could also be reused as the effective base score during
subsequent merges, allowing the diversity contribution to be counted again.

Scientific Impact

Discovery candidates could receive an inflated source-diversity contribution
that did not correspond to the number of independent discovery source types
supporting the candidate.

This affected discovery score explainability and ranking confidence signals,
although it did not alter the separate scientific pathway usefulness score.

Resolution

✓ Source diversity is now calculated from distinct discovery source types.

✓ Repeated encounters from the same source type do not increase the diversity
bonus.

✓ One distinct source receives no source-diversity bonus.

✓ Two distinct source types receive a 10-point bonus.

✓ Three distinct source types receive a 20-point bonus.

✓ Candidate merging tracks the winning base discovery score separately from
the accumulated source-diversity bonus.

✓ The winning base score breakdown is preserved independently from contextual
evidence gathered from other candidate encounters.

✓ Existing aggregate discovery scores are not reused as base scores for
subsequent diversity calculations.

✓ Discovery paths and explanations continue to aggregate across contributing
sources.

✓ Substitution paths can still be populated by later candidate encounters.

✓ Internal source-tracking and base-score provenance metadata is removed before
public API serialization.

✓ Public API compatibility is preserved.

Regression Verification

✓ Candidate merge characterization tests

✓ Repeated same-source encounter tests

✓ Distinct-source diversity tests

✓ Winning-score provenance tests

✓ Exact-score tie tests

✓ Later substitution-path population tests

✓ Discovery candidate endpoint verification

✓ Substitution-path endpoint verification

✓ Full regression suite

✓ LiFePO4 → Na/phosphate reference workflow

Scientific Changes

LiFePO4 Criticality

No change (32.0)

LiFePO4 Risk

No change (2.833)

Scientific Usefulness

No change (95.65)

Reason

The remediation changes discovery source-diversity accounting and candidate
score provenance only.

Scientific pathway scoring is independent of the candidate source-diversity
bonus, and the reference pathway score remains unchanged.

Performance Improvements

✓ No additional database queries introduced.

✓ Distinct source tracking is maintained in memory during candidate merging.

✓ No measurable performance impact.

Breaking API

No

Database Migration

No

Lessons Learned

Discovery source diversity should represent independent evidence channels, not
the number of times a candidate is encountered.

Aggregate scores and base scoring provenance must remain separate so that
bonuses cannot be counted more than once during incremental candidate merging.

Contextual evidence may accumulate across discovery sources while numeric score
provenance must remain explicit and internally consistent.

Related Scientific Principles

Principle 10

Principle 11

Related ADR

ADR-002

---

# MG-AUD-008

Title

Partial risk evidence can unlock full low-risk bonus eligibility.

Severity

High

Status

✅ Resolved

Resolution Version

v1.9.14

Affected Components

- MaterialRiskService
- MaterialQualityService
- DiscoveryPathRankingService
- ScientificPathwayAnalysisService
- ResearchEvidenceIntelligenceService
- ComparativeResearchIntelligenceService
- EndpointSensitiveResearchRankingService
- DiscoveryKBestPathService
- DiscoveryGraphAlgorithmsService
- DiscoveryGraphBuilder
- DiscoveryGraphAnalyticsService

Root Cause

MaterialRiskService correctly distinguished unknown, partially covered, and completely covered material-element risk evidence. MaterialQualityService, however, used only `risk_known` and `risk_score` when determining favorable risk-quality bonus eligibility.

Consequently, a material with at least one calculable constituent-element risk could receive the same low-risk or medium-risk quality bonus as a fully covered material even when `risk_profile_coverage < 1.0` and `risk_evidence_complete = false`.

Scientific Impact

Partial evidence could be interpreted as established favorable risk evidence. This could inflate material quality and propagate into scientific usefulness, pathway ranking, quality summaries, confidence explanations, evidence readiness, comparative explanations, endpoint-sensitive ranking, K-best ordering, weighted shortest paths, and graph community importance.

Investigation Findings

- ✓ Finding confirmed against v1.9.13.
- ✓ MaterialRiskService already exposed the evidence metadata needed for a narrow remediation.
- ✓ Partial coverage correctly produced `risk_known = true`, `risk_profile_coverage < 1.0`, and `risk_evidence_complete = false`.
- ✓ MaterialQualityService ignored evidence completeness for favorable bonus eligibility.
- ✓ Scalar and bulk quality paths converge on the same scoring implementation.
- ✓ No database migration or backfill is required.
- ✓ Material-element coverage, composition-weighted coverage, and risk-dimension coverage were confirmed as distinct concepts.

Resolution

- ✓ Favorable risk-quality bonuses now require `risk_known = true`, `risk_evidence_complete = true`, and a non-null `risk_score` satisfying the existing threshold.
- ✓ Partial risk evidence remains visible and retains its observed numeric risk score.
- ✓ Partial evidence no longer qualifies as favorable evidence for quality scoring.
- ✓ Existing risk thresholds and quality weights are unchanged.
- ✓ MaterialRiskService aggregation semantics are unchanged.
- ✓ Public API compatibility is preserved.
- ✓ No new database queries were introduced.

Characterization Verification

Before remediation, a case with `risk_score = 1.5`, `risk_known = true`, `risk_profile_coverage = 0.25`, and `risk_evidence_complete = false` received `quality_score = 13.95`, including the favorable low-risk bonus.

After remediation, the same partial-evidence case produces `quality_score = 11.7` and receives no favorable risk-quality bonus. A complete-evidence low-risk case continues to receive the existing bonus.

Regression Verification

- ✓ Material quality characterization and remediation tests
- ✓ Material risk partial-coverage characterization tests
- ✓ Scalar and bulk risk-signal parity characterization
- ✓ Existing partial risk-dimension calculability semantics characterized
- ✓ LiFePO4 → Na/phosphate reference workflow
- ✓ Full regression suite

Reference Workflow Verification

Materials 5–10 were checked. All reported `risk_profile_coverage = 1.0`, `known_risk_element_count = 4`, `total_element_count = 4`, `risk_evidence_complete = true`, and no unknown risk elements.

LiFePO4 (material 5) retained `risk_score = 2.833` and `quality_score = 13.95`. Materials 6–10 retained `risk_score = 1.583` and `quality_score = 15.0`.

The reference pathway material-quality contribution remains 14.65.

Scientific Usefulness

95.65 → 95.65

Reason

The reference workflow has complete material-element risk evidence, so its materials remain eligible for the existing favorable risk-quality bonus. The unchanged score is therefore expected.

Downstream Dependency Findings

DiscoveryPathRankingService directly averages material quality into the `material_quality` component of `scientific_usefulness_score`.

ScientificPathwayAnalysisService reuses material quality in researcher-facing quality summaries and confidence explanations.

ResearchEvidenceIntelligenceService can use strong average material quality as a supporting signal, so corrected quality can legitimately alter evidence readiness.

ComparativeResearchIntelligenceService consumes scientific usefulness and material-quality score breakdowns.

EndpointSensitiveResearchRankingService uses endpoint quality in deterministic tie-breaking.

DiscoveryKBestPathService orders K-best paths by scientific usefulness and uses scientific usefulness to break equal-hop K-shortest ties.

DiscoveryGraphAlgorithmsService incorporates target-node quality into weighted shortest-path edge cost.

DiscoveryGraphBuilder propagates material quality and risk evidence metadata into graph nodes.

DiscoveryGraphAnalyticsService uses quality scores in community average quality and community importance calculations.

No downstream implementation changes were required for the narrow remediation; these consumers inherit corrected MaterialQualityService values.

Additional Findings Discovered During Investigation

1. During MG-AUD-008 dependency inspection, DiscoveryGraphAnalyticsService was found to use raw formula substring matching for community-summary element counts. This was tracked independently as MG-AUD-049 and remediated in the same v1.9.14 development cycle using canonical graph-node element membership.

2. Material-element risk coverage and risk-profile dimension coverage are distinct evidence concepts. MG-AUD-008 resolves only the former bonus-eligibility defect.

3. Composition-weighted risk coverage was considered but intentionally not introduced because changing coverage weighting would introduce a new scientific policy rather than a minimal remediation.

Breaking API

No

Database Migration

No

Performance Improvements

- ✓ No additional database queries introduced.
- ✓ Existing evidence-aware bulk risk and quality paths preserved.

Lessons Learned

Partial scientific evidence may support an observed score without supporting a favorable conclusion about the entire material.

Evidence availability and favorable-score eligibility are separate concepts.

Coverage semantics should be explicit: constituent-element coverage, composition-weighted coverage, and risk-dimension coverage are not interchangeable.

Related Scientific Principles

Principle 10

Principle 11

Related ADR

ADR-002

---

# MG-AUD-009

Title

Research objective evaluation only considers the first avoided and preferred element.

Severity

High

Status

✅ Resolved

Resolution Version

v1.9.15

Affected Components

- ResearchObjectiveService
- DiscoveryPathRankingService
- ScientificPathwayAnalysisService
- ResearchObjectiveExplorationService
- Scientific pathway response schemas

Root Cause

Research objective evaluation assumed a single avoided element and a single
preferred element.

Although the public research objective schema already accepted lists of
avoided and preferred elements, downstream deterministic scoring and pathway
evaluation only considered the first element from each list.

Scientific Impact

Multi-element research objectives could be evaluated incorrectly.

Researchers specifying objectives such as:

- avoid: Li, Co
- prefer: Na, K

would receive deterministic scoring equivalent to:

- avoid: Li
- prefer: Na

Additional requested objective elements were ignored during objective-alignment
evaluation and researcher-facing explanations.

Resolution

✓ Research objective evaluation now propagates complete avoided-element and
preferred-element collections through deterministic pathway analysis.

✓ Objective-alignment scoring now evaluates every requested avoided and
preferred element.

✓ Objective alignment is proportional to deterministic pathway evidence.

✓ Scientific pathway responses now expose structured objective satisfaction
metadata including:

- requested objective elements
- matched objective elements
- unmatched objective elements
- coverage percentages
- completion status

✓ Existing deterministic traversal behaviour is preserved.

✓ Existing pathway ranking behaviour is preserved.

✓ Existing scientific usefulness weighting is preserved.

✓ Public API compatibility is preserved.

Characterization Verification

Before remediation:

Multi-element objectives behaved identically to equivalent single-element
objectives because only the first avoided element and first preferred element
were evaluated.

After remediation:

Single-element objectives remain unchanged.

Multi-element objectives now evaluate every requested avoided and preferred
element.

Objective-alignment scores scale proportionally according to deterministic
transition evidence.

Regression Verification

✓ Research objective characterization tests

✓ Discovery path ranking tests

✓ Scientific pathway analysis tests

✓ Objective explainability tests

✓ Single-element endpoint verification

✓ Multi-element endpoint verification

✓ Full regression suite

✓ LiFePO4 → Na/phosphate reference workflow

Reference Workflow Verification

Single-element objective

avoid:

- Li

prefer:

- Na

Scientific usefulness

95.65

Objective alignment

25.0

Verified unchanged.

Multi-element objective

avoid:

- Li
- Co

prefer:

- Na
- K

Scientific usefulness

83.15

Objective alignment

12.5

Verified as expected.

Deterministic transition evidence removes Li and introduces Na while no
transition removes Co or introduces K.

The resulting proportional objective alignment correctly represents partial
objective fulfillment.

Scientific Changes

LiFePO4 Criticality

No change (32.0)

LiFePO4 Risk

No change (2.833)

Scientific Usefulness

Single-element objective

95.65

Multi-element objective

83.15

Reason

The reference single-element workflow remains unchanged.

Multi-element objectives now receive proportional deterministic objective
alignment based on all requested objective elements rather than only the first
requested element.

Performance Improvements

✓ No measurable performance impact.

✓ No additional database queries introduced.

Breaking API

No.

The new `objective_satisfaction` response object is additive.

Database Migration

No.

Lessons Learned

Research objective schemas and deterministic reasoning must remain
semantically aligned.

Supporting collections at the API boundary is insufficient if downstream
scientific reasoning evaluates only a subset of the requested objective.

Researcher explainability should expose not only deterministic scores but also
how completely each requested scientific objective has been satisfied.

Additional Finding Discovered During Investigation

During implementation and endpoint verification, an additional researcher
explainability opportunity was identified.

Current objective satisfaction correctly represents deterministic path-wide
objective fulfillment.

However, researcher responses do not yet distinguish:

- path-wide objective satisfaction
- endpoint-specific objective satisfaction

This does not affect deterministic scoring or scientific correctness.

The enhancement has been recorded separately as MG-AUD-050.

Related Scientific Principles

Principle 10

Principle 11

Related ADR

ADR-002

---

# MG-AUD-049

Title

Community analytics uses raw formula substring matching for element membership.

Severity

Medium

Status

✅ Resolved

Resolution Version

v1.9.14

Discovery Context

This finding was discovered while tracing the full downstream dependency chain for MG-AUD-008.

It is scientifically related to the exact-element-membership defect class resolved by MG-AUD-004, but occurs in a separate consumer and affects community-summary metadata rather than discovery scoring.

Affected Components

- DiscoveryGraphBuilder
- DiscoveryGraphAnalyticsService
- DiscoveryGraphNode schema
- discovery graph node metadata
- community analytics responses
- community `dominant_elements`

Root Cause

`DiscoveryGraphAnalyticsService._summarize_community()` determined element membership by checking configured element-symbol strings directly against chemical formula text.

Conceptually:

`element in formula`

Chemical formulas are structured scientific data, so raw substring membership is not a valid general element-membership test.

The current hard-coded symbol set limited obvious collisions, but correctness depended on the configured vocabulary remaining collision-free and could fail as supported elements expanded.

Scientific Impact

Community `dominant_elements` could become incorrect when an element symbol was matched as a substring rather than as an exact chemical element.

The affected field is researcher-facing descriptive analytics metadata.

Dependency analysis confirmed that the substring-derived element counts did not feed:

- community membership
- connected components
- greedy modularity detection
- centrality calculations
- hub selection
- average quality
- average edge score
- community importance score

Therefore, no numeric graph-ranking or community-scoring defect was confirmed.

Characterization Verification

Two pre-remediation characterization boundaries were established.

1. Graph-builder nodes did not expose canonical `elements`, producing a missing-field failure.

2. A deliberate mismatch between formula text and canonical node membership proved that community analytics trusted formula text instead of structured element metadata.

The analytics characterization returned formula-derived Li membership when canonical node metadata specified Na membership.

Resolution

✓ `DiscoveryGraphBuilder` now attaches canonical `elements` to graph nodes.

✓ Canonical elements are derived from persisted `MaterialElement → Element.symbol` relationships.

✓ The graph builder reuses its existing element map.

✓ No additional database query is introduced.

✓ `DiscoveryGraphAnalyticsService` now counts community elements from `node_data["elements"]`.

✓ Raw formula substring matching was removed from community element counting.

✓ `DiscoveryGraphNode` exposes the additive canonical `elements` field.

✓ Existing graph topology and numeric analytics calculations are unchanged.

✓ API compatibility is preserved.

Regression Verification

✓ Graph-builder canonical-element characterization test

✓ Community canonical-membership characterization test

✓ Existing graph-builder focused tests

✓ Existing graph-analytics focused tests

✓ Greedy modularity community endpoint verification

✓ LiFePO4 → Na/phosphate reference workflow

Endpoint Verification

Greedy modularity community analytics returned two communities.

Community 1 contained materials 5–10 and reported:

`dominant_elements = ["Fe", "O", "P", "Na", "Li"]`

This matches exact canonical membership frequencies:

- Fe, O, P in all six materials
- Na in materials 6–10
- Li only in material 5

Community 2 contained materials 1–2 and reported:

`dominant_elements = ["Fe", "Li", "O", "P"]`

Community numeric outputs remained internally consistent.

Community 1:

- average_quality_score = 14.83
- average_edge_score = 93.33
- density = 1
- average_degree = 5
- community_importance_score = 78.36

Community 2:

- average_quality_score = 13.95
- average_edge_score = 90
- density = 1
- average_degree = 1
- community_importance_score = 72.48

Scientific Changes

LiFePO4 Criticality

No change (32.0)

LiFePO4 Risk

No change (2.833)

Scientific Usefulness

No change (95.65)

Material Quality Path Contribution

No change (14.65)

Reason

MG-AUD-049 corrects community descriptive element metadata only.

The LiFePO4 → Na/phosphate objective workflow, candidate ranking, transition semantics, shared-element semantics, pathway ranking, and scientific usefulness remain unchanged.

Performance Improvements

✓ Existing graph-builder element map reused.

✓ No additional database queries introduced.

Breaking API

No.

The canonical graph-node `elements` field is additive.

Database Migration

No.

Lessons Learned

Chemical element membership must come from structured scientific representations rather than raw formula substrings.

A defect discovered during remediation of another finding should be tracked independently when it has a distinct root-cause location and downstream impact.

Descriptive scientific metadata requires the same correctness discipline as numeric scoring because researchers may use both for interpretation and decision support.

Related Findings

MG-AUD-004 — Exact chemical element membership in discovery reasoning.

MG-AUD-008 — Partial risk evidence and favorable quality bonus eligibility.

Related Scientific Principles

Principle 10

Principle 11

Related ADR

ADR-002

---

# MG-AUD-050

Title

Research objective explainability does not distinguish path-wide and endpoint-specific objective satisfaction.

Severity

Medium

Status

✅ Resolved

Resolution Version

v1.9.16

Affected Components

- ScientificPathwayAnalysisService
- ResearchObjectiveExplorationService
- Scientific pathway response schemas

Root Cause

Scientific pathway responses exposed deterministic objective satisfaction
only from a pathway-wide perspective.

Researchers could determine whether requested avoided or preferred elements
appeared somewhere along the pathway, but could not independently determine
whether the final endpoint material itself satisfied the requested research
objective.

Scientific Impact

Researcher explainability was incomplete.

Path-wide deterministic transition evidence and endpoint material composition
represent different scientific concepts and should be evaluated separately.

Deterministic scoring remained scientifically correct.

Resolution

✓ Preserved existing path-wide objective satisfaction.

✓ Added endpoint-specific objective evaluation.

✓ Endpoint evaluation now reports:

- endpoint_matched_avoid_elements
- endpoint_unmatched_avoid_elements
- endpoint_matched_prefer_elements
- endpoint_unmatched_prefer_elements
- endpoint_avoid_coverage
- endpoint_prefer_coverage
- endpoint_overall_coverage
- endpoint_status
- endpoint_interpretation

✓ Endpoint evaluation uses exact chemical element membership.

✓ Existing deterministic scoring preserved.

✓ Existing pathway ranking preserved.

✓ Public API compatibility preserved.

Characterization Verification

Before remediation

Only path-wide objective satisfaction was available.

Researchers could not distinguish pathway transitions from endpoint material
composition.

After remediation

Scientific pathway responses independently report:

- deterministic path-wide objective satisfaction
- endpoint-specific objective satisfaction

Characterization tests confirmed these remain independent concepts.

Regression Verification

✓ Scientific pathway analysis tests

✓ Research objective exploration tests

✓ Endpoint verification

✓ Characterization tests

✓ Full regression suite

✓ LiFePO4 → Na/phosphate reference workflow

Reference Workflow Verification

Objective

avoid:

- Li

prefer:

- Na

Endpoint materials

- Na3Fe3(PO4)4
- Na9Fe3P8O29
- NaFeP2O7
- NaFePO4
- Na3Fe(PO4)2

All endpoint materials:

- exclude Li
- contain Na

Path-wide objective satisfaction

Complete.

Endpoint-specific objective satisfaction

Complete.

Scientific Changes

LiFePO4 Criticality

No change (32.0)

LiFePO4 Risk

No change (2.833)

Scientific Usefulness

95.65

Reason

The remediation introduces endpoint-specific explainability only.

Deterministic scoring, pathway generation, and scientific ranking remain
unchanged.

Performance Improvements

✓ No measurable performance impact.

✓ No additional database queries introduced.

Breaking API

No.

Endpoint objective fields are additive.

Existing path-wide fields remain unchanged.

Database Migration

No.

Lessons Learned

Pathway reasoning and endpoint evaluation answer different scientific
questions.

Scientific explainability should distinguish transition evidence from
endpoint material composition while preserving deterministic scoring.

Related Scientific Principles

Principle 10

Principle 11

Related ADR

ADR-002

---

# MG-AUD-051

Title

Comparative research outputs used ranking as pathway identity.

Severity

Medium

Status

✅ Resolved

Resolution Version

v1.9.17

Affected Components

- ScientificPathwayAnalysisService
- ComparativeResearchIntelligenceService
- ResearchObjectiveExplorationService
- Scientific pathway schemas
- Comparative research schemas

Root Cause

Competition rank was used as both ordering and identity. Tied pathways therefore became ambiguous in comparative analyses.

Scientific Impact

Researchers could not uniquely reference tied pathways, and comparative aggregation could collapse distinct pathways sharing the same rank.

Resolution

✓ Added stable pathway_id.

✓ Added deterministic position.

✓ Preserved competition ranking semantics.

✓ Comparative summaries, pairwise comparisons, and element highlights now use pathway identity.

✓ Element aggregation tracks pathway_ids rather than ranks.

Regression Verification

✓ Scientific pathway tests

✓ Comparative intelligence tests

✓ Research route tests

✓ Full regression suite

Scientific Changes

LiFePO4 Criticality

No change (32.0)

LiFePO4 Risk

No change (2.833)

Scientific Usefulness

No change (95.65)

Reason

Identity and explainability remediation only.

Breaking API

No

Identity fields are additive.

Database Migration

No

Lessons Learned

Ordering, ranking, and identity represent different concepts and should remain independent in scientific systems.

Related Scientific Principles

Principle 10

Principle 11

Related ADR

ADR-002

---

# MG-AUD-012

Title

`framework_preserving` fallback lacked independent validation.

Severity

High

Status

✅ Resolved

Resolution Version

Post-v1.9.18

Affected Components

- DiscoverySubstitutionPathService
- DiscoveryTransitionValidator
- DiscoveryKBestPathService
- DiscoveryEdgeIntelligenceService
- DiscoveryPathRankingService
- Discovery transition API values

Root Cause

Elemental overlap and `shared_chemistry` evidence could be classified as
`framework_preserving`, although the system had no independent bonding,
structure-matching, or crystallographic validation. The validator also used
`framework_preserving` as its final fallback when no substitution-path evidence
was available.

Scientific Impact

The serialized transition value overstated the strength of the available
evidence. It could imply validated structural continuity where MaterialGraph
had established only shared-element continuity or no more specific transition
classification.

Resolution

✓ Renamed the qualifying element-overlap fallback to
`shared_element_continuity`.

✓ Changed the evidence-free validator fallback to `candidate_transition`.

✓ Updated K-best transition inference for `shared_chemistry` to emit
`shared_element_continuity`.

✓ Updated edge-intelligence and path-ranking branches to recognize the new
serialized transition value.

✓ Retained `preserved_framework` as a compatibility field while preserving its
element-overlap provenance and `structural_preservation_validated: false`
qualifier.

Regression Verification

✓ All focused service tests and the full regression suite passed locally.

✓ Production deployment and service restart succeeded after correcting the EC2
security-group SSH rule.

✓ Production discovery, chain, objective, and balanced-mode responses remained
operational and contained no `framework_preserving` transition value.

✓ Production responses retained evidence qualifiers and compatibility fields.

Verification Scope Note

The current production dataset exercised `alkali_substitution` and
`family_expansion`, but did not yield legitimate examples of
`shared_element_continuity` or `candidate_transition`. Those replacement
branches were verified by focused automated tests. Production endpoint checks
therefore establish deployment and general regression behavior, not direct
production-data coverage of both replacement branches.

Scientific Changes

Transition terminology changed to match evidence strength. Candidate admission,
score values, weights, and ranking logic did not change.

Breaking API

Affected serialized transition values changed from `framework_preserving` to
`shared_element_continuity` or `candidate_transition`, according to available
evidence. The response schema and fields did not change.

Database Migration

No.

Lessons Learned

Classification names are scientific claims. Element overlap, structural
preservation, and neutral fallback states must remain distinct even when their
initial numeric weights are intentionally preserved for compatibility.

Related Findings

MG-AUD-011

MG-AUD-013

Related ADR

ADR-002

---

# MG-AUD-013

Title

Framework scoring inherited elemental-overlap semantics.

Severity

High

Status

✅ Resolved

Resolution Version

Post-v1.9.18

Affected Components

- DiscoveryPathRankingService
- ResearchEvidenceIntelligenceService
- ScientificPathwayAnalysisService
- ComparativeResearchIntelligenceService
- Research objective and pathway response score breakdowns

Root Cause

The path-ranking dimension named `framework_preservation` was calculated from
shared elements across transitions. This composition-level evidence did not
validate bonding, crystallographic structure, site equivalence, or continuous
framework preservation through the path.

Scientific Impact

The numeric contribution represented elemental continuity, but its name could
lead researchers and downstream consumers to interpret it as independently
validated structural preservation.

Resolution

✓ Renamed the canonical score dimension to `shared_element_continuity`.

✓ Updated path-ranking output, research evidence provenance, scientific
pathway analysis, comparative intelligence, and positive test fixtures to use
the new dimension.

✓ Retained the established continuity weights while qualifying explanations as
elemental overlap and explicitly stating that structural preservation is not
validated.

✓ Preserved intentional negative regression assertions that ensure
`framework_preservation` is absent from score breakdowns.

Regression Corrections During Remediation

✓ Restored path efficiency to `EFFICIENCY_WEIGHT = 10.0` after a terminology
edit temporarily referenced the shared-element-continuity weight.

✓ Corrected empty-path scoring so zero transitions receive `0.0` path
efficiency instead of the one-hop bonus.

✓ Kept established score invariants unchanged: a representative full
single-hop alkali-substitution path scores `85.0`, and the verified two-hop
objective-exploration result scores `95.65`.

Regression Verification

✓ Focused path-ranking, evidence-semantics, and pathway-analysis tests passed.

✓ Full regression suite passed locally.

✓ Local objective exploration for material 5 returned `200 OK` with
`shared_element_continuity: 30`, total usefulness score `95.65`, and qualified
structural-uncertainty wording.

Production Verification

✓ Production verification passed on 2026-07-23 using objective exploration for
material 5.

✓ The response retained total usefulness score `95.65` with
`shared_element_continuity: 30`.

✓ The score breakdown contained no `framework_preservation` field.

✓ Evidence remained qualified as `preservation_basis: element_overlap` with
`structural_preservation_validated: false`, and explanations made no unsupported
structural-preservation claim.

Scientific Changes

The semantic label and evidence wording changed to match the available
composition-level evidence. Final numeric weights and valid pathway rankings
did not change.

Breaking API

Yes. The score-breakdown key changed from `framework_preservation` to
`shared_element_continuity`. Response structure and numeric score values remain
unchanged.

Database Migration

No.

Lessons Learned

Terminology-only migrations must be protected by focused numeric-invariant and
empty-input tests. Elemental overlap and validated structural preservation must
remain separate concepts in score keys, provenance, and explanations.

Related Findings

MG-AUD-005

MG-AUD-011

MG-AUD-012

Related ADR

ADR-002