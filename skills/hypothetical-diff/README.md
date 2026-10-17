# hypothetical-diff

last updated: 2026-10-17

A universal **Hypothetical Diff (HyDiff)** skill and plugin (`v0.2.0`) for **Google Antigravity** (`agy` CLI v1.4.0+ and Antigravity App v2.24.0+) and **Gemini Spark** (including Gemini web/desktop `Customize > Skills` and Gemini Enterprise).

---

## Inspiration: From HyDE (2023) to Universal State Transitions

In **HyDE** (*Hypothetical Document Embeddings*, Gao et al., ACL 2023, *"Precise Zero-Shot Dense Retrieval without Relevance Labels"*), an LLM bridges the semantic gap between a short, ambiguous query and a rich target document by **generating a hypothetical target document ($\hat{d}$) first**, and then using that concrete artifact to retrieve and ground against real data. Even when $\hat{d}$ contains unverified details, its structure, vocabulary, and shape place it in the right neighborhood of solution space, and grounding washes out the hallucinations.

**`hypothetical-diff` generalizes HyDE from static documents ($\hat{d}$) to universal state transitions ($\hat{\Delta} = \text{After} - \text{Before}$)** across **every everyday non-coding and coding domain—in any tone set by the user**:
- **Difficult Conversations, Negotiation & Relationships** (*Spoken Script + Subtext + Counterparty Reaction Diffs*)
- **Learning, Research & Unlearning** (*Intuitive Misconception $\rightarrow$ Expert Mental Model + Prediction Flip Diffs*)
- **Creative Writing, Storytelling, Speeches & Tone Re-Skinning** (*Show-Don't-Tell, Narrative Beats & Multi-Tone Dial Diffs*)
- **Habits, Personal Life, Health & Travel Itineraries** (*Environment Friction, Low-Energy Fallbacks & Time/Energy Conservation Diffs*)
- **Policy, Economics, History & Society** (*1st-, 2nd- [Goodhart/Loophole], and 3rd-Order Ripple Diffs*)
- **Legal Contracts, Redlines & Company Policies**
- **Product Strategy, Org Design & Career/Life Decisions**
- **Calendars, Weekly Schedules & Workspace Operations**
- **Spreadsheets, Budgets, Pricing & Financial Models**
- **Scientific Hypotheses & Root-Cause Troubleshooting**
- **Software Architecture, Config & Codebases**

Instead of advising, debating, searching, or planning in abstract prose, `hypothetical-diff` synthesizes a concrete `--- Before` / `+++ After` delta in the native medium of the domain first, simulates scenarios in **any user-specified tone or persona**, and lets you **cherry-pick or mix-and-match numbered hunks (`A1 + B2`)** before execution.

---

## How It Works: Project $\rightarrow$ Ground $\rightarrow$ Converge

| Step | Action | Why It Works |
|------|--------|--------------|
| **1. Project ($\hat{\Delta}$)** | Synthesize a concrete `--- Before` / `+++ After` diff with numbered semantic hunks (`@@ Hunk 1: ... @@`) in the target medium and user-specified tone, tagging unverified specifics as `[HYPOTHETICAL]`. | Humans and search tools react poorly to abstract descriptions ("be firm but empathetic", "make it more executive") but have instant high-bandwidth precision when given a concrete delta. |
| **2. Ground (The Bottleneck)** | Intersect $\hat{\Delta}$ with reality: query corpora using `-`/`+` anchors, verify conservation laws ($\sum \Delta = 0$ on time, energy, attention, or budget), trace 2nd-order adaptations, or test discriminating observables. | Just like HyDE's contrastive encoder bottleneck, grounding washes out wishful thinking and fabricated placeholders while locking onto the true target state. |
| **3. Converge ($\Delta_{\text{real}}$)** | Use **Interactive Hunk Selection** (`ask_question` checkboxes in Antigravity or a 1-line Mix-and-Match Ballot in Gemini Spark) to combine exact hunks (`Keep 1 & 3` or `A1 + B2`). | Produces a precision-verified rewrite, script, decision plan, or diagnosis with zero wasted full-document rewrites. |

---

## Six Operational Modes

| Mode | When to Use | Example Prompt |
|------|-------------|----------------|
| **`search`** *(HyDE Retrieval)* | Locate where a policy, clause, note, metric, or behavior lives—or find past precedents—using `-` (Before) and `+` (After) anchors from $\hat{\Delta}$. | *"Use a hypothetical diff to find where our vendor agreements or handbook cover AI model training on customer data."* |
| **`align`** *(Prototype Slice)* | Resolve subjective writing, editing, or design goals by previewing a 1–3 hunk Before/After slice before rewriting an entire document or deck. | *"Show me a hypothetical diff on the opening scene of my story to make it show-don't-tell in a minimalist tone."* |
| **`decide`** *(Counterfactual)* | Stress-test a career move, habit routine, travel itinerary, strategy, or budget by enforcing the **Conservation Law of Diffs** (every `+` must name the `-` that funds it). | *"Run a counterfactual diff on my Kyoto itinerary so I'm not exhausted by 3pm, conserving walking energy and transit time."* |
| **`diagnose`** *(Reverse-Diff)* | Debug any regression or plateau (a stalled habit, broken negotiation, funnel drop, or bug) by generating competing upstream causal diffs ($\hat{\Delta}_{\text{cause}}$) and their discriminating check. | *"Our mobile checkout conversion dropped from 6.1% to 1.2% this week while desktop stayed flat. Reverse-diff the top 3 upstream causes."* |
| **`ensemble`** *($K$-Diffs)* | Explore multiple creative, strategic, or tonal directions by generating $K=2\text{–}3$ orthogonal diffs, separating **Consensus Hunks** from **Divergent Hunks** for mix-and-match (`A1 + B2`). | *"Give me 3 hypothetical diffs for replying to this scope-creep request across 3 tones: collaborative, crisp executive, and zero-cushion."* |
| **`simulate`** *(Scenario, Dialogue & Ripple)* | Simulate how any conversation, negotiation, historical counterfactual, or policy plays out across **Subtext**, **Counterparty Reactions**, or **1st/2nd/3rd-Order Ripples** in **any user-set tone**. | *"Simulate a hypothetical diff for asking for a $165k compensation adjustment (spoken script + subtext + manager reaction) in a warm, unshakeable peer tone."* |

---

## Universal Tone, Voice & Persona Engine

You can ask `hypothetical-diff` to simulate or rewrite **anything in any tone**—for example:
- **Interpersonal & Coaching**: *Warm therapist, calm senior partner, diplomatic hostage negotiator, Socratic tutor*
- **Direct & Analytical**: *Brutally honest VC partner, appellate judge, skeptical physicist, Warren Buffett shareholder letter*
- **Creative & Literary**: *Hemingway sparse, Raymond Carver minimalist, deadpan roast, noir detective, Regency drama, sports commentator*

Tone works in three ways:
1. **Tone *as* the Diff**: Hold facts invariant ($\Delta \text{Facts} = 0$) while diffing the voice (`--- Baseline Draft` $\rightarrow$ `+++ Target Tone`).
2. **Tone *of* the Simulation**: Run a career decision, policy ripple diff, or negotiation in the persona's voice to expose blind spots that neutral corporate prose hides.
3. **Multi-Tone Dial (`ensemble` mode)**: View $K=3$ calibrated intensity steps side-by-side and mix-and-match hunks (`A1 + B2`).

---

## Examples Across Everyday Non-Coding Domains

### Example 1: Difficult Conversation — Script, Subtext & Reaction Diff (`simulate` mode)

```diff
--- Baseline: Instinctive Reply to Scope Creep (Over-Apologetic)
+++ Simulated: Warm "Yes, If" Trade-Off (Tone: Calm, Senior Partner)
@@ Hunk 1: The Spoken / Written Reply @@
- Sorry, we're totally swamped right now so we can't add the custom workshop before Friday.
+ I'd love to make the custom workshop happen. Because our week is fully committed to the Friday launch, we can either (a) run the workshop next Wednesday, or (b) do it Thursday if we move the launch review to Monday. Which works best for you?
@@ Hunk 2: Subtext & Counterparty Reaction @@
- Heard as: "Refusal / bottleneck" -> Triggers pushback or escalation.
+ Heard as: "Shared ownership of a trade-off" -> Shifts the other person from fighting you to prioritizing their own list.
```

### Example 2: Learning & Unlearning — Mental Model Diff (`align` mode)

```diff
--- Baseline: Intuitive Misconception (Antibiotic Resistance)
+++ Updated Mental Model: Evolutionary Selection Mechanism
@@ Hunk 1: What Actually Becomes Resistant? @@
- "If I take antibiotics too often, MY BODY becomes resistant/tolerant to the drug."
+ Your body never becomes resistant—the BACTERIA population undergoes natural selection. The drug kills 99.9% of susceptible bacteria, leaving the 0.1% with a resistance mutation an open field to multiply.
@@ Hunk 2: Real-World Prediction Flip @@
- Old Prediction: Resistance is personal tolerance (like caffeine) that resets if I take a break.
+ New Prediction: Resistant bacteria selected in one person can spread to someone who has never taken an antibiotic in their life.
```

### Example 3: Policy & Society — 1st / 2nd / 3rd-Order Ripple Diff (`simulate` mode)

```diff
--- Baseline: Uncapped Hospital ER Wait Times
+++ Simulated Policy: Strict 4-Hour ER Wait-Time Mandate (+12 Months)
@@ Hunk 1 (1st-Order Direct Effect): Fast-Track Triage @@
- Minor cases wait 5–7 hours behind complex admissions.
+ Dedicated nurse-practitioner lanes clear minor cases in <90m.
@@ Hunk 2 (2nd-Order Goodhart Loophole): Clock-Start Gaming @@
- Patients enter the ER clock immediately upon ambulance arrival.
+ At Hour 3:50, overloaded hospitals hold patients in ambulance bays ("ramping") to delay starting the official ER clock.
@@ Hunk 3 (3rd-Order Equilibrium Fix): Paired Metric @@
- Scoreboard tracks only "Door-to-Decision <= 4h".
+ Scoreboard pairs "Ambulance Offload Time + 4h Target + 7-Day Readmission Rate" to close the loophole.
```

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

In Gemini Spark conversations, invoke the skill automatically via natural trigger phrases (*"show me a hypothetical diff"*, *"simulate a diff in the tone of..."*, *"script and subtext diff"*, *"mental model diff"*) or explicitly via `/hypothetical-diff` or `@hypothetical-diff`.

---

## Directory Structure

```text
skills/hypothetical-diff/
├── plugin.json                                     # Native Antigravity plugin manifest (v0.2.0)
├── assets/
│   └── logo.svg                                    # 128x128 square SVG icon for App/Marketplace cards
├── README.md                                       # Plugin & dual-platform documentation (this file)
└── skills/
    └── hypothetical-diff/
        ├── SKILL.md                                # Self-contained skill (Antigravity + Gemini Spark)
        └── references/
            ├── domain-playbooks.md                 # 12 worked playbooks across everyday non-coding & coding domains
            └── hyde-theory-and-patterns.md         # HyDE theory, ripple diffs, tone projection & hunk algebra
```
