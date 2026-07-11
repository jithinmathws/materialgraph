# What MaterialGraph Should Be

> **Project direction, scientific boundaries, and development
> principles**
>
> Initial version derived from architecture and code review through
> **v1.9.6 --- Endpoint-Sensitive Research Ranking**.

## 1. Purpose of This Document

This document defines what MaterialGraph should become and what it
should avoid becoming.

It is intentionally different from a feature list, roadmap, or
architecture inventory. It records project-level principles discovered
by reviewing the actual implementation and real API behavior.

This document should be updated only when code review, researcher
feedback, real-response verification, or external validation reveals
something important about:

-   researcher usefulness;
-   scientific meaning;
-   verifiability;
-   system boundaries;
-   architecture integration;
-   misleading terminology;
-   missing capabilities;
-   duplicated intelligence;
-   uncertainty;
-   validation needs.

MaterialGraph should not grow by accumulating impressive-sounding
features. It should grow by improving the quality, usefulness,
traceability, and scientific honesty of research decision support.

------------------------------------------------------------------------

## 2. Core Identity

MaterialGraph should be:

> **A deterministic, explainable, graph-driven materials research
> intelligence system that helps researchers explore, compare, inspect,
> and validate material opportunities while keeping scientific judgement
> with the researcher.**

MaterialGraph may:

-   organize materials and relationships;
-   generate constrained discovery opportunities;
-   explore multi-hop pathways;
-   rank using explicit deterministic dimensions;
-   expose score breakdowns;
-   compare alternatives;
-   identify evidence gaps;
-   expose assumptions;
-   preserve unresolved ties;
-   prioritize validation needs;
-   show why an opportunity was generated;
-   help researchers decide what to inspect next.

MaterialGraph must not claim to replace:

-   domain expertise;
-   literature review;
-   crystallographic analysis;
-   DFT or other computational validation;
-   synthesis planning by experts;
-   laboratory experiments;
-   peer review;
-   scientific judgement.

------------------------------------------------------------------------

## 3. The System Should Work as One Intelligence Pipeline

The reviewed implementation shows a meaningful layered flow:

``` text
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

New capabilities should normally improve or enrich this flow rather than
create parallel, disconnected intelligence systems.

A new service should answer:

1.  What upstream output does it consume?
2.  What genuinely new information does it add?
3.  Which downstream capability uses that information?
4.  Why does this logic belong here rather than in an existing service?
5.  Can the researcher inspect the result?

If these questions are unclear, implementation should not begin.

------------------------------------------------------------------------

## 4. MaterialGraph Should Prefer Honest Uncertainty Over Artificial Precision

The verified LiFePO4 → Na/phosphate case is an important project
principle.

For the objective:

-   avoid `Li`;
-   prefer `Na`;
-   preserve `Fe`, `P`, `O`;
-   target `phosphate`;
-   `max_hops = 2`;
-   `limit = 5`;

MaterialGraph returned five scientifically distinct endpoint
opportunities:

-   Na3Fe3(PO4)4
-   Na9Fe3P8O29
-   NaFeP2O7
-   NaFePO4
-   Na3Fe(PO4)2

All five received the same scientific usefulness score of `94.95`.

The correct response was not to invent a tie-breaker.

The v1.9.5 comparative layer exposed meaningful differences while
preserving the tie. The v1.9.6 endpoint-sensitive layer examined
available endpoint evidence and still preserved the tie because current
evidence did not justify deterministic differentiation.

This behavior should remain a core principle:

> **If available evidence cannot justify differentiation, MaterialGraph
> should say so explicitly.**

A genuine tie is a valid scientific decision-support output.

Tie preservation must apply not only to numeric scores but also to
summaries, labels, selected representatives, and downstream comparisons.

> **If several pathways share the highest supported score or evidence
> state, MaterialGraph must not imply a unique winner merely because
> list order, stable sorting, or a selection function returns one
> item.**

A tied top group should remain a tied top group unless additional
evidence justifies differentiation.

------------------------------------------------------------------------

## 5. MaterialGraph Should Distinguish Signal From Proof

A major finding from code review is that some current scientific
language can be stronger than the underlying computation.

For example, current transition logic derives `preserved_framework` from
the intersection of element symbols present in the source and target
materials.

That is useful as a deterministic compositional signal.

However:

> **Shared elements are not proof of preserved crystal structure,
> bonding topology, phase behavior, coordination environment, or
> functional framework.**

Therefore MaterialGraph should distinguish among concepts such as:

-   shared elemental composition;
-   preserved chemistry overlap;
-   inferred family continuity;
-   encoded relationship continuity;
-   structural framework preservation;
-   experimentally validated preservation.

These concepts must not be treated as interchangeable.

### Directional rule

Until stronger structural evidence exists, outputs derived from element
intersection should use terminology that reflects what is actually
known.

Prefer language such as:

-   `shared_compositional_framework`
-   `shared_chemistry_elements`
-   `composition_overlap`
-   `preserved_element_set`

Avoid implying verified structural preservation unless supported by
appropriate structural evidence.

This is not merely a naming issue. Terminology affects researcher trust
and the scientific interpretation of downstream ranking, confidence,
comparison, and evidence outputs.

The same inferred signal may propagate through multiple layers:

``` text
element-set overlap
        │
        ▼
preserved_framework
        │
        ▼
framework-preservation score
        │
        ▼
supporting signal
        │
        ▼
confidence / readiness interpretation
        │
        ▼
comparative research output
```

This creates an important rule:

> **An inferred signal must not become stronger merely because multiple
> downstream services reuse it. Repetition across ranking, evidence, and
> comparison layers does not create independent evidence.**

MaterialGraph should preserve provenance through the full pipeline so a
researcher can distinguish several independent supporting facts from
several downstream interpretations of the same upstream fact.

------------------------------------------------------------------------

## 6. MaterialGraph Should Make Objective Semantics Match Actual Execution

Current objective handling exposes list-shaped concepts such as:

-   `avoid_elements`
-   `prefer_elements`
-   `preserve_elements`

However, reviewed objective-chain execution currently forwards only the
first avoid element and first prefer element into chain generation and
path ranking.

This creates an important principle:

> **The apparent expressiveness of a research objective must match the
> actual semantics executed by the system.**

MaterialGraph should not accept a richer objective shape while silently
executing only a subset unless that limitation is explicit.

Future work should determine whether to:

-   support all avoid/prefer elements end to end;
-   constrain the schema to actual supported semantics; or
-   expose explicit warnings when only part of an objective is applied.

The correct choice should be made after tracing all dependent services.
It should not be patched locally without understanding candidate
generation, transition validation, ranking, comparison, and backward
compatibility.

------------------------------------------------------------------------

## 7. Search-Space Construction Is Part of Scientific Meaning

The reviewed chain service is production-aware:

-   bounded hop depth;
-   bounded expansion;
-   cycle prevention;
-   candidate caching;
-   relationship caching;
-   family-result caching;
-   delegated transition validation.

These are valuable engineering properties.

However, the chain-generation process also determines which
opportunities can ever reach downstream intelligence.

Therefore:

> **Search-space construction is not only a performance concern. It is
> part of the scientific behavior of MaterialGraph.**

Limits such as:

-   maximum hops;
-   expansion limits;
-   candidate ordering;
-   family-neighborhood selection;
-   preferred-element filtering;
-   chain completion rules;

can influence which research opportunities are visible and which remain
unseen.

MaterialGraph should make these constraints inspectable and should avoid
presenting a bounded search result as exhaustive discovery.

Production safety and scientific completeness are different concerns.
The system should represent that distinction clearly.

------------------------------------------------------------------------

## 8. Transition Validation Should Be Conservative and Explainable

Current transition validation requires recognized relationships and at
least one strong relationship before accepting a transition.

This conservative direction should be preserved.

MaterialGraph should prefer:

-   explicit accepted relationship classes;
-   deterministic validation rules;
-   inspectable rejection reasons;
-   explicit removed elements;
-   explicit introduced elements;
-   explicit shared elements;
-   traceable transition types.

It should avoid:

-   accepting graph adjacency as sufficient scientific plausibility;
-   inferring strong chemistry from weak similarity alone;
-   hiding why a transition was accepted;
-   silently upgrading an inferred relationship into verified evidence.

A transition should be understood as:

> **an explainable research hypothesis or exploration step supported by
> encoded relationships and available evidence**

---not as proof that the physical transformation is experimentally
feasible.

------------------------------------------------------------------------

## 9. MaterialGraph Should Preserve Layer Ownership

The reviewed architecture currently has a useful separation of concerns:

-   objective service orchestrates objective-constrained chain
    selection;
-   chain service constructs bounded multi-hop opportunities;
-   transition validator owns transition acceptance;
-   path ranking owns scientific usefulness scoring;
-   scientific pathway analysis constructs researcher-facing
    opportunities;
-   evidence intelligence owns evidence summaries and gaps;
-   comparative intelligence owns comparison;
-   endpoint-sensitive ranking examines tied endpoints without replacing
    the original score.

This separation should be protected.

### Ownership rule

New capabilities should reuse existing outputs rather than recreate
them.

Examples:

-   comparison should not become a second ranking engine;
-   endpoint-sensitive analysis should not recreate material quality;
-   evidence intelligence should not invent transition plausibility;
-   graph centrality should not silently become scientific usefulness;
-   confidence should not duplicate the total score under a different
    name;
-   validation planning should not fabricate missing evidence.

------------------------------------------------------------------------

## 10. MaterialGraph Should Treat Researcher-Facing Language as Part of the Model

Explanations are not cosmetic.

Terms such as:

-   `preserved_framework`;
-   `scientific_plausibility`;
-   `confidence`;
-   `evidence_readiness`;
-   `stable`;
-   `strong`;
-   `validated`;

carry scientific meaning.

MaterialGraph should ensure that the strength of its language does not
exceed the strength of the underlying evidence.

Every researcher-facing term should be traceable to:

-   a stored property;
-   a deterministic rule;
-   a graph fact;
-   an attributed external source;
-   or an explicitly labeled inference.

If a term is inferential, the output should make that visible.

------------------------------------------------------------------------

## 11. MaterialGraph Should Separate Internal Support From External Scientific Evidence

MaterialGraph currently derives useful support from its own
deterministic intelligence layers. Examples include:

-   graph relationships;
-   objective alignment;
-   ranking dimensions;
-   material-property heuristics;
-   transition-type rules;
-   graph-derived pathway facts;
-   deterministic comparisons.

These are valuable forms of **internal deterministic support**.

They are not automatically equivalent to **external scientific
evidence**, such as:

-   attributed scientific literature;
-   experimental synthesis reports;
-   independently validated computational results;
-   measured electrochemical data;
-   crystallographic or structural evidence;
-   independently sourced property measurements.

MaterialGraph should keep these categories explicit.

> **A pathway should not receive a researcher-facing interpretation of
> strong scientific evidence solely because several internally derived
> signals agree when literature, experimental, structural, or
> computational validation is absent.**

Evidence readiness should therefore communicate what kind of evidence is
ready, not merely how many internal signals are present.

Where useful, MaterialGraph should distinguish concepts such as:

-   `internal_support_strength`;
-   `external_evidence_readiness`;
-   `evidence_coverage`;
-   `validation_readiness`.

The exact schema should be decided only after reviewing current
consumers and avoiding duplicate concepts. The principle is more
important than any specific field name.

------------------------------------------------------------------------

## 12. Missing Evidence Must Remain Missing

Absence of evidence must not silently become favorable evidence.

> **Unknown risk is not low risk. Partial evidence coverage is not
> equivalent to complete evidence. Missing evidence must never receive a
> favorable score merely because a numeric fallback resembles a
> desirable value.**

This principle applies beyond risk intelligence. It should govern:

-   missing material properties;
-   missing risk profiles;
-   incomplete element coverage;
-   absent literature evidence;
-   unavailable structural evidence;
-   unavailable experimental validation;
-   unavailable computational validation.

Whenever incomplete coverage can materially affect ranking, confidence,
or comparison, MaterialGraph should expose coverage alongside the value.

Useful coverage concepts may include:

-   whether the value is known;
-   fraction of relevant entities covered;
-   known and unknown contributors;
-   whether evidence is complete;
-   provenance of available values.

The risk-intelligence correction made during the v1.9.6 architecture
audit is an example of this principle: unknown risk must remain
distinguishable from known low risk, and downstream quality scoring must
not reward missing risk evidence.

------------------------------------------------------------------------

## 13. MaterialGraph Should Separate Internal Consistency From External Validity

Passing tests proves important things:

-   code behavior is stable;
-   contracts are preserved;
-   deterministic rules execute as expected;
-   regressions can be detected.

But passing tests does not prove:

-   scientific correctness;
-   synthesis feasibility;
-   structural preservation;
-   experimental performance;
-   usefulness to researchers.

MaterialGraph should maintain two distinct validation tracks.

### Engineering validation

-   unit tests;
-   integration tests;
-   API contract tests;
-   performance tests;
-   regression tests;
-   production monitoring.

### Scientific and researcher validation

-   representative case studies;
-   literature cross-checking;
-   domain-expert review;
-   comparison with known materials behavior;
-   DFT or domain-specific computational checks where appropriate;
-   researcher workflow feedback;
-   experimental validation where possible.

Both tracks are necessary.

------------------------------------------------------------------------

## 14. MaterialGraph Should Become Verifiable, Not Merely Explainable

Explainability answers:

> Why did the system produce this result?

Verifiability should also answer:

> What facts support it, where did those facts come from, what is
> inferred, what is missing, and how could a researcher check it?

MaterialGraph should increasingly make visible:

-   source provenance;
-   property provenance;
-   rule provenance;
-   relationship provenance;
-   evidence attribution;
-   missing evidence;
-   assumptions;
-   validation priorities;
-   uncertainty boundaries.

A polished explanation without inspectable support is not enough for a
research system.

------------------------------------------------------------------------

## 15. MaterialGraph Should Be Useful to More Than One Research Persona Without Becoming Vague

Potential users may include:

-   materials researchers;
-   computational materials scientists;
-   battery researchers;
-   R&D teams;
-   critical-material analysts;
-   supply-risk researchers;
-   research program decision-makers.

MaterialGraph should not claim equal readiness for all of these users.

Each use case should be earned through:

-   appropriate data;
-   appropriate objectives;
-   appropriate evidence;
-   representative case studies;
-   user feedback.

The shared platform can remain broad, while validated workflows should
be specific.

------------------------------------------------------------------------

## 16. New Capabilities Should Be Evidence-Driven

Before naming or implementing the next milestone, inspect:

1.  current code;
2.  current service ownership;
3.  a real API response;
4.  the exact limitation;
5.  what evidence is missing;
6.  what a researcher would need next.

Then choose the smallest capability that improves the system.

Potential future directions may include:

-   stronger evidence provenance;
-   validation planning;
-   multi-element objective semantics;
-   structural evidence integration;
-   property-specific endpoint analysis;
-   literature-linked evidence;
-   researcher-facing case-study workflows.

These are possibilities, not automatic roadmap commitments.

The next capability should be selected because the current system
demonstrates a need for it.

------------------------------------------------------------------------

## 17. A Practical Gate for Every Future Feature

Before implementation, answer:

1.  What researcher question does this capability answer?
2.  What current limitation demonstrates the need?
3.  Which layer owns the logic?
4.  What existing services does it reuse?
5.  What new information does it add?
6.  What is the scientific basis?
7.  Can the researcher inspect the basis?
8.  Does it duplicate an existing score or signal?
9.  What happens when data is missing?
10. Can uncertainty remain unresolved?
11. Can a genuine tie remain a tie?
12. What terminology could overstate the evidence?
13. What requires external validation?
14. What real case study will verify usefulness?
15. What production cost or search bias could it introduce?

If these questions cannot be answered clearly, the feature should not be
added yet.

------------------------------------------------------------------------

## 18. MaterialGraph Should Support Open-Ended Material and Element Exploration

The long-term research goal should not be limited to a fixed seed
dataset or a small set of preselected materials.

> **A researcher should eventually be able to begin from any material,
> element, material family, property target, or constrained research
> objective that the system can identify and support with traceable
> data.**

Valid research entry points may include:

-   an element such as `Li`, `Na`, `Fe`, or `Mg`;
-   a known material formula;
-   a material family;
-   a property target;
-   an application context;
-   an avoidance constraint;
-   a preservation constraint;
-   a substitution question;
-   a multi-objective research problem.

The intended direction is:

``` text
Research Question
        │
        ▼
Query / Identity Resolution
        │
        ▼
Known Data and Coverage Check
        │
        ├── sufficient ──► research intelligence pipeline
        │
        └── insufficient
                 │
                 ▼
       controlled data acquisition
                 │
                 ▼
       normalization + provenance
                 │
                 ▼
       graph integration / temporary research context
                 │
                 ▼
       research intelligence pipeline
```

This does not mean MaterialGraph should pretend to know every material.

When a requested material or element is outside current coverage, the
system should explicitly distinguish:

-   known and locally available;
-   externally resolvable;
-   partially characterized;
-   identity-ambiguous;
-   unsupported by current data;
-   unavailable for a requested analysis.

### Universal exploration requires identity discipline

Scaling beyond a curated dataset requires a stronger identity model.

MaterialGraph should distinguish where scientifically necessary among:

-   canonical material identity;
-   composition identity;
-   phase identity;
-   structure identity;
-   polymorph identity;
-   source-specific identity;
-   aliases and naming variants.

A shared formula must not automatically imply identical phase,
structure, properties, or physical behavior.

### Dynamic ingestion must be controlled

Future external data acquisition should preserve:

-   source attribution;
-   source licensing constraints;
-   retrieval time;
-   dataset version;
-   normalization decisions;
-   conflicting values;
-   missing values;
-   uncertainty;
-   whether data is stored, cached, or temporary.

> **Universal exploration should expand the research space without
> weakening provenance, identity precision, or scientific honesty.**

------------------------------------------------------------------------

## 19. MaterialGraph Should Include Physical Modeling Readiness as a First-Class Intelligence Layer

MaterialGraph should eventually help a researcher determine not only
what may be worth investigating, but whether a candidate or research
hypothesis is sufficiently specified to proceed into a particular
physical modeling workflow.

> **Physical Modeling Readiness should assess readiness for modeling. It
> should not claim that a model has been executed, validated, or shown
> to represent reality merely because required inputs appear
> available.**

The intended pipeline is:

``` text
Research Opportunity
        │
        ▼
Evidence and Property Context
        │
        ▼
Physical Modeling Readiness
        │
        ▼
Model-Specific Readiness Profile
        │
        ├── ready
        ├── partially ready
        ├── blocked by missing inputs
        ├── applicability uncertain
        └── unsupported
        │
        ▼
Future Model Routing / External Compute
        │
        ▼
Attributed Simulation Result
        │
        ▼
Evidence and Validation Loop
```

### Readiness must be model-specific

MaterialGraph should avoid a single universal
`physical_modeling_readiness_score` that collapses fundamentally
different requirements.

Potential readiness profiles may include:

-   DFT readiness;
-   molecular dynamics readiness;
-   thermodynamic modeling readiness;
-   phase-field readiness;
-   finite-element readiness;
-   electrochemical modeling readiness;
-   quantum-model readiness.

Each profile should define its own:

-   required inputs;
-   optional inputs;
-   blocking gaps;
-   applicability conditions;
-   assumptions;
-   evidence requirements;
-   uncertainty handling;
-   validation expectations.

For example, DFT readiness may depend on structural and calculation
context, while molecular dynamics readiness may depend on an appropriate
potential or force field, topology, thermodynamic conditions, and
simulation configuration.

### Readiness should expose missing prerequisites

A researcher-facing result should be able to communicate:

``` text
Model route: DFT

Available:
- composition
- atomic species
- crystal structure
- lattice parameters

Unresolved:
- partial occupancy
- magnetic initialization

Missing:
- explicit calculation assumptions

Readiness:
PARTIAL

Blocking gaps:
- unresolved occupancy

Recommended next action:
- resolve structure representation before model execution
```

The exact schema should be implemented only after reviewing actual
modeling workflows and domain requirements.

### Hamiltonian and model-family reasoning must remain conservative

For future quantum or statistical physical modeling, MaterialGraph may
help represent relationships such as:

``` text
Research Target
      │
      ▼
Degrees of Freedom
      │
      ▼
Relevant Interactions
      │
      ▼
Candidate Model Family
      │
      ▼
Required Parameters
      │
      ├── available
      ├── uncertain
      └── missing
```

For example, the system may identify that a magnetic research context
appears compatible with investigation through a Heisenberg-type model
while still reporting missing exchange parameters.

It must not infer:

-   that the selected Hamiltonian is uniquely correct;
-   that parameters are known when they are not;
-   that solving a mathematical model validates the physical system;
-   that model applicability is established without evidence.

### Physical Modeling Readiness should reuse existing intelligence

It should consume, where appropriate:

-   material identity;
-   property observations;
-   structural evidence;
-   evidence attribution;
-   uncertainty;
-   contradiction intelligence;
-   research objectives;
-   validation priorities.

It should not create a parallel evidence system or silently reinterpret
missing data as readiness.

------------------------------------------------------------------------

## 20. MaterialGraph Should Treat Physical Compute as a Future Integration Boundary

MaterialGraph should not attempt to become every scientific simulator.

Its stronger long-term role is to connect research intelligence with
appropriate modeling workflows while preserving clear boundaries.

``` text
MaterialGraph Research Intelligence
        │
        ▼
Physical Modeling Readiness
        │
        ▼
Model / Workflow Selection
        │
        ▼
External or Dedicated Compute
        │
        ├── electronic-structure workflow
        ├── molecular simulation workflow
        ├── thermodynamic workflow
        ├── continuum workflow
        └── other validated domain workflow
        │
        ▼
Versioned Result + Provenance
        │
        ▼
MaterialGraph Evidence Context
```

Every imported simulation result should preserve, where available:

-   engine and version;
-   input configuration;
-   material identity;
-   structure version;
-   parameter set;
-   assumptions;
-   convergence state;
-   execution time;
-   output artifact references;
-   validation status.

> **A computed result should become attributed evidence context, not
> automatic scientific truth.**

MaterialGraph should also distinguish:

-   readiness to run;
-   successful execution;
-   numerical convergence;
-   model validity;
-   agreement with experiment.

These are separate states.

------------------------------------------------------------------------

## 21. MaterialGraph Should Be Architected for Polyglot Compute Without Premature Distribution

The current Python, FastAPI, and PostgreSQL foundation should remain the
primary development environment while scientific semantics and
researcher workflows are still evolving.

However, the architecture should prepare for future compute
specialization.

A possible long-term ownership model is:

``` text
FastAPI / Python
├── API contracts
├── research orchestration
├── objective handling
├── evidence and provenance
├── explanation assembly
├── experiment management
└── rapidly evolving scientific intelligence

Future Go Compute Services
├── concurrent graph exploration
├── high-throughput background jobs
├── large traversal workloads
├── batch path computation
└── worker coordination where justified

Future Rust Compute Core
├── performance-critical kernels
├── memory-sensitive graph operations
├── numerical routines
├── compact scientific computation
└── validated reusable compute modules
```

This is a direction, not a commitment to immediate decomposition.

### Introduce another runtime only when there is evidence

A Go service should be considered when measurements show needs such as:

-   sustained concurrent experiment workloads;
-   graph traversal dominating request or worker time;
-   large batch exploration;
-   Python worker throughput becoming a demonstrated constraint.

A Rust component should be considered when measurements show needs such
as:

-   performance-critical numerical kernels;
-   memory-sensitive graph operations;
-   repeated hot loops that remain bottlenecks after algorithmic
    optimization;
-   a stable compute contract suitable for a lower-level implementation.

Other technologies should be evaluated by the same rule.

> **MaterialGraph should adopt a technology because a measured workload
> and stable ownership boundary justify it, not because the technology
> appears impressive.**

### Prepare boundaries early

Even before introducing Go, Rust, or another runtime, MaterialGraph
should strengthen:

-   typed request and result schemas;
-   explicit service ownership;
-   experiment identifiers;
-   versioned compute contracts;
-   deterministic test fixtures;
-   benchmark cases;
-   timing instrumentation;
-   job-state semantics;
-   reproducibility metadata.

This allows later extraction without forcing premature microservices.

------------------------------------------------------------------------

## 22. MaterialGraph Should Be Deployed and Validated in Controlled Stages

Professional deployment should be treated as part of research
validation, not merely infrastructure hosting.

The project should avoid two extremes:

-   remaining indefinitely private while claiming researcher usefulness;
-   opening unrestricted expensive research computation before
    scientific and operational boundaries are understood.

A staged direction is preferable.

### Stage 1 --- Controlled Research Preview

Purpose:

-   verify deployment behavior;
-   expose bounded workflows;
-   collect early scientific criticism;
-   measure real endpoint cost;
-   validate reproducibility and provenance.

Characteristics may include:

-   static React research interface;
-   FastAPI API;
-   PostgreSQL;
-   bounded synchronous computation;
-   strict graph-depth and result limits;
-   local or simple background jobs;
-   experiment identifiers;
-   timing and error observability;
-   invited users.

The goal is not scale.

> **The goal is to discover where MaterialGraph is scientifically
> misleading, operationally fragile, or genuinely useful.**

### Stage 2 --- Research Validation Beta

Introduce only when repeated external use demonstrates the need.

Possible additions:

-   persistent research accounts;
-   private experiments;
-   background job queue;
-   shared cache;
-   API keys;
-   quotas;
-   rate limiting;
-   saved workspaces;
-   researcher feedback;
-   result versioning;
-   stronger monitoring and backups.

### Stage 3 --- Professional Research Platform

Introduce when usage proves a need for compute separation, stronger
service levels, institutional workflows, or private data.

Possible additions:

-   separate API and compute workers;
-   managed cache;
-   stronger database operations;
-   dedicated graph compute;
-   specialized Go or Rust components where profiling justifies them;
-   institutional access controls;
-   private deployments;
-   auditable integrations.

### Endpoint cost should influence execution mode

A useful classification is:

``` text
Class A — cheap
lookup, metadata, saved result retrieval

Class B — moderate
bounded candidate generation, small path search, cached comparison

Class C — expensive
community detection, large graph expansion, k-best path exploration,
comparative research workloads

Class D — research compute
large objective exploration, batch studies, future modeling or ML workloads
```

A likely execution direction is:

``` text
A → synchronous

B → synchronous when bounded, otherwise cached or queued

C → asynchronous background jobs

D → dedicated compute infrastructure
```

The classification should be based on measurement, not labels alone.

### External validation should be systematic

Researcher feedback should be structured into failure and usefulness
categories such as:

-   incorrect identity;
-   invalid edge;
-   weak substitution;
-   missing property;
-   misleading terminology;
-   poor ranking;
-   insufficient evidence;
-   misleading confidence;
-   invalid pathway;
-   search-space omission;
-   useful opportunity;
-   known result rediscovered;
-   novel result worth investigation.

Feedback must not automatically become truth. It should remain
attributed, reviewable input.

### Commercialization should follow demonstrated value

Researcher use does not automatically imply payment.

MaterialGraph should first learn:

-   which workflows researchers repeat;
-   which capabilities save meaningful time;
-   which outputs influence decisions;
-   whether labs need collaboration;
-   whether institutions need private workspaces;
-   whether industrial teams need proprietary data integration;
-   whether users need API access or private deployment.

Potential future paid capabilities may include:

-   private research workspaces;
-   larger compute quotas;
-   institutional collaboration;
-   proprietary dataset integration;
-   API access;
-   private deployment;
-   industrial pilots;
-   support and audit requirements.

> **The business model should emerge from validated research value
> rather than forcing early payment around an unvalidated system.**

------------------------------------------------------------------------

## 23. Current Direction After v1.9.6

The immediate priority should not be feature accumulation.

The priority should be:

1.  understand the current code path end to end;
2.  trace one representative real response through the full intelligence
    stack;
3.  document strategically important findings before remediation changes
    the observed baseline;
4.  identify semantic mismatches;
5.  identify where terminology overstates evidence;
6.  identify where one upstream inference propagates through multiple
    downstream layers;
7.  identify where search constraints shape scientific outputs;
8.  fix critical correctness issues discovered during inspection;
9.  verify fixes with focused tests, the full suite, and representative
    real responses where possible;
10. build reference case studies;
11. seek researcher feedback;
12. add capabilities only where demonstrated gaps exist.

The current LiFePO4 → Na/phosphate objective should continue to serve as
a reference trace while the architecture audit proceeds. Its five-way
`94.95` tie is especially useful for checking whether downstream
services preserve uncertainty rather than manufacturing differentiation.

The project is now mature enough that restraint, auditability, and
remediation are part of good engineering.

------------------------------------------------------------------------

## 24. North Star

MaterialGraph should help researchers answer:

-   What opportunities exist?
-   Why were they generated?
-   What relationships support them?
-   What trade-offs distinguish them?
-   What evidence is available?
-   What evidence is missing?
-   Which assumptions are weak?
-   What cannot currently be differentiated?
-   What should be validated next?
-   Is this opportunity ready for a specific physical modeling workflow?
-   Which modeling prerequisites are missing or uncertain?
-   What is known locally, what requires external resolution, and what
    is outside current coverage?
-   How can the reasoning be independently checked?

MaterialGraph should not hide uncertainty behind ranking precision.

It should make the boundary between:

-   known;
-   derived;
-   inferred;
-   missing;
-   uncertain;
-   and experimentally unvalidated

as clear as possible.

> **The goal is not to make MaterialGraph appear certain. The goal is to
> make materials research exploration more structured, inspectable,
> verifiable, and useful while preserving scientific judgement with the
> researcher.**
>
> **Long term, MaterialGraph should help researchers move coherently
> from open-ended material or element exploration, through explainable
> opportunity and evidence analysis, toward model-specific physical
> readiness and externally validated computation---without confusing
> inference, readiness, simulation, or validation with scientific
> proof.**