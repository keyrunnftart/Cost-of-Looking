# Detector criterion — frozen before observed build

Frozen at: **2026-08-28T14:02:10Z**, before the observed build phase of this
piece begins. Nothing below may be edited after this timestamp except to
append a change log entry with a new hash; the values themselves are locked.

## How this was calibrated

No prior telemetry existed for this kind of number. A prior pass checked
`D:\Drift` and `D:\MergeConflict` for token spend, latency, and retry data
from their build sessions and found none — no logs, no JSON with usage
fields, nothing recoverable. Git commit-gap timing was considered and
rejected as a substitute: it measures save-points, not API behavior.

Instead, 8 throwaway, artwork-unrelated API calls were run on this current
setup (`claude -p <trivial prompt> --output-format json --model
claude-sonnet-5 --no-session-persistence`) purely to observe normal
operating ranges before the real build starts. Prompts were trivial
arithmetic/word tasks with no relation to this piece's subject matter, so
they calibrate the instrument without peeking at the observed run's own
data. Raw responses are logged verbatim, one JSON object per line, in
`calibration/calibration_raw.jsonl` — every number below is read directly
from that log, nothing here is estimated.

Sample size: n=8. This is a small, disclosed convenience sample, not a
statistically powered one. Thresholds derived from it are treated as
informed floors, not precise statistical cutoffs.

SHA256 of `calibration/calibration_raw.jsonl` at freeze time:
`3d8b17daf9575b1a6dda4869c9f64efa904886a47c0a3e6bd09eb168eb8c7c3c`

## Raw calibration sample (n=8)

| call | duration_ms | duration_api_ms | ttft_ms | time_to_request_ms | cache_read | cache_creation | cost_usd |
|---|---|---|---|---|---|---|---|
| 1 | 1593 | 2546 | 1568 | 42 | 32513 | 0 | 0.007501600000000001 |
| 2 | 1741 | 2732 | 1711 | 36 | 27668 | 4851 | 0.025933600000000005 |
| 3 | 1698 | 2657 | 1686 | 40 | 27668 | 4844 | 0.0259046 |
| 4 | 1592 | 2546 | 1568 | 38 | 27668 | 4845 | 0.025907600000000003 |
| 5 | 1797 | 2776 | 1752 | 48 | 27668 | 4845 | 0.025920600000000002 |
| 6 | 1700 | 2832 | 1687 | 35 | 27668 | 4853 | 0.026006599999999998 |
| 7 | 1759 | 2723 | 1735 | 40 | 27668 | 4845 | 0.025906600000000002 |
| 8 | 2844 | 3824 | 2824 | 37 | 27668 | 4850 | 0.0259296 |

`duration_api_ms`: min 2546, max 3824, mean 2829.5, stdev 387.8 (population).
`is_error` was `false` and `api_error_status` was `null` on all 8 calls.
Call 1 is a cold-cache outlier (0 cache-creation, 32513 cache-read,
inherited from a prior session's cache state); calls 2–8 form the stable
band (4844–4853 cache-creation tokens) used below.

## Detector 1 — latency

**Fires when `duration_api_ms > 4000`.**

Derivation: mean (2829.5) + ~3×stdev (387.8) ≈ 4993, rounded *down* to 4000
rather than up, because call 8 already reached 3824ms within a confirmed
clean run — the threshold should not hug the observed maximum of a sample
this small.

## Detector 2 — retry

**Fires on the first retry event, full stop.**

There is no numeric retry-rate baseline. Zero retries occurred across the
8-call calibration sample, and the design deliberately did not run more
calls to try to manufacture one — padding the sample to thicken a retry
count would be optimizing the calibration itself, which this whole
approach exists to avoid. The honest finding is that a normal run does not
retry. This detector is therefore not a threshold in the statistical sense
of the other two: it fires on the first real occurrence, whenever that is,
with no claim about expected frequency.

## Detector 3 — cache-creation deviation

**Fires when `cache_creation_input_tokens` falls outside the 4844–4853
band** observed in calls 2–8 (call 1 excluded as a known cold-start
outlier, not part of the stable baseline).

Known benign cause: the raw `usage.cache_creation` field exposes
`ephemeral_5m_input_tokens` / `ephemeral_1h_input_tokens` — the cache has
its own TTLs, so a deviation here can reflect ordinary cache expiry rather
than a build-time anomaly. This is the weakest of the three signals for
that reason (see tie-break below).

## Tie-break rule (decided now, before any real run can force a hindsight call)

**Priority order if multiple detectors fire on the same call: Retry >
Latency > Cache-creation deviation.**

- Retry is a discrete infrastructure-level event with no benign alternative
  explanation available — the strongest, least-confoundable signal.
- Latency is a real statistical threshold from calibration data, but it's
  continuous and can be pushed by ordinary network/server jitter.
- Cache-creation deviation is weakest: a known benign explanation (TTL
  expiry) exists for it that doesn't exist for the other two.

If more than one detector's condition is true on the same call, **all are
still logged in full** — nothing is suppressed. The priority order above
only decides which one is recorded as the primary/headline flag for that
event in the provenance record.

## Disclosable finding for the artwork statement (not a footnote)

Every one of the 8 calibration calls silently invoked a second, cheaper
model in the background — `claude-haiku-4-5-20251001`, ~900 input tokens,
~$0.001 per call — alongside the visible `claude-sonnet-5` response,
visible only in the raw `modelUsage` field of the JSON output (not in any
user-facing surface). This appears to be session/title-naming overhead,
not something the calling agent requested or was aware of at the time it
happened. It is a genuine finding about what "the agent" actually is in
this setup — a visible model plus an invisible one — discovered only
because this calibration pass looked at raw output most workflows never
inspect. This belongs in the piece's eventual description/statement, not
buried in this criterion file.

## Change log

- 2026-08-28T14:02:10Z — initial freeze, n=8 calibration sample.
  SHA256 at that freeze:
  `884f13c8f442d88fd7b876dd45915b469c98b30ace9fbe0d78889969fde953c0`
- 2026-08-28T14:15:32Z — **superseded, see notice below.**

## Supersession notice — 2026-08-28T14:15:32Z

The three thresholds frozen above (latency > 4000ms, first retry,
cache-creation band 4844–4853) are **invalidated** and must not be applied
to any real build log. This section is appended, not edited into the
original text above, so the original miscalibration stays visible in the
record rather than being quietly corrected away.

**Diagnosis:** the original n=8 calibration sample used trivial one-word
pings (`input_tokens=2`, `output_tokens` 3–7). The real build calls this
detector exists to judge are substantive generation calls (up to 994
output tokens in the first real build log). Pinging latency and
substantive-generation latency are not the same distribution — a one-word
reply completes as soon as the model emits one token past `ttft`, while a
several-hundred-word generation is dominated by output-token streaming
time that a ping never exercises. Applying the ping-calibrated threshold
to real generation calls produced 5/5 false positives on both the latency
and cache-creation detectors on the first real build log — not because
the build was anomalous, but because the yardstick was measuring the
wrong thing. This is a flaw in the calibration methodology, not a finding
about that run.

**Resolution:** a second calibration pass (n=8, same discipline: real
disclosed throwaway calls, no padding to manufacture a retry) was run
using trivial-but-substantive content — comparable in output scale to
real generation calls, still unrelated to the piece's subject matter. See
`DETECTOR_CRITERION_V2.md` for the new frozen thresholds. The original
thresholds and this notice remain here, unedited, as the record of what
went wrong and why.

## Correction — 2026-08-28T14:52:37Z

The pointer above to `DETECTOR_CRITERION_V2.md` was written prospectively
and never resolved: the v2 pass's own ttft-corrected latency ratio was
caught as confounded (task-type mismatch — expository-writing prompts vs.
the real build's design/reasoning prompts) *before* any threshold was
frozen from it, so no `DETECTOR_CRITERION_V2.md` file was ever written.
That's the calibration-before-freezing discipline working as intended,
not a second miscalibration reaching the record. A third pass (v3,
design/reasoning-matched prompts) was attempted and also caught as
confounded before freezing (within-sample short-answer variance). Both
v2's and v3's raw calibration logs exist
(`calibration/calibration_v2_raw.jsonl`, `calibration/calibration_v3_raw.jsonl`)
as evidence of the attempts; neither produced a frozen file. The actual
next frozen file is `DETECTOR_CRITERION_V3.md`, which drops the latency
detector entirely and carries the retry and cache-creation-deviation
detectors forward unchanged from this document.
