# Improve a studio skill or role

Arguments: a skill or role name. With no name, show usage and stop.

1. Run `$gs-skill-test` for the target and retain baseline evidence. Read its
   workflow, spec and native runtime semantics. Distinguish real failures from
   superseded upstream assertions. A model label or an old frontmatter field is
   not a missing Codex capability.
2. Reproduce the highest-impact demonstrated failure in an isolated fixture.
   Add a regression case whose expected outcome is independent of the proposed fix.
3. Make the smallest authorized change to its source/semantic override. Preserve
   user scope and existing unrelated behavior. Regenerate the Codex layer when
   applicable; do not edit a generated file without updating its source.
4. Rerun the failing case and related regression tests plus the structural
   validator. Keep the change only if it fixes the demonstrated defect without
   regressions; otherwise revise or revert only your own change.
5. Report the before/after evidence, commands and remaining limitations. Never
   improve a score by weakening evidence requirements or removing a failing case.
