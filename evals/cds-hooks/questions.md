# cds-hooks Skill Test Questions

Answer each in a few sentences, as to an engineer integrating CDS. The key is in `answers.md`; don't read it.

**CH-01.** Our service has nothing to say for this patient. What does it return?

**CH-02.** We return `"links": []` and `"detail": ""` on every card. Any problem?

**CH-03.** A PlanDefinition action has `selectionBehavior: exactly-one`. What should the card carry?

**CH-04.** Served by HAPI FHIR (clinical-reasoning 4.13.0), our PlanDefinition's cards have no indicator and no source. Why, and how do we fix it in the content?

**CH-05.** The same service answers "element can not be null" for children but works for adults; the PlanDefinition's top-level actions have applicability conditions on age. Why?

**CH-06.** Which JWT signing algorithms may a CDS client use?

## Task

**TK-01.** Write the CDS Hooks 2.0 response of a service that tells the clinician the patient is due for a second dose, cites "Example immunization guideline" as source, and offers one suggestion that creates a draft ServiceRequest for the dose. Save it as `response.json`.
