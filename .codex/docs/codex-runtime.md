# Codex runtime adapter

This adapter takes precedence over host-specific mechanics in the migrated
workflows. Game design requirements, phase dependencies and evidence gates are
preserved. Explicit user instructions and host/system policy always take priority.

## Discovery and paths

Skills live in `.agents/skills/gs-<name>/SKILL.md`; invoke `$gs-<name> arguments`
or describe the task. Original `/start`, `/help` and `/settings` names are not
Codex commands. The `gs-` prefix prevents collisions with host commands.
Workflows in `references/workflow.md` use the skill folder as their reference
base: `references/2-load-context.md` means a sibling of workflow.md. Root paths
such as `.codex/docs/...` are relative to the game project.

Locate the root from the discovered skill's path (three parents above its folder)
or the nearest ancestor with `AGENTS.md`, `project.yaml` and `.codex/`. In each
shell call using a helper, explicitly set `CGS_ROOT` to that absolute root and
run from it. It is a studio variable, not an environment supplied by Codex.
`CGS_SKILL_DIR`, if needed, is that skill's absolute folder. Never expand user
arguments as shell code; pass quoted arguments or use subprocess argument arrays.
Codex does not execute Markdown shell snippets as preprocessing. A workflow's
"Run explicitly" instruction requires a real shell tool call and checked output.

## Logical operations and actual tools

Names below are operations used in detailed workflows, not registered tools:

| Workflow operation | Codex implementation |
| --- | --- |
| Read / Glob / Grep | Exposed file tools, or shell `cat`, `rg --files`, `rg` |
| Write / Edit | Native `apply_patch` or an exposed file tool |
| Bash / PowerShell | Available shell tool (`exec_command`); use host's shell |
| capture_user_decision | Structured user input when exposed and valid in the current mode; otherwise ask in chat and wait |
| update_plan | Native plan tool when available; otherwise update a file-backed checklist |
| read_task_checkpoint | Read the checklist and `production/session-state/active.md` |
| delegate_role | Native `spawn_agent`/collaboration facility using the named custom role; see below |
| message_role | Native follow-up/message tool for a live subagent, only within authorized delegation |
| WebSearch / WebFetch | Available search/browser tools; prefer official engine docs |
| Skill loading | Read the selected SKILL.md and follow it; no Claude Skill tool |

Do not call a nonexistent tool or manufacture a tool result. A host without
subagents, structured input or GUI access can run the rest of the workflow, but
must disclose unavailable capabilities and preserve pending gates. A required
answer cannot be replaced by an assumption. Optional preferences may use a
stated reasonable default; never treat that default as authorization.

## User intent and automation

The upstream's repeated per-write approval text describes collaboration points.
In Codex, a user's request to implement a feature authorizes its necessary
reversible edits. Show meaningful decisions and progress; do not demand another
"yes" for every file when scope is already authorized. If the user explicitly
requests draft-only work, write nothing beyond permitted drafts.

Resolve `modes.automation` and project-specific always-ask categories as the
workflow specifies. These settings never grant external permissions or waive
host approval, hook trust or sandbox restrictions. Ask when a choice affects
unresolved scope, destructive actions, contracts, secrets or external publishing
that has not already been authorized. No response means no permission. An
existing authorization remains valid across phases and compaction.

## Roles and scheduling

The 49 native roles are TOML files under `.codex/agents/` with `name`,
`description` and `developer_instructions`. Models inherit the active session;
Claude aliases (opus/sonnet/haiku) and `maxTurns` have no runtime meaning here.
No role silently changes a user's model or broadens permissions. Read-only
roles specify a read-only sandbox; all others inherit the parent's permissions.
Upstream tool lists and model labels are retained only as provenance in the
port manifest, not enforced access restrictions. Domain ownership remains an
instruction; the sandbox is the actual execution boundary.

Use the host's custom-agent selector (for example `agent_type`) if exposed.
If its collaboration API accepts only a task/prompt, read the named TOML and
include its `developer_instructions` in the delegated prompt. If delegation is
unavailable or unauthorized, perform the role's work sequentially and say so.
Never create user-owned chats/threads to simulate subagents.

Parallelize only independent inputs and disjoint file ownership. The parent
defines owned paths, dependencies and acceptance criteria. Shared-file edits,
schema decisions, integration, publishing and dependent phases are sequential.
Wait for every prerequisite; a blocked role produces a partial report, not
silent approval. A reviewer first examines raw evidence without the author's
desired verdict, then provides counterexamples with reproducible steps.

## Rules, lifecycle and honest verification

Before modifying a file, run `path_rules.py` and read the matching Markdown
rules. Their YAML `paths:` headers are not native automatic Codex rules.
Native executable deny prefixes live separately in `.codex/rules/studio.rules`.

Repo-local `.codex/hooks.json` uses a stdlib Python bridge with documented Codex
events. Review and trust the project layer and exact hook definitions via
`/hooks` in a compatible Codex CLI before relying on them. New hashes need
review. No installer modifies global trust or bypasses the sandbox.
Hooks are guardrails, not a complete security boundary; edits through uncovered
tools may require manual checks. A post-write failure cannot undo the edit.
The bridge preserves the active checkpoint at Stop; it never calls the upstream
archive-and-clear routine on each assistant reply. Subagent lifecycle events
append bounded metadata, not secrets or entire transcripts.

For validation, distinguish static parsing, direct handler tests, native client
discovery and actual model/tool behavior. Structural tests do not prove gameplay
quality or all 74 workflows. Run failures through reproduce → regression case →
fix → targeted retest → relevant suite. A missing engine or authentic visual
evidence is NOT ASSESSED. Never use a generated image as a screenshot of a run.

Official references verified 2026-10-09:
- https://learn.chatgpt.com/docs/build-skills
- https://learn.chatgpt.com/docs/agent-configuration/agents-md
- https://learn.chatgpt.com/docs/agent-configuration/subagents
- https://learn.chatgpt.com/docs/hooks
