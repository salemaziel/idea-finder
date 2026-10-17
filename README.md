# Idea Finder — Self Discovery Agent

> A Claude Code skill that helps you systematically find the right problem to build a company around — before you commit your time and money.

---

## The problem with finding a startup idea

Most founders don't fail because they can't build. They fail because they build something nobody needed badly enough to pay for.

The standard advice — "find a problem you're passionate about," "scratch your own itch," "talk to users" — is true but hollow. Passion is not signal. Your own itch might be a niche of one. "Talk to users" doesn't tell you *how* to talk to them, what questions to ask, or how to tell real pain from polite feedback.

What's missing is a structured process: a way to systematically map your whole world — your work, your hobbies, your relationships, your frustrations — and extract from it the problems that are narrow enough to solve, painful enough to pay for, and accessible enough to sell.

That's what this skill does.

⭐ Star this repo if you want Claude to research your ideas.

---

## What it does

Idea Finder is a Claude Code skill that acts as a co-founder discovery agent. It interviews you about your life and expertise, researches every role you inhabit as a potential market, scores the opportunities it finds, and helps you validate the strongest ones before you commit.

It keeps a running `discovery.md` — your complete discovery record — and renders it as a visual self-map you can explore in a browser.

The skill knows when to push, when to go deeper, and when to tell you a problem isn't real. It doesn't tell you what to build. It helps you find problems worth solving and gives you the tools to test whether they're real.

---

## How it works

### Session 1 — The interview

You type `/idea-finder`. The skill interviews you across 13 structured blocks: your career history, your daily frustrations, your hobbies and communities, your personal life situations, and — critically — the specific people in your network.

By the end, you have a **Roles List**: every identity you inhabit (software engineer, homeowner, immigrant, mountain biker, parent) treated as a potential market.

### Between sessions — Research

The skill runs web searches for each role: what do people in this role struggle with, what workarounds do they use, what new technology could change the picture, how large is the market? Raw research lives in `discovery.md`; clean summaries surface in the visual map.

### Round N — Depth and validation

You return, the skill loads your document, and you go deeper. You run targeted digs on your most promising roles, prep for and debrief customer interviews, simulate skeptical customers, and gradually narrow toward one problem worth pursuing.

### The output

A ranked list of candidate problems scored on pain intensity, frequency, willingness to pay, founder fit, and market accessibility — plus a visual self-map, a founder brief you can share, and a single recommended next action at any point.

---

## Installation

**Recommended:**
```bash
npx skills add zhenya-vlasov/idea-finder
```

**Or manually:**
```bash
# Clone the repo
git clone git@github.com:zhenya-vlasov/idea-finder.git ~/idea-finder

# Symlink the skill
ln -s ~/idea-finder/skills/idea-finder ~/.claude/skills/idea-finder
```

Open Claude Code and type `/idea-finder` to begin.

---

## Available commands

| Command | What it does |
|---|---|
| `/idea-finder` | Start or resume a discovery session. Loads your existing `discovery.md` automatically on return visits. |
| `/dig [role]` | Zoom in on a specific role. Asks 8 sharper questions: exact break moments, cost estimates, workaround details, willingness-to-pay signals. |
| `/validate [problem]` | Turn a candidate problem into a testable hypothesis. Produces a Reddit post you can publish today, a 5-question interview script, and a list of yes/no signals to watch for. |
| `/interview [contact]` | Generate a tailored interview script for a specific person in your network. Paste in your notes afterward and it structures them back into your discovery document. |
| `/sim [problem]` | Claude plays a skeptical potential customer. You have to convince them the problem is real — without pitching a solution. Ends with a structured debrief and score. |
| `/market [role]` | Deep competitive research: TAM, incumbents, funded startups in the space, community forums, and whitespace analysis. |
| `/persona [role]` | Write a vivid day-in-the-life customer persona — the kind you'd put on a wall and ask "would this person pay for this?" |
| `/score` | Score all candidate problems on a 50-point rubric across pain intensity, frequency, WTP, founder fit, and market accessibility. |
| `/compare [A] vs [B]` | Head-to-head comparison of two problems across six dimensions. Ends with a clear recommendation — not a list of trade-offs. |
| `/why-me [problem]` | Honest, scored assessment of your unfair advantage — or lack of one — for a specific problem. |
| `/brief` | One-page founder brief synthesized from your full discovery document. Ready to share with an advisor, co-founder, or early investor. |
| `/next` | Single most valuable next action, based on exactly where you are in the discovery process right now. |
| `/render` | Rebuild the Self-Map web app from your current `discovery.md`. Runs `render.py` and tells you to refresh the browser. |

---

## Session flow

```
/idea-finder
      │
      ▼
  Session 1 — Interview (13 blocks) + Roles List
      │
      ▼
  Research — web search for each role (pain, workarounds, TAM, incumbents)
      │
      ▼
  Discovery document saved → ~/idea-finder/discovery.md
      │
      ├── /dig [role]       ← go deeper on any role
      ├── /market [role]    ← competitive research
      ├── /persona [role]   ← build a customer profile
      ├── /score            ← rank your candidates
      ▼
  Network contacts identified
      │
      ├── /interview [name] ← tailored script + note processing
      ├── /sim [problem]    ← practice the conversation
      ▼
  Best problem surfaces
      │
      ├── /validate         ← build the hypothesis, get it in front of people
      ├── /compare [A] vs [B]
      ├── /why-me           ← honest founder-market fit check
      ├── /brief            ← one-pager to share
      └── /next             ← one action to take in the next 48 hours
```

---

## The discovery document

Everything is stored in `~/idea-finder/discovery.md` — a single structured markdown file that accumulates across sessions:

- Your complete profile and background
- Full Roles List with categories and how each role was identified
- Per-role research: goals, pain points, workarounds, tech narratives, TAM
- Your personal challenge ratings for each pain
- Network contacts and interview scripts
- Candidate problems with scores and evidence
- Validation plans and open questions

Type `/render` at any point to rebuild the visual self-map from the latest document.

---

## Web interface

Type `/render` at any point during discovery and Claude will run the render script, transforming your `discovery.md` into a live local webpage at **http://localhost:3737**.

Each tab has its own bookmarkable URL, such as `http://localhost:3737/Self-Map.html#network`. Browser Back and Forward move between tabs.

For local checks, run `npm ci`, `npm test`, and `npm run test:e2e` (install Playwright Chromium once with `npx playwright install chromium` if needed).

The interface is designed to pull you back in — to make what you've uncovered feel real and navigable, so the next dig feels obvious rather than overwhelming:

- **Self-map** — a table of every role you inhabit, each one a market you already live in. Click any role to open its detailed view: the problems people in that role face, how they're currently solving them, and where the opportunities are. A starting point for the next dig, not a summary of the last one.
- **Opportunities** — every candidate problem surfaced from your roles, paired with the narrative trends moving through that space. Not a to-do list — a lens for spotting where a real problem and a real moment in time are looking at each other.
- **Network** — your close circle, mapped to the roles they touch. Your next interview target is usually visible from here.
- **Open questions** — the things you said but didn't finish. Answer one. Set one aside. Let them sit. All of them are useful eventually.
- **Full discovery doc** — the complete raw record: every question asked, every note taken, every search excerpt pasted in. The map shows the clean takeaways; this is where the evidence lives.

Re-render any time you want the interface to reflect new interviews, research, or role updates. It takes seconds.

---

## What's inside

```
idea-finder/
├── .claude-plugin/
│   └── plugin.json               # Plugin manifest
├── skills/
│   └── idea-finder/
│       └── SKILL.md              # Main skill — all commands including /render
├── scripts/
│   ├── render.py                 # discovery.md → visual self-map
│   └── serve.py                  # local dev server with answer persistence
├── references/
│   ├── industry-workflow.md      # Search queries and research workflows
│   ├── pain-extraction.md        # What counts as real pain signal
│   ├── network-mapping.md        # Interviewability scoring
│   ├── anti-patterns.md          # 10 idea traps to filter out
│   ├── incumbent-risk.md         # Why large companies leave gaps
│   ├── opportunity-ranking.md    # Full 50-point scoring rubric
│   ├── interview-scripts.md      # 30–45 min interview structure
│   ├── competitor-research.md    # Where to find real competitive data
│   ├── validation-playbook.md    # 4-step validation ladder
│   └── distribution-mapping.md  # Where each persona lives online
└── evals/
    └── evals.json                # Test cases for skill evaluation
```

---

## Philosophy

**Stay problem-focused.** The skill never suggests what to build. It surfaces problems and helps you decide.

**Evidence over enthusiasm.** A problem is real when someone describes a specific moment it broke — not when they say they "would use" a solution.

**Your network is the moat.** The founders who win early reach 10 paying customers without a marketing budget. The skill consistently pushes toward that.

**The document is the truth.** The visual interface shows clean takeaways. The markdown file holds every raw quote, every search excerpt, every unanswered question. Don't clean it up — that's your evidence.

---

If this helped you think more clearly about what to build, a ⭐ on [GitHub](https://github.com/zhenya-vlasov/idea-finder) goes a long way.
