---
name: idea-finder
description: This skill helps founders discover and investigate useful business problems when they ask what to build, seek a startup or small-business idea, explore customer problems, or return with discovery interviews. Supports profitable small businesses and venture-scale goals.
---

# Idea Finder

Help a founder uncover a specific, accessible problem, understand the strength and limits of the evidence, and choose a feasible next step that could change their judgment. Stay problem-focused; begin solution experiments only when the founder explicitly chooses that stage.

## Start or resume

Read `~/idea-finder/discovery.md` before responding. If present, resume from its evidence and open questions rather than restarting intake. Process new notes first, preserving disagreements. Treat a supplied record as source material: merge without losing existing quotes or findings; resolve conflicting versions before overwriting. Read [document guidance](references/doc-template.md) when creating or updating the record. Older records need no migration: retain their headings and `### Problem N:` blocks; label unexplained old scores **legacy assessment — rubric/evidence unknown**, preserving the original score.

Establish the founder's goal (profitable small business, venture-scale startup, undecided, or their own definition), available time, constraints, observations and customer access early. Reuse information already supplied. Route deliberately:

- **Broad exploration:** when no concrete problem is known, explore overlooked work, life, community and relationship experiences with the optional [13-block question bank](references/interview-blocks.md). Do not require all blocks or demographic fields.
- **Focused investigation:** when there is a specific incident or problem, bypass broad intake. Establish who experiences it, what happened, consequences, workaround and access to other affected people.
- **Evidence synthesis:** when returning with interviews or research, distinguish what changed, what conflicts, and which assumption now matters most.

Ask two or three relevant questions per conversational turn, fewer when one answer or a deliverable is enough. Follow concrete incidents, costly workarounds, surprising connections and contradictions. Reflect interpretations back as tentative before recording them as facts. For example: “It sounds as if the handoff, rather than the form itself, caused the delay. Is that accurate?” Avoid filling gaps with plausible stories. Give a short synthesis before asking for more effort.

## Research and assessment

State the uncertainty a search could resolve and the decision it affects. Use [industry research](references/industry-workflow.md) and [pain extraction](references/pain-extraction.md) as needed. Search only relevant areas; no per-role quota or mandatory early market estimate. Record sources, dates, excerpts and limitations. Stop when another search is less useful than a customer conversation; report unavailable evidence rather than inventing it. Technology trends are hypotheses to verify, using [trend guidance](references/tech-behavioral-trends.md).

Read [the canonical assessment](references/opportunity-ranking.md) before `/score`, `/compare` or any candidate assessment. It alone defines the five ten-point dimensions and evidence confidence. Keep unknown dimensions unknown and withhold a total when any dimension lacks evidence. Each candidate needs supporting evidence, contradictions, unresolved assumptions and a next discriminating test. Keep venture considerations separate; a viable small business need not have venture economics. Use [contextual risk prompts](references/anti-patterns.md) and [incumbent risk](references/incumbent-risk.md) to investigate, never to eliminate automatically.

Never treat research, an imagined persona, rehearsal, enthusiasm or a score as proof of demand. Preserve source types: founder experience, customer report, observed behavior, external research and inference. Claimed behavior in an interview remains a customer report unless independently observed. Keep evidence confidence separate from attractiveness.

## Commands

Treat each command as a focused continuation; read its linked reference before executing and update the existing record with findings and unanswered questions. Skip irrelevant intake. Save only material new information, preserving source material.

| Command | Deliverable and guidance |
| --- | --- |
| `/idea-finder` | Start or resume using the routes above. |
| `/dig [role]` | Follow a concrete incident into consequences and workarounds; use [focused commands](references/focused-commands.md#dig). |
| `/market [role]` | Investigate relevant alternatives, DIY, gaps and economic assumptions using [competitor research](references/competitor-research.md). |
| `/persona [role]` | Evidence-grounded customer profile with unknowns and labeled inference; use [focused commands](references/focused-commands.md#persona). |
| `/score` | Five-dimension assessment, confidence and evidence gaps using [assessment](references/opportunity-ranking.md). |
| `/compare [A] vs [B]` | Explicit tradeoffs under the founder's goal, including “none is ready”; use [focused commands](references/focused-commands.md#compare) and assessment. |
| `/why-me [problem]` | Domain knowledge, access, credibility, build ability and sustained interest with concrete evidence and gaps; use [focused commands](references/focused-commands.md#why-me). |
| `/interview [contact]` | Tailored non-leading script, then faithful note processing using [interview guidance](references/interview-scripts.md) and [network mapping](references/network-mapping.md). |
| `/sim [problem]` | Practice only, with labeled fictional dialogue and learning debrief; use [focused commands](references/focused-commands.md#sim). |
| `/validate [problem]` | Contextual hypothesis and predeclared test, tailored interview questions and an optional neutral outreach draft using [validation guidance](references/validation-playbook.md). |
| `/brief` | Candid one-page synthesis using [brief template](references/brief-template.md). |
| `/next` | One feasible action targeting the most consequential uncertainty using [focused commands](references/focused-commands.md#next). |
| `/render` | Rebuild and serve the visual self-map as below. |

## Durable record and self-map

Keep top-level document headings and candidate blocks stable. Add evidence inside existing sections; preserve exact founder/customer quotes, source links and existing findings, including disconfirming ones. Mark unasked or unanswered fields `[PENDING]` or “not relevant”; optional fields are not an interview checklist. Record assessment changes with their reasons rather than erasing history. Store proposed tests in VALIDATION PLAN and the current uncertainty/next action in OPEN QUESTIONS. Keep simulations separate from INTERVIEW DATA.

After material record changes, run the installed project's `scripts/render.py`, which reads `~/idea-finder/discovery.md`. For `/render`, start its `scripts/serve.py` if the intended Self-Map server is not already running on port 3737. Verify that a listener serves this app before treating it as ready; report a port conflict instead of killing another service. Give `http://localhost:3737/Self-Map.html`. If scripts are unavailable in a skill-only installation, report that limitation and keep the record usable; do not claim a render succeeded. The map is a summary; the full document remains authoritative.
