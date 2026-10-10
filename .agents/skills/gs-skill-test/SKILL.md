---
name: gs-skill-test
description: "Validate skill files for structural compliance and behavioral correctness. Four modes: static linter, spec, category rubric, audit."
---

# Skill Test

Use this workflow for the game project in this repository. Arguments: static [skill-name | all] | spec [skill-or-agent-name] | category [skill-or-agent-name | all] | audit.

1. Locate the project root containing `AGENTS.md`, `project.yaml` and `.codex/`.
   Read `.codex/docs/codex-runtime.md` for tool, authorization and delegation mappings.
2. Read [the workflow](references/workflow.md). Follow its phases and load only
   the phase references needed now. Paths in that workflow are relative to this
   skill folder unless they begin with `.codex/`, `.agents/`, or a project directory.
3. Honor existing user choices and authorization; ask only for missing decisions
   or additional scope. Never treat an unanswered question as approval.
4. Record tool evidence for assessments. Report PASS, FAIL, BLOCKED or
   NOT ASSESSED as the workflow requires; never invent execution or screenshots.

The detailed workflow inherits the runtime adapter's semantics. Its logical
operations are not literal tool names. Use tools actually exposed by the host.
