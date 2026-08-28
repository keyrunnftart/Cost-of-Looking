"""
Third calibration pass, v3.

v1 failed: one-word pings don't share a distribution with substantive
generation calls. v2 failed differently: matching output-token scale
wasn't enough, because v2 used expository-writing prompts (explain how X
works) while the real build calls are structured design/creative-reasoning
prompts (propose a mapping, propose a palette) -- a task-type confound,
not a length confound. v2's ttft-corrected streaming rate (~1.7 ms/token)
was 4-6x faster than every real call's, uniformly.

v3 matches task *category* (creative/structured reasoning: propose,
describe a metaphor for, design a scheme for) as well as varying target
length, while staying artwork-unrelated in subject. Same n=8, same
disclosure discipline: no padding for a retry, no massaging the result.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from mechanical_logger import logged_call

ROOT = os.path.join(os.path.dirname(__file__), "..")
LOG_PATH = os.path.join(ROOT, "calibration", "calibration_v3_raw.jsonl")

prompts = [
    "Propose a naming scheme for a fictional coffee roastery's seasonal "
    "single-origin blends. Explain the logic behind the scheme. Under 150 words.",
    "Describe a visual metaphor for teaching children how compound interest "
    "works, and why it communicates the idea better than a bar chart. Under 200 words.",
    "Propose a 4-color palette (hex values) for a farmers-market brand identity, "
    "with a one-line reason for each color. Under 120 words.",
    "Propose an icon/symbol system for rating hiking-trail difficulty (not the "
    "standard diamond/circle system). Describe each symbol and what it signals. "
    "Under 180 words.",
    "Describe a structural metaphor for organizing a personal recipe-box app's "
    "navigation, and why that metaphor beats a plain folder tree. Under 150 words.",
    "Propose a grid and typography scheme for a neighborhood print newsletter. "
    "Be specific about column count, type sizes, and why they fit the format. "
    "Under 200 words.",
    "Propose a scoring-rubric structure for a home-baking contest with three "
    "judged categories. Explain how the categories were chosen. Under 130 words.",
    "Describe a visual language for a weather app's icon set, distinct from "
    "existing weather-icon conventions. Under 170 words.",
]

for i, prompt in enumerate(prompts, start=1):
    print(f"[{i}/{len(prompts)}] calibration_v3 ...", file=sys.stderr)
    r = logged_call(prompt, i, purpose="calibration_v3:design-reasoning", log_path=LOG_PATH)
    print(
        f"    is_error={r.get('is_error')} duration_api_ms={r.get('duration_api_ms')} "
        f"ttft_ms={r.get('ttft_ms')} output_tokens={r.get('usage', {}).get('output_tokens')}",
        file=sys.stderr,
    )

print("\nv3 calibration complete. Log at:", LOG_PATH, file=sys.stderr)
