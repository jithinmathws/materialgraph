# MaterialGraph Change Impact History

This document is the concise chronological record of externally meaningful
scientific, scoring, explanation, and API behavior changes made through the
MaterialGraph audit.

It does not contain root-cause analysis, file-level implementation details,
complete tests, or full production responses. Those belong in
`MATERIALGRAPH_AUDIT_RESOLUTION.md`. The canonical finding status remains in
`MaterialGraph_Architecture_Implementation_Audit_v2_Regenerated.md`.

## Impact legend

- **Scientific result:** computed scientific values or conclusions changed.
- **Ranking:** candidate or pathway order may change.
- **API contract:** response fields or serialized values changed.
- **Data migration:** stored data required recalculation or backfill.

---

## Composition-aware criticality weighting

Related findings: MG-AUD-001  
Release reference: v1.9.7  
Status: Production verified

### Before

Material criticality treated constituent elements without correct
stoichiometric weighting.

### After

Criticality uses composition-aware weighting. For the reference material
LiFePO4, criticality changed from `36.5` to `32.0`, and the reference pathway's
scientific usefulness changed from `94.95` to `95.65`.

### Impact

- Scientific result: **Yes**
- Ranking: **Potentially**, where corrected values distinguish candidates
- API contract: **No**
- Data migration: **Yes**

---

## Unknown criticality remains unknown

Related findings: MG-AUD-002  
Release reference: v1.9.8  
Status: Production verified

### Before

Missing criticality evidence could be treated like favorable zero criticality
and contribute a quality advantage.

### After

Unknown criticality remains `null` and receives no favorable quality bonus.
Known-material values and the LiFePO4 reference workflow are unchanged.

### Impact

- Scientific result: **Yes**, for materials with incomplete evidence
- Ranking: **Potentially**, for affected materials
- API contract: **No**
- Data migration: **No**

---

## Unknown risk preserved during candidate screening

Related findings: MG-AUD-003  
Release reference: v1.9.9  
Status: Production verified

### Before

Candidate screening and comparison could collapse unknown risk into a
favorable numeric value.

### After

Unknown risk remains unknown throughout screening and comparison. Candidate
responses expose risk-evidence metadata, and bulk loading avoids repeated
per-material lookups.

### Impact

- Scientific result: **Yes**, for candidates with unknown risk
- Ranking: **Potentially**, for affected candidates
- API contract: **Additive metadata only**
- Data migration: **No**

---

## Exact chemical-element membership

Related findings: MG-AUD-004  
Release reference: v1.9.10  
Status: Production verified

### Before

Some discovery logic used raw formula substring matching, which could confuse
symbols such as `N` and `Na`, `S` and `Si`, or `C` and `Ca`.

### After

Candidate scoring, chain filtering, warnings, and research-objective logic use
structured or parsed chemical-element membership.

### Impact

- Scientific result: **Yes**, for ambiguous element symbols
- Ranking: **Potentially**, for affected objectives
- API contract: **No**
- Data migration: **No**

---

## Qualified framework-preservation provenance

Related findings: MG-AUD-005  
Release reference: v1.9.11  
Status: Production verified

### Before

Shared elements could be described as framework preservation without exposing
the limits of the underlying evidence.

### After

Discovery and research outputs distinguish shared-element continuity from
validated structural preservation. They expose `shared_elements`,
`preservation_basis: "element_overlap"`, and
`structural_preservation_validated: false`. The existing
`preserved_framework` field remains as a compatibility alias.

### Impact

- Scientific result: **No**
- Ranking: **No**
- API contract: **Additive metadata; compatibility field retained**
- Data migration: **No**

---

## Reconciled discovery-score provenance

Related findings: MG-AUD-006  
Release reference: v1.9.12  
Status: Production verified

### Before

Candidate merging could combine score breakdowns from competing sources, so a
displayed breakdown did not always describe the final score.

### After

The winning source's score and breakdown remain together while contextual
discovery evidence is aggregated. For every candidate:

```text
sum(score_breakdown) = discovery_score
```

### Impact

- Scientific result: **No**
- Ranking: **No**
- API contract: **No**
- Data migration: **No**

---

## Source-diversity bonus based on distinct sources

Related findings: MG-AUD-007  
Release reference: v1.9.13  
Status: Production verified

### Before

Repeated encounters and previously aggregated scores could inflate the
source-diversity contribution.

### After

The bonus uses distinct discovery source types: one source receives `0`, two
receive `10`, and three receive `20`. Base-score provenance is kept separate
from the diversity bonus so the bonus is applied once.

### Impact

- Scientific result: **Yes**, where prior source accounting was inflated
- Ranking: **Potentially**, for affected candidates
- API contract: **No**
- Data migration: **No**

---

## Complete evidence required for favorable risk-quality bonuses

Related findings: MG-AUD-008  
Release reference: v1.9.14  
Status: Production verified

### Before

A calculable risk score based on incomplete material-element coverage could
still qualify for a favorable risk-quality bonus.

### After

Low- and medium-risk quality bonuses require complete constituent-element risk
evidence. Partial evidence remains visible but is not treated as favorable.
The LiFePO4 and inspected Na-phosphate reference materials had complete
coverage and therefore retained their results.

### Impact

- Scientific result: **Yes**, for incomplete-evidence materials
- Ranking: **Potentially**, across quality-dependent graph and pathway ranking
- API contract: **No**
- Data migration: **No**

---

## Exact community element membership

Related findings: MG-AUD-049  
Release reference: v1.9.14 development cycle  
Status: Production verified

### Before

Graph community summaries could count elements using formula substrings.

### After

Community analytics use exact element membership, preventing false matches
between short and longer chemical symbols.

### Impact

- Scientific result: **Yes**, for ambiguous symbols in community summaries
- Ranking: **No**
- API contract: **No**
- Data migration: **No**

---

## Multi-element research objectives

Related findings: MG-AUD-009  
Release reference: v1.9.15  
Status: Production verified

### Before

Objective alignment could evaluate only the first avoided and preferred
element even when several were requested.

### After

Every requested avoided and preferred element contributes to deterministic
objective evaluation. Responses expose matched and unmatched elements,
coverage percentages, and completion status. Single-element behavior remains
unchanged; multi-element objectives may now receive different scores.

### Impact

- Scientific result: **Yes**, for multi-element objectives
- Ranking: **Potentially**, for multi-element objectives
- API contract: **Additive objective-satisfaction metadata**
- Data migration: **No**

---

## Path-wide and endpoint-specific objective satisfaction

Related findings: MG-AUD-050  
Release reference: v1.9.16  
Status: Production verified

### Before

Path-wide transition events could be interpreted as proof that the final
material satisfied the same objective.

### After

Research responses distinguish objective events anywhere along a path from the
composition of the final endpoint. Endpoint matched and unmatched elements,
coverage, status, and interpretation are exposed separately.

### Impact

- Scientific result: **No**
- Ranking: **No**
- API contract: **Additive endpoint-evaluation fields**
- Data migration: **No**

---

## Stable pathway identity with tie-aware comparison

Related findings: MG-AUD-051  
Release reference: v1.9.17  
Status: Production verified

### Before

Comparative research could use rank as pathway identity, causing distinct tied
pathways to be conflated.

### After

Each pathway exposes a stable `pathway_id`, `position`, and `rank`.
Comparative summaries and element aggregation reference pathway identity while
preserving competition ranking and valid ties.

### Impact

- Scientific result: **No**
- Ranking: **No**
- API contract: **Additive pathway identity fields**
- Data migration: **No**

---

## Canonical criticality comparison terminology

Related findings: MG-AUD-036  
Release reference: v1.9.18  
Status: Production verified

### Before

The `criticality_direction` field used risk-oriented values even though it was
derived from `criticality_score`.

### After

Serialized values use `LOWER_CRITICALITY`, `HIGHER_CRITICALITY`,
`SAME_CRITICALITY`, and `UNKNOWN`. Numeric deltas, bonuses, ranking, and
human-readable explanations are unchanged.

### Impact

- Scientific result: **No**
- Ranking: **No**
- API contract: **Yes; serialized enum values changed**
- Data migration: **No**

---

## Direction-aware scenario explanations

Related findings: MG-AUD-052  
Release reference: Post-v1.9.18  
Status: Production verified

### Before

Scenario explanations could describe a positive adjustment as a negative
penalty or display a signed penalty inconsistently.

### After

Positive deltas are described as bonuses, negative deltas as penalties using
their absolute magnitude, and zero as no adjustment. The invariant is:

```text
scenario_delta = scenario_score - recommendation_score
```

Numeric scores, weights, ranking, and response fields are unchanged.

### Impact

- Scientific result: **No**
- Ranking: **No**
- API contract: **No; human-readable wording only**
- Data migration: **No**

---

## Correct discovery base-score selection and deterministic ties

Related findings: MG-AUD-053  
Release reference: Post-v1.9.18  
Status: Production verified

### Before

A stronger incoming source could be rejected when an earlier candidate's
displayed score appeared larger only because it already included a diversity
bonus. Exact-score ordering also lacked an explicit stable tie-breaker.

### After

Source merging compares base score with base score. Results remain sorted by
descending `discovery_score`, with ascending `material_id` used only for exact
ties. Valid equal-evidence scores, including the family-only `125.0` ties, are
preserved.

### Impact

- Scientific result: **Yes**, when the wrong base source previously won
- Ranking: **Yes**, for affected merges and deterministic exact ties
- API contract: **No**
- Data migration: **No**

---

## Evidence-calibrated phosphate and oxide explanations

Related findings: MG-AUD-011  
Date: 2026-07-22  
Status: Production verified

### Before

Researcher-facing explanations used phrases such as `shares phosphate
framework`, `shares oxide chemistry`, and path wording that could imply
validated structural preservation from elemental overlap alone.

### After

Explanations now state the evidence and its limit:

- both materials contain phosphorus and oxygen; structural framework
  similarity is not validated;
- both materials contain oxygen; oxide structure similarity is not validated;
- paths retain shared elemental overlap; structural preservation is not
  validated.

Compatibility fields such as `preserved_framework` remain available and are
qualified by element-overlap provenance.

### Impact

- Scientific result: **No**
- Ranking: **No**
- API contract: **No; human-readable wording only**
- Data migration: **No**

---

## Evidence-calibrated transition classifications

Related findings: MG-AUD-012  
Date: 2026-07-22  
Release reference: Post-v1.9.18  
Status: Production verified; replacement branches covered by automated tests

### Before

Element overlap or an evidence-free validator fallback could be serialized as
`framework_preserving`, implying stronger structural evidence than the system
possessed.

### After

Qualifying elemental-overlap transitions use `shared_element_continuity`.
The validator's evidence-free final fallback uses `candidate_transition`.
Compatibility evidence fields remain available and structural validation
continues to be reported as false.

### Impact

- Scientific result: **No; terminology now matches evidence strength**
- Ranking: **No; existing numeric weights were retained**
- API contract: **Yes; affected serialized transition values changed**
- Data migration: **No**

---

## Shared-element continuity scoring semantics

Related findings: MG-AUD-013  
Date: 2026-07-22  
Release reference: Post-v1.9.18  
Status: Locally verified; production deployment pending

### Before

The path-ranking score breakdown exposed `framework_preservation`, although
the dimension was computed from shared-element overlap rather than independent
bonding, structure-matching, or crystallographic evidence.

### After

The score dimension is `shared_element_continuity`. Research evidence,
pathway analysis, comparative explanations, and provenance use the same term
and explicitly state that structural preservation is not validated. Existing
continuity weights and valid final scores are retained.

Regression checks also confirmed that one-hop path efficiency remains `10.0`
and empty paths receive `0.0` efficiency. Local objective exploration for
material 5 returned `shared_element_continuity: 30` with the expected total
score of `95.65`.

### Impact

- Scientific result: **No; the evidence label is now scientifically qualified**
- Ranking: **No; final weights and valid rankings are unchanged**
- API contract: **Yes; one score-breakdown key changed**
- Data migration: **No**

---

## Contributor-aware recommendation explanations

Related findings: MG-AUD-037  
Date: 2026-07-23  
Release reference: Post-v1.9.18  
Status: Locally verified; production deployment pending

### Before

Recommendation reasons mixed scoring contributors with contextual comparisons.
Criticality could be mentioned even when its preference was disabled, shared
elements and applications were not identified as the basis of the similarity
score, and the low-energy-above-hull contribution was omitted from the reason.

### After

Recommendation reasons now distinguish:

- the similarity score and its shared-element/shared-application basis;
- active score contributors, including stability, qualifying low energy above
  hull, and criticality when lower criticality is preferred;
- non-scoring criticality comparison under `context` when the preference is
  disabled; and
- the final recommendation score.

Local checks confirmed that a similarity score of `130.0`, stability bonus of
`10`, and low-energy bonus of `5` produce `145.0` when criticality preference is
disabled. With the preference enabled, the applicable criticality adjustment
is also reflected in both the score and explanation.

### Impact

- Scientific result: **No**
- Ranking: **No; scoring policy and numeric calculations are unchanged**
- API contract: **No; human-readable wording only**
- Data migration: **No**