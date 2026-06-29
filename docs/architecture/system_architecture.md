# MaterialGraph System Architecture

## Overview

MaterialGraph is a deterministic, explainable Materials Discovery Knowledge Graph
designed to support scientific exploration and research decision support.

The platform combines graph intelligence, explainable reasoning,
graph analytics, and research-oriented exploration while preserving
researcher autonomy.

---

## Architectural Vision

MaterialGraph is built as a layered intelligence platform.

Each layer answers increasingly complex scientific questions.

The platform progresses from material representation
to scientific exploration without replacing scientific judgement.

---

## Intelligence Layers

```text
Materials Project
        │
        ▼
Material Graph Foundation
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
        ▼
Research Intelligence
        │
        ▼
Scientific Knowledge Layer
        (Future)
```


### Foundation Intelligence

#### Purpose

- Represent materials.
- Represent relationships.
- Build graph.

#### Services

- Material Graph Service
- Neighborhood Service
- Families Service
- Similarity Service
- Recommendation Service
- Criticality Service
- Scenario Policies Service

### Discovery Intelligence

#### Question answered:

- What materials should I investigate?

#### Services:

- Discovery Candidates
- Scoring
- Warnings
- Substitution Paths
- Discovery Chains
- Path Ranking

### Knowledge Graph Intelligence

#### Question answered:

- How are these materials connected?

#### Services:

- Graph Builder
- Traversal
- Graph Algorithms
- Community Detection
- Community Intelligence
- Subgraph Exploration
- Material Quality
- Node Intelligence
- Edge Intelligence

### Research Intelligence

#### Question answered:

- How should I explore this scientific objective?

#### Services:

- Research Objective Exploration

(Current)

- Scientific Pathway Analysis
- Research Opportunity Analysis
- Research Gap Analysis
- Hypothesis Exploration

### Scientific Knowledge Layer

Future layer for advanced scientific reasoning and knowledge synthesis.

#### Purpose

- Store Human Knowledge
- Research sessions
- Observations
- Evidence
- Experimental Outcomes
- Literature
- Community insights

This layer records evidence.

It does not replace deterministic graph intelligence.

---

# Research Workflow

```
Research Objective
        │
        ▼
Research Objective Exploration
        │
        ▼
Research Opportunities
        │
        ▼
Researcher Selection
        │
        ▼
Scientific Pathway Analysis
        │
        ▼
Experimental Validation
        │
        ▼
Scientific Evidence
```

---

# Design Principles

* Deterministic reasoning
* Explainability
* Researcher-in-the-loop
* Rank 
* Explain
* Warn
* Score
* No autonomous scientific decisions

---

# Current Technology Stack

Backend:

* Python
* FastAPI
* SQLAlchemy
* PostgreSQL
* Alembic
* NetworkX

Infrastructure:

* AWS EC2
* Neon PostgreSQL
* systemd
* Nginx

Testing:

* pytest

---

# Future Architecture

* Go GraphCompute Worker
* Rust Graph Engine
* Distributed Graph Jobs
* Scientific Knowledge Layer
* Graph Embeddings
* ML Integration