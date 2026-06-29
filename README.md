# MaterialGraph

> **Deterministic, Explainable Materials Discovery Knowledge Graph for
> Scientific Exploration**

MaterialGraph is an open-source platform for deterministic, explainable
materials discovery and scientific decision support. It combines
graph-based knowledge representation, explainable scoring, graph
analytics, and research-oriented exploration to help researchers
investigate scientifically plausible material alternatives.

Unlike autonomous AI systems, MaterialGraph does **not** replace
scientific judgment. It computes, ranks, explains, and contextualizes
research opportunities while keeping researchers in control of
scientific decisions.

------------------------------------------------------------------------

# Why MaterialGraph?

Modern materials research requires balancing chemistry, stability,
criticality, supply risk, and scientific plausibility.

MaterialGraph helps researchers:

-   Discover scientifically related materials
-   Explore explainable substitution pathways
-   Analyze graph relationships and communities
-   Evaluate research objectives
-   Understand risks, trade-offs, and assumptions
-   Make informed scientific decisions

------------------------------------------------------------------------

## Documentation

Additional project documentation is available in the `docs/` directory.

| Document                                                            | Description                                                              |
| ------------------------------------------------------------------- | ------------------------------------------------------------------------ |
| [Getting Started](docs/guide/getting_started.md)                    | Local development setup and project bootstrapping                        |
| [System Architecture](docs/architecture/system_architecture.md)     | Current architecture and intelligence layer design                       |
| [Scientific Principles](docs/architecture/scientific_principles.md) | Scientific principles and design rationale                               |
| [Research Architecture](docs/architecture/research_architecture.md) | Research-focused architecture and design decisions                       |
| [Roadmap](docs/architecture/roadmap.md)                             | Future development plans and feature roadmap                             |
| [Known Issues](docs/guide/technical_notes.md)                       | Current limitations and tracked issues                                   |
| [Deployment Guide](docs/development/deployment.md)                  | Production deployment using AWS EC2, Neon PostgreSQL, systemd, and Nginx |


------------------------------------------------------------------------

# Core Principles

-   Deterministic reasoning
-   Explainable intelligence
-   Graph-driven scientific exploration
-   Researcher-in-the-loop decision support
-   Rank, explain, warn, and score
-   No LLM reasoning in scientific computation

------------------------------------------------------------------------

# Current Capabilities (v1.9.1)

## Foundation Intelligence

-   Material Graph Foundation
-   Material Neighborhood Intelligence
-   Material Family Intelligence
-   Similarity Engine
-   Recommendation Engine
-   Criticality Analysis
-   Scenario Policy Engine

## Discovery Intelligence

-   Discovery Candidate Engine
-   Explainable Discovery Scoring
-   Discovery Warnings
-   Substitution Path Engine
-   Multi-Hop Discovery Chains
-   Discovery Path Ranking
-   Research Objective Exploration

## Knowledge Graph Intelligence

-   Graph Builder
-   Graph Traversal
-   BFS / DFS / Dijkstra / K-shortest Paths
-   Community Detection
-   Community Intelligence
-   Ranked Subgraph Exploration
-   Graph Analytics
-   Material Quality
-   Node & Edge Intelligence

------------------------------------------------------------------------

# Architecture

``` text
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
Scientific Knowledge Layer (Future)
```

------------------------------------------------------------------------

# Technology Stack

## Backend

-   Python
-   FastAPI
-   SQLAlchemy
-   PostgreSQL
-   Alembic
-   NetworkX
-   Pydantic v2

## Infrastructure

-   AWS EC2
-   Nginx
-   systemd
-   Docker

## Testing

-   pytest

------------------------------------------------------------------------

# Quick Start

``` bash
git clone https://github.com/<username>/materialgraph.git
cd materialgraph

python -m venv .venv
pip install -r requirements.txt

alembic upgrade head
python scripts/import_materials_project.py

uvicorn app.main:app --reload
```

------------------------------------------------------------------------

# Documentation

See the `docs/` directory for:

-   System Architecture
-   Scientific Principles
-   Getting Started
-   Deployment Guide
-   Technical Notes
-   Roadmap

------------------------------------------------------------------------

# Roadmap

## Phase 2.5 -- Decision Intelligence

-   Multi-element constraints
-   Application-aware exploration
-   USGS criticality enrichment
-   Geopolitical, toxicity, and recyclability policies

## Phase 3 -- Knowledge Graph Intelligence

Completed:

-   Community Detection
-   Community Intelligence
-   Ranked Subgraph Exploration
-   Research Objective Exploration

Current Focus:

-   Scientific Pathway Analysis
-   Research Opportunity Analysis

Future:

-   Research Gap Analysis
-   Hypothesis Exploration
-   Multi-objective Optimization

## Phase 4

-   PostgreSQL graph jobs
-   Go GraphCompute Worker
-   Background analytics

## Phase 5

-   Rust graph engine
-   Large-scale traversal
-   High-performance scientific path search

------------------------------------------------------------------------

# Project Scope

MaterialGraph assists scientific exploration. It does **not**:

-   Replace DFT calculations
-   Guarantee synthesis feasibility
-   Replace laboratory validation
-   Replace scientific judgment

Researchers remain responsible for evaluating, selecting, and validating
research opportunities.

------------------------------------------------------------------------

# License

MIT License
