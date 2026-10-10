---
name: gs-help
description: "What should I do next? Use when stuck or you don't know what to do."
---

# Help

Use this workflow for the game project in this repository. Arguments: [optional: what you just finished, e.g. 'finished design-review' or 'stuck on ADRs'].

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
