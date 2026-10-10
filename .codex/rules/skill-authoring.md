---
paths:
  - ".agents/skills/**"
  - ".codex/agents/**"
---

# Codex skill and role authoring

Skills require YAML frontmatter with `name` and `description`; use a lowercase
`gs-` name matching the directory. Do not add Claude-only model, allowed-tools,
context or user-invocable fields. Put workflow detail in references and load it
on demand. Keep automatic matching enabled unless the user explicitly requests
otherwise. Discovery metadata must describe the actual scope.

Custom agents use TOML with name, description and developer_instructions. Do not
carry over model aliases, maxTurns or tool lists as if Codex enforced them. Model
and permissions inherit the parent unless an explicit valid override is needed.

Use only available tools. For portable workflows, reference the logical
operations in codex-runtime.md; these operations are not literal tool names.
Preserve user intent, existing authorization and pending decisions. Require
real evidence for verdicts. Avoid rigid phase-count requirements for simple skills.

Update tools/codex-overrides/ for generated workflows or docs, then regenerate.
Run the structural validator and relevant behavioral tests; a structural PASS
does not prove behavioral correctness. Fix demonstrated failures with a narrow
regression case and rerun the affected checks.
