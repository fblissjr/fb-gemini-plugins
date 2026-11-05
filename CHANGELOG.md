# Changelog

<!-- path-privacy: skip-file -->

All notable changes to `fb-gemini-plugins` are documented in this file.

## [0.33.0] - 2026-11-05

### Added

- **`omni-flash-prompting` (`v0.1.0` — Structured Prompting, Storyboard Choreography & Deterministic Linter/Compiler for Gemini Omni 1.2 Flash)**:
  - Added [`skills/omni-flash-prompting/`](skills/omni-flash-prompting/) for **Google Antigravity**, **Claude Code**, **Gemini CLI**, and **Gemini Spark**, targeting **Google Gemini Omni 1.2 Flash (`gemini-omni-1.2-flash`)** on the Gemini Interactions API.
  - **5 Operational Modes (`SKILL.md`)**:
    1. `generate`: Assembles the **6-Layer Cinematic Spec** for native `3s–15s` video generation (`1s` increments, +50% ceiling over 1.1)—covering single-shot continuity locks vs. multi-shot rhythms, subject/costume/packaging micro-detail, `[0-5s] / [5-10s] / [10-15s]` timecode beat choreography, continuous FPV/orbital camera trajectories, `"quoted"` on-screen typography, and inline audio/negative guardrails.
    2. `edit`: Enforces the **Minimal Delta + Anchor Rule** (`[Imperative Target Modification] + "Keep everything else the same."`) to eliminate over-description drift, paired with the **Audio Stream Gate** (preserving existing audio vs. mandatory `ffmpeg -an` audio stripping to force full soundtrack regeneration).
    3. `extend`: Crafts `3s–10s` per-turn horizon extensions (up to `30s–40s` total using the final `10s` as context) with the **Prompt-Only Extension Unlock** (omitting `task="extend"` so `<IMAGE_REF_0..5>` and `<VIDEO_REF_0..2>` can inject new characters and motion into extended timelines) and relative `0s` timecode alignment.
    4. `multiturn`: Choreographs the **720p Stateful Draft (\$0.07/s, -30% vs. 1.1) $\rightarrow$ Conversational `previous_interaction_id` Refine $\rightarrow$ 1080p/4K `URI` Upscale Loop**, including multi-turn voice/dialogue extension rules.
    5. `lint`: Audits draft prompts and configs against 12 Gemini Omni 1.2 Flash failure modes (`R01`–`R12`).
  - **Progressive-Disclosure Reference Suite (`references/`)**: Ships [`prompt-architecture-and-tags.md`](skills/omni-flash-prompting/skills/omni-flash-prompting/references/prompt-architecture-and-tags.md), [`editing-extension-and-multiturn.md`](skills/omni-flash-prompting/skills/omni-flash-prompting/references/editing-extension-and-multiturn.md), and [`domain-prompt-playbooks.md`](skills/omni-flash-prompting/skills/omni-flash-prompting/references/domain-prompt-playbooks.md) (8 production playbooks).
  - **Zero-Dependency Stdlib CLI (`scripts/omni_prompt.py`)**: Provides `compile` (role-tagged prompt + `google-genai` Interactions API Python snippet), `lint` (12-rule validator), `cost` (draft-to-upscale budget & 30% savings calculator), and `--self-test`.

## [0.32.2] - 2026-11-05

### Changed

- **`heylook-provider` (`v0.23.2` $\rightarrow$ `v0.23.3`, verified against `heylookitsanllm 2.0.242`)**:
  - Updated [`embeddings.md`](skills/heylook-provider/skills/heylook-provider/references/embeddings.md): documented `engine.embedding.video_windows` (`{max_seconds, sampling, default_sampling}`) and `engine.embedding.limits` (`{items, blocks_per_item, text_chars, media_bytes: {image, audio, video}, request_media_bytes}`), MLX windowed video embeddings (`windows: {seconds?, sampling?: "content"|"fps"}` on a video block and `data[].windows: [{start, end, frame_times, embedding}]`), and the `256 MiB` video block and total request media limits.
  - Updated [`wire_reference.md`](skills/heylook-provider/skills/heylook-provider/references/wire_reference.md): updated `sampler_defaults` on `/v1/models` to the flat map shape (`enable_thinking` matching `thinking_default`), set `engine.image` to `null` in the discovery example, and noted that interleaved `text` and `image` blocks in a user message preserve their order on both engines.
  - Updated [`older_servers.md`](skills/heylook-provider/skills/heylook-provider/references/older_servers.md) and [`routes.md`](skills/heylook-provider/skills/heylook-provider/references/routes.md): added version boundaries for `2.0.33` (`sampler_defaults` flattening), `2.0.207` (interleaved MLX user-turn images), and `2.0.233`/`2.0.236`/`2.0.238` (windowed video embeddings, `256 MiB` video cap, and `engine.embedding.limits`), plus `POST /v1/admin/models/{id}/reload[?warm=true]` load-setting body notes.
- **Antigravity Marketplace & CLI/App Installation Docs (`README.md`, `GEMINI.md`, and `skills/*/README.md`)**:
  - Updated installation and plugin management instructions across [`README.md`](README.md), [`GEMINI.md`](GEMINI.md), and all plugin `README.md` files to match the latest [Google Antigravity Marketplace documentation](https://antigravity.google/docs/marketplace/), covering shell `agy plugin` commands (`install`, `list [--json]`, `enable`, `disable`, `uninstall`, `validate --strict`, and `@antigravity-plugins-official`), interactive TUI `/plugin` (alias `/plugins`) **Installed** / **Discover** tabs and inline `/plugin` slash commands, and Antigravity App **Customizations $\rightarrow$ Marketplace / Installed** workflows with automatic cross-surface synchronization.

## [0.32.1] - 2026-11-04

### Changed

- **`heylook-provider` (`v0.23.1` $\rightarrow$ `v0.23.2`, verified against `heylookitsanllm 2.0.224`)**:
  - Updated [`routes.md`](skills/heylook-provider/skills/heylook-provider/references/routes.md): `POST /v1/conversations/{id}/generate/reasoning-end` now answers `{"signalled": 1, "conversation_id"}`, matching the request route's shape.
  - Updated [`wire_reference.md`](skills/heylook-provider/skills/heylook-provider/references/wire_reference.md): clarified that the streamed "omitted, never null" rule covers `performance`'s own top-level keys only, while nested `cache` and `speculative` carry `null` in both modes for fields that do not apply.
- **`README.md` & `GEMINI.md`**: Condensed the repository catalog, installation commands, and validation instructions; removed duplicate version copies in `skills/heylook-provider/README.md` and `GEMINI.md` so `plugin.json` and `SKILL.md` (`metadata.verified_against`) remain the single sources of truth.
- **Cross-Vendor `SKILL.md` & Manifest Schema Alignment**: Trimmed `SKILL.md` frontmatter `description` fields in `epistemic-fork` and `hypothetical-diff` under the 1,024-character Agent Skills spec cap, removed angle brackets and added explicit `Use when...` triggers in `video-understanding`, and trimmed `plugin.json` descriptions in `epistemic-fork` and `hypothetical-diff` under the 500-character limit so all 7 skills pass `skill-maintain validate --all --strict --verbose` with zero errors and zero warnings.

## [0.32.0] - 2026-11-04

### Added

- **`heylook-provider` (`v0.23.1` — Local Apple Silicon Multimodal LLM Server Integration & Capability Probe, verified against `heylookitsanllm 2.0.223`)**:
  - Ported [`skills/heylook-provider/`](skills/heylook-provider/) from `fb-claude-skills` for **Google Antigravity**, **Gemini CLI**, **Gemini Spark**, and **Claude Code**.
  - **Core `/v1/messages` & Single-User Local Server Contract (`SKILL.md`)**: Covers runtime model discovery against install-local model IDs (`/v1/models` and `/v1/capabilities`), capability and `engine` fact gating (`context.length`, `thinking.depth.values`, `decoding.request_fields`), handling late streaming refusals (`event: error` with `invalid_request_error`), client-side image downscaling and `/v1/models/{id}/image-plan`, optional `max_tokens` cascade semantics, `503` + `Retry-After` queue backpressure, pre-warming via `POST /v1/models/{id}/load`, per-request `X-Request-ID` cancellation (`DELETE /v1/requests/{id}`) and early thinking termination (`POST /v1/requests/{id}/reasoning-end`), and `generation_duration_ms` throughput telemetry.
  - **Progressive-Disclosure Reference Suite (`references/`)**: Ships [`wire_reference.md`](skills/heylook-provider/skills/heylook-provider/references/wire_reference.md), [`older_servers.md`](skills/heylook-provider/skills/heylook-provider/references/older_servers.md), [`openai_wire.md`](skills/heylook-provider/skills/heylook-provider/references/openai_wire.md), [`embeddings.md`](skills/heylook-provider/skills/heylook-provider/references/embeddings.md) (`POST /v1/embeddings`), [`routes.md`](skills/heylook-provider/skills/heylook-provider/references/routes.md) (including the `/v1/conversations` store and `/v1/presets`), [`gemini_migration.md`](skills/heylook-provider/skills/heylook-provider/references/gemini_migration.md) (field-by-field mapping and 5 provider-abstraction seams alongside Gemini `generateContent`), and [`client_recipes.md`](skills/heylook-provider/skills/heylook-provider/references/client_recipes.md) (verified Python/TypeScript streaming clients and Pillow/sharp resize recipes).
  - **Zero-Dependency Capability Probe CLI (`scripts/probe.py`) & Test Suite (`tests/`)**: Resolves served models, providers, context lengths, thinking-depth vocabularies, and capabilities from a live server (`--base`, `--need`, `--json`, `--api-key`), backed by 43 unit tests in `tests/test_probe.py` and `tests/test_image_recipe.py`.

## [0.31.0] - 2026-10-28

### Added

- **`epistemic-fork` (`v0.1.0` — Specification & Judgment Matrix Engine based on Herdağdelen, Joren, & Tamkin 2026)**:
  - Added [`skills/epistemic-fork/`](skills/epistemic-fork/) for **Google Antigravity**, **Claude Code**, and **Gemini Spark**, operationalizing the empirical findings of *"Who's Aligned to Whom? How AI Agents Shape Experts' Research Judgment Calls"* across ML/video pipelines, software architecture, empirical data science, and strategy—with **zero hidden background automation**.
  - **4 Explicit User-Controlled Modes**:
    1. `matrix`: Partitions tasks into **Layer 1 (Verifiable Hygiene)** vs. **Layer 2 (Underdetermined Judgment Axes $d_1 \dots d_k$)** and renders the **6-Column Contrastive Judgment & Sensitivity Matrix** supporting $N$-way, continuous, and hybrid options alongside **Level-2 structural worldviews**, **failure modes**, **discriminating observable diagnostics**, and **marginal leverage ($\Delta$)**.
    2. `sweep`: Parameterizes upstream forks and decomposes **Marginal Fork Leverage ($\Delta_j$)**, single-factor variance share ($R^2_j$), and decision-band crossings (`ABOVE_BAND`, `BELOW_BAND`, `INSIDE_BAND`, `STRADDLES_BAND`).
    3. `lock`: Enforces a **Zero-Advocacy Execution Lock** when the user declares a specification—preserving the agent's 55%-to-6% objective procedural bug reduction while blocking unsolicited prior pushback, "sensitivity check" demotions, and competing baseline anchoring.
    4. `audit`: Runs a strict **Two-Pass Audit** separating **Pass 1 (`[HYGIENE AUDIT]`)** objective bugs from **Pass 2 (`[ANTIPODAL & PROVENANCE AUDIT]`)** silent defaults (`AI_SILENT_DEFAULT`), the steelmanned **Antipodal Configuration ($\overline{L}$)**, and an in-chat **Decision Provenance Map**.
  - **Bundled Zero-Dependency CLI (`scripts/spec_matrix.py`)**: Includes `sweep` (Cartesian/fractional grid generator and marginal leverage / $R^2$ decomposition), `scan-defaults` (AST + regex scanner for hardcoded thresholds, weights, filters, estimators, and signature defaults), `lint-neutrality` (detector for asymmetric first-person advocacy or sensitivity-check demotion), and `--self-test`.

## [0.30.0] - 2026-10-28

### Added

- **`video-understanding` (`v0.1.0` — Progressive-Disclosure Video, Image & Audio Understanding Router + CLI Toolkit)**:
  - Added [`skills/video-understanding/`](skills/video-understanding/) for **Google Antigravity**, **Claude Code**, and **Gemini Spark** with a strict **Rule 0 Native-First Gate** (`$0` API spend via `read_file` on `.1fps` frame-held companions, `<100 MB` clips, and local image crops first; escalating to `gemini-api` only for capabilities the harness cannot perform natively).
  - **Self-Contained CLI Helper (`scripts/gemini_media.py`)**:
    1. `encode-1fps`: Encodes any video (or `[--first..--last]` frame span) into `<80 MB` `<stem>.1fps.<first:05d>-<last:05d>.mp4` companions (`-r 1`, muted, optional `--burn-frame-numbers`) for deterministic `1:1` frame alignment in `read_file` at `$0` API spend.
    2. `crop`: Crops pixel (`--box x1,y1,x2,y2`) or normalized `0..1000` (`--box-1000 ymin,xmin,ymax,xmax`) image regions to a local PNG for `$0` native `read_file` inspection.
    3. `boxes`: Runs `0..1000` `box_2d` (`[ymin, xmin, ymax, xmax]`) and polygon `mask` (`[[x, y], ...]`) grounding, descaling to exact pixel coordinates (`box_xyxy_px` and `box_ltwh_px`) on the image's canvas and optionally matching against local `.json` or bit-packed `.npz` detections (`--match-boxes`, `IoU >= 0.50`).
    4. `slice`: Runs server-side `[first..last]` frame-span slicing (`start_offset` / `end_offset` in seconds) at native FPS (auto-probed via `ffprobe` or `--fps`) in high-resolution static mode.
    5. `agentic-video`: Runs opt-in `"processing": "agentic"` timeline navigation on `>100 MB` single-canvas videos or mixed `agentic` + `static` (`--compare-clip`) continuity queries while mechanically refusing multi-panel (`*_STACKED*` / `.1fps.`) strips.
    6. `zoom`: Runs Agentic Vision (`tools: [{"type": "code_execution"}]` + `"resolution": "ultra_high"`) on dense contact sheets and diagnostic grids.
    7. `transcribe-spans`: Runs audio or multimodal (`--visual-speakers`) speaker transcription and converts `MM:SS.mmm` timestamps into inclusive `[start_frame, end_frame]` spans.
    8. `--self-test`: Deterministic offline unit and `--dry-run` payload validation suite.

## [0.29.0] - 2026-10-28

### Changed

- **`sparring-partner` (`v0.1.2`) and `council-of-rivals` (`v0.1.2`)**: Removed remaining cross-vocabulary and residual phrasing from `hypothetical-diff` across `SKILL.md`, `references/`, and plugin `README.md` files (replacing `Instant Replay Diff` / `diff` blocks in `sparring-partner` with native `Pivotal Turn Replay (What You Said -> The Unlock Line)`, replacing `conserved trade-off` / `L3`/`L0` zoom-ladder terminology with native negotiation terms, and tightening the opening and closing sections of `council-of-rivals`). Synced version strings in `README.md` and `GEMINI.md`.

## [0.28.0] - 2026-10-19

### Changed

- **`council-of-rivals` (`v0.1.1`) and `sparring-partner` (`v0.1.1`)**: Decoupled skills from each other. Removed all cross-skill links, handoff controls, "suite loop" sections, and comparison tables from `SKILL.md`, references, and plugin READMEs; each skill is now fully standalone and can be chained by the user via progressive disclosure. `hypothetical-diff` (`v0.3.0`) required no changes.
- **`GEMINI.md` / `AGENTS.md`**: Added a "Skill Independence" rule forbidding direct cross-skill entanglement unless the user explicitly requests it.
- **`README.md`**: Reframed the "Simulation & Decision Suite" section as independent plugins.

## [0.27.0] - 2026-10-18

### Added

- **`council-of-rivals` (`v0.1.0` — Adversarial Multi-Persona Collision Arena & Double-Crux Extractor)**:
  - Added [`skills/council-of-rivals/`](skills/council-of-rivals/) for **Google Antigravity** and **Gemini Spark** as the third orthogonal pillar of the simulation & reasoning suite alongside `hypothetical-diff` (3rd-person state-transition blueprint) and `sparring-partner` (1st-person 1-on-1 flight simulator).
  - **Incompatible-Incentive Casting & Direct Cross-Examination**: Casts 3–5 conflicting minds with mutually exclusive objective functions and zero-tolerance boundaries in any user-set tone, forbids lukewarm consensus, and forces rivals to quote and attack each other's load-bearing premises in Round 2.
  - **Double-Crux Extraction ($\mathcal{C}$) & Subagent Fan-Out**: Distills every collision into an **Uncontested Bedrock**, explicit **"If/Then Flip Conditions"** (separating Empirical Cruxes from Value Cruxes), and a **24-Hour Decisive Test**; supports parallel isolated subagent fan-out (`invoke_subagent`) in Antigravity and ships with [`references/rival-panels-and-archetypes.md`](skills/council-of-rivals/skills/council-of-rivals/references/rival-panels-and-archetypes.md) (12 domain panels) and [`references/crux-extraction-and-protocols.md`](skills/council-of-rivals/skills/council-of-rivals/references/crux-extraction-and-protocols.md).

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
