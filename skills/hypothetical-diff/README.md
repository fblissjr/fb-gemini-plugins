# hypothetical-diff

last updated: 2026-10-17

A universal **Hypothetical Diff (HyDiff)** skill and plugin for **Google Antigravity** (`agy` CLI v1.4.0+ and Antigravity App v2.24.0+) and **Gemini Spark** (including Gemini web/desktop `Customize > Skills` and Gemini Enterprise).

---

## Inspiration: From HyDE (2023) to Hypothetical Diffs

In **HyDE** (*Hypothetical Document Embeddings*, Gao et al., ACL 2023, *"Precise Zero-Shot Dense Retrieval without Relevance Labels"*), an LLM bridges the semantic gap between a short, ambiguous query and a rich target document by **generating a hypothetical target document ($\hat{d}$) first**, and then using that concrete artifact to retrieve and ground against real data. Even when $\hat{d}$ contains unverified details, its structure, vocabulary, and shape place it in the right neighborhood of solution space, and grounding washes out the hallucinations.

**`hypothetical-diff` generalizes HyDE from static documents ($\hat{d}$) to universal state transitions ($\hat{\Delta} = \text{After} - \text{Before}$)** across **any domain—not just code**:
- **Writing, Essays & Executive Memos**
- **Legal Contracts, Redlines & Company Policies**
- **Product Strategy, Org Design & Career/Life Decisions**
- **Calendars, Weekly Schedules & Personal/Team Operations**
- **Spreadsheets, Budgets, Pricing & Financial Models**
- **Scientific Hypotheses, Research & Root-Cause Troubleshooting**
- **Software Architecture, Config & Codebases**

Instead of debating, searching, or planning in abstract prose, `hypothetical-diff` synthesizes a concrete `--- Before` / `+++ After` delta in the native medium of the domain first, and then uses that diff to **retrieve real context**, **expose hidden assumptions**, **enforce resource conservation**, and **align on exact hunks before execution**.

---

## How It Works: Project $\rightarrow$ Ground $\rightarrow$ Converge

| Step | Action | Why It Works |
|------|--------|--------------|
| **1. Project ($\hat{\Delta}$)** | Synthesize a concrete `--- Before` / `+++ After` diff (or $K$ orthogonal diffs) in the target medium, tagging unverified specifics as `[HYPOTHETICAL]`. | Humans and search tools react poorly to abstract descriptions ("make it more executive", "find where we handle data retention") but have instant high-bandwidth precision when given a concrete delta. |
| **2. Ground (The Bottleneck)** | Intersect $\hat{\Delta}$ with reality: query corpora using `-`/`+` anchors, verify conservation laws ($\sum \Delta = 0$), test discriminating observables, or get hunk-level user feedback. | Just like HyDE's contrastive encoder bottleneck, grounding washes out fabricated placeholders while locking onto the true target state. |
| **3. Converge ($\Delta_{\text{real}}$)** | Replace `[HYPOTHETICAL]` placeholders with verified data and approved hunks. | Produces a precision-verified edit, decision plan, or root-cause diagnosis with zero wasted full-document rewrites. |

---

## Five Operational Modes

| Mode | When to Use | Example Prompt |
|------|-------------|----------------|
| **`search`** *(HyDE Retrieval)* | Locate where a policy, clause, metric, or behavior lives—or find past precedents—using `-` (Before) and `+` (After) anchors from $\hat{\Delta}$. | *"Use a hypothetical diff to find where our vendor agreements or handbook cover AI model training on customer data."* |
| **`align`** *(Prototype Slice)* | Resolve vague or subjective goals by previewing a 1–3 hunk Before/After slice before rewriting an entire document, deck, or system. | *"Show me a hypothetical diff on the first two paragraphs of this memo to make it thesis-first and cut 30% of the words."* |
| **`decide`** *(Counterfactual)* | Stress-test a strategy, pricing change, calendar overhaul, or career decision by enforcing the **Conservation Law of Diffs** (every `+` must name the `-` that funds it). | *"Run a counterfactual diff comparing staying PLG vs. pivoting to enterprise sales over the next 6 months across engineering headcount, cashflow, and my weekly calendar."* |
| **`diagnose`** *(Reverse-Diff)* | Debug any regression (a funnel drop, stalled project, failed experiment, or broken build) by generating competing upstream causal diffs ($\hat{\Delta}_{\text{cause}}$) and their discriminating check. | *"Our mobile checkout conversion dropped from 6.1% to 1.2% this week while desktop stayed flat. Reverse-diff the top 3 hypothetical upstream causes and tell me what to check first."* |
| **`ensemble`** *($K$-Diffs)* | Explore multiple valid directions by generating $K=2\text{–}3$ orthogonal diffs, separating **Consensus Hunks** from **Divergent Hunks**. | *"Give me 3 hypothetical diffs for restructuring our Q4 budget: one conservative, one content-heavy, and one event-led."* |

---

## Examples Across Domains

### Example 1: Counterfactual Calendar & Operations Diff (`decide` mode)
In prose, it is easy to wish for *"10 hours of deep work a week"*. In a **Hypothetical Diff**, a 40-hour week is a conserved system ($\Delta t = 0$), forcing every `+` block to name the exact `-` block it replaces:

```diff
--- Baseline: Current Weekly Schedule (40h allocated)
+++ Hypothetical: Maker-Morning Operating Rhythm (Net Delta: 0h)
@@ Tue / Thu Morning Protection @@
- [09:30–10:00] Daily Standup & Triage (2x/wk = 1.0h)
- [10:00–12:00] Open calendar / ad-hoc 1:1s & Slack triage (2x/wk = 4.0h)
+ [09:00–11:30] Protected Deep Work Block — notifications paused (2x/wk = 5.0h)
@@ Tue / Thu Afternoon Relocation @@
+ [13:30–14:00] Batched Async Standup + Triage Window (2x/wk = 1.0h)
- [14:00–15:00] Optional cross-team status syncs -> move to async digest (-1.0h)
```

### Example 2: HyDE Diff-Anchored Search (`search` mode)
When searching a Google Drive, Notion/Docs wiki, legal repository, or codebase for where to make a change:
1. **Project $\hat{\Delta}$**: Draft what the existing paragraph/clause/config (`-`) and the updated version (`+`) would look like.
2. **Extract Dual Anchors**:
   - **Before-anchors (`-`)** find *where the current policy or code lives today* (e.g., `"aggregated, de-identified data"`, `"solely to provide the Services"`).
   - **After-anchors (`+`)** find *historical precedents/amendments that already made this change* (e.g., `"train, fine-tune, or evaluate"`).
3. **Ground**: Run the search using those concrete phrases, retrieve the real source, and present the grounded diff.

### Example 3: Executive Writing & Redline Alignment (`align` mode)
Instead of rewriting a 10-page document in the dark, `hypothetical-diff` projects a 2-hunk diff on a representative section alongside its **Load-Bearing Assumptions**, letting you approve Hunk 1 and tweak Hunk 2 in a single turn.

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

In Gemini Spark conversations, invoke the skill automatically via natural trigger phrases (*"show me a hypothetical diff"*, *"counterfactual diff"*, *"HyDE diff"*) or explicitly via `/hypothetical-diff` or `@hypothetical-diff`.

---

## Directory Structure

```text
skills/hypothetical-diff/
├── plugin.json                                     # Native Antigravity plugin manifest
├── README.md                                       # Plugin & dual-platform documentation (this file)
├── assets/
│   └── logo.svg                                    # 128x128 square SVG icon for App & Marketplace cards
└── skills/
    └── hypothetical-diff/
        ├── SKILL.md                                # Self-contained skill (Antigravity + Gemini Spark)
        └── references/
            ├── domain-playbooks.md                 # Worked templates across 7 non-coding & coding domains
            └── hyde-theory-and-patterns.md         # HyDE (Gao et al. 2023) theory, anchor extraction & K-diffs
```
