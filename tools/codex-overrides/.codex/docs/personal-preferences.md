# Personal game workflow preferences

Use gitignored `project.local.yaml` for settings on the helper's local-override
whitelist. A base project.yaml must exist. Use `$gs-settings --local key=value`
to validate a setting before writing. Do not copy a Markdown instruction file
to project.local.yaml; it must be YAML configuration.

Model selection and host permissions are Codex client settings, not game YAML
preferences. This repository does not modify your global configuration.
