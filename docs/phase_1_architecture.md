# MaterialGraph Phase 1 Architecture

## Mission

MaterialGraph is a graph-based material intelligence and candidate screening platform focused on battery material candidates.

It is not a general materials knowledge graph, DFT platform, or bulk Materials Project clone.

## Core Question

Given lithium or cobalt scarcity, which alternative battery material candidates remain attractive under defined constraints?

## Phase 1 Scope

MaterialGraph supports:

- Battery candidate exploration
- Constraint-aware reasoning
- Supply-risk-aware ranking
- Substitution analysis
- Decision support

## Candidate Universe

Initial Materials Project import is intentionally small:

- Li-Fe-P-O
- Na-Fe-P-O
- Na-Mn-O
- Mg-Mn-O
- Li-Mn-O

Example candidates:

- LiFePO4
- NaFePO4
- NaMnO2
- MgMn2O4
- LiMn2O4

## Integration Flow

Materials Project API  
→ fetch battery-focused candidates  
→ normalize material data  
→ upsert materials  
→ upsert elements  
→ create material-element relationships  
→ store raw JSON snapshot  
→ later connect to screening/ranking logic

## Guardrail

If a feature does not help answer the core candidate-screening question, it does not belong in Phase 1.