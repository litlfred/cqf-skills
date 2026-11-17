# cds-hooks evals

Evals for the `cds-hooks` skill (litlfred fork). `triggers.md` checks when the skill loads;
`questions.md` (questions and task TK-01) is given to the agent under test, `answers.md` is the key
and is not. Run each with and without the skill installed and compare.

TK-01 is graded with the skill's own checker: `python skills/cds-hooks/scripts/check_cds.py response
response.json` must report 0 findings, and the card must say what the task asks (graded by hand).
