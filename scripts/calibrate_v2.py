"""
Second calibration pass, v2 -- fixes the flaw found in v1.

v1 used one-word pings, which don't share a latency distribution with the
real generation calls the detector is meant to judge (output streaming
time dominates real calls; a ping never exercises that). v2 uses trivial,
artwork-unrelated content that is nonetheless substantive in output scale
(a few hundred words), matched to the real build log's output_tokens
range (245-994).

Same discipline as v1: n=8, real disclosed throwaway calls, no padding to
manufacture a retry, no threshold decided until the raw numbers are in.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from mechanical_logger import logged_call

ROOT = os.path.join(os.path.dirname(__file__), "..")
LOG_PATH = os.path.join(ROOT, "calibration", "calibration_v2_raw.jsonl")

prompts = [
    "In about 250 words, explain how a sourdough starter works.",
    "In about 250 words, describe the history of the bicycle.",
    "In about 250 words, explain how ocean tides form.",
    "In about 250 words, describe the history of the paperclip.",
    "In about 250 words, explain how coffee beans are roasted.",
    "In about 250 words, describe the history of the postage stamp.",
    "In about 250 words, explain how rainbows form.",
    "In about 250 words, describe the domestication of cats.",
]

for i, prompt in enumerate(prompts, start=1):
    print(f"[{i}/{len(prompts)}] calibration_v2 ...", file=sys.stderr)
    r = logged_call(prompt, i, purpose="calibration_v2:trivial-substantive", log_path=LOG_PATH)
    print(
        f"    is_error={r.get('is_error')} duration_api_ms={r.get('duration_api_ms')} "
        f"output_tokens={r.get('usage', {}).get('output_tokens')}",
        file=sys.stderr,
    )

print("\nv2 calibration complete. Log at:", LOG_PATH, file=sys.stderr)
