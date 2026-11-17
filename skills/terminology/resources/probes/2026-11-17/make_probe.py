#!/usr/bin/env python3
"""Write the two probe projects for RESULTS.md. Synthetic data; every code is illustrative.

    python3 -I make_probe.py

project-a keeps ValueSets in input/vocabulary/valueset/ with flat tests, project-b flat in
input/vocabulary/, project-c in input/vocabulary/valueset/ with tests and resources grouped by type
(input/tests/patient/, input/tests/condition/, input/resources/library/).
Python 3.9+, standard library only.
"""
import base64, json, shutil
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCT = "http://snomed.info/sct"
BASE = "http://example.org/fhir"

CQL = """library TerminologyProbe version '1.0.0'

using FHIR version '4.0.1'

include FHIRHelpers version '4.0.1' called FHIRHelpers

codesystem "SCT": 'http://snomed.info/sct'

valueset "Expanded": 'http://example.org/fhir/ValueSet/vs-expanded'
valueset "ComposeOnly": 'http://example.org/fhir/ValueSet/vs-compose'
valueset "Missing": 'http://example.org/fhir/ValueSet/vs-missing'

// Illustrative codes, not real SNOMED CT concepts.
code "C1 Other Display": '1000001' from "SCT" display 'Display B'

context Patient

define "Retrieve Expanded": [Condition: "Expanded"] C return C.id
define "Retrieve ComposeOnly": [Condition: "ComposeOnly"] C return C.id
define "Retrieve Missing": [Condition: "Missing"] C return C.id
define "Retrieve By Code": [Condition: "C1 Other Display"] C return C.id
define "In Expanded": [Condition] C where C.code in "Expanded" return C.id
define "Equivalent To Code": [Condition] C where C.code ~ "C1 Other Display" return C.id

define "Equal Different Display":
  Code { code: '1', system: 's', display: 'A' } = Code { code: '1', system: 's', display: 'B' }
define "Equivalent Different Display":
  Code { code: '1', system: 's', display: 'A' } ~ Code { code: '1', system: 's', display: 'B' }
define "Equal Different Version":
  Code { code: '1', system: 's', version: '1' } = Code { code: '1', system: 's', version: '2' }
define "Equivalent Different Version":
  Code { code: '1', system: 's', version: '1' } ~ Code { code: '1', system: 's', version: '2' }
"""

def vs(vid, expansion=True):
    r = {"resourceType": "ValueSet", "id": vid, "url": f"{BASE}/ValueSet/{vid}", "version": "1.0.0",
         "name": vid.replace("-", ""), "status": "active"}
    if expansion:
        r["compose"] = {"include": [{"system": SCT, "concept": [{"code": "1000001"}, {"code": "1000002"}]}]}
        r["expansion"] = {"timestamp": "2026-11-17T00:00:00Z",
                          "contains": [{"system": SCT, "code": "1000001"}, {"system": SCT, "code": "1000002"}]}
    else:
        r["compose"] = {"include": [{"system": SCT, "concept": [{"code": "1000003"}]}]}
    return r

def cond(cid, system, code, display=None):
    coding = {"system": system, "code": code}
    if display:
        coding["display"] = display
    return {"resourceType": "Condition", "id": cid, "subject": {"reference": "Patient/p1"},
            "code": {"coding": [coding]}}

def project(name, vocab_subdir, typed_tests=False):
    root = HERE / name
    shutil.rmtree(root, ignore_errors=True)
    res, tests = root / "input" / "resources", root / "input" / "tests"
    vocab = root / "input" / "vocabulary" / vocab_subdir
    for d in (res, tests, vocab):
        d.mkdir(parents=True)
    pt = ct = tests
    lib = res
    if typed_tests:
        pt, ct, lib = tests / "patient", tests / "condition", res / "library"
        pt.mkdir(); ct.mkdir(); lib.mkdir()
    w = lambda d, n, r: (d / f"{n}.json").write_text(json.dumps(r, indent=2) + "\n")
    w(lib, "Library-TerminologyProbe", {
        "resourceType": "Library", "id": "TerminologyProbe", "url": f"{BASE}/Library/TerminologyProbe",
        "version": "1.0.0", "name": "TerminologyProbe", "status": "active",
        "type": {"coding": [{"system": "http://terminology.hl7.org/CodeSystem/library-type", "code": "logic-library"}]},
        "content": [{"contentType": "text/cql", "data": base64.b64encode(CQL.encode()).decode()}]})
    w(vocab, "ValueSet-vs-expanded", vs("vs-expanded"))
    w(vocab, "ValueSet-vs-compose", vs("vs-compose", expansion=False))
    w(pt, "Patient-p1", {"resourceType": "Patient", "id": "p1"})
    w(ct, "Condition-c1", cond("c1", SCT, "1000001", "Display A"))
    w(ct, "Condition-c2", cond("c2", "urn:oid:2.16.840.1.113883.6.96", "1000002"))
    w(ct, "Condition-c3", cond("c3", SCT, "1000003"))

if __name__ == "__main__":
    project("project-a", "valueset")
    project("project-b", "")
    project("project-c", "valueset", typed_tests=True)
