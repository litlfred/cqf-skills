#!/usr/bin/env python3
"""Check a CDS Hooks 2.0 JSON document against the specification's rules.

    python3 check_cds.py discovery FILE   # GET {baseUrl}/cds-services
    python3 check_cds.py request FILE     # POST {baseUrl}/cds-services/{id}
    python3 check_cds.py response FILE    # the service's response
    python3 check_cds.py feedback FILE    # POST {baseUrl}/cds-services/{id}/feedback

Prints one line per finding ("ERROR path: message") and exits 1 if there is any. Each rule names the
section of https://cds-hooks.hl7.org/2.0/ it comes from. Python 3.9+, standard library only; no
network.
"""
import json
import re
import sys

INDICATORS = ("info", "warning", "critical")
SELECTION = ("at-most-one", "any")
ACTION_TYPES = ("create", "update", "delete")
LINK_TYPES = ("absolute", "smart")
USER_TOKENS = ("userPractitionerId", "userPractitionerRoleId", "userPatientId", "userRelatedPersonId")


class Checker:
    def __init__(self):
        self.findings = []

    def err(self, path, msg):
        self.findings.append(f"ERROR {path}: {msg}")

    # "Use of JSON": no null and no empty value unless the spec says so (cards may be []).
    def no_null_or_empty(self, value, path, allow_empty=()):
        if value is None:
            self.err(path, "null is not allowed (Use of JSON)")
        elif value in ("", [], {}) and path not in allow_empty:
            self.err(path, "an empty value is not allowed; omit the attribute (Use of JSON)")
        elif isinstance(value, dict):
            for k, v in value.items():
                self.no_null_or_empty(v, f"{path}.{k}", allow_empty)
        elif isinstance(value, list):
            for i, v in enumerate(value):
                self.no_null_or_empty(v, f"{path}[{i}]", allow_empty)

    def required(self, obj, path, fields):
        for f in fields:
            if f not in obj:
                self.err(path, f"'{f}' is REQUIRED")

    def string(self, obj, path, field):
        if field in obj and not isinstance(obj[field], str):
            self.err(f"{path}.{field}", "must be a string")

    def coding(self, c, path):
        if not isinstance(c, dict):
            self.err(path, "must be a Coding object")
            return
        self.required(c, path, ("code", "system"))  # Data Types > Coding

    # Discovery > Response
    def discovery(self, doc):
        self.no_null_or_empty(doc, "$", allow_empty=("$.services",))
        if not isinstance(doc.get("services"), list):
            self.err("$", "'services' must be an array (an empty one if no services)")
            return
        for i, s in enumerate(doc["services"]):
            p = f"$.services[{i}]"
            self.required(s, p, ("hook", "description", "id"))
            for f in ("hook", "title", "description", "id", "usageRequirements"):
                self.string(s, p, f)
            for key, tmpl in (s.get("prefetch") or {}).items():
                self.prefetch_template(tmpl, f"{p}.prefetch.{key}")

    # Providing FHIR Resources > Prefetch tokens
    def prefetch_template(self, tmpl, path):
        if not isinstance(tmpl, str):
            self.err(path, "a prefetch template is a string")
            return
        for tok in re.findall(r"\{\{(.*?)\}\}", tmpl):
            tok = tok.strip()
            if tok in USER_TOKENS:
                continue
            if not tok.startswith("context."):
                self.err(path, f"prefetch token '{{{{{tok}}}}}' is neither context.<field> nor a user token")
            elif tok.count(".") > 1:
                self.err(path, f"prefetch token '{{{{{tok}}}}}' is not a root-level context field")

    # Calling a CDS Service > HTTP Request
    def request(self, doc):
        self.no_null_or_empty(doc, "$")
        self.required(doc, "$", ("hook", "hookInstance", "context"))
        if "fhirAuthorization" in doc:
            if "fhirServer" not in doc:
                self.err("$", "'fhirServer' is REQUIRED when 'fhirAuthorization' is present")
            a = doc["fhirAuthorization"]
            self.required(a, "$.fhirAuthorization", ("access_token", "token_type", "expires_in", "scope", "subject"))
            if a.get("token_type") not in (None, "Bearer"):
                self.err("$.fhirAuthorization.token_type", "fixed value 'Bearer'")

    # CDS Service Response
    def response(self, doc):
        self.no_null_or_empty(doc, "$", allow_empty=("$.cards",))
        if not isinstance(doc.get("cards"), list):
            self.err("$", "'cards' is REQUIRED and is an array (an empty one for no guidance)")
            return
        for i, c in enumerate(doc["cards"]):
            self.card(c, f"$.cards[{i}]")
        for i, a in enumerate(doc.get("systemActions", [])):
            self.action(a, f"$.systemActions[{i}]")

    def card(self, c, p):
        self.required(c, p, ("summary", "indicator", "source"))
        s = c.get("summary")
        if isinstance(s, str) and len(s) >= 140:
            self.err(f"{p}.summary", "must be under 140 characters")
        if "indicator" in c and c["indicator"] not in INDICATORS:
            self.err(f"{p}.indicator", f"must be one of {', '.join(INDICATORS)}")
        src = c.get("source")
        if isinstance(src, dict):
            self.required(src, f"{p}.source", ("label",))
            if "topic" in src:
                self.coding(src["topic"], f"{p}.source.topic")
        if "suggestions" in c:
            if "selectionBehavior" not in c:
                self.err(p, "'selectionBehavior' is REQUIRED when 'suggestions' are present")
            for j, sg in enumerate(c["suggestions"]):
                sp = f"{p}.suggestions[{j}]"
                self.required(sg, sp, ("label",))
                for k, a in enumerate(sg.get("actions", [])):
                    self.action(a, f"{sp}.actions[{k}]")
        if "selectionBehavior" in c and c["selectionBehavior"] not in SELECTION:
            self.err(f"{p}.selectionBehavior", f"must be one of {', '.join(SELECTION)}; a client MUST treat any other value as an error")
        for j, r in enumerate(c.get("overrideReasons", [])):
            self.coding(r, f"{p}.overrideReasons[{j}]")
            if isinstance(r, dict) and "display" not in r:
                self.err(f"{p}.overrideReasons[{j}]", "an override reason MUST have a display")
        for j, l in enumerate(c.get("links", [])):
            lp = f"{p}.links[{j}]"
            self.required(l, lp, ("label", "url", "type"))
            if "type" in l and l["type"] not in LINK_TYPES:
                self.err(f"{lp}.type", "must be absolute or smart")
            if "appContext" in l and l.get("type") != "smart":
                self.err(f"{lp}.appContext", "only valid on a link of type smart")

    def action(self, a, p):
        self.required(a, p, ("type", "description"))
        t = a.get("type")
        if t is not None and t not in ACTION_TYPES:
            self.err(f"{p}.type", "must be create, update or delete")
        if t in ("create", "update") and not isinstance(a.get("resource"), dict):
            self.err(p, f"a {t} action carries the whole FHIR resource in 'resource'")
        if t == "delete" and "resourceId" not in a:
            self.err(p, "a delete action SHOULD give 'resourceId' (a string id in 'resource' is deprecated)")

    # Feedback
    def feedback(self, doc):
        self.no_null_or_empty(doc, "$")
        if not isinstance(doc.get("feedback"), list):
            self.err("$", "'feedback' is an array")
            return
        for i, f in enumerate(doc["feedback"]):
            p = f"$.feedback[{i}]"
            self.required(f, p, ("card", "outcome", "outcomeTimestamp"))
            if f.get("outcome") not in (None, "accepted", "overridden"):
                self.err(f"{p}.outcome", "must be accepted or overridden")
            if f.get("outcome") == "accepted" and "acceptedSuggestions" not in f:
                self.err(p, "'acceptedSuggestions' is REQUIRED for an accepted outcome")
            ts = f.get("outcomeTimestamp")
            if isinstance(ts, str) and not re.fullmatch(r"\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d(\.\d+)?Z", ts):
                self.err(f"{p}.outcomeTimestamp", "must be an RFC 3339 date-time in UTC (ending in Z)")


def check(kind, doc):
    c = Checker()
    getattr(c, kind)(doc)
    return c.findings


def main():
    if len(sys.argv) != 3 or sys.argv[1] not in ("discovery", "request", "response", "feedback"):
        print(__doc__.strip())
        return 2
    with open(sys.argv[2]) as fh:
        findings = check(sys.argv[1], json.load(fh))
    for f in findings:
        print(f)
    print(f"{len(findings)} finding(s)")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
