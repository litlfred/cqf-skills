---
name: measure
description: Authors, reviews and evaluates FHIR R4 Measure resources and their MeasureReports — scoring types (proportion, ratio, continuous-variable, cohort), population criteria and how populations nest, population basis, stratifiers, supplemental data, improvement notation, and the $evaluate-measure, $data-requirements, $collect-data and $submit-data operations — following the HL7 Quality Measure IG (hl7.fhir.us.cqfmeasures). Use when writing or debugging a Measure's group/population/stratifier elements, linking a Measure to its CQL Library, reading population counts or measureScore in a MeasureReport, or explaining why a subject landed in the wrong population. Not for the CQL logic itself (cql, cms-qmd), test-case zips (madie) or packaging ($package, crmi).
license: Apache-2.0
---

# FHIR Measure

> **Status: draft (litlfred fork).** Written from the FHIR R4 Measure and MeasureReport resources and
> the Quality Measure IG; not yet checked by running an engine, as the upstream skills are. Each
> engine-behaviour claim below says so where it is a specification claim only.

Targets **FHIR R4 (4.0.1)** `Measure`, `MeasureReport` and the Measure operations
(<https://hl7.org/fhir/R4/measure.html>), and the **Quality Measure IG**
(<https://hl7.org/fhir/us/cqfmeasures/>). Pin the IG version the project's `sushi-config.yaml` or
`ig.ini` depends on and say which one you answered for.

Related skills: `cql` and `cms-qmd` for the expressions a population names, `cql-ig` for the
`Library` that carries them, `crmi` for `$package` and artifact lifecycle, `madie` for test cases.

## Workflow

1. Pick the **scoring** (`Measure.scoring`, code system
   `http://terminology.hl7.org/CodeSystem/measure-scoring`). It fixes which populations are allowed
   (table below).
2. Decide the **population basis**: `boolean` (one result per subject, usually Patient) or a resource
   type such as `Encounter` (one result per resource). In R4 it is the
   `cqfm-populationBasis` extension on `Measure.group`; every population expression in the group must
   return that type (`Boolean`, or `List<Encounter>` for `Encounter`).
3. Point `Measure.library` at exactly one primary Library canonical, and name each population's
   expression in it (`criteria.language` `text/cql-identifier` — or `text/cql` on strict R4 —
   `criteria.expression` the CQL definition name).
4. Declare the `"Measurement Period"` parameter in the CQL as `Interval<DateTime>`; engines bind
   `periodStart`/`periodEnd` of `$evaluate-measure` to it.
5. Add stratifiers and supplemental data, then `improvementNotation`.
6. Evaluate against synthetic test patients and read the MeasureReport (section below).

## Populations by scoring

Codes are from `http://terminology.hl7.org/CodeSystem/measure-population`.

| scoring | required | optional |
|---|---|---|
| `proportion` | `initial-population`, `denominator`, `numerator` | `denominator-exclusion`, `denominator-exception`, `numerator-exclusion` |
| `ratio` | `initial-population` (one, or two to separate numerator and denominator), `denominator`, `numerator` | `denominator-exclusion`, `numerator-exclusion`, `measure-observation` |
| `continuous-variable` | `initial-population`, `measure-population`, `measure-observation` | `measure-population-exclusion` |
| `cohort` | `initial-population` | — |

### How proportion populations nest

- Denominator ⊆ Initial Population; Numerator ⊆ Denominator.
- Exclusions are removed before the numerator is evaluated against the denominator.
- **Exceptions are removed only for subjects not already in the numerator.** A subject who meets the
  numerator stays in it even if it also meets an exception.
- Score: `(Numerator − Numerator Exclusion) / (Denominator − Denominator Exclusion − Denominator Exception)`.

When a count looks wrong, check membership in this order: IP → Denom → DenEx → Numer → NumerEx →
DenExcep. Most "wrong population" reports are a criteria expression that does not restrict itself to
the population above it (write `"Denominator": "Initial Population"` and build on it).

### Continuous variable

`measure-observation` names a CQL **function** taking one population-basis item (for example
`define function "Length of Stay"(Encounter E): duration in days of E.period`) and the
`cqfm-aggregateMethod` extension on that population says how to aggregate (`sum`, `average`,
`median`, `min`, `max`, `count`). `criteriaReference` on the observation points at the population
id it observes.

## Stratifiers and supplemental data

- `group.stratifier.criteria` names an expression returning the stratum value per subject (or a
  `component` list for several axes). Results appear under `MeasureReport.group.stratifier.stratum`.
- `Measure.supplementalData` names expressions reported alongside, with `usage`
  `supplemental-data` or `risk-adjustment-factor`. Sex, race, ethnicity and payer are the usual SDEs
  in US measures.
- `improvementNotation` is `increase` or `decrease` (`measure-improvement-notation`); without it a
  reader cannot tell whether a higher score is better.

## Operations

| operation | on | returns |
|---|---|---|
| `$evaluate-measure` | `Measure/[id]` | a `MeasureReport`; parameters `periodStart`, `periodEnd`, `reportType` (`subject`, `subject-list`, `population`), `subject`, `practitioner`, `lastReceivedOn` |
| `$data-requirements` | `Measure/[id]` | a `Library` of type `module-definition` listing `dataRequirement`s and dependencies |
| `$collect-data` | `Measure/[id]` | the data an evaluation would use, as a MeasureReport of type `data-collection` plus resources |
| `$submit-data` | `Measure/[id]` | accepts a `data-collection` report and its resources |

## Reading a MeasureReport

- `type`: `individual` (one subject), `subject-list` (with `subjectResults` List references per
  population), `summary`, or `data-collection`.
- `group.population.count` per population code; `group.measureScore` for proportion, ratio and
  continuous-variable.
- `evaluatedResource` lists what the engine read; an empty list for a subject you expected in the
  numerator usually means the retrieve found nothing (wrong profile, code or date range), not that
  the logic is wrong.

## Example: a proportion group (FHIR JSON, synthetic)

```json
{
  "resourceType": "Measure",
  "url": "http://example.org/fhir/Measure/ExampleScreening",
  "version": "0.1.0",
  "status": "draft",
  "scoring": {"coding": [{"system": "http://terminology.hl7.org/CodeSystem/measure-scoring", "code": "proportion"}]},
  "improvementNotation": {"coding": [{"system": "http://terminology.hl7.org/CodeSystem/measure-improvement-notation", "code": "increase"}]},
  "library": ["http://example.org/fhir/Library/ExampleScreening|0.1.0"],
  "group": [{
    "extension": [{"url": "http://hl7.org/fhir/us/cqfmeasures/StructureDefinition/cqfm-populationBasis", "valueCode": "boolean"}],
    "population": [
      {"id": "ip", "code": {"coding": [{"system": "http://terminology.hl7.org/CodeSystem/measure-population", "code": "initial-population"}]}, "criteria": {"language": "text/cql-identifier", "expression": "Initial Population"}},
      {"id": "denom", "code": {"coding": [{"system": "http://terminology.hl7.org/CodeSystem/measure-population", "code": "denominator"}]}, "criteria": {"language": "text/cql-identifier", "expression": "Denominator"}},
      {"id": "denex", "code": {"coding": [{"system": "http://terminology.hl7.org/CodeSystem/measure-population", "code": "denominator-exclusion"}]}, "criteria": {"language": "text/cql-identifier", "expression": "Denominator Exclusions"}},
      {"id": "numer", "code": {"coding": [{"system": "http://terminology.hl7.org/CodeSystem/measure-population", "code": "numerator"}]}, "criteria": {"language": "text/cql-identifier", "expression": "Numerator"}}
    ]
  }]
}
```

## Checklist before review

- [ ] Every population allowed by the scoring, none extra; every `criteria.expression` exists in the
      primary Library and returns the population-basis type.
- [ ] One primary Library; its version pinned in the canonical.
- [ ] `"Measurement Period"` declared in CQL and used by every time-bounded criterion.
- [ ] Exceptions and exclusions used for what they mean (exclusion: never eligible; exception: eligible
      but a valid reason not to be in the numerator).
- [ ] `improvementNotation` set; stratifiers and SDEs named.
- [ ] Test patients are synthetic and cover each population boundary.
