---
# cqf-skills-sk03
title: 'SK-03: skills still missing from the catalog'
status: completed
type: feature
priority: normal
tags:
    - this-repository
created_at: 2026-11-17T00:00:00Z
updated_at: 2026-11-17T21:00:00Z
---

Gaps found when the fork was made, not yet written:

- `cds-hooks`: CDS Hooks services backed by PlanDefinition `$apply` (hooks, prefetch, cards).
- `elm`: reading and checking ELM (CQL-to-ELM translator options, annotations, locators) without the cql-mcp server.
- `immunization-cds`: immunization schedules as CQL and PlanDefinitions (ImmunizationRecommendation, SMART Immunizations).
- `cql-tests`: the cql-tests repository's test format and how to report an engine discrepancy (now partly in `madie`).

## Done when

- [x] Each is written in the upstream format with evals, or recorded here as not needed and why

Done 2026-11-17:

- `cds-hooks`: written, checked against CDS Hooks 2.0 and by running clinical-reasoning 4.13.0's CDS service.
- `immunization-cds`: written, checked against the R4 and CPG 2.0.0 packages, the WHO IMMZ IG and by running `$apply`.
- `elm`: **not needed.** ELM semantics and the ELM schema are in `cql` (its spec copy), packaging ELM in a Library in `cql-ig` ("Using ELM"), and translating and inspecting ELM in `cql-mcp` (`cql_view_elm`). A separate skill would repeat them.
- `cql-tests`: **not needed.** `cql` uses the cql-tests suite as its conformance reference and `madie` (`resources/vscode.md`) says how to report an engine discrepancy there.
