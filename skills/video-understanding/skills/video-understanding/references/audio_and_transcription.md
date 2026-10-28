# Path 4: Audio & Active-Speaker Transcription (`gemini_media.py transcribe-spans` & `gemini-api transcribe`)

Companion reference to [`../SKILL.md`](../SKILL.md).

## 0. Native-First Gate (`agy` Check Before Using Path 4)

- **Always use `agy`'s built-in `read_file` tool (plus local audio/VAD tools if present) on `<100 MB` clips first (`$0` API spend)**:
  1. Call `read_file` on the `<100 MB` video/audio clip (and `.1fps.<first>-<last>.mp4` if inspecting frame-by-frame lip sync) to hear the audio and visually see which on-screen speaker is active.
  2. If your workspace includes a local VAD or stem-separation tool, run it locally first.
- **When Path 4 (`gemini_media.py transcribe-spans` or `gemini-api transcribe`) IS permitted**:
  1. The video or audio file exceeds `read_file`'s `100 MB` ceiling, or
  2. You specifically need structured multi-speaker JSON (`speaker`, `start_frame`, `end_frame`, `mouth_visibly_open`, `text`) with high-resolution visual speaker attribution (`--visual-speakers`) across a multi-person scene where audio-only VAD cannot tell which on-screen person is speaking or singing.
- **Media privacy gate**: Always ask the user and name the file before uploading local media via `gemini-api`.

---

## 1. Frame-Aligned Speaker Spans (`scripts/gemini_media.py transcribe-spans`)

`scripts/gemini_media.py transcribe-spans` converts `MM:SS(.mmm)` transcript segments directly into inclusive `[start_frame, end_frame]` spans at the video's frame rate (auto-probed via `ffprobe` or specified via `--fps`):

```bash
# Audio-only or multimodal (--visual-speakers) speaker span extraction mapped to video frame numbers:
python3 "<plugin-root>/skills/video-understanding/scripts/gemini_media.py" transcribe-spans "$CLIP_MP4" \
  --shot-first 0 \
  --visual-speakers \
  --prompt "Identify which on-screen person is speaking or singing and transcribe the exact words."
```

- Without `--visual-speakers`, `transcribe-spans` runs audio-focused timestamp transcription.
- With `--visual-speakers`, `transcribe-spans` passes `"type": "video"`, `"resolution": "high"`, and `"processing": {"type": "static", "fps": <fps>}` (plus `start_offset`/`end_offset` when `--slice-master` is set) so the model sees lip movement at native FPS while transcribing audio.
- **Timestamp-to-frame formula**:
  $$\text{frame} = \text{shot\_first} + \text{round}(t_{\text{seconds}} \times \text{FPS})$$

---

## 2. Direct CLI Transcription (`gemini-api transcribe`)

For standalone audio/video files where frame-number conversion is not needed, `gemini-api transcribe` outputs `json`, `srt`, `vtt`, or `text` directly:

```bash
# JSON transcript with speaker labels and timestamps:
gemini-api transcribe -i "$CLIP_MP4" \
  -m "${GEMINI_VIDEO_MODEL:-gemini-3.8-flash}" \
  --format json \
  --out /tmp/transcript.json

# Or SRT captions:
gemini-api transcribe -i "$CLIP_MP4" \
  -m "${GEMINI_VIDEO_MODEL:-gemini-3.8-flash}" \
  --format srt \
  --out /tmp/transcript.srt
```
