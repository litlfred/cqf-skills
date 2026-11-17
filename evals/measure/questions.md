# measure Skill Test Questions

Answer each in a few sentences, as to a measure developer. The key is in `answers.md`; don't read it.

**ME-01. Exceptions.** A patient meets the numerator and a denominator exception. Which populations is it counted in?

**ME-02. Score.** IP 100, Denom 80, DenEx 10, DenExcep 5, Numer 40, NumerEx 0. What is the measure score?

**ME-03. Basis.** In an Encounter-based proportion measure, what type must "Numerator" return in CQL, and where does an R4 Measure say the basis?

**ME-04. Continuous variable.** Which populations does a continuous-variable measure need, and how does the observation say how to aggregate?

**ME-05. Not in the numerator.** A patient I expected in the numerator is only in the IP, and the population report's evaluatedResource is empty. What does that tell me, and what do I run next?

**ME-06. Stratifier.** I added `stratifier.criteria` = `"Sex"` (returns the patient's gender) to a boolean-basis proportion measure. On a HAPI FHIR server (clinical-reasoning 4.13.0) every count is now 0. Why, and what is the fix?

**ME-07. Errors.** How do I tell, from the MeasureReport alone, that the counts are not to be trusted?

## Task

**TK-01.** Write a FHIR R4 boolean-basis proportion Measure `screening` whose library is `http://example.org/fhir/Library/Screening|1.0.0`, with initial population, denominator, denominator exclusion, numerator, a stratifier by sex and `improvementNotation` `increase`. Save it as `Measure-screening.json`.
