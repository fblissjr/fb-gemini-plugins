# GEMINI.md

<!-- path-privacy: skip-file -->

This file provides guidance to Google Antigravity (`agy` CLI v1.4.0+ and Antigravity App v2.24.0+) when working with code in this repository. (`AGENTS.md` is a symlink to `GEMINI.md`.)

## Overview

`fb-gemini-plugins` is a monorepo of native plugins, skills, and hooks for **Google Antigravity** (`agy` CLI v1.4.0+ and Antigravity App v2.24.0+) and **Gemini Spark** (including Gemini web/desktop `Customize > Skills` and Gemini Enterprise). Each plugin lives under `skills/<plugin-name>/` and conforms to the Antigravity Plugin Specification (`https://antigravity.google/schemas/v1/plugin.json`) while shipping open-standard `SKILL.md` definitions that work in both Antigravity and Gemini Spark.

## Repository Structure

```
fb-gemini-plugins/
├── .agents/
│   └── plugins.json                         # Workspace plugin registry (do NOT duplicate in .agents/skills/)
├── skills/
│   ├── hypothetical-diff/                   # Universal HyDE-inspired Before/After diff plugin & skill (v0.1.1)
│   │   ├── plugin.json                      # Native Antigravity plugin manifest
│   │   ├── assets/
│   │   │   └── logo.svg                     # 128x128 square SVG icon for App/Marketplace cards
│   │   ├── skills/
│   │   │   └── hypothetical-diff/
│   │   │       ├── SKILL.md                 # Self-contained skill definition (Antigravity + Gemini Spark)
│   │   │       └── references/              # Deep-dive domain playbooks and HyDE theory
│   │   │           ├── domain-playbooks.md
│   │   │           └── hyde-theory-and-patterns.md
│   │   └── README.md                        # Plugin and dual-platform documentation
│   └── path-privacy/                        # Path & author privacy plugin (v0.21.0)
│       ├── plugin.json                      # Native Antigravity plugin manifest
│       ├── hooks.json                       # Plugin-root hooks configuration (SessionStart, PreToolUse)
│       ├── assets/
│       │   └── logo.svg                     # 128x128 square SVG icon for App/Marketplace cards
│       ├── hooks/                           # Dual-harness hook scripts (Antigravity + Claude Code)
│       │   ├── path-privacy-session-start.sh
│       │   └── path-privacy-pre-tool-use.sh
│       ├── skills/
│       │   └── path-privacy/
│       │       ├── SKILL.md                 # Skill definition with YAML frontmatter
│       │       ├── references/              # Reference documentation loaded on demand
│       │       │   ├── patterns.md
│       │       │   ├── scrub_workflow.md
│       │       │   └── path-privacy.local.json.example
│       │       └── scripts/                 # Scanner, scrubber, and git hooks
│       │           ├── _hooks_dir.sh
│       │           ├── _name_guard.sh
│       │           ├── _skip_marker.sh
│       │           ├── _version_compare.sh
│       │           ├── find-external-paths.sh
│       │           ├── git-commit-msg
│       │           ├── git-pre-commit
│       │           ├── install-git-hooks.sh
│       │           └── scrub-paths.sh
│       └── README.md                        # Plugin documentation
├── GEMINI.md                                # Project instructions (this file)
├── AGENTS.md                                # Symlink to GEMINI.md
├── CHANGELOG.md                             # Version history
├── LICENSE                                  # MIT License
└── README.md                                # Repository catalog and installation guide
```

## Path & Author Privacy Rules (CRITICAL)

Every file created or modified inside this repository MUST obey these rules:

1. **Repo-relative paths only**:
   - Never write `/Users/<username>/...`, `/home/<username>/...`, `~/...`, `$HOME/...`, or external sibling repo paths into tracked files.
   - Always use paths relative to the repo root (e.g., `skills/path-privacy/plugin.json`).
   - When illustrating external path patterns in documentation, use **explicit angle-bracket placeholders** (`<HOME>/...`, `/Users/<user>/...`, `/home/<username>/...`) or shell variables (`/Users/$USER/...`). Unbracketed generic words like `/home/user/xyz`, `/Users/dev/xyz`, or `/Users/alice/xyz` are **blocked** so LLM-sanitized paths carrying real project directory names are caught.
   - Append `# path-privacy: ignore` or `<!-- path-privacy: skip-file -->` only in files that document or implement `path-privacy` rules themselves.
2. **No personal full name**:
   - Never write the git author's full name (`git config user.name`) into repo files, commit messages, PR titles/bodies, or branch names (`LICENSE` files and `Signed-off-by:` trailers excepted).
   - Use the GitHub handle `fblissjr` or `<author>` instead.
3. **Artifact paths**:
   - Paths inside the Antigravity conversation artifact directory (`artifactDirectoryPath` / `/.gemini/antigravity-cli/brain/<conversation-id>/`) are valid during active sessions for artifacts and scratch scripts, and are automatically exempted by `path-privacy-pre-tool-use.sh`, but must never be copied into committed repository files.

## Antigravity Plugin Architecture (CLI v1.4.0+ / App v2.24.0+ / Marketplace)

```
<plugin-root>/
├── plugin.json                       # Required: Plugin manifest
├── README.md                         # Human-facing plugin documentation
├── assets/
│   └── logo.svg                      # Optional: Square >=128x128 icon (~10% margin)
├── mcp_config.json                   # Optional: MCP servers & connectors
├── hooks.json                        # Optional: Lifecycle hooks (MUST be at plugin root)
├── skills/
│   └── <skill-name>/
│       ├── SKILL.md                  # Required for each skill (YAML frontmatter on line 1)
│       ├── references/               # Optional progressive-disclosure docs
│       ├── scripts/                  # Optional executable helpers
│       └── resources/                # Optional schemas/templates
├── agents/
│   └── <agent-name>.md               # Optional custom subagents (YAML frontmatter + prompt)
├── rules/
│   ├── AGENTS.md                     # Optional always-on plugin rule (no frontmatter)
│   └── <rule-name>.md                # Optional scoped rule (YAML frontmatter required)
└── sidecars/
    └── <sidecar-name>/
        └── sidecar.json              # Optional managed background process / schedule
```

### 1. Plugin Manifest (`plugin.json`) & Workspace Registration (`.agents/plugins.json`)

- Placed at the plugin root (`skills/<name>/plugin.json`).
- Schema: `"$schema": "https://antigravity.google/schemas/v1/plugin.json"`.
- Supported runtime & Marketplace fields:
  - `name` (required, lowercase kebab-case matching `^[a-zA-Z0-9-_]+$`; global unique key across all plugins)
  - `displayName` (human-readable title for UI headers and cards)
  - `version` (semantic version string)
  - `description` (required, 1–2 sentences matched by Marketplace search)
  - `logo` (relative path such as `"assets/logo.svg"` ending in `.svg`, `.png`, `.jpg`, `.jpeg`, or `.webp`; square $\ge 128\times128$ with ~10% margin)
  - `suggestedPrompts` (up to 3 starter prompts for UI cards; additional items beyond 3 are ignored)
  - `disabled` (optional boolean to ship turned off by default)
  - Metadata fields (`author`, `repository`, `homepage`, `license`, `keywords`) are also permitted for catalog/GitHub metadata.
- **Workspace discovery**: `.agents/plugins.json` (`{"entries": [{"path": "skills"}]}`) registers all plugins in this repository for workspace sessions. **Do NOT also symlink plugin skills into `.agents/skills/`**, as Antigravity does not deduplicate skills across `.agents/skills/` and `.agents/plugins.json` and would inject every skill twice into the system prompt.
- **Install directories**: Global plugins live in `~/.gemini/config/plugins/<dir>/` (or `~/.gemini/antigravity-cli/plugins/<dir>/` when staged by `agy` CLI). Marketplace installs use a signed 64-bit hash for `<dir>` rather than `plugin.json`'s `name`.

### 2. Hooks Configuration (`hooks.json`)

- **Location**: MUST be at the **plugin root** (`skills/<name>/hooks.json`), NOT inside `hooks/hooks.json`.
- **Execution working directory**: Antigravity runs hook commands with `cwd` set to the directory containing `hooks.json` (`skills/<name>/`). Reference scripts as `bash ./hooks/<script>.sh`.
- **Top-level schema**: Top-level keys are hook group names mapping to supported lifecycle events:
  - `SessionStart` (flat handler array; fires once when a new conversation starts)
  - `PreToolUse` (grouped with `matcher` regex and `hooks` array; fires before a tool executes)
  - `PostToolUse` (grouped with `matcher` regex and `hooks` array; fires after a tool completes)
  - `PreInvocation` (flat handler array; fires before the model is called)
  - `PostInvocation` (flat handler array; fires after model invocation completes)
  - `Stop` (flat handler array; fires when the execution loop terminates)
- **stdin payload**: Antigravity passes camelCase JSON on stdin:
  - Common fields: `workspacePaths` (array of strings), `conversationId`, `transcriptPath`, `artifactDirectoryPath`, `modelName`.
  - `<app_data_dir>` resolves to `~/.gemini/antigravity` (App), `~/.gemini/antigravity-cli` (CLI), or `~/.gemini/antigravity-ide` (IDE).
  - `PreToolUse` fields: `toolCall.name`, `toolCall.args`, `stepIdx`.
- **`SessionStart` stdout**:
  - When no notice is needed: `{}`
  - When injecting system context:
    ```json
    {
      "injectSteps": [
        {
          "systemMessage": {
            "systemMessage": "[plugin:<name>]\n..."
          }
        }
      ]
    }
    ```
- **`PreToolUse` matchers & stdout**:
  - Antigravity file/shell tool names: `write_to_file`, `replace_file_content`, `multi_replace_file_content`, `run_command`.
  - Allow without modification: `{"decision": "allow"}`
  - Allow with argument rewrite (shallow top-level merge into `toolCall.args`):
    ```json
    {
      "decision": "allow",
      "reason": "...",
      "overwrite": {
        "CodeContent": "..."
      }
    }
    ```
  - Hard-block tool call:
    ```json
    {
      "decision": "deny",
      "reason": "..."
    }
    ```
  - Never return `"decision": "auto_approve"` unless a plugin is explicitly intended to bypass user permission prompts.

### 3. Skill Definition (`skills/<skill-name>/SKILL.md`)

- **YAML frontmatter**: Must start on **line 1** with `---` and include `name` (lowercase hyphenated) and `description` (written in third person with explicit trigger phrases so both Antigravity and Gemini Spark parse and auto-route it reliably).
- **Dual-platform compatibility (Antigravity + Gemini Spark)**:
  - Keep `SKILL.md` concise, action-oriented, and **self-contained** so it works as a standalone single-file upload/paste in **Gemini Spark** (`Customize > Skills` / Canvas) as well as inside an Antigravity plugin (where skills also auto-register as `/<skill-name>` slash commands).
  - Place extended domain playbooks, pattern catalogs, and theoretical references in `references/` and helper scripts in `scripts/` for progressive disclosure in Antigravity and ZIP package uploads in Gemini Spark.
- Always invoke helper shell scripts with `bash <script>` or check `[ -r "$SCRIPT" ]` so gates do not silently fail if executable bits are stripped on checkout.

### 4. MCP Servers & Connectors (`mcp_config.json`)

- **Location**: `<plugin-root>/mcp_config.json` (or `.agents/mcp_config.json` for workspace-scoped servers). Never name this file `mcp.json`.
- **Namespace**: MCP server names are global across the user's config and all installed plugins—prefix server keys with the plugin name (e.g., `"<plugin>-<service>"`).
- **Schema**:
  ```json
  {
    "mcpServers": {
      "my-plugin-local": {
        "command": "node",
        "args": ["./mcp/server.js"],
        "env": {}
      },
      "my-plugin-remote": {
        "serverUrl": "https://api.example.com/mcp/",
        "headers": {
          "Authorization": "Bearer YOUR_API_TOKEN"
        },
        "tools": {
          "search_items": {
            "eager": true
          }
        }
      }
    }
  }
  ```
- **Transport & Auth**:
  - Local `stdio`: requires `command` (optional `args`, `env`, `cwd`).
  - Remote `Streamable HTTP` / `SSE`: requires **`serverUrl`** (`url` and `httpUrl` are not supported in `agy` CLI).
  - Supports `"authProviderType": "google_credentials"` (ADC), automatic OAuth via Dynamic Client Registration (DCR), or manual `"oauth": {"clientId": "...", "clientSecret": "..."}` (redirect URI: `https://antigravity.google/oauth-callback`), plus `"disabled"` and `"disabledTools"`.

### 5. Rules (`rules/AGENTS.md` and `rules/<rule-name>.md`)

- **Consolidated plugin rule (`rules/AGENTS.md` or `rules/GEMINI.md`)**: Plain Markdown with **no frontmatter**; always active while the plugin is enabled.
- **Modular rule files (`rules/<rule-name>.md` or `.agents/rules/*.md`)**:
  - **MUST** begin with YAML frontmatter declaring a valid snake_case `trigger` (`always_on`, `model_decision`, `glob`, or `manual`), `description` (required for `model_decision`), and `globs` (required for `glob`, e.g., `"*.ts, *.tsx"`). Files in `rules/*.md` without valid frontmatter are **silently discarded**.
  - Antigravity scans `rules/` one level deep (unless nested paths are listed in `.agents/rules.json`).
  - Supports `@[label](relative/path.md)` (inlines target file content with frontmatter stripped) and `@path/to/file` (rewritten to canonical workspace path).
  - Enforces a **24 KB (`24,000` bytes)** per-file cap and a **20,000-token** aggregate rules budget.

### 6. Custom Subagents (`agents/<agent-name>.md`)

- Placed at `<plugin-root>/agents/<agent-name>.md` (or `agents/<agent-name>/agent.md`).
- Requires YAML frontmatter followed by the Markdown system prompt:
  ```markdown
  ---
  name: my-plugin-auditor
  description: Specialized subagent for ...
  tools:
    - view_file
    - grep_search
    - run_command
  subagent: true
  mainAgent: false
  model: inherit
  commandExecutionPolicy: sandbox
  skills:
    - skills/my-skill
  ---

  # System Prompt
  ...
  ```
- Only list exact valid Antigravity tool names in `tools` (`view_file`, `write_to_file`, `replace_file_content`, `multi_replace_file_content`, `list_dir`, `find_by_name`, `grep_search`, `search_web`, `read_url_content`, `run_command`, `manage_task`, `schedule`, `invoke_subagent`, `define_subagent`, `send_message`, `manage_subagents`, `ask_question`, `generate_image`).

### 7. Sidecars (`sidecars/<sidecar-name>/sidecar.json`)

- **Location**: `<plugin-root>/sidecars/<sidecar-name>/sidecar.json` (never `sidecars.json` at the plugin root).
- Sidecar ID is `<pluginName>/<sidecarName>`, and `cwd` is set to the sidecar's directory.
- **Schema**:
  ```json
  {
    "command": "python3",
    "args": ["worker.py"],
    "restart_policy": "on-failure"
  }
  ```
  (`command` is mutually exclusive with `"builtin": "schedule"`; `restart_policy` is `"always"` [default], `"on-failure"`, or `"never"`).

### 8. Version Cascade

When updating a plugin's version, keep these locations in sync:
1. `skills/<name>/plugin.json` (`version`)
2. `README.md` (catalog table)
3. `CHANGELOG.md` (new release section)
4. If `install-git-hooks.sh` changes its generated `.git/hooks/` wrapper template, bump `WRAPPER_TEMPLATE_VERSION` in `skills/path-privacy/skills/path-privacy/scripts/install-git-hooks.sh`.

## Validation & Maintenance Commands

Run these checks before committing any changes:

```bash
# 1. Validate plugin structures and manifests against the Antigravity runtime loader
agy plugin validate skills/hypothetical-diff --strict --json
agy plugin validate skills/path-privacy --strict --json

# 2. Check git hook installation health
bash skills/path-privacy/skills/path-privacy/scripts/install-git-hooks.sh --doctor

# 3. Scan working tree for external path or full-name leaks
bash skills/path-privacy/skills/path-privacy/scripts/find-external-paths.sh -d .
```
