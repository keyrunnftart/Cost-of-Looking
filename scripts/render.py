"""
Renderer for "Cost of Looking".

Subject: the full, disclosed, chronological record of every real API call
made in the course of calibrating and building this piece -- 37 calls
across four calibration attempts (v1 pings, v2 expository, v3
design-reasoning, v4 context-matched) and the 5-call real build. Composed
per the frozen record: retry is the only surviving detector
(DETECTOR_CRITERION_V3.md + the v4 finding), and it never fired. Every
mark below is real telemetry, not fabricated or estimated.

Composition, agreed before writing this code:
- one continuous horizontal strip, chronological, grouped by attempt
- small equal gaps between the four calibration groups, a visibly larger
  gap before the real build group (the one categorical break that matters)
- minimal low-contrast group labels (v1 v2 v3 v4), BUILD at higher contrast
- a thin baseline rule spanning the full strip, at the fastest real
  duration observed (2546ms) -- a real data point, not an arbitrary line
- hue is binary: every mark is baseline-colored; the three flag colors
  (LATENCY, RETRY, CACHE_DEVIATION) exist only in the legend, unused
"""

import json
import math
import os
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.join(os.path.dirname(__file__), "..")
OUT_DIR = os.path.join(ROOT, "output")
os.makedirs(OUT_DIR, exist_ok=True)

# ---- palette (content/palette_proposal.md, verbatim) ----
BG = "#1a1a1a"
BASELINE = "#8a8f98"
LATENCY = "#e8543e"
RETRY = "#f2c14e"
CACHE_DEVIATION = "#4ea8de"
TEXT_QUIET = "#5a5f68"   # dimmer than baseline, for v1-v4 labels
TEXT_BRIGHT = "#c8ccd2"  # brighter than baseline, for the BUILD label + legend text

GROUPS = [
    ("v1", os.path.join(ROOT, "calibration", "calibration_raw.jsonl")),
    ("v2", os.path.join(ROOT, "calibration", "calibration_v2_raw.jsonl")),
    ("v3", os.path.join(ROOT, "calibration", "calibration_v3_raw.jsonl")),
    ("v4", os.path.join(ROOT, "calibration", "calibration_v4_raw.jsonl")),
    ("BUILD", os.path.join(ROOT, "build", "build_log.jsonl")),
]


def load_all():
    rows = []
    for group, path in GROUPS:
        with open(path, encoding="utf-8") as f:
            for line in f:
                rec = json.loads(line)
                r = rec["response"]
                u = r.get("usage", {})
                mu = r.get("modelUsage", {})
                haiku = mu.get("claude-haiku-4-5-20251001")
                rows.append({
                    "group": group,
                    "duration_api_ms": r.get("duration_api_ms"),
                    "ttft_ms": r.get("ttft_ms"),
                    "input_tokens": u.get("input_tokens"),
                    "output_tokens": u.get("output_tokens"),
                    "cache_read": u.get("cache_read_input_tokens"),
                    "cache_creation": u.get("cache_creation_input_tokens"),
                    "cost_usd": r.get("total_cost_usd"),
                    "is_error": bool(r.get("is_error")),
                    "api_error_status": r.get("api_error_status"),
                    "has_haiku": haiku is not None,
                })
    return rows


def lerp(a, b, t):
    return a + (b - a) * t


def norm(v, lo, hi, lo_out=0.0, hi_out=1.0):
    if hi == lo:
        return lo_out
    t = (v - lo) / (hi - lo)
    t = max(0.0, min(1.0, t))
    return lerp(lo_out, hi_out, t)


def hex_to_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def main():
    rows = load_all()
    n = len(rows)
    assert n == 37, f"expected 37 real calls, found {n}"

    # ---- global ranges (real min/max across all 37 calls) ----
    durations = [r["duration_api_ms"] for r in rows]
    ttfts = [r["ttft_ms"] for r in rows]
    outputs = [r["output_tokens"] for r in rows]
    costs = [r["cost_usd"] for r in rows]
    cache_reads = [r["cache_read"] for r in rows]
    inputs = [r["input_tokens"] for r in rows]

    dur_min, dur_max = min(durations), max(durations)
    ttft_min, ttft_max = min(ttfts), max(ttfts)
    out_min, out_max = min(outputs), max(outputs)
    cost_min, cost_max = min(costs), max(costs)
    cread_min, cread_max = min(cache_reads), max(cache_reads)
    in_min, in_max = min(inputs), max(inputs)  # 2..2, flat -- kept honest, not forced

    log_dur_min, log_dur_max = math.log(dur_min), math.log(dur_max)

    # ---- canvas ----
    W, H = 2400, 1100
    LEFT, RIGHT = 100, 100
    LEGEND_TOP, LEGEND_H = 40, 130
    PLOT_TOP = LEGEND_TOP + LEGEND_H + 40
    PLOT_BOTTOM = H - 140
    LABEL_Y = PLOT_BOTTOM + 30

    img = Image.new("RGB", (W, H), hex_to_rgb(BG))
    draw = ImageDraw.Draw(img, "RGBA")

    try:
        font_label = ImageFont.load_default(size=22)
        font_label_bright = ImageFont.load_default(size=26)
        font_legend_title = ImageFont.load_default(size=20)
        font_legend_sub = ImageFont.load_default(size=16)
        font_title = ImageFont.load_default(size=30)
    except TypeError:
        font_label = font_label_bright = font_legend_title = font_legend_sub = font_title = ImageFont.load_default()

    # ---- legend: the unused vocabulary, at full weight ----
    legend_items = [
        (BASELINE, "BASELINE", "the record, as it actually happened"),
        (LATENCY, "LATENCY", "dropped -- no stable threshold survived calibration"),
        (RETRY, "RETRY", "never fired -- 0 of 37 real calls"),
        (CACHE_DEVIATION, "CACHE DEVIATION", "dropped -- no stable threshold survived calibration"),
    ]
    lx = LEFT
    swatch_w = (W - LEFT - RIGHT) / len(legend_items)
    for color, title, sub in legend_items:
        cx = lx + 18
        cy = LEGEND_TOP + 20
        draw.ellipse([cx - 14, cy - 14, cx + 14, cy + 14], fill=hex_to_rgb(color))
        draw.text((lx + 44, LEGEND_TOP + 6), title, font=font_legend_title, fill=hex_to_rgb(TEXT_BRIGHT))
        draw.text((lx, LEGEND_TOP + 40), sub, font=font_legend_sub, fill=hex_to_rgb(TEXT_QUIET))
        lx += swatch_w

    # ---- x layout: unit space with grouped gaps, then scaled to plot width ----
    mark_spacing = 1.0
    gap_small = 1.3
    gap_large = 4.5

    x_units = []
    group_bounds = {}  # group -> (first_x_unit, last_x_unit)
    cursor = 0.0
    prev_group = None
    for i, row in enumerate(rows):
        g = row["group"]
        if prev_group is not None and g != prev_group:
            cursor += gap_large if g == "BUILD" else gap_small
        x_units.append(cursor)
        group_bounds.setdefault(g, [cursor, cursor])
        group_bounds[g][1] = cursor
        cursor += mark_spacing
        prev_group = g

    unit_min, unit_max = 0.0, cursor - mark_spacing
    plot_left, plot_right = LEFT + 30, W - RIGHT - 30

    def x_px(u):
        return lerp(plot_left, plot_right, norm(u, unit_min, unit_max))

    # ---- baseline rule: at the fastest real call ever observed ----
    baseline_y = PLOT_TOP + 20  # fastest duration sits near the top
    draw.line([(plot_left - 10, baseline_y), (plot_right + 10, baseline_y)],
              fill=hex_to_rgb(BASELINE) + (120,), width=2)

    # ---- draw marks ----
    for row, xu in zip(rows, x_units):
        cx = x_px(xu)

        # y: log-scale duration, slower sinks lower; baseline_y is the fastest-ever line
        t = norm(math.log(row["duration_api_ms"]), log_dur_min, log_dur_max)
        cy = lerp(baseline_y, PLOT_BOTTOM, t)

        # outer ring radius: output_tokens, sqrt scale
        out_sqrt = math.sqrt(row["output_tokens"])
        out_sqrt_min, out_sqrt_max = math.sqrt(out_min), math.sqrt(out_max)
        outer_r = norm(out_sqrt, out_sqrt_min, out_sqrt_max, 6, 40)

        # inner disc radius: input_tokens, sqrt scale -- flat at 2 across all 37 calls,
        # kept true to that rather than forced to vary
        inner_r = 5.0 if in_min == in_max else norm(math.sqrt(row["input_tokens"]),
                                                      math.sqrt(in_min), math.sqrt(in_max), 4, 20)

        # opacity: cache_read / input_tokens reuse ratio, normalized across the real range
        ratio = row["cache_read"] / row["input_tokens"]
        ratio_min = cread_min / in_max  # input_tokens is flat, so this reduces to cache_read's own range
        ratio_max = cread_max / in_min
        opacity = norm(ratio, ratio_min, ratio_max, 1.0, 0.55)  # more reuse -> more ghostly

        # lightness: cost_usd, normalized
        light_t = norm(row["cost_usd"], cost_min, cost_max)
        base_rgb = hex_to_rgb(BASELINE)
        rgb = tuple(int(lerp(c * 0.5, min(255, c * 1.6), light_t)) for c in base_rgb)

        # stroke width: ttft_ms
        stroke_w = norm(row["ttft_ms"], ttft_min, ttft_max, 1, 7)

        alpha = int(255 * opacity)

        # retry check -- real logic, simply never triggers on this dataset
        is_retry = row["is_error"] or row["api_error_status"] is not None
        outline_color = hex_to_rgb(RETRY) + (255,) if is_retry else rgb + (alpha,)

        # hidden Haiku satellite: fixed size, low opacity, offset behind the main mark
        if row["has_haiku"]:
            sx, sy = cx - outer_r * 0.6, cy - outer_r * 0.6
            draw.ellipse([sx - 5, sy - 5, sx + 5, sy + 5], fill=hex_to_rgb(BASELINE) + (60,))

        # outer ring (halo)
        draw.ellipse([cx - outer_r, cy - outer_r, cx + outer_r, cy + outer_r],
                     outline=outline_color, width=max(1, int(stroke_w)))
        # inner disc
        draw.ellipse([cx - inner_r, cy - inner_r, cx + inner_r, cy + inner_r],
                     fill=rgb + (alpha,))

        if is_retry:
            # RETRY treatment: concentric echo-ring, per detector_visual_language.md
            draw.ellipse([cx - outer_r - 8, cy - outer_r - 8, cx + outer_r + 8, cy + outer_r + 8],
                         outline=hex_to_rgb(RETRY) + (200,), width=2)

    # ---- group labels ----
    for g, (first_u, last_u) in group_bounds.items():
        cx = (x_px(first_u) + x_px(last_u)) / 2
        if g == "BUILD":
            draw.text((cx, LABEL_Y), g, font=font_label_bright, fill=hex_to_rgb(TEXT_BRIGHT), anchor="ma")
        else:
            draw.text((cx, LABEL_Y), g, font=font_label, fill=hex_to_rgb(TEXT_QUIET), anchor="ma")

    # ---- title ----
    draw.text((LEFT, H - 60), "Cost of Looking - the complete disclosed record, 37 real calls, 0 flagged",
               font=font_title, fill=hex_to_rgb(TEXT_QUIET))

    out_path = os.path.join(OUT_DIR, "cost_of_looking_v1.png")
    img.save(out_path)
    print("wrote", out_path, img.size)

    # ---- thumbnails for legibility check ----
    for size in (256, 128, 64):
        thumb = img.resize((size, int(size * H / W)), Image.LANCZOS)
        tpath = os.path.join(OUT_DIR, f"cost_of_looking_thumb{size}.png")
        thumb.save(tpath)
        print("wrote", tpath, thumb.size)


if __name__ == "__main__":
    main()
