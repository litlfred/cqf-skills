# The knowledge-graph layer (litlfred fork)

`litlfred/cqf-skills` is a fork of [cqframework/cqf-skills](https://github.com/cqframework/cqf-skills)
made a [cat-harness](https://github.com/litlfred/cat-harness) layer: its skills become nodes of a
knowledge graph, alongside the processes that use them and the roles that play those processes.

**Upstream's layout stays the source.** `skills/<name>/SKILL.md`, `evals/`, `.claude-plugin/marketplace.json`
and `scripts/validate_skills.py` are not restructured, so the fork can keep syncing from cqframework
and offer skills back. Everything below is added beside them.

| path | what | how it is made |
|---|---|---|
| `cqf-skills.json` | the layer's declaration: the directories it scans and the graph typology of each | by hand |
| `index.config.json` | the harness layers it needs (fhir-harness, and through it cat-harness and below), pinned by commit | by hand; `index.lock.json` by `bun run cat mount:lock` |
| `harness/skills/<plugin>/` | one package per marketplace plugin: `package-manifest.json` and one node per skill | **generated**: `python3 -I tools/kg-index/kg_index.py` (`--check` in CI) |
| `processes/content/*.bpmn` | the work the skills serve, lanes by role, tasks naming skills | by hand (BPMN 2.0) |
| `scenarios/roles.json` | the roles that play the lanes, with the skills each needs | by hand |
| `memory/` | owner directives | by hand |
| `beans/defs/` | open issues of the fork | by hand |

## The processes

| process | lanes | skills, in order |
|---|---|---|
| [Author a CQL library](processes/content/cql-library-authoring.bpmn) | knowledge engineer | cql → terminology → vscode-cql → cql-ig → crmi |
| [Develop a quality measure](processes/content/measure-development.bpmn) | measure developer, IG author | cms-qmd → measure → terminology → madie → measure → crmi → ig-publisher |
| [Turn a DAK into L3 content](processes/content/dak-to-l3.bpmn) | knowledge engineer, IG author | smart-dak → fsh → terminology → cql → cpg → plan-definition → measure → questionnaire → ig-publisher |
| [Build and publish a content IG](processes/content/ig-publication.bpmn) | IG author | fsh → fhir-extensions → ig-publisher → crmi |
| [Add or change a skill](processes/content/skill-contribution.bpmn) | skill maintainer, cqframework maintainer | (template, evals) → skill-registration → upstream review |

## Skills the fork adds

`measure`, `terminology` and `smart-dak` were missing from the catalog for the processes above. They
are written in the upstream format, with evals, and marked **draft** until each claim is checked by
running, as upstream's are (`memory/dir-upstream-bar.md`, beans SK-01 and SK-02). Further gaps are in
bean SK-03.

## Commands

```sh
python scripts/validate_skills.py            # upstream's lint
python3 -I tools/kg-index/kg_index.py        # regenerate harness/skills/
python3 -I tools/kg-index/kg_index.py --check
```

The harness's own checks (`bun run cat skill:register:check`, `harness:dirs:check`, the BPMN checks)
need the mounts laid down first: bean HK-01.

## Syncing from upstream

Merge cqframework's `main` into the fork's `main`. Conflicts can only arise in `README.md` (catalog
rows), `CHANGELOG.md`, `marketplace.json` and the appended section of `AGENTS.md`. Then regenerate
`harness/skills/`. A skill that becomes upstream's replaces the fork's copy.
