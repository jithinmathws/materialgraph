# MaterialGraph
## Phase 1 — Battery Material Candidate Screening Core
### Mission

Build a graph-based material intelligence platform capable of screening and exploring battery material candidates under scientific, industrial, and supply-risk constraints.

The platform does not perform material discovery.

The platform supports:

 - candidate exploration
 - constraint-aware reasoning
 - supply-risk-aware ranking
 - substitution analysis
 - decision support
### Core Question

The entire Phase 1 should be optimized around answering questions like:

Given lithium or cobalt scarcity, which alternative battery material candidates remain attractive under defined constraints?

or

How does candidate ranking change when abundance, toxicity, recyclability, or geopolitical concentration constraints are modified?

If a feature does not help answer those questions, it probably does not belong in Phase 1.

Architectural Identity

MaterialGraph is:

a material intelligence platform

not:

 - a materials database
 - a DFT workflow engine
 - a generic knowledge graph
 - a supply-chain platform
### Phase 1 Architecture
External Datasets
        ↓
Knowledge Integration Layer
        ↓
Material Graph Layer
        ↓
Constraint Engine
        ↓
Scoring Engine
        ↓
Simulation Engine
        ↓
Decision Support APIs

This becomes the backbone of the entire project.

## Dataset Strategy
### Scientific Data

Primary:

 - Materials Project

Used for:

 - composition
 - stability
 - formation energy
 - band gap
 - material metadata
Industrial Data

Primary:

 - USGS

Used for:

 - criticality
 - country concentration
 - abundance
 - supply-risk metadata
## Graph Model
### Nodes
#### Material

Examples:

 - LiFePO4
 - NaFePO4
 - MgMn2O4
#### Element

Examples:

 - Lithium
 - Sodium
 - Magnesium
 - Iron
 - Manganese
#### Application

Examples:

 - Battery Cathode
 - Battery Anode
 - Solid Electrolyte
#### Property

Examples:

 - Stability
 - Formation Energy
 - Band Gap
 - Conductivity
#### Constraint

Examples:

 - Low Toxicity
 - Low Scarcity
 - High Recyclability
 - Low Geopolitical Risk
#### RiskFactor

Examples:

 - Country Concentration
 - Import Dependency
 - Critical Mineral Exposure
#### Relationships
##### Scientific
 - CONTAINS_ELEMENT
 - HAS_PROPERTY
 - SUITABLE_FOR_APPLICATION
 - Reasoning
 - ALTERNATIVE_TO
 - SUBSTITUTES_FOR
 - COMPETES_WITH
 - Industrial
 - EXPOSED_TO_RISK
 - PRODUCED_IN
 - REQUIRES_PROCESS
#### Constraint Engine

This becomes the heart of MaterialGraph.

Input:

{
  "max_toxicity": 0.3,
  "min_abundance": 0.6,
  "max_supply_risk": 0.4
}

Output:

 - candidate filtering
 - candidate penalties
 - candidate weighting

Every future feature will eventually pass through this layer.

Explainable Scoring Engine

Every score must be decomposable.

Bad:

{
  "score": 84.2
}

Good:

{
  "score": 84.2,
  "explanation": {
    "stability": 22,
    "abundance": 18,
    "recyclability": 15,
    "supply_risk": 12,
    "toxicity_penalty": -5,
    "criticality_penalty": -7
  }
}

MaterialGraph should always explain why a candidate ranks where it does.

Simulation Engine

Generic scenario model:

{
  "constraint": "lithium_availability",
  "modifier": -60
}

Examples:

Lithium shortage
Cobalt export restriction
Nickel demand surge
Rare-earth concentration increase

The engine should recompute:

 - candidate rankings
 - alternative pathways
 - risk exposure
#### APIs
##### Materials
GET /materials
GET /materials/{id}
##### Graph
GET /graph/summary
GET /graph/material/{id}
##### Candidates
POST /candidates/search
POST /candidates/rank
##### Simulations
POST /simulations/scenario
#### Explicitly Out of Scope

Not Phase 1:

 - Neo4j
 - GNNs
 - property prediction
 - material discovery claims
 - DFT workflows
 - large-scale KG construction
 - literature mining
 - patent mining
#### Development Milestones
##### M1

### Backend foundation

FastAPI
PostgreSQL
SQLAlchemy
Alembic
pytest
##### M2

### Core domain models

Material
Element
Application
Property
Constraint
RiskFactor
##### M3

### Materials Project integration

Import a limited battery-focused dataset.

##### M4

###### Graph construction

Build NetworkX graph.

##### M5

###### Constraint Engine

Filtering and weighting.

##### M6

###### Explainable Scoring Engine

Transparent ranking.

##### M7

###### Simulation Engine

Scenario-based recomputation.

##### M8

### Decision Support APIs

Candidate exploration workflows.