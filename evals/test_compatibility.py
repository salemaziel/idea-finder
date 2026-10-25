"""Compatibility tests for discovery records and the Self-Map workflow."""

from __future__ import annotations

import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import threading
import unittest
import urllib.request
from contextlib import contextmanager
from http.server import HTTPServer
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RENDER_PATH = ROOT / "scripts" / "render.py"
SERVE_PATH = ROOT / "scripts" / "serve.py"
ORIGINAL_TEMPLATE = ROOT / "evals" / "baselines" / "original" / "references" / "doc-template.md"
LIVE_TEMPLATE = ROOT / "skills" / "idea-finder" / "references" / "doc-template.md"
RECORDS = ROOT / "evals" / "fixtures" / "records"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def structural_headings(markdown: str) -> list[str]:
    """Return structural headings from the template's fenced document."""
    fenced = re.search(r"```\n(.*?)\n```", markdown, re.DOTALL)
    if fenced is None:
        raise AssertionError("document template must contain a fenced template")
    return [
        line
        for line in fenced.group(1).splitlines()
        if line.startswith("## ") or re.match(r"^### Problem(?: \[N\]| \d+):", line)
    ]


@contextmanager
def running_server(serve_module, ui_dir: Path, discovery_md: Path):
    original_ui = serve_module.UI_DIR
    original_discovery = serve_module.DISCOVERY_MD
    serve_module.UI_DIR = ui_dir
    serve_module.DISCOVERY_MD = discovery_md
    server = HTTPServer(("127.0.0.1", 0), serve_module.Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_port}"
    finally:
        server.shutdown()
        thread.join(timeout=5)
        server.server_close()
        serve_module.UI_DIR = original_ui
        serve_module.DISCOVERY_MD = original_discovery


class DiscoveryPathCompatibilityTests(unittest.TestCase):
    def test_server_and_renderer_use_same_home_discovery_record(self):
        render = load_module("idea_finder_render_paths", RENDER_PATH)
        serve = load_module("idea_finder_serve_paths", SERVE_PATH)

        self.assertEqual(serve.DISCOVERY_MD, render.DEFAULT_INPUT)
        self.assertEqual(render.DEFAULT_INPUT, Path.home() / "idea-finder" / "discovery.md")

    def test_default_cli_renders_from_isolated_home_into_isolated_install(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp = Path(temp_dir)
            isolated_home = temp / "home"
            discovery_dir = isolated_home / "idea-finder"
            discovery_dir.mkdir(parents=True)
            record = (RECORDS / "revised.md").read_text(encoding="utf-8")
            (discovery_dir / "discovery.md").write_text(record, encoding="utf-8")

            install = temp / "install"
            (install / "scripts").mkdir(parents=True)
            (install / "ui").mkdir()
            shutil.copy2(RENDER_PATH, install / "scripts" / "render.py")

            env = os.environ.copy()
            env["HOME"] = str(isolated_home)
            result = subprocess.run(
                [sys.executable, str(install / "scripts" / "render.py")],
                cwd=install,
                env=env,
                capture_output=True,
                text=True,
                check=False,
            )

            output = install / "ui" / "data.jsx"
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue(output.exists())
            self.assertIn("Move-in evidence reconstruction", output.read_text(encoding="utf-8"))


class DiscoveryRecordCompatibilityTests(unittest.TestCase):
    def setUp(self):
        self.render = load_module(f"idea_finder_render_{self.id()}", RENDER_PATH)

    def test_legacy_record_parses_candidate_and_preserves_source_quote_in_full_document(self):
        raw = (RECORDS / "legacy-returning.md").read_text(encoding="utf-8")

        parsed = self.render.parse_document(raw)
        generated = self.render.generate_data_jsx(parsed, raw)

        self.assertEqual(parsed["roles"][0]["name"], "Agency operations lead")
        self.assertEqual(parsed["candidate_problems"][0]["name"], "Contractor-invoice reconciliation")
        self.assertIn('"Contractor invoices always arrive in different formats."', generated)
        self.assertIn("### Problem 1: Contractor-invoice reconciliation", generated)
        self.assertIn(f"const DISCOVERY_DOC = `{raw}`;", generated)

    def test_revised_record_parses_evidence_fields_and_preserves_full_document(self):
        raw = (RECORDS / "revised.md").read_text(encoding="utf-8")

        parsed = self.render.parse_document(raw)
        generated = self.render.generate_data_jsx(parsed, raw)
        candidate = parsed["candidate_problems"][0]

        self.assertEqual(parsed["roles"][0]["name"], "Property manager")
        self.assertEqual(candidate["name"], "Move-in evidence reconstruction")
        self.assertEqual(
            candidate["details"]["evidence confidence"],
            "Medium for one witnessed incident; low for prevalence and willingness to pay",
        )
        self.assertIn("Founder witnessed one incident", candidate["details"]["supporting evidence"])
        self.assertEqual(candidate["details"]["frequency"], "Unknown")
        self.assertIn('Exact quote: "I would pay to never reconstruct that trail again."', generated)
        self.assertIn("### Problem 1: Move-in evidence reconstruction", generated)
        self.assertIn(f"const DISCOVERY_DOC = `{raw}`;", generated)

    def test_live_template_preserves_original_structural_headings(self):
        original = ORIGINAL_TEMPLATE.read_text(encoding="utf-8")
        live = LIVE_TEMPLATE.read_text(encoding="utf-8")

        self.assertEqual(structural_headings(live), structural_headings(original))


class SelfMapHttpCompatibilityTests(unittest.TestCase):
    def test_get_and_save_answer_update_same_record_then_rerender_without_data_loss(self):
        render = load_module("idea_finder_render_http", RENDER_PATH)
        serve = load_module("idea_finder_serve_http", SERVE_PATH)
        with tempfile.TemporaryDirectory() as temp_dir:
            temp = Path(temp_dir)
            ui = temp / "ui"
            ui.mkdir()
            page = "<!doctype html><title>Idea Finder Self-Map</title>"
            (ui / "Self-Map.html").write_text(page, encoding="utf-8")
            discovery = temp / "idea-finder" / "discovery.md"
            discovery.parent.mkdir()
            original = (RECORDS / "revised.md").read_text(encoding="utf-8")
            discovery.write_text(original, encoding="utf-8")

            with running_server(serve, ui, discovery) as base_url:
                with urllib.request.urlopen(f"{base_url}/Self-Map.html", timeout=5) as response:
                    self.assertEqual(response.status, 200)
                    self.assertEqual(response.read().decode(), page)

                payload = json.dumps(
                    {
                        "roleLabel": "Property manager",
                        "question": "What happened in the most recent dispute?",
                        "answer": "We spent two hours matching 43 photos to timestamps.",
                    }
                ).encode()
                request = urllib.request.Request(
                    f"{base_url}/save-answer",
                    data=payload,
                    headers={"Content-Type": "application/json"},
                    method="POST",
                )
                with urllib.request.urlopen(request, timeout=5) as response:
                    self.assertEqual(response.status, 200)
                    self.assertEqual(json.loads(response.read()), {"ok": True})

            updated = discovery.read_text(encoding="utf-8")
            rendered = render.generate_data_jsx(render.parse_document(updated), updated)

            self.assertIn('Exact quote: "I would pay to never reconstruct that trail again."', updated)
            self.assertIn("### Problem 1: Move-in evidence reconstruction", updated)
            self.assertIn("A: We spent two hours matching 43 photos to timestamps.", updated)
            self.assertIn("A: We spent two hours matching 43 photos to timestamps.", rendered)
            self.assertIn(f"const DISCOVERY_DOC = `{updated}`;", rendered)


if __name__ == "__main__":
    unittest.main()
