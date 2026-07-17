# MaterialGraph Architecture & Implementation Audit Resolution

Version: 1.1
Last Updated: 2026-07-17

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

