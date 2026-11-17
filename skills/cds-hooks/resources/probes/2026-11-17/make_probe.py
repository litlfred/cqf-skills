#!/usr/bin/env python3
"""Write the probe project for RESULTS.md. Synthetic data only.

    python3 -I make_probe.py

Python 3.9+, standard library only.
"""
import base64, json
from pathlib import Path

HERE = Path(__file__).resolve().parent
RES, TESTS = HERE / "input" / "resources", HERE / "input" / "tests"
BASE = "http://example.org/fhir"

CQL = """library CdsProbe version '1.0.0'
using FHIR version '4.0.1'
context Patient
define "Is Adult": AgeInYears() >= 18
define "Is Child": AgeInYears() < 18
"""

def w(d, n, r):
    (d / f"{n}.json").write_text(json.dumps(r, indent=2) + "\n")

def cond(expr):
    return [{"kind": "applicability", "expression": {"language": "text/cql-identifier", "expression": expr}}]

def act(aid, title, **kw):
    a = {"id": aid, "title": title}
    a.update(kw)
    return a

def plan(pid, actions, **kw):
    p = {"resourceType": "PlanDefinition", "id": pid, "url": f"{BASE}/PlanDefinition/{pid}", "version": "1.0.0",
         "name": pid.replace("-", ""), "title": f"Probe {pid}", "description": f"Probe PlanDefinition {pid}.",
         "status": "active", "library": [f"{BASE}/Library/CdsProbe"], "action": actions}
    p.update(kw)
    return p

def main():
    RES.mkdir(parents=True, exist_ok=True); TESTS.mkdir(parents=True, exist_ok=True)
    w(RES, "Library-CdsProbe", {
        "resourceType": "Library", "id": "CdsProbe", "url": f"{BASE}/Library/CdsProbe", "version": "1.0.0",
        "name": "CdsProbe", "status": "active",
        "type": {"coding": [{"system": "http://terminology.hl7.org/CodeSystem/library-type", "code": "logic-library"}]},
        "content": [{"contentType": "text/cql", "data": base64.b64encode(CQL.encode()).decode()}]})
    w(RES, "ActivityDefinition-order-test", {
        "resourceType": "ActivityDefinition", "id": "order-test", "url": f"{BASE}/ActivityDefinition/order-test",
        "version": "1.0.0", "name": "OrderTest", "status": "active", "kind": "ServiceRequest", "intent": "proposal",
        "code": {"text": "Illustrative test order"}})
    trigger = [{"type": "named-event", "name": "patient-view"}]
    w(RES, "PlanDefinition-cds-probe", plan("cds-probe", [
        act("routine", "Routine advice", description="Detail for the routine card.", priority="routine",
            trigger=trigger, condition=cond("Is Adult"),
            documentation=[{"type": "documentation", "display": "Example guideline",
                            "url": "http://example.org/guideline",
                            "document": {"url": "http://example.org/icon.png"}}]),
        act("urgent", "Urgent advice", description="Detail for the urgent card.", priority="urgent", condition=cond("Is Adult")),
        act("stat", "Stat advice", priority="stat", condition=cond("Is Adult")),
        act("no-priority", "Advice with no priority", condition=cond("Is Adult")),
        act("choose", "Choose an order", priority="routine", selectionBehavior="at-most-one", condition=cond("Is Adult"),
            action=[act("order-a", "Order the test", description="Create the order",
                        type={"coding": [{"system": "http://terminology.hl7.org/CodeSystem/action-type", "code": "create"}]},
                        definitionCanonical=f"{BASE}/ActivityDefinition/order-test")]),
        act("child-only", "Not for adults", priority="routine", condition=cond("Is Child")),
    ], relatedArtifact=[{"type": "documentation", "display": "Guide", "url": "http://example.org/guide"}]))
    # The same cards without the action that applies an ActivityDefinition.
    w(RES, "PlanDefinition-cds-cards", plan("cds-cards", [
        act("routine", "Routine advice", description="Detail for the routine card.", priority="routine",
            trigger=trigger, condition=cond("Is Adult"),
            documentation=[{"type": "documentation", "display": "Example guideline",
                            "url": "http://example.org/guideline",
                            "document": {"url": "http://example.org/icon.png"}}]),
        act("urgent", "Urgent advice", description="Detail for the urgent card.", priority="urgent", condition=cond("Is Adult")),
        act("stat", "Stat advice", priority="stat", condition=cond("Is Adult")),
        act("no-priority", "Advice with no priority", condition=cond("Is Adult")),
        act("child-only", "Not for adults", priority="routine", condition=cond("Is Child")),
    ], relatedArtifact=[{"type": "documentation", "display": "Guide", "url": "http://example.org/guide"}]))
    # One action each, to isolate what the encoder accepts.
    single = {
        "one-routine": act("a", "Routine advice", priority="routine", trigger=trigger, condition=cond("Is Adult")),
        "one-doc": act("a", "Advice with a source", priority="routine", trigger=trigger, condition=cond("Is Adult"),
                       documentation=[{"type": "documentation", "display": "Example guideline", "url": "http://example.org/guideline"}]),
        "one-no-priority": act("a", "Advice with no priority", trigger=trigger, condition=cond("Is Adult")),
        "one-false": act("a", "Not for adults", priority="routine", trigger=trigger, condition=cond("Is Child")),
    }
    for pid, a in single.items():
        w(RES, f"PlanDefinition-{pid}", plan(pid, [a]))
    w(RES, "PlanDefinition-one-link", plan("one-link", [single["one-routine"]],
        relatedArtifact=[{"type": "documentation", "display": "Guide", "url": "http://example.org/guide"}]))
    w(RES, "PlanDefinition-two-true", plan("two-true", [single["one-routine"],
        act("b", "Urgent advice", priority="urgent", condition=cond("Is Adult"))]))
    w(RES, "PlanDefinition-true-and-false", plan("true-and-false", [single["one-routine"],
        act("b", "Not for adults", priority="routine", condition=cond("Is Child"))]))
    # A choice group whose actions all apply: what becomes of its suggestions.
    for pid, behavior in (("choose", "at-most-one"), ("choose-exactly-one", "exactly-one")):
        w(RES, f"PlanDefinition-{pid}", plan(pid, [
            act("choose", "Choose an order", priority="routine", selectionBehavior=behavior, trigger=trigger,
                condition=cond("Is Adult"),
                action=[act("order-a", "Order the test", description="Create the order",
                            type={"coding": [{"system": "http://terminology.hl7.org/CodeSystem/action-type", "code": "create"}]},
                            definitionCanonical=f"{BASE}/ActivityDefinition/order-test")])]))
    w(RES, "PlanDefinition-no-trigger", plan("no-trigger", [act("a", "Advice", priority="routine", condition=cond("Is Adult"))]))
    w(RES, "PlanDefinition-asap", plan("asap", [act("a", "ASAP advice", priority="asap", trigger=trigger, condition=cond("Is Adult"))]))
    w(TESTS, "Patient-adult-1", {"resourceType": "Patient", "id": "adult-1", "birthDate": "1980-01-01"})

if __name__ == "__main__":
    main()
