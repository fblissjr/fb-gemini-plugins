# omni-flash-prompting

last updated: 2026-11-05

A **Structured Prompting, Storyboard Choreography & Deterministic Prompt Linter/Compiler Plugin** (`v0.1.0`) for **Google Gemini Omni 1.2 Flash (`gemini-omni-1.2-flash`)** across **Google Antigravity** (`agy` CLI v1.4.0+ and Antigravity App v2.24.0+), **Claude Code**, **Gemini CLI**, and **Gemini Spark** (`Customize > Skills` and Gemini Enterprise).

---

## Why `omni-flash-prompting`?

Prompting **Gemini Omni 1.2 Flash (`gemini-omni-1.2-flash`)** via the Gemini Interactions API requires a fundamentally different discipline from prompting text LLMs or older 5-to-10-second diffusion models:

1. **Opposite Prompt Polarity (Generation vs. Editing)**:
   - **New Video Generation (`3s–15s`)** requires a **6-Layer Cinematic Specification**—explicitly locking shot continuity (`"Continuous, unbroken shot. No scene cuts."` to override Omni Flash's default multi-shot director cuts), material/packaging micro-detail, `[0-5s] / [5-10s] / [10-15s]` beat choreography, camera trajectory, quoted on-screen text, and inline audio/negative guardrails.
   - **Conversational Video Editing (`<=10s` or `previous_interaction_id`)** requires the **exact opposite**: **Minimal Delta + Anchor Lock** (`[Imperative Target Modification] + "Keep everything else the same."`). Re-describing the scene in an edit prompt triggers unwanted re-synthesis and character/background drift.
2. **Hidden Media Role & API Collisions**:
   - Mixing `<FIRST_FRAME>`, `<LAST_FRAME>`, `<IMAGE_REF_0>`..`<IMAGE_REF_5>` (up to 6 images), and `<VIDEO_REF_0>`..`<VIDEO_REF_2>` (up to 3 ~3s motion clips) without `[# Sources ...]` / `[# References ...]` prefix declarations and closing role-disambiguation sentences causes reference images to be mistaken for literal frame `0`.
   - Setting `task="extend"` in `video_config` **disables** multimodal references (`<IMAGE_REF_N>` / `<VIDEO_REF_N>`), whereas omitting `task` and prompting `"Extend this video."` unlocks mid-extension reference injection.
   - Requesting a brand-new soundtrack while editing a video that still has an audio stream fails unless the source audio is stripped first (`ffmpeg -an`).

**`omni-flash-prompting` codifies the complete Gemini Omni 1.2 Flash prompting specification into 5 operational modes (`generate`, `edit`, `extend`, `multiturn`, `lint`) and ships a zero-dependency CLI (`scripts/omni_prompt.py`)** that compiles structured storyboards into role-tagged prompts + Interactions API payloads and audits draft prompts against 12 real failure modes.

This plugin is fully self-contained; it can be used alone or chained with other skills in conversation.

---

## Five Operational Modes

| Mode | When to Use | What It Does | Reference Guide |
| :--- | :--- | :--- | :--- |
| **`generate`** *(6-Layer 3s–15s Prompt Architect)* | Creating a new `3s–15s` video from text, `<FIRST_FRAME>` / `<LAST_FRAME>`, or up to 6 image + 3 video references | Builds a 6-Layer Omni 1.2 Flash prompt with `[0-15s]` timecode beats, `[# Sources ...]` / `[# References ...]` role declarations, quoted on-screen text, audio direction, and inline negatives. | [`references/prompt-architecture-and-tags.md`](skills/omni-flash-prompting/references/prompt-architecture-and-tags.md) |
| **`edit`** *(Minimal Delta + Anchor Refactor)* | Editing an existing `<=10s` clip (style transfer, object add/remove, relighting, background or colorway swap) | Converts verbose edit descriptions into a surgical **Minimal Delta + Anchor Prompt** and checks the **Audio Stream Gate** (`keep audio` vs. `ffmpeg -an` full audio regeneration). | [`references/editing-extension-and-multiturn.md`](skills/omni-flash-prompting/references/editing-extension-and-multiturn.md) |
| **`extend`** *(Horizon Extension & Ref Injection)* | Appending `3s–10s` per turn (using the final `10s` as context, up to `30s–40s` total) | Crafts a **Prompt-Only Extension** (omitting `task="extend"` so `<IMAGE_REF_N>` and `<VIDEO_REF_N>` work), resets relative timecodes to `0s`, and enforces spoken-dialogue extension rules. | [`references/editing-extension-and-multiturn.md`](skills/omni-flash-prompting/references/editing-extension-and-multiturn.md) |
| **`multiturn`** *(720p Draft $\rightarrow$ 4K Upscale Loop)* | Iterating statefully via `previous_interaction_id` at \$0.07/s (`720p` draft, 30% cheaper than 1.1) before final `1080p`/`4k` render | Designs a turn-by-turn conversational storyboard (`Turn 1` `720p` base with `store=True` $\rightarrow$ `Turn 2..N` single-axis edits/extensions $\rightarrow$ final `URI` delivery upscale). | [`references/domain-prompt-playbooks.md`](skills/omni-flash-prompting/references/domain-prompt-playbooks.md) |
| **`lint`** *(12-Rule Deterministic Audit)* | Auditing a draft prompt or Interactions API config before calling `gemini-omni-1.2-flash` | Runs [`scripts/omni_prompt.py`](skills/omni-flash-prompting/scripts/omni_prompt.py) to catch 12 prompting and API traps (`R01`–`R12`). | [`references/prompt-architecture-and-tags.md`](skills/omni-flash-prompting/references/prompt-architecture-and-tags.md) |

---

## Quick Start Examples

Define `OMNI_PY` pointing to the installed plugin script (or local checkout):

```bash
OMNI_PY="$HOME/.gemini/config/plugins/omni-flash-prompting/skills/omni-flash-prompting/scripts/omni_prompt.py"
# Or from a local fb-gemini-plugins checkout:
# OMNI_PY="skills/omni-flash-prompting/skills/omni-flash-prompting/scripts/omni_prompt.py"
```

### 1. Compile a 15-Second 3-Act Product Prompt with Keyframe & Reference Tags

```bash
python3 "$OMNI_PY" compile \
  --mode generate \
  --duration 15 \
  --aspect-ratio 16:9 \
  --resolution 720p \
  --single-shot \
  --first-frame "frames/opening.jpg" \
  --image-refs "refs/hero.png,refs/bottle.png" \
  --video-refs "refs/orbit.mp4" \
  --beats "0-5:Slow push-in on <IMAGE_REF_0> holding the serum bottle <IMAGE_REF_1> on a sunlit stone terrace|5-10:Camera orbits 180 degrees following <VIDEO_REF_0> as golden light refracts through the glass|10-15:Macro close-up on the bottle label" \
  --text-overlays "LUMEN 1.2" \
  --audio "Calm ambient piano with soft morning breeze" \
  --negatives "dialogue,scene cuts,extra sound effects"
```

### 2. Lint a Draft Edit Prompt for Over-Description Drift & Audio Regeneration Traps

```bash
python3 "$OMNI_PY" lint \
  --mode edit \
  --prompt "In the video of the man sitting on the sofa in the living room, add a small black cat that runs in from the right and jumps onto his lap, and replace the soundtrack with a synthwave beat." \
  --has-source-audio
```

### 3. Estimate Draft-to-Upscale Workflow Budget (`$0.07/s` 720p Draft $\rightarrow$ 4K Final)

```bash
python3 "$OMNI_PY" cost --duration 15 --draft-turns 3 --final-resolution 4k
```

### 4. Run the Offline Self-Test Suite

```bash
python3 "$OMNI_PY" --self-test
```

---

## Installation & Setup

### 1. Google Antigravity (`agy` CLI v1.4.0+ & Antigravity App v2.24.0+)

Plugins installed in **Antigravity CLI (`agy`)** and **Antigravity App** share `~/.gemini/config/plugins/` and synchronize automatically across both surfaces ([Marketplace docs](https://antigravity.google/docs/marketplace/)).

- **From your shell (`agy plugin`)**:
  ```bash
  # Install directly from GitHub
  agy plugin install https://github.com/fblissjr/fb-gemini-plugins/tree/main/skills/omni-flash-prompting

  # Or install from a local checkout of fb-gemini-plugins
  agy plugin install ./skills/omni-flash-prompting

  # List, toggle, uninstall, or validate
  agy plugin list
  agy plugin enable omni-flash-prompting
  agy plugin disable omni-flash-prompting
  agy plugin validate ./skills/omni-flash-prompting --strict
  ```
- **Inside the `agy` interactive CLI (`/plugin` / `/plugins`)**:
  - Run `/plugin install ./skills/omni-flash-prompting` inline, or run `/plugin` (alias `/plugins`), press `Tab` to switch to **Discover**, and select **`+ Install from local directory...`** (`Space` toggles enable/disable in **Installed**; `Ctrl+S` installs/uninstalls).
- **In the Antigravity App**:
  - Open **Customizations** in the left sidebar $\rightarrow$ **Marketplace** (to browse and click **Add** / **`+`**) or **Installed** (where plugins installed via `agy` appear automatically; use the **`⋮`** menu or detail card to enable/disable, run suggested starter prompt chips, or uninstall).

### 2. Gemini Spark & Gemini App (`Customize > Skills`)

- **Option A — Single-File Upload or Paste**:
  Upload or paste `skills/omni-flash-prompting/skills/omni-flash-prompting/SKILL.md` in **Customize $\rightarrow$ Skills**.
- **Option B — Full Skill Package ZIP Upload (Includes `references/` and `scripts/`)**:
  ```bash
  (cd skills/omni-flash-prompting/skills/omni-flash-prompting && zip -r ../../../../omni-flash-prompting-skill.zip SKILL.md references/ scripts/)
  ```
  Upload `omni-flash-prompting-skill.zip` via **Skills $\rightarrow$ + $\rightarrow$ Upload skill**.

---

## Directory Structure

```text
skills/omni-flash-prompting/
├── plugin.json                                         # Native Antigravity plugin manifest (v0.1.0)
├── .claude-plugin/
│   └── plugin.json                                     # Claude Code plugin manifest (v0.1.0)
├── assets/
│   └── logo.svg                                        # 128x128 square SVG icon for App/Marketplace cards
├── README.md                                           # Plugin & multi-platform documentation (this file)
└── skills/
    └── omni-flash-prompting/
        ├── SKILL.md                                    # Self-contained 5-mode skill (Antigravity + Gemini Spark)
        ├── references/
        │   ├── prompt-architecture-and-tags.md         # 6-Layer spec, [0-15s] beats, and media role tagging
        │   ├── editing-extension-and-multiturn.md      # Minimal Delta + Anchor, audio gate, and extensions
        │   └── domain-prompt-playbooks.md              # 8 production prompt blueprints and multi-turn scripts
        └── scripts/
            └── omni_prompt.py                          # Zero-dependency stdlib compiler, 12-rule linter & cost CLI
```
