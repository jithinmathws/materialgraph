# MaterialGraph Performance Baseline

## v1.9.4.1 Production Hardening

Measured on AWS EC2 production instance.

| Endpoint | Before | After |
|---|---:|---:|
| `/discovery/candidates` default | ~14.7s | ~2.1s |
| `/discovery/chains` | — | ~0.9s |
| `/discovery/graph` | ~20.4s | ~4.2s |
| `/discovery/path` | ~21.5s | ~3.1s |
| `/research/scientific-pathways` | ~46.8s | ~5.0s |

## Improvements

- Added fast default discovery candidate mode.
- Kept rich candidate mode behind explicit flags.
- Added lightweight graph expansion.
- Added request-level graph caches.
- Added bulk criticality and risk loading.
- Added threshold-based performance logging.
- Reduced noisy per-candidate instrumentation.

## Notes

MaterialGraph preserves deterministic and explainable behavior while improving production responsiveness.