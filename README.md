# Idea Finder — useful discovery

A discovery skill for founders seeking a profitable small business or a venture-scale startup. Start with the founder's goal, available time, constraints, lived experience and customer access. The outcome is a specific problem worth investigating, a candid account of the evidence, and a feasible next step that could change the decision.

## How discovery works

Start or resume with `/idea-finder`. An uncertain founder can explore overlooked work, life, community and relationship experience using an optional bank of 13 interview blocks. A founder with a concrete problem goes straight into that problem. Returning founders begin with new evidence and contradictions. Expect two or three relevant conversational questions at a time, not mandatory demographic intake.

Research follows a decision-relevant uncertainty. There are no search quotas or required early market estimates. When a conversation or artifact can teach more than another search, the skill recommends that step. Rare but costly problems stay eligible; a small business need not meet venture criteria.

The durable record is `~/idea-finder/discovery.md`. It preserves quotes, research, findings, contradictions, assessments and tests across sessions. Older records remain readable without migration; unexplained scores are labeled legacy assessments. The self-map summarizes the record and includes the full document.

## Commands

| Command | Result |
| --- | --- |
| `/idea-finder` | Start or resume broad exploration, focused investigation or evidence synthesis. |
| `/dig [role]` | Follow a concrete incident into consequences, workarounds, costs and unanswered questions. |
| `/market [role]` | Investigate relevant competitors, services, DIY and doing nothing; estimate a market only when useful to a decision. |
| `/persona [role]` | Evidence-grounded workflow/customer profile with unknowns and labeled inference. |
| `/score` | Assess pain intensity, frequency, willingness to pay, founder fit and accessibility, each out of ten. Unknown dimensions remain unknown; no total if evidence is missing. |
| `/compare [A] vs [B]` | Explain tradeoffs, evidence gaps and goal fit; conditional preference, pause or none ready are valid. |
| `/why-me [problem]` | Assess concrete founder strengths, gaps and ways to test them. |
| `/interview [contact]` | Tailor a non-leading script and process returned notes without losing quotes or contradictions. |
| `/sim [problem]` | Practice a skeptical customer conversation; fictional responses never count as demand evidence. |
| `/validate [problem]` | Set a contextual hypothesis, test, success/disconfirming signals and fallback before gathering results; prepare questions and an optional neutral outreach draft. |
| `/brief` | Produce a candid one-page founder brief, including evidence limits and the next test. |
| `/next` | Choose one feasible action addressing the uncertainty most likely to change the decision. |
| `/render` | Rebuild and serve the visual self-map at `http://localhost:3737/Self-Map.html`. |

Evidence confidence is separate from attractiveness: assumptions and indirect evidence are low confidence; specific firsthand reports are medium; high confidence requires independent reports converging with behavioral or economic evidence for the claim. A persona, simulation or score cannot establish demand. Solution experiments begin only when the founder explicitly chooses that stage. Outreach remains a draft until sending or publishing is requested.

## Installation

For the complete skill and visual map:

```bash
git clone git@github.com:zhenya-vlasov/idea-finder.git ~/idea-finder
mkdir -p ~/.claude/skills
ln -s ~/idea-finder/skills/idea-finder ~/.claude/skills/idea-finder
```

Alternatively, `npx skills add zhenya-vlasov/idea-finder` installs the skill through the skills installer. A skill-only installation may omit the scripts and UI; use the full checkout for rendering. These remote installation commands do not include unpublished local revisions.

The repository includes Claude and Codex plugin manifests. In a host with the skill loaded, request `/idea-finder` or ask for business-problem discovery.

## Local self-map

From the full project checkout, after creating a discovery record:

```bash
python3 scripts/render.py
python3 scripts/serve.py
```

Open `http://localhost:3737/Self-Map.html`. Both scripts use `~/idea-finder/discovery.md` even when the installation is elsewhere. The renderer writes `ui/data.jsx` in the installation; the server persists answers in the same home-directory record. Re-render after answers to refresh map summaries. The renderer also accepts explicit input and output paths for offline conversion; the interactive server always uses the home-directory record.

The UI includes role views, opportunities, network, open questions and the full source document. Existing headings and `### Problem N:` blocks remain stable. New evidence fields are retained in the full document; the map does not display every assessment field as a separate widget. The browser loads React and Babel from a CDN, so an offline browser may not render the app.

## Files and verification

- `skills/idea-finder/SKILL.md`: routing, discovery principles and command index.
- `skills/idea-finder/references/`: authoritative question bank, command guidance, assessment and document templates.
- `references/`: compatibility pointers to the skill-local references.
- `scripts/`: Markdown-to-map renderer and answer server.
- `ui/`: visual self-map.
- `evals/`: frozen original/compressed baselines, fixed multi-turn scenarios, review rubric and compatibility checks.
- `REVISION.md`: behavior inventory, changes, verification evidence and limitations.

The evaluation compares discovery quality, decision usefulness and evidence fidelity under matched model settings, fixed research evidence, two runs per case and blinded review. Static checks and instruction length do not establish improved discovery. See [the evaluation protocol](evals/README.md) and [revision report](REVISION.md) for actual results and gaps.
