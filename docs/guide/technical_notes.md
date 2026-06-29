# MaterialGraph Technical Notes

## Purpose

This document records technical decisions, implementation notes, known limitations, and future engineering improvements.

Unlike the roadmap, which describes future capabilities, this document focuses on engineering considerations that influence development and maintenance.

---

# Dependency Notes

## HTTP Client

Current implementation uses a temporary compatibility solution for HTTP client dependencies.

Current state:

- httpx2
- httpcore2

Reason:

The dependency was introduced during development to resolve compatibility issues with the original HTTP client stack.

Future work:

- migrate back to the standard `httpx` ecosystem once compatibility issues are resolved.

---

# Current Engineering Decisions

## Graph Storage

MaterialGraph currently stores graph data using PostgreSQL together with NetworkX.

Reason:

- deterministic traversal
- production simplicity
- relational persistence
- easier testing
- avoids unnecessary infrastructure complexity

Graph databases are intentionally deferred.

---

## Deterministic Computation

Scientific reasoning is deterministic.

MaterialGraph intentionally avoids:

- probabilistic recommendations
- opaque scoring
- LLM-based scientific reasoning

Every result should be reproducible.

---

## Explainable Scoring

Scores are never intended to stand alone.

Every score should be explainable through:

- graph relationships
- material quality
- criticality
- scientific pathways
- objective alignment
- policy evaluation

---

# Production Notes

Current production deployment:

- FastAPI
- PostgreSQL
- SQLAlchemy
- AWS EC2
- systemd
- Nginx

Deployment documentation is maintained separately in `DEPLOYMENT.md`.

---

# Current Limitations

MaterialGraph currently does not include:

- experimental evidence management
- literature integration
- DFT workflow integration
- laboratory workflow support
- collaborative research sessions
- distributed graph computation

These limitations are intentional and align with the current development roadmap.

---

# Future Engineering Improvements

## Distributed Computation

Planned:

- PostgreSQL graph jobs
- Go GraphCompute Worker
- background graph analytics
- asynchronous ranking

---

## High Performance Graph Engine

Planned:

- Rust graph engine
- optimized graph traversal
- high-performance scientific path search

---

## Scientific Data Enrichment

Future data sources may include:

- USGS Mineral Commodity Summaries
- scientific literature
- industrial supply-chain datasets

---

# Documentation Notes

Technical architecture is documented in:

- system_architecture.md
- research_architecture.md
- scientific_principles.md

Development priorities are documented in:

- roadmap.md