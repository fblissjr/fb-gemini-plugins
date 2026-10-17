---
name: hypothetical-diff
description: >-
  Generalizes Hypothetical Document Embeddings (HyDE, Gao et al. 2023) from
  static documents to universal Before/After diffs across any domain—writing,
  strategy, calendars, contracts, spreadsheets, operations, research, and code.
  Instead of searching, planning, or debating in abstract prose, first
  synthesizes a concrete hypothetical delta (--- Before / +++ After) in the
  target medium, then uses that diff to anchor retrieval, surface hidden
  assumptions, enforce resource conservation, or preview changes before
  execution. Use when user says "hypothetical diff", "hydiff", "HyDE diff",
  "show me the diff if", "what would actually change if", "counterfactual diff",
  "diff my options", "search using a hypothetical diff", "redline this
  hypothetically", "stress-test this decision with a diff", "reverse-diff this
  problem", or wants a concrete Before/After preview before committing to a
  change.
---

# Hypothetical Diff (`hypothetical-diff`)

Bridges the gap between abstract intent and concrete reality by synthesizing a
plausible **Before $\rightarrow$ After delta ($\hat{\Delta}$)** *first*, then
grounding that delta against real documents, data, constraints, or user feedback.

Inspired by **HyDE** (*Hypothetical Document Embeddings*, Gao et al., ACL 2023,
*"Precise Zero-Shot Dense Retrieval without Relevance Labels"*), which showed
that projecting an abstract query into a concrete (even partially hallucinated)
target document places it in the exact structural and lexical neighborhood of
the real answer. **Hypothetical Diff** lifts this principle from static
documents ($\hat{d}$) to **state transitions ($\hat{\Delta} = \text{After} - \text{Before}$)**
for anything that can change: an essay, a legal clause, a quarterly roadmap, a
weekly calendar, a budget model, a scientific hypothesis, or a codebase.

---

## Core Mechanism: Project $\rightarrow$ Ground $\rightarrow$ Converge

Never reason, search, or ask for approval purely in abstract prose when the goal
is a change. Run this three-step loop:

1. **Project ($\hat{\Delta}$ — Zero-Shot Delta Synthesis)**
   - Translate the user's goal, question, or hypothesis into a concrete
     `--- Before` / `+++ After` diff written in the **native medium of the
     domain** (clauses for a contract, time blocks for a calendar, rows/formulas
     for a sheet, prose hunks for an article, unified diff for code).
   - Where exact real-world details are not yet known, fill in plausible,
     high-specificity exemplars and mark them `[HYPOTHETICAL]`. Specificity is a
     feature, not a bug: concrete numbers, names, and structures expose false
     assumptions immediately.

2. **Ground (The Reality Bottleneck)**
   - Intersect $\hat{\Delta}$ with reality to wash out ungrounded assumptions:
     - **In `search` mode**: Extract **Before-anchors** (`-` lines: terms,
       structures, or anti-patterns that must currently exist) and
       **After-anchors** (`+` lines: vocabulary of prior precedents) to query
       the workspace, Drive, Docs, Gmail, or repository.
     - **In `decide` / `align` modes**: Test the **Conservation Law of Diffs**
       (every `+` addition in a finite system must name the `-` removal that
       pays for it) and expose load-bearing assumptions for user critique.
     - **In `diagnose` mode**: Test whether the discriminating observable
       predicted by the hypothetical causal diff actually appears in reality.

3. **Converge ($\Delta_{\text{real}}$ — Verified Delta)**
   - Replace `[HYPOTHETICAL]` placeholders with retrieved evidence or confirmed
     user choices, producing an actionable, verified diff ready for execution.

---

## Five Operational Modes

Select the mode that matches the user's immediate bottleneck (or combine them
sequentially, such as `search` $\rightarrow$ `align`):

| Mode | Trigger / Situation | What $\hat{\Delta}$ Represents | How Grounding Works |
|------|---------------------|--------------------------------|---------------------|
| **`search`** *(HyDE Retrieval)* | "Where do we handle X?", "Find past memos/commits/clauses that changed Y" | A plausible diff of the target passage, policy, sheet, or file (`-` current pattern, `+` target pattern) | Queries the corpus using `-` tokens (to find what needs changing) and `+` tokens (to find historical precedents) |
| **`align`** *(Prototype Slice)* | Vague or subjective request ("Make this punchier", "Tighten our SLA", "Reorganize the deck") | A 1–3 hunk Before/After diff on a representative slice before touching the whole artifact | User reacts to concrete hunks ("Yes to Hunk 1, keep the 30-day cap in Hunk 2") in one turn |
| **`decide`** *(Counterfactual)* | Choosing between strategies, life/career paths, policies, or priorities | `--- Baseline (Status Quo / Option A)` vs. `+++ Counterfactual (Option B +6mo)` across concrete artifacts | Enforces resource conservation ($\sum \Delta = 0$ on time, budget, headcount, or scope) to reveal hidden trade-offs |
| **`diagnose`** *(Reverse-Diff)* | Something broke or regressed (metrics dropped, project stalled, experiment or build failed) | $K=2\text{–}3$ competing upstream **Causal Diffs** ($\hat{\Delta}_{\text{cause}}$) that could yield the observed symptom delta | Identifies the single **discriminating check** that confirms one causal diff and falsifies the others |
| **`ensemble`** *($K$-Diffs)* | Open-ended improvement where multiple valid directions exist | $K=3$ orthogonal diffs (e.g., *Minimal/Safe*, *Structural/Clean*, *Bold/Inversion*) | Separates **Consensus Hunks** (agreed across all $K$) from **Divergent Hunks** (the exact decision frontier) |

---

## Universal Diff Notation (Any Domain)

Always render $\hat{\Delta}$ in the representation most native to the subject
matter. Use fenced ```` ```diff ```` blocks for line-oriented deltas and
structured Delta Tables for multi-dimensional models:

### 1. Prose, Documents, Contracts & Communications
Use semantic unified hunks at the sentence, bullet, or clause level. Keep
unchanged context lines (` `) minimal (1–2 lines) so the signal stands out:

```diff
--- Baseline: Vendor Agreement §8.2 (Limitation of Liability) [HYPOTHETICAL]
+++ Counterfactual: Mutual Super-Cap for Data Processing
@@ §8.2 Liability Cap @@
  EXCEPT FOR BREACHES OF CONFIDENTIALITY, NEITHER PARTY'S AGGREGATE LIABILITY
- SHALL EXCEED THE FEES PAID BY CUSTOMER IN THE TWELVE (12) MONTHS PRECEDING THE CLAIM.
+ SHALL EXCEED TWO TIMES (2X) THE ANNUALIZED FEES PAID OR PAYABLE UNDER THIS AGREEMENT;
+ PROVIDED THAT FOR DATA PROTECTION BREACHES (§11), LIABILITY SHALL NOT EXCEED $1,000,000.
```

### 2. Schedules, Calendars, Habits & Operations
Enforce **strict time/capacity conservation** ($\Delta \text{Hours} = 0$). A
diff that adds `+6h` of deep work or new meetings without deleting `-6h` of
existing commitments is invalid:

```diff
--- Baseline: Weekly Operating Rhythm (40h allocated)
+++ Hypothetical: Maker-Morning Schedule (Net Delta: 0h)
@@ Tue / Thu 09:00–12:00 @@
- [09:30–10:00] Daily Standup & Triage (2x/wk = 1.0h)
- [10:00–12:00] Open calendar / ad-hoc 1:1s & Slack responsiveness (2x/wk = 4.0h)
+ [09:00–11:30] Protected Deep Work Block — no meetings, notifications paused (2x/wk = 5.0h)
@@ Tue / Thu Afternoon Relocation @@
+ [13:30–14:00] Batched Async Standup + Triage Window (2x/wk = 1.0h)
- [14:00–15:00] Optional cross-team syncs (move to async digest = -1.0h)
```

### 3. Spreadsheets, Budgets, Pricing & Quantitative Models
Use a **Delta Table** coupled with a formula/assumption diff so both numerical
shifts and structural driver changes are explicit:

| Dimension / Row | `--- Before` | `+++ After (Hypothetical)` | Net Delta ($\Delta$) | Load-Bearing Assumption |
|-----------------|--------------|----------------------------|----------------------|-------------------------|
| Self-Serve Tier | \$29 / seat / mo | *Discontinued (Free $\rightarrow$ Pro)* | -\$29 tier | Bottom 40% of seats convert at $\ge 18\%$ to Pro |
| Pro Tier | \$79 / seat / mo | \$99 / seat / mo (incl. AI) | +\$20 (+25.3%) | Churn increase stays $< 1.5\%/\text{mo}$ |
| Support Load | 420 tickets / wk | ~260 tickets / wk | -160 (-38%) | Low-ARR self-serve accounts drove 55% of ticket volume |

### 4. Strategy, Org Design & Life/Career Decisions
Diff the **concrete artifacts of reality 6–12 months out** rather than listing
abstract pros and cons:
- `@@ Commitments & Deliverables @@` (`-` what you stop doing / `+` what you own)
- `@@ Incentives & Metrics @@` (`-` old scoreboard / `+` new scoreboard)
- `@@ Interfaces & Dependencies @@` (`-` old handoffs / `+` new handoffs)
- `@@ Failure Modes @@` (`-` risks retired / `+` new risks introduced)

### 5. Software, Config & System Architecture
Use standard unified diffs (`--- a/path/to/file`, `+++ b/path/to/file`) with
exact symbol names, types, and config keys to maximize search anchor precision.

---

## Step-by-Step Execution Workflow

1. **Classify the Domain & Mode**
   - Identify the artifact or system being changed and select `search`, `align`,
     `decide`, `diagnose`, or `ensemble`.
2. **Enforce the Conservation Constraint**
   - Ask: *What is finite here?* (Word count, reader attention, 24 hours/day,
     headcount, budget, risk tolerance, API surface, latency). Ensure every `+`
     in $\hat{\Delta}$ accounts for the corresponding `-`.
3. **Synthesize the Hypothetical Diff ($\hat{\Delta}$)**
   - Keep each hunk focused on **one logical decision or mechanism**.
   - Tag unverified details with `[HYPOTHETICAL]` so the user never mistakes a
     projection for a fetched fact.
4. **Extract Anchors & Ground (When Connected to Files / Tools / Apps)**
   - **In Antigravity**: Use `-` and `+` anchors from $\hat{\Delta}$ to run
     targeted searches or view relevant files, then update $\hat{\Delta}$ into a
     grounded diff.
   - **In Gemini Spark / Workspace**: Use anchors from $\hat{\Delta}$ to locate
     relevant Google Docs, Sheets, Slides, Calendar events, Gmail threads, or
     Drive files before proposing edits.
5. **Surface the Decision Frontier**
   - List the 2–4 **Load-Bearing Assumptions** behind the diff and ask the user
     which hunks to accept, modify, or reject.

---

## Output Format

Structure responses using this template (adapt section headers naturally to the
size of the request):

```markdown
### 1. Intent & Mode
- **Mode**: `<search | align | decide | diagnose | ensemble>`
- **Target Medium**: `<e.g., Contract Clause | Weekly Calendar | Product Strategy | Codebase>`
- **Conservation Constraint**: `<e.g., Net time = 0h/wk | Max length = 250 words | Budget neutral>`

### 2. Hypothetical Diff ($\hat{\Delta}$)
> Status: `[HYPOTHETICAL — UNGROUNDED]` (or `[GROUNDED AGAINST <source>]`)

```diff
--- Baseline: <description of current or assumed state>
+++ Hypothetical: <description of target or counterfactual state>
@@ Hunk 1: <name of mechanism or section> @@
- <concrete before state>
+ <concrete after state>
```

### 3. Load-Bearing Assumptions & Trade-offs
1. **[Hunk 1]**: Assumes `<X>`. If false, `<consequence>`.
2. **[Conservation Check]**: Adding `+<A>` requires removing `-<B>`.

### 4. Grounding & Next Step
- **Anchors / Verification**: `<search terms used, discriminating check, or hunk approval prompt>`
```

---

## Approval & Safety Guardrails

- **Never fabricate citations or claim a `[HYPOTHETICAL]` diff is already live**:
  Always distinguish between the *projected* diff ($\hat{\Delta}$) used for
  discovery/alignment and the *grounded* diff ($\Delta_{\text{real}}$) verified
  against real data.
- **Approval Gate (Low $\rightarrow$ High)**:
  - **Generating a Hypothetical Diff** is always a **safe, read-only preview**
    (Low risk).
  - **Applying the converged diff** to real files, sending emails (Gmail),
    modifying shared calendars (Google Calendar), updating trackers (Sheets), or
    editing documents (Docs/Drive/repo files) requires **explicit user approval
    of the hunks** whenever the action is external, shared, or destructive.

---

## Optional Deep-Dive References

When running in an environment with bundled skill files (Google Antigravity or a
ZIP skill upload in Gemini Spark), load these on demand only when needed:
- [references/domain-playbooks.md](references/domain-playbooks.md): Worked
  Before/After diff templates across 7 domains (Writing, Legal/Policy, Strategy,
  Calendar/Workspace Operations, Finance/Sheets, Science/Debugging, and Code).
- [references/hyde-theory-and-patterns.md](references/hyde-theory-and-patterns.md):
  Deep dive on Gao et al. (2023) HyDE mechanics, asymmetric `-`/`+` anchor
  extraction, $K$-diff variance analysis, and failure modes to avoid.
