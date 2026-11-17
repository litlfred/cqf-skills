---
name: cds-hooks
description: Builds, reviews and debugs CDS Hooks 2.0 services and clients — discovery documents, hook requests and context, prefetch templates and tokens, fhirAuthorization, cards (summary, indicator, source, suggestions, links, selectionBehavior, overrideReasons), systemActions, the feedback endpoint and client JWT authentication — and what clinical-reasoning 4.13.0 (HAPI FHIR) makes of a PlanDefinition when it serves one as a CDS Service. Use when writing or checking a /cds-services discovery response, a card or a feedback POST, choosing a hook such as patient-view or order-sign, writing prefetch, or when a PlanDefinition-backed CDS service returns an error or a card missing its indicator, source or suggestions. Not for PlanDefinition $apply itself (plan-definition), CPG profiles (cpg) or SMART app launch.
license: Apache-2.0
---

# CDS Hooks

> **litlfred fork.** Specification claims are from **CDS Hooks 2.0** as HL7 publishes it
> (<https://cds-hooks.hl7.org/2.0/>); clinical-reasoning claims are from its source and from running
> it on a synthetic probe. Both are recorded in
> [resources/probes/2026-11-17/RESULTS.md](resources/probes/2026-11-17/RESULTS.md), cited as *P§n*.

Related skills: `plan-definition` for `$apply` and actions, `cpg` for the profiles, `cql` for the logic
behind conditions, `fhir` for the resources in prefetch and actions.

## The exchange

| step | who | endpoint | body |
|---|---|---|---|
| discovery | client → service | `GET {base}/cds-services` | `{"services": [...]}` (an empty array if none) |
| call | client → service | `POST {base}/cds-services/{id}` | `hook`, `hookInstance` (UUID), `context`; optional `fhirServer`, `fhirAuthorization`, `prefetch` |
| response | service → client | 200 | `{"cards": [...]}` and optional `systemActions`; **`{"cards": []}` for no guidance** |
| feedback | client → service | `POST {base}/cds-services/{id}/feedback` | `{"feedback": [{"card": <card.uuid>, "outcome": "accepted"\|"overridden", "outcomeTimestamp", ...}]}` |

A service that cannot get the FHIR data it needs answers **412**. Every call from an authenticating
client carries `Authorization: Bearer <JWT>` (*P§4*).

## Rules that trip implementations (*P§4*)

- **No `null`, `""`, `[]` or `{}`** anywhere: omit an optional attribute instead. The only empty value
  allowed is `cards: []` (and `services: []`).
- A card needs `summary` (under 140 characters), `indicator` (`info`, `warning`, `critical`) and
  `source` with a `label`. `detail` is GitHub-flavoured Markdown.
- `suggestions` require `selectionBehavior`, which is `at-most-one` or `any` only; a client MUST treat
  any other value as an error. FHIR's `exactly-one`, `all`, `one-or-more` have no CDS Hooks equivalent.
- An action is `create` or `update` with the **whole** resource in `resource`, or `delete` with
  `resourceId`. Actions inside one suggestion are applied together, as a transaction.
- `overrideReasons` are Codings, each with a `display`.
- A link has `label`, `url` and `type` (`absolute`, or `smart` for a SMART launch); `appContext` only on
  `smart` links.
- Give each card a `uuid`: feedback names the card by it.
- `fhirServer` is REQUIRED when `fhirAuthorization` is sent; `fhirAuthorization` has `access_token`,
  `token_type` `Bearer`, `expires_in`, `scope`, `subject` (and `patient` with patient scopes).
- JWT: header `alg`, `kid`, `typ: JWT` (`jku` optional); payload `iss`, `aud` (the URL of the endpoint
  being called), `exp`, `iat`, `jti` (`tenant` optional). Never `none` or an HMAC algorithm; ES384 or
  RS384 recommended.

## Prefetch

- A template is a relative FHIR read or search with tokens: `{{context.patientId}}`, any **root-level
  primitive** context field the hook marks as a prefetch token, or `{{userPractitionerId}}`,
  `{{userPractitionerRoleId}}`, `{{userPatientId}}`, `{{userRelatedPersonId}}`.
  `{{context.medication.id}}` is invalid.
- Keep to the subset the spec recommends: instance reads; type searches by reference; token equality
  (and `:in`); date searches with `eq`, `lt`, `gt`, `ge`, `le`; `_count`; `_sort`.
- The client may satisfy none, some or all; it omits a key it did not satisfy and may page results.
  The service checks what arrived and fetches the rest itself (with `fhirAuthorization`) or answers 412.

## Hooks

| hook | maturity | context (REQUIRED; *optional*) |
|---|---|---|
| `patient-view` | 5 Mature | `userId`, `patientId`; *`encounterId`* |
| `order-sign` | 5 Mature | `userId`, `patientId`, `draftOrders` (Bundle); *`encounterId`* |
| `order-select` | 4 Documented | `userId`, `patientId`, `selections`, `draftOrders`; *`encounterId`* |
| `order-review` | 3 Considered | `userId`, `patientId`, `orders`; *`encounterId`* |
| `medication-prescribe` | 2 Tested | `userId`, `patientId`, `medications`; *`encounterId`* |

Hooks are versioned separately from the spec (`hookVersion`); lower-maturity hooks
(`encounter-start`, `encounter-discharge`, `appointment-book`, …) may change. `draftOrders`,
`selections` and similar objects are not prefetch tokens.

## A PlanDefinition as a CDS Service: clinical-reasoning 4.13.0

HAPI FHIR's CR module serves PlanDefinitions as CDS Services. What it does (*P§1–§3*):

- **Discovery.** A PlanDefinition is a service only if a top-level action has a trigger of type
  `named-event`; its `name` is the hook. `id` is the PlanDefinition id; `title` and `description` are
  copied. Prefetch always has `Patient?_id={{context.patientId}}`, then one `itemN` per data requirement.
- **Call.** On R4 it runs `$r5.apply` and makes **one card per top-level action** of the RequestGroup:
  `title` → `summary`, `description` → `detail`, `priority` `routine`/`urgent`/`stat` →
  `info`/`warning`/`critical`, the first `documentation` → `source` (`display` → `label`, `url`,
  `document.url` → `icon`), and every PlanDefinition `relatedArtifact` with a `url` → a link on every
  card.

**Its known defects, and how to author around them:**

| what happens | so |
|---|---|
| A top-level action whose condition is false makes the service **throw** (`element can not be null`), for that patient, instead of returning `{"cards": []}`; also in 4.15.0 (*P§3*) | Test with an ineligible patient. Until fixed, keep every top-level action unconditional, or expect errors for ineligible patients |
| No `priority` → no `indicator`; another code (`asap`) → the call throws | Set `priority` `routine`, `urgent` or `stat` on every top-level action |
| No `documentation` → no `source` | Give every top-level action a `documentation` with `display` |
| No `relatedArtifact` URL → `"links": []` | Give the PlanDefinition one `relatedArtifact` with `url` and `display` |
| Child actions are **never** returned as suggestions, though `selectionBehavior` is copied — FHIR values like `exactly-one` included | Do not rely on suggestions from this service |
| Cards have no `uuid` | Feedback cannot identify cards |

Check any response with `scripts/check_cds.py response <file>` before trusting it.

## Run it locally

- `scripts/check_cds.py discovery|request|response|feedback FILE` checks a JSON document against the 2.0
  rules above (Python 3.9+, no dependencies).
- `scripts/encode/run.sh PROJECT discovery|response|apply PLAN_DEFINITION_ID [Patient/<id>]` shows what
  clinical-reasoning 4.13.0 makes of a PlanDefinition in an IG folder (Java 17+, Maven; about 320 MB of
  dependencies on first run).

## Example: a valid response (synthetic)

```json
{
  "cards": [{
    "uuid": "6b2c5f4e-2f0a-4f1b-9a51-0d3c2a7e8b11",
    "summary": "Due for the second dose",
    "indicator": "info",
    "source": {"label": "Example immunization guideline", "url": "https://example.org/guideline"},
    "suggestions": [{
      "label": "Propose the dose",
      "actions": [{"type": "create", "description": "Propose the second dose",
                   "resource": {"resourceType": "ServiceRequest", "status": "draft", "intent": "proposal",
                                "subject": {"reference": "Patient/example"}, "code": {"text": "Second dose"}}}]
    }],
    "selectionBehavior": "at-most-one"
  }]
}
```

## Files

| file | what |
|---|---|
| [scripts/check_cds.py](scripts/check_cds.py) | the 2.0 checker, with its tests |
| [scripts/encode/run.sh](scripts/encode/run.sh) | clinical-reasoning's discovery and card encoding on a local PlanDefinition |
| [resources/probes/2026-11-17/RESULTS.md](resources/probes/2026-11-17/RESULTS.md) | the probe, the spec extract and what each run returned |
