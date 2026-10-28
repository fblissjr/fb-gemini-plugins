# Path 3B: Agentic Vision (`code_execution` Zoom-and-Inspect) & Per-Item `media_resolution`

Companion reference to [`../SKILL.md`](../SKILL.md).

## 0. Native-First Gate (`agy` Check Before Using Path 3B)

- **Inside the Antigravity (`agy`) harness, `agy` can already crop, zoom, and compute pixel math locally at `$0` API spend**:
  1. Call `read_file` directly on the `.png` / `.jpg` image (contact sheets, diagnostic grids, charts, or extracted frames).
  2. If a tile is small or you need RGB/luma pixel measurements, run `gemini_media.py crop` (or a local Python `PIL`/`cv2`/`numpy` snippet) to crop the exact region to `/tmp/crop.png`, then call `read_file` on `/tmp/crop.png`:
     ```bash
     python3 "<plugin-root>/skills/video-understanding/scripts/gemini_media.py" crop "$IMAGE_PATH" \
       --box 256,128,768,512 --out /tmp/crop.png
     ```
- **When Path 3B (`gemini_media.py zoom`) IS permitted**:
  - Only when you specifically need an external model in `gemini-api` to run autonomous remote sandboxed `code_execution` (`tools: [{"type": "code_execution"}]` + `"resolution": "ultra_high"`) or when referencing the Gemini 3 / Gemini 4 per-item `media_resolution` token table below for `gemini-api` calls.
- **Media privacy gate**: Always ask the user and name the file before uploading local media via `gemini-api`.

---

## 1. Per-Content-Item `media_resolution` Token Table (Gemini 3 & Gemini 4)

Gemini 3 and Gemini 4 models allow setting `"resolution"` on **each individual media item** inside the `input` array. You can mix resolutions in a single request (for example, `"resolution": "low"` on a clean reference image and `"resolution": "ultra_high"` on a dense multi-row contact sheet or architectural diagram):

| `resolution` Value | Image Tokens (Gemini 3 / 4) | Video Tokens / Frame (Gemini 3 / 4) | Audio Tokens / Sec | Recommended Use |
| :--- | :--- | :--- | :--- | :--- |
| `"unspecified"` (Default) | `1120` | `70` | `25` | General single-still questions |
| `"low"` | `280` | `70` | `25` | Reference stills passed for coarse identity or style context |
| `"medium"` | `560` | `70` | `25` | Routine frame pair comparisons |
| `"high"` | `1120` | `280` | `25` | **Mandatory for high-FPS static video QA**, burned-in frame numbers, and `box_2d` grounding |
| `"ultra_high"` | `2240` | N/A (image item only) | N/A | **Dense contact sheets**, multi-row diagnostic strips, fine UI screenshots, and small-print diagrams |

---

## 2. How Agentic Vision (`tools: [{"type": "code_execution"}]`) Works on Images

While `"processing": "agentic"` on **video** is banned on multi-panel strips because server-side video cropping cannot see the tile grid layout, **Code Execution with Images** (`tools: [{"type": "code_execution"}]` on an **image** input) works differently and is purpose-built for dense visual artifacts:
- The model receives the full image at `"resolution": "ultra_high"` (`2240 tokens`) and writes explicit Python code (`PIL`, `numpy`, `matplotlib`) in its sandbox to:
  1. **Zoom and inspect**: Crop specific tile coordinates or labels (`code_execution_call`) and re-examine the cropped high-resolution patch in the next step (`code_execution_result`).
  2. **Visual math & pixel measurement**: Compute RGB/luma channel shifts or count grid cells.
  3. **Annotate**: Draw bounding boxes or arrows on an output image to prove where an artifact sits.

---

## 3. Running Agentic Image Zoom (`scripts/gemini_media.py zoom` or Direct CLI)

### Using `scripts/gemini_media.py zoom`

```bash
python3 "<plugin-root>/skills/video-understanding/scripts/gemini_media.py" zoom "$CONTACT_SHEET_JPG" \
  --prompt "Crop into each flagged tile, read the burned-in frame number, and describe any boundary or rendering artifacts."
```

### Direct `gemini-api` Command

```bash
FILE_ID=$(gemini-api files upload "$CONTACT_SHEET_JPG" --wait)

gemini-api agent run -m "${GEMINI_VIDEO_MODEL:-gemini-3.8-flash}" --stream=false -o json --body "{
  \"input\": [
    {
      \"type\": \"image\",
      \"uri\": \"https://generativelanguage.googleapis.com/v1beta/${FILE_ID}\",
      \"mime_type\": \"image/jpeg\",
      \"resolution\": \"ultra_high\"
    },
    {
      \"type\": \"text\",
      \"text\": \"Use Python code to crop and zoom into the individual tiles in this contact sheet. Report the exact frame numbers and describe the visual details on each tile.\"
    }
  ],
  \"tools\": [
    {\"type\": \"code_execution\"}
  ]
}"

gemini-api files delete "$FILE_ID"
```
