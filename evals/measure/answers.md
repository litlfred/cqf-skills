# measure answers

**ME-01.** IP, Denominator and Numerator; not removed as an exception — exceptions only remove subjects not in the numerator. *Fail if* it removes the patient from the denominator.

**ME-02.** 40 / (80 − 10 − 5) = 40/65 ≈ 0.615. *Fail if* it uses 80 or 70 as the denominator.

**ME-03.** `List<Encounter>`; the `cqfm-populationBasis` extension on `Measure.group` with value `Encounter`. *Fail if* Boolean.

**ME-04.** initial-population, measure-population, measure-observation (optional measure-population-exclusion); `cqfm-aggregateMethod` extension on the observation; the observation names a CQL function over one basis item.

**ME-05.** The retrieve, not the logic: profile, code/value set expansion, code system URI, date range against Measurement Period.
