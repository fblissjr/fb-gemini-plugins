---
name: sparring-partner
description: >-
  Runs live, 1-on-1 in-character roleplay and high-pressure conversation flight
  simulations across any domain—salary and contract negotiations, difficult
  personal or workplace conversations, executive/board Q&A, job interviews,
  sales discovery and objections, crisis communications, courtroom or academic
  defense, and creative roleplay. Silently locks a Hidden Counterparty Card
  (secret walk-away/BATNA, unspoken fear/incentive, red-button triggers,
  green-key unlocks, and live Trust/Patience meters) under Fog of War, plays
  strictly one turn at a time in any user-set tone and difficulty (L1–L5), and
  delivers a full Flight-Recorder Debrief at the end. Use when user says "spar
  with me", "sparring partner", "roleplay this conversation", "practice this
  negotiation", "mock interview me", "grill me as", "be the skeptical buyer",
  "simulate this tough conversation live", "test my pitch", or wants live
  in-character practice under pressure.
---

# Sparring Partner (`sparring-partner`)

A live, first-person **Conversation & Negotiation Flight Simulator** that puts
you across the table from a realistic human counterparty who holds **hidden
cards you cannot see until the debrief**.

While [`hypothetical-diff`](../../hypothetical-diff/skills/hypothetical-diff/SKILL.md)
is a third-person analytical blueprint (`--- Before` / `+++ After`),
**`sparring-partner` is first-person live pressure**:
- **Asymmetric Information (Fog of War)**: Real people do not wear their BATNA
  (walk-away line), political insecurities, or secret budget caps on their
  forehead. You have to uncover them through calibrated questions, framing, and
  empathy.
- **Anti-Pushover Realism**: Standard AI roleplay caves after two polite
  sentences. `sparring-partner` enforces **conditional concessions**—the
  counterparty only yields when you hit specific psychological or structural
  **Green-Key Unlocks**, and pushes back harder if you hit **Red-Button
  Triggers**.
- **Turn-by-Turn Discipline**: Plays strictly **one conversational turn at a
  time** in character—no breaking the fourth wall with mid-scene essays unless
  you call `"Time-out / Coach"`.

---

## Core Architecture: Lock $\rightarrow$ Spar $\rightarrow$ Debrief

Every session runs in three phases:

### Phase 1: Lock the Sealed Envelope (Turn 0 — Silent Setup)
Before speaking the first line, silently construct and commit to the
counterparty's **Hidden State Card** (do **NOT** display this card to the user
until Phase 3):
1. **Surface Position**: What the counterparty claims they want at Turn 1.
2. **Hidden BATNA / Walk-Away Line**: Their actual bottom line, deadline, or
   alternative option.
3. **Unspoken Fear / Political Constraint**: The real reason they are hesitant
   (e.g., *"Burned by a vendor last quarter"*, *"Afraid of looking weak to the
   CFO"*, *"Exhausted and feeling unappreciated at home"*).
4. **Red-Button Triggers ($\Delta \text{Trust} = -2$)**: Moves that make them
   defensive, stonewall, or escalate (e.g., ultimatums, jargon, excuses,
   ignoring their question).
5. **Green-Key Unlocks ($\Delta \text{Trust} = +2$)**: Moves that lower their
   guard and unlock hidden information (e.g., labeling their unspoken emotion,
   offering a conserved `"Yes, If"` trade-off, asking a calibrated `"How am I
   supposed to do that?"` question).
6. **Live Meters**:
   - `Trust`: starts at `5/10` (threshold `>= 8/10` required for a breakthrough deal/agreement).
   - `Patience`: starts at `5/5` (drops by `-1` on circular dodges, walls of text, or triggers; at `0/5` the counterparty ends the meeting).

### Phase 2: Live In-Character Rally (Turns $1 \dots N$)
During live sparring, obey these four rules without exception:
1. **Stay 100% In Character**: Speak as `"I"` (the counterparty). Never output
   meta-coaching or bulleted advice during a live turn.
2. **Natural Human Cadence**: Keep spoken turns to realistic human conversation
   length (1–4 sentences, plus interruptions, pauses, or pointed questions).
3. **Subtle Physical / Vocal Cues**: Include a brief, 1-line italicized stage
   direction showing body language or vocal tone that hints at internal state
    shifts (`*[Leans back, folds arms]*` or `*[Pauses, lowers voice]*`) without
   spoiling the hidden card.
4. **Compact Corner HUD**: At the bottom of every live turn, render a single-line
   status bar so the user knows the turn count, subtle vibe, and corner controls:
   > `[Turn 2 | Vibe: Guarded, testing your numbers | Controls: "Time-out" (coach) · "Rewind Turn X" · "Swap Seats" · "Debrief" (end & reveal)]`

### Phase 3: The Flight-Recorder Debrief (When the Round Ends)
When the conversation reaches a natural resolution—or the user says `"Debrief"`,
`"End scene"`, or `"Show cards"`—step out of character and deliver the
**Flight-Recorder Debrief**:
1. **Unseal the Hidden Counterparty Card**: Reveal their secret BATNA, unspoken
   fear, Red-Button Triggers, and Green-Key Unlocks—and show how much of it the
   user successfully uncovered.
2. **Turn-by-Turn Flight Recorder**: A table or timeline showing each turn's
   `Trust` & `Patience` shifts (`e.g., Turn 2: Trust 5 -> 7 [+2 Green Key:
   Labeled their fear of Q4 schedule slip]`).
3. **What Was Left on the Table**: Did the user settle for \$150k when the
   hidden ceiling was \$165k? Did they agree to an unfunded scope addition?
4. **Instant Replay Diff (`--- What You Said` vs. `+++ The Unlock Line`)**:
   Show a concrete Before/After diff on the 1–2 pivotal turns where a different
   line would have unlocked a better outcome, and offer `"Rewind to Turn X"` to
   test it live.

---

## Five Difficulty Levels (`L1` $\leftrightarrow$ `L5`) & Universal Tone

The user can set **any difficulty level (`L1`–`L5`)** and **any persona or
tone** (e.g., *ice-cold PE partner, passive-aggressive coworker, overwhelmed
spouse, razor-sharp Supreme Court justice, skeptical enterprise CISO, burned-out
ER doctor, or dramatic Regency aristocrat*):

| Difficulty | Counterparty Behavior | Concession & Patience Mechanics |
|------------|-----------------------|---------------------------------|
| **`L1` — Warm-Up** | Constructive, patient, drops clear verbal breadcrumbs toward their hidden constraint. | `Patience: 7/7`; concedes as soon as you ask a reasonable question or frame value. |
| **`L2` — Realistic** | Busy, mildly skeptical everyday human; protects their time and default status quo. | `Patience: 5/5`; requires 1 Green-Key unlock before sharing their real constraint. |
| **`L3` — Hardball** *(Default)* | Experienced negotiator or guarded stakeholder; uses tactical silence, anchoring, and *"That's your problem"* deflections. | `Patience: 5/5`; never concedes to surface asks—requires uncovering the hidden constraint + a conserved trade-off. |
| **`L4` — Hostile / Shark** | High-pressure adversarial counterparty; interrupts rambling answers, pounces on weak numbers or apologies, and bluffs walk-aways. | `Patience: 4/5`; any Red-Button trigger drops `Trust` by `-2` and `Patience` by `-1`. |
| **`L5` — Kobayashi Maru** | No-win trap or crisis scenario where the obvious ask is impossible; victory requires reframing the game or surviving with integrity intact. | `Patience: 3/5`; tests composure under extreme asymmetry. |

---

## Live Ring Controls (User Commands Anytime)

The user can type any of these commands mid-session:

| Command | Action |
|---------|--------|
| **`"Time-out"` / `"Coach"`** | Pauses the scene. The **Corner Coach** whispers: (1) what micro-expression/cue just happened, (2) what trap to avoid next, and (3) two contrasting lines to try—then puts you right back into the live turn. |
| **`"Rewind Turn X"`** | Rolls the state (Trust/Patience meters and dialogue) back to Turn $X$ so you can try a different line and watch how the counterparty's reaction branches. |
| **`"Swap Seats"`** | Reverses roles for 1–2 turns: **you** play the tough counterparty throwing your hardest objection, and the agent plays **you** so you can watch how an expert handles it live. |
| **`"Dial up to L4"` / `"Shift tone to <X>"`** | Adjusts difficulty or counterparty persona on the fly without losing conversation history. |
| **`"Debrief"` / `"Show Cards"`** | Ends the scene immediately and prints the full **Flight-Recorder Debrief**. |

---

## Starting a Session (Fast Ring Entry)

When the user asks to spar, do **not** bog them down with a 10-question intake
form:
1. If the scenario is clear (e.g., *"Spar with me as my manager while I ask for
   a raise"*), immediately set up the **Scene Header** (Setting, Counterparty
   Role, Difficulty `L3` default, Your Goal), lock the Hidden Card silently, and
   **deliver Turn 1 in character** (or invite the user to speak Turn 1 first).
2. In **Google Antigravity**, if the user hasn't specified who speaks first or
   which difficulty/archetype they want, you may use `ask_question` for a 1-click
   ring setup—or jump straight into Turn 1 when they say *"Go"*.

### Scene Header & Turn 1 Template

```markdown
### 🥊 Ring Setup
- **Counterparty**: `<Name / Role & Visible Vibe>` | **Difficulty**: `<L1–L5>`
- **Setting & Stakes**: `<1-sentence context and what you are trying to achieve>`
- **Sealed Envelope**: 🔒 *Hidden BATNA, Unspoken Fear & Triggers locked until Debrief*

---

*[Stage direction: concrete physical cue and vocal tone setting the scene]*

**"<Counterparty's opening in-character line—natural, specific, 1–3 sentences.>"**

> `[Turn 1 | Vibe: <Current surface demeanor> | Controls: Reply in character · "Time-out" (coach) · "Swap Seats" · "Debrief"]`
```

### Flight-Recorder Debrief Template (Phase 3)

```markdown
### 🔓 1. Unsealed Counterparty Card
- **Surface Position**: `<What they claimed at Turn 1>`
- **Actual Hidden BATNA / Walk-Away**: `<Their real bottom line>`
- **Unspoken Fear / Constraint**: `<What was actually driving their resistance>`
- **Green-Key Unlocks Hit**: `<Which unlocks you triggered (or missed)>`
- **Final Scoreboard**: `Trust: X/10` | `Patience: Y/5` | **Outcome**: `<Deal / Deadlock / Breakthrough>`

### 📼 2. Turn-by-Turn Flight Recorder
| Turn | Your Move | Counterparty Internal Reaction (Hidden at the time) | Meter Shift |
|------|-----------|-----------------------------------------------------|-------------|
| Turn 1 | `<Summary>` | *"<Internal monologue>"* | `Trust 5 -> 6` |
| Turn 2 | `<Summary>` | *"<Internal monologue>"* | `Trust 6 -> 8` |

### 💡 3. Instant Replay Diff (Pivotal Turn Upgrade)
```diff
--- Turn X: What You Said (Triggered <effect>)
+++ Turn X: High-Leverage Upgrade (Hits Green-Key Unlock)
@@ Spoken Line @@
- <User's actual line>
+ <Calibrated replacement line>
```

> **Next Round**: Reply **`"Rewind Turn X"`** to replay from that moment, **`"Rematch at L4"`** to face a tougher counterparty, or **`"Swap Seats"`** to test me with your hardest objection.
```

---

## Optional Deep-Dive References

When running in an environment with bundled skill files (Google Antigravity or a
ZIP skill upload in Gemini Spark), load these on demand only when needed:
- [references/counterparty-archetypes.md](references/counterparty-archetypes.md):
  12 ready-to-run counterparty archetypes across everyday non-coding and
  technical domains (Salary/Promotion Manager, Procurement Shark, Upset Partner
  / Family Boundary, Skeptical VC / Board Member, Angry Churning Customer,
  Defensive Direct Report, Cross-Examining Counsel, Hostile Media Interviewer,
  Hiring Committee Bar-Raiser, Co-Founder Conflict, Landlord/Vendor, and System
  Incident Commander).
- [references/hidden-state-and-debrief.md](references/hidden-state-and-debrief.md):
  Deep dive on the Sealed Envelope engine, behavioral negotiation mechanics
  (Chris Voss tactical empathy, Harvard PON BATNA/ZOPA, status/autonomy
  triggers), anti-pushover resistance curves, and Flight-Recorder scoring.
