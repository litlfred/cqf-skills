# Probe results, 2026-11-17

Three sources:

- **FHIR R4** `hl7.fhir.r4.core` 4.0.1 (package sha256
  `ebd7731df7d36b5b7d39d5fb6c9d77b44bb7fe5742f1a2e87f164738c3289d44`): the Immunization,
  ImmunizationEvaluation and ImmunizationRecommendation definitions and their code systems.
- **CPG 2.0.0** `hl7.fhir.uv.cpg` (package sha256
  `e87e671224571ed545d21a982683e7bf77ec8ccd0877b4addd4a11024852bcc4`): `cpg-immunizationactivity` and
  `cpg-immunizationrequest`.
- **clinical-reasoning 4.13.0** run through `scripts/apply/run.sh` on the project in this folder
  (`make_probe.py`; synthetic; vaccine codes illustrative). `output/` holds what each run printed. The
  WHO Immunizations IG (`WorldHealthOrganization/smart-immunizations` at
  `bd7fa726706efc92d972d0dcebba9505f386b078`) was read for how it emits recommendations.

## 1. The resources (R4)

- **Immunization**: `status` 1..1, required binding `completed` | `entered-in-error` | `not-done`;
  `vaccineCode` 1..1; `occurrence[x]` 1..1, **`dateTime` or `string`**; `protocolApplied` 0..*, each with
  `doseNumber[x]` 1..1 (**`positiveInt` or `string`**), `seriesDoses[x]`, `series`, `targetDisease`;
  `isSubpotent`, `primarySource`.
- **ImmunizationEvaluation**: `status` (`completed` | `entered-in-error`), `patient`, `targetDisease`,
  `immunizationEvent` and `doseStatus` 1..1; `doseStatus` codes `valid`, `notvalid`.
- **ImmunizationRecommendation**: `patient`, `date` 1..1; `recommendation` 1..*, each with
  `forecastStatus` 1..1 (codes `due`, `overdue`, `immune`, `contraindicated`, `complete` in
  `http://terminology.hl7.org/CodeSystem/immunization-recommendation-status`), `vaccineCode` 0..*,
  `targetDisease` 0..1 (**imr-1: one of `vaccineCode` or `targetDisease` SHALL be present**),
  `dateCriterion` (`code` from LOINC `30981-5`, `30980-7`, `59777-3`, `59778-1`, and `value`),
  `doseNumber[x]`, `seriesDoses[x]`, `series`, `supportingImmunization`, `contraindicatedVaccineCode`.

## 2. CPG 2.0.0

- `cpg-immunizationactivity` (ActivityDefinition): `kind` fixed **`MedicationRequest`**, `intent` fixed
  `proposal`, `profile` 1..1, `doNotPerform` 1..1, `code` pattern `cpg-activity-type-cs#recommend-immunization`.
- `cpg-immunizationrequest` (MedicationRequest): `category` 1..*, slice `immunization` 1..1 with pattern
  `cpg-activity-type-cs#recommend-immunization`; `cpg-rationale` and `cpg-rating` extensions.
- The WHO IMMZ IG emits "due" as such an activity: `IMMZD2DTMR`, `InstanceOf cpg-immunizationactivity`,
  `kind #MedicationRequest`, `intent #proposal`, `productCodeableConcept IMMZ.Z#DE0`, and the vaccine
  set per decision table by a `dynamicValue` on `medication`; `status` set to `'draft'` by dynamicValue.

## 3. Counting doses in CQL (`Library/ImmzProbe`, `child-1`)

`child-1` has four Immunizations with the same vaccine code: `i1` completed, dated, dose 1; `i2`
not-done; `i3` entered-in-error; `i4` completed with `occurrenceString` and `doseNumberString` `first`.

| definition | result |
|---|---|
| `[Immunization: "MCV"]` | **all four**, `not-done` and `entered-in-error` included |
| `… where I.status = 'completed'` | `i1`, `i4` |
| `Count(completed)` | **2** |
| completed `where I.occurrence is FHIR.dateTime` | `i1` only (count 1) |
| `Max(… return I.occurrence as FHIR.dateTime)` | `2025-03-10T10:00:00Z` |
| `I.protocolApplied[0].doseNumber` | `1` (positiveInt) and `'first'` (string) |
| `"Due For MCV"` (completed count < 2 and 4 weeks since the last dated dose) | **false**: the undated dose counts |

`child-2` (one completed dated dose `i5`): count 1, `"Due For MCV"` **true**.

## 4. `$apply`

- `ActivityDefinition/recommend-mcv` (claims `cpg-immunizationactivity`; `profile`
  `cpg-immunizationrequest`): a **MedicationRequest** with `meta.profile` `cpg-immunizationrequest`,
  `status` **`active`**, `intent` `proposal`, `doNotPerform` false, `medicationCodeableConcept` = the
  `productCodeableConcept`, `subject`, `instantiatesCanonical` — and **no `category`**, which
  `cpg-immunizationrequest` requires. The ActivityDefinition's `code` is not copied.
- `ActivityDefinition/recommend-mcv-fixed`, the same with the two `dynamicValue`s of SKILL.md's example
  (`status` `'draft'`; `category` a list of one Concept `cpg-activity-type-cs#recommend-immunization`):
  `status` **`draft`**, `category` **`[recommend-immunization]`** — the profile's required slice is filled.
- `PlanDefinition/mcv-due` for `child-2`: a CarePlan whose RequestGroup action `Client is due for MCV`
  references the contained MedicationRequest (same shape: `active`, no `category`). For `child-1` the
  action is absent.
- `kind` **`ImmunizationRecommendation`**:
  - without `product[x]` (`forecast-mcv`): **throws** `Missing required ActivityDefinition.product property
    for ImmunizationRecommendation`;
  - with `productCodeableConcept` (`forecast-mcv-no-status`): an ImmunizationRecommendation with
    `patient`, `date` = now, one `recommendation` with `vaccineCode` = the product and **`forecastStatus`
    `due` set by the engine** although nothing asked for it;
  - with a `dynamicValue` on `recommendation.forecastStatus` (`forecast-mcv-product`): the value given.
