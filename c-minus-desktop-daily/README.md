# c-minus-desktop-daily

Read an authenticated Discord desktop morning report, retain full evidence, assemble five sections or explicit short commentary, and prepare a Chinese comparison with deduplicated delivery.

## Installation and usage

Copy this complete directory to your configured OpenClaw skill root; set `SKILL_DIR` to its installed location. Read SKILL.md and the installed `discord-reader` skill. Installation does not enable jobs, send messages, or grant external-action authorization.

Requires macOS with `open`, an authenticated Discord desktop exposing a loopback CDP endpoint, Node.js 20+, Python 3.9+ with IANA timezone data, OpenClaw file/message/scheduler tools, and the `discord-reader` skill. Install dependencies in an isolated directory **outside the skill**:

```sh
mkdir -p discord-reader-runtime
cd discord-reader-runtime
npm init -y
npm install --save-exact @jackwener/opencli@1.8.7 ws@8
```

Runtime layout: `runtime_dir/package.json`, `runtime_dir/node_modules/.bin/opencli`, and `runtime_dir/node_modules/ws`. Keep the generated dependency lockfile locally. Do not upgrade to opencli 2.x without revalidating desktop Electron support. No third-party implementation is bundled. Capture reads full rendered DOM, not the CLI's truncated message previews. Native read syntax is `read --count 20`, not `read 20`.

Copy `config.example.json` to a private location, replace all `SET_` values, and export `C_MINUS_CONFIG` pointing to that JSON file. Every field is required:

- `output_dir`: private evidence/state directory; relative to the JSON file.
- `runtime_dir`: isolated npm runtime directory; relative to the JSON file.
- `timezone`: IANA timezone; default example America/Los_Angeles.
- `source_guild_id`, `source_channel_id`: authorized read-only Discord source, numeric strings.
- `author_id`: numeric identity verified from an actual source message, not a display-name guess.
- `destination_account`: configured OpenClaw Discord account for authorized delivery.
- `destination_channel_id`: numeric destination, must differ from the source.
- `cdp_endpoint`: local HTTP CDP origin with explicit port, no path or credentials; example localhost port 9232.

The config environment variable is required by all helpers. Output paths never depend on the invoking working directory or installed skill depth. Delivery configuration is consumed by the agent's message tool; helpers never send. Keep your private JSON, runtime, reports, receipts, and locks out of version control.

```sh
node "$SKILL_DIR/scripts/capture.mjs"
python3 "$SKILL_DIR/scripts/assemble.py"
python3 "$SKILL_DIR/scripts/delivery.py" status YYYY-MM-DD
```

Replace the date with an actual ISO date; capture uses the current configured local date. For historical assembly, pass the capture directory date. See references/OPERATIONS.md for dry-run and scheduling, references/COMPATIBILITY.md for the legacy analysis contract.

## Validation limits

Synthetic assembly/delivery/configuration/evidence/lock tests and syntax/frontmatter checks only. No real desktop capture, notification, account modification, scheduler enablement, or end-to-end financial workflow is tested by publication preparation.

## Safe helper checks

```sh
python3 "$SKILL_DIR/tests/test_helpers.py"
node "$SKILL_DIR/tests/test_capture_utils.mjs"
node "$SKILL_DIR/tests/test_capture_mock.mjs"
```

The mocked capture test replaces process/CDP interfaces before execution. It does not contact Discord, launch apps, or send messages. `scripts/config.py` and `scripts/capture-utils.mjs` are shared configuration/evidence/lock helpers imported by the entry points. Always use the latest assembler stdout and matching `captured_at` before considering an assembled file current: if a new capture has no matching report, an older assembled artifact can remain as history and must not be sent.
