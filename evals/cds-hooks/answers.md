# cds-hooks answers

**CH-01.** HTTP 200 with `{"cards": []}`. *Fail if* it returns 204, `null` or omits `cards`.

**CH-02.** Yes: CDS Hooks 2.0 forbids empty values; omit `links` and `detail` instead. *Fail if* it says empty is fine.

**CH-03.** CDS Hooks has only `at-most-one` and `any`; a client must treat other values as an error. Map to `at-most-one` (and enforce one choice in the client or the content), never send `exactly-one`.

**CH-04.** The encoder maps `priority` (routine/urgent/stat → info/warning/critical) and the first `documentation` (→ source); without them the card lacks both, although 2.0 requires them. Set `priority` and a `documentation` with `display` on every top-level action.

**CH-05.** In 4.13.0 (and 4.15.0) a top-level action whose condition is false leaves a null action in the RequestGroup, and the CDS encoder throws on it instead of returning no card. *Pass if* it names the non-applicable top-level action as the cause and suggests testing with an ineligible patient or restructuring.

**CH-06.** Any asymmetric algorithm; never `none` or HMAC (symmetric); ES384 or RS384 recommended.

**TK-01.** `check_cds.py response response.json` reports 0 findings; one card with `summary`, `indicator`, `source.label` "Example immunization guideline", a `uuid`, one suggestion with a `create` action carrying a whole ServiceRequest (status `draft`), and `selectionBehavior` `at-most-one` or `any`.
