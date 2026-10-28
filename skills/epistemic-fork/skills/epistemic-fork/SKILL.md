---
name: epistemic-fork
description: >-
  Operationalizes Herdagdelen, Joren, & Tamkin (2026, "Who's Aligned to Whom?
  How AI Agents Shape Experts' Research Judgment Calls") into a 4-mode
  Specification & Judgment Matrix engine across ML/video pipelines, software
  architecture, empirical data science, and strategy. Separates verifiable
  procedural hygiene from underdetermined judgment axes, maps N-way, continuous,
  and hybrid choices in a 6-column Contrastive Judgment & Sensitivity Matrix
  (Level-2 structural worldviews, failure modes, discriminating observable
  diagnostics, and marginal leverage), decomposes multiverse variance via
  scripts/spec_matrix.py, enforces zero-advocacy execution lock when a user
  declares a spec, and runs two-pass hygiene + antipodal stress-test audits.
  Use when user says "epistemic fork", "spec matrix", "judgment matrix",
  "contrastive fork", "specification curve", "multiverse sweep", "fork leverage",
  "lock my spec", "zero advocacy build", "antipodal audit", "two-pass audit",
  "what are the underdetermined choices", or wants to surface hidden upstream
  assumptions before locking in a single implementation or analytical path.
---

# Epistemic Fork & Specification Matrix (`epistemic-fork`)

Counteracts **silent upstream prior capture**, **first-mover anchoring**, **stock model monoculture**, and **unsolicited pushback** when working on tasks that mix **verifiable engineering/analytical hygiene** with **underdetermined judgment calls**.

Grounded in **Amaç Herdağdelen, Hailey Joren, & Alex Tamkin (2026), *"Who's Aligned to Whom? How AI Agents Shape Experts' Research Judgment Calls"*** (see [references/paper-mechanisms.md](references/paper-mechanisms.md) for the empirical findings and Lipton 1990 / Kelly 2010 / Mason 1969 foundations):
- **The Competence Paradox**: Experts without AI made fatal procedural errors **55%** of the time vs. **6%** with AI ($p = 0.002$)—which is why humans trust the agent when it silently bundles **underdetermined judgment priors** into working code.
- **Upstream Pipeline Capture ($d_1\text{–}d_4 \rightarrow d_5$)**: Experts aligned with the agent's upstream technical leans **86%** of the time (**72pp flip rate**), and those upstream leans alone predicted **82%** of final recommendations (AUC **0.84**) even when experts pushed back on the final recommendation step ($d_5$).
- **Unsolicited Pushback ($H_4$)**: When experts declared their own choice *first*, unsolicited opposing advocacy from the agent caused them to abandon their choice **60%** of the time (**+53pp gap**).

---

## Core Principle: Explicit User Control (Zero Hidden Automation)

1. **Never run hidden background workflows or write unrequested sidecar files**:
   - Do **not** silently create or mutate tracking files (such as `DECISION_LEDGER.md`) in the user's repository unless explicitly asked.
   - Do **not** block the user with artificial quizzes or uninvited gates when they ask for straightforward execution.
2. **Always Partition Every Task into Two Layers First (`Step 0`)**:
   - **Layer 1 — Verifiable Hygiene (`VERIFIABLE_HYGIENE`)**: Objective correctness invariants that hold under *every* worldview (join key integrity, preventing data leakage, frame-count/canvas parity, cluster-robust variance aligned with assignment, tensor shape/dtype safety, bounded timeouts, explicit seeds). **Execute and verify Layer 1 automatically.**
   - **Layer 2 — Underdetermined Judgment Axes (`UNDERDETERMINED_FORK`, $d_1 \dots d_k$)**: Choices where two or more competent domain experts can reasonably disagree based on structural assumptions, continuous parameter trade-offs, or domain priorities (metrics, denominators, identification models, mask feathering/window lengths, consistency vs. latency, weighting schemes). **Handle Layer 2 transparently using the selected operational mode below.**

---

## Four Operational Modes

Select the mode requested by the user (or default to **`matrix`** when asked to map options/assumptions, **`sweep`** when asked to test sensitivity across combinations, **`lock`** when the user has already specified their choices and wants implementation, and **`audit`** when reviewing existing code/plans/results):

| Mode | When to Use | What It Does |
| :--- | :--- | :--- |
| **`matrix`** *(Contrastive Judgment Matrix)* | Before locking a single path on an underdetermined ML, engineering, analytical, or strategic task | Separates **Layer 1 (Hygiene)** from **Layer 2 ($d_1 \dots d_k$)** and renders the **6-column Contrastive Judgment & Sensitivity Matrix** ($N$-way/continuous options, Level-2 worldviews, failure modes, discriminating observable check, and expected leverage $\Delta$). |
| **`sweep`** *(Multiverse & Leverage Decomposition)* | When 2–5 upstream parameters or forks can shift a quantitative metric, benchmark, or threshold decision | Parameterizes the axes ($d_1 \dots d_k$), runs or evaluates the grid via [`scripts/spec_matrix.py`](scripts/spec_matrix.py), and ranks every upstream knob by **Marginal Fork Leverage ($\Delta_j$)** and variance share ($R^2_j$). |
| **`lock`** *(Zero-Advocacy Execution Lock)* | When the user declares their chosen specification or selects a vector from the matrix | Implements the user's exact declared choices with **100% Layer-1 procedural bug protection** and a **0% Unsolicited Prior Pushback Firewall** (no unsolicited pivots, no "sensitivity check" demotions, no competing baseline anchoring). |
| **`audit`** *(Two-Pass Hygiene + Antipodal $\overline{L}$ Stress-Test)* | Reviewing an existing script, PR, pipeline config, benchmark, or research report | **Pass 1 (`[HYGIENE AUDIT]`)**: Strictly objective bugs only.<br>**Pass 2 (`[ANTIPODAL & PROVENANCE AUDIT]`)**: Surfaces hardcoded silent defaults (`AI_SILENT_DEFAULT`), steelmans the **Antipodal Configuration ($\overline{L}$)**, and prints an in-chat **Decision Provenance Map**. |

---

## Mode 1: `matrix` — The 6-Column Contrastive Judgment & Sensitivity Matrix

Unlike rigid binary (`Side A vs Side B`) tables that assume every problem is an econometrics script (`analysis.py`), real judgment calls span **discrete alternatives, continuous parameter ranges, $N$-way trade-offs, and hybrid combinations** across ML/video pipelines, systems engineering, data science, and strategy (see [references/domain-templates.md](references/domain-templates.md) for domain-specific templates).

### Step 1.1: List Layer 1 Verifiable Hygiene Invariants
Briefly list (2–4 bullets) the objective procedural hygiene checks that will be enforced regardless of which judgment branch is chosen.

### Step 1.2: Render the 6-Column Contrastive Judgment & Sensitivity Matrix
Identify the **2 to 5 highest-leverage underdetermined axes ($d_1 \dots d_k$)** (never pad with trivial cosmetic choices). For each axis, populate all 6 columns:

| Axis ($d_k$) | Option Spectrum ($N$-Way / Continuous / Hybrid) | Level-2 Worldview (When Each Option Is Structurally Right) | Failure Mode if Worldview Is Wrong | Discriminating Diagnostic (Observable Check Before Deciding) | Leverage / Sensitivity ($\Delta$) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **`d1`: `<Name>`** | • **Opt A**: `<Discrete/Low>`<br>• **Opt B**: `<Discrete/High>`<br>• **Opt C / Hybrid**: `<Range/Joint>` | • **A**: `<Structural condition where A is optimal>`<br>• **B**: `<Structural condition where B is optimal>`<br>• **C**: `<When hybrid/pareto applies>` | • **A**: `<What breaks if A's assumption fails>`<br>• **B**: `<What breaks if B's assumption fails>` | `<Concrete observable check on raw inputs, activations, traces, or pre-trends that tests between A and B>` | **High / Med / Low** (`<Why: flips sign/threshold vs minor scale shift>`) |

### Step 1.3: Enforce Linguistic Symmetry
- **Level-2 Contrastive Parity**: Never present one option as a strawman or default while labeling the alternative a "secondary sensitivity check." State the strongest structural worldview under which a competent expert would insist on each option.
- **No Uninvited First-Person Advocacy**: Avoid phrases like `"I lean toward"`, `"My preference is"`, or `"On principle, I prefer"` when laying out the matrix (unless the user explicitly asks for a recommendation, in which case tie the recommendation directly to the **Discriminating Diagnostic**). You can verify neutrality with:
  ```bash
  python3 scripts/spec_matrix.py lint-neutrality --file <draft.md>
  ```

### Step 1.4: Present the Compact Decision Selector
Close with a concise 1-line vector ballot so the user can lock their choice, request the discriminating diagnostic first, or run a sensitivity sweep:
- **Lock a Vector**: e.g., `d1=A, d2=Moderate (8px), d3=Hybrid`
- **Run Discriminating Diagnostics First**: Execute the column-5 observable checks on the current data/inputs before choosing.
- **Run `sweep` Mode**: Parameterize the high-leverage axes and compare outcomes across the grid.

---

## Mode 2: `sweep` — Parameterized Multiverse & Leverage Decomposition

When upstream choices ($d_1 \dots d_k$) can shift a downstream metric, benchmark score, latency/quality frontier, or policy threshold $[T_{\min}, T_{\max}]$:

### Step 2.1: Parameterize the High-Leverage Forks
Instead of hardcoding a single path, structure the script or evaluation harness so each axis $d_1 \dots d_k$ is an explicit parameter while **Layer 1 Hygiene** remains fixed across all runs.
- To generate a full Cartesian or fractional strided specification grid from axis definitions:
  ```bash
  python3 scripts/spec_matrix.py sweep --axes-json '{"d1_metric": ["physical", "cost_norm"], "d2_model": ["did", "ancova"], "d3_weight": ["equal", "volume"]}' --max-specs 32
  ```

### Step 2.2: Decompose Marginal Fork Leverage ($\Delta_j$)
Feed the executed specification runs (JSON or CSV) into [`scripts/spec_matrix.py`](scripts/spec_matrix.py):
```bash
python3 scripts/spec_matrix.py sweep --runs <spec_runs.json> --estimate-key estimate --ci-low-key ci_low --ci-high-key ci_high --t-min 0.0 --t-max 2.0
```
For each upstream decision axis $d_j$, the tool computes:
1. **Marginal Spread ($\Delta_j$)**:
   $$\Delta_j = \max_{o \in d_j} \mathbb{E}[\hat{y} \mid d_j = o] - \min_{o \in d_j} \mathbb{E}[\hat{y} \mid d_j = o]$$
2. **Single-Factor Variance Share ($R^2_j$)**: The fraction of total specification variance across the grid explained by flipping axis $d_j$ alone.
3. **Sign-Flip & Threshold Crossing Status**: Whether flipping $d_j$ flips the mean sign or pushes the 95% CI across the decision band $[T_{\min}, T_{\max}]$ (`ABOVE_BAND`, `BELOW_BAND`, `INSIDE_BAND`, `STRADDLES_BAND`).

### Step 2.3: Report the Sensitivity Ledger
Present two compact tables:
1. **Distributional Summary**: Total specs run, median, IQR (`q25`–`q75`), min/max range, sign split, and share of specifications in each threshold band.
2. **Fork Leverage Ranking (Ranked by $|\Delta_j|$ and $R^2_j$)**: Highlights which upstream knob is the true **Load-Bearing Crux** ("Trojan horse" fork) vs. which knobs are low-leverage noise.

---

## Mode 3: `lock` — Zero-Advocacy Execution Lock

When the user declares their specification upfront (e.g., *"Implement X with Y estimator and Z weights"* or locks a vector `d1=A, d2=B`), protect them from the **60% switch-on-pushback trap ($H_4$)**:

1. **Parse Declared vs. Omitted Choices**:
   - Treat every user-declared choice as `LOCKED_BY_USER`.
   - If a required mechanical parameter is missing and blocks execution, ask a neutral 1-line question without expressing a lean.
2. **Enforce the Zero-Advocacy Firewall on Layer 2**:
   - **Do NOT** append unsolicited commentary such as *"Where I would have set this up differently..."* or *"You should consider Option B instead..."*
   - **Do NOT** label the user's chosen specification a *"sensitivity check"* or *"secondary baseline"* while promoting the model's modal prior to the headline result.
   - **Do NOT** run an unrequested competing specification alongside the user's specification to create an anchoring contrast.
3. **Enforce 100% Layer-1 Objective Bug Protection**:
   - Preserve the coding agent's **55% $\rightarrow$ 6% fatal-bug reduction**: actively catch and fix syntax errors, broken joins, silent NaN drops, data leakage, unclustered variance where assignment is clustered, or schema impossibilities that break the user's declared specification *on its own terms*.
   - If a requested choice is mathematically impossible on the input schema (e.g., requesting multi-period fixed effects when $T = 1$, or a window longer than the clip), report the factual schema constraint neutrally without steering toward a policy conclusion.

---

## Mode 4: `audit` — Two-Pass Hygiene + Antipodal ($\overline{L}$) Stress-Test & Provenance Map

When asked to review, red-team, or audit an existing script, PR, benchmark, plan, or analysis report, **never mix objective bugs with methodological opinion in the same pass**. Run two strictly separated passes:

### Pass 1: `[PASS 1: VERIFIABLE HYGIENE AUDIT]` (Ground Truth Only)
- Audit the code/artifact strictly for **objective procedural errors** that are wrong under *every* competent worldview:
  - Data leakage or conditioning on post-treatment variables that violate the stated goal.
  - Broken join keys, silent asymmetric row drops (`dropna`), off-by-one frame/index slicing, or unseeded stochastic calls.
  - Mismatched variance clustering, tensor device/dtype corruption, or resource leaks.
- **Hard Rule**: Never classify a defensible judgment choice (e.g., ANCOVA vs. DiD, equal vs. volume weights, tight vs. feathered mask) as a Pass 1 bug.

### Pass 2: `[PASS 2: ANTIPODAL & PROVENANCE AUDIT]` (Underdetermined Priors)
1. **Surface Explicit & Silent Defaults ($L$)**:
   - Run the deterministic default scanner on the target files to catch hardcoded thresholds, filters, estimators, and signature defaults:
     ```bash
     python3 scripts/spec_matrix.py scan-defaults <target_file_or_dir>
     ```
   - Extract the active specification vector $L = (d_1, d_2, \dots, d_k)$, explicitly flagging any choice that was hardcoded without discussion as `AI_SILENT_DEFAULT`.
2. **Construct & Steelman the Antipodal Configuration ($\overline{L}$)**:
   - To break foundation model prior monoculture (where stock models pick the same vector 91%+ of the time), construct the strongest defensible **Antipodal Specification Vector $\overline{L} = (\neg d_1, \neg d_2, \dots, \neg d_k)$** supported by the data/system schema.
   - *(In harnesses with subagent support such as Google Antigravity's `invoke_subagent`, you may optionally run the Antipodal Referee in an isolated subagent context assigned exclusively to steelmanning $\overline{L}$.)*
   - State the **Level-2 Higher-Order Evidence** for $\overline{L}$: why a competent domain peer inspecting the exact same system/dataset would insist on $\overline{L}$ over $L$, and report the counterfactual outcome under $\overline{L}$ (executing the counter-run when fast/local).
3. **Render the In-Chat Decision Provenance Map**:
   - Print a transparent provenance table directly in the response (never silently written to disk unless requested):

| Axis ($d_k$) | Active Choice in $L$ | Provenance Trajectory | Antipodal Choice in $\overline{L}$ | Counterfactual Shift ($L \rightarrow \overline{L}$) | Discriminating Crux Test |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `d1` | `<Option>` | `HUMAN_DECLARED` / `AI_PROPOSED_ACCEPTED` / `FLIPPED_AFTER_PUSHBACK` / `AI_SILENT_DEFAULT` | `<Counter-Option>` | `<Delta on metric/behavior>` | `<Observable test settling L vs ~L>` |

---

## Bundled CLI Tool Reference (`scripts/spec_matrix.py`)

`scripts/spec_matrix.py` is a zero-dependency Python 3 stdlib CLI bundled with this skill:

```bash
# 1. Run built-in verification suite
python3 scripts/spec_matrix.py --self-test

# 2. Generate a Cartesian or fractional specification grid from axis options
python3 scripts/spec_matrix.py sweep \
  --axes-json '{"d1_metric": ["A", "B", "C"], "d2_window": ["narrow", "wide"]}' \
  --max-specs 32

# 3. Decompose marginal fork leverage (Delta_j & R^2_j) across executed runs (JSON or CSV)
python3 scripts/spec_matrix.py sweep \
  --runs runs.json \
  --estimate-key estimate \
  --ci-low-key ci_low \
  --ci-high-key ci_high \
  --t-min 0.0 --t-max 2.0

# 4. Scan source/config files for candidate silent defaults (Pass 2 audit)
python3 scripts/spec_matrix.py scan-defaults path/to/script.py

# 5. Lint drafted prose for asymmetric first-person advocacy or "sensitivity check" demotion
python3 scripts/spec_matrix.py lint-neutrality --file draft_matrix.md
```
