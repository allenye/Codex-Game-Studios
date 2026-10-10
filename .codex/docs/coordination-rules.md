# Codex agent coordination

Read codex-runtime.md for actual tools and authorization. Leadership resolves
cross-domain decisions; leads own their domains; specialists implement them.
Creative conflicts escalate to creative-director, technical conflicts to
technical-director; producer coordinates changes affecting multiple domains.

Use native roles under `.codex/agents/*.toml`. On hosts with a prompt-only
delegation interface, pass the role's developer_instructions explicitly. If
delegation is unavailable or unauthorized, execute the role sequentially and
report that fact. Never claim that a role was spawned when it was not.

Parallel tasks must have independent inputs and disjoint owned files. Specify
allowed paths, acceptance criteria, dependencies and evidence in each prompt.
Start independent tasks together, collect all outputs, then integrate serially.
Never start a dependent task before its prerequisites complete. Conflicting
changes require an explicit integration decision. BLOCKED roles stay visible.

Reviewers receive the task and raw artifacts before the author's conclusions.
Find counterexamples and reproduce them; resolve by adding regression cases and
retesting. Do not confuse an author's completion claim with independent evidence.

All roles inherit the selected session model unless a user explicitly changes
it. The original hierarchy describes responsibility, not model pricing.
