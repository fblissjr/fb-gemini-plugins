# video-understanding

last updated: 2026-10-28

A **Progressive-Disclosure Video, Image, and Audio Understanding Router & Deterministic CLI Toolkit** (`v0.1.0`) for **Google Antigravity** (`agy` CLI v1.4.0+ and Antigravity App v2.24.0+), **Claude Code**, and **Gemini Spark** (including Gemini web/desktop `Customize > Skills` and Gemini Enterprise).

---

## Why `video-understanding`?

Multimodal coding agents routinely run into three expensive traps when inspecting video, dense images, and audio:

1. **The `1 fps` Sampling Trap**: Built-in file viewers (`read_file`) sample standard video at `1 frame/second` (`t ≈ N + 0.5s`) and reject files over `100 MB`—silently skipping `23` of every `24` frames on a `24 fps` clip (`29/30` on `30 fps`), or failing outright on full-length renders.
2. **Unnecessary API Spend on Tasks the Harness Can Do Natively**: Calling an external API with a billed API key to inspect a local `<100 MB` clip or crop a high-resolution image wastes tokens and uploads files unnecessarily when local `.1fps` frame-hold encoding (`encode-1fps`) and local cropping (`crop`) let `read_file` inspect every frame natively at **`$0` API spend**.
3. **Coordinate Transposition & Multi-Panel Hallucinations**: Gemini's `box_2d` returns `[ymin, xmin, ymax, xmax]` (`y`-first!) scaled to `0..1000`, while enabling `"processing": "agentic"` on multi-panel / side-by-side comparison videos causes server-side dynamic spatial cropping to misread stacked rows.

**`video-understanding` enforces a strict Native-First Gate (`Rule 0`) and ships a zero-dependency CLI helper (`scripts/gemini_media.py`)** covering both `$0` local preparation (`encode-1fps`, `crop`) and the five capabilities that genuinely require the Gemini Interactions API (`slice`, `agentic-video`, `boxes`, `zoom`, `transcribe-spans`).

This plugin is fully self-contained; it can be used alone or chained with other skills via the conversation.

---

## How It Works: Rule 0 Native-First Gate $\rightarrow$ 5 Progressive-Disclosure Paths

| Path / Capability | Can `agy` Do This Natively? | Mandatory Native Path First (`$0` API Spend) | When to Escalate to `gemini-api` + Reference Guide | Helper Subcommand (`scripts/gemini_media.py`) |
| :--- | :--- | :--- | :--- | :--- |
| **Path 1: Native `read_file` + Local `encode-1fps` / `crop`** | **YES** | Encode `<stem>.1fps.<first:05d>-<last:05d>.mp4` via `encode-1fps` and call `read_file` for `1:1` every-frame QA; call `read_file` on the native-FPS `.mp4` for audio/motion; run `crop` for small image regions. | **Never** when Path 1 satisfies the task. (`gemini_media.py` mechanically refuses uploading any `<100 MB` `.mp4` that has a `.1fps.*.mp4` sibling on disk.) | `gemini_media.py encode-1fps <video.mp4>` / `gemini_media.py crop <img.png>` + native `read_file` |
| **Path 2A: Static High-FPS Video & Frame-Span Slicing** | **NO** on `>100 MB` files or raw high-FPS video without `.1fps.mp4` | Use `.1fps.mp4` via `read_file` whenever local `ffmpeg` is available and clip is `<100 MB`. | Slicing `[first..last]` frame spans (`start_offset` / `end_offset`) from an uploaded `>100 MB` master video at native FPS (`"resolution": "high"`). See [`references/video_static_and_slicing.md`](skills/video-understanding/references/video_static_and_slicing.md). | `gemini_media.py slice <video_or_file_id> --first F --last L --prompt "..."` |
| **Path 2B: Opt-In Agentic Video (`"processing": "agentic"`)** | **NO** (`read_file` has no `>100 MB` support or dynamic agentic pass) | Use `.1fps.mp4` parts via `read_file` on short clips (`<5 min`). | Long single-canvas videos (`>5–10 min` or `>100 MB`) or mixed `agentic` (master video) + `static` (candidate clip via `--compare-clip`). **BANNED on multi-panel/stacked strips.** See [`references/video_agentic.md`](skills/video-understanding/references/video_agentic.md). | `gemini_media.py agentic-video <master.mp4> [--compare-clip <clip.mp4>] --prompt "..."` |
| **Path 3A: `0..1000` `box_2d` & Polygon `mask` Grounding** | **NO** (chat text is not schema-calibrated to `0..1000` `box_2d`/`mask` heads) | Inspect existing local detector outputs (`.json` / `.npz`) first if present. | Schema-calibrated `0..1000` `box_2d` (`[ymin, xmin, ymax, xmax]`) and polygon `mask` (`[[x, y], ...]`) descaled to exact image pixels (`xyxy` & `ltwh`), plus optional IoU matching (`--match-boxes`). See [`references/image_boxes_and_masks.md`](skills/video-understanding/references/image_boxes_and_masks.md). | `gemini_media.py boxes <frame.png> [--ref <pic.png>] [--match-boxes <path>] [--with-masks] --prompt "..."` |
| **Path 3B: Agentic Image Zoom (`code_execution` + `ultra_high`)** | **YES** via local `gemini_media.py crop` + `read_file` | Crop tiles or compute pixel math locally and call `read_file` on the crop (`$0` API spend). | Only when remote sandboxed `code_execution` + `"resolution": "ultra_high"` (`2240` tokens) is needed, or for the Gemini 3+ `media_resolution` token table. See [`references/image_agentic_zoom.md`](skills/video-understanding/references/image_agentic_zoom.md). | `gemini_media.py zoom <grid.jpg> --prompt "..."` |
| **Path 4: Active-Speaker & Frame-Span Transcription** | **YES** on `<100 MB` clips (`read_file` + local audio tools) | Call `read_file` on the `<100 MB` video/audio clip first. | Videos `>100 MB`, or structured multi-speaker JSON (`speaker`, `start_frame`, `end_frame`, `mouth_visibly_open`, `text`) with high-res visual lip attribution (`--visual-speakers`). See [`references/audio_and_transcription.md`](skills/video-understanding/references/audio_and_transcription.md). | `gemini_media.py transcribe-spans <clip.mp4> [--shot-first F] [--visual-speakers]` |

---

## Quick Start Examples

Define `MEDIA_PY` pointing to the installed plugin script (or local checkout):

```bash
MEDIA_PY="$HOME/.gemini/config/plugins/video-understanding/skills/video-understanding/scripts/gemini_media.py"
# Or from a local fb-gemini-plugins checkout:
# MEDIA_PY="skills/video-understanding/skills/video-understanding/scripts/gemini_media.py"
```

### 1. Generate a `.1fps` Companion for `$0` Every-Frame `read_file` Inspection (Path 1)

```bash
# Hold every frame for 1.0s (muted, <80 MB parts) with optional burned-in frame numbers:
python3 "$MEDIA_PY" encode-1fps path/to/clip.mp4 --burn-frame-numbers
# -> Writes path/to/clip.1fps.00000-00119.mp4 (ready for native `read_file` at $0 API spend)
```

### 2. Detect & Segment Objects with Exact Pixel Coordinates & IoU Matching (Path 3A)

```bash
python3 "$MEDIA_PY" boxes path/to/scene.png \
  --ref path/to/reference_object.png \
  --with-masks \
  --prompt "Locate the target subject from the first reference image in the second scene frame."
```

### 3. Run the Built-In Self-Test Suite (Zero Network / Zero API Spend)

```bash
python3 "$MEDIA_PY" --self-test
```

---

## Installation & Setup

### 1. Google Antigravity (`agy` CLI v1.4.0+ & Antigravity App v2.24.0+)

```bash
# Install directly from GitHub
agy plugin install https://github.com/fblissjr/fb-gemini-plugins/tree/main/skills/video-understanding

# Or install from a local checkout of fb-gemini-plugins
agy plugin install ./skills/video-understanding

# Validate plugin manifest and skill structure
agy plugin validate ./skills/video-understanding --strict
```

### 2. Gemini Spark & Gemini App (`Customize > Skills`)

- **Option A — Single-File Upload or Paste**:
  Upload or paste `skills/video-understanding/skills/video-understanding/SKILL.md` in **Customize $\rightarrow$ Skills**.
- **Option B — Full Skill Package ZIP Upload (Includes `references/` and `scripts/`)**:
  ```bash
  (cd skills/video-understanding/skills/video-understanding && zip -r ../../../../video-understanding-skill.zip SKILL.md references/ scripts/)
  ```
  Upload `video-understanding-skill.zip` via **Skills $\rightarrow$ + $\rightarrow$ Upload skill**.

---

## Directory Structure

```text
skills/video-understanding/
├── plugin.json                                         # Native Antigravity plugin manifest (v0.1.0)
├── .claude-plugin/
│   └── plugin.json                                     # Claude Code plugin manifest (v0.1.0)
├── assets/
│   └── logo.svg                                        # 128x128 square SVG icon for App/Marketplace cards
├── README.md                                           # Plugin & multi-platform documentation (this file)
└── skills/
    └── video-understanding/
        ├── SKILL.md                                    # Self-contained skill router (Antigravity + Gemini Spark)
        ├── references/
        │   ├── video_static_and_slicing.md             # Path 2A: High-FPS static inspection & server-side slicing
        │   ├── video_agentic.md                        # Path 2B: Opt-in agentic timeline navigation & multi-video mixing
        │   ├── image_boxes_and_masks.md                # Path 3A: 0..1000 box_2d & polygon mask pixel grounding
        │   ├── image_agentic_zoom.md                   # Path 3B: Per-item media_resolution & code_execution zoom
        │   └── audio_and_transcription.md              # Path 4: Active-speaker & frame-span transcription
        └── scripts/
            └── gemini_media.py                         # Self-contained CLI helper (encode-1fps, crop, boxes, slice, agentic-video, zoom, transcribe-spans, --self-test)
```
