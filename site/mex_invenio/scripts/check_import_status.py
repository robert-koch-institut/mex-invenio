    """Watchdog: check whether the S3 import (s3_manager.py) is running healthily.

Deliberately standalone (no Flask app context, no DB/OpenSearch dependency) so
the watchdog itself can't fail for reasons unrelated to the thing it's checking.

Combines two signals:
  - The daily s3_manager log file (logs/s3_manager-<YYYYMMDD>.log) for a recent
    "S3 sync complete." line -- confirms the cron actually ran, even on a
    no-op day where there was nothing new to import.
  - The .import_state file (written by import_data.py) for an explicit
    "failed" status, or a "in_progress" status stuck for too long (crashed
    mid-import) -- only written when a diff was actually imported.

Writes a JSON status document to IMPORT_STATUS_OUTPUT_PATH, meant to be served
directly by nginx from a volume shared with a web pod.

Environment variables:
    INVENIO_S3_DOWNLOAD_FOLDER: same download folder s3_manager.py itself uses
        (read-only for this script). Default: s3_downloads
    IMPORT_STATUS_OUTPUT_PATH: where to write the status JSON.
        Default: import_status.json
    IMPORT_STATUS_STALE_HOURS: age (hours) after which the last successful
        sync log line is considered stale. Default: 30
    IMPORT_STATUS_STUCK_HOURS: age (hours) after which an "in_progress"
        .import_state is considered crashed rather than still running.
        Default: 3

Usage:
    python check_import_status.py

Exit code is 1 if the status is not ok, 0 otherwise (in addition to the
"ok" field in the written JSON) -- gives a second, independent signal via
the CronJob's own Job status.
"""
import glob
import json
import os
import re
import sys
from datetime import datetime, timezone

LOG_LINE_RE = re.compile(
    r"^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\.\d+ - \S+ - \w+ - (.*)$"
)


def find_last_sync_completion(log_dir: str):
    """Return the datetime of the most recent 'S3 sync complete.' log line."""
    pattern = os.path.join(log_dir, "s3_manager-*.log")
    # filenames sort correctly by date (s3_manager-YYYYMMDD.log); a handful of
    # recent files is enough to cross a midnight boundary safely.
    files = sorted(glob.glob(pattern))[-3:]

    last_completion = None
    for path in files:
        try:
            with open(path, encoding="utf-8", errors="replace") as f:
                for line in f:
                    match = LOG_LINE_RE.match(line)
                    if not match:
                        continue
                    ts_str, message = match.groups()
                    if "S3 sync complete." not in message:
                        continue
                    ts = datetime.strptime(ts_str, "%Y-%m-%d %H:%M:%S").replace(
                        tzinfo=timezone.utc
                    )
                    if last_completion is None or ts > last_completion:
                        last_completion = ts
        except OSError:
            continue

    return last_completion


def read_import_state(s3_download_folder: str):
    """Return the parsed .import_state contents, or None if absent/corrupt."""
    state_file = os.path.join(s3_download_folder, ".import_state")
    try:
        with open(state_file) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def check(s3_download_folder: str, stale_hours: float, stuck_hours: float) -> dict:
    now = datetime.now(timezone.utc)
    log_dir = os.path.join(s3_download_folder, "logs")

    last_completion = find_last_sync_completion(log_dir)
    state = read_import_state(s3_download_folder)

    ok = True
    messages = []

    if last_completion is None:
        ok = False
        messages.append("No 'S3 sync complete.' log entry found.")
    else:
        age_hours = (now - last_completion).total_seconds() / 3600
        if age_hours > stale_hours:
            ok = False
            messages.append(
                f"Last successful sync was {age_hours:.1f}h ago "
                f"(> {stale_hours}h threshold)."
            )

    if state:
        status = state.get("status")
        if status == "failed":
            ok = False
            messages.append(f"Last import failed at {state.get('finished_at')}.")
        elif status == "in_progress":
            started_at = state.get("started_at")
            if started_at:
                try:
                    started = datetime.fromisoformat(started_at)
                except ValueError:
                    started = None
                if started and (now - started).total_seconds() / 3600 > stuck_hours:
                    ok = False
                    messages.append(
                        f"Import has been 'in_progress' since {started_at} "
                        f"(> {stuck_hours}h) -- likely crashed."
                    )

    return {
        "ok": ok,
        "checked_at": now.isoformat(),
        "last_sync_completed_at": (
            last_completion.isoformat() if last_completion else None
        ),
        "import_state": state,
        "messages": messages,
    }


def write_status(output_path: str, result: dict) -> None:
    """Write the status JSON atomically so nginx never serves a partial file."""
    out_dir = os.path.dirname(output_path)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
    tmp_path = f"{output_path}.tmp"
    with open(tmp_path, "w") as f:
        json.dump(result, f, indent=2)
    os.replace(tmp_path, output_path)


def main() -> int:
    s3_download_folder = os.environ.get("INVENIO_S3_DOWNLOAD_FOLDER", "s3_downloads")
    output_path = os.environ.get("IMPORT_STATUS_OUTPUT_PATH", "import_status.json")
    stale_hours = float(os.environ.get("IMPORT_STATUS_STALE_HOURS", "30"))
    stuck_hours = float(os.environ.get("IMPORT_STATUS_STUCK_HOURS", "3"))

    result = check(s3_download_folder, stale_hours, stuck_hours)
    write_status(output_path, result)

    print(json.dumps(result, indent=2))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
