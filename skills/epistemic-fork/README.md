# Epistemic Fork & Specification Matrix (`epistemic-fork`)

Operationalizes the empirical findings of **Amaç Herdağdelen, Hailey Joren, & Alex Tamkin (2026), *"Who's Aligned to Whom? How AI Agents Shape Experts' Research Judgment Calls"*** into a standalone, 4-mode **Contrastive Judgment & Sensitivity Matrix** plugin (`v0.1.0`) for **Google Antigravity**, **Gemini CLI**, **Gemini Spark**, and **Claude Code**.

---

## Why This Plugin Exists

When a coding or research task combines **objective implementation hygiene** with **underdetermined judgment calls**, frontier AI agents exhibit four empirically measured failure modes:

1. **The Competence Paradox (55% vs. 6% fatal coding errors)**: Experts without AI made fatal procedural bugs 55% of the time vs. 6% with AI ($p = 0.002$)—causing humans to trust the agent when it silently bundles underdetermined judgment defaults into clean, working code.
2. **Upstream Exploratory Pipeline Capture (72pp flip rate; 82% downstream prediction)**: Experts aligned with the agent's upstream analytical leans 86% of the time ($d_1\text{–}d_4$), and those upstream leans alone predicted 82% of final recommendations (AUC 0.84) even when experts pushed back on the final recommendation step ($d_5$).
3. **Unsolicited Pushback & Switching a Taken Side (+53pp gap; 60% switch rate)**: Even when experts declared a side *before* the agent spoke, unsolicited opposing advocacy from the agent caused them to abandon their choice 60% of the time.
4. **Stock Model Prior Monoculture (91% identical vector) & Epistemic Ventriloquism (77% verbatim rationales)**: Unmanipulated frontier models converge on the exact same specification vector over 90% of the time, and 77% of experts repeated the agent's talking points while believing the judgment was mostly their own.

`epistemic-fork` counteracts all four mechanisms with **zero hidden background automation** and **full user control**.

---

## Four Operational Modes

| Mode | Purpose | Key Output |
| :--- | :--- | :--- |
| **`matrix`** *(Contrastive Judgment Matrix)* | Surface upstream judgment forks before locking a single implementation or analytical path | Separates **Layer 1 (Verifiable Hygiene)** from **Layer 2 (Judgment Axes $d_1 \dots d_k$)** and renders the **6-Column Contrastive Judgment & Sensitivity Matrix** ($N$-way/continuous options, Level-2 structural worldviews, failure modes, discriminating observable diagnostics, and expected leverage $\Delta$). |
| **`sweep`** *(Multiverse & Leverage Decomposition)* | Quantify how upstream knobs drive the downstream outcome across combinations | Uses `scripts/spec_matrix.py sweep` to compute distributional bounds, decision-band crossings, and **Marginal Fork Leverage ($\Delta_j$, $R^2_j$)** ranked from highest epistemic stake to lowest. |
| **`lock`** *(Zero-Advocacy Execution Lock)* | Implement a user's declared specification without unsolicited model pushback | Applies **100% Layer-1 objective bug protection** while enforcing a **0% Unsolicited Prior Pushback Firewall** (no unsolicited pivots, no "sensitivity check" demotions, no competing baseline anchoring). |
| **`audit`** *(Two-Pass Hygiene + Antipodal $\overline{L}$ Stress-Test)* | Red-team existing code, pipeline configs, benchmarks, or reports | **Pass 1 (`[HYGIENE AUDIT]`)**: Strictly objective procedural errors.<br>**Pass 2 (`[ANTIPODAL & PROVENANCE AUDIT]`)**: Scans for hardcoded silent defaults (`scan-defaults`), steelmans the **Antipodal Configuration ($\overline{L}$)**, and prints an in-chat **Decision Provenance Map**. |

---

## Bundled Zero-Dependency CLI (`scripts/spec_matrix.py`)

```bash
# Run built-in verification suite
python3 skills/epistemic-fork/scripts/spec_matrix.py --self-test

# Generate a Cartesian or fractional specification grid
python3 skills/epistemic-fork/scripts/spec_matrix.py sweep \
  --axes-json '{"d1_metric": ["A", "B", "C"], "d2_window": ["narrow", "wide"]}'

# Decompose marginal fork leverage (Delta_j & R^2_j) across specification runs
python3 skills/epistemic-fork/scripts/spec_matrix.py sweep \
  --runs runs.json --t-min 0.0 --t-max 2.0

# Scan code/config files for candidate silent judgment defaults
python3 skills/epistemic-fork/scripts/spec_matrix.py scan-defaults path/to/file.py

# Lint drafted matrix text for asymmetric advocacy markers
python3 skills/epistemic-fork/scripts/spec_matrix.py lint-neutrality --file draft.md
```

---

## Installation

### Google Antigravity (`agy`)
```bash
agy plugin install ./skills/epistemic-fork
```

### Gemini CLI
```bash
gemini skills install https://github.com/fblissjr/fb-gemini-plugins.git --path skills/epistemic-fork/skills/epistemic-fork
```
