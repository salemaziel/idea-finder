# Useful discovery revision

## Behavior inventory and implementation plan (before rewrite)

| Existing behavior | Treatment | Reason |
| --- | --- | --- |
| Durable discovery.md, resume, exact quotes and research | Preserve | Source material and continuity are essential |
| Whole-life discovery and 13 blocks | Preserve as optional bank | Overlooked experiences matter; exhaustive intake adds effort |
| All existing command names and document headings | Preserve | User and renderer compatibility |
| Two or three conversational questions | Preserve and strengthen | Follow incidents and contradictions before moving on |
| Five ten-point dimensions in original command/README | Canonicalize | Deferred rubric currently conflicts with ten five-point dimensions |
| Detailed commands in original, terse compressed table | Restore in deferred guidance | Depth should be available without mandatory full loading |
| Demographics first, every block, three searches per role, early TAM | Intentionally replace | Route from founder goal and consequential uncertainties |
| Automatic elimination, annual-pain rejection, fixed validation gates | Intentionally replace | Context, costly rare events, access and purchase cycles matter |
| Confident brief and simulated WTP scoring | Intentionally replace | Preserve uncertainty; rehearsal cannot establish demand |
| Duplicate root and skill references | Replace root bodies with pointers | One authoritative source prevents conflicting rules |
| Renderer home path vs server install path | Align to home path | Answers and rendering must use the same durable record |

Sequence: snapshot committed original and working compressed bundles; create fixed multi-turn fixtures, rubric and compatibility tests; obtain an independent rubric review; revise instructions/references/README; run compatibility tests and matched behavioral evaluation; review findings and report evidence and limitations. No commits, pushes, publishing or new dependencies.

Behavioral acceptance requires matched two-run comparisons with blind annotated review; static checks alone cannot establish improvement. Original source quotes and old unexplained scores remain preserved, with legacy assessments labeled rather than silently reinterpreted.

## Implemented revision and verification (2026-09-26)

The main skill now routes from the founder's goal, time, constraints, observations and customer access. Whole-life discovery remains available through an optional 13-block bank. Focused commands have deferred guidance, and the skill-local five-by-ten assessment is the single scoring authority. Evidence confidence is separate from attractiveness; unknown dimensions stay unknown, with no incomplete total. Rare costly problems and small-business goals remain eligible. Root references now point to the skill-local guidance. The README describes the revised behavior and installation limits.

The renderer and answer server now both use `~/idea-finder/discovery.md`; the server creates its parent directory when needed. Six compatibility tests passed, including legacy and revised parsing, preserved headings/quotes in the full document, isolated-home rendering, and HTTP GET/POST answer persistence followed by rerendering. Python compilation, JSON fixture parsing, reference link checks and `git diff --check` passed. The pre-fix path assertion failed as expected and passed after the change.

An independent reviewer approved the behavior fixtures and rubric after five corrections, documented in `evals/design-review.md`. The original and compressed baselines are self-contained and hash-verified. Seven scenarios/eight variants, focused-command cases, and blinded review instructions are in `evals/`. The pilot completed one matched three-version case with Luna, and the broader run recorded seven complete founder runs before the user asked to scale back. The broad run was stopped; it did not reach the required 48 runs or blinded grading. No claim of higher average discovery quality or decision usefulness is justified. The observed pilot outputs were useful for runner smoke testing, not an acceptance result.

**Measured model usage from completed turn events:** the three-version pilot used 296,958 input tokens (17,152 cached input) and 20,469 output tokens across nine turns. The interrupted broader run recorded 1,119,951 input tokens (398,336 cached input) and 49,498 output tokens across 33 completed turns; some runs were incomplete. An earlier frontier-model probe recorded 69,545 input, 7,199 output and 138 reasoning-output tokens across two completed turns; an initialization probe recorded 23,484 input and 5 output tokens. Across these completed events, the measured minimum is 1,509,938 input tokens (415,488 cached input, included within input) and 77,171 output tokens, plus 138 reasoning-output tokens. Interrupted in-flight turns may have incurred unreported usage. No dollar cost is asserted without a reliable price/rate source.

**Gains established by inspection and tests:** intake and research quotas are removed; the commands, document headings, legacy record, and full-document self-map survive; server answers now target the same record the renderer reads. **Regressions established:** none in the tested document-to-map workflow. **Unresolved limitations:** the full two-run blinded behavior acceptance was intentionally stopped at the user's request, and focused command behavior has fixture contracts but no complete model-run results. The map retains new evidence fields in the full document rather than separate widgets. The CLI harness preloads all references, replays conversation state between ephemeral turns and disables live research, so its results would not prove installed command dispatch or live browser behavior. Local partial transcripts remain in ignored `evals/results/`; the pilot remains under `/tmp`.

No publishing, commit or push was performed.
