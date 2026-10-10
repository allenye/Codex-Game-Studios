# Codex Game Studios

Game development workflows adapted from Donchitos/Claude-Code-Game-Studios 1.1.3.
The preserved `.claude/` layer is upstream source, not Codex configuration.

## Technology Stack

- **Engine**: [CHOOSE: Godot 4 / Unity / Unreal Engine 5]
- **Language**: [CHOOSE: GDScript / C# / C++ / Blueprint]
- **Version Control**: Git
- **Build System**: [SPECIFY after choosing engine]
- **Asset Pipeline**: [SPECIFY after choosing engine]

## Entry and configuration

- First read `.codex/docs/codex-runtime.md`. It defines tool mappings,
  authorization, delegation and evidence requirements for every studio workflow.
- `project.yaml` is the game config; `project.local.yaml` is a personal override.
  Run `.codex/hooks/yaml-helper.sh resolve_config` through Bash; resolve from the
  project root, not the session's current subdirectory. Never infer an engine
  from the default Godot reference or template placeholders.
- Begin with `$gs-start`, or invoke any `.agents/skills/gs-*/SKILL.md` by name.
  Native Codex slash commands remain reserved for the host.
- Before editing a path, run `python3 .codex/scripts/path_rules.py <path>...`
  from the root and read the returned `.codex/rules/*.md` guidance.
  This is an explicit routing step, not automatic loading of Claude rule files.
- Read `.codex/docs/coding-standards.md` for code, directory-structure.md for
  engine layout, coordination-rules.md for delegation. Other docs load on demand.

## Engine Version Reference

<!-- ENGINE-REFERENCE-IMPORT: explicit read pointer, not an @ import -->
Read on demand: docs/engine-reference/godot/VERSION.md

`$gs-setup-engine` updates this pointer and `project.yaml` together. Read the
selected engine's pinned version before using its APIs; verify unfamiliar APIs
against official engine documentation.

## Work and evidence

- Respect the user's explicit decisions and authorization. Existing authorization
  covers necessary reversible edits within scope; do not ask again per file.
  Ask for missing project decisions or new scope. An unanswered question gives
  no answer or permission. Never infer consent from timeout or a default option.
- Preserve unrelated work. No commits or remote writes unless the user's request
  authorizes them. Team skills authorize bounded delegation of their feature.
- Use native custom roles under `.codex/agents/` when delegation is available and
  authorized; otherwise execute the same role sequentially and disclose it.
  Never claim subagents ran without tool evidence.
- Retain `production/session-state/active.md` until the task actually finishes.
  Read it after compaction or resume. Update a concise checkpoint before a long
  phase, including completed work, next action, decisions and unresolved blockers.
- Assessments need actual observations. Missing engine, tests, screenshots or
  execution produces NOT ASSESSED/BLOCKED, never PASS. Visible game changes
  require launching and observing the game and retaining genuine screenshots.
- Helpers emit observations, not overall quality verdicts. When tests fail,
  reproduce, add a regression case, fix the cause and rerun related checks.

## Maintaining this fork

- `python3 tools/port_to_codex.py` builds the Codex layer from preserved sources
  and semantic overrides under `tools/codex-overrides/`. Change those inputs for
  generated files; use `--check` to detect drift. The manifest records coverage.
- Validate with `python3 tools/validate_codex.py` and
  `python3 -m unittest discover -s tests/codex_port -v`.
- Do not modify user-level configuration, weaken the sandbox, bypass approval
  requirements, or claim hook protection when hook trust is still pending.
