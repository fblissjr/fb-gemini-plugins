# Multi-Granularity Simulation Engine (`simulation-engine.md`)

This reference defines the mechanics and worked templates for simulating
**anything at any granularity** ($\mathcal{G} = \langle \text{Scale}, \text{Time}, \text{Fidelity}, \text{Lens} \rangle$)
and in **any user-set tone ($\tau$)**.

---

## 1. The 5-Level Structural Zoom Ladder (`L0` $\leftrightarrow$ `L4`)

Any decision, habit, conversation, policy, creative work, or system can be
inspected through a continuous zoom lens. Below is the **exact same scenario**
(*"Transitioning from overwhelmed reactive work to writing a book / launching an
independent practice"*) simulated across all 5 zoom levels so you can see how
each level exposes a different class of truth:

```diff
--- Baseline: Reactive Status Quo (Across All 5 Zoom Levels)
+++ Simulated: Autonomous Creator / Practitioner Trajectory
@@ Zoom L4 (Macro / 5-Year Era): Identity & Compounding Asset Shift @@
- 2026–2031: 100% of output is rented time inside ephemeral Slack threads; 0 durable public assets at Year 5.
+ 2026–2031: 1 published book + 150 canonical essays + advisory practice generating 60% of income independently.

@@ Zoom L3 (System / 1-Year Equilibrium): Operating Model & Boundary Shift @@
- Say yes to every cross-functional committee and late-afternoon sync; writing happens "whenever I have spare energy" (0.5h/wk actual).
+ Fixed 35h/wk day-job boundary + 7.5h/wk protected morning studio block; drop 2 low-leverage committees to fund the energy budget.

@@ Zoom L2 (Artifact / Weekly Schedule): 40h Calendar Conservation @@
- [Mon–Fri 07:30–09:00] Inbox triage, news scrolling, and reactive Slack before standup (7.5h/wk).
+ [Mon–Fri 07:30–09:00] Offline Studio Block — 500 drafted words/day before opening email or browser (7.5h/wk; Net Time Delta = 0h).

@@ Zoom L1 (Tactical / Single Interaction): Saying No to an 8:30 AM Meeting Invite @@
- "Sure, I can move my morning around to join the 8:30 AM sync."
+ "I'm offline until 9:00 AM daily, but I've added my written input to the doc and can join the 9:30 AM slot or review the recording at 10:00."

@@ Zoom L0 (Micro / Atomic — Tuesday 07:14:50 AM): Physical Cue & 10-Second Friction @@
- Alarm rings on phone -> thumb taps notification banner -> 45m dopamine loop in bed.
+ Phone charges in kitchen overnight; mechanical alarm in bedroom; laptop wakes directly into fullscreen draft with Wi-Fi off until 08:45.
```

### Cross-Scale Consistency Rule (*The Macro-Ambition / Micro-Starvation Check*)
Whenever a user asks for a big goal (`L3`/`L4`), automatically check whether the
`L0`/`L1` micro-diff exists to pay for it. If an `L3` plan promises `+100 pages
written` without an `L0` friction diff and an `L2` calendar deletion, flag the
**Scale Mismatch** immediately.

---

## 2. Turn-by-Turn Rally State Machines (`Turn 1` $\rightarrow$ `Turn 2` $\rightarrow$ `Turn 3`)

When simulating a live human interaction—such as a tough negotiation, a sales
objection, a board grilling, a courtroom cross-examination, a co-founder or
relationship conflict, or a job interview—a static single-turn script isn't
enough because **the magic is in Turn 2 and Turn 3 after the other person pushes
back**.

Render a **Multi-Turn Rally Diff** tracking three state variables at each turn:
1. **Spoken / Written Line**
2. **Unspoken Subtext (How It Lands)**
3. **Emotional / Tactical Temperature ($\Delta \text{Temp}$)**

### Template: 3-Turn High-Stakes Rally Simulation

```diff
--- Path A (Baseline): Default Reactive Rally (Ends in Deadlock / Concession)
+++ Path B (Simulated): Calibrated Steering Rally (Tone: Calm, Unshakeable Peer)
@@ Turn 1: Opening the Price / Scope Conversation @@
- You: "We need to raise our retainer by 25% next quarter because our costs went up."
- [Subtext: "Pay for my internal problem"] -> Client Temp: +2 Defensive
+ You: "Over the last two quarters, we've expanded from core analytics into owning your full attribution pipeline, which lifted ROAS by 31%. For Q3, we can either lock in the expanded Full-Pipeline tier at $15k/mo, or scope back to the core analytics tier at the current $12k/mo."
+ [Subtext: "You control the dial between price and scope"] -> Client Temp: 0 Analytical

@@ Turn 2: Counterparty Pushback ("We want the full scope at the old $12k price") @@
- Client: "Our budget is capped at $12k, and we still need the attribution pipeline."
- You (Default): "Okay, let's keep it at $12k for one more quarter and revisit in Q4." (Unfunded concession; sets precedent that boundaries are bluffs)
+ Client: "Our budget is capped at $12k, and we still need the attribution pipeline."
+ You (Calibrated): "I completely respect the $12k ceiling. To keep the attribution pipeline inside $12k, we can drop the custom weekly slide deck and switch to an automated Monday Looker dashboard. Does that trade-off work for your team?"
+ [Subtext: "Conservation law holds: $12k buys $12k of work"] -> Client Temp: -1 Collaborative

@@ Turn 3: Convergence & Lock-In @@
- Outcome: You do $15k of work for $12k; team burns out by month 2.
+ Client: "Nobody reads the weekly slide deck anyway—keep the pipeline and automate the dashboard at $12k."
+ Outcome: Margin increases while client keeps their highest-value deliverable.
```

---

## 3. Multi-Horizon Temporal Compounding & Inversion Diffs (`+10m` $\rightarrow$ `+5yr`)

Many of the worst human, strategic, and engineering decisions happen because
**the sign of the diff flips across time horizons** ($\Delta_{t_1} > 0$ while
$\Delta_{t_3} \ll 0$, or vice versa).

When simulating a habit, career move, architectural shortcut, policy, or
relationship choice, project a **Multi-Horizon Timeline Diff**:

| Horizon | `--- Option A: Conflict Avoidance / Shortcut` | `+++ Option B: Upfront Truth / Structural Fix` | Sign Flip ($\Delta$) |
|---------|-----------------------------------------------|------------------------------------------------|----------------------|
| **`t = +10 min`** | **+Relief**: Avoids awkward 10-minute conversation; zero immediate friction. | **-Friction**: 10 minutes of elevated heart rate and direct honesty. | Option A wins at `+10m` |
| **`t = +2 weeks`** | **-Carry Cost**: You silently redo their work at 9 PM twice a week (-3h/wk). | **+Calibration**: Expectations are explicit; new checklist catches errors early. | **Inversion Point** |
| **`t = +6 months`** | **-Explosion**: Resentment boils over in a surprise performance review; trust breaks. | **+Compounding**: Team member operates autonomously; you reclaim +75 hours. | Option B wins 10x at `+6mo` |
| **`t = +3 years`** | **-Identity Ceiling**: You remain the bottleneck heroic fixer who cannot scale. | **+Trajectory**: High-trust culture capable of delegating complex ownership. | Option B compounds |

---

## 4. Monte Carlo Branching Envelopes & Curveball Perturbations

Deterministic simulations fail when reality throws a shock. In **`simulate`**
mode, when uncertainty is high, project a **3-Branch Probability Envelope**
paired with a **Pre-Emptive Hedge Hunk**:

```diff
--- Baseline: Single-Point Naive Plan (Assumes 100% Sunny Weather / Happy Path)
+++ Simulated: Monte Carlo Envelope (Base 60% | Upside 20% | Tail-Risk 20% + Hedge)
@@ Hunk 1 [Base Case — 60% Probability]: Expected Execution Trajectory @@
- Assumes launch hits 1,000 signups on Day 1 with 0 support bottlenecks.
+ Launch hits 600–900 signups over Week 1; onboarding completion averages 42%; 35 support tickets/day handled within 4h SLA.

@@ Hunk 2 [Upside Breakout — 20% Probability]: Viral / High-Demand Surge @@
- No capacity plan if post hits #1 on Hacker News / LinkedIn (10x traffic).
+ 8,000+ signups in 24h; self-serve queue saturates API rate limits unless burst quota and waitlist toggle are pre-configured.

@@ Hunk 3 [Tail-Risk / Murphy's Law — 20% Probability]: The Silent Killer @@
- Assumes primary third-party API / key speaker / lead engineer has 0% downtime.
+ Primary upstream provider throttles requests (or lead presenter loses voice 2h before keynote), stalling live demos.

@@ Hunk 4 [Pre-Emptive Hedge — Cost: 45 Minutes Today]: Capping the Tail Risk @@
- Do nothing until an outage happens live.
+ Record a 90-second cached fallback demo video + add a 1-flag circuit breaker to queue jobs asynchronously if upstream latency > 2,000ms.
```

---

## 5. Multi-Perspective Simultaneous Lens Diffing

A change that looks like a pure `+` from your seat often looks like an
unfunded `-` from someone else's seat. Simulate how the **exact same diff**
lands across multiple actors simultaneously:

```diff
--- Proposed Change: Replace Daily 30m Standup with Mandatory Written 5-Bullet EOD Update
+++ Multi-Perspective Impact Simulation (4 Lenses)
@@ Lens 1: IC Engineer / Maker @@
- Loses 30m prime morning focus to status recital.
+ Gains uninterrupted 09:00–12:00 flow block (+2.5h/wk), at the cost of 10m writing at 17:15.

@@ Lens 2: Engineering Manager / Project Lead @@
- Gets instant verbal pulse check at 09:30 AM.
+ Must actually read and react to async updates by 09:00 AM next day—if manager ignores threads, team stops writing them within 10 days.

@@ Lens 3: Junior / New Hire (Hidden Risk) @@
- Has a guaranteed daily low-friction moment to mention being stuck.
+ Might spin wheels silently for 24h out of fear of posting "I'm blocked" in a public channel -> Hedge: Pair with a dedicated #unstuck-in-15m buddy channel.

@@ Lens 4: Cross-Functional Partner / Product Stakeholder @@
- Drops into verbal standup sporadically; no searchable record of when scope slipped.
+ Gets a searchable daily written changelog of shipped items and blockers without attending a meeting.
```

---

## 6. Interactive Simulation Controller Protocol

At the end of any simulation, offer the user live steering controls. When the
user invokes a control command, respond with a **targeted delta on the
simulation itself**:

| Control Command | What the Agent Does Next |
|-----------------|--------------------------|
| **`Zoom In (<Hunk> -> L0/L1)`** | Expands that specific hunk into word-for-word dialogue, sensory detail, exact timestamps, or line-level mechanics. |
| **`Zoom Out (-> L3/L4)`** | Projects how the current tactical diff ripples across 6–12 months (`L3`) or 5–10 years (`L4`). |
| **`Step +1 (<Turn / Horizon>)`** | Advances the simulation clock by one conversational turn or time horizon (`+1wk`, `+6mo`, `+1yr`) based on the chosen path. |
| **`Curveball: <Shock>`** | Injects the user's adversarial event (e.g., *"Counterparty threatens to walk"*, *"Budget cut by 40%"*, *"Flight delayed 6 hours"*) and diffs the recovery path. |
| **`Tone / Lens: <Persona>`** | Re-renders the simulation through the new voice or stakeholder perspective while holding the core scenario fixed. |
| **`Mix & Match: <A1 + B2>`** | Merges the chosen hunks into the converged diff ($\Delta_{\text{real}}$) and verifies that conservation laws still balance. |
