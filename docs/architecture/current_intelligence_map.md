# MaterialGraph Current Intelligence Map

> **Architecture guardrail for understanding, extending, and validating the
> MaterialGraph intelligence system**

## 1. Purpose

This document maps the current MaterialGraph intelligence architecture as of
**v1.9.6 — Endpoint-Sensitive Research Ranking**.

Its purpose is to make the existing system understandable before new
capabilities are added. It defines:

- what each intelligence layer is responsible for;
- what inputs each layer consumes;
- what outputs each layer produces;
- which existing capabilities and services it should reuse;
- what downstream layers depend on it;
- what each layer must not do;
- where current scientific and engineering limitations remain.

This document is an architectural guardrail, not a claim of scientific
validation.

MaterialGraph is designed as deterministic, explainable, researcher-in-the-loop
decision support. It may compute, rank, compare, explain, contextualize, and
prioritize research opportunities. Researchers remain responsible for
scientific judgement, external verification, computational validation, synthesis
decisions, and experimental validation.

---

## 2. Governing Architecture Principles

Every new capability should satisfy the following checks before implementation.

### 2.1 Researcher usefulness

The capability must help answer a concrete research or decision-support
question.

### 2.2 Scientific grounding

The capability must be grounded in existing material properties, graph facts,
objective constraints, deterministic rules, attributed evidence, or another
explicitly identified source.

### 2.3 Verifiability

A researcher should be able to inspect why an output was produced and which
facts, assumptions, scores, or missing evidence influenced it.

### 2.4 Non-duplication

A new layer must reuse existing intelligence where possible. It must not
silently rescore the same concept under a new name.

### 2.5 Explicit uncertainty and validation boundaries

The system must distinguish among:

- available evidence;
- derived deterministic signals;
- assumptions;
- missing evidence;
- unresolved ties;
- conclusions requiring external validation.

### 2.6 Genuine ties are valid outputs

MaterialGraph must not force different scores or rankings when available
evidence does not justify differentiation.

### 2.7 Researcher autonomy

MaterialGraph may prioritize and explain opportunities, but it must not present
its ranking as a replacement for scientific judgement.

### 2.8 Real-response verification

A capability is not complete merely because unit tests pass. It should also be
verified against representative end-to-end API responses and known research
objectives.

---

## 3. Current Intelligence Flow

```text
Material / Element / Property Data
                │
                ▼
      Foundation Intelligence
                │
                ▼
       Discovery Intelligence
                │
                ▼
   Knowledge Graph Intelligence
                │
                ├──────────────┐
                ▼              │
      Material Quality         │
                │              │
                └──────┬───────┘
                       ▼
          Research Intelligence
                       │
                       ▼
          Evidence Intelligence
                       │
                       ▼
 Comparative Research Intelligence
                (v1.9.5)
                       │
                       ▼
 Endpoint-Sensitive Research Ranking
                (v1.9.6)
                       │
                       ▼
      Researcher Decision Support
```

This flow is conceptual rather than a requirement that every request execute
every layer. Production paths may use caching, bulk loading, lightweight graph
expansion, or fast candidate modes.

---

## 4. Intelligence Layer Map

## 4.1 Foundation Intelligence

### Purpose

Represent core materials knowledge and provide reusable deterministic signals
for all higher layers.

### Current capabilities

- Material Graph Foundation
- Material Neighborhood Intelligence
- Material Family Intelligence
- Similarity Engine
- Recommendation Engine
- Criticality Analysis
- Scenario Policy Engine

### Primary inputs

- material records;
- element composition;
- material-element relationships;
- family or chemistry relationships;
- material properties;
- criticality and risk inputs;
- scenario constraints and policies.

### Primary outputs

- material relationships;
- related-material neighborhoods;
- family associations;
- similarity signals;
- recommendation signals;
- criticality signals;
- scenario-alignment signals.

### Downstream consumers

- Discovery Intelligence
- Knowledge Graph Intelligence
- Material Quality
- Research Objective Exploration

### Must not do

- invent scientific evidence;
- claim synthesis feasibility;
- duplicate pathway ranking;
- make researcher decisions;
- treat similarity as proof of scientific equivalence.

### Known limitations

- usefulness depends on source data coverage and quality;
- relationship rules may be scientifically coarse for some domains;
- family and similarity relationships require external scientific validation
  for high-stakes use.

---

## 4.2 Discovery Intelligence

### Purpose

Generate explainable material candidates and pathways under explicit research
constraints.

### Current capabilities

- Discovery Candidate Engine
- Discovery Scoring
- Discovery Warnings
- Explainable Discovery
- Substitution Path Engine
- Multi-Hop Discovery
- Discovery Path Ranking
- Research Objective Exploration

### Primary inputs

- foundation-layer material relationships;
- avoid/prefer element constraints;
- preserve-element constraints;
- target family;
- hop limits;
- candidate limits;
- stability preferences;
- criticality preferences;
- recommendation and scenario signals.

### Primary outputs

- candidate materials;
- discovery scores and score breakdowns;
- warnings;
- substitution explanations;
- multi-hop chains;
- objective-aligned pathways;
- pathway transitions and scientific reasons.

### Downstream consumers

- Knowledge Graph Intelligence
- Scientific Pathway Analysis
- Comparative Research Intelligence

### Must not do

- interpret a generated candidate as experimentally validated;
- force pathways beyond configured production safety limits;
- hide objective violations;
- duplicate evidence-readiness logic;
- add arbitrary ranking tie-breakers.

### Known limitations

- candidate quality depends on graph coverage;
- multi-hop expansion can increase computational cost;
- objective satisfaction does not prove synthesis feasibility;
- distinct endpoints can remain tied under pathway-level dimensions.

---

## 4.3 Knowledge Graph Intelligence

### Purpose

Represent and analyze the structural context around materials, transitions,
paths, and communities.

### Current capabilities

- Graph Builder
- Graph Traversal
- BFS
- DFS
- Shortest Path
- Weighted Shortest Path / Dijkstra
- K-Shortest Paths
- K-Best Scientific Paths
- Graph Analytics
- Degree Centrality
- Betweenness Centrality
- Closeness Centrality
- Material Importance Scoring
- Community Detection
- Community Intelligence
- Ranked Subgraph Exploration
- Node Intelligence
- Edge Intelligence

### Primary inputs

- material nodes;
- explainable material relationships;
- discovery transitions;
- node properties;
- edge scientific facts;
- traversal limits;
- objective constraints.

### Primary outputs

- graphs and subgraphs;
- traversed paths;
- ranked paths;
- communities;
- graph metrics;
- node intelligence;
- edge intelligence;
- structural context for research exploration.

### Downstream consumers

- Discovery pathway exploration
- Research Intelligence
- future researcher-facing graph exploration
- future validation and case-study workflows

### Must not do

- equate graph proximity with scientific proof;
- use centrality as a substitute for material quality;
- hide traversal constraints;
- infer unsupported chemistry solely from topology.

### Known limitations

- graph conclusions are bounded by graph construction rules and data coverage;
- structural importance is not identical to scientific usefulness;
- production traversal depth requires careful performance controls.

---

## 4.4 Material Quality Intelligence

### Purpose

Provide reusable deterministic material-level quality, stability, risk, and
criticality signals.

### Current capabilities

- stability scoring;
- energy-above-hull handling;
- criticality scoring;
- risk scoring;
- quality scoring;
- shared quality caching;
- bulk quality loading;
- DB-aware production use.

### Primary inputs

- endpoint and intermediate material properties;
- stability information;
- energy above hull;
- criticality inputs;
- risk inputs.

### Primary outputs

- `stability_score`;
- `energy_above_hull`;
- `criticality_score`;
- `risk_score`;
- `quality_score`.

### Downstream consumers

- Discovery Path Ranking
- Node Intelligence
- Research Intelligence
- Endpoint-Sensitive Research Ranking

### Must not do

- duplicate pathway plausibility;
- treat a capped or bucketed quality score as fine-grained scientific evidence;
- silently convert missing properties into unjustified certainty;
- claim experimental stability from a derived score alone.

### Known limitations

- bucketed or capped scoring can cause distinct materials to collapse to equal
  values;
- missing or coarse properties reduce differentiation;
- material-level quality does not alone establish pathway usefulness.

---

## 4.5 Research Intelligence

### Purpose

Transform discovery chains into structured, explainable research opportunities.

### Current capabilities

- Scientific Pathway Analysis
- Explainable Confidence
- Research Opportunity Analysis

### Primary inputs

- objective-generated chains;
- ranked pathway outputs;
- material quality;
- transition facts;
- preserved, removed, and introduced elements;
- objective alignment;
- pathway score breakdowns.

### Primary outputs

- pathway opportunities;
- scientific usefulness scores;
- pathway facts;
- confidence explanations;
- research opportunity context;
- explicit researcher decision boundaries.

### Downstream consumers

- Evidence Intelligence
- Comparative Research Intelligence
- Endpoint-Sensitive Research Ranking

### Must not do

- invent literature support;
- interpret a score as proof;
- hide weak assumptions;
- override researcher judgement;
- duplicate comparison logic.

### Known limitations

- pathway-level dimensions may be identical across scientifically distinct
  endpoints;
- usefulness scoring remains constrained by available properties and rules;
- external validation is still required.

---

## 4.6 Evidence Intelligence

### Purpose

Make the support, gaps, assumptions, and validation needs of each research
opportunity explicit.

### Current capabilities

- Structured Evidence Summary
- Evidence Attribution
- Explainable Missing Evidence
- Structured Weak Assumptions
- Validation Priorities
- Evidence Readiness

### Primary inputs

- pathway opportunities;
- existing scientific facts;
- material properties;
- objective constraints;
- transition explanations;
- available evidence signals;
- identified missing evidence.

### Primary outputs

- structured evidence summaries;
- attributed evidence;
- missing-evidence explanations;
- weak assumptions;
- validation priorities;
- evidence-readiness classification.

### Downstream consumers

- Comparative Research Intelligence
- Endpoint-Sensitive Research Ranking
- future validation planning

### Must not do

- present derived signals as external experimental evidence;
- fabricate citations or literature support;
- convert missing evidence into a positive signal;
- imply that evidence readiness equals scientific truth.

### Known limitations

- readiness categories may be coarse;
- equal readiness labels can hide differences not represented in current data;
- literature-backed evidence depth remains a future validation concern.

---

## 4.7 Comparative Research Intelligence — v1.9.5

### Purpose

Compare existing pathway opportunities without replacing their underlying
ranking logic or inventing a winner.

### Current capabilities

- deterministic multi-pathway comparison;
- comparative strengths;
- comparative trade-offs;
- comparative research gaps;
- comparative evidence readiness;
- comparative assumptions;
- adjacent pairwise pathway comparisons;
- score-dimension difference explanations;
- preservation of lower-ranked pathway advantages;
- tie-aware pathway comparisons;
- endpoint material comparisons;
- neutral first-pathway / second-pathway semantics;
- backward-compatible comparison aliases;
- comparative element opportunity highlights;
- introduced-element signals;
- removed/avoided-element signals;
- preserved-framework element signals;
- pathway-grounded element intelligence;
- explicit `requires_validation` boundaries;
- researcher autonomy preservation.

### Primary inputs

- already-built pathway opportunities;
- existing score breakdowns;
- endpoint identities;
- evidence readiness;
- assumptions;
- pathway scientific facts;
- introduced, removed, avoided, and preserved elements.

### Primary outputs

- pairwise comparisons;
- strengths and trade-offs;
- research-gap comparisons;
- evidence-readiness comparisons;
- assumption comparisons;
- endpoint comparisons;
- element opportunity highlights;
- explicit ties.

### Downstream consumers

- researcher decision support;
- future researcher-facing UI;
- case-study analysis.

### Must not do

- rerank pathways;
- add a second scientific usefulness score;
- invent endpoint superiority;
- suppress lower-ranked advantages;
- turn comparison into recommendation without evidence.

### Known limitations

- comparison can expose a tie but cannot resolve one without justified
  endpoint-sensitive evidence;
- adjacent pairwise comparison is not a substitute for all-pairs analysis where
  that is scientifically necessary.

---

## 4.8 Endpoint-Sensitive Research Ranking — v1.9.6

### Purpose

Examine equal-score pathway groups and determine whether existing
endpoint-specific evidence justifies deterministic differentiation.

### Primary inputs

- existing pathway opportunities;
- existing `scientific_usefulness_score`;
- endpoint material identity;
- endpoint-specific quality;
- stability;
- energy above hull;
- criticality;
- risk;
- evidence readiness.

### Primary outputs

- equal-score groups;
- differentiation status;
- preserved-tie status;
- endpoint evidence snapshots;
- explicit reasons for differentiation or non-differentiation;
- `score_preserved`;
- explicit indication that no duplicate endpoint score was added.

### Downstream consumers

- researcher decision support;
- future validation planning;
- case-study analysis.

### Must not do

- modify the original scientific usefulness score;
- add arbitrary tie-breakers;
- force unique ordering;
- duplicate Material Quality logic;
- duplicate Evidence Intelligence logic;
- claim endpoint superiority from unavailable evidence.

### Known limitations

- endpoint differentiation is only as strong as available endpoint properties
  and evidence;
- equivalent endpoint evidence correctly preserves ties;
- coarse or bucketed upstream signals may limit differentiation.

### Verified real-response behavior

For the LiFePO4 research objective:

- avoid `Li`;
- prefer `Na`;
- preserve `Fe`, `P`, `O`;
- target `phosphate`;
- `max_hops = 2`;
- `limit = 5`.

MaterialGraph returned five scientifically distinct endpoint opportunities:

- Na3Fe3(PO4)4
- Na9Fe3P8O29
- NaFeP2O7
- NaFePO4
- Na3Fe(PO4)2

All five received a scientific usefulness score of `94.95`.

The v1.9.5 comparative layer exposed the tie without inventing a winner. The
v1.9.6 endpoint-sensitive layer then examined available endpoint-specific
evidence and preserved the tie because current evidence did not justify
deterministic differentiation.

This is intended behavior.

---

## 5. Cross-Layer Ownership Rules

The following ownership rules should be preserved to prevent architecture drift.

| Concern | Owning layer | Other layers should |
| --- | --- | --- |
| Material relationships | Foundation Intelligence | consume, not redefine |
| Candidate generation | Discovery Intelligence | consume candidates |
| Path generation | Discovery / Graph Intelligence | analyze existing paths |
| Graph topology | Knowledge Graph Intelligence | consume metrics carefully |
| Material quality | Material Quality | reuse quality outputs |
| Pathway usefulness | Research / Path Ranking | preserve existing score |
| Evidence gaps | Evidence Intelligence | compare, not recreate |
| Pathway comparison | Comparative Intelligence | avoid reranking |
| Tied endpoint analysis | Endpoint-Sensitive Ranking | preserve original score |
| Experimental decision | Researcher | support, never replace |

---

## 6. Production Architecture Considerations

The intelligence architecture must remain compatible with current production
hardening.

Current production-oriented capabilities include:

- service modularization;
- fast candidate mode;
- lightweight graph expansion;
- request-level caching;
- bulk criticality loading;
- bulk risk loading;
- bulk quality loading;
- threshold-based timing logs;
- documented performance baselines;
- focused tests;
- API integration tests;
- full-suite regression testing.

New intelligence layers should avoid:

- repeated database queries per pathway;
- rebuilding graphs unnecessarily;
- recomputing existing quality signals;
- hidden N+1 query patterns;
- unbounded traversal;
- expensive all-pairs comparisons without demonstrated need.

---

## 7. Current System Strengths

MaterialGraph currently has several architectural strengths:

1. **Deterministic reasoning**  
   Scientific computation does not depend on opaque LLM reasoning.

2. **Explainability**  
   Scores, transitions, assumptions, evidence gaps, and comparison reasons are
   exposed.

3. **Layer separation**  
   Discovery, graph analysis, quality, evidence, comparison, and endpoint
   analysis have distinct responsibilities.

4. **Researcher autonomy**  
   The system preserves explicit decision boundaries.

5. **Tie awareness**  
   Equal evidence is allowed to remain equal.

6. **Production awareness**  
   Performance controls, caching, bulk loading, and timing instrumentation are
   part of the architecture.

7. **Real-response testing**  
   Representative scientific objectives are used to inspect end-to-end
   behavior.

---

## 8. Current System Limitations

The following limitations should guide future work.

### 8.1 Scientific validation

Internal consistency and deterministic reasoning do not establish external
scientific validity.

### 8.2 Data coverage

Missing or coarse material properties constrain ranking and differentiation.

### 8.3 Evidence depth

Structured evidence readiness is useful, but richer externally verifiable
evidence may be required for researcher trust.

### 8.4 Endpoint differentiation

Scientifically distinct endpoints can remain tied when current evidence is
equivalent or too coarse.

### 8.5 Synthesis feasibility

MaterialGraph does not currently prove that a proposed pathway or endpoint is
synthesizable.

### 8.6 Computational validation

MaterialGraph does not replace DFT or other domain-specific computational
methods.

### 8.7 Experimental validation

MaterialGraph does not replace laboratory validation.

### 8.8 Researcher workflow validation

The system still requires structured feedback from real researchers to confirm
which outputs are useful, confusing, missing, or misleading.

---

## 9. Gate for New Capabilities

Before implementing a new capability, answer all of the following.

1. What concrete researcher or decision-support question does it answer?
2. Which current layer should own it?
3. Which existing services and outputs can it reuse?
4. What new information does it add?
5. Is that information scientifically grounded?
6. Can the result be inspected and audited?
7. Does it duplicate an existing score or rule?
8. What happens when evidence is missing?
9. Can a genuine tie remain a tie?
10. What explicitly requires validation?
11. What focused tests are required?
12. What API integration test is required?
13. Which real response or case study will verify usefulness?
14. What is the production performance risk?
15. Does it preserve researcher autonomy?

If these questions cannot be answered clearly, implementation should not begin.

---

## 10. Recommended Immediate Development Discipline

For each next milestone:

1. inspect the current implementation;
2. trace the current end-to-end data flow;
3. reproduce the real response that motivates the change;
4. identify the exact limitation;
5. verify that an existing service does not already own the logic;
6. propose the smallest scientifically defensible increment;
7. implement one layer at a time;
8. add focused unit tests;
9. add or update API integration tests;
10. run the full test suite;
11. inspect a real endpoint response;
12. update architecture documentation;
13. only then choose the next capability.

---

## 11. Current Architectural Position

As of v1.9.6, MaterialGraph should be understood as an:

> **advanced deterministic research-software prototype for explainable,
> graph-driven materials exploration and researcher decision support**

It is beyond a toy graph project and beyond a simple candidate recommender. It
already integrates discovery, graph analysis, material quality, research
opportunity analysis, evidence reasoning, comparative intelligence, and
endpoint-sensitive tie analysis.

However, it should not yet be described as a scientifically validated research
platform. The next phase of maturity depends increasingly on:

- researcher usefulness;
- external verifiability;
- representative case studies;
- domain-expert feedback;
- evidence quality;
- validation workflows;
- careful integration rather than feature accumulation.

---

## 12. Architectural North Star

MaterialGraph should become better by making research opportunities:

- more useful;
- more scientifically grounded;
- more explainable;
- more verifiable;
- more honest about uncertainty;
- easier for researchers to inspect and validate.

The goal is not to eliminate uncertainty with artificial precision.

The goal is to make the available knowledge, reasoning, trade-offs, gaps,
assumptions, and validation boundaries explicit enough that researchers can make
better-informed decisions.