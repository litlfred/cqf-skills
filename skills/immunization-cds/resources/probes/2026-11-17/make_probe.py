#!/usr/bin/env python3
"""Write the probe project for RESULTS.md. Synthetic data; vaccine codes are illustrative.

    python3 -I make_probe.py

Python 3.9+, standard library only.
"""
import base64, json
from pathlib import Path

HERE = Path(__file__).resolve().parent
RES, TESTS = HERE / "input" / "resources", HERE / "input" / "tests"
BASE = "http://example.org/fhir"
VAX = "http://example.org/fhir/CodeSystem/illustrative-vaccines"

CQL = """library ImmzProbe version '1.0.0'

using FHIR version '4.0.1'

include FHIRHelpers version '4.0.1' called FHIRHelpers

codesystem "VAX": 'http://example.org/fhir/CodeSystem/illustrative-vaccines'
code "MCV": 'MCV' from "VAX" display 'Measles-containing vaccine (illustrative)'

parameter "Today" Date default Today()

context Patient

define "All MCV": [Immunization: "MCV"]
define "All MCV Ids": "All MCV" I return I.id
define "Completed MCV": "All MCV" I where I.status = 'completed'
define "Completed MCV Ids": "Completed MCV" I return I.id
define "Not Done MCV Ids": "All MCV" I where I.status = 'not-done' return I.id
define "Completed Dose Count": Count("Completed MCV")
define "Dated Completed MCV": "Completed MCV" I where I.occurrence is FHIR.dateTime
define "Dated Dose Count": Count("Dated Completed MCV")
define "Latest Dose Date":
  Max("Dated Completed MCV" I return (I.occurrence as FHIR.dateTime))
define "Dose Numbers":
  "Completed MCV" I return I.protocolApplied[0].doseNumber
define "Due For MCV":
  "Completed Dose Count" < 2
    and ("Latest Dose Date" is null or date from "Latest Dose Date" + 4 weeks <= "Today")
"""

def w(d, n, r):
    (d / f"{n}.json").write_text(json.dumps(r, indent=2) + "\n")

def imm(iid, status, occ, dose=None, string_occ=False):
    r = {"resourceType": "Immunization", "id": iid, "status": status,
         "vaccineCode": {"coding": [{"system": VAX, "code": "MCV"}]},
         "patient": {"reference": "Patient/child-1"}}
    r["occurrenceString" if string_occ else "occurrenceDateTime"] = occ
    if dose is not None:
        key = "doseNumberPositiveInt" if isinstance(dose, int) else "doseNumberString"
        r["protocolApplied"] = [{"targetDisease": [{"text": "Measles"}], key: dose}]
    return r

def main():
    RES.mkdir(parents=True, exist_ok=True); TESTS.mkdir(parents=True, exist_ok=True)
    w(RES, "Library-ImmzProbe", {
        "resourceType": "Library", "id": "ImmzProbe", "url": f"{BASE}/Library/ImmzProbe", "version": "1.0.0",
        "name": "ImmzProbe", "status": "active",
        "type": {"coding": [{"system": "http://terminology.hl7.org/CodeSystem/library-type", "code": "logic-library"}]},
        "content": [{"contentType": "text/cql", "data": base64.b64encode(CQL.encode()).decode()}]})
    # CPG 2.0.0 cpg-immunizationactivity: kind MedicationRequest, intent proposal, code recommend-immunization.
    w(RES, "ActivityDefinition-recommend-mcv", {
        "resourceType": "ActivityDefinition", "id": "recommend-mcv", "url": f"{BASE}/ActivityDefinition/recommend-mcv",
        "version": "1.0.0", "name": "RecommendMCV", "status": "active",
        "meta": {"profile": ["http://hl7.org/fhir/uv/cpg/StructureDefinition/cpg-immunizationactivity"]},
        "kind": "MedicationRequest", "intent": "proposal", "doNotPerform": False,
        "profile": "http://hl7.org/fhir/uv/cpg/StructureDefinition/cpg-immunizationrequest",
        "code": {"coding": [{"system": "http://hl7.org/fhir/uv/cpg/CodeSystem/cpg-activity-type-cs", "code": "recommend-immunization"}]},
        "productCodeableConcept": {"coding": [{"system": VAX, "code": "MCV"}]}})
    # The same, with the dynamicValues SKILL.md recommends for status and category.
    fixed = json.loads(json.dumps({
        "resourceType": "ActivityDefinition", "id": "recommend-mcv-fixed", "url": f"{BASE}/ActivityDefinition/recommend-mcv-fixed",
        "version": "1.0.0", "name": "RecommendMCVFixed", "status": "active",
        "meta": {"profile": ["http://hl7.org/fhir/uv/cpg/StructureDefinition/cpg-immunizationactivity"]},
        "kind": "MedicationRequest", "intent": "proposal", "doNotPerform": False,
        "profile": "http://hl7.org/fhir/uv/cpg/StructureDefinition/cpg-immunizationrequest",
        "code": {"coding": [{"system": "http://hl7.org/fhir/uv/cpg/CodeSystem/cpg-activity-type-cs", "code": "recommend-immunization"}]},
        "productCodeableConcept": {"coding": [{"system": VAX, "code": "MCV"}]},
        "dynamicValue": [
            {"path": "status", "expression": {"language": "text/cql-expression", "expression": "'draft'"}},
            {"path": "category", "expression": {"language": "text/cql-expression",
             "expression": "{ Concept { codes: { Code { code: 'recommend-immunization', system: 'http://hl7.org/fhir/uv/cpg/CodeSystem/cpg-activity-type-cs' } } } }"}}]}))
    w(RES, "ActivityDefinition-recommend-mcv-fixed", fixed)
    # R4 allows kind ImmunizationRecommendation.
    w(RES, "ActivityDefinition-forecast-mcv", {
        "resourceType": "ActivityDefinition", "id": "forecast-mcv", "url": f"{BASE}/ActivityDefinition/forecast-mcv",
        "version": "1.0.0", "name": "ForecastMCV", "status": "active", "kind": "ImmunizationRecommendation",
        "code": {"coding": [{"system": VAX, "code": "MCV"}]}})
    w(RES, "ActivityDefinition-forecast-mcv-product", {
        "resourceType": "ActivityDefinition", "id": "forecast-mcv-product",
        "url": f"{BASE}/ActivityDefinition/forecast-mcv-product", "version": "1.0.0", "name": "ForecastMCVProduct",
        "status": "active", "kind": "ImmunizationRecommendation",
        "code": {"coding": [{"system": VAX, "code": "MCV"}]},
        "productCodeableConcept": {"coding": [{"system": VAX, "code": "MCV"}]},
        "dynamicValue": [{"path": "recommendation.forecastStatus",
                          "expression": {"language": "text/cql-expression",
                                         "expression": "Concept { codes: { Code { code: 'due', system: 'http://terminology.hl7.org/CodeSystem/immunization-recommendation-status' } } }"}}]})
    w(RES, "ActivityDefinition-forecast-mcv-no-status", {
        "resourceType": "ActivityDefinition", "id": "forecast-mcv-no-status",
        "url": f"{BASE}/ActivityDefinition/forecast-mcv-no-status", "version": "1.0.0", "name": "ForecastMCVNoStatus",
        "status": "active", "kind": "ImmunizationRecommendation",
        "productCodeableConcept": {"coding": [{"system": VAX, "code": "MCV"}]}})
    w(RES, "PlanDefinition-mcv-due", {
        "resourceType": "PlanDefinition", "id": "mcv-due", "url": f"{BASE}/PlanDefinition/mcv-due", "version": "1.0.0",
        "name": "MCVDue", "status": "active", "library": [f"{BASE}/Library/ImmzProbe"],
        "action": [{"id": "due", "title": "Client is due for MCV",
                    "condition": [{"kind": "applicability", "expression": {"language": "text/cql-identifier", "expression": "Due For MCV"}}],
                    "definitionCanonical": f"{BASE}/ActivityDefinition/recommend-mcv"}]})
    w(TESTS, "Patient-child-1", {"resourceType": "Patient", "id": "child-1", "birthDate": "2024-06-01"})
    w(TESTS, "Immunization-i1", imm("i1", "completed", "2025-03-10T10:00:00Z", 1))
    w(TESTS, "Immunization-i2", imm("i2", "not-done", "2025-04-10T10:00:00Z"))
    w(TESTS, "Immunization-i3", imm("i3", "entered-in-error", "2025-05-10T10:00:00Z", 2))
    # child-2: one dated dose, so due for the second.
    w(TESTS, "Patient-child-2", {"resourceType": "Patient", "id": "child-2", "birthDate": "2024-06-01"})
    i5 = imm("i5", "completed", "2025-03-10T10:00:00Z", 1)
    i5["patient"] = {"reference": "Patient/child-2"}
    w(TESTS, "Immunization-i5", i5)
    w(TESTS, "Immunization-i4", imm("i4", "completed", "at the 9-month visit (historical, no date)", "first", string_occ=True))

if __name__ == "__main__":
    main()
