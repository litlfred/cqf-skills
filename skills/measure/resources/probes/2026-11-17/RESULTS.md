# Probe results, 2026-11-17

Run with clinical-reasoning **4.13.0** (`org.opencds.cqf.fhir:cqf-fhir-cr`, which brings the CQL
translator and engine and HAPI FHIR 8.12.0), through `scripts/evaluate/run.sh`, on the project in this
folder. `make_probe.py` writes it: `input/resources/` holds `Library/MeasureProbe` (CQL base64 in
`Library.content`; FHIRHelpers 4.0.1 comes from the translator) and the Measures, `input/tests/` six
patients and five encounters. All data is synthetic. Every run's period is
`2025-01-01T00:00:00Z` to `2025-12-31T23:59:59Z` unless noted.

Population membership in the boolean measures is fixed by patient id, so each population boundary is one
patient:

| patient | sex | Denominator Exclusions | Denominator Exceptions | Numerator | Numerator Exclusions |
|---|---|---|---|---|---|
| p1 | female | | | yes | |
| p2 | male | | | yes | yes |
| p3 | female | | yes | yes | |
| p4 | male | | yes | | |
| p5 | female | yes | | yes | |
| p6 | other | | | | |

Encounters (all `IMP`): e1 p1 finished, 2 days; e2 p2 finished, 4 days; e3 p3 in-progress, 1 day;
e4 p4 finished, 10 days (the encounter exclusion); e5 p1 finished, in 2024 (outside the period).

## 1. `Measure/proportion` (boolean basis), report type `population`

`MeasureReport` type `summary`, status `complete`.

| population | count | members (from `subject-list`) |
|---|---|---|
| initial-population | 6 | all |
| denominator | 6 | all |
| denominator-exclusion | 1 | p5 |
| denominator-exception | **1** | **p4 only** |
| numerator | **3** | **p1, p2, p3** |
| numerator-exclusion | 1 | p2 |

`measureScore` **0.5**.

- **p3 meets the numerator and an exception and is counted in the numerator, not as an exception.**
  Exceptions remove only subjects not in the numerator.
- **p5 meets the numerator expression but is denominator-excluded, and is not counted in the
  numerator.** Exclusions are applied before the numerator is counted.
- **The numerator count includes the numerator-excluded p2**; the score subtracts it:
  (3 − 1) / (6 − 1 − 1) = 0.5.
- Stratifier `by-sex` written as a **`component`** with criteria `Sex`: three strata, by `value.text`
  `female` (IP 3, DenEx 1, Numer 2, score 0.667), `male` (IP 2, DenExcep 1, Numer 1, NumerEx 1,
  score 0.5) and `other` (IP 1, score 0.0). Each stratum is scored on its own.
- `supplementalData` `Sex` (usage `supplemental-data`) is reported as contained `Observation`s, one
  per value, referenced from the report by the R5 cross-version extension
  `http://hl7.org/fhir/5.0/StructureDefinition/extension-MeasureReport.supplementalData`.
- `improvementNotation` is copied to the report. `period` is the requested period.
- `evaluatedResource` is **empty** in a `summary` report.

## 2. Report types `subject` and `subject-list`

- `subject` with `Patient/p3`: type **`individual`**, IP 1, Denom 1, Numer 1, DenExcep **0**,
  `measureScore` 1.0, `evaluatedResource` `Patient/p3`.
- `subject` with `Patient/p1` on `Measure/encounter-basis`: IP 1, Denom 1, Numer 1;
  `evaluatedResource` lists **`Encounter/e5` and `Encounter/e1`**: every resource the retrieves
  returned, including e5, which is outside the period and in no population.
- `subject-list`: each `group.population` has `subjectResults` referencing a contained `List` of
  `Patient/<id>`; the stratum populations get their own Lists.

## 3. `Measure/criteria-stratifier`: a top-level stratifier `criteria` returning a value

The same `Sex` stratifier as `stratifier.criteria` instead of a `component`. The report has status
**`error`**, every count **0**, and a contained `OperationOutcome` with one issue per patient:

> criteria-based stratifier is invalid for expression: [Sex] due to mismatch between population basis:
> [boolean] and result types: [AdministrativeGender] …

In 4.13.0 a stratifier with `criteria` is a *criteria* stratifier and must return the population basis
type; a stratifier with only `component`s is a *value* stratifier (`R4MeasureDefBuilder.getStratifierType`,
`PopulationBasisValidator`). A stratifier with both is refused.

## 4. `Measure/encounter-basis` (`cqfm-populationBasis` = `Encounter`)

IP 4 (e1–e4; e5 is outside the period), Denom 4, DenEx 1 (e4), Numer **2** (e1, e2; e4 is finished
but excluded, e3 is in progress). `measureScore` 2/3 = 0.667. Counts are of encounters, not patients.

## 5. `Measure/continuous` (continuous-variable, Encounter basis)

IP 4, measure-population 4, measure-population-exclusion 1 (e4), measure-observation **3**.
`cqfm-aggregateMethod` `median` over `"Length Of Stay Days"` of e1, e2, e3 (2, 4, 1 days) gives
`measureScore` **2.0**: the excluded e4 (10 days) is not observed.

## 6. `Measure/cohort`, `Measure/text-cql`

- Cohort with `"IP Without p6"`: IP 5, no `measureScore`.
- The same population with `criteria.language` **`text/cql`** (the R4 code) instead of
  `text/cql-identifier`: IP 5. A bare definition name under `text/cql` is evaluated as a named
  expression.

## 7. `Measure/wrong-basis`: boolean basis, population returns `List<Encounter>`

Status **`error`**, IP **0**, and an `OperationOutcome` issue for each patient with encounters
(p1–p4):

> group expression criteria results for expression: [Wrong Type For Boolean] and scoring: [COHORT] must
> fall within accepted types for population basis: [boolean] …

Patients whose list is empty (p5, p6) raise no issue. The operation does not throw; the error is in
the report.

## 8. Reversed period

`periodStart` 2025-12-31, `periodEnd` 2025-01-01: the operation **throws** `InvalidInterval`:
"Invalid Period - the ending boundary … must be greater than or equal to the starting boundary".

## 9. `$data-requirements` on `Measure/proportion`

Returns a `Library` of type **`module-definition`** with `relatedArtifact` `depends-on`
`FHIR-ModelInfo|4.0.1` and `Library/FHIRHelpers|4.0.1`, a `parameter` (`use` `out`) for each
definition (`boolean` for the population criteria; no type for `Sex`), and `dataRequirement`s of type
`Patient`, each with a `cqfm-fhirQueryPattern` extension (`Patient?_id={{context.patientId}}`).
