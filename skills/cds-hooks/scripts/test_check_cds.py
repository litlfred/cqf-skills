from check_cds import check

GOOD_CARD = {"summary": "Due for a vaccine", "indicator": "info", "source": {"label": "Example guideline"}}


def test_empty_cards_is_valid():
    assert check("response", {"cards": []}) == []


def test_good_card_is_valid():
    assert check("response", {"cards": [GOOD_CARD]}) == []


def test_card_without_indicator_and_source():
    f = check("response", {"cards": [{"summary": "x"}]})
    assert "ERROR $.cards[0]: 'indicator' is REQUIRED" in f
    assert "ERROR $.cards[0]: 'source' is REQUIRED" in f


def test_empty_links_array_is_an_error():
    f = check("response", {"cards": [dict(GOOD_CARD, links=[])]})
    assert any("$.cards[0].links" in x and "empty" in x for x in f)


def test_suggestions_need_selection_behavior_and_spec_values():
    card = dict(GOOD_CARD, suggestions=[{"label": "Order"}])
    assert any("selectionBehavior" in x for x in check("response", {"cards": [card]}))
    card = dict(card, selectionBehavior="exactly-one")
    assert any("at-most-one, any" in x for x in check("response", {"cards": [card]}))


def test_action_rules():
    a = {"type": "delete", "description": "Remove", "resource": "ServiceRequest/1"}
    f = check("response", {"cards": [dict(GOOD_CARD, suggestions=[{"label": "x", "actions": [a]}], selectionBehavior="any")]})
    assert any("resourceId" in x for x in f)


def test_discovery_prefetch_tokens():
    doc = {"services": [{"hook": "patient-view", "id": "s", "description": "d",
                         "prefetch": {"p": "Patient/{{context.patientId}}", "m": "Medication/{{context.medication.id}}",
                                      "u": "PractitionerRole?_id={{userPractitionerRoleId}}"}}]}
    f = check("discovery", doc)
    assert f == ["ERROR $.services[0].prefetch.m: prefetch token '{{context.medication.id}}' is not a root-level context field"]


def test_request_authorization_needs_fhir_server():
    doc = {"hook": "patient-view", "hookInstance": "u", "context": {"patientId": "1"},
           "fhirAuthorization": {"access_token": "t", "token_type": "Bearer", "expires_in": 300, "scope": "s", "subject": "c"}}
    assert check("request", doc) == ["ERROR $: 'fhirServer' is REQUIRED when 'fhirAuthorization' is present"]


def test_feedback():
    ok = {"feedback": [{"card": "u", "outcome": "overridden", "outcomeTimestamp": "2020-12-11T00:00:00Z"}]}
    assert check("feedback", ok) == []
    bad = {"feedback": [{"card": "u", "outcome": "accepted", "outcomeTimestamp": "2020-12-11 00:00"}]}
    f = check("feedback", bad)
    assert any("acceptedSuggestions" in x for x in f) and any("RFC 3339" in x for x in f)
