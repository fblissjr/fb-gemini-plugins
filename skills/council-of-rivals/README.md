# council-of-rivals

last updated: 2026-10-18

An **Adversarial Multi-Persona Collision Arena & Double-Crux Extractor** (`v0.1.0`) for **Google Antigravity** (`agy` CLI v1.4.0+ and Antigravity App v2.24.0+) and **Gemini Spark** (including Gemini web/desktop `Customize > Skills` and Gemini Enterprise).

---

## Why `council-of-rivals`? (The 3rd Pillar of the Simulation Suite)

When you ask a standard AI for "multiple perspectives," you get three polite paragraphs from the same underlying voice that agree to "balance all factors."

**`council-of-rivals` bans lukewarm consensus**. It casts **3–5 sharply opposing minds with incompatible objective functions**, forces them to **cross-examine your idea and each other**, and distills the clash into a **Double-Crux Map ($\mathcal{C}$)**—the exact factual threshold or value trade-off where the rivals split, plus the single decisive test that resolves the debate.

### How the 3 Simulation & Reasoning Plugins Fit Together

| Plugin | POV & Topology | Best Used When... |
|--------|----------------|-------------------|
| **[`hypothetical-diff`](../hypothetical-diff/)** | **3rd-Person State-Transition Blueprint** (`--- Before` / `+++ After`) | You want to preview, zoom (`L0`–`L4`), and edit a concrete change before committing. |
| **[`sparring-partner`](../sparring-partner/)** | **1st-Person 1-on-1 Flight Simulator** (*You vs. Counterparty with Sealed Envelope*) | You need to practice delivering a negotiation, interview, or tough talk live under Fog of War. |
| **`council-of-rivals`** | **Multi-Agent Collision Arena** (*3–5 Rivals colliding with each other $\rightarrow$ Crux Map*) | You face a high-stakes decision or thesis and want conflicting experts/incentives to tear it apart and find the **Crux**. |

---

## How It Works: Cast $\rightarrow$ Indict $\rightarrow$ Collide $\rightarrow$ Extract Crux

1. **Cast the Council (3–5 Seats with Incompatible Incentives & User-Set Tone)**:
   - Assigns each seat a distinct optimization function ($+$) and zero-tolerance boundary ($-$)—from custom archetypes (*Asymmetric Builder vs. Tail-Risk Hawk vs. Tired-Tuesday Practitioner*) to legendary thinkers (*Munger vs. Taleb vs. Feynman*) in any user-specified tone (*Ruthless Boardroom, Supreme Court Oral Argument, Socratic Symposium, Deadpan Roast*).
   - In **Google Antigravity**, can optionally fan out parallel isolated subagents (`invoke_subagent`) so each rival researches and builds its case independently with zero context contamination.
2. **Round 1 — Opening Indictments**:
   - Each rival steelmans what your proposal gets right in 1 sentence, then attacks its fatal flaw from their orthogonal lens.
3. **Round 2 — Direct Cross-Examination Clash (Rival vs. Rival)**:
   - Rivals turn on **each other** (`Seat 2 -> Seat 1`), quoting and attacking the weakest load-bearing premise in each other's arguments.
4. **Round 3 — The Double-Crux Map ($\mathcal{C}$) & Decisive Test**:
   - **Uncontested Bedrock**: What survived every rival's attack intact.
   - **The Double Crux ($\mathcal{C}$)**: Explicit flip conditions (*"If $X > \text{threshold}$, Rival 2 concedes to Rival 1; if $X < \text{threshold}$, Rival 1 concedes to Rival 2"*), distinguishing **Empirical Cruxes** (resolvable by data) from **Value Cruxes** (pure priority choices).
   - **The 24-Hour Decisive Test**: The fastest experiment, query, or calculation to settle $\mathcal{C}$.

---

## Installation & Setup

### 1. Google Antigravity (`agy` CLI v1.4.0+ & Antigravity App v2.24.0+)

```bash
# Install directly from GitHub
agy plugin install https://github.com/fblissjr/fb-gemini-plugins/tree/main/skills/council-of-rivals

# Or install from a local checkout of fb-gemini-plugins
agy plugin install ./skills/council-of-rivals

# Validate plugin manifest and skill structure
agy plugin validate ./skills/council-of-rivals --strict
```

### 2. Gemini Spark & Gemini App (`Customize > Skills`)

- **Option A — Single-File Upload or Paste**:
  Upload or paste `skills/council-of-rivals/skills/council-of-rivals/SKILL.md` in **Customize $\rightarrow$ Skills**.
- **Option B — Full Skill Package ZIP Upload (Includes `references/`)**:
  ```bash
  (cd skills/council-of-rivals/skills/council-of-rivals && zip -r ../../../../council-of-rivals-skill.zip SKILL.md references/)
  ```
  Upload `council-of-rivals-skill.zip` via **Skills $\rightarrow$ + $\rightarrow$ Upload skill**.

---

## Directory Structure

```text
skills/council-of-rivals/
├── plugin.json                                     # Native Antigravity plugin manifest (v0.1.0)
├── assets/
│   └── logo.svg                                    # 128x128 square SVG icon for App/Marketplace cards
├── README.md                                       # Plugin & dual-platform documentation (this file)
└── skills/
    └── council-of-rivals/
        ├── SKILL.md                                # Self-contained skill (Antigravity + Gemini Spark)
        └── references/
            ├── rival-panels-and-archetypes.md      # 12 pre-built Rival Panels across non-coding & coding domains
            └── crux-extraction-and-protocols.md    # Double-Crux theory, Empirical vs. Value Cruxes & subagent fan-out
```
