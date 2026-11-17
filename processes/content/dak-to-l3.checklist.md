<!-- GENERATED from cqf-skills/processes/content/dak-to-l3.bpmn by cat-harness-tools/scripts/bpmn-checklist.ts. Do not edit: change the diagram and regenerate (bun run cat bpmn:checklist). -->

# Checklist — Turn a DAK into L3 content

> **Generated, and not the authority.** This is `cqf-skills/processes/content/dak-to-l3.bpmn` (process `Process_DakToL3`) walked as a state machine. The diagram and the workflow engine decide; this list only reads them. Follow the `next:` line of each step rather than the order on the page, and record each step with the call it names, so the engine's committed state — not this list — says which edge was taken.

A WHO SMART Guidelines DAK (L2) is ready: the knowledge engineer maps each component to an L3 artifact and writes the logic, the IG author models the data and builds the IG.

## Begin — A DAK is ready for L3 (`Start`)

- Begin here.
- Call `workflow_start` with `process: "Process_DakToL3"` and the subject this run is about; keep the instance id it returns.
- next: → `Task_Map` (Map each DAK component to an L3 artifact)

### 1. Map each DAK component to an L3 artifact (`Task_Map`)

- Who: the `Knowledge engineer` lane (role `knowledge-engineer`).
- What: Decision tables to CQL and PlanDefinitions, data elements to logical models and value sets, indicators to Measures, personas to ActorDefinitions, keeping the DAK ids.
- Record it: `workflow_complete` with `node: "Task_Map"`.
- next: → `Task_Model` (Model the data elements)

### 2. Model the data elements (`Task_Model`)

- Who: the `IG author` lane (role `ig-author`).
- What: One logical model per activity in FSH, with the ValueSets and CodeSystems the data dictionary defines.
- Record it: `workflow_complete` with `node: "Task_Model"`.
- next: → `Task_Terms` (Bind and map the terminology)

### 3. Bind and map the terminology (`Task_Terms`)

- Who: the `IG author` lane (role `ig-author`).
- What: ValueSets for each coded element and ConceptMaps to standard terminologies; pin versions.
- Record it: `workflow_complete` with `node: "Task_Terms"`.
- next: → `Task_Logic` (Write each decision table as CQL)

### 4. Write each decision table as CQL (`Task_Logic`)

- Who: the `Knowledge engineer` lane (role `knowledge-engineer`).
- What: One library per table, one definition per row condition and per output, the hit policy encoded and tested.
- Record it: `workflow_complete` with `node: "Task_Logic"`.
- next: → `Task_Plan` (Write the PlanDefinitions)

### 5. Write the PlanDefinitions (`Task_Plan`)

- Who: the `Knowledge engineer` lane (role `knowledge-engineer`).
- What: One ECA-rule PlanDefinition per decision table claiming the CPG profile, actions naming the CQL definitions.
- Record it: `workflow_complete` with `node: "Task_Plan"`.
- next: → `Task_Apply` (Check $apply per row)

### 6. Check $apply per row (`Task_Apply`)

- Who: the `Knowledge engineer` lane (role `knowledge-engineer`).
- What: Run $apply against one synthetic case per row and one where no row fires.
- Record it: `workflow_complete` with `node: "Task_Apply"`.
- next: → `Task_Indicators` (Write the indicators as Measures)

### 7. Write the indicators as Measures (`Task_Indicators`)

- Who: the `Knowledge engineer` lane (role `knowledge-engineer`).
- What: One Measure and library per DAK indicator, numerator and denominator from its definition.
- Record it: `workflow_complete` with `node: "Task_Indicators"`.
- next: → `Task_Forms` (Write the data-capture Questionnaires)

### 8. Write the data-capture Questionnaires (`Task_Forms`)

- Who: the `IG author` lane (role `ig-author`).
- What: Questionnaires for the activities, with $populate and $extract against the logical models.
- Record it: `workflow_complete` with `node: "Task_Forms"`.
- next: → `Task_Build` (Build the IG)

### 9. Build the IG (`Task_Build`)

- Who: the `IG author` lane (role `ig-author`).
- What: Run the IG Publisher on SMART Base and read qa.html until it is clean.
- Record it: `workflow_complete` with `node: "Task_Build"`.
- next: → `End` (L3 IG built)

## Done — L3 IG built (`End`)

- The instance completes here. `workflow_next` then reports nothing enabled — that, not this line, is the record of completion.
