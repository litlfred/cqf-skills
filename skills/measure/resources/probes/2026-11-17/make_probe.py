#!/usr/bin/env python3
"""Write the probe project (input/resources, input/tests) for RESULTS.md. Synthetic data only.

    python3 -I make_probe.py

Python 3.9+, standard library only.
"""
import base64, json
from pathlib import Path

HERE = Path(__file__).resolve().parent
RES, TESTS = HERE / "input" / "resources", HERE / "input" / "tests"
MP = "http://terminology.hl7.org/CodeSystem/measure-population"
CQFM = "http://hl7.org/fhir/us/cqfmeasures/StructureDefinition/"
BASE = "http://example.org/fhir"

CQL = """library MeasureProbe version '1.0.0'

using FHIR version '4.0.1'

include FHIRHelpers version '4.0.1' called FHIRHelpers

parameter "Measurement Period" Interval<DateTime>

context Patient

// Population membership is fixed by patient id, so each population boundary is one patient.
define "Id": Patient.id
define "Initial Population": true
define "Denominator": "Initial Population"
define "Denominator Exclusions": "Id" in { 'p5' }
define "Denominator Exceptions": "Id" in { 'p3', 'p4' }
define "Numerator": "Id" in { 'p1', 'p2', 'p3', 'p5' }
define "Numerator Exclusions": "Id" in { 'p2' }
define "Sex": Patient.gender
define "Not In IP": "Id" in { 'p6' }
define "IP Without p6": not "Not In IP"

// Encounter basis: encounters that start in the Measurement Period.
define "Encounters In Period":
  [Encounter] E where E.period.start during "Measurement Period"
define "Finished Encounters":
  "Encounters In Period" E where E.status = 'finished'
define "Encounter Exclusions":
  "Encounters In Period" E where E.id in { 'e4' }

define function "Length Of Stay Days"(E Encounter):
  difference in days between start of E.period and end of E.period

// A population that returns the wrong type for a boolean basis.
define "Wrong Type For Boolean": "Encounters In Period"
"""

def write(d, name, r):
    (d / f"{name}.json").write_text(json.dumps(r, indent=2) + "\n")

def pop(pid, code, expr, lang="text/cql-identifier", **extra):
    p = {"id": pid, "code": {"coding": [{"system": MP, "code": code}]},
         "criteria": {"language": lang, "expression": expr}}
    p.update(extra)
    return p

def measure(mid, scoring, groups, **extra):
    m = {"resourceType": "Measure", "id": mid, "url": f"{BASE}/Measure/{mid}", "version": "1.0.0",
         "name": mid.replace("-", ""), "status": "active",
         "scoring": {"coding": [{"system": "http://terminology.hl7.org/CodeSystem/measure-scoring", "code": scoring}]},
         "library": [f"{BASE}/Library/MeasureProbe"], "group": groups}
    m.update(extra)
    return m

def basis(code):
    return [{"url": CQFM + "cqfm-populationBasis", "valueCode": code}]

def main():
    RES.mkdir(parents=True, exist_ok=True); TESTS.mkdir(parents=True, exist_ok=True)
    write(RES, "Library-MeasureProbe", {
        "resourceType": "Library", "id": "MeasureProbe", "url": f"{BASE}/Library/MeasureProbe",
        "version": "1.0.0", "name": "MeasureProbe", "status": "active",
        "type": {"coding": [{"system": "http://terminology.hl7.org/CodeSystem/library-type", "code": "logic-library"}]},
        "content": [{"contentType": "text/cql", "data": base64.b64encode(CQL.encode()).decode()}]})

    # 1. Proportion, boolean basis: nesting, exceptions vs numerator, score, stratifier, SDE.
    write(RES, "Measure-proportion", measure("proportion", "proportion", [{
        "id": "g1", "extension": basis("boolean"),
        "population": [
            pop("ip", "initial-population", "Initial Population"),
            pop("denom", "denominator", "Denominator"),
            pop("denex", "denominator-exclusion", "Denominator Exclusions"),
            pop("denexcep", "denominator-exception", "Denominator Exceptions"),
            pop("numer", "numerator", "Numerator"),
            pop("numex", "numerator-exclusion", "Numerator Exclusions")],
        "stratifier": [{"id": "by-sex", "component": [{"id": "sex", "code": {"text": "sex"},
                        "criteria": {"language": "text/cql-identifier", "expression": "Sex"}}]}]}],
        improvementNotation={"coding": [{"system": "http://terminology.hl7.org/CodeSystem/measure-improvement-notation", "code": "increase"}]},
        supplementalData=[{"id": "sde-sex", "usage": [{"coding": [{"system": "http://terminology.hl7.org/CodeSystem/measure-data-usage", "code": "supplemental-data"}]}],
                           "criteria": {"language": "text/cql-identifier", "expression": "Sex"}}]))

    # 1b. The same stratifier as a top-level criteria returning a value.
    write(RES, "Measure-criteria-stratifier", measure("criteria-stratifier", "proportion", [{
        "id": "g1", "extension": basis("boolean"),
        "population": [
            pop("ip", "initial-population", "Initial Population"),
            pop("denom", "denominator", "Denominator"),
            pop("numer", "numerator", "Numerator")],
        "stratifier": [{"id": "by-sex", "criteria": {"language": "text/cql-identifier", "expression": "Sex"}}]}]))

    # 2. Proportion, Encounter basis.
    write(RES, "Measure-encounter-basis", measure("encounter-basis", "proportion", [{
        "id": "g1", "extension": basis("Encounter"),
        "population": [
            pop("ip", "initial-population", "Encounters In Period"),
            pop("denom", "denominator", "Encounters In Period"),
            pop("denex", "denominator-exclusion", "Encounter Exclusions"),
            pop("numer", "numerator", "Finished Encounters")]}]))

    # 3. Continuous variable: median length of stay.
    write(RES, "Measure-continuous", measure("continuous", "continuous-variable", [{
        "id": "g1", "extension": basis("Encounter"),
        "population": [
            pop("ip", "initial-population", "Encounters In Period"),
            pop("mp", "measure-population", "Encounters In Period"),
            pop("mpex", "measure-population-exclusion", "Encounter Exclusions"),
            pop("obs", "measure-observation", "Length Of Stay Days",
                extension=[{"url": CQFM + "cqfm-aggregateMethod", "valueCode": "median"},
                           {"url": CQFM + "cqfm-criteriaReference", "valueString": "mp"}])]}]))

    # 4. Cohort.
    write(RES, "Measure-cohort", measure("cohort", "cohort", [{
        "id": "g1", "extension": basis("boolean"),
        "population": [pop("ip", "initial-population", "IP Without p6")]}]))

    # 5. Boolean basis, but the population returns List<Encounter>.
    write(RES, "Measure-wrong-basis", measure("wrong-basis", "cohort", [{
        "id": "g1", "extension": basis("boolean"),
        "population": [pop("ip", "initial-population", "Wrong Type For Boolean")]}]))

    # 6. R4 language code text/cql for a named expression.
    write(RES, "Measure-text-cql", measure("text-cql", "cohort", [{
        "id": "g1", "extension": basis("boolean"),
        "population": [pop("ip", "initial-population", "IP Without p6", lang="text/cql")]}]))

    genders = {"p1": "female", "p2": "male", "p3": "female", "p4": "male", "p5": "female", "p6": "other"}
    for pid, g in genders.items():
        write(TESTS, f"Patient-{pid}", {"resourceType": "Patient", "id": pid, "gender": g, "birthDate": "1980-01-01"})
    encs = [  # id, patient, status, start, end
        ("e1", "p1", "finished", "2025-03-01", "2025-03-03"),
        ("e2", "p2", "finished", "2025-04-01", "2025-04-05"),
        ("e3", "p3", "in-progress", "2025-05-01", "2025-05-02"),
        ("e4", "p4", "finished", "2025-06-01", "2025-06-11"),
        ("e5", "p1", "finished", "2024-06-01", "2024-06-02"),  # outside the period
    ]
    for eid, pid, status, s, e in encs:
        write(TESTS, f"Encounter-{eid}", {
            "resourceType": "Encounter", "id": eid, "status": status,
            "class": {"system": "http://terminology.hl7.org/CodeSystem/v3-ActCode", "code": "IMP"},
            "subject": {"reference": f"Patient/{pid}"},
            "period": {"start": f"{s}T08:00:00Z", "end": f"{e}T08:00:00Z"}})

if __name__ == "__main__":
    main()
