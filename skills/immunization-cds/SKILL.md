---
name: immunization-cds
description: Writes and reviews immunization decision support in CQL and FHIR R4 — reading a client's history from Immunization (status, occurrence[x], protocolApplied doseNumber[x]), expressing "due", "not due", "complete" and contraindications, and emitting the result as a CPG 2.0.0 immunization recommendation (cpg-immunizationactivity, a MedicationRequest proposal) or an ImmunizationRecommendation with forecastStatus and dateCriterion, as WHO's SMART Immunizations IG does and as clinical-reasoning 4.13.0 $apply produces them. Use when counting doses or intervals in CQL, deciding whether a vaccine is due, writing the ActivityDefinition or PlanDefinition that proposes a dose, or reading an ImmunizationRecommendation or ImmunizationEvaluation. Not for general decision-table conversion (smart-dak), PlanDefinition $apply in general (plan-definition) or CDS Hooks cards (cds-hooks).
license: Apache-2.0
---

# Immunization decision support

> **litlfred fork.** Resource rules are from FHIR R4 4.0.1 and CPG 2.0.0 (the packages); engine
> behaviour from running clinical-reasoning 4.13.0 (HAPI FHIR) on a synthetic probe; the WHO pattern
> from `WorldHealthOrganization/smart-immunizations` at a pinned commit. All are recorded in
> [resources/probes/2026-11-17/RESULTS.md](resources/probes/2026-11-17/RESULTS.md), cited as *P§n*.

Related skills: `smart-dak` for turning the DAK's decision and scheduling tables into CQL and
PlanDefinitions, `plan-definition` for `$apply`, `cpg` for the profiles, `terminology` for vaccine
value sets, `cds-hooks` for delivering the result as cards.

## Reading the history: the pitfalls

1. **Filter on status.** A retrieve by vaccine code returns `completed`, `not-done` and
   `entered-in-error` alike (*P§3*). Count only `I.status = 'completed'`; read `not-done` with its
   `statusReason` (refusal, contraindication, shortage) as information, never as a dose.
2. **`occurrence[x]` can be a string** ("at the 9-month visit"). An undated completed dose still counts
   as a dose, but it has no date for interval rules: in the probe it made a child with one dated dose
   "not due" (*P§3*). Decide, per rule, whether undated doses count, and say so in the logic:

   ```cql
   define "Completed MCV": [Immunization: "MCV"] I where I.status = 'completed'
   define "Dated Completed MCV": "Completed MCV" I where I.occurrence is FHIR.dateTime
   define "Latest MCV Date": Max("Dated Completed MCV" I return (I.occurrence as FHIR.dateTime))
   ```
3. **`protocolApplied.doseNumber[x]` is `positiveInt` or `string`** (*P§1, §3*): do not compare it as an
   integer without testing its type. Prefer counting valid doses over trusting recorded dose numbers.
4. `isSubpotent = true` doses do not count; an ImmunizationEvaluation with `doseStatus` `notvalid`
   says the same for a given dose (*P§1*).
5. Compare dates at the precision of the rule (`date from …`), and anchor "today" in a parameter (WHO
   IMMZ libraries declare `parameter Today Date default Today()`), so tests are reproducible.

## Emitting the result

Two shapes, for two purposes:

| shape | when | what |
|---|---|---|
| **CPG immunization recommendation** (`cpg-immunizationactivity` → MedicationRequest `proposal`) | a PlanDefinition proposes "give this dose now" to a health worker; WHO IMMZ does this (*P§2*) | ActivityDefinition: `kind` `MedicationRequest`, `intent` `proposal`, `doNotPerform` false, `profile` `cpg-immunizationrequest`, `code` `cpg-activity-type-cs#recommend-immunization`, the vaccine in `productCodeableConcept` |
| **ImmunizationRecommendation** | a forecast over a whole schedule: due, overdue, complete, immune or contraindicated, with dates | `patient`, `date`, and per vaccine or disease a `recommendation` with `forecastStatus` (required), `vaccineCode` or `targetDisease` (one of them, imr-1), `dateCriterion` (LOINC `30980-7` due date, `30981-5` earliest, `59777-3` latest, `59778-1` overdue), `doseNumber[x]`, `supportingImmunization` |

### What clinical-reasoning 4.13.0 `$apply` produces (*P§4*)

- From a `cpg-immunizationactivity`: a MedicationRequest claiming `cpg-immunizationrequest`, with
  `status` **`active`** and **no `category`** — so it does not conform to the profile it claims. Add a
  `dynamicValue` for `category` (the `recommend-immunization` coding) and one setting `status` to
  `'draft'`, as WHO IMMZ does for status. The example below, run, gives `status` `draft` and the
  required `category` (*P§4*).
- From `kind` `ImmunizationRecommendation`: `product[x]` is required (without it `$apply` throws), and
  the engine sets `forecastStatus` **`due`** when nothing else does. Always set `forecastStatus` with a
  `dynamicValue` from the logic, or a "complete" schedule will read as "due".

```json
{
  "resourceType": "ActivityDefinition",
  "id": "recommend-mcv",
  "url": "http://example.org/fhir/ActivityDefinition/recommend-mcv",
  "version": "1.0.0",
  "status": "draft",
  "meta": {"profile": ["http://hl7.org/fhir/uv/cpg/StructureDefinition/cpg-immunizationactivity"]},
  "kind": "MedicationRequest",
  "intent": "proposal",
  "doNotPerform": false,
  "profile": "http://hl7.org/fhir/uv/cpg/StructureDefinition/cpg-immunizationrequest",
  "code": {"coding": [{"system": "http://hl7.org/fhir/uv/cpg/CodeSystem/cpg-activity-type-cs", "code": "recommend-immunization"}]},
  "productCodeableConcept": {"coding": [{"system": "http://example.org/fhir/CodeSystem/illustrative-vaccines", "code": "MCV"}]},
  "dynamicValue": [
    {"path": "status", "expression": {"language": "text/cql-expression", "expression": "'draft'"}},
    {"path": "category", "expression": {"language": "text/cql-expression",
      "expression": "{ Concept { codes: { Code { code: 'recommend-immunization', system: 'http://hl7.org/fhir/uv/cpg/CodeSystem/cpg-activity-type-cs' } } } }"}}
  ]
}
```

## The WHO SMART Immunizations pattern

IMMZ decision tables `IMMZ.D2.DT.<vaccine>…` (is the client due?), schedules `IMMZ.D18.S…` and
contraindication tables `IMMZ.D5.DT…` each become a Library `…Logic` and a `cpg-recommendationdefinition`
PlanDefinition (see `smart-dak`). A "due" output's action points at `IMMZD2DTMR`, a
`cpg-immunizationactivity`, and a `dynamicValue` sets the vaccine (`medication`); guidance goes to a
CommunicationRequest (`IMMZD2DTCR`) (*P§2*).

## Run it locally

`scripts/apply/run.sh PROJECT plan|r5|activity|library ID Patient/<id>` runs `$apply` or
`Library/$evaluate` with clinical-reasoning 4.13.0 on a folder in IG layout (Java 17+, Maven). Test each
rule with: no doses; one dated dose inside and outside the interval; an undated dose; a `not-done` and an
`entered-in-error` record; a contraindication.

## Checklist

- [ ] Only `completed` doses counted; `entered-in-error` ignored; `not-done` read for its reason.
- [ ] Undated (`occurrenceString`) and subpotent doses handled explicitly.
- [ ] `doseNumber[x]` not assumed to be an integer.
- [ ] "Today" is a parameter.
- [ ] Generated MedicationRequests get `category` and `status` by dynamicValue.
- [ ] Every ImmunizationRecommendation sets `forecastStatus` from the logic, and `vaccineCode` or
      `targetDisease`.
