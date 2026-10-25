#!/usr/bin/env python3
"""serve.py — static file server + answer persistence for discovery.md.

Replaces `python3 -m http.server` so the frontend can POST answers back
to discovery.md without a full build pipeline.

Usage:
    python3 scripts/serve.py           # port 3737 (default)
    python3 scripts/serve.py 8080      # custom port
"""

import json
import re
import sys
from datetime import date
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler

ROOT = Path(__file__).resolve().parent.parent
UI_DIR = ROOT / "ui"
DISCOVERY_MD = Path.home() / "idea-finder" / "discovery.md"

SECTION_HEADER = "## QUESTION ANSWERS"


# ── Answer persistence ────────────────────────────────────────────────────────

def save_answer(data: dict) -> None:
    role     = data.get("roleLabel", "Unknown")
    question = data.get("question", "").strip()
    answer   = data.get("answer", "").strip()
    today    = date.today().isoformat()

    if not question or not answer:
        raise ValueError("question and answer are required")

    entry = f"\n### {role} — {today}\nQ: {question}\nA: {answer}\n"

    text = DISCOVERY_MD.read_text(encoding="utf-8") if DISCOVERY_MD.exists() else ""

    if SECTION_HEADER in text:
        # Append right after the section header (before any next ## section)
        idx = text.index(SECTION_HEADER) + len(SECTION_HEADER)
        m = re.search(r"\n## ", text[idx:])
        if m:
            pos = idx + m.start()
            text = text[:pos] + entry + text[pos:]
        else:
            text = text + entry
    else:
        # Create the section at the end of the file
        text = text.rstrip() + f"\n\n{SECTION_HEADER}\n" + entry

    DISCOVERY_MD.parent.mkdir(parents=True, exist_ok=True)
    DISCOVERY_MD.write_text(text, encoding="utf-8")
    print(f"  saved  [{role}] {question[:70]}")


# ── HTTP handler ──────────────────────────────────────────────────────────────

class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(UI_DIR), **kwargs)

    def log_message(self, fmt, *args):
        pass  # silence per-request logs; saves/errors print explicitly

    def do_POST(self):
        if self.path != "/save-answer":
            self.send_response(404)
            self.end_headers()
            return

        try:
            length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(length))
            save_answer(body)
            self._json({"ok": True})
        except Exception as exc:
            print(f"  error  {exc}")
            self._json({"ok": False, "error": str(exc)}, 500)

    def _json(self, data: dict, code: int = 200) -> None:
        payload = json.dumps(data).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 3737
    server = HTTPServer(("", port), Handler)
    print(f"serving  {UI_DIR}")
    print(f"answers  {DISCOVERY_MD}")
    print(f"→  http://localhost:{port}")
    server.serve_forever()
