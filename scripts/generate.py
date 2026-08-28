"""
Real build-content generator for "Cost of Looking".

Every call here is genuine engineering work toward the piece's concept
and visual language -- not throwaway calibration content. Each call is
routed through mechanical_logger.logged_call, which appends the full raw
response to build/build_log.jsonl.

No detector threshold is applied here. This script only produces content
and lets the log accumulate, per instruction.
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from mechanical_logger import logged_call

ROOT = os.path.join(os.path.dirname(__file__), "..")
LOG_PATH = os.path.join(ROOT, "build", "build_log.jsonl")
CONTENT_DIR = os.path.join(ROOT, "content")

os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
os.makedirs(CONTENT_DIR, exist_ok=True)

CONTEXT = """You are helping develop a real generative artwork called "Cost of Looking",
submitted by an AI agent to an AI-art magazine's open call. The piece's raw material
is the agent's own build-session telemetry: real duration_api_ms, ttft_ms, token usage
(input/output/cache-read/cache-creation), and cost_usd from actual Claude API calls made
while building the piece itself. A frozen detector was calibrated in advance on 8 throwaway
calls (0 retries observed) with three rules: latency > 4000ms, first retry (no numeric
baseline, fires on first occurrence), and cache-creation-token deviation outside a
4844-4853 token band. A genuine, undisclosed-until-now finding from that calibration:
every visible Sonnet call silently triggers a second, cheaper background call to
claude-haiku-4-5-20251001 (~900 input tokens) for session-title generation -- invisible
in normal use, only found by inspecting raw usage JSON.
"""

tasks = [
    (
        "concept_brief",
        CONTEXT
        + "\n\nWrite a 150-200 word concept brief for this piece, in the same register "
        "as a serious gallery statement (not marketing copy). It should state plainly what "
        "the piece's data actually is (real per-call API telemetry from its own construction), "
        "why a detector was frozen before the data existed, and what that guards against "
        "(post-hoc rationalization of whatever the real run happens to produce). Do not "
        "invent any numbers -- describe the method, not fabricated results.",
    ),
    (
        "visual_mapping_proposal",
        CONTEXT
        + "\n\nPropose a concrete mapping from real per-call telemetry fields "
        "(duration_api_ms, ttft_ms, input_tokens, output_tokens, cache_read_input_tokens, "
        "cache_creation_input_tokens, cost_usd, is_error) to visual channels (position, size, "
        "color hue/saturation/lightness, opacity, stroke) for a single generative mark per "
        "API call, rendered as SVG. Be specific about which field drives which channel and "
        "why that pairing is legible rather than arbitrary. List as a short numbered spec, "
        "under 200 words.",
    ),
    (
        "detector_visual_language",
        CONTEXT
        + "\n\nThe frozen detector can flag a mark as: LATENCY (duration_api_ms > 4000ms), "
        "RETRY (first retry event, no baseline), or CACHE_DEVIATION (cache-creation tokens "
        "outside 4844-4853), with tie-break priority RETRY > LATENCY > CACHE_DEVIATION when "
        "more than one fires on the same call. Propose a distinct, legible visual treatment "
        "for each flag type that reads clearly against the unflagged baseline marks, and a "
        "treatment for the tie-break case that still shows the suppressed secondary flags "
        "were true (nothing hidden). Under 150 words.",
    ),
    (
        "haiku_disclosure_paragraph",
        CONTEXT
        + "\n\nWrite a single disclosure paragraph (80-120 words) for the piece's artist "
        "statement, plainly describing the background Haiku session-naming call discovery: "
        "that every visible model call is actually two calls, one visible and one the agent "
        "did not request or know about at call time, found only by reading raw usage JSON. "
        "State why this belongs in the statement rather than a footnote -- it is a real fact "
        "about what 'the agent' making this piece actually is.",
    ),
    (
        "palette_proposal",
        CONTEXT
        + "\n\nPropose a 4-color palette (hex values) plus one background color for this "
        "piece: baseline (unflagged calls), latency flag, retry flag, cache-deviation flag. "
        "Should read cleanly in both light and dark contexts. State each hex value and a "
        "one-line reason for the choice. Under 100 words.",
    ),
]

def _run():
    # Guarded so importing this module (e.g. to reuse CONTEXT) can never
    # re-trigger real, costly API calls. Learned the hard way: an earlier
    # `from generate import CONTEXT` re-ran the whole real build because
    # this loop used to sit at module level.
    results = {}
    for i, (name, prompt) in enumerate(tasks, start=1):
        print(f"[{i}/{len(tasks)}] {name} ...", file=sys.stderr)
        response = logged_call(prompt, i, purpose=f"build:{name}", log_path=LOG_PATH)
        text = response.get("result", "")
        is_error = response.get("is_error")
        print(f"    is_error={is_error} duration_api_ms={response.get('duration_api_ms')}", file=sys.stderr)
        results[name] = text
        with open(os.path.join(CONTENT_DIR, f"{name}.md"), "w", encoding="utf-8") as f:
            f.write(text)

    print("\nAll build calls complete. Log at:", LOG_PATH, file=sys.stderr)


if __name__ == "__main__":
    _run()
