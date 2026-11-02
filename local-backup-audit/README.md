# local-backup-audit

"For local duplicate backups or disk-space audits, inventory copies and verify content overlap before recommending cleanup."

## Installation and usage

Copy this complete directory into your configured OpenClaw skill root. Verify discovery with `openclaw skills check --json`, then request the task described in SKILL.md. Read its branch-specific references before execution. Installation does not install dependencies, enable jobs, change accounts, or grant external-action authorization.

## Dependencies

- macOS df, du, tmutil and launchd inspection tools
- Python 3 standard library
- Authorized cleanup tool only for separately authorized cleanup branch

## Local configuration

Resolve documentation placeholders before use: `RESEARCH_VAULT_ROOT` is your research vault, `OPENCLAW_SKILLS_DIR` your configured shared skill directory, and `DISCORD_READER_RUNTIME` your isolated compatible CLI runtime. These are not bundled settings. Configure vault-relative tracker/archive paths and the QMD collection (source default: `agentbrain`) to match your installation. No vault files are included. Choose your own accounts, channels, lists and output paths. Timezone/language defaults in the procedure can be overridden by the user.

## Validation limits

Static YAML, package, resource-link and privacy checks only. No business workflows, desktop capture, notifications, account modifications or cleanup operations were run for publication.
