# sparring-partner

last updated: 2026-10-18

A live 1-on-1 **In-Character Roleplay & High-Pressure Conversation Flight Simulator** (`v0.1.0`) for **Google Antigravity** (`agy` CLI v1.4.0+ and Antigravity App v2.24.0+) and **Gemini Spark** (including Gemini web/desktop `Customize > Skills` and Gemini Enterprise).

---

## Why `sparring-partner`? (Orthogonal to `hypothetical-diff`)

While **[`hypothetical-diff`](../hypothetical-diff/)** gives you a third-person analytical blueprint (`--- Before` / `+++ After`) before a conversation, knowing your script on paper is completely different from **performing under live pressure when the other person interrupts, deflects, or stonewalls—and you cannot see their cards**.

`sparring-partner` solves the two biggest flaws of standard AI roleplay:
1. **No Sycophantic Cave-Ins**: Normal AI roleplay folds after two polite sentences (*"Great point, here's the 20% raise!"*). `sparring-partner` enforces **conditional concessions**—the counterparty only yields when you hit specific psychological or structural **Green-Key Unlocks**, and pushes back harder if you trigger **Red-Button Triggers**.
2. **True Fog of War (The Sealed Envelope)**: At Turn 0, the agent silently commits to a **Hidden Counterparty Card** (secret walk-away/BATNA, unspoken political or personal fear, Red-Button Triggers, Green-Key Unlocks, and live `Trust` & `Patience` meters) that stays **locked and invisible** during the live turns until you call **`"Debrief"`**.

---

## How It Works: Lock $\rightarrow$ Spar $\rightarrow$ Debrief

| Phase | What Happens | Why It Works |
|-------|--------------|--------------|
| **1. Lock (Turn 0)** | Silently seals the counterparty's hidden BATNA, unspoken fear, triggers, unlocks, and `Trust (5/10)` / `Patience (5/5)` meters. | Forces you to discover what the other person actually cares about through calibrated questions and active listening rather than reading a cheat sheet. |
| **2. Spar (Turns $1 \dots N$)** | Plays strictly **1 turn at a time** in first-person character (`"I"`), with subtle nonverbal micro-cues (`*[Closes laptop halfway]*`) and a 1-line Corner HUD. | Builds real conversational reflexes under pressure without fourth-wall-breaking essays. |
| **3. Debrief (Flight Recorder)** | Unseals the Hidden Counterparty Card, prints the turn-by-turn `Trust`/`Patience` flight recorder, reveals what you left on the table, and shows an **Instant Replay Diff**. | Lets you see the exact moment a turn succeeded or derailed—and immediately **`"Rewind Turn X"`** to test the upgraded line live. |

---

## Five Difficulty Levels (`L1` $\leftrightarrow$ `L5`) & Any User-Set Tone

| Level | Difficulty | Counterparty Behavior |
|-------|------------|-----------------------|
| **`L1`** | **Warm-Up** | Constructive, patient (`7/7`), drops clear verbal hints toward their hidden constraint. |
| **`L2`** | **Realistic** | Busy everyday human (`Patience 5/5`); protects their time and status quo until 1 Green-Key unlock lands. |
| **`L3`** | **Hardball** *(Default)* | Guarded negotiator; uses tactical silence, anchoring, and deflections; requires uncovering their hidden constraint + a conserved trade-off. |
| **`L4`** | **Hostile / Shark** | High-pressure adversarial counterparty; interrupts rambling answers, pounces on weak numbers or apologies, and bluffs walk-aways. |
| **`L5`** | **Kobayashi Maru** | No-win trap or crisis scenario where the obvious ask is impossible; victory requires reframing the game or surviving with integrity intact. |

---

## Live Ring Controls

Use these commands at any point during a sparring match:
- **`"Time-out"` / `"Coach"`**: Freezes the scene; the **Corner Coach** whispers what body-language cue just happened and suggests 2 tactical lines, then resumes play.
- **`"Rewind Turn X"`**: Rolls the conversation and meters back to Turn $X$ so you can try a different line.
- **`"Swap Seats"`**: Reverses roles for 1–2 turns—you play the tough counterparty throwing your hardest objection while the AI plays *you* so you can see how an expert handles it.
- **`"Dial up to L4"` / `"Shift tone to <X>"`**: Changes difficulty or persona on the fly.
- **`"Debrief"` / `"Show Cards"`**: Ends the scene and opens the **Flight-Recorder Debrief**.

---

## Installation & Setup

### 1. Google Antigravity (`agy` CLI v1.4.0+ & Antigravity App v2.24.0+)

```bash
# Install directly from GitHub
agy plugin install https://github.com/fblissjr/fb-gemini-plugins/tree/main/skills/sparring-partner

# Or install from a local checkout of fb-gemini-plugins
agy plugin install ./skills/sparring-partner

# Validate plugin manifest and skill structure
agy plugin validate ./skills/sparring-partner --strict
```

### 2. Gemini Spark & Gemini App (`Customize > Skills`)

- **Option A — Single-File Upload or Paste**:
  Upload or paste `skills/sparring-partner/skills/sparring-partner/SKILL.md` in **Customize $\rightarrow$ Skills**.
- **Option B — Full Skill Package ZIP Upload (Includes `references/`)**:
  ```bash
  (cd skills/sparring-partner/skills/sparring-partner && zip -r ../../../../sparring-partner-skill.zip SKILL.md references/)
  ```
  Upload `sparring-partner-skill.zip` via **Skills $\rightarrow$ + $\rightarrow$ Upload skill**.

---

## Directory Structure

```text
skills/sparring-partner/
├── plugin.json                                     # Native Antigravity plugin manifest (v0.1.0)
├── assets/
│   └── logo.svg                                    # 128x128 square SVG icon for App/Marketplace cards
├── README.md                                       # Plugin & dual-platform documentation (this file)
└── skills/
    └── sparring-partner/
        ├── SKILL.md                                # Self-contained skill (Antigravity + Gemini Spark)
        └── references/
            ├── counterparty-archetypes.md          # 12 ready-to-run counterparty blueprints & sealed envelopes
            └── hidden-state-and-debrief.md         # Sealed Envelope mechanics, micro-cues & Flight-Recorder debriefs
```
