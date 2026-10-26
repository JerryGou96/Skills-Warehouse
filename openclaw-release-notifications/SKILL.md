---
name: openclaw-release-notifications
description: "When asked about OpenClaw updates or new-release reminders, verify release status and configure notification-only monitoring."
---

# OpenClaw release notifications

1. Read the installed docs `docs/install/updating.md` and `docs/install/updating/automatic-updates.md` under the OpenClaw installation before explaining update behavior, because Gateway and headless-node automatic-update defaults differ.
2. Run the read-only commands `openclaw --version`, `openclaw update status --json`, and `openclaw config get update`; compare the installed version with `update.registry.latestVersion`, `availability`, and `channel`. Treat an unset config key as the documented runtime default rather than an error.
3. For a reminder request, inspect existing automations with the available scheduler tool before creating one, because repeated requests should not produce duplicate notifications. Use `openclaw cron list --json` for read-only inspection if needed. Discover current scheduler schemas and use first-class tools for mutations; do not bypass tool restrictions through CLI or RPC.
4. Default the owner’s release checks to weekly rather than daily unless he requests another cadence; use Monday at 10:00 America/Los_Angeles (`0 10 * * 1`) when no different time is specified. For cadence corrections, patch the existing automation’s schedule and matching payload wording, preserving its enabled state, delivery route, and version deduplication rather than creating another job. Configure a recurring isolated check with an explicit timezone and a verified delivery destination. Obtain the destination from trusted current-session context or ask for it; do not infer the current channel from another automation. Use a stable declaration key where supported to make creation idempotent.
5. Put this procedure in the scheduled payload: run `openclaw update status --json` and `openclaw --version`, wait for terminal results, and notify only when a newer stable release is confirmed. Keep a persistent last-notified-version record so repeated checks do not repeat the same release. Return the scheduler-supported silent response when no new release exists. Record lookup failures separately rather than reporting that no update exists.
6. Make the payload notification-only: do not install packages, change update configuration, or restart services. Include installed and available versions plus the official release-notes link `https://github.com/openclaw/openclaw/releases`. Direct the owner to send `/update` for this chat Gateway rather than promising to execute its update through shell tools.
7. Verify the saved automation has the intended enabled state, schedule, timezone, payload, and delivery route. Report that it is configured without claiming an end-to-end delivery test unless one was observed.
8. Confirm the check time and timezone concisely in Chinese for Chinese requests, and state that notifications do not install updates.
