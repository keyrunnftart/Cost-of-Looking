# Detector criterion v3 — frozen, latency dropped

Frozen at: **2026-08-28T14:52:37Z**. This supersedes `DETECTOR_CRITERION.md`
for the purpose of judging real build calls. That original document and
its supersession notice remain unedited as the record of what was tried
and why it failed — nothing here retroactively cleans that record up.

## What survived and what didn't

Two detectors carry forward **unchanged** from the original freeze,
because neither was ever confounded across any of the three latency
calibration attempts:

- **Retry** — fires on the first retry event, full stop. No numeric
  window, no manufactured baseline. (`is_error` truthy or
  `api_error_status` non-null on a call.)
- **Cache-creation deviation** — fires when `cache_creation_input_tokens`
  falls outside **4844–4853**, the band observed across the original n=8
  calibration's calls 2–8 (call 1 excluded as a known cold-start outlier).

The **latency detector is dropped entirely.** No threshold, scaled or
otherwise, is frozen for latency. See below for why, in full — this is
real content for the piece, not an engineering footnote.

## Why latency was dropped

Three calibration passes were run, each fixing the specific flaw found in
the one before it, and each producing a new, different, previously
invisible flaw:

1. **v1** (n=8, one-word pings, e.g. "reply with exactly one word: ack").
   Applied to the real build log, this flagged 5/5 calls on both latency
   and cache-creation. Diagnosis: a one-word reply and a several-hundred-
   word generation are not the same distribution — the ping never
   exercises output-token streaming time at all, so its latency profile
   cannot judge a call that is mostly streaming.

2. **v2** (n=8, trivial-but-substantive: "explain how sourdough works in
   ~250 words" and seven similarly-scoped, artwork-unrelated expository
   prompts). Matched the real calls' output-token scale. A raw
   `duration_api_ms / output_tokens` ratio, applied to the real log,
   flagged exactly the three shortest real calls — length bias, visible
   as soon as the raw ratio was checked, because fixed per-call setup
   cost (time-to-first-token) is roughly constant regardless of output
   length, so dividing by fewer tokens mechanically inflates the ratio
   for short replies. Correcting for this by subtracting `ttft_ms` before
   dividing (isolating pure output-streaming rate) removed the length
   bias — but exposed a *different* gap: v2's corrected streaming rate
   (~1.7 ms/token) was uniformly 4–6x faster than every real call's,
   regardless of length. The real driver wasn't length at all — it was
   task type. v2's prompts asked for straightforward expository writing;
   the real build's prompts asked for structured design/creative
   reasoning (propose a mapping, propose a palette). That is plausibly a
   genuinely different, slower per-token computation, not noise.

3. **v3** (n=8, design/reasoning-matched prompts: "propose a naming
   scheme for...", "describe a visual metaphor for...", still
   artwork-unrelated in subject but matched in task category to the real
   build calls). This fixed the v2 task-type confound — applied to the
   real log, the ttft-corrected ratio no longer ranked by output length
   at all (the longest real call was not the most flagged; the shortest
   was not either). But it produced a new degenerate result: 0/5 flagged,
   because v3's *own* calibration sample contained a short-answer outlier
   (159 output tokens, a design-reasoning answer that still needed to
   "settle into" its structure before most tokens streamed) with a ratio
   nearly 3x the rest of the sample. That single outlier alone roughly
   doubled the sample's standard deviation, inflating the cutoff past
   every real value — including a real call that visually looked like the
   genuine outlier in the build log, indistinguishable in scale from v3's
   own internal noise.

**The pattern across all three attempts is the same mechanism recurring
at a smaller and smaller scale**: a short answer's fixed "settle into the
response" overhead distorts any per-token rate computed from it, whether
that short answer is a calibration call being compared to real calls
(v1), a real call being compared to calibration (v2), or a calibration
call being compared to the rest of its own sample (v3). Fixing the
comparison one level up did not remove the mechanism — it only moved
where it showed up next.

**The conclusion drawn from this is not "we haven't found the right
correction yet."** It is that no stable, task-independent latency
baseline exists for reasoning-dependent creative generation at n=8. The
real source of variance — how much a short answer's settle-in overhead
distorts its own per-token rate — needs a calibration sample large enough
to average that overhead out statistically, and a sample that large,
built from real API calls, stops being a small disclosed throwaway pass
and starts being a second, expensive optimization project layered under
the first. Running it would mean tuning the calibration until it produces
a threshold that happens to discriminate, which is precisely the kind of
post-hoc rationalization this whole frozen-before-the-real-run design
exists to prevent. Dropping the latency detector is the more honest
choice than freezing a threshold known to be unstable at this sample
size, or manually adjusting one to force a plausible-looking split.

This is understood as a property of the work being measured — reasoning-
dependent generation has real, structural, short-answer-driven latency
variance that a handful of calibration calls cannot separate from genuine
anomaly — not a failure to calibrate correctly.

## Retry and cache-creation-deviation applied to the real build log

Both detectors below are unchanged from the original freeze. Applied to
`build/build_log.jsonl` (5 real calls, SHA256
`54579fb16c165b7d78f5f0b4c7869c9f3af43b6ea99e8899b2e7078e7b4718df`):

| call | purpose | is_error | api_error_status | retry fired | cache_creation | cache-deviation fired |
|---|---|---|---|---|---|---|
| 1 | concept_brief | False | null | No | 5296 | **Yes** |
| 2 | visual_mapping_proposal | False | null | No | 5337 | **Yes** |
| 3 | detector_visual_language | False | null | No | 5360 | **Yes** |
| 4 | haiku_disclosure_paragraph | False | null | No | 5294 | **Yes** |
| 5 | palette_proposal | False | null | No | 5256 | **Yes** |

**Retry: 0/5 fired.** No retries occurred in the real build, consistent
with every calibration pass run so far.

**Cache-creation deviation: 5/5 fired.** Every real call's cache-creation
token count (5256–5360) exceeds the original 4844–4853 band. This is
reported as found, unchanged and unmodified, per instruction — it was not
re-diagnosed or re-tuned here. One structural observation, not acted on:
the real build's prompts each carry a fixed block of piece-specific
context (the concept, the frozen detector rules, the Haiku finding) that
calibration prompts never include, by design — calibration must stay
artwork-unrelated to avoid peeking at the real run. If that context block
is what is adding the extra ~450–500 cached tokens (rather than response
content), the cache-creation detector may be structurally biased to flag
every real call regardless of anomaly, for a reason unrelated to the one
that broke the latency detector. That possibility is noted here and left
for a deliberate decision, not resolved unilaterally.

## Tie-break rule (only retry and cache-deviation remain)

With latency dropped, only two detectors remain, so the original
three-way priority order (Retry > Latency > Cache-creation) collapses to
**Retry > Cache-creation deviation** whenever both fire on the same call.
Reasoning carried over unchanged: retry is a discrete infrastructure-level
event with no benign alternative explanation; cache-creation deviation has
a known benign explanation available (TTL expiry, or now also the
context-block possibility noted above) that retry doesn't. Both still get
logged in full regardless of which is primary.

## Disclosable finding for the artwork statement (carried forward)

The background Haiku session-naming call finding from the original freeze
still stands and still belongs in the piece's eventual statement — see
`DETECTOR_CRITERION.md`'s equivalent section for the full text.

## Hash chain

This file's freeze depends on the following inputs, hashed at freeze
time:

- `DETECTOR_CRITERION.md` (with correction note): SHA256
  `39b8c1fad9d008e3c7f6cfb4386743a804fe46f19fa80c65c427cd2c3172b5b6`
- `calibration/calibration_raw.jsonl` (v1, n=8): SHA256
  `3d8b17daf9575b1a6dda4869c9f64efa904886a47c0a3e6bd09eb168eb8c7c3c`
- `calibration/calibration_v2_raw.jsonl` (v2, n=8, invalidated): SHA256
  `a4aa99ae099f289a97b2168509fdb616dea1564d1652e79f9a450bae10de13dd`
- `calibration/calibration_v3_raw.jsonl` (v3, n=8, invalidated): SHA256
  `348be81c3f5b195217e97ffc627db8310038f1a0301da23760779220b352a9f8`
- `build/build_log.jsonl` (real build, n=5, judged above): SHA256
  `54579fb16c165b7d78f5f0b4c7869c9f3af43b6ea99e8899b2e7078e7b4718df`

This file's own SHA256 is computed after writing and recorded in
`calibration/DETECTOR_CRITERION_V3.md.sha256`.

## Change log

- 2026-08-28T14:52:37Z — initial and final freeze. Latency dropped,
  retry and cache-creation deviation carried forward unchanged, both
  applied to the existing 5-call real build log.
