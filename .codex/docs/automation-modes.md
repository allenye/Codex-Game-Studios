# Automation modes on Codex

Resolve modes.automation with the existing YAML helper and resolution chain.
`collaborative` prompts for unresolved creative and architectural decisions;
`guided` prompts for major decisions; `autonomous` uses reasonable choices and
records them with log_decision. Project-specific automation_always_ask categories
still require a decision (use is_always_ask_category).

Existing user authorization covers necessary reversible edits inside the chosen
scope. Per-write wording in detailed workflows is not a demand to ask repeatedly
for already authorized edits. A draft-only request remains draft-only. Never
infer consent from silence, a dismissed question or a preselected UI option.

Automation settings cannot override host permissions, hook trust or the sandbox.
Clarify missing scope and material project decisions; require separate
authorization for external or destructive actions outside the current request.
Use a structured input tool when available and valid in the current mode;
otherwise ask in chat and wait. See codex-runtime.md for operation mappings.
