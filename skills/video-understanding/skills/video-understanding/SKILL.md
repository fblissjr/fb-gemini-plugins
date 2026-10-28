---
name: video-understanding
description: >-
  Route video, image, and audio inspection with a strict Native-First Gate
  inside the Antigravity (agy) harness — always using built-in read_file
  (.1fps.<first>-<last>.mp4 frame-held companions, <100 MB video/audio clips,
  .png/.jpg stills) and local Python tools (encode-1fps, crop, PIL/cv2/numpy)
  at $0 API spend first, and calling gemini-api ONLY for capabilities agy
  cannot perform natively (>100 MB master videos, server-side frame-span
  slicing, opt-in agentic timeline navigation, 0..1000 box_2d and polygon mask
  grounding, agentic code-execution zoom, and visual speaker transcription).
---

# Video, Image, and Audio Understanding Router

This skill routes media QA, grounding, and perception across `read_file`, local Python helpers (`scripts/gemini_media.py`), and the `gemini-api` CLI. To keep context lean, **read only the specific reference file in `references/` when you hit a task `agy` cannot perform natively**.

`<plugin-root>` is `~/.gemini/config/plugins/video-understanding` for an installed Antigravity plugin, `skills/video-understanding` in a checkout of `fb-gemini-plugins`, or `${CLAUDE_PLUGIN_ROOT}` in Claude Code. Helper scripts live in `<plugin-root>/skills/video-understanding/scripts/gemini_media.py`.

---

## Rule 0 — Native-First Gate (`agy` Native Tools Before Any `gemini-api` Call)

Inside the Antigravity (`agy`) harness, **never invoke `gemini-api` or upload local media for a task `agy` can perform natively (`$0` API key spend, zero external uploads)**:

1. **Every-frame video QA (`<100 MB`) -> Local `encode-1fps` + Native `read_file` on `.1fps.<first>-<last>.mp4`**:
   - Built-in `read_file` samples standard video at `1 frame/second` (`t ≈ N + 0.5s`), which skips `23` of every `24` frames on a `24 fps` clip (`29/30` on `30 fps`).
   - Run `python3 <plugin-root>/skills/video-understanding/scripts/gemini_media.py encode-1fps <video.mp4> [--first F --last L] [--burn-frame-numbers]` to encode `<stem>.1fps.<first:05d>-<last:05d>.mp4` companions where each source frame is held for `1.0s` (`-r 1`, muted, capped under `80 MB` per part).
   - Calling `read_file` on `.1fps.<first>-<last>.mp4` gives deterministic `1:1` frame alignment at `$0` API spend. `scripts/gemini_media.py` mechanically refuses uploading any local `<100 MB` `.mp4` that has a `<stem>.1fps.*.mp4` sibling on disk unless `--force-api` is explicitly passed.
2. **Audio, vocal sync, and real-time motion (`<100 MB`) -> Native `read_file` on the native-FPS `.mp4`**:
   - Call `read_file` directly on the `<100 MB` video or audio clip (and inspect local audio/VAD streams if present) before considering any `gemini-api` transcription call.
3. **Images, contact sheets, and dense grids -> Native `read_file` + Local `crop` (`PIL` / `cv2` / `numpy`)**:
   - Call `read_file` directly on `.png` / `.jpg` stills. If a tile on a contact sheet, chart, or multi-row diagnostic strip is small, or if you need RGB/luma pixel math, run `gemini_media.py crop <image> --box x1,y1,x2,y2 --out /tmp/crop.png` (or a local Python snippet) and call `read_file` on `/tmp/crop.png`.
4. **Object boxes and masks -> Inspect existing local detections first**:
   - If the workspace already has local detector outputs (`.json` bounding boxes or `.npz` segmentation masks), inspect them locally with Python before making any remote `box_2d` / `mask` grounding call.
5. **When `gemini-api` escalation IS permitted (capabilities `agy` cannot do natively)**:
   - **File size `>100 MB`**: `read_file` rejects files over `100 MB` (e.g., full-length master cuts or long recordings).
   - **Server-side high-FPS static inspection or `start_offset`/`end_offset` slicing on a remote `files/<id>` or when local `ffmpeg` `.1fps.mp4` generation is not possible**: Native `read_file` is locked to `1 fps` sampling on raw high-FPS video.
   - **Opt-in `"processing": "agentic"` timeline navigation**: Long single-canvas videos (`>5–10 min` or `>100 MB`) where transcript-first dynamic frame loading or mixed `agentic` + `static` multi-video comparison is needed.
   - **Schema-calibrated `0..1000` `box_2d` / polygon `mask` grounding**: Zero-VRAM 2D bounding-box and polygon segmentation localization when local detectors are unavailable or missed the target object.
   - **Media privacy gate**: Never upload private or sensitive user media (videos, stills, audio) to `gemini-api` without asking the user and naming what leaves the machine.

---

## Progressive Disclosure Routing Matrix

| Path / Capability | Can `agy` Do This Natively? | Mandatory Native Path First (`$0` API Spend) | When to Escalate to `gemini-api` + Reference Guide | Helper Subcommand (`<plugin-root>/skills/video-understanding/scripts/gemini_media.py`) |
| :--- | :--- | :--- | :--- | :--- |
| **Path 1: Native `read_file` + Local `encode-1fps` / `crop`** | **YES** | `encode-1fps` + `read_file` on `.1fps.<first>-<last>.mp4`; `read_file` on `<100 MB` native-FPS `.mp4` + `.png`/`.jpg`; local `crop`. | **Never** when Path 1 satisfies the task. | `gemini_media.py encode-1fps <video.mp4>` / `gemini_media.py crop <img.png>` + native `read_file` |
| **Path 2A: `gemini-api` Static High-FPS & Frame-Span Slicing** | **NO** on `>100 MB` files or raw high-FPS video without `.1fps.mp4` (`read_file` samples at `1 fps`) | Use `.1fps.mp4` via `read_file` whenever present or generatable via `encode-1fps`. | Raw high-FPS video without `.1fps.mp4`, or slicing `[first..last]` spans from an uploaded `>100 MB` master video. See [`references/video_static_and_slicing.md`](references/video_static_and_slicing.md). | `gemini_media.py slice <video_or_file_id> --first F --last L --prompt "..."` |
| **Path 2B: `gemini-api` Opt-In Agentic Video (`"processing": "agentic"`)** | **NO** (`read_file` has no `>100 MB` support or dynamic agentic pass) | Use `.1fps.mp4` parts via `read_file` when inspecting short clips (`<5 min`). | Long single-canvas videos (`>5–10 min` or `>100 MB`) or mixed `agentic` (master video) + `static` (candidate clip). **BANNED on multi-panel/stacked strips.** See [`references/video_agentic.md`](references/video_agentic.md). | `gemini_media.py agentic-video <master.mp4> [--compare-clip <clip.mp4>] --prompt "..."` |
| **Path 3A: `gemini-api` `0..1000` `box_2d` & Polygon `mask`** | **NO** (chat text is not schema-calibrated to `0..1000` `box_2d`/`mask` heads) | Check existing local `.json` / `.npz` detector outputs with Python first. | Zero-VRAM `0..1000` `box_2d` / `mask` grounding descaled to exact image pixels (`xyxy` & `ltwh`), plus optional IoU matching (`--match-boxes`). See [`references/image_boxes_and_masks.md`](references/image_boxes_and_masks.md). | `gemini_media.py boxes <frame.png> [--ref <pic.png>] [--match-boxes <path>] [--with-masks] --prompt "..."` |
| **Path 3B: `gemini-api` Agentic Image Zoom (`code_execution` + `ultra_high`)** | **YES** via local `gemini_media.py crop` + `read_file` | Crop tiles or compute pixel math locally (`gemini_media.py crop` or `PIL`/`cv2`/`numpy`) and call `read_file` on the crop. | Only when remote sandboxed `code_execution` + `"resolution": "ultra_high"` is explicitly needed (or for the Gemini 3/4 `media_resolution` token table). See [`references/image_agentic_zoom.md`](references/image_agentic_zoom.md). | `gemini_media.py zoom <grid.jpg> --prompt "..."` |
| **Path 4: `gemini-api` Speaker & Frame-Span Transcription** | **YES** on `<100 MB` clips (`read_file` + local audio tools) | Call `read_file` on the `<100 MB` video/audio clip (plus local VAD/audio tools if available). | Only on `>100 MB` videos or when multi-speaker visual+audio attribution (`--visual-speakers`) mapped to exact frame numbers is needed. See [`references/audio_and_transcription.md`](references/audio_and_transcription.md). | `gemini_media.py transcribe-spans <clip.mp4> [--shot-first F] [--visual-speakers]` |

---

## 1. Path 1 (Mandatory Default): Local `encode-1fps` + Native `read_file`

Use this path for all `<100 MB` video clips, frame-by-frame QA, and multi-panel comparison videos:

1. **Generate `.1fps.` companions on demand (`gemini_media.py encode-1fps`)**:
   - If `<stem>.1fps.<first:05d>-<last:05d>.mp4` does not already exist alongside the clip, generate it locally:
     ```bash
     python3 "<plugin-root>/skills/video-understanding/scripts/gemini_media.py" encode-1fps path/to/clip.mp4 --burn-frame-numbers
     ```
   - Each source frame is held for `1.0s` (`-r 1`, muted, `-c:v libx264 -crf 18 -pix_fmt yuv420p`) in parts capped under `80,000,000` bytes (safely under `read_file`'s `100 MB` ceiling).
2. **Every-frame visual QA**:
   - Call `read_file` on `<stem>.1fps.<first>-<last>.mp4`. Because `read_file` samples video at `1 fps` midpoints (`t ≈ N + 0.5s`), timestamp `00:00` maps `1:1` to source frame `first`, `00:01` to `first + 1`, through `00:(N-1)` to `last` with zero boundary drift.
3. **Audio and real-time cadence QA**:
   - Call `read_file` on the companion native-FPS `.mp4` (`<stem>.mp4`) to inspect audio sync, vocal delivery, and real-time motion cadence.

---

## 2. Global `gemini-api` Rules (When Escalation Is Permitted)

1. **Flexible model selection (`-m "${GEMINI_VIDEO_MODEL:-gemini-3.8-flash}"`)**:
   - Omit `"model"` from `--body` JSON payloads and pass `-m "${GEMINI_VIDEO_MODEL:-gemini-3.8-flash}"` on the CLI so callers can switch models (`gemini-3.8-flash` default, `gemini-4-argon`, `gemini-flash-latest`, `gemini-3.6-flash`, `gemini-3.5-flash-lite`, or future models in `gemini-api models`) without editing JSON templates.
2. **Built-in credential store (`gemini-api configure` / `gemini-api auth login`)**:
   - Credentials live in `gemini-api`'s OS keychain or user config (`--no-keyring`), checked via `gemini-api whoami`, or in `GEMINI_API_KEY`. Never reference key file paths, run `cat` on secret files, or pass raw keys inline. If `gemini-api whoami` reports `--api-key [unset]`, stop and ask the user to run `gemini-api configure` or `gemini-api auth login`.
3. **Delete remote `Files API` uploads immediately after use**:
   - Local files under `~12 MB` (`<20 MB` base64) can be sent inline with zero cleanup. Uploaded `files/<id>` objects persist for `48h` against the `20 GB` project quota unless deleted with `gemini-api files delete "$FILE_ID"`.
