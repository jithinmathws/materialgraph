# MaterialGraph Security

**Status:** Initial security planning
**Project stage:** Deterministic scientific prototype
**Last updated:** 2026-07-20

## Purpose

This directory documents the security workstream for MaterialGraph.

MaterialGraph began as an individual scientific and engineering prototype. Security was not originally developed as a separate architectural track.

The project is now moving toward a broader research platform that may eventually support:

* public API access
* researcher accounts
* organizations and collaborative research workspaces
* organization administrators and role-based administration
* organization membership and invitation workflows
* private research projects
* saved objectives and pathways
* API keys
* subscriptions
* document and literature ingestion
* LLM-assisted workflows

Security must be introduced before these capabilities are exposed in a production multi-user environment.

## Current Position

MaterialGraph currently consists primarily of:

* public scientific and materials data
* deterministic scoring and reasoning logic
* graph traversal and pathway analysis
* FastAPI services
* PostgreSQL data storage
* Nginx and systemd deployment
* AWS EC2 infrastructure
* external scientific data integrations

The current security concerns are mainly:

* secrets handling
* infrastructure exposure
* public API abuse
* expensive graph operations
* dependency vulnerabilities
* production logging and error handling
* backup and recovery readiness

Future multi-user capabilities will introduce additional risks involving:

* authentication
* authorization
* organization isolation
* private research data
* uploaded documents
* LLM access
* subscription and billing workflows

These future risks are acknowledged but are not yet treated as implemented vulnerabilities.

## Security Principles

MaterialGraph security work will follow these principles:

1. Security changes must preserve deterministic scientific behaviour.
2. Security controls must be verified through tests and deployment inspection.
3. Authentication and authorization must be treated separately.
4. Private data must be denied by default.
5. Tenant boundaries must be enforced in the backend.
6. Expensive scientific endpoints must have resource limits.
7. Secrets must not be stored in source control or exposed through logs.
8. Uploaded documents, external data, and LLM outputs must be treated as untrusted.
9. Services and users should receive only the permissions they require.
10. Security will be introduced incrementally rather than through one large rewrite.

## Initial Security Workstream

Security work will begin with a small foundation phase.

### Stage 1 — Current Prototype Review

The first stage will inspect:

* API endpoint exposure
* request validation
* graph traversal limits
* execution timeouts
* rate limiting
* secrets management
* Nginx configuration
* systemd configuration
* EC2 network exposure
* database connectivity
* logging and error handling
* dependencies
* backups and recovery

The purpose is to understand the current system before confirming security findings.

### Stage 2 — Multi-User Foundation

This stage will begin only when user and organization features are introduced.

It will cover:

* user authentication
* organization creation and management
* organization membership
* organization administrator capabilities
* role-based access control
* object-level authorization
* tenant isolation
* API keys
* authorization and permission testing

### Stage 3 — Future Commercial and AI Capabilities

This stage will cover:

* subscriptions
* billing-provider integration
* usage quotas
* document uploads
* retrieval authorization
* LLM tool restrictions
* prompt-injection risks
* model usage and cost controls

## Security Findings

Confirmed security findings will eventually use identifiers such as:

```text
MG-SEC-001
MG-SEC-002
MG-SEC-003
```

A finding should include:

* title
* status
* severity
* affected component
* threat scenario
* current safeguards
* missing safeguards
* recommended remediation
* verification requirements
* resolution version

No issue should be marked as a confirmed vulnerability until the relevant code or infrastructure configuration has been inspected.

## Relationship to the Architecture Audit

The existing `MG-AUD-*` audit remains focused on:

* scientific correctness
* deterministic behaviour
* architecture
* semantics
* explainability
* ranking policy
* performance

Security findings will use the separate `MG-SEC-*` series.

The two workstreams may proceed in parallel, but security changes must not silently alter scientific outputs.

## Next Step

After the current architecture audit remediation reaches the agreed transition point, the first security task will be to inspect the deployed prototype and create an initial set of verified security findings.

Until then, this document serves as the baseline for the MaterialGraph security workstream.

Security documentation will evolve alongside MaterialGraph. As major capabilities such as authentication, organization workspaces, document ingestion, AI integration, and subscription management are introduced, dedicated security documentation and implementation guidance will be added for those features. This approach keeps the documentation aligned with the actual system architecture and avoids documenting designs that have not yet been implemented.