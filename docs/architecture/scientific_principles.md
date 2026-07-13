# MaterialGraph Scientific Principles

## Introduction

MaterialGraph is built on the belief that scientific software should assist researchers through deterministic, explainable, and transparent computation rather than replace scientific judgment.

The platform is designed to compute, rank, explain, and contextualize research opportunities while preserving researcher autonomy.

These principles guide every architectural and implementation decision within MaterialGraph.

---

# 1. Deterministic Reasoning

MaterialGraph uses deterministic algorithms for all scientific reasoning.

The same inputs should always produce the same outputs.

Scientific conclusions should never depend on non-deterministic reasoning.

---

# 2. Explainability

Every recommendation should be explainable.

MaterialGraph should always provide the reasoning behind:

- recommendations
- rankings
- graph traversal
- pathway selection
- scientific opportunities

Opaque scores without explanation are not acceptable.

---

# 3. Researcher-in-the-Loop

MaterialGraph assists scientific research.

Researchers make scientific decisions.

MaterialGraph never replaces scientific judgement.

The platform presents opportunities.

Researchers decide which opportunities to investigate.

---

# 4. Rank Rather Than Discard

MaterialGraph follows an inclusive exploration philosophy.

By default, materials are:

- ranked
- explained
- warned
- scored

They are not discarded unless explicit constraints require filtering.

Potentially valuable discoveries should remain visible whenever scientifically reasonable.

---

# 5. Facts Before Recommendations

Recommendations should be supported by explicit scientific facts.

Examples include:

- preserved frameworks
- substitution pathways
- material quality
- graph relationships
- community membership
- criticality analysis

MaterialGraph should distinguish computed facts from interpretation.

---

# 6. Explicit Uncertainty

Scientific uncertainty should never be hidden.

MaterialGraph should clearly distinguish between:

Known

- graph relationships
- computed scores
- pathway structure
- objective alignment

Unknown

- synthesis feasibility
- laboratory validation
- industrial scalability
- long-term performance

Unknowns should be presented explicitly.

---

# 7. Scientific Opportunities

MaterialGraph does not search for a single "best" answer.

Instead, it presents multiple scientifically plausible opportunities.

Each opportunity should describe:

- strengths
- trade-offs
- risks
- assumptions
- confidence
- required validation

Researchers choose which opportunity to pursue.

---

# 8. Research Evidence

MaterialGraph separates computation from evidence.

Deterministic graph intelligence computes opportunities.

Researchers generate evidence through:

- experiments
- simulations
- literature
- observations

Evidence enriches the platform but should not alter deterministic computation without explicit validation.

---

# 9. Continuous Scientific Evolution

MaterialGraph is designed as a scientific platform that evolves incrementally.

New capabilities should strengthen existing deterministic foundations rather than replace them.

The long-term vision is an explainable scientific exploration platform that combines graph intelligence, research workflows, and scientific knowledge management.

---

# 10. Structured Scientific Data Takes Precedence

Whenever structured scientific data is available, MaterialGraph shall use it as
the canonical source of truth.

Derived or inferred representations (such as parsing chemical formulas) should
never override structured scientific measurements.

Scientific calculations should preserve the fidelity of the original data source.

---

# 11. Unknown Evidence Is Not Favorable Evidence

Missing scientific evidence shall never be interpreted as favorable evidence.

MaterialGraph distinguishes between:

- known favorable evidence
- known unfavorable evidence
- unknown evidence

Unknown evidence should remain explicit and should not improve rankings,
scores, confidence, or recommendations.

---

# 12. Scientific Semantics Before Performance

Performance optimizations must preserve scientific semantics.

Caching, indexing, batching, graph expansion limits, or parallel execution
must not change scientific meaning unless explicitly documented and validated.

Scientific correctness always takes precedence over computational efficiency.

---

# 13. One Canonical Scientific Interpretation

MaterialGraph should maintain a single canonical implementation for each
scientific concept.

Normalization, scoring, composition handling, and evidence interpretation
should be implemented once and reused throughout the platform.

Duplicated scientific logic increases the risk of inconsistent reasoning.