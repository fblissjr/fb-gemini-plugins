# Hidden-State Engine & Flight-Recorder Debrief Mechanics (`hidden-state-and-debrief.md`)

This reference explains how `sparring-partner` maintains realistic human
resistance under **Fog of War** and turns every roleplay session into a
high-precision diagnostic via the **Flight-Recorder Debrief**.

---

## 1. Why Standard AI Roleplay Fails (And How the Sealed Envelope Fixes It)

Standard LLM roleplay suffers from two fatal flaws:
1. **Sycophantic Cave-In**: Because instruction-following models are trained to
   be helpful and agreeable, an unguided roleplay counterparty will accept weak
   arguments by Turn 2 (*"That's a fair point, I'll approve the raise!"*), giving
   the user false confidence that backfires in the real room.
2. **Omniscient Leakage**: If the prompt prints the counterparty's secret
   walk-away price or hidden objection at the top of the conversation, the user
   never practices the hardest skill in human interaction: **discovering hidden
   constraints through calibrated questions and active listening**.

### The Sealed Envelope Protocol
At Turn 0, the model binds five latent variables internally without printing
them:

$$\mathcal{S}_{\text{hidden}} = \langle \text{BATNA}, \text{Fear}, \mathcal{T}_{\text{red}}, \mathcal{U}_{\text{green}}, (\text{Trust}_t, \text{Patience}_t) \rangle$$

- **Conditional Concession Rule**: The counterparty **cannot** grant their core
  concession while $\text{Trust}_t < 8$ or before at least one Green-Key Unlock
  $u \in \mathcal{U}_{\text{green}}$ has been triggered by the user.
- **Information Drip Rule**: At `Trust 5–6`, the counterparty only states their
  *surface position* (and drops a subtle nonverbal or phrasing cue). At
  `Trust 7+` (after a calibrated question or empathy label), they reveal their
  *actual hidden constraint* so the user can solve for it.

---

## 2. Behavioral Negotiation & Conversation Primitives

`sparring-partner` evaluates user turns against proven behavioral frameworks:

| Framework / Move | Example User Line | Effect on Counterparty State ($\mathcal{S}_{\text{hidden}}$) |
|------------------|-------------------|--------------------------------------------------------------|
| **Tactical Empathy / Labeling** *(Voss)* | *"It sounds like you're worried that making an exception here creates a precedent you'll have to defend across the whole org."* | **`Trust +2`** (Hits Green-Key Unlock; counterparty says *"That's exactly it"* and reveals the real constraint). |
| **Calibrated "How / What" Question** | *"How can we structure this so your Q3 cashflow cap stays untouched while locking in the adjustment for Q4?"* | **`Trust +1 to +2`** (Invites the counterparty to solve your problem using their own constraints). |
| **Conditional "Yes, If" Trade-Off** | *"We can hit the May 1 date if we move the custom PDF export to Phase 2—or keep both for May 15."* | **`Trust +1`**, preserves boundary without triggering defensive escalation. |
| **Unanchored Concession / Apology** | *"Sorry to bother you, I can drop the price by 15% if that helps."* | **`Trust -1`**, encourages L3/L4 counterparties to pocket the concession and demand more. |
| **Premature Ultimatum / Blame** | *"If you can't match this, I'll have to look elsewhere."* | **`Trust -2`, `Patience -1`** (Hits Red-Button Trigger; counterparty shifts to defensive stonewalling). |
| **Rambling / Dodging a Direct Question** | 3-paragraph monologue that never answers their question. | **`Patience -1`**, counterparty interrupts: *"Give me the 10-second version."* |

---

## 3. Nonverbal & Vocal Micro-Cue Calibration

Because real conversations are 50%+ nonverbal, every in-character turn includes
a concise stage direction that encodes the current internal state **without**
breaking the fourth wall:

- **When `Trust` drops (`-1` or `-2`)**:
  - `*[Stops taking notes and closes the folder halfway.]*`
  - `*[Voice flattens into polite corporate neutral.]*`
- **When `Patience` drops (`<= 2/5`)**:
  - `*[Glances at calendar notification in the corner of the screen.]*`
  - `*[Cuts in before you finish the second sentence.]*`
- **When a Green-Key Unlock lands (`Trust +2`)**:
  - `*[Pauses, uncrosses arms, and leans forward slightly.]*`
  - `*[Exhales and speaks off-the-record in a quieter tone.]*`

---

## 4. Debrief Replay Loop

1. **In the Ring**: Pressure-test your delivery live one turn at a time
   against a counterparty with hidden cards.
2. **In the Debrief**: Review the **Flight-Recorder Debrief** and the
   **Pivotal Turn Replay** (what you said vs. the Green-Key unlock line).
3. **Rewind**: Use `"Rewind Turn X"` to practice the upgraded line until it
   feels effortless.
