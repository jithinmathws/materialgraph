# MaterialGraph Current Implementation Audit

**Status:** Active architecture and implementation audit\
**Project stage:** Post-v1.9.6\
**Primary reference trace:** LiFePO4 → Na/phosphate objective

## 1. Purpose

Understand what MaterialGraph actually computes, how semantics propagate
across layers, and which findings are ready for remediation before
adding new capabilities.

Audit method:

1.  inspect source behavior;
2.  trace upstream/downstream dependencies;
3.  compare with representative API responses;
4.  record only architecture-, correctness-, scientific-, evidence-,
    contract-, or production-relevant findings;
5.  fix critical issues only when semantics and consumers are
    sufficiently understood;
6.  verify with focused tests, full tests, and real-response regression
    checks.

## 2. Reference Response

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

All received `scientific_usefulness_score = 94.95`.

v1.9.5 exposed the tie without inventing a winner. v1.9.6 preserved it
because available endpoint-sensitive evidence did not justify
differentiation.

## 3. Verified Architecture Flow

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

The system generally reuses existing services, keeps route logic thin,
preserves deterministic reasoning, and applies production bounds.

## 4. Verified Strengths

-   Thin route boundary; no hidden reranking observed.
-   Existing services are composed rather than reimplemented.
-   Bounded exploration includes hop guards, per-node bounds, result
    limits, cycle prevention, and caches.
-   v1.9.6 preserves equal-evidence ties and adds no arbitrary endpoint
    score.
-   Responses expose score breakdowns, assumptions, evidence state,
    comparisons, and researcher decision boundaries.
-   The risk fix introduced evidence-aware signals while retaining
    legacy compatibility.

## 5. Confirmed Correctness and Semantic Findings

### 5.1 Unknown risk interpreted as favorable low risk --- fixed

Previous behavior:

``` text
missing risk evidence → numeric 0.0 → low-risk interpretation → favorable quality bonus
```

Corrected quality path:

``` text
missing evidence → explicit unknown state → no low-risk bonus
```

Current risk metadata includes score, known state, coverage,
known/unknown element counts, completeness, and unknown elements.

**Status:** Fixed; focused and full tests passed. Real known-risk
LiFePO4 flow verified. One real partial/unknown-risk integration path
remains open.

### 5.2 Multi-element objectives are reduced downstream

The API accepts lists for avoid/prefer elements, but downstream
chain/ranking interfaces are scalar.

**Impact:** API semantics exceed implementation semantics.\
**Status:** Confirmed; do not fix by merely removing `[0]` or looping
over scalar heuristics.

### 5.3 Preservation can be satisfied by union across transitions

Required elements can be accepted when different transitions preserve
different subsets.

``` text
required = {Fe, P, O}
T1 = {Fe}
T2 = {P, O}
union = required → accepted
```

This does not prove continuous preservation through the path.

### 5.4 Raw formula substring membership is used

Unsafe examples include `"N" in "Na..."`, `"S" in "Si..."`, and
`"C" in "Ca..."`.

**Status:** Confirmed. Structured element membership should be preferred
after consumer inventory.

### 5.5 `preserved_framework` is compositional overlap, not validated structure

`DiscoveryTransitionValidator` derives the field from source/target
element-set intersection. No crystallographic, bonding-topology,
coordination-environment, or independent structural-preservation
analysis was found.

Propagation:

``` text
element overlap
    ↓
preserved_framework
    ↓
transition explanation
    ↓
objective filtering
    ↓
path ranking
    ↓
evidence/confidence
    ↓
comparison
    ↓
public API
```

This is a cross-layer semantic issue. Do not rename locally; remediate
from the source with compatibility planning.

### 5.6 Framework explanation overstates evidence

Shared elements can become language equivalent to "preserving Fe-O-P
chemistry," although the computation establishes shared element
membership rather than preserved bonding, motif, topology, or structure.

### 5.7 `framework_preserving` fallback lacks independent framework validation

The transition type can be emitted without separate
structural-preservation analysis.

### 5.8 Framework scoring inherits overlap semantics

Path ranking consumes transition `preserved_framework` sets and
intersects them across the path.

Observed contribution:

-   P and O common → 30/30
-   O common → 21/30
-   any common element → 15/30
-   none → 0/30

### 5.9 Objective alignment scores path-wide events

Removed and introduced elements are unioned across transitions. A path
can receive credit because an avoided element was removed somewhere or a
preferred element introduced somewhere without proving endpoint
satisfaction.

Distinguish:

-   transition event alignment;
-   path continuity;
-   endpoint satisfaction.

### 5.10 Path efficiency is hop-count based

Equal-hop paths receive equal contributions, contributing to score
collapse.

### 5.11 Path material quality is path-average quality

For `A → B → C`:

``` text
path quality = average(quality(A), quality(B), quality(C))
```

Shared bases/intermediates can dilute endpoint differences.

### 5.12 Material quality scale is intentionally 0--15

`QUALITY_SCORE_MAX = 15.0`.

Allocation:

-   stable flag: 5.25
-   very low energy above hull: 5.25
-   low criticality: 2.25
-   low known risk: 2.25

No missing multiplication bug was found.

### 5.13 Stability and energy signals are imported separately

`is_stable` and `energy_above_hull` are copied separately from Materials
Project and stored independently. No local derivation of `is_stable`
from hull energy was found in the inspected import path.

Both signals are reused across quality, similarity, and recommendation
scoring.

**Status:** Repeated weighting confirmed; scientific appropriateness
remains open.

### 5.14 Strict exploration mode does not guarantee hard rejection

Avoided-element violations can remain with penalties/warnings rather
than guaranteed exclusion.

### 5.15 Exploration candidate attribution can use future transitions

For `A → B → C`, candidate B can be scored using transitions including
`B → C`, attributing reasons/bonuses not responsible for reaching B.

### 5.16 Retained max score can be paired with merged reasons

Repeated candidates can retain a maximum score from one context while
merging explanations from several contexts.

### 5.17 Material family relationships are composition heuristics

`MaterialFamilyService` uses structured `MaterialElement` membership,
which avoids raw formula-substring ambiguity. Relationship labels are
deterministic element-set heuristics, not validated structural-family
assignments.

Key semantics:

-   `shared_chemistry`: at least 3 shared elements;
-   `transition_metal_related`: at least one shared configured
    transition metal;
-   `phosphate_related`: base contains P; candidate contains P and O;
-   `oxide_related`: both contain O;
-   `alkali_substitution`: configured alkali-like element sets differ
    and at least 3 elements are shared.

**Status:** Confirmed. Structured membership is a strength; scientific
terminology should remain qualified.

### 5.18 Family explanations can overstate heuristic evidence

`phosphate_related` can become "shares phosphate framework," although
the rule establishes only element-presence conditions.
`alkali_substitution` likewise does not prove a substitution mechanism,
site equivalence, or structural compatibility.

**Status:** Confirmed cross-layer semantic issue. Treat together with
broader framework/inference terminology remediation.

### 5.19 Family taxonomy requires review

`ALKALI_ELEMENTS` includes Mg, so Mg-containing changes can participate
in `alkali_substitution` classification even though Mg is not an alkali
metal.

**Status:** Likely taxonomy correctness issue. Verify intended domain
policy and tests before remediation.

### 5.20 Family candidate ordering affects bounded discovery

Related candidates are sorted descending by:

1.  number of relationship labels;
2.  number of shared elements.

Because downstream expansion is bounded, this ordering can determine
which candidates and chains reach objective filtering and ranking.

**Status:** Confirmed cross-layer search effect.

### 5.21 Correlated relationship labels can multiply search priority

Several labels can arise from the same shared composition facts.
Relationship-count sorting can therefore reward repeated interpretations
of one upstream fact as if they were multiple search-priority signals.

**Status:** Confirmed search-semantics concern.

### 5.22 Equal-key family ordering lacks an explicit deterministic tie-breaker

The candidate query has no explicit ordering, and the final sort key
contains only relationship count and shared-element count. Equal-key
candidates can inherit database-return order.

Under bounded expansion:

``` text
equal heuristic key
    ↓
unspecified candidate order
    ↓
bounded expansion
    ↓
possibly different surviving chains
```

**Status:** Confirmed implementation risk. Near-ready after
characterization testing; a deterministic tie-breaker need not invent
scientific weights.

### 5.23 Family discovery performs global scans

Each family request loads the global material-element map and scans all
non-test candidate materials in Python before sorting admitted results.

**Status:** Confirmed scalability concern; benchmark before redesign.

## 6. Candidate Generation, Screening, and Comparison Checkpoint

### 7.1 Discovery top-N ties lack deterministic tie-breaking

Discovery candidates are sorted only by `discovery_score` before
truncation. Equal scores can therefore inherit insertion/source order
and affect which candidates survive top-N limits.

**Status:** Confirmed. Add characterization tests before introducing a
deterministic non-scientific tie-breaker.

### 6.2 Recommendation-source generation hardcodes lower-criticality preference

The recommendation candidate path calls the recommendation service with
`prefer_lower_criticality=True` regardless of whether the current
discovery request explicitly asks for it.

**Status:** Confirmed implicit policy. Inspect recommendation semantics
before remediation.

### 6.3 Scenario generation has avoid-first primary-element precedence

The scenario path selects:

``` text
scenario_element = avoid_element or prefer_element
```

When both exist, the avoided element becomes the primary scenario
element, although both constraints are also passed downstream.

**Status:** Confirmed asymmetric policy.

### 6.4 Candidate merge provenance is blurred

Repeated candidates are merged using:

``` text
max(existing_score, new_score)
+ source diversity bonus
```

while discovery paths, score breakdowns, and explanation parts are also
merged.

The final candidate can therefore combine:

-   score anchored to one source;
-   diversity bonus from repeated presence;
-   reasons from several sources;
-   merged breakdown fields.

**Status:** Confirmed provenance concern.

### 6.6 Screening still interprets unknown risk as favorable zero

`CandidateScreeningService` uses the legacy numeric risk API. Unknown
risk can therefore become:

``` text
unknown evidence
    ↓
risk score 0.0
    ↓
risk penalty 0.0
    ↓
favorable screening outcome
```

The explanation can also present the unknown state as a numeric
zero-risk penalty.

**Severity:** Critical correctness/evidence semantics.\
**Status:** Confirmed cross-layer.\
**Readiness:** High-priority remediation candidate after consumer/test
inventory.

### 6.7 Screening has N+1 access patterns

The service loads all materials, then performs per-material element
lookup and per-material risk lookup despite existing bulk risk
capabilities.

**Status:** Confirmed scalability issue.

### 6.8 Missing-data policies differ across screening constraints

-   `require_stable=True`: non-true/unknown stability is rejected.
-   `max_energy_above_hull`: unknown energy is allowed because only
    known threshold violations are rejected.

**Status:** Confirmed policy inconsistency; define intended semantics
before change.

### 6.9 Screening scores are explicit policy heuristics

The score uses fixed base, scarcity, avoidance, stability, and risk
weights, then clamps to 0--100.

**Status:** Deterministic and transparent, but policy-derived rather
than scientific evidence. Clipping can collapse distinct candidates into
ties.

### 6.10 Pairwise comparison invents a winner on exact ties

Comparison uses `material_a.score >= material_b.score`, so equal scores
select material A as winner.

The response can therefore declare A the winner while also explaining
that both candidates are similar under the selected constraints.

**Severity:** High comparative semantics.\
**Status:** Confirmed.

### 6.11 Comparison inherits screening risk semantics

Because comparison delegates to screening, unknown-risk-as-zero behavior
can propagate into screening scores and pairwise winner selection.

**Severity:** Critical cross-layer propagation.\
**Status:** Confirmed.

### 6.12 Comparison conflates filtered and unavailable candidates

Both candidates must survive global screening. If either is absent after
filtering, comparison returns no result, without distinguishing missing
material from constraint-based exclusion.

**Status:** Confirmed API-diagnostic gap.

### 6.13 Element constraints use raw formula-substring membership

Preferred/avoided element checks use string membership against the
formula. This can confuse symbols such as N/Na, S/Si, or C/Ca and
directly alter candidate scores through bonuses or penalties.

**Severity:** Critical correctness.\
**Status:** Confirmed.\
**Readiness:** High; structured material-element data already exists in
the candidate pipeline.

### 6.14 Source-diversity bonus accumulates per repeated encounter

The diversity bonus increments whenever an existing candidate is
encountered. No distinct source identity is tracked.

**Finding:** the current behavior is closer to a repeated-encounter
bonus than verified independent-source diversity.

**Severity:** High scoring/provenance.\
**Status:** Confirmed.

### 6.15 Final score and score breakdown use different merge semantics

Candidate score merging uses:

``` text
max(existing_score, incoming_score)
+ source diversity bonus
```

Most score-breakdown fields instead use additive merging.

Therefore the breakdown can materially exceed and fail to decompose the
returned `discovery_score`.

**Severity:** High explainability/provenance.\
**Status:** Confirmed.

### 6.16 Repeated score components can inflate merged breakdowns

Only preferred-element, avoided-element-removed, and
avoided-element-present adjustments are explicitly non-additive. Other
repeated components can accumulate in the merged breakdown.

**Status:** Confirmed.

### 6.17 Lower-risk and lower-criticality terminology is inconsistent

Recommendation scoring checks `criticality_direction == "LOWER_RISK"`
and then awards a lower-criticality bonus/path.

Because risk and criticality are distinct derived metrics with
overlapping evidence, the terms should not be treated as interchangeable
without an explicit upstream contract.

**Status:** Confirmed terminology/contract concern. Inspect
recommendation service before remediation.

### 6.18 Family labels have different scoring roles

Only `shared_chemistry` and `alkali_substitution` directly add
family-candidate score in this service. Other family labels can still
affect admission, paths, explanations, and upstream ordering.

**Status:** Confirmed; refines earlier family-ordering conclusions.

### 6.19 Avoid/prefer constraints are soft score adjustments in candidate scoring

-   preferred element present: bonus;
-   avoided element absent: bonus;
-   avoided element present: penalty.

An avoided-element candidate can remain if other score sources outweigh
the penalty.

**Status:** Confirmed soft-constraint semantics.

### 6.20 Recommendation/similarity pipeline semantics

Confirmed pipeline:

``` text
structured element/application neighbors
→ neighbor ranking
→ top-N truncation
→ similarity scoring
→ recommendation scoring
→ scenario evaluation
```

Key facts:

-   neighbor score is `2×shared_elements + 3×shared_applications`;
-   similarity preserves the same 2:3 ratio at 10× scale, then adds
    stability/energy terms;
-   truncation occurs before similarity scoring, so later stages cannot
    recover excluded candidates;
-   similarity tie ordering uses criticality closeness, while
    recommendation defaults to lower-criticality preference;
-   `LOWER_RISK/HIGHER_RISK/SAME_RISK` are generated from criticality
    deltas, creating a terminology mismatch;
-   recommendation/scenario sorts lack explicit final tie-breakers;
-   recommendation reasons do not cleanly distinguish score contributors
    from contextual facts.

**Status:** Pipeline behavior confirmed. Scientific appropriateness of
truncation and repeated stability/energy weighting remains open.

## 7. Criticality and Risk Checkpoint

### 7.1 Criticality computation

Per-element criticality:

``` text
mean(
    abundance_score,
    supply_risk_score,
    toxicity_score,
    geopolitical_risk_score,
    10 - recyclability_score
) × 10
```

Only non-null dimensions are averaged.

Material criticality:

``` text
Σ(element_criticality × material_fraction) / Σ(material_fraction)
```

Latest available risk profile is selected independently per element by
year.

### 7.2 Risk computation

Per-element risk:

``` text
mean(
    supply_risk_score,
    geopolitical_risk_score,
    toxicity_score
)
```

Only non-null dimensions are averaged.

Material risk signal:

``` text
mean(calculable element risk scores)
```

Known elements are equally weighted; material fractions are not used.

### 7.3 Risk and criticality share upstream evidence

All three dimensions used by `MaterialRiskService` are also used by
`MaterialCriticalityService`:

-   supply risk;
-   geopolitical risk;
-   toxicity.

Criticality additionally uses abundance and inverted recyclability.

**Finding:** `risk_score` and `criticality_score` are distinct derived
metrics but not independent evidence dimensions.

**Status:** Confirmed. Inspect downstream weighting before remediation.

### 7.4 Unknown criticality evidence becomes favorable zero

Two paths produce `0.0`:

-   no `ElementRiskProfile`;
-   profile exists but all relevant dimensions are null.

The element fraction remains in the material denominator, so unknown
evidence can lower material criticality.

``` text
missing criticality evidence
    ↓
0.0
    ↓
fraction-weighted aggregation
    ↓
apparently lower material criticality
```

**Severity:** Critical correctness/evidence semantics.\
**Status:** Confirmed.\
**Readiness:** Near-ready; inventory consumers and define evidence-aware
compatibility path before change.

### 7.5 Partial criticality profiles look complete

A score can be computed from only one available dimension, but no
dimension-level coverage is exposed.

**Status:** Confirmed evidence-provenance gap.

### 7.6 Partial material risk sets `risk_known = True`

If at least one material element has a calculable risk score:

``` text
risk_known = True
risk_score = mean(known element scores)
coverage = known_count / total_count
```

Other elements may remain unknown.

Therefore `risk_known = True` means "some calculable material-element
risk evidence exists," not "material risk is fully characterized."

### 7.7 Partial risk evidence can unlock full low-risk quality-bonus eligibility

Current quality bonus eligibility consumes `risk_score` and
`risk_known`, while coverage metadata is transported but not used
directly for the bonus decision.

``` text
partial coverage
    ↓
risk_known = True
    ↓
low known-element average
    ↓
same low-risk bonus eligibility path as complete coverage
```

**Severity:** High correctness/evidence semantics.\
**Status:** Confirmed cross-layer.

### 7.8 `risk_evidence_complete` is element-coverage completeness

Current completeness means every material element produced some
calculable risk score. It does not prove that every expected risk
dimension exists for every element.

**Status:** Confirmed semantic/API gap.

### 7.9 Risk profile partiality exists at two levels

1.  material-element coverage: known elements / total elements;
2.  profile-dimension coverage: available risk dimensions / expected
    dimensions.

The service models level 1 but not level 2.

### 7.10 Risk and criticality aggregate differently

-   risk: equal average across known elements;
-   criticality: composition-fraction-weighted average.

Do not change this without defining intended metric semantics.

### 7.11 Legacy risk APIs retain unknown → `0.0`

Legacy numeric APIs preserve zero for compatibility.
Correctness-sensitive consumers should use evidence-aware signal APIs.

**Status:** Intentional compatibility hazard; consumer inventory needed.

### 7.12 `prefer_lower_criticality` is not handled by `MaterialCriticalityService`

The service computes criticality but does not consume research
objectives.

**Status:** Objective propagation remains open downstream.

### 7.13 Materials Project import discards composition weighting

The inspected Materials Project pipeline stores every linked element
with `fraction = 1.0`. `MaterialCriticalityService` later uses this
field as the aggregation weight.

**Confirmed consequence for this import path:** criticality becomes an
equal-weight average across distinct constituent elements, not a
stoichiometric/composition-weighted average.

No inspected seed, count, or cleanup script corrects these fractions.

**Severity:** Critical data/correctness.\
**Status:** Confirmed for the inspected import path; live-database
extent remains unverified.

## 8. Evidence and Comparative Findings

### 7.1 Internal deterministic support can look like scientific evidence

Framework-derived and other internal signals can contribute to evidence
strength/readiness even when experimental, literature, DFT, synthesis,
electrochemical, or manufacturing evidence is missing.

**Risk:** repeated reuse of one upstream inference can appear as
multiple independent supporting signals.

### 7.2 Evidence readiness semantics are too broad

Current readiness can imply strong scientific evidence from internal
support counts.

Future remediation should distinguish concepts such as:

-   internal support strength;
-   external evidence readiness;
-   evidence coverage;
-   validation readiness.

Do not finalize field names until source-signal provenance is fully
audited.

### 7.3 Comparative tie handling is partly strong, partly inconsistent

Strength: pairwise comparison can preserve equal-score ties.

Open issues:

-   `top_ranked_pathway` can select one representative from a top tie;
-   highest-readiness summaries can select one member of a readiness
    tie;
-   comparative element highlights inherit framework terminology.

### 7.4 Endpoint-sensitive ranking has implicit policy

Current ordering is lexicographic:

``` text
quality
→ stability
→ energy above hull
→ criticality
→ risk
→ evidence readiness
```

Earlier dimensions dominate later ones.

Do not replace with weighted scoring without justified policy.

### 7.5 Exact numeric inequality can differentiate endpoints

Tiny differences can split evidence groups without a scientifically
justified tolerance or precision policy.

Do not add arbitrary epsilon thresholds.

### 7.6 Risk coverage is not fully propagated into endpoint evidence

Equal numeric risk values can represent different evidence coverage
states.

## 9. Search-Space and Production Findings

-   Objective filtering occurs after bounded chain generation.
-   Completed-chain `limit` shapes discovery, not only presentation.
-   Candidate expansion is bounded per node.
-   Main expansion tends to finalize max-hop chains.
-   Search order may affect which opportunities survive bounds.
-   Do not remove production guards blindly.

Key distinction to preserve:

``` text
production search bounds ≠ scientific completeness
```

## 10. API and Contract Findings

Confirmed/open contract issues:

-   multi-element objective promise exceeds scalar downstream handling;
-   requested `preserve_elements` and inferred `preserved_framework` are
    distinct concepts;
-   `preserved_framework` is embedded in public schemas, requiring
    compatibility planning;
-   evidence readiness is an unconstrained public string;
-   confidence scope is ambiguous;
-   material quality, endpoint-sensitive ranking, and comparative nested
    structures are under-typed;
-   objective validation remains open for invalid symbols, casing, empty
    values, and contradictions.

Type contracts only after corrected semantics stabilize.

## 11. Data Provenance Findings

-   Risk profiles are manual Phase 1 seed values
    (`manual_phase_1_seed`), not independently validated external
    evidence.
-   Materials Project imports preserve upstream `is_stable` and
    `energy_above_hull` separately.
-   The inspected importer discards composition fractions by writing
    `1.0` for every material-element link.
-   Exact live-database exposure to the fraction defect remains to be
    measured.

## 12. Main Dependency Groups

### A. Transition/framework semantics

Affects:

-   preservation objectives;
-   family matching;
-   explanations;
-   ranking;
-   evidence;
-   comparison;
-   public API.

**Rule:** correct/qualify the source fact before downstream consumers.

### B. Evidence semantics

Affects:

-   support counts;
-   readiness;
-   confidence;
-   comparison;
-   endpoint differentiation.

**Rule:** separate internal deterministic support from external
scientific evidence.

### C. Objective semantics

Affects:

-   multi-element handling;
-   strict constraints;
-   stability requirement;
-   criticality preference;
-   preservation semantics.

**Rule:** define hard/soft objective semantics before local fixes.

### D. Bounded search and ranking

Affects:

-   candidate ordering;
-   expansion bounds;
-   chain limits;
-   objective filtering;
-   final opportunity set.

**Rule:** separate production bounds from scientific ranking semantics.

### E. Risk, criticality, and quality evidence

Affects:

-   unknown/partial evidence;
-   shared provenance;
-   quality bonuses;
-   endpoint evidence;
-   completeness semantics.

**Rule:** values and evidence coverage/provenance should travel together
when downstream decisions depend on them.

## 13. Remediation Readiness

  ------------------------------------------------------------------------
  Issue               Readiness          Immediate next action
  ------------------- ------------------ ---------------------------------
  Unknown-risk        Fixed              Verify one real partial/unknown
  favorable-zero                         path
  quality path                           

  Unknown criticality Near-ready         Inventory consumers; design
  → favorable zero                       evidence-aware compatibility path

  Partial risk        Provisional, high  Inspect exact quality consumer
  unlocking full      confidence         tests and define coverage-aware
  low-risk bonus                         eligibility semantics
  eligibility                            

  Risk--criticality   Do not remediate   Trace downstream weighting and
  shared provenance   blindly            intended metric roles

  Formula substring   Provisional        Inventory occurrences and
  membership                             structured alternatives

  Multi-element       Provisional        Inspect remaining
  objective reduction                    candidate/validator capabilities

  Preservation union  Provisional        Define exact path continuity
  logic                                  invariant

  Framework semantics Provisional source Plan source-first correction and
                      issue, cross-layer compatibility
                      remediation        
                      blocked            

  Evidence readiness  Provisional        Finish source-signal provenance
                                         audit

  Strict-mode         Provisional        Define hard rejection semantics
  mismatch                               

  Exploration         Ready candidate    Preserve candidate-specific path
  future-transition   after              context
  attribution         characterization   
                      test               

  Merged reasons vs   Provisional        Define score/explanation
  retained max score                     provenance

  Comparative top     Provisional        Design tie-aware compatible
  representative                         representation
  under tie                              

  Endpoint            Do not remediate   Define
  exact-value         yet                precision/meaningful-difference
  differentiation                        policy

  Endpoint            Do not remediate   Decide/document intentional
  lexicographic       yet                policy
  priority                               

  Bounded search      Do not remediate   Inspect ordering and benchmark
  before objective    blindly            
  filtering                              

  Under-typed schemas Provisional        Wait for semantic stabilization
  ------------------------------------------------------------------------

## 14. Dependency-Ordered Remediation Sequence

1.  Preserve baseline with characterization tests and reference-response
    snapshots.
2.  Finish source-level inspections and consumer inventories.
3.  Correct objective and structured element-membership semantics.
4.  Correct framework semantics from the canonical source outward.
5.  Separate internal support from external evidence.
6.  Repair exploration score attribution/provenance.
7.  Make comparative summaries fully tie-aware.
8.  Revisit endpoint-sensitive differentiation only after evidence
    semantics stabilize.
9.  Separate bounded search from completeness claims while retaining
    production safety.
10. Strengthen schemas after semantics stabilize.

The sequence is a living consequence of the audit, not a fixed roadmap.

## 15. Verification Requirements for Significant Fixes

Every significant remediation should verify:

1.  **Correctness** --- explicit old/new behavior and focused test.
2.  **Scientific semantics** --- names match evidence; inference is not
    presented as proof.
3.  **Cross-layer integration** --- downstream consumers remain
    consistent.
4.  **Production behavior** --- query count, latency, expansion, cache,
    and response-size impact.
5.  **Real-response regression** --- rerun the LiFePO4 → Na/phosphate
    trace and explain every intentional difference.

A changed score is not automatically a regression. An unexplained score
change is.

## 16. Current Open Questions

1.  What fraction values are present in the live database, and which
    rows came through the affected importer?
2.  Which consumers still use legacy numeric risk/criticality APIs?
3.  What coverage threshold should govern low-risk bonuses?
4.  Is repeated stability/energy weighting intentional across quality,
    similarity, and recommendation layers?
5.  Are bounded top-N gates acceptable for intended research semantics?
6.  How should hard/soft multi-element objectives and preservation
    continuity be defined?
7.  How should internal support be separated from external scientific
    evidence?
8.  What precision policy should govern endpoint differentiation and
    ties?

## 17. Files and Areas Inspected

### Research Intelligence

-   `scientific_pathway_analysis_service.py`
-   `research_evidence_intelligence_service.py`
-   `comparative_research_intelligence_service.py`
-   `endpoint_sensitive_research_ranking_service.py`
-   `objective_exploration_service.py`
-   `objective_service.py`

### Discovery Intelligence

-   `chain_service.py`
-   discovery routes/endpoints
-   discovery schemas
-   `DiscoveryTransitionValidator`
-   `DiscoveryPathRankingService`

### Material Intelligence

-   `risk_service.py`
-   `quality_service.py`
-   `criticality_service.py`
-   `similarity_service.py`
-   `recommendation_service.py`
-   `neighbor_service.py`
-   `material_import_service.py`
-   `materials_project_service.py`
-   `material.py`
-   `material_element.py`
-   import/seed/count/cleanup scripts

### API/schema layer

-   research route
-   research objective exploration schemas
-   discovery schemas

## 18. Current Audit Position

The audit has verified a strong integrated architecture but also shown
that local inferences can propagate into ranking, evidence, comparison,
and public semantics.

Most important current conclusions:

-   missing evidence must not become favorable evidence;
-   framework terminology exceeds what compositional overlap proves;
-   public objective semantics exceed some downstream implementations;
-   bounded search shapes the opportunity set before final ranking;
-   internal deterministic agreement is not independent scientific
    evidence;
-   risk and criticality share substantial upstream evidence;
-   discovery score provenance and breakdown arithmetic can diverge;
-   the inspected Materials Project importer loses composition weighting
    by storing `fraction=1.0`;
-   genuine ties should remain unresolved when evidence does not justify
    differentiation.

**Immediate next step:** verify live `MaterialElement.fraction` values
and affected-row provenance before estimating production impact.
Continue to separate confirmed behavior, provisional interpretation, and
remediation decisions.
