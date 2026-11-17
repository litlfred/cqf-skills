<!-- GENERATED from cqf-skills/processes/content/skill-contribution.bpmn by cat-harness-tools/scripts/bpmn-checklist.ts. Do not edit: change the diagram and regenerate (bun run cat bpmn:checklist). -->

# Checklist — Add or change a skill

> **Generated, and not the authority.** This is `cqf-skills/processes/content/skill-contribution.bpmn` (process `Process_SkillContribution`) walked as a state machine. The diagram and the workflow engine decide; this list only reads them. Follow the `next:` line of each step rather than the order on the page, and record each step with the call it names, so the engine's committed state — not this list — says which edge was taken.

A gap in the catalog (a bean) or a change upstream: the skill maintainer writes or changes the skill and its evals, regenerates the knowledge-graph view, and offers a skill of general use to cqframework.

## Begin — A gap or an upstream change (`Start`)

- Begin here.
- Call `workflow_start` with `process: "Process_SkillContribution"` and the subject this run is about; keep the instance id it returns.
- next: → `Task_Bean` (Record the gap as a bean)

### 1. Record the gap as a bean (`Task_Bean`)

- Who: the `Skill maintainer` lane (role `skill-maintainer`).
- What: One bean in beans/defs/ naming the tasks, two or three example prompts and the spec versions targeted.
- Record it: `workflow_complete` with `node: "Task_Bean"`.
- next: → `Task_Write` (Write the skill from the template)

### 2. Write the skill from the template (`Task_Write`)

- Who: the `Skill maintainer` lane (role `skill-maintainer`).
- What: Copy template/ to skills/<name>/, self-contained, versions stated, claims cited; mark draft until checked by running.
- Record it: `workflow_complete` with `node: "Task_Write"`.
- next: → `Task_Evals` (Write its evals)

### 3. Write its evals (`Task_Evals`)

- Who: the `Skill maintainer` lane (role `skill-maintainer`).
- What: Trigger prompts (should and should not load), questions and an answer key in evals/<name>/.
- Record it: `workflow_complete` with `node: "Task_Evals"`.
- next: → `Task_Register` (Validate and regenerate the graph view)

### 4. Validate and regenerate the graph view (`Task_Register`)

- Who: the `Skill maintainer` lane (role `skill-maintainer`).
- What: Add it to marketplace.json, the README catalog and CHANGELOG; run validate_skills.py and tools/kg-index/kg_index.py.
- Record it: `workflow_complete` with `node: "Task_Register"`.
- next: → `Task_Offer` (Review the skill offered upstream)

### 5. Review the skill offered upstream (`Task_Offer`)

- Who: the `cqframework maintainer` lane (role `cqframework-maintainer`).
- What: A skill of general use is proposed to cqframework/cqf-skills as an issue, then a PR, once its evals pass with the skill and do worse without it.
- Record it: `workflow_complete` with `node: "Task_Offer"`.
- next: → `End` (Skill in the catalog)

## Done — Skill in the catalog (`End`)

- The instance completes here. `workflow_next` then reports nothing enabled — that, not this line, is the record of completion.
