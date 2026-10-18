# Domain Playbooks for `hypothetical-diff`

Concrete templates and worked examples showing how to project, ground, and
converge **Hypothetical Diffs ($\hat{\Delta}$)** across everyday non-coding,
creative, interpersonal, analytical, and coding domains—in any tone set by the
user. (For multi-granularity `L0`–`L4` zoom ladders, turn-by-turn rallies,
temporal inversion tables, and Monte Carlo branching envelopes, see
[simulation-engine.md](simulation-engine.md).)

---

## 1. Writing, Creative Storytelling & Tone Re-Skinning (`align`, `ensemble`, `simulate`)

**When to use**: The user says *"make this memo more executive"*, *"turn this
scene into show-don't-tell"*, *"rewrite this in the tone of `<X>`"*, *"tighten
this essay"*, or *"fix the pacing of my keynote/Substack post"*.

**Why abstract prose fails**: Asking *"Do you want a formal or conversational
tone?"* yields low-signal answers. Showing numbered hunks on a representative
slice lets the author mix-and-match rhythm, sensory detail, and claim structure
instantly.

### Playbook A: Executive vs. Narrative Hook (`ensemble` mode)

```diff
--- Baseline: Draft Opening Paragraph
+++ Diff A (Executive / Thesis-First — Cuts 35% word count)
@@ Hunk A1: Bottom-Line Up Front @@
- Over the past three quarters, our customer support team has been experimenting
- with several different triage workflows to handle incoming enterprise tickets.
+ Consolidating enterprise support into a single intake channel will cut first-response
+ time by 42% (from 3.8h to 2.2h) without adding headcount.

@@ Hunk A2: Explicit Decision & Deadline @@
- After reviewing the data from Q1 through Q3, we believe there is an opportunity
- to reduce first-response times by consolidating our intake channels.
+ We need sign-off by Friday to retire the legacy email alias on November 1.
```

```diff
--- Baseline: Draft Opening Paragraph
+++ Diff B (Narrative / Stakes-First — Keeps story, sharpens tension)
@@ Hunk B1: Visceral Problem Hook @@
- Over the past three quarters, our customer support team has been experimenting
- with several different triage workflows to handle incoming enterprise tickets.
+ Every enterprise escalation that misses our 4-hour SLA starts the same way: a ticket
+ bounces between three unlinked intake queues before an engineer ever sees it.

@@ Hunk B2: Resolution Arc @@
  After reviewing the data from Q1 through Q3, we believe there is an opportunity
- to reduce first-response times by consolidating our intake channels.
+ to eliminate that blind spot by unifying intake into one routed queue.
```

**Mix & Match Prompt**: *"Pick your combination: `A1 + A2` (pure executive),
`B1 + B2` (narrative), or `B1 + A2` (narrative hook + hard Friday deadline)."*

### Playbook B: Creative Writing — "Show, Don't Tell" & Subtext Diff

```diff
--- Baseline: Exposition-Heavy Draft (Telling the emotion)
+++ Hypothetical: Sensory Action & Subtext (Tone: Raymond Carver / Minimalist)
@@ Hunk 1: Replacing Emotional Labels with Physical Detail @@
- Marcus was furious that Elena had forgotten their anniversary again, but he
- pretended everything was fine so they wouldn't fight at the restaurant.
+ Marcus folded the paper wrapper from his straw into a tight accordion, pressed
+ it flat with his thumb, and asked the waiter if the kitchen was still doing
+ the shared dessert menu. Elena hadn't looked up from her email since the bread arrived.

@@ Hunk 2: Dialogue Subtext (Cutting On-the-Nose Speech) @@
- "You don't care about us anymore," he said quietly.
+ "Keep your phone on the table," he said. "In case Chicago calls back."
```

---

## 2. Difficult Conversations, Negotiation & Relationships (`simulate` & `align`)

**When to use**: Asking for a raise or promotion, saying no to scope creep,
setting boundaries with family or coworkers, resolving co-founder tension,
negotiating rent/salary/contracts, or replying to a tense message.

**Core Principle**: Never output generic advice ("use I-statements and be
firm"). Diff (1) the **exact spoken/written script**, (2) the **unspoken
subtext**, and (3) the **counterparty's simulated reaction**.

### Template: Salary / Role Negotiation Script + Reaction Diff

```diff
--- Baseline: Instinctive Ask (Apologetic & Anchored on Personal Need)
+++ Simulated: Value-Anchored "How Do We Get There" Ask (Tone: Warm, Unshakeable Peer)
@@ Hunk 1: The Opening Framing @@
- I know budgets are super tight right now, and I hate to bring this up, but with my rent going up I was hoping we could talk about a 15% raise.
+ Over the past 8 months, taking ownership of the onboarding overhaul lifted activation by 28% and saved two enterprise renewals. Now that my scope permanently includes leading the growth pod, I'd like to align my compensation with the Senior Lead band at $165k.

@@ Hunk 2: Handling the "Wait Until Next Cycle" Pushback @@
- "Okay, I understand, thanks for checking anyway." (Drops the thread; builds resentment)
+ "I understand off-cycle adjustments take extra sign-off. Can we put a written 60-day milestone plan in place today so that hitting X and Y locks in the $165k adjustment on July 1?"

@@ Hunk 3: Simulated Counterparty Reaction Diff @@
- Reaction to Baseline: Manager feels sympathy but has zero ammunition to take to HR/Finance -> polite deferral.
+ Reaction to Simulated: Manager is handed the exact ROI case they need to copy-paste to Finance, plus a bounded July 1 path if immediate budget is frozen.
```

---

## 3. Learning, Mental Models & Concept Deconstruction (`align` & `diagnose`)

**When to use**: Learning a hard concept in science, economics, medicine,
history, philosophy, law, or statistics; studying for exams; or explaining a
complex topic to a specific audience.

**Why summaries fail**: Summaries append new facts on top of a broken mental
model. A **Mental Model Diff** explicitly deletes the intuitive misconception
(`-`) and replaces it with the structural mechanism (`+`) and a **Prediction
Flip**.

### Template: Misconception $\rightarrow$ Mastery Diff (Example: Antibiotics vs. Viral Infections / Resistance)

```diff
--- Baseline: Folk Intuition (Common Everyday Misconception)
+++ Updated Mental Model: Evolutionary Selection Mechanism
@@ Hunk 1: What Develops Resistance? @@
- "If I take antibiotics too often, MY BODY becomes resistant/immune to the antibiotic."
+ Your body does not become resistant—the BACTERIA population inside you undergoes natural selection. The antibiotic kills 99.9% of susceptible bacteria, leaving behind the 0.1% carrying a random resistance mutation to multiply without competition.

@@ Hunk 2: Stopping Early When You Feel Better @@
- "I feel 100% better on Day 3 of 7, so stopping early saves my gut from unnecessary medicine."
+ On Day 3, only the weakest bacteria are dead; the semi-tolerant bacteria are still alive. Stopping at Day 3 hands the surviving hardest-to-kill strains an open field to rebound.

@@ Hunk 3: Real-World Prediction Flip @@
- Old Prediction: Resistance is a personal tolerance problem (like caffeine tolerance) that resets if I take a break.
+ New Prediction: Resistant strains evolved in one host can spread to other people who have never taken that antibiotic in their life.
```

---

## 4. Habits, Personal Life, Health & Travel Itineraries (`decide` & `simulate`)

**When to use**: Designing a morning/evening routine, fitness or nutrition plan,
household chore split, digital minimalism reset, personal budget, or travel
itinerary.

**Core Principle**: Enforce **Time, Money, and Human Energy Conservation**, plus
**Environment Friction Diffs** and a **Low-Energy Fallback**.

### Template: Travel Itinerary Diff (Conservation: 10h Awake Energy + Budget Cap)

```diff
--- Baseline: Overpacked "Checklist" Day in Kyoto (14h high-output -> 3pm burnout)
+++ Grounded: High-Savoring, Geographic-Clustered Day (Net Energy: Sustainable)
@@ Hunk 1: Morning Block (07:30–12:00) — Crowd & Transit Optimization @@
- [09:30–13:00] Fushimi Inari peak-hour crowds + 55m cross-city bus to Arashiyama + Kinkaku-ji (2.5h in transit/lines)
+ [07:15–11:30] Early quiet walk through Higashiyama -> Kiyomizu-dera -> Sannenzaka coffee stop (Single walkable zone; 0m transit waste)

@@ Hunk 2: Midday Energy Recovery (Conservation of Legs & Attention) @@
- [13:00–15:30] Stand in 45m ramen line + rush through Nishiki Market + 3rd temple
+ [12:00–14:30] Pre-booked sit-down lunch near Gion + 60m afternoon rest/reading at hotel before evening lantern walk

@@ Hunk 3: Rain / Low-Energy Fallback @@
- No backup plan -> miserable 2-hour walk in downpour.
+ If raining or >18,000 steps from yesterday: Swap afternoon walk for covered Teramachi arcades + tea ceremony indoor booking.
```

---

## 5. Policy, Economics, History & Society (`simulate` & `decide`)

**When to use**: Analyzing civic policy, regulations, pricing/market dynamics,
urban planning, or historical *"What if..."* counterfactuals.

**Core Principle**: Static pros/cons miss how intelligent humans adapt to new
rules. Always project a **1st-, 2nd- (Goodhart/Loophole), and 3rd-Order Ripple
Diff**.

### Template: Multi-Order Ripple Diff (Example: Hospital ER 4-Hour Wait-Time Target)

```diff
--- Baseline: Uncapped ER Wait Times
+++ Simulated Policy: Strict 4-Hour Admission-or-Discharge Mandate (+12 Months)
@@ Hunk 1 (1st-Order Direct Effect): Triage & Fast-Track Velocity @@
- Minor lacerations and simple fractures wait 5–7 hours behind complex cases.
+ Dedicated fast-track nurse-practitioner lanes clear minor cases in <90 minutes; average reported wait drops sharply.

@@ Hunk 2 (2nd-Order Goodhart Adaptation / Loophole): The Clock-Start Workaround @@
- Patients are registered into the ER clock immediately upon stepping out of the ambulance.
+ When ER bays hit capacity at Hour 3:50, hospitals delay official "ER check-in" by holding patients in ambulance hallways ("ramping") or creating "Clinical Decision Units" that technically count as inpatient admissions to stop the 4-hour clock.

@@ Hunk 3 (3rd-Order Fix / Equilibrium): Closing the Gaming Loop @@
- Metric tracks only "Door-to-Decision <= 4h".
+ Paired metric tracks "Ambulance Offload Time + Total Clinical Outcome + 7-Day Readmission Rate" so clock-gaming is penalized.
```

---

## 6. Universal Tone & Persona Simulation Showcase (`simulate`)

**When to use**: The user asks to simulate **any** scenario, critique, rewrite,
or counterfactual in a specific tone—whether deadpan, playful, ruthless, poetic,
or roleplay.

**Rule**: Let the user's chosen tone saturate the voice, vocabulary, and energy
of the diff while keeping the `--- Before` / `+++ After` structure razor-sharp.

### Example: Same Career Decision Simulated in 2 User-Set Tones

```diff
--- Baseline: Staying at Comfortable BigCo vs. Joining 6-Person Seed Startup
+++ Simulation A (Tone: Brutally Honest Silicon Valley VC Partner)
@@ Hunk A1: Your Daily Reality at +90 Days @@
- BigCo: You spend 14 hours a week aligning three VPs on whether a button should be blue, collect $280k in RSUs, and slowly forget how to ship.
+ Startup: You are the entire data infrastructure department, the staging server is on fire during your cousin's wedding, and your equity is either a down payment on a house or expensive digital confetti.

@@ Hunk A2: The Real Question You're Avoiding @@
- "Which role has better career progression on paper?"
+ "Do you want to optimize for guaranteed floor (BigCo) or maximum slope and learning rate per month (Startup) while your burn rate is still low?"
```

```diff
--- Baseline: Staying at Comfortable BigCo vs. Joining 6-Person Seed Startup
+++ Simulation B (Tone: Warm, Grounded Executive Coach)
@@ Hunk B1: Energy & Identity Shift at +90 Days @@
- BigCo: Predictable boundaries and psychological safety after 5:30 PM, paired with a quiet sense of under-utilization during the workday.
+ Startup: High agency and visible impact every afternoon, paired with the emotional weight of ambiguous priorities and blurred evening boundaries.

@@ Hunk B2: Designing the Guardrail @@
- Taking the leap blindly and hoping burnout doesn't happen.
+ Taking the startup role with two explicit non-negotiables agreed with the founders upfront: protected Sunday offline time and a 12-month cash runway buffer in personal savings.
```

---

## 7. Legal, Contracts & Policy Redlines (`search` & `align`)

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
   @@ Hunk 1: Data Processing & Model Training @@
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

## 8. Strategy, Product & Org Design (`decide` mode)

**When to use**: Evaluating a strategic pivot, a product roadmap change, or a
hiring trade-off.

### Template: 6-Month World-State Diff

```diff
--- Baseline: Stay on Self-Serve PLG Strategy (Next 6 Months)
+++ Counterfactual: Pivot to Enterprise Sales-Led Motion (+6 Months)
@@ Hunk 1: Roadmap & Engineering Allocation (Conservation: 6 Engineers = Fixed) @@
- [4 Eng] Self-serve onboarding funnel, viral loops, and instant workspace templates
- [2 Eng] Core product velocity & community feature requests
+ [3 Eng] SAML/OIDC SSO, SCIM provisioning, audit logs, and SOC2 Type II controls
+ [2 Eng] Custom deployment / VPC peering & enterprise admin console
+ [1 Eng] Core product velocity (75% reduction in general feature shipping)

@@ Hunk 2: Revenue & Cashflow Dynamics @@
- Monthly predictable self-serve cohorts ($15k–$25k net new ARR/mo, 0-day sales cycle)
+ Lumpy quarterly enterprise bookings ($50k–$150k ACV, 90–180 day procurement/legal cycle)

@@ Hunk 3: Founder / Lead Weekly Calendar (Conservation: 45h/wk = Fixed) @@
- [15h/wk] Product design, user research with individual makers, shipping experiments
+ [15h/wk] Security questionnaires, custom MSA redlines, executive sponsor calls
```

---

## 9. Time, Calendar & Workspace Operations (`decide` & `align`)

**When to use in Gemini Spark / Google Workspace**: Rebalancing a weekly
calendar, turning a cluttered inbox into a task system, reorganizing a Google
Drive folder tree, or restructuring a recurring team meeting.

### Playbook: Approval-First Workspace Diff
Before Gemini Spark or Antigravity modifies a Calendar, Sheet, Doc, or Drive
folder:
1. Synthesize the **Hypothetical Diff** of the schedule, folder hierarchy, or
   tracker with numbered hunks.
2. Verify the **Conservation Constraint** (total weekly hours equal 40h; no
   tracked action item is silently dropped).
3. Present the numbered hunks for interactive selection before executing writes.

---

## 10. Finance, Spreadsheets & Quantitative Models (`decide` & `diagnose`)

**When to use**: Budget re-allocations, pricing changes, personal financial
planning, or investigating why a metric missed forecast.

### Template: Structural Driver & Formula Diff

```diff
--- Baseline: Q4 Marketing Budget ($120,000 / quarter — Fixed Cap)
+++ Hypothetical: Shift 40% of Paid Social into Technical Content & Events
@@ Hunk 1: Budget Allocation (Net Delta: $0) @@
- Row 14 [Paid Social - LinkedIn/X]: $60,000/qtr (CAC = $1,200, 50 SQLs)
+ Row 14 [Paid Social - Retargeting Only]: $20,000/qtr (CAC = $800, 25 SQLs)
+ Row 18 [Technical Benchmarks & Partner Workshops]: $40,000/qtr (Target: 35 SQLs)

@@ Hunk 2: Lag & Risk Structure @@
- Pipeline realization: Immediate (same-month click-to-trial)
+ Pipeline realization: 6–8 week lag (content production -> organic/event conversion)
```

---

## 11. Science, Research & Diagnostic Troubleshooting (`diagnose`)

**When to use**: A system, experiment, health/fitness plateau, business funnel,
or physical process deviated from expectation, and the root cause is unknown.

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

## 12. Software Engineering & Architecture (`search`, `align`, `diagnose`)

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
   - Instead of grepping for `"sanitize"` or `"child_process"`, search for
     co-occurring Before-anchors from the hypothetical diff: `'PATH'`, `'HOME'`,
     `'LANG'` or `ALLOWED_ENV`.
4. **Ground**: Run `grep_search` with those exact tokens, locate the real file
   and line range, and produce the grounded diff.
