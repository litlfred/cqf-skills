# Sources, read 2026-11-17

What the `smart-dak` skill says about WHO's own L3 content was read from these repositories, at
these commits. Nothing is copied here beyond identifiers, element names and short structural facts.

| | repository | commit | commit date |
|---|---|---|---|
| SMART Base | `WorldHealthOrganization/smart-base` | `781a8b991548cb2a47657470416370a73d7664a1` | 2026-10-20 |
| Immunizations IG | `WorldHealthOrganization/smart-immunizations` | `bd7fa726706efc92d972d0dcebba9505f386b078` | 2026-10-01 |
| ANC IG | `WorldHealthOrganization/smart-anc` | `301a6b8b904361315ca38b28ee9fbd133f9d0e94` | 2026-10-16 |

## 1. SMART Base: the DAK model

- `sushi-config.yaml`: `id: smart.who.int.base`, `version: 0.3.0`, `fhirVersion: 4.0.1`.
- `input/fsh/models/DAK.fsh`: the `DAK` logical model's components, in order: `healthInterventions`,
  `personas`, `userScenarios`, `businessProcesses`, `dataElements`, `decisionLogic`, `indicators`,
  `requirements`, `testScenarios`. `input/pagecontent/StructureDefinition-DAK.md`: "all 9 DAK
  components".
- `input/fsh/models/DecisionSupportLogic.fsh`: `source 1..1 uri`, "Link to a DMN file containing the
  decision logic".
- `input/pagecontent/`: the authoring pages speak of layers L1 to L4.

## 2. Immunizations IG: decision tables

- `sushi-config.yaml` depends on `smart.who.int.base: 0.2.0`.
- `input/cql/`: 279 libraries, e.g. `IMMZD2DTHPV2DosesLogic.cql` (header: Library, Rule, Decision
  Table, Trigger `IMMZ.D2`), including `IMMZD2DTHPVEncounterElements`; definitions
  `"Client is not due for HPV vaccination Case 1"` … `Case 4`, the output as their `or`, `@output`,
  `@pseudocode` and `@guidance` annotations, `"Guidance"` (a `case` over the outputs) and
  `"Has Guidance"`. Shared: `IMMZCommon`, `IMMZConcepts`, `IMMZAgeConcepts`, and one `…Elements` and
  `…EncounterElements` library per vaccine.
- `input/fsh/plandefinitions/IMMZD2DTDengue3DosesWithPreVaccinationScreening.fsh`:
  `InstanceOf: http://hl7.org/fhir/uv/cpg/StructureDefinition/cpg-recommendationdefinition`, title
  `"IMMZ.D2.DT.Dengue.3 doses with pre-vaccination screening"`.
- `input/fsh/rulesets/rulesets-plandefinition.fsh`, `PlanDefMain`: `meta.profile`
  `crmi-shareableplandefinition` and `crmi-publishableplandefinition`, `library = Canonical({library}Logic)`,
  `cpg-knowledgeCapability` `#computable`, `relatedArtifact` type `#citation` to the WHO
  recommendation summary tables. `PlanDefMRAction`: `cpg-rationale`, `condition.kind #applicability`,
  `language #text/cql-identifier`, `definitionCanonical`. `PlanDefCommunicationRequestAction` for the
  guidance.

## 3. Immunizations IG: data elements and indicators

- `input/fsh/models/IMMZC4.fsh`: `Logical: IMMZC4`, title `"IMMZ.C4.Create client record"`, "Data
  elements for the IMMZ.C4.Create client record Data Dictionary Activity", CRMI shareable and
  publishable StructureDefinition profiles. One model per activity (`IMMZD1`, `IMMZD2`, …).
- `input/fsh/questionnaires/`: `QIMMZC4`, `QIMMZD1`, … one per activity.
- `input/fsh/measures/IMMZIND01.fsh`: `InstanceOf:
  http://hl7.org/fhir/us/cqfmeasures/StructureDefinition/proportion-measure-cqfm`, title
  `IMMZ.IND.01 Immunization coverage for BCG vaccine`.

## 4. ANC IG

- `input/cql/ANCDT01.cql` … : `library ANCDT01`, including `ANCConfig`, `ANCConcepts`,
  `ANCDataElements`, `ANCContactDataElements`; each rule a definition named after its output, the DAK
  condition kept as a comment above it.
- `input/resources/plandefinition/plandefinition-ANCDT01.json`: `library`
  `http://smart.who.int/anc/Library/ANCDT01`; one top action titled `ANC.DT.01 Danger signs`, child
  actions `id` "1", "2", … each with an `applicability` condition in `text/cql-identifier` and a
  `documentation` entry of type `citation`; no `relatedArtifact`, no `meta.profile`.
