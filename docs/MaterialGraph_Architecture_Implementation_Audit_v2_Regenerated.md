# MaterialGraph Architecture & Implementation Audit

**Version:** v2 --- Restructured Living Audit\
**Status:** Active\
**Project stage:** Post-v1.9.6\
**Primary regression trace:** LiFePO4 → Na/phosphate objective\
**Source:** Refactored from the complete v1 implementation audit and
later code/live-data investigations

------------------------------------------------------------------------

# 0. Executive Summary

MaterialGraph has a strong deterministic, service-composed architecture
with thin API routes, bounded exploration, explicit reasoning paths, and
a growing evidence layer.

The audit also identified several upstream correctness and semantic
issues that propagate into discovery, ranking, evidence, comparison, and
public API responses.

## Architecture Health

  ---------------------------------------------------------------------
  Area                               Assessment
  ---------------------------------- ----------------------------------
  Service composition                Strong

  Deterministic reasoning            Strong

  Explainability direction           Strong, with provenance gaps

  Production safeguards              Strong

  Scientific terminology             Needs qualification

  Evidence semantics                 Needs separation of internal
                                     support and external evidence

  Data correctness                   One confirmed import-path defect

  Audit confidence                   High for confirmed findings below
  ---------------------------------------------------------------------

## Highest-Priority Confirmed Findings

### P0 --- Correctness (Resolved)

1.  **MG-AUD-001 - Resolved (v1.9.7) --- Materials Project composition weights are discarded
    on import.**
2.  **MG-AUD-002 - Resolved (v1.9.8) --- Unknown criticality evidence can become favorable
    numeric zero.**
3.  **MG-AUD-003 - Resolved (v1.9.9) --- Candidate screening still interprets unknown risk
    as zero penalty.**
4.  **MG-AUD-004 - Resolved (v1.9.10) --- Raw formula substring membership can corrupt
    element-constraint scoring.**

### P1 --- Cross-Layer Semantics and Explainability

5.  **MG-AUD-005 - Resolved (v1.9.11) --- `preserved_framework` represents element overlap,
    not validated structural preservation.**
6.  **MG-AUD-006 - Resolved (v1.9.12) --- Discovery score and merged score breakdown used
    incompatible aggregation semantics.**
7.  **MG-AUD-007 - Resolved (v1.9.13) --- Repeated candidate encounters could accumulate a
    mislabeled source-diversity bonus.**
8.  **MG-AUD-008 - Resolved (v1.9.14) --- Partial risk evidence can unlock full low-risk
    bonus eligibility.**
9. **MG-AUD-009 - Resolved (v1.9.15) --- Multi-element research objectives now propagate 
    through deterministic pathway evaluation and scoring.**
10. **MG-AUD-010 --- Exact ties are handled inconsistently across comparison and 
    ranking layers.**
11. **MG-AUD-049 - Resolved (v1.9.14) --- Community analytics used raw formula 
    substring matching for element membership.**
12. **MG-AUD-050 --- Scientific pathway explainability does not distinguish path-wide 
    and endpoint-specific objective satisfaction.**

## Current Data Reality

Development database inspection found:

-   760 total materials
-   28 Materials Project materials
-   732 `mp-test-*` materials
-   3022 `material_elements` rows
-   all 3022 rows currently have `fraction = 1.0`
-   all 28 real Materials Project records retain structured
    `raw_data["composition"]`
-   the 732 test records generally lack structured composition

Therefore, the importer defect is confirmed in live development data.
Correct fractions are recoverable for all 28 real imported materials.

## Immediate Engineering Recommendation

Correct upstream composition weighting and missing-evidence semantics
before expanding research intelligence.

------------------------------------------------------------------------

# 1. Audit Philosophy

The audit follows this process:

``` text
observe implementation
→ trace upstream and downstream dependencies
→ separate fact from interpretation
→ inspect enough code and data
→ classify confidence
→ update audit
→ remediate only with characterization and regression tests
```

## Decision Rules

-   Do not call correlated signals "double-counting" until provenance
    and policy intent are understood.
-   Do not infer scientific invalidity from bounded production behavior
    alone.
-   Do not invent arbitrary weights or epsilon thresholds to break ties.
-   Correct source semantics before correcting downstream wording.
-   Preserve compatibility where public contracts already expose
    problematic fields.
-   No v1 finding is removed unless it is explicitly merged, resolved,
    or superseded.

## Confidence Levels

  Level        Meaning
  ------------ ------------------------------------------------------
  Confirmed    Verified through implementation and/or live data
  High         Strong evidence; minor assumptions remain
  Medium       Plausible; further inspection required
  Low          Hypothesis only
  Resolved     Investigation completed
  Superseded   Earlier interpretation replaced by stronger evidence

------------------------------------------------------------------------

# 2. Architecture Overview

## Verified Flow

``` text
Research objective
    ↓
ScientificPathwayAnalysisService
    ↓
ResearchObjectiveService
    ↓
DiscoveryChainService
    ├── MaterialFamilyService
    ├── bounded candidate expansion
    └── DiscoveryTransitionValidator
    ↓
objective filtering
    ↓
DiscoveryPathRankingService
    ↓
MaterialQualityService
    ↓
ResearchEvidenceIntelligenceService
    ↓
ComparativeResearchIntelligenceService
    ↓
EndpointSensitiveResearchRankingService
    ↓
researcher-facing API
```

## Recommendation / Scenario Flow

``` text
MaterialNeighborService
    ↓
neighbor ranking
    ↓
top-N truncation
    ↓
MaterialSimilarityService
    ↓
MaterialRecommendationService
    ↓
ScenarioPolicyEvaluator
```

------------------------------------------------------------------------

# 3. Verified Architecture Strengths

-   Thin route boundaries; no hidden reranking was observed.
-   Existing services are composed rather than reimplemented.
-   Deterministic reasoning is preserved.
-   Bounded exploration includes depth guards, per-node limits, cycle
    prevention, result limits, and caches.
-   Structured element/application IDs are used in family and neighbor
    services.
-   Risk signals now expose known/unknown state, element coverage,
    counts, completeness, and unknown elements.
-   v1.9.6 preserves equal-evidence ties in the reference research
    trace.
-   Responses expose score breakdowns, assumptions, evidence state,
    comparisons, and researcher decision boundaries.
-   Material-element duplicate pairs are prevented by a unique
    `(material_id, element_id)` constraint.
-   Bulk criticality, risk, and quality methods exist in several core
    paths.

------------------------------------------------------------------------

# 4. Confirmed Findings

## 4.1 Correctness and Data Integrity

------------------------------------------------------------------------

## MG-AUD-001 --- Materials Project Import Discards Composition Weighting

**Status:** Resolved\
**Confidence:** Confirmed\
**Priority:** P0\
**Evidence:** Implementation + live development database\
**Last verified:** 2026-07-13
**Resolution version:** v1.9.7

### Finding

The Materials Project import path creates every `MaterialElement` row
with:

``` text
fraction = 1.0
```

`MaterialCriticalityService` later treats this field as an aggregation
weight:

``` text
Σ(element_criticality × fraction) / Σ(fraction)
```

### Live Data

-   3022 `material_elements` rows
-   all 3022 have `fraction = 1.0`
-   LiFePO4 is stored as Fe=1, Li=1, O=1, P=1
-   28 real Materials Project materials contain structured composition
-   732 test materials generally do not

### Consequence

For imported LiFePO4:

``` text
current criticality
= (C_Li + C_Fe + C_P + C_O) / 4
```

rather than stoichiometric weighting:

``` text
Li = 1/7
Fe = 1/7
P  = 1/7
O  = 4/7
```

### Affected Layers

-   criticality
-   quality
-   similarity
-   recommendation
-   discovery ranking
-   endpoint-sensitive analysis

### Recommended Action

1.  Fix future imports using `raw_data["composition"]`.
2.  Normalize structured composition to fractions summing to 1.
3.  Backfill the 28 real imported materials.
4.  Leave test records unchanged unless their tests require realistic
    fractions.
5.  Rerun criticality and reference-response regressions.

------------------------------------------------------------------------

## MG-AUD-002 --- Unknown Criticality Evidence Becomes Favorable Zero

**Status:** Resolved\
**Last verified:** 2026-07-13\
**Confidence:** Confirmed\
**Priority:** P0\
**Resolution version:** v1.9.8

### Finding

Two paths produce element criticality `0.0`:

-   no `ElementRiskProfile`
-   profile exists but all relevant dimensions are null

The element fraction remains in the material denominator.

``` text
missing criticality evidence
→ 0.0
→ weighted aggregation
→ apparently lower material criticality
```

### Impact

Unknown evidence can look like favorable low criticality.

### Dependencies

-   consumer inventory
-   evidence-aware criticality contract
-   compatibility strategy for numeric APIs

------------------------------------------------------------------------

## MG-AUD-003 --- Screening Uses Legacy Unknown-Risk-as-Zero Semantics

**Status:** Resolved\
**Last verified:** 2026-07-13\
**Confidence:** Confirmed\
**Priority:** P0\
**Resolution version:** v1.9.9

### Finding

`CandidateScreeningService` uses the legacy numeric risk API.

``` text
unknown risk
→ risk_score = 0.0
→ risk penalty = 0.0
→ favorable screening effect
```

The explanation can also present unknown risk as a real numeric zero.

### Propagation

``` text
screening
→ ranked candidates
→ CandidateComparisonService
→ pairwise winner
```

### Recommended Action

Migrate correctness-sensitive screening logic to evidence-aware risk
signals.

------------------------------------------------------------------------

## MG-AUD-004 --- Formula Substring Membership Corrupts Element Constraints

**Status:** Resolved\
**Last verified:** 2026-07-16\
**Confidence:** Confirmed\
**Priority:** P0\
**Resolution version:** v1.9.10

### Finding

Discovery scoring uses string membership:

``` text
prefer_element in formula
avoid_element in formula
avoid_element not in formula
```

Unsafe examples:

-   `N` in `Na...`
-   `S` in `Si...`
-   `C` in `Ca...`

### Score Impact

-   preferred element: +25
-   avoided element removed: +25
-   avoided element present: -50

### Existing Safe Primitive

`chemical_formula.extract_elements()` and structured `MaterialElement`
membership already avoid the raw substring problem for simple membership
checks.

### Recommended Action

Pass structured element sets into scoring rather than formula strings.

------------------------------------------------------------------------

## MG-AUD-005 --- `preserved_framework` Is Element Overlap, Not Structural Preservation

**Status:** Resolved\
**Last verified:** 2026-07-16\
**Confidence:** Confirmed\
**Priority:** P1\
**Resolution version:** v1.9.11

### Finding

`DiscoveryTransitionValidator` derives `preserved_framework` from
source/target element-set intersection.

No independent analysis was found for:

-   crystallographic framework
-   bonding topology
-   coordination environment
-   motif preservation
-   site correspondence

### Propagation

``` text
element overlap
→ preserved_framework
→ transition explanation
→ objective filtering
→ path ranking
→ evidence/confidence
→ comparison
→ public API
```

### Resolution

✓ Introduced canonical `shared_elements` metadata.

✓ Preserved `preserved_framework` as a backward-compatible alias.

✓ Added `preservation_basis = "element_overlap"`.

✓ Added `structural_preservation_validated = false`.

✓ Qualified researcher-facing wording throughout discovery,
ranking, evidence, comparison, and research layers.

✓ Distinguished deterministic element continuity from validated
structural preservation while preserving scientific scores and API
compatibility.

### Regression Verification

✓ Transition validation tests

✓ Substitution path tests

✓ Scientific pathway tests

✓ Research evidence tests

✓ Comparative research tests

✓ Full regression suite

✓ LiFePO4 → Na/phosphate reference workflow

### Scientific Impact

Scientific semantics and evidence provenance improved.

No numerical scientific scores changed.

LiFePO4 Scientific Usefulness

95.65 → 95.65

------------------------------------------------------------------------

## MG-AUD-006 --- Discovery Score and Breakdown Arithmetic Diverge

**Status:** Resolved\
**Last verified:** 2026-07-17\
**Confidence:** Confirmed\
**Priority:** P1\
**Resolution version:** v1.9.12

### Finding

Candidate score merging used:

``` text
max(existing_score, incoming_score)
+ source diversity bonus
```

while score-breakdown fields were merged additively.

### Consequence

The final breakdown could materially exceed and fail to decompose
`discovery_score`.

### Resolution

✓ Candidate merging now preserves the score breakdown corresponding to
the winning score provenance.

✓ Contextual discovery paths and explanations continue to aggregate
across contributing candidate encounters.

✓ Substitution paths can still be populated by later candidate
encounters.

✓ Discovery score arithmetic is internally consistent:

``` text
sum(score_breakdown) == discovery_score
```

✓ Public API compatibility was preserved.

### Regression Verification

✓ Candidate merge characterization tests

✓ Discovery scoring tests

✓ Discovery candidate endpoint tests

✓ Discovery chain tests

✓ Full regression suite

✓ LiFePO4 → Na/phosphate reference workflow

### Scientific Impact

Explainability provenance is now consistent with the reported discovery
score.

LiFePO4 Scientific Usefulness

95.65 → 95.65

------------------------------------------------------------------------

## MG-AUD-007 --- Source Diversity Is Actually Repeated-Encounter Accumulation

**Status:** Resolved\
**Last verified:** 2026-07-17\
**Confidence:** Confirmed\
**Priority:** P1\
**Resolution version:** v1.9.13

### Finding

The source-diversity bonus previously incremented whenever an existing
candidate was encountered.

No distinct source identity was tracked, so repeated encounters could be
treated as additional source diversity.

### Resolution

✓ Candidate encounters now carry explicit source types.

✓ Distinct contributing source types are tracked internally during
candidate merging.

✓ Repeated encounters from the same source type do not increase the
source-diversity bonus.

✓ Source-diversity accounting is now:

``` text
1 distinct source  → 0 bonus
2 distinct sources → 10 bonus
3 distinct sources → 20 bonus
```

✓ Winning base discovery score provenance is tracked separately from the
accumulated source-diversity bonus.

✓ Aggregate scores that already contain a diversity bonus are not reused
as base scores during subsequent merges.

✓ Contextual discovery paths, explanations, and substitution paths
continue to aggregate independently from numeric score provenance.

✓ Internal source/base-score provenance fields are removed before public
API serialization.

✓ Public API compatibility was preserved.

### Regression Verification

✓ Repeated same-source encounter tests

✓ Distinct-source diversity tests

✓ Candidate merge characterization tests

✓ Winning-score provenance tests

✓ Exact-score tie tests

✓ Discovery candidate endpoint verification

✓ Substitution-path endpoint verification

✓ Full regression suite

✓ LiFePO4 → Na/phosphate reference workflow

### Scientific Impact

Source diversity now represents distinct discovery evidence channels
rather than repeated candidate encounters.

Scientific pathway scoring remains unchanged.

LiFePO4 Scientific Usefulness

95.65 → 95.65

------------------------------------------------------------------------

## MG-AUD-008 --- Partial Risk Evidence Can Unlock Full Low-Risk Bonus Eligibility

**Status:** Resolved\
**Last verified:** 2026-07-17\
**Confidence:** Confirmed\
**Priority:** P1\
**Resolution version:** v1.9.14

### Finding

If at least one material element had calculable risk:

``` text
risk_known = True
```

Coverage could still be below 1.0.

Before remediation, `MaterialQualityService` used `risk_known` and
`risk_score` for low-risk bonus eligibility without requiring complete
material-element risk coverage.

### Consequence

``` text
partial coverage
→ risk_known = True
→ low known-element average
→ same full low-risk bonus path as complete evidence
```

This allowed partial evidence to unlock favorable treatment equivalent to
complete evidence.

### Resolution

✓ Low-risk quality bonus eligibility is now coverage-aware.

✓ Full low-risk bonus eligibility requires complete material-element risk
evidence.

✓ Partial or unknown risk evidence cannot become favorable evidence.

✓ Existing risk evidence metadata remains available, including coverage,
known/unknown element counts, completeness, and unknown elements.

✓ Public API compatibility was preserved.

### Characterization Verification

A pre-remediation characterization boundary demonstrated that a material with
25% risk-profile coverage and a low known risk score could enter the full
low-risk bonus path.

The remediation changed only bonus eligibility semantics; evidence reporting
remained explicit.

### Regression Verification

✓ Material quality focused tests

✓ Partial-risk evidence characterization test

✓ Complete-risk evidence behavior

✓ Full regression suite

✓ LiFePO4 → Na/phosphate reference workflow

### Scientific Impact

Incomplete evidence no longer receives the same favorable low-risk quality
treatment as complete evidence.

The reference LiFePO4 workflow has complete risk evidence and therefore remains
unchanged.

LiFePO4 Scientific Usefulness

95.65 → 95.65

Material Quality Path Contribution

14.65 → 14.65

------------------------------------------------------------------------

## MG-AUD-009 --- Multi-Element Research Objectives Were Reduced to Single-Element Evaluation

**Status:** Resolved\
**Last verified:** 2026-07-18\
**Confidence:** Confirmed\
**Priority:** P1\
**Resolution version:** v1.9.15

### Finding

The public research objective API accepted collections of avoided and
preferred elements.

However, downstream deterministic pathway evaluation and objective-alignment
scoring only considered the first avoided element and the first preferred
element.

As a result, multi-element research objectives were effectively reduced to
single-element evaluation.

### Scientific Impact

Researchers specifying objectives such as:

```text
avoid:  Li, Co
prefer: Na, K
```

received deterministic scoring equivalent to:

```text
avoid:  Li
prefer: Na
```

Additional requested objective elements were ignored during objective
evaluation, pathway scoring, and researcher-facing explanations.

### Resolution

✓ Research objective evaluation now propagates complete avoided-element and
preferred-element collections throughout deterministic pathway analysis.

✓ Objective-alignment scoring now evaluates every requested objective
element.

✓ Scientific pathway responses expose structured objective satisfaction
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

### Regression Verification

✓ Research objective characterization tests

✓ Scientific pathway analysis tests

✓ Discovery path ranking tests

✓ Objective explainability tests

✓ Single-element endpoint verification

✓ Multi-element endpoint verification

✓ Full regression suite

✓ LiFePO4 → Na/phosphate reference workflow

### Scientific Impact

Single-element objective

Scientific usefulness

95.65 → 95.65

Multi-element objective

Objective alignment

12.5 (verified proportional deterministic alignment)

Scientific usefulness

83.15 (verified)

### Remaining Work

An additional researcher explainability opportunity was identified during
verification.

Current objective satisfaction correctly represents deterministic path-wide
objective fulfillment.

Endpoint-specific objective satisfaction has been recorded separately as
MG-AUD-050.

------------------------------------------------------------------------

## MG-AUD-010 --- Tie Handling Is Inconsistent

**Status:** Confirmed\
**Confidence:** Confirmed\
**Priority:** P1

### Findings

-   research comparative layers can preserve equal-score ties
-   `CandidateComparisonService` selects material A on exact equality
    using `>=`
-   some top-ranked and highest-readiness summaries select one
    representative from a tie
-   several sorts lack a final deterministic non-scientific key

### Rule

Stable ordering and scientific winning are different concepts.

A deterministic key may stabilize output, but should not imply
scientific superiority.

------------------------------------------------------------------------

## 4.2 Scientific and Domain Semantics

------------------------------------------------------------------------

## MG-AUD-011 --- Framework Explanations Overstate Evidence

**Status:** Confirmed\
**Confidence:** Confirmed\
**Priority:** P1

Shared elements can become wording such as:

-   "preserving Fe-O-P chemistry"
-   "shares phosphate framework"

The implementation establishes membership overlap, not preserved bonding
or structure.

------------------------------------------------------------------------

## MG-AUD-012 --- `framework_preserving` Fallback Lacks Independent Validation

**Status:** Confirmed\
**Confidence:** Confirmed\
**Priority:** P1

The transition type can be emitted without independent
structural-preservation evidence.

------------------------------------------------------------------------

## MG-AUD-013 --- Framework Scoring Inherits Overlap Semantics

**Status:** Confirmed\
**Confidence:** Confirmed\
**Priority:** P1

Observed path-ranking contribution:

-   P and O common: 30/30
-   O common: 21/30
-   any common element: 15/30
-   none: 0/30

The numeric precision exceeds the strength of the underlying structural
evidence.

------------------------------------------------------------------------

## MG-AUD-014 --- Preservation Can Be Satisfied by Union Across Transitions

**Status:** Confirmed\
**Confidence:** Confirmed\
**Priority:** P1

Example:

``` text
required = {Fe, P, O}
T1 preserves {Fe}
T2 preserves {P, O}
union satisfies required
```

This does not prove continuous preservation through the path.

------------------------------------------------------------------------

## MG-AUD-015 --- Objective Alignment Uses Path-Wide Events

**Status:** Confirmed\
**Confidence:** Confirmed\
**Priority:** P1

Removed and introduced elements are unioned across transitions.

A path can receive credit because an avoided element was removed
somewhere or a preferred element appeared somewhere without proving
endpoint satisfaction.

Distinguish:

-   transition event alignment
-   path continuity
-   endpoint satisfaction

------------------------------------------------------------------------

## MG-AUD-016 --- Avoid/Prefer Constraints Are Soft in Candidate Scoring

**Status:** Confirmed\
**Confidence:** Confirmed\
**Priority:** P1

-   preferred element present: bonus
-   avoided element absent: bonus
-   avoided element present: penalty

An avoided-element candidate can remain if other sources outweigh the
penalty.

------------------------------------------------------------------------

## MG-AUD-017 --- Strict Exploration Does Not Guarantee Hard Rejection

**Status:** Confirmed\
**Confidence:** Confirmed\
**Priority:** P1

Avoided-element violations can remain with penalties and warnings.

Hard versus soft semantics must be defined explicitly.

------------------------------------------------------------------------

## MG-AUD-018 --- Family Relationships Are Composition Heuristics

**Status:** Confirmed\
**Confidence:** Confirmed\
**Priority:** P1

Key rules:

-   `shared_chemistry`: at least 3 shared elements
-   `transition_metal_related`: at least one shared configured
    transition metal
-   `phosphate_related`: base contains P; candidate contains P and O
-   `oxide_related`: both contain O
-   `alkali_substitution`: configured alkali-like sets differ and at
    least 3 elements are shared

These are deterministic and explainable, but are not validated
structural-family assignments.

------------------------------------------------------------------------

## MG-AUD-019 --- Family Taxonomy Includes Mg as Alkali

**Status:** Confirmed implementation; domain intent unverified\
**Confidence:** High\
**Priority:** P1

`ALKALI_ELEMENTS` includes Mg, although Mg is an alkaline-earth metal.

Verify intended domain policy and tests before remediation.

------------------------------------------------------------------------

## MG-AUD-020 --- Alkali Substitution Does Not Prove Mechanism

**Status:** Confirmed\
**Confidence:** Confirmed\
**Priority:** P1

The rule proves differing configured element sets plus shared elements.

It does not prove:

-   site equivalence
-   one-for-one substitution
-   charge compensation
-   structural compatibility
-   actual substitution mechanism

------------------------------------------------------------------------

## 4.3 Evidence, Risk, Criticality, and Quality

------------------------------------------------------------------------

## MG-AUD-021 --- Risk and Criticality Share Upstream Evidence

**Status:** Confirmed\
**Confidence:** Confirmed\
**Priority:** P1

Both use:

-   supply risk
-   geopolitical risk
-   toxicity

Criticality additionally uses abundance and inverted recyclability.

They are distinct metrics, but not independent evidence dimensions.

------------------------------------------------------------------------

## MG-AUD-022 --- Risk and Criticality Aggregate Differently

**Status:** Confirmed\
**Confidence:** Confirmed\
**Priority:** P1

-   risk: equal average across calculable elements
-   criticality: `MaterialElement.fraction`-weighted average

Do not unify them without defining metric intent.

------------------------------------------------------------------------

## MG-AUD-023 --- Partial Criticality Profiles Look Complete

**Status:** Confirmed\
**Confidence:** Confirmed\
**Priority:** P1

A criticality score can be computed from one available dimension without
dimension-level coverage metadata.

------------------------------------------------------------------------

## MG-AUD-024 --- Risk Completeness Measures Element Coverage Only

**Status:** Confirmed\
**Confidence:** Confirmed\
**Priority:** P1

`risk_evidence_complete` means each material element produced some
calculable risk score.

It does not prove all expected dimensions are present.

Two distinct coverage layers exist:

1.  material-element coverage
2.  profile-dimension coverage

------------------------------------------------------------------------

## MG-AUD-025 --- Legacy Numeric Risk APIs Retain Unknown → 0.0

**Status:** Confirmed and intentional\
**Confidence:** Confirmed\
**Priority:** P1

Legacy compatibility APIs preserve numeric zero for unknown risk.

Correctness-sensitive consumers must use evidence-aware signals.

------------------------------------------------------------------------

## MG-AUD-026 --- Material Quality Scale Is Intentionally 0--15

**Status:** Resolved\
**Confidence:** Confirmed

`QUALITY_SCORE_MAX = 15.0`.

Allocation:

-   stable flag: 5.25
-   very low energy above hull: 5.25
-   low criticality: 2.25
-   low known risk: 2.25

No missing multiplication bug was found.

------------------------------------------------------------------------

## MG-AUD-027 --- Stability and Energy Are Imported Separately but Reused

**Status:** Confirmed behavior; policy open\
**Confidence:** Confirmed implementation / Medium policy\
**Priority:** P2

`is_stable` and `energy_above_hull` are imported separately from
Materials Project.

Both are rewarded in:

-   quality
-   similarity
-   recommendation

Repeated weighting is confirmed. Scientific appropriateness remains a
policy question.

------------------------------------------------------------------------

## MG-AUD-028 --- Internal Deterministic Support Can Look Like Scientific Evidence

**Status:** Confirmed\
**Confidence:** Confirmed\
**Priority:** P1

Framework-derived and other internal signals can increase
evidence/readiness even when external evidence is absent.

Future semantics should distinguish:

-   internal support strength
-   external evidence readiness
-   evidence coverage
-   validation readiness

------------------------------------------------------------------------

## MG-AUD-029 --- Risk Coverage Is Not Fully Propagated to Endpoint Evidence

**Status:** Confirmed\
**Confidence:** Confirmed\
**Priority:** P1

Equal numeric risk values can represent different evidence coverage
states.

Values and coverage should travel together when downstream decisions
depend on them.

------------------------------------------------------------------------

## 4.4 Discovery, Ranking, and Search Space

------------------------------------------------------------------------

## MG-AUD-030 --- Bounded Search Shapes the Opportunity Set

**Status:** Confirmed\
**Confidence:** Confirmed\
**Priority:** P2

-   objective filtering occurs after bounded chain generation
-   completed-chain limit shapes discovery, not only presentation
-   candidate expansion is bounded per node
-   search order can affect which opportunities survive

``` text
production search bounds ≠ scientific completeness
```

Do not remove production guards blindly.

------------------------------------------------------------------------

## MG-AUD-031 --- Family Ordering Can Affect Bounded Discovery

**Status:** Confirmed\
**Confidence:** Confirmed\
**Priority:** P2

Family candidates are ordered by:

1.  relationship-label count
2.  shared-element count

Correlated labels derived from the same composition facts can multiply
search priority.

------------------------------------------------------------------------

## MG-AUD-032 --- Equal-Key Family Ordering Lacks a Final Tie-Breaker

**Status:** Confirmed\
**Confidence:** Confirmed\
**Priority:** P2

Equal-key candidates can inherit database-return order.

Under bounded expansion, this can affect which chains survive.

------------------------------------------------------------------------

## MG-AUD-033 --- Recommendation Pipeline Contains Irreversible Preselection

**Status:** Confirmed\
**Confidence:** Confirmed\
**Priority:** P2

``` text
structured neighbors
→ neighbor ranking
→ top-N truncation
→ similarity scoring
→ recommendation scoring
→ scenario evaluation
```

Candidates excluded before similarity scoring cannot be recovered later.

The upstream and similarity stages share the same 2:3
element/application weighting ratio, which makes the gate coherent but
still irreversible.

------------------------------------------------------------------------

## MG-AUD-034 --- Recommendation Defaults to Lower Criticality

**Status:** Confirmed behavior; policy open\
**Confidence:** Confirmed implementation\
**Priority:** P2

`get_recommendations()` defaults `prefer_lower_criticality=True`.

Scenario recommendations also force this preference in their base
recommendation stage.

Whether this is appropriate for every objective remains open.

------------------------------------------------------------------------

## MG-AUD-035 --- Similarity and Recommendation Use Different Criticality Policies

**Status:** Confirmed\
**Confidence:** Confirmed\
**Priority:** P2

-   similarity tie ordering prefers smaller absolute criticality
    difference
-   recommendation scoring prefers lower criticality

These are layered policies, not necessarily contradictions.

------------------------------------------------------------------------

## MG-AUD-036 --- Criticality Direction Uses Risk Terminology

**Status:** Confirmed\
**Confidence:** Confirmed\
**Priority:** P1

Criticality deltas produce:

-   `LOWER_RISK`
-   `HIGHER_RISK`
-   `SAME_RISK`

This is a terminology/contract mismatch.

------------------------------------------------------------------------

## MG-AUD-037 --- Recommendation Reasons Mix Contributors and Context

**Status:** Confirmed\
**Confidence:** Confirmed\
**Priority:** P1

Reasons can:

-   mention criticality when the preference flag is disabled
-   omit the low-energy score contribution
-   include shared elements/applications as context even when not
    directly added in recommendation scoring

Contributor facts and contextual facts are not distinguished.

------------------------------------------------------------------------

## MG-AUD-038 --- Path Efficiency Is Hop-Count Based

**Status:** Confirmed\
**Confidence:** Confirmed\
**Priority:** P2

Equal-hop paths receive equal path-efficiency contributions,
contributing to score collapse.

------------------------------------------------------------------------

## MG-AUD-039 --- Path Material Quality Is Averaged Across the Path

**Status:** Confirmed\
**Confidence:** Confirmed\
**Priority:** P2

``` text
A → B → C
path quality = average(quality(A), quality(B), quality(C))
```

Shared bases/intermediates can dilute endpoint differences.

------------------------------------------------------------------------

## MG-AUD-040 --- Exploration Attribution Can Use Future Transitions

**Status:** Confirmed\
**Confidence:** Confirmed\
**Priority:** P1

For `A → B → C`, candidate B can receive reasons or bonuses using
`B → C`, even though that transition did not produce B.

------------------------------------------------------------------------

## 4.5 Comparison, Endpoint Ranking, and Contracts

------------------------------------------------------------------------

## MG-AUD-041 --- Endpoint Ranking Uses Implicit Lexicographic Policy

**Status:** Confirmed\
**Confidence:** Confirmed\
**Priority:** P2

Ordering:

``` text
quality
→ stability
→ energy above hull
→ criticality
→ risk
→ evidence readiness
```

Earlier dimensions dominate later ones.

Do not replace with weighted scoring without policy justification.

------------------------------------------------------------------------

## MG-AUD-042 --- Exact Numeric Differences Can Split Evidence Groups

**Status:** Confirmed\
**Confidence:** Confirmed\
**Priority:** P2

Tiny numeric differences can separate endpoints without a defined
precision or meaningful-difference policy.

Do not add arbitrary epsilon thresholds.

------------------------------------------------------------------------

## MG-AUD-043 --- Comparative Summaries Are Not Uniformly Tie-Aware

**Status:** Confirmed\
**Confidence:** Confirmed\
**Priority:** P1

Some layers preserve ties, while:

-   `top_ranked_pathway`
-   highest-readiness summaries
-   legacy candidate comparison

can select one representative.

------------------------------------------------------------------------

## MG-AUD-044 --- Comparison Conflates Filtered and Unavailable Candidates

**Status:** Confirmed\
**Confidence:** Confirmed\
**Priority:** P2

If either candidate does not survive screening, comparison returns no
result without distinguishing:

-   missing material
-   filtered by stability
-   filtered by energy threshold
-   otherwise unavailable

------------------------------------------------------------------------

## MG-AUD-045 --- API Contracts Are Under-Typed or Semantically Broader Than Implementation

**Status:** Confirmed/open mix\
**Confidence:** High\
**Priority:** P2

Issues include:

-   multi-element objective promise exceeds scalar handling
-   requested `preserve_elements` differs from inferred
    `preserved_framework`
-   evidence readiness is an unconstrained string
-   confidence scope is ambiguous
-   nested quality/comparison structures are under-typed
-   objective validation remains open for casing, invalid symbols,
    empties, and contradictions

Type contracts should strengthen after semantic stabilization.

------------------------------------------------------------------------

## 4.6 Production and Performance

------------------------------------------------------------------------

## MG-AUD-046 --- Family Discovery Performs Global Scans

**Status:** Confirmed\
**Confidence:** Confirmed\
**Priority:** P2

Each family request loads the global material-element map and scans
non-test materials in Python.

Benchmark before redesign.

------------------------------------------------------------------------

## MG-AUD-047 --- Candidate Screening Has N+1 Access Patterns

**Status:** Confirmed\
**Confidence:** Confirmed\
**Priority:** P2

Screening loads all materials, then performs per-material:

-   element lookup
-   risk lookup

Bulk risk capabilities already exist.

------------------------------------------------------------------------

## MG-AUD-048 --- Candidate Service Duplicates Global Element-Map Loading

**Status:** Confirmed\
**Confidence:** Confirmed\
**Priority:** P2

`MaterialFamilyService` and `DiscoveryCandidateService` can each load
global material-element mappings in the same request path.

------------------------------------------------------------------------

## MG-AUD-049 --- Community Analytics Uses Raw Formula Substring Matching for Element Membership

**Status:** Resolved\
**Last verified:** 2026-07-17\
**Confidence:** Confirmed\
**Priority:** P2\
**Resolution version:** v1.9.14

### Discovery Context

This finding was discovered while tracing the downstream dependency chain for
MG-AUD-008.

It belongs to the same general exact-element-membership defect class addressed
by MG-AUD-004, but occurs in a separate consumer and affects community-summary
metadata rather than discovery scoring.

### Finding

`DiscoveryGraphAnalyticsService._summarize_community()` determined configured
element membership by checking raw element-symbol substrings against chemical
formula text.

Conceptually:

``` text
element in formula
```

Chemical formulas are structured scientific data. Raw substring membership is
not a valid general exact-element-membership test.

The configured symbol set limited obvious collisions in the current dataset,
but the implementation was structurally unsafe and could misclassify membership
as the supported element vocabulary expanded.

### Impact

The affected dependency chain was:

``` text
formula substring membership
→ element_counts
→ dominant_elements
→ researcher-facing community summary
```

Dependency inspection confirmed that these counts did not feed:

- community membership
- connected-component detection
- greedy modularity community detection
- degree centrality
- betweenness centrality
- closeness centrality
- hub selection
- density
- average degree
- average quality score
- average edge score
- community importance score

No numeric graph-ranking or community-scoring defect was confirmed.

### Characterization Verification

Two pre-remediation boundaries confirmed the defect.

1. Discovery graph nodes did not expose canonical `elements` metadata.
2. A deliberate mismatch between formula text and canonical node membership
   showed that community analytics trusted formula text instead of structured
   element membership.

### Resolution

✓ `DiscoveryGraphBuilder` now attaches canonical `elements` metadata to graph
nodes.

✓ Canonical membership comes from persisted
`MaterialElement → Element.symbol` relationships.

✓ The existing graph-builder element map is reused.

✓ No additional database query is introduced.

✓ `DiscoveryGraphAnalyticsService` now counts community elements from exact
`node_data["elements"]` membership.

✓ Raw formula substring matching was removed from community element counting.

✓ `DiscoveryGraphNode` exposes the additive canonical `elements` field.

✓ Existing graph topology and numeric analytics calculations are unchanged.

✓ API compatibility was preserved.

### Regression Verification

✓ Graph-builder canonical-element characterization test

✓ Community canonical-membership characterization test

✓ Existing focused graph-builder tests

✓ Existing focused graph-analytics tests

✓ Greedy modularity community endpoint verification

✓ LiFePO4 → Na/phosphate reference workflow

### Endpoint Verification

Greedy modularity community analytics returned two verified communities.

Community 1, containing materials 5–10, reported:

``` text
dominant_elements = ["Fe", "O", "P", "Na", "Li"]
```

This matches exact canonical membership frequencies:

- Fe, O, P in all six materials
- Na in materials 6–10
- Li only in material 5

Community 2, containing materials 1–2, reported:

``` text
dominant_elements = ["Fe", "Li", "O", "P"]
```

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

### Scientific Impact

Community descriptive element metadata now uses exact canonical membership.

LiFePO4 Criticality

32.0 → 32.0

LiFePO4 Risk

2.833 → 2.833

Scientific Usefulness

95.65 → 95.65

Material Quality Path Contribution

14.65 → 14.65

### Breaking API

No.

The canonical graph-node `elements` field is additive.

### Database Migration

No.


------------------------------------------------------------------------


## MG-AUD-050 --- Scientific Pathway Explainability Does Not Distinguish Path-Wide and Endpoint-Specific Objective Satisfaction

**Status:** Open\
**Confidence:** Confirmed\
**Priority:** P2

### Discovery Context

This finding was identified during implementation and verification of
MG-AUD-009.

MG-AUD-009 correctly propagates multi-element research objectives through
deterministic pathway evaluation.

During endpoint verification it became apparent that researcher-facing
objective satisfaction currently summarizes deterministic path-wide
objective fulfillment but does not independently evaluate the final
endpoint material.

### Finding

Scientific pathway responses expose:

- requested objective elements
- matched objective elements
- unmatched objective elements
- objective coverage
- completion status

These values correctly describe deterministic path-wide transition
evidence.

However, they do not distinguish whether the endpoint material itself
satisfies those objectives.

### Scientific Impact

No scientific scoring defect exists.

Deterministic scoring, objective alignment, scientific usefulness,
transition plausibility, and pathway ranking are already correct.

The limitation affects researcher explainability only.

Researchers cannot immediately distinguish:

- objective satisfied somewhere along the pathway
- objective satisfied by the final endpoint material

### Proposed Remediation

Introduce endpoint-specific objective satisfaction metadata while
preserving the existing path-wide objective satisfaction.

Potential additions include:

- endpoint_matched_avoid_elements
- endpoint_unmatched_avoid_elements
- endpoint_matched_prefer_elements
- endpoint_unmatched_prefer_elements
- endpoint_objective_status

The existing path-wide semantics should remain unchanged.

### Expected Impact

Researcher interpretability improves.

No deterministic scoring changes.

No ranking changes.

No traversal changes.

No scientific usefulness changes.

### Performance

Expected to reuse existing endpoint material information.

No additional database queries should be required.

### Breaking API

No.

Implementation should be additive.

------------------------------------------------------------------------

# 5. Provisional Findings

## PROV-001 --- Repeated Stability/Energy Weighting

**Current evidence:** Reuse is confirmed across multiple stages.\
**Unknown:** intended scientific/policy meaning.\
**Action:** Do not modify until policy is documented.

## PROV-002 --- Bounded Top-N Completeness

**Current evidence:** Irreversible preselection is confirmed.\
**Unknown:** acceptable recall for intended researcher workflows.\
**Action:** benchmark and define scope before redesign.

## PROV-003 --- Mg Inclusion in Alkali Taxonomy

**Current evidence:** implementation includes Mg.\
**Unknown:** deliberate battery-domain grouping or taxonomy mistake.\
**Action:** inspect tests/domain intent.

## PROV-004 --- Exact Precision Policy

**Current evidence:** exact numeric inequality affects grouping.\
**Unknown:** meaningful precision from source data and models.\
**Action:** define provenance-aware precision policy.

------------------------------------------------------------------------

# 6. Resolved and Superseded Investigations

## RES-001 --- Unknown Risk Quality Bonus

**Question:** Did missing risk evidence receive a favorable quality
bonus?\
**Result:** Yes, previously.\
**Resolution:** Evidence-aware risk signal path introduced.\
**Remaining:** screening still uses the legacy numeric API.

## RES-002 --- Material Quality Scale

**Question:** Was a missing multiplication causing low quality scores?\
**Result:** No.\
**Resolution:** 0--15 is intentional.

## RES-003 --- `is_stable` Provenance

**Question:** Is `is_stable` derived locally from hull energy?\
**Result:** No in the inspected import path.\
**Resolution:** Both fields are imported separately from Materials
Project.

## RES-004 --- Duplicate Material-Element Rows

**Question:** Could duplicate rows inflate neighbor counts?\
**Result:** Database model has a unique `(material_id, element_id)`
constraint.\
**Resolution:** Closed unless migrations differ from the model.

## RES-005 --- Importer Scope

**Earlier concern:** The entire material dataset may consist of real
imported materials affected by the importer.\
**Result:** 28 real Materials Project materials and 732 test materials.\
**Resolution:** Real imported subset is small and fully reconstructable.

## RES-006 --- Structured Composition Availability

**Question:** Can correct fractions be reconstructed without formula
parsing?\
**Result:** Yes for all 28 real Materials Project materials via
`raw_data["composition"]`.\
**Resolution:** Use structured composition as the canonical backfill
source.

## RES-007 --- Current Formula Utility for Backfill

**Question:** Can `chemical_formula.extract_elements()` reconstruct
fractions?\
**Result:** No. It safely extracts membership but loses stoichiometry
and grouping.\
**Resolution:** Use it for membership only, not fraction reconstruction.

## RES-008 --- `mp_id` / `raw_data.material_id` Difference

**Question:** Is the systematic identifier difference a confirmed
importer bug?\
**Result:** No computation issue has been established.\
**Resolution:** Closed pending future lookup/provenance evidence.

## RES-009 --- All Family Labels Directly Add Candidate Score

**Earlier concern:** Every family label may directly multiply discovery
score.\
**Result:** Only `shared_chemistry` and `alkali_substitution` directly
add family score in `DiscoveryScoringService`.\
**Resolution:** Other labels still affect admission, paths,
explanations, and ordering.

------------------------------------------------------------------------

# 7. Remediation Roadmap

## Phase 1 --- Baseline Preservation

1.  Snapshot the LiFePO4 → Na/phosphate reference response.
2.  Add characterization tests for current criticality, screening,
    scoring, and tie behavior.
3.  Record current performance/query baselines.

## Phase 2 --- Data Correctness

``` text
Materials Project importer
→ normalized composition fractions
→ backfill 28 real materials
→ criticality regression
```

Actions:

1.  Normalize `raw_data["composition"]`.
2.  Fix importer.
3.  Backfill 28 real materials.
4.  Verify fractions sum to 1.
5.  Recompute and compare criticality outputs.

## Phase 3 --- Missing Evidence Correctness

1.  Introduce evidence-aware criticality signal semantics.
2.  Migrate screening from legacy numeric risk.
3.  ✓ Define and enforce coverage-aware low-risk bonus eligibility.
4.  Preserve legacy APIs only where necessary.

## Phase 4 --- Structured Objective Semantics

1. ✓ Replace formula substring membership.
2. ✓ Define multi-element avoid/prefer semantics.
3.  Define hard versus soft constraints.
4.  Implement endpoint-specific objective satisfaction (MG-AUD-050).
5.  Define preservation continuity semantics.

## Phase 5 --- Explainability Provenance

1.  ✓ Track candidate source identities.
2.  ✓ Align discovery score with breakdown semantics.
3.  ✓ Separate candidate scoring provenance from contextual discovery evidence.
4.  Make comparison outputs consistently tie-aware.

## Phase 6 --- Scientific Terminology

1.  ✓ Correct canonical framework semantics.
2.  Qualify family/substitution wording.
3.  Separate internal deterministic support from external evidence.
4.  Update public schemas with compatibility planning.

## Phase 7 --- Search and Performance

1.  Benchmark family global scans.
2.  Replace screening N+1 patterns.
3.  Evaluate bounded-search recall.
4.  Add stable non-scientific tie-breakers where needed.
5.  Retain production safety limits.

## Phase 8 --- Contract Strengthening

1.  Type nested response structures.
2.  Constrain readiness/status values.
3.  Clarify confidence scope.
4.  Add objective validation.
5.  Update documentation and examples.

------------------------------------------------------------------------

# 8. Verification Requirements

Every significant remediation must verify:

1.  **Correctness** --- explicit old/new behavior and focused tests.
2.  **Scientific semantics** --- names match evidence; inference is not
    presented as proof.
3.  **Cross-layer integration** --- downstream consumers remain
    consistent.
4.  **Production behavior** --- query count, latency, expansion, cache,
    and response-size impact.
5.  **Real-response regression** --- rerun the LiFePO4 → Na/phosphate
    trace.
6.  **Intentional differences** --- explain every changed score or
    ranking.

A changed score is not automatically a regression. An unexplained score
change is.

------------------------------------------------------------------------

# 9. Open Questions

1.  What evidence-aware criticality response should replace favorable
    zero without breaking legacy clients?
2.  Are repeated stability and energy terms intentional policy?
3.  What are the final hard/soft semantics for multi-element objectives?
4.  What constitutes continuous preservation across a path?
5.  What precision is scientifically meaningful for endpoint comparison?
6.  What recall is acceptable for bounded recommendation/scenario pools?
7.  How should internal support and external evidence be represented
    separately?
8.  Which remaining consumers use legacy numeric risk/criticality APIs?
9.  Should test materials receive parsed composition fractions or remain
    lightweight fixtures?

------------------------------------------------------------------------

# 10. Investigation Log

## 2026-07-11 --- Criticality and Risk

-   inspected criticality and risk computations
-   confirmed shared upstream evidence
-   confirmed missing criticality → zero
-   confirmed partial risk coverage semantics
-   identified legacy risk consumers

## 2026-07-11 --- Family and Candidate Generation

-   confirmed structured family membership
-   confirmed heuristic family terminology
-   confirmed candidate ordering and tie behavior
-   confirmed formula substring scoring
-   confirmed source-diversity accumulation
-   confirmed score/breakdown divergence

## 2026-07-11 --- Recommendation, Similarity, and Neighbor Pipeline

-   established full preselection pipeline
-   located criticality-direction terminology source
-   confirmed criticality closeness tie ordering
-   confirmed lower-criticality recommendation policy
-   confirmed repeated stability/energy use

## 2026-07-11 --- Materials Project Import and Live Data

-   confirmed `fraction=1.0` importer behavior
-   confirmed all 3022 development rows are `1.0`
-   found 28 real MP materials and 732 test materials
-   confirmed structured composition for all 28 real records
-   established safe backfill source

## 2026-07-17 --- Discovery Score and Source Provenance

-   resolved MG-AUD-006 score/breakdown arithmetic divergence
-   preserved winning score provenance during candidate merging
-   resolved MG-AUD-007 repeated-encounter source-diversity semantics
-   introduced distinct discovery source tracking
-   separated base discovery score provenance from diversity bonuses
-   verified merged-source candidate arithmetic and substitution paths
-   full regression suite passed
-   LiFePO4 → Na/phosphate scientific usefulness remained 95.65

## 2026-07-17 --- Risk Coverage and Community Element Membership

-   resolved MG-AUD-008 partial-risk-evidence bonus eligibility
-   made low-risk quality bonus eligibility coverage-aware
-   preserved complete-evidence LiFePO4 quality behavior
-   discovered separate raw-formula substring membership in community analytics
-   tracked the separate issue as MG-AUD-049
-   added canonical `elements` metadata to discovery graph nodes
-   replaced community formula substring counting with exact canonical membership
-   reused the existing graph-builder element map with no additional database query
-   verified greedy modularity community `dominant_elements`
-   preserved community numeric analytics
-   full regression suite passed
-   LiFePO4 → Na/phosphate scientific usefulness remained 95.65

------------------------------------------------------------------------

# Appendix A --- Reference Response

Base material:

-   LiFePO4
-   `material_id = 5`
-   `mp_id = mp-19017`

Objective:

``` json
{
  "avoid_elements": ["Li"],
  "prefer_elements": ["Na"],
  "preserve_elements": ["Fe", "P", "O"],
  "target_family": "phosphate",
  "max_hops": 2,
  "limit": 5,
  "prefer_lower_criticality": true,
  "require_stable_materials": false
}
```

Observed endpoints:

-   Na3Fe3(PO4)4
-   Na9Fe3P8O29
-   NaFeP2O7
-   NaFePO4
-   Na3Fe(PO4)2

The original pre-remediation reference response recorded
`scientific_usefulness_score = 94.95`.

After MG-AUD-001 corrected stoichiometric composition weighting, the
verified reference score became `95.65`.

MG-AUD-002 through MG-AUD-008 preserved the verified `95.65` score and
the equal-evidence tie across the five reference pathways.

MG-AUD-049 also preserved the verified `95.65` score while correcting
researcher-facing community element metadata.

------------------------------------------------------------------------

# Appendix B --- Main Dependency Groups

## Transition / Framework Semantics

Affects:

-   preservation objectives
-   family matching
-   explanations
-   ranking
-   evidence
-   comparison
-   public API

**Rule:** correct or qualify the source fact before downstream
consumers.

## Evidence Semantics

Affects:

-   support counts
-   readiness
-   confidence
-   comparison
-   endpoint differentiation

**Rule:** separate internal support from external scientific evidence.

## Objective Semantics

Affects:

-   multi-element handling
-   strict constraints
-   stability requirement
-   criticality preference
-   preservation semantics

**Rule:** define hard/soft semantics before local fixes.

## Bounded Search and Ranking

Affects:

-   candidate ordering
-   expansion bounds
-   chain limits
-   objective filtering
-   final opportunity set

**Rule:** separate production bounds from scientific completeness
claims.

## Risk, Criticality, and Quality

Affects:

-   unknown/partial evidence
-   shared provenance
-   quality bonuses
-   endpoint evidence
-   completeness semantics

**Rule:** values and evidence coverage should travel together.

------------------------------------------------------------------------

# Appendix C --- Inspected Components

## Research Intelligence

-   `scientific_pathway_analysis_service.py`
-   `research_evidence_intelligence_service.py`
-   `comparative_research_intelligence_service.py`
-   `endpoint_sensitive_research_ranking_service.py`
-   `objective_exploration_service.py`
-   `objective_service.py`

## Discovery Intelligence

-   `chain_service.py`
-   discovery routes/endpoints
-   discovery schemas
-   `DiscoveryTransitionValidator`
-   `DiscoveryPathRankingService`
-   `candidate_service.py`
-   `candidate_screening_service.py`
-   `candidate_comparison_service.py`
-   `scoring_service.py`
-   `graph_builder.py`
-   `graph_analytics_service.py`
-   `graph_algorithms_service.py`
-   `k_best_path_service.py`

## Material Intelligence

-   `risk_service.py`
-   `quality_service.py`
-   `criticality_service.py`
-   `family_service.py`
-   `neighbor_service.py`
-   `similarity_service.py`
-   `recommendation_service.py`

## Data and Import

-   `material.py`
-   `material_element.py`
-   `materials_project_service.py`
-   `material_import_service.py`
-   `import_materials_project.py`
-   `seed_core_data.py`
-   count/cleanup scripts
-   live read-only database inspection scripts

## Utilities

-   `chemical_formula.py`

------------------------------------------------------------------------

# Appendix D --- Finding Template

``` text
Finding ID
Title
Status
Confidence
Priority
Evidence
Finding
Impact
Affected Layers
Dependencies
Recommended Action
Verification
Last Verified
```

------------------------------------------------------------------------

# Current Audit Position

MaterialGraph has a strong deterministic architecture, but several
upstream data and semantic conventions propagate into ranking, evidence,
comparison, and public meaning.

The sequential remediation set
(MG-AUD-001 through MG-AUD-009) has been implemented and verified.

MG-AUD-049, discovered during MG-AUD-008 dependency inspection, has also
been implemented and verified independently.

MG-AUD-050 has been identified as a follow-on explainability enhancement
discovered during MG-AUD-009 verification.

The remaining work now focuses primarily on scientific semantics,
researcher explainability, ranking policies, and production
performance while preserving deterministic reasoning and the verified
LiFePO4 → Na/phosphate reference workflow.

No new major capability should be added until upstream correctness fixes
are characterized and verified.

------------------------------------------------------------------------

------------------------------------------------------------------------

# 11. Audit Cycle 2 --- Scientific Scoring Architecture

**Status:** Paused after provenance investigation\
**Scope:** Scientific scoring architecture (observation phase)\
**Decision:** No additional confirmed findings were identified during
this phase.

## 11.1 Objective

Audit Cycle 2 focused on understanding the scientific meaning,
provenance, propagation, and explainability of MaterialGraph scoring
before making any semantic changes.

The investigation intentionally prioritized observation over
remediation.

## 11.2 Verified Outcomes

The investigation established:

-   Material-level scientific scoring (criticality, risk, and material
    quality) has been traced through implementation.
-   Primary propagation into the Research Intelligence pipeline has been
    verified.
-   Additional propagation into Similarity and Recommendation pipelines
    has been verified.
-   Consumer classes were identified:
    -   Primary consumers (semantic propagation)
    -   Secondary consumers (scientific application)
    -   Tertiary consumers (policy application)

The investigation reached a point where additional file-by-file
inspection was primarily confirming existing architectural patterns
rather than discovering new scientific-scoring behavior.

## 11.3 Audit Decision

Audit Cycle 2 is intentionally paused.

No additional MG-AUD findings are introduced.

Future scoring investigations should resume only when remediation
changes scientific semantics or introduces new scoring capabilities.

## 11.4 Next Engineering Phase

Implementation should now focus on the existing confirmed findings in
roadmap order:

The sequential remediation set through MG-AUD-009 has been completed.

MG-AUD-049 and MG-AUD-050 were identified as independent findings during subsequent remediation and verification work.

Future audit work should continue with the remaining confirmed
semantic, evidence, ranking, and performance findings in roadmap
priority order.

After each remediation:

-   characterization tests
-   regression verification
-   reference response comparison
-   downstream propagation verification

Only after these changes should Audit Cycle 2 be reopened.

------------------------------------------------------------------------

# Current Audit Position

MaterialGraph now has a comprehensive architectural audit and a
prioritized remediation roadmap.

The highest engineering value is no longer additional architectural
inspection, but systematic correction of confirmed upstream issues
followed by regression verification.