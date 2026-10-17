# GEMINI.md

<!-- path-privacy: skip-file -->

This file provides guidance to Google Antigravity (`agy` CLI v1.4.0+ and Antigravity App v2.24.0+) when working with code in this repository. (`AGENTS.md` is a symlink to `GEMINI.md`.)

## Overview

`fb-gemini-plugins` is a monorepo of native plugins, skills, and hooks for **Google Antigravity** (`agy` CLI v1.4.0+ and Antigravity App v2.24.0+) and **Gemini Spark** (including Gemini web/desktop `Customize > Skills` and Gemini Enterprise). Each plugin lives under `skills/<plugin-name>/` and conforms to the Antigravity Plugin Specification (`https://antigravity.google/schemas/v1/plugin.json`) while shipping open-standard `SKILL.md` definitions that work in both Antigravity and Gemini Spark.

## Repository Structure

```
fb-gemini-plugins/
├── skills/
│   ├── hypothetical-diff/                   # Universal HyDE-inspired Before/After diff plugin & skill (v0.1.0)
│   │   ├── plugin.json                      # Native Antigravity plugin manifest
│   │   ├── skills/
│   │   │   └── hypothetical-diff/
│   │   │       ├── SKILL.md                 # Self-contained skill definition (Antigravity + Gemini Spark)
│   │   │       └── references/              # Deep-dive domain playbooks and HyDE theory
│   │   │           ├── domain-playbooks.md
│   │   │           └── hyde-theory-and-patterns.md
│   │   └── README.md                        # Plugin and dual-platform documentation
│   └── path-privacy/                        # Path & author privacy plugin (v0.20.0)
│       ├── plugin.json                      # Native Antigravity plugin manifest
│       ├── hooks.json                       # Plugin-root hooks configuration (SessionStart, PreToolUse)
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

## Antigravity Plugin Architecture (CLI v1.4.0+ / App v2.24.0+)

### 1. Plugin Manifest (`skills/<name>/plugin.json`)

- Placed at the plugin root (`skills/<name>/plugin.json`).
- Schema: `"$schema": "https://antigravity.google/schemas/v1/plugin.json"`.
- Supported fields: `name` (required, kebab-case matching directory), `description` (required), `displayName`, `version`, `author` (`{"name": "fblissjr"}`), `repository`, `license`, `keywords`, `logo`, and `suggestedPrompts`.
- Component directories are discovered by convention from the plugin root (`skills/`, `agents/`, `rules/`, `hooks.json`, `mcp.json`, `sidecars.json`).

### 2. Hooks Configuration (`skills/<name>/hooks.json`)

- **Location**: MUST be at the **plugin root** (`skills/<name>/hooks.json`), NOT inside `hooks/hooks.json`.
- **Execution working directory**: Antigravity runs hook commands with `cwd` set to the directory containing `hooks.json` (`skills/<name>/`). Reference scripts as `bash ./hooks/<script>.sh`.
- **Top-level schema**: Top-level keys are hook group names mapping to lifecycle events (`SessionStart`, `PreToolUse`, `PostToolUse`, `PostToolUseFailure`, `UserPromptSubmit`, `Stop`, `SubagentStop`, `PreCompact`).
- **stdin payload**: Antigravity passes camelCase JSON on stdin:
  - Common fields: `workspacePaths` (array of strings), `conversationId`, `transcriptPath`, `artifactDirectoryPath`, `modelName`.
  - `PreToolUse` fields: `toolCall.name` and `toolCall.args`.
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

### 3. Skill Definition (`skills/<name>/skills/<skill-name>/SKILL.md`)

- **YAML frontmatter**: Must start on **line 1** with `---` and include `name` and `description` (with explicit trigger conditions so both Antigravity and Gemini Spark parse and auto-route it reliably).
- **Dual-platform compatibility (Antigravity + Gemini Spark)**:
  - Keep `SKILL.md` concise, action-oriented, and **self-contained** so it works as a standalone single-file upload/paste in **Gemini Spark** (`Customize > Skills` / Canvas) as well as inside an Antigravity plugin.
  - Place extended domain playbooks, pattern catalogs, and theoretical references in `references/` and helper scripts in `scripts/` for progressive disclosure in Antigravity and ZIP package uploads in Gemini Spark.
- Always invoke helper shell scripts with `bash <script>` or check `[ -r "$SCRIPT" ]` so gates do not silently fail if executable bits are stripped on checkout.

### 4. Version Cascade

When updating a plugin's version, keep these locations in sync:
1. `skills/<name>/plugin.json` (`version`)
2. `CHANGELOG.md` (new release section)
3. If `install-git-hooks.sh` changes its generated `.git/hooks/` wrapper template, bump `WRAPPER_TEMPLATE_VERSION` in `skills/path-privacy/skills/path-privacy/scripts/install-git-hooks.sh`.

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
