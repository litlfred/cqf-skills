---
$schema: folio-memory/v1
id: dir-beans-on-main
label: stable
summary: "Owner directive: this layer's beans stay on main, not on a state branch"
createdAt: 2026-11-17
---
Given by the owner on 2026-11-17: "keep beans on main". `beans/defs/` stays tracked on `main`, as litlfred/smart-trust-demo keeps its own, rather than moving to a state branch `cat/cqf-skills/beans` (the smart-trust-tools pattern). `check:declaration-resolution` reports cat-harness's `beans` directory as "not-cut-over" because it reads this layer's root `beans/`; that finding is accepted, not fixed by moving the beans.
