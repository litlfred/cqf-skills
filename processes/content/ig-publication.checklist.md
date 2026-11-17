<!-- GENERATED from cqf-skills/processes/content/ig-publication.bpmn by cat-harness-tools/scripts/bpmn-checklist.ts. Do not edit: change the diagram and regenerate (bun run cat bpmn:checklist). -->

# Checklist — Build and publish a content IG

> **Generated, and not the authority.** This is `cqf-skills/processes/content/ig-publication.bpmn` (process `Process_IgPublication`) walked as a state machine. The diagram and the workflow engine decide; this list only reads them. Follow the `next:` line of each step rather than the order on the page, and record each step with the call it names, so the engine's committed state — not this list — says which edge was taken.

Artifacts changed: the IG author compiles the FSH, checks the extensions used, builds with the IG Publisher and packages the artifacts.

## Begin — Artifacts changed (`Start`)

- Begin here.
- Call `workflow_start` with `process: "Process_IgPublication"` and the subject this run is about; keep the instance id it returns.
- next: → `Task_Fsh` (Compile the FSH with SUSHI)

### 1. Compile the FSH with SUSHI (`Task_Fsh`)

- Who: the `IG author` lane (role `ig-author`).
- What: Fix every SUSHI error and warning before the publisher runs.
- Record it: `workflow_complete` with `node: "Task_Fsh"`.
- next: → `Task_Ext` (Check the extensions used)

### 2. Check the extensions used (`Task_Ext`)

- Who: the `IG author` lane (role `ig-author`).
- What: Each extension from the Extensions Pack version pinned, none deprecated without its replacement.
- Record it: `workflow_complete` with `node: "Task_Ext"`.
- next: → `Task_Pub` (Run the IG Publisher)

### 3. Run the IG Publisher (`Task_Pub`)

- Who: the `IG author` lane (role `ig-author`).
- What: Pinned publisher version, ig.ini and parameters; read qa.html.
- Record it: `workflow_complete` with `node: "Task_Pub"`.
- next: → `Task_Pkg` (Package the artifacts)

### 4. Package the artifacts (`Task_Pkg`)

- Who: the `IG author` lane (role `ig-author`).
- What: $package the knowledge artifacts with a manifest Library pinning dependencies.
- Record it: `workflow_complete` with `node: "Task_Pkg"`.
- next: → `End` (IG published)

## Done — IG published (`End`)

- The instance completes here. `workflow_next` then reports nothing enabled — that, not this line, is the record of completion.
