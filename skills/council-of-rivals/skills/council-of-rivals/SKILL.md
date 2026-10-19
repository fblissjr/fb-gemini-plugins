---
name: council-of-rivals
description: >-
  Convenes an adversarial multi-persona collision arena (3–5 conflicting minds
  with incompatible incentives, priors, and worldviews) to stress-test any
  decision, strategy, belief, creative work, policy, investment, or technical
  architecture—in any user-set tone. Forbids lukewarm consensus, forces direct
  cross-examination between rivals, and extracts the Double-Crux Map (the exact
  empirical premise or threshold where the rivals split, plus the single
  decisive test that resolves the debate). Use when user says "council of
  rivals", "convene a council", "adversarial tribunal", "red-team panel",
  "pit these perspectives against each other", "what is the crux", "double crux
  this", "debate this from conflicting angles", or wants rigorous multi-agent
  collision before making a high-stakes call.
---

# Council of Rivals (`council-of-rivals`)

An **Adversarial Multi-Persona Collision Arena & Double-Crux Extractor** that
replaces polite, sycophantic "pros and cons" lists with **3–5 sharply opposing
minds who have incompatible incentives and are forced to cross-examine your
proposal and each other**.

`council-of-rivals` is a *Multi-Agent Collision Arena & Crux Extractor*: 3–5
conflicting minds collide with **each other** to isolate the exact load-bearing
premise—the **Crux ($\mathcal{C}$)**—that decides the outcome.

---

## Why Standard "Multi-Perspective" Prompts Fail

When you ask a standard LLM for "3 perspectives on X", it generates three mild
paragraphs from the same underlying voice that politely agree to "balance all
factors." **`council-of-rivals` enforces three hard laws**:

1. **The Incompatible-Incentive Law**: Every rival on the council (`3–5` seats)
   must optimize for a **mutually exclusive objective function** (e.g., *Seat 1
   maximizes survival / zero tail-risk*, *Seat 2 maximizes asymmetric upside /
   speed*, *Seat 3 minimizes daily human friction / cognitive load*).
2. **The Direct Cross-Examination Rule**: Rivals are **forbidden** from saying
   *"I agree with Rival A and would add..."*. In Round 2, each rival must quote
   and attack the **weakest load-bearing assumption** in another rival's argument.
3. **The Double-Crux Extraction Law**: The debate never ends with a mushy
   compromise ("it depends"). It ends by isolating the **Crux Map**:
   - **Surprise Bedrock**: What even bitter rivals are forced to agree on.
   - **The Double Crux ($\mathcal{C}$)**: The exact factual threshold or value
     weight where Rival A would flip to Rival B's conclusion (and vice versa).
   - **The Decisive Test**: The fastest concrete check, experiment, or question
     that resolves $\mathcal{C}$ in the real world.

---

## Core Workflow: Cast $\rightarrow$ Indict $\rightarrow$ Collide $\rightarrow$ Extract Crux

### Step 1: Cast the Rivals (3–5 Seats with Orthogonal Priors & User-Set Tone)
Pick 3 (or up to 5) rivals tailored to the user's domain—or use the user's
requested cast and tone (e.g., *Supreme Court oral argument, ruthless boardroom,
Socratic symposium, deadpan roast, noir war-room, or specific thinkers like
Munger vs. Taleb vs. Feynman*):

| Seat | Role / Archetype | Optimizes For ($+$) | Refuses to Tolerate ($-$) |
|------|------------------|---------------------|---------------------------|
| **Rival 1** | *The Asymmetric Builder / Bull* | Speed, compounding upside, bold differentiation | Status-quo stagnation, death by committee |
| **Rival 2** | *The Fragility / Tail-Risk Hawk* | Survival, downside cap, skin-in-the-game, ergodicity | Unhedged ruin, hidden leverage, naive optimism |
| **Rival 3** | *The Ground-Truth Practitioner / User* | Day-2 human reality, zero friction, immediate utility | Abstract theory that fails on a tired Tuesday |
| *(Optional)* **Rival 4** | *The Adversarial Outsider / Short-Seller* | Exploiting loopholes, competitive counter-moves | Assuming competitors or counterparties stand still |

*(In **Google Antigravity**, when the user requests a **Deep Council** or
workspace investigation, you can optionally spawn isolated `research` or `self`
subagents via `invoke_subagent`—one per rival—so each rival gathers evidence
from the repo/docs independently before colliding in Step 3.)*

### Step 2: Round 1 — Opening Indictments (Steelman + Attack)
Each rival delivers a sharp, punchy opening statement (3–5 sentences in their
distinct voice/tone):
- **What the user's proposal gets right** (1 sentence—no straw-manning).
- **The Fatal Flaw**: The exact mechanism by which the user's current plan fails
  under that rival's lens.

### Step 3: Round 2 — Direct Cross-Examination (Rival vs. Rival Clash)
Rivals turn on **each other** in 2–3 rapid exchanges:
- `Rival 2 -> Rival 1`: Attacks Rival 1's unhedged assumption.
- `Rival 3 -> Rival 2`: Attacks Rival 2's over-engineered caution for ignoring
  human/operational friction.
- `Rival 1 -> Rival 3`: Challenges whether incrementalism is actually the
  riskiest move of all.

### Step 4: Round 3 — The Crux Map ($\mathcal{C}$) & Decisive Test
Synthesize the collision into a structured **Crux Map**:
1. **Uncontested Bedrock (High-Signal Consensus)**: Points that survived attacks
   from all rivals intact.
2. **The Double-Crux Frontier ($\mathcal{C}_1, \mathcal{C}_2$)**:
   - State each crux as an explicit **"If / Then Flip Condition"**:
     - *If `<observable X>` is `> threshold`, Rival 2 concedes and Rival 1's path wins.*
     - *If `<observable X>` is `< threshold`, Rival 1 concedes and Rival 2's path wins.*
3. **The 24-Hour Decisive Test**: What is the cheapest, fastest way to measure
   `<observable X>` before committing?

---

## Output Format

Structure responses using this template (adapting voice and energy to the
user's requested tone):

```markdown
### ⚖️ 1. The Council Cast & Stakes
- **Topic & Tone**: `<Decision / Thesis | Tone: e.g., Ruthless Boardroom / Socratic / Deadpan>`
- **Seat 1 — `<Name / Archetype>`**: Optimizes for `<X>` | Zero tolerance for `<Y>`
- **Seat 2 — `<Name / Archetype>`**: Optimizes for `<X>` | Zero tolerance for `<Y>`
- **Seat 3 — `<Name / Archetype>`**: Optimizes for `<X>` | Zero tolerance for `<Y>`

---

### 🔥 2. Round 1: Opening Indictments
- **Seat 1 (`<Name>`)**: *"<Punchy indictment from Lens 1>"*
- **Seat 2 (`<Name>`)**: *"<Punchy indictment from Lens 2>"*
- **Seat 3 (`<Name>`)**: *"<Punchy indictment from Lens 3>"*

---

### ⚔️ 3. Round 2: Cross-Examination Clash (Rival vs. Rival)
- **`<Seat 2>` $\rightarrow$ `<Seat 1>`**: *"<Direct attack on Seat 1's load-bearing premise>"*
- **`<Seat 1>` $\rightarrow$ `<Seat 2>`**: *"<Counter-punch exposing Seat 2's hidden cost>"*
- **`<Seat 3>` $\rightarrow$ Both**: *"<Ground-truth reality check on where both theories break>"*

---

### 🎯 4. Round 3: The Crux Map ($\mathcal{C}$) & Decisive Test
- **Uncontested Bedrock (What All Rivals Agree On)**:
  - `<High-confidence truth that survived every attack>`
- **Double Crux 1 ($\mathcal{C}_1$ — `<Name of Variable / Assumption>`)**:
  - **`<Seat 1>` wins if**: `<Measurable condition A>`
  - **`<Seat 2>` wins if**: `<Measurable condition B>`
- **Decisive Test (Run This First)**:
  - `<1-sentence concrete check or experiment that resolves Crux 1>`

> **Arena Controls**: `Cross-Examine <Rival>` · `Inject Evidence ("What if...")` · `Swap Seat / Shift Tone`
```

---

## Interactive Arena Controls (Steer the Tribunal)

After convening the council, let the user steer the next round (via
`ask_question` in Google Antigravity or shorthand in Gemini Spark):
- 🎤 **`Cross-Examine <Seat X>`**: Put one specific rival on the witness stand
  and grill them on their claim.
- 💣 **`Inject Evidence / Curveball`**: Drop a new constraint or data point into
  the room and force the rivals to update their positions.
- 🪑 **`Swap Seat / Change Tone`**: Add a 4th rival (e.g., *"Add a Regulator"* or
  *"Re-run in a Deadpan Roast tone"*).

This skill is self-contained. Its output (the Crux Map and Decisive Test) is
plain text the user can carry into any follow-up request.

---

## Optional Deep-Dive References

When running in an environment with bundled skill files (Google Antigravity or a
ZIP skill upload in Gemini Spark), load these on demand only when needed:
- [references/rival-panels-and-archetypes.md](references/rival-panels-and-archetypes.md):
  12 ready-to-convene Rival Panels across non-coding and coding domains (Career
  & Life Crossroads, Personal Finance & Investing, Writing & Rhetoric Critique,
  Product & Pricing Strategy, Relationship & Boundary Dilemmas, Policy & Ethics,
  Scientific Hypothesis Testing, Health/Habit Design, Legal/Contract Strategy,
  and System Architecture).
- [references/crux-extraction-and-protocols.md](references/crux-extraction-and-protocols.md):
  Deep dive on Double-Crux decision theory, Empirical vs. Value Cruxes,
  anti-sycophancy prompts, and parallel subagent fan-out (`invoke_subagent`) in
  Google Antigravity.
