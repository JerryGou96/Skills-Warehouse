# openclaw-release-notifications

When asked about OpenClaw updates or new-release reminders, verify release status and configure notification-only monitoring.

## Install and use

Copy this directory into your agent’s configured skill directory, then check discovery with `openclaw skills check --json`. Ask the agent for the audit or release monitoring described above. Read SKILL.md before execution.

## Dependencies and configuration

- OpenClaw CLI and agent tools

Resolve `OPENCLAW_INSTALL_DIR` to the installed OpenClaw package directory and, when applicable, `AGENTBRAIN_ROOT` to your own vault root. These are documentation placeholders, not bundled configuration. The `agentbrain` QMD collection is optional and must match your local setup.

Release monitoring retains the source default of Monday 10:00 America/Los_Angeles; honor an explicitly requested cadence/timezone. No credentials or delivery destination are bundled.

## Validation limits

Static package/frontmatter/reference checks only; no notifications, account changes or business workflows are executed by installation.
