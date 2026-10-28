# Path 3A: Image Understanding — 2D Bounding Boxes, Polygon Segmentation & Detector Matching

Companion reference to [`../SKILL.md`](../SKILL.md).

## 0. Native-First Gate (`agy` Check Before Using Path 3A)

- **Inspect existing local detector outputs first (`$0` API spend)**: Before calling `gemini-api` for bounding boxes or masks, check whether local detector outputs (`.json` bounding boxes or `.npz` segmentation masks) already cover the target object on that frame using Python and `agy`'s built-in `read_file` tool on the image.
- **When Path 3A IS permitted**:
  1. `agy` cannot produce schema-calibrated `0..1000` `box_2d` / polygon `mask` JSON natively from chat text, and
  2. You need zero-VRAM `0..1000` `box_2d` / `mask` grounding—for example, to locate a specific subject or object across frames using a reference still (`--ref`), extract a polygon segmentation contour, or disambiguate which local detection box matches a visual query (`--match-boxes`).
- **Media privacy gate**: Always ask the user and name the file before uploading local media via `gemini-api`.

---

## 1. Key Use Cases for `box_2d` & Polygon `mask` Grounding

1. **Multi-Image Reference-Conditioned Object / Subject Localization (`--ref`)**:
   - Pass a reference image alongside a target scene frame in a multi-image prompt to locate that specific person, product, or UI element after a camera cut or occlusion.
   - Convert Gemini's normalized `[ymin, xmin, ymax, xmax]` (`0..1000`) box to pixel coordinates (`box_xyxy_px` and `box_ltwh_px`) on the image's canvas `(W, H)`.
2. **Zero-VRAM Polygon Segmentation (`--with-masks`)**:
   - Request polygon contours (`[[x, y], ...]` in `0..1000`, automatically descaled to pixel vertices `mask_polygon_px`) when a local GPU segmentation model is unavailable or missed a fine region.
3. **Snapping to Local Detector Boxes or Masks (`--match-boxes`)**:
   - Match Gemini's grounded box against a local detector's candidate boxes (from a JSON file of `xyxy`/`ltwh` boxes or a bit-packed `.npz` mask archive) by Intersection-over-Union (`IoU >= 0.50`).

---

## 2. Coordinate Convention Warning (`[ymin, xmin, ymax, xmax]` in `0..1000`)

- **Gemini `box_2d`**: Always `[ymin, xmin, ymax, xmax]` (note **`y` first, `x` second**!) scaled to `[0, 1000]`.
- **Gemini `mask`**: Polygon list of `[[x, y], ...]` vertices scaled to `[0, 1000]`.
- **Descaling formula for canvas `(W, H)`**:
  $$x_1 = \frac{\text{xmin}}{1000} \cdot W, \quad y_1 = \frac{\text{ymin}}{1000} \cdot H, \quad x_2 = \frac{\text{xmax}}{1000} \cdot W, \quad y_2 = \frac{\text{ymax}}{1000} \cdot H$$
  $$\text{LEFT} = x_1, \quad \text{TOP} = y_1, \quad \text{WIDTH} = x_2 - x_1, \quad \text{HEIGHT} = y_2 - y_1$$

---

## 3. One-Command Grounding + Detector IoU Snap (`scripts/gemini_media.py boxes`)

Use [`../scripts/gemini_media.py`](../scripts/gemini_media.py) to run detection/segmentation, automatically read the image's `(W, H)` dimensions (or use `--target-size WxH`), descale `[ymin, xmin, ymax, xmax]` to both `[x1, y1, x2, y2]` (`box_xyxy_px`) and `[left, top, width, height]` (`box_ltwh_px`) without `x`/`y` transposition risk, and optionally match against local detections:

```bash
# Detect a target subject using a reference still and return pixel boxes + polygon masks:
python3 "<plugin-root>/skills/video-understanding/scripts/gemini_media.py" boxes "$FRAME_PNG" \
  --ref "$REF_STILL_PNG" \
  --prompt "Locate the subject from the first reference image in the second scene frame." \
  --with-masks

# Optionally snap to local detector boxes (.json or bit-packed .npz):
python3 "<plugin-root>/skills/video-understanding/scripts/gemini_media.py" boxes "$FRAME_PNG" \
  --prompt "Locate the primary speaker." \
  --match-boxes "$LOCAL_DETECTIONS_JSON_OR_NPZ" \
  --frame 120
```

The JSON output includes:
- `box_2d_1000`: raw `[ymin, xmin, ymax, xmax]` (`0..1000`)
- `box_xyxy_px`: `[x1, y1, x2, y2]` in image pixels
- `box_ltwh_px`: `[left, top, width, height]` in image pixels
- `mask_polygon_px`: `[[x_px, y_px], ...]` when `--with-masks` is passed
- `detector_match`: when `--match-boxes` is supplied, reports `best_iou`, `passes_0_50_gate`, and the matched detector box in `[left, top, width, height]` coordinates.

---

## 4. Direct `gemini-api` Structured JSON Call (`box_2d` + `mask`)

When calling `gemini-api agent run` directly for segmentation masks, set `"thinking_level": "minimal"` in `"generation_config"` and `"resolution": "high"` on the image input:

```bash
FILE_ID=$(gemini-api files upload "$FRAME_PNG" --wait)

gemini-api agent run -m "${GEMINI_VIDEO_MODEL:-gemini-3.8-flash}" --stream=false -o json --body "{
  \"input\": [
    {
      \"type\": \"image\",
      \"uri\": \"https://generativelanguage.googleapis.com/v1beta/${FILE_ID}\",
      \"mime_type\": \"image/png\",
      \"resolution\": \"high\"
    },
    {
      \"type\": \"text\",
      \"text\": \"Detect the primary objects. Return box_2d as [ymin, xmin, ymax, xmax] normalized to 0-1000, mask as a polygon of [x, y] coordinates normalized to 0-1000, and a descriptive label.\"
    }
  ],
  \"response_format\": {
    \"type\": \"text\",
    \"mime_type\": \"application/json\",
    \"schema\": {
      \"type\": \"object\",
      \"properties\": {
        \"boxes\": {
          \"type\": \"array\",
          \"items\": {
            \"type\": \"object\",
            \"properties\": {
              \"box_2d\": {\"type\": \"array\", \"items\": {\"type\": \"integer\"}},
              \"mask\": {\"type\": \"array\", \"items\": {\"type\": \"array\", \"items\": {\"type\": \"integer\"}}},
              \"label\": {\"type\": \"string\"}
            },
            \"required\": [\"box_2d\", \"mask\", \"label\"]
          }
        }
      },
      \"required\": [\"boxes\"]
    }
  },
  \"generation_config\": {
    \"thinking_level\": \"minimal\"
  }
}"

gemini-api files delete "$FILE_ID"
```
