# terminology Skill Trigger Prompts

## Should load the skill

1. My retrieve `[Condition: "Diabetes"]` returns nothing though the patient has a diabetes Condition.
2. Expand this ValueSet and pin the SNOMED CT version for a reproducible test run.
3. Should I use `=` or `~` to compare a direct-reference code in CQL?
4. Translate these local codes to LOINC with ConceptMap/$translate.

## Should not load the skill

1. Write a FSH ValueSet with an include rule.
2. Configure the IG Publisher's terminology server in ig.ini.
3. Write the CQL for the numerator.

Prompt 1 belongs to `fsh`, 2 to `ig-publisher`, 3 to `cql`.
