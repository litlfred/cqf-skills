import { toolFactory } from "@litlfred/cat-harness-tools/schemas/tools/tool-folders.js";
import { defineTool } from "@litlfred/cat-harness-tools/schemas/tools/tool.js";

export default toolFactory((t) =>
  defineTool({
    id: "kg-index",
    title: "Skill graph view",
    description:
      "Write harness/skills/<plugin>/ (one package-manifest.json and one node per skill) from skills/*/SKILL.md and the plugins of .claude-plugin/marketplace.json, so the upstream Agent Skills layout stays the source and the knowledge graph reads the same skills.",
    install: { none: true },
    invoke: { shell: "python3 -I tools/kg-index/kg_index.py" },
    io: {
      inputs: [
        { name: "check", schema: t("Flag"), required: false, arg: { flag: "--check" }, description: "Write nothing; fail if harness/skills/ is stale." },
      ],
      outputs: [
        { name: "packages", schema: t("RepoPath"), description: "harness/skills/." },
      ],
    },
    satisfies: ["skill-registration"],
    selection: {
      when: "A skill or marketplace.json changed, or CI checks the graph view is current.",
      limits: "Derives the view only; the skills themselves are authored in skills/.",
      cost: "Milliseconds.",
    },
    requires: { runtime: ["python3"], network: false },
  }),
);
