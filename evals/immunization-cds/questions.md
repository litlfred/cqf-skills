# immunization-cds Skill Test Questions

Answer each in a few sentences, as to a knowledge engineer. The key is in `answers.md`; don't read it.

**IM-01.** `Count([Immunization: "MCV"])` says 3 for a child who has had one dose. What is wrong?

**IM-02.** One completed dose has `occurrenceString` "at the 9-month visit". How does it affect a rule "second dose due 4 weeks after the first"?

**IM-03.** Can I compare `protocolApplied.doseNumber` with an integer?

**IM-04.** Our `cpg-immunizationactivity` ActivityDefinition, run through `$apply` on a HAPI FHIR server (clinical-reasoning 4.13.0), produces a MedicationRequest that fails validation against `cpg-immunizationrequest`. Why, and what is the fix?

**IM-05.** We generate ImmunizationRecommendations with `$apply` from an ActivityDefinition of kind ImmunizationRecommendation. A child whose schedule is complete is shown as "due". Why?

**IM-06.** Which element of an ImmunizationRecommendation must say when a dose is due, and with which code?
