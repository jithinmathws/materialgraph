# MaterialGraph

**Graph-Based Material Intelligence Platform for Battery Material Candidate Screening, Risk Analysis, and Decision Support**

## Overview

MaterialGraph is a graph-based material intelligence platform designed to support candidate screening, risk-aware ranking, substitution analysis, and scenario-driven decision support for battery materials.

The platform integrates scientific material datasets with supply-risk intelligence to help answer questions such as:

> Given lithium or cobalt scarcity, which alternative battery material candidates remain attractive under defined constraints?

MaterialGraph is intentionally designed as a **decision-support platform**, not a material discovery system.

The platform evaluates and compares known material candidates using explainable scoring, risk models, graph relationships, and scenario analysis.

---

## Documentation

Additional project documentation is available in the `docs/` directory.

| Document                                             | Description                                                              |
| ---------------------------------------------------- | ------------------------------------------------------------------------ |
| [Getting Started](docs/getting_started.md)           | Local development setup and project bootstrapping                        |
| [Phase 1 Scope](docs/phase_1_scope.md)               | Phase 1 objectives, constraints, and mission                             |
| [Phase 1 Architecture](docs/phase_1_architecture.md) | System architecture and design decisions                                 |
| [Phase 1 Review](docs/phase_1_review.md)             | Feature completion review and implementation summary                     |
| [Known Issues](docs/known_issues.md)                 | Current limitations and tracked issues                                   |
| [Deployment Guide](docs/DEPLOYMENT.md)               | Production deployment using AWS EC2, Neon PostgreSQL, systemd, and Nginx |


## Quick Start

```bash
git clone https://github.com/<username>/materialgraph.git
cd materialgraph

python -m venv .venv
pip install -r requirements.txt

alembic upgrade head

python scripts/import_materials_project.py

uvicorn app.main:app --reload
```

## Key Features

### Materials Project Integration

* Import real battery material candidates from Materials Project
* Store computed material properties
* Preserve raw source metadata
* Upsert materials and element relationships

### Material-Element Graph

Model relationships between:

* Materials
* Elements
* Applications
* Risk Profiles

Graph relationships include:

* Material → Element
* Material → Application
* Element → Risk Profile

### Risk Intelligence

Aggregate element-level risk information into material-level risk scores.

Current risk dimensions:

* Supply Risk
* Geopolitical Risk
* Toxicity
* Abundance

### Candidate Screening

Evaluate materials under configurable constraints:

* Scarce elements
* Avoided elements
* Stability requirements
* Energy-above-hull limits

Example:

```text
Lithium Scarcity
Avoid Cobalt
Require Stable Candidates
```

### Candidate Comparison

Directly compare two materials.

Example:

```text
Na3Fe(PO4)2
vs
Na2Mn2O3
```

Outputs:

* Screening scores
* Risk scores
* Winner selection
* Explainable reasoning

### Scenario Ranking

Evaluate candidate rankings under strategic scenarios.

Examples:

* Lithium Supply Shock
* Cobalt Restriction
* Critical Material Constraints

### Sensitivity Analysis

Analyze ranking sensitivity under changing risk conditions.

Examples:

* +25% supply risk
* +50% supply risk
* +25% geopolitical risk
* +50% geopolitical risk

### Substitution Analysis

Identify potential substitutes for a material candidate.

Example:

```text
LiFePO4
→ NaFePO4
→ Na3Fe(PO4)2
```

Using:

* Composition similarity
* Material risk
* Shared chemistry
* Explainable substitution reasoning

---

## Technology Stack

### Backend

* Python
* FastAPI
* PostgreSQL
* SQLAlchemy
* Alembic
* NetworkX
* Pydantic v2
* Loguru

### Infrastructure

* Docker
* AWS EC2 (Ubuntu 24.04 LTS)
* Neon PostgreSQL
* systemd
* Nginx

### Testing

* pytest

### Planned Extensions

- Go — GraphCompute Worker for background scenario and ranking jobs
- Rust — Multigraph computation engine for high-performance traversal and scoring

### Data Sources

Current:

* Materials Project

Future:

* USGS Mineral Commodity Summaries
* Scientific Literature Sources
* Industrial Supply Chain Datasets

---

## Architecture

```text
Materials Project
        ↓
Material Import
        ↓
Material Graph
        ↓
Element Risk Profiles
        ↓
Material Risk Scoring
        ↓
Candidate Screening
        ↓
Candidate Comparison
        ↓
Scenario Ranking
        ↓
Sensitivity Analysis
        ↓
Substitution Analysis
```

---

## Current Data Model

### Material

Represents battery material candidates.

Examples:

* LiFePO4
* NaFePO4
* NaMnO2
* MgMn2O4

### Element

Represents chemical elements.

Examples:

* Li
* Na
* Mg
* Fe
* Mn
* O

### MaterialElement

Associative relationship between materials and elements.

### Application

Target application domain.

Examples:

* Battery Cathode
* Battery Anode
* Solid Electrolyte

### RiskFactor

Risk categories used for evaluation.

### ElementRiskProfile

Element-level risk intelligence.

---

## Example Workflow

### Candidate Screening

Request:

```json
{
  "scarce_elements": ["Li"],
  "avoid_elements": ["Co"],
  "require_stable": true,
  "max_energy_above_hull": 0.05
}
```

MaterialGraph:

* Evaluates candidates
* Applies penalties
* Computes risk-aware scores
* Returns ranked candidates

---

## Example Questions

MaterialGraph is designed to answer:

### Screening

```text
Which battery material candidates remain attractive under lithium scarcity?
```

### Comparison

```text
Why is candidate A better than candidate B?
```

### Scenario Analysis

```text
How do rankings change when cobalt becomes constrained?
```

### Sensitivity Analysis

```text
How sensitive is a candidate to worsening supply risk?
```

### Substitution Analysis

```text
If LiFePO4 becomes unattractive, what should I consider instead?
```

---

## Candidate Screening Core (Completed & Deployed)

* FastAPI foundation
* PostgreSQL integration
* SQLAlchemy models
* Alembic migrations
* Materials Project importer
* Material graph foundation
* Risk-aware screening engine
* Candidate comparison
* Scenario ranking
* Sensitivity analysis
* Substitution analysis
* Service tests
* API tests

---

## Current Status

### Go GraphCompute Worker

* PostgreSQL-backed job queue
* Background scenario simulation
* Candidate ranking jobs
* Supply-risk reweighting jobs
* systemd-managed worker process

### Rust Multigraph Engine

* CLI-based graph computation engine
* JSON input/output
* High-performance multigraph traversal
* Candidate scoring
* Path explanation and substitution analysis

---

## Project Scope

MaterialGraph does **not**:

* Perform autonomous material discovery
* Replace computational chemistry workflows
* Replace DFT calculations
* Guarantee synthesis feasibility
* Provide laboratory validation

MaterialGraph focuses on:

* Candidate exploration
* Risk-aware reasoning
* Substitution analysis
* Decision support
* Graph-based material intelligence

---

## Production Deployment

MaterialGraph Phase 1 is deployed using:

* AWS EC2 (Ubuntu 24.04)
* Neon PostgreSQL
* FastAPI
* SQLAlchemy
* Alembic
* systemd
* Nginx

Public Endpoints:

* API: `http://35.154.84.47`
* Swagger UI: `http://35.154.84.47/docs`
* Health Check: `http://35.154.84.47/health`

For complete deployment instructions, see:

`docs/DEPLOYMENT.md`

---

## Future Roadmap

### Phase 2 - Scientific Intelligence Layer

* USGS integration
* Criticality analysis
* Supply concentration intelligence
* Material family exploration
* Similarity search
* Enhanced graph relationships
* Constraint-aware recommendation engine
* Candidate neighborhood exploration

### Phase 3 - Discovery Intelligence Layer

* Graph analytics
* Graph embeddings
* Recommendation systems
* Machine-assisted candidate exploration
* Candidate generation workflows
* Material relationship discovery
* Scientific hypothesis exploration
* Embedding-based similarity search

### Phase 4 - Distributed Computation Layes

* PostgreSQL-backed job system
* Go GraphCompute worker
* Background scenario processing
* Candidate ranking jobs
* Supply-risk recomputation
* Async graph computation

### Phase 5 - High Performance Graph Engine

* Rust-based multigraph engine
* High-performance graph traversal
* Candidate scoring engine
* Path explanation engine
* Substitution analysis engine
* Large-scale graph optimization

---

## License

MIT License