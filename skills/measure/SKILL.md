---
name: measure
description: Authors, reviews and evaluates FHIR R4 Measure resources and their MeasureReports — scoring types (proportion, ratio, continuous-variable, cohort), population criteria and how populations nest, population basis, stratifiers, supplemental data, improvement notation, and the $evaluate-measure, $data-requirements, $collect-data and $submit-data operations — following the HL7 Quality Measure IG (hl7.fhir.us.cqfmeasures). Use when writing or debugging a Measure's group/population/stratifier elements, linking a Measure to its CQL Library, reading population counts or measureScore in a MeasureReport, or explaining why a subject landed in the wrong population. Not for the CQL logic itself (cql, cms-qmd), test-case zips (madie) or packaging ($package, crmi).
license: Apache-2.0
---

# FHIR Measure

> **litlfred fork.** Each engine behaviour below is checked by running clinical-reasoning 4.13.0
> (HAPI FHIR) on a synthetic probe project, recorded in
> [resources/probes/2026-11-17/RESULTS.md](resources/probes/2026-11-17/RESULTS.md) (cited as *P§n*).
> Claims about the resources themselves come from FHIR R4 and the Quality Measure IG.

Targets **FHIR R4 (4.0.1)** `Measure`, `MeasureReport` and the Measure operations
(<https://hl7.org/fhir/R4/measure.html>), and the **Quality Measure IG**
(<https://hl7.org/fhir/us/cqfmeasures/>) **5.0.0** (`hl7.fhir.us.cqfmeasures`, the `latest` tag on
packages.fhir.org; package sha256 `f2d83218…a4cb37`), in which `cqfm-populationBasis`,
`cqfm-aggregateMethod` and `cqfm-criteriaReference` are active. If the project's `sushi-config.yaml`
depends on another version, say which one you answered for.

Related skills: `cql` and `cms-qmd` for the expressions a population names, `cql-ig` for the
`Library` that carries them, `crmi` for `$package` and artifact lifecycle, `madie` for test cases.

## Workflow

1. Pick the **scoring** (`Measure.scoring`, code system
   `http://terminology.hl7.org/CodeSystem/measure-scoring`). It fixes which populations are allowed
   (table below).
2. Decide the **population basis**: `boolean` (one result per subject, usually Patient) or a resource
   type such as `Encounter` (one result per resource). In R4 it is the
   `cqfm-populationBasis` extension on `Measure.group`; every population expression in the group must
   return that type (`Boolean`, or `List<Encounter>` for `Encounter`); counts are then of
   encounters, not patients (*P§4*).
3. Point `Measure.library` at exactly one primary Library canonical, and name each population's
   expression in it (`criteria.language` `text/cql-identifier`, or `text/cql`, the R4 code, which
   clinical-reasoning also evaluates as a named expression (*P§6*); `criteria.expression` the CQL
   definition name).
4. Declare the `"Measurement Period"` parameter in the CQL as `Interval<DateTime>`; engines bind
   `periodStart`/`periodEnd` of `$evaluate-measure` to it.
5. Add stratifiers and supplemental data, then `improvementNotation`.
6. Evaluate against synthetic test patients and read the MeasureReport (section below). To run
   `$evaluate-measure` locally: `scripts/evaluate/run.sh <project> evaluate <Measure id> <start> <end>
   population|subject-list|subject [Patient/<id>]` on a folder in IG layout (Java 17+, Maven; the
   first run downloads clinical-reasoning 4.13.0 into `scripts/evaluate/lib/`).

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
- Exclusions are removed before the numerator is counted: a denominator-excluded subject that meets
  the numerator expression is not counted in the numerator (*P§1*).
- **Exceptions are removed only for subjects not already in the numerator.** A subject who meets the
  numerator stays in it even if it also meets an exception, and is not counted as an exception (*P§1*).
- The numerator **count includes** numerator-excluded subjects; the score subtracts them:
  `(Numerator − Numerator Exclusion) / (Denominator − Denominator Exclusion − Denominator Exception)`
  (*P§1*: 3, 1, 6, 1, 1 → 0.5).

When a count looks wrong, check membership in this order: IP → Denom → DenEx → Numer → NumerEx →
DenExcep. Most "wrong population" reports are a criteria expression that does not restrict itself to
the population above it (write `"Denominator": "Initial Population"` and build on it).

### Continuous variable

`measure-observation` names a CQL **function** taking one population-basis item (for example
`define function "Length of Stay"(Encounter E): duration in days of E.period`) and the
`cqfm-aggregateMethod` extension on that population says how to aggregate: `sum`, `average`,
`median`, `minimum`, `maximum` or `count` (value set `measure-aggregate-method`, preferred binding;
clinical-reasoning 4.13.0 accepts exactly these six, `ContinuousVariableObservationAggregateMethod`). `cqfm-criteriaReference` on the observation names the population id
it observes. Measure-population exclusions are not observed: four encounters, one excluded, give three
observations and the median of those (*P§5*).

## Stratifiers and supplemental data

- **A value stratifier (by sex, age group, payer) goes in `stratifier.component[].criteria`, not in
  `stratifier.criteria`.** clinical-reasoning 4.13.0 treats a top-level `criteria` as a *criteria*
  stratifier that must return the population basis type (Boolean for a boolean basis); one returning a
  value gives a report with status `error`, every count 0 and an OperationOutcome per subject. A
  stratifier with both is refused (*P§3*). Strata appear under `MeasureReport.group.stratifier.stratum`
  with `component[].value`, each scored on its own (*P§1*).
- `Measure.supplementalData` names expressions reported alongside, with `usage`
  `supplemental-data` or `risk-adjustment-factor`. Sex, race, ethnicity and payer are the usual SDEs
  in US measures. clinical-reasoning reports each as contained `Observation`s, referenced from the
  report by the R5 cross-version extension `extension-MeasureReport.supplementalData` (*P§1*).
- `improvementNotation` is `increase` or `decrease` (`measure-improvement-notation`); without it a
  reader cannot tell whether a higher score is better.

## Operations

| operation | on | returns |
|---|---|---|
| `$evaluate-measure` | `Measure/[id]` | a `MeasureReport`; parameters `periodStart`, `periodEnd`, `reportType` (`subject`, `subject-list`, `population`), `subject`, `practitioner`, `lastReceivedOn` |
| `$data-requirements` | `Measure/[id]` | a `Library` of type `module-definition` listing `dataRequirement`s, `depends-on` artifacts and an `out` parameter per definition (*P§9*). clinical-reasoning 4.13.0 marks each query with `cqfm-fhirQueryPattern`; the Quality Measure IG 5.0.0 examples use `http://hl7.org/fhir/StructureDefinition/cqf-fhirQueryPattern`, so a validator against 5.0.0 may not know the engine's URL |
| `$collect-data` | `Measure/[id]` | the data an evaluation would use, as a MeasureReport of type `data-collection` plus resources |
| `$submit-data` | `Measure/[id]` | accepts a `data-collection` report and its resources |

## Reading a MeasureReport

- `type`: `individual` (report type `subject`), `subject-list` (with `subjectResults` referencing a
  contained `List` per population and per stratum population), `summary` (report type `population`),
  or `data-collection` (*P§1, §2*).
- `group.population.count` per population code; `group.measureScore` for proportion, ratio and
  continuous-variable.
- `evaluatedResource` is filled only in an `individual` report, and lists **every resource the
  retrieves returned**, in a population or not (an encounter outside the period included); a `summary`
  report has none (*P§1, §2*). For a subject you expected in the numerator, run `subject` for that
  subject: if the resource you expected is missing from `evaluatedResource`, the retrieve did not find
  it (wrong profile, code or value set), and the logic is not the problem.
- **A type mismatch does not throw.** A population that returns the wrong type for the basis, or a
  wrong stratifier, gives status `error`, counts of 0 and a contained OperationOutcome; read
  `MeasureReport.status` before the counts (*P§3, §7*). A reversed period does throw (*P§8*).

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

## Files

| file | what |
|---|---|
| [scripts/evaluate/run.sh](scripts/evaluate/run.sh) | `$evaluate-measure` and `$data-requirements` with clinical-reasoning 4.13.0 (Java 17+, Maven) |
| [resources/probes/2026-11-17/RESULTS.md](resources/probes/2026-11-17/RESULTS.md) | the probe project (`make_probe.py`) and what each run returned |

## Checklist before review

- [ ] Every population allowed by the scoring, none extra; every `criteria.expression` exists in the
      primary Library and returns the population-basis type.
- [ ] One primary Library; its version pinned in the canonical.
- [ ] `"Measurement Period"` declared in CQL and used by every time-bounded criterion.
- [ ] Exceptions and exclusions used for what they mean (exclusion: never eligible; exception: eligible
      but a valid reason not to be in the numerator).
- [ ] `improvementNotation` set; SDEs named; value stratifiers written as `component`s.
- [ ] `MeasureReport.status` is `complete` before any count is read.
- [ ] Test patients are synthetic and cover each population boundary.
