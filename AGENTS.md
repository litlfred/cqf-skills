# Agent instructions for this repository

This repository publishes Agent Skills for CQL, FHIR, Clinical Reasoning, and FHIR IGs. Follow [CONTRIBUTING.md](CONTRIBUTING.md).

- Each skill lives in `skills/<name>/SKILL.md`, and the folder name must equal the frontmatter `name`.
- Each skill must be self-contained: never link to files outside its own folder.
- When you add or rename a skill, update `.claude-plugin/marketplace.json`, the catalog table in `README.md`, and `CHANGELOG.md`.
- Run `python scripts/validate_skills.py` after you change skills or the marketplace.
- Never add real patient data. All examples must be synthetic.

## litlfred fork: the knowledge-graph layer

This fork adds a cat-harness layer beside the upstream layout; [HARNESS.md](HARNESS.md) says what it
is and what to run. After changing a skill or the marketplace, also run
`python3 -I tools/kg-index/kg_index.py`.
