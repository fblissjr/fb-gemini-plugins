# Prompt Architecture, Timecode Choreography & Media Role Tagging (`gemini-omni-1.2-flash`)

This reference covers the structural grammar of **Gemini Omni 1.2 Flash (`gemini-omni-1.2-flash`)** generation prompts, `3s–15s` timecode choreography, simple vs. explicit `[# Sources ...]` / `[# References ...]` role declarations, on-screen typography, and inline negative guardrails.

---

## 1. The 6-Layer Cinematic Spec for `3s–15s` Generation

Because `gemini-omni-1.2-flash` processes text, image, audio, and video natively in a single pass and defaults to cutting between multiple shots to tell a story, vague "vibe" prompts yield unpredictable shot cuts and generic audio. Structure every new generation prompt across these 6 ordered layers:

| Layer | Purpose | Key Directives & Examples |
| :--- | :--- | :--- |
| **1. Shot & Continuity Lock** | Overrides or directs Omni Flash's default multi-shot director behavior | • **Single unbroken shot**: `"Continuous, unbroken handheld shot in a single scene. No scene cuts."`<br>• **Planned montage**: `"Rapid-fire sequence cutting to a new location every 1 second (24 frames at 24fps)."` |
| **2. Subject & Material Micro-Detail** | Locks physical anatomy, costume design, product geometry, and surface properties | • Replace generic nouns (`"a sneaker"`) with exact material/color specs (`"a matte-white trail running shoe with cobalt-blue mesh panels, carbon-fiber heel clip, and sculpted lug sole"`).<br>• Add meta-prompting when needed: `"Apply costume design principles to characters. Consider micro-detail, expression, and timing."` |
| **3. Action, Physics & `[0-15s]` Beats** | Defines momentum, fluid/cloth dynamics, and temporal progression across up to `15s` | • Natural language: `"After 4 seconds, she turns toward the window; at 10 seconds, she opens the shutters."`<br>• Timecode brackets: `[0-5s] ... [5-10s] ... [10-15s] ...` |
| **4. Camera Trajectory & Framing** | Controls lens focal feel, camera movement, and angle continuity | • `"16:9 widescreen, low-angle 35mm tracking shot pushing in smoothly"`<br>• `"Continuous FPV drone flight skimming across a cobblestone piazza and rising through a glass dome"`<br>• `"180-degree orbital pan around the pedestal at constant eye level"` |
| **5. Lighting, Environment & `"Quoted"` Text** | Sets atmosphere, reflections, and exact readable text on signs, labels, or overlays | • `"Golden-hour sidelight casting long volumetric shadows through mist"`<br>• Wrap every rendered string in double quotes: `A street sign reads "OMNI BLVD", the cafe awning says "ESPRESSO", and the license plate reads "FLSH12".` |
| **6. Audio Direction & Inline Negatives** | Directs synthesized music/Foley/speech and embeds negative constraints | • `"Sound design: crisp footsteps on wet gravel, distant harbor foghorn, calm acoustic guitar track."`<br>• `"No dialogue. No scene cuts. No embellishments. No extra sound effects."` |

---

## 2. Timecode Choreography (`3s–15s` Native Canvas & `24 FPS` Frame Math)

Gemini Omni 1.2 Flash expands single-pass generation from `10s` to **`15s`** (configurable as any integer from `3` to `15` seconds at `24 FPS`).

### A. 3-Act `[0-15s]` Bracket Syntax
Use explicit bracketed spans (`[start-end s]`) so every beat has a dedicated temporal budget:

```text
[0-5s] Establishing tracking shot: a chef in a charcoal linen apron slices fresh basil on a walnut cutting board in a sunlit kitchen.
[5-10s] Medium close-up: he tosses the basil into a copper skillet where cherry tomatoes sizzle in olive oil, steam rising into the warm backlight.
[10-15s] Macro overhead shot: he plates the dish on a matte ceramic bowl and drizzles aged balsamic glaze. Sound design: rhythmic knife chops, gentle pan sizzle, warm acoustic jazz. No dialogue.
```

### B. Rapid-Fire & Rhythmic Frame Cuts (`24 FPS`)
Omni Flash understands both second-based and frame-based rhythm instructions at its native `24 FPS` cadence:
- **Half-second cuts (`12 frames`)**: `"In a rapid-fire sequence, every half a second (12 frames at 24fps) cut to a new macro angle of the watch mechanism."`
- **One-second cuts with kinetic labels (`24 frames`)**: `"Make a rapid-fire 10-second video that shows a different rare deep-sea bioluminescent creature every 1s, upbeat electronic music, include on-screen text in quotes to label each creature."`
- **Audio-visual drop sync**: `"At 6s the bass drops into the chorus in the background audio, synchronized with a whip-pan transition to the neon stage."`

---

## 3. Complete Media Role Binding Grammar

When uploading images or videos via the Files API (or inline base64) alongside your prompt, bind each asset to its exact role so Omni Flash never confuses a **reference image** with a **literal starting frame**, or a **motion reference video** with a **source video to edit**.

### A. Simple Role Tags (Recommended for 1–2 Clear Roles)

| Tag | Indexing | Max Count | Purpose & Rules | Example |
| :--- | :--- | :--- | :--- | :--- |
| **`<FIRST_FRAME>`** | Singleton | `1` | Uses the uploaded image as the literal frame `0` of the generated video. | `<FIRST_FRAME> The origami crane unfolds its wings and takes flight.` |
| **`<LAST_FRAME>`** | Singleton | `1` | Uses the uploaded image as the final frame for interpolation. **Must** be paired with `<FIRST_FRAME>`. Passing the **same image** to both creates a seamless loop. | `<FIRST_FRAME> <LAST_FRAME> A crystal prism rotating 360 degrees in place.` |
| **`<IMAGE_REF_N>`** | `0`-indexed (`0..5`) | Up to `6` *(up to 3 per character for 2 characters)* | Locks visual style, character identity, clothing, object geometry, or packaging typography without forcing the image to be frame `0`. | `In the painterly style of <IMAGE_REF_0>, detective <IMAGE_REF_1> inspects the compass <IMAGE_REF_2>.` |
| **`<VIDEO_REF_N>`** | `0`-indexed (`0..2`) | Up to `3` *(ideal length `~3s` each; audio is ignored)* | Transfers character likeness, object behavior, or movement/dance choreography from a reference video. | `The character <IMAGE_REF_0> performs the martial arts kata shown in <VIDEO_REF_0>.` |

#### Multi-Reference 6-Image Sequence Example
```text
[0-5s] A studio fashion sequence. Starting with woman <IMAGE_REF_0>, she is holding the handbag <IMAGE_REF_1>.
[5-10s] Then we see the man <IMAGE_REF_2> holding the briefcase <IMAGE_REF_3>.
[10-15s] And finally another woman <IMAGE_REF_4> who is holding the clutch <IMAGE_REF_5> while walking down the runway.
```

### B. Explicit Prefix Declarations (`[# Sources ...]` & `[# References ...]`)

When mixing multiple media inputs and roles (e.g., a starting frame + character reference image + motion reference video), place explicit declarations at the **very beginning** of the prompt and append **mandatory natural-language role guardrails** at the **very end**.

> [!IMPORTANT]
> **Index Mapping Rule**: In `[# Sources ...]` and `[# References ...]` headers, `@Image1`, `@Image2`, `@Video1` are **1-indexed** by their order in the API `input` array, whereas `<IMAGE_REF_0>`, `<IMAGE_REF_1>`, `<VIDEO_REF_0>` are **0-indexed** role tags used inside your prompt body.

| Scenario | Opening Prefix Declaration | Mandatory Closing Guardrail Sentence(s) |
| :--- | :--- | :--- |
| **Starting frame only** | `[# Sources <FIRST_FRAME>@Image1]` | `"Use this image as the starting frame."` |
| **First-to-last frame interpolation** | `[# Sources <FIRST_FRAME>@Image1 <LAST_FRAME>@Image2]` | `"Use Image1 as the starting frame and Image2 as the final frame."` |
| **Seamless loop (same start & end frame)** | `[# Sources <FIRST_FRAME>@Image1 <LAST_FRAME>@Image1]` | `"Use this image as the first frame and the last frame."` |
| **Starting frame + image reference** | `[# Sources <FIRST_FRAME>@Image1] [# References <IMAGE_REF_0>@Image2]` | `"Use Image1 as the starting frame. Use Image2 as a reference for the video generation. The reference image should not be used as a literal initial frame."` |
| **Source video for editing** | `[# Sources <VIDEO_0>@Video1]` | `"Edit Video1 according to the instructions. Keep everything else the same."` |
| **Previous turn video for extension** | `[# Sources <PREVIOUS_VIDEO>@Video1]` | `"Extend Video1 seamlessly."` |
| **Image reference + video reference** | `[# References <IMAGE_REF_0>@Image1 <VIDEO_REF_0>@Video1]` | `"Use the given image(s) as references for video generation. The images should not be used as literal initial frames. Use the given video(s) as references. Do not use them as a source for video editing."` |

#### Full Prefix-Declared Prompt Examples

**1. Starting Frame + Character Reference Image:**
```text
[# Sources <FIRST_FRAME>@Image1] [# References <IMAGE_REF_0>@Image2]
Continuous tracking shot as the woman <IMAGE_REF_0> walks across the misty courtyard shown in the opening frame.
Use Image1 as the starting frame. Use Image2 as a reference for the video generation. The reference image should not be used as a literal initial frame.
```

**2. Object Reference Image + Character/Motion Reference Video:**
```text
[# References <IMAGE_REF_0>@Image1 <VIDEO_REF_0>@Video1]
The musician in <VIDEO_REF_0> is playing the carved acoustic violin shown in <IMAGE_REF_0> on a dimly lit concert stage.
Use Video1 as a character and motion reference and Image1 as an object reference. Do not use Video1 as a source for video editing, and do not use Image1 as a literal initial frame.
```

---

## 4. Typography & On-Screen Text Rendering

Gemini Omni 1.2 Flash renders legible text on both kinetic graphic overlays and physical in-scene surfaces (street signs, storefronts, product labels, digital screens, license plates) when prompted with exact strings:

1. **Always enclose target text in quotation marks (`"..."`)**:
   - `"There is a street sign that says \"OMNI WAY\", a neon storefront that says \"CYBER CAFE\", and a parked coupe with the license plate \"OMNI1.2\"."`
2. **Word-by-word kinetic sequences**:
   - `"One word on the screen at a time: \"did, you, know, that, Omni, can, do, awesome, text?\" Each word appears for 1s with a different animated typographic style. Upbeat percussive audio. No dialogue."`
3. **Product packaging lock (`<IMAGE_REF_N>`)**:
   - When animating a branded product photo, explicitly anchor the typography: `"Ensure the packaging typography, logo placement, and brand colors on <IMAGE_REF_0> remain sharp and identical to the reference image across the entire camera pan."`

---

## 5. Inline Negative Constraints & Unsupported API Fields

The Interactions API for `gemini-omni-1.2-flash` does **not** accept `system_instruction`, `temperature`, `top_p`, `stop_sequences`, or a separate `negative_prompt` field. Any negative constraint must be written as a short, direct sentence at the end of the prompt:

- `"No dialogue."` (prevents unsolicited voiceovers or character speech)
- `"No scene cuts."` (prevents multi-shot editing jumps)
- `"No extra sound effects."` (prevents cartoonish Foley layers)
- `"No embellishments."` (prevents hallucinated props or visual flourishes)
- `"Do not show the reference sketch in the final video; use it only as a movement guide."`
