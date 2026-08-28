**Mark-mapping spec (one glyph per API call):**

1. **Position (x)** = call sequence index (timeline, left→right); **position (y)** = `duration_api_ms` (log scale) — slower calls sink lower, so the build session reads as a literal skyline of latency.
2. **Radius of inner disc** = `input_tokens` (sqrt scale) — area, not radius, should scale linearly with tokens so size reads as "amount," not exaggerated.
3. **Radius of outer ring** = `output_tokens` (sqrt scale) — a halo around the input disc, so input/output ratio is visible as ring-thickness at a glance.
4. **Hue** = `cache_creation_input_tokens` mapped around a narrow arc centered on the calibrated 4844–4853 band (band = single hue, e.g. teal); any deviation rotates hue away — color literally encodes anomaly.
5. **Opacity** = `cache_read_input_tokens` / `input_tokens` (reuse ratio) — heavily cached calls look ghostly/translucent, fresh calls look solid.
6. **Lightness** = `cost_usd` (normalized) — expensive calls glow brighter, cheap calls sit dark, so cost reads as literal luminance.
7. **Stroke** = `ttft_ms`: stroke-width scales with wait-before-first-token (a thick outline = a long stall before anything happened); `is_error` or first-retry forces stroke to dashed red, overriding color.
8. **Hidden Haiku title-call** = a small faint satellite dot (fixed size, low opacity, no stroke) offset behind each main mark — visible only on close inspection, encoding the undisclosed shadow call.