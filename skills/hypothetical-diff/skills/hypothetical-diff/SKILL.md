---
name: hypothetical-diff
description: >-
  Generalizes Hypothetical Document Embeddings (HyDE, Gao et al. 2023) from
  static documents to universal Before/After diffs across any non-coding or
  coding domain—writing, tone/voice rewrites, difficult conversations and
  negotiations, learning and mental models, habits and travel, creative
  storytelling, policy/history counterfactuals, strategy, calendars, contracts,
  spreadsheets, research, and code. Synthesizes concrete hypothetical deltas
  (--- Before / +++ After), simulates any scenario or dialogue in any user-set
  tone, enforces resource/energy conservation, and supports interactive
  mix-and-match hunk selection. Use when user says "hypothetical diff",
  "hydiff", "HyDE diff", "show me the diff if", "what would actually change if",
  "counterfactual diff", "simulate a diff", "diff this in the tone of",
  "script and subtext diff", "mental model diff", "ripple diff", "diff my
  options", "search using a hypothetical diff", "redline this hypothetically",
  "stress-test this decision with a diff", "reverse-diff this problem", or wants
  a concrete Before/After preview before committing to a change.
---

# Hypothetical Diff (`hypothetical-diff`)

Bridges the gap between abstract intent and concrete reality by synthesizing a
plausible **Before $\rightarrow$ After delta ($\hat{\Delta}$)** *first*, then
grounding that delta against real documents, data, human reactions, constraints,
or interactive hunk-by-hunk user feedback.

Inspired by **HyDE** (*Hypothetical Document Embeddings*, Gao et al., ACL 2023,
*"Precise Zero-Shot Dense Retrieval without Relevance Labels"*), which showed
that projecting an abstract query into a concrete (even partially hallucinated)
target document places it in the exact structural and lexical neighborhood of
the real answer. **Hypothetical Diff** lifts this principle from static
documents ($\hat{d}$) to **state transitions ($\hat{\Delta} = \text{After} - \text{Before}$)**
for **anything that can change or be simulated**—whether a difficult
conversation, a mental model, a habit routine, a story beat, a historical
counterfactual, a legal clause, a weekly calendar, a budget model, or a
codebase—and in **any tone or persona set by the user**.

---

## Core Mechanism: Project $\rightarrow$ Ground $\rightarrow$ Converge

Never reason, advise, search, or ask for approval purely in abstract prose when
the goal is a change, comparison, or simulation. Run this three-step loop:

1. **Project ($\hat{\Delta}$ — Zero-Shot Delta Synthesis)**
   - Translate the user's goal, question, scenario, or hypothesis into a
     concrete `--- Before` / `+++ After` diff written in the **native medium of
     the domain** (spoken lines + subtext for a conversation, beliefs +
     predictions for learning, cues + friction for habits, clauses for a
     contract, time blocks for a calendar, rows for a sheet, unified diff for
     code) and rendered in the **user's requested tone or persona**.
   - Where exact real-world details are not yet known, fill in plausible,
     high-specificity exemplars and mark them `[HYPOTHETICAL]`. Specificity is a
     feature, not a bug: concrete numbers, dialogue, and structures expose false
     assumptions immediately.

2. **Ground (The Reality & Conservation Bottleneck)**
   - Intersect $\hat{\Delta}$ with reality to wash out wishful thinking and
     ungrounded assumptions:
     - **In `search` mode**: Extract **Before-anchors** (`-` lines: terms,
       structures, or patterns that currently exist) and **After-anchors** (`+`
       lines: vocabulary of prior precedents) to query the workspace, Drive,
       Docs, Gmail, or repository.
     - **In `decide` / `align` / `simulate` modes**: Enforce the **Conservation
       Law of Diffs** (every `+` addition in a finite system must name the `-`
       removal that pays for it—across time, energy, attention, word count, or
       budget) and trace **2nd-order ripple/adaptation effects**.
     - **In `diagnose` mode**: Test whether the discriminating observable
       predicted by the hypothetical causal diff actually appears in reality.

3. **Converge ($\Delta_{\text{real}}$ — Interactive Hunk Selection)**
   - Present numbered hunks (`[Hunk 1]`, `[Hunk 2]`, ...) so the user can
     cherry-pick, mix-and-match across options (`A1 + B2`), or adjust the tone
     in a single turn before applying the final change.

---

## Six Operational Modes

Select the mode that matches the user's immediate bottleneck (or chain them,
such as `search` $\rightarrow$ `align` or `ensemble` $\rightarrow$ `simulate`):

| Mode | Trigger / Situation | What $\hat{\Delta}$ Represents | How Grounding Works |
|------|---------------------|--------------------------------|---------------------|
| **`search`** *(HyDE Retrieval)* | "Where do we handle X?", "Find past memos/notes/commits/clauses that changed Y" | A plausible diff of the target passage, policy, note, sheet, or file (`-` current pattern, `+` target pattern) | Queries the corpus using `-` tokens (to find what needs changing) and `+` tokens (to find historical precedents) |
| **`align`** *(Prototype Slice)* | Subjective or open request ("Make this punchier", "Rewrite in a warmer tone", "Tighten our SLA") | A 1–3 hunk Before/After diff on a representative slice before touching the whole artifact | User reacts to concrete numbered hunks via interactive selection or shorthand ballot in one turn |
| **`decide`** *(Counterfactual)* | Choosing between life/career paths, habits, strategies, itineraries, or priorities | `--- Baseline (Status Quo / Option A)` vs. `+++ Counterfactual (Option B)` across concrete world-state artifacts | Enforces resource conservation ($\sum \Delta = 0$ on time, human energy, budget, attention, or scope) to reveal hidden trade-offs |
| **`diagnose`** *(Reverse-Diff)* | Something broke, stalled, or felt off (habit failed, talks broke down, metric dropped, bug appeared) | $K=2\text{–}3$ competing upstream **Causal Diffs** ($\hat{\Delta}_{\text{cause}}$) that could yield the observed symptom delta | Identifies the single **discriminating check** that confirms one causal diff and falsifies the others |
| **`ensemble`** *($K$-Diffs)* | Exploring multiple creative, strategic, or tonal directions | $K=3$ orthogonal diffs (e.g., *Minimal/Safe*, *Structural/Direct*, *Bold/Inversion*—or 3 distinct tones) | Separates **Consensus Hunks** (agreed across all $K$) from **Divergent Hunks** so the user can mix-and-match (`A1 + B2`) |
| **`simulate`** *(Scenario, Dialogue & Ripple)* | "Simulate how this conversation/policy/change plays out", "Show me this in a `<X>` tone" | A turn-by-turn **Dialogue + Subtext Diff**, **1st/2nd/3rd-Order Ripple Diff**, or **Adversarial Pre-Mortem Diff** in any user-set tone | Tests how counterparties, audiences, or systems adapt to, push back on, or game the first-order change |

---

## Universal Tone, Voice & Persona Control

The user can set **any tone, voice, register, persona, or emotional temperature**
for any domain or simulation (e.g., *warm therapist, brutal VC partner, deadpan
roast, Socratic tutor, Hemingway sparse, diplomatic negotiator, Regency drama,
noir detective, appellate judge, sports commentator, Gen-Z group chat, or a
custom voice sample*). Apply tone in three ways:

1. **Tone *as* the Diff (Voice & Style Re-Skinning)**:
   - Hold the underlying facts and commitments invariant ($\Delta \text{Facts} = 0$)
     while diffing the voice, rhythm, and subtext:
     `--- Baseline: Current / Neutral Draft` $\rightarrow$
     `+++ Target Tone: <User-Specified Tone>`.
2. **Tone *of* the Simulation**:
   - When simulating a scenario, career choice, historical counterfactual, habit
     overhaul, or negotiation in `simulate` or `decide` mode, adopt the user's
     requested tone across the hunk headers, simulated dialogue, counterparty
     reactions, and trade-off commentary—**without ever sacrificing the
     structural rigor of the `--- Before` / `+++ After` diff or Conservation
     Laws**.
3. **Multi-Tone Dial (`ensemble` mode)**:
   - If the user wants to explore tone options (e.g., *"How intense should I
     make this message?"*), project $K=3$ calibrated intensity steps (e.g.,
     *Diff A: Collaborative / Soft*, *Diff B: Crisp / Firm Boundary*, *Diff C:
     Blunt / Zero-Cushion*) so the user can combine specific lines across tones
     (e.g., `B1 + A2`).

---

## Universal Diff Notation (Non-Coding & Coding Domains)

Always render $\hat{\Delta}$ in the representation most native to the subject
matter. Use fenced ```` ```diff ```` blocks for line/beat-oriented deltas and
structured **Delta Tables** for multi-dimensional models:

### 1. Difficult Conversations, Negotiation & Relationships (`simulate` / `align`)
Never give generic communication advice ("be firm but empathetic"). Diff the
**exact words spoken/sent**, the **unspoken subtext**, and the **counterparty's
likely reaction**, while enforcing boundary/scope conservation:

```diff
--- Baseline: Instinctive Reply (Over-Apologetic / Defensive)
+++ Simulated: Warm "Yes, If" Boundary (Tone: Calm, Senior Partner)
@@ Hunk 1: The Spoken / Written Reply @@
- Hey, I'm really sorry, we're super swamped right now so there's no way we can add the custom workshop before Friday.
+ I'd love to make the custom workshop happen. Because our week is fully committed to the Friday launch, we can either (a) run the workshop next Wednesday, or (b) do it Thursday if we push the launch review to Monday. Which works best for you?
@@ Hunk 2: Subtext & How It Lands @@
- Heard as: "No / You're an inconvenience" -> Triggers pushback or escalation.
+ Heard as: "Shared ownership of a finite constraint" -> Invites the other person to choose which trade-off they prefer.
```

### 2. Learning, Mental Models & Concept Deconstruction (`align` / `diagnose`)
When teaching or researching any subject (science, economics, history,
philosophy, medicine, law), diff the **learner's intuitive misconception**
against the **expert mental model**, followed by the **Prediction Flip**:

```diff
--- Baseline: Intuitive Misconception (How Smart Beginners Think It Works)
+++ Updated Mental Model: How the Mechanism Actually Works
@@ Hunk 1: Core Mechanism (Example: Highway Traffic & Induced Demand) @@
- Adding a 5th highway lane increases road capacity against a fixed pool of drivers, permanently reducing commute times.
+ Travel time acts like a price; lowering congestion releases latent demand (rerouted trips, shifted departure times, new sprawl) until congestion returns to the traveler's time-pain threshold.
@@ Hunk 2: Real-World Prediction Flip @@
- Old Prediction: Widening the freeway by 25% cuts rush-hour delay by ~25% at Year 3.
+ New Prediction: Rush-hour speed reverts to baseline within 2–4 years (though total vehicle-miles traveled increases); only congestion pricing or transit alternatives shift equilibrium speed.
```

### 3. Writing, Storytelling, Speeches & Tone Re-Skinning (`align` / `ensemble`)
Diff prose at the sentence, scene-beat, or rhetorical level while enforcing
**Reader Attention Conservation** (every added detail must earn its keep or cut
throat-clearing prose):
- **Show-Don't-Tell Diffs**: `- Abstract emotional label` $\rightarrow$ `+ Concrete sensory action / dialogue subtext`.
- **Narrative / Deck Arc Diffs**: Diff the 5-beat sequence of an essay, story,
  or presentation *before* writing 3,000 words (e.g., moving the inciting tension
  from Paragraph 4 to Sentence 1).

### 4. Schedules, Habits, Personal Life & Travel (`decide` / `simulate`)
Enforce **strict Time, Money, and Human Energy Conservation** ($\Delta \text{Hours} = 0$,
$\Delta \text{Energy} \le \text{Cap}$). A habit or travel diff that adds `+6h`
of deep work, workouts, or sightseeing without deleting `-6h` of existing usage
*and* designing for low-energy days is invalid:

```diff
--- Baseline: Wishful Evening Routine (Fails by Wednesday)
+++ Grounded: Friction-Engineered Routine (Net Time Delta: 0h)
@@ Hunk 1: Environment & Cue Friction (21:30–22:30) @@
- [21:30–22:30] "Try to read more and stop scrolling in bed" (Phone on nightstand = 0s friction)
+ [21:30–22:30] Phone plugs into kitchen charger at 21:30 (30s walk friction); Kindle + physical book open on pillow (-1.0h doomscroll / +1.0h reading & wind-down)
@@ Hunk 2: Low-Energy Tuesday Fallback (Anti-All-or-Nothing) @@
- If exhausted after late dinner: Skip routine entirely -> revert to 90m scrolling.
+ Minimum Viable Habit (MVH): Read 2 pages or listen to 10m audio in dark room; streak stays intact.
```

### 5. Policy, Economics, History & World Simulation (`simulate` / `decide`)
When analyzing policies, market shifts, or historical *"What if..."*
counterfactuals, project a **Multi-Order Ripple Diff** ($\hat{\Delta}^{(1)} \rightarrow \hat{\Delta}^{(2)} \rightarrow \hat{\Delta}^{(3)}$)
and an **Adversarial / Goodhart Counter-Diff** (how actors adapt to or game the
new rule):
- `@@ Hunk 1 (1st-Order): Direct Rule / Event Change @@`
- `@@ Hunk 2 (2nd-Order Adaptation / Loophole): How Actors Game or Route Around It @@`
- `@@ Hunk 3 (3rd-Order Equilibrium): Surprising Long-Term Shift @@`

### 6. Legal Contracts, Strategy, Spreadsheets & Quantitative Models
- **Contracts & Policies**: Semantic clause hunks (`@@ §8.2 Liability Cap @@`)
  with `[HYPOTHETICAL]` tags for unverified clauses.
- **Strategy & Career Decisions**: Diff concrete world-state artifacts 6–12
  months out (`@@ Commitments @@`, `@@ Scoreboard/Incentives @@`,
  `@@ Weekly Calendar @@`, `@@ Failure Modes @@`) rather than abstract pros/cons.
- **Spreadsheets & Budgets**: Pair a **Delta Table** (`Dimension | --- Before | +++ After | Net Delta | Load-Bearing Assumption`)
  with structural driver diffs.

### 7. Software, Config & System Architecture
Use standard unified diffs (`--- a/path/to/file`, `+++ b/path/to/file`) with
exact symbol names, types, and config keys to maximize search anchor precision.

---

## Step-by-Step Execution Workflow

1. **Classify the Domain, Mode & User Tone**
   - Identify the artifact, conversation, belief, or system being changed; select
     `search`, `align`, `decide`, `diagnose`, `ensemble`, or `simulate`; and
     lock in the **user's requested tone/persona** (or default to crisp, high-signal
     clarity if unspecified).
2. **Enforce the Conservation Constraint**
   - Ask: *What is finite here?* (24 hours/day, physical/emotional energy,
     reader attention, word count, budget, goodwill, headcount, risk tolerance).
     Ensure every `+` in $\hat{\Delta}$ names the `-` that funds it.
3. **Synthesize the Hypothetical Diff ($\hat{\Delta}$) with Numbered Hunks**
   - Break $\hat{\Delta}$ into **2–4 numbered semantic hunks** (`@@ Hunk 1: ... @@`,
     `@@ Hunk 2: ... @@`) so each hunk represents one clear, independent choice.
   - Tag unverified facts with `[HYPOTHETICAL]` so a projection is never
     mistaken for a fetched fact.
4. **Extract Anchors & Ground (When Connected to Files / Tools / Apps)**
   - **In Antigravity**: Use `-` and `+` anchors from $\hat{\Delta}$ to search or
     view relevant files, then update $\hat{\Delta}$ into a grounded diff.
   - **In Gemini Spark / Workspace**: Use anchors from $\hat{\Delta}$ to locate
     relevant Google Docs, Sheets, Slides, Calendar events, Gmail threads, or
     Drive files before proposing edits.
5. **Interactive Hunk Staging ("Mix-and-Match Menu")**
   - Surface the 2–4 **Important Assumptions** and let the user cherry-pick
     or combine hunks effortlessly:
     - **In Google Antigravity**: When multiple hunks or $K$-diff options require
       a user choice, invoke `ask_question` (`is_multi_select: true`) listing
       each numbered hunk (or `A1`, `B1`, etc.) so the user can select their
       exact combination with one click.
     - **In Gemini Spark / Text Chat**: End with a **1-Line Mix-and-Match
       Ballot** (e.g., *"Reply with the hunks you want—such as `Keep 1 & 3`,
       `A1 + B2`, or `Re-run Hunk 2 in a <X> tone`"*).

---

## Output Format

Structure responses using this template (adapt section headers naturally to the
size and tone of the request):

```markdown
### 1. Intent, Mode & Tone
- **Mode**: `<search | align | decide | diagnose | ensemble | simulate>`
- **Target Medium & Tone**: `<e.g., Difficult Conversation (Tone: Warm & Unshakeable) | Mental Model Diff | Weekly Routine>`
- **Conservation Constraint**: `<e.g., Net time = 0h/wk | Reader attention = 200 words max | Delivery date fixed>`

### 2. Hypothetical Diff ($\hat{\Delta}$)
> Status: `[HYPOTHETICAL — UNGROUNDED]` (or `[GROUNDED AGAINST <source>]`)

```diff
--- Baseline: <current state, instinctive draft, or status quo>
+++ Hypothetical: <target state, simulated scenario, or counterfactual>
@@ Hunk 1: <name of first mechanism, beat, or choice> @@
- <concrete before state>
+ <concrete after state>

@@ Hunk 2: <name of second mechanism, reaction, or ripple> @@
- <concrete before state>
+ <concrete after state>
```

### 3. Load-Bearing Assumptions & Ripple Effects
1. **[Hunk 1]**: Assumes `<X>`. If false, `<consequence or fallback>`.
2. **[Conservation / 2nd-Order Check]**: Adding `+<A>` requires removing `-<B>` (and watch for `<2nd-order adaptation>`).

### 4. Mix & Match (Next Step)
- **Pick your hunks**: `<e.g., Reply "1 & 2", "A1 + B2", or "Shift tone to <X>">`
```

---

## Approval & Safety Guardrails

- **Never fabricate citations or claim a `[HYPOTHETICAL]` diff is already live**:
  Always distinguish between the *projected/simulated* diff ($\hat{\Delta}$) and
  the *grounded* diff ($\Delta_{\text{real}}$) verified against real data.
- **Approval Gate (Low $\rightarrow$ High)**:
  - **Generating or simulating a Hypothetical Diff** in any tone is always a
    **safe, read-only preview** (Low risk).
  - **Applying the converged diff** to real files, sending emails/messages,
    modifying shared calendars, updating sheets, or editing documents requires
    **explicit user approval of the selected hunks**.

---

## Optional Deep-Dive References

When running in an environment with bundled skill files (Google Antigravity or a
ZIP skill upload in Gemini Spark), load these on demand only when needed:
- [references/domain-playbooks.md](references/domain-playbooks.md): 12 worked
  Before/After diff playbooks across everyday non-coding and coding domains
  (Writing & Storytelling, Difficult Conversations & Negotiation, Learning &
  Mental Models, Habits & Travel, Policy/History Ripple Diffs, Universal Tone &
  Persona Showcases, Legal, Strategy, Calendar, Finance, Science, and Code).
- [references/hyde-theory-and-patterns.md](references/hyde-theory-and-patterns.md):
  Deep dive on Gao et al. (2023) HyDE mechanics, asymmetric `-`/`+` anchor
  extraction, $K$-diff variance, multi-order ripple diffs ($\hat{\Delta}^{(2)}$),
  orthogonal tone projection, and interactive hunk algebra.
