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
| `index.config.json` | the harness layers it needs (fhir-harness, folio-assistant-core, cat-harness, cat-harness-tools, bootstrap, bootstrap-tools), pinned by commit with the owner's consent at each ref | by hand |
| `index.lock.json` | what those pins resolved to, by tree digest | `bun run cat mount:lock` |
| `package.json`, `bun.lock`, `bunfig.toml` | the mounted code layers as workspaces, and the `cat` entry point | by hand; lockfile frozen |
| `tools/kg-index/` | the Tool node (`kg-index.ts`) and its script | by hand |
| `processes/content/*.checklist.md` | one checklist per process | **generated**: `bun run cat bpmn:checklist` |
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

## Cold start for the harness checks

```sh
python3 -c "import json;[print(m['harness'],m['repository'],m['ref']) for m in json.load(open('index.lock.json'))['mounts']]" > /tmp/mounts.txt
while read h r ref; do git clone -q --filter=blob:none --no-checkout https://github.com/$r $h && git -C $h checkout -q $ref && rm -rf $h/.git; done < /tmp/mounts.txt
bun install --frozen-lockfile
bun run cat mount:lock
```

A layer that no longer hashes to the lock is reported `missing`: delete it and run `mount:lock` again.
Checks that judge this layer and pass: `harness:dirs:check`, `check:schema-nodes`,
`node-kinds:check`, `subgraph:jsonld:check`, `check:process-bindings`, `check:process-documentation`,
`bpmn:checklist:check`, `check:bean-front-matter`, `check:asset-roles`, `check:declaration-claims`, and
the declared-skills half of `skill:register:check` (19 skills, 4 packages). What stays red is in the
pinned layers, not here: bean HK-01.

## Syncing from upstream

Merge cqframework's `main` into the fork's `main`. Conflicts can only arise in `README.md` (catalog
rows), `CHANGELOG.md`, `marketplace.json` and the appended section of `AGENTS.md`. Then regenerate
`harness/skills/`. A skill that becomes upstream's replaces the fork's copy.
