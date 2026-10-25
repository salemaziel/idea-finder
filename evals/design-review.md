# Independent fixture and rubric review

An independent `critic` agent reviewed the behavior inventory, fixtures, rubric, and compatibility expectations before the live skill rewrite. The first pass rejected the fixture gate. It required five corrections:

1. Count only founder-response questions in conversational turns, excluding generated interview scripts and command deliverables.
2. Give full specificity credit to a precisely investigated focused problem without demanding artificial novelty.
3. Add focused command cases covering the promised outputs and record updates.
4. Add explicit legacy and revised resume/render fixtures, with parser candidate checks and full-document source preservation rather than an unsupported candidate UI widget assertion.
5. Check the canonical five 10-point dimensions, unknown/no-total behavior, confidence separated from attractiveness, and venture considerations outside the common score.

The corrected fixtures and rubric passed the review gate before the rewrite was applied. The reviewer also confirmed that baseline snapshots are self-contained and hash-verifiable, and that any revised failure gate blocks acceptance while baseline failures are reported as diagnostics.

This review approved the evaluation design. It did not grade model transcripts or establish behavioral superiority; those require the matched, blinded runs described in `README.md`.
