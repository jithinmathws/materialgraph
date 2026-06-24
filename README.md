# MaterialGraph

**Deterministic Materials Discovery Knowledge Graph for Candidate Exploration, Scientific Pathways, and Explainable Decision Support**

## Overview

MaterialGraph is a deterministic, explainable Materials Discovery Knowledge Graph designed to support candidate exploration, substitution analysis, scientific pathway discovery, graph analytics, and risk-aware decision support.

MaterialGraph does not perform autonomous scientific reasoning or replace computational chemistry workflows. Instead, it provides graph-driven, explainable discovery intelligence built upon known materials and scientific constraints.

The platform evaluates and compares known material candidates using explainable scoring, risk models, graph relationships, and scenario analysis.

---

## Design Principles

- Deterministic
- Explainable
- Graph-driven
- Scientifically grounded
- Production-ready
- No LLM reasoning

---

## Documentation

Additional project documentation is available in the `docs/` directory.

| Document                                             | Description                                                              |
| ---------------------------------------------------- | ------------------------------------------------------------------------ |
| [Getting Started](docs/getting_started.md)           | Local development setup and project bootstrapping                        |
| [System Architecture](docs/system_architecture.md)   | Current architecture and intelligence layer design                       |
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

### Scenario Policy Engine

Evaluate candidate materials under configurable scenario policies.

Supports:

* Supply-risk multipliers
* Element avoidance penalties
* Preferred element bonuses
* Explainable policy scoring
* Reusable policy evaluation pipeline

The policy engine provides centralized scoring logic that can be extended to future geopolitical, toxicity, abundance, and recyclability constraints.

### Material Exploration Layer

Explore chemically related candidate materials through family relationships.

Current family exploration includes:

* Same element families
* Alkali substitution families
* Transition metal families
* Phosphate families
* Oxide families

Family exploration supports explainable candidate expansion and future scientific intelligence workflows.

### Policy Sensitivity Analysis

Analyze how candidate recommendations change as policy parameters evolve.

Examples:

* Increasing supply-risk multiplier
* Changing preferred elements
* Changing avoided elements
* Comparing alternative policy configurations

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

### Discovery Knowledge Graph

MaterialGraph has evolved from a material intelligence platform into an explainable Materials Discovery Knowledge Graph.

The graph contains:

#### Node Intelligence

Each material node exposes:

- stability_score
- energy_above_hull
- criticality_score
- risk_score
- quality_score

#### Edge Intelligence

Each transition exposes:

- transition_type
- scientific_plausibility
- edge_score
- scientific_reason

#### Multi-Path Intelligence

Supports:

- K-best scientific paths
- K-shortest paths
- weighted shortest path search

#### Graph Algorithms

Supports:

- BFS traversal
- DFS traversal
- shortest path
- weighted shortest path
- K-shortest path search

#### Graph Analytics

Supports:

- degree centrality
- betweenness centrality
- closeness centrality
- material importance scoring

All reasoning is deterministic and explainable.

No LLM reasoning is used.

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
                                │
                                ▼

                Material Graph Foundation
                                │
                                ▼

                Material Intelligence Layer
        ┌──────────────┬──────────────┬──────────────┐
        ▼              ▼              ▼

        Similarity   Criticality    Recommendation

                                │
                                ▼

                Scenario Policy Engine
                                │
                                ▼

                Discovery Intelligence
        ┌──────────────┬──────────────┬──────────────┐
        ▼              ▼              ▼

        Candidates     Chains      Path Ranking

                                │
                                ▼

                Discovery Knowledge Graph
        ┌──────────────┬──────────────┬──────────────┐
        ▼              ▼              ▼

        Node        Edge         Multi-Path
        Intelligence Intelligence Intelligence

                                │
                                ▼

                Graph Algorithms Layer
                                │
                                ▼

                Graph Analytics Layer
                                │
                                ▼

                Explainable Discovery Intelligence
```
---

## Current Architecture

### Foundation Layer
✓ Material Graph Foundation
✓ Material Neighborhood Intelligence
✓ Material Family Intelligence

### Discovery Layer
✓ Candidate Engine
✓ Multi-Hop Chains
✓ Path Ranking

### Knowledge Graph Layer
✓ Node Intelligence
✓ Edge Intelligence

### Multi-Path Intelligence
✓ K-Best Paths
✓ K-Shortest Paths

### Graph Algorithms
✓ BFS
✓ DFS
✓ Weighted Shortest Path

### Graph Analytics
✓ Degree Centrality
✓ Betweenness Centrality
✓ Closeness Centrality
✓ Material Importance Scoring

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

### Scenario-Aware Recommendation

MaterialGraph supports scenario-aware recommendation ranking under changing supply-risk conditions and strategic constraints.

Example:

```bash
curl "http://35.154.84.47/api/v1/materials/5/recommendations/scenario?element=Li&supply_risk_multiplier=1.5&avoid_element=Co&limit=5"
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

### Material Exploration Layer

```text
What chemically related material families should I explore for LiFePO4?
```

### Sensitivity Analysis

```text
How sensitive is a candidate to worsening supply risk?
```

### Policy Evaluation

```text
How does candidate ranking change if cobalt is avoided and sodium is preferred?
```

### Substitution Analysis

```text
If LiFePO4 becomes unattractive, what should I consider instead?
```

---

## MaterialGraph Current Capabilities (v1.9.0)

### Foundation Layer

✓ Material Graph Foundation
✓ Material Neighborhood Intelligence
✓ Material Family Intelligence
✓ Similarity Engine
✓ Criticality Analysis
✓ Recommendation Engine
✓ Scenario Policy Engine

### Discovery Layer

✓ Discovery Candidate Engine
✓ Discovery Scoring
✓ Discovery Warnings
✓ Explainable Discovery Reasoning
✓ Substitution Path Engine
✓ Multi-Hop Discovery Chain Engine

### Knowledge Graph Layer

✓ Material Quality Layer
✓ Node Intelligence
✓ Edge Intelligence
✓ Scientific transition scoring

### Multi-Path Intelligence

✓ K-best paths
✓ K-shortest paths

### Graph Algorithms

✓ BFS
✓ DFS
✓ Shortest path
✓ Weighted shortest path (Dijkstra)

### Graph Analytics

✓ Degree centrality
✓ Betweenness centrality
✓ Closeness centrality
✓ Material importance scoring

### Production

✓ FastAPI
✓ PostgreSQL
✓ SQLAlchemy
✓ AWS EC2 deployment
✓ Tests passing
✓ Deterministic reasoning
✓ No LLM reasoning

---

## Production Hadening

- Added shared material response schemas
- Added material family response schema
- Improved OpenAPI documentation
- Added pagination validation tests
- Centralized route-level material-not-found handling
- Optimized material intelligence services
- Reduced repeated criticality lookups
- Improved neighborhood traversal performance

## Current Status

Completed:
* Phase 1 Decision Intelligence Platform
* Phase 1.5 Async Graph Job Foundation
* Phase 2 Material Intelligence MVP
  - Material neighbors
  - Similarity search
  - Candidate neighborhood analysis
  - Material criticality analysis
  - Material exploration layer
  - Constraint-aware recommendations
  - Criticality-aware recommendations
  - Scenario-aware recommendations
  - Element-aware scenario scoring
  - Constraint-aware recommendation workflow
  - Scenario Policy Engine
  - Explainable policy evaluation

Planned:
* USGS-backed criticality enrichment
* Go GraphCompute Worker
* Rust Multigraph Engine

---

## Project Scope

MaterialGraph does not:

* Perform autonomous scientific reasoning
* Replace computational chemistry workflows
* Replace DFT calculations
* Guarantee synthesis feasibility
* Provide laboratory validation

MaterialGraph focuses on:

* Explainable candidate exploration
* Scientific pathway discovery
* Graph analytics
* Substitution analysis
* Risk-aware reasoning
* Deterministic discovery intelligence

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

### Phase 2.5 — Decision Intelligence Expansion

* Constraint reasoning
* Multi-element constraints
* Material family intelligence
* Application-aware candidate exploration
* USGS-backed criticality enrichment
* Geopolitical-risk-aware policies
* Toxicity-aware policies
* Recyclability-aware policies

### Phase 3 - Community Intelligence & Scientific Exploration

- Community detection
- Community importance scoring
- Ranked subgraph exploration
- Phosphate neighborhoods
- Na-substitution neighborhoods
- Battery-material subgraphs
- Research objective exploration
- Scientific pathway analysis

### Phase 4 - Distributed Computation Layer

- PostgreSQL-backed graph jobs
- Go GraphCompute Worker
- Background graph analytics
- Candidate ranking jobs
- Supply-risk recomputation

### Phase 5 - High Performance Graph Engine

- Rust multigraph engine
- Large-scale graph traversal
- High-performance scientific path search
- Graph optimization

---

## License

MIT License