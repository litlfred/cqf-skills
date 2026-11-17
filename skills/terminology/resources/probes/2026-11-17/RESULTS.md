# Probe results, 2026-11-17

Two sources: the FHIR R4 core package, and runs of clinical-reasoning **4.13.0**
(`org.opencds.cqf.fhir:cqf-fhir-cr`, HAPI FHIR 8.12.0) through `scripts/evaluate/run.sh`, which runs
`Library/$evaluate` against a folder through the engine's `IgRepository`.

`make_probe.py` writes three projects with the same library `TerminologyProbe`, two ValueSets and one
patient `p1` with three Conditions. All codes are illustrative, not real SNOMED CT concepts:

| | ValueSets | tests and resources |
|---|---|---|
| `project-a` | `input/vocabulary/valueset/` | flat (`input/tests/`, `input/resources/`) |
| `project-b` | `input/vocabulary/` (flat) | flat |
| `project-c` | `input/vocabulary/valueset/` | by type (`input/tests/patient/`, `input/tests/condition/`, `input/resources/library/`) |

- `vs-expanded`: `compose` and a committed `expansion` with `http://snomed.info/sct` `1000001`,
  `1000002`.
- `vs-compose`: `compose` only (`1000003`), **no expansion**.
- `vs-missing`: declared in the CQL, absent from the project.
- Conditions: `c1` `http://snomed.info/sct|1000001` display `Display A`; `c2`
  `urn:oid:2.16.840.1.113883.6.96|1000002` (the SNOMED CT OID as system); `c3`
  `http://snomed.info/sct|1000003`.
- `code "C1 Other Display": '1000001' from "SCT" display 'Display B'`.

Each definition is evaluated on its own run, under each retrieve terminology mode of the engine's
`RetrieveSettings.TERMINOLOGY_FILTER_MODE`: `auto` (the default), `inline-codes`
(`USE_INLINE_CODES`), `in-memory` (`FILTER_IN_MEMORY`).

## 1. Code equality and equivalence

Same in every project and mode:

| expression | result |
|---|---|
| `Code { code: '1', system: 's', display: 'A' } = Code { code: '1', system: 's', display: 'B' }` | **false** |
| the same with `~` | **true** |
| `Code { code: '1', system: 's', version: '1' } = Code { …, version: '2' }` | **false** |
| the same with `~` | **true** |
| `[Condition] C where C.code ~ "C1 Other Display"` (display `Display A` vs `Display B`) | `c1` |
| `[Condition: "C1 Other Display"]` (retrieve by direct-reference code) | `c1` |

## 2. Where the ValueSets are found

`IgConventions.autoDetect` picks **one** layout for the whole project. It looks at the first category
folder that exists, in the order `input/tests`, `input/vocabulary`, `input/resources`. If that folder
has type subfolders (`patient/`, `valueset/`, …), every category is read by type; otherwise every
category is read flat.

- `project-a` (flat tests, `vocabulary/valueset/`): **`Unable to locate ValueSet …/vs-expanded`**, in
  every mode. The ValueSets are not read.
- `project-b` (flat everywhere): the ValueSets are found.
- `project-c` (by type everywhere): the ValueSets are found. A by-type project also needs its Library
  in `input/resources/library/`: with the Library flat in `input/resources/`, the run throws
  `Resource Library/TerminologyProbe is not known`.

## 3. Retrieve by value set, by mode (`project-b`, and the same in `project-c`)

| definition | `auto` | `inline-codes` | `in-memory` |
|---|---|---|---|
| `[Condition: "Expanded"]` | **error** `Only the NOT modifier is supported on tokens at this time` | `c1` | `c1` |
| `[Condition: "ComposeOnly"]` (no expansion) | error, as above | **error** `HAPI-2542: instance-level invoke is not supported by this repository` | same |
| `[Condition: "Missing"]` | error, as above | **error** `Unable to locate ValueSet …/vs-missing` | same |
| `[Condition] C where C.code in "Expanded"` | `c1` | `c1` | `c1` |

- In `auto`, a value-set retrieve becomes a `code:in=<url>` search, and `IgRepository` supports no
  token modifier but `:not`. `in` inside a `where` does not search, so it works in every mode.
- A ValueSet with no committed `expansion` makes the engine invoke `$expand` on the repository, which
  a folder cannot do. It is not expanded from `compose`.
- **`c2` matches nothing**: its system is the OID form, the expansion's is `http://snomed.info/sct`.
- Errors come back as an `evaluation error` OperationOutcome parameter, not as an exception.

## 4. R4 terminology operations (FHIR R4 core package)

From `hl7.fhir.r4.core` 4.0.1 (package sha256
`ebd7731df7d36b5b7d39d5fb6c9d77b44bb7fe5742f1a2e87f164738c3289d44`), the `in` parameters of:

- `ValueSet/$expand`: `url`, `valueSet`, `valueSetVersion`, `context`, `contextDirection`, `filter`,
  `date`, `offset`, `count`, `includeDesignations`, `designation`, `includeDefinition`, `activeOnly`,
  `excludeNested`, `excludeNotForUI`, `excludePostCoordinated`, `displayLanguage`, `exclude-system`,
  `system-version`, `check-system-version`, `force-system-version`.
  - `system-version`: the version to use for a system **if the value set does not specify one**.
  - `check-system-version`: if the value set specifies a different version, **an error is returned**
    instead of the expansion.
  - `force-system-version`: **overrides** any version in the value set and those it depends on;
    flagged by the spec as having obvious safety issues.
  - All three are `canonical`, `0..*`, written `[system]|[version]`.
- `ValueSet/$validate-code`: `url`, `context`, `valueSet`, `valueSetVersion`, `code`, `system`,
  `systemVersion`, `display`, `coding`, `codeableConcept`, `date`, `abstract`, `displayLanguage`.
- `CodeSystem/$lookup`: `code`, `system`, `version`, `coding`, `date`, `displayLanguage`, `property`.
- `CodeSystem/$subsumes`: `codeA`, `codeB`, `system`, `version`, `codingA`, `codingB`.
- `ConceptMap/$translate`: `url`, `conceptMap`, `conceptMapVersion`, `code`, `system`, `version`,
  `source`, `coding`, `codeableConcept`, `target`, `targetsystem`, `dependency`, `reverse`.
