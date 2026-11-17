---
# cqf-skills-hk01
title: 'HK-01: harness checks still red in the pinned layers'
status: in-progress
type: task
priority: normal
tags:
    - this-repository
created_at: 2026-11-17T00:00:00Z
updated_at: 2026-11-17T21:30:00Z
---

The mounts are laid down from `index.lock.json` (the six layers litlfred/smart-trust-demo pins on 2026-11-17) and the checks that judge this layer pass (HARNESS.md lists them). Red at those pins, from the mounted layers rather than from cqf-skills:

- `skill:commands` (and so `skill:register`): cat-harness's committed `.claude/commands/*.md` name skills that no longer declare `user_invocable` — regenerate in cat-harness.
- `kg:audit:check`: ten `test/attestations/kg-qa/sdlc/processes/*.attestations.json` in cat-harness judge subjects no report covers.
- `check:declaration-resolution`: cat-harness and cat-harness-tools directories cut over to state branches are not mounted (`state:mount`), and cat-harness's `beans` directory reads this layer's `beans/` (smart-trust-demo keeps its beans on main the same way).
- `skills:docs:check`, `check:glossary`: need the state branches and the QA corpus (`qa:fetch`).

## Done when

- [ ] Re-pinned to layers where these are green, or each is a bean in the layer that owns it
- [x] A CI job here runs `mount:lock` and the passing checks, with actions pinned by SHA (`harness` in `.github/workflows/validate.yml`)
- [ ] Decide whether `beans/` moves to a state branch `cat/cqf-skills/beans`

2026-11-17: checked cat-harness `main` (`72b0bc13`): the stale `.claude/commands/*.md` and the ten orphaned `test/attestations/kg-qa/sdlc/processes/*.attestations.json` are still there, so a re-pin does not clear `skill:commands` or `kg:audit:check`; they belong to cat-harness, and litlfred/smart-trust-demo, on the same pins, is in the same state. Left for the owner: whether to raise them in cat-harness, and whether `beans/` moves to a state branch (recommendation: keep it on main, as smart-trust-demo does, until cat-harness's `beans` directory stops reading a downstream's root `beans/`).
