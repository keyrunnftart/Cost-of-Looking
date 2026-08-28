"""
Fourth calibration pass, v4 -- cache-creation-deviation only.

The original cache-creation band (4844-4853) was calibrated from calls
that never carried the real build's fixed context block (the piece's
concept, the frozen detector rules, the Haiku finding -- prepended to
every real generation call, see generate.py's CONTEXT). That's a
structural, predictable mismatch, the same shape as v1/v2/v3's latency
confounds: calibration and real calls differ in a way that guarantees a
gap regardless of any real anomaly.

Fix: reuse CONTEXT verbatim (imported, not retyped, to guarantee an exact
match), prepended to trivial artwork-unrelated task content. This matches
the known structural condition (context-block size) without looking at
any real outcome data -- it's fixing a predictable mismatch, not reacting
to a result. Task content is trivial/short (task type doesn't matter for
cache footprint, only prompt/context size does). Same discipline as
before: n=8, real disclosed throwaway calls, no padding for a retry.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from mechanical_logger import logged_call
from generate import CONTEXT

ROOT = os.path.join(os.path.dirname(__file__), "..")
LOG_PATH = os.path.join(ROOT, "calibration", "calibration_v4_raw.jsonl")

trivial_tasks = [
    "Name a fruit. One word only.",
    "What is the boiling point of water in Celsius? One number only.",
    "Name a mountain range. A few words only.",
    "What year did the Wright brothers first fly? One number only.",
    "Name a type of cloud. One or two words only.",
    "What is the chemical symbol for gold? One or two characters only.",
    "Name a constellation. One or two words only.",
    "What is the freezing point of water in Fahrenheit? One number only.",
]


def _run():
    for i, task in enumerate(trivial_tasks, start=1):
        prompt = CONTEXT + "\n\n" + task
        print(f"[{i}/{len(trivial_tasks)}] calibration_v4 ...", file=sys.stderr)
        r = logged_call(prompt, i, purpose="calibration_v4:cache-context-matched", log_path=LOG_PATH)
        print(
            f"    is_error={r.get('is_error')} "
            f"cache_creation={r.get('usage', {}).get('cache_creation_input_tokens')}",
            file=sys.stderr,
        )
    print("\nv4 calibration complete. Log at:", LOG_PATH, file=sys.stderr)


if __name__ == "__main__":
    _run()
