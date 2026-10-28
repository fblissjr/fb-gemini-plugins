# Domain Templates for the Contrastive Judgment & Sensitivity Matrix

Unlike narrow econometrics-only fork tables that force every problem into a binary `Side A vs Side B` regression script, `epistemic-fork` applies across **any domain where objective implementation hygiene and underdetermined judgment calls are entangled**.

Use the domain templates below to structure the **6-column Contrastive Judgment & Sensitivity Matrix** for the user's task.

---

## Template 1: ML, Generative Video / Audio & Multimodal Pipelines

Use when tuning model conditioning, masking/compositing parameters, attention kernels, sampling schedules, window lengths, or evaluation metrics.

### Layer 1: Verifiable Hygiene (Apply Automatically)
- Frame rate (FPS), resolution canvas alignment (e.g., multiples of patch/stride size), and exact frame-count parity between source, mask, and output.
- Determinism controls (explicit RNG seed, cache state reporting) and tensor dtype/device invariants.
- Grading numerical/kernel changes on captured activations rather than eye-balling a single rendered clip.

### Layer 2: Contrastive Judgment & Sensitivity Matrix

| Axis ($d_k$) | Option Spectrum ($N$-Way / Continuous / Hybrid) | Level-2 Worldview (When Each Option Is Structurally Right) | Failure Mode if Worldview Is Wrong | Discriminating Diagnostic (Observable Check Before Deciding) | Leverage / Sensitivity ($\Delta$) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **`d1`: Spatial Mask Boundary & Feathering** | • **Tight (`0–2px`)**<br>• **Moderate (`6–12px` feather)**<br>• **Adaptive (motion-scaled dilation)** | • **Tight**: Background near subject edge is high-detail and must never be regenerated<br>• **Moderate**: Latent stride (`8x/16x`) requires transition band to avoid seam halos<br>• **Adaptive**: Fast motion creates motion-blur spill outside static silhouette | • **Tight**: Hard latent-grid seam / silhouette cutout artifact<br>• **Moderate**: Bleeds generated texture onto adjacent static objects<br>• **Adaptive**: Over-masks during fast camera pans | Inspect latent-grid stride overlap and boundary pixel delta on 3 frames (static, slow turn, fast motion) | **High** on edge seam quality & background preservation |
| **`d2`: Temporal Window Length ($T$)** | • **Shot-tight ($T = 97\text{–}145$)**<br>• **Full-span ($T = 241\text{–}362$)**<br>• **Overlapping chunked windows** | • **Shot-tight**: Attention cost scales $O(T^2)$; short window maximizes local temporal coherence<br>• **Full-span**: Long-range identity/lighting persistence across the entire take dominates<br>• **Chunked**: Shot exceeds VRAM ceiling or has natural cut/beat points | • **Shot-tight**: Identity or lighting drift at shot boundary<br>• **Full-span**: Quadratic attention dilution + 3–6x wall-clock cost<br>• **Chunked**: Blend ghosting at overlap frames | Measure subject motion continuity and VRAM/step wall time at $T_1$ vs $T_2$ | **High** on compute ($O(T^2)$) and long-range consistency |
| **`d3`: Conditioning & Prompt Specificity** | • **Minimal identity anchor + motion**<br>• **Dense beat-by-beat choreography**<br>• **Hybrid: Reference image lock + sparse temporal cues** | • **Minimal**: Reference latents already carry appearance; extra text tokens fight the visual prior<br>• **Dense**: Unconstrained trajectory requires explicit temporal verb staging<br>• **Hybrid**: Appearance is locked by ref, action needs timing anchors | • **Minimal**: Unintended action or mouth/gesture hallucination<br>• **Dense**: Token overload causes prompt bleeding or rigid pose lock<br>• **Hybrid**: Ref/text conflict if prompt re-describes altered clothing | Compare cross-attention token entropy or inspect what the encoder actually received on a 1-seed probe | **High** on action adherence vs. visual naturalness |
| **`d4`: Numerical / Kernel Approximation** | • **Stock dense FP16/BF16**<br>• **Sparse / quantized attention (e.g., Sol / Sage)** | • **Dense**: Baseline reference or micro-benchmark where any approximation error confounds attribution<br>• **Sparse/Quant**: Attention map is sparse enough that speed gain ($1.5\text{–}2.5\times$) causes negligible activation drift | • **Dense**: Slow iteration throughput<br>• **Sparse/Quant**: Tail-block errors degrade fine texture or temporal stability | Grade cosine similarity / relative $L_2$ error on captured DiT activations against dense baseline | **Low-to-Medium** on output if activation cosine $> 0.995$; **High** on throughput |

---

## Template 2: Software Architecture, Distributed Systems & Performance Engineering

Use when designing storage schemas, caching tiers, consistency models, retry/backpressure policies, or API boundaries.

### Layer 1: Verifiable Hygiene (Apply Automatically)
- Idempotency keys on mutating endpoints, bounded timeouts, connection pool cleanup, and deterministic unit/property test coverage.
- Schema migration backward compatibility and zero secret/credential leakage.

### Layer 2: Contrastive Judgment & Sensitivity Matrix

| Axis ($d_k$) | Option Spectrum ($N$-Way / Continuous / Hybrid) | Level-2 Worldview (When Each Option Is Structurally Right) | Failure Mode if Worldview Is Wrong | Discriminating Diagnostic (Observable Check Before Deciding) | Leverage / Sensitivity ($\Delta$) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **`d1`: State Consistency vs. Latency** | • **Strict serializable / sync write**<br>• **Read-your-writes session consistency**<br>• **Eventual async projection** | • **Strict**: Stale reads cause financial/invariant corruption that cannot be reconciled post-hoc<br>• **Session**: Users only notice staleness on their own mutations<br>• **Eventual**: High write bursts dominate and downstream consumers tolerate $100\text{–}500\text{ms}$ lag | • **Strict**: Cross-AZ lock contention spikes $p_{99}$ latency under burst<br>• **Session**: Cross-user race conditions remain possible<br>• **Eventual**: Phantom UI state / duplicate user retries | Measure write-conflict rate and read-after-write interval distribution in production traces | **High** on $p_{99}$ tail latency and invariant safety |
| **`d2`: Failure Backpressure Policy** | • **Fail-fast (`HTTP 429/503`)**<br>• **Bounded queue + jittered backoff**<br>• **Graceful degraded fallback (stale cache)** | • **Fail-fast**: Caller has better context to retry or shed load; queueing causes retry storms<br>• **Bounded queue**: Traffic spikes are short micro-bursts ($<2\text{s}$)<br>• **Degraded**: Serving slightly stale data is strictly better than an error screen | • **Fail-fast**: User-visible error spike during brief dependency blips<br>• **Bounded queue**: Queue saturation increases memory & tail latency<br>• **Degraded**: Silent serving of invalidated permissions/prices | Inspect burst duration histogram (`p50` vs `p99` spike width) in traffic logs | **High** on availability during dependency brownouts |

---

## Template 3: Empirical Data Science, Causal Inference & Econometrics

Use when analyzing observational or experimental datasets, defining metrics, choosing estimators, or evaluating policy/business thresholds.

### Layer 1: Verifiable Hygiene (Apply Automatically)
- Join key cardinality verification, duplicate row detection, cluster-robust variance aligned with the unit of treatment assignment, and explicit post-treatment variable screening.

### Layer 2: Contrastive Judgment & Sensitivity Matrix

| Axis ($d_k$) | Option Spectrum ($N$-Way / Continuous / Hybrid) | Level-2 Worldview (When Each Option Is Structurally Right) | Failure Mode if Worldview Is Wrong | Discriminating Diagnostic (Observable Check Before Deciding) | Leverage / Sensitivity ($\Delta$) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **`d1`: Outcome Denominator** | • **Physical / baseline capacity unit**<br>• **Total operating / induced spend**<br>• **Joint Pareto frontier (both)** | • **Physical**: Spend responds endogenously to treatment (post-treatment collider/mediator)<br>• **Spend-normalized**: Decision mandate is net ROI per dollar spent<br>• **Joint**: Report physical gain and cost shift separately before combining | • **Physical**: Ignores severe cost overruns<br>• **Spend-normalized**: Confounds output gains with induced input purchases | Regress denominator (spend) on treatment indicator to test if denominator is post-treatment responsive | **High** (Often shifts estimate by $2\text{–}4\text{pp}$ or flips sign) |
| **`d2`: Identification Strategy** | • **Two-way Fixed Effects / DiD**<br>• **Baseline-lagged ANCOVA / Matching**<br>• **Doubly-Robust AIPW** | • **DiD**: Selection is driven by persistent time-invariant level differences across units<br>• **ANCOVA**: Selection is driven by transitory pre-treatment shocks (Ashenfelter's dip) or serial correlation is low<br>• **AIPW**: Both propensity and outcome response depend on rich baseline covariates | • **DiD**: Credits mean reversion from temporary pre-treatment dip to the treatment<br>• **ANCOVA**: Biased if permanent unobserved unit levels drive trends | Plot multi-period pre-treatment event study (`t-3, t-2, t-1`) and test autocorrelation $\rho$ of outcome | **Very High** (Frequently the #1 variance driver across specs) |
| **`d3`: Target Estimand & Weighting** | • **Unweighted ATT (treated units)**<br>• **Size/volume-weighted ATT**<br>• **Population ATE (reweighted to full target)** | • **Unweighted ATT**: Evaluates average entity-level program governance on actual participants<br>• **Volume-weighted**: Evaluates aggregate macro output across the sector<br>• **Population ATE**: Decision is whether to mandate universal rollout to non-participants | • **Unweighted**: Dominated by numerous tiny units<br>• **Volume-weighted**: Driven by top 5% mega-units<br>• **ATE**: Extrapolates over thin common support if participants are atypical | Check covariate overlap (propensity score distribution) between treated and untreated + treatment heterogeneity by size | **Medium-to-High** depending on treatment effect heterogeneity |

---

## Template 4: Product Strategy, Evaluation Benchmarks & Policy Design

Use when designing LLM/system benchmarks, pricing/packaging tiers, rollout gates, or organizational policies.

### Layer 1: Verifiable Hygiene (Apply Automatically)
- Train/eval contamination checks, stratified sample balance, confidence intervals on benchmark scores, and fixed prompt/judge templates across compared arms.

### Layer 2: Contrastive Judgment & Sensitivity Matrix

| Axis ($d_k$) | Option Spectrum ($N$-Way / Continuous / Hybrid) | Level-2 Worldview (When Each Option Is Structurally Right) | Failure Mode if Worldview Is Wrong | Discriminating Diagnostic (Observable Check Before Deciding) | Leverage / Sensitivity ($\Delta$) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **`d1`: Aggregation Rule Across Tasks** | • **Macro-average (equal per category)**<br>• **Micro-average (traffic-weighted)**<br>• **Worst-slice floor ($\min_c \text{score}_c$)** | • **Macro**: Capability breadth across rare and common tasks matters equally<br>• **Micro**: Expected daily user experience in production is what ships<br>• **Worst-slice**: Safety/reliability SLA is governed by the weakest critical slice | • **Macro**: Overweights tiny synthetic edge categories<br>• **Micro**: Hides catastrophic regressions in 5% high-stakes slices<br>• **Worst-slice**: Blocks major mean gains over noisy small slices | Compute slice-level score dispersion and check if candidate models trade off head vs. tail slices | **High** when models have inverse head/tail profiles |
| **`d2`: Judge / Grading Strictness** | • **Exact / deterministic verifier**<br>• **Rubric LLM-as-judge (lenient equivalence)**<br>• **Pairwise human-calibrated Elo** | • **Deterministic**: Output format/code execution is part of the contract<br>• **Rubric**: Semantic correctness matters across varied phrasing<br>• **Pairwise**: Relative user preference matters more than absolute rubric checklists | • **Deterministic**: Penalizes valid alternative formulations as `0`<br>• **Rubric**: Verbosity and self-preference bias inflate scores<br>• **Pairwise**: Transitivity cycles and style over substance | Audit 20 disagreement cases where deterministic verifier and rubric judge diverge | **High** on ranking between concise vs. verbose models |
