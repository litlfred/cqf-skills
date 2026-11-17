---
$schema: folio-memory/v1
id: dir-fork
label: stable
summary: "Owner directive: litlfred/cqf-skills is a fork of cqframework/cqf-skills, made a cat-harness knowledge graph"
createdAt: 2026-11-17
---
Given by the owner on 2026-11-17: "make litlfred fork https://github.com/cqframework/cqf-skills and harness as KG and add missing processes/skills". So: the upstream layout (skills/<name>/SKILL.md, evals/, marketplace.json, validate_skills.py) stays the source and is never restructured; the harness layer is added beside it (cqf-skills.json, index.config.json, harness/skills/ generated from SKILL.md, processes/, scenarios/, memory/, beans/). Missing skills are added in the upstream format, marked draft, so that any of general use can be offered back to cqframework as an issue and PR. Nothing is merged into cqframework from here.
