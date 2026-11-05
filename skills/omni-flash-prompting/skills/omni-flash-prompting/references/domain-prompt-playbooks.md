# Domain Prompt Playbooks for Gemini Omni 1.2 Flash (`gemini-omni-1.2-flash`)

Eight production-tested prompt blueprints and multi-turn scripts designed specifically for **Gemini Omni 1.2 Flash (`gemini-omni-1.2-flash`)**.

---

## Playbook 1: 15-Second 3-Act Product Commercial (Brand Color & Packaging Typography Lock)

**Use Case**: Turning a static product photo (`<IMAGE_REF_0>`) and a mood/lighting reference (`<IMAGE_REF_1>`) into a 15-second commercial where brand colors and label typography never warp across camera angles.

- **Duration**: `15s` (`9:16` vertical or `16:9` landscape)
- **Media Inputs**: `Image1` = Product bottle photo (`<IMAGE_REF_0>`), `Image2` = Lighting/style reference (`<IMAGE_REF_1>`)

```text
[# References <IMAGE_REF_0>@Image1 <IMAGE_REF_1>@Image2]
Continuous, unbroken 15-second commercial shot in the lighting and palette style of <IMAGE_REF_1>. No scene cuts.
[0-5s] Low-angle macro tracking shot pushing toward the skincare serum bottle <IMAGE_REF_0> resting on a wet travertine stone pedestal as morning sunbeams slice through tropical foliage.
[5-10s] Camera orbits 120 degrees smoothly around the pedestal; a single crystal water droplet rolls down the frosted amber glass, catching golden specular highlights. Ensure the packaging text "AURA BOTANICA" and cobalt-blue cap match <IMAGE_REF_0> precisely.
[10-15s] Camera settles into a centered hero frame as subtle ripples spread across the shallow water base and the on-screen title "PURE HYDRATION" fades in cleanly below the pedestal.
Sound design: gentle water ripple, warm resonant synth pad with soft chime harmonics. No dialogue. No scene cuts.
Use the given image(s) as references for video generation. The images should not be used as literal initial frames.
```

---

## Playbook 2: Continuous FPV Drone & Architectural Flythrough (Zero Jump Cuts)

**Use Case**: Guiding a high-speed, continuous single-take camera trajectory through complex architecture using spatial reference photos without unwanted cutaways.

- **Duration**: `12s–15s` (`16:9`)
- **Media Inputs**: `Image1` = Architectural courtyard photo (`<IMAGE_REF_0>`)

```text
[# References <IMAGE_REF_0>@Image1]
Continuous, unbroken single-take FPV drone shot. No scene cuts.
[0-5s] The FPV camera glides rapidly at eye level across the sunlit Renaissance cobblestone piazza inspired by <IMAGE_REF_0>, banking smoothly between marble columns as pigeons scatter upward in slow motion.
[5-10s] The camera pitches upward at 45 degrees and flies directly through the open oculus of the vaulted limestone dome, transitioning from warm courtyard shadow into brilliant golden sunbeams.
[10-15s] Clearing the rooftop parapet, the camera levels out into a sweeping panoramic reveal of the terracotta skyline at sunset.
Consider micro-detail in the weathered stone carvings, realistic motion blur at the frame edges, and physically accurate sunlight flare.
Sound design: rushing wind whoosh synchronized with camera banking, distant church bells echoing across the square. No dialogue. No scene cuts.
Use Image1 as an architectural reference for video generation. The image should not be used as a literal initial frame.
```

---

## Playbook 3: Multi-Character Consistency & 3-Second Motion Transfer (`<IMAGE_REF>` + `<VIDEO_REF>`)

**Use Case**: Combining up to 6 character/object reference images with a `~3s` motion reference clip (`<VIDEO_REF_0>`) so characters maintain facial identity and wardrobe across angles while executing exact choreography.

- **Duration**: `10s–15s` (`16:9`)
- **Media Inputs**: `Image1` = Lead dancer (`<IMAGE_REF_0>`), `Image2` = Partner dancer (`<IMAGE_REF_1>`), `Image3` = Violin prop (`<IMAGE_REF_2>`), `Video1` = 3-second choreography reference clip (`<VIDEO_REF_0>`)

```text
[# References <IMAGE_REF_0>@Image1 <IMAGE_REF_1>@Image2 <IMAGE_REF_2>@Image3 <VIDEO_REF_0>@Video1]
[0-5s] Medium tracking shot on a candlelit wooden theater stage: performer <IMAGE_REF_0> holds the vintage violin <IMAGE_REF_2> and initiates the sweeping spin and bow choreography shown in <VIDEO_REF_0>.
[5-10s] Camera pans smoothly right to include partner <IMAGE_REF_1> in a tailored midnight-blue coat stepping into frame, mirroring the exact cadence and footwork of <VIDEO_REF_0>.
[10-15s] Two-shot finale as both performers lock eyes at center stage under a warm overhead spotlight, amber dust motes swirling around them.
Apply costume design principles to keep fabric drape, facial features, and violin woodgrain consistent across every angle.
Sound design: virtuosic solo violin melody at 120 BPM matching the bow strokes, crisp shoe taps on hollow stage floorboards. No dialogue.
Use the given image(s) as references for video generation; do not use them as literal initial frames. Use Video1 as a motion reference; do not use it as a source for video editing.
```

---

## Playbook 4: Keyframe Interpolation & Seamless Infinite Loops (`<FIRST_FRAME>` + `<LAST_FRAME>`)

### Variant A: State-to-State Keyframe Transition (`Start != End`)
- **Media Inputs**: `Image1` = Closed antique wooden door (`<FIRST_FRAME>`), `Image2` = Open door revealing a bioluminescent garden (`<LAST_FRAME>`)
```text
[# Sources <FIRST_FRAME>@Image1 <LAST_FRAME>@Image2]
Continuous, unbroken dolly-in shot in a single scene. No scene cuts.
The heavy carved oak door slowly unlatches and swings inward at a natural, weighty pace, transitioning smoothly from the dim stone hallway in the first frame to the glowing bioluminescent night garden in the final frame.
Sound design: heavy iron latch click, slow wooden hinge creak, swelling ambient night crickets and soft wind chimes. No dialogue.
Use Image1 as the starting frame and Image2 as the final frame.
```

### Variant B: Seamless Infinite Loop (`Start == End`)
- **Media Inputs**: `Image1` = Floating kinetic glass sculpture (`<FIRST_FRAME>` and `<LAST_FRAME>`)
```text
[# Sources <FIRST_FRAME>@Image1 <LAST_FRAME>@Image1]
Continuous, unbroken macro shot in a single scene. No scene cuts.
The iridescent blown-glass kinetic sculpture completes one smooth, physically consistent 360-degree rotation in mid-air, refracting caustic rainbow light across the matte slate backdrop before returning to its exact starting orientation.
Sound design: seamless ambient crystalline hum. No dialogue. No extra sound effects.
Use this image as the first frame and the last frame.
```

---

## Playbook 5: Multi-Turn Conversational Editing Sequence (`previous_interaction_id`)

**Use Case**: Iterating on a `720p` draft (\$0.07/s) across 4 chat turns—modifying environment, product colorway, and aspect ratio one axis at a time without losing the base performance.

| Turn | Mode / API Call | Exact Prompt | Why It Works |
| :--- | :--- | :--- | :--- |
| **Turn 1** | `generate` (`720p`, `10s`, `16:9`, `store=True`) | `"Continuous, unbroken medium tracking shot of a runner in a crimson windbreaker jogging across the Golden Gate Bridge at sunrise. Fog rolls beneath the towers. Sound design: rhythmic footsteps, ocean wind. No dialogue. No scene cuts."` | Establishes a clean single-take base with `store=True` so `previous_interaction_id` is saved. |
| **Turn 2** | `edit` (`previous_interaction_id=turn1.id`) | `"Change the runner's windbreaker colorway from crimson to electric lime green. Keep the runner's stride, facial features, bridge background, and sunrise lighting identical to the source video."` | Isolates a single colorway change with an explicit anchor lock. |
| **Turn 3** | `edit` (`previous_interaction_id=turn2.id`) | `"Change the weather to a dramatic twilight rainstorm with wet pavement reflections. Keep the runner's performance, electric lime windbreaker, and camera framing the same."` | Relights the scene without re-rolling the runner's motion or Turn 2's jacket color. |
| **Turn 4** | `upscale` (`previous_interaction_id=turn3.id`, `resolution="4k"`, `delivery="uri"`) | `"Render this scene in 4K resolution. Keep everything else the same."` | Locks the final approved cut at `4k` via `URI` delivery. |

---

## Playbook 6: Rapid-Fire 24fps Montage & Kinetic Typography

**Use Case**: High-tempo social ads, title sequences, or educational explainers with exact beat cuts and readable on-screen labels.

- **Duration**: `10s` (`9:16` vertical)

```text
Make a rapid-fire 10-second vertical 9:16 video that cuts to a new macro culinary shot every 2 seconds (48 frames at 24fps), synchronized to a crisp 120 BPM funk drum beat.
[0-2s] Extreme close-up of espresso extracting from a bottomless portafilter in rich tiger-striped crema; bold white on-screen text reads "01. GRIND".
[2-4s] High-speed macro shot of steamed micro-foam pouring into a ceramic cup to form a rosette; on-screen text reads "02. POUR".
[4-6s] Torch flame caramelizing raw sugar crystals atop a pastry crust; on-screen text reads "03. TORCH".
[6-8s] Powdered matcha sifting in slow motion through a fine brass mesh; on-screen text reads "04. DUST".
[8-10s] Overhead hero table shot of all four items arranged on a sunny marble counter; centered title text reads "MORNING RITUAL".
Sound design: tight 120 BPM percussive groove with subtle tactile Foley on each cut. No dialogue.
```

---

## Playbook 7: Multi-Speaker Dialogue, Lip-Sync & Stateful Voice Extension

**Use Case**: Generating natural two-person dialogue with accurate lip-sync and acoustic room tone, then extending the conversation in Turn 2 via `previous_interaction_id`.

### Turn 1 (`generate`, `12s`, `16:9`):
```text
[0-6s] Medium two-shot inside a warm vintage recording studio with acoustic foam walls: a woman in round tortoiseshell glasses leans toward a condenser microphone and says in a calm, warm voice: "Did we capture the final room tone on track four?"
[6-12s] The sound engineer sitting beside her at the mixing console glances up from the glowing VU meters, smiles, and replies clearly: "Locked and leveled. Listen to the decay on that last chord."
Consider subtle facial micro-expressions, natural eye contact, and accurate lip-sync. Sound design: quiet studio room tone, soft analog console switch click. No background music.
```

### Turn 2 (`extend` via `previous_interaction_id`, `+8s` $\rightarrow$ `20s` total):
```text
Extend this video.
[0-4s] He pushes the master fader up with a smooth motion as a warm resonant piano chord fills the studio monitors.
[4-8s] She nods slowly and says: "That's the take. Print it." Keep the characters, studio lighting, and camera framing consistent.
```
*(Note: Extending spoken dialogue works here because Turn 2 extends a **model-generated** video via `previous_interaction_id`, whereas uploaded videos with speech cannot be extended with new dialogue.)*

---

## Playbook 8: Horizon Extension with Mid-Scene Reference Injection (Prompt-Only Extend)

**Use Case**: Extending an existing `10s` clip by `10s` while introducing a brand-new character (`<IMAGE_REF_0>`) and motion reference (`<VIDEO_REF_0>`) into the extended timeline.

- **Critical Setup**: Do **not** set `task="extend"` in `video_config` (which disables reference media). Omit `task` and use `"Extend this video."` at the start of the prompt.
- **Media Inputs**: `Video1` = 10s source clip to extend (`<VIDEO_0>`), `Image1` = New character reference (`<IMAGE_REF_0>`), `Video2` = 3s motion reference (`<VIDEO_REF_0>`)

```text
[# Sources <VIDEO_0>@Video1] [# References <IMAGE_REF_0>@Image1 <VIDEO_REF_0>@Video2]
Extend this video. The scene continues seamlessly in the same sunlit atrium.
[0-4s] After 1s in the extended timeline, the camera pans right toward the glass staircase as the character shown in <IMAGE_REF_0> walks down into the frame.
[4-10s] They greet the main subject with the exact wave and spin gesture shown in <VIDEO_REF_0> while the ambient acoustic soundtrack swells into the main melody.
Use Image1 as a character reference; do not use it as a literal initial frame. Use Video2 as a motion reference; do not use it as a source for video editing.
```
