# MaterialGraph Performance Baseline

## v1.9.4.1 Production Hardening

Measured on AWS EC2 production instance.

| Endpoint | Before | After |
|---|---:|---:|
| /discovery/candidates default | ~14.7s | ~2.1s |
| /discovery/chains | — | ~0.9s |
| /discovery/graph | ~20.4s | ~3.9s |
| /discovery/path | ~21.5s | ~3.2s |
| /research/scientific-pathways | ~46.8s | ~5.2s |

## Notes

- Discovery candidates now support fast default mode.
- Rich candidate generation remains available using include_recommendations=true and include_scenarios=true.
- Graph builder uses lightweight candidate expansion.
- Graph endpoints use request-level family, relationship, and quality caches.
- Material quality supports bulk loading through bulk criticality and bulk risk helpers.