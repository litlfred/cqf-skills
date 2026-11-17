# smart-dak Skill Trigger Prompts

## Should load the skill

1. Convert decision table ANC.DT.01 from the antenatal care DAK into CQL and a PlanDefinition.
2. Which FHIR resource should carry the DAK's program indicators in our L3 IG?
3. Check our L3 IG covers every decision table in the DAK.
4. How do I name the CQL library for an immunization DAK decision table?

## Should not load the skill

1. What does the cpg-recommendationdefinition profile require?
2. Run $apply on this PlanDefinition.
3. Fix this SUSHI error.

Prompt 1 belongs to `cpg`, 2 to `plan-definition`, 3 to `fsh`.
