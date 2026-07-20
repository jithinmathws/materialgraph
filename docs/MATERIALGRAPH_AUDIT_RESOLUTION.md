# MaterialGraph Architecture & Implementation Audit Resolution

Version: 1.2
Last Updated: 2026-07-18

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
