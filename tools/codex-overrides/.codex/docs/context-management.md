# Context management

`production/session-state/active.md` is the resumable task checkpoint. Keep a
concise record of the task, completed phases, owned files, next action, accepted
choices, pending decisions and failures. Read it after compaction or resume.
A reply ending does not finish the task: native Stop preserves the file.

Write long artifacts incrementally by section within the user's authorization.
Load only relevant skill phase references, engine docs and matching path rules.
Do not repeatedly reload the entire studio roster or all specs.

Scripts under `.codex/scripts/` emit observations, never overall verdicts.
Use actual shell calls after locating the root, inspect output and preserve
provenance. Config checks are not Markdown preprocessing and no allowed-tools
frontmatter grant applies. See config-resolution.md for exact resolution order.

The model decides assessments from real observations, the effective workflow
and required evidence. Missing observations must remain visible. Do not mistake
an empty helper result, a parser success or an unanswered question for completion.
