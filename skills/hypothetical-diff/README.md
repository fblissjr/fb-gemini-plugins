# hypothetical-diff

last updated: 2026-10-18

A universal **Hypothetical Diff (HyDiff)** skill and plugin (`v0.3.0`) for **Google Antigravity** (`agy` CLI v1.4.0+ and Antigravity App v2.24.0+) and **Gemini Spark** (including Gemini web/desktop `Customize > Skills` and Gemini Enterprise).

---

## Inspiration: From HyDE (2023) to Multi-Granularity State Transitions

In **HyDE** (*Hypothetical Document Embeddings*, Gao et al., ACL 2023, *"Precise Zero-Shot Dense Retrieval without Relevance Labels"*), an LLM bridges the semantic gap between a short, ambiguous query and a rich target document by **generating a hypothetical target document ($\hat{d}$) first**, and then using that concrete artifact to retrieve and ground against real data. Even when $\hat{d}$ contains unverified details, its structure, vocabulary, and shape place it in the right neighborhood of solution space, and grounding washes out the hallucinations.

**`hypothetical-diff` generalizes HyDE from static documents ($\hat{d}$) to universal state transitions ($\hat{\Delta} = \text{After} - \text{Before}$)**—allowing you to **simulate anything at any granularity (`L0` atomic micro-choice $\leftrightarrow$ `L4` macro era)** and **in any tone set by the user**:
- **Difficult Conversations, Negotiation & Relationships** (*Turn-by-Turn Rallies + Spoken Script + Subtext + Counterparty Reaction Diffs*)
- **Learning, Research & Unlearning** (*Intuitive Misconception $\rightarrow$ Expert Mental Model + Prediction Flip Diffs*)
- **Creative Writing, Storytelling, Speeches & Tone Re-Skinning** (*Show-Don't-Tell, Narrative Beats & Multi-Tone Dial Diffs*)
- **Habits, Personal Life, Health & Travel Itineraries** (*Telescoping `L3` $\rightarrow$ `L0` Cue Friction, Low-Energy Fallbacks & Time/Energy Conservation Diffs*)
- **Policy, Economics, History & Society** (*1st-, 2nd- [Goodhart/Loophole], and 3rd-Order Ripple Diffs + Multi-Horizon Timelines*)
- **Legal Contracts, Redlines & Company Policies**
- **Product Strategy, Org Design & Career/Life Decisions** (*Monte Carlo Branching Envelopes + Multi-Perspective Lens Diffs*)
- **Calendars, Weekly Schedules & Workspace Operations**
- **Spreadsheets, Budgets, Pricing & Financial Models**
- **Scientific Hypotheses & Root-Cause Troubleshooting**
- **Software Architecture, Config & Codebases**

Instead of advising, debating, searching, or planning in abstract prose, `hypothetical-diff` synthesizes a concrete `--- Before` / `+++ After` delta in the native medium of the domain first, simulates scenarios across **any zoom level or time horizon**, and lets you **steer the simulation live (`Zoom In`, `Zoom Out`, `Step +1 Turn`, `Curveball`, `Mix & Match Hunks`)**.

---

## Six Operational Modes

| Mode | When to Use | Example Prompt |
|------|-------------|----------------|
| **`search`** *(HyDE Retrieval)* | Locate where a policy, clause, note, metric, or behavior lives—or find past precedents—using `-` (Before) and `+` (After) anchors from $\hat{\Delta}$. | *"Use a hypothetical diff to find where our vendor agreements or handbook cover AI model training on customer data."* |
| **`align`** *(Prototype Slice)* | Resolve subjective writing, editing, or design goals by previewing a 1–3 hunk Before/After slice before rewriting an entire document or deck. | *"Show me a hypothetical diff on the opening scene of my story to make it show-don't-tell in a minimalist tone."* |
| **`decide`** *(Counterfactual)* | Stress-test a career move, habit routine, travel itinerary, strategy, or budget by enforcing the **Conservation Law of Diffs** (every `+` must name the `-` that funds it). | *"Run a counterfactual diff on my Kyoto itinerary so I'm not exhausted by 3pm, conserving walking energy and transit time."* |
| **`diagnose`** *(Reverse-Diff)* | Debug any regression or plateau (a stalled habit, broken negotiation, funnel drop, or bug) by generating competing upstream causal diffs ($\hat{\Delta}_{\text{cause}}$) and their discriminating check. | *"Our mobile checkout conversion dropped from 6.1% to 1.2% this week while desktop stayed flat. Reverse-diff the top 3 upstream causes."* |
| **`ensemble`** *($K$-Diffs)* | Explore multiple creative, strategic, or tonal directions by generating $K=2\text{–}3$ orthogonal diffs, separating **Consensus Hunks** from **Divergent Hunks** for mix-and-match (`A1 + B2`). | *"Give me 3 hypothetical diffs for replying to this scope-creep request across 3 tones: collaborative, crisp executive, and zero-cushion."* |
| **`simulate`** *(Multi-Granularity Simulation)* | Simulate **anything at any granularity** (`L0`–`L4` zoom ladder, turn-by-turn rallies, `+10m` vs `+5yr` temporal inversions, Monte Carlo branching envelopes, or multi-perspective lenses) in **any user-set tone**. | *"Simulate a 3-turn negotiation rally for a $165k raise (spoken script + subtext + manager pushback) in a warm, unshakeable peer tone."* |

---

## Multi-Granularity Simulation Engine (`L0` $\leftrightarrow$ `L4`)

Every simulation can be viewed and steered across four dimensions: **Structural Scale (`L0`–`L4`)**, **Temporal Horizon**, **Fidelity**, and **Perspective Lens**:

| Level | Scale | Resolution | Examples |
|-------|-------|------------|----------|
| **`L0`** | **Micro / Atomic** | Sub-second to 1 min; single phrase, cue, or cell | Exact phrasing & pause in a tough talk; physical location of a phone charger at 9:30 PM; one sensory verb; a single formula or 3-line guard clause. |
| **`L1`** | **Tactical / Hunk** | 5–60 min; 1 interaction, clause, or block | Opening exchange + immediate pushback; a 2-hour morning deep-work block; a liability clause redline; a single function refactor. |
| **`L2`** | **Artifact / Routine** | 1 day to 1 month; complete script or workflow | A full 4-turn negotiation rally; a 1-day travel itinerary; a 40h weekly calendar; an executive memo; a service module. |
| **`L3`** | **System / Equilibrium** | 1 quarter to 2 years; multi-actor ecosystem | Household or team operating rhythm; a 6-month strategy pivot; 2nd-order Goodhart gaming of a policy; multi-service architecture. |
| **`L4`** | **Macro / Era** | 5 to 100+ years; life arc, market, or history | 10-year career/wealth/health compounding; industry disruption; historical or geopolitical counterfactuals (*"What if..."*). |

### Four Multi-Granularity Simulation Archetypes
1. **Telescoping Zoom Diff (`L3 Macro` $\rightarrow$ `L2 Meso` $\rightarrow$ `L0 Micro`)**: Connects a 1-year goal directly down to Tuesday at 07:15 AM (`L0`), catching *"Macro Ambition / Micro Starvation"* mismatches.
2. **Turn-by-Turn Rally State Machine (`Turn 1` $\rightarrow$ `Turn 2` $\rightarrow$ `Turn 3`)**: Compares the **Default Derailment Path (`-`)** against the **Calibrated Steering Path (`+`)** across multiple conversational turns, tracking spoken lines, subtext, and emotional temperature ($\Delta \text{Temp}$).
3. **Multi-Horizon Temporal Compounding Diff (`+10m | +2wk | +6mo | +3yr`)**: Exposes **Temporal Inversions** where avoiding conflict feels great at `+10m` (`+`) but compounds negatively at `+6mo` (`-`), vs. paying 10 minutes of upfront friction (`-`) for 10x long-term autonomy (`+`).
4. **Monte Carlo Branching Envelope (`Base Case 60% | Upside 20% | Murphy's Law Tail-Risk 20% + Pre-Emptive Hedge`)**: Replaces naive single-line forecasts with a probability envelope and the minimum-cost **Pre-Emptive Hedge Hunk** you can execute today.

### Interactive Simulation Controller
After any diff, steer the simulation live (via `ask_question` checkboxes in Antigravity or shorthand in Gemini Spark):
- **`Mix & Match`** (`1 & 3` / `A1 + B2`) · **`Zoom In`** (`L0` exact words/cues on Hunk X) · **`Zoom Out`** (`L3/L4` 1yr ripple) · **`Step +1`** (next turn/horizon) · **`Curveball`** (*"what if X fails?"*) · **`Tone/Lens`** (*"re-run as <persona>"*)

---

## Universal Tone, Voice & Persona Engine

You can ask `hypothetical-diff` to simulate or rewrite **anything in any tone**—for example:
- **Interpersonal & Coaching**: *Warm therapist, calm senior partner, diplomatic hostage negotiator, Socratic tutor*
- **Direct & Analytical**: *Brutally honest VC partner, appellate judge, skeptical physicist, Warren Buffett shareholder letter*
- **Creative & Literary**: *Hemingway sparse, Raymond Carver minimalist, deadpan roast, noir detective, Regency drama, sports commentator*

---

## Installation & Setup

### 1. Google Antigravity (`agy` CLI v1.4.0+ & Antigravity App v2.24.0+)

Plugins installed into `~/.gemini/config/plugins/` are automatically shared between the **Antigravity CLI (`agy`)** and the **Antigravity App**.

```bash
# Install directly from GitHub
agy plugin install https://github.com/fblissjr/fb-gemini-plugins/tree/main/skills/hypothetical-diff

# Or install from a local checkout of fb-gemini-plugins
agy plugin install ./skills/hypothetical-diff

# Validate plugin manifest and skill structure
agy plugin validate ./skills/hypothetical-diff --strict
```

### 2. Gemini Spark & Gemini App (`Customize > Skills`)

`skills/hypothetical-diff/skills/hypothetical-diff/SKILL.md` is authored to the open `SKILL.md` standard with a self-contained instruction body so it works both as a **single-file upload/paste** and as a **ZIP bundle**:

- **Option A — Single-File Upload or Paste (Fastest, ideal for Gemini Spark & Canvas)**:
  1. Open Gemini Spark / Gemini web or desktop app and go to **Customize $\rightarrow$ Skills** (or **Skills** in the left navigation).
  2. Click **+ $\rightarrow$ Upload skill** and select `skills/hypothetical-diff/skills/hypothetical-diff/SKILL.md` (or click **Create skill** and paste the contents of `SKILL.md`).
  3. Gemini automatically parses the `name` (`hypothetical-diff`) and `description` from the YAML frontmatter on line 1 and enables the skill.
- **Option B — Full Skill Package ZIP Upload (Includes `references/`)**:
  1. Create a ZIP archive with `SKILL.md` at the root of the archive:
     ```bash
     (cd skills/hypothetical-diff/skills/hypothetical-diff && zip -r ../../../../hypothetical-diff-skill.zip SKILL.md references/)
     ```
  2. In **Skills $\rightarrow$ + $\rightarrow$ Upload skill**, upload `hypothetical-diff-skill.zip` and click **Import**.

In Gemini Spark conversations, invoke the skill automatically via natural trigger phrases (*"show me a hypothetical diff"*, *"simulate turn by turn"*, *"zoom in on Hunk 2"*, *"telescoping diff"*, *"mental model diff"*) or explicitly via `/hypothetical-diff` or `@hypothetical-diff`.

---

## Directory Structure

```text
skills/hypothetical-diff/
├── plugin.json                                     # Native Antigravity plugin manifest (v0.3.0)
├── assets/
│   └── logo.svg                                    # 128x128 square SVG icon for App/Marketplace cards
├── README.md                                       # Plugin & dual-platform documentation (this file)
└── skills/
    └── hypothetical-diff/
        ├── SKILL.md                                # Self-contained skill (Antigravity + Gemini Spark)
        └── references/
            ├── simulation-engine.md                # L0-L4 Zoom Ladder, Turn-by-Turn Rallies, Temporal Inversions & Monte Carlo
            ├── domain-playbooks.md                 # 12 worked playbooks across everyday non-coding & coding domains
            └── hyde-theory-and-patterns.md         # HyDE theory, scale consistency, ripple diffs, tone projection & hunk algebra
```
