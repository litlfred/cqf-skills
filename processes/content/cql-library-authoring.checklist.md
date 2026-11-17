<!-- GENERATED from cqf-skills/processes/content/cql-library-authoring.bpmn by cat-harness-tools/scripts/bpmn-checklist.ts. Do not edit: change the diagram and regenerate (bun run cat bpmn:checklist). -->

# Checklist — Author a CQL library

> **Generated, and not the authority.** This is `cqf-skills/processes/content/cql-library-authoring.bpmn` (process `Process_CqlLibraryAuthoring`) walked as a state machine. The diagram and the workflow engine decide; this list only reads them. Follow the `next:` line of each step rather than the order on the page, and record each step with the call it names, so the engine's committed state — not this list — says which edge was taken.

A logic requirement is agreed: the knowledge engineer writes the CQL, runs it against synthetic cases, packages it as a FHIR Library and claims the CRMI profile it meets.

## Begin — A logic requirement is agreed (`Start`)

- Begin here.
- Call `workflow_start` with `process: "Process_CqlLibraryAuthoring"` and the subject this run is about; keep the instance id it returns.
- next: → `Task_Write` (Write the CQL)

### 1. Write the CQL (`Task_Write`)

- Who: the `Knowledge engineer` lane (role `knowledge-engineer`).
- What: Write the library against the model and version the project pins, with FHIRHelpers, and declare terminology as value sets or codes.
- Record it: `workflow_complete` with `node: "Task_Write"`.
- next: → `Task_Terminology` (Declare and pin terminology)

### 2. Declare and pin terminology (`Task_Terminology`)

- Who: the `Knowledge engineer` lane (role `knowledge-engineer`).
- What: Declare code systems, value sets and codes; expand the value sets the tests use and keep the expansions with their version parameters.
- Record it: `workflow_complete` with `node: "Task_Terminology"`.
- next: → `Task_Test` (Run it against synthetic test cases)

### 3. Run it against synthetic test cases (`Task_Test`)

- Who: the `Knowledge engineer` lane (role `knowledge-engineer`).
- What: Lay out test cases for the VS Code CQL extension and compare Execute CQL results with the expected values.
- Record it: `workflow_complete` with `node: "Task_Test"`.
- next: → `Task_Library` (Package as a FHIR Library)

### 4. Package as a FHIR Library (`Task_Library`)

- Who: the `Knowledge engineer` lane (role `knowledge-engineer`).
- What: Encode the CQL (and ELM) in a Library as Using CQL with FHIR requires: content, parameters, dataRequirements, relatedArtifact.
- Record it: `workflow_complete` with `node: "Task_Library"`.
- next: → `Task_Crmi` (Claim the CRMI profile)

### 5. Claim the CRMI profile (`Task_Crmi`)

- Who: the `Knowledge engineer` lane (role `knowledge-engineer`).
- What: Choose shareable, publishable, computable or executable and fill what that profile requires.
- Record it: `workflow_complete` with `node: "Task_Crmi"`.
- next: → `End` (Library ready to publish)

## Done — Library ready to publish (`End`)

- The instance completes here. `workflow_next` then reports nothing enabled — that, not this line, is the record of completion.
