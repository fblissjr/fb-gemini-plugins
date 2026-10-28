# Path 2A: Static Video Processing, Frame-Span Slicing, and File Input Methods

Companion reference to [`../SKILL.md`](../SKILL.md).

## 0. Native-First Gate (`agy` Check Before Using Path 2A)

- **Never use Path 2A on a `<100 MB` local clip that already has (or can be given via `encode-1fps`) a `<stem>.1fps.<first>-<last>.mp4` companion**: Call `agy`'s built-in `read_file` tool on `.1fps.mp4` (and on the native-FPS `.mp4` for audio) at `$0` API spend. [`../scripts/gemini_media.py`](../scripts/gemini_media.py) mechanically refuses local `<100 MB` videos when a `.1fps.*.mp4` sibling exists on disk.
- **When Path 2A IS permitted**:
  1. Slicing a `[first..last]` frame span (`start_offset` / `end_offset` at the video's frame rate) out of a `>100 MB` master video that exceeds `read_file`'s `100 MB` cap, or
  2. Inspecting a raw high-FPS video at its native frame rate when `.1fps.mp4` does not exist and cannot be generated locally (since `read_file` samples raw video at `1 fps`).
- **Media privacy gate**: Always ask the user and name the file before uploading local media via `gemini-api`.

---

## 1. How Static Video Processing Works (API Default)

By default, all Gemini models (including Gemini 4 Argon and Gemini 3.8 Flash) process video in **static** mode (`"processing": "static"` or `{"type": "static", ...}`):
- **Default sampling**: Extracts `1 frame/second` (`1 fps`) and places all extracted frames into context in a single pass, alongside single-channel audio (`32 tokens/s`).
- **Why use Static over Agentic on short clips (`<5 min`)**: Static processing avoids the extra thinking tokens (`total_thought_tokens`) and tool-call round-trips (`total_tool_use_tokens`) incurred by timeline navigation when most or all of a short clip is relevant.
- **Per-item `resolution` on video (Gemini 3 and Gemini 4)**:
  - `"low"` / `"medium"` / `"unspecified"` (default): `~70 visual tokens/frame` (`~100 tokens/s` with audio and metadata).
  - `"high"`: `~280 visual tokens/frame` (`~300 tokens/s` with audio and metadata). **Always set `"resolution": "high"` when reading burned-in frame numbers, fine visual boundaries, or multi-panel diagnostic strips.**

---

## 2. File Input Methods (`gemini-api`)

| Method | Size Limit | Retention / Cleanup | Best Use |
| :--- | :--- | :--- | :--- |
| **Inline (`gemini-api analyze -i <path>`)** | `<20 MB` total request (`~12 MB` raw file before base64) | Stateless (no remote object created) | Quick single-still, pair-still, or tiny clip questions where custom `VideoContent.processing` is not needed |
| **Files API (`gemini-api files upload <path> --wait`)** | Up to `2 GB` per file (`20 GB` project quota) | `48 hours` TTL; delete immediately after use with `gemini-api files delete "$FILE_ID"` | Any high-FPS static inspection, `start_offset`/`end_offset` frame-span slicing, or `>12 MB` video |
| **GCS Registration (`gemini-api files register gs://...`)** | GCS object limit | Registered reference (no copy) | Cloud-hosted video/audio assets |

> **CLI quirk (`v0.4.4`)**: Never pass `-i files/<id>` to `gemini-api generate` or `gemini-api analyze` when you need custom `"processing"` (`fps`, `start_offset`, `end_offset`, or `agentic`); the CLI serializes `-i files/<id>` as `{"type": "document", "uri": "..."}`. Always pass `--body` to `gemini-api agent run` with an explicit `"type": "video"` block and place the `"type": "text"` prompt **after** the video part.

---

## 3. Whole-Clip High-FPS Static Inspection

Use when inspecting a short raw video clip at its native frame rate (e.g., `24` or `30 fps`) when a `.1fps.<first>-<last>.mp4` companion cannot be used:

```bash
FILE_ID=$(gemini-api files upload "$CLIP_PATH" --wait)

gemini-api agent run -m "${GEMINI_VIDEO_MODEL:-gemini-3.8-flash}" --stream=false -o json --body "{
  \"input\": [
    {
      \"type\": \"video\",
      \"uri\": \"https://generativelanguage.googleapis.com/v1beta/${FILE_ID}\",
      \"mime_type\": \"video/mp4\",
      \"resolution\": \"high\",
      \"processing\": {\"type\": \"static\", \"fps\": 24}
    },
    {
      \"type\": \"text\",
      \"text\": \"Inspect every frame at 24 fps and report exact frame numbers or timestamps.\"
    }
  ]
}"

gemini-api files delete "$FILE_ID"
```

---

## 4. Server-Side Frame-Span Slicing (`start_offset` / `end_offset`)

Instead of running `ffmpeg` and uploading a separate file for each shot when inspecting a large master video (`>100 MB`), upload the video **once** and slice any `[first..last]` frame span on the server using `start_offset` and `end_offset` (in seconds) for the video's frame rate ($\text{FPS}$):

$$\text{start\_offset} = \frac{\text{first}}{\text{FPS}}, \qquad \text{end\_offset} = \frac{\text{last} + 1}{\text{FPS}}$$

### Using `scripts/gemini_media.py slice` (Recommended)

`gemini_media.py slice` automatically probes the video's native frame rate via `ffprobe` when a local path is provided (or uses `--fps`, defaulting to `24.0` for remote `files/<id>` URIs):

```bash
# Upload the master video once for the session:
FILE_ID=$(gemini-api files upload "$MASTER_MP4" --wait)

# Inspect frames 1200..1271 at 24 fps high resolution (computes start_offset/end_offset automatically):
python3 "<plugin-root>/skills/video-understanding/scripts/gemini_media.py" slice "$FILE_ID" \
  --first 1200 --last 1271 --fps 24 \
  --prompt "Inspect the subject transition across frames 1200 to 1271."

# Clean up when finished with all slices:
gemini-api files delete "$FILE_ID"
```

### Direct `gemini-api` Command

```bash
FPS=24.0
START_S=$(awk "BEGIN {printf \"%.3f\", 1200 / ${FPS}}")
END_S=$(awk "BEGIN {printf \"%.3f\", (1271 + 1) / ${FPS}}")

gemini-api agent run -m "${GEMINI_VIDEO_MODEL:-gemini-3.8-flash}" --stream=false -o json --body "{
  \"input\": [
    {
      \"type\": \"video\",
      \"uri\": \"https://generativelanguage.googleapis.com/v1beta/${FILE_ID}\",
      \"mime_type\": \"video/mp4\",
      \"resolution\": \"high\",
      \"processing\": {
        \"type\": \"static\",
        \"start_offset\": ${START_S},
        \"end_offset\": ${END_S},
        \"fps\": 24
      }
    },
    {
      \"type\": \"text\",
      \"text\": \"Inspect this frame slice at 24 fps and report any visual or transition artifacts.\"
    }
  ]
}"
```
