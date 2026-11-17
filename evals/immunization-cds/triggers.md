# immunization-cds Skill Trigger Prompts

## Should load the skill

1. Write CQL that decides whether a child is due for the second measles dose.
2. Our logic says the child has had two doses, but one record has no date. Is that right?
3. Should our PlanDefinition propose a MedicationRequest or an ImmunizationRecommendation for a due vaccine?
4. $apply gives a MedicationRequest that fails validation against cpg-immunizationrequest.
5. What forecastStatus codes can an ImmunizationRecommendation carry?

## Should not load the skill

1. Convert this DAK decision table to CQL and a PlanDefinition.
2. Return this recommendation as a CDS Hooks card.
3. Which CPG profile should a recommendation PlanDefinition claim?

Prompt 1 belongs to `smart-dak`, 2 to `cds-hooks`, 3 to `cpg`.
