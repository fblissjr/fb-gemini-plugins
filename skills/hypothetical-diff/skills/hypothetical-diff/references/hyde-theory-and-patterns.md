# From HyDE to Hypothetical Diffs: Theory & Advanced Patterns

This reference explains the theoretical foundation of `hypothetical-diff` and
how it generalizes **HyDE** (*Hypothetical Document Embeddings*, Gao et al., ACL
2023, arXiv:2212.10496) from static document retrieval to universal state
transitions.

---

## 1. The Original HyDE Insight (Gao et al., 2023)

In *"Precise Zero-Shot Dense Retrieval without Relevance Labels"*, Luyu Gao,
Xueguang Ma, Jimmy Lin, and Jamie Callan identified why zero-shot search fails:
- **The Query-Document Asymmetry**: A user's query $q$ is short, abstract, and
  phrased in *intent space* (the language of the question or problem). The
  target document $d^*$ is detailed, structured, and phrased in *artifact space*
  (the language of the answer).
- **The HyDE Pipeline**:
  1. Prompt an instruction-following LLM to generate $K$ hypothetical documents
     $\hat{d}_1, \dots, \hat{d}_K \sim p_{\text{LLM}}(\cdot \mid q)$ that look
     like plausible answers.
  2. Encode the hypothetical documents into a dense representation:
     $$\hat{\mathbf{v}} = \frac{1}{K} \sum_{k=1}^{K} f_{\text{enc}}(\hat{d}_k)$$
  3. Retrieve real documents $d$ from the corpus that maximize inner-product
     similarity with $\hat{\mathbf{v}}$.
- **Why Hallucinations Help Instead of Hurt**: Even though $\hat{d}_k$ contains
  ungrounded or fabricated specifics, it captures the **true structural template,
  register, and co-occurring vocabulary** of $d^*$. The grounding step acts as a
  lossy bottleneck that discards the fabricated details while locking onto the
  real document neighborhood.

---

## 2. Why Generalize from Documents ($\hat{d}$) to Diffs ($\hat{\Delta}$)?

Most real-world agentic work—whether editing an essay, negotiating a contract,
rebalancing a schedule, planning a strategy, debugging a failure, or writing
code—is not about retrieving a static document in isolation. It is about a
**state transition**:

$$\Delta = \text{State}_{\text{after}} - \text{State}_{\text{before}}$$

Projecting a static target document $\hat{d}_{\text{after}}$ alone has three
blind spots that a **Hypothetical Diff ($\hat{\Delta}$)** solves:

| Blind Spot of Static $\hat{d}$ | How Hypothetical Diff ($\hat{\Delta}$) Solves It |
|-------------------------------|--------------------------------------------------|
| **1. Invisible Deletion Cost**: A static target plan or rewrite hides what was removed or sacrificed to make room for the new state. | Every `+` line sits next to the `-` line it replaces, enforcing **resource and scope conservation**. |
| **2. Single-Sided Search Anchors**: Searching only for the *target* state (`+`) misses the *current* state (`-`) that needs to be modified. | $\hat{\Delta}$ provides **two distinct anchor sets**: `-` anchors locate *where the current artifact lives now*, while `+` anchors locate *historical precedents that made similar changes*. |
| **3. High Cognitive Load in Review**: Reviewing a full 2,000-word rewrite or 50-row sheet forces the human to diff it mentally against the original. | Hunk-by-hunk diffs (`@@ ... @@`) isolate the exact 5% of state that changes, letting humans approve, reject, or tweak individual hunks in seconds. |

---

## 3. Asymmetric Anchor Extraction (`-` vs. `+` Signatures)

When using `hypothetical-diff` in **`search`** mode across a codebase, Google
Drive, Docs, Gmail, or research corpus, extract two separate query families from
$\hat{\Delta}$:

1. **Target-Locating Queries (from `--- Before` / `-` lines and context ` ` lines)**:
   - Use these when you want to find **the existing document, clause, row, or
     code that needs to be modified**.
   - Why: The target file does *not* yet contain your proposed `+` change—it
     currently contains the `-` state and surrounding ` ` context!
   - *Rule of thumb*: Strip the specific hallucinated numbers, keep the
     structural headers, boilerplate phrases, config keys, or surrounding
     invariant tokens from the `-` side.

2. **Precedent-Locating Queries (from `+++ After` / `+` lines paired with `-` lines)**:
   - Use these when you want to find **past commits, prior amendments, postmortems,
     or historical threads** that already executed an analogous transition.
   - Why: A precedent record (like a past PR description, changelog, legal
     amendment, or decision memo) typically mentions *both* the old term (`-`)
     and the new term (`+`) in close proximity.

---

## 4. $K$-Diff Ensemble & Variance as an Ambiguity Detector

In the original HyDE paper, generating $K$ samples $\hat{d}_1, \dots, \hat{d}_K$
and averaging them reduces variance from any single hallucination.

In `hypothetical-diff` (**`ensemble`** mode), generating $K = 2\text{–}3$
hypothetical diffs along distinct axes serves as a **zero-shot ambiguity
detector**:
- **Low-Variance (Consensus) Hunks**: Hunks that appear almost identically across
  $\hat{\Delta}_1, \hat{\Delta}_2, \hat{\Delta}_3$ represent the **unambiguous
  core** of the user's request.
- **High-Variance (Divergent) Hunks**: Hunks where $\hat{\Delta}_1$ deletes $X$
  while $\hat{\Delta}_2$ expands $X$ pinpoint the **exact underspecified
  degrees of freedom** in the user's prompt.
- Instead of asking open-ended clarifying questions, show the Consensus Hunks as
  ready-to-apply and present the Divergent Hunks as a crisp A/B choice.

---

## 5. The Conservation Law of Finite Systems

Whenever $\hat{\Delta}$ models a system with a hard capacity constraint $C$
(e.g., 24 hours in a day, 168 hours in a week, a fixed quarterly budget, a
1-page executive summary limit, a fixed team size, or a latency SLA):

$$\sum_{i \in \text{Additions}} \text{Cost}(+_i) - \sum_{j \in \text{Removals}} \text{Cost}(-_j) = \Delta C = 0$$

- **The Anti-Wishful-Thinking Rule**: If a user asks *"What would my week look
  like if I added 8 hours of writing and 4 hours of exercise?"*, never output a
  diff with only `+12h` of additions. The hypothetical diff **must** include
  explicit `-12h` deletions from existing low-leverage blocks so the user can
  evaluate whether they are actually willing to pay the deletion cost.

---

## 6. Anti-Patterns & Failure Modes to Avoid

1. **Mistaking the Projection for Ground Truth**:
   - *Failure*: Presenting `[HYPOTHETICAL]` numbers, file paths, or clause
     numbers as if they were already verified in the user's workspace.
   - *Fix*: Always badge ungrounded diffs with `[HYPOTHETICAL — UNGROUNDED]`
     until the Grounding step completes.
2. **Prose Masquerading as a Diff**:
   - *Failure*: Writing `- Make the email nicer` / `+ Make the email more
     direct` instead of diffing the actual email sentences.
   - *Fix*: Diff the **artifact itself**, not a meta-description of the artifact
     (except in multi-month strategy diffs where the artifact *is* the operating
     model).
3. **Monolithic Wall-of-Red-and-Green**:
   - *Failure*: Replacing a 100-line block with a 100-line block in a single
     hunk (`-100` / `+100`), making it impossible to see what actually changed.
   - *Fix*: Break changes into small, named semantic hunks (`@@ Hunk 1: ... @@`,
     `@@ Hunk 2: ... @@`) with 1–2 lines of unchanged context.
