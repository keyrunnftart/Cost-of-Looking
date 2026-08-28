"""
Profile picture for "Cost of Looking" -- not a resize of the main piece.

The main piece (render.py) is a 37-mark chronological strip meant to be read
full-size. This is a separate composition, built for legibility at ~128px:
the five real BUILD-phase calls (the actual construction of this piece, not
throwaway calibration pings), reduced to their bare mark vocabulary -- a
baseline rule and five discs/rings, no legend, no text, no fine channels
(stroke-width, cache-satellite dots, hue) that wouldn't survive the
downscale anyway. Still real telemetry, just five points instead of 37.
"""

import json
import math
import os
from PIL import Image, ImageDraw

ROOT = os.path.join(os.path.dirname(__file__), "..")
OUT_DIR = os.path.join(ROOT, "output")
os.makedirs(OUT_DIR, exist_ok=True)

BG = "#1a1a1a"
BASELINE = "#8a8f98"


def hex_to_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def lerp(a, b, t):
    return a + (b - a) * t


def norm(v, lo, hi, lo_out=0.0, hi_out=1.0):
    if hi == lo:
        return lo_out
    t = (v - lo) / (hi - lo)
    t = max(0.0, min(1.0, t))
    return lerp(lo_out, hi_out, t)


def load_build_rows():
    rows = []
    path = os.path.join(ROOT, "build", "build_log.jsonl")
    with open(path, encoding="utf-8") as f:
        for line in f:
            rec = json.loads(line)
            r = rec["response"]
            u = r.get("usage", {})
            rows.append({
                "duration_api_ms": r.get("duration_api_ms"),
                "output_tokens": u.get("output_tokens"),
                "cost_usd": r.get("total_cost_usd"),
            })
    return rows


def main():
    rows = load_build_rows()
    n = len(rows)
    assert n == 5, f"expected 5 real BUILD calls, found {n}"

    durations = [r["duration_api_ms"] for r in rows]
    outputs = [r["output_tokens"] for r in rows]
    costs = [r["cost_usd"] for r in rows]

    dur_min, dur_max = min(durations), max(durations)
    log_dur_min, log_dur_max = math.log(dur_min), math.log(dur_max)
    out_sqrt_min, out_sqrt_max = math.sqrt(min(outputs)), math.sqrt(max(outputs))
    cost_min, cost_max = min(costs), max(costs)

    # square canvas, rendered big and downscaled -- avatar crops are always square
    S = 1024
    MARGIN = 170
    RULE_Y = 300  # fixed near-top, matches the main piece's "fastest sits near the top" logic
    FLOOR_Y = S - 200

    img = Image.new("RGB", (S, S), hex_to_rgb(BG))
    draw = ImageDraw.Draw(img, "RGBA")

    # baseline rule -- the fastest real BUILD call sits on it, everything else sinks below
    draw.line([(MARGIN - 20, RULE_Y), (S - MARGIN + 20, RULE_Y)],
              fill=hex_to_rgb(BASELINE) + (140,), width=4)

    xs = [lerp(MARGIN, S - MARGIN, i / (n - 1)) for i in range(n)]

    for row, cx in zip(rows, xs):
        t = norm(math.log(row["duration_api_ms"]), log_dur_min, log_dur_max)
        cy = lerp(RULE_Y, FLOOR_Y, t)

        out_sqrt = math.sqrt(row["output_tokens"])
        # strict multiplicative rescale of the original (34, 92) mapping, not an
        # independently-picked floor/ceiling -- preserves exact relative proportions
        # between marks while shrinking overall scale to stop the overlap at 64px
        outer_r = norm(out_sqrt, out_sqrt_min, out_sqrt_max, 34, 92) * (68 / 92)
        inner_r = outer_r * 0.28

        light_t = norm(row["cost_usd"], cost_min, cost_max)
        base_rgb = hex_to_rgb(BASELINE)
        rgb = tuple(int(lerp(c * 0.55, min(255, c * 1.65), light_t)) for c in base_rgb)

        draw.ellipse([cx - outer_r, cy - outer_r, cx + outer_r, cy + outer_r],
                     outline=rgb + (255,), width=5)
        draw.ellipse([cx - inner_r, cy - inner_r, cx + inner_r, cy + inner_r],
                     fill=rgb + (255,))

    out_path = os.path.join(OUT_DIR, "cost_of_looking_profile.png")
    img.save(out_path)
    print("wrote", out_path, img.size)

    for size in (256, 128, 64):
        thumb = img.resize((size, size), Image.LANCZOS)
        tpath = os.path.join(OUT_DIR, f"cost_of_looking_profile_{size}.png")
        thumb.save(tpath)
        print("wrote", tpath, thumb.size)


if __name__ == "__main__":
    main()
