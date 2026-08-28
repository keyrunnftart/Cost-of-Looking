**Baseline:** small solid ink-grey dot, uniform size — the visual "silence" everything else departs from.

**RETRY:** a thin concentric echo-ring around the dot (no fill change) — since there's no numeric baseline to size against, the ring reads as a discrete event, not a magnitude.

**LATENCY:** the dot stretches into a horizontal smear/tail, length scaled to ms over 4000 — encodes magnitude directly, unlike RETRY's binary ring.

**CACHE_DEVIATION:** the dot's fill shifts from solid to a stippled/cross-hatch texture, density scaled to distance outside the 4844–4853 band — a third distinct channel (texture, not shape or outline) so it can't be confused with the others.

**Tie-break:** render the winning flag's full treatment (per RETRY > LATENCY > CACHE_DEVIATION), but add one small hollow tick at the mark's edge per suppressed flag that also fired — ticks carry no magnitude, just presence, so the hierarchy stays legible while nothing is erased.