# MaterialGraph Architecture & Implementation Audit Findings Register

**Document role:** Canonical register of audit findings and current status  
**Status:** Active living audit  
**Detailed remediation record:** `MATERIALGRAPH_AUDIT_RESOLUTION.md`

This document contains only MaterialGraph audit findings. Update an existing finding's status here when its state changes, and add every newly confirmed finding here before recording implementation details elsewhere.

## Status legend

- **Confirmed:** Verified defect or semantic risk awaiting resolution.
- **Verification:** Remediation implemented and locally verified; remaining
  deployment or production checks are pending.
- **Resolved:** Implemented, regression-tested, and—where applicable—production-verified.
- **Domain decision required:** Implementation is known, but remediation depends on an explicit scientific or product-policy decision.
- **Accepted behavior:** Verified behavior retained intentionally; document rather than remediate.

## Register summary

- **Total findings:** 53
- **Resolved:** 20
- **Not resolved:** 33

## Correctness and Data Integrity

### MG-AUD-001 — Materials Project Import Discards Composition Weighting

- **Status:** Resolved
- **Priority:** P0
- **Confidence:** Confirmed

**Finding:** The Materials Project import path creates every `MaterialElement` row
with:

``` text
fraction = 1.0
```

`MaterialCriticalityService` later treats this field as an aggregation
weight:

``` text
Σ(element_criticality × fraction) / Σ(fraction)
```

**Impact:** For imported LiFePO4:

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

### MG-AUD-002 — Unknown Criticality Evidence Becomes Favorable Zero

- **Status:** Resolved
- **Priority:** P0
- **Confidence:** Confirmed

**Finding:** Two paths produce element criticality `0.0`:

-   no `ElementRiskProfile`
-   profile exists but all relevant dimensions are null

The element fraction remains in the material denominator.

``` text
missing criticality evidence
→ 0.0
→ weighted aggregation
→ apparently lower material criticality
```

**Impact:** Unknown evidence can look like favorable low criticality.

### MG-AUD-003 — Screening Uses Legacy Unknown-Risk-as-Zero Semantics

- **Status:** Resolved
- **Priority:** P0
- **Confidence:** Confirmed

**Finding:** `CandidateScreeningService` uses the legacy numeric risk API.

``` text
unknown risk
→ risk_score = 0.0
→ risk penalty = 0.0
→ favorable screening effect
```

The explanation can also present unknown risk as a real numeric zero.

### MG-AUD-004 — Formula Substring Membership Corrupts Element Constraints

- **Status:** Resolved
- **Priority:** P0
- **Confidence:** Confirmed

**Finding:** Discovery scoring uses string membership:

``` text
prefer_element in formula
avoid_element in formula
avoid_element not in formula
```

Unsafe examples:

-   `N` in `Na...`
-   `S` in `Si...`
-   `C` in `Ca...`

### MG-AUD-005 — `preserved_framework` Is Element Overlap, Not Structural Preservation

- **Status:** Resolved
- **Priority:** P1
- **Confidence:** Confirmed

**Finding:** `DiscoveryTransitionValidator` derives `preserved_framework` from
source/target element-set intersection.

No independent analysis was found for:

-   crystallographic framework
-   bonding topology
-   coordination environment
-   motif preservation
-   site correspondence

**Impact:** Scientific semantics and evidence provenance improved.

No numerical scientific scores changed.

LiFePO4 Scientific Usefulness

95.65 → 95.65

### MG-AUD-006 — Discovery Score and Breakdown Arithmetic Diverge

- **Status:** Resolved
- **Priority:** P1
- **Confidence:** Confirmed

**Finding:** Candidate score merging used:

``` text
max(existing_score, incoming_score)
+ source diversity bonus
```

while score-breakdown fields were merged additively.

**Impact:** The final breakdown could materially exceed and fail to decompose
`discovery_score`.

### MG-AUD-007 — Source Diversity Is Actually Repeated-Encounter Accumulation

- **Status:** Resolved
- **Priority:** P1
- **Confidence:** Confirmed

**Finding:** The source-diversity bonus previously incremented whenever an existing
candidate was encountered.

No distinct source identity was tracked, so repeated encounters could be
treated as additional source diversity.

**Impact:** Source diversity now represents distinct discovery evidence channels
rather than repeated candidate encounters.

Scientific pathway scoring remains unchanged.

LiFePO4 Scientific Usefulness

95.65 → 95.65

### MG-AUD-008 — Partial Risk Evidence Can Unlock Full Low-Risk Bonus Eligibility

- **Status:** Resolved
- **Priority:** P1
- **Confidence:** Confirmed

**Finding:** If at least one material element had calculable risk:

``` text
risk_known = True
```

Coverage could still be below 1.0.

Before remediation, `MaterialQualityService` used `risk_known` and
`risk_score` for low-risk bonus eligibility without requiring complete
material-element risk coverage.

**Impact:** ``` text
partial coverage
→ risk_known = True
→ low known-element average
→ same full low-risk bonus path as complete evidence
```

This allowed partial evidence to unlock favorable treatment equivalent to
complete evidence.

### MG-AUD-009 — Multi-Element Research Objectives Were Reduced to Single-Element Evaluation

- **Status:** Resolved
- **Priority:** P1
- **Confidence:** Confirmed

**Finding:** The public research objective API accepted collections of avoided and
preferred elements.

However, downstream deterministic pathway evaluation and objective-alignment
scoring only considered the first avoided element and the first preferred
element.

As a result, multi-element research objectives were effectively reduced to
single-element evaluation.

**Impact:** Researchers specifying objectives such as:

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

### MG-AUD-010 — Stable Pathway Identity and Tie-Aware Comparative Research

- **Status:** Resolved
- **Priority:** P1
- **Confidence:** Confirmed

**Finding:** Three different concepts had become conflated:

- pathway identity
- deterministic ordering
- scientific ranking

For example:

```text
rank = 1
rank = 1
rank = 1
```

represents three equally ranked pathways, but rank alone cannot uniquely
identify them.

This ambiguity propagated into comparative summaries, research gaps,
assumptions, pairwise comparisons, and element aggregation.

**Impact:** No deterministic scientific scoring defect existed.

Scientific usefulness, pathway ranking, objective alignment, and endpoint
evaluation remained correct.

The limitation affected researcher explainability, deterministic API
contracts, and future extensibility.

## Scientific and Domain Semantics

### MG-AUD-011 — Framework Explanations Overstate Evidence

- **Status:** Resolved
- **Priority:** P1
- **Confidence:** Confirmed

**Finding:** Shared elements can become wording such as:

-   "preserving Fe-O-P chemistry"
-   "shares phosphate framework"

The implementation establishes membership overlap, not preserved bonding
or structure.

### MG-AUD-012 — `framework_preserving` Fallback Lacks Independent Validation

- **Status:** Resolved
- **Priority:** P1
- **Confidence:** Confirmed

**Finding:** The transition type can be emitted without independent
structural-preservation evidence.

**Impact:** Elemental overlap could be serialized as a stronger structural
claim than the available evidence supported. The remediation changed the
unvalidated overlap classification to `shared_element_continuity` and the
evidence-free fallback to `candidate_transition`; admission rules and numeric
scores were unchanged.

### MG-AUD-013 — Framework Scoring Inherits Overlap Semantics

- **Status:** Resolved
- **Priority:** P1
- **Confidence:** Confirmed

**Finding:** Observed path-ranking contribution:

-   P and O common: 30/30
-   O common: 21/30
-   any common element: 15/30
-   none: 0/30

The numeric precision exceeds the strength of the underlying structural
evidence.

**Remediation:** Renamed the score dimension from `framework_preservation` to
`shared_element_continuity` throughout path ranking, research evidence,
scientific pathway analysis, comparative intelligence, and test fixtures. The
numeric continuity weights were retained, but researcher-facing explanations
now qualify the signal as elemental overlap and explicitly state that
structural preservation is not validated.

During remediation, regression checks detected and corrected two unrelated
efficiency defects: the path-efficiency calculation briefly referenced the
wrong weight, and an empty path received a one-hop efficiency bonus. The final
implementation uses `EFFICIENCY_WEIGHT = 10.0` and assigns `0.0` efficiency to
an empty path.

**Verification:** The focused tests and full regression suite passed locally.
Local and production objective exploration for material 5 returned `200 OK`,
emitted `shared_element_continuity: 30`, retained the expected total usefulness
score of `95.65`, and made no unsupported structural-preservation claim.
Production verification on 2026-07-23 also confirmed
`preservation_basis: element_overlap`,
`structural_preservation_validated: false`, and the absence of the legacy
`framework_preservation` score field.

### MG-AUD-014 — Preservation Can Be Satisfied by Union Across Transitions

- **Status:** Verification
- **Priority:** P1
- **Confidence:** Confirmed

**Finding:** Example:

``` text
required = {Fe, P, O}
T1 preserves {Fe}
T2 preserves {P, O}
union satisfies required
```

This does not prove continuous preservation through the path.

**Remediation:** Research-objective preservation now requires the requested
elements to occur in the intersection of shared-element evidence across every
transition. `shared_elements` takes precedence whenever present, including
when explicitly empty; `preserved_framework` is used only as a compatibility
fallback when the primary field is absent. Every transition participates in
the intersection, missing evidence contributes an empty set, and a
zero-transition path does not establish preservation. Scientific pathway facts
now use the same semantics.

**Verification:** All 26 focused research-service tests and the full regression
suite passed. Regression coverage rejects disjoint union-only evidence, empty
paths, missing transition evidence, and fallback from an explicitly empty
primary field. Local two-hop objective exploration correctly reported the
intersection of `{Fe, O, P}` and `{Fe, Na, O, P}` as `Fe-O-P` shared-element
continuity. Production deployment and EC2 endpoint verification remain
pending.

### MG-AUD-015 — Objective Alignment Uses Path-Wide Events

- **Status:** Confirmed
- **Priority:** P1
- **Confidence:** Confirmed

**Finding:** Removed and introduced elements are unioned across transitions.

A path can receive credit because an avoided element was removed
somewhere or a preferred element appeared somewhere without proving
endpoint satisfaction.

Distinguish:

-   transition event alignment
-   path continuity
-   endpoint satisfaction

### MG-AUD-016 — Avoid/Prefer Constraints Are Soft in Candidate Scoring

- **Status:** Confirmed
- **Priority:** P1
- **Confidence:** Confirmed

**Finding:** -   preferred element present: bonus
-   avoided element absent: bonus
-   avoided element present: penalty

An avoided-element candidate can remain if other sources outweigh the
penalty.

### MG-AUD-017 — Strict Exploration Does Not Guarantee Hard Rejection

- **Status:** Confirmed
- **Priority:** P1
- **Confidence:** Confirmed

**Finding:** Avoided-element violations can remain with penalties and warnings.

Hard versus soft semantics must be defined explicitly.

### MG-AUD-018 — Family Relationships Are Composition Heuristics

- **Status:** Confirmed
- **Priority:** P1
- **Confidence:** Confirmed

**Finding:** Key rules:

-   `shared_chemistry`: at least 3 shared elements
-   `transition_metal_related`: at least one shared configured
    transition metal
-   `phosphate_related`: base contains P; candidate contains P and O
-   `oxide_related`: both contain O
-   `alkali_substitution`: configured alkali-like sets differ and at
    least 3 elements are shared

These are deterministic and explainable, but are not validated
structural-family assignments.

### MG-AUD-019 — Family Taxonomy Includes Mg as Alkali

- **Status:** Confirmed implementation; domain intent unverified
- **Priority:** P1
- **Confidence:** High

**Finding:** `ALKALI_ELEMENTS` includes Mg, although Mg is an alkaline-earth metal.

Verify intended domain policy and tests before remediation.

### MG-AUD-020 — Alkali Substitution Does Not Prove Mechanism

- **Status:** Confirmed
- **Priority:** P1
- **Confidence:** Confirmed

**Finding:** The rule proves differing configured element sets plus shared elements.

It does not prove:

-   site equivalence
-   one-for-one substitution
-   charge compensation
-   structural compatibility
-   actual substitution mechanism

## 4.3 Evidence, Risk, Criticality, and Quality

## Evidence, Risk, Criticality, and Quality

### MG-AUD-021 — Risk and Criticality Share Upstream Evidence

- **Status:** Confirmed
- **Priority:** P1
- **Confidence:** Confirmed

**Finding:** Both use:

-   supply risk
-   geopolitical risk
-   toxicity

Criticality additionally uses abundance and inverted recyclability.

They are distinct metrics, but not independent evidence dimensions.

### MG-AUD-022 — Risk and Criticality Aggregate Differently

- **Status:** Confirmed
- **Priority:** P1
- **Confidence:** Confirmed

**Finding:** -   risk: equal average across calculable elements
-   criticality: `MaterialElement.fraction`-weighted average

Do not unify them without defining metric intent.

### MG-AUD-023 — Partial Criticality Profiles Look Complete

- **Status:** Confirmed
- **Priority:** P1
- **Confidence:** Confirmed

**Finding:** A criticality score can be computed from one available dimension without
dimension-level coverage metadata.

### MG-AUD-024 — Risk Completeness Measures Element Coverage Only

- **Status:** Confirmed
- **Priority:** P1
- **Confidence:** Confirmed

**Finding:** `risk_evidence_complete` means each material element produced some
calculable risk score.

It does not prove all expected dimensions are present.

Two distinct coverage layers exist:

1.  material-element coverage
2.  profile-dimension coverage

### MG-AUD-025 — Legacy Numeric Risk APIs Retain Unknown → 0.0

- **Status:** Confirmed and intentional
- **Priority:** P1
- **Confidence:** Confirmed

**Finding:** Legacy compatibility APIs preserve numeric zero for unknown risk.

Correctness-sensitive consumers must use evidence-aware signals.

### MG-AUD-026 — Material Quality Scale Is Intentionally 0--15

- **Status:** Resolved
- **Priority:** P1
- **Confidence:** Confirmed

**Finding:** `QUALITY_SCORE_MAX = 15.0`.

Allocation:

-   stable flag: 5.25
-   very low energy above hull: 5.25
-   low criticality: 2.25
-   low known risk: 2.25

No missing multiplication bug was found.

### MG-AUD-027 — Stability and Energy Are Imported Separately but Reused

- **Status:** Confirmed behavior; policy open
- **Priority:** P2
- **Confidence:** Confirmed implementation / Medium policy

**Finding:** `is_stable` and `energy_above_hull` are imported separately from
Materials Project.

Both are rewarded in:

-   quality
-   similarity
-   recommendation

Repeated weighting is confirmed. Scientific appropriateness remains a
policy question.

### MG-AUD-028 — Internal Deterministic Support Can Look Like Scientific Evidence

- **Status:** Confirmed
- **Priority:** P1
- **Confidence:** Confirmed

**Finding:** Framework-derived and other internal signals can increase
evidence/readiness even when external evidence is absent.

Future semantics should distinguish:

-   internal support strength
-   external evidence readiness
-   evidence coverage
-   validation readiness

### MG-AUD-029 — Risk Coverage Is Not Fully Propagated to Endpoint Evidence

- **Status:** Confirmed
- **Priority:** P1
- **Confidence:** Confirmed

**Finding:** Equal numeric risk values can represent different evidence coverage
states.

Values and coverage should travel together when downstream decisions
depend on them.

## 4.4 Discovery, Ranking, and Search Space

## Discovery, Ranking, and Search Space

### MG-AUD-030 — Bounded Search Shapes the Opportunity Set

- **Status:** Confirmed
- **Priority:** P2
- **Confidence:** Confirmed

**Finding:** -   objective filtering occurs after bounded chain generation
-   completed-chain limit shapes discovery, not only presentation
-   candidate expansion is bounded per node
-   search order can affect which opportunities survive

``` text
production search bounds ≠ scientific completeness
```

Do not remove production guards blindly.

### MG-AUD-031 — Family Ordering Can Affect Bounded Discovery

- **Status:** Confirmed
- **Priority:** P2
- **Confidence:** Confirmed

**Finding:** Family candidates are ordered by:

1.  relationship-label count
2.  shared-element count

Correlated labels derived from the same composition facts can multiply
search priority.

### MG-AUD-032 — Equal-Key Family Ordering Lacks a Final Tie-Breaker

- **Status:** Confirmed
- **Priority:** P2
- **Confidence:** Confirmed

**Finding:** Equal-key candidates can inherit database-return order.

Under bounded expansion, this can affect which chains survive.

### MG-AUD-033 — Recommendation Pipeline Contains Irreversible Preselection

- **Status:** Confirmed
- **Priority:** P2
- **Confidence:** Confirmed

**Finding:** ``` text
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

### MG-AUD-034 — Recommendation Defaults to Lower Criticality

- **Status:** Confirmed behavior; policy open
- **Priority:** P2
- **Confidence:** Confirmed implementation

**Finding:** `get_recommendations()` defaults `prefer_lower_criticality=True`.

Scenario recommendations also force this preference in their base
recommendation stage.

Whether this is appropriate for every objective remains open.

### MG-AUD-035 — Similarity and Recommendation Use Different Criticality Policies

- **Status:** Confirmed
- **Priority:** P2
- **Confidence:** Confirmed

**Finding:** -   similarity tie ordering prefers smaller absolute criticality
    difference
-   recommendation scoring prefers lower criticality

These are layered policies, not necessarily contradictions.

### MG-AUD-036 — Criticality Direction Uses Risk Terminology

- **Status:** Resolved
- **Priority:** P1
- **Confidence:** Confirmed

**Finding:** Criticality deltas produce:

-   `LOWER_RISK`
-   `HIGHER_RISK`
-   `SAME_RISK`

This is a terminology/contract mismatch.

### MG-AUD-037 — Recommendation Reasons Mix Contributors and Context

- **Status:** Resolved
- **Priority:** P1
- **Confidence:** Confirmed

**Finding:** Reasons can:

-   mention criticality when the preference flag is disabled
-   omit the low-energy score contribution
-   include shared elements/applications as context even when not
    directly added in recommendation scoring

Contributor facts and contextual facts are not distinguished.

**Remediation:** Recommendation explanation generation now receives
`prefer_lower_criticality` and distinguishes the similarity basis, active score
contributors, contextual criticality information, and the final recommendation
score. Shared elements and applications are labelled as components of the
similarity score rather than independent recommendation bonuses. The
low-energy-above-hull contribution is included when its scoring condition
(`energy_above_hull <= 0.01`) is satisfied. Criticality is presented as an
active contributor only when the preference is enabled; otherwise it remains
available under `context`.

**Verification:** Focused recommendation-service tests and the full regression
suite passed locally. Local and production endpoint checks for material 5
confirmed that
`prefer_lower_criticality=true` includes criticality in scoring and that
`prefer_lower_criticality=false` excludes it from the score while retaining the
comparison as context. Displayed recommendation scores reconciled with their
stated contributors in both modes. Production verification passed on
2026-07-23.

### MG-AUD-038 — Path Efficiency Is Hop-Count Based

- **Status:** Confirmed
- **Priority:** P2
- **Confidence:** Confirmed

**Finding:** Equal-hop paths receive equal path-efficiency contributions,
contributing to score collapse.

### MG-AUD-039 — Path Material Quality Is Averaged Across the Path

- **Status:** Confirmed
- **Priority:** P2
- **Confidence:** Confirmed

**Finding:** ``` text
A → B → C
path quality = average(quality(A), quality(B), quality(C))
```

Shared bases/intermediates can dilute endpoint differences.

### MG-AUD-040 — Exploration Attribution Can Use Future Transitions

- **Status:** Confirmed
- **Priority:** P1
- **Confidence:** Confirmed

**Finding:** For `A → B → C`, candidate B can receive reasons or bonuses using
`B → C`, even though that transition did not produce B.

## 4.5 Comparison, Endpoint Ranking, and Contracts

## Comparison, Endpoint Ranking, and Contracts

### MG-AUD-041 — Endpoint Ranking Uses Implicit Lexicographic Policy

- **Status:** Confirmed
- **Priority:** P2
- **Confidence:** Confirmed

**Finding:** Ordering:

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

### MG-AUD-042 — Exact Numeric Differences Can Split Evidence Groups

- **Status:** Confirmed
- **Priority:** P2
- **Confidence:** Confirmed

**Finding:** Tiny numeric differences can separate endpoints without a defined
precision or meaningful-difference policy.

Do not add arbitrary epsilon thresholds.

### MG-AUD-043 — Comparative Summaries Are Not Uniformly Tie-Aware

- **Status:** Confirmed
- **Priority:** P1
- **Confidence:** Confirmed

**Finding:** Some layers preserve ties, while:

-   `top_ranked_pathway`
-   highest-readiness summaries
-   legacy candidate comparison

can select one representative.

### MG-AUD-044 — Comparison Conflates Filtered and Unavailable Candidates

- **Status:** Confirmed
- **Priority:** P2
- **Confidence:** Confirmed

**Finding:** If either candidate does not survive screening, comparison returns no
result without distinguishing:

-   missing material
-   filtered by stability
-   filtered by energy threshold
-   otherwise unavailable

### MG-AUD-045 — API Contracts Are Under-Typed or Semantically Broader Than Implementation

- **Status:** Confirmed/open mix
- **Priority:** P2
- **Confidence:** High

**Finding:** Issues include:

-   multi-element objective promise exceeds scalar handling
-   requested `preserve_elements` differs from inferred
    `preserved_framework`
-   evidence readiness is an unconstrained string
-   confidence scope is ambiguous
-   nested quality/comparison structures are under-typed
-   objective validation remains open for casing, invalid symbols,
    empties, and contradictions

Type contracts should strengthen after semantic stabilization.

## 4.6 Production and Performance

## Production and Performance

### MG-AUD-046 — Family Discovery Performs Global Scans

- **Status:** Confirmed
- **Priority:** P2
- **Confidence:** Confirmed

**Finding:** Each family request loads the global material-element map and scans
non-test materials in Python.

Benchmark before redesign.

### MG-AUD-047 — Candidate Screening Has N+1 Access Patterns

- **Status:** Confirmed
- **Priority:** P2
- **Confidence:** Confirmed

**Finding:** Screening loads all materials, then performs per-material:

-   element lookup
-   risk lookup

Bulk risk capabilities already exist.

### MG-AUD-048 — Candidate Service Duplicates Global Element-Map Loading

- **Status:** Confirmed
- **Priority:** P2
- **Confidence:** Confirmed

**Finding:** `MaterialFamilyService` and `DiscoveryCandidateService` can each load
global material-element mappings in the same request path.

### MG-AUD-049 — Community Analytics Uses Raw Formula Substring Matching for Element Membership

- **Status:** Resolved
- **Priority:** P2
- **Confidence:** Confirmed

**Finding:** `DiscoveryGraphAnalyticsService._summarize_community()` determined configured
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

**Impact:** The affected dependency chain was:

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

### MG-AUD-050 — Scientific Pathway Responses Did Not Distinguish Path-Wide and Endpoint-Specific Objective Satisfaction

- **Status:** Resolved
- **Priority:** P2
- **Confidence:** Confirmed

**Finding:** Scientific pathway responses exposed:

- requested objective elements
- matched objective elements
- unmatched objective elements
- objective coverage
- completion status

These correctly described deterministic path-wide transition evidence.

However, they did not distinguish whether the final endpoint material
itself satisfied the requested research objective.

**Impact:** No scientific scoring defect existed.

Objective alignment, deterministic traversal, scientific usefulness,
transition plausibility, and pathway ranking were already correct.

The limitation affected researcher explainability only.

Researchers could not immediately distinguish:

- objective satisfied somewhere along the pathway
- objective satisfied by the final endpoint material

### MG-AUD-051 — Comparative Research Outputs Used Ranking as Pathway Identity

- **Status:** Resolved
- **Priority:** P1
- **Confidence:** Confirmed

**Finding:** Competition rank was used as both ordering and identity. Tied pathways therefore became ambiguous in comparative analyses.

**Impact:** Researchers could not uniquely reference tied pathways, and comparative aggregation could collapse distinct pathways sharing the same rank.

### MG-AUD-052 — Scenario Explanation Sign and Label Can Contradict the Score Contribution

- **Status:** Resolved
- **Priority:** P1
- **Confidence:** Confirmed

**Finding:** Scenario recommendation explanations can label a beneficial adjustment as
a penalty and can render the final value with the opposite sign from its
effect on the score.

Observed examples include:

```text
contains preferred element Na, bonus 10.0; final scenario penalty -10.0
```

and responses where `scenario_score` is greater than
`recommendation_score` while the explanation still reports a negative
"final scenario penalty."

For an avoided-element candidate, the wording can instead report:

```text
contains avoided element Li, penalty 20.0; final scenario penalty 20.0
```

The individual preferred/avoided-element clauses are understandable, but
the shared final label and sign convention do not reliably communicate
whether the scenario stage increased or decreased the candidate score.

**Impact:** -   Numeric scenario scoring and ordering appear internally consistent in
    the inspected responses.
-   Researcher-facing explanations can misstate the direction of the score
    adjustment.
-   API consumers cannot safely interpret the final prose as a faithful
    description of `scenario_delta` without inspecting the numeric fields.

### MG-AUD-053 — Discovery Base-Score Selection and Deterministic Tie Ordering

- **Status:** Resolved
- **Priority:** P1
- **Confidence:** Confirmed

**Finding:** Discovery candidate source merging compared an incoming base score with the
existing displayed `discovery_score`, which could already contain a
source-diversity bonus. The comparison therefore mixed two score stages and
could retain a weaker existing base score.

Exact score ties were also sorted only by `discovery_score`, leaving their
final order dependent on upstream insertion order rather than an explicit
deterministic response rule.

**Impact:** -   A stronger incoming source could fail to become the candidate's winning
    base score and score-breakdown provenance.
-   Exact ties could lack reproducible ordering if source encounter order
    changed.
-   Artificially changing weights to split valid ties would claim scientific
    differentiation unsupported by the available evidence.

### MG-AUD-054 — Discovery Explanation Clauses Can Lack a Separator

- **Status:** Confirmed
- **Priority:** P3
- **Confidence:** Confirmed

**Finding:** A discovery explanation can concatenate an evidence-limitation
clause and the next score clause without punctuation, producing wording such
as:

```text
oxide structure similarity is not validated similarity score 110.0
```

**Impact:** Numeric scores, ranking, and scientific classifications are not
affected. The defect reduces readability and can make independently generated
explanation clauses appear to form one unsupported statement.

## Maintenance rule

For future audit work:

1. Add or update the finding in this register.
2. Keep the finding description concise and evidence-based.
3. Store root cause, code changes, tests, production responses, scientific-impact checks, compatibility notes, and lessons learned in `MATERIALGRAPH_AUDIT_RESOLUTION.md`.
4. Do not duplicate resolution narratives, test logs, roadmaps, architecture summaries, or investigation diaries in this register.