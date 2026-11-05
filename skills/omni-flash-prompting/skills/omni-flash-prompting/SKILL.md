---
name: omni-flash-prompting
description: >-
  Craft, choreograph, refactor, and lint prompts and multi-turn storyboards for
  Google Gemini Omni 1.2 Flash (gemini-omni-1.2-flash) via the Interactions API.
  Covers native 3s-to-15s video generation, 3-act timecode beat choreography,
  the Minimal Delta plus Anchor rule for conversational video editing, media role
  binding for up to 6 reference images and 3 reference videos, first-and-last
  frame interpolation, horizon extensions, audio preservation vs. full audio
  regeneration, and the 720p-to-4K draft-to-upscale loop. Use when user says
  "omni 1.2 flash", "gemini-omni-1.2-flash", "omni flash prompt", "prompt omni
  flash", "15-second video prompt", "multi-turn video edit prompt", "video
  reference tags", "first and last frame prompt", or wants to write, debug, or
  optimize video generation and editing prompts for Gemini Omni Flash.
---

# Gemini Omni 1.2 Flash Prompting Engine (`omni-flash-prompting`)

Transforms rough creative ideas, storyboards, and video-editing requests into high-precision prompts, role-tagged media bindings, and multi-turn conversational sequences for **Google Gemini Omni 1.2 Flash (`gemini-omni-1.2-flash`)** on the Gemini **Interactions API**.

`<plugin-root>` is `~/.gemini/config/plugins/omni-flash-prompting` for an installed Antigravity plugin, `skills/omni-flash-prompting` in a checkout of `fb-gemini-plugins`, or `${CLAUDE_PLUGIN_ROOT}` in Claude Code. Helper CLI: `<plugin-root>/skills/omni-flash-prompting/scripts/omni_prompt.py`.

---

## What Changed in Gemini Omni 1.2 Flash (`gemini-omni-1.2-flash` vs. `1.1`)

| Capability / Spec | Gemini Omni 1.1 Flash (`gemini-omni-1.1-flash`) | Gemini Omni 1.2 Flash (`gemini-omni-1.2-flash`) | Prompting & Workflow Impact |
| :--- | :--- | :--- | :--- |
| **Single-Pass Duration** | `3s–10s` (`1s` increments) | **`3s–15s` (`1s` increments, +50% ceiling)** | Enables complete 3-act micro-narratives (`[0-5s]`, `[5-10s]`, `[10-15s]`) and full product arcs without stitching. |
| **720p Draft Cost** | ~\$0.10 / second | **\$0.07 / second (-30%, \$12 / 1M video tokens)** | Makes iterative multi-turn drafting at `720p` (`store=true`) cheap before rendering the final cut at `1080p` or `4k`. |
| **Reference Adherence** | Baseline multi-reference tracking | **62–63% consistency win rate over 1.1** | Stronger identity, garment, brand color, and packaging text lock across camera angles (up to **6 image refs** + **3 video refs**). |
| **Camera & Motion Physics** | Occasional jump cuts on complex moves | **Continuous trajectory & FPV lock** | Smoother FPV drone flights, orbital tracking, and dolly zooms when paired with explicit single-shot locks and spatial refs. |
| **Multi-Turn Editing & Speech** | Basic stateful turn editing | **Granular conversational edits & lip-sync** | Swaps backgrounds, lighting, weather, or product colorways across chat turns (`previous_interaction_id`) while locking subject performance; improved multi-speaker dialogue and lip-sync. |
| **Output Resolutions** | `360p`, `720p`, `1080p`, `4k` (`24 FPS`, `16:9` / `9:16`) | `360p`, `720p` (default), `1080p`, `4k` (`24 FPS`, `16:9` / `9:16`, SynthID watermarked) | Draft fast at `360p`/`720p`; use `delivery="uri"` in `response_format` for `>4 MB` (`1080p`, `4k`, or `15s`) outputs. |

---

## Core Principle: Generation vs. Editing Prompt Polarity

Gemini Omni 1.2 Flash uses **opposite prompting polarities** depending on whether you are **generating new footage** or **editing existing footage**:

1. **New Video Generation (`generate` mode) requires Rich 6-Layer Specification**:
   - By default, Omni Flash acts like an autonomous multi-shot director and inserts scene cuts to build a narrative.
   - To control the output, explicitly specify: **(1) Shot & Continuity Lock**, **(2) Subject & Micro-Detail**, **(3) Action, Physics & `[0-15s]` Timecode Beats**, **(4) Camera Trajectory**, **(5) Lighting, Setting & `"Quoted"` Text**, and **(6) Audio & Inline Negatives**.
2. **Video Editing (`edit` and `multiturn` modes) requires Minimal Delta + Anchor Lock**:
   - **Never** re-describe the entire scene when editing an uploaded video or a previous turn (`previous_interaction_id`). Overly descriptive edit prompts cause unintended re-generation and character/background drift.
   - State **only** the targeted modification in plain imperative language, followed immediately by an explicit **Anchor Clause**: `"Keep everything else the same."` or `"Keep [subject performance, camera framing, and reflections] identical to the source video, only change [target]."`.
3. **Zero Unsupported API Knobs (Inline Everything)**:
   - `gemini-omni-1.2-flash` does **not** support `system_instruction`, `temperature`, `top_p`, `stop_sequences`, or a separate `negative_prompt` field. Embed all meta-prompting rules and negative constraints (`"No dialogue."`, `"No scene cuts."`, `"No embellishments."`, `"No extra sound effects."`) directly inside the prompt text.

---

## Five Operational Modes

Select the mode matching the user's task (or chain them for end-to-end production):

| Mode | When to Use | What It Produces | Reference Guide |
| :--- | :--- | :--- | :--- |
| **`generate`** *(6-Layer 3s–15s Prompt Architect)* | Creating a new `3s–15s` video from text, keyframes (`<FIRST_FRAME>` / `<LAST_FRAME>`), or up to 6 image + 3 video references | A copy-pasteable **6-Layer Omni 1.2 Prompt**, explicit media role bindings (`<IMAGE_REF_N>`, `<VIDEO_REF_N>`, or `[# Sources ...]` headers), `[0-15s]` beat sheet, and `interactions.create` snippet. | [`references/prompt-architecture-and-tags.md`](references/prompt-architecture-and-tags.md) |
| **`edit`** *(Minimal Delta + Anchor Refactor)* | Modifying an existing `<=10s` video (style transfer, object add/remove, relighting, background/colorway swap, text replacement) | Strips dangerous over-description into a **Minimal Delta + Anchor Prompt**, sets the **Audio Stream Gate** (`keep audio` vs. `strip audio` via `ffmpeg -an`), and provides before/after prompt diffs. | [`references/editing-extension-and-multiturn.md`](references/editing-extension-and-multiturn.md) |
| **`extend`** *(Horizon Extension & Ref Injection)* | Extending a clip by `3s–10s` per turn (using the final `10s` as context, up to `30s–40s` total) | Builds a **Prompt-Only Extension** (omitting `task="extend"` so `<IMAGE_REF_N>` / `<VIDEO_REF_N>` work), resets timecodes to `0s` at the extension boundary, and locks audio continuity. | [`references/editing-extension-and-multiturn.md`](references/editing-extension-and-multiturn.md) |
| **`multiturn`** *(Conversational Draft-to-Upscale Playbook)* | Planning a multi-turn `previous_interaction_id` session (draft at `720p` for \$0.07/s $\rightarrow$ refine turn-by-turn $\rightarrow$ upscale to `1080p`/`4k`) | A turn-by-turn conversational script (`Turn 1` base generation with `store=true` $\rightarrow$ `Turn 2..N` isolated delta edits or dialogue extensions $\rightarrow$ final URI delivery upscale) + cost estimate. | [`references/domain-prompt-playbooks.md`](references/domain-prompt-playbooks.md) |
| **`lint`** *(12-Rule Deterministic Prompt & Config Audit)* | Reviewing or debugging a draft Omni 1.2 prompt, tag binding, or Interactions API payload before spending tokens | Runs [`scripts/omni_prompt.py`](scripts/omni_prompt.py) to flag 12 failure modes (tag errors, `task="extend"` conflicts, edit verbosity drift, missing shot locks, audio traps, payload size limits) and outputs the repaired prompt. | [`references/prompt-architecture-and-tags.md`](references/prompt-architecture-and-tags.md) |

---

## Mode 1: `generate` — The 6-Layer Cinematic Spec (`3s–15s`)

When crafting a generation prompt for `gemini-omni-1.2-flash`, assemble all 6 layers explicitly:

### Layer 1: Shot Structure & Continuity Lock
- **Single-Scene Take**: Omni Flash cuts between shots by default. To force one unbroken shot, open with: `"Continuous, unbroken [camera type] shot in a single scene. No scene cuts."`
- **Multi-Shot Montage**: Declare the exact cut rhythm upfront: `"Rapid-fire sequence cutting to a new angle every 1 second"` or use explicit timecode brackets.

### Layer 2: Subject, Costume & Packaging Micro-Detail
- Replace generic nouns (`"a dog"`, `"a bottle"`) with high-specificity physical descriptors, costume design principles, and material properties (`"a matte-amber frosted glass serum bottle with a brushed gold dropper cap"`).
- **Meta-Prompting Boosters**: When photorealism or dense environmental storytelling is needed, append: `"Consider micro-detail, expression, and timing to create a rich, natural scene. Apply costume design principles to characters and include realistic background detail."`

### Layer 3: Action, Physics & `[0-15s]` Timecode Choreography
- Detail how objects interact with gravity, momentum, reflections, and light.
- For `10s–15s` clips, anchor pacing with natural-language cues (`"After 4 seconds..."`, `"Every half a second (12 frames at 24fps)..."`) or **Timecode Brackets**:
  ```text
  [0-5s] Wide tracking shot: a cyclist in a neon rain jacket sprints down a wet Tokyo alley at dusk, tires kicking up mist.
  [5-10s] Camera pushes into a medium profile shot as she checks a holographic wrist display reading "SECTOR 4".
  [10-15s] She banks sharply into a sunlit courtyard and brakes to a smooth halt as the camera orbits 180 degrees around her.
  ```

### Layer 4: Camera Trajectory & Framing
- Specify aspect ratio (`16:9` landscape or `9:16` vertical), lens/framing (`macro close-up`, `low-angle wide`, `35mm anamorphic`), and trajectory (`continuous FPV drone flight through the archway`, `slow dolly-in`, `180-degree orbital pan`).

### Layer 5: Lighting, Environment & `"Quoted"` On-Screen Text
- Specify light quality and atmospheric interaction (`volumetric golden-hour sunbeams illuminating dust motes`).
- **On-Screen & Environmental Typography**: Put every word that should appear on screen, signs, storefronts, or license plates in **exact quotation marks**:
  - *Example*: `A neon storefront sign reads "OMNI 1.2", a street banner says "OPEN 24 HRS", and kinetic title text "CHAPTER ONE" fades in at the center.`

### Layer 6: Audio Direction & Inline Negative Guardrails
- Omni Flash synthesizes synchronized audio by default. Always direct it explicitly:
  - **Soundscape / Foley**: `"Sound design: rain pattering on asphalt, distant thunder, crisp tire spray."`
  - **Music**: `"Audio: high-energy 124 BPM synthwave beat; at 10s the bass drops into the chorus."`
  - **Inline Negatives** (place at the very end): `"No dialogue. No scene cuts. No extra sound effects. No embellishments."`

---

## Media Role Tagging Grammar (`<FIRST_FRAME>`, `<IMAGE_REF_N>`, `<VIDEO_REF_N>`)

Bind uploaded images and videos to exact generation roles using **Simple Tags** (for clear 1–2 role prompts) or **Explicit Prefix Declarations** (when mixing keyframes, multiple character/object images, and motion reference videos):

### 1. Simple Role Tags (0-Indexed)
- **`<FIRST_FRAME>`**: Anchor the first uploaded image as the literal starting frame (`<FIRST_FRAME> A woman in a red coat steps onto the train platform.`).
- **`<LAST_FRAME>`**: Anchor the final frame for interpolation. **Must** be used together with `<FIRST_FRAME>` (`<FIRST_FRAME> <LAST_FRAME> Smooth timelapse transition from dawn to starry night.`). Passing the **same image** to both `<FIRST_FRAME>` and `<LAST_FRAME>` creates a **seamless loop**.
- **`<IMAGE_REF_0>` .. `<IMAGE_REF_5>`** *(Up to 6 images; up to 3 per character for 2 characters)*: Bind style, subject identity, garment, or product references (`In the visual style of <IMAGE_REF_0>, the woman <IMAGE_REF_1> holds the bottle <IMAGE_REF_2>.`).
- **`<VIDEO_REF_0>` .. `<VIDEO_REF_2>`** *(Up to 3 clips, ideal duration `~3s` each; audio in reference videos is ignored)*: Bind character likeness, object behavior, or motion choreography (`The musician <IMAGE_REF_0> plays cello with the bowing motion of <VIDEO_REF_0>.`).

### 2. Explicit Prefix Declarations (`[# Sources ...]` & `[# References ...]`) + Closing Guardrails
When combining multiple media types, open the prompt with `[# Sources ...]` and/or `[# References ...]` (`@Image1`, `@Image2`, `@Video1` are 1-indexed by upload order, while `<IMAGE_REF_0>` is 0-indexed) and **always append the matching natural-language role guardrail at the end**:

```text
[# Sources <FIRST_FRAME>@Image1] [# References <IMAGE_REF_0>@Image2 <VIDEO_REF_0>@Video1]
Continuous tracking shot of the woman <IMAGE_REF_0> walking down a rain-slicked street with the stride shown in <VIDEO_REF_0>.
Use Image1 as the starting frame. Use Image2 as a reference for video generation; do not use it as a literal initial frame. Use Video1 as a reference; do not use it as a source for video editing.
```

---

## Mode 2: `edit` — Minimal Delta + Anchor Lock & The Audio Stream Gate

When editing an existing video (`<=10s` uploaded source or a prior turn via `previous_interaction_id`):

### 1. The Minimal Delta + Anchor Formula
> **`[Imperative Target Modification] + "Keep everything else the same."`** (or `"Keep [A, B, and C] identical to the source video, only change [D]."`)

| User Request | Anti-Pattern (Causes Scene Drift & Hallucinations) | Omni 1.2 Flash Minimal Delta + Anchor Prompt |
| :--- | :--- | :--- |
| Add a cat to a sofa clip | *"In the video of the man sitting on the leather sofa in the living room, add a small black cat that runs in from the right and jumps onto his lap while he pets it."* | `"Add a small black cat that jumps onto his lap, and he begins to pet it. Keep everything else the same."` |
| Remove a held object | *"Please remove the smartphone from the woman's hand and fill in the background so her hand looks empty."* | `"Make the phone invisible. Keep everything else the same."` |
| Commercial product / liquid swap | *"Reshoot this close-up kitchen video so that instead of dark chocolate being poured over the dish, golden melted cheddar cheese is poured with the same lighting."* | `"Keep the hand movement, dish, and background lighting identical to the source video, but replace the chocolate being poured with melted cheese."` |
| Background / weather swap | *"Change the medieval marketplace behind the armored knight into an oak forest while keeping his walk and armor reflections."* | `"Swap the background to a sunlit oak forest. Keep the knight's performance, steel armor reflections, and camera framing identical to the source video."` |

### 2. The Audio Stream Gate (Preserve vs. Regenerate from Scratch)
- **Keep / Adapt Original Audio (Default)**: If the input video contains an audio track, Omni Flash preserves and adapts that existing audio stream.
- **Regenerate All Audio from Scratch (Mandatory `ffmpeg -an` Strip)**: If you want a brand-new soundtrack, genre shift, or fresh soundscape tailored to a visual style change (e.g., turning a live clip into 90s anime with a synthwave score), you **must strip the audio stream from the source video before uploading** (`ffmpeg -i input.mp4 -c:v copy -an input_silent.mp4`). If any audio stream remains attached, Omni Flash will attempt to preserve it instead of generating new audio from scratch.

---

## Mode 3: `extend` — Horizon Extensions (`3s–10s` per Turn) & Reference Injection

1. **Extension Mechanics**:
   - Appends `3s–10s` to the end of a video (using the final `10s` as context, up to `30s–40s` total length; prepending or mid-clip insertion is not supported). Some final frames of the source clip are blended for a seamless transition.
2. **Unlocking Multimodal References During Extension (Omit `task="extend"`)**:
   - **Critical API Rule**: Explicitly setting `task="extend"` in `video_config` **blocks** passing `<IMAGE_REF_N>` and `<VIDEO_REF_N>`.
   - Instead, **omit the `task` parameter** and trigger extension via the prompt text (`"Extend this video."` or `"The scene continues."`). This lets you inject new reference images and reference videos into the extended segment:
     ```text
     Extend this video. The camera pans right as the character in <IMAGE_REF_0> enters the room dancing like <VIDEO_REF_0>. The background music builds into the chorus.
     ```
3. **Relative `0s` Extension Timecodes**:
   - In an extension prompt, `0s` refers to the **start of the newly added extension**, not the start of the original clip (e.g., `"After 2s, cut to a close-up"` on a `10s` base video triggers the cut at `12s` in the combined timeline).
4. **Spoken Dialogue Extension Rule**:
   - You **cannot** extend an *uploaded* video where someone is talking in order to add more spoken dialogue (silent characters or non-dialogue extensions work). To extend spoken dialogue across turns, generate the base clip with Omni Flash and extend it statefully via **`previous_interaction_id`**.

---

## Mode 4: `multiturn` — The 720p Draft $\rightarrow$ Conversational Refine $\rightarrow$ 4K Upscale Loop

Because `gemini-omni-1.2-flash` cuts `720p` draft pricing by 30% to **\$0.07/second** and supports stateful editing via `previous_interaction_id`, always structure production workflows as a **3-Stage Stateful Loop**:

1. **Turn 1 — Base Generation at `720p` (`store=true`)**:
   - Generate the `3s–15s` base clip at `720p` (do **not** set `store=false`, or `previous_interaction_id` will be unavailable for follow-up turns).
2. **Turns 2..N — Isolated Single-Axis Conversational Edits (`previous_interaction_id`)**:
   - Pass `previous_interaction_id=res1.id` and apply **one focused Minimal Delta + Anchor edit per turn** (e.g., Turn 2: swap background/lighting; Turn 3: refine audio track or extend by `5s–10s` with spoken dialogue).
3. **Final Turn — High-Resolution Render (`1080p` or `4k` with `delivery="uri"`)**:
   - Once motion, framing, and timing are locked, request `1080p` or `4k` (`3840x2160` / `2160x3840`) and set `delivery="uri"` in `response_format` so payloads over `4 MB` stream via the Files API without hitting inline size limits.

---

## Mode 5: `lint` & `compile` — Deterministic CLI Helper (`scripts/omni_prompt.py`)

Use the bundled zero-dependency CLI (`<plugin-root>/skills/omni-flash-prompting/scripts/omni_prompt.py`) to lint draft prompts against all 12 Gemini Omni 1.2 Flash traps, compile structured specs into role-tagged prompts + Interactions API code, or calculate draft-to-upscale budgets:

```bash
OMNI_PY="<plugin-root>/skills/omni-flash-prompting/scripts/omni_prompt.py"

# 1. Lint a draft prompt and configuration for Omni 1.2 Flash traps & anti-patterns
python3 "$OMNI_PY" lint \
  --mode edit \
  --prompt "In the video of the man sitting on the sofa in the living room, add a small black cat that runs in from the right and jumps onto his lap, and replace the soundtrack with a synthwave beat." \
  --has-source-audio

# 2. Compile a structured 15s generation spec with media references into a prompt + Interactions API payload
python3 "$OMNI_PY" compile \
  --mode generate \
  --duration 15 \
  --aspect-ratio 16:9 \
  --resolution 720p \
  --single-shot \
  --first-frame "frames/opening.jpg" \
  --image-refs "refs/hero.png,refs/bottle.png" \
  --video-refs "refs/camera_orbit.mp4" \
  --beats "0-5:Slow push-in on <IMAGE_REF_0> holding the serum bottle <IMAGE_REF_1> on a sunlit stone terrace|5-10:Camera orbits 180 degrees following <VIDEO_REF_0> as golden light refracts through the glass|10-15:Macro close-up on the bottle label reading \"LUMEN 1.2\" as water droplets roll down" \
  --audio "Calm ambient piano with soft morning breeze" \
  --negatives "dialogue,scene cuts,extra sound effects"

# 3. Estimate cost across 720p draft turns + final 1080p/4K render (with 1.2 vs 1.1 savings)
python3 "$OMNI_PY" cost --duration 15 --draft-turns 3 --final-resolution 4k

# 4. Run offline self-tests
python3 "$OMNI_PY" --self-test
```

---

## Regional & Safety Constraints Checklist

Always account for these hard platform boundaries before executing or debugging an Omni Flash workflow:
- **Regional Video Upload Restriction**: Uploading existing videos for **editing or extension** is **not available** in the **EEA, Switzerland, the UK**, and certain US states (returns fast with `total_output_tokens: 0` / empty video output). Generating new videos and editing/extending *model-generated* videos via `previous_interaction_id` works normally.
- **Person & Minor Safety Filters**: Uploading/editing images of minors (in EEA/CH/UK) or recognizable public figures is blocked by safety filters.
- **Reference Limits**: Maximum **6 reference images** (`<IMAGE_REF_0>`..`<IMAGE_REF_5>`) and **3 reference videos** (`<VIDEO_REF_0>`..`<VIDEO_REF_2>`, up to `~3s` each; audio in reference videos is ignored). Uploading standalone audio reference files or YouTube URLs is not supported.
- **Provenance**: Every generated clip embeds an imperceptible **SynthID** watermark.
