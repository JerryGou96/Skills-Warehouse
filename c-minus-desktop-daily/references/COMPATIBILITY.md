# Legacy analysis compatibility

This package is the portable production successor to the locally authored `c-minus-daily-review` analysis entry point. The legacy dated capture prototype and private operations record are intentionally not included. No third-party source is copied. Do not run the old prototype or automatically import a legacy aggregate state.json: reconcile historical delivery records before enabling a new output directory, otherwise duplicates are possible.

Preserved contract:

- Numeric author verification; full desktop DOM; bounded history with raw IDs, timestamps, edits and attachments; content-hash versions and explicit provenance.
- Five sections: Macro Regime & Setup, Top Signals, Earnings Digest, Extra Alpha Playbook, Levels. Headings ignore case and optional prefixes. Require substantive closing content, not a Levels heading alone. Any unreadable meaningful attachment, missing author or pagination discontinuity must be disclosed and blocks declaring a complete report until reviewed.
- Explicit substantive short commentary before 09:00 with a closing passage can be complete without five sections; it must be labeled short_commentary and standard_five_sections_complete=false. Unrelated intraday news cannot qualify. Inspect intervening raw messages to confirm continuity even though assembly filters the configured author.
- Compare to the previous complete five-section trading-day report and name both dates; capture spans approximately seven days. If no baseline is in this capture, inspect saved earlier complete reports; never invent one. Changed earlier content is an edit, not necessarily a fresh stance change.
- Extract direction, conditional trigger, price range, expected move, horizon, self-reported position/execution, intended action and invalidation. Missing mention means not updated, not closed or reversed. Preserve ambiguous tickers. Add zones are not stops; expected moves are not targets; bullishness does not imply same-day entry. Missing size/stop/options data is “not provided.”
- Separate attributed research, self-reported transactions, independently verified facts and assistant interpretation. Do not claim fills or real-time prices from morning text. Supplemental ideas require explicit invalidation.
- Six-part Chinese output, cutoff/completeness/baseline/source links, full earnings details locally, compact chat without tables. Include opening, Levels (or short closure), and baseline message links using configured guild/channel and captured message IDs.
- Bounded weekday checks, calendar uncertainty, no repeated missing notices, exclusive claims, pending reconciliation, distinct labeled corrections, and independent scheduler acceptance.

Export hardening: configuration replaces private constants; null authors are handled conservatively; delivery status is read-only, receipt commits are atomic and conflicting receipt replacement is rejected. Existing source implementations and deployments are unchanged. These synthetic checks do not establish live desktop compatibility on a new installation.
