import copy

from grade_measure import grade

MP = "http://terminology.hl7.org/CodeSystem/measure-population"
GOOD = {
    "resourceType": "Measure",
    "scoring": {"coding": [{"system": "http://terminology.hl7.org/CodeSystem/measure-scoring", "code": "proportion"}]},
    "library": ["http://example.org/fhir/Library/Screening|1.0.0"],
    "improvementNotation": {"coding": [{"system": "http://terminology.hl7.org/CodeSystem/measure-improvement-notation", "code": "increase"}]},
    "group": [{
        "extension": [{"url": "http://hl7.org/fhir/us/cqfmeasures/StructureDefinition/cqfm-populationBasis", "valueCode": "boolean"}],
        "population": [{"code": {"coding": [{"system": MP, "code": c}]}, "criteria": {"language": "text/cql-identifier", "expression": e}}
                       for c, e in [("initial-population", "Initial Population"), ("denominator", "Denominator"),
                                    ("denominator-exclusion", "Denominator Exclusions"), ("numerator", "Numerator")]],
        "stratifier": [{"component": [{"code": {"text": "sex"}, "criteria": {"language": "text/cql-identifier", "expression": "Sex"}}]}],
    }],
}


def failed(m):
    return [n for n, p in grade(m) if not p]


def test_good_passes():
    assert failed(GOOD) == []


def test_top_level_stratifier_criteria_fails():
    m = copy.deepcopy(GOOD)
    m["group"][0]["stratifier"] = [{"criteria": {"language": "text/cql-identifier", "expression": "Sex"}}]
    assert failed(m) == ["stratifier as component, not top-level criteria"]


def test_measure_population_in_proportion_fails():
    m = copy.deepcopy(GOOD)
    m["group"][0]["population"].append({"code": {"coding": [{"system": MP, "code": "measure-population"}]}, "criteria": {"expression": "X"}})
    assert failed(m) == ["no population outside proportion"]


def test_missing_basis_fails():
    m = copy.deepcopy(GOOD)
    m["group"][0]["extension"] = []
    assert failed(m) == ["populationBasis boolean"]
