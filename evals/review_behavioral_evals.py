#!/usr/bin/env python3
"""Blindly grade complete Idea Finder behavior packets, then unblind for a report."""

from __future__ import annotations

import argparse
import concurrent.futures
import json
import secrets
import subprocess
import sys
from pathlib import Path

from run_behavioral_evals import EVAL_DIR, evidence_for, flatten_cases, load_json, usage_from_events

RUBRIC = (EVAL_DIR / "rubric.md").read_text(encoding="utf-8")
SCHEMA = EVAL_DIR / "review_schema.json"
DIMS = (
    "adaptive_listening", "specificity_originality", "evidence_fidelity",
    "contradiction_response", "decision_usefulness", "founder_effort",
)


def make_prompt(packet: Path) -> str:
    meta = load_json(packet / "run-metadata.json")
    cases = {c.key: c for c in flatten_cases(None)}
    key = meta["scenario_id"] + (f"__{meta['variant_id']}" if meta["variant_id"] else "")
    case = cases[key]
    initial = (EVAL_DIR / case.initial_record).read_text(encoding="utf-8") if case.initial_record else "[No prior record]"
    return f"""You are a blind evaluator of a founder-discovery transcript. The instruction version and run number are hidden. Judge only the supplied transcript, final record, fixed evidence, and rubric. Do not browse or use tools. Cite an exact turn and short supporting span for each dimension and any failure gate. A score of 4 requires the rubric's full conditions. Avoid inferring missing facts. If a claim is ambiguous, state that in uncertainty_note. Use [] for failure_gates when no gate is present. Use null for assessment-contract checks only if no candidate assessment was made or updated. Return only schema-valid JSON and do not mention an instruction version.

<rubric>
{RUBRIC}
</rubric>

<output_id>{meta['output_id']}</output_id>
<scenario_id>{meta['scenario_id']}</scenario_id>
<fixed_evidence>
{json.dumps(evidence_for(case), ensure_ascii=False, indent=2)}
</fixed_evidence>
<initial_record>
{initial}
</initial_record>
<transcript>
{(packet / 'transcript.jsonl').read_text(encoding='utf-8')}
</transcript>
<final_discovery_document>
{(packet / 'discovery.md').read_text(encoding='utf-8')}
</final_discovery_document>
"""


def grade_one(packet: Path, grade_root: Path, model: str, reasoning: str) -> str:
    output_id = packet.name
    target = grade_root / output_id
    target.mkdir(parents=True, exist_ok=True)
    existing = target / "assessment.json"
    if existing.exists():
        return output_id
    prompt = make_prompt(packet)
    (target / "prompt.txt").write_text(prompt, encoding="utf-8")
    command = [
        "codex", "exec", "-", "--ephemeral", "--ignore-user-config", "--ignore-rules",
        "--skip-git-repo-check", "--json", "--sandbox", "read-only",
        "--model", model, "-c", f'model_reasoning_effort="{reasoning}"',
        "--output-schema", str(SCHEMA), "--output-last-message", str(target / "last-message.json"),
        "--cd", str(target),
    ]
    result = subprocess.run(command, input=prompt, text=True, capture_output=True, timeout=300, check=False)
    (target / "stderr.txt").write_text(result.stderr, encoding="utf-8")
    (target / "events.jsonl").write_text(result.stdout, encoding="utf-8")
    if result.returncode:
        raise RuntimeError(f"grader failed for {output_id}: {result.stderr[-300:]}")
    events = [json.loads(line) for line in result.stdout.splitlines()]
    usage = usage_from_events(events)
    assessment = load_json(target / "last-message.json")
    if assessment.get("output_id") != output_id:
        raise ValueError(f"grader output ID mismatch: {output_id}")
    for dim in DIMS:
        score = assessment["scores"][dim]
        if not isinstance(score["score"], int) or not 0 <= score["score"] <= 4 or not score["citation"]:
            raise ValueError(f"missing score/citation {output_id} {dim}")
    (target / "assessment.json").write_text(json.dumps(assessment, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (target / "usage.json").write_text(json.dumps(usage, indent=2) + "\n", encoding="utf-8")
    print(f"graded {output_id}", flush=True)
    return output_id


def aggregate(root: Path) -> dict:
    mapping = load_json(root / "private" / "blind-map.json")
    out = []
    for item in mapping:
        grade = load_json(root / "grades" / item["output_id"] / "assessment.json")
        packet = load_json(root / "review" / item["output_id"] / "run-metadata.json")
        quality = sum(grade["scores"][d]["score"] for d in DIMS[:4]) / 4
        out.append(item | {"grade": grade, "quality": quality, "generation_usage": packet["usage"],
                           "review_usage": load_json(root / "grades" / item["output_id"] / "usage.json")})
    if len(out) != load_json(root / "private" / "run-manifest.json")["run_count"]:
        raise ValueError("incomplete graded output set")
    grouped = {}
    for r in out:
        grouped.setdefault(r["version"], []).append(r)
    version_stats = {}
    for version, rows in grouped.items():
        avg = lambda values: sum(values) / len(values)
        usage = {k: sum((r["generation_usage"].get(k) or 0) for r in rows) for k in rows[0]["generation_usage"]}
        version_stats[version] = {
            "count": len(rows), "discovery_quality_mean": avg([r["quality"] for r in rows]),
            "decision_usefulness_mean": avg([r["grade"]["scores"]["decision_usefulness"]["score"] for r in rows]),
            "evidence_fidelity_mean": avg([r["grade"]["scores"]["evidence_fidelity"]["score"] for r in rows]),
            "founder_effort_mean": avg([r["grade"]["scores"]["founder_effort"]["score"] for r in rows]),
            "failure_gates": sum(bool(r["grade"]["failure_gates"]) or any(v is False for v in r["grade"]["assessment_contract"].values()) for r in rows),
            "generation_usage": usage,
        }
    comparisons = []
    for case_key in sorted({r["scenario_id"] + (f"__{r['variant_id']}" if r["variant_id"] else "") for r in out}):
        row = {"case": case_key}
        for version in grouped:
            samples = [r for r in grouped[version] if r["scenario_id"] + (f"__{r['variant_id']}" if r["variant_id"] else "") == case_key]
            row[version] = {
                "quality": [r["quality"] for r in samples],
                "decision": [r["grade"]["scores"]["decision_usefulness"]["score"] for r in samples],
                "evidence": [r["grade"]["scores"]["evidence_fidelity"]["score"] for r in samples],
                "gates": [r["grade"]["failure_gates"] for r in samples],
                "output_ids": [r["output_id"] for r in samples],
            }
        comparisons.append(row)
    revised = version_stats["revised"]
    acceptance = {
        "no_revised_gates": revised["failure_gates"] == 0,
        "quality_not_worse": all(revised["discovery_quality_mean"] >= version_stats[v]["discovery_quality_mean"] for v in ("original", "compressed")),
        "decision_not_worse": all(revised["decision_usefulness_mean"] >= version_stats[v]["decision_usefulness_mean"] for v in ("original", "compressed")),
        "evidence_not_worse_each_case": all(
            sum(row["revised"]["evidence"]) >= sum(row[v]["evidence"])
            for row in comparisons for v in ("original", "compressed")
        ),
    }
    result = {"version_stats": version_stats, "cases": comparisons, "acceptance": acceptance,
              "review_usage": {k: sum((r["review_usage"].get(k) or 0) for r in out) for k in out[0]["review_usage"]}}
    (root / "aggregate.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=EVAL_DIR / "results")
    parser.add_argument("--model", default="gpt-6-luna")
    parser.add_argument("--reasoning", default="low")
    parser.add_argument("--jobs", type=int, default=6)
    args = parser.parse_args()
    root = args.output_dir.resolve()
    manifest = load_json(root / "private" / "run-manifest.json")
    packets = [p for p in (root / "review").iterdir() if (p / "run-metadata.json").exists()]
    if len(packets) != manifest["run_count"]:
        raise ValueError(f"expected {manifest['run_count']} complete outputs, got {len(packets)}")
    secrets.SystemRandom().shuffle(packets)
    grade_root = root / "grades"
    grade_root.mkdir(exist_ok=True)
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.jobs) as pool:
        futures = [pool.submit(grade_one, p, grade_root, args.model, args.reasoning) for p in packets]
        for future in concurrent.futures.as_completed(futures):
            future.result()
    summary = aggregate(root)
    print(json.dumps(summary["acceptance"], indent=2))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise
