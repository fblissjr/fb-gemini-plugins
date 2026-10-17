# fb-gemini-plugins

<!-- path-privacy: skip-file -->

Native plugins, skills, and hooks for **Google Antigravity** (`agy` CLI v1.4.0+ and Antigravity App v2.24.0+).

## Plugin Catalog

| Plugin | Version | Components | Description |
|--------|---------|------------|-------------|
| **[path-privacy](skills/path-privacy/)** | `0.20.0` | Skill (`path-privacy`), Hooks (`SessionStart`, `PreToolUse`), Git Hooks (`pre-commit`, `commit-msg`) | Keeps personal identifiers and external paths out of repository files, commit messages, PR descriptions, and branch names. Auto-rewrites in-repo absolute paths to repo-relative form and hard-blocks external paths and the git `user.name` full name. |

---

## Installation (Antigravity CLI & App)

Plugins installed into `~/.gemini/config/plugins/` are shared automatically between the **Antigravity CLI (`agy`)** and the **Antigravity App (v2.24.0+)**.

### Method 1: Antigravity CLI (`agy`) — Direct from GitHub or Local Checkout

`agy plugin install` supports GitHub URLs directly (both single-plugin URLs and bulk-directory URLs) as well as local directories:

```bash
# Option A: Install path-privacy directly from GitHub (no manual git clone needed)
agy plugin install https://github.com/fblissjr/fb-gemini-plugins/tree/main/skills/path-privacy

# Option B: Bulk-install ALL plugins in this repo directly from GitHub
agy plugin install https://github.com/fblissjr/fb-gemini-plugins/tree/main/skills

# Option C: Install from a local checkout of fb-gemini-plugins
agy plugin install ./skills/path-privacy

# Verify installed plugins
agy plugin list

# Validate plugin manifest, skills, and hooks against the runtime loader
agy plugin validate ./skills/path-privacy --strict
```

### Method 2: Antigravity CLI Interactive TUI (`/plugin`)

1. Start an interactive session with `agy`.
2. Run `/plugin` in the prompt.
3. Switch to the **Discover** tab and select **+ Install from local directory...**.
4. Enter the path to `skills/path-privacy` in your `fb-gemini-plugins` checkout.

### Method 3: Antigravity App (v2.24.0+)

- Because Antigravity App and `agy` CLI share `~/.gemini/config/plugins/`, running `agy plugin install ./skills/path-privacy` immediately enables `path-privacy` in the Antigravity App as well.
- When opening the `fb-gemini-plugins` workspace directly in Antigravity App or CLI, `.agents/plugins.json` and `.agents/skills/` also register the plugin automatically for the workspace.

### Per-Repository Git Hooks (`pre-commit` & `commit-msg`)

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
├── skills/
│   └── path-privacy/            # Native Antigravity plugin (plugin.json + hooks.json + skills/)
├── GEMINI.md                    # Workspace instructions for Antigravity
├── AGENTS.md                    # Symlink to GEMINI.md
├── CHANGELOG.md                 # Release history
├── LICENSE                      # MIT License
└── README.md                    # This file
```

## Development & Validation

Requires Google Antigravity CLI `v1.4.0+` (`agy`), `ripgrep` (`rg`), and `jq`.

```bash
# Validate plugin manifest and components
agy plugin validate skills/path-privacy --strict --json

# Check installed git hooks health
bash skills/path-privacy/skills/path-privacy/scripts/install-git-hooks.sh --doctor

# Run path-privacy scan on the repository
bash skills/path-privacy/skills/path-privacy/scripts/find-external-paths.sh -d .
```

## License

[MIT](LICENSE)
