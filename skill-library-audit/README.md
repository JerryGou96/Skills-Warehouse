# skill-library-audit

After local skills are reorganized or migrated, verify agent discovery, resource references, automation bindings, and deployed-copy consistency.

## Install and use

Copy this directory into your agent’s configured skill directory, then check discovery with `openclaw skills check --json`. Ask the agent for the audit or release monitoring described above. Read SKILL.md before execution.

## Dependencies and configuration

- OpenClaw CLI and agent tools
- skill-creator skill (including scripts/quick_validate.py)
- Target repository validator and proper YAML parser

Resolve `OPENCLAW_INSTALL_DIR` to the installed OpenClaw package directory and, when applicable, `AGENTBRAIN_ROOT` to your own vault root. These are documentation placeholders, not bundled configuration. The `agentbrain` QMD collection is optional and must match your local setup.

Release monitoring retains the source default of Monday 10:00 America/Los_Angeles; honor an explicitly requested cadence/timezone. No credentials or delivery destination are bundled.

## Validation limits

Static package/frontmatter/reference checks only; no notifications, account changes or business workflows are executed by installation.
