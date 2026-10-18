# Double-Crux Theory & Collision Protocols (`crux-extraction-and-protocols.md`)

This reference explains the decision-theoretic mechanics behind
`council-of-rivals`: why multi-agent adversarial collision outperforms single-voice
reasoning, how **Double-Crux Extraction** works, and how to run isolated
subagent panels in Google Antigravity.

---

## 1. The Double-Crux Formalism ($\mathcal{C}$)

In ordinary debates, participants trade surface arguments endlessly without ever
asking whether those arguments are **load-bearing**.

A statement $C$ is a **Double Crux** between Rival $A$ (who believes conclusion
$P$) and Rival $B$ (who believes conclusion $\neg P$) if and only if:

$$P_A(P \mid C \text{ is false}) < 0.5 \quad \text{and} \quad P_B(P \mid C \text{ is true}) > 0.5$$

In plain language:
- **If $C$ turns out to be false**, Rival $A$ is willing to abandon their thesis
  and agree with Rival $B$.
- **If $C$ turns out to be true**, Rival $B$ is willing to drop their objection
  and agree with Rival $A$.

### Two Types of Cruxes

1. **Empirical / Threshold Crux ($\mathcal{C}_{\text{empirical}}$)**:
   - The rivals actually agree on the goal, but disagree on a measurable fact or
     number about reality.
   - *Example*:
     - **Rival 1 (Pivot to Enterprise)** vs. **Rival 2 (Stay Self-Serve PLG)**.
     - **Double Crux**: *"Can our current product pass an enterprise InfoSec
       review in $\le 30$ days without custom VPC engineering?"*
     - **Decisive Test**: Send the security questionnaire packet to 3 warm
       design-partner CISOs this week and measure blocker count.
2. **Value / Objective-Function Crux ($\mathcal{C}_{\text{value}}$)**:
   - The rivals agree on all the facts, including the probabilities, but have
     different weights on the outcome (e.g., *Max Slope / Variance* vs. *Zero
     Downside / Predictable Evenings*).
   - When the crux is a **Value Crux**, no external data test can settle it—the
     council's job is to strip away the fake factual arguments and present the
     pure value choice cleanly to the user.

---

## 2. Anti-Sycophancy & Collision Laws

To prevent the council from collapsing into polite, homogenized LLM prose,
enforce these four rules in every session:

1. **Zero-Fluff Indictments**: Rivals never open with *"That's an interesting
   perspective."* They open directly with the structural vulnerability they see.
2. **Named Direct Rebuttals in Round 2**: Every Round-2 statement must address
   another rival by name (`Seat 2 -> Seat 1`) and attack a specific assumption
   that rival just made.
3. **Forced Quantified Thresholds**: Whenever a rival says *"X is too risky"* or
   *"Y will take too long"*, force them in Round 3 to state the **exact number**
   at which they would change their mind (e.g., *"If churn stays under 2.5%/mo,
   I withdraw my objection"*).
4. **Tone Fidelity Without Losing Rigor**: If the user sets a playful, dramatic,
   or ruthless tone (e.g., *Deadpan Roast*, *Succession Boardroom*, *Socratic
   Dialogue*, *Supreme Court Bench*), let the dialogue crackle with that voice
   in Rounds 1 and 2 while keeping the Round 3 **Crux Map** crystal-clear and
   actionable.

---

## 3. Parallel Subagent Fan-Out in Google Antigravity (`invoke_subagent`)

When running in **Google Antigravity** on a complex codebase, research question,
or multi-document strategy where the user wants a **Deep Council**:

1. **Independent Briefs**: Use `invoke_subagent` to launch 3 parallel `research`
   (or `self`) subagents in a single tool call—assigning each subagent one
   Rival Seat, its strict optimization function, and instructions to gather the
   strongest evidence from the workspace supporting its indictment.
2. **Zero Context Contamination**: Because each subagent investigates
   independently in its own context window, Rival 2 is not anchored or softened
   by Rival 1's framing.
3. **Collision & Crux Synthesis**: Once the 3 subagents return their briefs, the
   main agent runs Round 2 (Cross-Examination Clash) and Round 3 (Double-Crux
   Map) directly over their competing evidence.

---

## 4. The Complete 3-Plugin Reasoning Suite Loop

`council-of-rivals`, [`hypothetical-diff`](../../../hypothetical-diff/skills/hypothetical-diff/SKILL.md),
and [`sparring-partner`](../../../sparring-partner/skills/sparring-partner/SKILL.md)
can be chained in any order:

```text
[1. council-of-rivals]  Collide 3–5 opposing minds -> Extract the Double Crux (C)
          │
          ▼
[2. hypothetical-diff]  Project the Crux-winning strategy as a concrete Before/After Diff (Δ̂)
          │
          ▼
[3. sparring-partner]   Step into the ring 1-on-1 against the toughest dissenting stakeholder
                        to practice defending the plan under live pressure
```
