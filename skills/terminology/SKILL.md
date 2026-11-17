---
name: terminology
description: Works with terminology for CQL and FHIR knowledge artifacts — CQL codesystem, valueset and code declarations and the in, ~ and = operators on codes; FHIR R4 ValueSet and CodeSystem resources; the $expand, $validate-code, $lookup, $subsumes and ConceptMap $translate operations; pinning value set and code system versions for reproducible evaluation (expansion parameters, CRMI manifests); and putting expanded value sets where local CQL tooling and test runs find them. Use when a retrieve finds nothing because of a code or value set, when a value set must be expanded or pinned, when choosing between a direct-reference code and a value set, or when wiring a terminology server. Not for authoring the CQL logic (cql), IG Publisher terminology settings (ig-publisher) or FSH syntax for ValueSets (fsh).
license: Apache-2.0
---

# Terminology for CQL and FHIR artifacts

> **Status: draft (litlfred fork).** Written from FHIR R4 terminology services and CQL 1.5.3; not yet
> checked by running a terminology server, as the upstream skills are.

Targets **FHIR R4 (4.0.1)** terminology (<https://hl7.org/fhir/R4/terminology-module.html>) and
**CQL 1.5.3** terminology declarations (<https://cql.hl7.org/02-authorsguide.html#value-sets>).
Version pinning follows **CRMI** (<https://hl7.org/fhir/uv/crmi/>); the `crmi` skill holds its
profiles.

## Decide: value set or direct-reference code

- Use a **value set** when the concept is a clinical grouping that a steward maintains.
- Use a **direct-reference code** (`code "X": '1234' from "SNOMEDCT"`) only for a single concept with
  no grouping, and compare with `~` (equivalent), never `=`: `=` also compares `display` and
  `version`, so a resource carrying a different display makes it false.
- `in` tests membership against the **expansion**; it is only as current as the expansion the engine
  sees.

```cql
codesystem "LOINC": 'http://loinc.org'
valueset "Example Screening Tests": 'http://example.org/fhir/ValueSet/example-screening'
code "Example Panel": '00000-0' from "LOINC" display 'Illustrative code, not a real LOINC'

define "Screening Observations":
  [Observation: "Example Screening Tests"] O
    where O.status in { 'final', 'amended', 'corrected' }
```

## Operations

| operation | asks | key parameters |
|---|---|---|
| `ValueSet/$expand` | which codes are in this value set now | `url`, `valueSetVersion`, `filter`, `count`, `offset`, `system-version`, `force-system-version`, `check-system-version`, `activeOnly` |
| `ValueSet/$validate-code` | is this code in the value set | `url`, `code` + `system` (or `coding`/`codeableConcept`), `display` |
| `CodeSystem/$lookup` | what does this code mean | `system`, `code`, `version`, `property` |
| `CodeSystem/$subsumes` | is A an ancestor of B | `codeA`, `codeB`, `system` |
| `ConceptMap/$translate` | map a code to another system | `url`, `code`, `system`, `target` |

## Reproducible evaluation: pin what the expansion used

An evaluation is reproducible only if the expansion is. Record and pin:

1. The **value set version** in the canonical (`url|version`).
2. The **code system versions** used to expand it — `system-version` (default) or
   `force-system-version` (override) on `$expand`.
3. For a packaged artifact, a CRMI **manifest Library** whose `relatedArtifact` and expansion
   parameters list every value set and code system version; `$package` and `$data-requirements`
   produce or read it.

Keep the resulting `ValueSet.expansion` (with `expansion.parameter` showing the versions) beside the
test data, so a test run never needs the server.

## Local tooling and test runs

- CQL tooling evaluates `in` against expanded ValueSet resources it can load. In an IG layout keep
  them under `input/vocabulary/valueset/` (one JSON per value set, with `expansion`), so that test runs
  and the IG Publisher read the same files.
- A retrieve that finds nothing: check, in order, (1) the value set is expanded at all, (2) the code's
  `system` URI is exactly the one the expansion uses (`http://snomed.info/sct`, `http://loinc.org`,
  `http://hl7.org/fhir/sid/icd-10-cm` — not an OID or `urn:` form), (3) the code system version the
  expansion used contains the code, (4) the resource element the retrieve filters on is the one carrying
  the code (the model info's primary code path).

## Servers and licensed terminology

- Use only a terminology server the user has configured. Never send patient data to one; send codes.
- Licensed systems (SNOMED CT, CPT, some LOINC uses, VSAC content behind a UMLS licence) need the
  user's own licence and credentials. Do not paste licensed content into examples: use codes marked
  illustrative, as above.

## Checklist

- [ ] Every `valueset` canonical resolves and is versioned for release builds.
- [ ] Direct-reference codes compared with `~`.
- [ ] System URIs are canonical URLs, not OIDs.
- [ ] Expansions used in tests are committed with their version parameters.
