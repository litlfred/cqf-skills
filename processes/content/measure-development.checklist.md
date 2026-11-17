<!-- GENERATED from cqf-skills/processes/content/measure-development.bpmn by cat-harness-tools/scripts/bpmn-checklist.ts. Do not edit: change the diagram and regenerate (bun run cat bpmn:checklist). -->

# Checklist — Develop a quality measure

> **Generated, and not the authority.** This is `cqf-skills/processes/content/measure-development.bpmn` (process `Process_MeasureDevelopment`) walked as a state machine. The diagram and the workflow engine decide; this list only reads them. Follow the `next:` line of each step rather than the order on the page, and record each step with the call it names, so the engine's committed state — not this list — says which edge was taken.

A measure is specified: the developer writes its CQL and the Measure resource, builds test cases with expected populations, evaluates them, and the IG author packages and publishes the measure.

## Begin — A measure specification is agreed (`Start`)

- Begin here.
- Call `workflow_start` with `process: "Process_MeasureDevelopment"` and the subject this run is about; keep the instance id it returns.
- next: → `Task_Cql` (Write the measure CQL)

### 1. Write the measure CQL (`Task_Cql`)

- Who: the `Measure developer` lane (role `measure-developer`).
- What: Write population criteria in the layers and patterns the measure programme requires, against the profiles it pins.
- Record it: `workflow_complete` with `node: "Task_Cql"`.
- next: → `Task_Measure` (Define the Measure resource)

### 2. Define the Measure resource (`Task_Measure`)

- Who: the `Measure developer` lane (role `measure-developer`).
- What: Scoring, population basis, populations naming the CQL definitions, stratifiers, supplemental data, improvement notation.
- Record it: `workflow_complete` with `node: "Task_Measure"`.
- next: → `Task_Terminology` (Pin the value sets)

### 3. Pin the value sets (`Task_Terminology`)

- Who: the `Measure developer` lane (role `measure-developer`).
- What: Expand every value set the measure uses at pinned code system versions; keep the expansions with the tests.
- Record it: `workflow_complete` with `node: "Task_Terminology"`.
- next: → `Task_Cases` (Build test cases with expected populations)

### 4. Build test cases with expected populations (`Task_Cases`)

- Who: the `Measure developer` lane (role `measure-developer`).
- What: One synthetic case per population boundary, with MeasureReport expected values; convert to and from MADiE where the programme uses it.
- Record it: `workflow_complete` with `node: "Task_Cases"`.
- next: → `Task_Evaluate` (Evaluate and compare)

### 5. Evaluate and compare (`Task_Evaluate`)

- Who: the `Measure developer` lane (role `measure-developer`).
- What: Run $evaluate-measure (or Execute CQL) and compare counts and scores with the expected values; explain every difference.
- Record it: `workflow_complete` with `node: "Task_Evaluate"`.
- next: → `Task_Package` (Package the measure)

### 6. Package the measure (`Task_Package`)

- Who: the `IG author` lane (role `ig-author`).
- What: Claim the CRMI profiles and $package the Measure with its libraries and value sets.
- Record it: `workflow_complete` with `node: "Task_Package"`.
- next: → `Task_Publish` (Build and publish the IG)

### 7. Build and publish the IG (`Task_Publish`)

- Who: the `IG author` lane (role `ig-author`).
- What: Run the IG Publisher and read qa.html until it is clean.
- Record it: `workflow_complete` with `node: "Task_Publish"`.
- next: → `End` (Measure published)

## Done — Measure published (`End`)

- The instance completes here. `workflow_next` then reports nothing enabled — that, not this line, is the record of completion.
