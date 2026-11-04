# fb-gemini-plugins

<!-- path-privacy: skip-file -->

Native plugins, skills, and hooks for **Google Antigravity** (`agy` CLI v1.4.0+ and Antigravity App v2.24.0+), **Gemini CLI**, and **Gemini Spark** (`Customize > Skills` and Gemini Enterprise).

## Plugin & Skill Catalog

| Plugin | Version | Platforms | Description |
|--------|---------|-----------|-------------|
| **[council-of-rivals](skills/council-of-rivals/)** | `0.1.2` | Antigravity, Gemini Spark | Adversarial multi-persona collision arena & Double-Crux extractor: casts 3–5 conflicting minds with incompatible incentives to cross-examine your idea and isolate the **Crux Map ($\mathcal{C}$)** and 24-hour decisive test. |
| **[epistemic-fork](skills/epistemic-fork/)** | `0.1.0` | Antigravity, Claude Code, Gemini Spark | Specification & Judgment Matrix engine (Herdağdelen, Joren, & Tamkin 2026): separates verifiable procedural hygiene from underdetermined judgment axes across 4 modes (`matrix`, `sweep`, `lock`, `audit`) with a stdlib multiverse CLI (`scripts/spec_matrix.py`). |
| **[heylook-provider](skills/heylook-provider/)** | `0.23.2` | Antigravity, Claude Code, Gemini Spark | Local Apple Silicon multimodal LLM server ([`heylookitsanllm`](https://github.com/fblissjr/heylookitsanllm)) integration & capability probe (`scripts/probe.py`): covers the `/v1/messages` wire, `/v1/embeddings`, runtime model discovery, capability gating, client-side image resize, and porting off the removed OpenAI route. |
| **[hypothetical-diff](skills/hypothetical-diff/)** | `0.3.0` | Antigravity, Gemini Spark | Generalizes HyDE (Gao et al. 2023) to universal **Before/After diffs ($\hat{\Delta}$)** across any domain, tone, and granularity (`L0` atomic micro-choices to `L4` macro eras, turn-by-turn rallies, multi-horizon timelines, and Monte Carlo envelopes). |
| **[path-privacy](skills/path-privacy/)** | `0.22.0` | Antigravity, Claude Code | Keeps personal identifiers and external paths out of repo files, commit messages, PR descriptions, and branch names. Auto-rewrites in-repo absolute paths to relative form and blocks external paths and the git `user.name` full name via `PreToolUse` and git hooks. |
| **[sparring-partner](skills/sparring-partner/)** | `0.1.2` | Antigravity, Gemini Spark | Live 1-on-1 in-character roleplay and conversation flight simulator across negotiations, interviews, sales objections, and difficult talks. Locks a **Sealed Envelope** (secret BATNA, triggers, and `Trust`/`Patience` meters) under Fog of War until the debrief. |
| **[video-understanding](skills/video-understanding/)** | `0.1.0` | Antigravity, Claude Code, Gemini Spark | Video, image, and audio understanding router with a strict Native-First Gate (`$0` local `.1fps` frame-hold companions and crops via `scripts/gemini_media.py` first; Gemini Interactions API escalation for `>100 MB` clips, slicing, agentic video, `box_2d`/masks, and transcription). |

## Installation

### 1. Google Antigravity (`agy` CLI & Antigravity App)

Plugins installed into `~/.gemini/config/plugins/` are shared between `agy` CLI and Antigravity App. Opening this repository as a workspace also auto-registers all plugins via `.agents/plugins.json`.

```bash
# Install a single plugin directly from GitHub (replace <plugin> with any name above)
agy plugin install https://github.com/fblissjr/fb-gemini-plugins/tree/main/skills/<plugin>

# Bulk-install all plugins in this repo from GitHub
agy plugin install https://github.com/fblissjr/fb-gemini-plugins/tree/main/skills

# Or install from a local checkout
agy plugin install ./skills/<plugin>
```

### 2. Gemini CLI

```bash
gemini skills install https://github.com/fblissjr/fb-gemini-plugins.git --path skills/<plugin>/skills/<plugin>
```

### 3. Gemini Spark (`Customize > Skills`)

- **Single-file upload**: Upload `skills/<plugin>/skills/<plugin>/SKILL.md` under **Customize $\rightarrow$ Skills**.
- **Full bundle ZIP (with `references/` and `scripts/`)**:
  ```bash
  (cd skills/<plugin>/skills/<plugin> && zip -r ../../../../<plugin>-skill.zip SKILL.md references/ scripts/)
  ```

### 4. Per-Repository Git Hooks (`path-privacy`)

To enforce `path-privacy` on terminal/GUI commits made outside the agent harness:

```bash
bash ~/.gemini/config/plugins/path-privacy/skills/path-privacy/scripts/install-git-hooks.sh -C <repo-path>
bash ~/.gemini/config/plugins/path-privacy/skills/path-privacy/scripts/install-git-hooks.sh --doctor
```

## Development & Validation

```bash
# Validate all plugin manifests, skills, and hooks
for p in skills/*; do agy plugin validate "$p" --strict; done

# Check git hook installation health & scan working tree for path/name leaks
bash skills/path-privacy/skills/path-privacy/scripts/install-git-hooks.sh --doctor
bash skills/path-privacy/skills/path-privacy/scripts/find-external-paths.sh -d .
```

## License

[MIT](LICENSE)
