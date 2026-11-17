# immunization-cds answers

**IM-01.** The retrieve returns every status: `not-done` and `entered-in-error` records are counted. Filter `I.status = 'completed'`. *Fail if* it blames the code or value set.

**IM-02.** It counts as a completed dose but has no date, so an interval rule cannot use it; unless the logic decides, it can make the child look complete (or block the interval). Filter dated doses (`occurrence is FHIR.dateTime`) for intervals and decide explicitly how undated doses count.

**IM-03.** No: `doseNumber[x]` is `positiveInt` or `string` in R4. Test the type or count valid doses instead.

**IM-04.** The engine's MedicationRequest has no `category`, which the profile's `immunization` slice requires (and its status is `active`). Add `dynamicValue`s for `category` (`cpg-activity-type-cs#recommend-immunization`) and `status` `'draft'`.

**IM-05.** clinical-reasoning sets `forecastStatus` to `due` when the content does not; set it with a `dynamicValue` from the logic (`complete`, `immune`, `contraindicated`, …). *Fail if* it blames the CQL alone.

**IM-06.** `recommendation.dateCriterion`, with `code` LOINC `30980-7` (date vaccine due) and `value`; `30981-5` earliest, `59777-3` latest, `59778-1` overdue.
