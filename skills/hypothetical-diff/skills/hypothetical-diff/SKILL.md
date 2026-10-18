---
name: hypothetical-diff
description: >-
  Generalizes Hypothetical Document Embeddings (HyDE, Gao et al. 2023) from
  static documents to universal Before/After diffs across any non-coding or
  coding domain—writing, tone/voice rewrites, difficult conversations and
  negotiations, learning and mental models, habits and travel, creative
  storytelling, policy/history counterfactuals, strategy, calendars, contracts,
  spreadsheets, research, and code. Simulates anything at any granularity
  (from sub-second L0 micro-choices and turn-by-turn dialogue rallies up to L4
  multi-year/historical cascades and Monte Carlo branching envelopes) in any
  user-set tone, enforces resource/energy conservation, and supports interactive
  zoom, curveball perturbation, and mix-and-match hunk selection. Use when user
  says "hypothetical diff", "hydiff", "HyDE diff", "show me the diff if", "what
  would actually change if", "counterfactual diff", "simulate a diff", "zoom in
  on this diff", "zoom out", "telescoping diff", "simulate turn by turn",
  "timeline diff", "Monte Carlo diff", "diff this in the tone of", "script and
  subtext diff", "mental model diff", "ripple diff", "diff my options", "search
  using a hypothetical diff", "redline this hypothetically", "stress-test this
  decision with a diff", "reverse-diff this problem", or wants a concrete
  Before/After preview before committing to a change.
---

# Hypothetical Diff (`hypothetical-diff`)

Bridges the gap between abstract intent and concrete reality by synthesizing a
plausible **Before $\rightarrow$ After delta ($\hat{\Delta}$)** *first*, then
grounding that delta against real documents, data, human reactions, constraints,
or interactive hunk-by-hunk user steering.

Inspired by **HyDE** (*Hypothetical Document Embeddings*, Gao et al., ACL 2023,
*"Precise Zero-Shot Dense Retrieval without Relevance Labels"*), which showed
that projecting an abstract query into a concrete (even partially hallucinated)
target document places it in the exact structural and lexical neighborhood of
the real answer. **Hypothetical Diff** lifts this principle from static
documents ($\hat{d}$) to **state transitions ($\hat{\Delta} = \text{After} - \text{Before}$)**
for **anything that can change or be simulated**—at **any granularity (`L0`
micro-choice $\leftrightarrow$ `L4` macro era)** and in **any tone or persona
set by the user**.

---

## Core Mechanism: Project $\rightarrow$ Ground $\rightarrow$ Converge

Never reason, advise, search, or ask for approval purely in abstract prose when
the goal is a change, comparison, or simulation. Run this three-step loop:

1. **Project ($\hat{\Delta}$ — Zero-Shot Delta Synthesis at Target Granularity)**
   - Translate the user's goal, question, scenario, or hypothesis into a
     concrete `--- Before` / `+++ After` diff written in the **native medium of
     the domain**, calibrated to the **target zoom level (`L0`–`L4`)**, and
     rendered in the **user's requested tone or persona**.
   - Where exact real-world details are not yet known, fill in plausible,
     high-specificity exemplars and mark them `[HYPOTHETICAL]`. Specificity is a
     feature, not a bug: concrete numbers, dialogue, and structures expose false
     assumptions immediately.

2. **Ground (The Reality, Conservation & Scale-Consistency Bottleneck)**
   - Intersect $\hat{\Delta}$ with reality to wash out wishful thinking and
     ungrounded assumptions:
     - **In `search` mode**: Extract **Before-anchors** (`-` lines: terms,
       structures, or patterns that currently exist) and **After-anchors** (`+`
       lines: vocabulary of prior precedents) to query the workspace, Drive,
       Docs, Gmail, or repository.
     - **In `decide` / `align` / `simulate` modes**: Enforce the **Conservation
       Law of Diffs** ($\sum \Delta = 0$ across time, energy, attention, word
       count, or budget), verify **Cross-Scale Consistency** (micro `L0` habits
       must actually sum to the macro `L3` goal), and trace **2nd/3rd-order
       ripple or branching effects**.
     - **In `diagnose` mode**: Test whether the discriminating observable
       predicted by the hypothetical causal diff actually appears in reality.

3. **Converge ($\Delta_{\text{real}}$ — Interactive Hunk & Zoom Steering)**
   - Present numbered hunks (`[Hunk 1]`, `[Hunk 2]`, ...) alongside the
     **Interactive Simulation Controller** so the user can cherry-pick hunks
     (`A1 + B2`), zoom in/out (`L0` $\leftrightarrow$ `L4`), step forward
     (`+1 Turn` / `+6mo`), inject a curveball, or shift tone in a single turn.

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
| **`simulate`** *(Multi-Granularity Simulation)* | "Simulate how this plays out", "Zoom in to the exact dialogue", "Show `+1d` vs `+1yr`", "Run in `<X>` tone" | A **Telescoping Zoom Diff (`L0`–`L4`)**, **Turn-by-Turn Rally**, **Multi-Horizon Timeline**, or **Monte Carlo Branching Diff** | Tests cross-scale consistency, counterparty reactions, temporal inversions, and tail-risk hedges across any user-set tone |

---

## Multi-Granularity Simulation Engine ($\mathcal{G} = \langle \text{Scale}, \text{Time}, \text{Fidelity}, \text{Lens} \rangle$)

Anything can be simulated at **any resolution**. When the user asks to simulate
a scenario—or wants to zoom in or out on an existing diff—control these four
axes explicitly:

### 1. The 5-Level Structural Zoom Ladder (`L0` $\leftrightarrow$ `L4`)

| Level | Scale | Resolution | Examples Across Non-Coding & Coding Domains |
|-------|-------|------------|---------------------------------------------|
| **`L0`** | **Micro / Atomic** | Sub-second to 1 min; single phrase, cue, or cell | Exact phrasing & vocal pause in a tough talk; physical location of a phone charger at 9:30 PM; one sensory verb in a story; a single formula or 3-line guard clause. |
| **`L1`** | **Tactical / Hunk** | 5–60 min; 1 interaction, clause, or block | Opening exchange + immediate pushback; a 2-hour morning deep-work block; a liability clause redline; a single function refactor. |
| **`L2`** | **Artifact / Routine** | 1 day to 1 month; complete script or workflow | A full 4-turn negotiation rally; a 1-day Kyoto travel itinerary; a 40h weekly calendar; an executive memo; a service module. |
| **`L3`** | **System / Equilibrium** | 1 quarter to 2 years; multi-actor ecosystem | Household or team operating rhythm; a 6-month strategy pivot; 2nd-order Goodhart gaming of a policy; multi-service architecture. |
| **`L4`** | **Macro / Era** | 5 to 100+ years; life arc, market, or history | 10-year career/wealth/health compounding; industry disruption; historical or geopolitical counterfactuals (*"What if..."*). |

### 2. Four Multi-Granularity Simulation Archetypes

1. **Telescoping Zoom Diff (`L3 Macro` $\rightarrow$ `L2 Meso` $\rightarrow$ `L0 Micro`)**:
   - Links a high-level ambition directly down to the Tuesday morning micro-action
     in a single diff (`@@ Hunk 1 [L3 System]: 6-Month Goal @@` $\rightarrow$
     `@@ Hunk 2 [L2 Weekly]: Calendar Trade-off @@` $\rightarrow$
     `@@ Hunk 3 [L0 Atomic]: 07:15 AM Cue & Friction @@`). Immediately exposes
     **"Macro Ambition / Micro Starvation"** (when an `L3` goal has zero `L0`
     behavioral support).
2. **Turn-by-Turn Rally Simulation (`Turn 1` $\rightarrow$ `Turn 2` $\rightarrow$ `Turn 3`)**:
   - Simulates live multi-turn exchanges (salary/contract negotiations, sales
     objections, interviews, debates, courtroom cross-examinations, conflict
     resolution, or fiction dialogue). At each turn, diffs the **Default
     Derailment Path (`-`)** against the **Calibrated Steering Path (`+`)**,
     including **Spoken Words**, **Internal Subtext**, and **Emotional
     Temperature ($\Delta \text{Temp}$)**.
3. **Multi-Horizon Temporal Compounding Diff (`t = +10m | +1wk | +6mo | +5yr`)**:
   - Projects how the *same* choice evolves across time horizons to expose
     **Temporal Inversions**:
     - *Trap Diff*: `+10m` feels great (`+` relief from avoiding a hard truth)
       $\rightarrow$ `+6mo` compounds negatively (`-` eroded trust / chronic
       bottleneck).
     - *Compounding Diff*: `+10m` costs friction (`-` 15 minutes of awkward
       clarity) $\rightarrow$ `+6mo` unlocks high-leverage autonomy (`+`).
4. **Monte Carlo Branching Envelope Diff (`Base Case | Upside | Murphy's Law Tail-Risk`)**:
   - Instead of pretending the future is a single deterministic line, projects
     3 probability-weighted branches (`@@ Hunk 1: Base Case (60%) @@`,
     `@@ Hunk 2: Upside Breakout (20%) @@`, `@@ Hunk 3: Tail-Risk / Murphy's Law (20%) @@`)
     followed by **`@@ Hunk 4: Pre-Emptive Hedge @@`** (the minimal change you
     make *today* to cap the downside while keeping the upside).

### 3. Multi-Perspective Lens Switching
Any simulation can be diffed simultaneously across conflicting actors:
- `@@ Lens 1: You (Proposer / Actor) @@`
- `@@ Lens 2: Counterparty (Skeptical Manager / Buyer / Partner) @@`
- `@@ Lens 3: Downstream / Silent Bystander (Team / Customer / Kids) @@`
- `@@ Lens 4: Future You (+1 Year) @@`

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
     overhaul, or negotiation at any granularity (`L0`–`L4`), adopt the user's
     requested tone across the hunk headers, simulated dialogue, counterparty
     reactions, and trade-off commentary—**without ever sacrificing the
     structural rigor of the `--- Before` / `+++ After` diff or Conservation
     Laws**.
3. **Multi-Tone Dial (`ensemble` mode)**:
   - Project $K=3$ calibrated intensity steps (e.g., *Diff A: Collaborative /
     Soft*, *Diff B: Crisp / Firm Boundary*, *Diff C: Blunt / Zero-Cushion*) so
     the user can combine specific lines across tones (`B1 + A2`).

---

## Universal Diff Notation (Non-Coding & Coding Domains)

Always render $\hat{\Delta}$ in the representation most native to the subject
matter. Use fenced ```` ```diff ```` blocks for line/beat-oriented deltas and
structured **Delta Tables** for multi-dimensional models:

### 1. Difficult Conversations, Negotiation & Turn-by-Turn Rallies (`simulate` / `align`)
Diff the **exact words spoken/sent**, the **unspoken subtext**, and the
**counterparty's likely reaction** across 1 or more turns:

```diff
--- Baseline: Instinctive Reply (Over-Apologetic / Defensive)
+++ Simulated: Warm "Yes, If" Boundary (Tone: Calm, Senior Partner | Zoom: L1)
@@ Hunk 1 (Turn 1): Your Opening Reply @@
- Hey, I'm really sorry, we're super swamped right now so there's no way we can add the custom workshop before Friday.
+ I'd love to make the custom workshop happen. Because our week is fully committed to the Friday launch, we can either (a) run the workshop next Wednesday, or (b) do it Thursday if we move the launch review to Monday. Which works best for you?
@@ Hunk 2 (Turn 2): Subtext & Counterparty Response @@
- Heard as: "Refusal / bottleneck" -> Counterparty escalates: "Why does every small ask take two weeks?" (Temp: +2 Escalation)
+ Heard as: "Shared ownership of a constraint" -> Counterparty pivots to choosing: "Let's keep Friday's launch and do the workshop Wednesday." (Temp: -2 De-escalation)
```

### 2. Learning, Mental Models & Concept Deconstruction (`align` / `diagnose`)
Diff the **learner's intuitive misconception** against the **expert mental
model**, followed by the **Prediction Flip**:

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
Diff prose at the word (`L0`), paragraph/scene (`L1`), or 5-beat structural arc
(`L2`) level while enforcing **Reader Attention Conservation**:
- **Show-Don't-Tell Diffs (`L0`/`L1`)**: `- Abstract emotional label` $\rightarrow$ `+ Concrete sensory action / dialogue subtext`.
- **Story / Deck Arc Diffs (`L2`)**: Diff the 5-beat sequence of an essay, story,
  or presentation *before* writing 3,000 words.

### 4. Schedules, Habits, Personal Life & Travel (`decide` / `simulate`)
Enforce **strict Time, Money, and Human Energy Conservation** ($\Delta \text{Hours} = 0$,
$\Delta \text{Energy} \le \text{Cap}$) and link `L2` routines to `L0` cues:

```diff
--- Baseline: Wishful Evening Routine (Fails by Wednesday)
+++ Grounded: Friction-Engineered Routine (Net Time Delta: 0h | Zoom: L2 -> L0)
@@ Hunk 1 [L0 Cue Friction]: 21:30 Environment Reset @@
- [21:30–22:30] "Try to read more and stop scrolling in bed" (Phone on nightstand = 0s friction)
+ [21:30–22:30] Phone plugs into kitchen charger at 21:30 (30s walk friction); Kindle + book open on pillow (-1.0h doomscroll / +1.0h reading & wind-down)
@@ Hunk 2 [L1 Perturbation Hedge]: Low-Energy Tuesday Fallback @@
- If exhausted after late dinner: Skip routine entirely -> revert to 90m scrolling.
+ Minimum Viable Habit (MVH): Read 2 pages or listen to 10m audio in dark room; streak stays intact.
```

### 5. Policy, Economics, History & World Simulation (`simulate` / `decide`)
Combine **1st/2nd/3rd-Order Ripple Diffs**, **Multi-Horizon Timelines**, and
**Monte Carlo Branching Envelopes**:
- `@@ Hunk 1 (1st-Order / +30d): Direct Rule or Event Change @@`
- `@@ Hunk 2 (2nd-Order / +6mo Goodhart Loophole): How Actors Game or Route Around It @@`
- `@@ Hunk 3 (3rd-Order / +3yr Equilibrium): Long-Term Structural Shift @@`

### 6. Legal Contracts, Strategy, Spreadsheets & Software Architecture
- **Contracts & Policies**: Semantic clause hunks (`@@ §8.2 Liability Cap @@`)
  with `[HYPOTHETICAL]` tags for unverified clauses.
- **Strategy & Career Decisions**: Telescoping world-state diffs from `L3`
  (6-month commitments/incentives) down to `L1` (weekly calendar trade-offs).
- **Spreadsheets & Quantitative Models**: Pair a **Delta Table** with structural
  formula diffs.
- **Software & Config**: Unified diffs (`--- a/path`, `+++ b/path`) at `L0`
  (line patch), `L2` (module interface), or `L3` (system dataflow).

---

## Step-by-Step Execution Workflow

1. **Classify Domain, Mode, Granularity ($\mathcal{G}$) & Tone ($\tau$)**
   - Identify the target domain; select `search`, `align`, `decide`, `diagnose`,
     `ensemble`, or `simulate`; pick the right starting **Zoom Level (`L0`–`L4`)**
     and **Time Horizon**; and lock in the **user's requested tone/persona**.
2. **Enforce Conservation & Scale Consistency**
   - Ask: *What is finite here?* (24 hours/day, physical/emotional energy,
     reader attention, word count, budget, goodwill, headcount, latency). Ensure
     every `+` names the `-` that funds it, and verify that micro `L0` actions
     match macro `L3` goals.
3. **Synthesize the Hypothetical Diff ($\hat{\Delta}$) with Numbered Hunks**
   - Break $\hat{\Delta}$ into **2–4 numbered semantic hunks** (`@@ Hunk 1: ... @@`,
     `@@ Hunk 2: ... @@`) so each hunk can be independently selected, zoomed, or
     perturbed. Tag unverified facts with `[HYPOTHETICAL]`.
4. **Extract Anchors & Ground (When Connected to Files / Tools / Apps)**
   - **In Antigravity**: Use `-` and `+` anchors from $\hat{\Delta}$ to search or
     view relevant files, then update $\hat{\Delta}$ into a grounded diff.
   - **In Gemini Spark / Workspace**: Use anchors from $\hat{\Delta}$ to locate
     relevant Google Docs, Sheets, Slides, Calendar events, Gmail threads, or
     Drive files before proposing edits.
5. **Present the Interactive Simulation Controller ("Steer & Mix-and-Match")**
   - Surface the 2–4 **Load-Bearing Assumptions** and let the user steer the
     simulation or cherry-pick hunks in one turn:
     - **In Google Antigravity**: Invoke `ask_question` (`is_multi_select: true`)
       offering hunk selections (`Keep Hunk 1`, `A1 + B2`) and simulation
       controls (`Zoom In to L0 dialogue`, `Step +1 Turn / +6mo`, `Inject
       Curveball`, `Shift Tone/Lens`).
     - **In Gemini Spark / Text Chat**: End with a compact **Simulation
       Controller & Mix-and-Match Bar**:
       > **Steer or Apply**: `Mix & Match` (`1 & 3` / `A1 + B2`) · `Zoom In` (`L0` exact words/cues on Hunk X) · `Zoom Out` (`L3/L4` 1yr ripple) · `Step +1` (next turn/horizon) · `Curveball` (*"what if X fails?"*) · `Tone/Lens` (*"re-run as <persona>"*)

---

## Output Format

Structure responses using this template (adapt section headers naturally to the
size and tone of the request):

```markdown
### 1. Intent, Mode, Granularity & Tone
- **Mode & Archetype**: `<e.g., simulate (Turn-by-Turn Rally) | decide (Telescoping L3 -> L0) | align>`
- **Granularity & Tone**: `<Zoom: L1 Tactical | Horizon: Turn 1–2 | Tone: Warm & Unshakeable>`
- **Conservation Constraint**: `<e.g., Net time = 0h/wk | Reader attention = 200 words | Delivery date fixed>`

### 2. Hypothetical Diff ($\hat{\Delta}$)
> Status: `[HYPOTHETICAL — UNGROUNDED]` (or `[GROUNDED AGAINST <source>]`)

```diff
--- Baseline: <current state, instinctive draft, or default derailment>
+++ Hypothetical: <target state, calibrated simulation, or counterfactual>
@@ Hunk 1 [<Scale/Horizon>]: <name of first mechanism, beat, or turn> @@
- <concrete before state>
+ <concrete after state>

@@ Hunk 2 [<Scale/Horizon>]: <name of second mechanism, reaction, or ripple> @@
- <concrete before state>
+ <concrete after state>
```

### 3. Load-Bearing Assumptions & Scale / Ripple Check
1. **[Hunk 1]**: Assumes `<X>`. If false, `<consequence or fallback>`.
2. **[Conservation / Scale Check]**: Adding `+<A>` requires removing `-<B>`.

### 4. Simulation Controller & Mix-and-Match
- **Steer next**: `Apply/Mix` (`1 & 2` / `A1 + B2`) | `Zoom In (L0)` | `Zoom Out (L3/L4)` | `Step +1 Turn/Yr` | `Curveball (<shock>)` | `Shift Tone/Lens (<persona>)`
```

---

## Approval & Safety Guardrails

- **Never fabricate citations or claim a `[HYPOTHETICAL]` diff is already live**:
  Always distinguish between the *projected/simulated* diff ($\hat{\Delta}$) and
  the *grounded* diff ($\Delta_{\text{real}}$) verified against real data.
- **Approval Gate (Low $\rightarrow$ High)**:
  - **Generating, zooming, or simulating a Hypothetical Diff** at any granularity
    or tone is always a **safe, read-only preview** (Low risk).
  - **Applying the converged diff** to real files, sending emails/messages,
    modifying shared calendars, updating sheets, or editing documents requires
    **explicit user approval of the selected hunks**.

---

## Optional Deep-Dive References

When running in an environment with bundled skill files (Google Antigravity or a
ZIP skill upload in Gemini Spark), load these on demand only when needed:
- [references/simulation-engine.md](references/simulation-engine.md): Complete
  multi-granularity simulation reference—worked examples of the `L0`–`L4` Zoom
  Ladder on a single scenario, Turn-by-Turn Rally state machines, Multi-Horizon
  Temporal Inversion tables, Monte Carlo branching envelopes, Multi-Perspective
  Lens diffs, and Curveball Perturbations.
- [references/domain-playbooks.md](references/domain-playbooks.md): 12 worked
  Before/After diff playbooks across everyday non-coding and coding domains
  (Writing & Storytelling, Difficult Conversations & Negotiation, Learning &
  Mental Models, Habits & Travel, Policy/History Ripple Diffs, Universal Tone &
  Persona Showcases, Legal, Strategy, Calendar, Finance, Science, and Code).
- [references/hyde-theory-and-patterns.md](references/hyde-theory-and-patterns.md):
  Deep dive on Gao et al. (2023) HyDE mechanics, asymmetric `-`/`+` anchor
  extraction, $K$-diff variance, multi-order ripple diffs ($\hat{\Delta}^{(2)}$),
  cross-scale consistency conservation, orthogonal tone projection, and
  interactive hunk algebra.
