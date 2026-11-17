# measure evals

Evals for the `measure` skill (litlfred fork). `triggers.md` checks when the skill loads;
`questions.md` (questions and task TK-01) is given to the agent under test, `answers.md` is the key
and is not. Run each with and without the skill installed and compare.

| File | Contents |
| --- | --- |
| [grade_measure.py](grade_measure.py) | Grader for the TK-01 Measure: `python grade_measure.py Measure-screening.json` |
| [test_grade_measure.py](test_grade_measure.py) | Tests for the grader, run in CI |

The answers to ME-01 to ME-07 are the engine's behaviour as recorded in the skill's probe
(`skills/measure/resources/probes/2026-11-17/RESULTS.md`).
