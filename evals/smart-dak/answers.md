# smart-dak answers

**SD-01.** One definition per rule row (IMMZ: `"<output> Case N"`), the output as the `or` of its cases, row conditions mutually exclusive, and a test that no input matches two rows. *Fail if* encoded as first-match with no overlap test.

**SD-02.** One FSH Logical model per data-dictionary activity (IMMZ: `IMMZC4` "IMMZ.C4.Create client record"), its ValueSets and CodeSystems, and a Questionnaire per activity (`QIMMZC4`).

**SD-03.** By id and title: the id is the DAK id without dots (`ANCDT01`, or `IMMZD2DTHPV2Doses` with Library `IMMZD2DTHPV2DosesLogic`), the title repeats the dotted id, and the CQL header names the table and trigger. The L1 recommendation is a `citation`. *Fail if* it requires `relatedArtifact` `derived-from`: neither WHO IG uses it.

**SD-04.** Six: one per row plus one where no row fires.

**SD-05.** Nine (SMART Base 0.3.0 `DAK` model): health interventions and recommendations, generic personas, user scenarios, business processes and workflows, core data elements, decision-support logic, program indicators, functional and non-functional requirements, test scenarios. *Fail if* scheduling logic is listed as its own component or test scenarios are missing.
