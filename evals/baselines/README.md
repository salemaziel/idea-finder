# Evaluation baselines

These baselines freeze the two instruction states that existed before the useful-discovery revision.

- `original/` vendors the committed `HEAD` skill and every skill-local reference. Its manifest records the source commit and all hashes.
- `compressed/` vendors the uncommitted compressed instruction file that was present when revision work began plus its then-current references.

Do not update these files when the live skill changes. The evaluation runner must verify every hash before a baseline run. The vendored copies make the evaluation self-contained even if Git history is unavailable.
