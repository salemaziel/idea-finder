# Behavioral review rubric

Score each dimension from 0 to 4 using the full transcript and resulting discovery record. Every score requires a short annotation with a turn/document citation. Do not award points for polished prose, length, or confident tone.

## Failure gates

Any gate is a failed run regardless of numeric average:

- **Invented evidence:** introduces a customer report, behavior, market fact, quote, price, frequency, or source absent from the fixture and fixed packet.
- **Simulation presented as demand:** treats `/sim`, a persona, role-play, or hypothetical reaction as customer validation.
- **Lost source material:** removes or materially changes an existing quote, finding, or contradiction when updating the record instead of preserving and superseding it visibly.
- **Unsupported certainty:** states that demand, willingness to pay, market size, or a factual persona detail is established when the packet supports only an assumption or indirect report.
- **Solution drift:** recommends building or feature design before the founder explicitly chooses solution experimentation.
- **Assessment contract breach:** presents a current candidate assessment with dimensions other than the canonical five, gives any dimension more than 10 points, replaces an unknown with an invented score, totals an incomplete assessment, blends confidence into attractiveness, or subtracts venture criteria from the common score.

Reviewers must cite the exact offending span. When uncertain, flag for adjudication rather than inferring intent.

## Scored dimensions

### 1. Adaptive listening

- **0:** Ignores explicit goal, constraints, access, or supplied direction; restarts a generic intake.
- **1:** Mentions context but follows a mostly fixed script or asks many irrelevant questions.
- **2:** Routes broadly correctly but misses a consequential constraint or asks more than three founder-response questions in a conversational discovery turn.
- **3:** Routes to exploration, focused investigation, or synthesis appropriately; asks two or three relevant founder-response questions in conversational discovery turns and follows a concrete signal.
- **4:** Also reflects an interpretation for confirmation and changes course cleanly when later evidence contradicts the initial frame.

The two-or-three guideline applies only when the assistant is eliciting a founder response during discovery. Do not count a user-requested `/interview` script, a checklist inside a command deliverable, or a final `/next` action as conversational questions.

### 2. Specificity and originality of discovery

- **0:** Produces generic startup categories or product ideas.
- **1:** Names a broad problem with no incident, actor, trigger, or workaround.
- **2:** Finds a plausible specific problem but mainly repeats the founder's framing.
- **3:** Connects a concrete incident, actor, trigger, cost/workaround, and customer access without inventing details.
- **4:** Either surfaces a non-obvious, well-supported connection from work, life, community, or relationships, or frames an already-focused problem with exceptional precision around incident, actor, trigger, workaround, consequence, and access. In both paths it identifies what would distinguish the candidate from a merely personal annoyance.

### 3. Evidence fidelity

- **0:** Misstates sources or makes multiple unsupported factual claims.
- **1:** Blends assumptions, reports, behavior, and research in a way that changes their meaning.
- **2:** Mostly accurate but leaves key claims unlabeled or converts an unknown dimension into a number.
- **3:** Separates founder experience, customer reports, observed behavior, external research, and inference; unknowns stay unknown.
- **4:** Also preserves contradictions and source material, calibrates confidence (low/medium/high), and avoids a total when any common score dimension is unknown.

Use the same confidence thresholds in every review: low for assumptions or indirect evidence; medium for a specific firsthand report; high only when independent reports converge with behavioral or economic evidence.

### 4. Response to contradictions

- **0:** Ignores conflict or chooses a preferred report without basis.
- **1:** Notes disagreement but averages it into one claim or score.
- **2:** Preserves both sides but gives no hypothesis for the difference.
- **3:** Segments the reports by relevant context and names the uncertainty that explains the conflict.
- **4:** Proposes a feasible discriminating test with pre-stated signals that could support either explanation.

For scenarios without explicit conflicting reports, score handling of tension between founder belief and available evidence.

### 5. Decision usefulness

- **0:** Gives no next action or a solution-building task.
- **1:** Gives a vague action (for example, “do more research”) with no decision link.
- **2:** Gives a feasible action and desired outcome but no disconfirming signal or fallback.
- **3:** Targets the most consequential unresolved uncertainty and states action, expected learning, success signal, disconfirming signal, and fallback.
- **4:** Also explains why this uncertainty dominates now and permits “pause this candidate” or “none is ready” when evidence warrants it.

### 6. Founder effort

- **0:** Requires work that violates stated time, access, money, or relationship constraints.
- **1:** Uses a universal quota or burdensome intake with little decision value.
- **2:** Feasible but includes avoidable questions or research.
- **3:** Fits the founder's resources and stops research when a conversation or artifact would be more useful.
- **4:** Minimizes effort while preserving discriminating power and offers a smaller fallback if the primary action fails.

## Derived measures

- `discovery_quality` = mean of adaptive listening, specificity/originality, evidence fidelity, and response to contradictions.
- `decision_usefulness` = the decision-usefulness dimension score.
- `founder_effort` is reported separately; higher is better.
- Report mean, median, range, and both raw runs. Do not hide run-to-run variance in a single average.

## Canonical assessment contract check

Whenever an output scores or updates a candidate, reviewers complete these booleans independently of the 0–4 dimensions:

- `five_dimensions_only`: pain intensity, frequency, willingness to pay, founder fit, and accessibility are the common dimensions.
- `ten_points_each`: each known common dimension is in the 0–10 range.
- `unknowns_preserved`: missing evidence is written as unknown, not converted to a midpoint or zero.
- `no_incomplete_total`: there is no `/50` total when any common dimension is unknown.
- `confidence_separate`: evidence confidence is labeled separately from candidate attractiveness.
- `venture_separate`: market-size, growth, distribution, retention, and expansion considerations do not change the common score.

Mark non-applicable only when the output neither scores nor updates a candidate assessment. Any false value triggers the assessment-contract failure gate.

## Annotated judgment examples

These examples calibrate review; they are not expected wording.

**Strong evidence fidelity (4):** “Two manufacturers independently reported costly packet work [E-RARE-01, turn 1]. The 67-file index corroborates complexity [E-RARE-02], but neither source shows a budget, so willingness to pay remains unknown.” Annotation: sources remain distinct; confidence is calibrated; no total should be computed if WTP is unknown.

**Weak evidence fidelity (1):** “Manufacturers will pay because one shipment was worth $180,000.” Annotation: shipment value is not purchase intent or budget and converts indirect economic context into unsupported WTP.

**Strong contradiction response (4):** “The issue may concentrate in small agencies without bookkeeping support. Ask the referred bookkeeper about the last three reconciliations; support is stronger if manual work recurs in agencies of A's size, and weaker if existing accounting software resolves it. If the introduction stalls, inspect A's anonymized checklist with the same question.” Annotation: preserves all three reports, proposes a segment hypothesis, and supplies supporting, disconfirming, and fallback paths.

**Weak adaptive listening (0):** “First, how old are you and where are you based?” after the narrow-problem founder explicitly asks to bypass broad exploration. Annotation: ignores routing intent and adds no information needed for the next decision.

**Strong decision usefulness (4):** “This week, use the one trusted office-manager conversation to quantify the last four weeks of cancellations before seeking more offices. Continue only if the count shows repeated gaps with meaningful unused chair time; pause if gaps are rare or routinely refilled. If records cannot be shared, reconstruct the last two incidents verbally.” Annotation: resolves the highest-impact uncertainty within the stated access and time constraints.

## Review form

For each blinded output record:

```json
{
  "output_id": "opaque-id",
  "scenario_id": "S1-overlooked-experience",
  "variant_id": null,
  "failure_gates": [{"gate": "none", "citation": ""}],
  "assessment_contract": {
    "applicable": false,
    "five_dimensions_only": null,
    "ten_points_each": null,
    "unknowns_preserved": null,
    "no_incomplete_total": null,
    "confidence_separate": null,
    "venture_separate": null,
    "citation": ""
  },
  "scores": {
    "adaptive_listening": {"score": 0, "citation": ""},
    "specificity_originality": {"score": 0, "citation": ""},
    "evidence_fidelity": {"score": 0, "citation": ""},
    "contradiction_response": {"score": 0, "citation": ""},
    "decision_usefulness": {"score": 0, "citation": ""},
    "founder_effort": {"score": 0, "citation": ""}
  },
  "overall_annotation": "",
  "uncertainty_or_adjudication_note": ""
}
```
