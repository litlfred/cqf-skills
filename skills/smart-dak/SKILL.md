---
name: smart-dak
description: Turns a WHO SMART Guidelines Digital Adaptation Kit (DAK, L2) into computable L3 content in a FHIR IG built on SMART Base — decision-support tables into CQL libraries and CPG PlanDefinitions, core data elements into logical models, ValueSets and Questionnaires, indicators into Measures, business processes and personas into the IG's narrative and ActorDefinitions — and traces each artifact back to its DAK component. Use when converting DAK spreadsheets or decision tables to CQL, naming L3 artifacts by DAK identifiers (for example ANC.DT.01), choosing which FHIR resource carries a DAK component, or reviewing an L3 IG for DAK coverage. Not for general CPG profile questions (cpg), CQL semantics (cql) or IG Publisher configuration (ig-publisher).
license: Apache-2.0
---

# WHO SMART Guidelines: from DAK (L2) to computable content (L3)

> **Status: draft (litlfred fork).** Written from the WHO SMART Guidelines approach and the SMART Base
> IG; not yet checked against a built L3 IG, as the upstream skills are. Confirm the SMART Base
> version the IG depends on (`sushi-config.yaml`, `dependencies: smart.who.int.base`).

The SMART Guidelines layers: **L1** narrative WHO guideline, **L2** the DAK (operational,
software-neutral), **L3** machine-readable FHIR IG, **L4** executable software, **L5** dynamic
(precision) systems. SMART Base: <https://smart.who.int/base/>. IG starter kit and authoring
conventions: <https://smart.who.int/ig-starter-kit/>.

Related skills: `cpg` for the PlanDefinition and case-feature profiles, `cql` for the logic,
`plan-definition` for `$apply`, `questionnaire` for data capture, `measure` for indicators,
`terminology` for value sets, `fsh` and `ig-publisher` to build the IG.

## Which L3 artifact carries each DAK component

| DAK component | L3 artifact | notes |
|---|---|---|
| Health interventions and recommendations | IG narrative; `cpg-recommendationdefinition` PlanDefinitions | cite the L1 recommendation id |
| Generic personas | `ActorDefinition` (and narrative) | one per persona |
| User scenarios | IG narrative pages | |
| Business processes and workflows | BPMN in the IG; `cpg-pathwaydefinition`/strategy PlanDefinitions where computable | |
| Core data elements (data dictionary) | logical models (FSH `Logical`), ValueSets/CodeSystems, Questionnaires, ConceptMaps to standard terminologies | one logical model per activity |
| Decision-support logic (decision tables) | one CQL `Library` and one `PlanDefinition` (ECA rule) per decision table | below |
| Scheduling logic | CQL + PlanDefinitions as for decision tables | |
| Program indicators | `Measure` (+ CQL library) per indicator | numerator/denominator from the DAK's definitions |
| Functional and non-functional requirements | `Requirements` resources (FHIR R5 / extension) or narrative | |

## Decision table → CQL + PlanDefinition

1. **Keep the DAK's identifiers.** A table `ANC.DT.01` becomes Library `ANCDT01` and PlanDefinition
   `ANCDT01`; each rule row keeps its row id in a comment or `action.id`. Reviewers trace by id.
2. **Inputs are data elements, never free text.** Each input column resolves to a data-element id
   (for example `ANC.B6.DE17`) whose ValueSet or type the logical model defines. Put shared input
   definitions in an `…Elements` library, so each decision library only states rules.
3. **One CQL definition per output, one per rule's condition.** Name the rule conditions after the row
   (`"Row 3 condition"`) and the outputs after the DAK output text, so the CQL reads as the table.
4. **Hit policy.** DAK tables are usually *unique* or *first*. Express *first* as an ordered `case`,
   and *unique* as mutually exclusive conditions — then test that no two rows match the same input.
5. **The PlanDefinition** has one action per output, `condition.kind` `applicability` naming the CQL
   definition, and the output's guidance in `action.description`/a CommunicationRequest
   ActivityDefinition. Claim the CPG profile (`cpg-recommendationdefinition` or the ECA-rule pattern)
   the `cpg` skill describes.
6. **Test each row**: one synthetic test case per rule plus one where no rule fires.

```cql
library ANCDT01 version '0.1.0'
using FHIR version '4.0.1'
include FHIRHelpers version '4.0.1'
include ANCElements called E

context Patient

// ANC.DT.01 row 1 (illustrative): danger sign present -> refer urgently
define "Row 1 condition": E."Danger signs" is not null and exists E."Danger signs"
define "Refer urgently": "Row 1 condition"
```

## Traceability and coverage

- Every L3 artifact names its DAK source: `relatedArtifact` of type `derived-from` (or
  `citation`) to the DAK component, plus the DAK id in `identifier` or the title.
- Review coverage both ways: every decision table, indicator and data element has an artifact; every
  artifact has a DAK source.
- All personas, test patients and examples are fictional.

## Checklist

- [ ] Artifact ids follow the DAK ids.
- [ ] Inputs resolve to data elements with ValueSets.
- [ ] Hit policy encoded and tested (overlap test for *unique*).
- [ ] One test case per rule, plus the no-rule case.
- [ ] `relatedArtifact` back to the DAK on every artifact.
