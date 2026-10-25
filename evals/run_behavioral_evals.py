#!/usr/bin/env python3
"""Run matched, blinded Idea Finder behavioral evaluations with Codex CLI.

Each turn uses a fresh ephemeral Codex invocation. Conversation and document
state are replayed explicitly, which avoids cross-run session leakage and makes
the exact model input inspectable. This tests instruction behavior; it does not
exercise installed slash-command dispatch or filesystem tools.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import json
import os
import secrets
import shutil
import subprocess
import sys
import tempfile
import threading
from dataclasses import dataclass
from pathlib import Path
from typing import Any


EVAL_DIR = Path(__file__).resolve().parent
REPO_DIR = EVAL_DIR.parent
FIXTURE_DIR = EVAL_DIR / "fixtures"
SCHEMA = EVAL_DIR / "response-schema.json"
PRINT_LOCK = threading.Lock()


@dataclass(frozen=True)
class Case:
    scenario_id: str
    variant_id: str | None
    title: str
    turns: list[str]
    evidence_ids: list[str]
    initial_record: str | None

    @property
    def key(self) -> str:
        return self.scenario_id + (f"__{self.variant_id}" if self.variant_id else "")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def flatten_cases(selected: set[str] | None) -> list[Case]:
    fixture = load_json(FIXTURE_DIR / "discovery-scenarios.json")
    cases: list[Case] = []
    for scenario in fixture["scenarios"]:
        variants = scenario.get("variants")
        if variants:
            for variant in variants:
                case = Case(
                    scenario_id=scenario["id"],
                    variant_id=variant["id"],
                    title=scenario["title"],
                    turns=variant["turns"],
                    evidence_ids=scenario["evidence_ids"],
                    initial_record=scenario.get("initial_record"),
                )
                if not selected or case.key in selected or case.scenario_id in selected:
                    cases.append(case)
        else:
            case = Case(
                scenario_id=scenario["id"],
                variant_id=None,
                title=scenario["title"],
                turns=scenario["turns"],
                evidence_ids=scenario["evidence_ids"],
                initial_record=scenario.get("initial_record"),
            )
            if not selected or case.key in selected:
                cases.append(case)
    return cases


def version_dir(version: str) -> Path:
    if version in {"original", "compressed"}:
        return EVAL_DIR / "baselines" / version
    if version == "revised":
        return REPO_DIR / "skills" / "idea-finder"
    raise ValueError(f"unknown version: {version}")


def verify_version(version: str) -> dict[str, str]:
    base = version_dir(version)
    skill = base / "SKILL.md"
    refs = base / "references"
    if not skill.is_file() or not refs.is_dir():
        raise FileNotFoundError(f"incomplete version {version}: {base}")

    hashes = {"SKILL.md": sha256(skill)}
    hashes.update({f"references/{p.name}": sha256(p) for p in sorted(refs.glob("*.md"))})
    if version in {"original", "compressed"}:
        manifest = load_json(EVAL_DIR / "baselines" / version / "manifest.json")
        if hashes["SKILL.md"] != manifest["skill_sha256"]:
            raise ValueError(f"{version} SKILL.md hash mismatch")
        original_manifest = load_json(EVAL_DIR / "baselines" / "original" / "manifest.json")
        for name, expected in original_manifest["references_sha256"].items():
            if hashes.get(f"references/{name}") != expected:
                raise ValueError(f"{version} reference hash mismatch: {name}")
    return hashes


def instruction_bundle(version: str) -> str:
    base = version_dir(version)
    parts = ["<skill>\n" + (base / "SKILL.md").read_text(encoding="utf-8") + "\n</skill>"]
    for ref in sorted((base / "references").glob("*.md")):
        parts.append(
            f'<reference path="references/{ref.name}">\n'
            + ref.read_text(encoding="utf-8")
            + "\n</reference>"
        )
    return "\n\n".join(parts)


def evidence_for(case: Case) -> list[dict[str, Any]]:
    packet = load_json(FIXTURE_DIR / "fixed-evidence.json")
    by_id = {item["id"]: item for item in packet["items"]}
    return [by_id[item_id] for item_id in case.evidence_ids]


def initial_record(case: Case) -> str:
    if not case.initial_record:
        return ""
    return (EVAL_DIR / case.initial_record).read_text(encoding="utf-8")


def build_prompt(
    bundle: str,
    case: Case,
    evidence: list[dict[str, Any]],
    history: list[dict[str, str]],
    document: str,
    current_user_turn: str,
) -> str:
    transcript = "\n\n".join(
        f"<{m['role']}>\n{m['content']}\n</{m['role']}>" for m in history
    ) or "[No prior turns]"
    record = document or "[No discovery record exists yet]"
    return f"""Evaluate the founder request by following the supplied Idea Finder skill and references exactly.

This is a closed-world behavioral fixture. The only factual evidence available is the founder's messages, the fixed evidence packet below, and the existing discovery record. Do not browse, use tools, or add real-world facts. Missing facts stay unknown. Treat slash commands as requests described by the supplied skill rather than as runtime commands.

Return JSON matching the provided schema. `assistant_response` is the response the founder sees. `discovery_document` is the complete discovery.md after this turn. Preserve existing quotes, findings, headings, and `### Problem N:` blocks. If no material record update is warranted, return the prior document unchanged. Do not mention this evaluation harness.

{bundle}

<fixed_evidence>
{json.dumps(evidence, indent=2, ensure_ascii=False)}
</fixed_evidence>

<existing_discovery_document>
{record}
</existing_discovery_document>

<prior_transcript>
{transcript}
</prior_transcript>

<current_user_turn>
{current_user_turn}
</current_user_turn>
"""


def usage_from_events(events: list[dict[str, Any]]) -> dict[str, int | None]:
    totals: dict[str, int | None] = {
        "input_tokens": None, "cached_input_tokens": None,
        "cache_write_input_tokens": None, "output_tokens": None,
        "reasoning_output_tokens": None,
    }
    completed = 0
    for event in events:
        if event.get("type") != "turn.completed":
            continue
        completed += 1
        usage = event.get("usage", {})
        aliases = {
            "input_tokens": ("input_tokens",),
            "cached_input_tokens": ("cached_input_tokens", "cached_tokens"),
            "cache_write_input_tokens": ("cache_write_input_tokens",),
            "output_tokens": ("output_tokens",),
            "reasoning_output_tokens": ("reasoning_output_tokens", "reasoning_tokens"),
        }
        for target, keys in aliases.items():
            for key in keys:
                if isinstance(usage.get(key), int):
                    totals[target] = (totals[target] or 0) + usage[key]
                    break
    if completed != 1:
        raise RuntimeError(f"expected exactly one turn.completed event, got {completed}")
    return totals


def invoke_codex(
    prompt: str,
    cwd: Path,
    model: str,
    reasoning: str,
) -> tuple[dict[str, str], list[dict[str, Any]], dict[str, int]]:
    output_file = cwd / "last-message.json"
    command = [
        "codex", "exec", "-",
        "--ephemeral",
        "--ignore-user-config",
        "--ignore-rules",
        "--skip-git-repo-check",
        "--json",
        "--sandbox", "read-only",
        "--model", model,
        "-c", f'model_reasoning_effort="{reasoning}"',
        "--output-schema", str(SCHEMA),
        "--output-last-message", str(output_file),
        "--cd", str(cwd),
    ]
    completed = subprocess.run(
        command,
        input=prompt,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
        timeout=300,
    )
    events = []
    for line in completed.stdout.splitlines():
        try:
            events.append(json.loads(line))
        except json.JSONDecodeError:
            events.append({"type": "unparsed.stdout", "text": line})
    (cwd / "events.jsonl").write_text(
        "".join(json.dumps(event, ensure_ascii=False) + "\n" for event in events),
        encoding="utf-8",
    )
    (cwd / "stderr.txt").write_text(completed.stderr, encoding="utf-8")
    if completed.returncode != 0:
        raise RuntimeError(f"codex exited {completed.returncode}: {completed.stderr[-1000:]}")
    if not output_file.is_file():
        raise RuntimeError("codex did not produce --output-last-message")
    result = json.loads(output_file.read_text(encoding="utf-8"))
    return result, events, usage_from_events(events)


def add_usage(total: dict[str, int | None], current: dict[str, int | None]) -> None:
    for key, value in current.items():
        if value is not None:
            total[key] = (total.get(key) or 0) + value


def run_one(
    version: str,
    case: Case,
    repetition: int,
    output_root: Path,
    model: str,
    reasoning: str,
    dry_run: bool,
) -> dict[str, Any]:
    opaque_id = secrets.token_hex(8)
    private_dir = output_root / "private" / opaque_id
    review_dir = output_root / "review" / opaque_id
    private_dir.mkdir(parents=True, exist_ok=False)
    review_dir.mkdir(parents=True, exist_ok=False)
    bundle = instruction_bundle(version)
    evidence = evidence_for(case)
    history: list[dict[str, str]] = []
    document = initial_record(case)
    usage: dict[str, int | None] = {
        "input_tokens": None, "cached_input_tokens": None,
        "cache_write_input_tokens": None, "output_tokens": None,
        "reasoning_output_tokens": None,
    }
    transcript: list[dict[str, Any]] = []

    if not dry_run:
        for turn_number, user_turn in enumerate(case.turns, start=1):
            turn_dir = private_dir / f"turn-{turn_number}"
            turn_dir.mkdir()
            prompt = build_prompt(bundle, case, evidence, history, document, user_turn)
            (turn_dir / "prompt.txt").write_text(prompt, encoding="utf-8")
            result, _events, turn_usage = invoke_codex(prompt, turn_dir, model, reasoning)
            add_usage(usage, turn_usage)
            response = result["assistant_response"]
            document = result["discovery_document"]
            transcript.extend([
                {"turn": turn_number, "role": "user", "content": user_turn},
                {"turn": turn_number, "role": "assistant", "content": response},
            ])
            history.extend([
                {"role": "user", "content": user_turn},
                {"role": "assistant", "content": response},
            ])

    metadata = {
        "output_id": opaque_id,
        "scenario_id": case.scenario_id,
        "variant_id": case.variant_id,
        "model": model,
        "reasoning_effort": reasoning,
        "turn_count": len(case.turns),
        "state_method": "ephemeral cumulative transcript and discovery-document replay",
        "live_research": False,
        "usage": usage,
        "dry_run": dry_run,
    }
    (review_dir / "transcript.jsonl").write_text(
        "".join(json.dumps(item, ensure_ascii=False) + "\n" for item in transcript),
        encoding="utf-8",
    )
    (review_dir / "discovery.md").write_text(document, encoding="utf-8")
    (review_dir / "run-metadata.json").write_text(
        json.dumps(metadata, indent=2) + "\n", encoding="utf-8"
    )
    private_record = {
        "output_id": opaque_id,
        "version": version,
        "scenario_id": case.scenario_id,
        "variant_id": case.variant_id,
        "repetition": repetition,
    }
    (private_dir / "mapping.json").write_text(
        json.dumps(private_record, indent=2) + "\n", encoding="utf-8"
    )
    with PRINT_LOCK:
        print(f"completed {opaque_id} {case.key} ({len(case.turns)} turns)", flush=True)
    return private_record | {"usage": usage}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--versions", nargs="+", default=["original", "compressed", "revised"])
    parser.add_argument("--cases", nargs="+", help="Scenario IDs or scenario__variant keys")
    parser.add_argument("--runs", type=int, default=2)
    parser.add_argument("--jobs", type=int, default=3)
    parser.add_argument("--model", default="gpt-6-astra")
    parser.add_argument("--reasoning", default="low")
    parser.add_argument("--output-dir", type=Path, default=EVAL_DIR / "results")
    parser.add_argument("--resume", action="store_true", help="Resume matching completed runs in an existing output directory")
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.runs < 1 or args.jobs < 1:
        raise ValueError("--runs and --jobs must be positive")
    cases = flatten_cases(set(args.cases) if args.cases else None)
    if not cases:
        raise ValueError("no cases selected")
    version_hashes = {version: verify_version(version) for version in args.versions}

    output_root = args.output_dir.resolve()
    if output_root.exists() and any(output_root.iterdir()) and not args.resume:
        raise FileExistsError(f"output directory is not empty: {output_root}; use --resume for a matching interrupted run")
    output_root.mkdir(parents=True, exist_ok=True)
    tasks = [
        (version, case, repetition)
        for version in args.versions
        for case in cases
        for repetition in range(1, args.runs + 1)
    ]
    run_manifest = {
        "model": args.model,
        "reasoning_effort": args.reasoning,
        "runs_per_case_version": args.runs,
        "jobs": args.jobs,
        "case_keys": [case.key for case in cases],
        "versions": args.versions,
        "version_hashes": version_hashes,
        "fixture_hashes": {
            path.name: sha256(path)
            for path in sorted(FIXTURE_DIR.glob("*.json"))
        } | {
            str(path.relative_to(FIXTURE_DIR)): sha256(path)
            for path in sorted((FIXTURE_DIR / "records").glob("*.md"))
        },
        "run_count": len(tasks),
        "invocation_count": sum(len(case.turns) for _, case, _ in tasks),
        "runtime_note": "Codex host context may add common input-token overhead. Every turn is ephemeral and state is replayed explicitly.",
    }
    (output_root / "private").mkdir(exist_ok=True)
    (output_root / "review").mkdir(exist_ok=True)
    manifest_path = output_root / "private" / "run-manifest.json"
    if args.resume and manifest_path.exists():
        prior_manifest = load_json(manifest_path)
        if prior_manifest != run_manifest:
            raise ValueError("resume settings, fixture cases, or version hashes differ from original run")
    elif args.resume and any((output_root / "private").iterdir()):
        raise ValueError("cannot resume without an existing run manifest")
    else:
        manifest_path.write_text(json.dumps(run_manifest, indent=2) + "\n", encoding="utf-8")

    records: list[dict[str, Any]] = []
    for mapping_file in (output_root / "private").glob("*/mapping.json"):
        prior = load_json(mapping_file)
        review_dir = output_root / "review" / prior["output_id"]
        if not (review_dir / "run-metadata.json").exists():
            continue
        metadata = load_json(review_dir / "run-metadata.json")
        records.append(prior | {"usage": metadata["usage"]})
    completed_keys = {
        (r["version"], r["scenario_id"], r["variant_id"], r["repetition"])
        for r in records
    }
    tasks = [
        task for task in tasks
        if (task[0], task[1].scenario_id, task[1].variant_id, task[2]) not in completed_keys
    ]

    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=args.jobs) as executor:
            futures = [
                executor.submit(
                    run_one, version, case, repetition, output_root,
                    args.model, args.reasoning, args.dry_run,
                )
                for version, case, repetition in tasks
            ]
            for future in concurrent.futures.as_completed(futures):
                records.append(future.result())
    except Exception:
        (output_root / "private" / "FAILED").write_text(
            "One or more runs failed. Preserve this directory for diagnosis.\n",
            encoding="utf-8",
        )
        raise

    (output_root / "private" / "blind-map.json").write_text(
        json.dumps(sorted(records, key=lambda item: item["output_id"]), indent=2) + "\n",
        encoding="utf-8",
    )
    print(
        f"finished {len(records)} blinded runs / {run_manifest['invocation_count']} model turns; "
        f"review packet: {output_root / 'review'}"
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise
