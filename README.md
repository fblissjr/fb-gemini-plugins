# fb-gemini-plugins

<!-- path-privacy: skip-file -->

Native plugins, skills, and hooks for **Google Antigravity** (`agy` CLI v1.4.0+ and Antigravity App v2.24.0+) and **Gemini Spark** (including Gemini web/desktop `Customize > Skills` and Gemini Enterprise).

## Plugin & Skill Catalog

| Plugin / Skill | Version | Platforms | Components | Description |
|----------------|---------|-----------|------------|-------------|
| **[council-of-rivals](skills/council-of-rivals/)** | `0.1.2` | Antigravity, Gemini Spark | Skill (`council-of-rivals`), References (`rival-panels-and-archetypes.md`, `crux-extraction-and-protocols.md`), Icon (`assets/logo.svg`) | **Adversarial multi-persona collision arena & Double-Crux extractor**: casts 3–5 conflicting minds with incompatible incentives to cross-examine your idea and each other in any user-set tone, isolating the exact **Crux Map ($\mathcal{C}$)** and decisive test. |
| **[epistemic-fork](skills/epistemic-fork/)** | `0.1.0` | Antigravity, Claude Code, Gemini Spark | Skill (`epistemic-fork`), References (`domain-templates.md`, `paper-mechanisms.md`), CLI (`scripts/spec_matrix.py`), Icon (`assets/logo.svg`) | **Specification & Judgment Matrix engine (Herdağdelen, Joren, & Tamkin 2026)**: separates **Layer 1 (Verifiable Hygiene)** from **Layer 2 (Underdetermined Judgment Axes $d_1 \dots d_k$)** across 4 explicit modes (`matrix`, `sweep`, `lock`, `audit`)—rendering the **6-Column Contrastive Judgment & Sensitivity Matrix** ($N$-way/continuous options, Level-2 structural worldviews, failure modes, discriminating observable checks, and marginal leverage $\Delta$), decomposing multiverse variance via `scripts/spec_matrix.py`, enforcing zero-advocacy execution lock, and running two-pass hygiene + antipodal ($\overline{L}$) audits. |
| **[hypothetical-diff](skills/hypothetical-diff/)** | `0.3.0` | Antigravity, Gemini Spark | Skill (`hypothetical-diff`), References (`simulation-engine.md`, `domain-playbooks.md`, `hyde-theory-and-patterns.md`), Icon (`assets/logo.svg`) | Generalizes **HyDE** (*Hypothetical Document Embeddings*, Gao et al. 2023) from static documents to universal **Before/After diffs ($\hat{\Delta}$)** across any non-coding or coding domain—simulating anything at any granularity (`L0` atomic micro-choices to `L4` macro eras, turn-by-turn rallies, multi-horizon timelines, and Monte Carlo envelopes) in any user-set tone with interactive zoom and hunk mix-and-match. |
| **[path-privacy](skills/path-privacy/)** | `0.22.0` | Antigravity, Claude Code | Skill (`path-privacy`), Hooks (`SessionStart`, `PreToolUse`), Git Hooks (`pre-commit`, `commit-msg`), Synchronizer (`sync-peer.sh`), Icon (`assets/logo.svg`) | Keeps personal identifiers and external paths out of repository files, commit messages, PR descriptions, and branch names. Auto-rewrites in-repo absolute paths to repo-relative form and hard-blocks external paths and the git `user.name` full name across both Antigravity and Claude Code. |
| **[sparring-partner](skills/sparring-partner/)** | `0.1.2` | Antigravity, Gemini Spark | Skill (`sparring-partner`), References (`counterparty-archetypes.md`, `hidden-state-and-debrief.md`), Icon (`assets/logo.svg`) | Live 1-on-1 **in-character roleplay and conversation flight simulator** across negotiations, difficult personal/workplace talks, interviews, sales objections, and crisis Q&A. Silently locks a **Hidden Counterparty Card** (secret BATNA, unspoken fear, triggers, and `Trust`/`Patience` meters) under Fog of War until the **Flight-Recorder Debrief**. |
| **[video-understanding](skills/video-understanding/)** | `0.1.0` | Antigravity, Claude Code, Gemini Spark | Skill (`video-understanding`), References (`video_static_and_slicing.md`, `video_agentic.md`, `image_boxes_and_masks.md`, `image_agentic_zoom.md`, `audio_and_transcription.md`), CLI (`scripts/gemini_media.py`), Icon (`assets/logo.svg`) | **Progressive-disclosure video, image, and audio understanding router with a strict Native-First Gate**: encodes `<80 MB` `.1fps` frame-held companions (`encode-1fps`) and local image crops (`crop`) for `$0` native `read_file` inspection first, escalating to the Gemini Interactions API only for `>100 MB` master videos, server-side frame-span slicing (`slice`), opt-in agentic timeline navigation (`agentic-video`), `0..1000` 2D box/polygon segmentation grounding (`boxes`), agentic code-execution zoom (`zoom`), and visual speaker transcription (`transcribe-spans`). |

---

## Installation (Antigravity CLI, Antigravity App & Gemini Spark)

Plugins installed into `~/.gemini/config/plugins/` are shared automatically between the **Antigravity CLI (`agy`)** and the **Antigravity App (v2.24.0+)**. Skills in `skills/<name>/skills/<name>/SKILL.md` also conform to the open `SKILL.md` standard for **Gemini Spark**.

### Method 1: Antigravity CLI (`agy`) — Direct from GitHub or Local Checkout

`agy plugin install` supports GitHub URLs directly (both single-plugin URLs and bulk-directory URLs) as well as local directories:

```bash
# Option A: Install a single plugin directly from GitHub (no manual git clone needed)
agy plugin install https://github.com/fblissjr/fb-gemini-plugins/tree/main/skills/council-of-rivals
agy plugin install https://github.com/fblissjr/fb-gemini-plugins/tree/main/skills/epistemic-fork
agy plugin install https://github.com/fblissjr/fb-gemini-plugins/tree/main/skills/hypothetical-diff
agy plugin install https://github.com/fblissjr/fb-gemini-plugins/tree/main/skills/path-privacy
agy plugin install https://github.com/fblissjr/fb-gemini-plugins/tree/main/skills/sparring-partner
agy plugin install https://github.com/fblissjr/fb-gemini-plugins/tree/main/skills/video-understanding

# Option B: Bulk-install ALL plugins in this repo directly from GitHub
agy plugin install https://github.com/fblissjr/fb-gemini-plugins/tree/main/skills

# Option C: Install from a local checkout of fb-gemini-plugins
agy plugin install ./skills/council-of-rivals
agy plugin install ./skills/epistemic-fork
agy plugin install ./skills/hypothetical-diff
agy plugin install ./skills/path-privacy
agy plugin install ./skills/sparring-partner
agy plugin install ./skills/video-understanding

# Verify installed plugins
agy plugin list

# Validate plugin manifests, skills, and hooks against the runtime loader
agy plugin validate ./skills/council-of-rivals --strict
agy plugin validate ./skills/epistemic-fork --strict
agy plugin validate ./skills/hypothetical-diff --strict
agy plugin validate ./skills/path-privacy --strict
agy plugin validate ./skills/sparring-partner --strict
agy plugin validate ./skills/video-understanding --strict
```

### Method 2: Antigravity CLI Interactive TUI (`/plugin`)

1. Start an interactive session with `agy`.
2. Run `/plugin` in the prompt.
3. Switch to the **Discover** tab and select **+ Install from local directory...**.
4. Enter the path to `skills/council-of-rivals`, `skills/hypothetical-diff`, `skills/path-privacy`, or `skills/sparring-partner` in your `fb-gemini-plugins` checkout.

### Method 3: Antigravity App (v2.24.0+)

- Because Antigravity App and `agy` CLI share `~/.gemini/config/plugins/`, running `agy plugin install ./skills/<name>` immediately enables the plugin in the Antigravity App as well.
- When opening the `fb-gemini-plugins` workspace directly in Antigravity App or CLI, `.agents/plugins.json` automatically registers all plugins in `skills/` for the workspace.

### Method 4: Gemini Spark & Gemini App (`Customize > Skills`)

Skills such as **[council-of-rivals](skills/council-of-rivals/)**, **[hypothetical-diff](skills/hypothetical-diff/)**, and **[sparring-partner](skills/sparring-partner/)** are authored with self-contained `SKILL.md` instructions and line-1 YAML frontmatter so they work directly in **Gemini Spark**, **Gemini web/desktop (`Customize > Skills`)**, and **Gemini Enterprise**:

1. **Single-File Upload or Paste (Recommended for Gemini Spark & Canvas)**:
   - Open Gemini Spark / Gemini and navigate to **Customize $\rightarrow$ Skills** (or **Skills** in the left sidebar).
   - Click **+ $\rightarrow$ Upload skill** and select `skills/<name>/skills/<name>/SKILL.md` (or click **Create skill** and paste its contents).
2. **Full Skill Bundle ZIP Upload (Includes `references/`)**:
   ```bash
   (cd skills/council-of-rivals/skills/council-of-rivals && zip -r ../../../../council-of-rivals-skill.zip SKILL.md references/)
   (cd skills/hypothetical-diff/skills/hypothetical-diff && zip -r ../../../../hypothetical-diff-skill.zip SKILL.md references/)
   (cd skills/sparring-partner/skills/sparring-partner && zip -r ../../../../sparring-partner-skill.zip SKILL.md references/)
   ```
   Upload the desired `*-skill.zip` via **Skills $\rightarrow$ + $\rightarrow$ Upload skill**.

### Per-Repository Git Hooks (`pre-commit` & `commit-msg` for `path-privacy`)

The Antigravity `PreToolUse` hook automatically guards agent edits and `git`/`gh` commands in every git workspace. To also guard commits made **outside** Antigravity (e.g., manual `git commit` in your terminal or GUI git clients), install the git commit gates in each repository you work on:

```bash
# Install into the current git repository
bash ~/.gemini/config/plugins/path-privacy/skills/path-privacy/scripts/install-git-hooks.sh

# Or target a specific repository path
bash ~/.gemini/config/plugins/path-privacy/skills/path-privacy/scripts/install-git-hooks.sh -C <repo-path>

# Check git hook health across a single repo or an entire parent directory tree
bash ~/.gemini/config/plugins/path-privacy/skills/path-privacy/scripts/install-git-hooks.sh --doctor
bash ~/.gemini/config/plugins/path-privacy/skills/path-privacy/scripts/install-git-hooks.sh --doctor <parent-dir>
```

---

## Simulation & Decision Plugins (`hypothetical-diff`, `sparring-partner`, `council-of-rivals`)

These three plugins are fully independent: each `SKILL.md` and its references never link to or depend on another skill. They can still be chained by the user in conversation when needed.

| Plugin | POV & Topology | Core Primitive |
|--------|----------------|----------------|
| **[`hypothetical-diff`](skills/hypothetical-diff/)** (`v0.3.0`) | **3rd-Person State-Transition Blueprint** | Synthesizes a concrete `--- Before` / `+++ After` delta ($\hat{\Delta}$) across any domain, tone, and granularity (`L0` atomic micro-choices $\leftrightarrow$ `L4` macro eras), enforcing resource/energy conservation ($\sum \Delta = 0$) and interactive hunk mix-and-match (`A1 + B2`). |
| **[`sparring-partner`](skills/sparring-partner/)** (`v0.1.2`) | **1st-Person 1-on-1 Flight Simulator** | Locks a **Sealed Envelope** (counterparty's secret BATNA, unspoken fear, triggers, unlocks, and live `Trust`/`Patience` meters) under Fog of War, plays strictly one turn at a time in character (`L1`–`L5`), and delivers a **Flight-Recorder Debrief** at the end. |
| **[`council-of-rivals`](skills/council-of-rivals/)** (`v0.1.2`) | **Multi-Agent Collision Arena** | Casts 3–5 conflicting minds with incompatible incentives, forces direct cross-examination between rivals (with optional parallel subagent fan-out in Antigravity), and extracts the **Double-Crux Map ($\mathcal{C}$)** and 24-hour decisive test. |

### How `hypothetical-diff` (`v0.3.0`) Works
Inspired by **HyDE** (*Hypothetical Document Embeddings*, Gao et al., ACL 2023), `hypothetical-diff` operates across six modes (**`search`**, **`align`**, **`decide`**, **`diagnose`**, **`ensemble`**, and **`simulate`**) and a **5-Level Structural Zoom Ladder (`L0`–`L4`)**:
- **Telescoping Zoom Diffs (`L3` $\rightarrow$ `L0`)**: Connects a 1-to-5-year strategy or habit goal directly down to Tuesday at 07:15 AM (`L0`), catching *"Macro Ambition / Micro Starvation"* mismatches.
- **Turn-by-Turn Rally & Subtext Diffs**: Diffs spoken scripts, unspoken subtext, and counterparty reactions across multi-turn conversations in any user-set tone.
- **Mental Model & Ripple Diffs**: Diffs *Intuitive Misconception (`-`) $\rightarrow$ Expert Mechanism (`+`)* with a **Real-World Prediction Flip**, or traces **1st / 2nd (Goodhart) / 3rd-Order Ripple Diffs** and **Monte Carlo Branching Envelopes**.
- See [skills/hypothetical-diff/README.md](skills/hypothetical-diff/README.md), [simulation-engine.md](skills/hypothetical-diff/skills/hypothetical-diff/references/simulation-engine.md), [domain-playbooks.md](skills/hypothetical-diff/skills/hypothetical-diff/references/domain-playbooks.md), and [hyde-theory-and-patterns.md](skills/hypothetical-diff/skills/hypothetical-diff/references/hyde-theory-and-patterns.md).

### How `sparring-partner` (`v0.1.2`) Works
- **No Sycophantic Cave-Ins**: The counterparty never folds to a generic ask; concessions require hitting **Green-Key Unlocks** (e.g., tactical empathy labeling, calibrated `"How/What"` questions, or conditional `"Yes, If"` trade-offs).
- **Live Ring Controls**: Call `"Time-out"` for a Corner Coach whisper, `"Rewind Turn X"` to re-shoot a turn, `"Swap Seats"` to watch the AI handle your hardest objection, or `"Debrief"` to unseal the Hidden Counterparty Card and view the **Pivotal Turn Replay**.
- See [skills/sparring-partner/README.md](skills/sparring-partner/README.md), [counterparty-archetypes.md](skills/sparring-partner/skills/sparring-partner/references/counterparty-archetypes.md), and [hidden-state-and-debrief.md](skills/sparring-partner/skills/sparring-partner/references/hidden-state-and-debrief.md).

### How `council-of-rivals` (`v0.1.2`) Works
- **3-Round Collision (`Indict` $\rightarrow$ `Cross-Examine` $\rightarrow$ `Crux Map`)**: Rivals attack each other's load-bearing assumptions directly and state the exact empirical threshold or value trade-off where they would flip sides.
- See [skills/council-of-rivals/README.md](skills/council-of-rivals/README.md), [rival-panels-and-archetypes.md](skills/council-of-rivals/skills/council-of-rivals/references/rival-panels-and-archetypes.md), and [crux-extraction-and-protocols.md](skills/council-of-rivals/skills/council-of-rivals/references/crux-extraction-and-protocols.md).

---

## What `path-privacy` Does (with Examples)

`path-privacy` enforces two core rules across every tracked file, commit message, PR description, and branch name:
1. **Every path written into the repo must be relative to the repo root** (no `/Users/<user>/...`, `/home/<user>/...`, `~/...`, or `$HOME/...` resolving outside the repo, and no unbracketed placeholder usernames like `/home/user/xyz` or `/Users/dev/xyz`).
2. **The git `user.name` full name is never written** (`LICENSE` files and `Signed-off-by:` trailers excepted; use the GitHub handle `fblissjr` or `<author>` instead).

### Example 1: Silent In-Repo Path Auto-Rewrite (`PreToolUse` `overwrite`)

When the agent calls `write_to_file`, `replace_file_content`, or `multi_replace_file_content` in Antigravity App or `agy` CLI and accidentally writes an absolute or `~/` path pointing **inside** the current repository, `path-privacy` rewrites the tool arguments in place before the file is touched:

- **Agent attempts (`write_to_file` on `README.md`)**:
  ```markdown
  See the configuration in `<repo-root>/skills/path-privacy/plugin.json`.
  ```
- **Hook response (`overwrite`)**:
  ```json
  {
    "decision": "allow",
    "reason": "path-privacy: rewrote 1 absolute in-repo path(s) in README.md to repo-relative form; they now resolve against the repo root. The correction is routine: commit messages, branch names and changelog entries do not mention it.",
    "overwrite": {
      "CodeContent": "See the configuration in `skills/path-privacy/plugin.json`."
    }
  }
  ```
- **Result in Antigravity App / CLI**: The file lands on disk with the clean repo-relative path `skills/path-privacy/plugin.json` without interrupting your workflow or requiring a retry.

### Example 2: Blocking an External Path or Unbracketed `/home/user/...` (`PreToolUse` `deny`)

If the agent tries to write a path that resolves **outside** the repository—including sibling repos, `~/...` directories, or unbracketed placeholder paths like `/home/user/xyz`:

- **Agent attempts (`replace_file_content` on `README.md`)**:
  ```markdown
  Copied helper from `/home/user/secret-project/utils.sh`.
  ```
- **Hook response (`deny`)**:
  ```text
  path-privacy: blocked -- README.md would gain a path outside the repo:
    README.md:1: /home/user/secret-project/utils.sh
  Write it repo-relative, or say it generically ("another project", <HOME>/...).
  For a file that is ABOUT such paths: 'path-privacy: ignore' on the line, or '<!-- path-privacy: skip-file -->' leading a line in the first 30.
  The correction is routine: commit messages, branch names and changelog entries do not mention it.
  ```
- **Result in Antigravity App / CLI**: The edit is blocked before touching disk, and the agent immediately self-corrects to a repo-relative reference, `<HOME>/...`, `/Users/<user>/...`, or a generic phrase.

### Example 3: Blocking Leaks in `git commit` or `gh pr create` (`run_command`)

When the agent runs `git commit`, `git tag`, `git checkout -b`, or `gh pr create` via `run_command`:

- **Agent attempts (`run_command`)**:
  ```bash
  git commit -m "Ported from ~/other-private-repo"
  ```
- **Hook response (`deny`)**:
  ```text
  path-privacy: blocked -- an external path in a commit/PR message or branch name:
    message line 1: ~/other-private-repo
  Use a repo-relative path or say it generically ("another project").
  The correction is routine: commit messages, branch names and changelog entries do not mention it.
  ```

### Example 4: Exempting Antigravity Conversation Artifacts & Scratch Files

During an active session in Antigravity App or CLI, the agent frequently writes implementation plans, walkthroughs, and scratch scripts to your conversation artifact directory (`artifactDirectoryPath` / `/.gemini/antigravity-cli/brain/<conversation-id>/`), where Antigravity requires absolute `file://` links and embedded media paths.
- `path-privacy-pre-tool-use.sh` automatically detects and allows writes to `artifactDirectoryPath` and gitignored files while still enforcing full protection on all tracked repository files.

### Example 5: Interactive Skill Commands in Antigravity App & CLI

Because `path-privacy` also ships as an Antigravity skill (`skills/path-privacy/skills/path-privacy/SKILL.md`), you can ask the agent in plain English in either the App or CLI:
- *"Scan this repo for path leaks or my full name"*
- *"Are our path-privacy git hooks installed and up to date?"*
- *"Scrub external paths using `.path-privacy.local.json`"*

Or run the scripts directly from the terminal:

```bash
# 1. Scan the working tree for external paths
bash skills/path-privacy/skills/path-privacy/scripts/find-external-paths.sh -d .

# 2. Scan staged files only
bash skills/path-privacy/skills/path-privacy/scripts/find-external-paths.sh --staged

# 3. Preview working-tree path replacements from .path-privacy.local.json (add --apply to write)
bash skills/path-privacy/skills/path-privacy/scripts/scrub-paths.sh -d .
```

See [skills/path-privacy/README.md](skills/path-privacy/README.md) and [patterns.md](skills/path-privacy/skills/path-privacy/references/patterns.md) for the complete rule reference.

---

## Repository Layout

```
fb-gemini-plugins/
├── .agents/
│   └── plugins.json             # Workspace plugin registry
├── skills/
│   ├── council-of-rivals/       # Adversarial multi-persona collision arena & Double-Crux extractor (v0.1.2)
│   ├── hypothetical-diff/       # Multi-granularity (L0-L4) Before/After diff & simulation plugin (v0.3.0)
│   ├── path-privacy/            # Dual-harness Antigravity & Claude Code path/author privacy plugin (v0.22.0)
│   ├── sparring-partner/        # Live 1-on-1 in-character flight simulator with Sealed Envelope debrief (v0.1.2)
│   └── video-understanding/     # Progressive-disclosure video, image & audio router + CLI toolkit (v0.1.0)
├── GEMINI.md                    # Workspace instructions for Antigravity
├── AGENTS.md                    # Symlink to GEMINI.md
├── CHANGELOG.md                 # Release history
├── LICENSE                      # MIT License
└── README.md                    # This file
```

## Development & Validation

Requires Google Antigravity CLI `v1.4.0+` (`agy`), `ripgrep` (`rg`), and `jq`.

```bash
# Validate plugin manifests and components
agy plugin validate skills/council-of-rivals --strict --json
agy plugin validate skills/hypothetical-diff --strict --json
agy plugin validate skills/path-privacy --strict --json
agy plugin validate skills/sparring-partner --strict --json
agy plugin validate skills/video-understanding --strict --json

# Check installed git hooks health
bash skills/path-privacy/skills/path-privacy/scripts/install-git-hooks.sh --doctor

# Run path-privacy scan on the repository
bash skills/path-privacy/skills/path-privacy/scripts/find-external-paths.sh -d .
```

## License

[MIT](LICENSE)
