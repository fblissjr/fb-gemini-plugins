# fb-gemini-plugins

<!-- path-privacy: skip-file -->

Native plugins, skills, and hooks for **Google Antigravity** (`agy` CLI v1.4.0+ and Antigravity App v2.24.0+), **Gemini CLI**, and **Gemini Spark** (`Customize > Skills` and Gemini Enterprise).

## Plugin & Skill Catalog

| Plugin | Version | Platforms | Description |
|--------|---------|-----------|-------------|
| **[council-of-rivals](skills/council-of-rivals/)** | `0.1.2` | Antigravity, Gemini Spark | Adversarial multi-persona collision arena & Double-Crux extractor: casts 3–5 conflicting minds with incompatible incentives to cross-examine your idea and isolate the **Crux Map ($\mathcal{C}$)** and 24-hour decisive test. |
| **[epistemic-fork](skills/epistemic-fork/)** | `0.1.0` | Antigravity, Claude Code, Gemini Spark | Specification & Judgment Matrix engine (Herdağdelen, Joren, & Tamkin 2026): separates verifiable procedural hygiene from underdetermined judgment axes across 4 modes (`matrix`, `sweep`, `lock`, `audit`) with a stdlib multiverse CLI (`scripts/spec_matrix.py`). |
| **[heylook-provider](skills/heylook-provider/)** | `0.23.3` | Antigravity, Claude Code, Gemini Spark | Local Apple Silicon multimodal LLM server ([`heylookitsanllm`](https://github.com/fblissjr/heylookitsanllm)) integration & capability probe (`scripts/probe.py`): covers the `/v1/messages` wire, `/v1/embeddings`, runtime model discovery, capability gating, client-side image resize, and porting off the removed OpenAI route. |
| **[hypothetical-diff](skills/hypothetical-diff/)** | `0.3.0` | Antigravity, Gemini Spark | Generalizes HyDE (Gao et al. 2023) to universal **Before/After diffs ($\hat{\Delta}$)** across any domain, tone, and granularity (`L0` atomic micro-choices to `L4` macro eras, turn-by-turn rallies, multi-horizon timelines, and Monte Carlo envelopes). |
| **[omni-flash-prompting](skills/omni-flash-prompting/)** | `0.1.0` | Antigravity, Claude Code, Gemini Spark | Structured prompting, storyboard choreography, and 12-rule prompt linter/compiler (`scripts/omni_prompt.py`) for **Gemini Omni 1.2 Flash (`gemini-omni-1.2-flash`)** across 3s–15s generation, Minimal Delta + Anchor editing, up to 6 image + 3 video references, extensions, and 720p-to-4K draft-to-upscale loops. |
| **[path-privacy](skills/path-privacy/)** | `0.22.0` | Antigravity, Claude Code | Keeps personal identifiers and external paths out of repo files, commit messages, PR descriptions, and branch names. Auto-rewrites in-repo absolute paths to relative form and blocks external paths and the git `user.name` full name via `PreToolUse` and git hooks. |
| **[sparring-partner](skills/sparring-partner/)** | `0.1.2` | Antigravity, Gemini Spark | Live 1-on-1 in-character roleplay and conversation flight simulator across negotiations, interviews, sales objections, and difficult talks. Locks a **Sealed Envelope** (secret BATNA, triggers, and `Trust`/`Patience` meters) under Fog of War until the debrief. |
| **[swift-lsp](skills/swift-lsp/)** | `0.1.1` | Antigravity, Claude Code, Gemini Spark | SourceKit-LSP (`xcrun sourcekit-lsp`) MCP bridge, multi-file `swiftc -dump-ast` sandbox fallback, & Xcode **macOS 27.2+ / iOS 27.2+** `.swiftinterface` inspector (`scripts/sourcekit_mcp.py`): provides symbol-anchored `hover`, `definition`, `references`, `symbols`, sandbox-free dual-platform (`macos` + `ios` simulator) live diagnostics, and direct `.swiftinterface` SDK header lookup. |
| **[video-understanding](skills/video-understanding/)** | `0.1.0` | Antigravity, Claude Code, Gemini Spark | Video, image, and audio understanding router with a strict Native-First Gate (`$0` local `.1fps` frame-hold companions and crops via `scripts/gemini_media.py` first; Gemini Interactions API escalation for `>100 MB` clips, slicing, agentic video, `box_2d`/masks, and transcription). |

## Installation

### 1. Google Antigravity (`agy` CLI & Antigravity App)

Plugins installed in **Antigravity App** and **Antigravity CLI (`agy`)** share `~/.gemini/config/plugins/` and **automatically synchronize across both surfaces** ([Marketplace docs](https://antigravity.google/docs/marketplace/)). Opening this repository as a workspace also auto-registers all plugins via `.agents/plugins.json`.

#### A. From Your Shell (`agy plugin`)

```bash
# Install a single plugin directly from GitHub (replace <plugin> with any name above)
agy plugin install https://github.com/fblissjr/fb-gemini-plugins/tree/main/skills/<plugin>

# Bulk-install all plugins in this repo from GitHub
agy plugin install https://github.com/fblissjr/fb-gemini-plugins/tree/main/skills

# Install from a local checkout
agy plugin install ./skills/<plugin>

# Install an official Marketplace plugin (@antigravity-plugins-official is the default)
agy plugin install <plugin-name>@antigravity-plugins-official

# List, enable, disable, or uninstall plugins
agy plugin list [--json]
agy plugin enable <plugin>
agy plugin disable <plugin>
agy plugin uninstall <plugin>
```

#### B. Inside the `agy` Interactive CLI (`/plugin` / `/plugins`)

- **Interactive Plugin Manager UI**: Run `/plugin` (or `/plugins`) to open the TUI manager:
  - Press `Tab` to switch between **Installed** and **Discover** tabs, start typing to search/filter, and press `Enter` to expand plugin details.
  - In **Discover**, highlight **`+ Install from local directory...`** and press `Enter` to enter `./skills/<plugin>` (or press `Ctrl+S` on a Marketplace entry to install/uninstall).
  - In **Installed**, press `Space` to toggle enable/disable (prompts for required MCP credentials if needed) or `Ctrl+S` to uninstall.
- **Inline `/plugin` slash commands**:
  ```text
  /plugin install ./skills/<plugin>
  /plugin install <plugin-name>@antigravity-plugins-official
  /plugin list
  /plugin enable <plugin>
  /plugin disable <plugin>
  /plugin uninstall <plugin>
  ```

#### C. In the Antigravity App (`Customizations > Marketplace` & `Installed`)

1. In the left sidebar, click **Customizations** (below *Automations*).
2. **Marketplace tab**: Browse or search curated Marketplace plugins; click any card to inspect its details and click **Add** (or click **`+`** in the list) to install.
3. **Installed tab**: Plugins installed via `agy plugin install` or `/plugin` appear here automatically. Click the **`⋮`** menu beside any plugin (or open its detail card) to **enable/disable**, configure API keys/OAuth, launch **suggested starter prompt chips**, or **Uninstall**.

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
