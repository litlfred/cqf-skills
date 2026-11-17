# cds-hooks Skill Trigger Prompts

## Should load the skill

1. Write the discovery response for a CDS service on the patient-view hook that needs the patient's last HbA1c.
2. Our CDS Hooks card is rejected by the EHR; here is the JSON. What's wrong?
3. Can I use {{context.medication.id}} in a prefetch template?
4. Our HAPI FHIR CR server returns "element can not be null" for some patients when we call the CDS service.
5. What goes in the feedback POST when the clinician overrides a card?

## Should not load the skill

1. Run $apply on this PlanDefinition and explain the CarePlan.
2. Which CPG profile should this PlanDefinition claim?
3. How does a SMART app do an EHR launch?

Prompt 1 belongs to `plan-definition`, 2 to `cpg`; prompt 3 is SMART App Launch.
