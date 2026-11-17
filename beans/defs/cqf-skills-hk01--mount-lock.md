---
# cqf-skills-hk01
title: 'HK-01: lay down the harness mounts and run the harness checks'
status: todo
type: task
priority: high
tags:
    - this-repository
created_at: 2026-11-17T00:00:00Z
updated_at: 2026-11-17T00:00:00Z
---

`index.config.json` pins fhir-harness at the commit smart-trust-tools pins, but `index.lock.json`, `package.json`, `bun.lock` and `.github/cat.ts` are not here yet, so `bun run cat mount:lock`, `skill:register:check`, `harness:dirs:check` and the BPMN checks have not run on this layer.

## Done when

- [ ] `index.lock.json` written by `mount:lock` and committed; mounts gitignored
- [ ] The harness checks pass, or their findings are beans
- [ ] A CI job runs `python3 -I tools/kg-index/kg_index.py --check` beside `validate_skills.py`
