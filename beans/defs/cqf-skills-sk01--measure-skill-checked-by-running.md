---
# cqf-skills-sk01
title: 'SK-01: check the measure skill by running clinical-reasoning'
status: completed
type: task
priority: high
tags:
    - this-repository
created_at: 2026-11-17T00:00:00Z
updated_at: 2026-11-17T19:00:00Z
---

`skills/measure` is draft: its population-nesting, score and operation claims come from FHIR R4 and the Quality Measure IG, not from a run. Upstream's `plan-definition` and `questionnaire` skills run clinical-reasoning 4.13.0 locally (`scripts/apply/run.sh`, `scripts/sdc/run.sh`).

## Done when

- [x] A `scripts/evaluate/run.sh` runs `$evaluate-measure` locally on clinical-reasoning, pinned
- [x] Each claim in SKILL.md is cited to the spec page or the engine source, with a probe record
- [x] The Quality Measure IG version is pinned, with a `build-kb.sh` for its profiles and extensions
- [x] A grader for a task case, as `evals/fhir/grade_bundle.py` does

Done 2026-11-17: `scripts/evaluate/run.sh`, probe `resources/probes/2026-11-17/` (RESULTS.md, cited P§n in SKILL.md), Quality Measure IG pinned at 5.0.0 with its sha256, grader `evals/measure/grade_measure.py` with tests. Four claims of the draft were corrected by the run (stratifier form, evaluatedResource, aggregate codes, the extension URL the engine emits).
