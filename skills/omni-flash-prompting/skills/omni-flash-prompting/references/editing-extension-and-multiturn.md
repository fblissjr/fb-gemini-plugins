# Video Editing, Horizon Extensions, Audio Control & Multi-Turn Workflows (`gemini-omni-1.2-flash`)

This reference covers the **Minimal Delta + Anchor Rule** for video editing, the **Audio Stream Gate** (`keep` vs. `ffmpeg -an` full regeneration), **Horizon Extensions** (`3s–10s` per turn up to `30s–40s`), **Prompt-Only Reference Injection** during extensions, and **Interactions API** payload configuration for `gemini-omni-1.2-flash`.

---

## 1. The Minimal Delta + Anchor Rule for Video Editing

When editing an existing video (`<=10s` uploaded source clip or a previous generation via `previous_interaction_id`), **simple, surgical prompts outperform long descriptive prompts**. Re-describing the existing scene causes the model to re-interpret and re-synthesize background details, lighting, or character motions that you wanted to preserve.

### The Formula
> **`[Plain Imperative Modification] + "Keep everything else the same."`**
> *(Or for high-precision commercial/VFX work: **`"Keep [Anchor Element 1, Anchor Element 2, and Camera Framing] identical to the source video, only change [Target Element]."`**)*

### 10 Side-by-Side Prompt Refactors (`Avoid` vs. `Omni 1.2 Optimal`)

| Edit Category | Verbose Prompt (Avoid — Causes Drift) | Minimal Delta + Anchor Prompt (Use This) |
| :--- | :--- | :--- |
| **1. Style Transfer** | *"Take this video of a city street with cars driving by and transform the entire aesthetic into a detailed vibrant Japanese anime film with cel shading."* | `"Make this video Japanese anime style. Keep everything else the same."` |
| **2. Adding an Subject/Pet** | *"In the video of the man sitting on the sofa in the living room, please add a small black cat that runs from the right side of the screen, jumps onto his lap, and then he starts to stroke its head while looking down."* | `"Add a small black cat that jumps onto his lap, and he begins to pet it. Keep everything else the same."` |
| **3. Object Removal (Inpainting)** | *"Please remove the cell phone that the person is holding in their hand and fill in the background so it looks like they are just holding their hand empty."* | `"Make the phone invisible. Keep everything else the same."` |
| **4. Wardrobe / Accessory Edit** | *"Keep the woman walking down the sidewalk but put a stylish wide-brimmed burgundy felt hat on her head that matches her coat."* | `"Put a fashionable burgundy felt hat on this person. Keep everything else the same."` |
| **5. Product / Liquid Swap** | *"Reshoot this close-up pouring shot so that instead of dark melted chocolate being poured over the dish, rich melted cheddar cheese is poured with the exact same hand motion."* | `"Keep the hand movement and background lighting identical to the source video, but replace the chocolate being poured with melted cheese."` |
| **6. Background / Environment Swap** | *"Change the medieval marketplace behind the knight in polished steel armor into a misty oak forest while keeping his walk and armor reflections."* | `"Swap the background to an oak forest while keeping the character's performance, armor reflections, and camera framing completely intact."` |
| **7. Relighting & Weather** | *"Modify the sunny afternoon street scene so it looks like a dramatic Moody cyberpunk night during a rainstorm with neon reflections."* | `"Change the lighting and weather to a rainy night with dramatic neon reflections. Keep everything else the same."` |
| **8. In-Scene Sign / Text Swap** | *"Find the wooden street sign in the background of the shot and rewrite the letters on it so that it reads Omni Flash instead."* | `"Change the text on the sign to say \"Omni Flash\". Keep everything else the same."` |
| **9. Product Colorway Iteration** | *"Update the sneaker shown rotating on the turntable so the upper mesh is emerald green instead of red, without changing the sole or logo."* | `"Change the sneaker's upper mesh colorway to emerald green. Keep the sole, logo typography, lighting, and turntable rotation identical to the source video."` |
| **10. Reference-Guided Object Swap** | *"Replace the guitar the musician is holding in the video with the vintage sunburst bass guitar shown in the uploaded reference image."* | `"Replace the guitar with the bass guitar in <IMAGE_REF_0>. Keep the musician's hands, performance, and stage lighting the same."` |

---

## 2. The Audio Stream Gate: Preserve vs. Regenerate from Scratch

When editing a source video, Gemini Omni Flash inspects the input file's container streams before deciding how to handle audio:

| Desired Audio Outcome | Input Video Preparation | Prompt Instruction | Why This Matters |
| :--- | :--- | :--- | :--- |
| **Path A: Keep or Slightly Adapt Original Audio** *(Default)* | Upload the source `.mp4` **with its original audio stream intact**. | Optional: `"Keep the original dialogue and room acoustics."` | When an audio stream is present, Omni Flash preserves the existing voice, timing, and soundscape (adapting subtly to visual edits). |
| **Path B: Regenerate All Audio from Scratch** *(New Genre / New Foley / New Score)* | **Strip the audio stream before uploading**:<br>`ffmpeg -i input.mp4 -c:v copy -an input_silent.mp4` | Describe the new soundscape explicitly: `"Transform the style to 1920s silent-era slapstick with an upbeat ragtime piano track and crisp comedic sound effects."` | **Critical Trap**: If *any* audio stream remains on an uploaded video, Omni Flash will attempt to preserve/modify it rather than synthesizing a fresh audio track from scratch. |

> [!WARNING]
> **Voice Editing Limitation**: Direct voice editing (changing the timbre or words of an existing recorded voice track inside an uploaded video) is not supported. Either keep the original spoken audio (Path A) or strip the audio stream (Path B) to generate a new ambient/musical soundscape.

---

## 3. Horizon Extensions (`3s–10s` per Turn, Up to `30s–40s` Total)

Gemini Omni Flash can extend a video by appending `3s–10s` per turn to the **end** of the clip (prepending before `0s` or inserting into the middle of a clip is not supported).

### A. How Context Blending Works
- Omni Flash uses the **last `10s`** of your video as context to maintain visual, motion, character, and audio coherence.
- A few final frames of the source video are blended/edited at the seam so the transition into the extended segment is seamless.
- Uploaded source videos for extension must be **`<=10s`** in length. Longer extensions (`20s`, `30s`, up to `40s`) are built turn-by-turn via **`previous_interaction_id`**.

### B. The Prompt-Only Extension Unlock (Why You Should Omit `task="extend"`)
In the Interactions API, `video_config` supports an optional `task` field (`"text_to_video"`, `"image_to_video"`, `"reference_to_video"`, `"edit"`, `"extend"`).
- **The Trap**: If you explicitly set `task="extend"`, the API **disables multimodal reference inputs** (`<IMAGE_REF_N>` and `<VIDEO_REF_N>` cannot be passed).
- **The Unlock**: **Omit `task="extend"`** and trigger the extension purely via your prompt text (`"Extend this video."` or `"The scene continues."`). This allows you to pass reference images and reference videos simultaneously during an extension:

```text
Extend this video. The camera pans toward the doorway as the character in <IMAGE_REF_0> enters the room and performs the dance move in <VIDEO_REF_0>. The background music transitions smoothly into the chorus.
```

### C. Relative `0s` Timecodes in Extensions
When you use timestamps or `[start-end s]` brackets inside an extension prompt, **`0s` always refers to the start of the newly extended segment**, not the beginning of the original video:
- *Example*: If you extend a `10s` video and prompt `"After 2s, cut to a wide aerial shot of the same characters"`, the cut occurs at **`12s`** (`10s + 2s`) in the final combined video.

### D. Spoken Dialogue Rules in Extensions
- **Uploaded Videos with Speech**: You **cannot** extend an *uploaded* video where someone is speaking in order to add new spoken dialogue (extensions work if the character stays silent or the prompt does not request new dialogue).
- **Model-Generated Videos (`previous_interaction_id`)**: Adding new spoken dialogue **is supported** when extending a video that was generated by Omni Flash in a prior turn via `previous_interaction_id`.

---

## 4. Multi-Turn Stateful Editing & The Draft-to-Upscale Loop

Gemini Omni 1.2 Flash reduces `720p` draft pricing by 30% to **\$0.07/second** (\$12.00 per 1M output video tokens) and links turns via `previous_interaction_id`.

### Recommended 3-Step Production Workflow

```python
import base64
from google import genai
from google.genai import interactions

client = genai.Client()

# Turn 1: Fast 15s Draft at 720p ($0.07/s = $1.05) with store=True (default)
turn1 = client.interactions.create(
    model="gemini-omni-1.2-flash",
    input=(
        "Continuous, unbroken tracking shot of a knight in polished steel armor "
        "walking through a bustling medieval marketplace at golden hour. "
        "Sound design: clinking armor, distant market chatter, lute music. No dialogue."
    ),
    generation_config=interactions.GenerationConfig(
        video_config=interactions.VideoConfig(
            duration_seconds=15,
        )
    ),
    response_format={
        "type": "video",
        "aspect_ratio": "16:9",
        "resolution": "720p",
    },
)

# Turn 2: Conversational Background Swap via previous_interaction_id (No re-upload!)
turn2 = client.interactions.create(
    model="gemini-omni-1.2-flash",
    previous_interaction_id=turn1.id,
    input=(
        "Swap the background to a misty oak forest while keeping the knight's "
        "performance, steel armor reflections, and camera framing completely intact."
    ),
)

# Turn 3: Final High-Resolution Render (1080p or 4k) using URI delivery for >4 MB payloads
turn3 = client.interactions.create(
    model="gemini-omni-1.2-flash",
    previous_interaction_id=turn2.id,
    input="Render this exact scene in ultra-crisp 4K detail. Keep everything else the same.",
    response_format={
        "type": "video",
        "aspect_ratio": "16:9",
        "resolution": "4k",
        "delivery": "uri",
    },
)
```

### Interactions API Performance & Delivery Knobs

| Parameter / Setting | Values | When to Use |
| :--- | :--- | :--- |
| **`model`** | `"gemini-omni-1.2-flash"` | Default GA model for 3s–15s generation, conversational editing, and reference lock. |
| **`duration_seconds`** | `3..15` (integer, default `10`) | Set in `generation_config.video_config` for single-pass clip length (`3s–15s`). |
| **`aspect_ratio`** | `"16:9"`, `"9:16"` | Landscape (`16:9`) or vertical social/mobile (`9:16`). Can also be changed across turns! |
| **`resolution`** | `"360p"`, `"720p"` (default), `"1080p"`, `"4k"` | Draft and iterate at `360p`/`720p`; render final keepers at `1080p` or `4k` (`24 FPS`). |
| **`delivery`** | `"inline"` (default), `"uri"` | Always set `"delivery": "uri"` in `response_format` when output video exceeds `4 MB` (`1080p`, `4k`, or long `15s` clips), then poll `client.files.get(...)` until `ACTIVE` and download. |
| **`store` / `background` / `stream`** | `false` for one-shot speed; `store=true` for multi-turn | Setting `background=false`, `store=false`, `stream=false` optimizes synchronous one-shot latency, **but `store=false` disables `previous_interaction_id`** for subsequent turns. Keep `store=true` whenever multi-turn editing is planned. |
