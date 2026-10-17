# Changelog

All notable changes to `fb-gemini-plugins` are documented in this file.

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
