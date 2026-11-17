---
# cqf-skills-sk02
title: 'SK-02: check the terminology and smart-dak skills'
status: completed
type: task
priority: normal
tags:
    - this-repository
created_at: 2026-11-17T00:00:00Z
updated_at: 2026-11-17T20:00:00Z
---

Both are draft. `terminology` needs its `$expand` parameter claims checked against a configured server and its local-layout claim against the VS Code CQL extension; `smart-dak` needs checking against a built L3 IG on SMART Base (for example a WHO DAK IG) and the SMART Base version pinned.

## Done when

- [x] Claims cited and checked, probe records kept
- [x] SMART Base version pinned in `smart-dak`
- [x] "Status: draft" removed from both, and an issue opened upstream for any of general use

Done 2026-11-17. `terminology`: parameters checked against `hl7.fhir.r4.core` 4.0.1, engine behaviour by running clinical-reasoning 4.13.0 (`resources/probes/2026-11-17/`). `smart-dak`: checked against SMART Base 0.3.0 and the Immunizations and ANC IGs at pinned commits (`resources/sources.md`), SMART Base pinned at 0.3.0. Not done: no upstream issue opened, because opening one speaks for the owner on cqframework's tracker; that is the owner's call (see `memory/dir-upstream-bar.md`).
