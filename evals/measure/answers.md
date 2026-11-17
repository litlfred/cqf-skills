# measure answers

**ME-01.** IP, Denominator and Numerator; not removed as an exception — exceptions only remove subjects not in the numerator. *Fail if* it removes the patient from the denominator.

**ME-02.** 40 / (80 − 10 − 5) = 40/65 ≈ 0.615. *Fail if* it uses 80 or 70 as the denominator.

**ME-03.** `List<Encounter>`; the `cqfm-populationBasis` extension on `Measure.group` with value `Encounter`. *Fail if* Boolean.

**ME-04.** initial-population, measure-population, measure-observation (optional measure-population-exclusion); `cqfm-aggregateMethod` extension on the observation; the observation names a CQL function over one basis item.

**ME-05.** Nothing: a `summary` report carries no evaluatedResource (clinical-reasoning 4.13.0). Run the report type `subject` for that patient: an `individual` report lists every resource the retrieves returned; if the expected resource is missing there, the retrieve (profile, code, value set, system URI) is at fault, not the logic. *Fail if* it reads the empty list as "the retrieve found nothing".

**ME-06.** A top-level `stratifier.criteria` is a criteria stratifier and must return the basis type (Boolean); returning a gender gives status `error`, counts 0 and an OperationOutcome. Put the expression in `stratifier.component[].criteria`. *Fail if* it blames the population logic.

**ME-07.** `MeasureReport.status` is `error` with a contained OperationOutcome; a basis mismatch does not throw.

**TK-01.** Graded by `grade_measure.py Measure-screening.json`: scoring `proportion`, the four populations with measure-population codes and named criteria, `cqfm-populationBasis` `boolean`, the library canonical, the sex stratifier as a component, improvementNotation `increase`.
