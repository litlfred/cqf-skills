# Probe results, 2026-11-17

Two sources:

- **The CDS Hooks 2.0 specification** as HL7 publishes it at <https://cds-hooks.hl7.org/2.0/> (page
  fetched 2026-11-17, sha256 `0a7c607f810460e4bd96df9fe37e0aa4491d66b154a6ca0619c4ae1ad603606e`), and
  the hook pages of `cds-hooks/docs` at `c66c8b601e498451c82c00f9509ee4c15030a701` (2026-11-12).
- **clinical-reasoning 4.13.0**: `cqf-fhir-cr-hapi`'s CDS Hooks classes (on `hapi-fhir-server-cds-hooks`
  8.12.0), read in source and run through `scripts/encode/run.sh` on the project in this folder
  (`make_probe.py`, synthetic; patient `adult-1`, born 1980). `output/` holds what each run printed;
  `scripts/check_cds.py` judged each against 2.0.

## 1. Discovery (`CrDiscoveryService`, `CrDiscoveryElement.getCdsServiceJson`)

- `PlanDefinition/cds-probe` (a top-level action with a `named-event` trigger named `patient-view`):
  `{"services": [{"hook": "patient-view", "title", "description", "id": "cds-probe", "prefetch":
  {"item1": "Patient?_id={{context.patientId}}"}}]}`. Hook = the first `named-event` trigger's `name`;
  `id` = the PlanDefinition id; `title` and `description` copied. Check: **0 findings**.
- `PlanDefinition/no-trigger` (no trigger): **not a service** (`resolveService` returns null).
- Prefetch: `Patient?_id={{context.patientId}}` is always added unless an equivalent is present; then one
  `itemN` per data requirement of the primary Library (or the module-definition Library named by the
  CRMI effective-data-requirements extension), keys `item1`, `item2`, …

## 2. Cards (`CdsResponseEncoderService`): what each action becomes

On R4 the service runs **`$r5.apply`** (`ICdsCrService.invokeApply`) and encodes the first Bundle
entry, the RequestGroup: **one card per top-level action**.

| PlanDefinition action | card | 2.0 check |
|---|---|---|
| `title` | `summary` | |
| `description` | `detail` | |
| `priority` `routine` / `urgent` / `stat` | `indicator` `info` / `warning` / `critical` | |
| no `priority` (`one-no-priority`) | **no `indicator`** | `indicator` is REQUIRED |
| `priority` `asap` (`asap`) | **throws** `Invalid priority code: asap` | |
| first `documentation` (`one-doc`): `display`, `url`, `document.url` | `source.label`, `source.url`, `source.icon` | |
| no `documentation` (`one-routine`) | **no `source`** | `source` is REQUIRED |
| PlanDefinition `relatedArtifact` with a `url` (`one-link`) | a `link` (`label` = `display`, `type` = the first extension's value, else `absolute`) on **every** card | |
| no such `relatedArtifact` | **`"links": []`** | empty arrays are not allowed |
| `selectionBehavior` with child actions (`choose`) | `selectionBehavior` copied, **no `suggestions`** | |
| `selectionBehavior` `exactly-one` (`choose-exactly-one`) | **`exactly-one` copied** | only `at-most-one` and `any` are allowed; a client MUST treat other values as an error |

- No card has a **`uuid`** (`setUuid` is never called for a card), so the feedback endpoint, which
  identifies a card by `card.uuid`, cannot be used.
- **Suggestions are never added**: `resolveAction` calls `action.getAction().forEach(this::resolveSuggestion)`
  and discards each result. `systemActions` are never produced (commented out in the source).
- `two-true` (two applicable actions): two cards.

## 3. A top-level action that does not apply

`one-false` (its only action's condition is false), `true-and-false` (one true, one false) and
`cds-probe`: **`IllegalArgumentException: element can not be null`**, not `{"cards": []}`.

`ApplyProcessor` sets each top-level action with
`requestOrchestration.setValue("action", Collections.singletonList(processAction(...)))`, and
`processAction` returns `null` for an action whose condition is false. The RequestGroup keeps a `null`
action, which the FHIR JSON parser skips (`apply` prints only the applicable action) and the encoder
does not. The same code is in 4.15.0 (`ApplyProcessor` lines 226–231; `CdsResponseEncoderService`
line 144). So a patient for whom any top-level action does not apply gets an error from the service.

## 4. The specification (2.0)

The rules `scripts/check_cds.py` applies, each from the 2.0 page:

- Use of JSON: no `null`, no empty string, array or object, except `cards: []` for no guidance and
  `services: []` for no services.
- Discovery: `services[]`, each with `hook`, `description`, `id` REQUIRED; `title` RECOMMENDED;
  `prefetch`, `usageRequirements` OPTIONAL.
- Request: `hook`, `hookInstance`, `context` REQUIRED; `fhirServer` REQUIRED if `fhirAuthorization`;
  `fhirAuthorization` with `access_token`, `token_type` (`Bearer`), `expires_in`, `scope`, `subject`.
- Prefetch tokens: `{{context.<root-level primitive field>}}`, or `userPractitionerId`,
  `userPractitionerRoleId`, `userPatientId`, `userRelatedPersonId`.
- Response: `cards` REQUIRED, `systemActions` OPTIONAL. Card: `summary` (under 140 characters),
  `indicator` (`info`, `warning`, `critical`), `source` (with `label`) REQUIRED; `selectionBehavior`
  REQUIRED with `suggestions`, values `at-most-one`, `any`; override reasons are Codings with a
  `display`; links with `label`, `url`, `type` (`absolute`, `smart`), `appContext` only for `smart`.
- Action: `type` (`create`, `update`, `delete`) and `description` REQUIRED; `resource` holds the whole
  resource for create and update; `resourceId` for delete.
- Feedback: `feedback[]`, each with `card`, `outcome` (`accepted`, `overridden`) and `outcomeTimestamp`
  (RFC 3339, UTC) REQUIRED; `acceptedSuggestions` REQUIRED when accepted.
- Status 412 when the service cannot get the FHIR data it needs.
- Client JWT: header `alg`, `kid`, `typ` (`JWT`) REQUIRED, `jku` OPTIONAL; payload `iss`, `aud` (the
  service endpoint URL), `exp`, `iat`, `jti` REQUIRED, `tenant` OPTIONAL; never `none` nor a symmetric
  (HMAC) algorithm; ES384 and RS384 RECOMMENDED.

Hooks in `cds-hooks/docs` and their maturity: `patient-view` 5 (Mature), `order-sign` 5, `order-select`
4, `order-review` 3, `medication-prescribe` 2, `allergyintolerance-create`, `appointment-book`,
`encounter-discharge`, `encounter-start`, `medication-refill`, `problem-list-item-create` 1,
`order-dispatch` 0. `patient-view` context: `userId`, `patientId` REQUIRED, `encounterId` OPTIONAL, all
three usable as prefetch tokens; `order-sign` adds `draftOrders` (REQUIRED, not a prefetch token).
