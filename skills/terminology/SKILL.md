---
name: terminology
description: Works with terminology for CQL and FHIR knowledge artifacts — CQL codesystem, valueset and code declarations and the in, ~ and = operators on codes; FHIR R4 ValueSet and CodeSystem resources; the $expand, $validate-code, $lookup, $subsumes and ConceptMap $translate operations; pinning value set and code system versions for reproducible evaluation (expansion parameters, CRMI manifests); and putting expanded value sets where local CQL tooling and test runs find them. Use when a retrieve finds nothing because of a code or value set, when a value set must be expanded or pinned, when choosing between a direct-reference code and a value set, or when wiring a terminology server. Not for authoring the CQL logic (cql), IG Publisher terminology settings (ig-publisher) or FSH syntax for ValueSets (fsh).
license: Apache-2.0
---

# Terminology for CQL and FHIR artifacts

> **litlfred fork.** Operation parameters are checked against the R4 core package; engine behaviour
> by running clinical-reasoning 4.13.0 (HAPI FHIR) on synthetic probe projects. Both are recorded in
> [resources/probes/2026-11-17/RESULTS.md](resources/probes/2026-11-17/RESULTS.md), cited as *P§n*.
> Behaviour against a live terminology server was not probed.

Targets **FHIR R4 (4.0.1)** terminology (<https://hl7.org/fhir/R4/terminology-module.html>) and
**CQL 1.5.3** terminology declarations (<https://cql.hl7.org/02-authorsguide.html#value-sets>).
Version pinning follows **CRMI** (<https://hl7.org/fhir/uv/crmi/>); the `crmi` skill holds its
profiles.

## Decide: value set or direct-reference code

- Use a **value set** when the concept is a clinical grouping that a steward maintains.
- Use a **direct-reference code** (`code "X": '1234' from "SNOMEDCT"`) only for a single concept with
  no grouping, and compare with `~` (equivalent), never `=`: `=` also compares `display` and
  `version`, so codes differing only in display or version are not equal, but are equivalent (*P§1*).
  A retrieve by a direct-reference code matches on system and code (*P§1*).
- `in` tests membership against the **expansion**; it is only as current as the expansion the engine
  sees. A local ValueSet with no committed `expansion` is not expanded from its `compose`: the engine
  asks the repository to run `$expand` (*P§3*).

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
| `ValueSet/$validate-code` | is this code in the value set | `url`, `code` + `system` (or `coding`/`codeableConcept`), `systemVersion` (one word here, unlike `$expand`), `display` |
| `CodeSystem/$lookup` | what does this code mean | `system`, `code`, `version`, `property` |
| `CodeSystem/$subsumes` | is A an ancestor of B | `codeA`, `codeB`, `system` |
| `ConceptMap/$translate` | map a code to another system | `url`, `code`, `system`, `target` |

## Reproducible evaluation: pin what the expansion used

An evaluation is reproducible only if the expansion is. Record and pin:

1. The **value set version** in the canonical (`url|version`).
2. The **code system versions** used to expand it, as `[system]|[version]` on `$expand` (*P§4*):
   `system-version` applies only where the value set names no version; `check-system-version` returns
   an error instead of an expansion if the value set names a different one; `force-system-version`
   overrides the value set's own version, which the spec flags as unsafe. For a reproducible
   expansion prefer `check-system-version`.
3. For a packaged artifact, a CRMI **manifest Library** whose `relatedArtifact` and expansion
   parameters list every value set and code system version; `$package` and `$data-requirements`
   produce or read it.

Keep the resulting `ValueSet.expansion` (with `expansion.parameter` showing the versions) beside the
test data, so a test run never needs the server.

## Local tooling and test runs

- clinical-reasoning (HAPI FHIR; the local runners `scripts/evaluate/run.sh`) reads an IG folder
  through `IgRepository`, which detects **one** layout for the whole project from the first of
  `input/tests/`, `input/vocabulary/`, `input/resources/` that exists (*P§2*):
  - flat tests → put ValueSets flat in `input/vocabulary/` (`ValueSet-<id>.json`);
  - tests grouped by type (`input/tests/patient/`) → `input/vocabulary/valueset/`, and the Library in
    `input/resources/library/`.
  A ValueSet in a `valueset/` folder of an otherwise flat project is **not read**: "Unable to locate
  ValueSet". Each ValueSet needs a committed `expansion`.
- **On a local folder, a retrieve by value set needs an in-memory or inline filter.** In the default
  terminology mode the engine turns `[Condition: "VS"]` into a `code:in=` search, which `IgRepository`
  refuses ("Only the NOT modifier is supported on tokens at this time"). Set the retrieve's
  terminology mode to `FILTER_IN_MEMORY` or `USE_INLINE_CODES` (`scripts/evaluate/run.sh … in-memory`),
  or test with `C.code in "VS"` in a `where`, which works in every mode (*P§3*).
- Errors come back as an `evaluation error` OperationOutcome in the result, not as an exception: read
  it before the values (*P§3*).
- A retrieve that finds nothing: check, in order, (1) the value set is expanded at all, (2) the code's
  `system` URI is exactly the one the expansion uses (`http://snomed.info/sct`, `http://loinc.org`,
  `http://hl7.org/fhir/sid/icd-10-cm` — not an OID or `urn:` form; a `urn:oid:` system matches
  nothing, *P§3*), (3) the code system version the
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
- [ ] Expansions used in tests are committed with their version parameters, in the folder the project's
      layout reads.

## Files

| file | what |
|---|---|
| [scripts/evaluate/run.sh](scripts/evaluate/run.sh) | `Library/$evaluate` with clinical-reasoning 4.13.0 on an IG folder, per definition and per terminology mode (Java 17+, Maven) |
| [resources/probes/2026-11-17/RESULTS.md](resources/probes/2026-11-17/RESULTS.md) | the probe projects (`make_probe.py`) and what each run returned |
