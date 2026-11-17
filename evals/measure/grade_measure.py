#!/usr/bin/env python3
"""Grade TK-01: a boolean-basis proportion Measure. Prints PASS/FAIL per criterion; exits 1 on a FAIL.

    python3 grade_measure.py Measure-screening.json

Python 3.9+, standard library only. Structural checks only; run scripts/evaluate/run.sh to evaluate.
"""
import json
import sys

MP = "http://terminology.hl7.org/CodeSystem/measure-population"
BASIS = "http://hl7.org/fhir/us/cqfmeasures/StructureDefinition/cqfm-populationBasis"
ALLOWED = {"initial-population", "denominator", "denominator-exclusion", "denominator-exception",
           "numerator", "numerator-exclusion"}
REQUIRED = {"initial-population", "denominator", "denominator-exclusion", "numerator"}


def codes(cc):
    return {(c.get("system"), c.get("code")) for c in (cc or {}).get("coding", [])}


def grade(m):
    out = []
    ok = lambda name, cond: out.append((name, bool(cond)))
    ok("resourceType Measure", m.get("resourceType") == "Measure")
    ok("scoring proportion", ("http://terminology.hl7.org/CodeSystem/measure-scoring", "proportion") in codes(m.get("scoring")))
    ok("library canonical", m.get("library") == ["http://example.org/fhir/Library/Screening|1.0.0"])
    ok("improvementNotation increase", ("http://terminology.hl7.org/CodeSystem/measure-improvement-notation", "increase") in codes(m.get("improvementNotation")))
    groups = m.get("group") or []
    ok("one group", len(groups) == 1)
    g = groups[0] if groups else {}
    ok("populationBasis boolean", any(e.get("url") == BASIS and e.get("valueCode") == "boolean" for e in g.get("extension", [])))
    pops = {}
    for p in g.get("population", []):
        for s, c in codes(p.get("code")):
            if s == MP:
                pops[c] = p
    ok("required populations", REQUIRED <= set(pops))
    ok("no population outside proportion", set(pops) <= ALLOWED)
    ok("every population names an expression", all((p.get("criteria") or {}).get("expression") for p in pops.values()))
    strats = g.get("stratifier", [])
    ok("one stratifier", len(strats) == 1)
    s = strats[0] if strats else {}
    ok("stratifier as component, not top-level criteria",
       not (s.get("criteria") or {}).get("expression") and any((c.get("criteria") or {}).get("expression") for c in s.get("component", [])))
    return out


def main():
    m = json.load(open(sys.argv[1]))
    res = grade(m)
    for name, passed in res:
        print(("PASS " if passed else "FAIL ") + name)
    return 0 if all(p for _, p in res) else 1


if __name__ == "__main__":
    sys.exit(main())
