# MaterialGraph Engineering Strengths

This document captures architectural patterns that have demonstrated
long-term value during MaterialGraph development.

Future implementations should preserve these patterns whenever possible.

---

# Layered Intelligence

Foundation

↓

Discovery

↓

Knowledge Graph

↓

Research Intelligence

↓

Evidence Intelligence

Each layer owns a single responsibility.

---

# Deterministic Scientific Reasoning

Scientific computation is deterministic.

LLMs may summarize.

LLMs do not generate scientific conclusions.

---

# Canonical Scientific Services

Each scientific concept has one implementation.

Examples

- MaterialCompositionService
- MaterialQualityService
- MaterialCriticalityService

Duplicate scientific logic is avoided.

---

# Explainability First

Every recommendation explains:

- why
- evidence
- assumptions
- weaknesses
- validation priorities

---

# Evidence Separation

Scientific computation is separated from evidence.

Evidence enriches reasoning.

Evidence does not silently alter deterministic algorithms.

---

# Progressive Production Hardening

Performance improvements must preserve scientific semantics.

Examples

- caching

- bulk loading

- graph expansion limits

- request timing

---

# Stable API Evolution

Public API contracts should remain stable.

Responses may be extended.

Existing fields should remain compatible.

---

# Endpoint-Sensitive Ranking

Scientific usefulness and endpoint differentiation are treated as
independent concepts.

---

# Explicit Unknown Handling

Unknown information is explicitly represented rather than hidden.

Missing evidence is never silently interpreted.