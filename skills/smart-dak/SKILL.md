---
name: smart-dak
description: Turns a WHO SMART Guidelines Digital Adaptation Kit (DAK, L2) into computable L3 content in a FHIR IG built on SMART Base — decision-support tables into CQL libraries and CPG PlanDefinitions, core data elements into logical models, ValueSets and Questionnaires, indicators into Measures, business processes and personas into the IG's narrative and ActorDefinitions — and traces each artifact back to its DAK component. Use when converting DAK spreadsheets or decision tables to CQL, naming L3 artifacts by DAK identifiers (for example ANC.DT.01), choosing which FHIR resource carries a DAK component, or reviewing an L3 IG for DAK coverage. Not for general CPG profile questions (cpg), CQL semantics (cql) or IG Publisher configuration (ig-publisher).
license: Apache-2.0
---

# WHO SMART Guidelines: from DAK (L2) to computable content (L3)

> **litlfred fork.** Checked against the WHO repositories themselves, read at a pinned commit and
> recorded in [resources/sources.md](resources/sources.md) (cited as *S§n*): SMART Base **0.3.0**
> (`WorldHealthOrganization/smart-base`), the Immunizations IG (`smart-immunizations`, on SMART Base
> 0.2.0) and the ANC IG (`smart-anc`). Where the two IGs differ, both patterns are given. Confirm
> the SMART Base version the IG depends on (`sushi-config.yaml`, `dependencies: smart.who.int.base`).

The SMART Guidelines layers: **L1** narrative WHO guideline, **L2** the DAK (operational,
software-neutral), **L3** machine-readable FHIR IG, **L4** executable software. SMART Base:
<https://smart.who.int/base/>. IG starter kit and authoring conventions:
<https://smart.who.int/ig-starter-kit/>.

Related skills: `cpg` for the PlanDefinition and case-feature profiles, `cql` for the logic,
`plan-definition` for `$apply`, `questionnaire` for data capture, `measure` for indicators,
`terminology` for value sets, `crmi` for the shareable and publishable profiles, `fsh` and
`ig-publisher` to build the IG.

## The nine DAK components and the L3 artifact each becomes

SMART Base 0.3.0's `DAK` logical model has exactly these nine components (*S§1*):

| DAK component (`DAK` element) | L3 artifact in the WHO IGs |
|---|---|
| Health interventions and recommendations (`healthInterventions`) | IG narrative; a `relatedArtifact` of type `citation` to the L1 recommendation on each PlanDefinition (*S§2*) |
| Generic personas (`personas`) | `ActorDefinition` and narrative |
| User scenarios (`userScenarios`) | IG narrative pages |
| Generic business processes and workflows (`businessProcesses`) | BPMN in the IG; the activity ids (`IMMZ.D2`) name the triggers of the decision tables |
| Core data elements (`dataElements`) | one FSH `Logical` model per data-dictionary activity (`IMMZC4` "IMMZ.C4.Create client record"), its ValueSets and CodeSystems, and a `Questionnaire` per activity (`QIMMZC4`) (*S§3*) |
| Decision-support logic (`decisionLogic`) | per decision table, a CQL Library and a PlanDefinition (below); SMART Base 0.3.0 sources each table as a **DMN** file |
| Program indicators (`indicators`) | one `Measure` per indicator (`IMMZIND01` for IMMZ.IND.01), claiming `proportion-measure-cqfm` where it is a proportion (*S§3*) |
| Functional and non-functional requirements (`requirements`) | `Requirements` resources and narrative |
| Test scenarios (`testScenarios`) | test cases (synthetic) |

Scheduling logic is not a separate component in 0.3.0: the IMMZ IG writes its schedules
(`IMMZ.D18.S…`) as decision tables of the same shape.

## Decision table → CQL + PlanDefinition

1. **Keep the DAK's identifiers, with the dots removed.** Two conventions are in use (*S§2, §4*):
   - ANC: table `ANC.DT.01` → Library `ANCDT01` and PlanDefinition `ANCDT01`.
   - IMMZ: table `IMMZ.D2.DT.HPV.2 doses` → PlanDefinition `IMMZD2DTHPV2Doses` and Library
     `IMMZD2DTHPV2DosesLogic` (the PlanDefinition's `library` is `Canonical({id}Logic)`).
   Follow the IG you are extending; for a new IG, the newer IMMZ form.
2. **Inputs are data elements, never free text.** Shared input definitions live in their own
   libraries, included by every decision library: ANC `ANCDataElements` and `ANCContactDataElements`
   (plus `ANCConcepts`, `ANCConfig`); IMMZ one `…Elements` and `…EncounterElements` library per
   vaccine (`IMMZD2DTHPVEncounterElements`) (*S§2, §4*). A decision library only states rules.
3. **One definition per rule row, named after its output.** IMMZ writes `"<output> Case 1"`,
   `"<output> Case 2"`…, and the output as the `or` of its cases; each definition carries
   `@output` and `@pseudocode` comment annotations, and the library a header naming the table and its
   trigger (*S§2*). ANC names each rule after its output and keeps the DAK condition as a comment
   (*S§4*).
4. **Guidance as a dynamic value.** IMMZ adds a `"Guidance"` definition (a `case` over the outputs)
   and `"Has Guidance"`, used by a CommunicationRequest action (*S§2*).
5. **Hit policy.** For a *unique* table, the case conditions must be mutually exclusive; for *first*,
   an ordered `case`. Test that no input matches two rows of a unique table.
6. **The PlanDefinition** (*S§2, §4*):
   - IMMZ: `InstanceOf: cpg-recommendationdefinition`, `meta.profile` `crmi-shareableplandefinition`
     and `crmi-publishableplandefinition`, `cpg-knowledgeCapability` `computable`; one action per
     output, each with a `cpg-rationale`, an `applicability` condition in `text/cql-identifier` naming
     the output definition, and a `definitionCanonical` to an ActivityDefinition.
   - ANC: one top action titled with the table id, one child action per rule row (`id` "1", "2"…),
     each with an `applicability` condition naming the row's definition and a `documentation`
     citation.
7. **Test each row**: one synthetic test case per rule, plus one where no rule fires.

```cql
/*
 * Library: EXDT01Logic (EX.DT.01, illustrative)
 * Decision Table: Danger signs
 * Trigger: EX.B6 Check for danger signs
 */
library EXDT01Logic
using FHIR version '4.0.1'
include FHIRHelpers version '4.0.1'
include EXEncounterElements called Encounter

context Patient

/*
@output: Refer urgently Case 1
@pseudocode: "Danger signs" = "Convulsing"
*/
define "Refer urgently Case 1":
  Encounter."Client is convulsing"

/*
@output: Refer urgently
*/
define "Refer urgently":
  "Refer urgently Case 1"
```

## Traceability and coverage

- An L3 artifact traces to its DAK by **id and title**: the id is the DAK id without dots, the title
  repeats the dotted id (`"IMMZ.D2.DT.Dengue.3 doses with pre-vaccination screening"`), and the CQL
  header names the table and trigger. Neither IG uses `relatedArtifact` `derived-from` for this
  (*S§2*).
- The L1 recommendation is cited with `relatedArtifact` (IMMZ, type `citation`) or action
  `documentation` (ANC, type `citation`).
- Review coverage both ways: every decision table, indicator and data-dictionary activity has an
  artifact; every artifact has a DAK id.
- All personas, test patients and examples are fictional.

## Checklist

- [ ] Artifact ids are the DAK ids without dots, in the convention of the IG being extended.
- [ ] Inputs come from shared elements libraries, with ValueSets.
- [ ] One definition per rule row; outputs as the `or` of their cases; hit policy tested.
- [ ] PlanDefinitions claim the CPG and CRMI profiles the IG uses.
- [ ] One test case per rule, plus the no-rule case.
