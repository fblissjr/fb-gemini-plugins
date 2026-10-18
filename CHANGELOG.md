# Changelog

All notable changes to `fb-gemini-plugins` are documented in this file.

## [0.26.0] - 2026-10-18

### Added

- **`sparring-partner` (`v0.1.0` — Live In-Character Roleplay & Flight Simulator)**:
  - Added [`skills/sparring-partner/`](skills/sparring-partner/) as an orthogonal companion to `hypothetical-diff` for **Google Antigravity** and **Gemini Spark**: whereas `hypothetical-diff` previews a 3rd-person Before/After delta upfront, `sparring-partner` runs a **1st-person, turn-by-turn live simulation under Fog of War**.
  - **The Sealed Envelope (Zero-Spoiler Hidden State)**: At Turn 0, silently locks the counterparty's secret walk-away/BATNA, unspoken political or personal fear, Red-Button Triggers (`Trust -2`), Green-Key Unlocks (`Trust +2`), and live `Trust (5/10)` / `Patience (5/5)` meters—preventing sycophantic AI cave-ins and holding all hidden cards until the debrief.
  - **5 Difficulty Levels (`L1 Warm-Up` $\leftrightarrow$ `L5 Kobayashi Maru`) & Live Ring Controls**: Supports any user-set tone or persona with mid-round controls (`"Time-out / Coach"`, `"Rewind Turn X"`, `"Swap Seats"`, `"Dial up to L4"`, `"Debrief"`).
  - **Flight-Recorder Debrief & References**: Unseals the Hidden Counterparty Card, prints a turn-by-turn `Trust`/`Patience` flight recorder, highlights what was left on the table, and renders an **Instant Replay Diff** (`--- What You Said` vs. `+++ The Unlock Line`). Ships with [`references/counterparty-archetypes.md`](skills/sparring-partner/skills/sparring-partner/references/counterparty-archetypes.md) (12 blueprints) and [`references/hidden-state-and-debrief.md`](skills/sparring-partner/skills/sparring-partner/references/hidden-state-and-debrief.md).

## [0.25.0] - 2026-10-18

### Added

- **`hypothetical-diff` (`v0.3.0` — Multi-Granularity Simulation Engine)**:
  - Added the **4-Axis Granularity Space ($\mathcal{G} = \langle \text{Scale}, \text{Time}, \text{Fidelity}, \text{Lens} \rangle$)** and the **5-Level Structural Zoom Ladder (`L0` Atomic/Sub-second $\leftrightarrow$ `L4` Macro/Era)** so any scenario, dialogue, habit, policy, strategy, or system can be simulated and zoomed continuously across resolutions.
  - Added [`references/simulation-engine.md`](skills/hypothetical-diff/skills/hypothetical-diff/references/simulation-engine.md) with four multi-granularity simulation archetypes:
    1. **Telescoping Zoom Diff (`L3 Macro` $\rightarrow$ `L2 Meso` $\rightarrow$ `L0 Micro`)**: Links 1-to-5-year goals directly down to Tuesday 07:15 AM micro-cues and enforces the **Cross-Scale Conservation Law** (detecting *"Macro Ambition / Micro Starvation"* mismatches).
    2. **Turn-by-Turn Rally State Machines (`Turn 1` $\rightarrow$ `Turn 2` $\rightarrow$ `Turn 3`)**: Simulates multi-turn negotiations, sales objections, interviews, and difficult conversations comparing the *Default Derailment Path (`-`)* vs. *Calibrated Steering Path (`+`)* with spoken lines, subtext, and emotional temperature deltas ($\Delta \text{Temp}$).
    3. **Multi-Horizon Temporal Compounding & Inversion Diffs (`+10m | +2wk | +6mo | +3yr`)**: Exposes sign flips between short-term relief traps and long-term compounding choices.
    4. **Monte Carlo Branching Envelopes & Curveball Perturbations (`Base Case 60% | Upside 20% | Murphy's Law Tail-Risk 20% + Pre-Emptive Hedge`)**: Replaces single-line projections with probability envelopes and minimum-cost pre-emptive hedges.
  - Added **Multi-Perspective Simultaneous Lens Diffing** (*Proposer*, *Skeptical Counterparty*, *Silent Bystander*, *Future-You*) and the **Interactive Simulation Controller** (`Zoom In`, `Zoom Out`, `Step +1 Turn/Yr`, `Curveball`, `Shift Tone/Lens`, `Mix & Match Hunks`).

## [0.24.0] - 2026-10-18

### Changed

- **`path-privacy` (`v0.22.0`, wrapper template `t5`)**:
  - **Unified Dual-Manifest Plugin Tree**: Added `.claude-plugin/plugin.json` (`v0.22.0`) and `hooks/hooks.json` alongside Antigravity's root `plugin.json` and `hooks.json` so the entire `skills/path-privacy/` directory is 100% byte-for-byte identical across `fb-gemini-plugins` and Claude Code plugin repositories.
  - **Cross-Harness Version Resolution in Git Hooks (`t5`)**: Updated `install-git-hooks.sh` (`WRAPPER_TEMPLATE_VERSION=5`) so generated `.git/hooks/pre-commit` and `.git/hooks/commit-msg` wrappers score all readable candidate scripts across both Antigravity (`~/.gemini/config/plugins/...`, `~/.gemini/antigravity-cli/plugins/...`) and Claude Code (`~/.claude/plugins/cache/...`) by `(wrapper_template_version, plugin_semver, is_frozen)` and execute the newest installed copy on the machine.
  - **Cross-Harness Drift Diagnostics (`--doctor` & `SessionStart`)**: `install-git-hooks.sh --doctor` now checks dual-manifest version parity and compares installed Antigravity and Claude Code plugin copies on disk, flagging lagging caches with the exact sync command; `path-privacy-session-start.sh` now names the lagging harness when hooks are ahead of the running plugin.
  - **Peer & Cache Synchronizer (`scripts/sync-peer.sh`)**: Added `sync-peer.sh` (`--check`, `--apply --peer <dir>`, `--install`) to verify and synchronize peer repository checkouts and local `~/.gemini` / `~/.claude` installed plugin caches in a single step.

## [0.23.0] - 2026-10-17

### Changed

- **`hypothetical-diff` (`v0.2.0`)**:
  - Added **`simulate` mode** (6 operational modes total: `search`, `align`, `decide`, `diagnose`, `ensemble`, `simulate`) and the **Universal Tone, Voice & Persona Engine**, allowing any scenario, rewrite, dialogue, or counterfactual to be simulated in any user-specified tone (e.g., warm therapist, brutal VC partner, calm senior peer, Socratic tutor, Hemingway minimalist, deadpan roast) while preserving `--- Before` / `+++ After` structural rigor and conservation laws.
  - Expanded everyday **non-coding domains and playbooks** (`references/domain-playbooks.md` and `SKILL.md` to 12 playbooks):
    - **Difficult Conversations, Negotiation & Relationships**: Spoken/written script + unspoken subtext + simulated counterparty reaction diffs.
    - **Learning, Research & Unlearning**: Intuitive Misconception $\rightarrow$ Expert Mental Model diffs with real-world **Prediction Flips**.
    - **Creative Writing, Storytelling & Speeches**: Show-Don't-Tell sensory diffs, narrative beat diffs, and Multi-Tone Dial ensembles.
    - **Habits, Personal Life, Health & Travel Itineraries**: Environment friction diffs, Low-Energy Tuesday fallbacks, and strict Time/Budget/Physical Energy conservation.
    - **Policy, Economics, History & Society**: 1st-, 2nd- (Goodhart/Loophole adaptation), and 3rd-Order Equilibrium Ripple Diffs ($\hat{\Delta}^{(1)} \rightarrow \hat{\Delta}^{(2)} \rightarrow \hat{\Delta}^{(3)}$).
  - Added **Interactive Hunk Staging ("Mix-and-Match Menu")**: Pairs numbered semantic hunks (`[Hunk 1]`, `[Hunk 2]`, ...) with `ask_question` (`is_multi_select: true`) in Antigravity and 1-line Mix-and-Match Ballots (`A1 + B2`) in Gemini Spark.
  - Expanded `references/hyde-theory-and-patterns.md` with formal sections on Higher-Order Ripple Diffs, Orthogonal Tone & Persona Projection ($\hat{\Delta}_{\text{tone}}$), and Interactive Hunk Algebra.

## [0.22.0] - 2026-10-17

### Changed

- **Antigravity App, CLI & Marketplace Alignment**:
  - Removed duplicate `.agents/skills/` symlinks so `.agents/plugins.json` serves as the single workspace discovery source without registering skills twice in the system prompt.
  - Added 128x128 square SVG icons (`assets/logo.svg` + `"logo": "assets/logo.svg"` in `plugin.json`) for both `hypothetical-diff` (`v0.1.1`) and `path-privacy` (`v0.21.0`) for Antigravity App and Marketplace cards.
  - Expanded `GEMINI.md` with complete, live-verified specifications for Antigravity plugins (`plugin.json`), lifecycle hooks (`hooks.json`), skills (`SKILL.md`), MCP servers and connectors (`mcp_config.json` with `serverUrl`, ADC/OAuth, and eager tools), rules (`rules/AGENTS.md` and `rules/*.md` frontmatter triggers), custom subagents (`agents/<name>.md`), and managed sidecars (`sidecars/<name>/sidecar.json`).
- **`path-privacy` (`v0.21.0`, wrapper template `t4`)**:
  - Updated `install-git-hooks.sh` (`WRAPPER_TEMPLATE_VERSION=4`) so generated `.git/hooks/` wrappers also resolve fallback scripts from `~/.gemini/antigravity-cli/plugins/` and Marketplace hash-named plugin directories (`~/.gemini/config/plugins/*/`).
  - Added `GIT_CONFIG_GLOBAL=/dev/null` fallback across `path-privacy` scripts and hooks when `git` commands run inside the Antigravity Terminal Sandbox and encounter an unreadable `[include]` file in `~/.gitconfig` (such as `~/.gitconfig.local`).
  - Updated `_name_guard.sh` (`pp_name_regex`) to check repo, global, and `--no-includes ~/.gitconfig` `user.name` values so setting a one-word handle in `.git/config` does not disable full-name protection when `~/.gitconfig` holds a multi-word full name.

## [0.21.0] - 2026-10-17

### Added

- **`hypothetical-diff` (`v0.1.0`)**:
  - Added universal **Hypothetical Diff (HyDiff)** plugin and skill (`skills/hypothetical-diff/`) inspired by **HyDE** (*Hypothetical Document Embeddings*, Gao et al., ACL 2023), generalized from static documents ($\hat{d}$) to state transitions ($\hat{\Delta} = \text{After} - \text{Before}$) across any domain (writing, contracts/policy, strategy, calendars/operations, spreadsheets/finance, research/debugging, and code).
  - Designed for dual-platform compatibility across **Google Antigravity** (`agy` CLI & App via `plugin.json` and progressive disclosure) and **Gemini Spark** (self-contained `SKILL.md` with line-1 YAML frontmatter for single-file upload/paste in `Customize > Skills`, Canvas, or ZIP bundle upload).
  - Defined five operational modes (`search`, `align`, `decide`, `diagnose`, `ensemble`), universal domain diff notations, the **Conservation Law of Finite Systems** ($\sum \Delta = 0$), and reference playbooks (`references/domain-playbooks.md` and `references/hyde-theory-and-patterns.md`).

## [0.20.0] - 2026-10-17

### Added

- **Repository Initialization (`fb-gemini-plugins`)**:
  - Configured repository structure for Google Antigravity CLI (`v1.4.0+`) and Antigravity App (`v2.24.0+`).
  - Added `GEMINI.md` (and `AGENTS.md` symlink) with Antigravity plugin conventions and path-privacy rules.
- **`path-privacy` (`v0.20.0`)**:
  - Ported and adapted `path-privacy` (`v0.19.0` from `fb-claude-skills`) as a native Antigravity plugin (`skills/path-privacy/plugin.json` + root `skills/path-privacy/hooks.json`).
  - **Dual-harness `PreToolUse` hook (`hooks/path-privacy-pre-tool-use.sh`)**:
    - Supports Antigravity tools (`write_to_file`, `replace_file_content`, `multi_replace_file_content`, `run_command`) alongside Claude Code tools (`Write`, `Edit`, `Bash`).
    - Auto-rewrites in-repo absolute paths to repo-relative paths across `CodeContent`, `ReplacementContent`, and `ReplacementChunks` via Antigravity's `overwrite` response field.
    - Explicitly exempts Antigravity conversation artifact and scratch files (`artifactDirectoryPath` and `/.gemini/antigravity*/brain/`).
    - Hard-blocks (`{"decision": "deny"}`) external paths (`/Users/<user>/...`, `/home/<user>/...`, `~/...`) and the git `user.name` full name.
  - **Dual-harness `SessionStart` hook (`hooks/path-privacy-session-start.sh`)**:
    - Auto-detects Antigravity `workspacePaths`/`conversationId` input, stays silent (`{}`) when git hooks are current, automatically refreshes stale git hook wrappers, and emits `injectSteps` system notices when hooks are missing, refreshed, stale, or ahead.
  - **Git hook installer (`scripts/install-git-hooks.sh`)**:
    - Bumped `WRAPPER_TEMPLATE_VERSION=3` to resolve scripts from `~/.gemini/config/plugins/path-privacy`, local `fb-gemini-plugins` or `fb-claude-skills` checkouts, or `~/.claude/plugins/cache`.
  - Validated with `agy plugin validate skills/path-privacy --strict --json` (0 findings, 1 skill, 1 hook).
