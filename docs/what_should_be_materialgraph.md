# What MaterialGraph Should Be

> **Project direction, scientific boundaries, and development principles**
>
> Initial version derived from architecture and code review through
> **v1.9.6 — Endpoint-Sensitive Research Ranking**.

## 1. Purpose of This Document

This document defines what MaterialGraph should become and what it should avoid
becoming.

It is intentionally different from a feature list, roadmap, or architecture
inventory. It records project-level principles discovered by reviewing the
actual implementation and real API behavior.

This document should be updated only when code review, researcher feedback,
real-response verification, or external validation reveals something important
about:

- researcher usefulness;
- scientific meaning;
- verifiability;
- system boundaries;
- architecture integration;
- misleading terminology;
- missing capabilities;
- duplicated intelligence;
- uncertainty;
- validation needs.

MaterialGraph should not grow by accumulating impressive-sounding features. It
should grow by improving the quality, usefulness, traceability, and scientific
honesty of research decision support.

---

## 2. Core Identity

MaterialGraph should be:

> **A deterministic, explainable, graph-driven materials research intelligence
> system that helps researchers explore, compare, inspect, and validate material
> opportunities while keeping scientific judgement with the researcher.**

MaterialGraph may:

- organize materials and relationships;
- generate constrained discovery opportunities;
- explore multi-hop pathways;
- rank using explicit deterministic dimensions;
- expose score breakdowns;
- compare alternatives;
- identify evidence gaps;
- expose assumptions;
- preserve unresolved ties;
- prioritize validation needs;
- show why an opportunity was generated;
- help researchers decide what to inspect next.

MaterialGraph must not claim to replace:

- domain expertise;
- literature review;
- crystallographic analysis;
- DFT or other computational validation;
- synthesis planning by experts;
- laboratory experiments;
- peer review;
- scientific judgement.

---

## 3. The System Should Work as One Intelligence Pipeline

The reviewed implementation shows a meaningful layered flow:

```text
Research Objective
        │
        ▼
Discovery Chain Generation
        │
        ▼
Objective Filtering
        │
        ▼
Deterministic Path Ranking
        │
        ▼
Research Opportunity Construction
        │
        ▼
Evidence Enrichment
        │
        ▼
Comparative Research Intelligence
        │
        ▼
Endpoint-Sensitive Tie Analysis
        │
        ▼
Researcher Decision Support
```

This is a direction MaterialGraph should preserve.

New capabilities should normally improve or enrich this flow rather than create
parallel, disconnected intelligence systems.

A new service should answer:

1. What upstream output does it consume?
2. What genuinely new information does it add?
3. Which downstream capability uses that information?
4. Why does this logic belong here rather than in an existing service?
5. Can the researcher inspect the result?

If these questions are unclear, implementation should not begin.

---

## 4. MaterialGraph Should Prefer Honest Uncertainty Over Artificial Precision

The verified LiFePO4 → Na/phosphate case is an important project principle.

For the objective:

- avoid `Li`;
- prefer `Na`;
- preserve `Fe`, `P`, `O`;
- target `phosphate`;
- `max_hops = 2`;
- `limit = 5`;

MaterialGraph returned five scientifically distinct endpoint opportunities:

- Na3Fe3(PO4)4
- Na9Fe3P8O29
- NaFeP2O7
- NaFePO4
- Na3Fe(PO4)2

All five received the same scientific usefulness score of `94.95`.

The correct response was not to invent a tie-breaker.

The v1.9.5 comparative layer exposed meaningful differences while preserving the
tie. The v1.9.6 endpoint-sensitive layer examined available endpoint evidence
and still preserved the tie because current evidence did not justify
deterministic differentiation.

This behavior should remain a core principle:

> **If available evidence cannot justify differentiation, MaterialGraph should
> say so explicitly.**

A genuine tie is a valid scientific decision-support output.

---

## 5. MaterialGraph Should Distinguish Signal From Proof

A major finding from code review is that some current scientific language can be
stronger than the underlying computation.

For example, current transition logic derives `preserved_framework` from the
intersection of element symbols present in the source and target materials.

That is useful as a deterministic compositional signal.

However:

> **Shared elements are not proof of preserved crystal structure, bonding
> topology, phase behavior, coordination environment, or functional framework.**

Therefore MaterialGraph should distinguish among concepts such as:

- shared elemental composition;
- preserved chemistry overlap;
- inferred family continuity;
- encoded relationship continuity;
- structural framework preservation;
- experimentally validated preservation.

These concepts must not be treated as interchangeable.

### Directional rule

Until stronger structural evidence exists, outputs derived from element
intersection should use terminology that reflects what is actually known.

Prefer language such as:

- `shared_compositional_framework`
- `shared_chemistry_elements`
- `composition_overlap`
- `preserved_element_set`

Avoid implying verified structural preservation unless supported by appropriate
structural evidence.

This is not merely a naming issue. Terminology affects researcher trust and the
scientific interpretation of downstream ranking, confidence, comparison, and
evidence outputs.

---

## 6. MaterialGraph Should Make Objective Semantics Match Actual Execution

Current objective handling exposes list-shaped concepts such as:

- `avoid_elements`
- `prefer_elements`
- `preserve_elements`

However, reviewed objective-chain execution currently forwards only the first
avoid element and first prefer element into chain generation and path ranking.

This creates an important principle:

> **The apparent expressiveness of a research objective must match the actual
> semantics executed by the system.**

MaterialGraph should not accept a richer objective shape while silently
executing only a subset unless that limitation is explicit.

Future work should determine whether to:

- support all avoid/prefer elements end to end;
- constrain the schema to actual supported semantics; or
- expose explicit warnings when only part of an objective is applied.

The correct choice should be made after tracing all dependent services. It
should not be patched locally without understanding candidate generation,
transition validation, ranking, comparison, and backward compatibility.

---

## 7. Search-Space Construction Is Part of Scientific Meaning

The reviewed chain service is production-aware:

- bounded hop depth;
- bounded expansion;
- cycle prevention;
- candidate caching;
- relationship caching;
- family-result caching;
- delegated transition validation.

These are valuable engineering properties.

However, the chain-generation process also determines which opportunities can
ever reach downstream intelligence.

Therefore:

> **Search-space construction is not only a performance concern. It is part of
> the scientific behavior of MaterialGraph.**

Limits such as:

- maximum hops;
- expansion limits;
- candidate ordering;
- family-neighborhood selection;
- preferred-element filtering;
- chain completion rules;

can influence which research opportunities are visible and which remain unseen.

MaterialGraph should make these constraints inspectable and should avoid
presenting a bounded search result as exhaustive discovery.

Production safety and scientific completeness are different concerns. The
system should represent that distinction clearly.

---

## 8. Transition Validation Should Be Conservative and Explainable

Current transition validation requires recognized relationships and at least one
strong relationship before accepting a transition.

This conservative direction should be preserved.

MaterialGraph should prefer:

- explicit accepted relationship classes;
- deterministic validation rules;
- inspectable rejection reasons;
- explicit removed elements;
- explicit introduced elements;
- explicit shared elements;
- traceable transition types.

It should avoid:

- accepting graph adjacency as sufficient scientific plausibility;
- inferring strong chemistry from weak similarity alone;
- hiding why a transition was accepted;
- silently upgrading an inferred relationship into verified evidence.

A transition should be understood as:

> **an explainable research hypothesis or exploration step supported by encoded
> relationships and available evidence**

—not as proof that the physical transformation is experimentally feasible.

---

## 9. MaterialGraph Should Preserve Layer Ownership

The reviewed architecture currently has a useful separation of concerns:

- objective service orchestrates objective-constrained chain selection;
- chain service constructs bounded multi-hop opportunities;
- transition validator owns transition acceptance;
- path ranking owns scientific usefulness scoring;
- scientific pathway analysis constructs researcher-facing opportunities;
- evidence intelligence owns evidence summaries and gaps;
- comparative intelligence owns comparison;
- endpoint-sensitive ranking examines tied endpoints without replacing the
  original score.

This separation should be protected.

### Ownership rule

New capabilities should reuse existing outputs rather than recreate them.

Examples:

- comparison should not become a second ranking engine;
- endpoint-sensitive analysis should not recreate material quality;
- evidence intelligence should not invent transition plausibility;
- graph centrality should not silently become scientific usefulness;
- confidence should not duplicate the total score under a different name;
- validation planning should not fabricate missing evidence.

---

## 10. MaterialGraph Should Treat Researcher-Facing Language as Part of the Model

Explanations are not cosmetic.

Terms such as:

- `preserved_framework`;
- `scientific_plausibility`;
- `confidence`;
- `evidence_readiness`;
- `stable`;
- `strong`;
- `validated`;

carry scientific meaning.

MaterialGraph should ensure that the strength of its language does not exceed
the strength of the underlying evidence.

Every researcher-facing term should be traceable to:

- a stored property;
- a deterministic rule;
- a graph fact;
- an attributed external source;
- or an explicitly labeled inference.

If a term is inferential, the output should make that visible.

---

## 11. MaterialGraph Should Separate Internal Consistency From External Validity

Passing tests proves important things:

- code behavior is stable;
- contracts are preserved;
- deterministic rules execute as expected;
- regressions can be detected.

But passing tests does not prove:

- scientific correctness;
- synthesis feasibility;
- structural preservation;
- experimental performance;
- usefulness to researchers.

MaterialGraph should maintain two distinct validation tracks.

### Engineering validation

- unit tests;
- integration tests;
- API contract tests;
- performance tests;
- regression tests;
- production monitoring.

### Scientific and researcher validation

- representative case studies;
- literature cross-checking;
- domain-expert review;
- comparison with known materials behavior;
- DFT or domain-specific computational checks where appropriate;
- researcher workflow feedback;
- experimental validation where possible.

Both tracks are necessary.

---

## 12. MaterialGraph Should Become Verifiable, Not Merely Explainable

Explainability answers:

> Why did the system produce this result?

Verifiability should also answer:

> What facts support it, where did those facts come from, what is inferred, what
> is missing, and how could a researcher check it?

MaterialGraph should increasingly make visible:

- source provenance;
- property provenance;
- rule provenance;
- relationship provenance;
- evidence attribution;
- missing evidence;
- assumptions;
- validation priorities;
- uncertainty boundaries.

A polished explanation without inspectable support is not enough for a research
system.

---

## 13. MaterialGraph Should Be Useful to More Than One Research Persona Without Becoming Vague

Potential users may include:

- materials researchers;
- computational materials scientists;
- battery researchers;
- R&D teams;
- critical-material analysts;
- supply-risk researchers;
- research program decision-makers.

MaterialGraph should not claim equal readiness for all of these users.

Each use case should be earned through:

- appropriate data;
- appropriate objectives;
- appropriate evidence;
- representative case studies;
- user feedback.

The shared platform can remain broad, while validated workflows should be
specific.

---

## 14. New Capabilities Should Be Evidence-Driven

Before naming or implementing the next milestone, inspect:

1. current code;
2. current service ownership;
3. a real API response;
4. the exact limitation;
5. what evidence is missing;
6. what a researcher would need next.

Then choose the smallest capability that improves the system.

Potential future directions may include:

- stronger evidence provenance;
- validation planning;
- multi-element objective semantics;
- structural evidence integration;
- property-specific endpoint analysis;
- literature-linked evidence;
- researcher-facing case-study workflows.

These are possibilities, not automatic roadmap commitments.

The next capability should be selected because the current system demonstrates a
need for it.

---

## 15. A Practical Gate for Every Future Feature

Before implementation, answer:

1. What researcher question does this capability answer?
2. What current limitation demonstrates the need?
3. Which layer owns the logic?
4. What existing services does it reuse?
5. What new information does it add?
6. What is the scientific basis?
7. Can the researcher inspect the basis?
8. Does it duplicate an existing score or signal?
9. What happens when data is missing?
10. Can uncertainty remain unresolved?
11. Can a genuine tie remain a tie?
12. What terminology could overstate the evidence?
13. What requires external validation?
14. What real case study will verify usefulness?
15. What production cost or search bias could it introduce?

If these questions cannot be answered clearly, the feature should not be added
yet.

---

## 16. Current Direction After v1.9.6

The immediate priority should not be feature accumulation.

The priority should be:

1. understand the current code path end to end;
2. document strategically important findings;
3. identify semantic mismatches;
4. identify where terminology overstates evidence;
5. identify where search constraints shape scientific outputs;
6. verify representative real responses;
7. build reference case studies;
8. seek researcher feedback;
9. add capabilities only where demonstrated gaps exist.

The project is now mature enough that restraint is part of good engineering.

---

## 17. North Star

MaterialGraph should help researchers answer:

- What opportunities exist?
- Why were they generated?
- What relationships support them?
- What trade-offs distinguish them?
- What evidence is available?
- What evidence is missing?
- Which assumptions are weak?
- What cannot currently be differentiated?
- What should be validated next?
- How can the reasoning be independently checked?

MaterialGraph should not hide uncertainty behind ranking precision.

It should make the boundary between:

- known;
- derived;
- inferred;
- missing;
- uncertain;
- and experimentally unvalidated

as clear as possible.

> **The goal is not to make MaterialGraph appear certain. The goal is to make
> materials research exploration more structured, inspectable, verifiable, and
> useful while preserving scientific judgement with the researcher.**
