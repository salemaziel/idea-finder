# Idea Finder behavioral evaluation

This suite compares `original`, `compressed`, and `revised` discovery behavior on identical multi-turn founder scenarios and fixed evidence. It evaluates whether the skill helps a founder find an accessible problem and choose a judgment-changing next step; instruction length and static lint scores are diagnostics only.

## Comparison protocol

1. Materialize one version with its skill-local references and verify its baseline hashes.
2. Run every case in `fixtures/discovery-scenarios.json` twice with the same model, reasoning effort, tool policy, and evidence packet. Start each run from a fresh isolated working directory and conversation. The Codex CLI still uses the host authentication store; `--ignore-user-config` and `--ignore-rules` suppress user config and rules for the model call. Do not reuse generated discovery records between runs.
3. Disable live research. The model may use only the evidence IDs named by the fixture from `fixtures/fixed-evidence.json`. A request for more evidence is valid; invented facts are not.
4. Preserve multi-turn state within a run. Send fixture turns in order without adapting their wording to a version's response.
5. Save the full transcript, final discovery document, model settings, tool events, and actual input/output/cached/reasoning token counts reported by the runtime.
6. Replace version and run names with random opaque IDs before review. Keep the mapping outside the review packet. Randomize output order independently for each reviewer.
7. Have at least one reviewer score all outputs using `rubric.md`. Reviewers record a score and one transcript citation for every dimension, plus every applicable failure gate.
8. Unblind only after scores and annotations are locked. Report per-case and aggregate results, run-to-run spread, token costs, gains, regressions, and unresolved limitations.

The comparison is incomplete if any version/case has fewer than two successful runs, settings differ, a reviewer can infer version labels from filenames, or token usage is estimated rather than read from runtime events.

`run_behavioral_evals.py` loads each frozen skill and all of its references into the prompt, then uses a fresh ephemeral Codex CLI call per turn. It replays prior user/assistant turns and the latest generated discovery document explicitly. This tests instructions under fixed evidence; it does not test installed slash-command dispatch, selective reference loading, or live browsing. The Codex host may add common input-token overhead. Runtime events, rather than local estimates, determine token counts. The runner sends only repository skill instructions and synthetic fixtures to the model runtime; review those inputs before using it with new records. Each turn has a five-minute timeout.

## Acceptance

- No revised output trips any failure gate. Baseline failures remain reported diagnostics and do not independently block acceptance.
- Revised average `discovery_quality` and `decision_usefulness` each equal or exceed both baselines.
- Revised evidence fidelity does not score below either baseline in any scenario.
- Resume, legacy/revised rendering, and focused-command checks pass.
- Every comparative judgment includes an annotated transcript example.

If these conditions are not met, the result is a diagnostic. Revise the weak behavior and repeat the full matched comparison rather than declaring success.
