# MaterialGraph System Architecture

## Overview

MaterialGraph is an explainable materials intelligence platform designed to support battery material candidate screening, material exploration, risk-aware recommendation, and constraint-driven decision support.

The platform does **not** perform autonomous material discovery or computational chemistry simulation.

Instead, MaterialGraph assists researchers and engineers by organizing known material candidates into a graph representation and applying explainable intelligence layers for comparison, recommendation, scenario evaluation, and exploration.

---

# Design Principles

MaterialGraph is designed around several core principles:

* Explainable recommendations
* Graph-based material representation
* Constraint-aware reasoning
* Modular intelligence services
* Production-oriented architecture
* Extensible policy evaluation
* Scientific decision support rather than autonomous discovery

Every recommendation should be explainable through observable relationships and explicit scoring logic.

---

# High-Level Architecture

```text
                     Materials Project
                             │
                             ▼
                   Material Import Pipeline
                             │
                             ▼
                  PostgreSQL Material Storage
                             │
                             ▼
                    Material Graph Layer
                             │
      ─────────────────────────────────────────────

        Criticality Engine

        Similarity Engine

        Recommendation Engine

        Scenario Policy Engine

        Material Exploration Layer

      ─────────────────────────────────────────────

                             │
                             ▼

               Explainable Decision Support API
```

---

# Material Graph Layer

The material graph represents relationships between:

* Materials
* Elements
* Applications
* Risk profiles

Core relationships include:

```text
Material
    │
    ├── contains → Element
    │
    ├── used in → Application
    │
    └── evaluated by → Risk Profile
```

The graph serves as the foundation for all intelligence services.

---

# Material Intelligence Layer

The Material Intelligence Layer consists of independent services that operate on the material graph.

## Criticality Engine

Aggregates element-level risk information into material-level criticality scores.

Current dimensions include:

* Supply risk
* Geopolitical risk
* Toxicity
* Abundance

---

## Similarity Engine

Identifies chemically related candidates using graph relationships and shared composition.

Supports:

* Similarity search
* Neighborhood exploration
* Candidate expansion

---

## Recommendation Engine

Ranks candidate materials using:

* Similarity
* Criticality
* Stability
* Shared relationships

Produces explainable recommendation scores.

---

## Scenario Policy Engine

Evaluates candidate recommendations under configurable policy constraints.

Current policy capabilities:

* Supply-risk multipliers
* Avoid element penalties
* Preferred element bonuses
* Explainable scenario scoring

The policy engine centralizes constraint evaluation and provides a reusable scoring pipeline for future policy extensions.

---

## Material Exploration Layer

Explores chemically related material families.

Current exploration includes:

* Same element families
* Alkali substitution families
* Transition metal families
* Phosphate families
* Oxide families

This layer supports explainable candidate expansion rather than autonomous material discovery.

---

# Data Flow

Typical recommendation workflow:

```text
Material Request
        │
        ▼
Similarity Engine
        │
        ▼
Recommendation Engine
        │
        ▼
Scenario Policy Evaluation
        │
        ▼
Explainable Recommendation
```

Material exploration workflow:

```text
Material Request
        │
        ▼
Material Graph
        │
        ▼
Material Exploration Layer
        │
        ▼
Related Material Families
```

---

# Explainability Philosophy

MaterialGraph does not generate opaque rankings.

Every recommendation should be explainable through:

* Similarity relationships
* Criticality scores
* Policy adjustments
* Material family relationships
* Constraint evaluation

This design enables transparent scientific decision support.

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

Future intelligence modules may include:

* Multi-element policy constraints
* Geopolitical policy evaluation
* Toxicity-aware policies
* Recyclability-aware policies
* Cost-aware candidate ranking
* Carbon footprint reasoning
* Constraint optimization
* Scientific hypothesis exploration
* Graph embeddings
* Explainable candidate expansion

The long-term vision is an explainable materials intelligence platform that assists researchers through graph reasoning and policy-aware decision support rather than autonomous material generation.