"""
Mechanical logger for real Claude API calls made during this piece's build.

Wraps every call in the same instrumentation used for calibration
(calibration/calibration_raw.jsonl), per the frozen rule in
DETECTOR_CRITERION.md. Does NOT apply any detector threshold -- this
module only records what happened. Detection is a separate, later step
applied against the accumulated log.

Unlike the calibration pass, calls made through this logger are real
build content (concept/visual-language generation for the piece), not
throwaway trivial prompts. The `purpose` field on each record marks that
distinction honestly.
"""

import json
import os
import subprocess
import sys
from datetime import datetime, timezone

CLAUDE_EXEC = os.environ.get(
    "CLAUDE_CODE_EXECPATH",
    r"C:\Users\keyru\AppData\Local\nvm\v22.22.2\node_modules\@anthropic-ai\claude-code\bin\claude.exe",
)
MODEL = "claude-sonnet-5"


def _now_iso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"


def logged_call(prompt: str, call_index: int, purpose: str, log_path: str) -> dict:
    """
    Run one real, non-throwaway `claude -p` call, mechanically log the
    full raw response, and return the parsed response dict.

    Never suppresses or edits the raw response. If the call errors, the
    error is logged as-is (that is exactly the kind of event the frozen
    retry detector cares about, applied later).
    """
    wall_start = _now_iso()
    proc = subprocess.run(
        [
            CLAUDE_EXEC,
            "-p",
            prompt,
            "--output-format",
            "json",
            "--model",
            MODEL,
            "--no-session-persistence",
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    wall_end = _now_iso()

    raw_stdout = proc.stdout.strip()
    try:
        response = json.loads(raw_stdout)
    except json.JSONDecodeError:
        # Genuine failure to parse -- log it honestly rather than hide it.
        response = {
            "is_error": True,
            "parse_error": True,
            "raw_stdout": raw_stdout,
            "raw_stderr": proc.stderr.strip(),
            "returncode": proc.returncode,
        }

    record = {
        "call_index": call_index,
        "purpose": purpose,
        "prompt": prompt,
        "wall_start": wall_start,
        "wall_end": wall_end,
        "response": response,
    }

    with open(log_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")

    return response


if __name__ == "__main__":
    # Smoke test only -- not part of the real build log.
    r = logged_call(
        "Reply with exactly one word: smoketest",
        0,
        "logger self-test, not build content",
        os.path.join(os.path.dirname(__file__), "..", "calibration", "logger_selftest.jsonl"),
    )
    print(json.dumps(r, indent=2)[:500])
