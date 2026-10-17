# Domain Playbooks for `hypothetical-diff`

Concrete templates and worked examples showing how to project, ground, and
converge **Hypothetical Diffs ($\hat{\Delta}$)** across non-coding and coding
domains.

---

## 1. Writing, Editing & Communications (`align` & `ensemble` modes)

**When to use**: The user says *"make this memo more executive"*, *"tighten this
essay"*, *"rewrite our cold outreach"*, or *"adapt this to our brand voice"*.

**Why abstract prose fails**: Asking *"Do you want a formal or conversational
tone?"* yields low-signal answers. Showing a 2-hunk hypothetical diff on the
opening paragraph lets the author react to rhythm, density, and claim structure
instantly.

### Template (`ensemble` mode — 2 Orthogonal Diffs)

```diff
--- Baseline: Draft Opening Paragraph
+++ Hypothetical A (Executive / Thesis-First — Cuts 35% word count)
@@ Paragraph 1: Hook & Ask @@
- Over the past three quarters, our customer support team has been experimenting
- with several different triage workflows to handle incoming enterprise tickets.
- After reviewing the data from Q1 through Q3, we believe there is an opportunity
- to reduce first-response times by consolidating our intake channels.
+ Consolidating enterprise support into a single intake channel will cut first-response
+ time by 42% (from 3.8h to 2.2h) without adding headcount. We need approval by Friday
+ to retire the legacy email alias on November 1.
```

```diff
--- Baseline: Draft Opening Paragraph
+++ Hypothetical B (Narrative / Problem-First — Keeps story, sharpens stakes)
@@ Paragraph 1: Hook & Ask @@
- Over the past three quarters, our customer support team has been experimenting
- with several different triage workflows to handle incoming enterprise tickets.
+ Every enterprise escalation that misses our 4-hour SLA starts the same way: a ticket
+ bounces between three unlinked intake queues before an engineer ever sees it.
  After reviewing the data from Q1 through Q3, we believe there is an opportunity
- to reduce first-response times by consolidating our intake channels.
+ to eliminate that blind spot by unifying intake into one routed queue.
```

**Grounding Question**: *"Do you want the thesis-first compression of Diff A, the
narrative hook of Diff B, or a hybrid (Diff B's first sentence + Diff A's
explicit deadline)?"*

---

## 2. Legal, Contracts & Policy Redlines (`search` & `align` modes)

**When to use**: Reviewing agreements, proposing redlines, updating company
SOPs/handbooks, or searching a Drive/Docs corpus for where a policy obligation
lives.

### Playbook: HyDE Diff-Anchored Policy Search (`search` mode)
1. **User asks**: *"Where in our employee handbook or vendor policies do we
   restrict using customer data for AI training, and how should we tighten it?"*
2. **Project $\hat{\Delta}$**:
   ```diff
   --- Baseline: Assumed Data Usage / Confidentiality Clause [HYPOTHETICAL]
   +++ Target: Explicit Zero-Retention & No-Training Covenant
   @@ Data Processing & Subprocessors @@
     Vendor shall process Customer Data solely to provide the Services.
   - Vendor may use aggregated, de-identified data to improve its products and services.
   + Vendor shall not use Customer Data, Prompts, or Outputs to train, fine-tune, or
   + evaluate any foundation or machine learning models, whether for Vendor or third parties.
   ```
3. **Extract Search Anchors**:
   - **Before-anchors (`-`)**: `"aggregated"`, `"de-identified"`, `"improve its products"`, `"solely to provide the Services"`.
   - **After-anchors (`+`)**: `"train"`, `"fine-tune"`, `"machine learning"`, `"foundation"`.
4. **Ground**: Search Google Drive / Docs / repo with the Before-anchors to find
   the exact clause that currently permits "aggregated/de-identified" service
   improvement, then rewrite the diff against the actual paragraph text.

---

## 3. Strategy, Product & Life/Career Decisions (`decide` mode)

**When to use**: Evaluating a strategic pivot, a product roadmap change, a
hiring trade-off, or a major personal/career decision (e.g., *"Should I take the
Staff IC role or the Engineering Manager role?"*, *"Should we move upmarket to
enterprise or double down on PLG?"*).

**Why pros/cons lists fail**: Pros/cons lists treat benefits as free additions
(`+`) detached from what must be sacrificed (`-`). A **World-State Diff** forces
every new commitment to delete an existing one.

### Template: 6-Month World-State Diff

```diff
--- Baseline: Stay on Self-Serve PLG Strategy (Next 6 Months)
+++ Counterfactual: Pivot to Enterprise Sales-Led Motion (+6 Months)
@@ 1. Roadmap & Engineering Allocation (Conservation: 6 Engineers = Fixed) @@
- [4 Eng] Self-serve onboarding funnel, viral loops, and instant workspace templates
- [2 Eng] Core product velocity & community feature requests
+ [3 Eng] SAML/OIDC SSO, SCIM provisioning, audit logs, and SOC2 Type II controls
+ [2 Eng] Custom deployment / VPC peering & enterprise admin console
+ [1 Eng] Core product velocity (75% reduction in general feature shipping)

@@ 2. Revenue & Cashflow Dynamics @@
- Monthly predictable self-serve cohorts ($15k–$25k net new ARR/mo, 0-day sales cycle)
+ Lumpy quarterly enterprise bookings ($50k–$150k ACV, 90–180 day procurement/legal cycle)

@@ 3. Founder / Lead Weekly Calendar (Conservation: 45h/wk = Fixed) @@
- [15h/wk] Product design, user research with individual makers, shipping experiments
+ [15h/wk] Security questionnaires, custom MSA redlines, executive sponsor calls

@@ 4. Primary Failure Mode @@
- Death by low ARPU / high logo churn if self-serve retention plateaus
+ Death by 9-month enterprise sales cycle stalling cashflow before 3 deals close
```

---

## 4. Time, Calendar & Workspace Operations (`decide` & `align` modes)

**When to use in Gemini Spark / Google Workspace**: Rebalancing a weekly
calendar, turning a cluttered inbox into a task system, reorganizing a Google
Drive folder tree, or restructuring a recurring team meeting.

### Playbook: Approval-First Workspace Diff
Before Gemini Spark modifies a Calendar, Sheet, Doc, or Drive folder:
1. Synthesize the **Hypothetical Diff** of the schedule, folder hierarchy, or
   tracker.
2. Verify the **Conservation Constraint** (e.g., total weekly meeting hours
   cannot exceed the user's cap; no tracked action item is silently dropped).
3. Present the diff and ask for approval before executing the connected-app
   writes.

---

## 5. Finance, Spreadsheets & Quantitative Models (`decide` & `diagnose` modes)

**When to use**: Budget re-allocations, pricing changes, headcount planning, or
investigating why a financial or operational metric missed forecast.

### Template: Structural Driver & Formula Diff

```diff
--- Baseline: Q4 Marketing Budget ($120,000 / quarter — Fixed Cap)
+++ Hypothetical: Shift 40% of Paid Social into Technical Content & Events
@@ Budget Allocation (Net Delta: $0) @@
- Row 14 [Paid Social - LinkedIn/X]: $60,000/qtr (CAC = $1,200, 50 SQLs)
+ Row 14 [Paid Social - Retargeting Only]: $20,000/qtr (CAC = $800, 25 SQLs)
+ Row 18 [Technical Benchmarks & Partner Workshops]: $40,000/qtr (Target: 35 SQLs)

@@ Lag & Risk Structure @@
- Pipeline realization: Immediate (same-month click-to-trial)
+ Pipeline realization: 6–8 week lag (content production -> organic/event conversion)
```

---

## 6. Science, Research & Diagnostic Troubleshooting (`diagnose` mode)

**When to use**: A system, experiment, business funnel, or physical process
deviated from expectation, and the root cause is unknown.

### Playbook: Reverse-Diff Debugging
1. **State the Observed Symptom Diff ($\Delta_{\text{symptom}}$)**:
   ```diff
   --- Expected: Trial-to-Paid Conversion (Weeks 1–8 Baseline)
   +++ Observed: Week 9 Cohort Anomaly
   - Overall conversion: 8.4% (Mobile: 6.1%, Desktop: 9.8%)
   + Overall conversion: 5.1% (Mobile: 1.2%, Desktop: 9.6%)
   ```
2. **Generate $K$ Competing Upstream Causal Diffs ($\hat{\Delta}_{\text{cause}}$)**:
   - **$\hat{\Delta}_1$ (Acquisition Mix Shift)**: Mobile traffic spiked from a
     low-intent campaign while checkout stayed intact.
   - **$\hat{\Delta}_2$ (Mobile Checkout Regression)**: A UI or payment-sheet
     change in Week 9 broke Apple Pay / mobile Safari submission.
3. **Identify the Discriminating Check**:
   - Compare *Mobile Checkout Initiation $\rightarrow$ Payment Submit* rate in
     Week 8 vs. Week 9. If initiation is flat and submit dropped by >70%,
     $\hat{\Delta}_2$ is confirmed and $\hat{\Delta}_1$ is falsified.

---

## 7. Software Engineering & Architecture (`search`, `align`, `diagnose`)

**When to use in Antigravity**: Locating where to implement a feature in an
unfamiliar repo, previewing an architectural refactor, or triaging a bug.

### Playbook: HyDE Diff for Zero-Shot Codebase Search (`search` mode)
1. **User asks**: *"Where do we strip or sanitize environment variables before
   spawning child processes, and how do we allowlist `CUSTOM_TRACE_ID`?"*
2. **Project $\hat{\Delta}$**:
   ```diff
   --- a/src/process/spawn.ts [HYPOTHETICAL]
   +++ b/src/process/spawn.ts [HYPOTHETICAL]
   @@ -20,6 +20,7 @@ const ALLOWED_ENV_KEYS = [
      'PATH',
      'HOME',
      'LANG',
   +  'CUSTOM_TRACE_ID',
    ];
   ```
3. **Extract Search Anchors**:
   - Instead of grepping for `"sanitize"` or `"child_process"` (which may have
     hundreds of hits or zero hits), search for co-occurring Before-anchors from
     the hypothetical diff: `'PATH'`, `'HOME'`, `'LANG'` or `ALLOWED_ENV`.
4. **Ground**: Run `grep_search` with those exact tokens, locate the real file
   and line range, and produce the grounded diff.
